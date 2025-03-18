import discord
from datetime import datetime
from funcs.numerize import numerize
import random
from src.funcs.data import get_data, update_data, update_balance
from src.funcs.globals import gamble_users
from src.funcs.steal import try_steal
from src.views.gamble import GambleConfirmationView


class Gains(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.command(description="Steal cookies from other people")
    async def steal(self, ctx, user: discord.User):
        await try_steal(ctx, user)
        
    @discord.user_command(name="Steal")
    async def user_steal(self, ctx, user: discord.Member):
        await try_steal(ctx, user)
    
    @discord.command(description="Gamble your cookies")
    async def gamble(self, ctx, quick_selection: discord.Option(str, choices=['all', 'half']) = None, amount: int = None): # type: ignore
        data = await get_data(ctx.author.id)
        last_gamble = data['last_gamble']
        balance = data['balance']
        if datetime.now().timestamp() - last_gamble < 120:
            await ctx.respond(
                f"You have already gambled recently.\nYou can gamble again <t:{int(last_gamble + 120)}:R>.", ephemeral=True)
            return

        if amount is None and quick_selection is None:
            await ctx.respond("You must specify an amount of cookies to gamble.", ephemeral=True)
            return

        if amount is not None and quick_selection is not None:
            await ctx.respond("You cannot specify both an amount and a quick selection.", ephemeral=True)
            return

        if quick_selection == 'all':
            amount = int(balance)
        elif quick_selection == 'half':
            amount = balance // 2

        if balance < amount:
            await ctx.respond("You don't have enough cookies to gamble that amount.")
            return
        if not amount > 0:
            await ctx.respond("You must gamble a positive amount of cookies.")
            return

        if ctx.author.id in gamble_users:
            await ctx.respond(f"You already have a confirmation window open.", ephemeral=True)
            return
        gamble_users.append(ctx.author.id)

        embed = discord.Embed(title=f"Are you sure you want to gamble {numerize(amount, 2)} cookies?", color=0x6b4f37)
        embed.add_field(name=f"You can either win or lose up to {numerize(amount, 2)} cookies.", value="", inline=False)
        embed.add_field(name="This action cannot be undone.", value="", inline=False)
        await ctx.respond(embed=embed, view=GambleConfirmationView(ctx.author.id, amount))
        
    @discord.command(description="Claim your daily reward")
    async def daily(self, ctx):
        data = await get_data(ctx.author.id)
        if datetime.now().timestamp() - data['last_daily'] < 57600:
            await ctx.respond(
                f"You have already claimed your daily reward.\nYou can claim your next daily reward <t:{int(data['last_daily'] + 57600)}:R>.", ephemeral=True)
        else:
            reward = int(0.02 * (1 + data['daily_streak']/5) * data['balance'])
            
            last_daily = data['last_daily']
            
            if last_daily == 0:
                last_daily = datetime.now().timestamp()
            
            if reward < 5:
                reward = 5
            
            if datetime.now().timestamp() - last_daily < 172800:
                data['daily_streak'] += 1
            else:
                data['daily_streak'] = 0

            data = await update_balance(data, reward)
            data['last_daily'] = datetime.now().timestamp()
            await update_data(data)
            if data['boost_time'] > datetime.now().timestamp():
                boost = data['boost_level'] * 0.25 + 1
            else:
                boost = 1
            await ctx.respond(f"You have claimed your daily reward of **{numerize(reward * boost, 2)} cookies**. You're on a {data['daily_streak']} day streak. You now have {numerize(data['balance'], 2)} cookies.")
    

def setup(bot):
    bot.add_cog(Gains(bot))