# Imports
import asyncio  # Asynchronous I/O support
import os  # File and path operations
import ssl  # Secure connection support
from datetime import datetime  # Date and time handling

import aiohttp  # Add this import at the top with other imports
import pytz  # Timezone support
from discord.ext import commands  # Discord bot commands and scheduled tasks
from dotenv import load_dotenv

from PledgePoints.approval import get_unapproved_points, change_point_approval, change_approval_with_discrete_values, \
    delete_unapproved_points
from PledgePoints.csvutils import create_csv, read_csv
from PledgePoints.pledges import change_pledge_points
from role.role_checking import *

# Warner: ssl_context until the on_ready function was ai generated because I couldn't be bothered
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
        create_csv(master_point_csv_name)

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
    if await check_brother_role(interaction) is False:
        await interaction.response.send_message("Naughty Pledge trying to edit points.")
        return
    points = int(points)
    if not points in range(-128, 128):
        await interaction.response.send_message("Points must be an integer within the range -128,127.")
        return
    pledge = pledge.title()
    try:
        df = read_csv(master_point_csv_name)
        df = change_pledge_points(df, pledge=pledge, brother=brother, comment=comment, points=points)
        df.to_csv(master_point_csv_name, index=False)
        if points >= 0:
            points_str = f"+{points}"
        else:
            points_str = str(points)
        await interaction.response.send_message(f"{brother}: {points_str} {pledge} {comment}")
    except Exception as error:
        print(error)
        await interaction.response.send_message(f"There was an error: {str(error)}")


@bot.tree.command(name="list_pending_points", description="List all points that have yet to be approved")
async def list_pending_points(interaction: discord.Interaction):
    if await check_brother_role(interaction) is False:
        await interaction.response.send_message("Naughty Pledge trying to use the points bot")
    df = read_csv(master_point_csv_name)
    unapproved_points_df = get_unapproved_points(df)
    unapproved_points_list = unapproved_points_df.values.tolist()
    response = ""
    for points in unapproved_points_list:
        if points[2] >= 0:
            points_str = f"+{points[2]}"
        else:
            points_str = str(points[2])
        entry = f"ID: {points[0]}. {points_str} {points[3]} {points[5]} - {points[4]}\n"
        response = response + entry
    await interaction.response.send_message(response)


@bot.tree.command(name="approve",
                  description="Approve points. If you want to approve more than one point then make a comma separated list of IDs ie(4,3,6)")
async def approve(interaction: discord.Interaction, point_id: str):
    if await check_eboard_role(interaction) is False and await check_info_systems_role(interaction) is False:
        await interaction.response.send_message("You don't have permission to do that.")
    # Reads in the points csv file
    df = await read_csv(master_point_csv_name)
    # If theres only one point id to approve
    if "," not in point_id:
        try:
            point_id = int(point_id)
            if point_id not in get_unapproved_points(df)["ID"].values.tolist():
                await interaction.response.send_message("Error: This ID is not in the unapproved list")
                return
            df = change_point_approval(df, point_id, new_approval=True)
            df.to_csv(master_point_csv_name, index=False)
            await interaction.response.send_message(f"Point {point_id} approved")
            return True
        except Exception as error:
            await interaction.response.send_message(f"There was an error: {str(error)}")
    # Splits the id string into a list of ints
    ids = point_id.split(",")
    for idx in range(len(ids)):
        ids[idx] = int(ids[idx])
    try:
        # Changes the points with the given ids
        change_approval_with_discrete_values(df, ids, new_approval=True)
        df.to_csv(master_point_csv_name, index=False)
        await interaction.response.send_message(f"Points {point_id} approved")
        return True
    except Exception as error:
        await interaction.response.send_message(f"There was an error: {str(error)}")


@bot.tree.command(name="delete_unapproved_points", description="Delete all points that have not been approved.")
async def delete_unapproved(interaction: discord.Interaction):
    if await check_eboard_role(interaction) is False and check_info_systems_role(interaction) is False:
        await interaction.response.send_message("I'm sorry Dave I can't do that. Notifying Standards board")
        return True
    df = await read_csv(master_point_csv_name)
    df = delete_unapproved_points(df)
    df.to_csv(master_point_csv_name, index=False)

if __name__ == "__main__":
    asyncio.run(main())

