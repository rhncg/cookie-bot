import discord
from funcs.numerize import numerize
from src.funcs.data import get_data
from src.funcs.db import get_db_connection
from src.views.leaderboard import LeaderboardView
from src.funcs.background import log_active

class Leaderboard(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.command(description="View the leaderboard")
    async def leaderboard(self, ctx):
        await log_active(ctx)
        
        data = await get_data(ctx.author.id)
        await ctx.defer()
        conn = await get_db_connection()
        cursor = await conn.cursor()
        
        query = '''
        SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10
        '''

        await cursor.execute(query)
        rows = await cursor.fetchall()
        embed = discord.Embed(title="Cookies Leaderboard", color=0x6b4f37)
        embed.add_field(name="The Cookies Leaderboard is currently not ordered, it will be fixed soon in an update.", value="", inline=False)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue
            embed.add_field(name="", value=f"{i + 1}. <@{row[0]}> - {numerize(row[1], 2)} cookies", inline=False)
        await ctx.respond(embed=embed, view=LeaderboardView(ctx))
        
def setup(bot):
    bot.add_cog(Leaderboard(bot))