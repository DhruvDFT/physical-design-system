# app.py - Minimal PD System with NEW Questions Added
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

# Questions - 10 per topic, 3+ experience level (NEW QUESTIONS)
QUESTIONS = {
    "floorplanning": [
        "Your chip has 8 voltage domains with different power requirements (1.8V, 1.2V, 0.9V, 0.6V). Design a floorplan strategy that minimizes the number of level shifters while ensuring proper power delivery. What are the key considerations for domain boundary placement?",
        "You're working on a 7nm design with double patterning requirements. How would you modify your floorplan approach to handle SRAM compiler restrictions and ensure routing feasibility across different metal layers?",
        "Your design requires 15 different clock domains with frequencies ranging from 50MHz to 2GHz. Describe your floorplanning strategy to minimize clock skew and reduce power consumption from clock distribution networks.",
        "During floorplan optimization, you discover that your critical timing paths have excessive wire delays due to poor macro placement. What systematic approach would you use to relocate macros while maintaining area efficiency?",
        "Your mixed-signal design has 6 ADCs requiring 80dB PSRR and 4 PLLs sensitive to substrate noise. How would you plan the floorplan to achieve isolation requirements while optimizing for routability and thermal management?",
        "You need to implement power gating for 12 different functional blocks with varying wake-up time requirements. How would you organize the floorplan to minimize the impact on timing closure and power grid design?",
        "Your design has temperature hotspots exceeding 125°C in simulation. What floorplan modifications would you implement to improve thermal distribution, and how would you validate the thermal impact of your changes?",
        "You're tasked with creating a hierarchical floorplan for a multi-core processor with 8 identical cores plus shared L3 cache. Describe your approach to balance area efficiency, thermal considerations, and inter-core communication latency.",
        "Your floorplan review shows that 30% of nets will require more than 3 routing layers due to congestion. What specific floorplan adjustments would you make to reduce routing complexity while maintaining functional correctness?",
        "You have a design with 20 high-speed differential pairs (10Gbps+) that must maintain controlled impedance. How would you plan the floorplan to ensure signal integrity requirements are met while optimizing for area and power?"
    ],
    "placement": [
        "Your placement results show 500+ timing violations with the worst negative slack of -200ps on critical paths. Develop a systematic recovery plan that addresses both setup and hold timing without significantly impacting power or area.",
        "You're implementing a design with 50,000+ flip-flops across 15 clock domains. Describe your placement strategy to minimize clock power while ensuring timing closure and managing clock domain crossing requirements.",
        "Your design has 300 high-fanout nets (fanout >1000) causing placement convergence issues. What specific techniques would you employ to handle these nets during global and detailed placement phases?",
        "After placement, your power analysis shows 40% higher dynamic power than target due to excessive switching activity. How would you modify your placement approach to reduce power while maintaining performance targets?",
        "You're working with a multi-Vt design using 4 different threshold voltage options (ULVT, LVT, RVT, HVT). Explain your placement optimization strategy to balance timing, power, and leakage requirements.",
        "Your design requires implementing scan chains with specific capture and shift mode timing requirements. How would you optimize placement to minimize impact on functional timing while meeting DFT constraints?",
        "You have a design with 1000+ memory instances of varying sizes that need to be placed optimally. What factors would you consider for memory placement, and how would you handle the interaction with logic placement?",
        "Your placement shows routing congestion exceeding 85% utilization in 25% of the chip area. What placement techniques would you use to redistribute logic and improve routability without timing degradation?",
        "You're implementing clock gating with 800+ ICG cells that need optimal placement for both power savings and timing closure. Describe your methodology for ICG placement and its impact on overall design optimization.",
        "Your design has critical nets with max transition time violations after placement. How would you address these violations through placement adjustments, buffer insertion, and driver sizing strategies?"
    ],
    "routing": [
        "Your detailed routing shows 2000+ DRC violations including minimum spacing, via enclosure, and metal density issues. Create a systematic debugging and resolution strategy that prioritizes violations by impact and difficulty.",
        "You're routing a high-speed DDR5 interface with 64 data lines requiring length matching within ±10ps and controlled impedance of 50Ω ±10%. Describe your routing methodology and verification approach.",
        "Your design has 50 critical nets showing crosstalk-induced timing violations exceeding 30ps. What routing techniques would you implement to reduce coupling while maintaining routability and meeting timing requirements?",
        "After routing completion, you discover 15% of your design has metal density violations that could impact manufacturing yield. How would you address these violations through routing modifications and fill strategies?",
        "Your power delivery network requires handling 150A peak current with IR drop <50mV across the chip. Design your power routing strategy including layer assignment, via sizing, and current density management.",
        "You're implementing a clock distribution network for a 1.5GHz design with 25,000 flip-flops requiring <25ps skew. Describe your clock routing methodology, including tree synthesis and skew optimization techniques.",
        "Your routing has 200+ electromigration violations on critical power and signal nets. What modifications would you make to via sizing, wire widths, and current path optimization to resolve these issues?",
        "You need to route in a 5nm process with quadruple patterning on critical layers. Explain how you would handle the decomposition challenges and ensure manufacturability while maintaining performance targets.",
        "Your design has 100+ antenna violations that could cause gate oxide damage during manufacturing. What routing strategies would you implement to prevent antenna accumulation during the fabrication process?",
        "You're routing a mixed-signal design where digital switching noise is coupling into sensitive analog circuits, causing 20dB degradation in SNR. How would you modify your routing approach to achieve the required isolation?"
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

def analyze_answer_quality(question, answer, topic):
    """
    Analyzes answer quality and suggests a score based on technical content
    Returns: (suggested_score, reasoning)
    """
    if not answer or len(answer.strip()) < 20:
        return 0, "Answer too short or empty"
    
    answer_lower = answer.lower()
    
    # Define key technical terms and concepts for each topic
    scoring_criteria = {
        'floorplanning': {
            'excellent_terms': ['voltage domain', 'level shifter', 'power delivery', 'thermal', 'isolation', 'macro placement', 'utilization', 'congestion', 'timing closure', 'ir drop', 'power grid', 'mixed-signal'],
            'good_terms': ['placement', 'routing', 'timing', 'power', 'area', 'floorplan', 'design', 'optimization', 'constraint', 'metal layer'],
            'methodology_terms': ['systematic', 'approach', 'strategy', 'methodology', 'analysis', 'verification', 'optimization', 'iteration']
        },
        'placement': {
            'excellent_terms': ['timing violation', 'setup time', 'hold time', 'slack', 'congestion', 'utilization', 'fanout', 'clock domain', 'power optimization', 'multi-vt', 'threshold voltage'],
            'good_terms': ['placement', 'timing', 'routing', 'optimization', 'constraint', 'critical path', 'delay', 'buffer', 'clock', 'power'],
            'methodology_terms': ['global placement', 'detailed placement', 'incremental', 'systematic', 'iterative', 'optimization', 'analysis']
        },
        'routing': {
            'excellent_terms': ['drc violation', 'crosstalk', 'coupling', 'skew', 'impedance', 'differential pair', 'electromigration', 'current density', 'metal density', 'antenna effect'],
            'good_terms': ['routing', 'via', 'spacing', 'width', 'layer', 'signal integrity', 'timing', 'power', 'ground', 'clock'],
            'methodology_terms': ['global routing', 'detailed routing', 'systematic', 'layer assignment', 'optimization', 'verification', 'debugging']
        }
    }
    
    criteria = scoring_criteria.get(topic, scoring_criteria['floorplanning'])
    
    # Count relevant technical terms
    excellent_count = sum(1 for term in criteria['excellent_terms'] if term in answer_lower)
    good_count = sum(1 for term in criteria['good_terms'] if term in answer_lower)
    methodology_count = sum(1 for term in criteria['methodology_terms'] if term in answer_lower)
    
    # Calculate base score based on technical content
    base_score = 0
    
    # Length and structure analysis
    word_count = len(answer.split())
    has_structure = any(marker in answer_lower for marker in ['1.', '2.', 'first', 'second', 'step', 'approach', 'strategy'])
    has_examples = any(marker in answer_lower for marker in ['example', 'for instance', 'such as', 'e.g.', 'like'])
    
    # Scoring logic
    if excellent_count >= 3 and word_count >= 100:
        base_score = 8
        reasoning = f"Strong technical content ({excellent_count} advanced terms)"
    elif excellent_count >= 2 and word_count >= 60:
        base_score = 7
        reasoning = f"Good technical knowledge ({excellent_count} advanced terms)"
    elif excellent_count >= 1 or good_count >= 3:
        base_score = 6
        reasoning = f"Adequate technical understanding"
    elif good_count >= 2 and word_count >= 40:
        base_score = 5
        reasoning = f"Basic technical knowledge"
    elif word_count >= 30:
        base_score = 4
        reasoning = "Limited technical content"
    else:
        base_score = 3
        reasoning = "Insufficient technical detail"
    
    # Bonus points for methodology and structure
    if methodology_count >= 2:
        base_score += 1
        reasoning += " + systematic approach"
    if has_structure:
        base_score += 0.5
        reasoning += " + well-structured"
    if has_examples and word_count >= 80:
        base_score += 0.5
        reasoning += " + practical examples"
    
    # Cap at 10 and round
    final_score = min(10, round(base_score))
    
    # Add word count info
    reasoning += f" ({word_count} words)"
    
    return final_score, reasoning

def create_test(eng_id, topic):
    global counter
    counter += 1
    test_id = f"PD_{topic}_{eng_id}_{counter}"
    
    # ONLY CHANGE: Each engineer gets all 10 questions (instead of 3)
    all_questions = QUESTIONS[topic]
    
    # All engineers get all 10 questions from their topic
    selected_questions = all_questions  # All 10 questions
    
    test = {
        'id': test_id,
        'engineer_id': eng_id,
        'topic': topic,
        'questions': selected_questions,
        'answers': {},
        'status': 'pending',
        'created': datetime.now().isoformat(),
        'due': (datetime.now() + timedelta(days=3)).isoformat(),
        'score': None,
        'auto_scores': {}  # Store AI-suggested scores
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
            <small>10 Questions | Max: 100 points</small><br>
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
    
    # Auto-analyze answers if not done yet
    if 'auto_scores' not in test:
        test['auto_scores'] = {}
        for i, answer in test.get('answers', {}).items():
            if answer and answer != 'No answer':
                suggested_score, reasoning = analyze_answer_quality(
                    test['questions'][int(i)], answer, test['topic']
                )
                test['auto_scores'][i] = {
                    'score': suggested_score,
                    'reasoning': reasoning
                }
    
    if request.method == 'POST':
        total = 0
        for i in range(10):  # Now 10 questions
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
        
        # Get AI suggestion
        auto_score_data = test.get('auto_scores', {}).get(str(i), {'score': 0, 'reasoning': 'No analysis available'})
        suggested_score = auto_score_data['score']
        reasoning = auto_score_data['reasoning']
        
        # Color coding for AI suggestion
        if suggested_score >= 8:
            suggestion_color = "#10b981"  # Green
        elif suggested_score >= 6:
            suggestion_color = "#f59e0b"  # Yellow
        else:
            suggestion_color = "#ef4444"  # Red
        
        questions_html += f'''
        <div style="background: white; border-radius: 8px; padding: 20px; margin: 15px 0; border-left: 4px solid {suggestion_color};">
            <h4>Question {i+1}</h4>
            <div style="background: #f1f5f9; padding: 15px; border-radius: 6px; margin: 10px 0;">
                {q}
            </div>
            <h5>Answer:</h5>
            <div style="background: #fefefe; border: 1px solid #e2e8f0; padding: 15px; border-radius: 6px; font-family: monospace; white-space: pre-wrap;">
                {answer}
            </div>
            <div style="background: #f8fafc; border-radius: 6px; padding: 12px; margin: 10px 0; border: 1px solid #e2e8f0;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="background: {suggestion_color}; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold;">
                        AI Suggests: {suggested_score}/10
                    </span>
                    <span style="color: #64748b; font-size: 14px;">{reasoning}</span>
                </div>
            </div>
            <div style="margin: 15px 0;">
                <label><strong>Your Score:</strong></label>
                <input type="number" name="score_{i}" min="0" max="10" value="{suggested_score}" style="width: 60px; padding: 5px; border: 2px solid {suggestion_color};">
                <span>/10</span>
                <button type="button" onclick="this.previousElementSibling.previousElementSibling.value={suggested_score}" style="margin-left: 10px; padding: 4px 8px; background: {suggestion_color}; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    Use AI Score
                </button>
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
                    <strong>Score: {t["score"]}/100</strong>
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
            <div class="stat"><div style="font-size: 20px; font-weight: bold;">10</div><div>Questions</div></div>
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
        for i in range(10):  # Now 10 questions
            answer = request.form.get(f'answer_{i}', '').strip()
            if answer:
                answers[str(i)] = answer
        
        if len(answers) == 10:  # All 10 must be answered
            test['answers'] = answers
            test['status'] = 'submitted'
        
        return redirect('/student')
    
    questions_html = ''
    for i, q in enumerate(test['questions']):
        questions_html += f'''
        <div style="background: rgba(255,255,255,0.95); border-radius: 16px; padding: 24px; margin: 20px 0;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-bottom: 16px;">
                Question {i+1} of 10
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
