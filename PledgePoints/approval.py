import pandas as pd


def change_point_approval(df, point_id, new_approval=True, id_column_name="ID", approved_column_name="Approved"):
    """
    This function updates the approval status of a specific point in the provided dataframe
    based on the given point ID. The function ensures that the provided `new_approval`
    value is of boolean type and that the specified point ID exists in the dataframe
    under the specified ID column.

    :param df: The Pandas DataFrame containing the dataset where the approval status
    is to be updated.
    :type df: pandas.DataFrame
    :param point_id: The unique identifier of the point whose approval status needs
    to be updated.
    :type point_id: int
    :param new_approval: The new approval status to be assigned. Must be a boolean value.
    :type new_approval: bool
    :param id_column_name: The name of the column in the DataFrame that stores
    identifiers for the points. Defaults to "ID".
    :type id_column_name: str
    :param approved_column_name: The name of the column in the DataFrame that stores
    the approval statuses. Defaults to "Approved".
    :type approved_column_name: str
    :return: A modified DataFrame with the updated approval status for the specified point ID.
    :rtype: pandas.DataFrame

    :raises TypeError: If the `new_approval` parameter is not a boolean value.
    :raises ValueError: If the `point_id` is not found within the specified ID column
    of the DataFrame.
    """

    # Believe it or not but this is much faster than any pandas vectorized thing I've tried so far
    # Input validation
    if type(new_approval) != bool:
        raise TypeError("new_approval must be a boolean")
    if point_id not in df[id_column_name].values:
        raise ValueError("Point ID not found in dataframe")

    # This finds the index values for the approval and ID columns from the given dataframe.
    columns = df.columns.tolist()
    approval_idx, id_idx = None, None
    for idx, column in enumerate(columns):
        if (approval_idx is not None) and (id_idx is not None):
            break  # This ends the loop if we've found both of our column indices
        if column == approved_column_name:  # This finds the index of the approval column
            approval_idx = idx
            continue
        if column == id_column_name:  # This finds the index of the id column
            id_idx = idx
            continue

    rows = df.values.tolist()
    # I know it's crazy but this is actually really fast. Maybe some pandas genius can come up with a better way, but
    # the benchmarking I've done makes it seem that this is the best way -Warner
    for row in rows:
        if row[id_idx] == point_id:
            row[approval_idx] = new_approval
            break
    new_df = pd.DataFrame(rows, columns=columns)
    return new_df


def get_approved_points(df, approval_column_name="Approved", id_column_name="ID"):
    """
    Author: Warner

    Extract rows with approved points from a DataFrame based on a specified column indicating approval status.

    This function filters the input DataFrame to return only rows where the specified
    approval column contains a value of True. The column used for the approval check
    is specified by the `approval_column_name` parameter, which defaults to "Approved". The resulting dataframe is
    sorted by the `id_column_name` column.

    :param id_column_name: The name of the column in the DataFrame that stores the ID column name
    :type id_column_name: str
    :param df: A pandas DataFrame containing the data to be filtered.
    :type df: pandas.DataFrame
    :param approval_column_name: The name of the column that indicates approval status.
        Defaults to "Approved".
    :type approval_column_name: str
    :return: A filtered DataFrame containing only rows where the value in the specified
        approval column is True.
    :rtype: pandas.DataFrame
    """
    return df.loc[df[approval_column_name] == True].sort_values(by=id_column_name)


def get_unapproved_points(df, approval_column_name="Approved", id_column_name="ID"):
    """
    Author: Warner

    Extract rows from the DataFrame that have not been approved.

    This function identifies and returns DataFrame rows where the specified
    approval column has a value of `False`. The resulting rows are sorted
    based on the `id_column_name` column.

    :param id_column_name: The name of the column in the DataFrame that stores the point ID.
    :type id_column_name: str
    :param df: The input DataFrame containing rows and an approval column.
    :type df: pandas.DataFrame
    :param approval_column_name: The column name to check for approval status.
        Defaults to "Approved".
    :type approval_column_name: str
    :return: A filtered DataFrame containing only unapproved rows, sorted
        by the "ID" column.
    :rtype: pandas.DataFrame
    """
    return df.loc[df[approval_column_name] == False].sort_values(by=id_column_name)


