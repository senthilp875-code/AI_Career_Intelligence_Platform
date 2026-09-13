from resume_builder.resume_generator import generate_resume_data
from resume_builder.pdf_generator import generate_pdf
from resume_builder.docx_generator import generate_docx
from flask import send_file

from utils.pdf_resume import create_pdf
from utils.docx_resume import create_docx
from services.resume_builder import generate_resume
from flask import send_file
from services.resume_builder import generate_resume
from services.job_engine import recommend_jobs
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash,
    jsonify
)

import uuid
import pymysql
import bcrypt
import os
import hashlib
import json
import secrets
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")


def send_password_reset_email(to_email, reset_link):

    print("=" * 60)
    print("MAIL CONFIG TEST")
    print("MAIL_USERNAME:", MAIL_USERNAME)
    print("MAIL_FROM:", MAIL_FROM)
    print("MAIL_PASSWORD loaded:", bool(MAIL_PASSWORD))
    print(
        "MAIL_PASSWORD length:",
        len(MAIL_PASSWORD.replace(" ", "")) if MAIL_PASSWORD else 0
    )
    print("=" * 60)

    try:
        # Remove spaces from Google App Password
        mail_password = MAIL_PASSWORD.replace(" ", "") if MAIL_PASSWORD else ""

        if not MAIL_USERNAME:
            print("ERROR: MAIL_USERNAME is missing.")
            return False

        if not mail_password:
            print("ERROR: MAIL_PASSWORD is missing.")
            return False

        if not MAIL_FROM:
            print("ERROR: MAIL_FROM is missing.")
            return False

        msg = EmailMessage()

        msg["Subject"] = "TalentIQ AI - Reset Your Password"
        msg["From"] = MAIL_FROM
        msg["To"] = to_email

        msg.set_content(
            f"""
Hello,

We received a request to reset your TalentIQ AI password.

Click the link below to create a new password:

{reset_link}

This link will expire in 30 minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
TalentIQ AI Team
"""
        )

        print("Connecting to Gmail SMTP...")

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:

            server.ehlo()

            print("Starting TLS...")
            server.starttls()

            server.ehlo()

            print("Logging in to Gmail...")

            server.login(
                MAIL_USERNAME,
                mail_password
            )

            print("Gmail login successful.")

            server.send_message(msg)

        print("Password reset email sent successfully to:", to_email)

        return True

    except Exception as e:

        print("=" * 60)
        print("EMAIL SENDING ERROR")
        print("Error:", repr(e))
        print("=" * 60)

        return False

from flask import request
from database import get_connection, ensure_core_schema
from werkzeug.utils import secure_filename

from resume_parser import extract_text
from ai_engine.analysis_service import analyze_resume
from ai_engine.ai_chatbot import generate_ai_reply
from pdf_generator import generate_report

from flask import send_file
from admin import init_admin
import io

from resume_builder.store import (
    delete_user_resume,
    duplicate_user_resume,
    ensure_user_resumes_table,
    list_user_resumes,
    load_user_resume,
    save_user_resume,
)
from resume_builder.resume_data import (
    build_resume_from_sources,
    normalize_resume,
    resume_filename,
    validate_resume,
)
from resume_builder.quality import evaluate_resume
from resume_builder.template_engine import list_templates

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "careerai_super_secret_key"
)
# ---------------- FILE UPLOAD ----------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- ADMIN PANEL ----------------

try:
    ensure_core_schema()
except Exception as exc:
    print("core schema:", exc)

init_admin(app)

try:
    ensure_user_resumes_table()
except Exception as exc:
    print("user_resumes table:", exc)

# ---------------- DATABASE ----------------



# ---------------- HOME ----------------

@app.route("/")
def home():

    if "username" in session:

        return redirect("/dashboard")

    return render_template(

        "login.html"

    )

# ---------------- REGISTER PAGE ----------------

