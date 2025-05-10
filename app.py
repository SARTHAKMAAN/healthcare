
from flask import Flask, render_template, request, redirect, session
from utils.db import get_db_connection 
import mysql.connector
import hashlib
from datetime import date

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'



@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/log')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = get_db_connection()
    if not conn:
        return "Database connection failed"
    cursor = conn.cursor(dictionary=True)
    

    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            return redirect('/log')
        else:
            return "Invalid credentials"

    return render_template('login.html')
     

@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return redirect('/login')

    return render_template('register.html')

@app.route('/log', methods=['GET', 'POST'])
def log():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        steps = request.form['steps']
        sleep = request.form['sleep']
        water = request.form['water']
        calories = request.form['calories']
        mood = request.form['mood']

        cursor.execute("""INSERT INTO daily_logs (user_id, log_date, steps, sleep_hours, water_intake, calories, mood)
                          VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                       (session['user_id'], date.today(), steps, sleep, water, calories, mood))
        conn.commit()
        return "Log saved successfully!"

    return render_template('form.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
   app.run(debug=True, host='127.0.0.1', port=5000)


    
