# cogs/utility.py
import discord
from discord.ext import commands
import asyncio # For AFK auto-response management
import datetime

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.qualified_name is automatically set by discord.py
        self.afk_users = {} # In-memory storage for AFK users: {user_id: {"reason": str, "time": datetime.datetime}}
        self.maintenance_mode = False # In-memory flag for maintenance mode
        self.voice_role_config = {} # {guild_id: {"role_id": int, "enabled": bool}} - For persistence, use Firestore

    @commands.command(name="ping", help="Checks the bot's latency.")
    async def ping(self, ctx):
        """
        Responds with the bot's current latency (ping).
        Usage: XTRM ping
        """
        await ctx.send(f'Pong! 🏓 {round(self.bot.latency * 1000)}ms')

    @commands.command(name="serverinfo", help="Displays information about the server.")
    async def serverinfo(self, ctx):
        """
        Displays detailed information about the current Discord server.
        Usage: XTRM serverinfo
        """
        guild = ctx.guild
        embed = discord.Embed(
            title=f"Server Info for {guild.name}",
            description="Overview of this Discord server.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Created On", value=guild.created_at.strftime("%b %d, %Y %H:%M %p"), inline=False)
        embed.set_footer(text=f"ID: {guild.id}")
        await ctx.send(embed=embed)

    @commands.command(name="afk", help="Sets your AFK status.")
    async def afk(self, ctx, *, reason: str = "No reason provided."):
        """
        Sets your AFK status with an optional reason.
        The bot will automatically respond to mentions while you are AFK.
        Your AFK status will be removed when you send a message.
        Usage: XTRM afk [reason]
        Example: XTRM afk Taking a break
        """
        if ctx.author.id in self.afk_users:
            return await ctx.send("You are already AFK. Send a message to remove your AFK status.")

        self.afk_users[ctx.author.id] = {"reason": reason, "time": datetime.datetime.utcnow()}
        await ctx.send(f"✅ {ctx.author.display_name} is now AFK: {reason}")
        # In a real bot, save this to Firestore for persistence

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listens for messages to remove AFK status or respond to AFK mentions.
        """
        if message.author.bot:
            return

        # Check if the author is AFK and remove status
        if message.author.id in self.afk_users:
            del self.afk_users[message.author.id]
            await message.channel.send(f"👋 Welcome back, {message.author.display_name}! Your AFK status has been removed.")
            # In a real bot, remove from Firestore here

        # Check for mentions of AFK users
        for member in message.mentions:
            if member.id in self.afk_users:
                afk_info = self.afk_users[member.id]
                afk_time = (datetime.datetime.utcnow() - afk_info["time"]).total_seconds()
                days, remainder = divmod(afk_time, 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)

                time_ago = []
                if days > 0: time_ago.append(f"{int(days)}d")
                if hours > 0: time_ago.append(f"{int(hours)}h")
                if minutes > 0: time_ago.append(f"{int(minutes)}m")
                if not time_ago: time_ago.append(f"{int(seconds)}s")

                await message.channel.send(f"😴 {member.display_name} is AFK since {' '.join(time_ago)} ago: {afk_info['reason']}")

    @commands.command(name="maintenance", help="Toggles bot maintenance mode.")
    @commands.has_permissions(administrator=True)
    async def maintenance_mode_toggle(self, ctx):
        """
        Toggles the bot's maintenance mode.
        When enabled, only administrators can use bot commands.
        Usage: XTRM maintenance
        """
        self.maintenance_mode = not self.maintenance_mode
        status = "enabled" if self.maintenance_mode else "disabled"
        await ctx.send(f"⚙️ Bot maintenance mode has been **{status}**.")
        # In a real bot, save this status to Firestore

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        Global error handler for commands, used to enforce maintenance mode.
        """
        # Only handle if the error is not already handled by a more specific handler
        if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, discord.Forbidden):
            # This is a common error, often due to missing permissions.
            await ctx.send(f"❌ I do not have the necessary permissions to perform this action. Please check my role permissions. Error: `{error.original}`")
            return
        
        if self.maintenance_mode and not ctx.author.guild_permissions.administrator:
            # Check if the error is specifically a CheckFailure (e.g., from has_permissions)
            # to avoid double error messages if the command already has a check.
            if isinstance(error, commands.CheckFailure): 
                return
            return await ctx.send("❌ The bot is currently in maintenance mode. Only administrators can use commands.")
        
        # Pass other errors to the default error handler or specific handlers
        # This ensures other errors are still handled appropriately
        if isinstance(error, commands.CommandNotFound):
            return # Ignore command not found errors to avoid spam
        
        # If it's not a maintenance mode error, let the default error handling take over
        # or implement specific error handling for other types of errors.
        # For example:
        # if isinstance(error, commands.MissingPermissions):
        #     await ctx.send(f"You don't have the required permissions to use this command: {error.missing_permissions}")
        # elif isinstance(error, commands.MissingRequiredArgument):
        #     await ctx.send(f"Missing required argument: {error.param.name}. Usage: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
        # else:
        #     print(f"Unhandled error in command {ctx.command}: {e}")


    @commands.group(name="voicerole", invoke_without_command=True, help="Manages the automatic voice role.")
    @commands.has_permissions(manage_roles=True)
    async def voicerole(self, ctx):
        """
        Base command for managing the automatic voice role feature.
        Usage: XTRM voicerole [subcommand]
        Example: XTRM voicerole setup @VoiceUser
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify a Voice Role subcommand (e.g., `setup`, `enable`, `disable`). Use `XTRM advhelp Utility` for more info.")

    @voicerole.command(name="setup", help="Sets up the role to be assigned when a user joins voice.")
    @commands.has_permissions(manage_roles=True)
    async def voicerole_setup(self, ctx, *, role: discord.Role):
        """
        Sets the role that will be automatically given to users when they join a voice channel.
        Usage: XTRM voicerole setup <@role/Role Name>
        Example: XTRM voicerole setup @InVoice
        """
        if role >= ctx.guild.me.top_role:
            return await ctx.send("❌ I cannot manage roles that are equal to or higher than my top role.")

        self.voice_role_config[ctx.guild.id] = {"role_id": role.id, "enabled": False}
        # In a real bot, save this config to Firestore
        await ctx.send(f"✅ Voice role set to `{role.name}`. Use `XTRM voicerole enable` to activate it.")

    @voicerole.command(name="enable", help="Enables the automatic voice role feature.")
    @commands.has_permissions(manage_roles=True)
    async def voicerole_enable(self, ctx):
        """
        Enables the automatic assignment/removal of the voice role.
        Usage: XTRM voicerole enable
        """
        if ctx.guild.id not in self.voice_role_config or not self.voice_role_config[ctx.guild.id]["role_id"]:
            return await ctx.send("❌ Voice role is not set up. Use `XTRM voicerole setup <role>` first.")
        
        self.voice_role_config[ctx.guild.id]["enabled"] = True
        # In a real bot, update this config in Firestore
        await ctx.send("✅ Automatic voice role feature enabled.")

    @voicerole.command(name="disable", help="Disables the automatic voice role feature.")
    @commands.has_permissions(manage_roles=True)
    async def voicerole_disable(self, ctx):
        """
        Disables the automatic assignment/removal of the voice role.
        Usage: XTRM voicerole disable
        """
        if ctx.guild.id not in self.voice_role_config:
            return await ctx.send("❌ Voice role feature is not configured for this server.")

        self.voice_role_config[ctx.guild.id]["enabled"] = False
        # In a real bot, update this config in Firestore
        await ctx.send("✅ Automatic voice role feature disabled.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Listens for voice state updates to assign/remove the voice role.
        """
        # Ignore bots
        if member.bot:
            return

        guild_id = member.guild.id
        if guild_id not in self.voice_role_config or not self.voice_role_config[guild_id]["enabled"]:
            return # Feature not enabled for this guild

        role_id = self.voice_role_config[guild_id]["role_id"]
        voice_role = member.guild.get_role(role_id)

        if not voice_role:
            print(f"Voice role with ID {role_id} not found in guild {member.guild.name}. Disabling feature.")
            self.voice_role_config[guild_id]["enabled"] = False # Auto-disable if role is missing
            # In a real bot, update this in Firestore
            return

        # User joined a voice channel
        if before.channel is None and after.channel is not None:
            if voice_role not in member.roles:
                try:
                    await member.add_roles(voice_role, reason="Joined voice channel.")
                    print(f"Added '{voice_role.name}' to {member.display_name} for joining voice.")
                except discord.Forbidden:
                    print(f"Bot lacks permissions to add role '{voice_role.name}' to {member.display_name}.")
                except Exception as e:
                    print(f"Error adding voice role to {member.display_name}: {e}")

        # User left a voice channel
        elif before.channel is not None and after.channel is None:
            if voice_role in member.roles:
                try:
                    await member.remove_roles(voice_role, reason="Left voice channel.")
                    print(f"Removed '{voice_role.name}' from {member.display_name} for leaving voice.")
                except discord.Forbidden:
                    print(f"Bot lacks permissions to remove role '{voice_role.name}' from {member.display_name}.")
                except Exception as e:
                    print(f"Error removing voice role from {member.display_name}: {e}")

async def setup(bot):
    """
    Adds the Utility cog to the bot.
    """
    await bot.add_cog(Utility(bot))
