import pandas as pd
import pytest

from PledgePoints.pledges import *


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
