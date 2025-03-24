import numpy as np
import pandas as pd
import pytest

from PledgePoints.pledges import *


@pytest.fixture
def sample_df():
    """Fixture to provide a sample DataFrame for testing."""
    data = {
        "ID": [1, 2, 3, 4, 5],
        "Time": [np.datetime64("2024-01-01")] * 5,
        "PointChange": [10, 20, 30, 40, 50],
        "Pledge": ["P1", "P2", "P3", "P4", "P5"],
        "Brother": ["B1", "B2", "B3", "B4", "B5"],
        "Comment": ["C1", "C2", "C3", "C4", "C5"],
        "Approved": [True, False, True, False, True]
    }
    return pd.DataFrame(data)


class TestGetOnePledgePoints:
    def test_get_one_pledge_points_valid_pledge(self):
        """Test calculating points for a valid pledge."""
        data = {
            "Pledge": ["Pledge1", "Pledge2", "Pledge1"],
            "PointChange": [10, 15, 20],
        }
        df = pd.DataFrame(data)
        pledge = "Pledge1"
        result = get_one_pledge_points(df, pledge)
        assert result == 30
    def test_get_one_pledge_points_invalid_pledge(self):
        """Test calculating points for a pledge not present in the DataFrame."""
        data = {
            "Pledge": ["Pledge1", "Pledge2"],
            "PointChange": [10, 15],
        }
        df = pd.DataFrame(data)
        pledge = "Pledge3"
        result = get_one_pledge_points(df, pledge)
        assert result == 0

    def test_get_one_pledge_points_empty_dataframe(self):
        """Test behavior with an empty DataFrame."""
        data = {
            "Pledge": [],
            "PointChange": [],
        }
        df = pd.DataFrame(data)
        pledge = "Pledge1"
        result = get_one_pledge_points(df, pledge)
        assert result == 0

    def test_get_one_pledge_points_custom_columns(self):
        """Test calculating points with custom column names."""
        data = {
            "CustomPledge": ["Pledge1", "Pledge2", "Pledge1"],
            "CustomPoints": [5, 10, 15],
        }
        df = pd.DataFrame(data)
        pledge = "Pledge1"
        result = get_one_pledge_points(df, pledge, point_column_name="CustomPoints", pledge_column_name="CustomPledge")
        assert result == 20

    def test_get_one_pledge_points_no_matching_rows(self):
        """Test behavior when no rows match the specified pledge."""
        data = {
            "Pledge": ["Pledge2", "Pledge3"],
            "PointChange": [10, 20],
        }
        df = pd.DataFrame(data)
        pledge = "Pledge1"
        result = get_one_pledge_points(df, pledge)
        assert result == 0




class TestGetPledgeNames:
    def test_get_pledge_names_regular_case(self):
        """Test retrieving unique pledge names from a standard DataFrame."""
        data = {"Pledge": ["Pledge1", "Pledge2", "Pledge1"]}
        df = pd.DataFrame(data)
        result = get_pledge_names(df)
        assert set(result) == {"Pledge1", "Pledge2"}

    def test_get_pledge_names_empty_dataframe(self):
        """Test retrieving pledge names when the DataFrame is empty."""
        data = {"Pledge": []}
        df = pd.DataFrame(data)
        result = get_pledge_names(df)
        assert result == []

    def test_get_pledge_names_with_custom_column(self):
        """Test retrieving pledge names with a custom pledge column."""
        data = {"CustomPledge": ["Pledge1", "Pledge3", "Pledge3"]}
        df = pd.DataFrame(data)
        result = get_pledge_names(df, pledge_column_name="CustomPledge")
        assert set(result) == {"Pledge1", "Pledge3"}

    def test_get_pledge_names_no_duplicates(self):
        """Test behavior when all pledges are duplicate."""
        data = {"Pledge": ["Pledge4", "Pledge4", "Pledge4"]}
        df = pd.DataFrame(data)
        result = get_pledge_names(df)
        assert result == ["Pledge4"]

    def test_get_pledge_names_case_sensitivity(self):
        """Test retrieving pledge names with case sensitivity."""
        data = {"Pledge": ["PledgeA", "pledgea", "PledgeA"]}
        df = pd.DataFrame(data)
        result = get_pledge_names(df)
        assert set(result) == {"PledgeA", "pledgea"}




class TestGetPointTotals:
    def test_get_point_totals_standard_case(self):
        """Test calculating cumulative point totals for multiple pledges."""
        data = {
            "Pledge": ["Pledge1", "Pledge2", "Pledge1", "Pledge3", "Pledge2"],
            "PointChange": [10, 20, 30, 40, 50],
        }
        df = pd.DataFrame(data)
        result = get_point_totals(df)
        assert result == [["Pledge1", "Pledge2", "Pledge3"], [40, 70, 40]]
    def test_get_point_totals_empty_dataframe(self):
        """Test behavior when the DataFrame is empty."""
        data = {
            "Pledge": [],
            "PointChange": [],
        }
        df = pd.DataFrame(data)
        result = get_point_totals(df)
        assert result == [[], []]

    def test_get_point_totals_no_matching_rows(self):
        """Test behavior when no rows match the specified conditions in DataFrame."""
        data = {
            "Pledge": ["PledgeX", "PledgeY"],
            "PointChange": [5, 10],
        }
        df = pd.DataFrame(data)
        df = df[df["Pledge"] == "NonExistent"]
        result = get_point_totals(df)
        assert result == [[], []]



