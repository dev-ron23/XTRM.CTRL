# cogs/emergency.py
import discord
from discord.ext import commands

class Emergency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.qualified_name is automatically set by discord.py

    @commands.command(name="serverlock", help="Locks down the entire server.")
    @commands.has_permissions(administrator=True)
    async def serverlock(self, ctx, *, reason: str = "Server lockdown initiated."):
        """
        Locks down all text channels in the server, preventing @everyone from sending messages.
        Usage: XTRM serverlock [reason]
        Example: XTRM serverlock Ongoing raid
        """
        # --- Implementation for server lockdown ---
        # This would iterate through all text channels and deny send_messages permission for @everyone.
        # It's crucial to have a corresponding unlock command.
        await ctx.send(f"🚨 Server lockdown initiated! Reason: {reason} (Placeholder)")
        print(f"Server locked by {ctx.author.name} for: {reason}")

    @commands.command(name="serverunlock", help="Unlocks the entire server.")
    @commands.has_permissions(administrator=True)
    async def serverunlock(self, ctx):
        """
        Unlocks all text channels in the server, restoring @everyone's ability to send messages.
        Usage: XTRM serverunlock
        """
        # --- Implementation for server unlock ---
        await ctx.send("✅ Server unlocked! (Placeholder)")
        print(f"Server unlocked by {ctx.author.name}")

    # Placeholder for other Emergency commands like massdelete, panic, etc.

async def setup(bot):
    """
    Adds the Emergency cog to the bot.
    """
    await bot.add_cog(Emergency(bot))
