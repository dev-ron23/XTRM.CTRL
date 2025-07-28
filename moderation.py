# cogs/moderation.py
import discord
from discord.ext import commands
import asyncio # For sleep in tempban/tempmute

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.qualified_name is automatically set by discord.py
        self.mutes = {} # In-memory storage for active mutes (for demonstration)
                        # In a real bot, use a database (e.g., Firestore) for persistence.
        self.reply_autoroles = {} # {guild_id: {trigger_word: role_id}} for reply-triggered autoroles

    @commands.command(name="kick", help="Kicks a member from the server.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided."):
        """
        Kicks a specified member from the server.
        Usage: XTRM kick <@member> [reason]
        Example: XTRM kick @User#1234 Spamming in general
        """
        if member == ctx.author:
            return await ctx.send("❌ You cannot kick yourself.")
        if member == self.bot.user:
            return await ctx.send("❌ I cannot kick myself.")
        if ctx.author.top_role <= member.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ You cannot kick someone with an equal or higher role than yourself.")

        try:
            await member.kick(reason=reason)
            await ctx.send(f"✅ Kicked {member.display_name} for: {reason}")
            # Log the action (e.g., to a moderation log channel)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick that member. Make sure my role is above theirs.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ An error occurred while kicking: {e}")

    @commands.command(name="ban", help="Bans a member from the server.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided."):
        """
        Bans a specified member from the server.
        Usage: XTRM ban <@member> [reason]
        Example: XTRM ban @User#1234 Rule breaking
        """
        if member == ctx.author:
            return await ctx.send("❌ You cannot ban yourself.")
        if member == self.bot.user:
            return await ctx.send("❌ I cannot ban myself.")
        if ctx.author.top_role <= member.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ You cannot ban someone with an equal or higher role than yourself.")

        try:
            await member.ban(reason=reason)
            await ctx.send(f"✅ Banned {member.display_name} for: {reason}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban that member. Make sure my role is above theirs.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ An error occurred while banning: {e}")

    @commands.command(name="warn", help="Issues a warning to a member.")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided."):
        """
        Issues a warning to a specified member.
        Usage: XTRM warn <@member> [reason]
        Example: XTRM warn @User#1234 Minor infraction
        """
        # --- Placeholder for Warning System ---
        # In a real bot, you'd store warnings in a database (e.g., Firestore)
        # and implement logic for automatic actions based on warning count.
        await ctx.send(f"⚠️ Warned {member.display_name} for: {reason} (Warning system placeholder)")
        print(f"Warned {member.name} by {ctx.author.name} for: {reason}")

    @commands.command(name="mute", help="Mutes a member in the server.")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason: str = "No reason provided."):
        """
        Mutes a specified member. Optionally for a duration (e.g., 10m, 1h, 1d).
        Usage: XTRM mute <@member> [duration] [reason]
        Example: XTRM mute @User#1234 30m Excessive spam
        """
        if member == ctx.author:
            return await ctx.send("❌ You cannot mute yourself.")
        if member == self.bot.user:
            return await ctx.send("❌ I cannot mute myself.")
        if ctx.author.top_role <= member.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ You cannot mute someone with an equal or higher role than yourself.")

        # Find or create a 'Muted' role
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            try:
                muted_role = await ctx.guild.create_role(name="Muted", reason="Muted role for moderation")
                # Set permissions for the muted role in all channels
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)
                await ctx.send("Created 'Muted' role and set channel permissions.")
            except discord.Forbidden:
                return await ctx.send("❌ I don't have permission to create roles or set channel permissions. Please grant me 'Manage Roles' and 'Manage Channels'.")

        try:
            await member.add_roles(muted_role, reason=reason)
            self.mutes[member.id] = True # Store mute status (in-memory)

            response_message = f"✅ Muted {member.display_name} for: {reason}"

            if duration:
                # Parse duration (e.g., 10m, 1h, 1d)
                seconds = 0
                if duration.endswith('s'): seconds = int(duration[:-1])
                elif duration.endswith('m'): seconds = int(duration[:-1]) * 60
                elif duration.endswith('h'): seconds = int(duration[:-1]) * 3600
                elif duration.endswith('d'): seconds = int(duration[:-1]) * 86400
                else:
                    return await ctx.send("❌ Invalid duration format. Use s (seconds), m (minutes), h (hours), d (days).")

                if seconds > 0:
                    response_message += f" (for {duration})"
                    await ctx.send(response_message)
                    await asyncio.sleep(seconds)
                    # Attempt to unmute after duration
                    if member.id in self.mutes: # Check if still muted (not manually unmuted)
                        await member.remove_roles(muted_role, reason="Temporary mute expired.")
                        del self.mutes[member.id]
                        await ctx.send(f"✅ Unmuted {member.display_name} (temporary mute expired).")
                else:
                    await ctx.send(response_message)
            else:
                await ctx.send(response_message)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to assign the 'Muted' role. Make sure my role is above the 'Muted' role and the target member's role.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ An error occurred while muting: {e}")

    @commands.command(name="unmute", help="Unmutes a member in the server.")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "No reason provided."):
        """
        Unmutes a specified member.
        Usage: XTRM unmute <@member> [reason]
        Example: XTRM unmute @User#1234 Behavior improved
        """
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            return await ctx.send("❌ No 'Muted' role found. The member might not be muted or the role was deleted.")

        if muted_role not in member.roles:
            return await ctx.send(f"❌ {member.display_name} is not currently muted.")

        try:
            await member.remove_roles(muted_role, reason=reason)
            if member.id in self.mutes:
                del self.mutes[member.id] # Remove from in-memory mute tracker
            await ctx.send(f"✅ Unmuted {member.display_name} for: {reason}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to remove the 'Muted' role.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ An error occurred while unmuting: {e}")

    @commands.command(name="tempban", help="Temporarily bans a member from the server.")
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided."):
        """
        Temporarily bans a specified member for a duration (e.g., 10m, 1h, 1d).
        Usage: XTRM tempban <@member> <duration> [reason]
        Example: XTRM tempban @User#1234 1d Severe rule violation
        """
        if member == ctx.author:
            return await ctx.send("❌ You cannot tempban yourself.")
        if member == self.bot.user:
            return await ctx.send("❌ I cannot tempban myself.")
        if ctx.author.top_role <= member.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ You cannot tempban someone with an equal or higher role than yourself.")

        seconds = 0
        if duration.endswith('s'): seconds = int(duration[:-1])
        elif duration.endswith('m'): seconds = int(duration[:-1]) * 60
        elif duration.endswith('h'): seconds = int(duration[:-1]) * 3600
        elif duration.endswith('d'): seconds = int(duration[:-1]) * 86400
        else:
            return await ctx.send("❌ Invalid duration format. Use s (seconds), m (minutes), h (hours), d (days).")

        if seconds <= 0:
            return await ctx.send("❌ Duration must be a positive value.")

        try:
            await member.ban(reason=reason)
            await ctx.send(f"✅ Temporarily banned {member.display_name} for {duration} for: {reason}")
            await asyncio.sleep(seconds)
            await ctx.guild.unban(member, reason="Temporary ban expired.")
            await ctx.send(f"✅ Unbanned {member.display_name} (temporary ban expired).")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban or unban that member.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ An error occurred during tempban: {e}")

    @commands.command(name="trial", help="Adds or removes the 'Trial Member' role.")
    @commands.has_permissions(manage_roles=True)
    async def trial(self, ctx, action: str, member: discord.Member, *, note: str = None):
        """
        Adds or removes the "Trial Member" role to/from a user.
        Usage: XTRM trial <add|remove> <@member> [note]
        Example: XTRM trial add @NewMember Starting trial period
        """
        action = action.lower()
        trial_role = discord.utils.get(ctx.guild.roles, name="Trial Member")

        if not trial_role:
            try:
                trial_role = await ctx.guild.create_role(name="Trial Member", reason="Role for trial members")
                await ctx.send("Created 'Trial Member' role.")
            except discord.Forbidden:
                return await ctx.send("❌ I don't have permission to create roles.")

        if action == "add":
            if trial_role in member.roles:
                return await ctx.send(f"❌ {member.display_name} already has the 'Trial Member' role.")
            try:
                await member.add_roles(trial_role, reason=f"Trial role added by {ctx.author.name}. Note: {note or 'None'}")
                await ctx.send(f"✅ Added 'Trial Member' role to {member.display_name}. Note: {note or 'None'}")
                if note:
                    try:
                        await member.send(f"You have been given the 'Trial Member' role in {ctx.guild.name}. Note from staff: {note}")
                    except discord.Forbidden:
                        await ctx.send(f"⚠️ Could not DM {member.display_name} about the trial role.")
            except discord.Forbidden:
                await ctx.send("❌ I don't have permission to assign the 'Trial Member' role. Make sure my role is above theirs.")
        elif action == "remove":
            if trial_role not in member.roles:
                return await ctx.send(f"❌ {member.display_name} does not have the 'Trial Member' role.")
            try:
                await member.remove_roles(trial_role, reason=f"Trial role removed by {ctx.author.name}. Note: {note or 'None'}")
                await ctx.send(f"✅ Removed 'Trial Member' role from {member.display_name}. Note: {note or 'None'}")
            except discord.Forbidden:
                await ctx.send("❌ I don't have permission to remove the 'Trial Member' role.")
        else:
            await ctx.send("❌ Invalid action. Use `add` or `remove`.")

    @commands.command(name="manageperms", help="Manages a user's send message permission in a channel.")
    @commands.has_permissions(manage_channels=True)
    async def manage_permissions(self, ctx, member: discord.Member, channel: discord.TextChannel, action: str):
        """
        Enables or disables send messages permission for a user in a specific channel.
        Usage: XTRM manageperms <@member> <#channel> <enable|disable>
        Example: XTRM manageperms @User#1234 #general disable
        """
        action = action.lower()
        if action not in ["enable", "disable"]:
            return await ctx.send("❌ Invalid action. Use `enable` or `disable`.")

        overwrite = channel.overwrites_for(member)
        if action == "enable":
            overwrite.send_messages = True
            message = f"✅ Enabled send messages for {member.display_name} in {channel.mention}."
        else: # disable
            overwrite.send_messages = False
            message = f"✅ Disabled send messages for {member.display_name} in {channel.mention}."
        
        try:
            await channel.set_permissions(member, overwrite=overwrite)
            await ctx.send(message)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage channel permissions.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command(name="manageroles", help="Gives or removes roles from users.")
    @commands.has_permissions(manage_roles=True)
    async def manage_roles(self, ctx, action: str, member: discord.Member, *, role: discord.Role):
        """
        Gives or removes a specified role from a user.
        Usage: XTRM manageroles <give|remove> <@member> <@role/Role Name>
        Example: XTRM manageroles give @User#1234 @Member
        """
        action = action.lower()

        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ You cannot manage roles that are equal to or higher than your top role.")
        if role >= ctx.guild.me.top_role:
            return await ctx.send("❌ I cannot manage roles that are equal to or higher than my top role.")
        if member == self.bot.user:
            return await ctx.send("❌ I cannot manage my own roles.")

        try:
            if action == "give":
                if role in member.roles:
                    return await ctx.send(f"❌ {member.display_name} already has the role {role.name}.")
                await member.add_roles(role, reason=f"Role given by {ctx.author.name}")
                await ctx.send(f"✅ Gave role `{role.name}` to {member.display_name}.")
            elif action == "remove":
                if role not in member.roles:
                    return await ctx.send(f"❌ {member.display_name} does not have the role {role.name}.")
                await member.remove_roles(role, reason=f"Role removed by {ctx.author.name}")
                await ctx.send(f"✅ Removed role `{role.name}` from {member.display_name}.")
            else:
                await ctx.send("❌ Invalid action. Use `give` or `remove`.")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage roles. Make sure my role is above the role you're trying to manage.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.group(name="autorole", invoke_without_command=True, help="Manages automatic role assignments.")
    @commands.has_permissions(manage_roles=True)
    async def autorole(self, ctx):
        """
        Base command for managing automatic role assignments.
        Usage: XTRM autorole [subcommand]
        Example: XTRM autorole reply list
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify an Autorole subcommand (e.g., `reply create`, `reply list`). Use `XTRM advhelp autorole` for more info.")

    @autorole.group(name="reply", invoke_without_command=True, help="Manages reply-triggered autoroles.")
    @commands.has_permissions(manage_roles=True)
    async def autorole_reply(self, ctx):
        """
        Base command for managing reply-triggered autoroles.
        Usage: XTRM autorole reply [subcommand]
        Example: XTRM autorole reply create "Staff" @StaffRole
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify a Reply Autorole subcommand (e.g., `create`, `list`, `edit`, `delete`, `test`). Use `XTRM advhelp autorole` for more info.")

    @autorole_reply.command(name="create", help="Creates a new reply-triggered autorole.")
    @commands.has_permissions(manage_roles=True)
    async def autorole_reply_create(self, ctx, trigger_word: str, *, role: discord.Role):
        """
        Creates a new reply-triggered autorole. When a user replies to a message with the trigger word,
        the replied-to user will receive the specified role.
        Usage: XTRM autorole reply create "<trigger_word>" <@role/Role Name>
        Example: XTRM autorole reply create "Staff" @StaffRole
        """
        trigger_word = trigger_word.lower()
        if trigger_word in self.reply_autoroles.get(ctx.guild.id, {}):
            return await ctx.send(f"❌ A reply autorole for `{trigger_word}` already exists.")
        
        if role >= ctx.guild.me.top_role:
            return await ctx.send("❌ I cannot assign roles that are equal to or higher than my top role.")

        if ctx.guild.id not in self.reply_autoroles:
            self.reply_autoroles[ctx.guild.id] = {}
        self.reply_autoroles[ctx.guild.id][trigger_word] = role.id
        # In a real bot, save this to Firestore here
        await ctx.send(f"✅ Reply autorole created: Replying with `{trigger_word}` will give the `{role.name}` role.")

    @autorole_reply.command(name="edit", help="Edits an existing reply-triggered autorole.")
    @commands.has_permissions(manage_roles=True)
    async def autorole_reply_edit(self, ctx, trigger_word: str, *, new_role: discord.Role):
        """
        Edits the role associated with an existing reply-triggered autorole.
        Usage: XTRM autorole reply edit "<trigger_word>" <@new_role/New Role Name>
        Example: XTRM autorole reply edit "Staff" @SeniorStaff
        """
        trigger_word = trigger_word.lower()
        if ctx.guild.id not in self.reply_autoroles or trigger_word not in self.reply_autoroles[ctx.guild.id]:
            return await ctx.send(f"❌ No reply autorole found for trigger `{trigger_word}`.")
        
        if new_role >= ctx.guild.me.top_role:
            return await ctx.send("❌ I cannot assign roles that are equal to or higher than my top role.")

        old_role_id = self.reply_autoroles[ctx.guild.id][trigger_word]
        old_role = ctx.guild.get_role(old_role_id)
        
        self.reply_autoroles[ctx.guild.id][trigger_word] = new_role.id
        # In a real bot, update this in Firestore here
        await ctx.send(f"✅ Reply autorole for `{trigger_word}` updated from `{old_role.name if old_role else 'Unknown Role'}` to `{new_role.name}`.")

    @autorole_reply.command(name="delete", help="Deletes a reply-triggered autorole.")
    @commands.has_permissions(manage_roles=True)
    async def autorole_reply_delete(self, ctx, trigger_word: str):
        """
        Deletes a reply-triggered autorole.
        Usage: XTRM autorole reply delete "<trigger_word>"
        Example: XTRM autorole reply delete "Staff"
        """
        trigger_word = trigger_word.lower()
        if ctx.guild.id in self.reply_autoroles and trigger_word in self.reply_autoroles[ctx.guild.id]:
            del self.reply_autoroles[ctx.guild.id][trigger_word]
            # In a real bot, delete from Firestore here
            await ctx.send(f"✅ Reply autorole for `{trigger_word}` deleted.")
        else:
            await ctx.send(f"❌ No reply autorole found for trigger `{trigger_word}`.")

    @autorole_reply.command(name="list", help="Lists all reply-triggered autoroles.")
    @commands.has_permissions(manage_roles=True)
    async def autorole_reply_list(self, ctx):
        """
        Lists all configured reply-triggered autoroles for this server.
        Usage: XTRM autorole reply list
        """
        if ctx.guild.id not in self.reply_autoroles or not self.reply_autoroles[ctx.guild.id]:
            return await ctx.send("No reply-triggered autoroles configured for this server.")
        
        embed = discord.Embed(
            title="Reply-Triggered Autoroles",
            description="Here are the configured reply autoroles:",
            color=discord.Color.blue()
        )
        for trigger, role_id in self.reply_autoroles[ctx.guild.id].items():
            role = ctx.guild.get_role(role_id)
            role_name = role.name if role else "Unknown Role (ID: {role_id})"
            embed.add_field(name=f"Trigger: `{trigger}`", value=f"Role: `{role_name}`", inline=False)
        await ctx.send(embed=embed)

    @autorole_reply.command(name="test", help="Tests a reply-triggered autorole.")
    @commands.has_permissions(manage_roles=True)
    async def autorole_reply_test(self, ctx, trigger_word: str):
        """
        Tests if a given trigger word has an associated reply-triggered autorole.
        Usage: XTRM autorole reply test "<trigger_word>"
        Example: XTRM autorole reply test "Staff"
        """
        trigger_word = trigger_word.lower()
        if ctx.guild.id in self.reply_autoroles and trigger_word in self.reply_autoroles[ctx.guild.id]:
            role_id = self.reply_autoroles[ctx.guild.id][trigger_word]
            role = ctx.guild.get_role(role_id)
            role_name = role.name if role else "Unknown Role (ID: {role_id})"
            await ctx.send(f"✅ Trigger `{trigger_word}` is configured to give the `{role_name}` role.")
        else:
            await ctx.send(f"❌ No reply autorole found for trigger `{trigger_word}`.")

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listens for messages that are replies and contain a trigger word for autoroles.
        """
        if message.author.bot or not message.reference or not message.reference.message_id:
            return # Ignore bots, non-replies, or replies without a valid message ID

        # Ensure the message is not a bot command
        current_prefixes = self.bot.command_prefix
        if not isinstance(current_prefixes, tuple):
            current_prefixes = (current_prefixes,)
        for prefix in current_prefixes:
            if message.content.lower().startswith(prefix.lower()):
                return # Do not trigger autorole if it's a bot command

        guild_id = message.guild.id
        if guild_id not in self.reply_autoroles or not self.reply_autoroles[guild_id]:
            return # No reply autoroles configured for this guild

        # Fetch the replied-to message to get the author
        try:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            target_member = replied_message.author
        except discord.NotFound:
            return # Replied message not found
        except discord.HTTPException:
            return # Error fetching message

        if target_member.bot:
            return # Don't give roles to bots

        msg_content_lower = message.content.lower()

        for trigger_word, role_id in self.reply_autoroles[guild_id].items():
            if msg_content_lower == trigger_word: # Exact match for the trigger word
                role = message.guild.get_role(role_id)
                if role and role not in target_member.roles:
                    try:
                        # Check if bot can manage this role
                        if role >= message.guild.me.top_role:
                            await message.channel.send(f"❌ I cannot assign the role `{role.name}` because it is higher than or equal to my top role.")
                            return

                        await target_member.add_roles(role, reason=f"Reply-triggered autorole: '{trigger_word}' by {message.author.display_name}")
                        await message.channel.send(f"✅ {target_member.display_name} has been given the `{role.name}` role by {message.author.display_name}'s reply!")
                    except discord.Forbidden:
                        await message.channel.send(f"❌ I don't have permission to assign the `{role.name}` role to {target_member.display_name}.")
                    except Exception as e:
                        print(f"Error assigning autorole: {e}")
                return # Only process one autorole per reply
            
async def setup(bot):
    """
    Adds the Moderation cog to the bot.
    """
    await bot.add_cog(Moderation(bot))
