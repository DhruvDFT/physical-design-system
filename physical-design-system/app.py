# app.py - Enhanced PD Interview System (Stable Version)
import os
import hashlib
import json
import re
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, session, url_for
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pd-secret-2024')

# Disable Flask logging to prevent errors
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Simple password hashing (keeping original logic)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed, password):
    return hashed == hashlib.sha256(password.encode()).hexdigest()

# In-memory storage (keeping original structure)
users = {}
assignments = {}
notifications = {}
assignment_counter = 0
engineer_question_sets = {}

# Enhanced question database with difficulty levels
ENHANCED_QUESTIONS = {
    "floorplanning": [
        {
            "question": "You have a 5mm x 5mm die with 4 hard macros (each 1mm x 0.8mm) and need to achieve 70% utilization. Describe your macro placement strategy considering timing and power delivery.",
            "difficulty": "intermediate",
            "category": "macro_planning",
            "keywords": ["macro", "timing", "power", "delivery", "strategy", "utilization"],
            "max_score": 10
        },
        {
            "question": "Your design has setup timing violations on paths crossing from left to right. The floorplan has macros placed randomly. How would you reorganize the floorplan to improve timing?",
            "difficulty": "intermediate", 
            "category": "timing_optimization",
            "keywords": ["timing", "violations", "floorplan", "macros", "reorganize"],
            "max_score": 10
        },
        {
            "question": "During floorplan, you notice routing congestion in the center region. What are 3 specific techniques you would use to reduce congestion without major timing impact?",
            "difficulty": "beginner",
            "category": "congestion_management", 
            "keywords": ["congestion", "routing", "techniques", "timing", "impact"],
            "max_score": 10
        }
    ],
    "placement": [
        {
            "question": "Your placement run shows timing violations on 20 critical paths with negative slack up to -50ps. Describe your systematic approach to fix these violations.",
            "difficulty": "intermediate",
            "category": "timing_optimization",
            "keywords": ["timing", "violations", "slack", "critical", "path", "systematic"],
            "max_score": 10
        },
        {
            "question": "You're seeing routing congestion hotspots after placement in 2-3 regions. What placement adjustments would you make to improve routability?",
            "difficulty": "intermediate",
            "category": "congestion_management", 
            "keywords": ["congestion", "placement", "routability", "adjustments"],
            "max_score": 10
        },
        {
            "question": "Your design has high-fanout nets (>500 fanout) causing placement issues. How would you handle these nets during placement optimization?",
            "difficulty": "advanced",
            "category": "high_fanout",
            "keywords": ["fanout", "nets", "placement", "optimization", "buffering"],
            "max_score": 10
        }
    ],
    "routing": [
        {
            "question": "After global routing, you have 500 DRC violations (spacing, via, width). Describe your systematic approach to resolve these violations efficiently.",
            "difficulty": "intermediate",
            "category": "drc_resolution",
            "keywords": ["DRC", "violations", "spacing", "via", "width", "systematic"],
            "max_score": 10
        },
        {
            "question": "Your design has 10 differential pairs for high-speed signals. Explain your routing strategy to maintain 100-ohm impedance and minimize skew.",
            "difficulty": "advanced",
            "category": "high_speed",
            "keywords": ["differential", "impedance", "skew", "routing", "strategy"],
            "max_score": 10
        },
        {
            "question": "You're seeing timing degradation after detailed routing compared to placement timing. What causes this and how would you recover the timing?",
            "difficulty": "intermediate",
            "category": "timing_closure",
            "keywords": ["timing", "degradation", "routing", "placement", "recovery"],
            "max_score": 10
        }
    ]
}