@app.route("/register")
def register_page():

    return render_template("register.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["POST"])
def register():

    full_name = request.form["full_name"].strip()
    username = request.form["username"].strip()
    email = request.form["email"].strip().lower()
    password = request.form["password"]

    connection = get_connection()
    cursor = connection.cursor()
    # Check duplicate user

    cursor.execute(

        """
        SELECT id
        FROM users
        WHERE username=%s
        OR email=%s
        """,

        (
            username,
            email
        )

    )

    existing_user = cursor.fetchone()

    if existing_user:

        flash(

            "Username or Email already exists.",

            "error"

        )

        return redirect("/register")

    # Hash Password

    hashed_password = bcrypt.hashpw(

        password.encode(),

        bcrypt.gensalt()

    )

    # Insert User

    cursor.execute(

        """
        INSERT INTO users
        (

            full_name,
            username,
            email,
            password

        )

        VALUES(%s,%s,%s,%s)

        """,

        (

            full_name,
            username,
            email,
            hashed_password

        )

    )

    connection.commit()
    connection.close()

    flash(

        "Account created successfully! Please login.",

        "success"

    )

    return redirect("/")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"].strip()
    password = request.form["password"]

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT username, password
        FROM users
        WHERE username=%s
        """,
        (username,)
    )

    user = cursor.fetchone()

    if user is None:

        connection.close()

        flash(
            "Username not found.",
            "error"
        )

        return redirect("/")

    stored_password = user[1]

    connection.close()

    if isinstance(stored_password, str):
        stored_password = stored_password.encode()

    if bcrypt.checkpw(
        password.encode(),
        stored_password
    ):

        session["username"] = username

        return redirect("/dashboard")

    flash(
        "Invalid Password.",
        "error"
    )

    return redirect("/")
# ---------------- FORGOT PASSWORD ----------------

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    # ---------------- SHOW PAGE ----------------

    if request.method == "GET":
        return render_template("forgot_password.html")

    # ---------------- GET EMAIL ----------------

    email = request.form.get("email", "").strip().lower()

    if not email:
        flash(
            "Please enter your email address.",
            "error"
        )
        return redirect("/forgot-password")

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ---------------- FIND USER ----------------

        cursor.execute(
            """
            SELECT id, username
            FROM users
            WHERE LOWER(email) = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        # ---------------- GENERIC RESPONSE ----------------
        # Do not reveal whether the email exists.

        if not user:

            flash(
                "If an account exists with this email, you will receive a password reset link.",
                "success"
            )

            return redirect("/forgot-password")

        user_id = user[0]

        # ---------------- GENERATE SECURE TOKEN ----------------

        reset_token = secrets.token_urlsafe(32)

        # ---------------- HASH TOKEN ----------------

        token_hash = hashlib.sha256(
            reset_token.encode()
        ).hexdigest()

        # ---------------- TOKEN EXPIRY ----------------
        # Token is valid for 30 minutes.

        expires_at = datetime.utcnow() + timedelta(
            minutes=30
        )

        # ---------------- INVALIDATE OLD TOKENS ----------------

        cursor.execute(
            """
            UPDATE password_reset_tokens
            SET used_at = UTC_TIMESTAMP()
            WHERE user_id = %s
            AND used_at IS NULL
            """,
            (user_id,)
        )

        # ---------------- SAVE NEW TOKEN ----------------

        cursor.execute(
            """
            INSERT INTO password_reset_tokens
            (
                user_id,
                token_hash,
                expires_at
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                user_id,
                token_hash,
                expires_at
            )
        )

        # ---------------- SAVE DATABASE CHANGES ----------------

        connection.commit()

        # ---------------- CREATE RESET LINK ----------------

        reset_link = (
            f"{request.host_url.rstrip('/')}"
            f"/reset-password/{reset_token}"
        )

        # ---------------- SEND EMAIL ----------------

        email_sent = send_password_reset_email(
            email,
            reset_link
        )

        # ---------------- EMAIL FAILED ----------------

        if not email_sent:

            print(
                "Password reset email could not be sent to:",
                email
            )

            flash(
                "Unable to send the password reset email. Please try again later.",
                "error"
            )

            return redirect("/forgot-password")

        # ---------------- EMAIL SENT ----------------

        flash(
            "If an account exists with this email, you will receive a password reset link.",
            "success"
        )

        return redirect("/forgot-password")

    # ---------------- ERROR ----------------

    except Exception as e:

        connection.rollback()

        print(
            "Forgot password error:",
            e
        )

        flash(
            "Something went wrong. Please try again.",
            "error"
        )

        return redirect("/forgot-password")

    # ---------------- CLOSE DATABASE ----------------

    finally:

        try:
            cursor.close()
            connection.close()

        except Exception:
            pass


# ---------------- RESET PASSWORD ----------------

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    token_hash = hashlib.sha256(
        token.encode()
    ).hexdigest()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, user_id, expires_at, used_at
            FROM password_reset_tokens
            WHERE token_hash = %s
            """,
            (token_hash,)
        )

        reset_data = cursor.fetchone()

        # Token does not exist
        if not reset_data:

            flash(
                "Invalid or expired password reset link.",
                "error"
            )

            return redirect("/forgot-password")

        token_id = reset_data[0]
        user_id = reset_data[1]
        expires_at = reset_data[2]
        used_at = reset_data[3]

        # Token already used
        if used_at is not None:

            flash(
                "This password reset link has already been used.",
                "error"
            )

            return redirect("/forgot-password")

        # Token expired
        if datetime.utcnow() > expires_at:

            flash(
                "This password reset link has expired.",
                "error"
            )

            return redirect("/forgot-password")

        # Show reset password page
        if request.method == "GET":

            return render_template(
                "reset_password.html",
                token=token
            )

        # Get passwords
        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # Check password
        if not password:

            flash(
                "Please enter a new password.",
                "error"
            )

            return render_template(
                "reset_password.html",
                token=token
            )

        # Check minimum length
        if len(password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return render_template(
                "reset_password.html",
                token=token
            )

        # Check confirmation
        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return render_template(
                "reset_password.html",
                token=token
            )

        # Hash new password
        hashed_password = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        )

        # Update user's password
        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE id = %s
            """,
            (
                hashed_password,
                user_id
            )
        )

        # Mark token as used
        cursor.execute(
            """
            UPDATE password_reset_tokens
            SET used_at = UTC_TIMESTAMP()
            WHERE id = %s
            """,
            (token_id,)
        )

        connection.commit()

        flash(
            "Password reset successfully! Please login with your new password.",
            "success"
        )

        return redirect("/")

    except Exception as e:

        connection.rollback()

        print(
            "Reset password error:",
            e
        )

        flash(
            "Something went wrong. Please try again.",
            "error"
        )

        return redirect("/forgot-password")

    finally:

        try:
            cursor.close()
            connection.close()
        except:
            pass        
# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "username" not in session:

        return redirect("/")

    # Default Career XP
    career_xp = 0
    career_level = 1
    career_title = "Career Beginner"
    xp_progress = 0

    # Get current resume analysis
    analysis = session.get("analysis")

    if analysis:

        # Get resume values safely
        resume_score = analysis.get("resume_score", 0) or 0
        ats_score = analysis.get("ats_score", 0) or 0
        skills = analysis.get("skills", []) or []

        # Calculate XP
        # Resume analysis completed
        career_xp += 100

        # Resume quality score contribution
        career_xp += int(resume_score * 2)

        # ATS score contribution
        career_xp += int(ats_score * 2)

        # Skills contribution
        career_xp += len(skills) * 25

    # Maximum XP for current progress display
    xp_per_level = 1000

    # Calculate level
    career_level = max(1, (career_xp // xp_per_level) + 1)

    # XP inside current level
    current_level_xp = career_xp % xp_per_level

    # Progress percentage
    xp_progress = min(
        100,
        (current_level_xp / xp_per_level) * 100
    )

    # Career titles based on level
    if career_level == 1:
        career_title = "Career Beginner"

    elif career_level == 2:
        career_title = "Career Learner"

    elif career_level == 3:
        career_title = "Skill Explorer"

    elif career_level == 4:
        career_title = "Career Builder"

    elif career_level == 5:
        career_title = "Career Achiever"

    elif career_level == 6:
        career_title = "Job Ready"

    else:
        career_title = "Career Explorer"

            # =====================================================
    # AI CAREER PERSONALITY
    # =====================================================

    personality_title = "Career Explorer 🌱"
    personality_description = (
        "You are exploring your strengths and building the "
        "skills needed for your future career."
    )
    personality_tags = [
        "Curious",
        "Learning",
        "Growing",
        "Exploring"
    ]

    if analysis:

        # Convert all skills to lowercase for comparison
        detected_skills = [
            str(skill).lower()
            for skill in analysis.get("skills", [])
        ]

        # Combine skills into one text
        skills_text = " ".join(detected_skills)

        # ---------------------------------------------
        # DATA / ANALYTICS PERSONALITY
        # ---------------------------------------------

        data_keywords = [
            "python",
            "sql",
            "power bi",
            "tableau",
            "excel",
            "pandas",
            "numpy",
            "data analysis",
            "data analytics",
            "machine learning"
        ]

        # ---------------------------------------------
        # DEVELOPMENT PERSONALITY
        # ---------------------------------------------

        developer_keywords = [
            "java",
            "javascript",
            "html",
            "css",
            "react",
            "flask",
            "django",
            "node",
            "api",
            "android"
        ]

        # ---------------------------------------------
        # DESIGN / CREATIVE PERSONALITY
        # ---------------------------------------------

        creative_keywords = [
            "figma",
            "ui",
            "ux",
            "design",
            "photoshop",
            "video editing",
            "blender"
        ]

        # ---------------------------------------------
        # LEADERSHIP PERSONALITY
        # ---------------------------------------------

        leadership_keywords = [
            "leadership",
            "management",
            "teamwork",
            "team leader",
            "communication",
            "project management"
        ]

        # Count matching skills
        data_score = sum(
            1 for keyword in data_keywords
            if keyword in skills_text
        )

        developer_score = sum(
            1 for keyword in developer_keywords
            if keyword in skills_text
        )

        creative_score = sum(
            1 for keyword in creative_keywords
            if keyword in skills_text
        )

        leadership_score = sum(
            1 for keyword in leadership_keywords
            if keyword in skills_text
        )

        # ---------------------------------------------
        # SELECT PERSONALITY
        # ---------------------------------------------

        highest_score = max(
            data_score,
            developer_score,
            creative_score,
            leadership_score
        )

        if highest_score == data_score and data_score > 0:

            personality_title = "Analytical Problem Solver 🧩"

            personality_description = (
                "You have a strong analytical mindset and enjoy "
                "finding insights, solving problems, and working "
                "with data-driven solutions."
            )

            personality_tags = [
                "Analytical",
                "Logical",
                "Problem Solver",
                "Curious"
            ]

        elif highest_score == developer_score and developer_score > 0:

            personality_title = "Tech Builder 💻"

            personality_description = (
                "You enjoy building technology solutions and turning "
                "ideas into real applications, systems, and digital "
                "experiences."
            )

            personality_tags = [
                "Builder",
                "Technical",
                "Creative",
                "Innovative"
            ]

        elif highest_score == creative_score and creative_score > 0:

            personality_title = "Creative Innovator 🎨"

            personality_description = (
                "You combine creativity with technology and enjoy "
                "designing engaging experiences and new ideas."
            )

            personality_tags = [
                "Creative",
                "Innovative",
                "Visual",
                "Curious"
            ]

        elif highest_score == leadership_score and leadership_score > 0:

            personality_title = "Strategic Leader 🚀"

            personality_description = (
                "You show strengths in communication, teamwork, and "
                "guiding people toward shared goals and results."
            )

            personality_tags = [
                "Leader",
                "Strategic",
                "Collaborative",
                "Confident"
            ]

    return render_template(

        "dashboard.html",

        username=session["username"],
        analysis=analysis,

        personality_title=personality_title,
        personality_description=personality_description,
        personality_tags=personality_tags,

        career_xp=career_xp,
        career_level=career_level,
        career_title=career_title,
        current_level_xp=current_level_xp,
        xp_per_level=xp_per_level,
        xp_progress=xp_progress

    )

# ---------------- PROFILE ----------------

@app.route("/profile")
def profile():

    if "username" not in session:
        return redirect("/")

    username = session["username"]

    connection = get_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:

        # =========================================
        # GET USER PROFILE
        # =========================================

        cursor.execute(
            """
            SELECT
                id,
                full_name,
                username,
                email,
                phone,
                location,
                headline,
                linkedin,
                github,
                portfolio,
                skills,
                created_at
            FROM users
            WHERE username = %s
            """,
            (username,)
        )

        user = cursor.fetchone()

        # User not found
        if not user:
            return redirect("/")

        # =========================================
        # TOTAL RESUMES
        # =========================================

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM resume_analysis
            WHERE username = %s
            """,
            (username,)
        )

        total_resumes = cursor.fetchone()["total"]

        # =========================================
        # AVERAGE ATS SCORE
        # =========================================

        cursor.execute(
            """
            SELECT AVG(ats_score) AS average_ats
            FROM resume_analysis
            WHERE username = %s
            """,
            (username,)
        )

        result = cursor.fetchone()

        if result["average_ats"] is None:
            average_ats = 0
        else:
            average_ats = round(float(result["average_ats"]), 1)

        # =========================================
        # BEST RESUME SCORE
        # =========================================

        cursor.execute(
            """
            SELECT MAX(resume_score) AS best_resume
            FROM resume_analysis
            WHERE username = %s
            """,
            (username,)
        )

        result = cursor.fetchone()

        if result["best_resume"] is None:
            best_resume = 0
        else:
            best_resume = result["best_resume"]

        # =========================================
        # SEND DATA TO PROFILE PAGE
        # =========================================

        return render_template(
            "profile.html",
            user=user,
            total_resumes=total_resumes,
            average_ats=average_ats,
            best_resume=best_resume
        )

    finally:

        cursor.close()
        connection.close()

        # ---------------- EDIT PROFILE ----------------

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    if "username" not in session:
        return redirect("/")

    username = session["username"]

    connection = get_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:

        # ==============================
        # GET CURRENT PROFILE
        # ==============================

        cursor.execute(
            """
            SELECT
                id,
                full_name,
                username,
                email,
                phone,
                location,
                headline,
                linkedin,
                github,
                portfolio,
                skills
            FROM users
            WHERE username = %s
            """,
            (username,)
        )

        user = cursor.fetchone()

        if not user:
            return redirect("/")

        # ==============================
        # SAVE PROFILE
        # ==============================

        if request.method == "POST":

            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            location = request.form.get("location", "").strip()
            headline = request.form.get("headline", "").strip()
            skills = request.form.get("skills", "").strip()
            linkedin = request.form.get("linkedin", "").strip()
            github = request.form.get("github", "").strip()
            portfolio = request.form.get("portfolio", "").strip()

            cursor.execute(
                """
                UPDATE users
                SET
                    full_name = %s,
                    email = %s,
                    phone = %s,
                    location = %s,
                    headline = %s,
                    skills = %s,
                    linkedin = %s,
                    github = %s,
                    portfolio = %s
                WHERE username = %s
                """,
                (
                    full_name,
                    email,
                    phone,
                    location,
                    headline,
                    skills,
                    linkedin,
                    github,
                    portfolio,
                    username
                )
            )

            connection.commit()

            session["username"] = username

            return redirect("/profile")

        # ==============================
        # SHOW EDIT PAGE
        # ==============================

        return render_template(
            "edit_profile.html",
            user=user
        )

    finally:

        cursor.close()
        connection.close()
        
