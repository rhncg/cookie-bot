import math

import discord
import os
from dotenv import load_dotenv
import aiosqlite
import asyncio
from datetime import datetime
import random

async def get_db_connection():
    if not hasattr(bot, 'db_conn'):
        bot.db_conn = await aiosqlite.connect("data.db")
    return bot.db_conn

bot = discord.Bot()

load_dotenv()
token = os.getenv('TOKEN')

baking_users = {}
bake_speed_upgrades = [60, 55, 50, 45, 40, 30, 20, 10]
oven_cap_upgrades = [1, 2, 3, 5, 8, 12, 16, 24, 32, 40, 50]

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
            await interaction.response.send_message("You cannot use this person's shop. Please use /shop and use the one provided.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Upgrade Bake Speed", style=discord.ButtonStyle.green)
    async def upgrade_bake_speed_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        upgrade_price = await calculate_next_upgrade(data, 'bake_speed')
        if data['balance'] >= upgrade_price:
            try:
                new_bake_speed = bake_speed_upgrades[bake_speed_upgrades.index(data['bake_speed']) + 1]
                data['balance'] -= upgrade_price
                data['bake_speed'] = new_bake_speed
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name=f'Your bake speed has been upgraded to {data["bake_speed"]} seconds', value="", inline=False)
                await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))
            except IndexError:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've reached the maximum bake speed.", value="", inline=False)
                await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your bake speed.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))

    @discord.ui.button(label="Upgrade Cookie Count", style=discord.ButtonStyle.green)
    async def upgrade_cookie_count_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        upgrade_price = await calculate_next_upgrade(data, 'oven_cap')
        if data['balance'] >= upgrade_price:
            try:
                new_oven_cap = oven_cap_upgrades[oven_cap_upgrades.index(data['oven_cap']) + 1]
                data['balance'] -= upgrade_price
                data['oven_cap'] = new_oven_cap
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name=f'Your cookie limit has been upgraded to {data["oven_cap"]} cookies', value="", inline=False)
                await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))
            except IndexError:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've reached the maximum oven_capacity.", value="", inline=False)
                await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your oven capacity.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))

    @discord.ui.button(label="Buy Idle Upgrade", style=discord.ButtonStyle.green)
    async def idle_upgrade_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        idle_upgrade_level = data['idle_upgrade_level']
        upgrade_price = await calculate_next_upgrade(data, 'idle_upgrade')
        if data ['balance'] >= upgrade_price:
            data['balance'] -= upgrade_price
            data['idle_upgrade_level'] = idle_upgrade_level + 1
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name=f'Your idle upgrade has been upgraded to level {data["idle_upgrade_level"]}.', value="", inline=False)
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
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've bought the ping upgrade!", value="", inline=False)
                await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))
            else:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You don't have enough cookies to buy the ping upgrade.", value="", inline=False)
                await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))
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
        data['balance'] += gamble_result
        await update_data(data)
        if gamble_result > 0:
            await interaction.response.edit_message(content=f"You gambled {self.amount} cookies and won {gamble_result} cookies! Your new balance is {data['balance']}.", embed=None, view=None)
        elif gamble_result < 0:
            await interaction.response.edit_message(content=f"You gambled {self.amount} cookies and lost {abs(gamble_result)} cookies. Your new balance is {data['balance']}.", embed=None, view=None)
        else:
            await interaction.response.edit_message(content=f"You gambled {self.amount} cookies and ended up with the same amount. Your balance is still {data['balance']}.", embed=None, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_callback(self, button, interaction):
        await interaction.response.edit_message(content="Gamble canceled.", embed=None, view=None)

async def get_data(user_id):
    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute("SELECT user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if row is None:
        await cursor.execute("INSERT INTO users (user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (user_id, 0, 1, 60, False, 0, 1, 0, 0))
        await conn.commit()
        await cursor.execute("SELECT user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp FROM users WHERE user_id = ?",
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
        'xp': row[8]
    }

    if data['last_active'] == 0:
        data['last_active'] = datetime.now().timestamp()
    time_elapsed = (datetime.now().timestamp() - data['last_active']) // 60
    if time_elapsed > 0 and data['idle_upgrade_level'] > 1:
        idle_upgrade = 1.1 ** (data['idle_upgrade_level'] - 1) - 1
        idle_cookies = int(time_elapsed * idle_upgrade)
        data['balance'] += idle_cookies
        data['last_active'] = datetime.now().timestamp()
        await update_data(data)
    else:
        data['last_active'] = datetime.now().timestamp()

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

async def make_shop_embed(user_id):
    data = await get_data(user_id)
    balance = data['balance']
    bake_speed = data['bake_speed']
    oven_cap = data['oven_cap']
    ping = data['ping']
    idle_upgrade_level = data['idle_upgrade_level']

    try:
        next_bake_upgrade = bake_speed_upgrades[bake_speed_upgrades.index(bake_speed) + 1]
        next_bake_upgrade = f"{next_bake_upgrade} seconds"
    except IndexError:
        next_bake_upgrade = "Max Level Reached"
    try:
        next_cookie_upgrade = oven_cap_upgrades[oven_cap_upgrades.index(oven_cap) + 1]
        next_cookie_upgrade = f"{next_cookie_upgrade} cookies"
    except IndexError:
        next_cookie_upgrade = oven_cap_upgrades[oven_cap_upgrades.index(oven_cap)]

    idle_upgrade = round(1.1 ** (idle_upgrade_level - 1) -1, 1)
    next_idle_upgrade = round((1.1 ** idle_upgrade_level)-1, 1)

    bake_upgrade_price = await calculate_next_upgrade(data, 'bake_speed')
    oven_upgrade_price = await calculate_next_upgrade(data, 'oven_cap')
    idle_upgrade_price = await calculate_next_upgrade(data, 'idle_upgrade')
    view = UpgradeView(user_id, data['ping'])
    user = await bot.fetch_user(user_id)

    embed = discord.Embed(title=f"{user.name}'s Shop", color=0x6b4f37)
    embed.add_field(name="Bake Speed Upgrade",
                    value=f"Current: {bake_speed} seconds\nNext: {next_bake_upgrade}\nCost: {bake_upgrade_price} cookies",
                    inline=True)
    embed.add_field(name="Oven Capacity Upgrade", value=f"Current: {oven_cap} cookies\nNext: {next_cookie_upgrade}\nCost: {oven_upgrade_price} cookies", inline=True)

    embed.add_field(name="Idle Upgrade", value=f"Current: {idle_upgrade} cookies per minute\nNext: {next_idle_upgrade} cookies per minute\nCost: {idle_upgrade_price} cookies", inline=True)

    if not ping == 0:
        embed.add_field(name="Ping When Done Baking", value=f"Owned")
    else:
        embed.add_field(name="Ping When Done Baking", value=f"Not owned\nCost: 10 cookies", inline=True)
    embed.add_field(name="Current Balance", value=f"{balance} cookies", inline=False)
    return embed

async def calculate_next_upgrade(data, upgrade_type):
    base_price = 5
    growth_rate = 1.15

    if upgrade_type == 'bake_speed':
        current_level = bake_speed_upgrades.index(data['bake_speed'])
    elif upgrade_type == 'oven_cap':
        current_level = oven_cap_upgrades.index(data['oven_cap'])
    elif upgrade_type == 'idle_upgrade':
        current_level = data['idle_upgrade_level']
        next_upgrade_price = int(5 * (1.15 ** current_level))
        next_upgrade_price = round(next_upgrade_price / 5) * 5
        return next_upgrade_price

    else:
        return 0

    next_upgrade_price = int(base_price * (growth_rate ** current_level))
    next_upgrade_price = round(next_upgrade_price / 5) * 5
    return next_upgrade_price

async def update_idle_balance(data):
    idle_upgrade = data['idle_upgrade']
    time_elapsed = (datetime.now().timestamp() - data['last_active']) // 60  # Minutes since last activity
    idle_cookies = int(time_elapsed * idle_upgrade)
    data['balance'] += idle_cookies
    data['last_active'] = datetime.now().timestamp()
    await update_data(data)

async def calculate_level(xp):
    return int(math.sqrt(xp)*0.5)

async def get_xp_bar_data(xp):
    level = await calculate_level(xp)
    current_level_xp = (level * 2) ** 2
    next_level_xp = ((level + 1) * 2) ** 2
    progress = (xp - current_level_xp) / (next_level_xp - current_level_xp) * 100
    bar = []
    for i in range(1,10):
        if i * 10 <= round(progress / 10) * 10:
            bar.append("⬜")
        else:
            bar.append("⬛")
    bar.append(f" ({progress:.0f}%)")
    bar = "".join(bar)
    return [current_level_xp, next_level_xp, progress, bar]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        conn = await get_db_connection()
        cursor = await conn.cursor()
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            oven_cap INTEGER DEFAULT 1,
            bake_speed INTEGER DEFAULT 1,
            ping INTEGER DEFAULT 0,
            last_active INTEGER DEFAULT 0,
            idle_upgrade_level INTEGER DEFAULT 1,
            last_daily INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0
        )
        """)
        await conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")

@bot.command()
async def ping(ctx):
    await ctx.respond(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def add_xp(ctx, amount):
    data = await get_data(ctx.author.id)
    data['xp'] += int(amount)
    await update_data(data)
    await ctx.respond(f'added {amount} xp')

@bot.command()
async def balance(ctx):
    data = await get_data(ctx.author.id)
    balance = data['balance']
    await ctx.respond(f'Your balance is {balance}')

@bot.command()
async def change_balance(ctx, amount: int):
    data = await get_data(ctx.author.id)
    data['balance'] += amount
    await update_data(data)
    await ctx.respond(f'Your balance has been updated to {data["balance"]}')

@bot.command()
async def bake(ctx):
    user_id = ctx.author.id
    data = await get_data(user_id)
    bake_speed = data['bake_speed']
    oven_cap = data['oven_cap']

    if user_id in baking_users:
        await ctx.respond(f'You are already baking cookies! Please wait until your current batch is done.')
        return

    current_time = datetime.now().timestamp()
    new_time = f'<t:{int(current_time + bake_speed)}:R>'

    baking_users[user_id] = True
    bake_message = await ctx.respond(f'You started baking {oven_cap} cookies. It will be done {new_time}')

    await asyncio.sleep(bake_speed - 1)
    data = await get_data(user_id)
    data['balance'] += oven_cap
    data['xp'] += oven_cap * 2
    await update_data(data)
    del baking_users[user_id]
    await bake_message.edit(content=f'You baked {oven_cap} cookies! Your new balance is {data["balance"]}.')

    await update_data(data)

    ping = data['ping']
    if ping == 2:
        await bake_message.channel.send(f"<@{user_id}>")

@bot.command()
async def shop(ctx):
    data = await get_data(ctx.author.id)
    embed = await make_shop_embed(ctx.author.id)
    await ctx.respond(embed=embed, view=UpgradeView(ctx.author.id, data['ping']))

@bot.command()
async def profile(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author
    data = await get_data(user.id)
    balance = data['balance']
    bake_speed = data['bake_speed']
    oven_cap = data['oven_cap']
    idle_upgrade_level = data['idle_upgrade_level']
    idle_upgrade = round(1.1 ** (idle_upgrade_level - 1) -1, 1)
    bar_data = await get_xp_bar_data(data['xp'])
    embed = discord.Embed(color=0x6b4f37)
    embed.add_field(name=f"Level {await calculate_level(data['xp'])} - {data['xp']} xp", value=bar_data[3], inline=False)
    embed.add_field(name=f"{bar_data[1] - bar_data[0]} xp to level {await calculate_level(data['xp']) + 1}", value="", inline=False)
    embed.add_field(name="Balance", value=f"{balance} cookies", inline=True)
    embed.add_field(name="Bake Speed", value=f"{bake_speed} seconds", inline=True)
    embed.add_field(name="Cookie Limit", value=f"{oven_cap} cookies", inline=True)
    embed.add_field(name="Idle Rate", value=f"{idle_upgrade} cookies per minute", inline=True)
    # embed.set_thumbnail(url=user.avatar.url)
    embed.set_author(name=f"{user.name}'s profile", icon_url=user.avatar.url)
    await ctx.respond(embed=embed)


@bot.command()
async def leaderboard(ctx):
    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute("SELECT user_id, balance FROM users ORDER BY balance DESC")
    rows = await cursor.fetchall()
    embed = discord.Embed(title="Leaderboard", color=0x6b4f37)
    for i, row in enumerate(rows):
        if row[1] == 0:
            continue
        embed.add_field(name="", value=f"{i+1}. <@{row[0]}> - {row[1]} cookies", inline=False)
    await ctx.respond(embed=embed)

@bot.command()
async def gamble(ctx, amount: int):
    data = await get_data(ctx.author.id)
    balance = data['balance']
    if balance < amount:
        await ctx.respond("You don't have enough cookies to gamble.")
        return
    if not amount > 0:
        await ctx.respond("You must gamble a positive amount of cookies.")
        return
    embed = discord.Embed(title=f"Are you sure you want to gamble {amount} cookies?", color=0x6b4f37)
    embed.add_field(name=f"You can either win or lose up to {amount} cookies.", value="", inline=False)
    embed.add_field(name="This action cannot be undone.", value="", inline=False)
    await ctx.respond(embed=embed, view=GambleConfirmationView(ctx.author.id, amount))

@bot.command()
async def daily(ctx):
    data = await get_data(ctx.author.id)
    if datetime.now().timestamp() - data['last_daily'] < 57600:
        await ctx.respond(f"You have already claimed your daily reward.\nYou can claim your next daily reward <t:{int(data['last_daily'] + 57600)}:R>.")
    else:
        reward = int(0.05 * data['balance'])
        if reward < 5:
            reward = 5
        data['balance'] += reward
        data['last_daily'] = datetime.now().timestamp()
        await update_data(data)
        await ctx.respond(f"You have claimed your daily reward of {reward} cookies. You now have {data['balance']} cookies.")

@bot.command()
async def reset_database(ctx):
    try:
        conn = await get_db_connection()
        cursor = await conn.cursor()

        # Drop the existing table
        await cursor.execute("DROP TABLE IF EXISTS users")
        await conn.commit()

        # Recreate the table
        await cursor.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                oven_cap INTEGER DEFAULT 1,
                bake_speed INTEGER DEFAULT 60,
                ping INTEGER DEFAULT 0,
                last_active INTEGER DEFAULT 0,
                idle_upgrade_level INTEGER DEFAULT 1,
                last_daily INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0
            )
            """)
        await conn.commit()

        await ctx.respond("database has been reset")
    except Exception as e:
        await ctx.respond(f"An error occurred while resetting the database: {e}")

bot.run(token)