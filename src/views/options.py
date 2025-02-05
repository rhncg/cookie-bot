import discord
from src.funcs.data import get_data, update_data

class OptionsView(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.select(
        placeholder="Select an option",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Ping when stolen from",
                description="Pings the user when someone steals cookies from them",
            )
        ]
    )
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You cannot use this person's options menu. Please use </options:1332478462354784256> and use the one provided.",
                ephemeral=True)
            return False
        return True
    
    async def select_callback(self, select, interaction):
        if select.values[0] == "Ping when stolen from":
            data = await get_data(interaction.user.id)
            if data['steal_ping'] == True or data['steal_ping'] == 1:
                data['steal_ping'] = False
                await update_data(data)
                await interaction.response.edit_message(view=OptionsView(), embed=await make_options_embed(interaction.user.id))
            else:
                data['steal_ping'] = True
                await update_data(data)
                await interaction.response.edit_message(view=OptionsView(), embed=await make_options_embed(interaction.user.id))
            await update_data(data)
            
async def make_options_embed(user_id):
    data = await get_data(user_id)
    embed = discord.Embed(title="Options", color=0x6b4f37)
    steal_ping = data['steal_ping']
    if steal_ping == True or steal_ping == 1:
        steal_ping = "Yes"
    else:
        steal_ping = "No"
    embed.add_field(name="Ping when stolen from", value=f"{steal_ping}", inline=False)
    return embed