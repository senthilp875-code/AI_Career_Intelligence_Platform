from flask import Flask, render_template, request, redirect
import pymysql
import bcrypt

app = Flask(__name__)

db = pymysql.connect(
    host="localhost",
    user="root",
    password="senthil777",      # Your MySQL password
    database="AI_Recruitment"
)

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():

    full_name = request.form["full_name"]
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor = db.cursor()

    sql = """
    INSERT INTO users(full_name, username, email, password)
    VALUES(%s,%s,%s,%s)
    """

    cursor.execute(sql, (full_name, username, email, hashed_password))
    db.commit()

    return redirect("/")


@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    cursor = db.cursor()

    cursor.execute(
        "SELECT username, password FROM users WHERE username=%s",
        (username,)
    )

    user = cursor.fetchone()

    if user:

        stored_password = user[1]

        if bcrypt.checkpw(password.encode(), stored_password.encode() if isinstance(stored_password, str) else stored_password):

            return render_template(
                "dashboard.html",
                username=username
            )

    return "❌ Invalid Username or Password"


if __name__ == "__main__":
    app.run(debug=True)