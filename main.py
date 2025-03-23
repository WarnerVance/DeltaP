# Imports
import asyncio  # Asynchronous I/O support
import os  # File and path operations
import ssl  # Secure connection support
from datetime import datetime, time as datetime_time  # Date and time handling

import certifi  # SSL certificate handling
import discord  # Discord API wrapper
import pandas as pd
import psutil  # System information
import pytz  # Timezone support
from discord import app_commands  # Discord slash commands
from discord.ext import commands, tasks  # Discord bot commands and scheduled tasks
from dotenv import load_dotenv
from pandas import DataFrame
import aiohttp  # Add this import at the top with other imports

from PledgePoints.csvutils import create_csv, read_csv, append_row_to_df

# Warner: This unitl on_ready was ai generated because I couldn't be bothered
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


if __name__ == "__main__":
    asyncio.run(main())

