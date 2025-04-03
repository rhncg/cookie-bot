import discord
import asyncio
from datetime import datetime
from src.funcs.globals import active_channels
from src.funcs.data import get_data, update_data, get_user_ids

async def run_background_tasks():
    asyncio.create_task(check_active())
    asyncio.create_task(fetch_users())

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
            data = await get_data(user_id)
            await update_data(data)
        except Exception as e:
            pass
    await asyncio.sleep(60)