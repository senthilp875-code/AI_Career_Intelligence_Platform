import pymysql

from config import DB_CONFIG


def get_connection():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        port=DB_CONFIG["port"],
        cursorclass=pymysql.cursors.DictCursor
    )


def ensure_core_schema():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(120) NOT NULL,
                    username VARCHAR(80) NOT NULL UNIQUE,
                    email VARCHAR(120) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    phone VARCHAR(30) DEFAULT NULL,
                    location VARCHAR(255) DEFAULT NULL,
                    headline VARCHAR(255) DEFAULT NULL,
                    linkedin VARCHAR(255) DEFAULT NULL,
                    github VARCHAR(255) DEFAULT NULL,
                    portfolio VARCHAR(255) DEFAULT NULL,
                    skills TEXT,
                    is_active TINYINT(1) NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_analysis (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) NOT NULL,
                    resume_name VARCHAR(255),
                    resume_score INT DEFAULT NULL,
                    ats_score INT DEFAULT NULL,
                    predicted_job VARCHAR(255),
                    job_match TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    skills_json LONGTEXT,
                    skill_gap_json LONGTEXT,
                    file_hash VARCHAR(128),
                    analysis_json LONGTEXT,
                    extracted_text LONGTEXT,
                    INDEX idx_resume_username (username),
                    INDEX idx_resume_uploaded_at (uploaded_at)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    token_hash VARCHAR(128) NOT NULL,
                    expires_at DATETIME NOT NULL,
                    used_at DATETIME DEFAULT NULL,
                    INDEX idx_reset_user_id (user_id),
                    INDEX idx_reset_token_hash (token_hash)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) NOT NULL,
                    rating INT NOT NULL,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_feedback_username (username)
                )
            """)

        connection.commit()
        print("Core database tables checked/created successfully.")

    finally:
        connection.close()