import discord
from src.views.options import OptionsView, make_options_embed

class Options(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.command()
    async def options(self, ctx):
        embed = await make_options_embed(ctx.author.id)
        await ctx.respond(embed=embed, view=OptionsView())
        
def setup(bot):
    bot.add_cog(Options(bot))