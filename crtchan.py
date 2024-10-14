import discord
from discord.ext import commands

class ChannelManager(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot
    @commands.command()  
    @commands.has_permissions(manage_channels=True)  
    async def crtchan(self, ctx, category_name: str, name: str, channel_type: str, privacy: str):
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        if category is None:
            await ctx.send(f"Category '{category_name}' not found.")
            return
        if channel_type not in ["tc", "vc"]:
            await ctx.send("Invalid channel type. Use 'tc' for text channel or 'vc' for voice channel.")
            return
        if privacy not in ["priv", "pub"]:
            await ctx.send("Invalid privacy setting. Use 'priv' for private channel or 'pub' for public channel.")
            return
        overwrites = {}
        if privacy == "priv":
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)
            }
        if channel_type == "tc":
            channel = await ctx.guild.create_text_channel(name, overwrites=overwrites, category=category)
        else:
            channel = await ctx.guild.create_voice_channel(name, overwrites=overwrites, category=category)

        await ctx.send(f"Channel '{channel.name}' created successfully in the category '{category.name}'!")
async def setup(bot):
    await bot.add_cog(ChannelManager(bot))
