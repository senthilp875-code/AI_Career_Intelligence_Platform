import json

from database import get_connection

from .resume_data import normalize_resume

MAX_JSON_CHARS = 400000


def ensure_user_resumes_table():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_resumes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) NOT NULL,
                title VARCHAR(255) NOT NULL DEFAULT 'Untitled Resume',
                template_key VARCHAR(64) NOT NULL DEFAULT 'modern_professional',
                resume_json LONGTEXT NOT NULL,
                ats_score INT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user_resumes_username (username)
            )
            """
        )
        try:
            cursor.execute(
                """
                ALTER TABLE user_resumes
                ADD COLUMN ats_score INT NULL
                """
            )
        except Exception:
            pass
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def list_user_resumes(username):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        try:
            cursor.execute(
                """
                SELECT id, title, template_key, ats_score, created_at, updated_at
                FROM user_resumes
                WHERE username = %s
                ORDER BY updated_at DESC
                """,
                (username,),
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "template": row[2],
                    "ats_score": row[3],
                    "created_at": row[4].strftime("%Y-%m-%d %H:%M") if row[4] else "",
                    "updated_at": row[5].strftime("%Y-%m-%d %H:%M") if row[5] else "",
                }
                for row in rows
            ]
        except Exception:
            cursor.execute(
                """
                SELECT id, title, template_key, updated_at
                FROM user_resumes
                WHERE username = %s
                ORDER BY updated_at DESC
                """,
                (username,),
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "template": row[2],
                    "ats_score": None,
                    "created_at": "",
                    "updated_at": row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "",
                }
                for row in rows
            ]
    finally:
        cursor.close()
        connection.close()


def load_user_resume(username, resume_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT id, resume_json, ats_score
            FROM user_resumes
            WHERE id = %s AND username = %s
            LIMIT 1
            """,
            (resume_id, username),
        )
        row = cursor.fetchone()
        if not row:
            return None
        payload = json.loads(row[1])
        payload["id"] = row[0]
        if payload.get("ats_score") in (None, "") and row[2] is not None:
            payload["ats_score"] = row[2]
        return normalize_resume(payload)
    finally:
        cursor.close()
        connection.close()


def save_user_resume(username, resume):
    data = normalize_resume(resume)
    encoded = json.dumps(data, ensure_ascii=False)
    if len(encoded) > MAX_JSON_CHARS:
        raise ValueError("Resume is too large to save.")

    connection = get_connection()
    cursor = connection.cursor()
    try:
        if data.get("id"):
            cursor.execute(
                """
                UPDATE user_resumes
                SET title = %s,
                    template_key = %s,
                    resume_json = %s,
                    ats_score = %s
                WHERE id = %s AND username = %s
                """,
                (
                    data["title"][:255],
                    data["template"],
                    encoded,
                    data.get("ats_score"),
                    data["id"],
                    username,
                ),
            )
            if cursor.rowcount == 0:
                data["id"] = None

        if not data.get("id"):
            cursor.execute(
                """
                INSERT INTO user_resumes
                    (username, title, template_key, resume_json, ats_score)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    username,
                    data["title"][:255],
                    data["template"],
                    encoded,
                    data.get("ats_score"),
                ),
            )
            data["id"] = cursor.lastrowid

        connection.commit()
        return data
    finally:
        cursor.close()
        connection.close()


def delete_user_resume(username, resume_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM user_resumes
            WHERE id = %s AND username = %s
            """,
            (resume_id, username),
        )
        connection.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        connection.close()


def duplicate_user_resume(username, resume_id):
    current = load_user_resume(username, resume_id)
    if not current:
        return None
    current["id"] = None
    title = current.get("title") or "Untitled Resume"
    if not title.endswith("(Copy)"):
        current["title"] = f"{title} (Copy)"
    return save_user_resume(username, current)
