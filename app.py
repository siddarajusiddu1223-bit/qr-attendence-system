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
    img = qrcode.make("Namratha")
    img.save("static/qr.png")
    return render_template("index.html")
@app.route('/clear', methods=['POST'])
def clear():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM attendance")
    conn.commit()
    conn.close()
    return redirect('/dashboard')
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM attendance")
    data = cur.fetchall()
    count = len(data)
    conn.close()
    return render_template("dashboard.html", data=data, count=count)
