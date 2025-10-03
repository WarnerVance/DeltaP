# DeltaP Discord Bot

A Discord bot for managing and tracking pledge points in a fraternity/organization setting. DeltaP automates point tracking, provides leaderboards, and includes administrative commands for managing the system.

[![Tests](https://github.com/warnervance/DeltaP/actions/workflows/tests.yml/badge.svg)](https://github.com/warnervance/DeltaP/actions/workflows/tests.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code Coverage](https://img.shields.io/badge/coverage-31%25-orange.svg)](htmlcov/index.html)

## Features

### 📊 Point Management
- **Point Submissions**: Brothers can submit points for pledges with comments
- **Smart Parsing**: Accepts various formats like `+10 Eli Great job` or `+10 to Eli for great work`
- **Float Support**: Automatically rounds float values to integers (e.g., `+10.7` → `11`)
- **Nickname Aliases**: Recognizes common nicknames and maps them to official names
- **Validation**: Ensures only valid pledge names and point values are accepted

### 🎯 Point Tracking
- **Approval System**: Point submissions require admin approval before counting
- **Rankings**: View real-time leaderboards with medal emojis for top 3
- **History**: Track all point entries with timestamps and comments
- **Filtering**: View pending, approved, or rejected points

### 🛡️ Administrative Features
- **Approve/Reject**: Admins can review and approve or reject point submissions
- **Delete Messages Logging**: Tracks deleted messages in a dedicated channel
- **Role-based Permissions**: Certain commands restricted to Info Systems role
- **Remote Shutdown**: Secure bot shutdown with permission checks
- **Ping Command**: Check bot responsiveness and latency

## Installation

### Prerequisites
- Python 3.13 or higher
- Discord Bot Token ([Create one here](https://discord.com/developers/applications))
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/warnervance/DeltaP.git
   cd DeltaP
   ```

2. **Install dependencies using uv**
   ```bash
   uv sync
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root:
   ```env
   # Discord Bot Configuration
   DISCORD_TOKEN=your_discord_bot_token_here

   # Database Configuration
   CSV_NAME=pledge_points.db
   TABLE_NAME=pledge_points

   # Discord Channel Configuration
   CHANNEL_ID=your_points_submission_channel_id
   ```

4. **Configure Discord Bot Intents**

   In the [Discord Developer Portal](https://discord.com/developers/applications):
   - Navigate to your bot application
   - Go to the "Bot" section
   - Enable the following Privileged Gateway Intents:
     - Message Content Intent
     - Server Members Intent (optional, for role checking)

5. **Update pledge configuration**

   Edit `PledgePoints/constants.py` to add current semester pledges:
   ```python
   VALID_PLEDGES: List[str] = [
       "Eli",
       "Evan",
       # ... add your pledges
   ]

   PLEDGE_ALIASES: Dict[str, str] = {
       "Matt": "Matthew",
       # ... add nickname mappings
   }
   ```

6. **Run the bot**
   ```bash
   uv run python main.py
   ```

## Usage

### Point Submission Commands

Submit points in the configured points channel:

```
+10 Eli Great job at recruitment
-5 Matthew Being late to chapter
+15 to Logan for excellent presentation
```

**Format**: `[+/-]<points> [to] <pledge_name> [for] <comment>`

### Slash Commands

#### General Commands
- `/ping` - Check bot responsiveness and latency
- `/test_deleted_channel` - Test deleted messages channel access

#### Point Commands
- `/points_view <entry_id>` - View details of a specific point entry
- `/points_history <pledge_name>` - View point history for a pledge
- `/points_rankings` - Display pledge rankings leaderboard
- `/points_pending` - View all pending point submissions (admin only)
- `/points_approve <entry_ids>` - Approve point submissions (admin only)
- `/points_reject <entry_ids>` - Reject point submissions (admin only)

#### Admin Commands
- `/shutdown` - Remotely shut down the bot (requires Info Systems role)

## Development

### Project Structure

```
DeltaP/
├── commands/           # Bot command modules
│   ├── admin.py       # Administrative commands
│   └── points.py      # Point management commands
├── config/            # Configuration management
│   └── settings.py    # Environment and config loading
├── PledgePoints/      # Core business logic
│   ├── constants.py   # Pledge names, aliases, constants
│   ├── models.py      # Data models
│   ├── validators.py  # Input validation and parsing
│   ├── sqlutils.py    # Database operations
│   ├── pledges.py     # Pledge-specific logic
│   └── messages.py    # Message handling
├── role/              # Role checking utilities
│   └── role_checking.py
├── utils/             # Shared utilities
│   └── discord_helpers.py  # Discord formatting helpers
├── tests/             # Comprehensive test suite
│   ├── commands/
│   ├── config/
│   ├── PledgePoints/
│   └── utils/
├── main.py            # Bot entry point
├── pytest.ini         # Test configuration
└── pyproject.toml     # Project dependencies
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov

# Run specific test file
uv run pytest tests/PledgePoints/test_validators.py

# Run with verbose output
uv run pytest -v
```

### Code Coverage

Current coverage: **31%** (45 tests passing)

- PledgePoints validators: **93%**
- Config settings: **100%**
- Discord helpers: **98%**
- Admin commands: **64%**

Generate HTML coverage report:
```bash
uv run pytest --cov --cov-report=html
open htmlcov/index.html
```

### CI/CD

GitHub Actions automatically runs tests on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

View workflow: `.github/workflows/tests.yml`

## Database Schema

The bot uses SQLite with the following schema:

```sql
CREATE TABLE pledge_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT NOT NULL,
    brother TEXT NOT NULL,
    point_change INTEGER NOT NULL,
    pledge TEXT NOT NULL,
    comment TEXT NOT NULL,
    approval_status TEXT DEFAULT 'pending',
    approved_by TEXT,
    approval_timestamp TEXT
);
```

## Configuration

### Pledge Configuration

Update `PledgePoints/constants.py` each semester:

- `VALID_PLEDGES` - List of valid pledge names
- `PLEDGE_ALIASES` - Nickname to official name mapping
- `RANK_MEDALS` - Emoji medals for rankings
- `POINT_REGEX_PATTERN` - Point parsing regex

### Discord Configuration

Set in `.env` file:

- `DISCORD_TOKEN` - Bot authentication token
- `CHANNEL_ID` - Channel for point submissions
- `CSV_NAME` - SQLite database filename

### Role Permissions

Configure in `role/role_checking.py`:

- Info Systems role ID for admin commands
- Custom role checks as needed

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`uv run pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions and classes
- Write tests for new features
- Maintain or improve code coverage

## Troubleshooting

### Bot won't start
- Verify `DISCORD_TOKEN` is correct in `.env`
- Check that all required intents are enabled in Discord Developer Portal
- Ensure Python 3.13+ is installed

### Point submissions not working
- Verify bot has permission to read messages in the points channel
- Check that pledge names in submission match `VALID_PLEDGES` (case-insensitive)
- Ensure message format is correct: `[+/-]<points> <pledge> <comment>`

### Commands not appearing
- Run `/sync` to force command synchronization
- Check bot has `applications.commands` scope
- Verify bot is in the server with proper permissions

### Database errors
- Ensure `CSV_NAME` path is writable
- Check SQLite database isn't locked by another process
- Verify schema is up to date

## License

This project is private and intended for internal use.

## Authors

- **Warner Vance** - Primary developer
- AI assistance for specific components

## Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Database powered by SQLite
- Testing with pytest and pytest-asyncio
- Dependency management with [uv](https://github.com/astral-sh/uv)

---

**Note**: Remember to update `VALID_PLEDGES` in `PledgePoints/constants.py` at the start of each semester!
