import discord
from funcs.numerize import numerize
from src.funcs.db import get_db_connection
from src.funcs.level import calculate_level

class LeaderboardView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.sort = "Cookies"
        self.page = 1

    @discord.ui.button(label="Sort by Level", style=discord.ButtonStyle.green, row=1)
    async def sort_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.sort == "Streak":
            self.sort = "Cookies"
            button.label = f"Sort by Level"
        elif self.sort == "Cookies":
            self.sort = "Level"
            button.label = f"Sort by Streak"
        elif self.sort == "Level":
            self.sort = "Streak"
            button.label = f"Sort by Cookies"

        self.page = 1

        conn = await get_db_connection()
        cursor = await conn.cursor()

        # Map self.sort to database fields
        sort_field = {
            "Cookies": "balance",
            "Level": "xp",
            "Streak": "daily_streak"
        }.get(self.sort, self.sort.lower())

        await cursor.execute(f"SELECT user_id, {sort_field} FROM users LIMIT 10 OFFSET {(self.page - 1) * 10}")
        rows = await cursor.fetchall()

        # Convert to integers and sort in Python
        if self.sort in ["Level", "Cookies", "Streak"]:
            rows = [(row[0], int(row[1])) for row in rows]
            rows = sorted(rows, key=lambda x: x[1], reverse=True)

        embed = discord.Embed(title=f"{self.sort} Leaderboard", color=0x6b4f37)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue

            if self.sort == "Level":
                label = f"Level {await calculate_level(row[1])} - {numerize(row[1], 2)} xp"
            elif self.sort == "Cookies":
                label = f"{numerize(row[1], 2)} cookies"
            elif self.sort == "Streak":
                label = f"{numerize(row[1], 2)} days"

            embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)
        
    @discord.ui.button(label="", emoji="⬅️", style=discord.ButtonStyle.secondary, row=0)
    async def prev_callback(self, button, interaction):
        if self.page > 1:
            self.page -= 1
        
        conn = await get_db_connection()
        cursor = await conn.cursor()

        # Map self.sort to database fields
        sort_field = {
            "Cookies": "balance",
            "Level": "xp",
            "Streak": "daily_streak"
        }.get(self.sort, self.sort.lower())

        await cursor.execute(f"SELECT user_id, {sort_field} FROM users LIMIT 10 OFFSET {(self.page - 1) * 10}")
        rows = await cursor.fetchall()

        # Convert to integers and sort in Python
        if self.sort in ["Level", "Cookies", "Streak"]:
            rows = [(row[0], int(row[1])) for row in rows]
            rows = sorted(rows, key=lambda x: x[1], reverse=True)

        embed = discord.Embed(title=f"{self.sort} Leaderboard", color=0x6b4f37)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue

            if self.sort == "Level":
                label = f"Level {await calculate_level(row[1])} - {numerize(row[1], 2)} xp"
            elif self.sort == "Cookies":
                label = f"{numerize(row[1], 2)} cookies"
            elif self.sort == "Streak":
                label = f"{numerize(row[1], 2)} days"

            embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="", emoji="➡️", style=discord.ButtonStyle.secondary, row=0)
    async def next_callback(self, button, interaction):
        conn = await get_db_connection()
        cursor = await conn.cursor()
        
        # Map self.sort to database fields
        sort_field = {
            "Cookies": "balance",
            "Level": "xp",
            "Streak": "daily_streak"
        }.get(self.sort, self.sort.lower())

        await cursor.execute(f"SELECT user_id, {sort_field} FROM users")
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

        await cursor.execute(f"SELECT user_id, {sort_field} FROM users LIMIT 10 OFFSET {(self.page - 1) * 10}")
        rows = await cursor.fetchall()

        # Convert to integers and sort in Python
        if self.sort in ["Level", "Cookies", "Streak"]:
            rows = [(row[0], int(row[1])) for row in rows]
            rows = sorted(rows, key=lambda x: x[1], reverse=True)

        embed = discord.Embed(title=f"{self.sort} Leaderboard", color=0x6b4f37)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue

            if self.sort == "Level":
                label = f"Level {await calculate_level(row[1])} - {numerize(row[1], 2)} xp"
            elif self.sort == "Cookies":
                label = f"{numerize(row[1], 2)} cookies"
            elif self.sort == "Streak":
                label = f"{numerize(row[1], 2)} days"

            embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)
        
    @discord.ui.button(label="", emoji="👤", style=discord.ButtonStyle.secondary, row=0)
    async def jump_to_profile(self, button, interaction):
        conn = await get_db_connection()
        cursor = await conn.cursor()
        user_id = interaction.user.id

        # Map self.sort to database fields
        sort_field = {
            "Cookies": "balance",
            "Level": "xp",
            "Streak": "daily_streak"
        }.get(self.sort, self.sort.lower())

        await cursor.execute(f"SELECT user_id, {sort_field} FROM users")
        rows = await cursor.fetchall()

        # Convert to integers and sort in Python
        if self.sort in ["Level", "Cookies", "Streak"]:
            rows = [(row[0], int(row[1])) for row in rows]
            rows = sorted(rows, key=lambda x: x[1], reverse=True)
            
        for i, row in enumerate(rows):
            if row[0] == user_id:
                position = i + 1
                break        
        

        position = row[0] if row else None
        if position:
            self.page = (position - 1) // 10 + 1
            
        conn = await get_db_connection()
        cursor = await conn.cursor()

        await cursor.execute(f"SELECT user_id, {sort_field} FROM users LIMIT 10 OFFSET {(self.page - 1) * 10}")
        rows = await cursor.fetchall()

        embed = discord.Embed(title=f"{self.sort} Leaderboard", color=0x6b4f37)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue

            if self.sort == "Level":
                label = f"Level {await calculate_level(row[1])} - {numerize(row[1], 2)} xp"
            elif self.sort == "Cookies":
                label = f"{numerize(row[1], 2)} cookies"
            elif self.sort == "Streak":
                label = f"{numerize(row[1], 2)} days"

            embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="", emoji="🔄", style=discord.ButtonStyle.secondary, row=1)
    async def refresh_callback(self, button, interaction):
        conn = await get_db_connection()
        cursor = await conn.cursor()

        # Map self.sort to database fields
        sort_field = {
            "Cookies": "balance",
            "Level": "xp",
            "Streak": "daily_streak"
        }.get(self.sort, self.sort.lower())

        await cursor.execute(f"SELECT user_id, {sort_field} FROM users LIMIT 10 OFFSET {(self.page - 1) * 10}")
        rows = await cursor.fetchall()

        # Convert to integers and sort in Python
        if self.sort in ["Level", "Cookies", "Streak"]:
            rows = [(row[0], int(row[1])) for row in rows]
            rows = sorted(rows, key=lambda x: x[1], reverse=True)
        
        embed = discord.Embed(title=f"{self.sort} Leaderboard", color=0x6b4f37)
        for i, row in enumerate(rows):
            if row[1] == 0:
                continue

            if self.sort == "Level":
                label = f"Level {await calculate_level(row[1])} - {numerize(row[1], 2)} xp"
            elif self.sort == "Cookies":
                label = f"{numerize(row[1], 2)} cookies"
            elif self.sort == "Streak":
                label = f"{numerize(row[1], 2)} days"

            embed.add_field(name="", value=f"{i + 1 + (self.page - 1) * 10}. <@{row[0]}> - {label}", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)