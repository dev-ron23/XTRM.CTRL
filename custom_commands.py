# cogs/custom_commands.py
import discord
from discord.ext import commands

# Import PREFIXES from bot.py (assuming bot.py is in the parent directory)
# This is a common pattern for shared configurations.
# You might need to adjust this import based on your exact file structure.
# For this setup, we'll assume it's accessible or passed during cog loading.
# A more robust solution would be to pass it via bot.py's __init__ or a config file.
# For now, we'll redefine it for standalone clarity, but be aware of this in a larger project.
# Alternatively, you can access bot.command_prefix within the cog.
PREFIXES = ("XTRM ", "xtrm ") # Redefine for standalone cog file clarity

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.custom_cmds = {} # In-memory storage for custom commands (for demonstration)
                              # In a real bot, use a database (e.g., Firestore) for persistence.

    @commands.group(name="customcmd", invoke_without_command=True, help="Manages custom commands.")
    @commands.has_permissions(manage_guild=True)
    async def customcmd(self, ctx):
        """
        Base command for managing custom commands.
        Usage: XTRM customcmd [subcommand]
        Example: XTRM customcmd list
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify a Custom Command subcommand (e.g., `create`, `list`). Use `XTRM advhelp CustomCommands` for more info.")

    @customcmd.command(name="create", help="Creates a new custom command.")
    @commands.has_permissions(manage_guild=True)
    async def create_custom_cmd(self, ctx, name: str, cmd_type: str, *, content: str):
        """
        Creates a new custom command.
        Usage: XTRM customcmd create <name> <type> <content>
        <type> can be: text, embed, image
        Example: XTRM customcmd create hello text "Hello, {user}!"
        Example (Embed): XTRM customcmd create rules embed "Read the rules in {channel:rules}!" --title "Server Rules" --color #FF0000
        """
        name = name.lower()
        cmd_type = cmd_type.lower()

        if name in self.custom_cmds:
            await ctx.send(f"❌ Custom command `{name}` already exists. Use `XTRM customcmd edit` to modify it.")
            return

        if cmd_type not in ["text", "embed", "image"]:
            await ctx.send("❌ Invalid command type. Must be `text`, `embed`, or `image`.")
            return

        # Parse content and options (simplified for demonstration)
        # In a full implementation, you'd parse --title, --color, etc. for embeds.
        self.custom_cmds[name] = {"type": cmd_type, "content": content}
        await ctx.send(f"✅ Custom command `{name}` created successfully!")

    @customcmd.command(name="list", help="Lists all custom commands.")
    async def list_custom_cmds(self, ctx):
        """
        Lists all currently configured custom commands.
        Usage: XTRM customcmd list
        """
        if not self.custom_cmds:
            await ctx.send("No custom commands have been created yet.")
            return

        embed = discord.Embed(
            title="Custom Commands",
            description="Here are the custom commands configured for this server:",
            color=discord.Color.purple()
        )
        for name, data in self.custom_cmds.items():
            embed.add_field(name=f"`{name}`", value=f"Type: `{data['type']}`", inline=True)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listens for messages to trigger custom commands.
        """
        if message.author.bot:
            return # Ignore bot messages

        # Check for bot prefixes
        # Accessing bot.command_prefix directly for robustness
        current_prefixes = self.bot.command_prefix if isinstance(self.bot.command_prefix, tuple) else (self.bot.command_prefix,)

        for prefix in current_prefixes:
            if message.content.lower().startswith(prefix.lower()):
                cmd_name = message.content[len(prefix):].split(' ')[0].lower()
                
                if cmd_name in self.custom_cmds:
                    cmd_data = self.custom_cmds[cmd_name]
                    
                    # Process variables like {user}, {channel:name}, {server}, etc.
                    processed_content = cmd_data['content'].replace("{user}", message.author.mention)
                    processed_content = processed_content.replace("{server}", message.guild.name if message.guild else "Unknown Server")
                    
                    # Handle {channel:name} variable
                    if "{channel:" in processed_content and "}" in processed_content:
                        import re
                        channel_matches = re.findall(r"\{channel:([^}]+)\}", processed_content)
                        for channel_name in channel_matches:
                            target_channel = discord.utils.get(message.guild.channels, name=channel_name)
                            if target_channel:
                                processed_content = processed_content.replace(f"{{channel:{channel_name}}}", target_channel.mention)
                            else:
                                processed_content = processed_content.replace(f"{{channel:{channel_name}}}", f"#{channel_name} (not found)")

                    if cmd_data['type'] == "text":
                        await message.channel.send(processed_content)
                    elif cmd_data['type'] == "embed":
                        # This is a basic embed. Full implementation would parse more options.
                        embed = discord.Embed(description=processed_content, color=discord.Color.blue())
                        # Example of parsing a simple title from content (needs more robust parsing)
                        if "--title " in processed_content:
                            title_start = processed_content.find("--title ") + len("--title ")
                            title_end = processed_content.find(" --", title_start)
                            if title_end == -1: title_end = len(processed_content)
                            embed.title = processed_content[title_start:title_end].strip().strip('"')
                        await message.channel.send(embed=embed)
                    elif cmd_data['type'] == "image":
                        await message.channel.send(processed_content) # Assuming content is a direct image URL
                    return # Stop processing after a custom command is triggered

async def setup(bot):
    """
    Adds the CustomCommands cog to the bot.
    """
    await bot.add_cog(CustomCommands(bot))
