import os

import pandas as pd

def get_one_pledge_points(df, pledge, point_column_name="PointChange", pledge_column_name="Pledge"):
    """
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

    :param df: The pandas DataFrame containing the data.
    :type df: pandas.DataFrame
    :param pledge_column_name: The name of the column containing the pledge names
    :type pledge_column_name: str
    :return: A list of the pledge names without duplicates in no particular order
    :rtype: list
    """
    pledges = df[pledge_column_name].to_list()
    pledges = list(set(pledges))
    return pledges


def get_point_totals(df, pledge_column_name="Pledge"):
    """
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
                  brother_column_name="Brother", comment_column_name="Comment"):
    """
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
    df = df[[time_column_name, point_column_name, pledge_column_name, brother_column_name, comment_column_name]]
    return df


def create_csv(filename, columns = ["Time", "PointChange", "Pledge", "Brother", "Comment"]):
    """
    This will create a csv file with the specified columns.

    :param columns: a list of strings containing the column names
    :type columns: list
    :param filename: The name/path of the file to create.
    :type filename: str
    :return: Boolean indicating if the file was successfully created.
    :rtype: bool
    """
    if os.path.exists(filename):
        raise FileExistsError("The file {} already exists.".format(filename))
        return False
    df = pd.DataFrame(columns=columns)
    df.to_csv(filename, index=False)
    return True


def read_csv(filename):
    """
    Reads a CSV file and returns a pandas DataFrame.
    :param filename: The name of the file to read.
    :type filename: str
    :return: A pandas DataFrame containing the data from the CSV file.
    :type: pandas.DataFrame
    """
    if not os.path.exists(filename):
        raise FileNotFoundError("The file {} doesn't exist.".format(filename))
    df = pd.read_csv(filename)
    return df


def append_row_to_df(df, new_row):
    """
    Appends a new row to the given DataFrame. new_row should be a list of values
    :param df:
    :param new_row:
    :return:
    """
    rows = df.values.tolist()
    headers = df.columns.tolist()
    if len(new_row) != len(headers):
        raise Exception("The new row must have the same number of columns as the headers.")
        return False
    rows.append(new_row)
    return pd.DataFrame(rows, columns=headers)
