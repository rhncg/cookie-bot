import discord
from src.funcs.data import get_data, update_data, update_balance
from src.funcs.globals import baking_users
from funcs.numerize import numerize
from src.funcs.drops import try_drop
from datetime import datetime
from funcs.log_server import log_active
import asyncio

class Bake(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description="Bake some cookies")
    async def bake(self, ctx):
        await log_active(ctx)
        
        user_id = ctx.author.id
        data = await get_data(user_id)
        bake_speed = data['bake_speed']
        oven_cap = data['oven_cap']

        if user_id in baking_users:
            await ctx.respond(f'You are already baking cookies! Please wait until your current batch is done.', ephemeral=True)
            return

        await try_drop(ctx.channel)

        current_time = datetime.now().timestamp()
        new_time = f'<t:{int(current_time + bake_speed)}:R>'

        baking_users[user_id] = True
        
        if data['boost_time'] > datetime.now().timestamp():
            boost = data['boost_level'] * 0.25 + 1
        else:
            boost = 1
        
        s = "s" if oven_cap * boost != 1 else "" 
        bake_message = await ctx.respond(f'You started baking **{numerize(oven_cap, 2)} cookie{s}**. They will be done {new_time}', delete_after=bake_speed+5)

        await update_data(data)

        try:
            await asyncio.sleep(bake_speed - 1)
            data = await get_data(user_id)
            data = await update_balance(data, oven_cap)
            data['xp'] += round(oven_cap * 0.5)
            await update_data(data)
        finally:
            del baking_users[user_id]
            
        s = "s" if oven_cap * boost != 1 else "" 
        await bake_message.edit(content=f'You baked **{numerize(oven_cap * boost, 2)} cookie{s}**! You now have **{numerize(data["balance"], 2)} cookies**. (+{numerize(round(oven_cap * 0.5), 2)} xp)')

        ping = data['ping']
        if ping == 2:
            ping_message = await bake_message.channel.send(f"<@{user_id}>")
            await asyncio.sleep(5)
            await ping_message.delete()

def setup(bot):
    bot.add_cog(Bake(bot))