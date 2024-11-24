import discord
import os
from dotenv import load_dotenv
import aiosqlite
import asyncio
from datetime import datetime

# Create a single persistent database connection
async def get_db_connection():
    # Only open the connection once and reuse it for the entire bot lifecycle
    if not hasattr(bot, 'db_conn'):
        bot.db_conn = await aiosqlite.connect("data.db")
    return bot.db_conn

bot = discord.Bot()

load_dotenv()
token = os.getenv('TOKEN')

baking_users = {}
bake_speed_upgrades = [60, 55, 50, 45, 40, 30, 20, 10, 5, 2, 1]
cookie_limit_upgrades = [1, 2, 3, 5, 8, 12, 16, 24, 32, 40, 50]

class UpgradeView(discord.ui.View):
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
                embed.add_field(name=f'Your bake speed has been upgraded to {data["bake_speed"]}', value="", inline=False)
                await interaction.response.edit_message(embed=embed, view=UpgradeView())
            except IndexError:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've reached the maximum bake speed.", value="", inline=False)
                await interaction.response.edit_message(embed=embed, view=UpgradeView())
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your bake speed.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView())

    @discord.ui.button(label="Upgrade Cookie Count", style=discord.ButtonStyle.green)
    async def upgrade_cookie_count_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        upgrade_price = await calculate_next_upgrade(data, 'cookie_limit')
        if data['balance'] >= upgrade_price:
            try:
                new_cookie_limit = cookie_limit_upgrades[cookie_limit_upgrades.index(data['cookie_limit']) + 1]
                data['balance'] -= upgrade_price
                data['cookie_limit'] = new_cookie_limit
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name=f'Your cookie limit has been upgraded to {data["cookie_limit"]}', value="", inline=False)
                await interaction.response.edit_message(embed=embed, view=UpgradeView())
            except IndexError:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've reached the maximum cookie limit.", value="", inline=False)
                await interaction.response.edit_message(embed=embed, view=UpgradeView())
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your cookie limit.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView())
        


async def get_data(user_id):
    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute("SELECT user_id, balance, cookie_limit, bake_speed FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if row is None:
        # Insert a new user if not found
        await cursor.execute("INSERT INTO users (user_id, balance, cookie_limit, bake_speed) VALUES (?, ?, ?, ?)",
                             (user_id, 0, 1, 60))
        await conn.commit()
        await cursor.execute("SELECT user_id, balance, cookie_limit, bake_speed FROM users WHERE user_id = ?",
                             (user_id,))
        row = await cursor.fetchone()

    # Map the tuple to a dictionary using the column names
    return {
        'user_id': row[0],
        'balance': row[1],
        'cookie_limit': row[2],
        'bake_speed': row[3]
    }

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
    cookie_limit = data['cookie_limit']
    next_bake_upgrade = bake_speed_upgrades[bake_speed_upgrades.index(bake_speed) + 1]
    next_cookie_upgrade = cookie_limit_upgrades[cookie_limit_upgrades.index(cookie_limit) + 1]
    bake_upgrade_price = await calculate_next_upgrade(data, 'bake_speed')
    cookie_upgrade_price = await calculate_next_upgrade(data, 'cookie_limit')

    embed = discord.Embed(title="Shop", color=0x6b4f37)
    embed.add_field(name="Bake Speed Upgrade",
                    value=f"Current: {bake_speed} seconds\nNext: {next_bake_upgrade} seconds\nCost: {bake_upgrade_price} cookies",
                    inline=True)
    embed.add_field(name="Cookie Upgrade", value=f"Current: {cookie_limit}\nNext: {next_cookie_upgrade}\nCost: {cookie_upgrade_price} cookies", inline=True)
    embed.add_field(name="Current Balance", value=f"{balance} cookies", inline=False)
    return embed

async def calculate_next_upgrade(data, upgrade_type):
    if upgrade_type == 'bake_speed':
        next_upgrade = int(2 ** (bake_speed_upgrades.index(data['bake_speed']) + 1))
    elif upgrade_type == 'cookie_limit':
        next_upgrade = int(2 ** (cookie_limit_upgrades.index(data['cookie_limit']) + 1))
    else:
        return 0
    return next_upgrade

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
            cookie_limit INTEGER DEFAULT 1,
            bake_speed INTEGER DEFAULT 1
        )
        """)
        await conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")

@bot.command()
async def ping(ctx):
    await ctx.respond(f'Pong! {round(bot.latency * 1000)}ms')

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

# Baking cookies command (example logic)
@bot.command()
async def bake(ctx):
    user_id = ctx.author.id
    data = await get_data(user_id)
    bake_speed = data['bake_speed']
    cookie_limit = data['cookie_limit']

    if user_id in baking_users:
        await ctx.respond(f'You are already baking cookies! Please wait until your current batch is done.')
        return

    current_time = datetime.now().timestamp()
    new_time = f'<t:{int(current_time + bake_speed)}:R>'

        # Start baking process
    baking_users[user_id] = True  # Mark the user as baking
    bake_message = await ctx.respond(f'You started baking {cookie_limit} cookies. It will be done {new_time}')

    # Wait for bake_speed seconds
    await asyncio.sleep(bake_speed - 1)

    # After baking, add cookies to balance
    data['balance'] += cookie_limit
    await update_data(data)

    # Finish baking and update user state
    del baking_users[user_id]  # Mark the user as not baking anymore
    await bake_message.edit(content=f'You baked {cookie_limit} cookies! Your new balance is {data["balance"]}.')

@bot.command()
async def shop(ctx):
    embed = await make_shop_embed(ctx.author.id)
    await ctx.respond(embed=embed, view=UpgradeView())

bot.run(token)