# app.py - Enhanced PD Interview System with AI Features
import os
import hashlib
import json
import re
import statistics
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, session, url_for
from collections import Counter
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pd-intelligent-system-2024')

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
engineer_question_sets = {}
answer_analytics = {}

# Initialize users
def init_users():
    # Admin (hidden credentials)
    users['admin'] = {
        'id': 'admin',
        'username': 'admin',
        'password': hash_password('Vibhuaya@3006'),
        'is_admin': True,
        'experience_years': 5,
        'department': 'Management'
    }
    
    # Engineers with varied experience levels
    engineers_data = [
        {'id': 'eng001', 'exp': 2, 'dept': 'Frontend Implementation'},
        {'id': 'eng002', 'exp': 4, 'dept': 'Backend Implementation'},
        {'id': 'eng003', 'exp': 6, 'dept': 'Physical Design'},
        {'id': 'eng004', 'exp': 3, 'dept': 'Verification'},
        {'id': 'eng005', 'exp': 5, 'dept': 'Physical Design'}
    ]
    
    for eng in engineers_data:
        users[eng['id']] = {
            'id': eng['id'],
            'username': eng['id'],
            'password': hash_password('password123'),
            'is_admin': False,
            'experience_years': eng['exp'],
            'department': eng['dept'],
            'skills': [],
            'assessment_history': []
        }

# Enhanced question sets with difficulty levels and categories
QUESTIONS_DATABASE = {
    "floorplanning": {
        "beginner": [
            {
                "question": "Explain the basic steps involved in floorplanning and why macro placement is critical for timing closure.",
                "category": "fundamentals",
                "keywords": ["macro", "placement", "timing", "closure", "floorplan", "steps"],
                "max_score": 10,
                "complexity": 1
            },
            {
                "question": "What factors would you consider when placing memory instances in your floorplan?",
                "category": "memory_planning",
                "keywords": ["memory", "placement", "access", "timing", "power", "routing"],
                "max_score": 10,
                "complexity": 1
            },
            {
                "question": "How does die utilization affect your floorplanning decisions? What's the typical target utilization?",
                "category": "utilization",
                "keywords": ["utilization", "die", "area", "routing", "congestion", "target"],
                "max_score": 10,
                "complexity": 1
            }
        ],
        "intermediate": [
            {
                "question": "You have a 5mm x 5mm die with 4 hard macros (each 1mm x 0.8mm) and need to achieve 70% utilization. Describe your macro placement strategy considering timing and power delivery.",
                "category": "macro_planning",
                "keywords": ["macro", "timing", "power", "delivery", "strategy", "utilization", "placement"],
                "max_score": 15,
                "complexity": 2
            },
            {
                "question": "Your design has 3 voltage domains (0.9V core, 1.2V IO, 0.7V low-power). Explain how you would plan the floorplan to minimize level shifter count and power grid complexity.",
                "category": "power_domains",
                "keywords": ["voltage", "domains", "level", "shifter", "power", "grid", "complexity"],
                "max_score": 15,
                "complexity": 2
            },
            {
                "question": "During floorplan, you notice routing congestion hotspots in the center region. What are 3 specific techniques you would use to reduce congestion without major timing impact?",
                "category": "congestion_management",
                "keywords": ["congestion", "routing", "techniques", "timing", "impact", "optimization"],
                "max_score": 15,
                "complexity": 2
            }
        ],
        "advanced": [
            {
                "question": "Your design has mixed-signal blocks requiring 60dB isolation from digital switching noise. Describe your comprehensive isolation strategy including floorplan, power delivery, and substrate considerations.",
                "category": "mixed_signal",
                "keywords": ["mixed", "signal", "isolation", "noise", "substrate", "power", "delivery", "switching"],
                "max_score": 20,
                "complexity": 3
            },
            {
                "question": "You're implementing a hierarchical design with 5 major blocks and complex timing constraints. Explain your partition-level floorplanning methodology and interface optimization strategy.",
                "category": "hierarchical_design",
                "keywords": ["hierarchical", "partition", "interface", "optimization", "timing", "constraints", "methodology"],
                "max_score": 20,
                "complexity": 3
            }
        ]
    },
    "placement": {
        "beginner": [
            {
                "question": "Explain the difference between global placement and detailed placement. What problems does each phase solve?",
                "category": "fundamentals",
                "keywords": ["global", "detailed", "placement", "phases", "optimization", "legalization"],
                "max_score": 10,
                "complexity": 1
            },
            {
                "question": "What is cell density and why is uniform density distribution important in placement?",
                "category": "density",
                "keywords": ["density", "uniform", "distribution", "routing", "congestion", "placement"],
                "max_score": 10,
                "complexity": 1
            },
            {
                "question": "How do timing constraints influence placement decisions? Give examples.",
                "category": "timing",
                "keywords": ["timing", "constraints", "placement", "slack", "critical", "path"],
                "max_score": 10,
                "complexity": 1
            }
        ],
        "intermediate": [
            {
                "question": "Your placement shows timing violations on 15 critical paths with negative slack up to -75ps. Describe your systematic approach to fix these violations through placement optimization.",
                "category": "timing_optimization",
                "keywords": ["timing", "violations", "slack", "critical", "path", "optimization", "placement"],
                "max_score": 15,
                "complexity": 2
            },
            {
                "question": "You have high-fanout nets (>1000 fanout) causing placement convergence issues. How would you handle these nets during placement optimization?",
                "category": "high_fanout",
                "keywords": ["fanout", "nets", "convergence", "optimization", "buffering", "placement"],
                "max_score": 15,
                "complexity": 2
            },
            {
                "question": "Your design operates in multiple power modes (high-performance, balanced, low-power). How does this affect your placement strategy and optimization targets?",
                "category": "power_optimization",
                "keywords": ["power", "modes", "optimization", "strategy", "leakage", "dynamic", "placement"],
                "max_score": 15,
                "complexity": 2
            }
        ],
        "advanced": [
            {
                "question": "You're working on a safety-critical design requiring triple modular redundancy (TMR). Describe your placement strategy to maximize fault tolerance while meeting timing and area constraints.",
                "category": "reliability",
                "keywords": ["TMR", "redundancy", "fault", "tolerance", "safety", "critical", "placement", "timing"],
                "max_score": 20,
                "complexity": 3
            },
            {
                "question": "Your 7nm design has both logic and analog blocks with stringent noise requirements. Explain your comprehensive placement strategy for mixed-signal isolation and optimization.",
                "category": "advanced_mixed_signal",
                "keywords": ["7nm", "mixed", "signal", "noise", "isolation", "analog", "logic", "placement"],
                "max_score": 20,
                "complexity": 3
            }
        ]
    },
    "routing": {
        "beginner": [
            {
                "question": "Explain the routing hierarchy: global routing, track assignment, and detailed routing. What is accomplished at each stage?",
                "category": "fundamentals",
                "keywords": ["global", "track", "detailed", "routing", "hierarchy", "stages"],
                "max_score": 10,
                "complexity": 1
            },
            {
                "question": "What are DRC violations and why are they critical to fix before tapeout?",
                "category": "drc",
                "keywords": ["DRC", "violations", "tapeout", "manufacturing", "rules", "design"],
                "max_score": 10,
                "complexity": 1
            },
            {
                "question": "How does metal layer assignment affect signal integrity and manufacturing yield?",
                "category": "layer_assignment",
                "keywords": ["metal", "layer", "signal", "integrity", "yield", "manufacturing"],
                "max_score": 10,
                "complexity": 1
            }
        ],
        "intermediate": [
            {
                "question": "After global routing, you have 500 DRC violations (spacing, via, width) across multiple layers. Describe your systematic approach to resolve these violations efficiently.",
                "category": "drc_resolution",
                "keywords": ["DRC", "violations", "spacing", "via", "width", "systematic", "resolution"],
                "max_score": 15,
                "complexity": 2
            },
            {
                "question": "Your design has 20 differential pairs for high-speed interfaces running at 5Gbps. Explain your routing strategy to maintain 100-ohm impedance and minimize skew.",
                "category": "high_speed",
                "keywords": ["differential", "high", "speed", "impedance", "skew", "routing", "strategy"],
                "max_score": 15,
                "complexity": 2
            },
            {
                "question": "You're seeing 200ps timing degradation after detailed routing compared to placement estimates. What causes this and how would you recover the timing?",
                "category": "timing_closure",
                "keywords": ["timing", "degradation", "routing", "placement", "recovery", "parasitic"],
                "max_score": 15,
                "complexity": 2
            }
        ],
        "advanced": [
            {
                "question": "Your 5nm design has double patterning constraints causing 50+ decomposition conflicts. Describe your comprehensive strategy to handle LELE patterning requirements while maintaining timing closure.",
                "category": "advanced_process",
                "keywords": ["5nm", "double", "patterning", "LELE", "decomposition", "conflicts", "timing"],
                "max_score": 20,
                "complexity": 3
            },
            {
                "question": "You need to implement advanced power delivery with integrated voltage regulators (IVR) and dynamic voltage scaling. Explain your routing strategy for power integrity and electromagnetic compatibility.",
                "category": "advanced_power",
                "keywords": ["IVR", "voltage", "scaling", "power", "integrity", "electromagnetic", "routing"],
                "max_score": 20,
                "complexity": 3
            }
        ]
    }
}