# ---------------- UPLOAD PAGE ----------------

@app.route("/upload")
def upload_page():

    if "username" not in session:
        return redirect("/")

    # If the user already analyzed a resume,
    # show the existing resume analysis again.
    if "analysis" in session:

        return render_template(
            "resume_dashboard.html",
            analysis=session["analysis"],
            resume_text=session.get("resume_text", ""),
            metadata=session.get("resume_metadata", {})
        )

    # No previous analysis → show upload page
    return render_template(
        "upload.html"
    )


# ---------------- NEW RESUME ----------------

@app.route("/new-resume")
def new_resume():

    if "username" not in session:
        return redirect("/")

    # Remove current resume analysis
    session.pop("analysis", None)

    # Open fresh resume upload page
    return redirect("/upload")


# ---------------- UPLOAD RESUME ----------------

@app.route("/upload", methods=["POST"])
def upload_resume():

    if "username" not in session:
        return redirect("/")

    if "resume" not in request.files:
        flash(
            "Please upload a resume.",
            "error"
        )
        return redirect("/upload")

    file = request.files["resume"]

    if file.filename == "":
        flash(
            "Please choose a resume file.",
            "error"
        )
        return redirect("/upload")

    original_filename = secure_filename(
    file.filename
    )

    file_extension = os.path.splitext(
     original_filename
    )[1]

    unique_filename = (
     f"{uuid.uuid4().hex}{file_extension}"
    )

    filepath = os.path.join(
    app.config["UPLOAD_FOLDER"],
    unique_filename
    )

    file.save(filepath)

 # Keep the original filename for database/history display
    filename = original_filename

    # ---------------- Calculate File Hash ----------------

    with open(filepath, "rb") as f:
        file_bytes = f.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()

    # ---------------- Check Duplicate Resume ----------------

    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT analysis_json, extracted_text
            FROM resume_analysis
            WHERE username = %s AND file_hash = %s
            ORDER BY uploaded_at DESC LIMIT 1
        """, (session["username"], file_hash))
        
        existing = cursor.fetchone()
        
        if existing and existing[0]:
            # Duplicate Found: Reuse existing analysis
            analysis = json.loads(existing[0])
            resume_text = existing[1]
            
            # Populate live jobs for the session
            jobs = recommend_jobs(
                analysis.get("predicted_job", ""),
                analysis.get("skills", [])
            )
            analysis["live_jobs"] = jobs
            
            session["analysis"] = analysis
            
            cursor.close()
            connection.close()
            
            flash("Resume detected! Reusing previous analysis.", "success")
            
            return render_template(
                "resume_dashboard.html",
                analysis=analysis,
                resume_text=resume_text,
                metadata={"file_name": filename} # Minimal metadata for reused
            )

        cursor.close()
        connection.close()

    except Exception as e:
        print("Duplicate Lookup Error:", e)

    # ---------------- Resume Extraction ----------------


    parser_result = extract_text(
        filepath
    )

    if not parser_result["success"]:
        flash(
            parser_result["message"],
            "error"
        )
        return redirect("/upload")

    resume_text = parser_result["text"]
    metadata = parser_result["metadata"]

       # ---------------- AI Analysis ----------------

    analysis = analyze_resume(
        resume_text
    )

    # ---------------- LIVE JOB RECOMMENDATIONS ----------------

   # ---------------- JOB RECOMMENDATIONS ----------------
    print(analysis.keys())
    jobs = recommend_jobs(
    analysis["predicted_job"],
    analysis["skills"]
)  
    analysis["live_jobs"] = jobs
    # ---------------- SAVE ANALYSIS HISTORY ----------------

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""

            INSERT INTO resume_analysis
            (
                username,
                resume_name,
                resume_score,
                ats_score,
                predicted_job,
                job_match,
                file_hash,
                analysis_json,
                extracted_text
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )

        """, (

            session["username"],
            filename,
            analysis["resume_score"],
            analysis["ats_score"],
            analysis["predicted_job"],
            analysis["job_match"],
            file_hash,
            json.dumps(analysis),
            resume_text

        ))


        connection.commit()

        cursor.close()

        connection.close()

    except Exception as e:

        print("Resume History Error:", e)

    session["analysis"] = analysis
    
    # ---------------- Show Premium Dashboard ----------------

    return render_template(
        "resume_dashboard.html",
        analysis=analysis,
        resume_text=resume_text,
        metadata=metadata
    )
    
