import discord
from src.funcs.data import get_data, update_data
from funcs.level import calculate_level

class OptionsView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You cannot use this person's options menu. Please use </options:1332478462354784256> and use the one provided.",
                ephemeral=True)
            return False
        return True
    
    @discord.ui.select(
        placeholder="Select an option",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Ping when stolen from",
                description="Pings the user when someone steals cookies from them",
            ),
            discord.SelectOption(
                label="Show gamble confirmation window",
                description="Shows a confirmation window before gambling",
            ),
            discord.SelectOption(
                label="Change profile color",
                description="You must must be level 200 or higher to change profile color",
            )
        ]
    )
    
    async def select_callback(self, select, interaction):
        if select.values[0] == "Ping when stolen from":
            data = await get_data(interaction.user.id)
            
            if data['options']['steal_ping'] == True:
                data['options']['steal_ping'] = False
                await update_data(data)
                await interaction.response.edit_message(view=OptionsView(interaction.user.id), embed=await make_options_embed(interaction.user.id))
            else:
                data['options']['steal_ping'] = True
                await update_data(data)
                await interaction.response.edit_message(view=OptionsView(interaction.user.id), embed=await make_options_embed(interaction.user.id))
                
            await update_data(data)
        
        elif select.values[0] == "Show gamble confirmation window":
            data = await get_data(interaction.user.id)
            
            if data['options']['gamble_confirmation'] == True:
                data['options']['gamble_confirmation'] = False
                await update_data(data)
                await interaction.response.edit_message(view=OptionsView(interaction.user.id), embed=await make_options_embed(interaction.user.id))
            else:
                data['options']['gamble_confirmation'] = True
                await update_data(data)
                await interaction.response.edit_message(view=OptionsView(interaction.user.id), embed=await make_options_embed(interaction.user.id))
                
            await update_data(data)
            
        elif select.values[0] == "Change profile color":
            data = await get_data(interaction.user.id)
            
            if calculate_level(data['xp']) < 200:
                await interaction.response.send_message("You must be level 200 or higher to change your profile color.", ephemeral=True)
                return
            
            await interaction.response.send_modal(ProfileModal())
            
async def make_options_embed(user_id):
    data = await get_data(user_id)
    embed = discord.Embed(title="Options", color=0x6b4f37)
    
    
    steal_ping = data['options']['steal_ping']
    if steal_ping == True:
        steal_ping = "Enabled"
    else:
        steal_ping = "Disabled"
        
    gamble_confirmation = data['options']['gamble_confirmation']
    if gamble_confirmation == True:
        gamble_confirmation = "Enabled"
    else:
        gamble_confirmation = "Disabled"
    
    embed.add_field(name="Ping when stolen from", value=f"{steal_ping}", inline=False)
    embed.add_field(name="Show gamble confirmation window", value=f"{gamble_confirmation}", inline=False)
    return embed

class ProfileModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(timeout=None, title="Change Profile Color")
        self.add_item(discord.ui.InputText(label="HEX Code"))
    
    async def callback(self, interaction: discord.Interaction):
        data = await get_data(interaction.user.id)
        hex_code = self.children[0].value
        if not hex_code.startswith("#"):
            hex_code = "#" + hex_code
        if len(hex_code) != 7:
            await interaction.response.send_message("Invalid HEX code. Please try again.", ephemeral=True)
            return
        if not all(c in "0123456789ABCDEFabcdef" for c in hex_code[1:]):
            await interaction.response.send_message("Invalid HEX code. Please try again.", ephemeral=True)
            return
        
        data['options']['profile_color'] = hex_code
        await update_data(data)
        
        await interaction.response.send_message(f"Your profile color has been changed to {hex_code}.")