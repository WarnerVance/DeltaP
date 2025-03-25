from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from main import delete_unapproved


@pytest_asyncio.fixture
async def mock_interaction():
    interaction = AsyncMock()
    interaction.response = AsyncMock()
    interaction.user = MagicMock()
    interaction.user.roles = []
    return interaction


@pytest.mark.asyncio
async def test_delete_unapproved_command_success(mock_interaction):
    # Mock role checks to return True (has permission)
    with patch('main.check_eboard_role', new_callable=AsyncMock, return_value=True), \
            patch('main.check_info_systems_role', new_callable=AsyncMock, return_value=False), \
            patch('main.read_csv', new_callable=AsyncMock) as mock_read_csv, \
            patch('main.delete_unapproved_points') as mock_delete_points:
        # Set up mock data
        mock_df = MagicMock()
        mock_read_csv.return_value = mock_df
        mock_delete_points.return_value = mock_df

        # Test delete unapproved command
        await delete_unapproved.callback(mock_interaction)

        # Verify CSV operations were called correctly
        mock_read_csv.assert_called_once()
        mock_delete_points.assert_called_once_with(mock_df)

        # Verify response message
        mock_interaction.response.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_delete_unapproved_command_no_permission(mock_interaction):
    # Mock role checks to return False (no permission)
    with patch('main.check_eboard_role', new_callable=AsyncMock, return_value=False), \
            patch('main.check_info_systems_role', new_callable=AsyncMock, return_value=False), \
            patch('main.read_csv', new_callable=AsyncMock) as mock_read_csv:
        # Set up mock data
        mock_df = MagicMock()
        mock_read_csv.return_value = mock_df

        await delete_unapproved.callback(mock_interaction)

        # Verify error message
        mock_interaction.response.send_message.assert_called_once_with(
            "I'm sorry Dave I can't do that. Notifying Standards board"
        )


@pytest.mark.asyncio
async def test_delete_unapproved_command_info_systems_permission(mock_interaction):
    # Mock role checks to return True for info systems role
    with patch('main.check_eboard_role', new_callable=AsyncMock, return_value=False), \
            patch('main.check_info_systems_role', new_callable=AsyncMock, return_value=True), \
            patch('main.read_csv', new_callable=AsyncMock) as mock_read_csv, \
            patch('main.delete_unapproved_points') as mock_delete_points:
        # Set up mock data
        mock_df = MagicMock()
        mock_read_csv.return_value = mock_df
        mock_delete_points.return_value = mock_df

        # Test delete unapproved command
        await delete_unapproved.callback(mock_interaction)

        # Verify CSV operations were called correctly
        mock_read_csv.assert_called_once()
        mock_delete_points.assert_called_once_with(mock_df)

        # Verify response message
        mock_interaction.response.send_message.assert_called_once()
