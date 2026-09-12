import json
import os
from collections import Counter

from database import get_connection


def log_user_activity(username, activity_type, description=""):
    if not username:
        return
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO user_activity (username, activity_type, description)
            VALUES (%s, %s, %s)
            """,
            (username, activity_type, description[:512]),
        )
        connection.commit()
    except Exception:
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def log_job_recommendations(username, resume_name, job_count):
    if not username:
        return
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO job_recommendation_log (username, resume_name, job_count)
            VALUES (%s, %s, %s)
            """,
            (username, resume_name, int(job_count or 0)),
        )
        connection.commit()
    except Exception:
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def log_ai_chat_message(username, session_key):
    if not username or not session_key:
        return
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT id, message_count FROM ai_chat_sessions
            WHERE username = %s AND session_key = %s
            ORDER BY id DESC LIMIT 1
            """,
            (username, session_key),
        )
        row = cursor.fetchone()
        if row:
            cursor.execute(
                """
                UPDATE ai_chat_sessions
                SET message_count = message_count + 1,
                    last_activity_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (row[0],),
            )
        else:
            cursor.execute(
                """
                INSERT INTO ai_chat_sessions (username, session_key, message_count)
                VALUES (%s, %s, 1)
                """,
                (username, session_key),
            )
        connection.commit()
    except Exception:
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def get_dashboard_stats():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT resume_name) FROM resume_analysis")
        total_resumes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM resume_analysis")
        total_analyses = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ai_chat_sessions")
        total_chat_sessions = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(job_count), 0) FROM job_recommendation_log")
        total_job_recs = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT username, activity_type, description, created_at
            FROM user_activity
            ORDER BY created_at DESC
            LIMIT 10
            """
        )
        recent_activity = cursor.fetchall()

        if not recent_activity:
            cursor.execute(
                """
                SELECT username, 'resume_upload', resume_name, uploaded_at
                FROM resume_analysis
                ORDER BY uploaded_at DESC
                LIMIT 10
                """
            )
            recent_activity = cursor.fetchall()

        return {
            "total_users": total_users,
            "total_resumes": total_resumes,
            "total_analyses": total_analyses,
            "total_chat_sessions": total_chat_sessions,
            "total_job_recs": total_job_recs,
            "recent_activity": recent_activity,
        }
    finally:
        cursor.close()
        connection.close()


def search_users(query="", page=1, per_page=15):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        where = ""
        params = []
        if query:
            where = """
            WHERE username LIKE %s OR email LIKE %s OR full_name LIKE %s
            """
            like = f"%{query}%"
            params = [like, like, like]

        cursor.execute(f"SELECT COUNT(*) FROM users {where}", params)
        total = cursor.fetchone()[0]

        offset = (page - 1) * per_page
        cursor.execute(
            f"""
            SELECT id, full_name, username, email, is_active, created_at
            FROM users
            {where}
            ORDER BY id DESC
            LIMIT %s OFFSET %s
            """,
            params + [per_page, offset],
        )
        rows = cursor.fetchall()
        return rows, total
    finally:
        cursor.close()
        connection.close()


def get_user_by_id(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT id, full_name, username, email, is_active, created_at
            FROM users WHERE id = %s
            """,
            (user_id,),
        )
        user = cursor.fetchone()

        cursor.execute(
            """
            SELECT resume_name, resume_score, ats_score, predicted_job, uploaded_at
            FROM resume_analysis
            WHERE username = %s
            ORDER BY uploaded_at DESC
            LIMIT 20
            """,
            (user[2],) if user else ("",),
        )
        analyses = cursor.fetchall()

        cursor.execute(
            """
            SELECT activity_type, description, created_at
            FROM user_activity
            WHERE username = %s
            ORDER BY created_at DESC
            LIMIT 15
            """,
            (user[2],) if user else ("",),
        )
        activity = cursor.fetchall()

        return user, analyses, activity
    finally:
        cursor.close()
        connection.close()


