from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from main import approve


@pytest_asyncio.fixture
async def mock_interaction():
    interaction = AsyncMock()
    interaction.response = AsyncMock()
    interaction.user = MagicMock()
    interaction.user.roles = []
    return interaction


@pytest.mark.asyncio
async def test_approve_command_single_point_success(mock_interaction):
    # Mock role checks to return True (has permission)
    with patch('main.check_eboard_role', new_callable=AsyncMock, return_value=True), \
            patch('main.check_info_systems_role', new_callable=AsyncMock, return_value=False), \
            patch('main.read_csv', new_callable=AsyncMock) as mock_read_csv, \
            patch('main.get_unapproved_points') as mock_get_unapproved, \
            patch('main.change_point_approval') as mock_change_approval:
        # Set up mock data
        mock_df = MagicMock()
        mock_read_csv.return_value = mock_df
        mock_get_unapproved.return_value = MagicMock()
        mock_get_unapproved.return_value["ID"].values.tolist.return_value = [1]
        mock_change_approval.return_value = mock_df

        # Test with single point ID
        await approve.callback(mock_interaction, "1")

        # Verify CSV operations were called correctly
        mock_read_csv.assert_called_once()
        mock_change_approval.assert_called_once_with(mock_df, 1, new_approval=True)

        # Verify response message
        mock_interaction.response.send_message.assert_called_once_with("Point 1 approved")


@pytest.mark.asyncio
async def test_approve_command_multiple_points_success(mock_interaction):
    # Mock role checks to return True (has permission)
    with patch('main.check_eboard_role', new_callable=AsyncMock, return_value=True), \
            patch('main.check_info_systems_role', new_callable=AsyncMock, return_value=False), \
            patch('main.read_csv', new_callable=AsyncMock) as mock_read_csv, \
            patch('main.change_approval_with_discrete_values') as mock_change_approval:
        # Set up mock data
        mock_df = MagicMock()
        mock_read_csv.return_value = mock_df
        mock_change_approval.return_value = mock_df

        # Test with multiple point IDs
        await approve.callback(mock_interaction, "1,2,3")

        # Verify CSV operations were called correctly
        mock_read_csv.assert_called_once()
        mock_change_approval.assert_called_once_with(mock_df, [1, 2, 3], new_approval=True)

        # Verify response message
        mock_interaction.response.send_message.assert_called_once_with("Points 1,2,3 approved")


@pytest.mark.asyncio
async def test_approve_command_no_permission(mock_interaction):
    # Mock role checks to return False (no permission)
    with patch('main.check_eboard_role', new_callable=AsyncMock, return_value=False), \
            patch('main.check_info_systems_role', new_callable=AsyncMock, return_value=False), \
            patch('main.read_csv', new_callable=AsyncMock) as mock_read_csv:
        # Set up mock data
        mock_df = MagicMock()
        mock_read_csv.return_value = mock_df

        await approve.callback(mock_interaction, "1")

        # Verify error message
        mock_interaction.response.send_message.assert_called_once_with(
            "You don't have permission to do that."
        )


@pytest.mark.asyncio
async def test_approve_command_invalid_id(mock_interaction):
    # Mock role checks to return True (has permission)
    with patch('main.check_eboard_role', new_callable=AsyncMock, return_value=True), \
            patch('main.check_info_systems_role', new_callable=AsyncMock, return_value=False), \
            patch('main.read_csv', new_callable=AsyncMock) as mock_read_csv, \
            patch('main.get_unapproved_points') as mock_get_unapproved:
        # Set up mock data
        mock_df = MagicMock()
        mock_read_csv.return_value = mock_df
        mock_get_unapproved.return_value = MagicMock()
        mock_get_unapproved.return_value["ID"].values.tolist.return_value = [1]

        # Test with invalid point ID
        await approve.callback(mock_interaction, "999")

        # Verify error message
        mock_interaction.response.send_message.assert_called_once_with(
            "Error: This ID is not in the unapproved list"
        )
