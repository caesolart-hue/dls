import discord
from discord.ext import commands
import os

# === Per-server (guild) per-channel hex color mapping ===
SERVER_CHANNEL_COLORS = {
    1180574159143706765: {  # Eminiserver
        "caevamp": "#57F287",     # Green
        "minivamp": "#7289DA",   # Blue
    },
    1402501839664189581: {  # Horizonbound
        "harlowe": "#d8be70",     # Gold
        "ellis": "#ffc4d7",   # Pink
    }
}

# === Discord intents ===
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

# === Create bot instance ===
bot = commands.Bot(command_prefix=">", intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Sorting the Dead Letters"))
    print(f"✅ Dead Letter Society is online as {bot.user}")

@bot.command()
async def send(ctx, channel_name: str, *, message: str = ""):
    # Use parent channel name if inside a thread; else use channel name
    if isinstance(ctx.channel, discord.Thread):
        origin_name = ctx.channel.parent.name
    else:
        origin_name = ctx.channel.name

    guild_id = ctx.guild.id
    destination_channel = None

    # Find target channel by name
    for channel in ctx.guild.text_channels:
        if channel.name.lower() == channel_name.lower():
            destination_channel = channel
            break

    if not destination_channel:
        await ctx.send(f"❌ Channel '{channel_name}' not found.")
        return

    # Collect attachments
    files = []
    for attachment in ctx.message.attachments:
        file = await attachment.to_file()
        files.append(file)

    # Get color based on guild + origin (parent channel) name
    server_colors = SERVER_CHANNEL_COLORS.get(guild_id, {})
    hex_color = server_colors.get(origin_name.lower(), "#99AAB5")  # Default grey

    try:
        embed_color = discord.Color.from_str(hex_color)
    except ValueError:
        embed_color = discord.Color.default()

    embed = discord.Embed(
        title=f"📩 Message from #{origin_name}",
        description=message or "*No message provided*",
        color=embed_color
    )

    try:
        await destination_channel.send(embed=embed, files=files)
        await ctx.send(f"✅ Message sent to #{destination_channel.name}.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to send messages to that channel.")
    except Exception as e:
        await ctx.send(f"⚠️ Error sending message: {e}")

# === Run bot ===
if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
