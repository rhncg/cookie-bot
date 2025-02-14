import discord
import random
from datetime import datetime
from numerize.numerize import numerize
from src.funcs.data import get_data, update_data, update_balance

async def try_steal(ctx, user):
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
    self_data['last_steal'] = datetime.now().timestamp()
    if chance == 1:
        self_data = await update_balance(self_data, amount)
        data = await update_balance(data, -amount)
        if data['boost_time'] > datetime.now().timestamp():
            boost = data['boost_level'] * 0.25 + 1
        else:
            boost = 1
        if data['steal_ping'] == True:
            await ctx.respond(f"You stole {numerize(amount * boost, 2)} cookies from {user.mention}.")
        else:
            await ctx.respond(f"You stole {numerize(amount * boost, 2)} cookies from {user.display_name}.")
    else:
        if data['steal_ping'] == True:
            await ctx.respond(f"You were caught! You failed to steal any cookies from {user.mention}.")
        else:
            await ctx.respond(f"You were caught! You failed to steal any cookies from {user.display_name}.")

    await update_data(data)
    await update_data(self_data)