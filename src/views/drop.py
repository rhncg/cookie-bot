import discord
from src.funcs.data import get_data, update_balance, update_data

class DropView(discord.ui.View):
    def __init__(self):
        super().__init__()
        
    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green)
    async def claim_callback(self, button, interaction):
        embed = discord.Embed(title=f"Drop Claimed by {interaction.user.name}", color=0x6b4f37)
        data = await get_data(interaction.user.id)
        amount = int(0.2 * data['balance'])
        if amount < 10:
            amount = 10
        await update_balance(data, amount)
        await update_data(data)
        embed.add_field(name=f"Drop Claimed!", value=f"<@{interaction.user.id}> won {amount} cookies!", inline=False)
        await interaction.response.edit_message(embed=embed, view=None)