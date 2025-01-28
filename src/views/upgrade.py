import discord
from datetime import datetime
from src.funcs.data import get_data, update_data, update_balance
from src.funcs.globals import bake_speed_upgrades
from src.funcs.upgrade_calc import calculate_next_upgrade_price, calculate_next_upgrade, make_shop_embed
from src.bot_instance import bot

class UpgradeView(discord.ui.View):
    def __init__(self, user_id, ping, boost_time):
        super().__init__(timeout=3600)
        self.user_id = user_id
        for child in self.children:
            if "Ping" in child.label and ping == 1:
                child.label = "Enable Ping Upgrade"
                child.style = discord.ButtonStyle.green
            elif "Ping" in child.label and ping == 2:
                child.label = "Disable Ping Upgrade"
                child.style = discord.ButtonStyle.red
        for child in self.children:
            if "Activate Boost" in child.label and boost_time + 900 > datetime.now().timestamp():
                child.disabled = True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You cannot use this person's shop. Please use </shop:1310001981066313738> and use the one provided.",
                ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Upgrade Bake Speed", custom_id="bake_speed", style=discord.ButtonStyle.green, row=0)
    async def upgrade_bake_speed_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        upgrade_price = await calculate_next_upgrade_price(data, 'bake_speed')
        if data['balance'] >= upgrade_price:
            try:
                new_bake_speed = bake_speed_upgrades[bake_speed_upgrades.index(data['bake_speed']) + 1]
                data = await update_balance(data, -upgrade_price)
                data['bake_speed'] = new_bake_speed
                data['xp'] += 5
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id, bot)
                embed.add_field(name=f'Your bake speed has been upgraded to {data["bake_speed"]} seconds (+5 xp)', value="",
                                inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
            except IndexError:
                embed = await make_shop_embed(interaction.user.id, bot)
                embed.add_field(name="You've reached the maximum bake speed.", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        else:
            embed = await make_shop_embed(interaction.user.id, bot)
            embed.add_field(name="You don't have enough cookies to upgrade your bake speed.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))

    @discord.ui.button(label="Upgrade Oven Capacity", custom_id="oven_cap", style=discord.ButtonStyle.green, row=0)
    async def upgrade_cookie_count_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        upgrade_price = await calculate_next_upgrade_price(data, 'oven_cap')
        if data['balance'] >= upgrade_price:
            try:
                new_oven_cap = await calculate_next_upgrade(data, 'oven_cap')
                data = await update_balance(data, -upgrade_price)
                data['oven_cap'] = new_oven_cap
                data['xp'] += 5
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id, bot)
                embed.add_field(name=f'Your oven capacity has been upgraded to {data["oven_cap"]} cookies (+5 xp)', value="",
                                inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
            except IndexError:
                embed = await make_shop_embed(interaction.user.id, bot)
                embed.add_field(name="You've reached the maximum oven capacity.", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        else:
            embed = await make_shop_embed(interaction.user.id, bot)
            embed.add_field(name="You don't have enough cookies to upgrade your oven capacity.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))

    @discord.ui.button(label="Buy Idle Upgrade", custom_id="idle_upgrade", style=discord.ButtonStyle.green, row=0)
    async def idle_upgrade_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        idle_upgrade_level = data['idle_upgrade_level']
        upgrade_price = await calculate_next_upgrade_price(data, 'idle_upgrade')
        if data['balance'] >= upgrade_price:
            data = await update_balance(data, -upgrade_price)
            data['idle_upgrade_level'] = idle_upgrade_level + 1
            data['xp'] += 5
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id, bot)
            embed.add_field(name=f'Your idle upgrade has been upgraded to level {data["idle_upgrade_level"]} (+5 xp)',
                            value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        else:
            embed = await make_shop_embed(interaction.user.id, bot)
            embed.add_field(name="You don't have enough cookies to upgrade your idle upgrade.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))

    @discord.ui.button(label="Buy Ping Upgrade", custom_id="ping_upgrade", style=discord.ButtonStyle.green, row=1)
    async def ping_upgrade_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        balance = data['balance']
        ping = data['ping']
        if ping == 0:
            if balance >= 10:
                data = await update_balance(data, -10)
                data['ping'] = 2
                data['xp'] += 5
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id, bot)
                embed.add_field(name="You've bought the ping upgrade! (+5 xp)", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
            else:
                embed = await make_shop_embed(interaction.user.id, bot)
                embed.add_field(name="You don't have enough cookies to buy the ping upgrade.", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        elif ping == 1:
            data['ping'] = 2
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id, bot)
            embed.add_field(name="You have enabled the ping upgrade.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        elif ping == 2:
            data['ping'] = 1
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id, bot)
            embed.add_field(name="You have disabled the ping upgrade.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))

    @discord.ui.button(label="Activate Boost", custom_id="boost_activate", style=discord.ButtonStyle.green, row=1)
    async def boost_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        balance = data['balance']
        if balance >= await calculate_next_upgrade_price(data, 'boost_activate'):
            data = await update_balance(data, -1 * await calculate_next_upgrade_price(data, 'boost_activate'))
            data['boost_time'] = datetime.now().timestamp() + 900
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id, bot)
            embed.add_field(name="You have activated the boost.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        else:
            embed = await make_shop_embed(interaction.user.id, bot)
            embed.add_field(name="You don't have enough cookies to activate the boost.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
    
    @discord.ui.button(label="Upgrade Boost", custom_id="boost_upgrade", style=discord.ButtonStyle.green, row=1)
    async def boost_upgrade_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        balance = data['balance']
        if balance >= await calculate_next_upgrade_price(data, 'boost_upgrade'):
            data = await update_balance(data, -1 * await calculate_next_upgrade_price(data, 'boost_upgrade'))
            data['boost_level'] += 1
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id, bot)
            embed.add_field(name="You have upgraded the boost.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
        else:
            embed = await make_shop_embed(interaction.user.id, bot)
            embed.add_field(name="You don't have enough cookies to upgrade the boost.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))
    
    @discord.ui.button(label="", emoji="🔄", custom_id="update_refresh", style=discord.ButtonStyle.secondary, row=1)
    async def refresh_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        # print(UpgradeView.is_persistent(UpgradeView(interaction.user.id, data['ping'], data['boost_time'])))
        await interaction.response.edit_message(embed=await make_shop_embed(interaction.user.id, bot), view=UpgradeView(interaction.user.id, data['ping'], data['boost_time']))

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True