# AI scoring keywords (enhanced but keeping simple logic)
ANSWER_KEYWORDS = {
    "floorplanning": {
        "basic": ["macro", "timing", "power", "congestion", "voltage", "clock"],
        "advanced": ["hierarchy", "partition", "isolation", "substrate", "methodology"]
    },
    "placement": {
        "basic": ["timing", "congestion", "fanout", "global", "detailed", "density"],
        "advanced": ["optimization", "convergence", "strategy", "systematic", "analysis"]
    },
    "routing": {
        "basic": ["DRC", "violations", "timing", "routing", "layer", "via"],
        "advanced": ["impedance", "skew", "crosstalk", "parasitic", "extraction"]
    }
}

# Smart question selection based on experience (keeping original logic intact)
def get_questions_for_engineer(engineer_id, topic):
    """Enhanced question selection while keeping original structure"""
    if engineer_id not in engineer_question_sets:
        engineer_num = int(engineer_id[-3:]) - 1
        set_index = engineer_num % 4  # Keep original 4 sets logic
        engineer_question_sets[engineer_id] = set_index
    
    # Get engineer experience for smart selection
    engineer = users.get(engineer_id, {})
    experience = engineer.get('experience_years', 3)
    
    questions = ENHANCED_QUESTIONS.get(topic, [])
    if not questions:
        # Fallback to original simple questions
        return [
            {"question": f"Basic {topic} question 1", "difficulty": "beginner", "max_score": 10},
            {"question": f"Basic {topic} question 2", "difficulty": "beginner", "max_score": 10},
            {"question": f"Basic {topic} question 3", "difficulty": "beginner", "max_score": 10}
        ]
    
    # Smart selection based on experience but keep 3 questions
    if experience <= 2:
        # Junior: easier questions
        selected = [q for q in questions if q.get('difficulty') in ['beginner', 'intermediate']]
    elif experience <= 4:
        # Mid: mixed difficulty
        selected = questions
    else:
        # Senior: harder questions
        selected = [q for q in questions if q.get('difficulty') in ['intermediate', 'advanced']]
    
    # Ensure we have 3 questions
    if len(selected) < 3:
        selected = questions
    
    return selected[:3]

# Enhanced AI scoring (keeping simple calculation)
def calculate_auto_score(answer, topic):
    """Enhanced scoring while keeping original simple logic"""
    if not answer:
        return 0
    
    answer_lower = answer.lower()
    keywords_found = 0
    
    # Use enhanced keywords but keep simple scoring
    topic_keywords = ANSWER_KEYWORDS.get(topic, {})
    all_keywords = []
    
    for category, keywords in topic_keywords.items():
        all_keywords.extend(keywords)
    
    # Count keyword matches (original logic)
    for keyword in all_keywords:
        if keyword.lower() in answer_lower:
            keywords_found += 1
    
    # Keep original scoring: 2 points per keyword, max 10
    base_score = min(keywords_found * 2, 10)
    
    # Small enhancement: bonus for answer length
    if len(answer.split()) > 50:
        base_score = min(base_score + 1, 10)
    
    return base_score

# Enhanced create assignment (keeping original structure)
def create_assignment(engineer_id, topic):
    global assignment_counter
    
    user = users.get(engineer_id)
    if not user or topic not in ENHANCED_QUESTIONS:
        return None
    
    assignment_counter += 1
    assignment_id = f"PD_{topic.upper()}_{engineer_id}_{assignment_counter}"
    
    # Use enhanced question selection
    questions = get_questions_for_engineer(engineer_id, topic)
    
    # Keep original assignment structure
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
        'published_date': None,
        # Enhanced fields
        'difficulty_level': 'adaptive',
        'max_possible_score': sum(q.get('max_score', 10) for q in questions)
    }
    
    assignments[assignment_id] = assignment
    
    # Keep original notification logic
    if engineer_id not in notifications:
        notifications[engineer_id] = []
    
    notifications[engineer_id].append({
        'title': f'New {topic} Assignment',
        'message': f'3 questions for {user.get("experience_years", 3)}+ years experience, due in 3 days',
        'created_at': datetime.now().isoformat()
    })
    
    return assignment

