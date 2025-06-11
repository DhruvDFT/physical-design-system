#!/usr/bin/env python3
import os
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session

# Create Flask application
application = Flask(__name__)
app = application  # For compatibility

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'pd-interview-secret-2024')

# Global storage
users = {}
assignments = {}
counter = 0

# Initialize data
def init_data():
    global users
    users = {
        'admin': {
            'id': 'admin',
            'password': hashlib.sha256('Vibhuaya@3006'.encode()).hexdigest(),
            'is_admin': True,
            'name': 'Administrator'
        },
        'eng001': {
            'id': 'eng001',
            'password': hashlib.sha256('password123'.encode()).hexdigest(),
            'is_admin': False,
            'name': 'Alex Chen'
        },
        'eng002': {
            'id': 'eng002',
            'password': hashlib.sha256('password123'.encode()).hexdigest(),
            'is_admin': False,
            'name': 'Sarah Kumar'
        },
        'eng003': {
            'id': 'eng003',
            'password': hashlib.sha256('password123'.encode()).hexdigest(),
            'is_admin': False,
            'name': 'Mike Johnson'
        }
    }

# Questions
QUESTIONS = {
    'floorplanning': [
        'Describe your approach to macro placement in a 5mm x 5mm die with 70% utilization target.',
        'How would you resolve setup timing violations in a floorplan with randomly placed macros?',
        'What techniques would you use to reduce routing congestion in the center region?',
        'Explain floorplan strategy for a design with 2 voltage domains (0.9V core, 1.2V IO).',
        'How would you approach floorplanning for 3 clock domains at 800MHz, 400MHz, and 100MHz?',
        'What factors influence memory instance placement and how do you verify quality?',
        'Describe your approach to fix IR drop violations through floorplan changes.',
        'How would you reduce die area by 10% while maintaining timing?',
        'How do you handle mixed-signal block placement for noise isolation?',
        'What methods help estimate routing congestion during early floorplan?',
        'Explain partition-level floorplanning for hierarchical designs with 3 major blocks.',
        'How does DFT impact floorplan decisions for scan chain routing?',
        'Describe floorplan techniques for power gating and retention strategies.',
        'How do you plan floorplan flexibility for late ECOs?',
        'What validation checks indicate a good floorplan ready for placement?'
    ],
    'placement': [
        'How do you fix timing violations on 20 critical paths with -50ps slack?',
        'What placement adjustments improve routability in congested regions?',
        'How do you handle high-fanout nets (>500) during placement?',
        'Compare global vs detailed placement and when to iterate between them.',
        'What placement techniques reduce leakage power while maintaining timing?',
        'Describe placement strategy for multi-voltage designs with voltage islands.',
        'How do you address scattered hold violations without affecting setup?',
        'What tools help identify and fix long route placement issues?',
        'Explain optimal clock gating cell placement strategy.',
        'How does dual-mode operation affect placement strategy?',
        'Why is even cell density important and how do you achieve it?',
        'Describe placement optimization for multiple timing corners (SS, FF, TT).',
        'How do you place redundant logic to avoid common-mode failures?',
        'How do you balance area and timing optimization in placement?',
        'What placement techniques minimize crosstalk and noise issues?'
    ],
    'routing': [
        'How do you resolve 500 DRC violations (spacing, via, width) after global routing?',
        'Explain routing strategy for 10 differential pairs maintaining 100-ohm impedance.',
        'What causes timing degradation after routing and how do you recover it?',
        'What techniques achieve 100% routing in congested regions?',
        'Describe power/ground routing for adequate current capacity and low IR drop.',
        'How do layer constraints (no M1 routing) impact your routing strategy?',
        'What routing techniques minimize crosstalk on critical nets?',
        'Describe clock routing methodology and skew optimization.',
        'How do you address electromigration violations through routing changes?',
        'Explain challenges and solutions for double patterning constraints.',
        'What causes antenna violations and how do you prevent them?',
        'Describe ECO routing strategy to minimize disruption.',
        'How do you control routing parasitics to meet timing targets?',
        'What routing challenges are specific to 7nm/5nm nodes?',
        'Explain routing verification methodology for manufacturability.'
    ]
}