# ---------------- DOWNLOAD PDF REPORT ----------------

@app.route("/download-report")
def download_report():

    if "username" not in session:

        return redirect("/")

    if "analysis" not in session:

        flash(

            "Please analyze a resume first.",

            "error"

        )

        return redirect("/upload")

    analysis = session["analysis"]

    report_path = "TalentIQ_AI_Report.pdf"

    generate_report(

        report_path,

        analysis

    )

    return send_file(

        report_path,

        as_attachment=True

    )






# ---------------- AI CHAT PAGE ----------------

@app.route("/ai-chat")
def ai_chat():

    if "username" not in session:
        return redirect("/")

    if "analysis" not in session:

        flash(
            "Please analyze a resume first.",
            "error"
        )

        return redirect("/upload")

    return render_template(
        "ai_chat.html",
        analysis=session["analysis"]
    )



# ---------------- ASK AI ----------------

@app.route("/ask-ai", methods=["POST"])
def ask_ai():

    if "username" not in session:
        return jsonify({
            "reply": "Please login to use the AI assistant.",
            "error": True
        }), 401

    if "analysis" not in session:
        return jsonify({
            "reply": "Please analyze a resume first.",
            "error": True
        }), 400

    message = request.form.get("message", "").strip()

    if not message:
        return jsonify({
            "reply": "Please enter a message.",
            "error": True
        }), 400

    if len(message) > 1000:
        return jsonify({
            "reply": "Message is too long. Please keep it under 1000 characters.",
            "error": True
        }), 400

    reply = generate_ai_reply(
        message,
        session["analysis"],
        session.get("username")
    )

    return jsonify({"reply": reply})
    

