from flask import Flask, render_template, request, redirect, session, send_file
import qrcode
import sqlite3
from datetime import datetime
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"


#  HOME (QR + Scanner)
@app.route('/')
def index():
    if 'student' not in session:
        return redirect('/student_login')

    if not os.path.exists("static"):
        os.makedirs("static")

    today = datetime.now().strftime("%Y-%m-%d")
    img = qrcode.make(today)
    img.save("static/qr.png")

    return render_template("index.html")


#  STUDENT LOGIN
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        name = request.form['name']
        session['student'] = name
        return redirect('/')
    return render_template('student_login.html')


#  TEACHER LOGIN
@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "teacher" and password == "1234":
            session['teacher'] = True
            return redirect('/dashboard')
        else:
            return "Invalid Teacher Login"

    return render_template('teacher_login.html')


#  SCAN ATTENDANCE
@app.route('/scan', methods=['POST'])
def scan():
    if 'student' not in session:
        return redirect('/student_login')

    name = session['student']

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        name TEXT,
        date TEXT,
        time TEXT
    )
    """)

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    cur.execute("INSERT INTO attendance VALUES (?, ?, ?)", (name, date, time))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


#  DASHBOARD (Teacher Only)
@app.route('/dashboard')
def dashboard():
    if 'teacher' not in session:
        return redirect('/teacher_login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # All attendance data
    cur.execute("SELECT * FROM attendance ORDER BY date DESC, time DESC")
    data = cur.fetchall()

    # Attendance percentage
    cur.execute("SELECT name, COUNT(*) FROM attendance GROUP BY name")
    student_counts = cur.fetchall()

    cur.execute("SELECT COUNT(DISTINCT date) FROM attendance")
    total_days = cur.fetchone()[0]

    percentage_data = []
    for name, count in student_counts:
        percent = (count / total_days) * 100 if total_days > 0 else 0
        percentage_data.append((name, count, round(percent, 2)))

    conn.close()

    return render_template("dashboard.html",
                           data=data,
                           percentage_data=percentage_data)


#  CLEAR DATA
@app.route('/clear', methods=['POST'])
def clear():
    if 'teacher' not in session:
        return redirect('/teacher_login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("DELETE FROM attendance")

    conn.commit()
    conn.close()

    return redirect('/dashboard')


#  DOWNLOAD EXCEL
@app.route('/download')
def download():
    if 'teacher' not in session:
        return redirect('/teacher_login')

    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query("SELECT * FROM attendance", conn)
    conn.close()

    file_path = "attendance.xlsx"
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)


#  LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/student_login')


# RUN APP
if __name__ == '__main__':
    app.run(debug=True, port=5001)
