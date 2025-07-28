# bot.py
import discord
from discord.ext import commands
import os

# Define the bot's prefixes
# The bot will respond to commands starting with 'XTRM ' or 'xtrm '
# Note the space after the prefix is crucial for proper parsing.
PREFIXES = ("XTRM ", "xtrm ")

# --- Bot Initialization ---
# We use intents to specify which events our bot needs to listen to.
# For moderation and security features, many intents are required.
# Make sure to enable all necessary intents in your Discord Developer Portal.
intents = discord.Intents.default()
intents.members = True  # Required for member-related events (joins, leaves, kicks, bans)
intents.messages = True  # Required for message content (automod, custom commands, autoresponders)
intents.message_content = True # Explicitly required for accessing message.content in Discord.py 2.0+
intents.guilds = True  # Required for guild-related events (channel/role creation/deletion)
intents.voice_states = True # Required for voice role feature (on_voice_state_update)

# Create the bot instance with defined prefixes and intents
bot = commands.Bot(command_prefix=PREFIXES, intents=intents)

# --- Bot Events ---
@bot.event
async def on_ready():
    """
    Event that fires when the bot successfully connects to Discord.
    Prints a confirmation message and loads all cogs.
    """
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('Bot is ready!')
    await load_cogs() # Load all cogs when the bot is ready

async def load_cogs():
    """
    Loads all command cogs from the 'cogs' directory.
    Each cog represents a module (e.g., Security, Moderation).
    """
    print("Loading cogs...")
    # List of cogs to load. Each entry corresponds to a file in the 'cogs' directory
    # (e.g., 'security' maps to 'cogs/security.py').
    cogs_to_load = [
        'cogs.security',
        'cogs.moderation',
        'cogs.emergency',
        'cogs.utility',
        'cogs.custom_commands',
        'cogs.autoresponders'
    ]
    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(f'Successfully loaded {cog}')
        except Exception as e:
            print(f'Failed to load {cog}: {e}')
    print("All cogs loaded (or attempted to load).")

