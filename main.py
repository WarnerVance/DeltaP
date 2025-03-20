# Imports
import asyncio  # Asynchronous I/O support
import functools  # Function and decorator tools
import os  # File and path operations
import platform  # System information
import ssl  # Secure connection support
import time
from datetime import datetime, time as datetime_time  # Date and time handling

import certifi  # SSL certificate handling
import discord  # Discord API wrapper
import pandas as pd
import psutil  # System information
import pytz  # Timezone support
from discord import app_commands  # Discord slash commands
from discord.ext import commands, tasks  # Discord bot commands and scheduled tasks
from dotenv import load_dotenv

from PledgePoints.pledges import create_csv

# Initialize SSL context for secure connections
ssl_context = ssl.create_default_context(cafile=certifi.where())

# Set up Discord bot with required permissions
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix='!', intents=intents)
bot.start_time = None

load_dotenv()  # Load environment variables from .env file
TOKEN = os.getenv('DISCORD_TOKEN')



async def on_ready():
    if bot.start_time is None:  # Only set on first connection
        bot.start_time = datetime.now(pytz.UTC)

    # Initialize required CSV files if they don't exist
    try:
        # Create pledges.csv if it doesn't exist
        if not os.path.exists('MasterPoints.csv'):
            create_csv('MasterPoints.csv')
            print(
                "Created pledges.csv, MasterPoints.csv, PendingPoints.csv, and Points.csv files if they didn't exist."
            )
    except Exception as e:
        print(f"Error creating CSV files: {str(e)}")
    try:
        # Synchronize slash commands with Discord's API
        synced = await bot.tree.sync()
    except Exception as e:
        print(f"Error synchronizing slash commands: {str(e)}")




async def main():
    try:
        # First set up the bot
        await bot.login(TOKEN)

        # Start the midnight update task
        # Then connect and start processing events
        await bot.connect()
    except Exception as e:
        print(f"Error during startup: {str(e)}")
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    asyncio.run(main())

