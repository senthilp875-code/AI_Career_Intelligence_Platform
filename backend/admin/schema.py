import json

import bcrypt
import pymysql

from database import get_connection

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin@123"


def _column_exists(cursor, table, column):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = %s
        AND COLUMN_NAME = %s
        """,
        (table, column),
    )
    return cursor.fetchone()[0] > 0


def _table_exists(cursor, table):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = %s
        """,
        (table,),
    )
    return cursor.fetchone()[0] > 0


def ensure_admin_schema():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        if not _table_exists(cursor, "admins"):
            cursor.execute(
                """
                CREATE TABLE admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(120) NOT NULL,
                    username VARCHAR(80) NOT NULL UNIQUE,
                    email VARCHAR(120) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL
                )
                """
            )

        if not _table_exists(cursor, "app_settings"):
            cursor.execute(
                """
                CREATE TABLE app_settings (
                    setting_key VARCHAR(100) PRIMARY KEY,
                    setting_value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP
                )
                """
            )

        if not _table_exists(cursor, "ai_chat_sessions"):
            cursor.execute(
                """
                CREATE TABLE ai_chat_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) NOT NULL,
                    session_key VARCHAR(64) NOT NULL,
                    message_count INT DEFAULT 0,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_chat_user (username),
                    INDEX idx_chat_session (session_key)
                )
                """
            )

        if not _table_exists(cursor, "job_recommendation_log"):
            cursor.execute(
                """
                CREATE TABLE job_recommendation_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) NOT NULL,
                    resume_name VARCHAR(255),
                    job_count INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_job_rec_user (username)
                )
                """
            )

        if not _table_exists(cursor, "user_activity"):
            cursor.execute(
                """
                CREATE TABLE user_activity (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) NOT NULL,
                    activity_type VARCHAR(64) NOT NULL,
                    description VARCHAR(512),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_activity_user (username),
                    INDEX idx_activity_created (created_at)
                )
                """
            )

        if _table_exists(cursor, "users"):
            if not _column_exists(cursor, "users", "is_active"):
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1"
                )

            if not _column_exists(cursor, "users", "created_at"):
                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    """
                )

        if _table_exists(cursor, "resume_analysis"):
            cursor.execute(
                """
                SELECT COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'resume_analysis'
                  AND CONSTRAINT_NAME = 'PRIMARY'
                LIMIT 1
                """
            )

            if not cursor.fetchone() and not _column_exists(
                cursor, "resume_analysis", "id"
            ):
                cursor.execute(
                    """
                    ALTER TABLE resume_analysis
                    ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST
                    """
                )

            # IMPORTANT:
            # All resume_analysis column checks are aligned at the same level.

            if not _column_exists(cursor, "resume_analysis", "skills_json"):
                cursor.execute(
                    "ALTER TABLE resume_analysis ADD COLUMN skills_json TEXT NULL"
                )

            if not _column_exists(cursor, "resume_analysis", "skill_gap_json"):
                cursor.execute(
                    "ALTER TABLE resume_analysis ADD COLUMN skill_gap_json TEXT NULL"
                )

            if not _column_exists(cursor, "resume_analysis", "file_hash"):
                cursor.execute(
                    "ALTER TABLE resume_analysis ADD COLUMN file_hash VARCHAR(64) NULL"
                )

            if not _column_exists(cursor, "resume_analysis", "analysis_json"):
                cursor.execute(
                    "ALTER TABLE resume_analysis ADD COLUMN analysis_json LONGTEXT NULL"
                )

            if not _column_exists(cursor, "resume_analysis", "extracted_text"):
                cursor.execute(
                    "ALTER TABLE resume_analysis ADD COLUMN extracted_text LONGTEXT NULL"
                )

        cursor.execute("SELECT COUNT(*) FROM admins")

        if cursor.fetchone()[0] == 0:
            hashed = bcrypt.hashpw(
                DEFAULT_ADMIN_PASSWORD.encode(),
                bcrypt.gensalt(),
            )

            cursor.execute(
                """
                INSERT INTO admins (full_name, username, email, password)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    "System Administrator",
                    DEFAULT_ADMIN_USERNAME,
                    "admin@talentiq.local",
                    hashed,
                ),
            )

        defaults = {
            "app_name": "TalentIQ AI",
            "ai_provider": "local",
            "ai_model": "career-assistant-v2",
            "ai_max_message_length": "1000",
            "supported_file_types": json.dumps(["pdf", "docx", "doc"]),
        }

        for key, value in defaults.items():
            cursor.execute(
                "SELECT setting_key FROM app_settings WHERE setting_key = %s",
                (key,),
            )

            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO app_settings (setting_key, setting_value)
                    VALUES (%s, %s)
                    """,
                    (key, value),
                )

        connection.commit()

    finally:
        cursor.close()
        connection.close()