# --- Custom Help Command (XTRM advhelp) ---
# This command will only respond to the prefix command 'XTRM advhelp'
# and will NOT appear in Discord's native slash command suggestions.
@bot.command(name="advhelp", help="Shows advanced help for bot modules and commands.")
async def advhelp(ctx, *, query: str = None):
    """
    Provides advanced, detailed help for bot modules or specific commands within modules.
    Usage: XTRM advhelp [module_name or command_name]
    Example: XTRM advhelp Security
    Example: XTRM advhelp antinuke
    Example: XTRM advhelp
    """
    # High-tech, unique aesthetic
    embed_color = 0x00FFFF # A vibrant cyan
    thumbnail_url = "https://placehold.co/128x128/000000/00FFFF?text=XTRM" # Placeholder for a tech-style icon
    footer_text = f"XTRM Bot // System Online // Requested by {ctx.author.display_name}"
    
    if query:
        query_lower = query.lower()
        
        # Try to find a specific command first
        command = bot.get_command(query_lower)
        if command and not command.hidden:
            embed = discord.Embed(
                title=f"≪ Command: {command.name.capitalize()} ≫",
                description=f"```fix\n{command.help if command.help else 'No detailed description available.'}\n```\n",
                color=embed_color
            )
            embed.set_thumbnail(url=thumbnail_url)
            embed.set_footer(text=footer_text, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

            # Usage/Syntax
            usage_text = f"```\n{ctx.prefix}{command.name} {command.signature}\n```"
            embed.add_field(name="`SYNTAX`", value=usage_text, inline=False)

            # Examples - More specific and detailed examples
            examples = []
            if command.name == "kick":
                examples = [
                    f"**Kick a user with a reason:** `{ctx.prefix}kick @User#1234 Spamming in general`",
                    f"**Kick a user without a reason:** `{ctx.prefix}kick @AnotherUser`"
                ]
            elif command.name == "ban":
                examples = [
                    f"**Ban a user for rule breaking:** `{ctx.prefix}ban @User#1234 Rule breaking`",
                    f"**Ban a malicious actor:** `{ctx.prefix}ban @BadActor Severe violation`"
                ]
            elif command.name == "mute":
                examples = [
                    f"**Mute for 30 minutes:** `{ctx.prefix}mute @User#1234 30m Excessive chat`",
                    f"**Mute for 1 hour:** `{ctx.prefix}mute @AnotherUser 1h`",
                    f"**Mute indefinitely:** `{ctx.prefix}mute @ThirdUser No reason`"
                ]
            elif command.name == "unmute":
                examples = [
                    f"**Unmute a user:** `{ctx.prefix}unmute @User#1234`",
                    f"**Unmute with a note:** `{ctx.prefix}unmute @AnotherUser Mute expired`"
                ]
            elif command.name == "tempban":
                examples = [
                    f"**Temporary ban for 1 day:** `{ctx.prefix}tempban @User#1234 1d Temporary ban for spam`",
                    f"**Temporary ban for 3 hours:** `{ctx.prefix}tempban @AnotherUser 3h`"
                ]
            elif command.name == "trial":
                examples = [
                    f"**Add 'Trial Member' role:** `{ctx.prefix}trial add @NewMember Starting trial period`",
                    f"**Remove 'Trial Member' role:** `{ctx.prefix}trial remove @OldMember Trial ended`"
                ]
            elif command.name == "manageperms":
                examples = [
                    f"**Disable send messages in #general:** `{ctx.prefix}manageperms @User#1234 #general disable`",
                    f"**Enable send messages in #private-chat:** `{ctx.prefix}manageperms @User#1234 #private-chat enable`"
                ]
            elif command.name == "manageroles":
                examples = [
                    f"**Give a role:** `{ctx.prefix}manageroles give @User#1234 @Member Role`",
                    f"**Remove a role:** `{ctx.prefix}manageroles remove @User#1234 Old Role`"
                ]
            elif command.name == "autorole": # New Autorole command group
                examples = [
                    f"**Create reply autorole:** `{ctx.prefix}autorole reply create \"Staff\" @StaffRole`",
                    f"**Edit reply autorole:** `{ctx.prefix}autorole reply edit \"Staff\" @NewStaffRole`",
                    f"**Delete reply autorole:** `{ctx.prefix}autorole reply delete \"Staff\"`",
                    f"**List all reply autoroles:** `{ctx.prefix}autorole reply list`",
                    f"**Test a reply autorole:** `{ctx.prefix}autorole reply test \"Staff\"`"
                ]
            elif command.name == "antinuke":
                examples = [
                    f"**Enable Anti-Nuke:** `{ctx.prefix}antinuke enable`",
                    f"**View Anti-Nuke settings:** `{ctx.prefix}antinuke settings`",
                    f"**Configure Anti-Nuke thresholds:** `{ctx.prefix}antinuke modify 5 ban`",
                    f"**Set logging channel:** `{ctx.prefix}antinuke logging #security-logs`"
                ]
            elif command.name == "accesscontrol":
                examples = [
                    f"**Grant bot access:** `{ctx.prefix}accesscontrol grant @User#1234`",
                    f"**Revoke bot access:** `{ctx.prefix}accesscontrol revoke @User#1234`",
                    f"**Reset user's access:** `{ctx.prefix}accesscontrol reset @User#1234`"
                ]
            elif command.name == "serverlock":
                examples = [
                    f"**Lock server during raid:** `{ctx.prefix}serverlock Raid detected`",
                    f"**Unlock server:** `{ctx.prefix}serverunlock`"
                ]
            elif command.name == "afk":
                examples = [
                    f"**Set AFK status with reason:** `{ctx.prefix}afk Taking a quick break`",
                    f"**Set AFK status without reason:** `{ctx.prefix}afk`",
                    f"**Remove AFK status:** Send any message in any channel."
                ]
            elif command.name == "maintenance":
                examples = [
                    f"**Toggle maintenance mode:** `{ctx.prefix}maintenance`"
                ]
            elif command.name == "voicerole":
                examples = [
                    f"**Setup voice role:** `{ctx.prefix}voicerole setup @VoiceUserRole`",
                    f"**Enable voice role feature:** `{ctx.prefix}voicerole enable`",
                    f"**Disable voice role feature:** `{ctx.prefix}voicerole disable`"
                ]
            elif command.name == "customcmd":
                examples = [
                    f"**Create text command:** `{ctx.prefix}customcmd create welcome text \"Welcome, {user}!\"`",
                    f"**Create embed command:** `{ctx.prefix}customcmd create rules embed \"Check #rules!\" --title \"Server Rules\" --color #FF0000`",
                    f"**Edit existing command:** `{ctx.prefix}customcmd edit welcome \"Updated: Welcome to the server!\"`",
                    f"**Delete a command:** `{ctx.prefix}customcmd delete welcome`",
                    f"**List all commands:** `{ctx.prefix}customcmd list`"
                ]
            elif command.name == "autoresponder":
                examples = [
                    f"**Create text autoresponder:** `{ctx.prefix}autoresponder create \"hello\" text \"Hi there!\"`",
                    f"**Create embed autoresponder:** `{ctx.prefix}autoresponder create \"rules?\" embed \"Check #rules!\" --title \"Rules\" --color #FF0000`",
                    f"**Edit autoresponder:** `{ctx.prefix}autoresponder edit \"hello\" \"Hello, {user}! How can I help?\"`",
                    f"**Delete autoresponder:** `{ctx.prefix}autoresponder delete \"rules?\"`",
                    f"**List all autoresponders:** `{ctx.prefix}autoresponder list`"
                ]
            # Add more specific examples for other commands here

            if examples:
                embed.add_field(name="`EXAMPLES`", value="\n".join(examples), inline=False)

            # Aliases
            if command.aliases:
                embed.add_field(name="`ALIASES`", value=", ".join([f"`{alias}`" for alias in command.aliases]), inline=False)
            
            # Permissions
            required_perms = []
            if command.checks:
                for check in command.checks:
                    if hasattr(check, 'predicate') and hasattr(check.predicate, '__qualname__'):
                        if 'has_permissions' in check.predicate.__qualname__:
                            try:
                                if hasattr(check.predicate, '__closure__') and check.predicate.__closure__:
                                    for cell in check.predicate.__closure__:
                                        if isinstance(cell.cell_contents, dict):
                                            for perm, value in cell.cell_contents.items():
                                                if value:
                                                    required_perms.append(perm.replace('_', ' ').title())
                            except Exception:
                                pass
                    elif 'is_owner' in check.__qualname__:
                        required_perms.append("Bot Owner")
            
            if required_perms:
                embed.add_field(name="`REQUIRED PERMISSIONS`", value=", ".join(required_perms), inline=False)
            else:
                embed.add_field(name="`REQUIRED PERMISSIONS`", value="None (or not explicitly defined)", inline=False)

            await ctx.send(embed=embed)
            return

        # If not a command, try to find a module (cog)
        target_cog = None
        for cog_name, cog_obj in bot.cogs.items():
            if cog_name.lower() == query_lower:
                target_cog = cog_obj
                break

        if target_cog:
            embed = discord.Embed(
                title=f"≪ Module: {target_cog.qualified_name} ≫",
                description=f"```fix\nOverview of commands within the {target_cog.qualified_name} module.\n```",
                color=embed_color
            )
            embed.set_thumbnail(url=thumbnail_url)
            embed.set_footer(text=f"Use `XTRM advhelp <command_name>` for specific command details. | {footer_text}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

            commands_in_module = []
            for command in target_cog.get_commands():
                if not command.hidden:
                    commands_in_module.append(f"`{command.name}`")
            
            if commands_in_module:
                embed.add_field(name="`AVAILABLE COMMANDS`", value="```\n" + ", ".join(commands_in_module) + "\n```", inline=False)
            else:
                embed.add_field(name="`AVAILABLE COMMANDS`", value="No commands found in this module.", inline=False)
            
            await ctx.send(embed=embed)
            return
        
        await ctx.send(f"❌ Could not find a command or module named `{query}`. Use `XTRM advhelp` to list all modules.")

    else:
        # Show a list of all available modules if no specific module or command is requested
        embed = discord.Embed(
            title="✨ XTRM BOT // ADVANCED HELP SYSTEM ✨",
            description="```fix\nNavigate the bot's powerful features. Select a module for detailed commands, or type XTRM advhelp <command_name> for specific command info.\n```\n",
            color=embed_color
        )
        embed.set_thumbnail(url=thumbnail_url)
        embed.set_footer(text=footer_text, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        module_descriptions = {
            "Security": "🛡️ Protect your server with advanced anti-nuke, raid mode, and access controls.",
            "Moderation": "🛠️ Tools for effective community management, warnings, mutes, and role handling.",
            "Emergency": "🚨 Critical commands for immediate server lockdown and mass actions.",
            "Utility": "⚙️ General purpose commands including AFK, server info, and voice roles.",
            "CustomCommands": "✍️ Create personalized, dynamic commands for your server.",
            "Autoresponders": "💬 Set up advanced automatic replies based on keywords and phrases."
        }

        module_list_str = []
        # Sort cogs alphabetically for consistent display
        sorted_cogs = sorted(bot.cogs.items(), key=lambda item: item[0])
        for cog_name, cog_obj in sorted_cogs:
            description = module_descriptions.get(cog_name, "No description available.")
            module_list_str.append(f"**`{cog_name}`** - {description}")
        
        if module_list_str:
            embed.add_field(name="`AVAILABLE MODULES`", value="\n".join(module_list_str), inline=False)
        else:
            embed.add_field(name="`AVAILABLE MODULES`", value="No modules found.", inline=False)

        await ctx.send(embed=embed)

# --- Run the Bot ---
# It's highly recommended to use environment variables for your bot token
# For example, set an environment variable named 'DISCORD_BOT_TOKEN'
# before running your bot.
# Example: export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
# If you run this in a local environment, you might need a .env file and `python-dotenv`.
# For Canvas, you would typically paste the token directly if not using env vars.
try:
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        print("Error: DISCORD_BOT_TOKEN environment variable not set.")
        print("Please set the DISCORD_BOT_TOKEN environment variable with your bot's token.")
    else:
        bot.run(bot_token)
except Exception as e:
    print(f"An error occurred while running the bot: {e}")
