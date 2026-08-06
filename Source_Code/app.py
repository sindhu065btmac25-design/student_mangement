from flask import Flask , render_template , request , redirect , session , Response
import sqlite3 , bcrypt
import csv
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from flask import send_file
import os
from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename
import os

app=Flask(__name__)
app.secret_key = "student_management_secret"

def hash_password(password):
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

def create_table():
    conn=sqlite3.connect(
        "Database/Student_management.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        course TEXT,
        semester TEXT,
        email TEXT
    )
    
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs(

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    action TEXT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("DELETE FROM users")

    cursor.execute(
    """
    INSERT INTO users(username, password, role)
    VALUES (?, ?, ?)
    """,
    ("admin", hash_password("Admin@123"), "Admin")
    )  

    cursor.execute(
    """
    INSERT INTO users(username, password, role)
    VALUES (?, ?, ?)
    """,
    ("faculty", hash_password("Faculty@123"), "Faculty")
    )

    cursor.execute(
    """
    INSERT INTO users(username, password, role)
    VALUES (?, ?, ?)
    """,
    ("student", hash_password("Student@123"), "Student")
    )
    conn.commit()
    conn.close()

def save_log(username, action):

    conn = sqlite3.connect(
        "Database/Student_management.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO audit_logs(username, action)
        VALUES (? , ?)
        """,
        (username, action)
    )

    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        username = username.strip()
        password = password.strip()

        if not username or not password:
            return "Username and Password are required."

        conn = sqlite3.connect("Database/Student_management.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT username, password, role
            FROM users
            WHERE username=?
            """,
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and bcrypt.checkpw(
            password.encode(),
            user[1].encode()
        ):

            session["username"] = user[0]
            session["role"] = user[2]

            save_log(
                user[0],
                "User Logged In"
            )

            return redirect("/dashboard")

        else:
            return "Invalid Username or Password"

    return render_template("login.html")

@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if session.get("role") != "Admin":
        return render_template("access_denied.html")

    if request.method == "POST":

        name = request.form["name"]
        course = request.form["course"]
        semester = request.form["semester"]
        email = request.form["email"]

        # Photo Upload
        photo = request.files["photo"]

        filename = secure_filename(photo.filename)

        photo.save(
            os.path.join("static/uploads", filename)
        )

        conn = sqlite3.connect(
            "Database/Student_management.db"
        )

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students
            (name, course, semester, email, photo)
            VALUES (?, ?, ?, ?, ?)
        """,
        (name, course, semester, email, filename)
        )

        conn.commit()
        conn.close()

        save_log(
            session["username"],
            f"Added Student : {name}"
        )

        return redirect("/view_student")

    return render_template("add_student.html")

@app.route("/view_student")
def view_student():

    conn = sqlite3.connect("Database/Student_management.db")
    cursor = conn.cursor()

    search = request.args.get("search", "")

    if search:

        cursor.execute(
            """
            SELECT * FROM students
            WHERE name LIKE ?
            """,
            ('%' + search + '%',)
        )

    else:

        cursor.execute(
            "SELECT * FROM students"
        )

    students = cursor.fetchall()
    
    print(students)
    conn.close()

    return render_template(
        "view_student.html",
        students=students,
        role=session.get("role")
    )

@app.route("/upload_assets/<int:id>", methods=["POST"])
def upload_assets(id):

    qr = request.files["qr"]
    barcode = request.files["barcode"]

    qr_name = None
    barcode_name = None

    if qr.filename != "":
        qr_name = secure_filename(qr.filename)
        qr.save(os.path.join("static/uploads", qr_name))

    if barcode.filename != "":
        barcode_name = secure_filename(barcode.filename)
        barcode.save(os.path.join("static/uploads", barcode_name))

    conn = sqlite3.connect("Database/Student_management.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE students
    SET qr=?, barcode=?
    WHERE id=?
    """, (qr_name, barcode_name, id))

    conn.commit()
    conn.close()

    return redirect(f"/id_card/{id}")

@app.route("/id_card/<int:id>")
def id_card(id):

    conn = sqlite3.connect("Database/Student_management.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "id_card.html",
        student=student
    )

@app.route("/edit_student/<int:id>" , methods = ["GET" , "POST"])
def edit_student(id):

    if session.get("role") not in ["Admin", "Faculty"]:
        return render_template("access_denied.html")

    conn = sqlite3.connect("Database/Student_management.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        course = request.form["course"]
        semester = request.form["semester"]
        email = request.form["email"]

        cursor.execute("""
        UPDATE students
        SET name=?, course=?, semester=?, email=?
        WHERE id=?
        """, (name, course, semester, email, id))

        conn.commit()
        conn.close()

        save_log(
            session["username"],
            f"Edited Student : {name}"
        )

        return redirect("/view_student")

    cursor.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )

@app.route("/delete_student/<int:id>")
def delete_student(id):

    if session.get("role") != "Admin":
        return render_template("access_denied.html")

    conn = sqlite3.connect(
        "Database/Student_management.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM students WHERE id=?",
        (id,)
    )

    student = cursor.fetchone()

    cursor.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    save_log(
        session["username"],
        f"Deleted Student : {student[0]}"
    )

    return redirect("/view_student")


@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/")

    conn = sqlite3.connect("Database/Student_management.db")
    cursor = conn.cursor()

    # Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Total Users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Total Audit Logs
    cursor.execute("SELECT COUNT(*) FROM audit_logs")
    total_logs = cursor.fetchone()[0]

    # Recent Activities
    cursor.execute("""
        SELECT username, action, time
        FROM audit_logs
        ORDER BY id DESC
        LIMIT 5
    """)
    recent_logs = cursor.fetchall()

    # Chart Data (Students Per Course)
    cursor.execute("""
        SELECT course, COUNT(*)
        FROM students
        GROUP BY course
    """)
    chart_data = cursor.fetchall()

    labels = []
    values = []

    for row in chart_data:
        labels.append(row[0])
        values.append(row[1])

    # Debug (optional)
    print(chart_data)
    print(labels)
    print(values)

    conn.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"],
        total_students=total_students,
        total_users=total_users,
        total_logs=total_logs,
        recent_logs=recent_logs,
        labels=labels,
        values=values
    )

