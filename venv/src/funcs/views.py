import math
import discord
from discord.ext.pages import Paginator, Page
# from dotenv import load_dotenv
import aiosqlite
import asyncio
from datetime import datetime
import random
from numerize.numerize import numerize
from src import bot
import funcs

class LeaderboardView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx  # Save the context to fetch data later
        self.sort_by_level = False  # Track sorting state
        self.page = 1

    @discord.ui.button(label="Sort by Level", style=discord.ButtonStyle.green)
    async def sort_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.sort_by_level = not self.sort_by_level  # Toggle state
        button.label = "Sort by Cookies" if self.sort_by_level else "Sort by Level"

        # Fetch new data based on sorting
        conn = await get_db_connection()
        cursor = await conn.cursor()
        sort = "xp" if self.sort_by_level else "balance"
        await cursor.execute(f"SELECT user_id, {sort} FROM users ORDER BY {sort} DESC")
        rows = await cursor.fetchall()

        # Update the embed with new leaderboard data
        embed = discord.Embed(title="Leaderboard", color=0x6b4f37)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue
            if self.sort_by_level:
                label = f"Level {await calculate_level(row[1])} - {numerize(row[1], 2)} xp"
                embed.add_field(name="", value=f"{i + 1}. <@{row[0]}> - {label}", inline=False)
            else:
                label = f"{numerize(row[1], 2)} cookies"
                embed.add_field(name="", value=f"{i + 1}. <@{row[0]}> - {label}", inline=False)

        # Update the interaction message with the new data and view
        await interaction.response.edit_message(embed=embed, view=self)

class UpgradeView(discord.ui.View):
    def __init__(self, user_id, ping):
        super().__init__()
        self.user_id = user_id
        for child in self.children:
            if "Ping" in child.label and ping == 1:
                child.label = "Enable Ping Upgrade"
                child.style = discord.ButtonStyle.green
            elif "Ping" in child.label and ping == 2:
                child.label = "Disable Ping Upgrade"
                child.style = discord.ButtonStyle.red

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Check if the user interacting matches the intended user
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You cannot use this person's shop. Please use </shop:1310001981066313738> and use the one provided.",
                ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Upgrade Bake Speed", style=discord.ButtonStyle.green)
    async def upgrade_bake_speed_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        upgrade_price = await calculate_next_upgrade_price(data, 'bake_speed')
        if data['balance'] >= upgrade_price:
            try:
                new_bake_speed = bake_speed_upgrades[bake_speed_upgrades.index(data['bake_speed']) + 1]
                data['balance'] -= upgrade_price
                data['bake_speed'] = new_bake_speed
                data['xp'] += 5
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name=f'Your bake speed has been upgraded to {data["bake_speed"]} seconds (+5 xp)', value="",
                                inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping']))
            except IndexError:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've reached the maximum bake speed.", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your bake speed.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))

    @discord.ui.button(label="Upgrade Oven Capacity", style=discord.ButtonStyle.green)
    async def upgrade_cookie_count_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        upgrade_price = await calculate_next_upgrade_price(data, 'oven_cap')
        if data['balance'] >= upgrade_price:
            try:
                new_oven_cap = await calculate_next_upgrade(data, 'oven_cap')
                data['balance'] -= upgrade_price
                data['oven_cap'] = new_oven_cap
                data['xp'] += 5
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name=f'Your oven capacity has been upgraded to {data["oven_cap"]} cookies (+5 xp)', value="",
                                inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping']))
            except IndexError:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've reached the maximum oven capacity.", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your oven capacity.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))

    @discord.ui.button(label="Buy Idle Upgrade", style=discord.ButtonStyle.green)
    async def idle_upgrade_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        idle_upgrade_level = data['idle_upgrade_level']
        upgrade_price = await calculate_next_upgrade_price(data, 'idle_upgrade')
        if data['balance'] >= upgrade_price:
            data['balance'] -= upgrade_price
            data['idle_upgrade_level'] = idle_upgrade_level + 1
            data['xp'] += 5
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name=f'Your idle upgrade has been upgraded to level {data["idle_upgrade_level"]} (+5 xp)',
                            value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))
        else:
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You don't have enough cookies to upgrade your idle upgrade.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))

    @discord.ui.button(label="Buy Ping Upgrade", style=discord.ButtonStyle.green)
    async def ping_upgrade_callback(self, button, interaction):
        data = await get_data(interaction.user.id)
        balance = data['balance']
        ping = data['ping']
        if ping == 0:
            if balance >= 10:
                data['balance'] -= 10
                data['ping'] = 2
                data['xp'] += 5
                await update_data(data)
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You've bought the ping upgrade! (+5 xp)", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping']))
            else:
                embed = await make_shop_embed(interaction.user.id)
                embed.add_field(name="You don't have enough cookies to buy the ping upgrade.", value="", inline=False)
                await interaction.response.edit_message(embed=embed,
                                                        view=UpgradeView(interaction.user.id, data['ping']))
        elif ping == 1:
            data['ping'] = 2
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You have enabled the ping upgrade.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))
        elif ping == 2:
            data['ping'] = 1
            await update_data(data)
            embed = await make_shop_embed(interaction.user.id)
            embed.add_field(name="You have disabled the ping upgrade.", value="", inline=False)
            await interaction.response.edit_message(embed=embed, view=UpgradeView(interaction.user.id, data['ping']))

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

class GambleConfirmationView(discord.ui.View):
    def __init__(self, user_id, amount):
        super().__init__()
        self.user_id = user_id
        self.amount = amount

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def confirm_callback(self, button, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You cannot accept this person's gamble.", ephemeral=True)
            return
        data = await get_data(interaction.user.id)
        gamble_result = random.randint(-self.amount, self.amount)
        await update_balance(data, gamble_result)
        data['last_gamble'] = datetime.now().timestamp()
        balance = data['balance']
        await update_data(data)
        gamble_users.remove(interaction.user.id)
        if gamble_result > 0:
            await interaction.response.edit_message(
                content=f"You gambled {numerize(self.amount, 2)} cookies and won {numerize(gamble_result, 2)} cookies! Your new balance is {numerize(balance, 2)}.",
                embed=None, view=None)
        elif gamble_result < 0:
            await interaction.response.edit_message(
                content=f"You gambled {numerize(self.amount, 2)} cookies and lost {numerize(abs(gamble_result), 2)} cookies. Your new balance is {numerize(balance, 2)}.",
                embed=None, view=None)
        else:
            await interaction.response.edit_message(
                content=f"You gambled {numerize(self.amount, 2)} cookies and ended up with the same amount. Your balance is still {numerize(balance, 2)}.",
                embed=None, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_callback(self, button, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You cannot cancel this person's gamble.", ephemeral=True)
            return
        await interaction.response.edit_message(content="Gamble canceled.", embed=None, view=None)
        gamble_users.remove(interaction.user.id)