def create_assignment(engineer_id, topic):
    global counter
    counter += 1
    assignment_id = f'PD_{topic}_{engineer_id}_{counter}'
    
    assignments[assignment_id] = {
        'id': assignment_id,
        'engineer_id': engineer_id,
        'topic': topic,
        'questions': QUESTIONS[topic],
        'answers': {},
        'status': 'pending',
        'created': datetime.now().isoformat()[:10],
        'total_score': None
    }
    return assignment_id

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/admin' if session.get('is_admin') else '/student')
    return redirect('/login')

@app.route('/health')
def health():
    return 'OK'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = users.get(username)
        if user and user['password'] == hashlib.sha256(password.encode()).hexdigest():
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']
            session['name'] = user['name']
            return redirect('/admin' if user['is_admin'] else '/student')
        
        error_msg = '<div style="color:red;margin:10px 0;">Invalid credentials</div>'
    else:
        error_msg = ''
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>PD Interview System V7</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .login-box {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }}
        .logo {{
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 24px;
            font-weight: bold;
        }}
        h1 {{ color: #333; margin-bottom: 30px; }}
        input {{
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
        }}
        button {{
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            font-weight: bold;
        }}
        .demo {{
            background: #f0f8ff;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="login-box">
        <div class="logo">V7</div>
        <h1>PD Interview System</h1>
        <div class="demo">
            <strong>Demo Access:</strong><br>
            Admin: admin<br>
            Engineers: eng001, eng002, eng003<br>
            Password: As provided
        </div>
        {error_msg}
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>'''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect('/login')
    
    engineers = [u for u in users.values() if not u['is_admin']]
    all_assignments = list(assignments.values())
    submitted = [a for a in all_assignments if a['status'] == 'submitted']
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
        .card {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .stat {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 2em; color: #667eea; font-weight: bold; }}
        .form-row {{ display: flex; gap: 15px; align-items: end; }}
        .form-group {{ flex: 1; }}
        select, button {{ padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        button {{ background: #667eea; color: white; border: none; cursor: pointer; }}
        .assignment {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .btn {{ background: #28a745; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; }}
        .logout {{ float: right; color: white; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>V7 Admin Dashboard - {session['name']}
            <a href="/logout" class="logout">Logout</a>
        </h1>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{len(engineers)}</div>
                <div>Engineers</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(all_assignments)}</div>
                <div>Total Assignments</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(submitted)}</div>
                <div>Pending Review</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Create Assignment</h2>
            <form method="POST" action="/admin/create">
                <div class="form-row">
                    <div class="form-group">
                        <label>Engineer:</label>
                        <select name="engineer_id" required>
                            <option value="">Select...</option>
                            {''.join(f'<option value="{e["id"]}">{e["name"]} ({e["id"]})</option>' for e in engineers)}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Topic:</label>
                        <select name="topic" required>
                            <option value="">Select...</option>
                            <option value="floorplanning">Floorplanning</option>
                            <option value="placement">Placement</option>
                            <option value="routing">Routing</option>
                        </select>
                    </div>
                    <button type="submit">Create</button>
                </div>
            </form>
        </div>
        
        <div class="card">
            <h2>Pending Reviews</h2>
            {''.join(f'<div class="assignment"><strong>{a["id"]}</strong><br>Engineer: {a["engineer_id"]} | Topic: {a["topic"]}<br><a href="/admin/review/{a["id"]}" class="btn">Review</a></div>' for a in submitted) if submitted else '<p>No pending reviews</p>'}
        </div>
    </div>
</body>
</html>'''

@app.route('/admin/create', methods=['POST'])
def admin_create():
    if not session.get('is_admin'):
        return redirect('/login')
    
    engineer_id = request.form.get('engineer_id')
    topic = request.form.get('topic')
    
    if engineer_id in users and topic in QUESTIONS:
        create_assignment(engineer_id, topic)
    
    return redirect('/admin')

@app.route('/admin/review/<assignment_id>', methods=['GET', 'POST'])
def admin_review(assignment_id):
    if not session.get('is_admin'):
        return redirect('/login')
    
    assignment = assignments.get(assignment_id)
    if not assignment:
        return redirect('/admin')
    
    if request.method == 'POST':
        total = 0
        for i in range(15):
            score = int(request.form.get(f'score_{i}', 0))
            total += max(0, min(score, 10))
        
        assignment['total_score'] = total
        assignment['status'] = 'published'
        return redirect('/admin')
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Review Assignment</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #667eea; color: white; padding: 20px; border-radius: 10px; }}
        .question {{ background: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 8px; }}
        .answer {{ background: white; padding: 10px; margin: 10px 0; border-left: 4px solid #28a745; }}
        input[type="number"] {{ width: 60px; padding: 5px; }}
        button {{ background: #28a745; color: white; padding: 15px 30px; border: none; border-radius: 8px; }}
        .back {{ background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <a href="/admin" class="back">← Back</a>
    <div class="header">
        <h1>Review: {assignment_id}</h1>
    </div>
    
    <form method="POST">
        {''.join(f'<div class="question"><strong>Q{i+1}:</strong> {q}<br><div class="answer">Answer: {assignment.get("answers", {}).get(str(i), "No answer")}</div>Score: <input type="number" name="score_{i}" min="0" max="10" value="5" required></div>' for i, q in enumerate(assignment["questions"]))}
        <button type="submit">Submit Scores</button>
    </form>
</body>
</html>'''

@app.route('/student')
def student():
    if session.get('is_admin') or 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    my_assignments = [a for a in assignments.values() if a['engineer_id'] == user_id]
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Student Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 20px auto; padding: 0 20px; }}
        .card {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .assignment {{ border: 1px solid #ddd; padding: 20px; margin: 15px 0; border-radius: 8px; }}
        .status {{ padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }}
        .pending {{ background: #fff3cd; color: #856404; }}
        .submitted {{ background: #d1ecf1; color: #0c5460; }}
        .published {{ background: #d4edda; color: #155724; }}
        .btn {{ background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        .logout {{ float: right; color: white; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>V7 Student Dashboard - {session['name']}
            <a href="/logout" class="logout">Logout</a>
        </h1>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>My Assignments</h2>
            {''.join(f'<div class="assignment"><h3>{a["topic"].title()}</h3><p>ID: {a["id"]}</p><span class="status {a["status"]}">{a["status"].title()}</span>{"<p>Score: " + str(a.get("total_score", 0)) + "/150</p>" if a["status"] == "published" else ""}<br>{"<a href=\\"/student/assignment/" + a["id"] + "\\" class=\\"btn\\">Start</a>" if a["status"] == "pending" else ""}</div>' for a in my_assignments) if my_assignments else '<p>No assignments yet</p>'}
        </div>
    </div>
</body>
</html>'''

@app.route('/student/assignment/<assignment_id>', methods=['GET', 'POST'])
def student_assignment(assignment_id):
    if session.get('is_admin') or 'user_id' not in session:
        return redirect('/login')
    
    assignment = assignments.get(assignment_id)
    if not assignment or assignment['engineer_id'] != session['user_id']:
        return redirect('/student')
    
    if request.method == 'POST':
        answers = {}
        for i in range(15):
            answer = request.form.get(f'answer_{i}', '').strip()
            if answer:
                answers[str(i)] = answer
        
        if len(answers) == 15:
            assignment['answers'] = answers
            assignment['status'] = 'submitted'
        
        return redirect('/student')
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>{assignment["topic"].title()} Assignment</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #28a745; color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .question {{ background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        textarea {{ width: 100%; min-height: 100px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        button {{ background: #28a745; color: white; padding: 15px 30px; border: none; border-radius: 8px; width: 100%; }}
        .back {{ background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <a href="/student" class="back">← Back</a>
    <div class="header">
        <h1>{assignment["topic"].title()} Assessment</h1>
        <p>15 Questions - Answer all thoroughly</p>
    </div>
    
    <form method="POST">
        {''.join(f'<div class="question"><h3>Question {i+1}/15</h3><p>{q}</p><textarea name="answer_{i}" placeholder="Your answer..." required></textarea></div>' for i, q in enumerate(assignment["questions"]))}
        <button type="submit">Submit All Answers</button>
    </form>
</body>
</html>'''

# Initialize data
init_data()

# Run application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
