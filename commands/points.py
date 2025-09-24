import os
import sqlite3
from datetime import datetime

from discord.ext import commands
from dotenv import load_dotenv
from PledgePoints.messages import *
from PledgePoints.pledges import *

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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Time TEXT,
            PointChange INTEGER,
            Pledge TEXT,
            Brother TEXT,
            Comment TEXT,
            approval_status TEXT DEFAULT 'pending',
            approved_by TEXT,
            approval_timestamp TEXT
        )
    """)

    # Add new columns to existing table if they don't exist
    try:
        cursor.execute("ALTER TABLE Points ADD COLUMN id INTEGER PRIMARY KEY AUTOINCREMENT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        cursor.execute("ALTER TABLE Points ADD COLUMN approval_status TEXT DEFAULT 'pending'")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        cursor.execute("ALTER TABLE Points ADD COLUMN approved_by TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        cursor.execute("ALTER TABLE Points ADD COLUMN approval_timestamp TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

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


    @bot.tree.command(name="pledge_rankings", description="Show rankings of all pledges by total points.")
    async def pledge_rankings(interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Fetching pledge rankings...")
            db_connection = sqlite3.connect(master_point_file_name)
            points = get_pledge_points(db_connection)
            db_connection.close()
            rankings_df = rank_pledges(points)
            rankings = [(pledge, int(total_points)) for pledge, total_points in rankings_df.items()]

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

    @bot.tree.command(name="plot_rankings", description="Plot rankings of all pledges by total points.")
    async def plot_rankings_command(interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Generating pledge rankings plot...")

            db_connection = sqlite3.connect(master_point_file_name)
            points = get_pledge_points(db_connection)
            db_connection.close()
            rankings_df = rank_pledges(points)

            if rankings_df.empty:
                await interaction.followup.send("No pledge data found in the database.")
                return

            plot_file = plot_rankings(rankings_df)
            await interaction.followup.send(file=discord.File(plot_file))

            # Clean up the generated plot file
            if os.path.exists(plot_file):
                os.remove(plot_file)

        except Exception as e:
            await interaction.followup.send(f"An error occurred while generating the plot: {str(e)}")
            raise

    @bot.tree.command(name="view_pending_points", description="View all pending point submissions that need approval")
    async def view_pending_points(interaction: discord.Interaction):
        """View all pending point submissions that need approval."""
        try:
            await interaction.response.send_message("Fetching pending points...")

            db_connection = sqlite3.connect(master_point_file_name)
            cursor = db_connection.cursor()
            cursor.execute("""
                SELECT id, Time, PointChange, Pledge, Brother, Comment
                FROM Points
                WHERE approval_status = 'pending'
                ORDER BY Time DESC
            """)
            rows = cursor.fetchall()
            db_connection.close()

            if not rows:
                await interaction.followup.send("No pending points found.")
                return

            # Format the pending points
            pending_text = "📋 **Pending Point Submissions**\n\n"
            for row in rows:
                point_id, time_str, point_change, pledge, brother, comment = row
                # Convert time string to readable format
                try:
                    time_dt = datetime.fromisoformat(time_str)
                    time_formatted = time_dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    time_formatted = time_str

                pending_text += f"**ID: {point_id}**\n"
                pending_text += f"⏰ Time: {time_formatted}\n"
                pending_text += f"👤 Brother: {brother}\n"
                pending_text += f"📊 Points: {point_change:+d}\n"
                pending_text += f"🎯 Pledge: {pledge}\n"
                pending_text += f"💬 Comment: {comment}\n\n"

            # Split message if too long
            if len(pending_text) > 1900:
                chunks = [pending_text[i:i+1900] for i in range(0, len(pending_text), 1900)]
                for chunk in chunks:
                    await interaction.followup.send(chunk)
            else:
                await interaction.followup.send(pending_text)

        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching pending points: {str(e)}")
            raise

    @bot.tree.command(name="approve_points", description="Approve specific point submissions by ID or all pending points")
    async def approve_points(interaction: discord.Interaction, point_ids: str):
        """Approve specific point submissions by ID (comma-separated list), or all pending points if 'all' is input."""
        try:
            # Check if user has Executive Board role
            from role.role_checking import check_eboard_role, check_info_systems_role
            if not (await check_eboard_role(interaction) or await check_info_systems_role(interaction)):
                await interaction.response.send_message("You don't have permission to approve points. Executive Board role required.", ephemeral=True)
                return

            await interaction.response.send_message("Processing approval...")

            db_connection = sqlite3.connect(master_point_file_name)
            cursor = db_connection.cursor()

            approve_all = point_ids.strip().lower() == "all"
            if approve_all:
                # Approve all pending points
                cursor.execute("""
                    SELECT id, Pledge, PointChange, Brother
                    FROM Points
                    WHERE approval_status = 'pending'
                """)
                existing_points = cursor.fetchall()
                if not existing_points:
                    await interaction.followup.send("No pending points found to approve.")
                    db_connection.close()
                    return

                current_time = datetime.now().isoformat()
                approver = interaction.user.display_name

                cursor.execute("""
                    UPDATE Points
                    SET approval_status = 'approved',
                        approved_by = ?,
                        approval_timestamp = ?
                    WHERE approval_status = 'pending'
                """, (approver, current_time))
                db_connection.commit()
                db_connection.close()

                approved_text = f"✅ **Approved ALL ({len(existing_points)}) pending point submission(s):**\n\n"
                for point_id, pledge, point_change, brother in existing_points:
                    approved_text += f"**ID {point_id}**: {brother} → {pledge} ({point_change:+d} points)\n"

                # Split message if too long
                if len(approved_text) > 1900:
                    chunks = [approved_text[i:i+1900] for i in range(0, len(approved_text), 1900)]
                    for chunk in chunks:
                        await interaction.followup.send(chunk)
                else:
                    await interaction.followup.send(approved_text)
            else:
                # Parse point IDs
                try:
                    ids = [int(id.strip()) for id in point_ids.split(',')]
                except ValueError:
                    await interaction.followup.send("Invalid point IDs. Please provide comma-separated numbers or 'all'.")
                    db_connection.close()
                    return

                # Check which IDs exist and are pending
                placeholders = ','.join('?' for _ in ids)
                cursor.execute(f"""
                    SELECT id, Pledge, PointChange, Brother
                    FROM Points
                    WHERE id IN ({placeholders}) AND approval_status = 'pending'
                """, ids)
                existing_points = cursor.fetchall()

                if not existing_points:
                    await interaction.followup.send("No pending points found with the provided IDs.")
                    db_connection.close()
                    return

                # Update approval status
                current_time = datetime.now().isoformat()
                approver = interaction.user.display_name

                cursor.execute(f"""
                    UPDATE Points
                    SET approval_status = 'approved',
                        approved_by = ?,
                        approval_timestamp = ?
                    WHERE id IN ({placeholders}) AND approval_status = 'pending'
                """, [approver, current_time] + ids)

                db_connection.commit()
                db_connection.close()

                # Format response
                approved_text = f"✅ **Approved {len(existing_points)} point submission(s):**\n\n"
                for point_id, pledge, point_change, brother in existing_points:
                    approved_text += f"**ID {point_id}**: {brother} → {pledge} ({point_change:+d} points)\n"

                # Split message if too long
                if len(approved_text) > 1900:
                    chunks = [approved_text[i:i+1900] for i in range(0, len(approved_text), 1900)]
                    for chunk in chunks:
                        await interaction.followup.send(chunk)
                else:
                    await interaction.followup.send(approved_text)

        except Exception as e:
            # If the error is due to message length, send a more helpful message
            error_message = str(e)
            if "Must be 2000 or fewer in length" in error_message or "Invalid Form Body" in error_message:
                await interaction.followup.send("The approval message was too long to send. Please approve fewer points at a time or contact an admin.")
            else:
                await interaction.followup.send(f"An error occurred while approving points: {error_message}")
            raise

    @bot.tree.command(name="reject_points", description="Reject specific point submissions by ID")
    async def reject_points(interaction: discord.Interaction, point_ids: str):
        """Reject specific point submissions by ID (comma-separated list)."""
        try:
            # Check if user has Executive Board role
            from role.role_checking import check_eboard_role
            if not await check_eboard_role(interaction):
                await interaction.response.send_message("You don't have permission to reject points. Executive Board role required.", ephemeral=True)
                return

            await interaction.response.send_message("Processing rejection...")

            # Parse point IDs
            try:
                ids = [int(id.strip()) for id in point_ids.split(',')]
            except ValueError:
                await interaction.followup.send("Invalid point IDs. Please provide comma-separated numbers.")
                return

            db_connection = sqlite3.connect(master_point_file_name)
            cursor = db_connection.cursor()

            # Check which IDs exist and are pending
            placeholders = ','.join('?' for _ in ids)
            cursor.execute(f"""
                SELECT id, Pledge, PointChange, Brother
                FROM Points
                WHERE id IN ({placeholders}) AND approval_status = 'pending'
            """, ids)
            existing_points = cursor.fetchall()

            if not existing_points:
                await interaction.followup.send("No pending points found with the provided IDs.")
                db_connection.close()
                return

            # Update approval status
            current_time = datetime.now().isoformat()
            approver = interaction.user.display_name

            cursor.execute(f"""
                UPDATE Points
                SET approval_status = 'rejected',
                    approved_by = ?,
                    approval_timestamp = ?
                WHERE id IN ({placeholders}) AND approval_status = 'pending'
            """, [approver, current_time] + ids)

            db_connection.commit()
            db_connection.close()

            # Format response
            rejected_text = f"❌ **Rejected {len(existing_points)} point submission(s):**\n\n"
            for point_id, pledge, point_change, brother in existing_points:
                rejected_text += f"**ID {point_id}**: {brother} → {pledge} ({point_change:+d} points)\n"

            await interaction.followup.send(rejected_text)

        except Exception as e:
            await interaction.followup.send(f"An error occurred while rejecting points: {str(e)}")
            raise

    @bot.tree.command(name="view_point_details", description="View detailed information about a specific point entry")
    async def view_point_details(interaction: discord.Interaction, point_id: int):
        """View detailed information about a specific point entry."""
        try:
            await interaction.response.send_message("Fetching point details...")

            db_connection = sqlite3.connect(master_point_file_name)
            cursor = db_connection.cursor()
            cursor.execute("""
                SELECT id, Time, PointChange, Pledge, Brother, Comment,
                       approval_status, approved_by, approval_timestamp
                FROM Points
                WHERE id = ?
            """, (point_id,))
            row = cursor.fetchone()
            db_connection.close()

            if not row:
                await interaction.followup.send(f"No point entry found with ID {point_id}.")
                return

            (point_id, time_str, point_change, pledge, brother, comment,
             approval_status, approved_by, approval_timestamp) = row

            # Format time
            try:
                time_dt = datetime.fromisoformat(time_str)
                time_formatted = time_dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                time_formatted = time_str

            # Format approval info
            approval_info = ""
            if approval_status == 'approved':
                approval_info = f"✅ **Approved** by {approved_by}"
                if approval_timestamp:
                    try:
                        approval_dt = datetime.fromisoformat(approval_timestamp)
                        approval_info += f" on {approval_dt.strftime('%Y-%m-%d %H:%M:%S')}"
                    except:
                        approval_info += f" on {approval_timestamp}"
            elif approval_status == 'rejected':
                approval_info = f"❌ **Rejected** by {approved_by}"
                if approval_timestamp:
                    try:
                        approval_dt = datetime.fromisoformat(approval_timestamp)
                        approval_info += f" on {approval_dt.strftime('%Y-%m-%d %H:%M:%S')}"
                    except:
                        approval_info += f" on {approval_timestamp}"
            else:
                approval_info = "⏳ **Pending Approval**"

            # Create detailed response
            details_text = f"📊 **Point Entry Details - ID {point_id}**\n\n"
            details_text += f"⏰ **Time**: {time_formatted}\n"
            details_text += f"👤 **Brother**: {brother}\n"
            details_text += f"📈 **Point Change**: {point_change:+d}\n"
            details_text += f"🎯 **Pledge**: {pledge}\n"
            details_text += f"💬 **Comment**: {comment}\n"
            details_text += f"🔍 **Status**: {approval_info}\n"

            await interaction.followup.send(details_text)

        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching point details: {str(e)}")
            raise
