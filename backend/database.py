import pymysql

from config import DB_CONFIG


def get_connection():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        port=DB_CONFIG["port"],
        cursorclass=pymysql.cursors.Cursor,
        autocommit=False,
    )


def ensure_core_schema():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(255),
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                phone VARCHAR(50),
                location VARCHAR(255),
                headline VARCHAR(255),
                linkedin VARCHAR(500),
                github VARCHAR(500),
                portfolio VARCHAR(500),
                skills TEXT,
                is_active TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS resume_analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100),
                resume_name VARCHAR(255),
                resume_score DECIMAL(5,2),
                ats_score DECIMAL(5,2),
                predicted_job VARCHAR(255),
                job_match DECIMAL(5,2),
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                skills_json TEXT,
                skill_gap_json TEXT,
                file_hash VARCHAR(255),
                analysis_json LONGTEXT,
                extracted_text LONGTEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                token VARCHAR(255) NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100),
                rating INT,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()
        print("Core database tables checked/created successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()