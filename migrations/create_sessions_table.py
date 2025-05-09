import mysql.connector
from config.config import Config

def create_sessions_table():
    try:
        # Connexion à la base de données
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = conn.cursor()

        # Script SQL pour créer la table sessions
        sql = """
        CREATE TABLE IF NOT EXISTS sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            token VARCHAR(255) NOT NULL UNIQUE,
            user_id INT NOT NULL,
            create_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expire_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """

        # Exécution du script
        cursor.execute(sql)
        conn.commit()

        print("Table sessions créée avec succès!")

    except Exception as e:
        print(f"Erreur lors de la création de la table: {str(e)}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_sessions_table() 