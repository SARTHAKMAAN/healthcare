from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import get_db_connection
import hashlib
from datetime import datetime
from ml_model import HealthModel

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['TEMPLATES_AUTO_RELOAD'] = True
health_model = HealthModel()

# Combined application routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('html_page'))  # Changed from dashboard to html_page
    return render_template('Home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('html_page'))  # Redirect to html.html if already logged in
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", "danger")
            return redirect(url_for('login'))
            
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM register WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['first_name'] = user.get('first_name', 'User')
                return redirect(url_for('html_page'))  # Redirect to html.html after login
            else:
                flash('Invalid email or password', 'danger')
        except Exception as e:
            flash(f"Login error: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('html_page'))  # Redirect to html.html if already logged in
        
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        dob = request.form.get('date_of_birth')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([first_name, last_name, email, dob, password, confirm_password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", "danger")
            return redirect(url_for('register'))
            
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM register WHERE email=%s", (email,))
            if cursor.fetchone():
                flash('Email already exists', 'danger')
                return redirect(url_for('register'))
            
            cursor.execute(
                """INSERT INTO register 
                (first_name, last_name, email, date_of_birth, password) 
                VALUES (%s, %s, %s, %s, %s)""",
                (first_name, last_name, email, dob, hashed_password)
            )
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash(f'Registration error: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

# New route to serve html.html
@app.route('/tracker')
def html_page():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    return render_template('tracker.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        data = request.json
        
        # Validate required fields
        required_fields = ['age', 'gender', 'weight', 'height', 'sleep', 
                         'exercise', 'stress', 'diet', 'water']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Convert data types
        input_data = {
            'age': int(data['age']),
            'gender': str(data['gender']),
            'weight': float(data['weight']),
            'height': float(data['height']),
            'sleep': float(data['sleep']),
            'exercise': int(data['exercise']),
            'stress': int(data['stress']),
            'diet': int(data['diet']),
            'water': int(data['water'])
        }
        
        # Get prediction
        result = health_model.predict_health(input_data)
        
        if not result:
            return jsonify({'error': 'Prediction failed'}), 500
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)