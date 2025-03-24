import os
import sys
from pathlib import Path

import pytest

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Set up test environment variables
os.environ['DISCORD_TOKEN'] = 'test_token'
os.environ['CSV_NAME'] = 'test_points.csv'


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup and teardown for each test"""
    # Setup
    yield
    # Teardown
    # Clean up any test files if needed
    pass