# Initialize users (keeping original logic)
def init_users():
    # Admin (keep original credentials hidden from UI)
    users['admin'] = {
        'id': 'admin',
        'username': 'admin',
        'password': hash_password('Vibhuaya@3006'),
        'is_admin': True,
        'experience_years': 3
    }
    
    # 5 Engineers (keep original structure, add experience variety)
    engineers_data = [
        {'id': 'eng001', 'exp': 2},
        {'id': 'eng002', 'exp': 4}, 
        {'id': 'eng003', 'exp': 6},
        {'id': 'eng004', 'exp': 3},
        {'id': 'eng005', 'exp': 5}
    ]
    
    for eng in engineers_data:
        users[eng['id']] = {
            'id': eng['id'],
            'username': eng['id'],
            'password': hash_password('password123'),
            'is_admin': False,
            'experience_years': eng['exp']
        }

# Routes (keeping original structure with UI enhancements)
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
    
    # Enhanced modern login page
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PD Assessment System - Login</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
            }}
            
            .login-container {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 40px;
                width: 400px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            .logo {{
                text-align: center;
                margin-bottom: 30px;
            }}
            
            .logo h1 {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            
            .logo p {{
                color: #6b7280;
                font-size: 14px;
            }}
            
            .form-group {{
                margin-bottom: 20px;
            }}
            
            .form-group label {{
                display: block;
                color: #374151;
                font-weight: 600;
                margin-bottom: 8px;
                font-size: 14px;
            }}
            
            .form-group input {{
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                font-size: 16px;
                transition: all 0.3s ease;
                background: #f9fafb;
            }}
            
            .form-group input:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                background: white;
            }}
            
            .login-btn {{
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .login-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }}
            
            .credentials-info {{
                background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
                border: 1px solid #0ea5e9;
                border-radius: 12px;
                padding: 16px;
                margin: 20px 0;
            }}
            
            .credentials-info h4 {{
                color: #0c4a6e;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 10px;
            }}
            
            .credentials-info p {{
                color: #0369a1;
                font-size: 13px;
                margin-bottom: 6px;
            }}
            
            .error {{
                background: linear-gradient(135deg, #fee2e2, #fecaca);
                border: 1px solid #f87171;
                color: #dc2626;
                padding: 12px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
                font-weight: 500;
            }}
            
            .features {{
                text-align: center;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
            }}
            
            .feature-tags {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                justify-content: center;
                margin-top: 10px;
            }}
            
            .feature-tag {{
                background: rgba(102, 126, 234, 0.1);
                color: #667eea;
                padding: 4px 10px;
                border-radius: 15px;
                font-size: 11px;
                font-weight: 500;
            }}
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">
                <h1>⚡ PD Assessment</h1>
                <p>Intelligent Interview System</p>
            </div>
            
            {f'<div class="error">❌ {error}</div>' if error else ''}
            
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" placeholder="Enter username" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="Enter password" required>
                </div>
                
                <button type="submit" class="login-btn">
                    Sign In
                </button>
            </form>
            
            <div class="credentials-info">
                <h4>🔑 Test Credentials</h4>
                <p><strong>Engineers:</strong> eng001, eng002, eng003, eng004, eng005</p>
                <p><strong>Password:</strong> password123</p>
            </div>
            
            <div class="features">
                <div class="feature-tags">
                    <span class="feature-tag">🤖 AI Scoring</span>
                    <span class="feature-tag">📊 Smart Analytics</span>
                    <span class="feature-tag">🎯 Adaptive Questions</span>
                    <span class="feature-tag">💡 Instant Feedback</span>
                </div>
            </div>
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
    
    # Enhanced admin dashboard with modern UI
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Dashboard - PD Assessment</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f8fafc;
                color: #1e293b;
            }}
            
            .header {{
                background: linear-gradient(135deg, #1e40af, #3b82f6);
                color: white;
                padding: 20px 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            
            .header-content {{
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 20px;
            }}
            
            .header h1 {{
                font-size: 24px;
                font-weight: 700;
            }}
            
            .logout-btn {{
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
            }}
            
            .logout-btn:hover {{
                background: rgba(255, 255, 255, 0.3);
            }}
            
            .container {{
                max-width: 1200px;
                margin: 20px auto;
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
                padding: 24px;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                border: 1px solid #e2e8f0;
                text-align: center;
            }}
            
            .stat-number {{
                font-size: 28px;
                font-weight: 700;
                color: #1e40af;
                margin-bottom: 6px;
            }}
            
            .stat-label {{
                color: #64748b;
                font-size: 14px;
                font-weight: 500;
            }}
            
            .card {{
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                border: 1px solid #e2e8f0;
                margin-bottom: 24px;
            }}
            
            .card-header {{
                background: #f8fafc;
                padding: 20px 24px;
                border-bottom: 1px solid #e2e8f0;
                border-radius: 12px 12px 0 0;
            }}
            
            .card-header h2 {{
                font-size: 18px;
                font-weight: 600;
                color: #1e293b;
            }}
            
            .card-body {{
                padding: 24px;
            }}
            
            .form-row {{
                display: flex;
                gap: 12px;
                align-items: end;
                flex-wrap: wrap;
            }}
            
            .form-group {{
                flex: 1;
                min-width: 150px;
            }}
            
            .form-group label {{
                display: block;
                margin-bottom: 6px;
                color: #374151;
                font-weight: 500;
                font-size: 14px;
            }}
            
            .form-group select {{
                width: 100%;
                padding: 10px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                background: white;
            }}
            
            .btn {{
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
            }}
            
            .btn-primary {{
                background: #3b82f6;
                color: white;
            }}
            
            .btn-primary:hover {{
                background: #2563eb;
            }}
            
            .btn-success {{
                background: #10b981;
                color: white;
            }}
            
            .btn-success:hover {{
                background: #059669;
            }}
            
            .assignment-item {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 12px;
            }}
            
            .assignment-title {{
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 6px;
            }}
            
            .assignment-meta {{
                color: #64748b;
                font-size: 13px;
                margin-bottom: 12px;
            }}
            
            .empty-state {{
                text-align: center;
                padding: 40px 20px;
                color: #64748b;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <h1>⚡ Admin Dashboard</h1>
                <div>
                    <span style="margin-right: 15px;">👨‍💼 {session['username']}</span>
                    <a href="/logout" class="logout-btn">Logout</a>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(engineers)}</div>
                    <div class="stat-label">Engineers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(all_assignments)}</div>
                    <div class="stat-label">Assignments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(submitted)}</div>
                    <div class="stat-label">Pending Review</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">9</div>
                    <div class="stat-label">Enhanced Questions</div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2>🎯 Create Assessment</h2>
                </div>
                <div class="card-body">
                    <form method="POST" action="/admin/create">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="engineer_id">Engineer</label>
                                <select name="engineer_id" required>
                                    <option value="">Select...</option>'''
    
    for eng in engineers:
        exp_level = "Junior" if eng['experience_years'] <= 2 else "Mid" if eng['experience_years'] <= 4 else "Senior"
        html += f'<option value="{eng["id"]}">{eng["username"]} ({exp_level} - {eng["experience_years"]}y)</option>'
    
    html += f'''
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="topic">Topic</label>
                                <select name="topic" required>
                                    <option value="">Select...</option>
                                    <option value="floorplanning">🏗️ Floorplanning</option>
                                    <option value="placement">📍 Placement</option>
                                    <option value="routing">🛤️ Routing</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <button type="submit" class="btn btn-primary">Create</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2>📋 Submitted Assessments</h2>
                </div>
                <div class="card-body">'''
    
    if submitted:
        for a in submitted:
            engineer = users.get(a['engineer_id'], {})
            html += f'''
                    <div class="assignment-item">
                        <div class="assignment-title">
                            {a["topic"].title()} Assessment - {a["engineer_id"]}
                        </div>
                        <div class="assignment-meta">
                            Experience: {engineer.get("experience_years", 0)} years | 
                            Questions: {len(a.get("questions", []))} | 
                            Max Score: {a.get("max_possible_score", 30)}
                        </div>
                        <a href="/admin/review/{a["id"]}" class="btn btn-success">
                            Review & Score
                        </a>
                    </div>'''
    else:
        html += '''
                    <div class="empty-state">
                        <p>📭 No pending reviews</p>
                    </div>'''
    
    html += '''
                </div>
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
        # Save scores (keeping original logic)
        total_score = 0
        for i in range(len(assignment.get('questions', []))):
            score = request.form.get(f'score_{i}', '0')
            try:
                total_score += float(score)
            except:
                pass
        
        assignment['total_score'] = total_score
        assignment['status'] = 'published'
        assignment['scored_by'] = session['username']
        assignment['scored_date'] = datetime.now().isoformat()
        
        return redirect('/admin')
    
    # Enhanced review interface
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Review Assessment</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f8fafc;
                color: #1e293b;
            }}
            
            .header {{
                background: linear-gradient(135deg, #1e40af, #3b82f6);
                color: white;
                padding: 20px 0;
            }}
            
            .header-content {{
                max-width: 1000px;
                margin: 0 auto;
                padding: 0 20px;
            }}
            
            .container {{
                max-width: 1000px;
                margin: 20px auto;
                padding: 0 20px;
            }}
            
            .assignment-info {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }}
            
            .question-card {{
                background: white;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                overflow: hidden;
            }}
            
            .question-header {{
                background: #f8fafc;
                padding: 16px 20px;
                border-bottom: 1px solid #e2e8f0;
            }}
            
            .question-content {{
                padding: 20px;
            }}
            
            .question-text {{
                background: #f1f5f9;
                padding: 16px;
                border-radius: 8px;
                margin-bottom: 16px;
                border-left: 4px solid #3b82f6;
            }}
            
            .answer-content {{
                background: #fefefe;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
                min-height: 80px;
                white-space: pre-wrap;
                font-family: monospace;
                font-size: 14px;
            }}
            
            .ai-analysis {{
                background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
                border: 1px solid #0ea5e9;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
            }}
            
            .scoring-section {{
                background: #f8fafc;
                padding: 16px;
                border-radius: 8px;
            }}
            
            .score-input {{
                width: 60px;
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                text-align: center;
                font-weight: 600;
            }}
            
            .btn {{
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin: 5px;
            }}
            
            .btn-primary {{
                background: #3b82f6;
                color: white;
            }}
            
            .btn-secondary {{
                background: #6b7280;
                color: white;
            }}
            
            .submit-section {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <h1>📝 Review Assessment: {assignment_id}</h1>
                <p>Topic: {assignment["topic"].title()}</p>
            </div>
        </div>
        
        <div class="container">
            <div class="assignment-info">
                <h3>👤 Engineer: {assignment["engineer_id"]}</h3>
                <p>📊 Questions: {len(assignment.get("questions", []))} | 🎯 Max Score: {assignment.get("max_possible_score", 30)}</p>
            </div>
            
            <form method="POST">'''
    
    # Display questions with enhanced scoring
    questions = assignment.get('questions', [])
    for i, question in enumerate(questions):
        answer = assignment.get('answers', {}).get(str(i), 'No answer provided')
        auto_score = calculate_auto_score(answer, assignment['topic'])
        
        # Get question metadata
        difficulty = question.get('difficulty', 'intermediate')
        category = question.get('category', 'general')
        max_score = question.get('max_score', 10)
        
        html += f'''
                <div class="question-card">
                    <div class="question-header">
                        <h4>Question {i+1} of {len(questions)}</h4>
                        <small>📂 {category.replace("_", " ").title()} | ⚡ {difficulty.title()} | 🎯 {max_score} pts</small>
                    </div>
                    
                    <div class="question-content">
                        <div class="question-text">
                            <strong>Q:</strong> {question.get("question", "Question not available")}
                        </div>
                        
                        <div>
                            <h5>📝 Engineer's Answer:</h5>
                            <div class="answer-content">{answer}</div>
                        </div>
                        
                        <div class="ai-analysis">
                            <h5>🤖 AI Analysis</h5>
                            <p><strong>Auto Score:</strong> {auto_score}/{max_score}</p>
                            <p><strong>Analysis:</strong> {"Good technical content" if auto_score >= 6 else "Needs more technical detail" if auto_score >= 3 else "Insufficient detail"}</p>
                        </div>
                        
                        <div class="scoring-section">
                            <label for="score_{i}"><strong>👨‍🏫 Your Final Score:</strong></label>
                            <input 
                                type="number" 
                                name="score_{i}" 
                                id="score_{i}"
                                min="0" 
                                max="{max_score}" 
                                step="0.5"
                                value="{auto_score}" 
                                class="score-input"
                                required
                            >
                            <span>/ {max_score} (AI suggested: {auto_score})</span>
                        </div>
                    </div>
                </div>'''
    
    html += f'''
                <div class="submit-section">
                    <h3>📊 Final Review</h3>
                    <p style="margin: 15px 0; color: #64748b;">
                        Review all scores and publish results for the engineer.
                    </p>
                    
                    <button type="submit" class="btn btn-primary">
                        ✅ Publish Final Scores
                    </button>
                    <a href="/admin" class="btn btn-secondary">
                        ← Back to Dashboard
                    </a>
                </div>
            </form>
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/student')
def student_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    user = users.get(user_id, {})
    my_assignments = [a for a in assignments.values() if a['engineer_id'] == user_id]
    
    # Enhanced student dashboard
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Engineer Dashboard</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #1e293b;
            }}
            
            .header {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                padding: 20px 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            
            .header-content {{
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 20px;
            }}
            
            .header h1 {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 24px;
                font-weight: 700;
            }}
            
            .user-info {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .logout-btn {{
                background: rgba(239, 68, 68, 0.1);
                color: #dc2626;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 500;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 20px auto;
                padding: 0 20px;
            }}
            
            .stats-overview {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .stat-card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                padding: 20px;
                border-radius: 16px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                text-align: center;
            }}
            
            .stat-number {{
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 6px;
            }}
            
            .stat-label {{
                color: #64748b;
                font-size: 12px;
                font-weight: 500;
                text-transform: uppercase;
            }}
            
            .assignments-section {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            }}
            
            .section-header {{
                margin-bottom: 20px;
                padding-bottom: 12px;
                border-bottom: 2px solid #f1f5f9;
            }}
            
            .section-header h2 {{
                font-size: 20px;
                font-weight: 700;
                color: #1e293b;
            }}
            
            .assignment-card {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                transition: all 0.3s ease;
            }}
            
            .assignment-card:hover {{
                border-color: #667eea;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
            }}
            
            .assignment-title {{
                font-size: 18px;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 8px;
            }}
            
            .assignment-meta {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
                gap: 10px;
                margin: 12px 0;
                padding: 12px;
                background: rgba(255, 255, 255, 0.7);
                border-radius: 8px;
                font-size: 13px;
            }}
            
            .meta-item {{
                text-align: center;
            }}
            
            .meta-value {{
                font-weight: 600;
                color: #1e293b;
            }}
            
            .meta-label {{
                color: #64748b;
                font-size: 11px;
                text-transform: uppercase;
            }}
            
            .status-badge {{
                padding: 6px 12px;
                border-radius: 15px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            
            .status-pending {{
                background: #fbbf24;
                color: white;
            }}
            
            .status-submitted {{
                background: #3b82f6;
                color: white;
            }}
            
            .status-published {{
                background: #10b981;
                color: white;
            }}
            
            .btn {{
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                text-align: center;
                transition: all 0.3s ease;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
            }}
            
            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            }}
            
            .empty-state {{
                text-align: center;
                padding: 40px 20px;
                color: #64748b;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <h1>⚡ Engineer Dashboard</h1>
                <div class="user-info">
                    <span>👨‍💼 {session['username']} ({user.get('experience_years', 0)} years)</span>
                    <a href="/logout" class="logout-btn">Logout</a>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="stats-overview">
                <div class="stat-card">
                    <div class="stat-number">{len(my_assignments)}</div>
                    <div class="stat-label">Assessments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([a for a in my_assignments if a['status'] == 'published'])}</div>
                    <div class="stat-label">Completed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{user.get('experience_years', 0)}y</div>
                    <div class="stat-label">Experience</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">🤖</div>
                    <div class="stat-label">AI Enhanced</div>
                </div>
            </div>
            
            <div class="assignments-section">
                <div class="section-header">
                    <h2>📚 My Assessments</h2>
                </div>'''
    
    if my_assignments:
        for a in my_assignments:
            status = a['status']
            topic_icon = {'floorplanning': '🏗️', 'placement': '📍', 'routing': '🛤️'}.get(a['topic'], '📝')
            
            html += f'''
                <div class="assignment-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div class="assignment-title">
                            {topic_icon} {a["topic"].title()} Assessment
                        </div>
                        <span class="status-badge status-{status}">{status}</span>
                    </div>
                    
                    <div class="assignment-meta">
                        <div class="meta-item">
                            <div class="meta-value">{len(a.get('questions', []))}</div>
                            <div class="meta-label">Questions</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-value">{a.get("max_possible_score", 30)}</div>
                            <div class="meta-label">Max Score</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-value">{a["due_date"][:10]}</div>
                            <div class="meta-label">Due Date</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-value">{a.get("difficulty_level", "adaptive").title()}</div>
                            <div class="meta-label">Difficulty</div>
                        </div>
                    </div>'''
            
            if status == 'published':
                percentage = (a['total_score'] / a.get('max_possible_score', 30)) * 100
                html += f'''
                    <div style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 12px; border-radius: 8px; text-align: center;">
                        <strong>Score: {a["total_score"]:.1f}/{a.get("max_possible_score", 30)} ({percentage:.1f}%)</strong>
                    </div>'''
            elif status == 'submitted':
                html += '<p style="text-align: center; color: #3b82f6; font-weight: 500;">⏳ Under AI analysis and admin review</p>'
            elif status == 'pending':
                html += f'''
                    <a href="/student/assignment/{a["id"]}" class="btn btn-primary" style="width: 100%; margin-top: 8px;">
                        🚀 Start Smart Assessment
                    </a>'''
            
            html += '</div>'
    else:
        html += '''
                <div class="empty-state">
                    <h3>📭 No Assessments Yet</h3>
                    <p>Your assessments will appear here when created by admin.</p>
                </div>'''
    
    html += '''
            </div>
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
        # Save answers (keeping original logic)
        answers = {}
        for i in range(len(assignment.get('questions', []))):
            answer = request.form.get(f'answer_{i}', '').strip()
            if answer:
                answers[str(i)] = answer
        
        if len(answers) == len(assignment.get('questions', [])):
            assignment['answers'] = answers
            assignment['status'] = 'submitted'
            assignment['submitted_date'] = datetime.now().isoformat()
        
        return redirect('/student')
    
    # Enhanced assignment interface
    topic_icon = {'floorplanning': '🏗️', 'placement': '📍', 'routing': '🛤️'}.get(assignment['topic'], '📝')
    questions = assignment.get('questions', [])
    
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{assignment["topic"].title()} Assessment</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #1e293b;
            }}
            
            .header {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                padding: 20px 0;
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
            
            .assessment-title {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            
            .container {{
                max-width: 1000px;
                margin: 20px auto;
                padding: 0 20px;
            }}
            
            .question-card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 20px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            }}
            
            .question-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 2px solid #f1f5f9;
            }}
            
            .question-number {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 600;
            }}
            
            .question-meta {{
                display: flex;
                gap: 10px;
                font-size: 12px;
                color: #64748b;
            }}
            
            .meta-badge {{
                background: rgba(102, 126, 234, 0.1);
                color: #4f46e5;
                padding: 4px 8px;
                border-radius: 10px;
                font-weight: 500;
            }}
            
            .question-text {{
                font-size: 16px;
                line-height: 1.6;
                color: #1e293b;
                margin-bottom: 20px;
                padding: 16px;
                background: linear-gradient(135deg, #f8fafc, #f1f5f9);
                border-radius: 12px;
                border-left: 4px solid #667eea;
            }}
            
            .answer-label {{
                font-weight: 600;
                color: #374151;
                margin-bottom: 8px;
                font-size: 14px;
            }}
            
            .answer-textarea {{
                width: 100%;
                min-height: 120px;
                padding: 16px;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                font-size: 14px;
                line-height: 1.5;
                background: #fefefe;
                transition: all 0.3s ease;
                resize: vertical;
            }}
            
            .answer-textarea:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            
            .submit-section {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                margin-top: 20px;
            }}
            
            .submit-warning {{
                background: linear-gradient(135deg, #fef3c7, #fde68a);
                border: 1px solid #f59e0b;
                color: #92400e;
                padding: 16px;
                border-radius: 12px;
                margin-bottom: 20px;
                font-weight: 500;
            }}
            
            .btn {{
                padding: 14px 28px;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 0 8px;
                transition: all 0.3s ease;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
            }}
            
            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
            }}
            
            .btn-secondary {{
                background: rgba(107, 114, 128, 0.1);
                color: #374151;
                border: 1px solid #d1d5db;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div class="assessment-title">
                    {topic_icon} {assignment["topic"].title()} Assessment
                </div>
                <p style="color: #64748b;">📊 {len(questions)} Smart Questions | 🎯 Max: {assignment.get('max_possible_score', 30)} Points</p>
            </div>
        </div>
        
        <div class="container">
            <form method="POST">'''
    
    # Display questions with enhanced UI
    for i, question in enumerate(questions):
        difficulty = question.get('difficulty', 'intermediate')
        category = question.get('category', 'general')
        max_score = question.get('max_score', 10)
        
        html += f'''
                <div class="question-card">
                    <div class="question-header">
                        <div class="question-number">
                            Question {i+1} of {len(questions)}
                        </div>
                        <div class="question-meta">
                            <span class="meta-badge">📂 {category.replace("_", " ").title()}</span>
                            <span class="meta-badge">⚡ {difficulty.title()}</span>
                            <span class="meta-badge">🎯 {max_score} pts</span>
                        </div>
                    </div>
                    
                    <div class="question-text">
                        {question.get("question", "Question not available")}
                    </div>
                    
                    <div>
                        <label for="answer_{i}" class="answer-label">
                            ✍️ Your Answer:
                        </label>
                        <textarea 
                            name="answer_{i}" 
                            id="answer_{i}"
                            class="answer-textarea"
                            placeholder="Provide a detailed technical answer with specific examples and methodologies..."
                            required
                        ></textarea>
                    </div>
                </div>'''
    
    html += f'''
                <div class="submit-section">
                    <div class="submit-warning">
                        ⚠️ Please review all answers before submitting. You cannot edit after submission.
                    </div>
                    
                    <button type="submit" class="btn btn-primary">
                        🚀 Submit Assessment
                    </button>
                    <a href="/student" class="btn btn-secondary">
                        ← Back to Dashboard
                    </a>
                </div>
            </form>
        </div>
    </body>
    </html>
    '''
    return html

# Initialize system
init_users()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)ap: 15pxpp.run(host='0.0.0.0', port=port, debug=False)
