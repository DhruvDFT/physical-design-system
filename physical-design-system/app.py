# app.py - Minimal Working PD System
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

# Questions - 10 per topic, 3+ experience level
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

# Enhanced scoring system with detailed analysis
def calculate_advanced_score(answer, question_text):
    """Advanced scoring system with multiple criteria"""
    if not answer or len(answer.strip()) < 10:
        return {
            'score': 0,
            'breakdown': {'technical': 0, 'depth': 0, 'clarity': 0, 'completeness': 0},
            'feedback': 'Answer too short or missing',
            'confidence': 0
        }
    
    answer_lower = answer.lower()
    words = answer.split()
    
    # Technical accuracy (0-3 points)
    technical_keywords = [
        'timing', 'placement', 'routing', 'congestion', 'power', 'voltage', 'clock',
        'macro', 'floorplan', 'DRC', 'violations', 'optimization', 'strategy',
        'methodology', 'analysis', 'verification', 'constraints', 'closure',
        'skew', 'impedance', 'fanout', 'density', 'leakage', 'parasitic'
    ]
    
    technical_score = 0
    found_keywords = sum(1 for kw in technical_keywords if kw in answer_lower)
    if found_keywords >= 8:
        technical_score = 3
    elif found_keywords >= 5:
        technical_score = 2.5
    elif found_keywords >= 3:
        technical_score = 2
    elif found_keywords >= 1:
        technical_score = 1
    
    # Depth and detail (0-2.5 points)
    depth_indicators = ['because', 'therefore', 'due to', 'approach', 'method', 'technique', 'consider', 'ensure', 'minimize', 'optimize', 'analyze', 'implement']
    depth_score = min(sum(1 for indicator in depth_indicators if indicator in answer_lower) * 0.3, 2.5)
    
    # Clarity and structure (0-2.5 points)
    clarity_indicators = ['first', 'second', 'third', 'then', 'next', 'finally', 'steps', 'process', 'workflow']
    clarity_score = min(sum(1 for indicator in clarity_indicators if indicator in answer_lower) * 0.4, 2.5)
    
    # Completeness (0-2 points)
    word_count = len(words)
    if word_count >= 100:
        completeness_score = 2
    elif word_count >= 60:
        completeness_score = 1.5
    elif word_count >= 30:
        completeness_score = 1
    else:
        completeness_score = 0.5
    
    total_score = technical_score + depth_score + clarity_score + completeness_score
    final_score = min(total_score, 10)
    
    # Generate detailed feedback
    feedback_parts = []
    if technical_score < 2:
        feedback_parts.append("More technical terminology needed")
    if depth_score < 1.5:
        feedback_parts.append("Explain reasoning and methodology")
    if clarity_score < 1.5:
        feedback_parts.append("Better structure and step-by-step approach")
    if completeness_score < 1.5:
        feedback_parts.append("More comprehensive coverage required")
    
    if not feedback_parts:
        feedback_parts.append("Excellent comprehensive answer")
    
    # Confidence level
    confidence = min((technical_score / 3) * (completeness_score / 2) * 1.2, 1.0)
    
    return {
        'score': round(final_score, 1),
        'breakdown': {
            'technical': round(technical_score, 1),
            'depth': round(depth_score, 1),
            'clarity': round(clarity_score, 1),
            'completeness': round(completeness_score, 1)
        },
        'feedback': "; ".join(feedback_parts),
        'confidence': round(confidence * 100, 0)
    }
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
    
    # Get all 10 questions for the topic
    all_questions = QUESTIONS[topic]
    
    # Create unique question selection based on engineer ID and counter
    # This ensures each engineer gets different questions even for the same topic
    import hashlib
    seed_string = f"{eng_id}_{topic}_{counter}"
    seed_hash = int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)
    
    # Use the seed to create a deterministic but unique selection
    import random
    random.seed(seed_hash)
    
    # Select 3 unique questions from the 10 available
    selected_questions = random.sample(all_questions, 3)
    
    # Reset random seed to avoid affecting other operations
    random.seed()
    
    test = {
        'id': test_id,
        'engineer_id': eng_id,
        'topic': topic,
        'questions': selected_questions,  # Unique 3 questions
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
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1e3a8a 0%, #64748b 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; position: relative; overflow: hidden; }
        body::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at 20% 80%, rgba(30, 58, 138, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(100, 116, 139, 0.3) 0%, transparent 50%); }
        .box { background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); padding: 50px; border-radius: 25px; width: 420px; box-shadow: 0 25px 50px rgba(30, 58, 138, 0.3); border: 1px solid rgba(255,255,255,0.3); position: relative; z-index: 1; }
        h1 { background: linear-gradient(135deg, #1e3a8a, #64748b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 35px; font-size: 32px; font-weight: 700; }
        input { width: 100%; padding: 16px 20px; margin: 12px 0; border: 2px solid #e2e8f0; border-radius: 12px; font-size: 16px; transition: all 0.3s ease; background: rgba(248, 250, 252, 0.8); }
        input:focus { outline: none; border-color: #1e3a8a; box-shadow: 0 0 0 4px rgba(30, 58, 138, 0.1); background: white; }
        button { width: 100%; padding: 18px; background: linear-gradient(135deg, #1e3a8a, #64748b); color: white; border: none; border-radius: 12px; font-size: 18px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 8px 20px rgba(30, 58, 138, 0.3); }
        button:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(30, 58, 138, 0.4); }
        .info { background: linear-gradient(135deg, rgba(30, 58, 138, 0.1), rgba(100, 116, 139, 0.1)); border: 1px solid #1e3a8a; padding: 20px; border-radius: 12px; margin: 25px 0; text-align: center; }
        .info h4 { color: #1e3a8a; margin-bottom: 12px; font-size: 16px; }
        .info p { color: #475569; font-size: 14px; margin: 8px 0; }
    </style>
</head>
<body>
    <div class="box">
        <h1>⚡ PD Assessment</h1>
        <form method="POST">
            <input type="text" name="username" placeholder="Enter Username" required>
            <input type="password" name="password" placeholder="Enter Password" required>
            <button type="submit">Sign In</button>
        </form>
        <div class="info">
            <h4>🔑 Test Login Credentials</h4>
            <p><strong>Engineers:</strong> eng001, eng002, eng003, eng004, eng005</p>
            <p><strong>Password:</strong> password123</p>
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
            <small>3 Unique Questions | Max: 30 points</small><br>
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
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); }}
        .header {{ background: linear-gradient(135deg, #1e3a8a, #64748b); color: white; padding: 25px 0; box-shadow: 0 4px 20px rgba(30, 58, 138, 0.2); }}
        .container {{ max-width: 1200px; margin: 25px auto; padding: 0 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 25px; margin-bottom: 35px; }}
        .stat {{ background: white; padding: 25px; border-radius: 16px; text-align: center; box-shadow: 0 8px 25px rgba(30, 58, 138, 0.1); border: 1px solid rgba(30, 58, 138, 0.1); transition: transform 0.3s ease; }}
        .stat:hover {{ transform: translateY(-5px); }}
        .stat-num {{ font-size: 28px; font-weight: bold; background: linear-gradient(135deg, #1e3a8a, #64748b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }}
        .card {{ background: white; border-radius: 16px; padding: 25px; margin: 25px 0; box-shadow: 0 8px 25px rgba(30, 58, 138, 0.1); border: 1px solid rgba(30, 58, 138, 0.1); }}
        .card h2 {{ color: #1e3a8a; margin-bottom: 20px; font-size: 22px; }}
        select, button {{ padding: 12px 16px; margin: 8px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 14px; transition: all 0.3s ease; }}
        button {{ background: linear-gradient(135deg, #1e3a8a, #64748b); color: white; border: none; cursor: pointer; font-weight: 600; }}
        button:hover {{ transform: translateY(-2px); box-shadow: 0 8px 20px rgba(30, 58, 138, 0.3); }}
        .logout {{ background: rgba(255,255,255,0.2); color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; float: right; transition: all 0.3s ease; }}
        .logout:hover {{ background: rgba(255,255,255,0.3); }}
    </style>
</head>
<body>
    <div class="header">
        <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
            <h1 style="font-size: 28px; font-weight: 700;">⚡ Admin Dashboard
                <a href="/logout" class="logout">Logout</a>
            </h1>
        </div>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat"><div class="stat-num">{len(engineers)}</div><div style="color: #64748b; font-weight: 500;">Engineers</div></div>
            <div class="stat"><div class="stat-num">{len(all_tests)}</div><div style="color: #64748b; font-weight: 500;">Total Tests</div></div>
            <div class="stat"><div class="stat-num">{len(pending)}</div><div style="color: #64748b; font-weight: 500;">Pending Review</div></div>
            <div class="stat"><div class="stat-num">30</div><div style="color: #64748b; font-weight: 500;">Questions</div></div>
        </div>
        
        <div class="card">
            <h2>🎯 Create Assessment</h2>
            <form method="POST" action="/admin/create">
                <select name="engineer_id" required>
                    <option value="">Select Engineer...</option>
                    {eng_options}
                </select>
                <select name="topic" required>
                    <option value="">Select Topic...</option>
                    <option value="floorplanning">🏗️ Floorplanning</option>
                    <option value="placement">📍 Placement</option>
                    <option value="routing">🛤️ Routing</option>
                </select>
                <button type="submit">Create Assessment</button>
            </form>
        </div>
        
        <div class="card">
            <h2>📋 Pending Reviews</h2>
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
        num_questions = len(test['questions'])  # Should be 3 unique questions
        for i in range(num_questions):
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
        
        # Calculate advanced score for this answer
        advanced_analysis = calculate_advanced_score(answer, q)
        
        questions_html += f'''
        <div style="background: white; border-radius: 16px; padding: 25px; margin: 20px 0; box-shadow: 0 8px 25px rgba(30, 58, 138, 0.1); border: 1px solid rgba(30, 58, 138, 0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h4 style="color: #1e3a8a; font-size: 18px;">Question {i+1} of {len(test['questions'])}</h4>
                <span style="background: linear-gradient(135deg, #1e3a8a, #64748b); color: white; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">3+ Experience</span>
            </div>
            
            <div style="background: linear-gradient(135deg, #f1f5f9, #e2e8f0); padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 4px solid #1e3a8a;">
                <strong>Question:</strong> {q}
            </div>
            
            <h5 style="color: #1e3a8a; margin: 15px 0 10px 0;">📝 Engineer's Answer:</h5>
            <div style="background: #fefefe; border: 2px solid #e2e8f0; padding: 20px; border-radius: 12px; font-family: 'Courier New', monospace; white-space: pre-wrap; min-height: 80px; line-height: 1.6;">
                {answer}
            </div>
            
            <div style="background: linear-gradient(135deg, rgba(30, 58, 138, 0.05), rgba(100, 116, 139, 0.05)); border: 2px solid #1e3a8a; border-radius: 12px; padding: 20px; margin: 20px 0;">
                <h5 style="color: #1e3a8a; margin-bottom: 15px; display: flex; align-items: center;">
                    🤖 Advanced AI Analysis
                    <span style="background: #22c55e; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; margin-left: 10px;">{advanced_analysis['confidence']}% Confidence</span>
                </h5>
                
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 15px;">
                    <div style="background: rgba(30, 58, 138, 0.1); padding: 12px; border-radius: 8px; text-align: center;">
                        <div style="font-weight: bold; color: #1e3a8a; font-size: 16px;">{advanced_analysis['breakdown']['technical']}/3</div>
                        <div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Technical</div>
                    </div>
                    <div style="background: rgba(30, 58, 138, 0.1); padding: 12px; border-radius: 8px; text-align: center;">
                        <div style="font-weight: bold; color: #1e3a8a; font-size: 16px;">{advanced_analysis['breakdown']['depth']}/2.5</div>
                        <div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Depth</div>
                    </div>
                    <div style="background: rgba(30, 58, 138, 0.1); padding: 12px; border-radius: 8px; text-align: center;">
                        <div style="font-weight: bold; color: #1e3a8a; font-size: 16px;">{advanced_analysis['breakdown']['clarity']}/2.5</div>
                        <div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Clarity</div>
                    </div>
                    <div style="background: rgba(30, 58, 138, 0.1); padding: 12px; border-radius: 8px; text-align: center;">
                        <div style="font-weight: bold; color: #1e3a8a; font-size: 16px;">{advanced_analysis['breakdown']['completeness']}/2</div>
                        <div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Complete</div>
                    </div>
                </div>
                
                <div style="background: rgba(34, 197, 94, 0.1); border-left: 4px solid #22c55e; padding: 12px; border-radius: 0 8px 8px 0;">
                    <strong style="color: #166534;">💡 AI Feedback:</strong> {advanced_analysis['feedback']}
                </div>
            </div>
            
            <div style="background: linear-gradient(135deg, #f8fafc, #f1f5f9); padding: 20px; border-radius: 12px; border: 2px solid #e2e8f0;">
                <label style="color: #1e3a8a; font-weight: bold; font-size: 16px; margin-bottom: 10px; display: block;">👨‍🏫 Your Final Score:</label>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <input type="number" name="score_{i}" min="0" max="10" value="{advanced_analysis['score']}" 
                           style="width: 80px; padding: 12px; border: 2px solid #1e3a8a; border-radius: 8px; text-align: center; font-weight: bold; font-size: 18px;" 
                           step="0.1" required>
                    <span style="font-weight: bold; color: #64748b; font-size: 16px;">/ 10.0</span>
                    <span style="background: rgba(30, 58, 138, 0.1); color: #1e3a8a; padding: 8px 12px; border-radius: 20px; font-size: 13px; font-weight: 500;">
                        AI Suggested: {advanced_analysis['score']}/10
                    </span>
                </div>
            </div>
        </div>'''+1}</h4>
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
    <title>Review Assessment</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); margin: 0; }}
        .header {{ background: linear-gradient(135deg, #1e3a8a, #64748b); color: white; padding: 25px 0; box-shadow: 0 4px 20px rgba(30, 58, 138, 0.2); }}
        .container {{ max-width: 1200px; margin: 25px auto; padding: 0 20px; }}
        button {{ background: linear-gradient(135deg, #1e3a8a, #64748b); color: white; padding: 15px 30px; border: none; border-radius: 10px; cursor: pointer; margin: 12px 8px; font-weight: 600; font-size: 16px; transition: all 0.3s ease; }}
        button:hover {{ transform: translateY(-2px); box-shadow: 0 8px 20px rgba(30, 58, 138, 0.3); }}
        .btn-sec {{ background: linear-gradient(135deg, #64748b, #94a3b8); }}
        input {{ padding: 8px; border: 2px solid #e2e8f0; border-radius: 6px; transition: all 0.3s ease; }}
        input:focus {{ outline: none; border-color: #1e3a8a; box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.1); }}
        .submit-section {{ background: white; border-radius: 16px; padding: 30px; text-align: center; box-shadow: 0 8px 25px rgba(30, 58, 138, 0.1); margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
            <h1 style="font-size: 28px; font-weight: 700;">📝 Assessment Review</h1>
            <p style="opacity: 0.9; font-size: 16px;">ID: {test_id} | Topic: {test["topic"].title()} | Engineer: {test["engineer_id"]}</p>
        </div>
    </div>
    
    <div class="container">
        <form method="POST">
            {questions_html}
            <div class="submit-section">
                <h3 style="color: #1e3a8a; margin-bottom: 15px;">📊 Assessment Summary</h3>
                <p style="color: #64748b; margin-bottom: 25px;">Review all AI analysis and adjust scores as needed before publishing results.</p>
                <button type="submit">✅ Publish Final Scores</button>
                <a href="/admin"><button type="button" class="btn-sec">← Back to Dashboard</button></a>
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
            <div style="background: white; border-radius: 16px; padding: 25px; margin: 20px 0; box-shadow: 0 8px 25px rgba(30, 58, 138, 0.1); border: 1px solid rgba(30, 58, 138, 0.1); transition: all 0.3s ease;">
                <h3 style="color: #1e3a8a; margin-bottom: 15px; font-size: 20px;">{t["topic"].title()} Assessment</h3>
                <div style="background: linear-gradient(135deg, #22c55e, #16a34a); color: white; padding: 20px; border-radius: 12px; text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; margin-bottom: 5px;">Score: {t["score"]}/30</div>
                    <div style="opacity: 0.9;">({(t["score"]/30*100):.1f}% • 3 Unique Questions)</div>
                </div>
            </div>'''
        elif status == 'submitted':
            tests_html += f'''
            <div style="background: white; border-radius: 16px; padding: 25px; margin: 20px 0; box-shadow: 0 8px 25px rgba(30, 58, 138, 0.1); border: 1px solid rgba(30, 58, 138, 0.1);">
                <h3 style="color: #1e3a8a; margin-bottom: 15px; font-size: 20px;">{t["topic"].title()} Assessment</h3>
                <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 20px; border-radius: 12px; text-align: center;">
                    <div style="font-size: 18px; font-weight: 600;">⏳ Under Advanced AI Analysis</div>
                    <div style="opacity: 0.9; margin-top: 8px;">Admin reviewing with AI insights</div>
                </div>
            </div>'''
        else:
            tests_html += f'''
            <div style="background: white; border-radius: 16px; padding: 25px; margin: 20px 0; box-shadow: 0 8px 25px rgba(30, 58, 138, 0.1); border: 1px solid rgba(30, 58, 138, 0.1); transition: all 0.3s ease;">
                <h3 style="color: #1e3a8a; margin-bottom: 15px; font-size: 20px;">{t["topic"].title()} Assessment</h3>
                <a href="/student/test/{t["id"]}" style="background: linear-gradient(135deg, #1e3a8a, #64748b); color: white; padding: 18px 30px; text-decoration: none; border-radius: 12px; display: block; text-align: center; font-weight: 600; font-size: 16px; transition: all 0.3s ease;">
                    🚀 Start Assessment (3 Unique Questions)
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
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: linear-gradient(135deg, #1e3a8a 0%, #64748b 100%); min-height: 100vh; position: relative; }}
        body::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at 20% 80%, rgba(30, 58, 138, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(100, 116, 139, 0.3) 0%, transparent 50%); }}
        .header {{ background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); padding: 25px 0; box-shadow: 0 4px 20px rgba(30, 58, 138, 0.2); position: relative; z-index: 1; }}
        .container {{ max-width: 1200px; margin: 25px auto; padding: 0 20px; position: relative; z-index: 1; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 25px; margin-bottom: 35px; }}
        .stat {{ background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); padding: 25px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(30, 58, 138, 0.2); border: 1px solid rgba(255,255,255,0.3); transition: all 0.3s ease; }}
        .stat:hover {{ transform: translateY(-8px); box-shadow: 0 15px 40px rgba(30, 58, 138, 0.3); }}
        .stat-num {{ font-size: 28px; font-weight: bold; background: linear-gradient(135deg, #1e3a8a, #64748b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }}
        .section {{ background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(30, 58, 138, 0.2); border: 1px solid rgba(255,255,255,0.3); }}
        .section h2 {{ color: #1e3a8a; margin-bottom: 25px; font-size: 24px; font-weight: 700; }}
        .logout {{ background: rgba(239,68,68,0.1); color: #dc2626; padding: 12px 20px; text-decoration: none; border-radius: 10px; float: right; transition: all 0.3s ease; font-weight: 600; }}
        .logout:hover {{ background: rgba(239,68,68,0.2); transform: translateY(-2px); }}
        .header h1 {{ background: linear-gradient(135deg, #1e3a8a, #64748b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 700; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
            <h1>⚡ Engineer Dashboard
                <a href="/logout" class="logout">Logout</a>
            </h1>
        </div>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat"><div class="stat-num">{len(my_tests)}</div><div style="color: #64748b; font-weight: 500;">Assessments</div></div>
            <div class="stat"><div class="stat-num">{len([t for t in my_tests if t['status'] == 'completed'])}</div><div style="color: #64748b; font-weight: 500;">Completed</div></div>
            <div class="stat"><div class="stat-num">{user.get('exp', 0)}y</div><div style="color: #64748b; font-weight: 500;">Experience</div></div>
            <div class="stat"><div class="stat-num">10</div><div style="color: #64748b; font-weight: 500;">Questions/Test</div></div>
        </div>
        
        <div class="section">
            <h2>📚 My Assessments</h2>
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
        num_questions = len(test['questions'])  # Should be 3 unique questions
        for i in range(num_questions):
            answer = request.form.get(f'answer_{i}', '').strip()
            if answer:
                answers[str(i)] = answer
        
        if len(answers) == num_questions:
            test['answers'] = answers
            test['status'] = 'submitted'
        
        return redirect('/student')
    
    questions_html = ''
    for i, q in enumerate(test['questions']):
        questions_html += f'''
        <div style="background: rgba(255,255,255,0.95); border-radius: 16px; padding: 24px; margin: 20px 0;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-bottom: 16px;">
                Question {i+1} of {len(test['questions'])}
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
