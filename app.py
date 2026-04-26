from mimetypes import inited
import sqlite3
from flask import Flask, render_template, request, redirect
from datetime import date

app = Flask(__name__)
inited()

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            xp INTEGER,
            streak INTEGER,
            last_completed TEXT
        )
    """)
    
    # Insert default user if not exists
    user = conn.execute("SELECT * FROM user WHERE id = 1").fetchone()
    if not user:
        conn.execute("INSERT INTO user (id, xp, streak, last_completed) VALUES (1, 120, 0, NULL)")
    
    conn.commit()
    conn.close()

xp = 120
streak = 0
last_completed_date = None
completed_today = False

def get_level(xp):
    if xp < 100:
        return 1
    elif xp < 200:
        return 2
    else:
        return 3

@app.route("/")
@app.route("/")
def home():
    conn = get_db()
    user = conn.execute("SELECT * FROM user WHERE id = 1").fetchone()
    conn.close()

    xp = user["xp"]
    streak = user["streak"]

    progress = min(100, round((xp / 300) * 100))
    level = get_level(xp)

    return render_template("index.html", xp=xp, streak=streak, progress=progress, level=level)
    

@app.route("/complete", methods=["POST"])
def complete_task():
    conn = get_db()
    user = conn.execute("SELECT * FROM user WHERE id = 1").fetchone()

    xp = user["xp"]
    streak = user["streak"]
    last_completed = user["last_completed"]

    today = date.today()

    # Convert last_completed to date
    if last_completed:
        last_completed = date.fromisoformat(last_completed)

    gained_xp = int(request.form["xp"])
    xp += gained_xp

    if last_completed is None:
        streak = 1
    else:
        days_difference = (today - last_completed).days

        if days_difference == 1:
            streak += 1
        elif days_difference > 1:
            streak = 1

    conn.execute("""
        UPDATE user 
        SET xp = ?, streak = ?, last_completed = ?
        WHERE id = 1
    """, (xp, streak, today.isoformat()))

    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)