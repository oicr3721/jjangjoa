import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "notices.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():

    conn.execute("""

    CREATE TABLE IF NOT EXISTS notices (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game TEXT,
        title TEXT,
        date TEXT,
        url TEXT UNIQUE,
        content TEXT,
        summary TEXT

    )

    """)

    conn.commit()



def save_notice(data):

    try:

        conn.execute("""

        INSERT INTO notices(
            game,
            title,
            date,
            url,
            content,
            summary
        )
        VALUES (?, ?, ?, ?, ?, ?)

        """, (
            data["game"],
            data["title"],
            data["date"],
            data["url"],
            data.get("content", ""),
            data.get("summary", "")
        ))

        conn.commit()

    except Exception as e:
        print("DB save error:", e)



def load_all():

    cursor = conn.execute("""

    SELECT
        game,
        title,
        date,
        url,
        summary
    FROM notices
    ORDER BY id DESC

    """)

    rows = cursor.fetchall()

    return rows