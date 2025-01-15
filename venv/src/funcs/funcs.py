import math
import discord
from discord.ext.pages import Paginator, Page
# from dotenv import load_dotenv
import aiosqlite
import asyncio
from datetime import datetime
import random
from numerize.numerize import numerize
from src import bot

class LeaderboardView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx  # Save the context to fetch data later
        self.sort_by_level = False  # Track sorting state
        self.page = 1

    @discord.ui.button(label="Sort by Level", style=discord.ButtonStyle.green)
    async def sort_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.sort_by_level = not self.sort_by_level  # Toggle state
        button.label = "Sort by Cookies" if self.sort_by_level else "Sort by Level"

        # Fetch new data based on sorting
        conn = await get_db_connection()
        cursor = await conn.cursor()
        sort = "xp" if self.sort_by_level else "balance"
        await cursor.execute(f"SELECT user_id, {sort} FROM users ORDER BY {sort} DESC")
        rows = await cursor.fetchall()

        # Update the embed with new leaderboard data
        embed = discord.Embed(title="Leaderboard", color=0x6b4f37)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue
            if self.sort_by_level:
                label = f"Level {await calculate_level(row[1])} - {numerize(row[1], 2)} xp"
                embed.add_field(name="", value=f"{i + 1}. <@{row[0]}> - {label}", inline=False)
            else:
                label = f"{numerize(row[1], 2)} cookies"
                embed.add_field(name="", value=f"{i + 1}. <@{row[0]}> - {label}", inline=False)

        # Update the interaction message with the new data and view
        await interaction.response.edit_message(embed=embed, view=self)

class UpgradeView(discord.ui.View):
    def __init__(self, user_id, ping):
        super().__init__()
        self.user_id = user_id
        for child in self.children:
            if "Ping" in child.label and ping == 1:
                child.label = "Enable Ping Upgrade"
                child.style = discord.ButtonStyle.green
            elif "Ping" in child.label and ping == 2:
                child.label = "Disable Ping Upgrade"
                child.style = discord.ButtonStyle.red

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Check if the user interacting matches the intended user
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You cannot use this person's shop. Please use </shop:1310001981066313738> and use the one provided.",
                ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Upgrade Bake Speed", style=discord.ButtonStyle.green)
    async def upgrade_bake_speed_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        upgrade_price = await calculate_next_upgrade_price(data, 'bake_speed')
        if data['balance'] >= upgrade_price:
            try:
                new_bake_speed = bake_speed_upgrades[bake_speed_upgrades.index(data['bake_speed']) + 1]
                data['balance'] -= upgrade_price
                data['bake_speed'] = new_bake_speed
                data['xp'] += 5
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name=f'Your bake speed has been upgraded to {data["bake_speed"]} seconds (+5 xp)', value="",
                                inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping']))
            except IndexError:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've reached the maximum bake speed.", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your bake speed.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))

    @discord.ui.button(label="Upgrade Oven Capacity", style=discord.ButtonStyle.green)
    async def upgrade_cookie_count_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        upgrade_price = await calculate_next_upgrade_price(data, 'oven_cap')
        if data['balance'] >= upgrade_price:
            try:
                new_oven_cap = await calculate_next_upgrade(data, 'oven_cap')
                data['balance'] -= upgrade_price
                data['oven_cap'] = new_oven_cap
                data['xp'] += 5
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name=f'Your oven capacity has been upgraded to {data["oven_cap"]} cookies (+5 xp)', value="",
                                inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping']))
            except IndexError:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've reached the maximum oven capacity.", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your oven capacity.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))

    @discord.ui.button(label="Buy Idle Upgrade", style=discord.ButtonStyle.green)
    async def idle_upgrade_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        idle_upgrade_level = data['idle_upgrade_level']
        upgrade_price = await calculate_next_upgrade_price(data, 'idle_upgrade')
        if data['balance'] >= upgrade_price:
            data['balance'] -= upgrade_price
            data['idle_upgrade_level'] = idle_upgrade_level + 1
            data['xp'] += 5
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name=f'Your idle upgrade has been upgraded to level {data["idle_upgrade_level"]} (+5 xp)',
                            value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your idle upgrade.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))

    @discord.ui.button(label="Buy Ping Upgrade", style=discord.ButtonStyle.green)
    async def ping_upgrade_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        balance = data['balance']
        ping = data['ping']
        if ping == 0:
            if balance >= 10:
                data['balance'] -= 10
                data['ping'] = 2
                data['xp'] += 5
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've bought the ping upgrade! (+5 xp)", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping']))
            else:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You don't have enough cookies to buy the ping upgrade.", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping']))
        elif ping == 1:
            data['ping'] = 2
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You have enabled the ping upgrade.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))
        elif ping == 2:
            data['ping'] = 1
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You have disabled the ping upgrade.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

