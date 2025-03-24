from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
import pytz

from main import give_pledge_points


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


@pytest.mark.asyncio
async def test_give_pledge_points_command_no_brother_role(mock_interaction):
    # Mock the role check to return False (no brother role)
    with patch('main.check_brother_role', return_value=False):
        await give_pledge_points.callback(mock_interaction, 10, "TestPledge", "TestBrother", "Test comment")

        # Verify error message
        mock_interaction.response.send_message.assert_called_once_with(
            "Naughty Pledge trying to edit points."
        )


@pytest.mark.asyncio
async def test_give_pledge_points_command_invalid_points(mock_interaction):
    # Mock the role check to return True
    with patch('main.check_brother_role', return_value=True):
        # Test with points outside valid range
        await give_pledge_points.callback(mock_interaction, 200, "TestPledge", "TestBrother", "Test comment")

        # Verify error message
        mock_interaction.response.send_message.assert_called_once_with(
            "Points must be an integer within the range -128,127."
        )


@pytest.mark.asyncio
async def test_give_pledge_points_command_negative_points(mock_interaction):
    # Mock the role check to return True
    with patch('main.check_brother_role', return_value=True), \
            patch('main.read_csv') as mock_read_csv, \
            patch('main.change_pledge_points') as mock_change_points:
        # Set up mock data
        mock_df = MagicMock()
        mock_read_csv.return_value = mock_df
        mock_change_points.return_value = mock_df

        # Test with negative points
        points = -10
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

        # Verify response message with negative sign
        mock_interaction.response.send_message.assert_called_once_with(
            f"{brother}: {points} {pledge.title()} {comment}"
        )
