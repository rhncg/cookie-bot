import discord
from datetime import datetime
from funcs.numerize import numerize
import random
from src.funcs.data import get_data, update_data, update_balance
from src.funcs.globals import gamble_users

class GambleConfirmationView(discord.ui.View):
    def __init__(self, user_id, amount):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.amount = amount

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def confirm_callback(self, button, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You cannot accept this person's gamble.", ephemeral=True)
            return
        data = await get_data(interaction.user.id)
        gamble_result = random.randint(-1 * int(self.amount), int(self.amount))
        data = await update_balance(data, gamble_result)
        data['last_gamble'] = datetime.now().timestamp()
        balance = data['balance']
        await update_data(data)
        gamble_users.remove(interaction.user.id)
        if gamble_result > 0:
            if data['boost_time'] > datetime.now().timestamp():
                boost = data['boost_level'] * 0.25 + 1
            else:
                boost = 1
            await interaction.response.edit_message(
                content=f"You gambled **{numerize(self.amount, 2)} cookies** and won **{numerize(gamble_result * boost, 2)} cookies**! You now have **{numerize(balance, 2)} cookies**.",
                embed=None, view=None)
        elif gamble_result < 0:
            await interaction.response.edit_message(
                content=f"You gambled **{numerize(self.amount, 2)} cookies** and lost **{numerize(abs(gamble_result), 2)} cookies**. You now have **{numerize(balance, 2)} cookies**.",
                embed=None, view=None)
        else:
            await interaction.response.edit_message(
                content=f"You gambled **{numerize(self.amount, 2)} cookies** and ended up with the same amount. Your balance is still **{numerize(balance, 2)}. cookies**.",
                embed=None, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_callback(self, button, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You cannot cancel this person's gamble.", ephemeral=True)
            return
        await interaction.response.edit_message(content="**Gamble canceled.**", embed=None, view=None)
        gamble_users.remove(interaction.user.id)