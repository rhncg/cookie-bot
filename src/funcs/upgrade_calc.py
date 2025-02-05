import discord
import math
from numerize.numerize import numerize
from datetime import datetime
from src.funcs.data import get_data
from src.bot_instance import bot
from src.funcs.globals import bake_speed_upgrades

async def make_shop_embed(user_id, bot):
    global bake_speed_upgrades
    data = await get_data(user_id)
    balance = data['balance']
    bake_speed = data['bake_speed']
    oven_cap = data['oven_cap']
    ping = data['ping']
    idle_upgrade_level = data['idle_upgrade_level']

    bake_upgrade_price = numerize(await calculate_next_upgrade_price(data, 'bake_speed'), 2)
    oven_upgrade_price = numerize(await calculate_next_upgrade_price(data, 'oven_cap'), 2)
    idle_upgrade_price = numerize(await calculate_next_upgrade_price(data, 'idle_upgrade'), 2)
    boost_upgrade_price = numerize(await calculate_next_upgrade_price(data, 'boost_upgrade'), 2)
    boost_speed_upgrade_price = numerize(await calculate_next_upgrade_price(data, 'boost_speed'), 2)
    boost_activate_price = numerize(await calculate_next_upgrade_price(data, 'boost_activate'), 2)

    try:
        next_bake_upgrade = numerize(bake_speed_upgrades[bake_speed_upgrades.index(bake_speed) + 1], 2)
        next_bake_upgrade = f"{next_bake_upgrade} seconds"
    except IndexError:
        next_bake_upgrade = "Max Level Reached"
        bake_upgrade_price = 0

    try:
        next_cookie_upgrade = numerize(await calculate_next_upgrade(data, 'oven_cap'), 2)
        next_cookie_upgrade = f"{next_cookie_upgrade} cookies"
    except IndexError:
        next_cookie_upgrade = "Max Level Reached"

    idle_upgrade = numerize(round(1.15 ** (idle_upgrade_level - 1) - 1, 1), 2)
    next_idle_upgrade = numerize(round((1.15 ** idle_upgrade_level) - 1, 1), 2)

    user = await bot.fetch_user(user_id)

    embed = discord.Embed(color=0x6b4f37)
    embed.set_author(name=f"{user.display_name}'s shop", icon_url=user.display_avatar.url)

    embed.add_field(name="Bake Speed Upgrade",
                    value=f"Current: {bake_speed} seconds\nNext: {next_bake_upgrade}\nCost: {bake_upgrade_price} cookies",
                    inline=True)
                    
    embed.add_field(name="Oven Capacity Upgrade",
                    value=f"Current: {numerize(oven_cap, 2)} cookies\nNext: {next_cookie_upgrade}\nCost: {oven_upgrade_price} cookies",
                    inline=True)

    embed.add_field(name="Idle Upgrade",
                    value=f"Current: {idle_upgrade} cookies per minute\nNext: {next_idle_upgrade} cookies per minute\nCost: {idle_upgrade_price} cookies",
                    inline=True)

    if data['boost_time'] + 900 > datetime.now().timestamp():
        active = f"Inactive (Cooldown ends <t:{int(data['boost_time'] + 900)}:R>)"
    if data['boost_time'] > datetime.now().timestamp():
        active = f"Active (Boost ends <t:{int(data['boost_time'])}:R>)"
    if data['boost_time'] + 900 < datetime.now().timestamp():
        active = "Inactive (Ready)"
        
    next_boost_multiplier = await calculate_next_upgrade(data, 'boost_level', False)
    next_boost_speed = await calculate_next_upgrade(data, 'boost_speed', False)
    
    
    embed.add_field(name="Boost", value=f"{active}\n"
                                        f"Current Multiplier: {data['boost_level'] * 0.25 + 1}x\n"
                                        f"Current Time: {data['boost_speed']} minutes\n"
                                        f"Upgrade multiplier to: {next_boost_multiplier}x for {boost_upgrade_price} cookies\n"
                                        f"Upgrade time to: {next_boost_speed} minutes for {boost_speed_upgrade_price} cookies\n"
                                        f"Activate boost: {boost_activate_price} cookies", inline=True)


    if not ping == 0:
        embed.add_field(name="Ping When Done Baking", value=f"Owned", inline=True)
    else:
        embed.add_field(name="Ping When Done Baking", value=f"Not owned\nCost: 10 cookies", inline=True)
    embed.add_field(name="Current Balance", value=f"{numerize(balance, 2)} cookies", inline=False)
    
    return embed

async def calculate_next_upgrade_price(data, upgrade_type):
    base_price = 5

    if upgrade_type == 'bake_speed':
        current_level = bake_speed_upgrades.index(data['bake_speed'])
        growth_rate = 2
    elif upgrade_type == 'oven_cap':
        current_level = await calculate_next_upgrade(data, 'oven_cap', True)
        growth_rate = 1.6
    elif upgrade_type == 'idle_upgrade':
        current_level = data['idle_upgrade_level']
        growth_rate = 1.3
    elif upgrade_type == 'boost_upgrade':
        base_price = 10
        current_level = data['boost_level']
        growth_rate = 45
    elif upgrade_type == 'boost_activate':
        price = 0.1 * data['balance']
        if price < 10:
            price = 10
        return price
    elif upgrade_type == 'boost_speed':
        base_price = 1000
        current_level = data['boost_speed'] / 5
        growth_rate = 1.4
        
    else:
        return None

    next_upgrade_price = int(base_price * (growth_rate ** current_level))
    next_upgrade_price = round(next_upgrade_price / 5) * 5
    return next_upgrade_price

async def calculate_next_upgrade(data, upgrade_type, inverse=False):
    if inverse != True:
        if upgrade_type == 'bake_speed':
            return
        elif upgrade_type == 'oven_cap':
            next_upgrade = math.ceil(1.5 * data['oven_cap'])
        elif upgrade_type == 'boost_level':
            next_upgrade = (data['boost_level'] + 1) * 0.25 + 1
        elif upgrade_type == 'boost_speed':
            next_upgrade = data['boost_speed'] + 5
        else:
            return
        return next_upgrade
    else:
        if upgrade_type == 'bake_speed':
            return
        elif upgrade_type == 'oven_cap':
            steps = math.ceil(math.log(data['oven_cap']) / math.log(1.5))
        else:
            return
        return steps