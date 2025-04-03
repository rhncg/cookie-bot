import discord
import asyncio
from datetime import datetime
from src.funcs.globals import active_channels
from src.funcs.data import get_data, get_user_ids

async def log_active(ctx):
    channel = ctx.channel
    time = datetime.now().timestamp()
    active_channels[channel] = time
    
async def check_active():
    while True:
        for channel, time in list(active_channels.items()):
            if time + 150 < datetime.now().timestamp():
                active_channels.pop(channel, None)

        await asyncio.sleep(1)
        
async def fetch_users():
    ids = await get_user_ids()
    for user_id in ids:
        try:
            await get_data(user_id)
        except Exception as e:
            pass
    await asyncio.sleep(60)