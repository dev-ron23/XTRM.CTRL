# bot.py
import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

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

def get_command_examples(prefix, command_name):
    """
    Helper function to provide specific examples for commands.
    """
    examples = []
    if command_name == "kick":
        examples = [
            f"**Kick a user with a reason:** `{prefix}kick @User#1234 Spamming in general`",
            f"**Kick a user without a reason:** `{prefix}kick @AnotherUser`"
        ]
    elif command_name == "ban":
        examples = [
            f"**Ban a user for rule breaking:** `{prefix}ban @User#1234 Rule breaking`",
            f"**Ban a malicious actor:** `{prefix}ban @BadActor Severe violation`"
        ]
    elif command_name == "mute":
        examples = [
            f"**Mute for 30 minutes:** `{prefix}mute @User#1234 30m Excessive chat`",
            f"**Mute for 1 hour:** `{prefix}mute @AnotherUser 1h`",
            f"**Mute indefinitely:** `{prefix}mute @ThirdUser No reason`"
        ]
    elif command_name == "unmute":
        examples = [
            f"**Unmute a user:** `{prefix}unmute @User#1234`",
            f"**Unmute with a note:** `{prefix}unmute @AnotherUser Mute expired`"
        ]
    elif command_name == "tempban":
        examples = [
            f"**Temporary ban for 1 day:** `{prefix}tempban @User#1234 1d Temporary ban for spam`",
            f"**Temporary ban for 3 hours:** `{prefix}tempban @AnotherUser 3h`"
        ]
    elif command_name == "trial":
        examples = [
            f"**Add 'Trial Member' role:** `{prefix}trial add @NewMember Starting trial period`",
            f"**Remove 'Trial Member' role:** `{prefix}trial remove @OldMember Trial ended`"
        ]
    elif command_name == "manageperms":
        examples = [
            f"**Disable send messages in #general:** `{prefix}manageperms @User#1234 #general disable`",
            f"**Enable send messages in #private-chat:** `{prefix}manageperms @User#1234 #private-chat enable`"
        ]
    elif command_name == "manageroles":
        examples = [
            f"**Give a role:** `{prefix}manageroles give @User#1234 @Member Role`",
            f"**Remove a role:** `{prefix}manageroles remove @User#1234 Old Role`"
        ]
    elif command_name == "autorole": # This is a group, its examples will be for subcommands
        examples = [] # This function is for direct commands, not groups.
    elif command_name == "reply": # Subcommand of autorole
        examples = [
            f"**Create reply autorole:** `{prefix}autorole reply create \"Staff\" @StaffRole`",
            f"**Edit reply autorole:** `{prefix}autorole reply edit \"Staff\" @NewStaffRole`",
            f"**Delete reply autorole:** `{prefix}autorole reply delete \"Staff\"`",
            f"**List all reply autoroles:** `{prefix}autorole reply list`",
            f"**Test a reply autorole:** `{prefix}autorole reply test \"Staff\"`"
        ]
    elif command_name == "antinuke":
        examples = [
            f"**Enable Anti-Nuke:** `{prefix}antinuke enable`",
            f"**View Anti-Nuke settings:** `{prefix}antinuke settings`",
            f"**Configure Anti-Nuke thresholds:** `{prefix}antinuke modify 5 ban`",
            f"**Set logging channel:** `{prefix}antinuke logging #security-logs`"
        ]
    elif command_name == "accesscontrol":
        examples = [
            f"**Grant bot access:** `{prefix}accesscontrol grant @User#1234`",
            f"**Revoke bot access:** `{prefix}accesscontrol revoke @User#1234`",
            f"**Reset user's access:** `{prefix}accesscontrol reset @User#1234`"
        ]
    elif command_name == "serverlock":
        examples = [
            f"**Lock server during raid:** `{prefix}serverlock Raid detected`",
            f"**Unlock server:** `{prefix}serverunlock`"
        ]
    elif command_name == "afk":
        examples = [
            f"**Set AFK status with reason:** `{prefix}afk Taking a quick break`",
            f"**Set AFK status without reason:** `{prefix}afk`",
            f"**Remove AFK status:** Send any message in any channel."
        ]
    elif command_name == "maintenance":
        examples = [
            f"**Toggle maintenance mode:** `{prefix}maintenance` (toggles mode)"
        ]
    elif command_name == "voicerole":
        examples = [
            f"**Setup voice role:** `{prefix}voicerole setup @VoiceUserRole`",
            f"**Enable voice role feature:** `{prefix}voicerole enable`",
            f"**Disable voice role feature:** `{prefix}voicerole disable`"
        ]
    elif command_name == "customcmd":
        examples = [
            f"**Create text command:** `{prefix}customcmd create welcome text \"Welcome, {{user}}!\"`",
            f"**Create embed command:** `{prefix}customcmd create rules embed \"Check #rules!\" --title \"Server Rules\" --color #FF0000`",
            f"**Edit existing command:** `{prefix}customcmd edit welcome \"Updated: Welcome to the server!\"`",
            f"**Delete a command:** `{prefix}customcmd delete welcome`",
            f"**List all commands:** `{prefix}customcmd list`"
        ]
    elif command_name == "autoresponder":
        examples = [
            f"**Create text autoresponder:** `{prefix}autoresponder create \"hello\" text \"Hi there!\"`",
            f"**Create embed autoresponder:** `{prefix}autoresponder create \"rules?\" embed \"Check #rules!\" --title \"Rules\" --color #FF0000`",
            f"**Edit autoresponder:** `{prefix}autoresponder edit \"hello\" \"Hello, {{user}}! How can I help?\"`",
            f"**Delete autoresponder:** `{prefix}autoresponder delete \"rules?\"`",
            f"**List all autoresponders:** `{prefix}autoresponder list`"
        ]
    return examples

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
    footer_text = f"Help Requested by {ctx.author.display_name}"
    
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

            # Examples
            examples = get_command_examples(ctx.prefix, command.name)
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

            commands_output_fields = [] # Will store tuples of (name, value, inline) for embed fields

            for command in target_cog.get_commands():
                if not command.hidden:
                    if isinstance(command, commands.Group):
                        # Handle group commands and their subcommands
                        group_commands_list = []
                        for subcommand in command.commands:
                            if not subcommand.hidden:
                                usage_sub = f"`{ctx.prefix}{command.name} {subcommand.name} {subcommand.signature}`"
                                description_sub = subcommand.help.splitlines()[0] if subcommand.help else "No description provided."
                                examples_sub = get_command_examples(ctx.prefix, subcommand.name)

                                subcommand_info = f"**`{subcommand.name.upper()}`**\n"
                                subcommand_info += f"  * {description_sub}\n"
                                subcommand_info += f"  Syntax: {usage_sub}\n"
                                if examples_sub:
                                    subcommand_info += f"  Examples:\n    " + "\n    ".join(examples_sub) + "\n"
                                group_commands_list.append(subcommand_info)
                        
                        if group_commands_list:
                            commands_output_fields.append((
                                f"`{command.name.upper()} GROUP`",
                                "\n".join(group_commands_list),
                                False
                            ))
                        else:
                            commands_output_fields.append((
                                f"`{command.name.upper()} GROUP`",
                                "No subcommands found.",
                                False
                            ))
                    else:
                        # Handle regular commands
                        usage = f"`{ctx.prefix}{command.name} {command.signature}`"
                        description = command.help.splitlines()[0] if command.help else "No description provided."
                        examples_cmd = get_command_examples(ctx.prefix, command.name)

                        command_info = f"**`{command.name.upper()}`**\n"
                        command_info += f"  * {description}\n"
                        command_info += f"  Syntax: {usage}\n"
                        if examples_cmd:
                            command_info += f"  Examples:\n    " + "\n    ".join(examples_cmd) + "\n"
                        
                        commands_output_fields.append((
                            f"`{command.name.upper()}`",
                            command_info,
                            False
                        ))

            if commands_output_fields:
                # Add fields to embed
                for name, value, inline in commands_output_fields:
                    embed.add_field(name=name, value=value, inline=inline)
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
        
        
        
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080)) # Use PORT from environment or default

# Start the Flask server in a separate thread
flask_thread = Thread(target=run_flask)
flask_thread.daemon = True # Allow the main program to exit even if this thread is running
flask_thread.start()

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
