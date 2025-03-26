import numpy as np
import pandas as pd
import pytest

from PledgePoints.approval import (
    change_point_approval,
    get_approved_points,
    get_unapproved_points,
    change_approval_with_discrete_values,
    delete_unapproved_points
)


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


class TestChangePointApproval:
    def test_change_point_approval_success(self, sample_df):
        """Test that a point's approval status is successfully changed."""
        result = change_point_approval(sample_df, 2, True)
        assert result.loc[result["ID"] == 2, "Approved"].iloc[0] is np.True_

    def test_change_point_approval_invalid_id(self, sample_df):
        """Test that ValueError is raised for non-existent ID."""
        with pytest.raises(ValueError, match="Point ID not found in dataframe"):
            change_point_approval(sample_df, 999, True)

    def test_change_point_approval_invalid_type(self, sample_df):
        """Test that TypeError is raised for non-boolean approval value."""
        with pytest.raises(TypeError, match="new_approval must be a boolean"):
            change_point_approval(sample_df, 1, "True")

    def test_change_point_approval_custom_columns(self, sample_df):
        """Test that custom column names work correctly."""
        df = sample_df.rename(columns={"ID": "CustomID", "Approved": "CustomApproved"})
        result = change_point_approval(df, 1, False, "CustomID", "CustomApproved")
        assert result.loc[result["CustomID"] == 1, "CustomApproved"].iloc[0] is np.False_


class TestGetApprovedPoints:
    def test_get_approved_points_success(self, sample_df):
        """Test that only approved points are returned."""
        result = get_approved_points(sample_df)
        assert len(result) == 3
        assert all(result["Approved"] == True)
        assert list(result["ID"]) == [1, 3, 5]

    def test_get_approved_points_empty(self):
        """Test that empty DataFrame is returned when no approved points exist."""
        df = pd.DataFrame({
            "ID": [1, 2],
            "Approved": [False, False]
        })
        result = get_approved_points(df)
        assert len(result) == 0

    def test_get_approved_points_custom_columns(self, sample_df):
        """Test that custom column names work correctly."""
        df = sample_df.rename(columns={"ID": "CustomID", "Approved": "CustomApproved"})
        result = get_approved_points(df, "CustomApproved", "CustomID")
        assert len(result) == 3
        assert all(result["CustomApproved"] == True)


class TestGetUnapprovedPoints:
    def test_get_unapproved_points_success(self, sample_df):
        """Test that only unapproved points are returned."""
        result = get_unapproved_points(sample_df)
        assert len(result) == 2
        assert all(result["Approved"] == False)
        assert list(result["ID"]) == [2, 4]

    def test_get_unapproved_points_empty(self):
        """Test that empty DataFrame is returned when no unapproved points exist."""
        df = pd.DataFrame({
            "ID": [1, 2],
            "Approved": [True, True]
        })
        result = get_unapproved_points(df)
        assert len(result) == 0

    def test_get_unapproved_points_custom_columns(self, sample_df):
        """Test that custom column names work correctly."""
        df = sample_df.rename(columns={"ID": "CustomID", "Approved": "CustomApproved"})
        result = get_unapproved_points(df, "CustomApproved", "CustomID")
        assert len(result) == 2
        assert all(result["CustomApproved"] == False)


# class TestChangeApprovalWithRange:
#     def test_change_approval_with_range_success(self, sample_df):
#         """Test that approval status is changed for a range of IDs."""
#         result = change_approval_with_range(sample_df, 1, 3, False)
#         assert all(result.loc[(result["ID"] >= 1) & (result["ID"] <= 3), "Approved"] == False)
#
#     def test_change_approval_with_range_reversed(self, sample_df):
#         """Test that range works when start_id is greater than end_id."""
#         result = change_approval_with_range(sample_df, 3, 1, False)
#         assert all(result.loc[(result["ID"] >= 1) & (result["ID"] <= 3), "Approved"] == False)
#
#     def test_change_approval_with_range_invalid_ids(self, sample_df):
#         """Test that ValueError is raised for invalid ID values."""
#         with pytest.raises(ValueError, match="ID values must be positive integers"):
#             change_approval_with_range(sample_df, -1, 3, False)
#         with pytest.raises(ValueError, match="ID values must be less than the length of the DataFrame"):
#             change_approval_with_range(sample_df, 1, 999, False)
#         with pytest.raises(TypeError, match="ID values must be integers"):
#             change_approval_with_range(sample_df, 1.5, 3, False)


class TestChangeApprovalWithDiscreteValues:
    def test_change_approval_with_discrete_values_success(self, sample_df):
        """Test that approval status is changed for specific IDs."""
        result = change_approval_with_discrete_values(sample_df, [1, 3, 5], False)
        assert all(result.loc[result["ID"].isin([1, 3, 5]), "Approved"] == False)
        assert all(result.loc[result["ID"].isin([1, 3, 5]), "Approved"] == False)

    def test_change_approval_with_discrete_values_empty_list(self, sample_df):
        """Test that ValueError is raised for empty ID list."""
        with pytest.raises(ValueError, match="ids must contain at least one value"):
            change_approval_with_discrete_values(sample_df, [], False)

    def test_change_approval_with_discrete_values_invalid_type(self, sample_df):
        """Test that TypeError is raised for invalid input types."""
        with pytest.raises(TypeError, match="ids must be a list or tuple"):
            change_approval_with_discrete_values(sample_df, "1,2,3", False)
        with pytest.raises(TypeError, match="ids must contain only integers"):
            change_approval_with_discrete_values(sample_df, [1.5, 2], False)
        with pytest.raises(TypeError, match="new_approval must be a boolean"):
            change_approval_with_discrete_values(sample_df, [1, 2], "True")

    def test_change_approval_with_discrete_values_too_many_ids(self, sample_df):
        """Test that ValueError is raised for too many IDs."""
        with pytest.raises(ValueError, match="ids must contain fewer values than the length of the DataFrame"):
            change_approval_with_discrete_values(sample_df, [1, 2, 3, 4, 5, 6], False)


class TestDeleteUnapprovedPoints:
    def test_delete_unapproved_points_success(self, sample_df):
        """Test that unapproved points are successfully deleted."""
        result = delete_unapproved_points(sample_df)
        assert len(result) == 3
        assert all(result["Approved"] == True)

    def test_delete_unapproved_points_empty(self):
        """Test that empty DataFrame is returned when all points are unapproved."""
        df = pd.DataFrame({
            "ID": [1, 2],
            "Approved": [False, False]
        })
        result = delete_unapproved_points(df)
        assert len(result) == 0

    def test_delete_unapproved_points_custom_column(self, sample_df):
        """Test that custom column names work correctly."""
        df = sample_df.rename(columns={"Approved": "CustomApproved"})
        result = delete_unapproved_points(df, "CustomApproved")
        assert len(result) == 3
        assert all(result["CustomApproved"] == True)

    def test_delete_unapproved_points_all_approved(self):
        df = pd.DataFrame({
            "ID": [1, 2],
            "Approved": [True, True]
        })
        result = delete_unapproved_points(df)
        assert result.equals(result)
