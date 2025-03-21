from PledgePoints.csvutils import append_row_to_df, get_current_time


def get_one_pledge_points(df, pledge, point_column_name="PointChange", pledge_column_name="Pledge"):
    """
    Author: Warner
    Calculates the total number of points for a specific pledge by summing the PointChange

    :param pledge_column_name: The name of the column containing the pledge names
    :type pledge_column_name: str
    :param point_column_name: The name of the column containing the point changes
    :type point_column_name: str
    :param df: A pandas DataFrame containing the data. It must have at least
        the columns "PointChange" and "Pledge".
    :type df: pandas.DataFrame
    :param pledge: The specific value within the "Pledge" column to filter rows
        for summing the corresponding "PointChange" values.
    :type pledge: str
    :return: Returns an integer representing the total sum of "PointChange"
        values for the filtered rows.
    :rtype: int
    """
    return int(df[point_column_name].loc[df[pledge_column_name] == pledge].sum())


def get_pledge_names(df, pledge_column_name="Pledge"):
    """
    Author: Warner
    Returns a list of the unique pledge names from the Dataframe
    :param df: The pandas DataFrame containing the data.
    :type df: pandas.DataFrame
    :param pledge_column_name: The name of the column containing the pledge names
    :type pledge_column_name: str
    :return: A list of the pledge names without duplicates in alphabetical order.
    :rtype: list
    """
    pledges = df[pledge_column_name].to_list()
    pledges = list(set(pledges))
    pledges = sorted(pledges)
    return pledges


def get_point_totals(df, pledge_column_name="Pledge"):
    """
    Author: Warner
    Calculates cumulative point totals for unique pledges in the DataFrame.

    The function extracts all unique pledges from a given column of the
    DataFrame and calculates cumulative point totals for each unique
    pledge. The results are then returned as a list containing the unique
    pledges and their corresponding cumulative totals.

    :param pledge_column_name: The name of the column containing the pledge names
    :type pledge_column_name: str
    :param df: The input pandas DataFrame containing the column `Pledge`.
    :type df: pandas.DataFrame
    :return: A list with two elements:
        - A list of unique pledges found in the `Pledge` column.
        - A list of the point totals for each unique pledge.
    :rtype: list
    """
    pledges = get_pledge_names(df, pledge_column_name)
    totals = []
    for pledge in pledges:
        totals.append(get_one_pledge_points(df, pledge))
    del df
    return [pledges, totals]


def get_point_history(df, pledge, pledge_column_name="Pledge", point_column_name="PointChange", time_column_name="Time",
                      brother_column_name="Brother", comment_column_name="Comment", approved_column_name="Approved"):
    """
    Author: Warner
    Filters and reorganizes a DataFrame to provide the point history of a specific pledge. The function
    filters rows based on the specified pledge, sorts them by time, and selects key columns to return
    a structured history of point changes.

    :param df: The input pandas DataFrame containing point records.
    :param pledge: The pledge to filter records by.
    :param pledge_column_name: The name of the column containing pledge data.
    :param point_column_name: The name of the column containing point change information.
    :param time_column_name: The name of the column containing timestamps of point changes.
    :param brother_column_name: The name of the column containing brother information.
    :param comment_column_name: The name of the column containing comments about point changes.
    :return: A DataFrame filtered, sorted, and reorganized to show the point history of the specified pledge.
    """
    df = df.loc[df[pledge_column_name] == pledge]
    df = df.sort_values(by=time_column_name)
    df = df.reset_index(drop=True)
    df = df[[time_column_name, point_column_name, pledge_column_name, brother_column_name, comment_column_name, approved_column_name]]
    return df


def change_pledge_points(df, pledge, brother, comment, points):
    """
    Modify the points associated with a pledge by appending a new row containing
    the relevant details to the provided DataFrame. This function records the
    update by adding information such as the timestamp, points value, pledge name,
    responsible brother, and a related comment.

    :param df: The DataFrame to which the new row will be appended. This should
        contain previous pledge point records.
    :type df: pandas.DataFrame
    :param pledge: The name or identifier of the pledge whose points are being
        adjusted.
    :type pledge: str
    :param brother: The name or identifier of the brother responsible for
        the points adjustment.
    :type brother: str
    :param time: The timestamp indicating when the points change is made.
    :type time: float
    :param comment: A brief description or context for the points adjustment.
    :type comment: str
    :param points: The numerical value of points to be added or deducted.
    :type points: int
    :return: A boolean value indicating whether the operation was successful.
    """
    new_row = [get_current_time(), points, pledge, brother, comment, False]
    append_row_to_df(df, new_row)
    return True

