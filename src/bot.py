import math
import discord
from discord.ext.pages import Paginator, Page
# from dotenv import load_dotenv
import aiosqlite
import asyncio
from datetime import datetime
import random
from numerize.numerize import numerize

async def get_db_connection():
    if not hasattr(bot, 'db_conn'):
        bot.db_conn = await aiosqlite.connect("data.db")
    return bot.db_conn

bot = discord.Bot()

# load_dotenv()
# token = os.getenv('TOKEN')

token = 'MTMyNjM5ODAzMDcxMDMxMzAxMg.GG-bmu.5Jq3gIuXkJwFQvDlKKPTcBwLUUwKq78JDEHcEc'

admins = [1066616669843243048]
baking_users = {}
bake_speed_upgrades = [60, 55, 50, 45, 40, 30, 20, 10]

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
    def __init__(self, user_id, ping, boost_time):
        super().__init__()
        self.user_id = user_id
        for child in self.children:
            if "Ping" in child.label and ping == 1:
                child.label = "Enable Ping Upgrade"
                child.style = discord.ButtonStyle.green
            elif "Ping" in child.label and ping == 2:
                child.label = "Disable Ping Upgrade"
                child.style = discord.ButtonStyle.red
        for child in self.children:
            if "Activate Boost" in child.label and boost_time + 900 > datetime.now().timestamp():
                child.disabled = True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Check if the user interacting matches the intended user
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You cannot use this person's shop. Please use </shop:1310001981066313738> and use the one provided.",
                ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Upgrade Bake Speed", style=discord.ButtonStyle.green, row=0)
    async def upgrade_bake_speed_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        upgrade_price = await calculate_next_upgrade_price(data, 'bake_speed')
        if data['balance'] >= upgrade_price:
            try:
                new_bake_speed = bake_speed_upgrades[bake_speed_upgrades.index(data['bake_speed']) + 1]
                data = await update_balance(data, -upgrade_price)
                data['bake_speed'] = new_bake_speed
                data['xp'] += 5
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name=f'Your bake speed has been upgraded to {data["bake_speed"]} seconds (+5 xp)', value="",
                                inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
            except IndexError:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've reached the maximum bake speed.", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your bake speed.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))

    @discord.ui.button(label="Upgrade Oven Capacity", style=discord.ButtonStyle.green, row=0)
    async def upgrade_cookie_count_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        upgrade_price = await calculate_next_upgrade_price(data, 'oven_cap')
        if data['balance'] >= upgrade_price:
            try:
                new_oven_cap = await calculate_next_upgrade(data, 'oven_cap')
                data = await update_balance(data, -upgrade_price)
                data['oven_cap'] = new_oven_cap
                data['xp'] += 5
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name=f'Your oven capacity has been upgraded to {data["oven_cap"]} cookies (+5 xp)', value="",
                                inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
            except IndexError:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've reached the maximum oven capacity.", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your oven capacity.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))

    @discord.ui.button(label="Buy Idle Upgrade", style=discord.ButtonStyle.green, row=0)
    async def idle_upgrade_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        for i in data:
            print(i)
        idle_upgrade_level = data['idle_upgrade_level']
        upgrade_price = await calculate_next_upgrade_price(data, 'idle_upgrade')
        if data['balance'] >= upgrade_price:
            data = await update_balance(data, -upgrade_price)
            data['idle_upgrade_level'] = idle_upgrade_level + 1
            data['xp'] += 5
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name=f'Your idle upgrade has been upgraded to level {data["idle_upgrade_level"]} (+5 xp)',
                            value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your idle upgrade.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))

    @discord.ui.button(label="Buy Ping Upgrade", style=discord.ButtonStyle.green, row=1)
    async def ping_upgrade_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        balance = data['balance']
        ping = data['ping']
        if ping == 0:
            if balance >= 10:
                data = await update_balance(data, -10)
                data['ping'] = 2
                data['xp'] += 5
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've bought the ping upgrade! (+5 xp)", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
            else:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You don't have enough cookies to buy the ping upgrade.", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        elif ping == 1:
            data['ping'] = 2
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You have enabled the ping upgrade.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        elif ping == 2:
            data['ping'] = 1
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You have disabled the ping upgrade.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))

    @discord.ui.button(label="Activate Boost", style=discord.ButtonStyle.green, row=1)
    async def boost_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        balance = data['balance']
        if balance >= await calculate_next_upgrade_price(data, 'boost_activate'):
            data = await update_balance(data, -1 * await calculate_next_upgrade_price(data, 'boost_activate'))
            data['boost_time'] = datetime.now().timestamp() + 900
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You have activated the boost.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to activate the boost.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
    
    @discord.ui.button(label="Upgrade Boost", style=discord.ButtonStyle.green, row=1)
    async def boost_upgrade_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        balance = data['balance']
        if balance >= await calculate_next_upgrade_price(data, 'boost_upgrade'):
            data = await update_balance(data, -1 * await calculate_next_upgrade_price(data, 'boost_upgrade'))
            data['boost_level'] += 1
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You have upgraded the boost.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade the boost.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))

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
        data = await update_balance(data, gamble_result)
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


