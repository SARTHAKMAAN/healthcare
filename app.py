from flask import Flask, render_template, request, redirect, session, url_for, flash
from utils.db import get_db_connection
import hashlib
from datetime import date

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this!

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('form'))
    return render_template('Home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        dob = request.form['dob']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        agreed = request.form.get('agreed_to_terms') == 'on'

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed", "danger")
            return redirect(url_for('register'))
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            flash("Email already registered", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for('register'))

        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, date_of_birth, password, agreed_to_terms)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, email, dob, password, agreed))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        print("User already logged in, redirecting to form...")
        return redirect(url_for('form'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        print(f"Attempt login with email: {email}")

        conn = get_db_connection()
        if conn is None:
            print("Database connection failed")
            flash("Database connection failed", "danger")
            return redirect(url_for('login'))
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            print("User found! Setting session and redirecting...")
            session['user_id'] = user['id']
            flash("Logged in successfully!", "success")
            return redirect(url_for('form'))
        else:
            print("Invalid login credentials")
            flash("Invalid email or password", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        steps = request.form['steps']
        sleep = request.form['sleep']
        water = request.form['water']
        calories = request.form['calories']
        mood = request.form['mood']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO daily_logs (user_id, log_date, steps, sleep_hours, water_intake, calories, mood)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], date.today(), steps, sleep, water, calories, mood))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Data saved successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('form.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
