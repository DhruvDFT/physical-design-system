# app.py - Minimal PD System with ONLY Unique Questions Added
import os
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = 'pd-secret-key'

# Global data
users = {}
assignments = {}
counter = 0

# Questions - 10 per topic, 3+ experience level (SAME AS WORKING VERSION)
QUESTIONS = {
    "floorplanning": [
        "You have a 5mm x 5mm die with 4 hard macros (each 1mm x 0.8mm) and need to achieve 70% utilization. Describe your macro placement strategy considering timing and power delivery.",
        "Your design has setup timing violations on paths crossing from left to right. The floorplan has macros placed randomly. How would you reorganize the floorplan to improve timing?",
        "During floorplan, you notice routing congestion in the center region. What are 3 specific techniques you would use to reduce congestion without major timing impact?",
        "Your design has 3 voltage domains (0.9V core, 1.2V IO, 0.7V retention). Explain how you would plan the floorplan to minimize level shifter count and power grid complexity.",
        "You need to place 12 memory instances (8 SRAMs, 4 ROMs) in your design. What factors would you consider for their placement, and how would you verify floorplan quality?",
        "Your floorplan review shows IR drop violations exceeding 50mV in certain regions. Describe your approach to fix this through floorplan changes and power grid improvements.",
        "You're told to reduce die area by 15% while maintaining timing closure. What floorplan modifications would you make and what risks would you monitor?",
        "Your design has mixed-signal blocks requiring 60dB isolation from digital switching noise. How would you handle their placement and what guard techniques would you use?",
        "During early floorplan, how would you estimate routing congestion and what tools/techniques help predict routability issues before placement?",
        "Your hierarchical design has 5 major blocks with complex timing constraints between them. Explain your approach to partition-level floorplanning and interface planning."
    ],
    "placement": [
        "Your placement run shows timing violations on 20 critical paths with negative slack up to -50ps. Describe your systematic approach to fix these violations.",
        "You're seeing routing congestion hotspots after placement in 2-3 regions. What placement adjustments would you make to improve routability?",
        "Your design has high-fanout nets (>500 fanout) causing placement issues. How would you handle these nets during placement optimization?",
        "Compare global placement vs detailed placement - what specific problems does each solve and when would you iterate between them?",
        "Your placement shows leakage power 20% higher than target. What placement techniques would you use to reduce power while maintaining timing?",
        "You have a multi-voltage design with 3 voltage islands. Describe your placement strategy for cells near domain boundaries and level shifter placement.",
        "Your timing report shows 150 hold violations scattered across the design. How would you address this through placement without affecting setup timing?",
        "During placement, you notice certain instances are creating routes longer than 500um. What tools and techniques help identify and fix such placement issues?",
        "Your design has 200+ clock gating cells. Explain their optimal placement strategy and impact on both power and timing closure.",
        "You're working with a design that has both high-performance (1GHz) and low-power (100MHz) modes. How does this affect your placement strategy and optimization targets?"
    ],
    "routing": [
        "After global routing, you have 500 DRC violations (spacing, via, width). Describe your systematic approach to resolve these violations efficiently.",
        "Your design has 10 differential pairs for high-speed signals. Explain your routing strategy to maintain 100-ohm impedance and minimize skew.",
        "You're seeing timing degradation after detailed routing compared to placement timing. What causes this and how would you recover the timing?",
        "Your router is struggling with congestion in certain regions leading to 5% routing non-completion. What techniques would you use to achieve 100% routing?",
        "Describe your approach to power/ground routing for a 200A peak current design. How do you ensure adequate current carrying capacity and low IR drop?",
        "Your design has specific layer constraints (no routing on M1 except local connections, M2-M3 for signal, M4-M6 for power). How does this impact your routing strategy?",
        "You have crosstalk violations on 50 critical nets causing functional failures. Explain your routing techniques to minimize crosstalk and meet noise requirements.",
        "Your clock distribution network requires <50ps skew across 10,000 flops. Describe clock routing methodology and skew optimization techniques.",
        "During routing, some power nets are showing electromigration violations. How would you address current density issues through routing changes and via sizing?",
        "You need to route in a 7nm design with double patterning constraints. Explain the challenges and your approach to handle LELE (Litho-Etch-Litho-Etch) decomposition issues."
    ]
}

