import os
import time

import numpy as np
import pandas as pd
from pandas import DataFrame


def create_csv(filename: str,
               columns: tuple = ("ID", "Time", "PointChange", "Pledge", "Brother", "Comment", "Approved")) -> str:
    """
    Author: Warner
    This will create a csv file with the points columns in the correct order.
    :param filename: The name/path of the file to create.
    :type filename: str
    :param columns: The names of the columns to include in the file.
    :type columns: tuple
    :return: Boolean indicating if the file was successfully created.
    :rtype: bool
    """
    if os.path.exists(filename):
        raise FileExistsError("The file {} already exists.".format(filename))
    df: pd.DataFrame = pd.DataFrame(columns=columns)
    df.to_csv(filename, index=False)
    return filename


def read_csv(filename: str) -> DataFrame:
    """
    Author: Warner

    Reads the points CSV file and returns a pandas DataFrame.
    :param filename: The name of the file to read.
    :type filename: str
    :return: A pandas DataFrame containing the data from the CSV file.
    :type: pandas.DataFrame
    """
    # Values in here are hardcoded. This is usually not good practice, but to change the columns for everything else
    # you can just change the values here. - Warner
    columns: tuple = ("ID", "Time", "PointChange", "Pledge", "Brother", "Comment", "Approved")
    if not os.path.exists(filename):
        raise FileNotFoundError("The file {} doesn't exist.".format(filename))
    dtypes: dict = {columns[0]: "uint16",  # ID should never be negative.
                    columns[2]: "int8",
                    # This limits point change values to -128 to 127. That shouldn't be an issue, but if
                    # you run into overflow problems you can change to int16 or in32.
                    columns[3]: "string",
                    columns[4]: "string",
                    columns[5]: "string",
                    columns[6]: "bool"}
    # Another option to optimize these dtypes for lower ram usage would be to store Pledge and Brother as int ids and
    # be able to map ids to names using a dict if needed.
    # Memory usage 3.8 MB with optimizations and 4.9 MB without with a 100,000 row dataframe (5.5 MB csv file). This hardly
    # seems worth it for our smaller datasets.
    df: pd.DataFrame = pd.read_csv(filename, dtype=dtypes, parse_dates=[columns[1]])
    return df


def write_csv(df: DataFrame, filename: str = "MasterPoints.csv") -> str:
    """
    Author: Warner
    Writes the points CSV file and returns the name of the new CSV file.
    :param df: The pandas DataFrame containing the data from the CSV file.
    :type df: pandas.DataFrame
    :param filename: The name of the file to write.
    :type filename: str
    :return: The name of the new CSV file.
    :rtype: str
    """
    df.to_csv(filename, index=False)
    return filename

def append_row_to_df(df: DataFrame, new_row: list) -> DataFrame:
    """

    Author: Warner

    Appends a new row to the given DataFrame. new_row should be a list of values that make up the vow, and should have
    the same number of columns as the dataframe.
    :param df: the pandas Dataframe that will be appended.
    :type df: DataFrame
    :param new_row: a list of values that make up the new row.
    :type new_row: list
    :return: A pandas DataFrame containing the new row appended.
    :rtype: DataFrame
    """
    # Warner: According to a stake overflow post I read turning a dataframe into a list of rows, appending that list
    # and then making a new dataframe is the most efficient way to append a row to a dataframe. Might be bs, but
    # it seems working fine so far

    # This creates a list of lists.  Each list in the list contains the values of the row
    rows: list = df.values.tolist()
    headers: list = df.columns.tolist()
    if len(new_row) != len(headers):
        raise Exception("The new row must have the same number of columns as the headers.")
    rows.append(new_row)
    return pd.DataFrame(rows, columns=headers)


def get_current_time() -> np.datetime64:
    """
    Returns the current time in milliseconds as a ``numpy.datetime64`` object.

    The function converts the current epoch time obtained from the system
    into a format that is compatible with ``numpy.datetime64``. The value is
    represented with millisecond precision.

    :return: Current time as a ``numpy.datetime64`` instance in milliseconds.
    """
    return np.datetime64(int(round(time.time() * 1000)), 'ms')
