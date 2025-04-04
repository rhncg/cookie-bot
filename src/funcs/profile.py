import discord
from funcs.numerize import numerize
from src.funcs.data import get_data, update_data
from src.funcs.level import get_xp_bar_data, calculate_level
from funcs.color import get_color

async def get_profile(ctx, user):
        if user is None:
            user = ctx.author
        try:
            data = await get_data(user.id)
            balance = data['balance']
            bake_speed = data['bake_speed']
            oven_cap = data['oven_cap']
            idle_upgrade_level = data['idle_upgrade_level']
            idle_upgrade = round(1.15 ** (idle_upgrade_level - 1) - 1, 1)
            bar_data = await get_xp_bar_data(data['xp'])
            
            color = await get_color(data)
            
            embed = discord.Embed(color=color)
            embed.add_field(name=f"Level {await calculate_level(data['xp'])} - {numerize(data['xp'], 2)} xp", value=bar_data[3],
                            inline=False)
            embed.add_field(name=f"{numerize(bar_data[1] - data['xp'], 2)} xp to level {await calculate_level(data['xp']) + 1}",
                            value="", inline=False)
            embed.add_field(name="Balance", value=f"{numerize(balance, 2)} cookies", inline=True)
            embed.add_field(name="Bake Speed", value=f"{numerize(bake_speed, 2)} seconds", inline=True)
            embed.add_field(name="Oven Capacity", value=f"{numerize(oven_cap, 2)} cookies", inline=True)
            embed.add_field(name="Idle Rate", value=f"{numerize(idle_upgrade, 2)} cookies per minute", inline=True)
            embed.add_field(name="Daily Streak", value=data['daily_streak'], inline=True)
            embed.add_field(name="Total Cookies Baked", value=numerize(data['total_cookies'], 2), inline=True)
            embed.set_author(name=f"{user.display_name}'s profile", icon_url=user.display_avatar.url)
            await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(f"That isn't a valid user. {e}", ephemeral=True)