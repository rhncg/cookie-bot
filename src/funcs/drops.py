import discord
import random
from src.views.drop_display import DropView

async def try_drop(channel, force = False):
    drop_chance = random.randint(1, 20)
    
    if force:
        drop_chance = 1
        
    if drop_chance == 1:
        embed = discord.Embed(title="Incoming Drop", color=0x6b4f37)
        embed.add_field(name="Claim the drop before everyone else for a reward", value="You will earn 10% of your balance", inline=False)
        await channel.send(embed=embed, view=DropView())