import sqlite3

conn = sqlite3.connect("notices.db")


def init_db():

    conn.execute("""

    CREATE TABLE IF NOT EXISTS notices (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game TEXT,
        title TEXT,
        date TEXT,
        url TEXT UNIQUE

    )

    """)

    conn.commit()


def save_notice(data):

    try:

        conn.execute("""

        INSERT INTO notices(game, title, date, url)
        VALUES (?, ?, ?, ?)

        """, (
            data["game"],
            data["title"],
            data["date"],
            data["url"]
        ))

        conn.commit()

    except:
        pass


def load_all():

    cursor = conn.execute("""

    SELECT game, title, date, url
    FROM notices

    """)

    rows = cursor.fetchall()

    return rows