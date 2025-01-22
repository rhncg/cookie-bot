import math
import discord
from discord.ext.pages import Paginator, Page
import aiosqlite
import asyncio
from datetime import datetime
import random
from numerize.numerize import numerize

class Bot(discord.Bot):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

bot = Bot()

