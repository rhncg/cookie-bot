import discord
import os
from dotenv import load_dotenv
import aiosqlite
from src.funcs.db import get_db_connection
from src.bot_instance import bot

load_dotenv()
token = os.getenv('TOKEN')

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
            boost_level INTEGER DEFAULT 1,
            steal_ping BOOLEAN DEFAULT True
        )
        """)
        await conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")

cogs_list = [
    'admin',
    'bake',
    'gains',
    'leaderboard',
    'options',
    'profile',
    'shop',
    'updates'
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')
    
bot.run(token)