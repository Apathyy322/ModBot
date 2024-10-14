import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
import traceback

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DB_FILE = 'bans.db'
        self.setup_database()

    def setup_database(self):
        try:
            conn = sqlite3.connect(self.DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS bans (
                user_id INTEGER,
                user_name TEXT NOT NULL,
                banned_by TEXT NOT NULL,
                reason TEXT NOT NULL,
                time TIMESTAMP NOT NULL
            )
            ''')
            conn.commit()
        except Exception as e:
            print(f"Error setting up database: {e}")
            print(traceback.format_exc())
        finally:
            conn.close()

    def log_ban(self, user_id, user_name, banned_by, reason):
        conn = sqlite3.connect(self.DB_FILE)
        cursor = conn.cursor()
        ban_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        cursor.execute('''
        INSERT INTO bans (user_id, user_name, banned_by, reason, time) 
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, user_name, banned_by, reason, ban_time))
        conn.commit()
        print(f'Logged ban for {user_name} in database. Time: {ban_time}')
        conn.close()

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if reason is None:
            reason = "No reason provided"
        messages = [message async for message in ctx.channel.history(limit=100)]
        for message in messages:
            if message.author == member:
                await message.delete()

        try:
            await member.ban(reason=reason)
            self.log_ban(member.id, member.name, ctx.author.name, reason)
            print(f'Logged ban for {member.name} by {ctx.author.name} with reason: {reason}')
            log_channel = discord.utils.get(ctx.guild.text_channels, name="logs")
            if log_channel:
                await log_channel.send(f'| **Banned:** {member.mention} \n| **Reason:** {reason} \n| **Banned by:** {ctx.author.mention} \n| **Time (UTC):** {datetime.utcnow().strftime("%Y-%m-%d %H:%M")} UTC')
                print(f'Message sent to logs channel: {member.name} was banned.')
            else:
                print('Logs channel not found.')

            await ctx.send(f'Banned {member.mention} for reason: {reason}')
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send("I don't have the required permissions to ban this user.")
        except Exception as e:
            await ctx.send(f"An error occurred while trying to ban the user: {str(e)}")
            print(f"Error in ban command: {str(e)}")
            print(traceback.format_exc())

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to ban members.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a member to ban. Usage: !ban @member [reason]")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Could not find the specified member. Make sure you're using a valid @mention.")
        else:
            await ctx.send(f"An error occurred: {str(error)}")
            print(f"Error in ban command: {str(error)}")
            print(traceback.format_exc())
async def setup(bot):
    await bot.add_cog(Ban(bot))
