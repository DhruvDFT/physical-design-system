```python
import os
import uuid
import hashlib
import random
import logging
from flask import Flask, request, session, redirect

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pd-secret-2024')

# In-memory data stores
users = {}
assignments = {}
notifications = {}
assignment_counter = 0

# Simple password hashing using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed, password):
    return hashed == hashlib.sha256(password.encode()).hexdigest()

# Initialize default users
def init_users():
    # Admin user (password hidden)
    users['admin'] = {
        'id': 'admin',
        'username': 'admin',
        # 'password': hash_password('Vibhuaya@3006'),  # Admin password commented out
        'is_admin': True,
        'experience_years': 3
    }
    # Engineer users
    for i in range(1, 6):
        user_id = f'eng00{i}'
        users[user_id] = {
            'id': user_id,
            'username': user_id,
            'password': hash_password('password123'),
            'is_admin': False,
            'experience_years': 3
        }

# Sample question sets: 4 sets, each with 3 categories of 15 questions
QUESTION_SETS = {
    1: {
        "floorplanning": [
            "You have a 5mm x 5mm die with 4 hard macros (each 1mm x 1mm). What's your macro placement strategy considering timing and power delivery?",
            # ... (14 more questions) 
        ],
        "placement": [
            "Describe your approach to placement optimization for design corners (SS, FF, TT). How do you ensure all corners meet timing?",
            # ... (14 more questions)
        ],
        "routing": [
            "After global routing, you have 500 DRC violations. What's your systematic approach to resolve these violations efficiently?",
            # ... (14 more questions)
        ],
    },
    2: {
        "floorplanning": [
            # ... 15 questions
        ],
        "placement": [
            # ... 15 questions
        ],
        "routing": [
            # ... 15 questions
        ],
    },
    3: {
        "floorplanning": [
            # ... 15 questions
        ],
        "placement": [
            # ... 15 questions
        ],
        "routing": [
            # ... 15 questions
        ],
    },
    4: {
        "floorplanning": [
            # ... 15 questions
        ],
        "placement": [
            # ... 15 questions
        ],
        "routing": [
            # ... 15 questions
        ],
    }
}

# Keywords for auto-scoring
KEYWORDS = ["placement", "timing", "power", "congestion", "skew", "routing", "DRC", "voltage"]

def calculate_auto_score(answer_text):
    """
    Simple heuristic: +1 for each keyword found (case-insensitive), capped to len(KEYWORDS).
    """
    score = sum(1 for kw in KEYWORDS if kw.lower() in answer_text.lower())
    return min(score, len(KEYWORDS))

# Assignment creation logic
def create_assignment(engineer_id):
    global assignment_counter
    assignment_counter += 1
    # Randomly select one of the question sets
    selected_set = QUESTION_SETS[random.randint(1, len(QUESTION_SETS))]
    assignment = {
        'id': str(assignment_counter),
        'engineer_id': engineer_id,
        'questions': selected_set,
        'status': 'pending',
        'score': None,
        'answers': None
    }
    assignments[assignment['id']] = assignment
    return assignment

# Flask routes
@app.route('/health')
def health():
    return 'OK', 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users.get(username)
        if user and check_password(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user.get('is_admin', False)
            return redirect('/admin' if user.get('is_admin') else '/student')
        else:
            error = 'Invalid credentials'
    return f"""
    <html><body>
      <h2>Login</h2>
      <form method='POST'>
        <input name='username' placeholder='Username' required />
        <input type='password' name='password' placeholder='Password' required />
        <button type='submit'>Login</button>
      </form>
      <p style='color:red;'>{error or ''}</p>
    </body></html>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect('/login')
    engineers = [u for u in users.values() if not u['is_admin']]
    all_assigns = assignments.values()
    return f"<html><body><h1>Admin Dashboard</h1>{len(engineers)} engineers, {len(all_assigns)} assignments</body></html>"

@app.route('/admin/create', methods=['POST'])
def admin_create():
    if not session.get('is_admin'):
        return redirect('/login')
    engineer_id = request.form.get('engineer_id')
    create_assignment(engineer_id)
    return redirect('/admin')

@app.route('/admin/review/<assignment_id>', methods=['GET', 'POST'])
def admin_review(assignment_id):
    if not session.get('is_admin'):
        return redirect('/login')
    assignment = assignments.get(assignment_id)
    if request.method == 'POST':
        score = int(request.form.get('manual_score', 0))
        assignment['score'] = score
        assignment['status'] = 'reviewed'
        return redirect('/admin')
    return f"<html><body><h2>Review {assignment_id}</h2>Current status: {assignment['status']}</body></html>"

@app.route('/student')
def student_dashboard():
    if session.get('is_admin') or 'user_id' not in session:
        return redirect('/login')
    sid = session['user_id']
    pending = [a for a in assignments.values() if a['engineer_id'] == sid and a['status']=='pending']
    links = ''.join(f"<p><a href='/student/assignment/{a['id']}'>Assignment {a['id']}</a></p>" for a in pending)
    return f"<html><body><h1>Your Assignments</h1>{links}</body></html>"

@app.route('/student/assignment/<assignment_id>', methods=['GET', 'POST'])
def student_assignment(assignment_id):
    if session.get('is_admin') or 'user_id' not in session:
        return redirect('/login')
    assignment = assignments.get(assignment_id)
    if request.method == 'POST':
        answers = {q: request.form.get(str(idx), '') for idx, q in enumerate(assignment['questions']['floorplanning'], 1)}
        score = calculate_auto_score(' '.join(answers.values()))
        assignment.update({'answers': answers, 'score': score, 'status': 'submitted'})
        return redirect('/student')
    form_fields = ''.join(f"<p>Q{idx}: {q}</p><textarea name='{idx}'></textarea>" for idx, q in enumerate(assignment['questions']['floorplanning'], 1))
    return f"<html><body><h2>Assignment {assignment_id}</h2><form method='POST'>{form_fields}<button>Submit</button></form></body></html>"

# Entry point
if __name__ == '__main__':
    init_users()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