# ===============================
# Resume History
# ===============================

@app.route("/resume-history")
def resume_history():

    if "username" not in session:
        return redirect("/")

    connection = get_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:

        # =========================================
        # GET RESUME HISTORY
        # =========================================

        cursor.execute("""
            SELECT
                id,
                resume_name,
                resume_score,
                ats_score,
                predicted_job,
                job_match,
                uploaded_at
            FROM resume_analysis
            WHERE username = %s
            ORDER BY uploaded_at DESC
        """, (session["username"],))

        history = cursor.fetchall()


        # =========================================
        # GET STATISTICS
        # =========================================

        cursor.execute("""
            SELECT
                COUNT(*) AS total_resumes,
                AVG(ats_score) AS average_ats,
                MAX(resume_score) AS best_resume
            FROM resume_analysis
            WHERE username = %s
        """, (session["username"],))

        stats = cursor.fetchone()


        # =========================================
        # PREPARE STATISTICS
        # =========================================

        total_resumes = stats["total_resumes"] or 0

        average_ats = (
            round(float(stats["average_ats"]), 1)
            if stats["average_ats"] is not None
            else 0
        )

        best_resume = (
            stats["best_resume"]
            if stats["best_resume"] is not None
            else 0
        )


        # =========================================
        # SHOW HISTORY PAGE
        # =========================================

        builder_resumes = []
        try:
            builder_resumes = list_user_resumes(session["username"])
        except Exception as exc:
            print("user_resumes history:", exc)

        return render_template(
            "resume_history.html",
            history=history,
            builder_resumes=builder_resumes,
            total_resumes=total_resumes,
            average_ats=average_ats,
            best_resume=best_resume
        )

    finally:

        cursor.close()
        connection.close()


