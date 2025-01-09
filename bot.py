import math
import discord
import os
from attr import dataclass
# from dotenv import load_dotenv
import aiosqlite
import asyncio
from datetime import datetime
import random


async def get_db_connection():
    if not hasattr(bot, 'db_conn'):
        bot.db_conn = await aiosqlite.connect("data.db")
    return bot.db_conn

bot = discord.Bot()

# load_dotenv()
# token = os.getenv('TOKEN')

token = 'MTMyNjM5ODAzMDcxMDMxMzAxMg.GJ1W6e.Y3GekmmRBoYrzRU5NRrHXfMrmp6_jIUapqcHWU'

admins = [1066616669843243048]
baking_users = {}
bake_speed_upgrades = [60, 55, 50, 45, 40, 30, 20, 10]

class LeaderboardView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx  # Save the context to fetch data later
        self.sort_by_level = False  # Track sorting state

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
                label = f"Level {await calculate_level(row[1])} - {row[1]} xp"
                embed.add_field(name="", value=f"{i + 1}. <@{row[0]}> - {label}", inline=False)
            else:
                label = f"{row[1]} cookies"
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
                embed.add_field(name=f'Your bake speed has been upgraded to {data["bake_speed"]} seconds', value="",
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
                embed.add_field(name=f'Your oven capacity has been upgraded to {data["oven_cap"]} cookies', value="",
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
            embed.add_field(name=f'Your idle upgrade has been upgraded to level {data["idle_upgrade_level"]}.',
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
                embed.add_field(name="You've bought the ping upgrade!", value="", inline=False)
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
        data['balance'] += gamble_result
        data['last_gamble'] = datetime.now().timestamp()
        await update_data(data)
        del gamble_users[self.user_id]
        if gamble_result > 0:
            await interaction.response.edit_message(
                content=f"You gambled {self.amount} cookies and won {gamble_result} cookies! Your new balance is {data['balance']}.",
                embed=None, view=None)
        elif gamble_result < 0:
            await interaction.response.edit_message(
                content=f"You gambled {self.amount} cookies and lost {abs(gamble_result)} cookies. Your new balance is {data['balance']}.",
                embed=None, view=None)
        else:
            await interaction.response.edit_message(
                content=f"You gambled {self.amount} cookies and ended up with the same amount. Your balance is still {data['balance']}.",
                embed=None, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_callback(self, button, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You cannot cancel this person's gamble.", ephemeral=True)
            return
        await interaction.response.edit_message(content="Gamble canceled.", embed=None, view=None)
        del gamble_users[self.user_id]


async def get_data(user_id):
    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute(
        "SELECT user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp, last_steal, last_gamble, daily_streak, interactions FROM users WHERE user_id = ?",
        (user_id,))
    row = await cursor.fetchone()
    if row is None:
        await cursor.execute(
            "INSERT INTO users (user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp, last_steal, last_gamble, daily_streak, interactions) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, 0, 1, 60, False, 0, 1, 0, 0, 0, 0, 0, 0))
        await conn.commit()
        await cursor.execute(
            "SELECT user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp, last_steal, last_gamble, daily_streak, interactions FROM users WHERE user_id = ?",
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
        'interactions': row[12]
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

    try:
        next_bake_upgrade = bake_speed_upgrades[bake_speed_upgrades.index(bake_speed) + 1]
        next_bake_upgrade = f"{next_bake_upgrade} seconds"
    except IndexError:
        next_bake_upgrade = "Max Level Reached"
    try:
        next_cookie_upgrade = await calculate_next_upgrade(data, 'oven_cap')
        next_cookie_upgrade = f"{next_cookie_upgrade} cookies"
    except IndexError:
        next_cookie_upgrade = "Max Level Reached"

    idle_upgrade = round(1.1 ** (idle_upgrade_level - 1) - 1, 1)
    next_idle_upgrade = round((1.1 ** idle_upgrade_level) - 1, 1)

    bake_upgrade_price = await calculate_next_upgrade_price(data, 'bake_speed')
    oven_upgrade_price = await calculate_next_upgrade_price(data, 'oven_cap')
    idle_upgrade_price = await calculate_next_upgrade_price(data, 'idle_upgrade')
    view = UpgradeView(user_id, data['ping'])
    user = await bot.fetch_user(user_id)

    embed = discord.Embed(color=0x6b4f37)
    embed.set_author(name=f"{user.name}'s shop")
    embed.add_field(name="Bake Speed Upgrade",
                    value=f"Current: {bake_speed} seconds\nNext: {next_bake_upgrade}\nCost: {bake_upgrade_price} cookies",
                    inline=True)
    embed.add_field(name="Oven Capacity Upgrade",
                    value=f"Current: {oven_cap} cookies\nNext: {next_cookie_upgrade}\nCost: {oven_upgrade_price} cookies",
                    inline=True)

    embed.add_field(name="Idle Upgrade",
                    value=f"Current: {idle_upgrade} cookies per minute\nNext: {next_idle_upgrade} cookies per minute\nCost: {idle_upgrade_price} cookies",
                    inline=True)

    if not ping == 0:
        embed.add_field(name="Ping When Done Baking", value=f"Owned")
    else:
        embed.add_field(name="Ping When Done Baking", value=f"Not owned\nCost: 10 cookies", inline=True)
    embed.add_field(name="Current Balance", value=f"{balance} cookies", inline=False)
    return embed


async def calculate_next_upgrade_price(data, upgrade_type):
    base_price = 5
    growth_rate = 1.15

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


async def update_idle_balance(data):
    idle_upgrade = data['idle_upgrade']
    time_elapsed = (datetime.now().timestamp() - data['last_active']) // 60  # Minutes since last activity
    idle_cookies = int(time_elapsed * idle_upgrade)
    data['balance'] += idle_cookies
    data['last_active'] = datetime.now().timestamp()
    await update_data(data)


async def calculate_level(xp):
    return int(math.sqrt(xp) * 0.5)


async def get_xp_bar_data(xp):
    level = await calculate_level(xp)
    current_level_xp = (level * 2) ** 2
    next_level_xp = ((level + 1) * 2) ** 2
    progress = (xp - current_level_xp) / (next_level_xp - current_level_xp) * 100
    bar = []
    for i in range(1, 11):
        if i * 10 <= round(progress / 10) * 10:
            bar.append("â¬")
        else:
            bar.append("â¬")
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
            xp INTEGER DEFAULT 0,
            last_steal INTEGER DEFAULT 0,
            last_gamble INTEGER DEFAULT 0,
            daily_streak INTEGER DEFAULT 0,
            interactions INTEGER DEFAULT 0
        )
        """)
        await conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")


@bot.command()
async def ping(ctx):
    await ctx.respond(f'Pong! {round(bot.latency * 1000)}ms')


'''
@bot.command()
async def add_xp(ctx, amount):
    data = await get_data(ctx.author.id)
    data['xp'] += int(amount)
    await update_data(data)
    await ctx.respond(f'added {amount} xp')
'''


@bot.command()
async def balance(ctx):
    data = await get_data(ctx.author.id)
    balance = data['balance']
    await ctx.respond(f'Your balance is {balance}')


'''
@bot.command()
async def change_balance(ctx, amount: int):
    data = await get_data(ctx.author.id)
    data['balance'] += amount
    await update_data(data)
    await ctx.respond(f'Your balance has been updated to {data["balance"]}')
'''


@bot.command()
async def bake(ctx):
    user_id = ctx.author.id
    data = await get_data(user_id)
    bake_speed = data['bake_speed']
    oven_cap = data['oven_cap']

    if user_id in baking_users:
        await ctx.respond(f'You are already baking cookies! Please wait until your current batch is done.',
                          ephemeral=True)
        return

    current_time = datetime.now().timestamp()
    new_time = f'<t:{int(current_time + bake_speed)}:R>'

    baking_users[user_id] = True
    bake_message = await ctx.respond(f'You started baking {oven_cap} cookies. It will be done {new_time}', delete_after=bake_speed+5)

    await update_data(data)

    await asyncio.sleep(bake_speed - 1)
    data = await get_data(user_id)
    data['balance'] += oven_cap
    data['xp'] += oven_cap * 2
    await update_data(data)
    del baking_users[user_id]
    await bake_message.edit(content=f'You baked {oven_cap} cookies! Your new balance is {data["balance"]}.')

    ping = data['ping']
    if ping == 2:
        ping_message = await bake_message.channel.send(f"<@{user_id}>")
        await asyncio.sleep(5)
        await ping_message.delete()


@bot.command()
async def shop(ctx):
    data = await get_data(ctx.author.id)
    embed = await make_shop_embed(ctx.author.id)
    await ctx.respond(embed=embed, view=UpgradeView(ctx.author.id, data['ping']))


@bot.command()
async def profile(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author
    try:
        data = await get_data(user.id)
        balance = data['balance']
        bake_speed = data['bake_speed']
        oven_cap = data['oven_cap']
        idle_upgrade_level = data['idle_upgrade_level']
        idle_upgrade = round(1.1 ** (idle_upgrade_level - 1) - 1, 1)
        bar_data = await get_xp_bar_data(data['xp'])
        embed = discord.Embed(color=0x6b4f37)
        embed.add_field(name=f"Level {await calculate_level(data['xp'])} - {data['xp']} xp", value=bar_data[3],
                        inline=False)
        embed.add_field(name=f"{bar_data[1] - bar_data[0]} xp to level {await calculate_level(data['xp']) + 1}",
                        value="", inline=False)
        embed.add_field(name="Balance", value=f"{balance} cookies", inline=True)
        embed.add_field(name="Bake Speed", value=f"{bake_speed} seconds", inline=True)
        embed.add_field(name="Cookie Limit", value=f"{oven_cap} cookies", inline=True)
        embed.add_field(name="Idle Rate", value=f"{idle_upgrade} cookies per minute", inline=True)
        embed.set_author(name=f"{user.name}'s profile")
        await ctx.respond(embed=embed)
    except Exception as e:
        await ctx.respond(f"That isn't a valid user. {e}", ephemeral=True)


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
        embed.add_field(name="", value=f"{i + 1}. <@{row[0]}> - {row[1]} cookies", inline=False)
    await ctx.respond(embed=embed, view=LeaderboardView(ctx))

gamble_users = []

@bot.command()
async def gamble(ctx, amount: int):
    data = await get_data(ctx.author.id)
    last_gamble = data['last_gamble']
    balance = data['balance']
    if datetime.now().timestamp() - last_gamble < 120:
        await ctx.respond(
            f"You have already gambled recently.\nYou can gamble again <t:{int(last_gamble + 600)}:R>.", ephemeral=True)
        return
    if balance < amount:
        await ctx.respond("You don't have enough cookies to gamble.")
        return
    if not amount > 0:
        await ctx.respond("You must gamble a positive amount of cookies.")
        return

    gamble_users.append(ctx.author.id)

    embed = discord.Embed(title=f"Are you sure you want to gamble {amount} cookies?", color=0x6b4f37)
    embed.add_field(name=f"You can either win or lose up to {amount} cookies.", value="", inline=False)
    embed.add_field(name="This action cannot be undone.", value="", inline=False)
    await ctx.respond(embed=embed, view=GambleConfirmationView(ctx.author.id, amount))


@bot.command()
async def daily(ctx):
    data = await get_data(ctx.author.id)
    if datetime.now().timestamp() - data['last_daily'] < 57600:
        await ctx.respond(
            f"You have already claimed your daily reward.\nYou can claim your next daily reward <t:{int(data['last_daily'] + 57600)}:R>.")
    else:
        reward = int(0.02 * (1 + data['daily_streak']/10) * data['balance'])
        if reward < 5:
            reward = 5
        last_daily = data['last_daily']
        if datetime.now().timestamp() - last_daily < 144000:
            data['daily_streak'] += 1
        else:
            data['daily_streak'] = 0

        data['balance'] += reward
        data['last_daily'] = datetime.now().timestamp()
        await update_data(data)
        await ctx.respond(
            f"You have claimed your daily reward of {reward} cookies. You now have {data['balance']} cookies.")

@bot.command()
async def steal(ctx, user: discord.User):
    if user.id == ctx.author.id:
        await ctx.respond("You cannot steal from yourself.", ephemeral=True)
        return
    data = await get_data(user.id)
    balance = data['balance']

    user_data = await get_data(ctx.author.id)
    last_steal = user_data['last_steal']
    if datetime.now().timestamp() - last_steal < 1800:
        await ctx.respond(
            f"You have already attempted to steal from someone recently.\nYou can steal again <t:{int(last_steal + 1800)}:R>.", ephemeral=True)
        return

    if int(balance * 0.2) < 1:
        await ctx.respond("That user doesn't have enough cookies.", ephemeral=True)
        return
    if int(balance * 0.2) > user_data['balance'] * 3:
        await ctx.respond("That user has too many cookies for you to steal from.", ephemeral=True)
        return
    amount = random.randint(1, int(balance * 0.2))
    chance = random.randint(1, 3)
    if chance == 1:
        data['balance'] -= amount
        user_data['balance'] += amount
        await ctx.respond(f"You stole {amount} cookies from <@{user.id}>.")
    else:
        await ctx.respond(f"You were caught! You failed to steal any cookies from <@{user.id}>.")

    user_data['last_steal'] = datetime.now().timestamp()

    await update_data(data)
    await update_data(user_data)

'''
@bot.command()
async def reset_database(ctx):
    if ctx.author.id in admins:
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
                    xp INTEGER DEFAULT 0,
                    last_steal INTEGER DEFAULT 0,
                    last_gamble INTEGER DEFAULT 0,
                    daily_streak INTEGER DEFAULT 0,
                    interactions INTEGER DEFAULT 0
                )
                """)
            await conn.commit()

            await ctx.respond("database has been reset")
        except Exception as e:
            await ctx.respond(f"An error occurred while resetting the database: {e}")
    else:
        await ctx.respond("You do not have permission to use this command.", ephemeral=True)
'''
bot.run(token)