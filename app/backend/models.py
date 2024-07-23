from .utils import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(255) UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cursor.execute(
        """CREATE TABLE user_achievements (
        user_id INT PRIMARY KEY,
        login_streak INT DEFAULT 0,
        doubled_bet_progress INT DEFAULT 0,
        doubled_bet_count INT DEFAULT 0,
        top_hand_progress INT DEFAULT 0,
        top_hand_count INT DEFAULT 0,
        consecutive_wins INT DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )

    print("Tables created successfully")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()