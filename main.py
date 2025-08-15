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
    },
    1403956190857265172: {  # Furrycon
        "mars": "#ac6c24",        # Amber
        "ava": "#8b9b5b",         # Green
    }
}

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix=">", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.command()
async def send(ctx, channel_name: str, *, message: str = ""):
    origin_channel = ctx.channel
    guild_id = ctx.guild.id
    destination_channel = None

    for channel in ctx.guild.text_channels:
        if channel.name.lower() == channel_name.lower():
            destination_channel = channel
            break

    if not destination_channel:
        await ctx.send(f"❌ Channel '{channel_name}' not found.")
        return

    # Get color based on guild and origin channel
    server_colors = SERVER_CHANNEL_COLORS.get(guild_id, {})
    hex_color = server_colors.get(origin_channel.name.lower(), "#99AAB5")  # Default grey

    try:
        embed_color = discord.Color.from_str(hex_color)
    except ValueError:
        embed_color = discord.Color.default()

    embed = discord.Embed(
        description=message or "*No message provided*",
        color=embed_color
    )
    embed.set_footer(text=f"Letter from {origin_channel.name.capitalize()}")

    # Handle attachments
    if len(ctx.message.attachments) == 1:
        embed.set_image(url=ctx.message.attachments[0].url)
        files = []
    else:
        files = [await attachment.to_file() for attachment in ctx.message.attachments]

    try:
        await destination_channel.send(embed=embed, files=files)
        await ctx.message.add_reaction("✅")  # React with checkmark instead of sending a message
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to send messages to that channel.")
    except Exception as e:
        await ctx.send(f"⚠️ Error sending message: {e}")

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))