class TestGetPointHistory:
    def test_get_point_history_for_valid_pledge(self):
        """Test filtering and organizing data for a specific pledge."""
        data = {
            "Pledge": ["Pledge1", "Pledge2", "Pledge1"],
            "PointChange": [10, 15, 20],
            "Time": ["2023-10-01", "2023-10-02", "2023-10-03"],
            "Brother": ["John", "Jane", "Smith"],
            "Comment": ["First", "Second", "Third"],
            "Approved": [True, False, True],
        }
        df = pd.DataFrame(data)
        pledge = "Pledge1"
        result = get_point_history(df, pledge)
        assert result.equals(
            pd.DataFrame({
                "Time": ["2023-10-01", "2023-10-03"],
                "PointChange": [10, 20],
                "Pledge": ["Pledge1", "Pledge1"],
                "Brother": ["John", "Smith"],
                "Comment": ["First", "Third"],
                "Approved": [True, True],
            }).reset_index(drop=True)
        )

    def test_get_point_history_empty_dataframe(self):
        """Test behavior with an empty DataFrame."""
        data = {
            "Pledge": [],
            "PointChange": [],
            "Time": [],
            "Brother": [],
            "Comment": [],
            "Approved": [],
        }
        df = pd.DataFrame(data)
        pledge = "Pledge1"
        result = get_point_history(df, pledge)
        assert result.empty

    def test_get_point_history_no_matching_pledge(self):
        """Test behavior when no pledge matches the input."""
        data = {
            "Pledge": ["Pledge2", "Pledge3"],
            "PointChange": [10, 20],
            "Time": ["2023-10-02", "2023-10-03"],
            "Brother": ["Jane", "Smith"],
            "Comment": ["Second", "Third"],
            "Approved": [False, True],
        }
        df = pd.DataFrame(data)
        pledge = "Pledge1"
        result = get_point_history(df, pledge)
        assert result.empty

    def test_get_point_history_custom_columns(self):
        """Test filtering and organizing data with custom column names."""
        data = {
            "CustomPledge": ["Pledge1", "Pledge2", "Pledge1"],
            "CustomPoints": [10, 15, 20],
            "CustomTime": ["2023-10-01", "2023-10-02", "2023-10-03"],
            "CustomBrother": ["John", "Jane", "Smith"],
            "CustomComment": ["First", "Second", "Third"],
            "CustomApproved": [True, False, True],
        }
        df = pd.DataFrame(data)
        pledge = "Pledge1"
        result = get_point_history(
            df,
            pledge,
            pledge_column_name="CustomPledge",
            point_column_name="CustomPoints",
            time_column_name="CustomTime",
            brother_column_name="CustomBrother",
            comment_column_name="CustomComment",
            approved_column_name="CustomApproved",
        )
        assert result.equals(
            pd.DataFrame({
                "CustomTime": ["2023-10-01", "2023-10-03"],
                "CustomPoints": [10, 20],
                "CustomPledge": ["Pledge1", "Pledge1"],
                "CustomBrother": ["John", "Smith"],
                "CustomComment": ["First", "Third"],
                "CustomApproved": [True, True],
            }).reset_index(drop=True)
        )


class TestChangePledgePoints:
    def test_append_new_row(self):
        """Test appending a new row for a valid pledge."""
        data = {
            "ID": [0, 1],
            "Time": ["2023-10-01", "2023-10-02"],
            "PointChange": [10, -5],
            "Pledge": ["Pledge1", "Pledge1"],
            "Brother": ["John", "Jane"],
            "Comment": ["First update", "Correction"],
            "Approved": [True, False],
        }
        df = pd.DataFrame(data)
        updated_df = change_pledge_points(df, "Pledge1", "Smith", "Added points", 15)
        assert len(updated_df) == 3
        assert updated_df.iloc[-1].to_dict() == {
            "ID": 2,
            "Time": updated_df.iloc[-1]["Time"],  # Dynamic time
            "PointChange": 15,
            "Pledge": "Pledge1",
            "Brother": "Smith",
            "Comment": "Added points",
            "Approved": False,
        }

    def test_empty_dataframe_initial_row(self):
        """Test adding the first row to an empty DataFrame."""
        data = {
            "ID": [],
            "Time": [],
            "PointChange": [],
            "Pledge": [],
            "Brother": [],
            "Comment": [],
            "Approved": [],
        }
        df = pd.DataFrame(data)
        updated_df = change_pledge_points(df, "Pledge1", "John", "Initial points", 10)
        assert len(updated_df) == 1
        assert updated_df.iloc[0].to_dict() == {
            "ID": 0,
            "Time": updated_df.iloc[0]["Time"],  # Dynamic time
            "PointChange": 10,
            "Pledge": "Pledge1",
            "Brother": "John",
            "Comment": "Initial points",
            "Approved": False,
        }

    def test_non_integer_points(self):
        """Test automatic conversion of non-integer point values."""
        data = {
            "ID": [0],
            "Time": ["2023-10-01"],
            "PointChange": [10],
            "Pledge": ["Pledge1"],
            "Brother": ["John"],
            "Comment": ["First update"],
            "Approved": [True],
        }
        df = pd.DataFrame(data)
        updated_df = change_pledge_points(df, "Pledge2", "Jane", "Added points", "20")
        assert updated_df.iloc[-1]["PointChange"] == 20  # Verify conversion to integer

    def test_invalid_row_length(self):
        """Test error handling for incorrect row length during append."""
        data = {
            "ID": [0],
            "Time": ["2023-10-01"],
            "PointChange": [10],
            "Pledge": ["Pledge1"],
            "Brother": ["John"],
            "Comment": ["First update"],
            "Approved": [True],
        }
        df = pd.DataFrame(data)
        with pytest.raises(Exception, match="The new row must have the same number of columns as the headers."):
            append_row_to_df(df, [0, "2023-10-05", 10, "Pledge1", "John"])  # Missing values


