import discord
from discord.ext import commands

class DeleteManager(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_channels=True)  
    async def delchan(self, ctx, *, args: str):
        try:
            category_name, channel_name = args.split(" | ")
        except ValueError:
            await ctx.send("Please format the input as: `category_name | channel_name`")
            return
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        if not category:
            await ctx.send(f"Category '{category_name}' not found.")
            return
        channel = discord.utils.get(category.channels, name=channel_name)
        if not channel:
            await ctx.send(f"Channel '{channel_name}' not found in category '{category_name}'.")
            return
        await channel.delete()
        await ctx.send(f"Channel '{channel_name}' deleted successfully!")

async def setup(bot):
    await bot.add_cog(DeleteManager(bot))
