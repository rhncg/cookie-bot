import discord
import asyncio
from datetime import datetime
from numerize.numerize import numerize
from src.funcs.data import get_data, update_balance, update_data
from src.bot_instance import bot

class DropView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.claimed_users = []
        
    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green)
    async def claim_callback(self, button, interaction):
        
        self.claimed_users.append(interaction.user.id)
        await asyncio.sleep(1)
        
        first_user = await bot.fetch_user(self.claimed_users[0])
        
        if interaction.user == first_user:
            embed = discord.Embed(title=f"Drop Claimed by {first_user.display_name}", color=0x6b4f37)
            data = await get_data(first_user.id)
            amount = int(0.1 * data['balance'])
            if amount < 10:
                amount = 10 
            await update_balance(data, amount)
            await update_data(data)
            if data['boost_time'] > datetime.now().timestamp():
                boost = data['boost_level'] * 0.25 + 1
            else:
                boost = 1
            embed.add_field(name=f"Drop Claimed!", value=f"<@{first_user.id}> won {numerize(amount * boost, 2)} cookies!", inline=False)
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(title=f"Drop Claimed by {first_user.display_name}", color=0x6b4f37)
            data = await get_data(first_user.id)
            amount = int(0.1 * data['balance'])
            if amount < 10:
                amount = 10
            if data['boost_time'] > datetime.now().timestamp():
                boost = data['boost_level'] * 0.25 + 1
            else:
                boost = 1
            embed.add_field(name=f"Drop Claimed!", value=f"<@{first_user.id}> won {numerize(amount * boost, 2)} cookies!", inline=False)
            await interaction.response.edit_message(embed=embed, view=None)