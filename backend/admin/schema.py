import json
import bcrypt

from database import get_connection


def _get_first_value(row):
    """
    Supports both PyMySQL tuple results and DictCursor results.
    """
    if isinstance(row, dict):
        return next(iter(row.values()))

    return row[0]


def _column_exists(cursor, table_name, column_name):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (table_name, column_name),
    )

    row = cursor.fetchone()
    return _get_first_value(row) > 0


def _table_exists(cursor, table_name):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
        """,
        (table_name,),
    )

    row = cursor.fetchone()
    return _get_first_value(row) > 0


def _add_column_if_missing(cursor, table_name, column_name, column_definition):
    if not _column_exists(cursor, table_name, column_name):
        cursor.execute(
            f"ALTER TABLE `{table_name}` "
            f"ADD COLUMN `{column_name}` {column_definition}"
        )


def ensure_admin_schema():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # ---------------------------------------------------------
        # ADMINS TABLE
        # ---------------------------------------------------------
        if not _table_exists(cursor, "admins"):
            cursor.execute(
                """
                CREATE TABLE admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    email VARCHAR(255) UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    is_active TINYINT(1) DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

        # ---------------------------------------------------------
        # APP SETTINGS TABLE
        # ---------------------------------------------------------
        if not _table_exists(cursor, "app_settings"):
            cursor.execute(
                """
                CREATE TABLE app_settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(150) NOT NULL UNIQUE,
                    setting_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP
                )
                """
            )

        # ---------------------------------------------------------
        # AI CHAT SESSIONS TABLE
        # ---------------------------------------------------------
        if not _table_exists(cursor, "ai_chat_sessions"):
            cursor.execute(
                """
                CREATE TABLE ai_chat_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100),
                    session_title VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP
                )
                """
            )

        # ---------------------------------------------------------
        # JOB RECOMMENDATION LOG TABLE
        # ---------------------------------------------------------
        if not _table_exists(cursor, "job_recommendation_log"):
            cursor.execute(
                """
                CREATE TABLE job_recommendation_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100),
                    job_title VARCHAR(255),
                    match_score DECIMAL(5,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

        # ---------------------------------------------------------
        # USER ACTIVITY TABLE
        # ---------------------------------------------------------
        if not _table_exists(cursor, "user_activity"):
            cursor.execute(
                """
                CREATE TABLE user_activity (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100),
                    activity_type VARCHAR(150),
                    activity_details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

        # ---------------------------------------------------------
        # USERS TABLE - ADD MISSING COLUMNS
        # ---------------------------------------------------------
        if _table_exists(cursor, "users"):
            _add_column_if_missing(
                cursor,
                "users",
                "is_active",
                "TINYINT(1) DEFAULT 1",
            )

            _add_column_if_missing(
                cursor,
                "users",
                "created_at",
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            )

            _add_column_if_missing(
                cursor,
                "users",
                "skills_json",
                "TEXT",
            )

        # ---------------------------------------------------------
        # RESUME ANALYSIS TABLE - ADD MISSING COLUMNS
        # ---------------------------------------------------------
        if _table_exists(cursor, "resume_analysis"):
            _add_column_if_missing(
                cursor,
                "resume_analysis",
                "skills_json",
                "TEXT",
            )

            _add_column_if_missing(
                cursor,
                "resume_analysis",
                "skill_gap_json",
                "TEXT",
            )

            _add_column_if_missing(
                cursor,
                "resume_analysis",
                "file_hash",
                "VARCHAR(255)",
            )

            _add_column_if_missing(
                cursor,
                "resume_analysis",
                "analysis_json",
                "LONGTEXT",
            )

            _add_column_if_missing(
                cursor,
                "resume_analysis",
                "extracted_text",
                "LONGTEXT",
            )

        # ---------------------------------------------------------
        # DEFAULT ADMIN ACCOUNT
        # ---------------------------------------------------------
        cursor.execute(
            "SELECT COUNT(*) FROM admins"
        )

        row = cursor.fetchone()
        admin_count = _get_first_value(row)

        if admin_count == 0:
            default_password = "Admin@123"
            password_hash = bcrypt.hashpw(
                default_password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            cursor.execute(
                """
                INSERT INTO admins
                (
                    username,
                    email,
                    password_hash,
                    full_name,
                    is_active
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    "admin",
                    "admin@talentiq.com",
                    password_hash,
                    "TalentIQ Administrator",
                    1,
                ),
            )

        # ---------------------------------------------------------
        # DEFAULT APP SETTINGS
        # ---------------------------------------------------------
        default_settings = {
            "app_name": "TalentIQ AI",
            "maintenance_mode": "0",
            "allow_registration": "1",
            "default_resume_score": "0",
        }

        for setting_key, setting_value in default_settings.items():
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM app_settings
                WHERE setting_key = %s
                """,
                (setting_key,),
            )

            row = cursor.fetchone()
            setting_exists = _get_first_value(row)

            if setting_exists == 0:
                cursor.execute(
                    """
                    INSERT INTO app_settings
                    (
                        setting_key,
                        setting_value
                    )
                    VALUES (%s, %s)
                    """,
                    (
                        setting_key,
                        setting_value,
                    ),
                )

        connection.commit()

        print("Admin database tables checked/created successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()