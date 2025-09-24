import asyncio
import re
import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

import discord
import pytz


async def fetch_messages_from_days_ago(bot: discord.Client, channel_id: int, days_ago: int) -> list[
    tuple[discord.User, datetime, str, discord.Message]]:
    """
    Fetch messages from a Discord channel that were sent a certain number of days ago.
    
    Args:
        bot (discord.Client): The Discord bot instance
        channel_id (int): The ID of the channel to fetch messages from
        days_ago (int): Number of days ago to fetch messages from
        
    Returns:
        list[tuple[discord.User, datetime, str, discord.Message]]: List of tuples containing (author, created_at, content, message)
    """
    # Get the channel
    channel = bot.get_channel(channel_id)
    if not channel:
        raise ValueError(f"Channel with ID {channel_id} not found")

    # Calculate the target date
    target_date = datetime.now(pytz.UTC) - timedelta(days=days_ago)

    # Fetch messages
    messages = []
    async for message in channel.history(limit=None, after=target_date):
        # Skip messages from bots
        if message.author.bot:
            continue
        messages.append((message.author, message.created_at, message.content, message))

    return messages


async def process_message_content(content: str, valid_pledges: list) -> Optional[Tuple[int, str, str]]:
    """
    Process a single message's content to extract point change, pledge name, and comment.
    Returns None if the message is invalid.
    """
    sql_int_min = -9223372036854775808
    sql_int_max = 9223372036854775807

    if not content.strip():
        return None

    # Extract point change using regex
    point_match = re.match(r'^([+-]\d+)', content)
    if not point_match:
        return None

    try:
        point_change = int(point_match.group(1))
        # Check if point change fits within SQL integer limits
        if point_change < sql_int_min or point_change > sql_int_max:
            return None
    except ValueError:
        return None

    # Remove the point change from the content
    remaining_content = content[len(point_match.group(1)):].strip()

    # Split the remaining content into pledge name and comment
    parts = remaining_content.split(' ', 1)
    if len(parts) < 2:
        return None

    pledge = parts[0].title()
    comment = parts[1].strip()

    if pledge == "To":
        pledge = comment.split(' ', 1)[0].title()
    if pledge == "Matt":
        pledge = "Matthew"
    if pledge == "Ozempic":
        pledge = "Eli"
    if pledge not in valid_pledges:
        return None

    return point_change, pledge, comment


async def add_reactions_with_rate_limit(messages: List[Tuple[discord.Message, bool]], rate_limit: float = 0.2):
    """
    Add reactions to messages with rate limiting.
    messages: List of (message, success) tuples where success is True for 👍 and False for 👎
    rate_limit: Minimum time between reactions in seconds
    """
    for message, success in messages:
        try:
            emoji = '👍' if success else '👎'
            await message.add_reaction(emoji)
            await asyncio.sleep(rate_limit)  # Rate limit the reactions
        except Exception:
            # Skip if we can't add the reaction
            continue


async def process_messages(messages: list[tuple[discord.User, datetime, str, discord.Message]]) -> list[
    tuple[datetime, int, str, str, str]]:
    """
    Process messages to extract point changes, pledge names, and comments.
    Returns processed messages and handles reactions separately with rate limiting.
    """
    processed_messages = []
    reaction_queue = []
    valid_pledges = [
        "Eli",
        "Evan",
        "Felix",
        "George",
        "Henrik",
        "James",
        "Kashyap",
        "Krishiv",
        "Logan",
        "Matthew",
        "Milo",
        "Nick",
        "Tony",
        "Will",
        "Zach",
        "Blake",
        "Devin"
    ]
    for author, timestamp, content, message in messages:
        result = await process_message_content(content, valid_pledges)

        if result is None:
            reaction_queue.append((message, False))
            continue

        point_change, pledge, comment = result
        processed_messages.append((timestamp, point_change, pledge, author.name, comment))
        reaction_queue.append((message, True))

    # Handle reactions separately with rate limiting
    asyncio.create_task(add_reactions_with_rate_limit(reaction_queue))
    
    return processed_messages


def get_old_points(db_connection: sqlite3.Connection) -> list[tuple[datetime, int, str, str, str]]:
    cursor = db_connection.cursor()
    cursor.execute("SELECT Time, PointChange, Pledge, Brother, Comment FROM Points WHERE approval_status IN ('approved', 'pending')")
    rows = cursor.fetchall()

    # Convert the time strings to datetime objects
    converted_rows = []
    for row in rows:
        time_str = row[0]
        # If time_str is already a datetime object, use it directly
        if isinstance(time_str, datetime):
            converted_rows.append(row)
        else:
            # Convert string to datetime
            try:
                time_dt = datetime.fromisoformat(time_str)
                converted_rows.append((time_dt, row[1], row[2], row[3], row[4]))
            except (ValueError, TypeError):
                # If conversion fails, skip this row
                continue

    return converted_rows


def get_approved_points(db_connection: sqlite3.Connection) -> list[tuple[datetime, int, str, str, str]]:
    """Get only approved points for rankings and other approved-only operations."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT Time, PointChange, Pledge, Brother, Comment FROM Points WHERE approval_status = 'approved'")
    rows = cursor.fetchall()

    # Convert the time strings to datetime objects
    converted_rows = []
    for row in rows:
        time_str = row[0]
        # If time_str is already a datetime object, use it directly
        if isinstance(time_str, datetime):
            converted_rows.append(row)
        else:
            # Convert string to datetime
            try:
                time_dt = datetime.fromisoformat(time_str)
                converted_rows.append((time_dt, row[1], row[2], row[3], row[4]))
            except (ValueError, TypeError):
                # If conversion fails, skip this row
                continue

    return converted_rows


def eliminate_duplicates(new_messages: list[tuple[datetime, int, str, str, str]],
                         old_points: list[tuple[datetime, int, str, str, str]]) -> list[
    tuple[datetime, int, str, str, str]]:
    """
    Eliminate duplicates by comparing the relevant fields of the tuples.
    Converts datetime to string for comparison to avoid microsecond differences.
    """
    # Convert old points to a set of string representations for faster lookup
    old_points_set = set()
    for point in old_points:
        # Convert datetime to string in a consistent format
        time_str = point[0].strftime('%Y-%m-%d %H:%M:%S')
        # Create a tuple of the relevant fields as strings
        point_key = (time_str, str(point[1]), point[2], point[3], point[4])
        old_points_set.add(point_key)

    # Filter new messages
    unique_messages = []
    for message in new_messages:
        # Convert datetime to string in the same format
        time_str = message[0].strftime('%Y-%m-%d %H:%M:%S')
        # Create a tuple of the relevant fields as strings
        message_key = (time_str, str(message[1]), message[2], message[3], message[4])

        if message_key not in old_points_set:
            unique_messages.append(message)

    return unique_messages


def add_new_points(db_connection: sqlite3.Connection, new_points: list[tuple[datetime, int, str, str, str]]) -> bool:
    cursor = db_connection.cursor()
    cursor.executemany("INSERT INTO Points (Time, PointChange, Pledge, Brother, Comment, approval_status) VALUES (?, ?, ?, ?, ?, 'pending')",
                       new_points)
    db_connection.commit()
    db_connection.close()
    return True
