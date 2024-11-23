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
# Retrieve data or create a new entry if not found
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

# Update user data in the database
async def update_data(data):
    user_id = data.pop('user_id', None)
    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
    values = list(data.values())
    values.append(user_id)

    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
    await conn.commit()

# Initialize database schema if not exists
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

# Basic ping command
@bot.command()
async def ping(ctx):
    await ctx.respond(f'Pong! {round(bot.latency * 1000)}ms')

# Show user balance
@bot.command()
async def balance(ctx):
    data = await get_data(ctx.author.id)
    balance = data['balance']
    await ctx.respond(f'Your balance is {balance}')

# Change user balance
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
    new_time = f'<t:{int(current_time + bake_speed + 1)}:R>'

        # Start baking process
    baking_users[user_id] = True  # Mark the user as baking
    bake_message = await ctx.respond(f'You started baking {cookie_limit} cookies. It will be done {new_time}')

    # Wait for bake_speed seconds
    await asyncio.sleep(bake_speed)

    # After baking, add cookies to balance
    data['balance'] += cookie_limit
    await update_data(data)

    # Finish baking and update user state
    del baking_users[user_id]  # Mark the user as not baking anymore
    await bake_message.edit(content=f'You baked {cookie_limit} cookies! Your new balance is {data["balance"]}.')


bot.run(token)