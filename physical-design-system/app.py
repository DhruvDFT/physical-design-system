# app.py - Deployment-Ready PD Interview System V7
import os
import hashlib
import json
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session

# Initialize Flask app with minimal configuration
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pd-v7-secret-key-2024')

# Simple password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed, password):
    return hashed == hashlib.sha256(password.encode()).hexdigest()

# In-memory storage
users = {}
assignments = {}
notifications = {}
assignment_counter = 0

# Initialize users
def init_users():
    # Admin user
    users['admin'] = {
        'id': 'admin',
        'username': 'admin',
        'password': hash_password('Vibhuaya@3006'),
        'is_admin': True,
        'display_name': 'Administrator',
        'department': 'Management'
    }
    
    # Engineering users
    names = ['Alex Chen', 'Sarah Kumar', 'Mike Johnson', 'Priya Singh', 'David Liu']
    for i in range(1, 6):
        user_id = f'eng00{i}'
        users[user_id] = {
            'id': user_id,
            'username': user_id,
            'password': hash_password('password123'),
            'is_admin': False,
            'display_name': names[i-1],
            'department': 'Physical Design'
        }

# Questions data
QUESTIONS = {
    "floorplanning": [
        "You have a 5mm x 5mm die with 4 hard macros (each 1mm x 0.8mm) and need to achieve 70% utilization. Describe your macro placement strategy considering timing and power delivery.",
        "Your design has setup timing violations on paths crossing from left to right. The floorplan has macros placed randomly. How would you reorganize the floorplan to improve timing?",
        "During floorplan, you notice routing congestion in the center region. What are 3 specific techniques you would use to reduce congestion without major timing impact?",
        "You're working with a design that has 2 voltage domains (0.9V core, 1.2V IO). Explain how you would plan the floorplan to minimize level shifter count and power grid complexity.",
        "Your design has 3 clock domains running at 800MHz, 400MHz, and 100MHz. How would you approach floorplanning to minimize clock tree power and skew?",
        "You need to place 8 memory instances in your design. What factors would you consider for their placement, and how would you verify the floorplan quality?",
        "Your floorplan review shows IR drop violations in certain regions. Describe your approach to fix this through floorplan changes and power grid improvements.",
        "You're told to reduce die area by 10% while maintaining timing. What floorplan modifications would you make and what risks would you monitor?",
        "Your design has mixed-signal blocks that need isolation from digital switching noise. How would you handle their placement and what guard techniques would you use?",
        "During early floorplan, how would you estimate routing congestion and what tools/techniques help predict routability issues?",
        "You have a hierarchical design with 3 major blocks. Explain your approach to partition-level floorplanning and interface planning between blocks.",
        "Your design requires scan chains for testing. How does DFT impact your floorplan decisions and what considerations are important for scan routing?",
        "You're working on a power-sensitive design. Describe floorplan techniques to enable effective power gating and retention strategies.",
        "Your floorplan needs to accommodate late ECOs (Engineering Change Orders). How would you plan for flexibility and what areas would you keep available?",
        "Explain your methodology for floorplan validation - what checks would you run and what metrics indicate a good floorplan ready for placement?"
    ],
    "placement": [
        "Your placement run shows timing violations on 20 critical paths with negative slack up to -50ps. Describe your systematic approach to fix these violations.",
        "You're seeing routing congestion hotspots after placement in 2-3 regions. What placement adjustments would you make to improve routability?",
        "Your design has high-fanout nets (>500 fanout) causing placement issues. How would you handle these nets during placement optimization?",
        "Compare global placement vs detailed placement - what specific problems does each solve and when would you iterate between them?",
        "Your placement shows leakage power higher than target. What placement techniques would you use to reduce power while maintaining timing?",
        "You have a multi-voltage design with voltage islands. Describe your placement strategy for cells near domain boundaries and level shifter placement.",
        "Your timing report shows hold violations scattered across the design. How would you address this through placement without affecting setup timing?",
        "During placement, you notice that certain instances are creating long routes. What tools and techniques help identify and fix such placement issues?",
        "Your design has clock gating cells. Explain their optimal placement strategy and impact on both power and timing.",
        "You're working with a design that has both high-performance and low-power modes. How does this affect your placement strategy?",
        "Your placement review shows uneven cell density distribution. Why is this problematic and how would you achieve better density distribution?",
        "Describe your approach to placement optimization for designs with multiple timing corners (SS, FF, TT). How do you ensure all corners meet timing?",
        "Your design has redundant logic for reliability. How would you place redundant instances to avoid common-mode failures?",
        "You need to optimize placement for both area and timing. Describe the trade-offs and how you would balance these competing requirements.",
        "Explain how placement impacts signal integrity. What placement techniques help minimize crosstalk and noise issues?"
    ],
    "routing": [
        "After global routing, you have 500 DRC violations (spacing, via, width). Describe your systematic approach to resolve these violations efficiently.",
        "Your design has 10 differential pairs for high-speed signals. Explain your routing strategy to maintain 100-ohm impedance and minimize skew.",
        "You're seeing timing degradation after detailed routing compared to placement timing. What causes this and how would you recover the timing?",
        "Your router is struggling with congestion in certain regions leading to routing non-completion. What techniques would you use to achieve 100% routing?",
        "Describe your approach to power/ground routing. How do you ensure adequate current carrying capacity and low IR drop?",
        "Your design has specific layer constraints (e.g., no routing on M1 except for local connections). How does this impact your routing strategy?",
        "You have crosstalk violations on critical nets. Explain your routing techniques to minimize crosstalk and meet noise requirements.",
        "Your clock nets require special routing with controlled skew. Describe clock routing methodology and skew optimization techniques.",
        "During routing, some nets are showing electromigration violations. How would you address current density issues through routing changes?",
        "You need to route in a design with double patterning constraints. Explain the challenges and your approach to handle decomposition issues.",
        "Your design has antenna violations after routing. What causes these and what routing techniques help prevent antenna issues?",
        "Describe your ECO (Engineering Change Order) routing strategy. How do you minimize disruption to existing clean routing?",
        "Your timing closure requires specific net delays. How do you control routing parasitics to meet timing targets?",
        "You're working with advanced technology nodes (7nm/5nm). What routing challenges are specific to these nodes and how do you address them?",
        "Explain your routing verification methodology. What checks ensure your routing is manufacturable and reliable?"
    ]
}

