# app.py - Simplified PD Interview System (3 Questions for Testing)
import os
import hashlib
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pd-secret-2024')

# Simple password hashing (no werkzeug to avoid issues)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed, password):
    return hashed == hashlib.sha256(password.encode()).hexdigest()

# In-memory storage
users = {}
assignments = {}
notifications = {}
assignment_counter = 0
engineer_question_sets = {}

# Initialize users
def init_users():
    # Admin
    users['admin'] = {
        'id': 'admin',
        'username': 'admin',
        'password': hash_password('Vibhuaya@3006'),
        'is_admin': True,
        'experience_years': 3
    }
    
    # 5 Engineers
    for i in range(1, 6):
        user_id = f'eng00{i}'
        users[user_id] = {
            'id': user_id,
            'username': user_id,
            'password': hash_password('password123'),
            'is_admin': False,
            'experience_years': 3
        }

# Simplified question sets - 3 questions each
QUESTIONS_SET1 = {
    "floorplanning": [
        "You have a 5mm x 5mm die with 4 hard macros (each 1mm x 0.8mm) and need to achieve 70% utilization. Describe your macro placement strategy considering timing and power delivery.",
        "Your design has setup timing violations on paths crossing from left to right. The floorplan has macros placed randomly. How would you reorganize the floorplan to improve timing?",
        "During floorplan, you notice routing congestion in the center region. What are 3 specific techniques you would use to reduce congestion without major timing impact?"
    ],
    "placement": [
        "Your placement run shows timing violations on 20 critical paths with negative slack up to -50ps. Describe your systematic approach to fix these violations.",
        "You're seeing routing congestion hotspots after placement in 2-3 regions. What placement adjustments would you make to improve routability?",
        "Your design has high-fanout nets (>500 fanout) causing placement issues. How would you handle these nets during placement optimization?"
    ],
    "routing": [
        "After global routing, you have 500 DRC violations (spacing, via, width). Describe your systematic approach to resolve these violations efficiently.",
        "Your design has 10 differential pairs for high-speed signals. Explain your routing strategy to maintain 100-ohm impedance and minimize skew.",
        "You're seeing timing degradation after detailed routing compared to placement timing. What causes this and how would you recover the timing?"
    ]
}

# Copy Set1 as other sets for now (in real system, these would be different)
QUESTIONS_SET2 = QUESTIONS_SET1
QUESTIONS_SET3 = QUESTIONS_SET1
QUESTIONS_SET4 = QUESTIONS_SET1

QUESTION_SETS = [QUESTIONS_SET1, QUESTIONS_SET2, QUESTIONS_SET3, QUESTIONS_SET4]

# Keywords for auto-scoring
ANSWER_KEYWORDS = {
    "floorplanning": ["macro", "timing", "power", "congestion", "voltage", "clock", "memory", "IR drop", "area", "noise"],
    "placement": ["timing", "congestion", "fanout", "global", "leakage", "voltage", "hold", "density", "clock", "signal"],
    "routing": ["DRC", "differential", "timing", "congestion", "power", "layer", "crosstalk", "clock", "antenna", "ECO"]
}

# Helper functions
def get_questions_for_engineer(engineer_id, topic):
    """Get unique question set for engineer"""
    if engineer_id not in engineer_question_sets:
        engineer_num = int(engineer_id[-3:]) - 1
        set_index = engineer_num % len(QUESTION_SETS)
        engineer_question_sets[engineer_id] = set_index
    
    set_index = engineer_question_sets[engineer_id]
    return QUESTION_SETS[set_index][topic]

def calculate_auto_score(answer, topic):
    """Simple keyword-based scoring"""
    if not answer:
        return 0
    
    answer_lower = answer.lower()
    keywords_found = 0
    
    if topic in ANSWER_KEYWORDS:
        for keyword in ANSWER_KEYWORDS[topic]:
            if keyword.lower() in answer_lower:
                keywords_found += 1
    
    return min(keywords_found * 2, 10)  # 2 points per keyword, max 10

