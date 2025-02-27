import discord
from src.funcs.globals import dev_bots
from src.funcs.quest_calc import make_quest_embed

class Quests(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.command()
    async def quests(self, ctx):
        if self.bot.user.id not in dev_bots:
            coming_soon_embed = discord.Embed(title="Quests are Coming Soon", color=0x6b4f37)
            await ctx.respond(embed=coming_soon_embed)
            return
        else:
            pass