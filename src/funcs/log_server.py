import discord
import asyncio
from datetime import datetime
from src.funcs.globals import active_channels

async def log_active(ctx):
    channel = ctx.channel.id
    time = datetime.now().timestamp()
    active_channels[channel] = time
    
async def check_active():
    while True:
        for channel, time in list(active_channels.items()):
            if time + 150 < datetime.now().timestamp():
                active_channels.pop(channel, None)
        
        await asyncio.sleep(150)