def create_assignment(engineer_id, topic):
    global assignment_counter
    
    user = users.get(engineer_id)
    if not user or topic not in QUESTIONS_SET1:
        return None
    
    assignment_counter += 1
    assignment_id = f"PD_{topic.upper()}_{engineer_id}_{assignment_counter}"
    
    questions = get_questions_for_engineer(engineer_id, topic)
    
    assignment = {
        'id': assignment_id,
        'engineer_id': engineer_id,
        'topic': topic,
        'questions': questions,
        'answers': {},
        'auto_scores': {},
        'final_scores': {},
        'status': 'pending',
        'created_date': datetime.now().isoformat(),
        'due_date': (datetime.now() + timedelta(days=3)).isoformat(),
        'total_score': None,
        'scored_by': None,
        'scored_date': None,
        'published_date': None
    }
    
    assignments[assignment_id] = assignment
    
    # Create notification
    if engineer_id not in notifications:
        notifications[engineer_id] = []
    
    notifications[engineer_id].append({
        'title': f'New {topic} Assignment',
        'message': f'3 questions for 3+ years experience, due in 3 days',
        'created_at': datetime.now().isoformat()
    })
    
    return assignment

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        if session.get('is_admin'):
            return redirect('/admin')
        else:
            return redirect('/student')
    return redirect('/login')

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
            
            if user.get('is_admin'):
                return redirect('/admin')
            else:
                return redirect('/student')
        else:
            error = 'Invalid credentials'
    
    # Simple login page
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - PD Interview System</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                background: #1a1a2e; 
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .login-box {{
                background: #16213e;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.5);
                width: 350px;
            }}
            h1 {{ text-align: center; color: #4CAF50; }}
            input {{ 
                width: 100%; 
                padding: 10px; 
                margin: 10px 0;
                border: 1px solid #444;
                background: #0f3460;
                color: white;
                border-radius: 5px;
            }}
            button {{
                width: 100%;
                padding: 12px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }}
            button:hover {{ background: #45a049; }}
            .info {{ 
                background: rgba(76, 175, 80, 0.1); 
                padding: 15px; 
                border-radius: 5px;
                margin: 15px 0;
                font-size: 14px;
            }}
            .error {{ color: #ff5252; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="login-box">
            <h1>🎯 PD Interview System</h1>
            <p style="text-align: center;">3 Questions Assessment (Test Mode)</p>
            
            <div class="info">
                <strong>Test Login Credentials:</strong><br>
                Admin: admin / Vibhuaya@3006<br>
                Engineers: eng001 to eng005 / password123
            </div>
            
            {f'<div class="error">{error}</div>' if error else ''}
            
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">LOGIN</button>
            </form>
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')
    
    engineers = [u for u in users.values() if not u.get('is_admin')]
    all_assignments = list(assignments.values())
    submitted = [a for a in all_assignments if a['status'] == 'submitted']
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                background: #f5f5f5; 
                margin: 0;
            }}
            .header {{
                background: #4caf50;
                color: white;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 20px auto;
                padding: 0 20px;
            }}
            .card {{
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin: 20px 0;
            }}
            .stat {{
                background: #4CAF50;
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }}
            .stat h2 {{ margin: 0; font-size: 36px; }}
            button {{
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            select, input {{
                padding: 8px;
                margin: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{ background: #f5f5f5; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Admin Dashboard - {session['username']} 
                <a href="/logout" style="float: right; color: white;">Logout</a>
            </h1>
        </div>
        
        <div class="container">
            <div class="stats">
                <div class="stat">
                    <h2>{len(engineers)}</h2>
                    <p>Engineers</p>
                </div>
                <div class="stat">
                    <h2>{len(all_assignments)}</h2>
                    <p>Assignments</p>
                </div>
                <div class="stat">
                    <h2>{len(submitted)}</h2>
                    <p>Submitted</p>
                </div>
                <div class="stat">
                    <h2>9</h2>
                    <p>Questions/Topic</p>
                </div>
            </div>
            
            <div class="card">
                <h2>Create Assignment</h2>
                <form method="POST" action="/admin/create">
                    <select name="engineer_id" required>
                        <option value="">Select Engineer...</option>
    '''
    
    for eng in engineers:
        html += f'<option value="{eng["id"]}">{eng["username"]}</option>'
    
    html += '''
                    </select>
                    <select name="topic" required>
                        <option value="">Select Topic...</option>
                        <option value="floorplanning">Floorplanning</option>
                        <option value="placement">Placement</option>
                        <option value="routing">Routing</option>
                    </select>
                    <button type="submit">Create Assignment</button>
                </form>
            </div>
            
            <div class="card">
                <h2>Submitted Assignments</h2>
    '''
    
    if submitted:
        for a in submitted:
            html += f'''
                <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
                    <strong>{a["id"]}</strong> - {a["engineer_id"]} - {a["topic"]}<br>
                    <small>Submitted: {a.get("submitted_date", "Unknown")}</small><br>
                    <a href="/admin/review/{a["id"]}"><button>Review & Score</button></a>
                </div>
            '''
    else:
        html += '<p>No assignments submitted yet</p>'
    
    html += '''
            </div>
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/admin/create', methods=['POST'])
def admin_create():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')
    
    engineer_id = request.form.get('engineer_id')
    topic = request.form.get('topic')
    
    if engineer_id and topic:
        create_assignment(engineer_id, topic)
    
    return redirect('/admin')

@app.route('/admin/review/<assignment_id>', methods=['GET', 'POST'])
def admin_review(assignment_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')
    
    assignment = assignments.get(assignment_id)
    if not assignment:
        return redirect('/admin')
    
    if request.method == 'POST':
        # Save scores
        total_score = 0
        for i in range(3):  # Changed from 15 to 3
            score = request.form.get(f'score_{i}', '0')
            try:
                total_score += int(score)
            except:
                pass
        
        assignment['total_score'] = total_score
        assignment['status'] = 'published'
        assignment['scored_by'] = session['username']
        assignment['scored_date'] = datetime.now().isoformat()
        
        return redirect('/admin')
    
    # Show review form
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Review Assignment</title>
        <style>
            body {{ font-family: Arial; margin: 20px; }}
            .question {{ 
                background: #f5f5f5; 
                padding: 15px; 
                margin: 10px 0;
                border-left: 4px solid #4CAF50;
            }}
            .answer {{ 
                background: white; 
                padding: 10px; 
                margin: 10px 0;
                border: 1px solid #ddd;
            }}
            input[type="number"] {{ width: 60px; }}
            button {{ background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Review Assignment: {assignment_id}</h1>
        <p><strong>Engineer:</strong> {assignment["engineer_id"]} | <strong>Topic:</strong> {assignment["topic"]}</p>
        <form method="POST">
    '''
    
    for i, question in enumerate(assignment['questions']):
        answer = assignment.get('answers', {}).get(str(i), 'No answer')
        auto_score = calculate_auto_score(answer, assignment['topic'])
        
        html += f'''
            <div class="question">
                <strong>Q{i+1}:</strong> {question}
                <div class="answer">
                    <strong>Answer:</strong> {answer}
                </div>
                <p>Auto-score: {auto_score}/10 | 
                   Your Score: <input type="number" name="score_{i}" min="0" max="10" value="{auto_score}">
                </p>
            </div>
        '''
    
    html += '''
            <button type="submit">Submit Scores & Publish Results</button>
            <a href="/admin" style="margin-left: 10px;"><button type="button">Back to Dashboard</button></a>
        </form>
    </body>
    </html>
    '''
    return html

@app.route('/student')
def student_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    my_assignments = [a for a in assignments.values() if a['engineer_id'] == user_id]
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Dashboard</title>
        <style>
            body {{ font-family: Arial; margin: 0; background: #f5f5f5; }}
            .header {{ background: #2196F3; color: white; padding: 20px; }}
            .container {{ max-width: 1000px; margin: 20px auto; padding: 0 20px; }}
            .card {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            button {{ background: #2196F3; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
            .status-pending {{ color: #ff9800; font-weight: bold; }}
            .status-submitted {{ color: #4caf50; font-weight: bold; }}
            .status-published {{ color: #2196f3; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Student Dashboard - {session['username']} 
                <a href="/logout" style="float: right; color: white;">Logout</a>
            </h1>
        </div>
        
        <div class="container">
            <h2>My Assignments (3 Questions Each)</h2>
    '''
    
    for a in my_assignments:
        status = a['status']
        status_class = f'status-{status}'
        html += f'''
            <div class="card">
                <h3>{a["topic"].title()} Assignment</h3>
                <p>Status: <span class="{status_class}">{status.upper()}</span> | Due: {a["due_date"][:10]}</p>
        '''
        
        if status == 'published':
            html += f'<p><strong>Score: {a["total_score"]}/30</strong> (Scored by: {a.get("scored_by", "Admin")})</p>'
        elif status == 'submitted':
            html += '<p>Assignment submitted. Waiting for admin review.</p>'
        elif status == 'pending':
            html += f'<a href="/student/assignment/{a["id"]}"><button>Take Assignment (3 Questions)</button></a>'
        
        html += '</div>'
    
    if not my_assignments:
        html += '<div class="card"><p>No assignments yet. Please wait for admin to create assignments.</p></div>'
    
    html += '''
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/student/assignment/<assignment_id>', methods=['GET', 'POST'])
def student_assignment(assignment_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    assignment = assignments.get(assignment_id)
    if not assignment or assignment['engineer_id'] != session['user_id']:
        return redirect('/student')
    
    if request.method == 'POST' and assignment['status'] == 'pending':
        # Save answers
        answers = {}
        for i in range(3):  # Changed from 15 to 3
            answer = request.form.get(f'answer_{i}', '').strip()
            if answer:
                answers[str(i)] = answer
        
        if len(answers) == 3:  # Changed from 15 to 3
            assignment['answers'] = answers
            assignment['status'] = 'submitted'
            assignment['submitted_date'] = datetime.now().isoformat()
        
        return redirect('/student')
    
    # Show assignment
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{assignment["topic"].title()} Assignment</title>
        <style>
            body {{ font-family: Arial; margin: 20px; }}
            .question {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #2196F3; }}
            textarea {{ width: 100%; min-height: 100px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
            button {{ background: #2196F3; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
            .header {{ background: #2196F3; color: white; padding: 15px; margin: -20px -20px 20px -20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{assignment["topic"].title()} Assignment</h1>
            <p>3 Questions | Due: {assignment["due_date"][:10]}</p>
        </div>
        
        <form method="POST">
    '''
    
    for i, question in enumerate(assignment['questions']):
        html += f'''
            <div class="question">
                <strong>Question {i+1} of 3:</strong><br>
                {question}<br><br>
                <textarea name="answer_{i}" required placeholder="Type your detailed answer here..."></textarea>
            </div>
        '''
    
    html += '''
            <button type="submit">Submit All Answers</button>
            <p><small>Note: Make sure to answer all 3 questions before submitting. You cannot edit after submission.</small></p>
        </form>
    </body>
    </html>
    '''
    return html

# Initialize
init_users()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