def set_user_active(user_id, active):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE users SET is_active = %s WHERE id = %s",
            (1 if active else 0, user_id),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def delete_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        username = row[0]
        cursor.execute("DELETE FROM resume_analysis WHERE username = %s", (username,))
        cursor.execute("DELETE FROM feedback WHERE username = %s", (username,))
        cursor.execute("DELETE FROM user_activity WHERE username = %s", (username,))
        cursor.execute("DELETE FROM ai_chat_sessions WHERE username = %s", (username,))
        cursor.execute(
            "DELETE FROM job_recommendation_log WHERE username = %s", (username,)
        )
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        return username
    finally:
        cursor.close()
        connection.close()


def search_resumes(query="", page=1, per_page=15):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        where = ""
        params = []
        if query:
            where = "WHERE resume_name LIKE %s OR username LIKE %s"
            like = f"%{query}%"
            params = [like, like]

        cursor.execute(
            f"SELECT COUNT(*) FROM resume_analysis {where}",
            params,
        )
        total = cursor.fetchone()[0]

        offset = (page - 1) * per_page
        cursor.execute(
            f"""
            SELECT id, username, resume_name, resume_score, ats_score,
                   predicted_job, uploaded_at
            FROM resume_analysis
            {where}
            ORDER BY uploaded_at DESC
            LIMIT %s OFFSET %s
            """,
            params + [per_page, offset],
        )
        rows = cursor.fetchall()
        return rows, total
    finally:
        cursor.close()
        connection.close()


def delete_resume_record(resume_id, upload_folder):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT resume_name FROM resume_analysis WHERE id = %s",
            (resume_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        name = row[0]
        cursor.execute("DELETE FROM resume_analysis WHERE id = %s", (resume_id,))
        connection.commit()
        path = os.path.join(upload_folder, name)
        if os.path.isfile(path):
            os.remove(path)
        return name
    finally:
        cursor.close()
        connection.close()


def get_ai_analytics():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT AVG(ats_score) FROM resume_analysis")
        avg_ats = cursor.fetchone()[0]
        avg_ats = round(float(avg_ats), 1) if avg_ats is not None else 0.0

        cursor.execute(
            """
            SELECT predicted_job, COUNT(*) AS cnt
            FROM resume_analysis
            WHERE predicted_job IS NOT NULL AND predicted_job != ''
            GROUP BY predicted_job
            ORDER BY cnt DESC
            LIMIT 10
            """
        )
        top_jobs = cursor.fetchall()

        cursor.execute(
            """
            SELECT skills_json FROM resume_analysis
            WHERE skills_json IS NOT NULL AND skills_json != ''
            """
        )
        skill_counter = Counter()
        gap_missing = 0
        gap_total = 0

        for (skills_json,) in cursor.fetchall():
            try:
                skills = json.loads(skills_json)
                if isinstance(skills, list):
                    for skill in skills:
                        skill_counter[str(skill).strip()] += 1
            except json.JSONDecodeError:
                continue

        cursor.execute(
            """
            SELECT skill_gap_json FROM resume_analysis
            WHERE skill_gap_json IS NOT NULL AND skill_gap_json != ''
            """
        )
        for (gap_json,) in cursor.fetchall():
            try:
                gap = json.loads(gap_json)
                if isinstance(gap, dict):
                    missing = gap.get("missing_skills") or gap.get("missing") or []
                    if isinstance(missing, list):
                        gap_total += len(missing)
                        gap_missing += len(missing)
                elif isinstance(gap, list):
                    gap_total += len(gap)
                    gap_missing += len(gap)
            except json.JSONDecodeError:
                continue

        top_skills = skill_counter.most_common(12)
        cursor.execute(
            "SELECT COUNT(*) FROM resume_analysis WHERE skill_gap_json IS NOT NULL"
        )
        gap_rows = cursor.fetchone()[0]

        return {
            "avg_ats": avg_ats,
            "top_jobs": top_jobs,
            "top_skills": top_skills,
            "skill_gap_stats": {
                "analyses_with_gap_data": gap_rows,
                "total_missing_skill_entries": gap_missing,
                "avg_missing_per_record": round(gap_missing / gap_rows, 1)
                if gap_rows
                else 0,
            },
        }
    finally:
        cursor.close()
        connection.close()


def pagination_meta(total, page, per_page):
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
    }