class TestChangePreviousPointEntry:
    def test_change_previous_point_entry_all_fields(self, sample_df):
        """Test changing all fields of a point entry."""
        result = change_previous_point_entry(
            sample_df,
            ID=1,
            new_pledge="NewPledge",
            new_points=75,
            new_brother="NewBrother",
            new_comment="New Comment"
        )
        modified_row = result.loc[result["ID"] == 1]
        assert modified_row["Pledge"].iloc[0] == "NewPledge"
        assert modified_row["PointChange"].iloc[0] == 75
        assert modified_row["Brother"].iloc[0] == "NewBrother"
        assert modified_row["Comment"].iloc[0] == "New Comment"
        # Check that Time and Approved weren't changed
        assert modified_row["Time"].iloc[0] == sample_df.loc[sample_df["ID"] == 1, "Time"].iloc[0]
        assert modified_row["Approved"].iloc[0] == sample_df.loc[sample_df["ID"] == 1, "Approved"].iloc[0]

    def test_change_previous_point_entry_single_field(self, sample_df):
        """Test changing only one field while leaving others unchanged."""
        result = change_previous_point_entry(sample_df, ID=1, new_comment="Only Comment Changed")
        modified_row = result.loc[result["ID"] == 1]
        original_row = sample_df.loc[sample_df["ID"] == 1]

        # Check that only comment changed
        assert modified_row["Comment"].iloc[0] == "Only Comment Changed"
        # Check that other fields remained the same
        assert modified_row["Pledge"].iloc[0] == original_row["Pledge"].iloc[0]
        assert modified_row["PointChange"].iloc[0] == original_row["PointChange"].iloc[0]
        assert modified_row["Brother"].iloc[0] == original_row["Brother"].iloc[0]
        assert modified_row["Time"].iloc[0] == original_row["Time"].iloc[0]
        assert modified_row["Approved"].iloc[0] == original_row["Approved"].iloc[0]

    def test_change_previous_point_entry_invalid_id(self, sample_df):
        """Test that attempting to change a non-existent ID raises an error."""
        with pytest.raises(IndexError):
            change_previous_point_entry(sample_df, ID=999, new_comment="Should Fail")

    def test_change_previous_point_entry_custom_id_column(self, sample_df):
        """Test that custom ID column name works correctly."""
        df = sample_df.rename(columns={"ID": "CustomID"})
        result = change_previous_point_entry(
            df,
            ID=1,
            new_pledge="NewPledge",
            id_column_name="CustomID"
        )
        assert result.loc[result["CustomID"] == 1, "Pledge"].iloc[0] == "NewPledge"

    def test_change_previous_point_entry_preserve_data(self, sample_df):
        """Test that the function preserves all data when modifying an entry."""
        # First, sort by a different column to change order
        reordered_df = sample_df.sort_values(by="PointChange", ascending=False)
        result = change_previous_point_entry(reordered_df, ID=1, new_comment="New Comment")

        # Check that all original rows except the modified one are present and unchanged
        for idx, row in reordered_df.iterrows():
            if row["ID"] != 1:  # Skip the modified row
                matching_rows = result.loc[result["ID"] == row["ID"]]
                assert not matching_rows.empty, f"Row with ID {row['ID']} not found in result"
                matching_row = matching_rows.iloc[0]
                assert row["Pledge"] == matching_row["Pledge"]
                assert row["PointChange"] == matching_row["PointChange"]
                assert row["Brother"] == matching_row["Brother"]
                assert row["Comment"] == matching_row["Comment"]
                assert row["Approved"] == matching_row["Approved"]

        # Check the modified row
        modified_rows = result.loc[result["ID"] == 1]
        assert not modified_rows.empty, "Modified row with ID 1 not found in result"
        modified_row = modified_rows.iloc[0]
        assert modified_row["Comment"] == "New Comment"
        assert len(result) == len(reordered_df)  # No rows were added or removed
