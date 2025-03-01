import discord
from src.funcs.db import get_db_connection

async def get_quests(data):
    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute(
        "SELECT user_id, bake_quest FROM quests WHERE user_id = ?",
        (data['user_id'],))
    row = await cursor.fetchone()
    if row is None:
        await cursor.execute(
            "INSERT INTO quests (user_id, bake_quest) VALUES (?, ?)",
            (data['user_id'], 0))
        await conn.commit()
        await cursor.execute(
        "SELECT user_id, bake_quest FROM quests WHERE user_id = ?",
        (data['user_id'],))
        row = await cursor.fetchone()

    quest_data = {
        'user_id': row[0],
        'bake_quest': row[1]
    }
    
    return quest_data

async def make_quest_embed(data):
    embed = discord.Embed(title="Quests", color=0x6b4f37)
    quests = await get_quests(data)
    embed.add_field(name="Bake Quest", value=quests['bake_quest'], inline=False)
    
    return embed