# AI-powered scoring keywords with weights
SCORING_KEYWORDS = {
    "floorplanning": {
        "technical": ["macro", "timing", "power", "congestion", "utilization", "IR drop", "voltage", "domains"],
        "methodology": ["strategy", "approach", "methodology", "systematic", "optimization", "analysis"],
        "tools": ["floorplan", "placement", "routing", "verification", "analysis", "simulation"],
        "advanced": ["hierarchical", "partition", "interface", "mixed-signal", "isolation", "substrate"]
    },
    "placement": {
        "technical": ["timing", "slack", "critical", "path", "density", "congestion", "fanout", "optimization"],
        "methodology": ["global", "detailed", "systematic", "iterative", "convergence", "strategy"],
        "tools": ["placement", "optimization", "timing", "analysis", "verification", "simulation"],
        "advanced": ["redundancy", "TMR", "fault", "tolerance", "mixed-signal", "noise", "isolation"]
    },
    "routing": {
        "technical": ["DRC", "violations", "timing", "parasitic", "impedance", "skew", "crosstalk", "noise"],
        "methodology": ["global", "detailed", "systematic", "resolution", "strategy", "optimization"],
        "tools": ["routing", "analysis", "verification", "simulation", "extraction", "timing"],
        "advanced": ["patterning", "decomposition", "LELE", "IVR", "integrity", "electromagnetic"]
    }
}

# Intelligent question selection based on experience
def select_questions_intelligently(engineer_id, topic, num_questions=3):
    """AI-powered question selection based on engineer experience and performance"""
    engineer = users.get(engineer_id)
    if not engineer:
        return []
    
    experience = engineer['experience_years']
    
    # Determine difficulty distribution based on experience
    if experience <= 2:
        difficulty_weights = {"beginner": 0.7, "intermediate": 0.3, "advanced": 0.0}
    elif experience <= 4:
        difficulty_weights = {"beginner": 0.3, "intermediate": 0.6, "advanced": 0.1}
    else:
        difficulty_weights = {"beginner": 0.1, "intermediate": 0.4, "advanced": 0.5}
    
    # Select questions based on weights
    selected_questions = []
    questions_db = QUESTIONS_DATABASE.get(topic, {})
    
    for difficulty, weight in difficulty_weights.items():
        if weight > 0 and difficulty in questions_db:
            count = max(1, int(num_questions * weight))
            available_questions = questions_db[difficulty]
            if available_questions:
                selected = random.sample(available_questions, min(count, len(available_questions)))
                selected_questions.extend(selected)
    
    # Ensure we have exactly num_questions
    while len(selected_questions) < num_questions:
        all_questions = []
        for diff_questions in questions_db.values():
            all_questions.extend(diff_questions)
        if all_questions:
            remaining = random.sample(all_questions, min(num_questions - len(selected_questions), len(all_questions)))
            selected_questions.extend(remaining)
        else:
            break
    
    return selected_questions[:num_questions]

# Advanced AI scoring system
def calculate_ai_score(answer, question_data, topic):
    """Advanced AI-powered scoring with multiple criteria"""
    if not answer or not answer.strip():
        return {
            'score': 0,
            'breakdown': {'content': 0, 'technical': 0, 'methodology': 0, 'depth': 0},
            'feedback': "No answer provided",
            'confidence': 1.0
        }
    
    answer_lower = answer.lower()
    answer_words = answer.split()
    
    # Content completeness (based on answer length and structure)
    content_score = min(len(answer_words) / 50 * 2.5, 2.5)  # Max 2.5 points
    
    # Technical accuracy (keyword matching with weights)
    technical_score = 0
    keyword_categories = SCORING_KEYWORDS.get(topic, {})
    
    for category, keywords in keyword_categories.items():
        category_weight = {
            'technical': 1.0,
            'methodology': 0.8,
            'tools': 0.6,
            'advanced': 1.2
        }.get(category, 0.5)
        
        found_keywords = sum(1 for kw in keywords if kw in answer_lower)
        technical_score += found_keywords * category_weight * 0.3
    
    technical_score = min(technical_score, 2.5)  # Max 2.5 points
    
    # Methodology and approach (structure and reasoning)
    methodology_indicators = ['approach', 'strategy', 'methodology', 'systematic', 'first', 'then', 'next', 'because', 'therefore', 'analysis', 'consideration']
    methodology_score = min(sum(1 for indicator in methodology_indicators if indicator in answer_lower) * 0.3, 2.5)
    
    # Depth and detail (specific examples and detailed explanations)
    depth_indicators = ['example', 'specifically', 'detail', 'such as', 'including', 'particular', 'instance', 'case', 'scenario']
    depth_score = min(sum(1 for indicator in depth_indicators if indicator in answer_lower) * 0.4, 2.5)
    
    # Calculate total score
    total_score = content_score + technical_score + methodology_score + depth_score
    max_possible = question_data.get('max_score', 10)
    final_score = min(total_score, max_possible)
    
    # Generate feedback
    feedback_parts = []
    if content_score < 1:
        feedback_parts.append("Answer could be more comprehensive")
    if technical_score < 1:
        feedback_parts.append("More technical details needed")
    if methodology_score < 1:
        feedback_parts.append("Could include systematic approach")
    if depth_score < 1:
        feedback_parts.append("Add specific examples or scenarios")
    
    if not feedback_parts:
        feedback_parts.append("Good comprehensive answer")
    
    # Confidence based on answer quality indicators
    confidence = min((len(answer_words) / 30) * (technical_score / 2.5) * 1.2, 1.0)
    
    return {
        'score': round(final_score, 1),
        'breakdown': {
            'content': round(content_score, 1),
            'technical': round(technical_score, 1),
            'methodology': round(methodology_score, 1),
            'depth': round(depth_score, 1)
        },
        'feedback': "; ".join(feedback_parts),
        'confidence': round(confidence, 2)
    }

