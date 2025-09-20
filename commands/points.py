import os
import sqlite3

import discord
from discord.ext import commands
from dotenv import load_dotenv

import PledgePoints
from PledgePoints.messages import get_old_points, fetch_messages_from_days_ago, process_messages, eliminate_duplicates, add_new_points

load_dotenv()
master_point_csv_name = os.getenv('CSV_NAME')
if not master_point_csv_name:
    raise ValueError("CSV_NAME not found in .env file")


def initialize_database(db_file_name: str):
    """Initialize the database with the required table structure."""
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()
    
    # Create the Points table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Points (
            Time TEXT,
            PointChange INTEGER,
            Pledge TEXT,
            Brother TEXT,
            Comment TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized: {db_file_name}")


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
    
    # Initialize the database
    initialize_database(master_point_file_name)

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


    def get_pledge_rankings(db_connection: sqlite3.Connection) -> list[tuple[str, int]]:
        """
        Get a ranking of all pledges by their total points.
        
        Args:
            db_connection: SQLite database connection
            
        Returns:
            List of tuples (pledge_name, total_points) sorted by total_points descending
        """
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT Pledge, SUM(PointChange) as TotalPoints
            FROM Points
            GROUP BY Pledge
            ORDER BY TotalPoints DESC
        """)
        rankings = cursor.fetchall()
        return rankings

    @bot.tree.command(name="pledge_rankings", description="Show rankings of all pledges by total points.")
    async def pledge_rankings(interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Fetching pledge rankings...")
            
            db_connection = sqlite3.connect(master_point_file_name)
            rankings = get_pledge_rankings(db_connection)
            db_connection.close()
            
            if not rankings:
                await interaction.followup.send("No pledge data found in the database.")
                return
            
            # Format the rankings
            ranking_text = "🏆 **Pledge Rankings by Total Points**\n\n"
            for i, (pledge, total_points) in enumerate(rankings, 1):
                # Add medal emojis for top 3
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"{i}."
                
                ranking_text += f"{medal} **{pledge}**: {total_points:,} points\n"
            
            # Split message if too long (Discord has a 2000 character limit)
            if len(ranking_text) > 1900:
                chunks = [ranking_text[i:i+1900] for i in range(0, len(ranking_text), 1900)]
                for chunk in chunks:
                    await interaction.followup.send(chunk)
            else:
                await interaction.followup.send(ranking_text)
                
        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching rankings: {str(e)}")
            raise

