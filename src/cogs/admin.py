import discord
from datetime import datetime
import os
import re
from src.funcs.data import get_data, update_balance, update_data
from src.funcs.globals import admins, baking_users, gamble_users, dev_bots, active_channels
from src.funcs.drops import try_drop
from bot_instance import bot

class Admin(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    '''
    Admin Commands:
    - rsmsg
    - balance++{amount} (only dev bot)
    - drop (only dev bot)
    '''
        
    @discord.command(description="nuh uh")
    async def admin(self, ctx, cmd: str, user: discord.User = None, index: str = None, set = None):
        if ctx.author.id in admins:
            cmd = cmd.lower()
            if cmd == "rsmsg":
                channels = []
                
                for channel in active_channels.keys():
                    await channel.send("Bot is restarting soon, please wait...")
                    channels.append(channel)
                
                await ctx.respond(f"Sent in {len(channels)} channels", ephemeral=True)
                
            elif cmd == "remsg":
                for channel in active_channels.keys():
                    await channel.send("Bot has finished restarting!")
                
                await ctx.respond("Sent", ephemeral=True)
                
            elif "balance++" in cmd:
                if self.bot.user.id in dev_bots:
                    try:
                        amount = int(re.search(r'\d+', cmd).group())
                    except Exception as e:
                        await ctx.respond(f"error {e}", ephemeral=True)
                        return
                    if not user:
                        user = ctx.author

                    data = await get_data(user.id)
                    data = await update_balance(data, amount)
                    await update_data(data)
                    await ctx.respond(f"added {amount} cookies to {user.mention}", ephemeral=True)
                else:
                    await ctx.respond("this can't be run on the prod bot", ephemeral=True)
                    
            elif cmd == "drop":
                if self.bot.user.id in dev_bots:
                    try:
                        await try_drop(ctx.channel, True)
                    except Exception as e:
                        await ctx.respond(f"error {e}", ephemeral=True)
                else:
                    await ctx.respond("this can't be run on the prod bot", ephemeral=True)
                    
            elif cmd == "md":
                if self.bot.user.id in dev_bots:
                    if not user:
                        user = ctx.author
                    data = await get_data(user.id)
                    data[index] = set
                    await update_data(data)
                    await ctx.respond(f"set {index} to {set}", ephemeral=True)
                else:
                    await ctx.respond("this can't be run on the prod bot", ephemeral=True)
            
            else:
                await ctx.respond("Invalid command.", ephemeral=True)
        else:
            await ctx.respond("You are not an admin.", ephemeral=True)
    
    @discord.command(description="View debug info")
    async def debug(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author
        data = await get_data(user.id)
        if ctx.author.id in admins:
            embed = discord.Embed(title="Debug", color=0x6b4f37)
            embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
            embed.add_field(name="Baking Users", value=f"{baking_users}", inline=False)
            embed.add_field(name="User Data", value=f"ID: {user.id}\n"
                                                    f"Balance: {data['balance']}\n"
                                                    f"Oven Cap: {data['oven_cap']}\n"
                                                    f"Bake Speed: {data['bake_speed']}\n"
                                                    f"Ping: {data['ping']}\n"
                                                    f"Last Active: {data['last_active']}\n"
                                                    f"Idle Upgrade Level: {data['idle_upgrade_level']}\n"
                                                    f"Last Daily: {data['last_daily']}\n"
                                                    f"XP: {data['xp']}\n"
                                                    f"Last Steal: {data['last_steal']}\n"
                                                    f"Last Gamble: {data['last_gamble']}\n"
                                                    f"Daily Streak: {data['daily_streak']}\n"
                                                    f"Interactions: {data['interactions']}\n"
                                                    f"Total Cookies: {data['total_cookies']}\n"
                                                    f"Boost Time: {data['boost_time']}\n"
                                                    f"Boost Level: {data['boost_level']}\n"
                                                    f"Steal Ping: {data['steal_ping']}\n"
                                                    f"Boost Speed: {data['boost_speed']}", inline=False)
            embed.add_field(name="Current Unix Time", value=f"{datetime.now().timestamp()}", inline=False)
            embed.add_field(name="GambleConfViewActive:", value=f"{gamble_users}", inline=False)
            embed.add_field(name="Active Channels", value=f"{active_channels}", inline=False)
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("Only admins can use this command.", ephemeral=True)
            
    @discord.command(description="View the bot's latency")
    async def ping(self, ctx):
        await ctx.respond(f'Pong! {round(self.bot.latency * 1000)}ms')
        
    '''
    print(bot.user.id)
    if bot.user.id == 1326398030710313012:
        @bot.command()
        async def reset_database(ctx):
            if ctx.author.id in admins:
                try:
                    conn = await get_db_connection()
                    cursor = await conn.cursor()

                    await cursor.execute("DROP TABLE IF EXISTS users")
                    await conn.commit()

                    await cursor.execute("""
                        CREATE TABLE users (
                            user_id INTEGER PRIMARY KEY,
                            balance INTEGER DEFAULT 0,
                            oven_cap INTEGER DEFAULT 1,
                            bake_speed INTEGER DEFAULT 60,
                            ping INTEGER DEFAULT 0,
                            last_active INTEGER DEFAULT 0,
                            idle_upgrade_level INTEGER DEFAULT 1,
                            last_daily INTEGER DEFAULT 0,
                            xp INTEGER DEFAULT 0,
                            last_steal INTEGER DEFAULT 0,
                            last_gamble INTEGER DEFAULT 0,
                            daily_streak INTEGER DEFAULT 0,
                            interactions INTEGER DEFAULT 0,
                            total_cookies INTEGER DEFAULT 0,
                            boost_time INTEGER DEFAULT 0,
                            boost_level INTEGER DEFAULT 1
                        )
                        """)
                    await conn.commit()

                    await ctx.respond("database has been reset")
                except Exception as e:
                    await ctx.respond(f"An error occurred while resetting the database: {e}")
            else:
                await ctx.respond("You do not have permission to use this command.", ephemeral=True)
    @bot.command()
    async def add_xp(ctx, amount):
        data = await get_data(ctx.author.id)
        data['xp'] += int(amount)
        await update_data(data)
        await ctx.respond(f'added {amount} xp')

    @bot.command()
    async def change_balance(ctx, amount: int):
        data = await get_data(ctx.author.id)
        data = await update_balance(data, amount)
        await update_data(data)
        await ctx.respond(f'Your balance has been updated to {data["balance"]}')
        print(amount, ctx.author.id)
    '''
            
def setup(bot):
    bot.add_cog(Admin(bot))