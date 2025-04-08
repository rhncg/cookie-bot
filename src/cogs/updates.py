import discord
from src.funcs.globals import admins, version

class Updates(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @discord.command(description="View bot info")
    async def about(self, ctx):
        embed = discord.Embed(title="About", color=0x6b4f37)
        embed.add_field(name="Use </help:1359289316957749469> to view all commands", value="", inline=False)
        embed.add_field(name="Use </updates:1328582089934766174> to view updates and upcoming features", value="", inline=False)
        embed.add_field(name="Use </suggest:1327132851371507824> to suggest new features", value="", inline=False)
        embed.add_field(name="Developed by", value="@rhncg", inline=False)
        embed.add_field(name="This bot's source code is open source", value="You can check out the [Github](https://github.com/rhncg/cookie-bot)", inline=False)
        embed.set_footer(text=f"Version: {version}")
        await ctx.respond(embed=embed)
        
    
    @discord.command(description="View command info")
    async def help(self, ctx):
        await ctx.responds("Coming soon", ephemeral=True)
        
    @discord.command(description="View updates and upcoming features")
    async def updates(self, ctx):
        embed = discord.Embed(title="Updates", color=0x6b4f37)
        embed.add_field(name="Version", value=f"{version}", inline=False)
        embed.add_field(name="Completed (in order of completion)", value="- Buffed Idle Upgrade (higher rate now)\n"
                                                "- Fixed stealing bug\n"
                                                "- Boosts are now available\n"
                                                "- Added options menu\n"
                                                "- Boosts are cheaper to activate now\n"
                                                "- Drops\n"
                                                "- You can now right click a user and go to \"Apps\" to steal from them or view their profile.\n"
                                                "- You can now refresh the shop.\n"
                                                "- Better XP scaling\n"
                                                "- Boost Duration Upgrade\n"
                                                "- More compact shop layout\n"
                                                "- Better Leaderboard (Pagination, Jumping to self)\n"
                                                "- Made better number numerizer\n"
                                                "- Leaderboard Sort Rework\n"
                                                "- You can now disable the gamble confirmation window\n"
                                                "- You can now change your profile color in /options (must be level 200 or higher)", inline=False)
        embed.add_field(name="Upcoming (in no particular order)", value="- Better Gambling\n"
                                                "- Quests\n"
                                                "- QOL stuff", inline=False)
        await ctx.respond(embed=embed)
    
    @discord.command(description="Suggest new features")
    async def suggest(self, ctx, suggestion: str):
        await ctx.defer(ephemeral=True)
        for users in admins:
            user = await self.bot.fetch_user(users)
            await user.send(f"{ctx.author.name} has suggested: {suggestion}")
        await ctx.respond("Your suggestion has been sent", ephemeral=True)
        
def setup(bot):
    bot.add_cog(Updates(bot))