def hash_pass(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def check_pass(hashed, pwd):
    return hashed == hashlib.sha256(pwd.encode()).hexdigest()

def init_data():
    global users
    users['admin'] = {
        'id': 'admin',
        'username': 'admin',
        'password': hash_pass('Vibhuaya@3006'),
        'is_admin': True,
        'exp': 5
    }
    
    for i in range(1, 6):
        uid = f'eng00{i}'
        users[uid] = {
            'id': uid,
            'username': uid,
            'password': hash_pass('password123'),
            'is_admin': False,
            'exp': 3 + (i % 3)
        }

def create_test(eng_id, topic):
    global counter
    counter += 1
    test_id = f"PD_{topic}_{eng_id}_{counter}"
    
    # ONLY CHANGE: Engineer-specific question selection
    all_questions = QUESTIONS[topic]
    
    # Simple mapping: each engineer gets different questions from the same pool
    engineer_offset = {
        'eng001': [0, 1, 2],
        'eng002': [3, 4, 5], 
        'eng003': [6, 7, 8],
        'eng004': [9, 0, 1],  # Wrap around for more engineers
        'eng005': [2, 3, 4]
    }
    
    indices = engineer_offset.get(eng_id, [0, 1, 2])
    selected_questions = [all_questions[i] for i in indices]
    
    test = {
        'id': test_id,
        'engineer_id': eng_id,
        'topic': topic,
        'questions': selected_questions,
        'answers': {},
        'status': 'pending',
        'created': datetime.now().isoformat(),
        'due': (datetime.now() + timedelta(days=3)).isoformat(),
        'score': None
    }
    
    assignments[test_id] = test
    return test

@app.route('/')
def home():
    if 'user_id' in session:
        if session.get('is_admin'):
            return redirect('/admin')
        return redirect('/student')
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
        if user and check_pass(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user.get('is_admin', False)
            
            if user.get('is_admin'):
                return redirect('/admin')
            return redirect('/student')
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>PD Assessment Login</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }
        .box { background: rgba(255,255,255,0.95); padding: 40px; border-radius: 20px; width: 350px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
        h1 { background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 30px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; }
        input:focus { outline: none; border-color: #667eea; }
        button { width: 100%; padding: 14px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
        .info { background: #f0f9ff; border: 1px solid #0ea5e9; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }
    </style>
</head>
<body>
    <div class="box">
        <h1>PD Assessment</h1>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <div class="info">
            <strong>Test Login:</strong><br>
            Engineers: eng001, eng002, eng003, eng004, eng005<br>
            Password: password123
        </div>
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
    
    engineers = [u for u in users.values() if not u.get('is_admin')]
    all_tests = list(assignments.values())
    pending = [a for a in all_tests if a['status'] == 'submitted']
    
    eng_options = ''
    for eng in engineers:
        eng_options += f'<option value="{eng["id"]}">{eng["username"]} (3+ Experience)</option>'
    
    pending_html = ''
    for p in pending:
        pending_html += f'''
        <div style="background: #f8fafc; padding: 15px; margin: 10px 0; border-radius: 8px; border: 1px solid #e2e8f0;">
            <strong>{p["topic"].title()} - {p["engineer_id"]}</strong><br>
            <small>3 Questions | Max: 30 points</small><br>
            <a href="/admin/review/{p["id"]}" style="background: #10b981; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 8px;">Review</a>
        </div>'''
    
    if not pending_html:
        pending_html = '<p style="text-align: center; color: #64748b; padding: 40px;">No pending reviews</p>'
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <style>
        body {{ font-family: Arial; margin: 0; background: #f8fafc; }}
        .header {{ background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 20px 0; }}
        .container {{ max-width: 1000px; margin: 20px auto; padding: 0 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
        .stat {{ background: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-num {{ font-size: 24px; font-weight: bold; color: #1e40af; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        select, button {{ padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }}
        button {{ background: #3b82f6; color: white; border: none; cursor: pointer; }}
        .logout {{ background: rgba(255,255,255,0.2); color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; float: right; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="max-width: 1000px; margin: 0 auto; padding: 0 20px;">
            <h1>Admin Dashboard
                <a href="/logout" class="logout">Logout</a>
            </h1>
        </div>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat"><div class="stat-num">{len(engineers)}</div><div>Engineers</div></div>
            <div class="stat"><div class="stat-num">{len(all_tests)}</div><div>Tests</div></div>
            <div class="stat"><div class="stat-num">{len(pending)}</div><div>Pending</div></div>
            <div class="stat"><div class="stat-num">30</div><div>Questions</div></div>
        </div>
        
        <div class="card">
            <h2>Create Test</h2>
            <form method="POST" action="/admin/create">
                <select name="engineer_id" required>
                    <option value="">Select Engineer...</option>
                    {eng_options}
                </select>
                <select name="topic" required>
                    <option value="">Select Topic...</option>
                    <option value="floorplanning">Floorplanning</option>
                    <option value="placement">Placement</option>
                    <option value="routing">Routing</option>
                </select>
                <button type="submit">Create</button>
            </form>
        </div>
        
        <div class="card">
            <h2>Pending Reviews</h2>
            {pending_html}
        </div>
    </div>
</body>
</html>'''

@app.route('/admin/create', methods=['POST'])
def admin_create():
    if not session.get('is_admin'):
        return redirect('/login')
    
    eng_id = request.form.get('engineer_id')
    topic = request.form.get('topic')
    
    if eng_id and topic and topic in QUESTIONS:
        create_test(eng_id, topic)
    
    return redirect('/admin')

@app.route('/admin/review/<test_id>', methods=['GET', 'POST'])
def admin_review(test_id):
    if not session.get('is_admin'):
        return redirect('/login')
    
    test = assignments.get(test_id)
    if not test:
        return redirect('/admin')
    
    if request.method == 'POST':
        total = 0
        for i in range(3):
            try:
                score = float(request.form.get(f'score_{i}', 0))
                total += score
            except:
                pass
        
        test['score'] = total
        test['status'] = 'completed'
        return redirect('/admin')
    
    questions_html = ''
    for i, q in enumerate(test['questions']):
        answer = test.get('answers', {}).get(str(i), 'No answer')
        questions_html += f'''
        <div style="background: white; border-radius: 8px; padding: 20px; margin: 15px 0;">
            <h4>Question {i+1}</h4>
            <div style="background: #f1f5f9; padding: 15px; border-radius: 6px; margin: 10px 0;">
                {q}
            </div>
            <h5>Answer:</h5>
            <div style="background: #fefefe; border: 1px solid #e2e8f0; padding: 15px; border-radius: 6px; font-family: monospace; white-space: pre-wrap;">
                {answer}
            </div>
            <div style="margin: 15px 0;">
                <label><strong>Score:</strong></label>
                <input type="number" name="score_{i}" min="0" max="10" value="7" style="width: 60px; padding: 5px;">
                <span>/10</span>
            </div>
        </div>'''
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Review Test</title>
    <style>
        body {{ font-family: Arial; background: #f8fafc; margin: 0; }}
        .header {{ background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 20px 0; }}
        .container {{ max-width: 1000px; margin: 20px auto; padding: 0 20px; }}
        button {{ background: #3b82f6; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; margin: 10px 5px; }}
        .btn-sec {{ background: #6b7280; }}
        input {{ padding: 5px; border: 1px solid #ddd; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="max-width: 1000px; margin: 0 auto; padding: 0 20px;">
            <h1>Review: {test_id}</h1>
        </div>
    </div>
    
    <div class="container">
        <form method="POST">
            {questions_html}
            <div style="text-align: center; padding: 20px;">
                <button type="submit">Publish Scores</button>
                <a href="/admin"><button type="button" class="btn-sec">Back</button></a>
            </div>
        </form>
    </div>
</body>
</html>'''

@app.route('/student')
def student():
    if not session.get('user_id') or session.get('is_admin'):
        return redirect('/login')
    
    user_id = session['user_id']
    user = users.get(user_id, {})
    my_tests = [a for a in assignments.values() if a['engineer_id'] == user_id]
    
    tests_html = ''
    for t in my_tests:
        status = t['status']
        if status == 'completed':
            tests_html += f'''
            <div style="background: white; border-radius: 12px; padding: 20px; margin: 15px 0;">
                <h3>{t["topic"].title()} Test</h3>
                <div style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 12px; border-radius: 8px; text-align: center;">
                    <strong>Score: {t["score"]}/30</strong>
                </div>
            </div>'''
        elif status == 'submitted':
            tests_html += f'''
            <div style="background: white; border-radius: 12px; padding: 20px; margin: 15px 0;">
                <h3>{t["topic"].title()} Test</h3>
                <p style="color: #3b82f6; text-align: center;">Under Review</p>
            </div>'''
        else:
            tests_html += f'''
            <div style="background: white; border-radius: 12px; padding: 20px; margin: 15px 0;">
                <h3>{t["topic"].title()} Test</h3>
                <a href="/student/test/{t["id"]}" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: block; text-align: center;">
                    Start Test
                </a>
            </div>'''
    
    if not tests_html:
        tests_html = '<div style="text-align: center; padding: 40px; color: #64748b;"><h3>No tests assigned</h3></div>'
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Student Dashboard</title>
    <style>
        body {{ font-family: Arial; margin: 0; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; }}
        .header {{ background: rgba(255,255,255,0.95); padding: 20px 0; }}
        .container {{ max-width: 1000px; margin: 20px auto; padding: 0 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
        .stat {{ background: rgba(255,255,255,0.95); padding: 20px; border-radius: 16px; text-align: center; }}
        .section {{ background: rgba(255,255,255,0.95); border-radius: 16px; padding: 24px; }}
        .logout {{ background: rgba(239,68,68,0.1); color: #dc2626; padding: 8px 16px; text-decoration: none; border-radius: 6px; float: right; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="max-width: 1000px; margin: 0 auto; padding: 0 20px;">
            <h1 style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Engineer Dashboard
                <a href="/logout" class="logout">Logout</a>
            </h1>
        </div>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat"><div style="font-size: 20px; font-weight: bold;">{len(my_tests)}</div><div>Tests</div></div>
            <div class="stat"><div style="font-size: 20px; font-weight: bold;">{len([t for t in my_tests if t['status'] == 'completed'])}</div><div>Done</div></div>
            <div class="stat"><div style="font-size: 20px; font-weight: bold;">{user.get('exp', 0)}y</div><div>Experience</div></div>
            <div class="stat"><div style="font-size: 20px; font-weight: bold;">3</div><div>Questions</div></div>
        </div>
        
        <div class="section">
            <h2>My Tests</h2>
            {tests_html}
        </div>
    </div>
</body>
</html>'''

@app.route('/student/test/<test_id>', methods=['GET', 'POST'])
def student_test(test_id):
    if not session.get('user_id') or session.get('is_admin'):
        return redirect('/login')
    
    test = assignments.get(test_id)
    if not test or test['engineer_id'] != session['user_id']:
        return redirect('/student')
    
    if request.method == 'POST' and test['status'] == 'pending':
        answers = {}
        for i in range(3):
            answer = request.form.get(f'answer_{i}', '').strip()
            if answer:
                answers[str(i)] = answer
        
        if len(answers) == 3:
            test['answers'] = answers
            test['status'] = 'submitted'
        
        return redirect('/student')
    
    questions_html = ''
    for i, q in enumerate(test['questions']):
        questions_html += f'''
        <div style="background: rgba(255,255,255,0.95); border-radius: 16px; padding: 24px; margin: 20px 0;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-bottom: 16px;">
                Question {i+1} of 3
            </div>
            <div style="background: linear-gradient(135deg, #f8fafc, #f1f5f9); padding: 16px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #667eea;">
                {q}
            </div>
            <label style="font-weight: 600; margin-bottom: 8px; display: block;">Your Answer:</label>
            <textarea name="answer_{i}" style="width: 100%; min-height: 120px; padding: 16px; border: 2px solid #e5e7eb; border-radius: 12px; font-size: 14px;" placeholder="Provide detailed technical answer..." required></textarea>
        </div>'''
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>{test["topic"].title()} Test</title>
    <style>
        body {{ font-family: Arial; margin: 0; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; }}
        .header {{ background: rgba(255,255,255,0.95); padding: 20px 0; position: sticky; top: 0; }}
        .container {{ max-width: 1000px; margin: 20px auto; padding: 0 20px; }}
        button {{ padding: 14px 28px; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; margin: 8px; }}
        .btn-primary {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; }}
        .btn-secondary {{ background: rgba(107,114,128,0.1); color: #374151; }}
        textarea:focus {{ outline: none; border-color: #667eea; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="max-width: 1000px; margin: 0 auto; padding: 0 20px; text-align: center;">
            <h1 style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {test["topic"].title()} Test
            </h1>
        </div>
    </div>
    
    <div class="container">
        <form method="POST">
            {questions_html}
            <div style="background: rgba(255,255,255,0.95); border-radius: 16px; padding: 24px; text-align: center; margin-top: 20px;">
                <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 16px; border-radius: 12px; margin-bottom: 20px; color: #92400e;">
                    ⚠️ Review all answers before submitting. Cannot edit after submission.
                </div>
                <button type="submit" class="btn-primary">Submit Test</button>
                <a href="/student"><button type="button" class="btn-secondary">Back</button></a>
            </div>
        </form>
    </div>
</body>
</html>'''

# Initialize
init_data()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
