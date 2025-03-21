import os

import numpy as np
import pandas as pd
import pytest
from PledgePoints.csvutils import create_csv, read_csv, get_current_time, append_row_to_df


@pytest.fixture
def temp_file(tmpdir):
    """Fixture to provide a temporary file path."""
    return os.path.join(tmpdir, "test.csv")


class TestCreateCsv:
    def test_create_csv_file_creation(self, temp_file):
        """Test that a CSV file is created successfully."""
        columns = ("A", "B", "C")
        result = create_csv(temp_file, columns=columns)
        assert os.path.exists(temp_file)
        assert pd.read_csv(result).columns.tolist() == list(columns)

    def test_create_csv_existing_file_error(self, temp_file):
        """Test that FileExistsError is raised if the file already exists."""
        open(temp_file, "w").close()  # Create the file
        with pytest.raises(FileExistsError):
            create_csv(temp_file)

    def test_create_csv_default_columns(self, temp_file):
        """Test that default columns are used when none are specified."""
        result = create_csv(temp_file)
        expected_columns = ["ID", "Time", "PointChange", "Pledge", "Brother", "Comment", "Approved"]
        assert pd.read_csv(result).columns.tolist() == expected_columns

class TestReadCsv:
    def test_read_csv_file_not_found(self):
        """Test that FileNotFoundError is raised if the file does not exist."""
        with pytest.raises(FileNotFoundError):
            read_csv("non_existent_file.csv")


class TestGetCurrentTime:
    def test_get_current_time_type(self):
        """Test that get_current_time returns a numpy.datetime64 object."""
        result = get_current_time()
        assert isinstance(result, np.datetime64)
# Checks if precision includes milliseconds




class TestAppendRowToDf:
    def test_append_row_to_df_success(self):
        """Test that a new row is successfully appended to the DataFrame."""
        data = {
            "ID": [1],
            "Time": [get_current_time()],
            "PointChange": [50],
            "Pledge": ["Pledge1"],
            "Brother": ["John"],
            "Comment": ["Test Comment"],
            "Approved": [True],
        }
        df = pd.DataFrame(data)

        new_row = [2, get_current_time(), 75, "Pledge2", "Doe", "Another Comment", False]
        updated_df = append_row_to_df(df, new_row)

        assert len(updated_df) == len(df) + 1
        assert updated_df.iloc[-1].tolist() == new_row

    def test_append_row_to_df_column_mismatch(self):
        """Test that an exception is raised when the new row has a different number of columns."""
        data = {
            "ID": [1],
            "Time": [get_current_time()],
            "PointChange": [50],
            "Pledge": ["Pledge1"],
            "Brother": ["John"],
            "Comment": ["Test Comment"],
            "Approved": [True],
        }
        df = pd.DataFrame(data)

        new_row = [2, get_current_time(), 75, "Pledge2"]  # Wrong size (missing columns)
        with pytest.raises(Exception, match="The new row must have the same number of columns as the headers."):
            append_row_to_df(df, new_row)

    def test_append_row_to_empty_dataframe(self):
        """Test that a row is successfully appended to an empty DataFrame."""
        columns = ["ID", "Time", "PointChange", "Pledge", "Brother", "Comment", "Approved"]
        df = pd.DataFrame(columns=columns)

        new_row = [1, get_current_time(), 50, "Pledge1", "John", "First comment", True]
        updated_df = append_row_to_df(df, new_row)

        assert len(updated_df) == 1
        assert updated_df.iloc[0].tolist() == new_row