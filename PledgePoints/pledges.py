import pandas as pd
from matplotlib import pyplot as plt
from pandas import DataFrame
import seaborn as sns

def change_pledge_points(db_connection, data_tuple) -> bool:
    if len(data_tuple) != 5:
        return False
    if data_tuple[1] not in range(-9223372036854775808, 9223372036854775807):
        raise ValueError("PointChange is too large")
    cursor = db_connection.cursor()
    sqlite_insert_query = """INSERT INTO Points
                              (Time, PointChange, Pledge, Brother, Comment)
                               VALUES
                              (?,?,?,?,?)"""
    cursor.execute(sqlite_insert_query, data_tuple)
    db_connection.commit()
    db_connection.close()
    return True

def get_pledge_points(db_connection) -> DataFrame:
    cursor = db_connection.cursor()
    cursor.execute("SELECT Time, PointChange, Pledge, Brother, Comment FROM Points")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=['Time', 'PointChange', 'Pledge', 'Brother', 'Comment'])
    df['Time'] = pd.to_datetime(df['Time'])
    df = df.sort_values(by='Time', ascending=False)
    return df

def rank_pledges(df: DataFrame) -> pd.Series:
    return df.groupby('Pledge')['PointChange'].sum().sort_values(ascending=False)

def plot_rankings(rankings: pd.Series) -> str:
    sns.set_theme(style="darkgrid")
    sns.barplot(x=rankings.index, y=rankings.values)
    plt.title("Pledge Rankings by Total Points")
    plt.xlabel("Pledge")
    plt.ylabel("Total Points")
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()
    plt.savefig("rankings.png")
    return "rankings.png"