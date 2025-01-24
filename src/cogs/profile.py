import discord
from numerize.numerize import numerize
from datetime import datetime
from src.funcs.data import get_data
from src.funcs.level import get_xp_bar_data, calculate_level

class Profile(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @discord.command()
    async def profile(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author
        try:
            data = await get_data(user.id)
            balance = data['balance']
            bake_speed = data['bake_speed']
            oven_cap = data['oven_cap']
            idle_upgrade_level = data['idle_upgrade_level']
            idle_upgrade = round(1.15 ** (idle_upgrade_level - 1) - 1, 1)
            bar_data = await get_xp_bar_data(data['xp'])
            embed = discord.Embed(color=0x6b4f37)
            embed.add_field(name=f"Level {await calculate_level(data['xp'])} - {numerize(data['xp'], 2)} xp", value=bar_data[3],
                            inline=False)
            embed.add_field(name=f"{numerize(bar_data[1] - data['xp'], 2)} xp to level {await calculate_level(data['xp']) + 1}",
                            value="", inline=False)
            embed.add_field(name="Balance", value=f"{numerize(balance, 2)} cookies", inline=True)
            embed.add_field(name="Bake Speed", value=f"{numerize(bake_speed, 2)} seconds", inline=True)
            embed.add_field(name="Oven Capacity", value=f"{numerize(oven_cap, 2)} cookies", inline=True)
            embed.add_field(name="Idle Rate", value=f"{numerize(idle_upgrade, 2)} cookies per minute", inline=True)
            embed.add_field(name="Total Cookies Baked", value=numerize(data['total_cookies'], 2), inline=True)
            embed.set_author(name=f"{user.name}'s profile", icon_url=user.display_avatar.url)
            await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(f"That isn't a valid user. {e}", ephemeral=True)
            
    @discord.command()
    async def cooldowns(self, ctx):
        data = await get_data(ctx.author.id)
        embed = discord.Embed(title="Cooldowns", color=0x6b4f37)
        if datetime.now().timestamp() - data['last_daily'] < 57600:
            embed.add_field(name="Daily", value=f"Your daily reward will be available <t:{int(data['last_daily']) + 57600}:R>", inline=False)
        else:
            embed.add_field(name="Daily", value="Your daily reward is available.", inline=False)

        if datetime.now().timestamp() - data['last_steal'] < 900:
            embed.add_field(name="Steal", value=f"Your steal will be available <t:{int(data['last_steal']) + 900}:R>", inline=False)
        else:
            embed.add_field(name="Steal", value="Your steal is available.", inline=False)

        if datetime.now().timestamp() - data['last_gamble'] < 120:
            embed.add_field(name="Gamble", value=f"Your gamble will be available <t:{int(data['last_gamble']) + 120}:R>", inline=False)
        else:
            embed.add_field(name="Gamble", value="Your gamble is available.", inline=False)
        
        if data['boost_time'] + 900 > datetime.now().timestamp():
            active = f"Inactive (Cooldown ends <t:{int(data['boost_time'] + 900)}:R>)"
        if data['boost_time'] > datetime.now().timestamp():
            active = f"Active (Boost ends <t:{int(data['boost_time'])}:R>)"
        if data['boost_time'] + 900 < datetime.now().timestamp():
            active = "Inactive (Ready)"
        
        embed.add_field(name="Boost", value=active, inline=False)

        await ctx.respond(embed=embed)
            
    @discord.command()
    async def balance(self, ctx):
        data = await get_data(ctx.author.id)
        balance = data['balance']
        await ctx.respond(f'You have {balance} cookies.')
            
def setup(bot):
    bot.add_cog(Profile(bot))