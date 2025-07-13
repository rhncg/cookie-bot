import aiosqlite
from src.bot_instance import bot

async def get_db_connection():
    if not hasattr(bot, 'db_conn'):
        bot.db_conn = await aiosqlite.connect("src/data.db")
    return bot.db_conn

