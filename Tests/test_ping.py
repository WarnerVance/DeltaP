from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
import pytest_asyncio
import pytz

from main import ping, give_pledge_points


@pytest_asyncio.fixture
async def mock_interaction():
    interaction = AsyncMock()
    interaction.response = AsyncMock()
    interaction.user = MagicMock()
    interaction.user.roles = []
    return interaction


@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.start_time = datetime.now(pytz.UTC)
    bot.latency = 0.1
    return bot


@pytest.mark.asyncio
async def test_ping_command(mock_interaction, mock_bot):
    # Mock the bot's start_time and latency
    with patch('main.bot', mock_bot):
        await ping.callback(mock_interaction)

        # Verify that send_message was called with an embed
        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert isinstance(call_args[1]['embed'], discord.Embed)

        # Verify embed fields
        embed = call_args[1]['embed']
        assert embed.title == "🏓 Pong!"
        assert embed.color == discord.Color.green()

        # Verify fields contain expected data
        fields = {field.name: field.value for field in embed.fields}
        assert "Latency" in fields
        assert "Uptime" in fields


@pytest.mark.asyncio
async def test_give_pledge_points_command_success(mock_interaction):
    # Mock the role check to return True (brother role)
    with patch('main.check_brother_role', return_value=True), \
            patch('main.read_csv') as mock_read_csv, \
            patch('main.change_pledge_points') as mock_change_points:
        # Set up mock data
        mock_df = MagicMock()
        mock_read_csv.return_value = mock_df
        mock_change_points.return_value = mock_df

        # Test parameters
        points = 10
        pledge = "TestPledge"
        brother = "TestBrother"
        comment = "Test comment"

        await give_pledge_points.callback(mock_interaction, points, pledge, brother, comment)

        # Verify CSV operations were called correctly
        mock_read_csv.assert_called_once()
        mock_change_points.assert_called_once_with(
            mock_df, pledge=pledge.title(), brother=brother,
            comment=comment, points=points
        )

        # Verify response message
        mock_interaction.response.send_message.assert_called_once_with(
            f"{brother}: +{points} {pledge.title()} {comment}"
        )
