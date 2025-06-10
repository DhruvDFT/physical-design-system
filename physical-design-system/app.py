# app.py - Professional PD Interview System V7 Edition
import os
import hashlib
import json
import secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, session, url_for

app = Flask(__name__)
# Generate a secure random secret key
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Enhanced password hashing with salt
def hash_password(password):
    salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + ':' + pwdhash.hex()

def check_password(stored_password, provided_password):
    try:
        salt, stored_hash = stored_password.split(':')
        pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return pwdhash.hex() == stored_hash
    except:
        return False

# In-memory storage
users = {}
assignments = {}
notifications = {}
assignment_counter = 0
engineer_question_sets = {}

# Initialize users securely
def init_users():
    # Admin with secure password (not displayed)
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Vibhuaya@3006')
    users['admin'] = {
        'id': 'admin',
        'username': 'admin',
        'password': hash_password(admin_password),
        'is_admin': True,
        'experience_years': 5,
        'display_name': 'Administrator',
        'department': 'Management'
    }
    
    # 5 Engineers with enhanced profiles
    engineer_names = ['Alex Chen', 'Sarah Kumar', 'Mike Johnson', 'Priya Singh', 'David Liu']
    for i in range(1, 6):
        user_id = f'eng00{i}'
        users[user_id] = {
            'id': user_id,
            'username': user_id,
            'password': hash_password('password123'),
            'is_admin': False,
            'experience_years': 3 + (i % 3),
            'display_name': engineer_names[i-1],
            'department': 'Physical Design'
        }

