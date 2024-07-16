from .utils import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS games (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            number_of_stars INTEGER,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            progress TEXT,  # Could store JSON data indicating progress in a campaign or tutorial
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """
    )

    print("Tables created successfully")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
from .utils import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS games (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            number_of_stars INTEGER,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            progress TEXT,  # Could store JSON data indicating progress in a campaign or tutorial
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """
    )

    print("Tables created successfully")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()