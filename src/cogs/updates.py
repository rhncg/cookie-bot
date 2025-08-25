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
        embed = discord.Embed(title="Help", color=0x6b4f37)
        
        embed.add_field(name="</bake:1309975983503183963>",value=
                        "This command allows you to bake cookies. "
                        "The number of cookies you bake and the time it "
                        "takes to bake them depends on your upgrades "
                        "which you can upgrade in the shop")
        
        embed.add_field(name="</gamble:1311561198604648560>", value=
                        "This command allows you to gamble your cookies. "
                        "You can choose to gamble a certain amount of cookies "
                        "and try to win up to that amount or lose up to that amount.")
        
        embed.add_field(name="</steal:1326045688160583823>", value=
                        "This command allows you to steal cookies from other users. "
                        "You cannot steal from people who have too many cookies compared to you. "
                        "You can also steal from people by right clicking them and going to \"Apps\".")
        
        embed.add_field(name="</daily:1312166223559266407>", value=
                        "This commands allows you to claim your daily reward. "
                        "Claiming a reward for multiple days in a row will give you an extra bonus "
                        "and increase your daily streak.")
        
        embed.add_field(name="</shop:1310001981066313738>", value=
                        "This command allows you to view the shop. "
                        "In the shop, you can buy upgrades and boosts. "
                        "These help you improve your cookie production.")
        
        embed.add_field(name="</leaderboard:1311162275482042370>", value=
                        "This command allows you to view the leaderboard and see the ranking of all users. "
                        "You can sort by balance, level, and daily streak.")
        
        embed.add_field(name="</profile:1311159037219569705>", value=
                        "This command allows you to view your or someone else's profile. "
                        "You can see balance, level, daily streak, and other stats.")
        
        embed.add_field(name="</options:1332478462354784256>", value=
                        "This command allows you to configure many settings. "
                        "More settings will be added in the future, "
                        "feel free to suggest any settings you would like to see.")
        
        embed.add_field(name="</cooldowns:1326803840858853520>", value=
                        "This command allows you to view cooldowns for various commands. ")
        
        embed.add_field(name="</updates:1328582089934766174>", value=
                        "This command allows you to view updates and upcoming features. ")
        
        embed.add_field(name="</suggest:1327132851371507824>", value=
                        "This command allows you to suggest new features. ")
        
        embed.add_field(name="</about:1359289316957749468>", value=
                        "This command allows you to view bot info. ")
        
        await ctx.respond(embed=embed)
        
        
        
        
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
                                                "- You can now change your profile color in /options (must be level 200 or higher)"
                                                "- Fixed Leaderboard"
                                                "- Added Gifting", inline=False)
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