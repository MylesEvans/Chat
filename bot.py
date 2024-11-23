import discord
from discord.ext import commands

# Replace with your bot token
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Intents for the bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store trigger channels in memory (for persistence, use a database or a file)
trigger_channels = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild

    # Check if the user joined a voice channel and it's a trigger channel
    if after.channel and after.channel.id in trigger_channels.get(guild.id, []):
        # Create a custom voice channel
        category = after.channel.category  # Use the same category as the joined voice channel
        voice_channel_name = f"{member.display_name}'s Voice Channel"
        custom_voice_channel = await guild.create_voice_channel(
            name=voice_channel_name,
            category=category
        )

        # Move the member to the custom voice channel
        await member.move_to(custom_voice_channel)

        # Give the member permission to manage the channel
        overwrite = discord.PermissionOverwrite(manage_channels=True)
        await custom_voice_channel.set_permissions(member, overwrite=overwrite)

        # Create a custom text channel
        text_channel_name = f"{member.display_name}-text"
        custom_text_channel = await guild.create_text_channel(
            name=text_channel_name,
            category=category
        )

        # Set permissions for the member in the text channel
        await custom_text_channel.set_permissions(member, overwrite=overwrite)

        # Optionally, send a message in the text channel
        await custom_text_channel.send(f"Welcome to your custom channel, {member.mention}!")

@bot.event
async def on_guild_channel_delete(channel):
    # Optional cleanup: delete text/voice channels when one of them is deleted
    guild = channel.guild
    for other_channel in guild.channels:
        if channel.name in other_channel.name:
            await other_channel.delete()

# Command to add a trigger channel
@bot.command(name="addtrigger")
@commands.has_permissions(administrator=True)
async def add_trigger(ctx, voice_channel: discord.VoiceChannel):
    guild_id = ctx.guild.id

    # Add the channel to the list of trigger channels
    if guild_id not in trigger_channels:
        trigger_channels[guild_id] = []
    if voice_channel.id not in trigger_channels[guild_id]:
        trigger_channels[guild_id].append(voice_channel.id)
        await ctx.send(f"{voice_channel.name} has been added as a trigger channel!")
    else:
        await ctx.send(f"{voice_channel.name} is already a trigger channel.")

# Command to remove a trigger channel
@bot.command(name="removetrigger")
@commands.has_permissions(administrator=True)
async def remove_trigger(ctx, voice_channel: discord.VoiceChannel):
    guild_id = ctx.guild.id

    # Remove the channel from the list of trigger channels
    if guild_id in trigger_channels and voice_channel.id in trigger_channels[guild_id]:
        trigger_channels[guild_id].remove(voice_channel.id)
        await ctx.send(f"{voice_channel.name} has been removed as a trigger channel!")
    else:
        await ctx.send(f"{voice_channel.name} is not a trigger channel.")

# Command to list all trigger channels
@bot.command(name="listtriggers")
@commands.has_permissions(administrator=True)
async def list_triggers(ctx):
    guild_id = ctx.guild.id

    # List all trigger channels for the server
    if guild_id in trigger_channels and trigger_channels[guild_id]:
        channel_names = [
            ctx.guild.get_channel(channel_id).name
            for channel_id in trigger_channels[guild_id]
            if ctx.guild.get_channel(channel_id)
        ]
        await ctx.send("Trigger channels:\n" + "\n".join(channel_names))
    else:
        await ctx.send("No trigger channels have been set.")

# Run the bot
bot.run(BOT_TOKEN)
