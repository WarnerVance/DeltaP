# Imports
import asyncio  # Asynchronous I/O support
import os  # File and path operations
import ssl  # Secure connection support
from datetime import datetime  # Date and time handling
from logging import exception

import aiohttp  # Add this import at the top with other imports
import pytz  # Timezone support
from discord.ext import commands  # Discord bot commands and scheduled tasks
from dotenv import load_dotenv

from PledgePoints.csvutils import create_csv, read_csv
from PledgePoints.pledges import change_pledge_points
from role.role_checking import *

# Warner: This until the  on_ready function was ai generated because I couldn't be bothered
# Initialize SSL context for secure connections
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Set up Discord bot with required permissions
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix='!', intents=intents)
bot.start_time = None

# Create aiohttp session with SSL context
async def get_session():
    return aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))

bot.http._HTTPClient__session = None
bot.http.get_session = get_session

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    
    if bot.start_time is None:  # Only set on first connection
        bot.start_time = datetime.now(pytz.UTC)
        print(f'Start time set to: {bot.start_time}')

    try:
        # Synchronize slash commands with Discord's API
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Error synchronizing slash commands: {str(e)}')




load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found in .env file")

master_point_csv_name = os.getenv('CSV_NAME')
if not master_point_csv_name:
    raise ValueError("CSV_NAME not found in .env file")


# Initialize required CSV files if they don't exist
try:
    if not os.path.exists(master_point_csv_name):
        # Warner: The Default values for columns in the create_csv function are fine here.
        if create_csv(master_point_csv_name):
            master_df = read_csv(master_point_csv_name)
        else:
            raise UserWarning("csv file doesn't exist and cannot be created.")

except Exception as e:
    print(f"Error creating CSV files: {str(e)}")
    del e

async def main():
    print('Starting bot...')
    try:
        # First set up the bot
        await bot.login(TOKEN)
        print('Successfully logged in')
        # Then connect and start processing events
        await bot.connect()
        print('Successfully connected to Discord')
    except Exception as e:
        print(f'Error during startup: {str(e)}')
    finally:
        if not bot.is_closed():
            await bot.close()


@bot.tree.command(name="ping", description="Check if the bot is responsive and get its latency")
async def ping(interaction: discord.Interaction):
    # Calculate uptime
    uptime = datetime.now(pytz.UTC) - bot.start_time
    hours = uptime.total_seconds() // 3600
    minutes = (uptime.total_seconds() % 3600) // 60
    seconds = uptime.total_seconds() % 60

    # Get bot latency
    latency = round(bot.latency * 1000)  # Convert to milliseconds

    # Create embed for better presentation
    embed = discord.Embed(
        title="🏓 Pong!",
        color=discord.Color.green()
    )
    embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
    embed.add_field(name="Uptime", value=f"{int(hours)}h {int(minutes)}m {int(seconds)}s", inline=True)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="give_take_pledge_points", description="Give or take pledge points from a specific pledge")
async def give_pledge_points(interaction: discord.Interaction, points: int, pledge: str, brother: str, comment: str):
    if check_brother_role(interaction) is False:
        await interaction.response.send_message("Naughty Pledge trying to edit points.")
    points = int(points)
    if not points in range(-128, 128):
        await interaction.response.send_message("Points must be an integer within the range -128,127.")
    pledge = pledge.title()
    try:
        df = read_csv(master_point_csv_name)
        df = change_pledge_points(df, pledge=pledge, brother=brother, comment=comment, points=points)
        df.to_csv(master_point_csv_name, index=False)
        if points >= 0:
            sign = "+"
        else:
            sign = "-"
        await interaction.response.send_message(f"{brother}: {sign}{points} {pledge} {comment}")
    except exception as error:
        print(error)
        await interaction.response.send_message(f"There was an error: {str(error)}")

if __name__ == "__main__":
    asyncio.run(main())

