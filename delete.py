import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
import traceback
import time
class Del(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def delete(self, ctx, amount: int = 150, member: discord.Member = None, *, reason=None):
        if reason is None:
            reason = "No reason provided"
        if amount < 1 or amount > 100:
            await ctx.send("Please specify an amount between 1 and 100.")
            return
        if member is None:
            messages = [message async for message in ctx.channel.history(limit=amount)]
            deleted_messages = 0
            for message in messages:
                await message.delete()
                time.sleep(0.5)
                deleted_messages += 1
            await ctx.send(f"Deleted {deleted_messages} messages from all users.")
        else:
            messages = [message async for message in ctx.channel.history(limit=amount)]
            deleted_messages = 0
            for message in messages:
                if message.author == member:
                    await message.delete()
                    time.sleep(0.5)                    
                    deleted_messages += 1
            await ctx.send(f"Deleted {deleted_messages} messages from {member.mention}.")

async def setup(bot):
    await bot.add_cog(Del(bot))
