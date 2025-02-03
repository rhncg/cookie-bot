import discord
from datetime import datetime
from numerize.numerize import numerize
from src.funcs.data import get_data, update_balance, update_data

class DropView(discord.ui.View):
    def __init__(self):
        super().__init__()
        
    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green)
    async def claim_callback(self, button, interaction):
        embed = discord.Embed(title=f"Drop Claimed by {interaction.user.display_name}", color=0x6b4f37)
        data = await get_data(interaction.user.id)
        amount = int(0.1 * data['balance'])
        if amount < 10:
            amount = 10
        await update_balance(data, amount)
        await update_data(data)
        if data['boost_time'] > datetime.now().timestamp():
            boost = data['boost_level'] * 0.25 + 1
        else:
            boost = 1
        embed.add_field(name=f"Drop Claimed!", value=f"<@{interaction.user.id}> won {numerize(amount * boost, 2)} cookies!", inline=False)
        await interaction.response.edit_message(embed=embed, view=None)