import discord
from datetime import datetime
from numerize.numerize import numerize
import random
from src.funcs.data import get_data, update_data, update_balance
from src.funcs.globals import gamble_users
from src.views.gamble import GambleConfirmationView

class Gains(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.command()
    async def steal(self, ctx, user: discord.User):
        if user.id == ctx.author.id:
            await ctx.respond("You cannot steal from yourself.", ephemeral=True)
            return
        data = await get_data(user.id)
        steal_balance = data['balance']

        self_data = await get_data(ctx.author.id)
        last_steal = self_data['last_steal']
        if datetime.now().timestamp() - last_steal < 900:
            await ctx.respond(
                f"You have already attempted to steal from someone recently.\nYou can steal again <t:{int(last_steal + 900)}:R>.", ephemeral=True)
            return

        if int(steal_balance * 0.2) < 1:
            await ctx.respond("That user doesn't have enough cookies.", ephemeral=True)
            return
        if int(steal_balance * 0.2) > self_data['balance'] * 3:
            await ctx.respond("That user has too many cookies for you to steal from.", ephemeral=True)
            return
        amount = random.randint(1, int(steal_balance * 0.2))
        chance = random.randint(1, 3)
        if chance == 1:
            self_data = await update_balance(self_data, amount)
            data = await update_balance(data, -amount)
            if data['boost_time'] > datetime.now().timestamp():
                boost = data['boost_level'] * 0.25 + 1
            else:
                boost = 1
            if data['steal_ping'] == True:
                await ctx.respond(f"You stole {numerize(amount * boost, 2)} cookies from <@{user.id}>.")
            else:
                await ctx.respond(f"You stole {numerize(amount * boost, 2)} cookies from {user.name}.")
        else:
            await ctx.respond(f"You were caught! You failed to steal any cookies from <@{user.id}>.")

        self_data['last_steal'] = datetime.now().timestamp()

        await update_data(data)
        await update_data(self_data)
    
    @discord.command()
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
            await ctx.respond("You don't have enough cookies to gamble.")
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
        
    @discord.command()
    async def daily(self, ctx):
        data = await get_data(ctx.author.id)
        if datetime.now().timestamp() - data['last_daily'] < 57600:
            await ctx.respond(
                f"You have already claimed your daily reward.\nYou can claim your next daily reward <t:{int(data['last_daily'] + 57600)}:R>.", ephemeral=True)
        else:
            reward = int(0.02 * (1 + data['daily_streak']/10) * data['balance'])
            if reward < 5:
                reward = 5
            last_daily = data['last_daily']
            if datetime.now().timestamp() - last_daily < 144000:
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
            await ctx.respond(
                f"You have claimed your daily reward of {numerize(reward * boost, 2)} cookies. You now have {data['balance']} cookies.")
    

def setup(bot):
    bot.add_cog(Gains(bot))