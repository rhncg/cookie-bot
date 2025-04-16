import discord
from funcs.numerize import numerize
from src.funcs.data import get_data
from src.funcs.db import get_db_connection
from src.views.leaderboard import LeaderboardView
from src.funcs.background import log_active
from funcs.globals import admins

class Leaderboard(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.command(description="View the leaderboard")
    async def leaderboard(self, ctx):
        await log_active(ctx)
        
        if ctx.author.id not in admins:
            await ctx.respond("Sorry, this command is temporarily disabled while I fix a bug.")
            return
        
        data = await get_data(ctx.author.id)
        await ctx.defer()
        conn = await get_db_connection()
        cursor = await conn.cursor()
        
        query = '''
        SELECT user_id, CAST(balance AS INTEGER) FROM users ORDER BY CAST(balance AS INTEGER) DESC LIMIT 10
        '''

        await cursor.execute(query)
        rows = await cursor.fetchall()
        embed = discord.Embed(title="Cookies Leaderboard", color=0x6b4f37)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue
            embed.add_field(name="", value=f"{i + 1}. <@{row[0]}> - {numerize(row[1], 2)} cookies", inline=False)
        await ctx.respond(embed=embed, view=LeaderboardView(ctx))
        
def setup(bot):
    bot.add_cog(Leaderboard(bot))