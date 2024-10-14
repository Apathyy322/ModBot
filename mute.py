import discord
from discord.ext import commands
import sqlite3
from datetime import datetime, timedelta, timezone
import traceback
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
DB_FILE = 'mutes.db'
log_channel_id = os.getenv('log_channel_id')

def setup_database():
    try:
        connec = sqlite3.connect(DB_FILE)
        cursor = connec.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mutes (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            user_name TEXT,
            muted_by TEXT,
            reason TEXT,
            length TEXT,
            muted_at TEXT,
            unmute_at TEXT
        )
        ''')
        connec.commit()
    except Exception as e:
        print(f"Error setting up database: {e}")
        print(traceback.format_exc())
    finally:
        connec.close()

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        setup_database()

    @commands.has_permissions(manage_roles=True)
    @commands.command(name="mute")
    async def mute(self, ctx, member: discord.Member, length: str, *, reason: str = None):
        try:
            # Delete the command message
            await ctx.message.delete()

            time_unit = length[-1] 
            time_value = int(length[:-1])
            if time_unit == 'm':
                mute_duration = timedelta(minutes=time_value)
            elif time_unit == 'h':
                mute_duration = timedelta(hours=time_value)
            elif time_unit == 'd':
                mute_duration = timedelta(days=time_value)
            else:
                await ctx.send("Invalid time unit! Use m (minutes), h (hours), or d (days).")
                return

            mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if mute_role is None:
                await ctx.send("Muted role not found! Make sure the 'Muted' role exists.")
                return

            await member.add_roles(mute_role)
            muted_at = datetime.now(timezone.utc)  
            unmute_at = muted_at + mute_duration  

            connec = sqlite3.connect(DB_FILE)
            cursor = connec.cursor()
            cursor.execute('''
            INSERT INTO mutes (user_id, user_name, muted_by, reason, length, muted_at, unmute_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (member.id, str(member), str(ctx.author), reason, length, muted_at.strftime("%Y-%m-%d %H:%M:%S"), unmute_at.strftime("%Y-%m-%d %H:%M:%S")))
            connec.commit()

            # Get the member's ID
            member_id = member.id

            # Logging the mute action
            log_channel = self.bot.get_channel(int(log_channel_id))
            if log_channel:
                await log_channel.send(f"**[+] Muted:** {member.display_name} ||({member_id})|| \n| **Muted by:** {ctx.author.mention} \n| **Mute Length:** {length} \n| **Reason:** {reason}. \n\n ***Successfully added to Database!***")
            else:
                print("Log channel not found!")

            await ctx.send(f"Muted {member.display_name} for {length} because: {reason}")
            await asyncio.sleep(mute_duration.total_seconds())  
            await member.remove_roles(mute_role)

            if log_channel:
                await log_channel.send(f"**[+] {member.display_name} has been unmuted after {length}.**")
        except Exception as e:
            print(f"Error muting user: {e}")
            print(traceback.format_exc())
            if log_channel:
                await log_channel.send("An error occurred while trying to mute the user.")

async def setup(bot):
    await bot.add_cog(Mute(bot))

# Main bot setup
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True  
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user.name}')

async def main():
    await setup(bot)
    token = os.getenv('token')
    await bot.start(token)

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
