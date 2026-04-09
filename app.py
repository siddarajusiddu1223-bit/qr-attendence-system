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
    img = qrcode.make("Scan to mark attendance")
    img.save("static/qr.png")
    return render_template("index.html")
@app.route('/scan', methods=['POST'])
def scan():
    name = request.form['name']
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS attendance (name TEXT, time TEXT)")
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO attendance VALUES (?, ?)", (name, time))
    conn.commit()
    conn.close()
    return redirect('/dashboard')
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM attendance")
    data = cur.fetchall()
    conn.close()
    return render_template("dashboard.html", data=data)
if __name__ == '__main__':
    app.run(debug=True)
