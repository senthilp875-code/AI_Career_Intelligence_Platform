import bcrypt
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from io import BytesIO

from admin.auth import admin_login_required
from admin.reports import (
    generate_analysis_report,
    generate_resume_report,
    generate_user_report,
)
from admin.services import (
    delete_resume_record,
    delete_user,
    get_ai_analytics,
    get_dashboard_stats,
    get_user_by_id,
    pagination_meta,
    search_resumes,
    search_users,
    set_user_active,
)
from admin.settings_store import get_all_settings, get_supported_extensions, save_settings
from database import get_connection


def register_routes(bp: Blueprint, upload_folder):

    @bp.route("/login", methods=["GET", "POST"])
    def login():
        if session.get("admin_id"):
            return redirect(url_for("admin.dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            connection = get_connection()
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    SELECT id, username, password, full_name
                    FROM admins WHERE username = %s
                    """,
                    (username,),
                )
                admin = cursor.fetchone()
            finally:
                cursor.close()
                connection.close()

            if not admin:
                flash("Invalid administrator credentials.", "error")
                return redirect(url_for("admin.login"))

            stored = admin[2]
            if isinstance(stored, str):
                stored = stored.encode()

            if not bcrypt.checkpw(password.encode(), stored):
                flash("Invalid administrator credentials.", "error")
                return redirect(url_for("admin.login"))

            session["admin_id"] = admin[0]
            session["admin_username"] = admin[1]
            session["admin_name"] = admin[3]

            connection = get_connection()
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE admins SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                    (admin[0],),
                )
                connection.commit()
            finally:
                cursor.close()
                connection.close()

            flash(f"Welcome, {admin[3]}!", "success")
            return redirect(url_for("admin.dashboard"))

        return render_template("admin/login.html")

    @bp.route("/logout")
    @admin_login_required
    def logout():
        session.pop("admin_id", None)
        session.pop("admin_username", None)
        session.pop("admin_name", None)
        flash("Admin session ended.", "success")
        return redirect(url_for("admin.login"))

    @bp.route("/")
    @admin_login_required
    def dashboard():
        stats = get_dashboard_stats()
        return render_template("admin/dashboard.html", stats=stats)

    @bp.route("/users")
    @admin_login_required
    def users():
        q = request.args.get("q", "").strip()
        page = request.args.get("page", 1, type=int)
        per_page = 15
        rows, total = search_users(q, page, per_page)
        pager = pagination_meta(total, page, per_page)
        return render_template(
            "admin/users.html",
            users=rows,
            q=q,
            pager=pager,
        )

    @bp.route("/users/<int:user_id>")
    @admin_login_required
    def user_detail(user_id):
        user, analyses, activity = get_user_by_id(user_id)
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("admin.users"))
        return render_template(
            "admin/user_detail.html",
            user=user,
            analyses=analyses,
            activity=activity,
        )

    @bp.route("/users/<int:user_id>/toggle", methods=["POST"])
    @admin_login_required
    def user_toggle(user_id):
        active = request.form.get("active") == "1"
        set_user_active(user_id, active)
        flash(
            "User account enabled." if active else "User account disabled.",
            "success",
        )
        return redirect(request.referrer or url_for("admin.users"))

    @bp.route("/users/<int:user_id>/delete", methods=["POST"])
    @admin_login_required
    def user_delete(user_id):
        username = delete_user(user_id)
        if not username:
            flash("User not found.", "error")
        else:
            flash(f"Deleted user '{username}' and related records.", "success")
        return redirect(url_for("admin.users"))

    @bp.route("/resumes")
    @admin_login_required
    def resumes():
        q = request.args.get("q", "").strip()
        page = request.args.get("page", 1, type=int)
        per_page = 15
        rows, total = search_resumes(q, page, per_page)
        pager = pagination_meta(total, page, per_page)
        return render_template(
            "admin/resumes.html",
            resumes=rows,
            q=q,
            pager=pager,
        )

    @bp.route("/resumes/<int:resume_id>/download")
    @admin_login_required
    def resume_download(resume_id):
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT resume_name FROM resume_analysis WHERE id = %s",
                (resume_id,),
            )
            row = cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

        if not row:
            flash("Resume record not found.", "error")
            return redirect(url_for("admin.resumes"))

        import os

        path = os.path.join(upload_folder, row[0])
        if not os.path.isfile(path):
            flash("File missing on server.", "error")
            return redirect(url_for("admin.resumes"))
        return send_file(path, as_attachment=True, download_name=row[0])

    @bp.route("/resumes/<int:resume_id>/delete", methods=["POST"])
    @admin_login_required
    def resume_delete(resume_id):
        name = delete_resume_record(resume_id, upload_folder)
        if not name:
            flash("Resume not found.", "error")
        else:
            flash(f"Deleted resume '{name}'.", "success")
        return redirect(url_for("admin.resumes"))


    # ===============================
    # FEEDBACK MANAGEMENT
    # ===============================

    @bp.route("/feedback")
    @admin_login_required
    def feedback():

        connection = get_connection()
        cursor = connection.cursor()

        try:

            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    rating,
                    message,
                    created_at
                FROM feedback
                ORDER BY created_at DESC
                """
            )

            feedback_rows = cursor.fetchall()

        finally:

            cursor.close()
            connection.close()

        return render_template(
            "admin/feedback.html",
            feedback=feedback_rows
        )
    
    @bp.route("/analytics")
    @admin_login_required
    def analytics():
        data = get_ai_analytics()
        job_labels = [row[0] for row in data["top_jobs"]]
        job_values = [row[1] for row in data["top_jobs"]]
        skill_labels = [row[0] for row in data["top_skills"]]
        skill_values = [row[1] for row in data["top_skills"]]
        return render_template(
            "admin/analytics.html",
            data=data,
            job_labels=job_labels,
            job_values=job_values,
            skill_labels=skill_labels,
            skill_values=skill_values,
        )

    @bp.route("/reports")
    @admin_login_required
    def reports():
        return render_template("admin/reports.html")

    @bp.route("/reports/<report_type>")
    @admin_login_required
    def download_report(report_type):
        if report_type == "users":
            content, filename = generate_user_report()
        elif report_type == "resumes":
            content, filename = generate_resume_report()
        elif report_type == "analysis":
            content, filename = generate_analysis_report()
        else:
            flash("Unknown report type.", "error")
            return redirect(url_for("admin.reports"))

        return send_file(
            BytesIO(content.encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=filename,
        )

    @bp.route("/settings", methods=["GET", "POST"])
    @admin_login_required
    def settings():
        if request.method == "POST":
            save_settings(request.form)
            flash("Application settings updated.", "success")
            return redirect(url_for("admin.settings"))

        rows = get_all_settings()
        settings_map = {row[0]: row[1] for row in rows}
        exts = get_supported_extensions()
        return render_template(
            "admin/settings.html",
            settings=settings_map,
            supported_exts=", ".join(exts),
        )
