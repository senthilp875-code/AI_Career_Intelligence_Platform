import csv
import io
from datetime import datetime

from database import get_connection


def _csv_response(filename, rows, header):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    buffer.seek(0)
    return buffer.getvalue(), f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"


def generate_user_report():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT id, full_name, username, email, is_active, created_at
            FROM users
            ORDER BY id ASC
            """
        )
        rows = cursor.fetchall()
        return _csv_response(
            "user_report",
            rows,
            ["ID", "Full Name", "Username", "Email", "Active", "Created At"],
        )
    finally:
        cursor.close()
        connection.close()


def generate_resume_report():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT id, username, resume_name, resume_score, ats_score,
                   predicted_job, job_match, uploaded_at
            FROM resume_analysis
            ORDER BY uploaded_at DESC
            """
        )
        rows = cursor.fetchall()
        return _csv_response(
            "resume_report",
            rows,
            [
                "ID",
                "Username",
                "Resume",
                "Resume Score",
                "ATS Score",
                "Predicted Job",
                "Job Match",
                "Uploaded At",
            ],
        )
    finally:
        cursor.close()
        connection.close()


def generate_analysis_report():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT username, COUNT(*) AS analyses,
                   AVG(ats_score) AS avg_ats,
                   AVG(resume_score) AS avg_resume,
                   MAX(uploaded_at) AS last_upload
            FROM resume_analysis
            GROUP BY username
            ORDER BY analyses DESC
            """
        )
        rows = cursor.fetchall()
        formatted = []
        for row in rows:
            formatted.append(
                (
                    row[0],
                    row[1],
                    round(float(row[2]), 1) if row[2] is not None else 0,
                    round(float(row[3]), 1) if row[3] is not None else 0,
                    row[4],
                )
            )
        return _csv_response(
            "analysis_report",
            formatted,
            [
                "Username",
                "Total Analyses",
                "Average ATS",
                "Average Resume Score",
                "Last Upload",
            ],
        )
    finally:
        cursor.close()
        connection.close()