@app.route("/audit_logs")
def audit_logs():

    if session.get("role") != "Admin":
        return render_template("access_denied.html")

    username = request.args.get("username", "")
    action = request.args.get("action", "")

    conn = sqlite3.connect("Database/Student_management.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, action, time
        FROM audit_logs
        WHERE username LIKE ?
        AND action LIKE ?
        ORDER BY id DESC
    """,
    (
        "%" + username + "%",
        "%" + action + "%"
    ))

    logs = cursor.fetchall()

    conn.close()

    return render_template(
        "audit_logs.html",
        logs=logs
    )


@app.route("/generate_report")
def generate_report():

    if session.get("role") != "Admin":
        return render_template("access_denied.html")

    conn = sqlite3.connect("Database/Student_management.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id,name,course,semester,email
        FROM students
    """)

    students = cursor.fetchall()

    conn.close()

    pdf_file = "Student_Report.pdf"

    doc = SimpleDocTemplate(pdf_file)

    data = [
        ["ID","Name","Course","Semester","Email"]
    ]

    for student in students:
        data.append(student)

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),

        ('GRID',(0,0),(-1,-1),1,colors.black),

        ('BACKGROUND',(0,1),(-1,-1),colors.beige),

        ('ALIGN',(0,0),(-1,-1),'CENTER')
    ]))

    doc.build([table])

    return send_file(
        pdf_file,
        as_attachment=True
    )

@app.route("/export_logs")
def export_logs():

    if session.get("role") != "Admin":
        return render_template("access_denied.html")

    username = request.args.get("username", "")
    action = request.args.get("action", "")

    conn = sqlite3.connect("Database/Student_management.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, action, time
        FROM audit_logs
        WHERE username LIKE ?
        AND action LIKE ?
        ORDER BY id DESC
    """,
    (
        "%" + username + "%",
        "%" + action + "%"
    ))

    logs = cursor.fetchall()

    conn.close()

    import pandas as pd

    df = pd.DataFrame(
        logs,
        columns=[
            "Username",
            "Action",
            "Time"
        ]
    )

    filename = "Filtered_Audit_Logs.csv"

    df.to_csv(
        filename,
        index=False
    )

    save_log(
        session["username"],
        "Exported Filtered Audit Logs"
    )

    return send_file(
        filename,
        as_attachment=True
    )

@app.route("/logout")
def logout():

    if "username" in session:

        save_log(
            session["username"],
            "User Logged Out"
        )

    session.clear()

    return redirect("/")

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404

create_table()

#conn = sqlite3.connect("Database/Student_management.db")
#cursor = conn.cursor()

#try:
 #   cursor.execute("ALTER TABLE students ADD COLUMN photo TEXT")
  ##  conn.commit()
    #print("✅ Photo column added successfully!")#
    #except Exception as e:
    #print(e)

#conn.close()

if __name__ == "__main__":
    app.run(debug=True)