# ===============================
# DELETE RESUME HISTORY
# ===============================

@app.route("/delete-resume/<int:resume_id>", methods=["POST"])
def delete_resume(resume_id):

    if "username" not in session:
        return redirect("/")

    username = session["username"]

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM resume_analysis
            WHERE id = %s
            AND username = %s
        """, (resume_id, username))

        connection.commit()

        flash(
            "Resume analysis deleted successfully.",
            "success"
        )

    except Exception as e:

        connection.rollback()

        print("Delete Resume History Error:", e)

        flash(
            "Failed to delete resume analysis.",
            "error"
        )

    finally:

        cursor.close()
        connection.close()

    return redirect("/resume-history")

# ---------------- ANALYTICS ----------------

@app.route("/analytics")
def analytics():

    if "username" not in session:
        return redirect("/")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            resume_name,
            resume_score,
            ats_score
        FROM resume_analysis
        WHERE username=%s
        ORDER BY uploaded_at ASC
    """, (session["username"],))

    rows = cursor.fetchall()

    labels = []
    resume_scores = []
    ats_scores = []

    for row in rows:
        labels.append(row[0])
        resume_scores.append(row[1])
        ats_scores.append(row[2])

    cursor.execute("""
        SELECT
            COUNT(*),
            AVG(ats_score),
            MAX(resume_score)
        FROM resume_analysis
        WHERE username=%s
    """, (session["username"],))

    stats = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "analytics.html",
        labels=labels,
        resume_scores=resume_scores,
        ats_scores=ats_scores,
        total_resumes=stats[0] or 0,
        average_ats=round(stats[1], 1) if stats[1] else 0,
        best_resume=stats[2] or 0
    )




@app.route("/settings")
def settings():
    return render_template("settings.html")
# ---------------- CHANGE PASSWORD ----------------

