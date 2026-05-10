import sqlite3
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "notices.db"


conn = sqlite3.connect(DB_PATH)



def debug_head(limit=5):

    query = f"""
    SELECT
        id,
        game,
        title,
        date,
        substr(summary, 1, 80) as summary_preview
    FROM notices
    ORDER BY id DESC
    LIMIT {limit}
    """

    df = pd.read_sql_query(query, conn)

    print("\\n===== DB HEAD =====\\n")

    if df.empty:
        print("DB가 비어있음")
        return

    print(df.to_string(index=False))

    print("\\n===================\\n")


if __name__ == "__main__":

    debug_head()