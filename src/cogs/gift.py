import discord
from funcs.data import get_data
from datetime import datetime
from views.gift_confirmation import GiftConfirmationView

class Gift(discord.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        
    @discord.command(description="Gift cookies to another user")
    async def gift(self, ctx, user: discord.User):
        receiver_data = await get_data(user.id)
        author_data = await get_data(ctx.author.id)
        last_gift = author_data['last_gift']
        
        if user.id == ctx.author.id:
            await ctx.respond("You cannot gift yourself.")
            return
        
        if datetime.now().timestamp() - last_gift < 43200:
            await ctx.respond(
                f"You have already gifted someone recently.\nYou can gift someone again <t:{int(last_gift + 43200)}:R>.", ephemeral=True)
            return
        
        if author_data['balance'] < 20:
            await ctx.respond("You need at least 20 cookies to gift.", ephemeral=True)
            return

        gift_amount = receiver_data['balance'] * 0.05
        if gift_amount < 5:
            gift_amount = 5

        if gift_amount > author_data['balance'] * 0.5:
            gift_amount = round(author_data['balance'] * 0.5)
            
        confirmation_embed = discord.Embed(
            title="Gift Confirmation",
            color=0x6b4f37
        )
        confirmation_embed.add_field(name=f"Are you sure you want to gift {user.display_name} {gift_amount} cookies?", value="", inline=False)
        confirmation_embed.add_field(name="", value=f"This is {(gift_amount / author_data['balance'] * 100):.2f}% of your balance.")
        await ctx.respond(embed=confirmation_embed, view=GiftConfirmationView(ctx.author, user, gift_amount), ephemeral=True)
        
def setup(bot):
    bot.add_cog(Gift(bot))