async def get_data(user_id):
    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute(
        "SELECT user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp, last_steal, last_gamble, daily_streak, interactions, total_cookies, boost_time, boost_level FROM users WHERE user_id = ?",
        (user_id,))
    row = await cursor.fetchone()
    if row is None:
        await cursor.execute(
            "INSERT INTO users (user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp, last_steal, last_gamble, daily_streak, interactions, total_cookies, boost_time, boost_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, 0, 1, 60, False, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1))
        await conn.commit()
        await cursor.execute(
            "SELECT user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp, last_steal, last_gamble, daily_streak, interactions, total_cookies, boost_time, boost_level FROM users WHERE user_id = ?",
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
        'total_cookies': row[13],
        'boost_time': row[14],
        'boost_level': row[15]
    }

    if data['last_active'] == 0:
        data['last_active'] = datetime.now().timestamp()
    time_elapsed = (datetime.now().timestamp() - data['last_active']) // 60
    if time_elapsed > 0 and data['idle_upgrade_level'] > 1:
        idle_upgrade = 1.15 ** (data['idle_upgrade_level'] - 1) - 1
        idle_cookies = int(time_elapsed * idle_upgrade)
        data = await update_balance(data, idle_cookies)
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
    boost_upgrade_price = numerize(await calculate_next_upgrade_price(data, 'boost_upgrade'), 2)
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

    if data['boost_time'] + 900 > datetime.now().timestamp():
        active = f"Inactive (Cooldown ends <t:{int(data['boost_time'] + 900)}:R>)"
    if data['boost_time'] > datetime.now().timestamp():
        active = f"Active (Boost ends <t:{int(data['boost_time'])}:R>)"
    if data['boost_time'] + 900 < datetime.now().timestamp():
        active = "Inactive (Ready)"
        
    
    embed.add_field(name="Boost", value=f'''{active}\nCurrent Multiplier: {data['boost_level'] * 0.25 + 1}x\nUpgrade to: {(data['boost_level'] + 1) * 0.25 + 1}x\nBuy next level: {boost_upgrade_price} cookies\nActivate boost: {boost_activate_price} cookies''', inline=True)


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
        price = 0.4 * data['balance']
        if price < 10:
            price = 10
        return price
    else:
        return None

    next_upgrade_price = int(base_price * (growth_rate ** current_level))
    next_upgrade_price = round(next_upgrade_price / 5) * 5
    return next_upgrade_price

async def update_balance(data, amount):
    if data['boost_time'] > datetime.now().timestamp() and amount > 0:
        boost_amount = data['boost_level'] * 0.25 + 1
        data['balance'] += math.ceil(amount * boost_amount)
        data['total_cookies'] += math.ceil(amount * boost_amount) 
    else:
        data['balance'] += amount
        if amount > 0:
            data['total_cookies'] += amount

    return data

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


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.CustomActivity(name="cookies + gambling = profit"))
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
            interactions INTEGER DEFAULT 0,
            total_cookies INTEGER DEFAULT 0,
            boost_time INTEGER DEFAULT 0,
            boost_level INTEGER DEFAULT 1
        )
        """)
        await conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")

    '''
    print(bot.user.id)
    if bot.user.id == 1326398030710313012:
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
                            interactions INTEGER DEFAULT 0,
                            total_cookies INTEGER DEFAULT 0,
                            boost_time INTEGER DEFAULT 0,
                            boost_level INTEGER DEFAULT 1
                        )
                        """)
                    await conn.commit()

                    await ctx.respond("database has been reset")
                except Exception as e:
                    await ctx.respond(f"An error occurred while resetting the database: {e}")
            else:
                await ctx.respond("You do not have permission to use this command.", ephemeral=True)
    @bot.command()
    async def add_xp(ctx, amount):
        data = await get_data(ctx.author.id)
        data['xp'] += int(amount)
        await update_data(data)
        await ctx.respond(f'added {amount} xp')

    @bot.command()
    async def change_balance(ctx, amount: int):
        data = await get_data(ctx.author.id)
        data = await update_balance(data, amount)
        await update_data(data)
        await ctx.respond(f'Your balance has been updated to {data["balance"]}')
        print(amount, ctx.author.id)
    '''

@bot.command()
async def ping(ctx):
    await ctx.respond(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def balance(ctx):
    data = await get_data(ctx.author.id)
    balance = data['balance']
    await ctx.respond(f'You have {balance} cookies.')

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
    bake_message = await ctx.respond(f'You started baking {numerize(oven_cap, 2)} cookies. It will be done {new_time}', delete_after=bake_speed+5)

    await update_data(data)

    await asyncio.sleep(bake_speed - 1)
    data = await get_data(user_id)
    data = await update_balance(data, oven_cap)
    data['xp'] += round(oven_cap * 0.5)
    await update_data(data)
    del baking_users[user_id]
    await bake_message.edit(content=f'You baked {numerize(oven_cap, 2)} cookies! Your new balance is {numerize(data["balance"], 2)}. (+{numerize(round(oven_cap * 0.5), 2)} xp)')

    ping = data['ping']
    if ping == 2:
        ping_message = await bake_message.channel.send(f"<@{user_id}>")
        await asyncio.sleep(5)
        await ping_message.delete()

@bot.command()
async def shop(ctx):
    data = await get_data(ctx.author.id)
    embed = await make_shop_embed(ctx.author.id)
    await ctx.respond(embed=embed, view=UpgradeView(ctx.author.id, data['ping'], data['boost_time']))

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

@bot.command()
async def leaderboard(ctx):
    await ctx.defer()
    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute("SELECT user_id, balance FROM users ORDER BY balance DESC")
    rows = await cursor.fetchall()
    embed = discord.Embed(title="Leaderboard", color=0x6b4f37)
    for i, row in enumerate(rows):
        if row[1] == 0:
            continue
        embed.add_field(name="", value=f"{i + 1}. <@{row[0]}> - {numerize(row[1], 2)} cookies", inline=False)
    await ctx.respond(embed=embed, view=LeaderboardView(ctx))

gamble_users = []

@bot.command()
async def gamble(ctx, quick_selection: discord.Option(str, choices=['all', 'half']) = None, amount: int = None):
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
        amount = balance
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

@bot.command()
async def daily(ctx):
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
        await ctx.respond(
            f"You have claimed your daily reward of {reward} cookies. You now have {data['balance']} cookies.")

@bot.command()
async def steal(ctx, user: discord.User):
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
        await ctx.respond(f"You stole {numerize(amount, 2)} cookies from <@{user.id}>.")
    else:
        await ctx.respond(f"You were caught! You failed to steal any cookies from <@{user.id}>.")

    self_data['last_steal'] = datetime.now().timestamp()

    await update_data(data)
    await update_data(self_data)

@bot.command()
async def cooldowns(ctx):
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

@bot.command(description="Debug command for rohan")
async def debug(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author
    data = await get_data(user.id)
    if ctx.author.id in admins:
        embed = discord.Embed(title="Debug", color=0x6b4f37)
        embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=False)
        embed.add_field(name="Baking Users", value=f"{baking_users}", inline=False)
        embed.add_field(name="User Data", value=f"ID: {user.id}\n"
                                                f"Balance: {data['balance']}\n"
                                                f"Oven Cap: {data['oven_cap']}\n"
                                                f"Bake Speed: {data['bake_speed']}\n"
                                                f"Ping: {data['ping']}\n"
                                                f"Last Active: {data['last_active']}\n"
                                                f"Idle Upgrade Level: {data['idle_upgrade_level']}\n"
                                                f"Last Daily: {data['last_daily']}\n"
                                                f"XP: {data['xp']}\n"
                                                f"Last Steal: {data['last_steal']}\n"
                                                f"Last Gamble: {data['last_gamble']}\n"
                                                f"Daily Streak: {data['daily_streak']}\n"
                                                f"Interactions: {data['interactions']}\n"
                                                f"Total Cookies: {data['total_cookies']}\n"
                                                f"Boost Time: {data['boost_time']}\n"
                                                f"Boost Level: {data['boost_level']}", inline=False)
        embed.add_field(name="Current Unix Time", value=f"{datetime.now().timestamp()}", inline=False)
        embed.add_field(name="GambleConfViewActive:", value=f"{gamble_users}", inline=False)
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("Only admins can use this command.", ephemeral=True)

@bot.command(description="Send a suggestion to rohan.")
async def suggest(ctx, suggestion: str):
    await ctx.defer(ephemeral=True)
    for users in admins:
        user = await bot.fetch_user(users)
        await user.send(f"{ctx.author.name} has suggested: {suggestion}")
    await ctx.respond("Your suggestion has been sent to rohan.", ephemeral=True)

@bot.command()
async def updates(ctx):
    embed = discord.Embed(title="Updates", color=0x6b4f37)
    embed.add_field(name="Version", value="1.8.1", inline=False)
    embed.add_field(name="Completed", value="- Buffed Idle Upgrade (higher rate now)\n"
                                            "- Fixed stealing bug\n"
                                            "- Boosts are now available", inline=False)
    embed.add_field(name="Upcoming", value="- Drops\n"
                                           "- Leaderboard Improvements\n"
                                           "- Better Gambling\n"
                                           "- QOL stuff\n"
                                           "- Better XP scaling", inline=False)
    await ctx.respond(embed=embed)

@bot.command()
async def admin(ctx, cmd: str):
    if ctx.author.id in admins:
        cmd = cmd.lower()
        if cmd == "rsmsg":
            await ctx.send("Bot is restarting soon, please wait...")
            await ctx.respond("Sent", ephemeral=True)
        else:
            await ctx.respond("Invalid command.", ephemeral=True)
    else:
        await ctx.respond("You are not an admin.", ephemeral=True)




bot.run(token)
