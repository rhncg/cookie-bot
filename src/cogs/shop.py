import discord
from src.funcs.data import get_data
from src.funcs.upgrade_calc import make_shop_embed
from src.views.upgrade import UpgradeView
from src.funcs.background import log_active

class Shop(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description="View the shop")
    async def shop(self, ctx):
        await log_active(ctx)
        
        data = await get_data(ctx.author.id)
        embed = await make_shop_embed(ctx.author.id, self.bot)
        await ctx.respond(embed=embed, view=UpgradeView(ctx.author.id, data['ping'], data['boost_time'], data['boost_speed']))

def setup(bot):
    bot.add_cog(Shop(bot))