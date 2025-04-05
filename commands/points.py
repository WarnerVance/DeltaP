import os
import sqlite3

import discord
from discord.ext import commands
from dotenv import load_dotenv

from PledgePoints.messages import add_new_points, eliminate_duplicates, fetch_messages_from_days_ago, get_old_points, \
    process_messages

load_dotenv()
master_point_csv_name = os.getenv('CSV_NAME')
if not master_point_csv_name:
    raise ValueError("CSV_NAME not found in .env file")


def setup(bot: commands.Bot):
    master_point_file_name = os.getenv('CSV_NAME')
    if not master_point_file_name:
        raise ValueError("CSV_NAME not found in .env file")
    table_name = os.getenv('TABLE_NAME')
    if not table_name:
        raise ValueError("TABLE_NAME not found in .env file")
    channel_id_str = os.getenv('CHANNEL_ID')
    if not channel_id_str:
        raise ValueError("CHANNEL_ID not found in .env file")

    try:
        channel_id = int(channel_id_str)
    except ValueError:
        raise ValueError(f"CHANNEL_ID must be a valid integer, got {channel_id_str}")

    @bot.tree.command(name="update_pledge_points", description="Update the point Database.")
    async def update_pledge_points(interaction: discord.Interaction, days_ago: int):
        try:
            await interaction.response.send_message(f"Updating pledge points for {days_ago} days ago")

            db_connection = sqlite3.connect(master_point_file_name)
            messages = await fetch_messages_from_days_ago(bot, channel_id, days_ago)

            if not messages:
                await interaction.followup.send("No messages found for the specified time period.")
                return

            new_points = await process_messages(messages)
            old_points = get_old_points(db_connection)
            new_points = eliminate_duplicates(new_points, old_points)

            if not new_points:
                await interaction.followup.send("No new points to add to the database.")
                return

            add_new_points(db_connection, new_points)
            await interaction.followup.send(f"Successfully added {len(new_points)} new points to the database.")

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")
            raise
