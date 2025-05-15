
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Mock database (replace with your actual database)
users = {}

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users:
            flash('Username already exists', 'danger')
        else:
            users[username] = {
                'password': generate_password_hash(password)
            }
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')
@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'username' not in session:  # Add this check
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Get form data
            steps = request.form['steps']
            sleep = request.form['sleep']
            water = request.form['water']
            calories = request.form['calories']
            mood = request.form['mood']
            
            # Validate data
            if not all([steps, sleep, water, calories, mood]):
                flash('Please fill all fields', 'error')
                return redirect(url_for('form'))
            
            # Save to database (example using SQLite)
            conn = sqlite3.connect('health.db')
            c = conn.cursor()
            c.execute('''INSERT INTO health_data 
                        (username, steps, sleep, water, calories, mood, date) 
                        VALUES (?,?,?,?,?,?,?)''',
                     (session['username'], steps, sleep, water, calories, mood, datetime.now()))
            conn.commit()
            conn.close()
            
            flash('Data saved successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Error saving data: {str(e)}', 'error')
            return redirect(url_for('form'))
    
    return render_template('form.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)


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



