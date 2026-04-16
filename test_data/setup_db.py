import sqlite3
from config.paths import DB_PATH


def setup():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.executescript("""
            DROP TABLE IF EXISTS users;
            DROP TABLE IF EXISTS auth;

            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                expected_email TEXT,
                expected_first_name TEXT
            );

            CREATE TABLE auth (
                id INTEGER PRIMARY KEY,
                scenario TEXT,
                email TEXT,
                password TEXT,
                expected_status INTEGER,
                expected_error TEXT
            );
        """)

        cursor.executemany("INSERT INTO users (user_id, expected_email, expected_first_name) VALUES (?, ?, ?)", [
            (1, "george.bluth@reqres.in", "George"),
            (2, "janet.weaver@reqres.in", "Janet"),
            (3, "emma.wong@reqres.in", "Emma"),
        ])

        cursor.executemany("INSERT INTO auth (scenario, email, password, expected_status, expected_error) VALUES (?, ?, ?, ?, ?)", [
            ("valid_login", "eve.holt@reqres.in", "cityslicka", 200, None),
            ("missing_password", "eve.holt@reqres.in", None, 400, "Missing password"),
            ("valid_register", "eve.holt@reqres.in", "pistol", 200, None),
            ("missing_password_register", "sydney@fife", None, 400, "Missing password"),
        ])

        conn.commit()
        print(f"Database setup complete: {DB_PATH}")
    except sqlite3.Error as e:
        raise RuntimeError(f"Database setup failed: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    setup()