class GambleConfirmationView(discord.ui.View):
    def __init__(self, user_id, amount):
        super().__init__()
        self.user_id = user_id
        self.amount = amount

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def confirm_callback(self, button, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You cannot accept this person's gamble.", ephemeral=True)
            return
        data = await get_data(interaction.user.id)
        gamble_result = random.randint(-self.amount, self.amount)
        await update_balance(data, gamble_result)
        data['last_gamble'] = datetime.now().timestamp()
        balance = data['balance']
        await update_data(data)
        gamble_users.remove(interaction.user.id)
        if gamble_result > 0:
            await interaction.response.edit_message(
                content=f"You gambled {numerize(self.amount, 2)} cookies and won {numerize(gamble_result, 2)} cookies! Your new balance is {numerize(balance, 2)}.",
                embed=None, view=None)
        elif gamble_result < 0:
            await interaction.response.edit_message(
                content=f"You gambled {numerize(self.amount, 2)} cookies and lost {numerize(abs(gamble_result), 2)} cookies. Your new balance is {numerize(balance, 2)}.",
                embed=None, view=None)
        else:
            await interaction.response.edit_message(
                content=f"You gambled {numerize(self.amount, 2)} cookies and ended up with the same amount. Your balance is still {numerize(balance, 2)}.",
                embed=None, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_callback(self, button, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You cannot cancel this person's gamble.", ephemeral=True)
            return
        await interaction.response.edit_message(content="Gamble canceled.", embed=None, view=None)
        gamble_users.remove(interaction.user.id)

async def get_db_connection():
    if not hasattr(bot, 'db_conn'):
        bot.db_conn = await aiosqlite.connect("../data.db")
    return bot.db_conn

admins = [1066616669843243048]
baking_users = {}
bake_speed_upgrades = [60, 55, 50, 45, 40, 30, 20, 10]
gamble_users = []

async def get_data(user_id):
    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute(
        "SELECT user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp, last_steal, last_gamble, daily_streak, interactions, total_cookies FROM users WHERE user_id = ?",
        (user_id,))
    row = await cursor.fetchone()
    if row is None:
        await cursor.execute(
            "INSERT INTO users (user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp, last_steal, last_gamble, daily_streak, interactions, total_cookies) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, 0, 1, 60, False, 0, 1, 0, 0, 0, 0, 0, 0, 0))
        await conn.commit()
        await cursor.execute(
            "SELECT user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp, last_steal, last_gamble, daily_streak, interactions, total_cookies FROM users WHERE user_id = ?",
            (user_id,))
        row = await cursor.fetchone()

    data = {
        'user_id': row[0],
        'balance': row[1],
        'oven_cap': row[2],
        'bake_speed': row[3],
        'ping': row[4],
        'last_active': row[5],
        'idle_upgrade_level': row[6],
        'last_daily': row[7],
        'xp': row[8],
        'last_steal': row[9],
        'last_gamble': row[10],
        'daily_streak': row[11],
        'interactions': row[12],
        'total_cookies': row[13]
    }

    if data['last_active'] == 0:
        data['last_active'] = datetime.now().timestamp()
    time_elapsed = (datetime.now().timestamp() - data['last_active']) // 60
    if time_elapsed > 0 and data['idle_upgrade_level'] > 1:
        idle_upgrade = 1.1 ** (data['idle_upgrade_level'] - 1) - 1
        idle_cookies = int(time_elapsed * idle_upgrade)
        await update_balance(data, idle_cookies)
        data['last_active'] = datetime.now().timestamp()
        await update_data(data)
    else:
        data['last_active'] = datetime.now().timestamp()

    data['interactions'] += 1

    return data

async def update_data(data):
    user_id = data.pop('user_id', None)
    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
    values = list(data.values())
    values.append(user_id)

    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
    await conn.commit()

async def calculate_next_upgrade(data, upgrade_type, inverse=False):
    if inverse != True:
        if upgrade_type == 'bake_speed':
            return
        elif upgrade_type == 'oven_cap':
            next_upgrade = math.ceil(1.5 * data['oven_cap'])
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

async def make_shop_embed(user_id):
    data = await get_data(user_id)
    balance = data['balance']
    bake_speed = data['bake_speed']
    oven_cap = data['oven_cap']
    ping = data['ping']
    idle_upgrade_level = data['idle_upgrade_level']

    bake_upgrade_price = numerize(await calculate_next_upgrade_price(data, 'bake_speed'), 2)
    oven_upgrade_price = numerize(await calculate_next_upgrade_price(data, 'oven_cap'), 2)
    idle_upgrade_price = numerize(await calculate_next_upgrade_price(data, 'idle_upgrade'), 2)

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

    idle_upgrade = numerize(round(1.1 ** (idle_upgrade_level - 1) - 1, 1), 2)
    next_idle_upgrade = numerize(round((1.1 ** idle_upgrade_level) - 1, 1), 2)


    view = UpgradeView(user_id, data['ping'])
    user = await bot.fetch_user(user_id)



    embed = discord.Embed(color=0x6b4f37)
    embed.set_author(name=f"{user.name}'s shop", icon_url=user.display_avatar.url)
    embed.add_field(name="Bake Speed Upgrade",
                    value=f"Current: {bake_speed} seconds\nNext: {next_bake_upgrade}\nCost: {bake_upgrade_price} cookies",
                    inline=True)
    embed.add_field(name="Oven Capacity Upgrade",
                    value=f"Current: {numerize(oven_cap, 2)} cookies\nNext: {next_cookie_upgrade}\nCost: {oven_upgrade_price} cookies",
                    inline=True)

    embed.add_field(name="Idle Upgrade",
                    value=f"Current: {idle_upgrade} cookies per minute\nNext: {next_idle_upgrade} cookies per minute\nCost: {idle_upgrade_price} cookies",
                    inline=True)

    if not ping == 0:
        embed.add_field(name="Ping When Done Baking", value=f"Owned")
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

    else:
        return 0

    next_upgrade_price = int(base_price * (growth_rate ** current_level))
    next_upgrade_price = round(next_upgrade_price / 5) * 5
    return next_upgrade_price

async def update_balance(data, amount):
    data['balance'] += amount
    if amount > 0:
        data['total_cookies'] += amount

async def update_idle_balance(data):
    idle_upgrade = data['idle_upgrade']
    time_elapsed = (datetime.now().timestamp() - data['last_active']) // 60  # Minutes since last activity
    idle_cookies = int(time_elapsed * idle_upgrade)
    await update_balance(data, idle_cookies)

    data['last_active'] = datetime.now().timestamp()
    await update_data(data)

async def calculate_level(xp):
    return int(math.sqrt(xp) * 0.2)

async def get_xp_bar_data(xp):
    level = await calculate_level(xp)
    current_level_xp = (level * 5) ** 2
    next_level_xp = ((level + 1) * 5) ** 2
    progress = (xp - current_level_xp) / (next_level_xp - current_level_xp) * 100
    bar = []
    for i in range(1, 11):
        if i * 10 <= round(progress / 10) * 10:
            bar.append("⬜")
        else:
            bar.append("⬛")
    bar.append(f" ({progress:.0f}%)")
    bar = "".join(bar)
    return [current_level_xp, next_level_xp, progress, bar]