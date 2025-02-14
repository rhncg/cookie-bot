import discord
from numerize.numerize import numerize
from src.funcs.db import get_db_connection
from src.funcs.level import calculate_level

class LeaderboardView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.sort_by_level = False
        self.page = 1
        
    # PAGINATION SOON (TM)

    @discord.ui.button(label="Sort by Level", style=discord.ButtonStyle.green)
    async def sort_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.sort_by_level = not self.sort_by_level
        button.label = "Sort by Cookies" if self.sort_by_level else "Sort by Level"

        conn = await get_db_connection()
        cursor = await conn.cursor()
        sort = "xp" if self.sort_by_level else "balance"
        await cursor.execute(f"SELECT user_id, {sort} FROM users ORDER BY {sort} DESC LIMIT 10 OFFSET {(self.page - 1) * 10}")
        rows = await cursor.fetchall()

        embed = discord.Embed(title="Leaderboard", color=0x6b4f37)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue
            if self.sort_by_level:
                label = f"Level {await calculate_level(row[1])} - {numerize(row[1], 2)} xp"
                embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)
            else:
                label = f"{numerize(row[1], 2)} cookies"
                embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)
        
    @discord.ui.button(label="", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def prev_callback(self, button, interaction):
        if self.page > 1:
            self.page -= 1
        
        conn = await get_db_connection()
        cursor = await conn.cursor()
        sort = "xp" if self.sort_by_level else "balance"
        await cursor.execute(f"SELECT user_id, {sort} FROM users ORDER BY {sort} DESC LIMIT 10 OFFSET {(self.page - 1) * 10}")
        rows = await cursor.fetchall()

        embed = discord.Embed(title="Leaderboard", color=0x6b4f37)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue
            if self.sort_by_level:
                label = f"Level {await calculate_level(row[1])} - {numerize(row[1], 2)} xp"
                embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)
            else:
                label = f"{numerize(row[1], 2)} cookies"
                embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def next_callback(self, button, interaction):
        conn = await get_db_connection()
        cursor = await conn.cursor()
        sort = "xp" if self.sort_by_level else "balance"
        await cursor.execute(f"SELECT user_id, {sort} FROM users ORDER BY {sort} DESC")
        rows = await cursor.fetchall()
        
        count = 0
        
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue
            count += 1
        
        if count > self.page * 10:
            self.page += 1
        
        conn = await get_db_connection()
        cursor = await conn.cursor()
        sort = "xp" if self.sort_by_level else "balance"
        await cursor.execute(f"SELECT user_id, {sort} FROM users ORDER BY {sort} DESC LIMIT 10 OFFSET {(self.page - 1) * 10}")
        rows = await cursor.fetchall()

        embed = discord.Embed(title="Leaderboard", color=0x6b4f37)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue
            if self.sort_by_level:
                label = f"Level {await calculate_level(row[1])} - {numerize(row[1], 2)} xp"
                embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)
            else:
                label = f"{numerize(row[1], 2)} cookies"
                embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)
        
    @discord.ui.button(label="", emoji="👤", style=discord.ButtonStyle.secondary)
    async def jumpt_to_profile(self, button, interaction):
        conn = await get_db_connection()
        cursor = await conn.cursor()
        sort = "xp" if self.sort_by_level else "balance"
        user_id = interaction.user.id
        await cursor.execute(f"SELECT COUNT(*) + 1 AS position FROM users WHERE {sort} > (SELECT {sort} FROM users WHERE user_id = {user_id})")
        row = await cursor.fetchone()
        position = row[0] if row else None
        if position:
            self.page = (position - 1) // 10 + 1
            
        conn = await get_db_connection()
        cursor = await conn.cursor()
        sort = "xp" if self.sort_by_level else "balance"
        await cursor.execute(f"SELECT user_id, {sort} FROM users ORDER BY {sort} DESC LIMIT 10 OFFSET {(self.page - 1) * 10}")
        rows = await cursor.fetchall()

        embed = discord.Embed(title="Leaderboard", color=0x6b4f37)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue
            if self.sort_by_level:
                label = f"Level {await calculate_level(row[1])} - {numerize(row[1], 2)} xp"
                embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)
            else:
                label = f"{numerize(row[1], 2)} cookies"
                embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)