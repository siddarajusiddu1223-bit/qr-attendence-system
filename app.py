from flask import Flask, render_template, request, redirect
import qrcode
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
@app.route('/')
def index():
    if not os.path.exists("static"):
        os.makedirs("static")
    today = datetime.now().strftime("%Y-%m-%d")
    img = qrcode.make(today)
    img.save("static/qr.png")
    return render_template("index.html")
@app.route('/scan', methods=['POST'])
def scan():
    name = request.form['name']
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
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM attendance ORDER BY date DESC, time DESC")
    data = cur.fetchall()
    count = len(data)
    conn.close()
    return render_template("dashboard.html", data=data, count=count)
@app.route('/clear', methods=['POST'])
def clear():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM attendance")
    conn.commit()
    conn.close()
    return redirect('/dashboard')
    
if __name__ == '__main__':
    app.run(debug=True)
