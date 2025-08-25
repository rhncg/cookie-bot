import discord
from funcs.data import get_data, update_data, update_balance

class GiftConfirmationView(discord.ui.View):
    def __init__(self, giver: discord.User, receiver: discord.User, amount: int):
        super().__init__()
        self.giver = giver
        self.receiver = receiver
        self.amount = amount

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await update_data(await update_balance(await get_data(self.giver.id), -self.amount))
        await update_data(await update_balance(await get_data(self.receiver.id), self.amount))

        success_embed = discord.Embed(title=f"Gifted {self.receiver.display_name} {self.amount} cookies")
        await interaction.response.edit_message(embed=success_embed, view=None)
        await interaction.channel.send(content=f"{self.giver.mention} gifted {self.receiver.mention} {self.amount} cookies!")
        
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        cancel_embed = discord.Embed(title="Gift Cancelled")
        await interaction.response.edit_message(embed=cancel_embed, view=None)