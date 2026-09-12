import json

from database import get_connection


def get_setting(key, default=None):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT setting_value FROM app_settings WHERE setting_key = %s",
            (key,),
        )
        row = cursor.fetchone()
        if not row:
            return default
        return row[0]
    finally:
        cursor.close()
        connection.close()


def get_supported_extensions():
    raw = get_setting("supported_file_types", '["pdf","docx","doc"]')
    try:
        items = json.loads(raw)
        if isinstance(items, list):
            return [str(x).lower().lstrip(".") for x in items if x]
    except (TypeError, json.JSONDecodeError):
        pass
    return ["pdf", "docx", "doc"]


def get_all_settings():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT setting_key, setting_value, updated_at FROM app_settings ORDER BY setting_key"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def save_settings(form_data):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        mapping = {
            "app_name": form_data.get("app_name", "").strip(),
            "ai_provider": form_data.get("ai_provider", "").strip(),
            "ai_model": form_data.get("ai_model", "").strip(),
            "ai_max_message_length": form_data.get("ai_max_message_length", "1000").strip(),
        }
        exts = form_data.get("supported_file_types", "")
        ext_list = [x.strip().lower().lstrip(".") for x in exts.split(",") if x.strip()]
        mapping["supported_file_types"] = json.dumps(ext_list or ["pdf", "docx", "doc"])

        for key, value in mapping.items():
            cursor.execute(
                """
                INSERT INTO app_settings (setting_key, setting_value)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
                """,
                (key, value),
            )
        connection.commit()
    finally:
        cursor.close()
        connection.close()
