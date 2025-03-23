import pytest
from unittest.mock import AsyncMock, MagicMock
import discord
from role.role_checking import check_eboard_role, check_brother_role


@pytest.fixture
def mock_interaction():
    interaction = MagicMock(spec=discord.Interaction)
    interaction.guild = MagicMock()
    interaction.user = MagicMock()
    interaction.response = AsyncMock()
    return interaction


@pytest.mark.asyncio
async def test_check_eboard_role(mock_interaction):
    # Setup
    eboard_role = MagicMock()
    eboard_role.name = "Executive Board"
    mock_interaction.guild.roles = [eboard_role]
    mock_interaction.user.roles = [eboard_role]

    # Execute
    result = await check_eboard_role(mock_interaction)

    # Assert
    assert result is True
    mock_interaction.response.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_check_eboard_role_failure(mock_interaction):
    # Setup
    mock_interaction.guild.roles = []
    mock_interaction.user.roles = []

    # Execute
    result = await check_eboard_role(mock_interaction)

    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_check_brother_role_success(mock_interaction):
    # Setup
    brother_role = MagicMock()
    brother_role.name = "Brother"
    mock_interaction.guild.roles = [brother_role]
    mock_interaction.user.roles = [brother_role]

    # Execute
    result = await check_brother_role(mock_interaction)

    # Assert
    assert result is True



@pytest.mark.asyncio
async def test_check_brother_role_failure(mock_interaction):
    # Setup
    mock_interaction.guild.roles = []
    mock_interaction.user.roles = []

    # Execute
    result = await check_brother_role(mock_interaction)

    # Assert
    assert result is False
