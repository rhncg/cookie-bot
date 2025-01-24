import discord
from src.funcs.globals import admins

class Updates(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @discord.command()
    async def updates(self, ctx):
        embed = discord.Embed(title="Updates", color=0x6b4f37)
        embed.add_field(name="Version", value="2.1.0", inline=False)
        embed.add_field(name="Completed", value="- Buffed Idle Upgrade (higher rate now)\n"
                                                "- Fixed stealing bug\n"
                                                "- Boosts are now available", inline=False)
        embed.add_field(name="Upcoming", value="- Drops\n"
                                            "- Leaderboard Improvements\n"
                                            "- Better Gambling\n"
                                            "- QOL stuff\n"
                                            "- Better XP scaling\n"
                                            "- Options Menu", inline=False)
        await ctx.respond(embed=embed)
    
    @discord.command()
    async def suggest(self, ctx, suggestion: str):
        await ctx.defer(ephemeral=True)
        for users in admins:
            user = await self.bot.fetch_user(users)
            await user.send(f"{ctx.author.name} has suggested: {suggestion}")
        await ctx.respond("Your suggestion has been sent to rohan.", ephemeral=True)
        
def setup(bot):
    bot.add_cog(Updates(bot))