def change_approval_with_range(df, start_id, end_id, new_approval=True, id_column_name="ID",
                               approved_column_name="Approved"):
    """
    Author: Warner

    Updates the approval status of entries in a DataFrame for a range of IDs. This
    function is intended to assist in bulk approval or disapproval of records by
    iterating through a given range of IDs and updating their status.

    :param df: The DataFrame containing the data to be updated.
    :param start_id: The starting ID of the range. Must be less than or equal to
        `end_id`.
    :param end_id: The ending ID of the range.
    :param new_approval: The new approval status to assign to entries within the
        specified ID range.
    :param id_column_name: The name of the column in the DataFrame that contains the
        ID values. Defaults to "ID".
    :param approved_column_name: The name of the column in the DataFrame that
        contains the approval status. Defaults to "Approved".
    :return: The updated DataFrame with the approval statuses modified for the given
        ID range.
k
    """
    # This check various input validation things
    if start_id < 0 or end_id < 0:
        raise ValueError("ID values must be positive integers")
    if start_id > len(df) or end_id > len(df):
        raise ValueError("ID values must be less than the length of the DataFrame")
    if type(start_id) != int or type(end_id) != int:
        raise TypeError("ID values must be integers")

    # If the user swaps the start and end ids then we switch tem
    if start_id > end_id:
        start_id, end_id = end_id, start_id

    # This iterates through the ids and makes the approval change for each one
    for i in range(start_id, end_id + 1):
        df = change_point_approval(df, i, new_approval, id_column_name, approved_column_name)
    return df


def change_approval_with_discrete_values(df, ids, new_approval=True, id_column_name="ID",
                                         approved_column_name="Approved"):
    """
    Author: Warner

    Modifies the approval status in a DataFrame for specific rows identified by their unique IDs.
    This function updates the `Approved` column for rows matching the IDs in the provided list or
    tuple, changing their values to the specified boolean (`True` or `False`) for approval. The operation
    is sensitive to the constraints of the input data, ensuring that types and lengths of arguments meet
    the expectations before proceeding.

    :param df:
        The DataFrame in which the approval status values will be updated.
    :type df: pandas.DataFrame
    :param ids:
        A list or tuple containing integer IDs of the rows to modify.
    :type ids: list | tuple
    :param new_approval
        The boolean value to set as the new approval status (e.g., `True` for approved,
        `False` for not approved).
    :type new_approval: bool
    :param id_column_name
        The name of the column in the DataFrame that contains the unique IDs.
        Defaults to `"ID"`.
    :type id_column_name: str
    :param approved_column_name
        The name of the column in the DataFrame that contains approval status values.
        Defaults to `"Approved"`.
    :type approved_column_name: str
    :return: DataFrame
        Returns the modified DataFrame with updated approval status values for the specified rows.
    :raises TypeError:
        - If `ids` is not a list or tuple.
        - If `new_approval` is not a boolean.
        - If elements within `ids` are not integers.
    :raises ValueError:
        - If `ids` is empty.
        - If the length of `ids` exceeds the number of rows in the DataFrame.
    """
    # Input validation
    if not isinstance(ids, (list, tuple)):
        raise TypeError("ids must be a list or tuple")
    if type(new_approval) != bool:
        raise TypeError("new_approval must be a boolean")
    if len(ids) == 0:
        raise ValueError("ids must contain at least one value")
    if len(ids) > len(df):
        raise ValueError("ids must contain fewer values than the length of the DataFrame")
    if not all(isinstance(id, int) for id in ids):
        raise TypeError("ids must contain only integers")

    # This iterates through the ids and makes the approval change for each one
    for i in ids:
        df = change_point_approval(df, i, new_approval, id_column_name, approved_column_name)
    return df


def delete_unapproved_points(df, approved_column_name="Approved"):
    """
    Author: Warner

    Goes through the rows in the DataFrame and deletes any rows that have their value in `approved_column_name~ as
    False
    :param df: input points dataframe
    :type df: pandas.DataFrame
    :param approved_column_name: The name
    :type approved_column_name: str
    :return: output dataframe without unapproved points
    :rtype: pandas.DataFrame
    """
    disapproved_idx = df.loc[df[approved_column_name] == False].index
    df = df.drop(disapproved_idx, axis=0)
    return df