# Analytics and performance tracking
def track_performance(engineer_id, assignment_id, scores):
    """Track engineer performance for analytics"""
    if engineer_id not in answer_analytics:
        answer_analytics[engineer_id] = {
            'total_assessments': 0,
            'topic_performance': {},
            'skill_progression': [],
            'strengths': [],
            'improvement_areas': []
        }
    
    analytics = answer_analytics[engineer_id]
    analytics['total_assessments'] += 1
    
    assignment = assignments.get(assignment_id)
    if assignment:
        topic = assignment['topic']
        if topic not in analytics['topic_performance']:
            analytics['topic_performance'][topic] = []
        
        avg_score = statistics.mean([s['score'] for s in scores.values()])
        analytics['topic_performance'][topic].append({
            'date': datetime.now().isoformat(),
            'score': avg_score,
            'assignment_id': assignment_id
        })

def create_assignment(engineer_id, topic):
    global assignment_counter
    
    user = users.get(engineer_id)
    if not user or topic not in QUESTIONS_DATABASE:
        return None
    
    assignment_counter += 1
    assignment_id = f"PD_{topic.upper()}_{engineer_id}_{assignment_counter}"
    
    # Intelligent question selection
    questions = select_questions_intelligently(engineer_id, topic, 3)
    
    assignment = {
        'id': assignment_id,
        'engineer_id': engineer_id,
        'topic': topic,
        'questions': questions,
        'answers': {},
        'ai_scores': {},
        'final_scores': {},
        'status': 'pending',
        'created_date': datetime.now().isoformat(),
        'due_date': (datetime.now() + timedelta(days=3)).isoformat(),
        'total_score': None,
        'max_possible_score': sum(q.get('max_score', 10) for q in questions),
        'scored_by': None,
        'scored_date': None,
        'published_date': None,
        'difficulty_level': 'adaptive',
        'time_started': None,
        'time_completed': None
    }
    
    assignments[assignment_id] = assignment
    
    # Create notification
    if engineer_id not in notifications:
        notifications[engineer_id] = []
    
    notifications[engineer_id].append({
        'title': f'New {topic.title()} Assessment',
        'message': f'Adaptive difficulty assessment with 3 questions',
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
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len([u for u in users.values() if u.get('last_login')]),
        'total_assignments': len(assignments)
    }), 200

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
            user['last_login'] = datetime.now().isoformat()
            
            if user.get('is_admin'):
                return redirect('/admin')
            else:
                return redirect('/student')
        else:
            error = 'Invalid credentials'
    
    # Modern login page with enhanced UI
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PD Interview System - Intelligent Assessment Platform</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }}
            
            .background-animation {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                z-index: 0;
            }}
            
            .floating-shapes {{
                position: absolute;
                width: 300px;
                height: 300px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.1);
                animation: float 6s ease-in-out infinite;
            }}
            
            .shape1 {{ top: 10%; left: 10%; animation-delay: 0s; }}
            .shape2 {{ top: 60%; right: 10%; animation-delay: 2s; }}
            .shape3 {{ bottom: 10%; left: 30%; animation-delay: 4s; }}
            
            @keyframes float {{
                0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
                50% {{ transform: translateY(-20px) rotate(180deg); }}
            }}
            
            .login-container {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 50px 40px;
                width: 450px;
                box-shadow: 0 25px 45px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                position: relative;
                z-index: 1;
                animation: slideUp 0.8s ease-out;
            }}
            
            @keyframes slideUp {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .logo {{
                text-align: center;
                margin-bottom: 30px;
            }}
            
            .logo h1 {{
                color: #4f46e5;
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 8px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .logo p {{
                color: #6b7280;
                font-size: 16px;
                font-weight: 500;
            }}
            
            .form-group {{
                margin-bottom: 25px;
                position: relative;
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
                padding: 15px 20px;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                font-size: 16px;
                transition: all 0.3s ease;
                background: #f9fafb;
            }}
            
            .form-group input:focus {{
                outline: none;
                border-color: #4f46e5;
                box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
                background: white;
            }}
            
            .login-btn {{
                width: 100%;
                padding: 16px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
            }}
            
            .login-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4);
            }}
            
            .login-btn:active {{
                transform: translateY(0);
            }}
            
            .credentials-info {{
                background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
                border: 1px solid #38bdf8;
                border-radius: 12px;
                padding: 20px;
                margin: 25px 0;
                position: relative;
                overflow: hidden;
            }}
            
            .credentials-info::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 4px;
                height: 100%;
                background: linear-gradient(135deg, #0ea5e9, #0284c7);
            }}
            
            .credentials-info h4 {{
                color: #0f172a;
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
            }}
            
            .credentials-info h4::before {{
                content: '🔑';
                margin-right: 8px;
                font-size: 18px;
            }}
            
            .credentials-info p {{
                color: #475569;
                font-size: 14px;
                line-height: 1.6;
                margin-bottom: 8px;
            }}
            
            .credentials-info .engineer-creds {{
                background: rgba(34, 197, 94, 0.1);
                border-radius: 8px;
                padding: 12px;
                margin-top: 10px;
            }}
            
            .error {{
                background: linear-gradient(135deg, #fee2e2, #fecaca);
                border: 1px solid #f87171;
                color: #dc2626;
                padding: 15px;
                border-radius: 12px;
                margin-bottom: 20px;
                text-align: center;
                font-weight: 500;
                animation: shake 0.5s ease-in-out;
            }}
            
            @keyframes shake {{
                0%, 100% {{ transform: translateX(0); }}
                25% {{ transform: translateX(-5px); }}
                75% {{ transform: translateX(5px); }}
            }}
            
            .features {{
                text-align: center;
                margin-top: 25px;
                padding-top: 25px;
                border-top: 1px solid #e5e7eb;
            }}
            
            .features p {{
                color: #6b7280;
                font-size: 14px;
                margin-bottom: 15px;
            }}
            
            .feature-tags {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                justify-content: center;
            }}
            
            .feature-tag {{
                background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
                color: #374151;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
            }}
        </style>
    </head>
    <body>
        <div class="background-animation">
            <div class="floating-shapes shape1"></div>
            <div class="floating-shapes shape2"></div>
            <div class="floating-shapes shape3"></div>
        </div>
        
        <div class="login-container">
            <div class="logo">
                <h1>⚡ PD Assessment</h1>
                <p>Intelligent Interview System</p>
            </div>
            
            {f'<div class="error">❌ {error}</div>' if error else ''}
            
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" placeholder="Enter your username" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="Enter your password" required>
                </div>
                
                <button type="submit" class="login-btn">
                    Sign In to Assessment Platform
                </button>
            </form>
            
            <div class="credentials-info">
                <h4>Test Credentials</h4>
                <div class="engineer-creds">
                    <p><strong>👨‍💼 Engineers:</strong> eng001, eng002, eng003, eng004, eng005</p>
                    <p><strong>🔐 Password:</strong> password123</p>
                </div>
            </div>
            
            <div class="features">
                <p>✨ Enhanced with intelligent features</p>
                <div class="feature-tags">
                    <span class="feature-tag">🤖 AI Scoring</span>
                    <span class="feature-tag">📊 Analytics</span>
                    <span class="feature-tag">🎯 Adaptive Questions</span>
                    <span class="feature-tag">💡 Smart Feedback</span>
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
    published = [a for a in all_assignments if a['status'] == 'published']
    
    # Calculate statistics
    total_questions_answered = sum(len(a.get('answers', {})) for a in all_assignments)
    avg_score = statistics.mean([a['total_score'] for a in published if a['total_score']]) if published else 0
    
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Dashboard - PD Assessment System</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f8fafc;
                color: #1e293b;
                line-height: 1.6;
            }}
            
            .header {{
                background: linear-gradient(135deg, #1e40af, #3b82f6);
                color: white;
                padding: 25px 0;
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
                font-size: 28px;
                font-weight: 700;
                display: flex;
                align-items: center;
            }}
            
            .header h1::before {{
                content: '⚡';
                margin-right: 10px;
                font-size: 32px;
            }}
            
            .user-info {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .logout-btn {{
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
            }}
            
            .logout-btn:hover {{
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }}
            
            .container {{
                max-width: 1200px;
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
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                border: 1px solid #e2e8f0;
                position: relative;
                overflow: hidden;
                transition: all 0.3s ease;
            }}
            
            .stat-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            }}
            
            .stat-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            }}
            
            .stat-number {{
                font-size: 36px;
                font-weight: 700;
                color: #1e40af;
                margin-bottom: 8px;
            }}
            
            .stat-label {{
                color: #64748b;
                font-size: 14px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .stat-icon {{
                position: absolute;
                top: 20px;
                right: 20px;
                font-size: 24px;
                opacity: 0.3;
            }}
            
            .card {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                border: 1px solid #e2e8f0;
                margin-bottom: 30px;
                overflow: hidden;
            }}
            
            .card-header {{
                background: linear-gradient(135deg, #f8fafc, #e2e8f0);
                padding: 25px 30px;
                border-bottom: 1px solid #e2e8f0;
            }}
            
            .card-header h2 {{
                font-size: 20px;
                font-weight: 600;
                color: #1e293b;
                display: flex;
                align-items: center;
            }}
            
            .card-header h2::before {{
                content: attr(data-icon);
                margin-right: 10px;
                font-size: 24px;
            }}
            
            .card-body {{
                padding: 30px;
            }}
            
            .form-row {{
                display: flex;
                gap: 15px;
                align-items: end;
                flex-wrap: wrap;
            }}
            
            .form-group {{
                flex: 1;
                min-width: 200px;
            }}
            
            .form-group label {{
                display: block;
                margin-bottom: 8px;
                color: #374151;
                font-weight: 500;
                font-size: 14px;
            }}
            
            .form-group select {{
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                font-size: 14px;
                background: white;
                transition: all 0.3s ease;
            }}
            
            .form-group select:focus {{
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }}
            
            .btn {{
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                color: white;
                box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
            }}
            
            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 15px rgba(59, 130, 246, 0.4);
            }}
            
            .btn-success {{
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
                box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
            }}
            
            .btn-success:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 15px rgba(16, 185, 129, 0.4);
            }}
            
            .assignment-item {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 15px;
                transition: all 0.3s ease;
            }}
            
            .assignment-item:hover {{
                background: #f1f5f9;
                border-color: #cbd5e1;
            }}
            
            .assignment-header {{
                display: flex;
                justify-content: between;
                align-items: center;
                margin-bottom: 10px;
            }}
            
            .assignment-title {{
                font-weight: 600;
                color: #1e293b;
                font-size: 16px;
            }}
            
            .assignment-meta {{
                color: #64748b;
                font-size: 14px;
                margin-bottom: 15px;
            }}
            
            .assignment-actions {{
                display: flex;
                gap: 10px;
            }}
            
            .empty-state {{
                text-align: center;
                padding: 60px 20px;
                color: #64748b;
            }}
            
            .empty-state-icon {{
                font-size: 48px;
                margin-bottom: 20px;
                opacity: 0.5;
            }}
            
            .ai-badge {{
                background: linear-gradient(135deg, #8b5cf6, #7c3aed);
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                margin-left: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <h1>Admin Dashboard</h1>
                <div class="user-info">
                    <span>👨‍💼 {session['username']}</span>
                    <a href="/logout" class="logout-btn">Logout</a>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">👥</div>
                    <div class="stat-number">{len(engineers)}</div>
                    <div class="stat-label">Engineers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📋</div>
                    <div class="stat-number">{len(all_assignments)}</div>
                    <div class="stat-label">Total Assignments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">✅</div>
                    <div class="stat-number">{len(submitted)}</div>
                    <div class="stat-label">Awaiting Review</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-number">{avg_score:.1f}</div>
                    <div class="stat-label">Average Score</div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2 data-icon="🎯">Create New Assessment</h2>
                    <span class="ai-badge">🤖 AI-Powered</span>
                </div>
                <div class="card-body">
                    <form method="POST" action="/admin/create">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="engineer_id">Select Engineer</label>
                                <select name="engineer_id" id="engineer_id" required>
                                    <option value="">Choose engineer...</option>'''
    
    for eng in engineers:
        exp_level = "Junior" if eng['experience_years'] <= 2 else "Mid" if eng['experience_years'] <= 4 else "Senior"
        html += f'<option value="{eng["id"]}">{eng["username"]} ({exp_level} - {eng["experience_years"]}y - {eng["department"]})</option>'
    
    html += f'''
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="topic">Assessment Topic</label>
                                <select name="topic" id="topic" required>
                                    <option value="">Choose topic...</option>
                                    <option value="floorplanning">🏗️ Floorplanning</option>
                                    <option value="placement">📍 Placement</option>
                                    <option value="routing">🛤️ Routing</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <button type="submit" class="btn btn-primary">
                                    🚀 Create Assessment
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2 data-icon="⏳">Pending Reviews</h2>
                </div>
                <div class="card-body">'''
    
    if submitted:
        for a in submitted:
            engineer = users.get(a['engineer_id'], {})
            time_taken = "In progress"
            if a.get('time_completed') and a.get('time_started'):
                start = datetime.fromisoformat(a['time_started'])
                end = datetime.fromisoformat(a['time_completed'])
                minutes = int((end - start).total_seconds() / 60)
                time_taken = f"{minutes} minutes"
            
            html += f'''
                    <div class="assignment-item">
                        <div class="assignment-header">
                            <div class="assignment-title">
                                📝 {a["topic"].title()} Assessment
                                <span class="ai-badge">🤖 AI Scored</span>
                            </div>
                        </div>
                        <div class="assignment-meta">
                            👤 Engineer: {a["engineer_id"]} ({engineer.get("experience_years", 0)}y exp) | 
                            📅 Submitted: {a.get("submitted_date", "Unknown")[:10]} | 
                            ⏱️ Time: {time_taken} | 
                            🎯 Max Score: {a.get("max_possible_score", 30)}
                        </div>
                        <div class="assignment-actions">
                            <a href="/admin/review/{a["id"]}" class="btn btn-success">
                                🔍 Review & Score
                            </a>
                        </div>
                    </div>'''
    else:
        html += '''
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <h3>No pending reviews</h3>
                        <p>All assessments have been reviewed or no submissions yet.</p>
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
        assignment = create_assignment(engineer_id, topic)
        if assignment:
            # Add success notification for admin
            if 'admin' not in notifications:
                notifications['admin'] = []
            notifications['admin'].append({
                'title': 'Assessment Created',
                'message': f'Created {topic} assessment for {engineer_id}',
                'created_at': datetime.now().isoformat(),
                'type': 'success'
            })
    
    return redirect('/admin')

@app.route('/admin/review/<assignment_id>', methods=['GET', 'POST'])
def admin_review(assignment_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')
    
    assignment = assignments.get(assignment_id)
    if not assignment:
        return redirect('/admin')
    
    if request.method == 'POST':
        # Save final scores and publish results
        total_score = 0
        final_scores = {}
        
        for i, question in enumerate(assignment['questions']):
            ai_score_data = assignment.get('ai_scores', {}).get(str(i), {})
            manual_score = request.form.get(f'score_{i}', ai_score_data.get('score', 0))
            
            try:
                manual_score = float(manual_score)
                final_scores[str(i)] = manual_score
                total_score += manual_score
            except:
                final_scores[str(i)] = ai_score_data.get('score', 0)
                total_score += ai_score_data.get('score', 0)
        
        assignment['final_scores'] = final_scores
        assignment['total_score'] = round(total_score, 1)
        assignment['status'] = 'published'
        assignment['scored_by'] = session['username']
        assignment['scored_date'] = datetime.now().isoformat()
        assignment['published_date'] = datetime.now().isoformat()
        
        # Track performance analytics
        track_performance(assignment['engineer_id'], assignment_id, assignment['ai_scores'])
        
        # Notify engineer
        engineer_id = assignment['engineer_id']
        if engineer_id not in notifications:
            notifications[engineer_id] = []
        
        notifications[engineer_id].append({
            'title': 'Assessment Results Published',
            'message': f'Your {assignment["topic"]} assessment has been scored: {total_score:.1f}/{assignment["max_possible_score"]}',
            'created_at': datetime.now().isoformat(),
            'type': 'result'
        })
        
        return redirect('/admin')
    
    # Generate AI scores if not already done
    if not assignment.get('ai_scores'):
        ai_scores = {}
        for i, question in enumerate(assignment['questions']):
            answer = assignment.get('answers', {}).get(str(i), '')
            ai_score_data = calculate_ai_score(answer, question, assignment['topic'])
            ai_scores[str(i)] = ai_score_data
        assignment['ai_scores'] = ai_scores
    
    engineer = users.get(assignment['engineer_id'], {})
    
    # Review interface with AI insights
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Review Assessment - {assignment_id}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f8fafc;
                color: #1e293b;
                line-height: 1.6;
            }}
            
            .header {{
                background: linear-gradient(135deg, #1e40af, #3b82f6);
                color: white;
                padding: 20px 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            
            .header-content {{
                max-width: 1000px;
                margin: 0 auto;
                padding: 0 20px;
            }}
            
            .header h1 {{
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            
            .header-meta {{
                opacity: 0.9;
                font-size: 14px;
            }}
            
            .container {{
                max-width: 1000px;
                margin: 30px auto;
                padding: 0 20px;
            }}
            
            .assignment-info {{
                background: white;
                border-radius: 16px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                border: 1px solid #e2e8f0;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
            }}
            
            .info-item {{
                text-align: center;
                padding: 15px;
                background: #f8fafc;
                border-radius: 8px;
            }}
            
            .info-value {{
                font-size: 20px;
                font-weight: 600;
                color: #1e40af;
                margin-bottom: 5px;
            }}
            
            .info-label {{
                color: #64748b;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .question-card {{
                background: white;
                border-radius: 16px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                border: 1px solid #e2e8f0;
                overflow: hidden;
            }}
            
            .question-header {{
                background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
                padding: 20px 25px;
                border-bottom: 1px solid #e2e8f0;
            }}
            
            .question-title {{
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 8px;
            }}
            
            .question-meta {{
                display: flex;
                gap: 15px;
                font-size: 12px;
                color: #64748b;
            }}
            
            .meta-badge {{
                background: rgba(103, 126, 234, 0.1);
                color: #4f46e5;
                padding: 4px 10px;
                border-radius: 12px;
                font-weight: 500;
            }}
            
            .question-text {{
                font-size: 18px;
                line-height: 1.7;
                color: #1e293b;
                margin-bottom: 30px;
                padding: 25px;
                background: linear-gradient(135deg, #f8fafc, #f1f5f9);
                border-radius: 15px;
                border-left: 5px solid #667eea;
            }}
            
            .answer-section {{
                margin-bottom: 20px;
            }}
            
            .answer-label {{
                font-weight: 600;
                color: #374151;
                margin-bottom: 12px;
                font-size: 16px;
                display: flex;
                align-items: center;
            }}
            
            .answer-label::before {{
                content: '✍️';
                margin-right: 8px;
                font-size: 18px;
            }}
            
            .answer-textarea {{
                width: 100%;
                min-height: 180px;
                padding: 20px;
                border: 2px solid #e5e7eb;
                border-radius: 15px;
                font-size: 16px;
                line-height: 1.6;
                background: #fefefe;
                transition: all 0.3s ease;
                resize: vertical;
                font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            
            .answer-textarea:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 4px rgba(103, 126, 234, 0.1);
                background: white;
            }}
            
            .answer-textarea::placeholder {{
                color: #9ca3af;
                font-style: italic;
            }}
            
            .character-count {{
                text-align: right;
                font-size: 12px;
                color: #6b7280;
                margin-top: 8px;
            }}
            
            .submit-section {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                margin-top: 40px;
            }}
            
            .submit-warning {{
                background: linear-gradient(135deg, #fef3c7, #fde68a);
                border: 1px solid #f59e0b;
                color: #92400e;
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 25px;
                font-weight: 500;
            }}
            
            .submit-warning::before {{
                content: '⚠️';
                margin-right: 8px;
                font-size: 18px;
            }}
            
            .btn {{
                padding: 18px 40px;
                border: none;
                border-radius: 15px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 0 10px;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                box-shadow: 0 8px 25px rgba(103, 126, 234, 0.3);
            }}
            
            .btn-primary:hover {{
                transform: translateY(-3px);
                box-shadow: 0 15px 35px rgba(103, 126, 234, 0.4);
            }}
            
            .btn-secondary {{
                background: rgba(107, 114, 128, 0.1);
                color: #374151;
                border: 2px solid #d1d5db;
            }}
            
            .btn-secondary:hover {{
                background: rgba(107, 114, 128, 0.2);
                transform: translateY(-2px);
            }}
            
            .progress-bar {{
                width: 100%;
                height: 8px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                overflow: hidden;
                margin: 10px 0;
            }}
            
            .progress-fill {{
                height: 100%;
                background: linear-gradient(135deg, #10b981, #059669);
                transition: width 0.3s ease;
            }}
            
            .auto-save {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: rgba(16, 185, 129, 0.9);
                color: white;
                padding: 12px 20px;
                border-radius: 25px;
                font-size: 14px;
                font-weight: 500;
                transform: translateY(100px);
                transition: transform 0.3s ease;
                z-index: 1000;
            }}
            
            .auto-save.show {{
                transform: translateY(0);
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 0 15px;
                }}
                
                .question-card {{
                    padding: 25px;
                    margin-bottom: 20px;
                }}
                
                .question-header {{
                    flex-direction: column;
                    gap: 15px;
                    text-align: center;
                }}
                
                .answer-textarea {{
                    min-height: 150px;
                    padding: 15px;
                    font-size: 14px;
                }}
                
                .btn {{
                    width: 100%;
                    margin: 5px 0;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="assessment-header">
            <div class="header-content">
                <div class="assessment-title">
                    {topic_icon} {assignment["topic"].title()} Assessment
                </div>
                <div class="progress-info">
                    <span>📊 {len(assignment['questions'])} Questions</span>
                    <span>🎯 Max: {assignment.get('max_possible_score', 30)} Points</span>
                    <div class="timer" id="timer">⏱️ 00:00:00</div>
                </div>
            </div>
        </div>
        
        <div class="container">
            <form method="POST" id="assessmentForm">'''
    
    # Display each question
    for i, question in enumerate(assignment['questions']):
        complexity_stars = "⭐" * question.get('complexity', 1) + "☆" * (3 - question.get('complexity', 1))
        
        html += f'''
                <div class="question-card">
                    <div class="question-header">
                        <div class="question-number">
                            Question {i+1} of {len(assignment['questions'])}
                        </div>
                        <div class="question-meta">
                            <span class="meta-badge">📂 {question.get("category", "general").replace("_", " ").title()}</span>
                            <span class="meta-badge">⚡ {complexity_stars}</span>
                            <span class="meta-badge">🎯 {question.get("max_score", 10)} pts</span>
                        </div>
                    </div>
                    
                    <div class="question-text">
                        {question.get("question", "Question not available")}
                    </div>
                    
                    <div class="answer-section">
                        <label for="answer_{i}" class="answer-label">
                            Your Answer:
                        </label>
                        <textarea 
                            name="answer_{i}" 
                            id="answer_{i}"
                            class="answer-textarea"
                            placeholder="Provide a detailed, technical answer. Include specific examples, methodologies, and considerations. The AI scoring system will evaluate technical accuracy, completeness, and depth of understanding."
                            required
                            data-question="{i}"
                        ></textarea>
                        <div class="character-count" id="count_{i}">0 characters</div>
                    </div>
                </div>'''
    
    html += f'''
                <div class="submit-section">
                    <div class="submit-warning">
                        Please review all your answers before submitting. You cannot edit your responses after submission.
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                        </div>
                        <p style="color: #64748b; margin-top: 10px;">
                            <span id="answeredCount">0</span> of {len(assignment['questions'])} questions answered
                        </p>
                    </div>
                    
                    <button type="submit" class="btn btn-primary" id="submitBtn" disabled>
                        🚀 Submit Assessment
                    </button>
                    <a href="/student" class="btn btn-secondary">
                        ← Back to Dashboard
                    </a>
                </div>
            </form>
        </div>
        
        <div class="auto-save" id="autoSave">
            💾 Answers saved automatically
        </div>
        
        <script>
            let startTime = new Date();
            let answers = {{}};
            
            // Timer functionality
            function updateTimer() {{
                const now = new Date();
                const elapsed = now - startTime;
                const hours = Math.floor(elapsed / 3600000);
                const minutes = Math.floor((elapsed % 3600000) / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);
                
                document.getElementById('timer').textContent = 
                    `⏱️ ${{hours.toString().padStart(2, '0')}}:${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
            }}
            
            // Update timer every second
            setInterval(updateTimer, 1000);
            
            // Character counting and progress tracking
            document.querySelectorAll('.answer-textarea').forEach(textarea => {{
                const questionNum = textarea.dataset.question;
                const countElement = document.getElementById(`count_${{questionNum}}`);
                
                textarea.addEventListener('input', function() {{
                    const length = this.value.length;
                    countElement.textContent = `${{length}} characters`;
                    
                    // Update answers object
                    answers[questionNum] = this.value.trim();
                    updateProgress();
                    
                    // Show auto-save indicator
                    showAutoSave();
                }});
            }});
            
            // Progress tracking
            function updateProgress() {{
                const totalQuestions = {len(assignment['questions'])};
                const answeredQuestions = Object.keys(answers).filter(key => answers[key].length > 0).length;
                const percentage = (answeredQuestions / totalQuestions) * 100;
                
                document.getElementById('progressFill').style.width = percentage + '%';
                document.getElementById('answeredCount').textContent = answeredQuestions;
                
                // Enable submit button when all questions are answered
                const submitBtn = document.getElementById('submitBtn');
                if (answeredQuestions === totalQuestions) {{
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🚀 Submit Assessment';
                }} else {{
                    submitBtn.disabled = true;
                    submitBtn.textContent = `🚀 Answer ${{totalQuestions - answeredQuestions}} more question(s)`;
                }}
            }}
            
            // Auto-save indicator
            function showAutoSave() {{
                const autoSave = document.getElementById('autoSave');
                autoSave.classList.add('show');
                setTimeout(() => {{
                    autoSave.classList.remove('show');
                }}, 2000);
            }}
            
            // Form submission confirmation
            document.getElementById('assessmentForm').addEventListener('submit', function(e) {{
                const totalQuestions = {len(assignment['questions'])};
                const answeredQuestions = Object.keys(answers).filter(key => answers[key].length > 0).length;
                
                if (answeredQuestions < totalQuestions) {{
                    e.preventDefault();
                    alert(`Please answer all ${{totalQuestions}} questions before submitting.`);
                    return;
                }}
                
                const confirmSubmit = confirm(
                    'Are you sure you want to submit your assessment?\\n\\n' +
                    '⚠️ You cannot edit your answers after submission.\\n' +
                    '🤖 Your answers will be automatically scored by AI.\\n' +
                    '👨‍🏫 Final review will be done by admin.'
                );
                
                if (!confirmSubmit) {{
                    e.preventDefault();
                }}
            }});
            
            // Prevent accidental page reload
            window.addEventListener('beforeunload', function(e) {{
                const hasAnswers = Object.keys(answers).some(key => answers[key].length > 0);
                if (hasAnswers) {{
                    e.preventDefault();
                    e.returnValue = 'You have unsaved answers. Are you sure you want to leave?';
                }}
            }});
            
            // Initialize progress
            updateProgress();
        </script>
    </body>
    </html>
    '''
    return html

# Initialize system
init_users()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False);
                font-size: 12px;
                color: #64748b;
            }}
            
            .question-content {{
                padding: 25px;
            }}
            
            .question-text {{
                background: #f8fafc;
                border-left: 4px solid #3b82f6;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 0 8px 8px 0;
                font-size: 16px;
                line-height: 1.6;
            }}
            
            .answer-section {{
                margin-bottom: 25px;
            }}
            
            .answer-content {{
                background: #fefefe;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 15px;
                min-height: 100px;
                white-space: pre-wrap;
                font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
                font-size: 14px;
                line-height: 1.5;
            }}
            
            .ai-analysis {{
                background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
                border: 1px solid #0ea5e9;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            
            .ai-analysis h4 {{
                color: #0c4a6e;
                font-weight: 600;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
            }}
            
            .ai-analysis h4::before {{
                content: '🤖';
                margin-right: 8px;
                font-size: 18px;
            }}
            
            .score-breakdown {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 10px;
                margin-bottom: 15px;
            }}
            
            .score-item {{
                background: rgba(59, 130, 246, 0.1);
                padding: 10px;
                border-radius: 6px;
                text-align: center;
            }}
            
            .score-value {{
                font-weight: 600;
                color: #1e40af;
                font-size: 16px;
            }}
            
            .score-label {{
                font-size: 11px;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .ai-feedback {{
                background: rgba(34, 197, 94, 0.1);
                border-left: 3px solid #22c55e;
                padding: 12px;
                border-radius: 0 6px 6px 0;
                margin-top: 10px;
                font-size: 14px;
                color: #166534;
            }}
            
            .scoring-section {{
                background: #f8fafc;
                padding: 20px;
                border-radius: 12px;
            }}
            
            .score-input-group {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .score-input {{
                width: 80px;
                padding: 10px;
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                text-align: center;
                font-weight: 600;
                font-size: 16px;
            }}
            
            .score-input:focus {{
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }}
            
            .max-score {{
                color: #64748b;
                font-weight: 500;
            }}
            
            .confidence-indicator {{
                display: flex;
                align-items: center;
                gap: 8px;
                margin-top: 10px;
            }}
            
            .confidence-bar {{
                width: 100px;
                height: 6px;
                background: #e5e7eb;
                border-radius: 3px;
                overflow: hidden;
            }}
            
            .confidence-fill {{
                height: 100%;
                background: linear-gradient(135deg, #22c55e, #16a34a);
                transition: width 0.3s ease;
            }}
            
            .submit-section {{
                background: white;
                border-radius: 16px;
                padding: 25px;
                margin-top: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                border: 1px solid #e2e8f0;
                text-align: center;
            }}
            
            .btn {{
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                margin: 0 10px;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                color: white;
                box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
            }}
            
            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 15px rgba(59, 130, 246, 0.4);
            }}
            
            .btn-secondary {{
                background: #6b7280;
                color: white;
            }}
            
            .btn-secondary:hover {{
                background: #4b5563;
                transform: translateY(-2px);
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <h1>🔍 Assessment Review</h1>
                <div class="header-meta">
                    Assignment ID: {assignment_id} | Topic: {assignment["topic"].title()}
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="assignment-info">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-value">👤 {assignment["engineer_id"]}</div>
                        <div class="info-label">Engineer</div>
                    </div>
                    <div class="info-item">
                        <div class="info-value">{engineer.get("experience_years", 0)}y</div>
                        <div class="info-label">Experience</div>
                    </div>
                    <div class="info-item">
                        <div class="info-value">{engineer.get("department", "N/A")}</div>
                        <div class="info-label">Department</div>
                    </div>
                    <div class="info-item">
                        <div class="info-value">{assignment.get("max_possible_score", 30)}</div>
                        <div class="info-label">Max Score</div>
                    </div>
                </div>
            </div>
            
            <form method="POST">'''
    
    # Display each question with AI analysis
    for i, question in enumerate(assignment['questions']):
        answer = assignment.get('answers', {}).get(str(i), 'No answer provided')
        ai_score_data = assignment.get('ai_scores', {}).get(str(i), {})
        
        html += f'''
                <div class="question-card">
                    <div class="question-header">
                        <div class="question-title">Question {i+1} of {len(assignment['questions'])}</div>
                        <div class="question-meta">
                            <span>📊 Category: {question.get("category", "general").replace("_", " ").title()}</span>
                            <span>⚡ Complexity: {"●" * question.get("complexity", 1)}{"○" * (3 - question.get("complexity", 1))}</span>
                            <span>🎯 Max Points: {question.get("max_score", 10)}</span>
                        </div>
                    </div>
                    
                    <div class="question-content">
                        <div class="question-text">
                            {question.get("question", "Question not available")}
                        </div>
                        
                        <div class="answer-section">
                            <h4>📝 Engineer's Answer:</h4>
                            <div class="answer-content">{answer}</div>
                        </div>
                        
                        <div class="ai-analysis">
                            <h4>AI Analysis & Insights</h4>
                            
                            <div class="score-breakdown">
                                <div class="score-item">
                                    <div class="score-value">{ai_score_data.get("breakdown", {}).get("content", 0)}</div>
                                    <div class="score-label">Content</div>
                                </div>
                                <div class="score-item">
                                    <div class="score-value">{ai_score_data.get("breakdown", {}).get("technical", 0)}</div>
                                    <div class="score-label">Technical</div>
                                </div>
                                <div class="score-item">
                                    <div class="score-value">{ai_score_data.get("breakdown", {}).get("methodology", 0)}</div>
                                    <div class="score-label">Method</div>
                                </div>
                                <div class="score-item">
                                    <div class="score-value">{ai_score_data.get("breakdown", {}).get("depth", 0)}</div>
                                    <div class="score-label">Depth</div>
                                </div>
                            </div>
                            
                            <div class="ai-feedback">
                                💡 <strong>AI Feedback:</strong> {ai_score_data.get("feedback", "No feedback available")}
                            </div>
                            
                            <div class="confidence-indicator">
                                <span>🎯 AI Confidence:</span>
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: {ai_score_data.get('confidence', 0) * 100}%"></div>
                                </div>
                                <span>{ai_score_data.get('confidence', 0) * 100:.0f}%</span>
                            </div>
                        </div>
                        
                        <div class="scoring-section">
                            <div class="score-input-group">
                                <label for="score_{i}"><strong>👨‍🏫 Your Final Score:</strong></label>
                                <input 
                                    type="number" 
                                    name="score_{i}" 
                                    id="score_{i}"
                                    min="0" 
                                    max="{question.get('max_score', 10)}" 
                                    step="0.1"
                                    value="{ai_score_data.get('score', 0)}" 
                                    class="score-input"
                                    required
                                >
                                <span class="max-score">/ {question.get('max_score', 10)}</span>
                                <span style="margin-left: 15px; color: #64748b;">
                                    (AI Suggested: {ai_score_data.get('score', 0)})
                                </span>
                            </div>
                        </div>
                    </div>
                </div>'''
    
    total_ai_score = sum(ai_score_data.get('score', 0) for ai_score_data in assignment.get('ai_scores', {}).values())
    
    html += f'''
                <div class="submit-section">
                    <h3>📊 Assessment Summary</h3>
                    <p style="margin: 15px 0; color: #64748b;">
                        AI Suggested Total: <strong>{total_ai_score:.1f}/{assignment.get("max_possible_score", 30)}</strong> 
                        ({(total_ai_score/assignment.get("max_possible_score", 30)*100):.1f}%)
                    </p>
                    
                    <div style="margin-top: 25px;">
                        <button type="submit" class="btn btn-primary">
                            ✅ Publish Final Scores
                        </button>
                        <a href="/admin" class="btn btn-secondary">
                            ← Back to Dashboard
                        </a>
                    </div>
                </div>
            </form>
        </div>
        
        <script>
            // Auto-calculate total as user changes scores
            document.querySelectorAll('input[type="number"]').forEach(input => {{
                input.addEventListener('input', function() {{
                    let total = 0;
                    document.querySelectorAll('input[type="number"]').forEach(inp => {{
                        total += parseFloat(inp.value) || 0;
                    }});
                    
                    // Update display if summary exists
                    const summary = document.querySelector('.submit-section p');
                    if (summary) {{
                        const maxScore = {assignment.get("max_possible_score", 30)};
                        const percentage = (total/maxScore*100).toFixed(1);
                        summary.innerHTML = `Current Total: <strong>${{total.toFixed(1)}}/${{maxScore}}</strong> (${{percentage}}%)`;
                    }}
                }});
            }});
        </script>
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
    
    # Calculate performance stats
    completed = [a for a in my_assignments if a['status'] == 'published']
    avg_score = statistics.mean([a['total_score']/a.get('max_possible_score', 30)*100 for a in completed]) if completed else 0
    
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Engineer Dashboard - PD Assessment</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #1e293b;
            }}
            
            .header {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                padding: 25px 0;
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
                font-size: 28px;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .user-profile {{
                display: flex;
                align-items: center;
                gap: 15px;
                background: rgba(103, 126, 234, 0.1);
                padding: 12px 20px;
                border-radius: 25px;
            }}
            
            .user-avatar {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea, #764ba2);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 600;
            }}
            
            .logout-btn {{
                background: rgba(239, 68, 68, 0.1);
                color: #dc2626;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                margin-left: 15px;
            }}
            
            .logout-btn:hover {{
                background: rgba(239, 68, 68, 0.2);
                transform: translateY(-2px);
            }}
            
            .container {{
                max-width: 1200px;
                margin: 30px auto;
                padding: 0 20px;
            }}
            
            .stats-overview {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 25px;
                margin-bottom: 40px;
            }}
            
            .stat-card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .stat-card:hover {{
                transform: translateY(-10px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
            }}
            
            .stat-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: linear-gradient(135deg, #667eea, #764ba2);
            }}
            
            .stat-icon {{
                font-size: 48px;
                margin-bottom: 15px;
                display: block;
            }}
            
            .stat-number {{
                font-size: 32px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 8px;
            }}
            
            .stat-label {{
                color: #64748b;
                font-size: 14px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .assignments-section {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            .section-header {{
                display: flex;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 15px;
                border-bottom: 2px solid #f1f5f9;
            }}
            
            .section-header h2 {{
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
                display: flex;
                align-items: center;
            }}
            
            .section-header h2::before {{
                content: '📚';
                margin-right: 12px;
                font-size: 28px;
            }}
            
            .ai-badge {{
                background: linear-gradient(135deg, #8b5cf6, #7c3aed);
                color: white;
                padding: 6px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                margin-left: auto;
            }}
            
            .assignment-card {{
                background: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                padding: 25px;
                margin-bottom: 20px;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .assignment-card:hover {{
                border-color: #667eea;
                box-shadow: 0 8px 25px rgba(103, 126, 234, 0.15);
                transform: translateY(-5px);
            }}
            
            .assignment-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 15px;
            }}
            
            .assignment-title {{
                font-size: 20px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 8px;
            }}
            
            .assignment-topic {{
                display: inline-block;
                padding: 4px 12px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border-radius: 15px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .assignment-meta {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 15px;
                margin: 15px 0;
                padding: 15px;
                background: rgba(255, 255, 255, 0.7);
                border-radius: 12px;
            }}
            
            .meta-item {{
                text-align: center;
            }}
            
            .meta-value {{
                font-weight: 600;
                color: #1e293b;
                font-size: 16px;
                margin-bottom: 4px;
            }}
            
            .meta-label {{
                color: #64748b;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .status-badge {{
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .status-pending {{
                background: linear-gradient(135deg, #fbbf24, #f59e0b);
                color: white;
            }}
            
            .status-submitted {{
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                color: white;
            }}
            
            .status-published {{
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
            }}
            
            .score-display {{
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
                padding: 15px 20px;
                border-radius: 12px;
                text-align: center;
                margin-top: 15px;
            }}
            
            .score-display .score {{
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 5px;
            }}
            
            .score-display .percentage {{
                font-size: 14px;
                opacity: 0.9;
            }}
            
            .btn {{
                padding: 15px 25px;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                text-align: center;
                font-size: 14px;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                box-shadow: 0 4px 15px rgba(103, 126, 234, 0.3);
            }}
            
            .btn-primary:hover {{
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(103, 126, 234, 0.4);
            }}
            
            .empty-state {{
                text-align: center;
                padding: 60px 20px;
                color: #64748b;
            }}
            
            .empty-state-icon {{
                font-size: 64px;
                margin-bottom: 20px;
                opacity: 0.5;
            }}
            
            .empty-state h3 {{
                font-size: 20px;
                margin-bottom: 10px;
                color: #374151;
            }}
            
            .notification-dot {{
                width: 8px;
                height: 8px;
                background: #ef4444;
                border-radius: 50%;
                position: absolute;
                top: 15px;
                right: 15px;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.5; transform: scale(1.2); }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <h1>⚡ Engineer Dashboard</h1>
                <div class="user-profile">
                    <div class="user-avatar">{session['username'][0].upper()}</div>
                    <div>
                        <div style="font-weight: 600;">{session['username']}</div>
                        <div style="font-size: 12px; color: #64748b;">
                            {user.get('experience_years', 0)} years • {user.get('department', 'Engineering')}
                        </div>
                    </div>
                    <a href="/logout" class="logout-btn">Logout</a>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="stats-overview">
                <div class="stat-card">
                    <span class="stat-icon">📋</span>
                    <div class="stat-number">{len(my_assignments)}</div>
                    <div class="stat-label">Total Assessments</div>
                </div>
                <div class="stat-card">
                    <span class="stat-icon">✅</span>
                    <div class="stat-number">{len(completed)}</div>
                    <div class="stat-label">Completed</div>
                </div>
                <div class="stat-card">
                    <span class="stat-icon">📊</span>
                    <div class="stat-number">{avg_score:.1f}%</div>
                    <div class="stat-label">Average Score</div>
                </div>
                <div class="stat-card">
                    <span class="stat-icon">🎯</span>
                    <div class="stat-number">{user.get('experience_years', 0)}y</div>
                    <div class="stat-label">Experience</div>
                </div>
            </div>
            
            <div class="assignments-section">
                <div class="section-header">
                    <h2>My Assessments</h2>
                    <span class="ai-badge">🤖 AI-Enhanced</span>
                </div>'''
    
    if my_assignments:
        for a in my_assignments:
            status = a['status']
            topic_icon = {'floorplanning': '🏗️', 'placement': '📍', 'routing': '🛤️'}.get(a['topic'], '📝')
            
            # Calculate time info
            time_info = "Not started"
            if a.get('time_completed') and a.get('time_started'):
                start = datetime.fromisoformat(a['time_started'])
                end = datetime.fromisoformat(a['time_completed'])
                minutes = int((end - start).total_seconds() / 60)
                time_info = f"{minutes} min"
            elif a.get('time_started'):
                time_info = "In progress"
            
            html += f'''
                <div class="assignment-card">'''
            
            if status == 'pending':
                html += '<div class="notification-dot"></div>'
            
            html += f'''
                    <div class="assignment-header">
                        <div>
                            <div class="assignment-title">{topic_icon} {a["topic"].title()} Assessment</div>
                            <span class="assignment-topic">{a["topic"]}</span>
                        </div>
                        <span class="status-badge status-{status}">{status.upper()}</span>
                    </div>
                    
                    <div class="assignment-meta">
                        <div class="meta-item">
                            <div class="meta-value">{len(a['questions'])}</div>
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
                            <div class="meta-value">{time_info}</div>
                            <div class="meta-label">Duration</div>
                        </div>
                    </div>'''
            
            if status == 'published':
                percentage = (a['total_score'] / a.get('max_possible_score', 30)) * 100
                html += f'''
                    <div class="score-display">
                        <div class="score">{a["total_score"]:.1f} / {a.get("max_possible_score", 30)}</div>
                        <div class="percentage">{percentage:.1f}% • Reviewed by {a.get("scored_by", "Admin")}</div>
                    </div>'''
            elif status == 'submitted':
                html += '<p style="text-align: center; color: #3b82f6; font-weight: 500; margin-top: 15px;">⏳ Under review by admin</p>'
            elif status == 'pending':
                html += f'''
                    <a href="/student/assignment/{a["id"]}" class="btn btn-primary" style="margin-top: 15px; width: 100%;">
                        🚀 Start Assessment
                    </a>'''
            
            html += '</div>'
    else:
        html += '''
                <div class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <h3>No Assessments Yet</h3>
                    <p>Your assessments will appear here when created by the admin.</p>
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
        # Record start time if not already set
        if not assignment.get('time_started'):
            assignment['time_started'] = datetime.now().isoformat()
        
        # Save answers
        answers = {}
        for i in range(len(assignment['questions'])):
            answer = request.form.get(f'answer_{i}', '').strip()
            if answer:
                answers[str(i)] = answer
        
        if len(answers) == len(assignment['questions']):
            assignment['answers'] = answers
            assignment['status'] = 'submitted'
            assignment['time_completed'] = datetime.now().isoformat()
            assignment['submitted_date'] = datetime.now().isoformat()
            
            # Generate AI scores immediately
            ai_scores = {}
            for i, question in enumerate(assignment['questions']):
                answer = answers.get(str(i), '')
                ai_score_data = calculate_ai_score(answer, question, assignment['topic'])
                ai_scores[str(i)] = ai_score_data
            assignment['ai_scores'] = ai_scores
        
        return redirect('/student')
    
    # Record start time when assessment is first accessed
    if not assignment.get('time_started') and assignment['status'] == 'pending':
        assignment['time_started'] = datetime.now().isoformat()
    
    topic_icon = {'floorplanning': '🏗️', 'placement': '📍', 'routing': '🛤️'}.get(assignment['topic'], '📝')
    
    # Assessment interface
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
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #1e293b;
            }}
            
            .assessment-header {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                padding: 25px 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                position: sticky;
                top: 0;
                z-index: 100;
            }}
            
            .header-content {{
                max-width: 1000px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 20px;
            }}
            
            .assessment-title {{
                font-size: 24px;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .progress-info {{
                display: flex;
                align-items: center;
                gap: 20px;
                font-size: 14px;
                color: #64748b;
            }}
            
            .timer {{
                background: rgba(239, 68, 68, 0.1);
                color: #dc2626;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 600;
            }}
            
            .container {{
                max-width: 1000px;
                margin: 30px auto;
                padding: 0 20px;
            }}
            
            .question-card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 40px;
                margin-bottom: 30px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
            }}
            
            .question-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
            }}
            
            .question-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 25px;
                padding-bottom: 15px;
                border-bottom: 2px solid #f1f5f9;
            }}
            
            .question-number {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 12px 20px;
                border-radius: 25px;
                font-weight: 700;
                font-size: 16px;
            }}
            
            .question-meta {{
                display: flex;
                gap: 15pxpp.run(host='0.0.0.0', port=port, debug=False)
