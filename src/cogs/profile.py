import discord
from funcs.numerize import numerize
from datetime import datetime
from src.funcs.data import get_data
from src.funcs.level import get_xp_bar_data, calculate_level
from src.funcs.profile import get_profile
from funcs.log_server import log_active

class Profile(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @discord.command(description="View your or someone else's profile")
    async def profile(self, ctx, user: discord.User = None):
        await log_active(ctx)
        
        if user is None:
            user = ctx.author
        await get_profile(ctx, user)
    
    @discord.user_command(name="Profile")
    async def user_profile(self, ctx, user: discord.Member):
        await log_active(ctx)
        await get_profile(ctx, user)
            
    @discord.command(description="View cooldowns for multiple commands")
    async def cooldowns(self, ctx):
        await log_active(ctx)
        
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
        
        if data['boost_time'] + data['boost_speed'] * 60 > datetime.now().timestamp():
            active = f"Inactive (Cooldown ends <t:{int(data['boost_time'] + data['boost_speed'] * 60)}:R>)"
        if data['boost_time'] > datetime.now().timestamp():
            active = f"Active (Boost ends <t:{int(data['boost_time'])}:R>)"
        if data['boost_time'] + data['boost_speed'] * 60 < datetime.now().timestamp():
            active = "Inactive (Ready)"
        
        embed.add_field(name="Boost", value=active, inline=False)

        await ctx.respond(embed=embed)
            
    @discord.command(description="View your balance")
    async def balance(self, ctx):
        await log_active(ctx)
        
        data = await get_data(ctx.author.id)
        balance = data['balance']
        await ctx.respond(f'You have {balance} cookies.')
            
def setup(bot):
    bot.add_cog(Profile(bot))