# Keyword scoring
KEYWORDS = {
    "floorplanning": ["macro", "timing", "power", "congestion", "voltage", "clock", "memory", "IR drop", "area", "noise"],
    "placement": ["timing", "congestion", "fanout", "global", "leakage", "voltage", "hold", "density", "clock", "signal"],
    "routing": ["DRC", "differential", "timing", "congestion", "power", "layer", "crosstalk", "clock", "antenna", "ECO"]
}

def calculate_score(answer, topic):
    if not answer:
        return 0
    answer_lower = answer.lower()
    score = 0
    for keyword in KEYWORDS.get(topic, []):
        if keyword.lower() in answer_lower:
            score += 1
    return min(score * 2, 10)

def create_assignment(engineer_id, topic):
    global assignment_counter
    assignment_counter += 1
    
    assignment_id = f"V7_PD_{topic.upper()}_{engineer_id}_{assignment_counter:03d}"
    
    assignment = {
        'id': assignment_id,
        'engineer_id': engineer_id,
        'topic': topic,
        'questions': QUESTIONS[topic],
        'answers': {},
        'status': 'pending',
        'created_date': datetime.now().isoformat(),
        'due_date': (datetime.now() + timedelta(days=3)).isoformat(),
        'total_score': None,
        'scored_by': None
    }
    
    assignments[assignment_id] = assignment
    return assignment

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/admin' if session.get('is_admin') else '/student')
    return redirect('/login')

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = users.get(username)
        if user and check_password(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['display_name'] = user['display_name']
            session['is_admin'] = user.get('is_admin', False)
            
            return redirect('/admin' if user.get('is_admin') else '/student')
        else:
            error = 'Invalid credentials'
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>V7 PD Interview System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .login-box {{
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }}
        .logo {{
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            color: white;
            font-size: 24px;
            font-weight: 900;
        }}
        h1 {{ margin-bottom: 10px; color: #333; font-size: 24px; }}
        .subtitle {{ color: #666; margin-bottom: 30px; }}
        .demo-info {{
            background: #f0f8ff;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 14px;
            text-align: left;
        }}
        input {{
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }}
        input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        button {{
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        button:hover {{ transform: translateY(-2px); }}
        .error {{
            background: #fee;
            color: #c33;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="login-box">
        <div class="logo">V7</div>
        <h1>PD Interview System</h1>
        <p class="subtitle">Physical Design Assessment Platform</p>
        
        <div class="demo-info">
            <strong>Demo Access:</strong><br>
            Admin: admin / [as provided]<br>
            Engineers: eng001-eng005 / password123
        </div>
        
        {f'<div class="error">{error}</div>' if error else ''}
        
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
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')
    
    engineers = [u for u in users.values() if not u.get('is_admin')]
    all_assignments = list(assignments.values())
    submitted = [a for a in all_assignments if a['status'] == 'submitted']
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>V7 Admin Dashboard</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', sans-serif; 
            background: #f5f5f5; 
            margin: 0;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo {{ 
            display: flex; 
            align-items: center; 
            gap: 15px; 
            font-size: 24px; 
            font-weight: 700; 
        }}
        .v7-logo {{
            width: 40px;
            height: 40px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
        }}
        .logout {{ color: white; text-decoration: none; padding: 8px 16px; background: rgba(255,255,255,0.1); border-radius: 5px; }}
        .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .card {{ background: white; padding: 25px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .form-row {{ display: flex; gap: 15px; align-items: end; }}
        .form-group {{ flex: 1; }}
        .form-group label {{ display: block; margin-bottom: 5px; font-weight: 500; }}
        select {{ padding: 10px; border: 1px solid #ddd; border-radius: 5px; width: 100%; }}
        .btn {{ background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
        .assignment {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; background: #f9f9f9; }}
        .btn-review {{ background: #28a745; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; }}
        @media (max-width: 768px) {{
            .form-row {{ flex-direction: column; }}
            .header {{ flex-direction: column; gap: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <div class="v7-logo">V7</div>
            Admin Dashboard - {session['display_name']}
        </div>
        <a href="/logout" class="logout">Logout</a>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{len(engineers)}</div>
                <div>Engineers</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(all_assignments)}</div>
                <div>Assignments</div>
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
                        <label>Engineer</label>
                        <select name="engineer_id" required>
                            <option value="">Select Engineer...</option>
                            {''.join(f'<option value="{e["id"]}">{e["display_name"]} ({e["id"]})</option>' for e in engineers)}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Topic</label>
                        <select name="topic" required>
                            <option value="">Select Topic...</option>
                            <option value="floorplanning">Floorplanning</option>
                            <option value="placement">Placement</option>
                            <option value="routing">Routing</option>
                        </select>
                    </div>
                    <button type="submit" class="btn">Create</button>
                </div>
            </form>
        </div>
        
        <div class="card">
            <h2>Pending Reviews</h2>
            {''.join(f'''
            <div class="assignment">
                <strong>{a["id"]}</strong><br>
                Engineer: {a["engineer_id"]} | Topic: {a["topic"]}<br>
                <a href="/admin/review/{a["id"]}" class="btn-review">Review</a>
            </div>
            ''' for a in submitted) if submitted else '<p>No pending reviews</p>'}
        </div>
    </div>
</body>
</html>'''

@app.route('/admin/create', methods=['POST'])
def admin_create():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')
    
    engineer_id = request.form.get('engineer_id')
    topic = request.form.get('topic')
    
    if engineer_id and topic and engineer_id in users and topic in QUESTIONS:
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
        total_score = 0
        for i in range(15):
            score = int(request.form.get(f'score_{i}', 0))
            total_score += max(0, min(score, 10))
        
        assignment['total_score'] = total_score
        assignment['status'] = 'published'
        assignment['scored_by'] = session['display_name']
        
        return redirect('/admin')
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Review Assignment</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; }}
        .header {{ background: #667eea; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .question {{ background: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 8px; }}
        .answer {{ background: white; padding: 10px; margin: 10px 0; border-left: 4px solid #28a745; }}
        .score {{ display: flex; align-items: center; gap: 10px; margin-top: 10px; }}
        input[type="number"] {{ width: 60px; padding: 5px; }}
        .btn {{ background: #28a745; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; }}
        .back {{ background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <a href="/admin" class="back">← Back</a>
    <div class="header">
        <h1>Review: {assignment_id}</h1>
        <p>Engineer: {assignment["engineer_id"]} | Topic: {assignment["topic"]}</p>
    </div>
    
    <form method="POST">
        {''.join(f'''
        <div class="question">
            <strong>Q{i+1}:</strong> {q}<br>
            <div class="answer">
                <strong>Answer:</strong> {assignment.get("answers", {}).get(str(i), "No answer")}
            </div>
            <div class="score">
                Auto: {calculate_score(assignment.get("answers", {}).get(str(i), ""), assignment["topic"])}/10
                | Your Score: <input type="number" name="score_{i}" min="0" max="10" value="{calculate_score(assignment.get("answers", {}).get(str(i), ""), assignment["topic"])}" required>
            </div>
        </div>
        ''' for i, q in enumerate(assignment["questions"]))}
        
        <button type="submit" class="btn">Submit Scores</button>
    </form>
</body>
</html>'''

@app.route('/student')
def student_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    my_assignments = [a for a in assignments.values() if a['engineer_id'] == user_id]
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>V7 Student Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ display: flex; align-items: center; gap: 15px; font-size: 24px; font-weight: 700; }}
        .v7-logo {{ width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 900; }}
        .logout {{ color: white; text-decoration: none; padding: 8px 16px; background: rgba(255,255,255,0.1); border-radius: 5px; }}
        .container {{ max-width: 1000px; margin: 20px auto; padding: 0 20px; }}
        .card {{ background: white; padding: 25px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .assignment {{ border: 1px solid #ddd; padding: 20px; margin: 15px 0; border-radius: 8px; background: #f9f9f9; }}
        .status {{ padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }}
        .pending {{ background: #fff3cd; color: #856404; }}
        .submitted {{ background: #d1ecf1; color: #0c5460; }}
        .published {{ background: #d4edda; color: #155724; }}
        .btn {{ background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        .score {{ font-size: 1.2em; font-weight: bold; color: #28a745; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <div class="v7-logo">V7</div>
            Student Dashboard - {session['display_name']}
        </div>
        <a href="/logout" class="logout">Logout</a>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>My Assignments</h2>
            {''.join(f'''
            <div class="assignment">
                <h3>{a["topic"].title()} Assessment</h3>
                <p>ID: {a["id"]}</p>
                <p>Due: {a["due_date"][:10]}</p>
                <span class="status {a["status"]}">{a["status"].title()}</span>
                {'<p class="score">Score: ' + str(a.get("total_score", 0)) + '/150</p>' if a["status"] == "published" else ''}
                {'<a href="/student/assignment/' + a["id"] + '" class="btn">Start Assignment</a>' if a["status"] == "pending" else ''}
                {'<p><em>Submitted - Awaiting review</em></p>' if a["status"] == "submitted" else ''}
            </div>
            ''' for a in my_assignments) if my_assignments else '<p>No assignments yet.</p>'}
        </div>
    </div>
</body>
</html>'''

@app.route('/student/assignment/<assignment_id>', methods=['GET', 'POST'])
def student_assignment(assignment_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    assignment = assignments.get(assignment_id)
    if not assignment or assignment['engineer_id'] != session['user_id'] or assignment['status'] != 'pending':
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
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>{assignment["topic"].title()} Assignment</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; }}
        .header {{ background: #28a745; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }}
        .question {{ background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        textarea {{ width: 100%; min-height: 100px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .btn {{ background: #28a745; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; width: 100%; }}
        .back {{ background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <a href="/student" class="back">← Back</a>
    <div class="header">
        <h1>{assignment["topic"].title()} Assessment</h1>
        <p>15 Questions | Answer all questions thoroughly</p>
    </div>
    
    <form method="POST">
        {''.join(f'''
        <div class="question">
            <h3>Question {i+1}/15</h3>
            <p>{q}</p>
            <textarea name="answer_{i}" placeholder="Your detailed answer..." required></textarea>
        </div>
        ''' for i, q in enumerate(assignment["questions"]))}
        
        <button type="submit" class="btn">Submit All Answers</button>
    </form>
</body>
</html>'''

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return '<h1>404 - Page Not Found</h1><a href="/">Home</a>', 404

@app.errorhandler(500)
def internal_error(error):
    return '<h1>500 - Internal Error</h1><a href="/">Home</a>', 500

# Initialize
init_users()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