@app.route("/change-password", methods=["POST"])
def change_password():

    if "username" not in session:
        return redirect("/")

    username = session["username"]

    current_password = request.form.get(
        "current_password", ""
    ).strip()

    new_password = request.form.get(
        "new_password", ""
    ).strip()

    confirm_password = request.form.get(
        "confirm_password", ""
    ).strip()

    # =========================================
    # BASIC VALIDATION
    # =========================================

    if not current_password:
        return redirect("/settings")

    if not new_password:
        return redirect("/settings")

    if new_password != confirm_password:
        return redirect("/settings")

    if len(new_password) < 6:
        return redirect("/settings")

    if current_password == new_password:
        return redirect("/settings")


    connection = get_connection()

    cursor = connection.cursor(
        pymysql.cursors.DictCursor
    )

    try:

        # =========================================
        # GET CURRENT PASSWORD
        # =========================================

        cursor.execute(
            """
            SELECT password
            FROM users
            WHERE username = %s
            """,
            (username,)
        )

        user = cursor.fetchone()

        if not user:
            return redirect("/")


        # =========================================
        # VERIFY CURRENT PASSWORD
        # =========================================

        if not bcrypt.checkpw(
            current_password.encode("utf-8"),
            user["password"].encode("utf-8")
            if isinstance(user["password"], str)
            else user["password"]
        ):
            return redirect("/settings")


        # =========================================
        # HASH NEW PASSWORD
        # =========================================

        hashed_password = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        )


        # =========================================
        # UPDATE PASSWORD
        # =========================================

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE username = %s
            """,
            (
                hashed_password.decode("utf-8"),
                username
            )
        )

        connection.commit()


        # =========================================
        # RETURN TO SETTINGS
        # =========================================

        return redirect("/settings")


    finally:

        cursor.close()
        connection.close()

# ---------------- FEEDBACK ----------------

@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    if "username" not in session:
        return redirect("/")

    if request.method == "POST":

        rating = request.form["rating"]
        message = request.form["message"]

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""

                INSERT INTO feedback
                (username, rating, message)

                VALUES (%s, %s, %s)

            """, (

                session["username"],
                rating,
                message

            ))

            connection.commit()

            cursor.close()
            connection.close()

            flash(
                "Thank you for your feedback!",
                "success"
            )

        except Exception as e:

            print("Feedback Error :", e)

            flash(
                "Failed to submit feedback.",
                "error"
            )

        return redirect("/feedback")

    return render_template("feedback.html")

@app.route("/skill-analysis")
def skill_analysis():

    if "username" not in session:
        return redirect("/")

    # Get latest resume analysis from session
    analysis = session.get("analysis")

    if not analysis:
        return render_template(
            "skill_analysis.html",
            skills=[]
        )

    # Get detected skills from AI analysis
    skills = analysis.get("skills", [])

    return render_template(
        "skill_analysis.html",
        skills=skills
    )

@app.route("/career-prediction")
def career_prediction():

    if "username" not in session:
        return redirect("/")

    return render_template("career_prediction.html")

@app.route("/career-roadmap")
def career_roadmap():

    if "username" not in session:
        return redirect("/")

    return render_template("career_roadmap.html")

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect("/")


@app.route("/resume-improvement")
def resume_improvement():

    if "username" not in session:
        return redirect("/")

    if "analysis" not in session:
        flash("Please analyze a resume first.", "error")
        return redirect("/upload")

    return render_template(
        "resume_improvement.html",
        analysis=session["analysis"]
    )

def _builder_user_profile(username):
    connection = get_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(
            """
            SELECT
                full_name,
                email,
                phone,
                location,
                headline,
                linkedin,
                github,
                portfolio,
                skills
            FROM users
            WHERE username = %s
            LIMIT 1
            """,
            (username,),
        )
        return cursor.fetchone() or {}
    finally:
        cursor.close()
        connection.close()


