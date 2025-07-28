# cogs/autoresponders.py
import discord
from discord.ext import commands
import re # Import regex for advanced variable parsing

# Import PREFIXES from bot.py (assuming bot.py is in the parent directory)
# For standalone cog file clarity, we'll keep a local PREFIXES, but on_message will use bot.command_prefix.
PREFIXES = ("XTRM ", "xtrm ") 

class Autoresponders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.qualified_name is automatically set by discord.py
        self.autoresponders = {} # In-memory storage for autoresponders (for demonstration)
                                 # In a real bot, use a database (e.g., Firestore) for persistence.

    @commands.group(name="autoresponder", invoke_without_command=True, help="Manages autoresponders.")
    @commands.has_permissions(manage_guild=True)
    async def autoresponder(self, ctx):
        """
        Base command for managing autoresponders.
        Usage: XTRM autoresponder [subcommand]
        Example: XTRM autoresponder list
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify an Autoresponder subcommand (e.g., `create`, `list`, `edit`, `delete`). Use `XTRM advhelp Autoresponders` for more info.")

    @autoresponder.command(name="create", help="Creates a new autoresponder.")
    @commands.has_permissions(manage_guild=True)
    async def create_autoresponder(self, ctx, trigger: str, response_type: str, *, content: str):
        """
        Creates a new autoresponder that replies when a specific trigger is detected.
        Usage: XTRM autoresponder create "<trigger>" <type> <content> [--match <type>] [--channel <channel>] [--title "Title"] [--color #HEX]
        <type> can be: text, embed, image
        <trigger> can be a word or phrase (use quotes for phrases).
        --match: exact, contains (default: contains)
        Example: XTRM autoresponder create "hello bot" text "Hello there, {user}!"
        Example (Embed): XTRM autoresponder create "rules?" embed "Check out #rules!" --title "Rules Reminder" --color #FFD700
        """
        trigger = trigger.lower()
        response_type = response_type.lower()

        if trigger in self.autoresponders:
            await ctx.send(f"❌ Autoresponder for trigger `{trigger}` already exists. Use `XTRM autoresponder edit` to modify it.")
            return

        if response_type not in ["text", "embed", "image"]:
            await ctx.send("❌ Invalid response type. Must be `text`, `embed`, or `image`.")
            return
        
        # Parse arguments for options like --match, --title, --color
        match_type = "contains"
        title = None
        color = None
        
        # Regex to find options and remove them from content
        content_parts = content.split(' --')
        main_content = content_parts[0]
        options_str = ' --' + ' --'.join(content_parts[1:]) if len(content_parts) > 1 else ''

        match_match = re.search(r'--match\s+(exact|contains)', options_str, re.IGNORECASE)
        if match_match:
            match_type = match_match.group(1).lower()
            options_str = options_str.replace(match_match.group(0), '')

        title_match = re.search(r'--title\s+"([^"]+)"', options_str)
        if title_match:
            title = title_match.group(1)
            options_str = options_str.replace(title_match.group(0), '')
        
        color_match = re.search(r'--color\s+(#[0-9a-fA-F]{6})', options_str)
        if color_match:
            try:
                color = int(color_match.group(1)[1:], 16) # Convert hex string to integer
            except ValueError:
                color = None # Invalid hex color
            options_str = options_str.replace(color_match.group(0), '')
        
        # Add more parsing for --image, --thumbnail, --footer, --field etc. as needed

        self.autoresponders[trigger] = {
            "type": response_type,
            "content": main_content.strip(), # Use the content without options
            "match_type": match_type,
            "title": title,
            "color": color
            # Store other parsed options here
        }
        # In a real bot, save this to Firestore here
        await ctx.send(f"✅ Autoresponder for trigger `{trigger}` created successfully!")

    @autoresponder.command(name="edit", help="Edits an existing autoresponder.")
    @commands.has_permissions(manage_guild=True)
    async def edit_autoresponder(self, ctx, trigger: str, *, new_content: str):
        """
        Edits the content of an existing autoresponder.
        Usage: XTRM autoresponder edit "<trigger>" <new_content> [--match <type>] [--title "Title"] [--color #HEX]
        Example: XTRM autoresponder edit "hello bot" "Updated greeting: Hello, {user}!" --match exact
        """
        trigger = trigger.lower()

        if trigger not in self.autoresponders:
            await ctx.send(f"❌ Autoresponder for trigger `{trigger}` does not exist.")
            return

        # Parse new_content for options, similar to create
        content_parts = new_content.split(' --')
        main_content = content_parts[0]
        options_str = ' --' + ' --'.join(content_parts[1:]) if len(content_parts) > 1 else ''

        # Update existing data with new content and potentially new options
        self.autoresponders[trigger]["content"] = main_content.strip()

        match_match = re.search(r'--match\s+(exact|contains)', options_str, re.IGNORECASE)
        if match_match:
            self.autoresponders[trigger]["match_type"] = match_match.group(1).lower()
        
        title_match = re.search(r'--title\s+"([^"]+)"', options_str)
        if title_match:
            self.autoresponders[trigger]["title"] = title_match.group(1)
        
        color_match = re.search(r'--color\s+(#[0-9a-fA-F]{6})', options_str)
        if color_match:
            try:
                self.autoresponders[trigger]["color"] = int(color_match.group(1)[1:], 16)
            except ValueError:
                pass # Ignore invalid color
        
        # In a real bot, update this in Firestore here
        await ctx.send(f"✅ Autoresponder for trigger `{trigger}` updated successfully!")

    @autoresponder.command(name="delete", help="Deletes an existing autoresponder.")
    @commands.has_permissions(manage_guild=True)
    async def delete_autoresponder(self, ctx, trigger: str):
        """
        Deletes a specified autoresponder.
        Usage: XTRM autoresponder delete "<trigger>"
        Example: XTRM autoresponder delete "hello bot"
        """
        trigger = trigger.lower()
        if trigger in self.autoresponders:
            del self.autoresponders[trigger]
            # In a real bot, delete from Firestore here
            await ctx.send(f"✅ Autoresponder for trigger `{trigger}` deleted successfully.")
        else:
            await ctx.send(f"❌ Autoresponder for trigger `{trigger}` not found.")


    @autoresponder.command(name="list", help="Lists all autoresponders.")
    async def list_autoresponders(self, ctx):
        """
        Lists all currently configured autoresponders.
        Usage: XTRM autoresponder list
        """
        if not self.autoresponders:
            await ctx.send("No autoresponders have been created yet.")
            return

        embed = discord.Embed(
            title="Autoresponders",
            description="Here are the autoresponders configured for this server:",
            color=discord.Color.orange()
        )
        for trigger, data in self.autoresponders.items():
            embed.add_field(name=f"Trigger: `{trigger}`", value=f"Type: `{data['type']}`, Match: `{data['match_type']}`", inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listens for messages to trigger autoresponders.
        """
        if message.author.bot:
            return # Ignore bot messages

        msg_content = message.content.lower()

        # Ensure the message is not a bot command
        # This prevents autoresponders from triggering on bot commands
        is_command = False
        # Access bot's prefixes directly from the bot instance
        current_prefixes = self.bot.command_prefix
        if not isinstance(current_prefixes, tuple): # Ensure it's iterable
            current_prefixes = (current_prefixes,)

        for prefix in current_prefixes:
            if msg_content.startswith(prefix.lower()):
                is_command = True
                break
        
        if is_command:
            return # Do not trigger autoresponder if it's a bot command

        for trigger, data in self.autoresponders.items():
            should_respond = False
            if data['match_type'] == "exact":
                if msg_content == trigger:
                    should_respond = True
            elif data['match_type'] == "contains":
                if trigger in msg_content:
                    should_respond = True
            
            if should_respond:
                # Process variables like {user}, {channel:name}, {server}, etc.
                processed_content = data['content'].replace("{user}", message.author.mention)
                processed_content = processed_content.replace("{server}", message.guild.name if message.guild else "Unknown Server")
                
                # Handle {channel:name} variable
                if "{channel:" in processed_content and "}" in processed_content:
                    channel_matches = re.findall(r"\{channel:([^}]+)\}", processed_content)
                    for channel_name in channel_matches:
                        target_channel = discord.utils.get(message.guild.channels, name=channel_name)
                        if target_channel:
                            processed_content = processed_content.replace(f"{{channel:{channel_name}}}", target_channel.mention)
                        else:
                            processed_content = processed_content.replace(f"{{channel:{channel_name}}}", f"#{channel_name} (not found)")

                if data['type'] == "text":
                    await message.channel.send(processed_content)
                elif data['type'] == "embed":
                    # Basic embed. Full implementation would parse more options.
                    embed_color = data.get("color", discord.Color.blue()) # Use stored color or default
                    embed = discord.Embed(description=processed_content, color=embed_color)
                    if data.get("title"):
                        embed.title = data["title"]
                    # Add more embed fields/options as parsed in create/edit
                    await message.channel.send(embed=embed)
                elif data['type'] == "image":
                    await message.channel.send(processed_content) # Assuming content is a direct image URL
                return # Respond only once per message

async def setup(bot):
    """
    Adds the Autoresponders cog to the bot.
    """
    await bot.add_cog(Autoresponders(bot))
