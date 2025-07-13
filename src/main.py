import discord
import os
from dotenv import load_dotenv
from src.funcs.db import get_db_connection
from src.bot_instance import bot
from src.funcs.background import run_background_tasks
from funcs.globals import version

load_dotenv()
token = os.getenv('TOKEN')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.CustomActivity(name="cookies + gambling = profit"))
    print(f'Bot is ready (v{version})')
    try:
        conn = await get_db_connection()
        cursor = await conn.cursor()
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance TEXT DEFAULT 0,
            oven_cap INTEGER DEFAULT 1,
            bake_speed INTEGER DEFAULT 1,
            ping INTEGER DEFAULT 0,
            last_active INTEGER DEFAULT 0,
            idle_upgrade_level INTEGER DEFAULT 1,
            last_daily INTEGER DEFAULT 0,
            xp TEXT DEFAULT 0,
            last_steal INTEGER DEFAULT 0,
            last_gamble INTEGER DEFAULT 0,
            daily_streak INTEGER DEFAULT 0,
            interactions INTEGER DEFAULT 0,
            total_cookies TEXT DEFAULT 0,
            boost_time INTEGER DEFAULT 0,
            boost_level INTEGER DEFAULT 1,
            steal_ping BOOLEAN DEFAULT True,
            boost_speed INTEGER DEFAULT 10,
            options TEXT DEFAULT '{"steal_ping": true, "gamble_confirmation": true, "profile_color": "default"}'
        )
        """)
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            user_id INTEGER PRIMARY KEY,
            bake_quest INTEGER DEFAULT 0
        )
        """)
        await conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
        
    await run_background_tasks()
    
cogs_list = [
    'admin',
    'bake',
    'gains',
    'leaderboard',
    'options',
    'profile',
    'shop',
    'updates',
    'quests'
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')
    
bot.run(token)