def _builder_analysis(username):
    analysis = session.get("analysis")
    if isinstance(analysis, dict) and analysis:
        return analysis

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT analysis_json
            FROM resume_analysis
            WHERE username = %s
              AND analysis_json IS NOT NULL
            ORDER BY uploaded_at DESC
            LIMIT 1
            """,
            (username,),
        )
        row = cursor.fetchone()
        if not row or not row[0]:
            return {}
        parsed = json.loads(row[0])
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}
    finally:
        cursor.close()
        connection.close()


def _builder_payload():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return {}
    return normalize_resume(payload)


def _render_resume_builder(username, resume_id=None):
    saved = None
    if resume_id is not None:
        saved = load_user_resume(username, resume_id)
        if not saved:
            flash("Resume not found.", "error")
            return redirect("/resume-builder")

    resume = build_resume_from_sources(
        user=_builder_user_profile(username),
        analysis=_builder_analysis(username),
        saved=saved,
    )
    return render_template(
        "resume_builder.html",
        resume=resume,
        templates=list_templates(),
        saved_resumes=list_user_resumes(username),
        quality=evaluate_resume(resume, _builder_analysis(username)),
    )


@app.route("/resume-builder")
def resume_builder():
    if "username" not in session:
        return redirect("/")
    return _render_resume_builder(session["username"])


@app.route("/resume-builder/<int:resume_id>")
def resume_builder_edit(resume_id):
    if "username" not in session:
        return redirect("/")
    return _render_resume_builder(session["username"], resume_id)


@app.route("/resume-builder/save", methods=["POST"])
def resume_builder_save():
    if "username" not in session:
        return jsonify({"ok": False, "error": "Please log in."}), 401

    username = session["username"]
    data = _builder_payload()
    validation = validate_resume(data)
    if validation["errors"]:
        return jsonify({"ok": False, "error": validation["errors"][0]}), 400

    analysis = _builder_analysis(username)
    quality = evaluate_resume(data, analysis)
    data["ats_score"] = quality["ats_score"]
    try:
        saved = save_user_resume(username, data)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify(
        {
            "ok": True,
            "resume": saved,
            "quality": quality,
        }
    )


@app.route("/resume-builder/duplicate", methods=["POST"])
def resume_builder_duplicate():
    if "username" not in session:
        return jsonify({"ok": False, "error": "Please log in."}), 401

    payload = request.get_json(silent=True) or {}
    resume_id = payload.get("id")
    try:
        resume_id = int(resume_id)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Save the resume before duplicating."}), 400

    copied = duplicate_user_resume(session["username"], resume_id)
    if not copied:
        return jsonify({"ok": False, "error": "Resume not found."}), 404
    return jsonify({"ok": True, "resume": copied})


@app.route("/resume-builder/delete", methods=["POST"])
def resume_builder_delete():
    if "username" not in session:
        return jsonify({"ok": False, "error": "Please log in."}), 401

    payload = request.get_json(silent=True) or {}
    resume_id = payload.get("id")
    try:
        resume_id = int(resume_id)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Invalid resume."}), 400

    deleted = delete_user_resume(session["username"], resume_id)
    if not deleted:
        return jsonify({"ok": False, "error": "Resume not found."}), 404
    return jsonify({"ok": True})


@app.route("/resume-builder/ats", methods=["POST"])
def resume_builder_ats():
    if "username" not in session:
        return jsonify({"ok": False, "error": "Please log in."}), 401

    data = _builder_payload()
    quality = evaluate_resume(data, _builder_analysis(session["username"]))
    return jsonify({"ok": True, "quality": quality})


@app.route("/resume-builder/pdf", methods=["POST"])
def resume_builder_pdf():
    if "username" not in session:
        return jsonify({"error": "Please log in."}), 401

    data = _builder_payload()
    validation = validate_resume(data)
    if not data.get("full_name"):
        return jsonify({"error": "Add your full name before downloading."}), 400
    if validation["errors"] and data.get("email"):
        return jsonify({"error": validation["errors"][0]}), 400

    buffer = io.BytesIO()
    generate_pdf(data, buffer)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=resume_filename(data, "pdf"),
        mimetype="application/pdf",
    )


@app.route("/resume-builder/docx", methods=["POST"])
def resume_builder_docx():
    if "username" not in session:
        return jsonify({"error": "Please log in."}), 401

    data = _builder_payload()
    if not data.get("full_name"):
        return jsonify({"error": "Add your full name before downloading."}), 400
    validation = validate_resume(data)
    if validation["errors"] and data.get("email"):
        return jsonify({"error": validation["errors"][0]}), 400

    buffer = io.BytesIO()
    generate_docx(data, buffer)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=resume_filename(data, "docx"),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.route("/download-resume-pdf")
def download_resume_pdf():

    if "analysis" not in session:
        return redirect("/upload")

    resume = generate_resume(session["analysis"])

    output = "AI_Resume.pdf"

    create_pdf(
        resume,
        output
    )

    return send_file(
        output,
        as_attachment=True
    )


@app.route("/download-resume-docx")
def download_resume_docx():

    if "analysis" not in session:
        return redirect("/upload")

    resume = generate_resume(session["analysis"])

    output = "AI_Resume.docx"

    create_docx(
        resume,
        output
    )

    return send_file(
        output,
        as_attachment=True
    )

# ---------------- PROFESSIONAL RESUME BUILDER ----------------

@app.route("/professional-resume")
def professional_resume():

    if "analysis" not in session:
        return redirect("/upload")

    resume = generate_resume_data(session["analysis"])

    return render_template(
        "professional_resume.html",
        resume=resume
    )


@app.route("/professional-resume/pdf")
def professional_resume_pdf():

    if "analysis" not in session:
        return redirect("/upload")

    resume = generate_resume_data(session["analysis"])

    output = "Professional_Resume.pdf"

    generate_pdf(
        resume,
        output
    )

    return send_file(
        output,
        as_attachment=True
    )


@app.route("/professional-resume/docx")
def professional_resume_docx():

    if "analysis" not in session:
        return redirect("/upload")

    resume = generate_resume_data(session["analysis"])

    output = "Professional_Resume.docx"

    generate_docx(
        resume,
        output
    )

    return send_file(
        output,
        as_attachment=True
    )
# ---------------- START APPLICATION ----------------

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)

