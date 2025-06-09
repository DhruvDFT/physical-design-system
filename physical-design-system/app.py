# app.py - PD Interview System (No Werkzeug)
import os
import hashlib
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'pd-secret-2024'

# Simple password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed, password):
    return hashed == hashlib.sha256(password.encode()).hexdigest()

# Storage
users = {
    'admin': {
        'username': 'admin',
        'password': hash_password('Vibhuaya@3006'),
        'is_admin': True
    },
    'eng001': {
        'username': 'eng001',
        'password': hash_password('password123'),
        'is_admin': False
    }
}

assignments = {}

# Simple questions (just 3 for testing)
QUESTIONS = {
    "floorplanning": [
        "Q1: Describe macro placement strategy",
        "Q2: Fix timing violations in floorplan",
        "Q3: Reduce routing congestion"
    ]
}

@app.route('/')
def home():
    if 'username' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/health')
def health():
    return 'OK'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users.get(username)
        if user and check_password(user['password'], password):
            session['username'] = username
            session['is_admin'] = user['is_admin']
            return redirect('/dashboard')
    
    return '''
    <html>
    <head><title>Login - PD System</title></head>
    <body style="font-family: Arial; max-width: 400px; margin: 50px auto;">
        <h2>PD Interview System Login</h2>
        <p>Admin: admin / Vibhuaya@3006<br>Student: eng001 / password123</p>
        <form method="POST">
            <p>Username: <input name="username" required></p>
            <p>Password: <input type="password" name="password" required></p>
            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    
    return f'''
    <html>
    <head><title>Dashboard</title></head>
    <body style="font-family: Arial; max-width: 800px; margin: 50px auto;">
        <h1>Welcome {session['username']}</h1>
        <p>Role: {'Admin' if session.get('is_admin') else 'Student'}</p>
        <p>System Status: Working ✓</p>
        <a href="/logout">Logout</a>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
