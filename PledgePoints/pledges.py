import pandas as pd
from matplotlib import pyplot as plt
from pandas import DataFrame
import seaborn as sns



def get_pledge_points(db_connection) -> DataFrame:
    """
    Fetches and processes pledge points data from the database.

    This function retrieves the pledge points data including the columns
    Time, PointChange, Pledge, Brother, and Comment from the database.
    It processes the data by converting the Time column to a datetime object
    and sorting it in descending order.

    Args:
        db_connection: Database connection object used to query the data.

    Returns:
        DataFrame: A pandas DataFrame containing the processed pledge points
        data with columns ['Time', 'PointChange', 'Pledge', 'Brother', 'Comment'].
    """
    cursor = db_connection.cursor()
    cursor.execute("SELECT Time, PointChange, Pledge, Brother, Comment FROM Points WHERE approval_status = 'approved'")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=['Time', 'PointChange', 'Pledge', 'Brother', 'Comment'])
    df['Time'] = pd.to_datetime(df['Time'])
    df = df.sort_values(by='Time', ascending=False)
    return df

def rank_pledges(df: DataFrame) -> pd.Series:
    """
    Ranks pledges by the sum of associated point changes in descending order.

    This function groups the provided DataFrame by the 'Pledge' column, sums the
    'PointChange' values for each group, and sorts the results in descending order of
    the summed values. The ranking highlights the pledges with the highest cumulative
    point changes.

    Args:
        df (DataFrame): Input DataFrame containing at least the following columns:
            - 'Pledge': Categorical or string column representing different pledge groups.
            - 'PointChange': Numeric column with values to be summed per group.

    Returns:
        pd.Series: A Series indexed by pledge, with values representing the cumulative
        point changes sorted in descending order.
    """
    return df.groupby('Pledge')['PointChange'].sum().sort_values(ascending=False)

def plot_rankings(rankings: pd.Series) -> str:
    """
    Generate a bar plot of rankings and save it as an image file.

    This function takes a pandas Series representing rankings data
    and creates a bar plot using the Seaborn library. The plot
    displays pledges on the x-axis and their corresponding total
    points on the y-axis. The function saves the plot to a PNG
    file named 'rankings.png' in the current directory and
    returns the filename.

    Args:
        rankings (pd.Series): A pandas Series object where the
            index represents the pledges and the values represent
            their corresponding total points.

    Returns:
        str: The filename of the saved bar plot image.
    """
    sns.set_theme(style="whitegrid")
    # Ensure rankings are sorted in descending order for consistent plotting
    rankings_sorted = rankings.sort_values(ascending=False)
    sns.barplot(x=rankings_sorted.index, y=rankings_sorted.values)
    plt.title("Pledge Rankings by Total Points")
    plt.xlabel("Pledge")
    plt.ylabel("Total Points")
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()
    plt.savefig("rankings.png")
    return "rankings.png"