# Enhanced Questions Set with Professional Structure
QUESTIONS_SET1 = {
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

# Create different sets for different engineers
QUESTIONS_SET2 = QUESTIONS_SET1.copy()
QUESTIONS_SET3 = QUESTIONS_SET1.copy()
QUESTIONS_SET4 = QUESTIONS_SET1.copy()

QUESTION_SETS = [QUESTIONS_SET1, QUESTIONS_SET2, QUESTIONS_SET3, QUESTIONS_SET4]

# Enhanced keywords for better scoring
ANSWER_KEYWORDS = {
    "floorplanning": ["macro", "timing", "power", "congestion", "voltage", "clock", "memory", "IR drop", "area", "noise", "utilization", "placement", "routing"],
    "placement": ["timing", "congestion", "fanout", "global", "leakage", "voltage", "hold", "density", "clock", "signal", "optimization", "violation"],
    "routing": ["DRC", "differential", "timing", "congestion", "power", "layer", "crosstalk", "clock", "antenna", "ECO", "via", "spacing", "impedance"]
}

# Helper functions
def get_questions_for_engineer(engineer_id, topic):
    if engineer_id not in engineer_question_sets:
        engineer_num = int(engineer_id[-1]) - 1
        set_index = engineer_num % len(QUESTION_SETS)
        engineer_question_sets[engineer_id] = set_index
    
    set_index = engineer_question_sets[engineer_id]
    return QUESTION_SETS[set_index][topic]

def calculate_auto_score(answer, topic):
    if not answer:
        return 0
    
    answer_lower = answer.lower()
    keywords_found = 0
    
    if topic in ANSWER_KEYWORDS:
        for keyword in ANSWER_KEYWORDS[topic]:
            if keyword.lower() in answer_lower:
                keywords_found += 1
    
    # Enhanced scoring: consider answer length and keyword density
    base_score = min(keywords_found * 1.5, 8)
    length_bonus = min(len(answer.split()) / 100, 2)  # Bonus for detailed answers
    
    return min(base_score + length_bonus, 10)

def create_assignment(engineer_id, topic):
    global assignment_counter
    
    user = users.get(engineer_id)
    if not user or topic not in QUESTIONS_SET1:
        return None
    
    assignment_counter += 1
    assignment_id = f"V7_PD_{topic.upper()}_{engineer_id}_{assignment_counter:03d}"
    
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
        'difficulty_level': 'experienced'
    }
    
    assignments[assignment_id] = assignment
    
    # Create notification
    if engineer_id not in notifications:
        notifications[engineer_id] = []
    
    notifications[engineer_id].append({
        'title': f'New {topic.title()} Assessment',
        'message': f'15 technical questions assigned - Due in 3 days',
        'created_at': datetime.now().isoformat(),
        'type': 'assignment'
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
    return jsonify({
        'status': 'healthy',
        'version': '7.0',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            error = 'Please enter both username and password'
        else:
            user = users.get(username)
            if user and check_password(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['display_name'] = user['display_name']
                session['is_admin'] = user.get('is_admin', False)
                session['department'] = user['department']
                
                if user.get('is_admin'):
                    return redirect('/admin')
                else:
                    return redirect('/student')
            else:
                error = 'Invalid credentials. Please try again.'
    
    # Professional login page with V7 branding
    login_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>V7 PD Interview System - Login</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        
        .background-animation {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            z-index: -1;
        }
        
        .background-animation::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 50px 40px;
            border-radius: 24px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 450px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .logo-section {
            margin-bottom: 30px;
        }
        
        .v7-logo {
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            font-weight: 900;
            color: white;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .system-title {
            font-size: 28px;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }
        
        .system-subtitle {
            color: #718096;
            font-size: 16px;
            margin-bottom: 40px;
            font-weight: 500;
        }
        
        .demo-info {
            background: linear-gradient(135deg, #e6fffa 0%, #f0fff4 100%);
            padding: 25px;
            border-radius: 16px;
            margin-bottom: 30px;
            border: 1px solid #bee3f8;
            text-align: left;
        }
        
        .demo-info h3 {
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 16px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .demo-info p {
            margin-bottom: 8px;
            font-size: 14px;
            color: #4a5568;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .demo-info .role-badge {
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
        }
        
        .form-group {
            margin-bottom: 25px;
            text-align: left;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #2d3748;
            font-weight: 600;
            font-size: 14px;
        }
        
        .input-wrapper {
            position: relative;
        }
        
        .input-wrapper i {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #a0aec0;
            font-size: 16px;
        }
        
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 16px 20px 16px 50px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: white;
        }
        
        input[type="text"]:focus, input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .login-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .error {
            background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
            color: #c53030;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 25px;
            border: 1px solid #feb2b2;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .version-info {
            position: absolute;
            bottom: 20px;
            right: 20px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
            font-weight: 500;
        }
        
        @media (max-width: 480px) {
            .login-container {
                margin: 20px;
                padding: 40px 30px;
            }
        }
    </style>
</head>
<body>
    <div class="background-animation"></div>
    
    <div class="login-container">
        <div class="logo-section">
            <div class="v7-logo">V7</div>
            <h1 class="system-title">PD Interview System</h1>
            <p class="system-subtitle">Physical Design Assessment Platform</p>
        </div>
        
        <div class="demo-info">
            <h3><i class="fas fa-info-circle"></i> Demo Access</h3>
            <p><span class="role-badge">ADMIN</span> Username: admin</p>
            <p><span class="role-badge">USER</span> Username: eng001 - eng005</p>
            <p><i class="fas fa-key"></i> Password: As provided</p>
        </div>
        
''' + (f'<div class="error"><i class="fas fa-exclamation-triangle"></i>{error}</div>' if error else '') + '''
        
        <form method="POST">
            <div class="form-group">
                <label for="username"><i class="fas fa-user"></i> Username</label>
                <div class="input-wrapper">
                    <i class="fas fa-user"></i>
                    <input type="text" id="username" name="username" placeholder="Enter your username" required>
                </div>
            </div>
            
            <div class="form-group">
                <label for="password"><i class="fas fa-lock"></i> Password</label>
                <div class="input-wrapper">
                    <i class="fas fa-lock"></i>
                    <input type="password" id="password" name="password" placeholder="Enter your password" required>
                </div>
            </div>
            
            <button type="submit" class="login-btn">
                <i class="fas fa-sign-in-alt"></i> Sign In
            </button>
        </form>
    </div>
    
    <div class="version-info">
        V7.0 Professional Edition
    </div>
</body>
</html>'''
    
    return login_html

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
    published = [a for a in all_assignments if a['status'] == 'published']
    
    admin_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>V7 Admin Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f7fafc;
            color: #2d3748;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header-left {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .v7-mini-logo {{
            width: 45px;
            height: 45px;
            background: rgba(255,255,255,0.2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 18px;
        }}
        
        .header-title {{
            font-size: 24px;
            font-weight: 700;
            margin: 0;
        }}
        
        .user-info {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .user-avatar {{
            width: 40px;
            height: 40px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .logout-btn {{
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        }}
        
        .logout-btn:hover {{
            background: rgba(255,255,255,0.2);
        }}
        
        .container {{
            max-width: 1400px;
            margin: 30px auto;
            padding: 0 20px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            text-align: center;
            border: 1px solid #e2e8f0;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
        }}
        
        .stat-icon {{
            width: 60px;
            height: 60px;
            margin: 0 auto 15px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: white;
        }}
        
        .stat-icon.engineers {{ background: linear-gradient(135deg, #4299e1, #3182ce); }}
        .stat-icon.assignments {{ background: linear-gradient(135deg, #48bb78, #38a169); }}
        .stat-icon.pending {{ background: linear-gradient(135deg, #ed8936, #dd6b20); }}
        .stat-icon.completed {{ background: linear-gradient(135deg, #9f7aea, #805ad5); }}
        
        .stat-number {{
            font-size: 36px;
            font-weight: 800;
            color: #2d3748;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #718096;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .dashboard-card {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            border: 1px solid #e2e8f0;
            overflow: hidden;
        }}
        
        .card-header {{
            padding: 25px 30px;
            border-bottom: 1px solid #e2e8f0;
            background: #f7fafc;
        }}
        
        .card-header h2 {{
            font-size: 20px;
            font-weight: 700;
            color: #2d3748;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .card-content {{
            padding: 30px;
        }}
        
        .assignment-grid {{
            display: grid;
            gap: 20px;
        }}
        
        .assignment-card {{
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            padding: 25px;
            border-radius: 16px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .assignment-card:hover {{
            border-color: #cbd5e0;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        
        .assignment-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}
        
        .assignment-title {{
            font-size: 18px;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 8px;
        }}
        
        .assignment-id {{
            font-size: 12px;
            color: #718096;
            font-family: monospace;
            background: #e2e8f0;
            padding: 4px 8px;
            border-radius: 6px;
        }}
        
        .assignment-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .detail-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #4a5568;
        }}
        
        .detail-item i {{
            color: #718096;
            width: 16px;
        }}
        
        .status-badge {{
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: absolute;
            top: 20px;
            right: 20px;
        }}
        
        .status-badge.pending {{
            background: #fed7d7;
            color: #c53030;
        }}
        
        .status-badge.submitted {{
            background: #bee3f8;
            color: #2b6cb0;
        }}
        
        .status-badge.published {{
            background: #c6f6d5;
            color: #22543d;
        }}
        
        .score-display {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 12px;
            text-align: center;
            margin-top: 15px;
        }}
        
        .score-number {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .score-percentage {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .btn-start {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
        }}
        
        .btn-start:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(72, 187, 120, 0.4);
            text-decoration: none;
            color: white;
        }}
        
        .submitted-indicator {{
            background: #bee3f8;
            color: #2b6cb0;
            padding: 15px 20px;
            border-radius: 12px;
            text-align: center;
            margin-top: 15px;
            font-weight: 600;
        }}
        
        .notification-item {{
            background: #e6fffa;
            border: 1px solid #b2f5ea;
            padding: 20px;
            margin: 15px 0;
            border-radius: 12px;
            border-left: 4px solid #38b2ac;
        }}
        
        .notification-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }}
        
        .notification-title {{
            font-weight: 600;
            color: #234e52;
        }}
        
        .notification-date {{
            font-size: 12px;
            color: #4a5568;
            margin-left: auto;
        }}
        
        .notification-message {{
            color: #2d3748;
            font-size: 14px;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #718096;
        }}
        
        .empty-state i {{
            font-size: 48px;
            margin-bottom: 20px;
            color: #cbd5e0;
        }}
        
        .empty-state h3 {{
            font-size: 18px;
            margin-bottom: 10px;
            color: #4a5568;
        }}
        
        @media (max-width: 768px) {{
            .header-content {{
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }}
            
            .assignment-details {{
                grid-template-columns: 1fr;
                gap: 10px;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="header-left">
                <div class="v7-mini-logo">V7</div>
                <h1 class="header-title">Student Dashboard</h1>
            </div>
            <div class="user-info">
                <div class="user-avatar">
                    <i class="fas fa-user-graduate"></i>
                </div>
                <div>
                    <div style="font-weight: 600;">{session['display_name']}</div>
                    <div style="font-size: 12px; opacity: 0.8;">{session['department']}</div>
                </div>
                <a href="/logout" class="logout-btn">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon total">
                    <i class="fas fa-clipboard-list"></i>
                </div>
                <div class="stat-number">{len(my_assignments)}</div>
                <div class="stat-label">Total Assignments</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon completed">
                    <i class="fas fa-check-circle"></i>
                </div>
                <div class="stat-number">{len(completed_assignments)}</div>
                <div class="stat-label">Completed</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon average">
                    <i class="fas fa-chart-line"></i>
                </div>
                <div class="stat-number">{avg_score}</div>
                <div class="stat-label">Average Score</div>
            </div>
        </div>
        
        <div class="dashboard-card">
            <div class="card-header">
                <h2><i class="fas fa-tasks"></i> My Assignments</h2>
            </div>
            <div class="card-content">'''
    
    if my_assignments:
        sorted_assignments = sorted(my_assignments, key=lambda x: x['created_date'], reverse=True)
        for assignment in sorted_assignments:
            status = assignment['status']
            due_date = assignment['due_date'][:10] if assignment['due_date'] else 'No due date'
            
            student_html += f'''
            <div class="assignment-card">
                <span class="status-badge {status}">{status}</span>
                
                <div class="assignment-header">
                    <div>
                        <div class="assignment-title">{assignment["topic"].title()} Assessment</div>
                        <div class="assignment-id">{assignment["id"]}</div>
                    </div>
                </div>
                
                <div class="assignment-details">
                    <div class="detail-item">
                        <i class="fas fa-calendar"></i>
                        <span>Due: {due_date}</span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-clock"></i>
                        <span>Created: {assignment["created_date"][:10]}</span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-question-circle"></i>
                        <span>15 Questions</span>
                    </div>
                </div>'''
            
            if status == 'published':
                score = assignment.get('total_score', 0)
                percentage = round((score / 150) * 100, 1)
                student_html += f'''
                <div class="score-display">
                    <div class="score-number">{score}/150</div>
                    <div class="score-percentage">{percentage}% Score</div>
                </div>'''
            elif status == 'pending':
                student_html += f'''
                <a href="/student/assignment/{assignment["id"]}" class="btn-start">
                    <i class="fas fa-play"></i> Start Assignment
                </a>'''
            elif status == 'submitted':
                student_html += '''
                <div class="submitted-indicator">
                    <i class="fas fa-check"></i> Submitted - Awaiting Review
                </div>'''
            
            student_html += '</div>'
    else:
        student_html += '''
        <div class="empty-state">
            <i class="fas fa-clipboard"></i>
            <h3>No Assignments Yet</h3>
            <p>Your assignments will appear here when they are created by your administrator.</p>
        </div>'''
    
    student_html += '''
            </div>
        </div>
        
        <div class="dashboard-card">
            <div class="card-header">
                <h2><i class="fas fa-bell"></i> Recent Notifications</h2>
            </div>
            <div class="card-content">'''
    
    if my_notifications:
        recent_notifications = sorted(my_notifications, key=lambda x: x['created_at'], reverse=True)[:5]
        for notification in recent_notifications:
            student_html += f'''
            <div class="notification-item">
                <div class="notification-header">
                    <i class="fas fa-info-circle"></i>
                    <span class="notification-title">{notification["title"]}</span>
                    <span class="notification-date">{notification["created_at"][:10]}</span>
                </div>
                <div class="notification-message">{notification["message"]}</div>
            </div>'''
    else:
        student_html += '''
        <div class="empty-state">
            <i class="fas fa-bell-slash"></i>
            <h3>No Notifications</h3>
            <p>Your notifications will appear here.</p>
        </div>'''
    
    student_html += '''
            </div>
        </div>
    </div>
</body>
</html>'''
    
    return student_html

@app.route('/student/assignment/<assignment_id>', methods=['GET', 'POST'])
def student_assignment(assignment_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    assignment = assignments.get(assignment_id)
    if not assignment or assignment['engineer_id'] != session['user_id']:
        return redirect('/student')
    
    if assignment['status'] != 'pending':
        return redirect('/student')
    
    if request.method == 'POST':
        # Save answers
        answers = {}
        all_answered = True
        
        for i in range(15):
            answer = request.form.get(f'answer_{i}', '').strip()
            if answer and len(answer) >= 10:  # Minimum answer length
                answers[str(i)] = answer
            else:
                all_answered = False
        
        if all_answered and len(answers) == 15:
            assignment['answers'] = answers
            assignment['status'] = 'submitted'
            assignment['submitted_date'] = datetime.now().isoformat()
            
            # Calculate auto scores
            auto_scores = {}
            for i in range(15):
                auto_scores[str(i)] = calculate_auto_score(answers[str(i)], assignment['topic'])
            assignment['auto_scores'] = auto_scores
            
        return redirect('/student')
    
    # Professional assignment interface
    user = users.get(session['user_id'], {})
    assignment_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>V7 Assessment - {assignment["topic"].title()}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f7fafc;
            color: #2d3748;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 25px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .header-content {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 0 20px;
            text-align: center;
        }}
        
        .header-title {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .header-subtitle {{
            opacity: 0.9;
            font-size: 16px;
        }}
        
        .progress-container {{
            background: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 99;
        }}
        
        .progress-content {{
            max-width: 1000px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .progress-bar-container {{
            flex: 1;
            background: #e2e8f0;
            height: 12px;
            border-radius: 6px;
            overflow: hidden;
        }}
        
        .progress-bar {{
            height: 100%;
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            width: 0%;
            transition: width 0.3s ease;
        }}
        
        .progress-text {{
            font-weight: 600;
            color: #2d3748;
            white-space: nowrap;
        }}
        
        .timer {{
            background: #e6fffa;
            color: #234e52;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 30px auto;
            padding: 0 20px;
        }}
        
        .navigation {{
            margin-bottom: 30px;
        }}
        
        .back-btn {{
            background: #718096;
            color: white;
            padding: 12px 20px;
            text-decoration: none;
            border-radius: 10px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .back-btn:hover {{
            background: #4a5568;
            transform: translateY(-1px);
        }}
        
        .instructions {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            border: 2px solid #e6fffa;
            border-left: 6px solid #48bb78;
        }}
        
        .instructions h3 {{
            color: #2d3748;
            margin-bottom: 20px;
            font-size: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .instructions ul {{
            list-style: none;
            padding: 0;
        }}
        
        .instructions li {{
            padding: 8px 0;
            display: flex;
            align-items: center;
            gap: 12px;
            color: #4a5568;
        }}
        
        .instructions li i {{
            color: #48bb78;
            width: 16px;
        }}
        
        .question-card {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            overflow: hidden;
            border: 1px solid #e2e8f0;
        }}
        
        .question-header {{
            background: #f7fafc;
            padding: 25px 30px;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .question-number {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 15px;
        }}
        
        .question-text {{
            font-size: 16px;
            line-height: 1.7;
            color: #2d3748;
            font-weight: 500;
        }}
        
        .answer-section {{
            padding: 30px;
        }}
        
        .answer-label {{
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .textarea-container {{
            position: relative;
        }}
        
        textarea {{
            width: 100%;
            min-height: 150px;
            padding: 20px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 15px;
            font-family: inherit;
            line-height: 1.6;
            resize: vertical;
            transition: all 0.3s ease;
        }}
        
        textarea:focus {{
            outline: none;
            border-color: #48bb78;
            box-shadow: 0 0 0 3px rgba(72, 187, 120, 0.1);
        }}
        
        .char-count {{
            position: absolute;
            bottom: 10px;
            right: 15px;
            font-size: 12px;
            color: #718096;
            background: rgba(255,255,255,0.9);
            padding: 4px 8px;
            border-radius: 4px;
        }}
        
        .auto-save-indicator {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #48bb78;
            color: white;
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            transform: translateY(100px);
            transition: transform 0.3s ease;
            z-index: 1000;
        }}
        
        .auto-save-indicator.show {{
            transform: translateY(0);
        }}
        
        .submit-section {{
            background: white;
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            margin-top: 30px;
        }}
        
        .submit-btn {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 18px 40px;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
            disabled: true;
        }}
        
        .submit-btn:enabled {{
            cursor: pointer;
        }}
        
        .submit-btn:disabled {{
            background: #cbd5e0;
            color: #718096;
            box-shadow: none;
            cursor: not-allowed;
        }}
        
        .submit-btn:enabled:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(72, 187, 120, 0.4);
        }}
        
        .completion-status {{
            margin-top: 15px;
            font-size: 14px;
            color: #718096;
        }}
        
        @media (max-width: 768px) {{
            .progress-content {{
                flex-direction: column;
                gap: 10px;
            }}
            
            .question-card {{
                margin-bottom: 20px;
            }}
            
            .question-header,
            .answer-section {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1 class="header-title">{assignment["topic"].title()} Assessment</h1>
            <p class="header-subtitle">Physical Design Technical Evaluation • 15 Questions • 150 Points Total</p>
        </div>
    </div>
    
    <div class="progress-container">
        <div class="progress-content">
            <div class="progress-bar-container">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <div class="progress-text" id="progressText">0/15 Complete</div>
            <div class="timer" id="timer">⏱️ 00:00:00</div>
        </div>
    </div>
    
    <div class="container">
        <div class="navigation">
            <a href="/student" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
        </div>
        
        <div class="instructions">
            <h3><i class="fas fa-info-circle"></i> Assessment Instructions</h3>
            <ul>
                <li><i class="fas fa-check"></i> Answer all 15 questions with detailed technical explanations</li>
                <li><i class="fas fa-star"></i> Each question is worth 10 points (150 points total)</li>
                <li><i class="fas fa-lightbulb"></i> Include specific examples, methodologies, and technical details</li>
                <li><i class="fas fa-save"></i> Your progress is automatically saved every 30 seconds</li>
                <li><i class="fas fa-clock"></i> Take your time - quality answers are more important than speed</li>
                <li><i class="fas fa-paper-plane"></i> Submit only when all questions are thoroughly answered</li>
            </ul>
        </div>
        
        <form method="POST" id="assignmentForm">'''
    
    for i, question in enumerate(assignment['questions']):
        assignment_html += f'''
        <div class="question-card">
            <div class="question-header">
                <div class="question-number">Question {i+1} of 15</div>
                <div class="question-text">{question}</div>
            </div>
            <div class="answer-section">
                <div class="answer-label">
                    <i class="fas fa-pen"></i> Your Answer:
                </div>
                <div class="textarea-container">
                    <textarea 
                        name="answer_{i}" 
                        id="answer_{i}"
                        placeholder="Provide a detailed technical answer here. Include specific methodologies, tools, techniques, and examples from your experience..."
                        required
                        oninput="updateProgress(); updateCharCount(this, 'count_{i}'); autoSave();"
                    ></textarea>
                    <div class="char-count" id="count_{i}">0 characters</div>
                </div>
            </div>
        </div>'''
    
    assignment_html += '''
        </form>
        
        <div class="submit-section">
            <button type="submit" form="assignmentForm" class="submit-btn" id="submitBtn" disabled>
                <i class="fas fa-paper-plane"></i> Submit Assessment
            </button>
            <div class="completion-status" id="completionStatus">
                Complete all questions to enable submission
            </div>
        </div>
    </div>
    
    <div class="auto-save-indicator" id="autoSaveIndicator">
        <i class="fas fa-save"></i> Auto-saved
    </div>
    
    <script>
        let startTime = Date.now();
        let autoSaveTimeout;
        
        // Timer functionality
        function updateTimer() {
            const elapsed = Date.now() - startTime;
            const hours = Math.floor(elapsed / 3600000);
            const minutes = Math.floor((elapsed % 3600000) / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            
            document.getElementById('timer').innerHTML = 
                `⏱️ ${hours.toString().padStart(2,'0')}:${minutes.toString().padStart(2,'0')}:${seconds.toString().padStart(2,'0')}`;
        }
        
        // Update timer every second
        setInterval(updateTimer, 1000);
        
        // Progress tracking
        function updateProgress() {
            const textareas = document.querySelectorAll('textarea');
            let completed = 0;
            
            textareas.forEach(textarea => {
                if (textarea.value.trim().length >= 50) { // Minimum 50 characters for substantial answer
                    completed++;
                }
            });
            
            const progress = (completed / textareas.length) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
            document.getElementById('progressText').textContent = `${completed}/15 Complete`;
            
            // Enable submit button only when all questions have substantial answers
            const submitBtn = document.getElementById('submitBtn');
            const statusText = document.getElementById('completionStatus');
            
            if (completed === textareas.length) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Assessment';
                statusText.textContent = 'Ready to submit! Review your answers before submitting.';
                statusText.style.color = '#48bb78';
            } else {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<i class="fas fa-edit"></i> Complete ${textareas.length - completed} more questions`;
                statusText.textContent = `Complete ${textareas.length - completed} more questions to enable submission`;
                statusText.style.color = '#718096';
            }
        }
        
        // Character counting
        function updateCharCount(textarea, countId) {
            const count = textarea.value.length;
            const element = document.getElementById(countId);
            element.textContent = count + ' characters';
            
            // Color coding based on length
            if (count < 50) {
                element.style.color = '#e53e3e';
            } else if (count < 200) {
                element.style.color = '#dd6b20';
            } else {
                element.style.color = '#38a169';
            }
        }
        
        // Auto-save functionality
        function autoSave() {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                const formData = new FormData(document.getElementById('assignmentForm'));
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                localStorage.setItem('assignment_{assignment_id}', JSON.stringify(data));
                
                // Show auto-save indicator
                const indicator = document.getElementById('autoSaveIndicator');
                indicator.classList.add('show');
                setTimeout(() => indicator.classList.remove('show'), 2000);
            }, 2000);
        }
        
        // Load saved data on page load
        window.addEventListener('load', function() {
            const saved = localStorage.getItem('assignment_{assignment_id}');
            if (saved) {
                const data = JSON.parse(saved);
                for (let key in data) {
                    const element = document.querySelector(`[name="${key}"]`);
                    if (element) {
                        element.value = data[key];
                        const countId = key.replace('answer_', 'count_');
                        updateCharCount(element, countId);
                    }
                }
                updateProgress();
            }
        });
        
        // Auto-save every 30 seconds
        setInterval(() => {
            const textareas = document.querySelectorAll('textarea');
            let hasContent = false;
            textareas.forEach(textarea => {
                if (textarea.value.trim().length > 0) hasContent = true;
            });
            if (hasContent) autoSave();
        }, 30000);
        
        // Prevent accidental page close
        window.addEventListener('beforeunload', function(e) {
            const textareas = document.querySelectorAll('textarea');
            let hasUnsavedChanges = false;
            textareas.forEach(textarea => {
                if (textarea.value.trim().length > 0) hasUnsavedChanges = true;
            });
            
            if (hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            }
        });
        
        // Form submission confirmation
        document.getElementById('assignmentForm').addEventListener('submit', function(e) {
            const confirmed = confirm('Are you sure you want to submit your assessment? You cannot make changes after submission.');
            if (!confirmed) {
                e.preventDefault();
            } else {
                // Clear auto-save data on successful submission
                localStorage.removeItem('assignment_{assignment_id}');
            }
        });
        
        // Initialize progress on load
        updateProgress();
    </script>
</body>
</html>'''
    
    return assignment_html

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>404 - Page Not Found</title>
        <style>
            body { 
                font-family: 'Inter', sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                text-align: center; 
                padding: 100px 20px;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .error-container {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(20px);
                padding: 50px;
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            h1 { font-size: 72px; margin-bottom: 20px; }
            p { font-size: 18px; margin-bottom: 30px; }
            a { 
                color: white; 
                background: rgba(255,255,255,0.2);
                padding: 12px 24px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            a:hover { background: rgba(255,255,255,0.3); }
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1>404</h1>
            <p>Page Not Found</p>
            <a href="/">← Return to Home</a>
        </div>
    </body>
    </html>
    ''', 404

@app.errorhandler(500)
def internal_error(error):
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>500 - Internal Error</title>
        <style>
            body { 
                font-family: 'Inter', sans-serif; 
                background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%);
                color: white; 
                text-align: center; 
                padding: 100px 20px;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .error-container {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(20px);
                padding: 50px;
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            h1 { font-size: 72px; margin-bottom: 20px; }
            p { font-size: 18px; margin-bottom: 30px; }
            a { 
                color: white; 
                background: rgba(255,255,255,0.2);
                padding: 12px 24px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            a:hover { background: rgba(255,255,255,0.3); }
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1>500</h1>
            <p>Internal Server Error</p>
            <a href="/">← Return to Home</a>
        </div>
    </body>
    </html>
    ''', 500

# Initialize users on startup
init_users()

# Additional API endpoints for future enhancements
@app.route('/api/stats')
def api_stats():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    all_assignments = list(assignments.values())
    engineers = [u for u in users.values() if not u.get('is_admin')]
    
    stats = {
        'total_engineers': len(engineers),
        'total_assignments': len(all_assignments),
        'pending_assignments': len([a for a in all_assignments if a['status'] == 'pending']),
        'submitted_assignments': len([a for a in all_assignments if a['status'] == 'submitted']),
        'published_assignments': len([a for a in all_assignments if a['status'] == 'published']),
        'average_score': 0
    }
    
    published = [a for a in all_assignments if a['status'] == 'published' and a.get('total_score')]
    if published:
        stats['average_score'] = round(sum(a['total_score'] for a in published) / len(published), 1)
    
    return jsonify(stats)

@app.route('/ping')
def ping():
    return jsonify({
        'status': 'healthy',
        'version': '7.0',
        'timestamp': datetime.now().isoformat(),
        'message': 'V7 PD Interview System is running'
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Security: Don't print sensitive information
    print("🚀 V7 PD Interview System Starting...")
    print(f"📍 Running on port {port}")
    print("✅ Ready for connections")
    app.run(host='0.0.0.0', port=port, debug=False)weight: 500;
            font-size: 14px;
        }}
        
        .dashboard-card {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            border: 1px solid #e2e8f0;
            overflow: hidden;
        }}
        
        .card-header {{
            padding: 25px 30px;
            border-bottom: 1px solid #e2e8f0;
            background: #f7fafc;
        }}
        
        .card-header h2 {{
            font-size: 20px;
            font-weight: 700;
            color: #2d3748;
            margin: 0;
        }}
        
        .card-content {{
            padding: 30px;
        }}
        
        .form-row {{
            display: grid;
            grid-template-columns: 1fr 1fr auto;
            gap: 20px;
            align-items: end;
        }}
        
        .form-group {{
            display: flex;
            flex-direction: column;
        }}
        
        .form-group label {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #4a5568;
            font-size: 14px;
        }}
        
        select {{
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 14px;
            background: white;
            transition: border-color 0.3s ease;
        }}
        
        select:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }}
        
        .assignment-item {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 25px;
            margin: 15px 0;
            border-radius: 12px;
            transition: all 0.3s ease;
        }}
        
        .assignment-item:hover {{
            border-color: #cbd5e0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .assignment-header {{
            display: flex;
            justify-content: between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}
        
        .assignment-id {{
            font-weight: 700;
            color: #2d3748;
            font-size: 16px;
            margin-bottom: 8px;
        }}
        
        .assignment-details {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .detail-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 14px;
            color: #718096;
        }}
        
        .status-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .status-badge.pending {{ background: #fed7d7; color: #c53030; }}
        .status-badge.submitted {{ background: #bee3f8; color: #2b6cb0; }}
        .status-badge.published {{ background: #c6f6d5; color: #22543d; }}
        
        .btn-review {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            transition: all 0.3s ease;
        }}
        
        .btn-review:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #718096;
        }}
        
        .empty-state i {{
            font-size: 48px;
            margin-bottom: 20px;
            color: #cbd5e0;
        }}
        
        @media (max-width: 768px) {{
            .form-row {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
            
            .header-content {{
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }}
            
            .assignment-details {{
                flex-direction: column;
                gap: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="header-left">
                <div class="v7-mini-logo">V7</div>
                <h1 class="header-title">Admin Dashboard</h1>
            </div>
            <div class="user-info">
                <div class="user-avatar">
                    <i class="fas fa-user-shield"></i>
                </div>
                <div>
                    <div style="font-weight: 600;">{session['display_name']}</div>
                    <div style="font-size: 12px; opacity: 0.8;">{session['department']}</div>
                </div>
                <a href="/logout" class="logout-btn">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon engineers">
                    <i class="fas fa-users"></i>
                </div>
                <div class="stat-number">{len(engineers)}</div>
                <div class="stat-label">Active Engineers</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon assignments">
                    <i class="fas fa-clipboard-list"></i>
                </div>
                <div class="stat-number">{len(all_assignments)}</div>
                <div class="stat-label">Total Assignments</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon pending">
                    <i class="fas fa-clock"></i>
                </div>
                <div class="stat-number">{len(submitted)}</div>
                <div class="stat-label">Pending Review</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon completed">
                    <i class="fas fa-check-circle"></i>
                </div>
                <div class="stat-number">{len(published)}</div>
                <div class="stat-label">Completed</div>
            </div>
        </div>
        
        <div class="dashboard-card">
            <div class="card-header">
                <h2><i class="fas fa-plus-circle"></i> Create New Assignment</h2>
            </div>
            <div class="card-content">
                <form method="POST" action="/admin/create">
                    <div class="form-row">
                        <div class="form-group">
                            <label><i class="fas fa-user"></i> Select Engineer</label>
                            <select name="engineer_id" required>
                                <option value="">Choose Engineer...</option>'''
    
    for eng in engineers:
        admin_html += f'<option value="{eng["id"]}">{eng["display_name"]} ({eng["id"]})</option>'
    
    admin_html += '''</select>
                        </div>
                        <div class="form-group">
                            <label><i class="fas fa-cogs"></i> Select Assessment Topic</label>
                            <select name="topic" required>
                                <option value="">Choose Topic...</option>
                                <option value="floorplanning">🏗️ Floorplanning (15 Questions)</option>
                                <option value="placement">📐 Placement (15 Questions)</option>
                                <option value="routing">🔌 Routing (15 Questions)</option>
                            </select>
                        </div>
                        <button type="submit" class="btn-primary">
                            <i class="fas fa-paper-plane"></i> Create Assignment
                        </button>
                    </div>
                </form>
            </div>
        </div>
        
        <div class="dashboard-card">
            <div class="card-header">
                <h2><i class="fas fa-clipboard-check"></i> Assignments Pending Review</h2>
            </div>
            <div class="card-content">'''
    
    if submitted:
        for assignment in submitted:
            user = users.get(assignment["engineer_id"], {})
            admin_html += f'''
            <div class="assignment-item">
                <div class="assignment-id">{assignment["id"]}</div>
                <div class="assignment-details">
                    <div class="detail-item">
                        <i class="fas fa-user"></i>
                        <strong>{user.get("display_name", assignment["engineer_id"])}</strong>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-cog"></i>
                        {assignment["topic"].title()}
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-calendar"></i>
                        {assignment.get("created_date", "")[:10]}
                    </div>
                    <div class="detail-item">
                        <span class="status-badge submitted">Submitted</span>
                    </div>
                </div>
                <a href="/admin/review/{assignment["id"]}" class="btn-review">
                    <i class="fas fa-search"></i> Review & Score
                </a>
            </div>'''
    else:
        admin_html += '''
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h3>No Pending Reviews</h3>
                <p>All assignments are either pending completion or already reviewed.</p>
            </div>'''
    
    admin_html += '''
            </div>
        </div>
        
        <div class="dashboard-card">
            <div class="card-header">
                <h2><i class="fas fa-history"></i> Recent Activity</h2>
            </div>
            <div class="card-content">'''
    
    recent_assignments = sorted(all_assignments, key=lambda x: x['created_date'], reverse=True)[:8]
    if recent_assignments:
        for assignment in recent_assignments:
            user = users.get(assignment["engineer_id"], {})
            status_class = {'pending': 'pending', 'submitted': 'submitted', 'published': 'published'}.get(assignment['status'], 'pending')
            admin_html += f'''
            <div class="assignment-item">
                <div class="assignment-id">{assignment["id"]}</div>
                <div class="assignment-details">
                    <div class="detail-item">
                        <i class="fas fa-user"></i>
                        {user.get("display_name", assignment["engineer_id"])}
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-cog"></i>
                        {assignment["topic"].title()}
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-calendar"></i>
                        {assignment["created_date"][:10]}
                    </div>
                    <div class="detail-item">
                        <span class="status-badge {status_class}">{assignment["status"].title()}</span>
                    </div>
                </div>'''
            
            if assignment['status'] == 'published':
                score = assignment.get('total_score', 0)
                percentage = round((score / 150) * 100, 1)
                admin_html += f'<div style="color: #48bb78; font-weight: 600;">Score: {score}/150 ({percentage}%)</div>'
            
            admin_html += '</div>'
    else:
        admin_html += '''
            <div class="empty-state">
                <i class="fas fa-clock"></i>
                <h3>No Recent Activity</h3>
                <p>Assignment activity will appear here.</p>
            </div>'''
    
    admin_html += '''
            </div>
        </div>
    </div>
</body>
</html>'''
    
    return admin_html

@app.route('/admin/create', methods=['POST'])
def admin_create():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')
    
    engineer_id = request.form.get('engineer_id', '').strip()
    topic = request.form.get('topic', '').strip()
    
    if engineer_id and topic and engineer_id in users and topic in QUESTIONS_SET1:
        assignment = create_assignment(engineer_id, topic)
        if assignment:
            # Add success notification (could be implemented with flash messages)
            pass
    
    return redirect('/admin')

@app.route('/admin/review/<assignment_id>', methods=['GET', 'POST'])
def admin_review(assignment_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')
    
    assignment = assignments.get(assignment_id)
    if not assignment:
        return redirect('/admin')
    
    if request.method == 'POST':
        # Calculate and save scores
        total_score = 0
        final_scores = {}
        
        for i in range(15):
            score_str = request.form.get(f'score_{i}', '0')
            try:
                score = max(0, min(int(score_str), 10))  # Ensure score is between 0-10
                final_scores[str(i)] = score
                total_score += score
            except ValueError:
                final_scores[str(i)] = 0
        
        assignment['final_scores'] = final_scores
        assignment['total_score'] = total_score
        assignment['status'] = 'published'
        assignment['scored_by'] = session['display_name']
        assignment['scored_date'] = datetime.now().isoformat()
        
        return redirect('/admin')
    
    # Generate professional review form
    user = users.get(assignment["engineer_id"], {})
    review_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>V7 Review Assignment - {assignment_id}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f7fafc;
            color: #2d3748;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .header-title {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .assignment-meta {{
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            opacity: 0.9;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }}
        
        .navigation {{
            margin-bottom: 30px;
        }}
        
        .back-btn {{
            background: #718096;
            color: white;
            padding: 12px 20px;
            text-decoration: none;
            border-radius: 10px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .back-btn:hover {{
            background: #4a5568;
            transform: translateY(-1px);
        }}
        
        .review-form {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            overflow: hidden;
        }}
        
        .question-card {{
            border-bottom: 1px solid #e2e8f0;
            padding: 30px;
        }}
        
        .question-card:last-child {{
            border-bottom: none;
        }}
        
        .question-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .question-number {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
        }}
        
        .question-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2d3748;
        }}
        
        .question-text {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
            font-size: 15px;
            line-height: 1.7;
        }}
        
        .answer-section {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            border-left: 4px solid #48bb78;
        }}
        
        .answer-label {{
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .answer-text {{
            color: #4a5568;
            line-height: 1.7;
            font-size: 15px;
        }}
        
        .scoring-section {{
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }}
        
        .auto-score {{
            background: #e6fffa;
            color: #234e52;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .manual-score {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .manual-score label {{
            font-weight: 600;
            color: #2d3748;
        }}
        
        .score-input {{
            width: 80px;
            padding: 10px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            text-align: center;
            font-size: 16px;
            font-weight: 600;
            transition: border-color 0.3s ease;
        }}
        
        .score-input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .score-range {{
            color: #718096;
            font-size: 14px;
        }}
        
        .submit-section {{
            background: #f7fafc;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e2e8f0;
        }}
        
        .submit-btn {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 16px 40px;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
        }}
        
        .submit-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(72, 187, 120, 0.4);
        }}
        
        .total-score {{
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .total-display {{
            font-size: 24px;
            font-weight: 700;
            color: #2d3748;
        }}
        
        .total-label {{
            color: #718096;
            margin-top: 5px;
        }}
        
        @media (max-width: 768px) {{
            .assignment-meta {{
                flex-direction: column;
                gap: 10px;
            }}
            
            .scoring-section {{
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1 class="header-title">Review Assignment</h1>
            <div class="assignment-meta">
                <div class="meta-item">
                    <i class="fas fa-id-card"></i>
                    <strong>Assignment:</strong> {assignment_id}
                </div>
                <div class="meta-item">
                    <i class="fas fa-user"></i>
                    <strong>Engineer:</strong> {user.get("display_name", assignment["engineer_id"])}
                </div>
                <div class="meta-item">
                    <i class="fas fa-cog"></i>
                    <strong>Topic:</strong> {assignment["topic"].title()}
                </div>
                <div class="meta-item">
                    <i class="fas fa-calendar"></i>
                    <strong>Submitted:</strong> {assignment.get("created_date", "")[:10]}
                </div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="navigation">
            <a href="/admin" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
        </div>
        
        <form method="POST" class="review-form">
            <div class="total-score">
                <div class="total-display" id="totalScore">0/150</div>
                <div class="total-label">Total Score</div>
            </div>'''
    
    for i, question in enumerate(assignment['questions']):
        answer = assignment.get('answers', {}).get(str(i), 'No answer provided')
        auto_score = calculate_auto_score(answer, assignment['topic'])
        
        review_html += f'''
        <div class="question-card">
            <div class="question-header">
                <div class="question-number">{i+1}</div>
                <div class="question-title">Question {i+1} of 15</div>
            </div>
            
            <div class="question-text">
                {question}
            </div>
            
            <div class="answer-section">
                <div class="answer-label">
                    <i class="fas fa-pen"></i> Candidate's Answer:
                </div>
                <div class="answer-text">{answer}</div>
            </div>
            
            <div class="scoring-section">
                <div class="auto-score">
                    <i class="fas fa-robot"></i>
                    Auto-Score: {auto_score}/10
                </div>
                
                <div class="manual-score">
                    <label for="score_{i}">Your Score:</label>
                    <input type="number" 
                           class="score-input" 
                           name="score_{i}" 
                           id="score_{i}"
                           min="0" 
                           max="10" 
                           value="{auto_score}" 
                           onchange="updateTotalScore()"
                           required>
                    <span class="score-range">/10</span>
                </div>
            </div>
        </div>'''
    
    review_html += '''
            <div class="submit-section">
                <button type="submit" class="submit-btn">
                    <i class="fas fa-check-circle"></i> Submit Final Scores
                </button>
            </div>
        </form>
    </div>
    
    <script>
        function updateTotalScore() {
            let total = 0;
            for (let i = 0; i < 15; i++) {
                const input = document.getElementById(`score_${i}`);
                const value = parseInt(input.value) || 0;
                total += Math.max(0, Math.min(value, 10));
            }
            
            const percentage = Math.round((total / 150) * 100);
            document.getElementById('totalScore').textContent = `${total}/150 (${percentage}%)`;
        }
        
        // Initialize total score
        updateTotalScore();
        
        // Add input validation
        document.querySelectorAll('.score-input').forEach(input => {
            input.addEventListener('input', function() {
                let value = parseInt(this.value);
                if (value < 0) this.value = 0;
                if (value > 10) this.value = 10;
                updateTotalScore();
            });
        });
    </script>
</body>
</html>'''
    
    return review_html

@app.route('/student')
def student_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    user = users.get(user_id, {})
    my_assignments = [a for a in assignments.values() if a['engineer_id'] == user_id]
    my_notifications = notifications.get(user_id, [])
    
    # Calculate statistics
    completed_assignments = [a for a in my_assignments if a['status'] == 'published']
    avg_score = 0
    if completed_assignments:
        total_score = sum(a.get('total_score', 0) for a in completed_assignments)
        avg_score = round(total_score / len(completed_assignments), 1)
    
    student_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>V7 Student Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f7fafc;
            color: #2d3748;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 25px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header-left {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .v7-mini-logo {{
            width: 45px;
            height: 45px;
            background: rgba(255,255,255,0.2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 18px;
        }}
        
        .header-title {{
            font-size: 24px;
            font-weight: 700;
            margin: 0;
        }}
        
        .user-info {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .user-avatar {{
            width: 45px;
            height: 45px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }}
        
        .logout-btn {{
            color: white;
            text-decoration: none;
            padding: 10px 16px;
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            transition: all 0.3s ease;
            font-weight: 500;
        }}
        
        .logout-btn:hover {{
            background: rgba(255,255,255,0.2);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            text-align: center;
            border: 1px solid #e2e8f0;
        }}
        
        .stat-icon {{
            width: 50px;
            height: 50px;
            margin: 0 auto 15px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: white;
        }}
        
        .stat-icon.total {{ background: linear-gradient(135deg, #4299e1, #3182ce); }}
        .stat-icon.completed {{ background: linear-gradient(135deg, #48bb78, #38a169); }}
        .stat-icon.average {{ background: linear-gradient(135deg, #ed8936, #dd6b20); }}
        
        .stat-number {{
            font-size: 24px;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #718096;
            font-
