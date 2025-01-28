import discord
from src.funcs.globals import admins

class Updates(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @discord.command()
    async def updates(self, ctx):
        embed = discord.Embed(title="Updates", color=0x6b4f37)
        embed.add_field(name="Version", value="2.2.5", inline=False)
        embed.add_field(name="Completed (in order of completion)", value="- Buffed Idle Upgrade (higher rate now)\n"
                                                "- Fixed stealing bug\n"
                                                "- Boosts are now available\n"
                                                "- Added options menu\n"
                                                "- Boosts are cheaper to activate now\n"
                                                "- Drops\n"
                                                "- You can now right click a user and go to \"Apps\" to steal from them or view their profile.\n"
                                                "- You can now refresh the shop.", inline=False)
        embed.add_field(name="Upcoming (in no particular order)", value="- Leaderboard Improvements\n"
                                                "- Boost Duration Upgrades\n"
                                                "- Better Gambling\n"
                                                "- QOL stuff\n"
                                                "- Better XP scaling", inline=False)
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