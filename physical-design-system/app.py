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

# Questions - 15 per topic, 3+ experience level (NEW QUESTIONS - 3 SETS OF 5 EACH)
QUESTIONS = {
    "floorplanning": [
        # Set 1 (Questions 1-5)
        "Your chip has 8 voltage domains with different power requirements (1.8V, 1.2V, 0.9V, 0.6V). Design a floorplan strategy that minimizes the number of level shifters while ensuring proper power delivery. What are the key considerations for domain boundary placement?",
        "You're working on a 7nm design with double patterning requirements. How would you modify your floorplan approach to handle SRAM compiler restrictions and ensure routing feasibility across different metal layers?",
        "Your design requires 15 different clock domains with frequencies ranging from 50MHz to 2GHz. Describe your floorplanning strategy to minimize clock skew and reduce power consumption from clock distribution networks.",
        "During floorplan optimization, you discover that your critical timing paths have excessive wire delays due to poor macro placement. What systematic approach would you use to relocate macros while maintaining area efficiency?",
        "Your mixed-signal design has 6 ADCs requiring 80dB PSRR and 4 PLLs sensitive to substrate noise. How would you plan the floorplan to achieve isolation requirements while optimizing for routability and thermal management?",
        
        # Set 2 (Questions 6-10)
        "You need to implement power gating for 12 different functional blocks with varying wake-up time requirements. How would you organize the floorplan to minimize the impact on timing closure and power grid design?",
        "Your design has temperature hotspots exceeding 125°C in simulation. What floorplan modifications would you implement to improve thermal distribution, and how would you validate the thermal impact of your changes?",
        "You're tasked with creating a hierarchical floorplan for a multi-core processor with 8 identical cores plus shared L3 cache. Describe your approach to balance area efficiency, thermal considerations, and inter-core communication latency.",
        "Your floorplan review shows that 30% of nets will require more than 3 routing layers due to congestion. What specific floorplan adjustments would you make to reduce routing complexity while maintaining functional correctness?",
        "You have a design with 20 high-speed differential pairs (10Gbps+) that must maintain controlled impedance. How would you plan the floorplan to ensure signal integrity requirements are met while optimizing for area and power?",
        
        # Set 3 (Questions 11-15)
        "Your SoC design has 25 different IP blocks with varying power consumption patterns. How would you create a power-aware floorplan that enables dynamic voltage and frequency scaling while maintaining timing closure across all operating modes?",
        "You're implementing a chiplet-based design with 4 compute dies and 1 I/O die. What are the key floorplanning considerations for inter-die communication, thermal coupling, and mechanical stress distribution across the package?",
        "Your design has 200+ clock gating cells distributed across the chip. Describe your floorplanning strategy to optimize clock gating effectiveness while minimizing clock tree power and ensuring proper enable signal timing.",
        "You need to floorplan a design with 50 different voltage and frequency islands for ultra-low power operation. How would you handle the complexity of multiple power domains, retention strategies, and isolation cell placement?",
        "Your automotive chip requires functional safety compliance with redundant processing units. How would you floorplan for fault isolation, redundancy implementation, and failure mode analysis while meeting area and power targets?"
    ],
    "placement": [
        # Set 1 (Questions 1-5)
        "Your placement results show 500+ timing violations with the worst negative slack of -200ps on critical paths. Develop a systematic recovery plan that addresses both setup and hold timing without significantly impacting power or area.",
        "You're implementing a design with 50,000+ flip-flops across 15 clock domains. Describe your placement strategy to minimize clock power while ensuring timing closure and managing clock domain crossing requirements.",
        "Your design has 300 high-fanout nets (fanout >1000) causing placement convergence issues. What specific techniques would you employ to handle these nets during global and detailed placement phases?",
        "After placement, your power analysis shows 40% higher dynamic power than target due to excessive switching activity. How would you modify your placement approach to reduce power while maintaining performance targets?",
        "You're working with a multi-Vt design using 4 different threshold voltage options (ULVT, LVT, RVT, HVT). Explain your placement optimization strategy to balance timing, power, and leakage requirements.",
        
        # Set 2 (Questions 6-10)
        "Your design requires implementing scan chains with specific capture and shift mode timing requirements. How would you optimize placement to minimize impact on functional timing while meeting DFT constraints?",
        "You have a design with 1000+ memory instances of varying sizes that need to be placed optimally. What factors would you consider for memory placement, and how would you handle the interaction with logic placement?",
        "Your placement shows routing congestion exceeding 85% utilization in 25% of the chip area. What placement techniques would you use to redistribute logic and improve routability without timing degradation?",
        "You're implementing clock gating with 800+ ICG cells that need optimal placement for both power savings and timing closure. Describe your methodology for ICG placement and its impact on overall design optimization.",
        "Your design has critical nets with max transition time violations after placement. How would you address these violations through placement adjustments, buffer insertion, and driver sizing strategies?",
        
        # Set 3 (Questions 11-15)
        "You're placing a machine learning accelerator with 10,000+ MAC units that have specific dataflow patterns. How would you optimize placement to minimize interconnect latency and maximize compute throughput while managing power density?",
        "Your design has 150+ power switches for fine-grained power gating. Describe your placement strategy to minimize power switch overhead while ensuring adequate current delivery and meeting wake-up time requirements.",
        "You need to place a design with 500+ high-speed I/O pads around the periphery. How would you optimize the placement of I/O logic and buffers to minimize simultaneous switching noise and ensure signal integrity?",
        "Your placement run shows 2000+ antenna violations during preliminary routing estimation. What placement modifications would you implement to reduce antenna accumulation while maintaining timing and congestion targets?",
        "You're implementing a safety-critical design with TMR (Triple Modular Redundancy) logic. How would you place the redundant modules to maximize fault isolation while minimizing area overhead and maintaining timing correlation?"
    ],
    "routing": [
        # Set 1 (Questions 1-5)
        "Your detailed routing shows 2000+ DRC violations including minimum spacing, via enclosure, and metal density issues. Create a systematic debugging and resolution strategy that prioritizes violations by impact and difficulty.",
        "You're routing a high-speed DDR5 interface with 64 data lines requiring length matching within ±10ps and controlled impedance of 50Ω ±10%. Describe your routing methodology and verification approach.",
        "Your design has 50 critical nets showing crosstalk-induced timing violations exceeding 30ps. What routing techniques would you implement to reduce coupling while maintaining routability and meeting timing requirements?",
        "After routing completion, you discover 15% of your design has metal density violations that could impact manufacturing yield. How would you address these violations through routing modifications and fill strategies?",
        "Your power delivery network requires handling 150A peak current with IR drop <50mV across the chip. Design your power routing strategy including layer assignment, via sizing, and current density management.",
        
        # Set 2 (Questions 6-10)
        "You're implementing a clock distribution network for a 1.5GHz design with 25,000 flip-flops requiring <25ps skew. Describe your clock routing methodology, including tree synthesis and skew optimization techniques.",
        "Your routing has 200+ electromigration violations on critical power and signal nets. What modifications would you make to via sizing, wire widths, and current path optimization to resolve these issues?",
        "You need to route in a 5nm process with quadruple patterning on critical layers. Explain how you would handle the decomposition challenges and ensure manufacturability while maintaining performance targets.",
        "Your design has 100+ antenna violations that could cause gate oxide damage during manufacturing. What routing strategies would you implement to prevent antenna accumulation during the fabrication process?",
        "You're routing a mixed-signal design where digital switching noise is coupling into sensitive analog circuits, causing 20dB degradation in SNR. How would you modify your routing approach to achieve the required isolation?",
        
        # Set 3 (Questions 11-15)
        "Your high-speed SerDes design requires routing 32 differential pairs at 25Gbps with strict jitter requirements. Describe your routing strategy for maintaining signal integrity, including layer stackup considerations and crosstalk mitigation.",
        "You need to route a design with 1000+ power domains requiring individual power gating controls. How would you handle the routing complexity of power switches, isolation signals, and retention power while minimizing area overhead?",
        "Your routing is failing convergence due to 5000+ short violations in dense standard cell regions. What routing parameter adjustments and design modifications would you implement to achieve 100% routing completion?",
        "You're routing a 3D IC with through-silicon vias (TSVs) connecting 4 stacked dies. Describe your routing methodology for managing inter-die connections, thermal considerations, and yield optimization across the stack.",
        "Your design has 500+ critical nets requiring redundant routing for fault tolerance. How would you implement redundant path routing while managing area overhead, delay matching, and failure mode isolation?"
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
    
    # 9 Engineers with actual names
    engineer_data = [
        ('eng001', 'Kranthi & Neela'),
        ('eng002', 'Bhanu & Lokeshwari'),
        ('eng003', 'Nagesh & VJ'),
        ('eng004', 'Pravalika & Daniel'),
        ('eng005', 'Karthik & Hema'),
        ('eng006', 'Naveen & Srinivas'),
        ('eng007', 'Meera & Suraj'),
        ('eng008', 'Akhil & Vikas'),
        ('eng009', 'Sahith & Sravan')
    ]
    
    for uid, display_name in engineer_data:
        users[uid] = {
            'id': uid,
            'username': uid,
            'display_name': display_name,
            'password': hash_pass('password123'),
            'is_admin': False,
            'exp': 3 + (int(uid[-1]) % 3)
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
    
    # Each engineer gets all 15 questions from their topic
    all_questions = QUESTIONS[topic]
    selected_questions = all_questions  # All 15 questions
    
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
    <title>Vibhuayu Technologies - PD Assessment</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%); 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            position: relative;
            overflow: hidden;
        }
        body::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 30% 40%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.15) 0%, transparent 50%),
                        radial-gradient(circle at 40% 80%, rgba(120, 119, 198, 0.1) 0%, transparent 50%);
            z-index: 1;
        }
        .container {
            position: relative;
            z-index: 2;
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 50px 40px;
            width: 450px;
            box-shadow: 
                0 25px 50px rgba(0, 0, 0, 0.25),
                0 0 0 1px rgba(255, 255, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.9);
        }
        .logo-section {
            text-align: center;
            margin-bottom: 35px;
        }
        .logo {
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #2563eb, #7c3aed, #db2777);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(37, 99, 235, 0.3);
            position: relative;
            overflow: hidden;
        }
        .logo::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
            transform: translateX(-100%);
            animation: shine 3s infinite;
        }
        .logo-text {
            color: white;
            font-size: 36px;
            font-weight: 900;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
            font-family: 'Arial Black', sans-serif;
        }
        @keyframes shine {
            0% { transform: translateX(-100%); }
            50% { transform: translateX(100%); }
            100% { transform: translateX(100%); }
        }
        .title {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #1e293b, #475569);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        .subtitle {
            color: #64748b;
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 35px;
        }
        .form-group {
            margin-bottom: 24px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #374151;
            font-weight: 600;
            font-size: 14px;
        }
        .form-input {
            width: 100%;
            padding: 16px 20px;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.8);
        }
        .form-input:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            background: white;
        }
        .login-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.4);
        }
        .login-btn:active {
            transform: translateY(0);
        }
        .info-card {
            background: linear-gradient(135deg, #f8fafc, #f1f5f9);
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 24px;
            text-align: center;
        }
        .info-title {
            color: #1e293b;
            font-weight: 700;
            margin-bottom: 16px;
            font-size: 16px;
        }
        .credentials {
            background: white;
            border-radius: 8px;
            padding: 12px;
            margin: 12px 0;
            border-left: 4px solid #3b82f6;
        }
        .eng-list {
            font-size: 12px;
            color: #64748b;
            line-height: 1.6;
            margin-top: 12px;
        }
        .footer {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.6);
            font-size: 14px;
            z-index: 2;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo-section">
            <div class="logo">
                <div class="logo-text">V7</div>
            </div>
            <div class="title">PD Assessment Portal</div>
            <div class="subtitle">Physical Design Evaluation System</div>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" class="form-input" placeholder="Enter your username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" class="form-input" placeholder="Enter your password" required>
            </div>
            <button type="submit" class="login-btn">Access Assessment Portal</button>
        </form>
        
        <div class="info-card">
            <div class="info-title">🔐 Test Credentials</div>
            <div class="credentials">
                <strong>Engineers:</strong> eng001 through eng009<br>
                <strong>Password:</strong> password123
            </div>
            <div class="eng-list">
                <strong>Team Members:</strong><br>
                eng001: Kranthi & Neela • eng002: Bhanu & Lokeshwari • eng003: Nagesh & VJ<br>
                eng004: Pravalika & Daniel • eng005: Karthik & Hema • eng006: Naveen & Srinivas<br>
                eng007: Meera & Suraj • eng008: Akhil & Vikas • eng009: Sahith & Sravan
            </div>
        </div>
    </div>
    
    <div class="footer">
        Vibhuayu Technologies © 2025 | Secure Assessment Platform
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
        display_name = eng.get('display_name', eng['username'])
        eng_options += f'<option value="{eng["id"]}">{display_name} (3+ Experience)</option>'
    
    pending_html = ''
    for p in pending:
        pending_html += f'''
        <div class="pending-item">
            <div class="pending-title">{p["topic"].title()} Assessment - {users.get(p["engineer_id"], {}).get('display_name', p["engineer_id"])}</div>
            <div class="pending-meta">📝 15 Questions | 🎯 Max: 150 points | ⏰ Submitted for review</div>
            <a href="/admin/review/{p["id"]}" class="review-btn">Review Assessment</a>
        </div>'''
    
    if not pending_html:
        pending_html = '<div class="no-pending"><h3>📭 No Pending Reviews</h3><p>All assessments have been reviewed and completed.</p></div>'
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Vibhuayu Technologies - Admin Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
            min-height: 100vh;
            color: #334155;
        }}
        .header {{ 
            background: linear-gradient(135deg, #1e40af, #3b82f6); 
            padding: 20px 0; 
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
        }}
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
            transform: translateX(-100%);
            animation: headerShine 4s infinite;
        }}
        @keyframes headerShine {{
            0% {{ transform: translateX(-100%); }}
            50% {{ transform: translateX(100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        .header-content {{
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 0 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
            z-index: 2;
        }}
        .header-title {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .header-logo {{
            width: 50px;
            height: 50px;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            color: white;
            font-size: 20px;
            backdrop-filter: blur(10px);
        }}
        .header h1 {{ 
            color: white; 
            font-size: 28px; 
            font-weight: 700;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        .logout {{ 
            background: rgba(255, 255, 255, 0.15); 
            color: white; 
            padding: 12px 20px; 
            text-decoration: none; 
            border-radius: 10px; 
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            font-weight: 600;
        }}
        .logout:hover {{
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 30px auto; 
            padding: 0 20px; 
        }}
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 25px; 
            margin-bottom: 40px; 
        }}
        .stat {{ 
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); 
            padding: 30px; 
            border-radius: 16px; 
            text-align: center; 
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }}
        .stat:hover {{
            transform: translateY(-5px);
        }}
        .stat-num {{ 
            font-size: 36px; 
            font-weight: 800; 
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}
        .stat-label {{
            color: #64748b;
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .card {{ 
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); 
            border-radius: 20px; 
            padding: 30px; 
            margin: 25px 0; 
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .card h2 {{
            color: #1e293b;
            margin-bottom: 25px;
            font-size: 24px;
            font-weight: 700;
        }}
        .form-row {{
            display: flex;
            gap: 15px;
            align-items: end;
        }}
        select, button {{ 
            padding: 14px 18px; 
            border: 2px solid #e2e8f0; 
            border-radius: 10px; 
            font-size: 16px;
            transition: all 0.3s ease;
            background: white;
        }}
        select:focus {{
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }}
        .btn-primary {{ 
            background: linear-gradient(135deg, #3b82f6, #1d4ed8); 
            color: white; 
            border: none; 
            cursor: pointer; 
            font-weight: 600;
            min-width: 120px;
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.4);
        }}
        .pending-item {{
            background: linear-gradient(135deg, #f8fafc, #f1f5f9); 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 12px; 
            border-left: 4px solid #10b981;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease;
        }}
        .pending-item:hover {{
            transform: translateX(5px);
        }}
        .pending-title {{
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 8px;
            font-size: 16px;
        }}
        .pending-meta {{
            color: #64748b;
            font-size: 14px;
            margin-bottom: 15px;
        }}
        .review-btn {{
            background: linear-gradient(135deg, #10b981, #059669); 
            color: white; 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 8px; 
            display: inline-block;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        .review-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
        }}
        .no-pending {{
            text-align: center; 
            color: #64748b; 
            padding: 60px 20px;
            background: linear-gradient(135deg, #f8fafc, #f1f5f9);
            border-radius: 12px;
            border: 2px dashed #cbd5e1;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="header-title">
                <div class="header-logo">V7</div>
                <h1>Admin Dashboard</h1>
            </div>
            <a href="/logout" class="logout">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat">
                <div class="stat-num">{len(engineers)}</div>
                <div class="stat-label">Engineers</div>
            </div>
            <div class="stat">
                <div class="stat-num">{len(all_tests)}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat">
                <div class="stat-num">{len(pending)}</div>
                <div class="stat-label">Pending Reviews</div>
            </div>
            <div class="stat">
                <div class="stat-num">45</div>
                <div class="stat-label">Questions</div>
            </div>
        </div>
        
        <div class="card">
            <h2>🎯 Create New Assessment</h2>
            <form method="POST" action="/admin/create">
                <div class="form-row">
                    <select name="engineer_id" required>
                        <option value="">Select Engineer...</option>
                        {eng_options}
                    </select>
                    <select name="topic" required>
                        <option value="">Select Topic...</option>
                        <option value="floorplanning">🏗️ Floorplanning</option>
                        <option value="placement">📍 Placement</option>
                        <option value="routing">🔗 Routing</option>
                    </select>
                    <button type="submit" class="btn-primary">Create Assessment</button>
                </div>
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
        for i in range(15):  # Now 15 questions
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
                    <strong>Score: {t["score"]}/150</strong>
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
            <div class="stat"><div style="font-size: 20px; font-weight: bold;">15</div><div>Questions</div></div>
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
        for i in range(15):  # Now 15 questions
            answer = request.form.get(f'answer_{i}', '').strip()
            if answer:
                answers[str(i)] = answer
        
        if len(answers) == 15:  # All 15 must be answered
            test['answers'] = answers
            test['status'] = 'submitted'
        
        return redirect('/student')
    
    questions_html = ''
    for i, q in enumerate(test['questions']):
        questions_html += f'''
        <div style="background: rgba(255,255,255,0.95); border-radius: 16px; padding: 24px; margin: 20px 0;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-bottom: 16px;">
                Question {i+1} of 15
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
