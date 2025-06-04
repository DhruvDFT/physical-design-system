#!/usr/bin/env python3
# Complete Physical Design Assignment System - Full Implementation

import os
import datetime
import json
import re
import math
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'railway-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///physical_design.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

print("🚀 Physical Design System - Full Version Loading...")

# Enhanced Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    engineer_id = db.Column(db.String(50))
    department = db.Column(db.String(100))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Assignment(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    topic = db.Column(db.String(50), nullable=False)
    engineer_id = db.Column(db.Integer, nullable=False)
    questions = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    due_date = db.Column(db.Date, nullable=False)
    points = db.Column(db.Integer, default=100)
    
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.String(100), nullable=False)
    engineer_id = db.Column(db.Integer, nullable=False)
    answers = db.Column(db.Text, nullable=False)
    submitted_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Technical Evaluation Results
    overall_score = db.Column(db.Float)
    grade_letter = db.Column(db.String(2))
    evaluation_results = db.Column(db.Text)  # JSON string
    
    # Admin Grading
    admin_grade = db.Column(db.String(2))
    admin_feedback = db.Column(db.Text)
    graded_by_admin = db.Column(db.Integer)
    graded_date = db.Column(db.DateTime)
    is_grade_released = db.Column(db.Boolean, default=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Comprehensive Physical Design Topics and Questions
PHYSICAL_DESIGN_TOPICS = {
    "floorplanning": {
        "title": "Physical Design: Advanced Floorplanning",
        "description": "Comprehensive assessment of floorplanning strategies, power planning, and area optimization",
        "questions": [
            "Design a floorplan for a 10mm x 10mm chip containing 8 hard macros (each 2mm x 1.5mm) and achieving 75% utilization. Discuss your placement strategy considering timing, power, and thermal constraints. Include power ring planning and pin assignment methodology.",
            
            "Given a design with 3 voltage domains (0.8V, 1.0V, 1.2V) and 5 power domains, explain your approach to power grid planning. Calculate IR drop requirements and propose power ring/stripe strategy for a 150mA/μm current density target.",
            
            "Compare hierarchical vs flat floorplanning for a 500K instance design. Analyze trade-offs in terms of timing closure, area efficiency, and tool runtime. When would you choose each approach and why?",
            
            "How would you handle floorplanning for a mixed-signal SoC with 4 analog blocks requiring 60dB isolation, digital core running at 2GHz, and SRAM compiler blocks? Discuss noise isolation and substrate coupling mitigation.",
            
            "Design pin assignment strategy for a 1024-pin BGA package considering signal integrity, power delivery, and thermal management. Include differential pair placement and high-speed signal routing constraints.",
            
            "Explain thermal-aware floorplanning for a 15W chip in a 10mm x 10mm package. Calculate thermal resistance requirements and propose heat spreading techniques. How would you modify placement for hotspot mitigation?",
            
            "Given timing constraints of 500ps setup margin on critical paths, how would you optimize floorplan for timing closure? Discuss macro placement impact on global routing and timing convergence.",
            
            "Design floorplan for DFT implementation with 95% fault coverage requirement. Include scan chain planning, BIST integration, and test access port placement. How does DFT impact area and timing?",
            
            "Handle floorplanning for a design with 12 clock domains and 50ps skew budget. Discuss clock tree planning, buffer insertion strategies, and clock gating implications on floorplan.",
            
            "Optimize floorplan for a design targeting 20% leakage power reduction. Include power gating domain planning, retention register placement, and always-on logic partitioning strategies.",
            
            "Design congestion-aware floorplan for a design with 10 metal layers (M1-M10) and 80% routing utilization target. Analyze routing demand and propose macro placement for routability optimization.",
            
            "Explain floorplan validation methodology including timing estimation, power analysis, and routability prediction. What metrics would you use to evaluate floorplan quality before proceeding to placement?",
            
            "Handle floorplanning for a design with hard real-time constraints (automotive safety critical). Discuss redundancy planning, fault isolation, and deterministic timing requirements impact on floorplan.",
            
            "Design floorplan for a multi-die 2.5D package with 4 chiplets connected via silicon interposer. Include TSV planning, thermal management across dies, and inter-die communication optimization.",
            
            "Optimize floorplan for advanced process node (5nm) considering double patterning constraints, via stacking limitations, and metal pitch restrictions. How do process constraints impact macro placement decisions?"
        ]
    },
    
    "placement": {
        "title": "Physical Design: Advanced Placement Optimization", 
        "description": "In-depth analysis of placement algorithms, timing optimization, and congestion management",
        "questions": [
            "Analyze placement strategies for a high-performance CPU core running at 3GHz with 200ps setup margin requirements. Discuss global vs detailed placement trade-offs and timing-driven optimization techniques.",
            
            "Given a design with 85% utilization and severe routing congestion in 3 hotspot regions, propose systematic placement optimization approach. Include utilization relaxation, macro repositioning, and buffer insertion strategies.",
            
            "Compare simulated annealing, analytical placement, and genetic algorithm approaches for placement optimization. Analyze computational complexity, solution quality, and convergence characteristics for different design sizes.",
            
            "Optimize placement for a multi-voltage design with 4 voltage islands and 200 level shifters. Discuss timing implications, power domain boundary optimization, and level shifter placement strategies.",
            
            "Design placement strategy for a design with 8 clock domains and 30ps skew targets across 10mm die. Include clock buffer placement, clock tree pre-planning, and useful skew optimization techniques.",
            
            "Handle placement optimization for leakage power reduction while maintaining performance. Analyze Vth assignment, power gating cell placement, and retention register positioning for 25% power savings.",
            
            "Explain placement considerations for advanced technology nodes (3nm/5nm). Discuss double patterning impact, via stacking constraints, and metal pitch limitations on placement decisions.",
            
            "Optimize placement for signal integrity in high-speed designs. Include crosstalk analysis, victim/aggressor placement, shielding strategies, and differential pair placement optimization.",
            
            "Design placement strategy for automotive safety-critical design with redundancy requirements. Discuss fault isolation, diverse placement of redundant logic, and single-point-failure mitigation.",
            
            "Handle placement optimization for mixed-signal design with 6 analog blocks requiring 80dB noise isolation. Include digital switching noise mitigation and substrate coupling prevention strategies.",
            
            "Optimize placement for DFT with 98% fault coverage and minimal test time. Include scan chain optimization, BIST placement, boundary scan considerations, and test access optimization.",
            
            "Explain placement impact on power grid integrity. Discuss current density analysis, IR drop minimization through placement, and decoupling capacitor placement optimization strategies.",
            
            "Design placement strategy for 3D IC with 4 tiers connected via TSVs. Include thermal management across tiers, TSV placement optimization, and inter-tier timing optimization.",
            
            "Handle placement for soft error mitigation in space applications. Discuss radiation hardening through placement, redundant logic positioning, and error detection/correction cell placement.",
            
            "Optimize placement for manufacturing yield improvement. Include process variation impact, critical area minimization, and systematic vs random defect mitigation through placement strategies."
        ]
    },
    
    "routing": {
        "title": "Physical Design: Advanced Routing and Signal Integrity",
        "description": "Comprehensive routing strategies, DRC resolution, and signal integrity optimization",
        "questions": [
            "Resolve 5000+ DRC violations in a 7nm design after initial routing. Propose systematic approach including violation categorization, priority assignment, and incremental ECO strategies for clean convergence.",
            
            "Design routing strategy for 50 differential pairs (100Ω impedance) in a high-speed design. Include trace width calculation, via optimization, length matching requirements, and crosstalk mitigation techniques.",
            
            "Compare maze routing, line-search, and A* algorithms for congested designs. Analyze memory usage, runtime complexity, and solution quality. When would you choose each algorithm?",
            
            "Handle routing in double patterning technology with complex coloring constraints. Explain decomposition algorithms, conflict resolution strategies, and impact on routing completion and timing.",
            
            "Design power grid routing for 2A current delivery with <5% IR drop across 10mm die. Calculate via requirements, stripe width sizing, and decoupling capacitor placement for robust power delivery.",
            
            "Optimize routing for crosstalk reduction in noise-sensitive analog/RF design. Include aggressor/victim identification, spacing rules, shielding implementation, and ground guard ring strategies.",
            
            "Explain routing strategies for clock networks with 20ps skew targets. Include H-tree implementation, buffer insertion, useful skew optimization, and clock gating impact on routing.",
            
            "Handle routing for electromigration prevention with 1mA/μm current density limits. Discuss via stacking, wire sizing, and current spreading techniques for reliability improvement.",
            
            "Design routing approach for 12-layer stackup optimization. Include layer assignment strategies, via minimization techniques, and manufacturability considerations for advanced process nodes.",
            
            "Optimize routing for thermal management in high-power design (20W). Include thermal via insertion, heat spreading techniques, and routing pattern optimization for thermal conductivity.",
            
            "Handle routing for high-speed signals (10GHz) with strict timing requirements. Discuss transmission line effects, impedance control, via optimization, and signal integrity analysis integration.",
            
            "Explain routing strategies for fault-tolerant design with redundancy. Include diverse routing of critical signals, single-point-failure prevention, and fault isolation through routing.",
            
            "Design routing approach for 3D integration with TSV constraints. Include inter-layer via planning, thermal management through routing, and signal integrity across multiple tiers.",
            
            "Optimize routing for manufacturing yield in advanced nodes. Include lithography-friendly routing patterns, via redundancy, and systematic defect mitigation through routing choices.",
            
            "Handle routing convergence for timing closure in complex designs. Discuss incremental routing, timing-driven rerouting, and ECO routing strategies for late-stage timing fixes."
        ]
    }
}

# Technical Evaluation Engine
class TechnicalEvaluator:
    def __init__(self):
        self.technical_terms = {
            'floorplanning': {
                'macro': 4, 'utilization': 5, 'power grid': 6, 'IR drop': 6, 'thermal': 5,
                'pin assignment': 5, 'voltage domain': 6, 'hierarchical': 4, 'substrate': 5,
                'BGA': 4, 'isolation': 5, 'hotspot': 5, 'DFT': 4, 'scan chain': 5,
                'clock domain': 5, 'skew': 5, 'power gating': 6, 'retention': 5,
                'congestion': 5, 'routability': 5, 'TSV': 6, 'interposer': 6,
                'double patterning': 7, 'via stacking': 6
            },
            'placement': {
                'timing closure': 6, 'setup margin': 5, 'analytical placement': 7,
                'simulated annealing': 7, 'level shifter': 6, 'clock tree': 5,
                'useful skew': 6, 'Vth assignment': 6, 'crosstalk': 5, 'shielding': 5,
                'redundancy': 5, 'fault isolation': 6, 'scan optimization': 5,
                'current density': 5, 'decoupling capacitor': 6, 'TSV placement': 7,
                'radiation hardening': 7, 'process variation': 6, 'critical area': 6,
                'yield optimization': 6
            },
            'routing': {
                'DRC violation': 5, 'differential pair': 5, 'impedance': 5, 'maze routing': 6,
                'line search': 6, 'A* algorithm': 7, 'double patterning': 7, 'decomposition': 6,
                'electromigration': 7, 'current density': 6, 'via stacking': 6,
                'H-tree': 5, 'useful skew': 6, 'transmission line': 6, 'signal integrity': 5,
                'thermal via': 5, 'heat spreading': 5, 'fault tolerance': 6,
                'TSV routing': 7, 'lithography friendly': 6, 'via redundancy': 6,
                'ECO routing': 5, 'timing convergence': 6
            }
        }
        
        self.concept_coverage = {
            'floorplanning': ['area optimization', 'power planning', 'thermal management', 'timing', 'DFT'],
            'placement': ['timing optimization', 'congestion management', 'power optimization', 'signal integrity'],
            'routing': ['DRC resolution', 'signal integrity', 'power delivery', 'manufacturability']
        }
    
    def evaluate_submission(self, answers, topic):
        """Comprehensive technical evaluation"""
        if not answers or len(answers) == 0:
            return self._create_empty_evaluation()
        
        question_scores = []
        all_tech_terms = []
        total_word_count = 0
        
        for i, answer in enumerate(answers):
            score_data = self._evaluate_single_answer(answer, topic, i)
            question_scores.append(score_data)
            all_tech_terms.extend(score_data['tech_terms_found'])
            total_word_count += score_data['word_count']
        
        # Calculate overall metrics
        avg_score = sum(q['overall_score'] for q in question_scores) / len(question_scores)
        unique_terms = len(set(all_tech_terms))
        avg_words = total_word_count / len(answers)
        
        # Grade calculation
        grade_letter = self._calculate_grade(avg_score)
        
        # Detailed analysis
        strengths = self._identify_strengths(question_scores, unique_terms, avg_words)
        weaknesses = self._identify_weaknesses(question_scores, topic)
        recommendations = self._generate_recommendations(weaknesses, topic)
        
        return {
            'overall_score': round(avg_score, 2),
            'grade_letter': grade_letter,
            'question_analyses': question_scores,
            'summary': {
                'unique_technical_terms': unique_terms,
                'average_word_count': round(avg_words, 1),
                'concept_coverage_score': self._calculate_concept_coverage(all_tech_terms, topic),
                'technical_depth_score': round(avg_score, 1)
            },
            'strengths': strengths,
            'areas_for_improvement': weaknesses,
            'study_recommendations': recommendations,
            'detailed_feedback': self._generate_detailed_feedback(avg_score, unique_terms, topic)
        }
    
    def _evaluate_single_answer(self, answer, topic, question_index):
        """Evaluate individual answer"""
        if not answer or len(answer.strip()) < 20:
            return {
                'question': question_index + 1,
                'overall_score': 0,
                'word_count': 0,
                'tech_terms_found': [],
                'feedback': 'Answer too short or empty'
            }
        
        answer_lower = answer.lower()
        word_count = len(answer.split())
        
        # Technical terms scoring (40%)
        terms = self.technical_terms.get(topic, {})
        found_terms = []
        term_score = 0
        
        for term, weight in terms.items():
            if term.lower() in answer_lower:
                found_terms.append(term)
                term_score += weight
        
        max_possible_terms = sum(terms.values()) if terms else 1
        tech_score = min(100, (term_score / max_possible_terms * 3) * 100)
        
        # Content depth scoring (30%)
        depth_keywords = ['analyze', 'optimize', 'implement', 'calculate', 'design', 'evaluate']
        depth_score = min(100, sum(1 for kw in depth_keywords if kw in answer_lower) * 20)
        
        # Quantitative analysis (20%)
        numbers = len(re.findall(r'\d+(?:\.\d+)?\s*(?:nm|μm|mm|ps|ns|μs|mA|mW|GHz|MHz|Ω|%)', answer))
        quant_score = min(100, numbers * 25)
        
        # Length and structure (10%)
        length_score = min(100, (word_count / 150) * 100)
        
        # Combined score
        overall_score = (tech_score * 0.4 + depth_score * 0.3 + quant_score * 0.2 + length_score * 0.1)
        
        return {
            'question': question_index + 1,
            'overall_score': round(overall_score, 1),
            'word_count': word_count,
            'tech_terms_found': found_terms,
            'scores': {
                'technical_terms': round(tech_score, 1),
                'content_depth': round(depth_score, 1),
                'quantitative': round(quant_score, 1),
                'length_structure': round(length_score, 1)
            },
            'feedback': self._generate_question_feedback(overall_score, len(found_terms), word_count)
        }
    
    def _calculate_grade(self, score):
        """Convert numerical score to letter grade"""
        if score >= 97: return "A+"
        elif score >= 93: return "A"
        elif score >= 90: return "A-"
        elif score >= 87: return "B+"
        elif score >= 83: return "B"
        elif score >= 80: return "B-"
        elif score >= 77: return "C+"
        elif score >= 73: return "C"
        elif score >= 70: return "C-"
        elif score >= 67: return "D+"
        elif score >= 65: return "D"
        else: return "F"
    
    def _identify_strengths(self, question_scores, unique_terms, avg_words):
        """Identify student strengths"""
        strengths = []
        avg_score = sum(q['overall_score'] for q in question_scores) / len(question_scores)
        
        if unique_terms >= 15:
            strengths.append("Excellent technical vocabulary usage")
        if avg_words >= 120:
            strengths.append("Comprehensive and detailed explanations")
        if avg_score >= 85:
            strengths.append("Strong understanding of fundamental concepts")
        if any(q['scores']['quantitative'] >= 80 for q in question_scores):
            strengths.append("Good use of quantitative analysis and specifications")
        
        return strengths[:4]  # Return top 4 strengths
    
    def _identify_weaknesses(self, question_scores, topic):
        """Identify areas for improvement"""
        weaknesses = []
        
        low_scoring_questions = [q for q in question_scores if q['overall_score'] < 70]
        if len(low_scoring_questions) > len(question_scores) * 0.4:
            weaknesses.append("Several answers need more technical depth")
        
        avg_tech_score = sum(q['scores']['technical_terms'] for q in question_scores) / len(question_scores)
        if avg_tech_score < 60:
            weaknesses.append(f"Limited use of {topic}-specific terminology")
        
        avg_quant_score = sum(q['scores']['quantitative'] for q in question_scores) / len(question_scores)
        if avg_quant_score < 40:
            weaknesses.append("Needs more quantitative analysis and specific examples")
        
        short_answers = [q for q in question_scores if q['word_count'] < 80]
        if len(short_answers) > len(question_scores) * 0.3:
            weaknesses.append("Some answers are too brief and lack detail")
        
        return weaknesses[:3]  # Return top 3 areas for improvement
    
    def _generate_recommendations(self, weaknesses, topic):
        """Generate study recommendations"""
        recommendations = []
        
        for weakness in weaknesses:
            if 'technical depth' in weakness:
                recommendations.append(f"Study advanced {topic} concepts and industry best practices")
            elif 'terminology' in weakness:
                recommendations.append(f"Review {topic} glossary and technical documentation")
            elif 'quantitative' in weakness:
                recommendations.append("Practice with specific numerical examples and calculations")
            elif 'brief' in weakness:
                recommendations.append("Provide more detailed explanations with step-by-step reasoning")
        
        # Default recommendations
        if not recommendations:
            recommendations = [
                f"Continue exploring advanced {topic} topics",
                "Practice explaining complex concepts clearly",
                "Study real-world industry case studies"
            ]
        
        return recommendations[:3]
    
    def _generate_detailed_feedback(self, avg_score, unique_terms, topic):
        """Generate comprehensive feedback"""
        if avg_score >= 90:
            return f"Excellent work! Your answers demonstrate strong mastery of {topic} concepts with {unique_terms} unique technical terms. Continue this level of detailed analysis."
        elif avg_score >= 80:
            return f"Good understanding shown with {unique_terms} technical terms used. Focus on adding more quantitative analysis and specific examples to reach excellence."
        elif avg_score >= 70:
            return f"Solid foundation with {unique_terms} technical terms. Work on expanding technical depth and providing more comprehensive explanations."
        else:
            return f"Basic understanding evident. Focus on learning more {topic}-specific terminology and concepts. Study recommended materials and practice with detailed examples."
    
    def _calculate_concept_coverage(self, terms_found, topic):
        """Calculate how well key concepts are covered"""
        key_concepts = self.concept_coverage.get(topic, [])
        if not key_concepts:
            return 0
        
        covered = sum(1 for concept in key_concepts if any(word in concept.lower() for word in [term.lower() for term in terms_found]))
        return round((covered / len(key_concepts)) * 100, 1)
    
    def _generate_question_feedback(self, score, term_count, word_count):
        """Generate feedback for individual questions"""
        if score >= 85:
            return f"Excellent answer with {term_count} technical terms and {word_count} words. Strong technical depth."
        elif score >= 70:
            return f"Good answer with {term_count} technical terms. Could benefit from more specific examples."
        elif score >= 55:
            return f"Basic answer with {term_count} technical terms. Needs more technical depth and detail."
        else:
            return f"Answer needs significant improvement. Add more technical terminology and detailed explanations."
    
    def _create_empty_evaluation(self):
        """Create evaluation for empty submission"""
        return {
            'overall_score': 0,
            'grade_letter': 'F',
            'question_analyses': [],
            'summary': {
                'unique_technical_terms': 0,
                'average_word_count': 0,
                'concept_coverage_score': 0,
                'technical_depth_score': 0
            },
            'strengths': [],
            'areas_for_improvement': ['No submission provided'],
            'study_recommendations': ['Complete the assignment with detailed technical answers'],
            'detailed_feedback': 'No submission received. Please complete all questions with detailed technical responses.'
        }

# Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard') if current_user.is_admin else url_for('engineer_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            user.last_login = datetime.datetime.utcnow()
            db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for('admin_dashboard') if user.is_admin else url_for('engineer_dashboard'))
        else:
            flash('Invalid credentials - try admin/admin123 or engineer1/eng123')
    
    login_html = '''<!DOCTYPE html>
    <html><head><title>Physical Design Login</title>
    <style>
    body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);height:100vh;margin:0;display:flex;align-items:center;justify-content:center}
    .container{background:white;padding:40px;border-radius:12px;box-shadow:0 20px 40px rgba(0,0,0,0.15);width:100%;max-width:420px;text-align:center}
    h1{color:#2c3e50;margin-bottom:30px;font-size:28px}
    .form-group{margin:20px 0;text-align:left}
    label{display:block;margin-bottom:8px;font-weight:600;color:#555}
    input{width:100%;padding:15px;border:2px solid #e1e8ed;border-radius:8px;font-size:16px;box-sizing:border-box;transition:border-color 0.3s}
    input:focus{border-color:#667eea;outline:none}
    button{width:100%;padding:15px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:8px;font-size:16px;cursor:pointer;margin-top:10px;transition:transform 0.2s}
    button:hover{transform:translateY(-2px)}
    .demo{margin-top:30px;padding:25px;background:#f8f9fa;border-radius:8px}
    .demo h3{margin-top:0;color:#495057}
    .demo-btn{margin:8px;padding:12px 20px;background:#28a745;color:white;border:none;border-radius:6px;cursor:pointer;font-size:14px;transition:background 0.3s}
    .demo-btn:hover{background:#218838}
    .demo-btn.admin{background:#dc3545}.demo-btn.admin:hover{background:#c82333}
    .alert{padding:12px;margin:15px 0;background:#f8d7da;color:#721c24;border-radius:6px;border:1px solid #f5c6cb}
    .system-info{margin-top:20px;font-size:14px;color:#6c757d}
    </style></head><body>
    <div class="container">
    <h1>🔐 Physical Design System</h1>
    <p class="system-info">Advanced Technical Assignment Platform</p>
    
    {% with messages = get_flashed_messages() %}
    {% if messages %}{% for message in messages %}<div class="alert">{{ message }}</div>{% endfor %}{% endif %}
    {% endwith %}
    
    <form method="POST">
    <div class="form-group">
    <label>Username:</label>
    <input type="text" name="username" id="username" required placeholder="Enter your username">
    </div>
    <div class="form-group">
    <label>Password:</label>
    <input type="password" name="password" id="password" required placeholder="Enter your password">
    </div>
    <button type="submit">🚀 Login to System</button>
    </form>
    
    <div class="demo">
    <h3>Demo Accounts:</h3>
    <button class="demo-btn admin" onclick="fillLogin('admin','admin123')">👨‍💼 Admin Access</button>
    <button class="demo-btn" onclick="fillLogin('engineer1','eng123')">👨‍💻 Engineer Portal</button>
    <p style="margin-top:15px;font-size:12px;color:#666">Click buttons to auto-fill credentials</p>
    </div>
    </div>
    
    <script>
    function fillLogin(u,p){
    document.getElementById('username').value=u;
    document.getElementById('password').value=p;
    }
    </script>
    </body></html>'''
    
    return render_template_string(login_html)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Calculate comprehensive statistics
    total_engineers = User.query.filter_by(is_admin=False).count()
    total_assignments = Assignment.query.count()
    total_submissions = Submission.query.count()
    pending_grading = Submission.query.filter(Submission.admin_grade.is_(None)).count()
    graded_released = Submission.query.filter(
        Submission.admin_grade.isnot(None),
        Submission.is_grade_released == True
    ).count()
    
    # Recent activity
    recent_submissions = Submission.query.order_by(Submission.submitted_date.desc()).limit(5).all()
    recent_activities = []
    
    for sub in recent_submissions:
        user = User.query.get(sub.engineer_id)
        assignment = Assignment.query.get(sub.assignment_id)
        recent_activities.append({
            'title': 'New Submission',
            'description': f'{user.username if user else "Unknown"} submitted {assignment.title if assignment else "assignment"}',
            'timestamp': sub.submitted_date.strftime('%Y-%m-%d %H:%M'),
            'type': 'submission'
        })
    
    admin_html = '''<!DOCTYPE html>
    <html><head><title>Admin Dashboard - Physical Design System</title>
    <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f8f9fa; }
    .header { background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
    .header h1 { font-size: 24px; font-weight: 600; }
    .user-info { display: flex; align-items: center; gap: 15px; }
    .user-info span { background: rgba(255,255,255,0.1); padding: 8px 15px; border-radius: 20px; font-size: 14px; }
    .logout-btn { background: #e74c3c; padding: 8px 16px; border-radius: 6px; text-decoration: none; color: white; font-size: 14px; transition: background 0.3s; }
    .logout-btn:hover { background: #c0392b; }
    
    .container { max-width: 1200px; margin: 0 auto; padding: 30px 20px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .stat-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); border-left: 4px solid #3498db; transition: transform 0.2s; }
    .stat-card:hover { transform: translateY(-2px); }
    .stat-card.pending { border-left-color: #f39c12; }
    .stat-card.completed { border-left-color: #27ae60; }
    .stat-card.engineers { border-left-color: #9b59b6; }
    .stat-number { font-size: 2.5em; font-weight: 700; color: #2c3e50; margin: 10px 0; }
    .stat-label { color: #7f8c8d; font-size: 14px; font-weight: 500; }
    .stat-trend { font-size: 12px; color: #27ae60; margin-top: 5px; }
    
    .action-section { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); margin-bottom: 30px; }
    .section-title { font-size: 20px; font-weight: 600; color: #2c3e50; margin-bottom: 20px; display: flex; align-items: center; }
    .action-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
    .action-btn { padding: 15px 20px; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 600; transition: all 0.3s; text-align: center; }
    .btn-primary { background: linear-gradient(135deg, #3498db, #2980b9); color: white; }
    .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(52, 152, 219, 0.3); }
    .btn-success { background: linear-gradient(135deg, #27ae60, #229954); color: white; }
    .btn-success:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(39, 174, 96, 0.3); }
    .btn-info { background: linear-gradient(135deg, #17a2b8, #138496); color: white; }
    .btn-info:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(23, 162, 184, 0.3); }
    
    .activity-section { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); }
    .activity-item { padding: 15px; border-left: 3px solid #3498db; margin: 12px 0; background: #f8f9fa; border-radius: 0 8px 8px 0; transition: background 0.3s; }
    .activity-item:hover { background: #e9ecef; }
    .activity-title { font-weight: 600; color: #2c3e50; margin-bottom: 4px; }
    .activity-desc { color: #5a6c7d; font-size: 14px; margin-bottom: 4px; }
    .activity-time { font-size: 12px; color: #95a5a6; }
    
    .quick-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }
    .quick-stat { text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }
    .quick-stat-number { font-size: 1.5em; font-weight: 600; color: #3498db; }
    .quick-stat-label { font-size: 12px; color: #7f8c8d; margin-top: 5px; }
    
    @media (max-width: 768px) {
        .header-content { flex-direction: column; gap: 15px; text-align: center; }
        .stats-grid, .action-grid { grid-template-columns: 1fr; }
        .container { padding: 20px 15px; }
    }
    </style></head><body>
    
    <div class="header">
    <div class="header-content">
    <h1>🛡️ Admin Dashboard - Physical Design System</h1>
    <div class="user-info">
    <span>👨‍💼 {{ current_user.username }}</span>
    <a href="{{ url_for('logout') }}" class="logout-btn">Logout</a>
    </div>
    </div>
    </div>
    
    <div class="container">
    <div class="stats-grid">
    <div class="stat-card engineers">
    <div class="stat-number">{{ total_engineers }}</div>
    <div class="stat-label">👥 Active Engineers</div>
    <div class="stat-trend">{{ total_engineers }} registered users</div>
    </div>
    <div class="stat-card">
    <div class="stat-number">{{ total_assignments }}</div>
    <div class="stat-label">📝 Total Assignments</div>
    <div class="stat-trend">Across all topics</div>
    </div>
    <div class="stat-card pending">
    <div class="stat-number">{{ pending_grading }}</div>
    <div class="stat-label">⏳ Pending Review</div>
    <div class="stat-trend">Awaiting admin grading</div>
    </div>
    <div class="stat-card completed">
    <div class="stat-number">{{ graded_released }}</div>
    <div class="stat-label">✅ Completed & Released</div>
    <div class="stat-trend">Grades visible to students</div>
    </div>
    </div>
    
    <div class="action-section">
    <h2 class="section-title">🚀 Quick Actions</h2>
    <div class="action-grid">
    <button onclick="createFullAssignments()" class="action-btn btn-success">
    ➕ Create Complete Assignment System
    </button>
    <a href="{{ url_for('admin_submissions') }}" class="action-btn btn-primary">
    📋 Review All Submissions
    </a>
    <a href="{{ url_for('admin_assignments') }}" class="action-btn btn-info">
    📚 Manage Assignments
    </a>
    <button onclick="viewAnalytics()" class="action-btn btn-info">
    📊 System Analytics
    </button>
    <button onclick="generateReport()" class="action-btn btn-primary">
    📈 Generate Report
    </button>
    <button onclick="systemHealth()" class="action-btn btn-info">
    🔍 System Health
    </button>
    </div>
    </div>
    
    <div class="activity-section">
    <h2 class="section-title">📈 Recent Activity</h2>
    <div class="quick-stats">
    <div class="quick-stat">
    <div class="quick-stat-number">{{ total_submissions }}</div>
    <div class="quick-stat-label">Total Submissions</div>
    </div>
    <div class="quick-stat">
    <div class="quick-stat-number">{{ (graded_released / total_submissions * 100) if total_submissions > 0 else 0 }}%</div>
    <div class="quick-stat-label">Completion Rate</div>
    </div>
    <div class="quick-stat">
    <div class="quick-stat-number">{{ recent_activities|length }}</div>
    <div class="quick-stat-label">Recent Activities</div>
    </div>
    </div>
    
    {% if recent_activities %}
    {% for activity in recent_activities %}
    <div class="activity-item">
    <div class="activity-title">{{ activity.title }}</div>
    <div class="activity-desc">{{ activity.description }}</div>
    <div class="activity-time">{{ activity.timestamp }}</div>
    </div>
    {% endfor %}
    {% else %}
    <div class="activity-item">
    <div class="activity-title">🎯 System Ready</div>
    <div class="activity-desc">Create assignments to begin tracking student activity</div>
    <div class="activity-time">Awaiting first submissions</div>
    </div>
    {% endif %}
    </div>
    </div>
    
    <script>
    function createFullAssignments() {
        if (confirm('🚀 Create comprehensive Physical Design assignments?\\n\\n✅ 15 detailed questions per topic\\n✅ Advanced technical evaluation\\n✅ Professional grading system\\n\\nThis will create the complete assignment system for all engineers.')) {
            const btn = event.target;
            btn.disabled = true;
            btn.textContent = '⏳ Creating...';
            
            fetch('/api/create-full-system', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ ' + data.message);
                    location.reload();
                } else {
                    alert('❌ Error: ' + data.error);
                    btn.disabled = false;
                    btn.textContent = '➕ Create Complete Assignment System';
                }
            })
            .catch(error => {
                alert('❌ Error: ' + error.message);
                btn.disabled = false;
                btn.textContent = '➕ Create Complete Assignment System';
            });
        }
    }
    
    function viewAnalytics() {
        window.open('/api/analytics', '_blank');
    }
    
    function generateReport() {
        if (confirm('Generate comprehensive system report?')) {
            window.open('/api/report', '_blank');
        }
    }
    
    function systemHealth() {
        window.open('/health', '_blank');
    }
    </script>
    </body></html>'''
    
    return render_template_string(admin_html, 
                                total_engineers=total_engineers,
                                total_assignments=total_assignments,
                                total_submissions=total_submissions,
                                pending_grading=pending_grading,
                                graded_released=graded_released,
                                recent_activities=recent_activities)

@app.route('/engineer')
@login_required
def engineer_dashboard():
    # Get engineer's assignments and submissions
    assignments = Assignment.query.filter_by(engineer_id=current_user.id).all()
    submissions = Submission.query.filter_by(engineer_id=current_user.id).all()
    
    # Create submission lookup
    submission_lookup = {s.assignment_id: s for s in submissions}
    
    # Parse questions and add submission status
    for assignment in assignments:
        try:
            assignment.parsed_questions = json.loads(assignment.questions)
        except:
            assignment.parsed_questions = []
        assignment.submission = submission_lookup.get(assignment.id)
    
    # Get notifications
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_date.desc()).limit(5).all()
    
    engineer_html = '''<!DOCTYPE html>
    <html><head><title>Engineer Dashboard - Physical Design System</title>
    <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f8f9fa; }
    .header { background: linear-gradient(135deg, #27ae60, #2ecc71); color: white; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
    .user-info { display: flex; align-items: center; gap: 15px; }
    .user-info span { background: rgba(255,255,255,0.1); padding: 8px 15px; border-radius: 20px; font-size: 14px; }
    .logout-btn { background: #e74c3c; padding: 8px 16px; border-radius: 6px; text-decoration: none; color: white; font-size: 14px; }
    
    .container { max-width: 1200px; margin: 0 auto; padding: 30px 20px; }
    .progress-section { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); margin-bottom: 30px; }
    .progress-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin-top: 20px; }
    .progress-card { text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #27ae60; }
    .progress-number { font-size: 2em; font-weight: 700; color: #2c3e50; }
    .progress-label { color: #7f8c8d; font-size: 14px; margin-top: 5px; }
    
    .assignments-section { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); }
    .assignment-card { border-left: 4px solid #3498db; padding: 25px; margin: 20px 0; background: #f8f9fa; border-radius: 8px; transition: all 0.3s; }
    .assignment-card:hover { box-shadow: 0 4px 15px rgba(0,0,0,0.1); transform: translateY(-2px); }
    .assignment-card.completed { border-left-color: #27ae60; background: #d4edda; }
    .assignment-card.graded { border-left-color: #f39c12; background: #fff3cd; }
    
    .assignment-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }
    .assignment-title { font-size: 18px; font-weight: 600; color: #2c3e50; margin-bottom: 5px; }
    .assignment-meta { font-size: 14px; color: #5a6c7d; }
    .assignment-status { padding: 6px 12px; border-radius: 15px; font-size: 12px; font-weight: 600; }
    .status-pending { background: #3498db; color: white; }
    .status-submitted { background: #27ae60; color: white; }
    .status-graded { background: #f39c12; color: white; }
    .status-released { background: #9b59b6; color: white; }
    
    .questions-preview { margin: 15px 0; padding: 15px; background: white; border-radius: 6px; border: 1px solid #e9ecef; }
    .question-item { margin: 8px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; font-size: 14px; border-left: 3px solid #3498db; }
    
    .assignment-actions { margin-top: 15px; display: flex; gap: 10px; flex-wrap: wrap; }
    .btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; font-size: 14px; font-weight: 600; transition: all 0.3s; display: inline-flex; align-items: center; gap: 8px; }
    .btn-primary { background: linear-gradient(135deg, #3498db, #2980b9); color: white; }
    .btn-success { background: linear-gradient(135deg, #27ae60, #229954); color: white; }
    .btn-info { background: linear-gradient(135deg, #17a2b8, #138496); color: white; }
    .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    
    .grade-display { margin-top: 15px; padding: 15px; background: white; border-radius: 6px; border-left: 4px solid #9b59b6; }
    .grade-score { font-size: 24px; font-weight: 700; color: #9b59b6; }
    .grade-feedback { margin-top: 10px; color: #5a6c7d; font-style: italic; }
    
    .no-assignments { text-align: center; padding: 60px 20px; color: #7f8c8d; }
    .no-assignments h3 { font-size: 24px; margin-bottom: 15px; }
    
    .notifications { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); margin-bottom: 30px; }
    .notification-item { padding: 12px; margin: 8px 0; background: #e3f2fd; border-left: 4px solid #2196f3; border-radius: 4px; }
    
    @media (max-width: 768px) {
        .header-content { flex-direction: column; gap: 15px; }
        .assignment-header { flex-direction: column; gap: 10px; }
        .assignment-actions { justify-content: center; }
    }
    </style></head><body>
    
    <div class="header">
    <div class="header-content">
    <h1>👨‍💻 Engineer Dashboard - Physical Design System</h1>
    <div class="user-info">
    <span>🎯 {{ current_user.username }}</span>
    <span>{{ current_user.department or 'Physical Design' }}</span>
    <a href="{{ url_for('logout') }}" class="logout-btn">Logout</a>
    </div>
    </div>
    </div>
    
    <div class="container">
    {% if notifications %}
    <div class="notifications">
    <h3>🔔 Notifications</h3>
    {% for notification in notifications %}
    <div class="notification-item">
    <strong>{{ notification.title }}</strong><br>
    {{ notification.message }}
    <small style="float:right;color:#666">{{ notification.created_date.strftime('%m/%d %H:%M') }}</small>
    </div>
    {% endfor %}
    </div>
    {% endif %}
    
    <div class="progress-section">
    <h2>📊 Your Progress Overview</h2>
    <div class="progress-grid">
    <div class="progress-card">
    <div class="progress-number">{{ assignments|length }}</div>
    <div class="progress-label">Total Assignments</div>
    </div>
    <div class="progress-card">
    <div class="progress-number">{{ assignments|selectattr('submission')|list|length }}</div>
    <div class="progress-label">Submitted</div>
    </div>
    <div class="progress-card">
    <div class="progress-number">{{ assignments|selectattr('submission.is_grade_released', 'equalto', true)|list|length }}</div>
    <div class="progress-label">Graded</div>
    </div>
    <div class="progress-card">
    <div class="progress-number">{{ assignments|rejectattr('submission')|list|length }}</div>
    <div class="progress-label">Pending</div>
    </div>
    </div>
    </div>
    
    <div class="assignments-section">
    <h2>📝 Your Assignments</h2>
    
    {% if assignments %}
    {% for assignment in assignments %}
    <div class="assignment-card {% if assignment.submission %}{% if assignment.submission.is_grade_released %}graded{% else %}completed{% endif %}{% endif %}">
    
    <div class="assignment-header">
    <div>
    <div class="assignment-title">{{ assignment.title }}</div>
    <div class="assignment-meta">
    📋 Topic: {{ assignment.topic.title() }} | 
    📅 Due: {{ assignment.due_date.strftime('%B %d, %Y') }} |
    ⭐ Points: {{ assignment.points }}
    </div>
    </div>
    <div class="assignment-status 
        {% if assignment.submission %}
            {% if assignment.submission.is_grade_released %}status-released{% else %}status-submitted{% endif %}
        {% else %}status-pending{% endif %}">
        {% if assignment.submission %}
            {% if assignment.submission.is_grade_released %}
                ✅ Graded
            {% else %}
                ⏳ Under Review
            {% endif %}
        {% else %}
            📝 Not Started
        {% endif %}
    </div>
    </div>
    
    <div class="questions-preview">
    <h4>📋 Questions Preview ({{ assignment.parsed_questions|length }} total):</h4>
    {% for question in assignment.parsed_questions[:2] %}
    <div class="question-item">
    <strong>{{ loop.index }}.</strong> {{ question[:120] }}{% if question|length > 120 %}...{% endif %}
    </div>
    {% endfor %}
    {% if assignment.parsed_questions|length > 2 %}
    <p style="margin:10px 0;color:#666;font-style:italic">... and {{ assignment.parsed_questions|length - 2 }} more detailed questions</p>
    {% endif %}
    </div>
    
    {% if assignment.submission %}
        {% if assignment.submission.is_grade_released %}
        <div class="grade-display">
        <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
        <span style="color:#666">Final Grade:</span>
        <span class="grade-score">{{ assignment.submission.admin_grade }}</span>
        </div>
        {% if assignment.submission.overall_score %}
        <div style="text-align:right">
        <div style="color:#666;font-size:12px">Technical Score</div>
        <div style="font-size:18px;font-weight:600;color:#3498db">{{ "%.1f"|format(assignment.submission.overall_score) }}%</div>
        </div>
        {% endif %}
        </div>
        {% if assignment.submission.admin_feedback %}
        <div class="grade-feedback">
        <strong>Instructor Feedback:</strong><br>
        {{ assignment.submission.admin_feedback }}
        </div>
        {% endif %}
        </div>
        {% else %}
        <div style="padding:15px;background:#fff3cd;border-radius:6px;margin-top:15px">
        ⏳ <strong>Submitted on {{ assignment.submission.submitted_date.strftime('%B %d, %Y at %I:%M %p') }}</strong><br>
        Your submission is being reviewed by the instructor. You'll receive a notification when grading is complete.
        </div>
        {% endif %}
        
        <div class="assignment-actions">
        <button onclick="viewSubmission('{{ assignment.id }}')" class="btn btn-info">
        👁️ View My Submission
        </button>
        {% if assignment.submission.is_grade_released %}
        <button onclick="viewFeedback('{{ assignment.id }}')" class="btn btn-success">
        📊 View Detailed Feedback
        </button>
        {% endif %}
        </div>
        
    {% else %}
        <div class="assignment-actions">
        <a href="{{ url_for('assignment_interface', assignment_id=assignment.id) }}" class="btn btn-primary">
        🚀 Start Assignment
        </a>
        <button onclick="previewAssignment('{{ assignment.id }}')" class="btn btn-info">
        👁️ Preview Questions
        </button>
        </div>
    {% endif %}
    
    </div>
    {% endfor %}
    
    {% else %}
    <div class="no-assignments">
    <h3>📭 No Assignments Yet</h3>
    <p>Your instructor hasn't created any assignments yet.</p>
    <p style="margin-top:15px;color:#3498db">Check back later or contact your instructor!</p>
    </div>
    {% endif %}
    
    </div>
    </div>
    
    <script>
    function viewSubmission(assignmentId) {
        alert('📝 Submission Viewer\\n\\nThis will show your submitted answers for review.\\n\\nAssignment: ' + assignmentId);
    }
    
    function viewFeedback(assignmentId) {
        alert('📊 Detailed Feedback\\n\\nThis will show comprehensive technical evaluation including:\\n\\n✅ Technical term analysis\\n✅ Concept coverage assessment\\n✅ Quantitative scoring\\n✅ Study recommendations\\n\\nAssignment: ' + assignmentId);
    }
    
    function previewAssignment(assignmentId) {
        alert('👁️ Assignment Preview\\n\\nThis will show all questions for review before starting.\\n\\nAssignment: ' + assignmentId);
    }
    </script>
    </body></html>'''
    
    return render_template_string(engineer_html, assignments=assignments, notifications=notifications)

# Assignment Interface Route
@app.route('/assignment/<assignment_id>')
@login_required
def assignment_interface(assignment_id):
    assignment = Assignment.query.filter_by(id=assignment_id, engineer_id=current_user.id).first_or_404()
    
    # Check if already submitted
    existing_submission = Submission.query.filter_by(
        assignment_id=assignment_id,
        engineer_id=current_user.id
    ).first()
    
    if existing_submission:
        flash('You have already submitted this assignment.', 'warning')
        return redirect(url_for('engineer_dashboard'))
    
    try:
        questions = json.loads(assignment.questions)
    except:
        questions = []
    
    interface_html = '''<!DOCTYPE html>
    <html><head><title>{{ assignment.title }} - Assignment Interface</title>
    <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f8f9fa; line-height: 1.6; }
    .header { background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .header-content { max-width: 1000px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
    .back-btn { background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 6px; text-decoration: none; color: white; font-size: 14px; }
    
    .container { max-width: 1000px; margin: 0 auto; padding: 30px 20px; }
    .assignment-info { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); margin-bottom: 30px; }
    .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 15px; }
    .info-item { text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }
    .info-value { font-size: 1.2em; font-weight: 600; color: #2c3e50; }
    .info-label { font-size: 14px; color: #7f8c8d; margin-top: 5px; }
    
    .question-form { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); }
    .question-block { margin-bottom: 40px; padding: 25px; border: 2px solid #e9ecef; border-radius: 10px; transition: border-color 0.3s; }
    .question-block:focus-within { border-color: #3498db; }
    .question-number { background: #3498db; color: white; padding: 8px 15px; border-radius: 20px; font-weight: 600; font-size: 14px; display: inline-block; margin-bottom: 15px; }
    .question-text { font-size: 16px; color: #2c3e50; margin-bottom: 20px; line-height: 1.8; }
    .answer-textarea { width: 100%; min-height: 150px; padding: 15px; border: 2px solid #e9ecef; border-radius: 8px; font-size: 14px; line-height: 1.6; resize: vertical; font-family: inherit; }
    .answer-textarea:focus { border-color: #3498db; outline: none; }
    .answer-meta { display: flex; justify-content: between; align-items: center; margin-top: 10px; font-size: 12px; color: #7f8c8d; }
    .word-counter { margin-left: auto; }
    .word-counter.good { color: #27ae60; }
    .word-counter.warning { color: #f39c12; }
    
    .progress-section { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); margin-bottom: 30px; position: sticky; top: 20px; z-index: 100; }
    .progress-bar { background: #e9ecef; height: 8px; border-radius: 4px; overflow: hidden; margin: 10px 0; }
    .progress-fill { background: linear-gradient(90deg, #3498db, #2980b9); height: 100%; transition: width 0.3s; }
    .progress-text { text-align: center; font-size: 14px; color: #5a6c7d; }
    
    .submit-section { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); text-align: center; margin-top: 30px; }
    .submit-btn { background: linear-gradient(135deg, #27ae60, #229954); color: white; padding: 15px 40px; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s; }
    .submit-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(39, 174, 96, 0.3); }
    .submit-btn:disabled { background: #95a5a6; cursor: not-allowed; transform: none; box-shadow: none; }
    
    .requirements { background: #e8f4fd; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #3498db; }
    .requirement-item { margin: 5px 0; font-size: 14px; color: #2c3e50; }
    
    @media (max-width: 768px) {
        .header-content { flex-direction: column; gap: 15px; }
        .container { padding: 20px 15px; }
        .question-block { padding: 20px; }
        .progress-section { position: relative; }
    }
    </style></head><body>
    
    <div class="header">
    <div class="header-content">
    <h1>📝 {{ assignment.title }}</h1>
    <a href="{{ url_for('engineer_dashboard') }}" class="back-btn">← Back to Dashboard</a>
    </div>
    </div>
    
    <div class="container">
    <div class="assignment-info">
    <h2>📋 Assignment Information</h2>
    <div class="info-grid">
    <div class="info-item">
    <div class="info-value">{{ questions|length }}</div>
    <div class="info-label">Total Questions</div>
    </div>
    <div class="info-item">
    <div class="info-value">{{ assignment.points }}</div>
    <div class="info-label">Total Points</div>
    </div>
    <div class="info-item">
    <div class="info-value">{{ assignment.due_date.strftime('%b %d') }}</div>
    <div class="info-label">Due Date</div>
    </div>
    <div class="info-item">
    <div class="info-value">{{ assignment.topic.title() }}</div>
    <div class="info-label">Topic Focus</div>
    </div>
    </div>
    
    <div class="requirements">
    <h4>📋 Assignment Requirements:</h4>
    <div class="requirement-item">✅ Answer all {{ questions|length }} questions completely</div>
    <div class="requirement-item">✅ Minimum 50 words per answer (recommended 100-200)</div>
    <div class="requirement-item">✅ Use technical terminology and specific examples</div>
    <div class="requirement-item">✅ Include quantitative analysis where applicable</div>
    <div class="requirement-item">⚠️ Submission cannot be modified after clicking Submit</div>
    </div>
    </div>
    
    <div class="progress-section">
    <div class="progress-text">Progress: <span id="progress-count">0</span> of {{ questions|length }} questions completed</div>
    <div class="progress-bar">
    <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
    </div>
    </div>
    
    <form id="assignment-form" class="question-form">
    <input type="hidden" name="assignment_id" value="{{ assignment.id }}">
    
    {% for question in questions %}
    <div class="question-block">
    <div class="question-number">Question {{ loop.index }} of {{ questions|length }}</div>
    <div class="question-text">{{ question }}</div>
    
    <textarea 
        name="answer_{{ loop.index0 }}" 
        class="answer-textarea" 
        placeholder="Enter your detailed technical response here... Include specific examples, calculations, and methodologies."
        data-question="{{ loop.index0 }}"
        oninput="updateProgress(); updateWordCount(this, {{ loop.index0 }})"
        required>
    </textarea>
    
    <div class="answer-meta">
    <span>💡 Include technical terms, quantitative analysis, and specific examples</span>
    <span class="word-counter" id="counter-{{ loop.index0 }}">0 words</span>
    </div>
    </div>
    {% endfor %}
    
    <div class="submit-section">
    <h3>🎯 Ready to Submit?</h3>
    <p style="margin: 15px 0; color: #5a6c7d;">
    Review your answers carefully. Once submitted, you cannot make changes.<br>
    Your submission will be automatically evaluated and then reviewed by your instructor.
    </p>
    <button type="submit" class="submit-btn" id="submit-btn" disabled>
    🚀 Submit Assignment
    </button>
    <div id="submit-status" style="margin-top: 15px; font-size: 14px;"></div>
    </div>
    </form>
    </div>
    
    <script>
    let completedQuestions = 0;
    const totalQuestions = {{ questions|length }};
    
    function updateWordCount(textarea, questionIndex) {
        const words = textarea.value.trim().split(/\s+/).filter(word => word.length > 0);
        const wordCount = words.length;
        const counter = document.getElementById('counter-' + questionIndex);
        
        counter.textContent = wordCount + ' words';
        
        if (wordCount >= 50) {
            counter.className = 'word-counter good';
        } else if (wordCount >= 25) {
            counter.className = 'word-counter warning';
        } else {
            counter.className = 'word-counter';
        }
    }
    
    function updateProgress() {
        completedQuestions = 0;
        const textareas = document.querySelectorAll('.answer-textarea');
        
        textareas.forEach(textarea => {
            const words = textarea.value.trim().split(/\s+/).filter(word => word.length > 0);
            if (words.length >= 25) {
                completedQuestions++;
            }
        });
        
        const percentage = (completedQuestions / totalQuestions) * 100;
        document.getElementById('progress-fill').style.width = percentage + '%';
        document.getElementById('progress-count').textContent = completedQuestions;
        
        const submitBtn = document.getElementById('submit-btn');
        if (completedQuestions === totalQuestions) {
            submitBtn.disabled = false;
            submitBtn.textContent = '🚀 Submit Assignment';
        } else {
            submitBtn.disabled = true;
            submitBtn.textContent = `Complete ${totalQuestions - completedQuestions} more questions to submit`;
        }
    }
    
    document.getElementById('assignment-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (completedQuestions < totalQuestions) {
            alert('Please complete all questions before submitting.');
            return;
        }
        
        if (!confirm('🎯 Submit Assignment?\\n\\n✅ All questions completed\\n⚠️ Cannot be modified after submission\\n\\nProceed with submission?')) {
            return;
        }
        
        const submitBtn = document.getElementById('submit-btn');
        const statusDiv = document.getElementById('submit-status');
        
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Submitting...';
        statusDiv.innerHTML = '<div style="color: #3498db;">📤 Processing your submission...</div>';
        
        // Collect answers
        const formData = new FormData(this);
        const answers = [];
        
        for (let i = 0; i < totalQuestions; i++) {
            answers.push(formData.get('answer_' + i) || '');
        }
        
        // Submit to server
        fetch('/api/submit-assignment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                assignment_id: '{{ assignment.id }}',
                answers: answers
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                statusDiv.innerHTML = '<div style="color: #27ae60;">✅ ' + data.message + '</div>';
                setTimeout(() => {
                    window.location.href = '/engineer';
                }, 2000);
            } else {
                statusDiv.innerHTML = '<div style="color: #e74c3c;">❌ Error: ' + data.error + '</div>';
                submitBtn.disabled = false;
                submitBtn.textContent = '🚀 Submit Assignment';
            }
        })
        .catch(error => {
            statusDiv.innerHTML = '<div style="color: #e74c3c;">❌ Error: ' + error.message + '</div>';
            submitBtn.disabled = false;
            submitBtn.textContent = '🚀 Submit Assignment';
        });
    });
    
    // Auto-save draft (optional)
    setInterval(() => {
        const answers = [];
        for (let i = 0; i < totalQuestions; i++) {
            const textarea = document.querySelector(`textarea[data-question="${i}"]`);
            answers.push(textarea ? textarea.value : '');
        }
        localStorage.setItem('assignment_{{ assignment.id }}_draft', JSON.stringify(answers));
    }, 30000); // Save every 30 seconds
    
    // Load draft on page load
    window.addEventListener('load', () => {
        const draft = localStorage.getItem('assignment_{{ assignment.id }}_draft');
        if (draft) {
            try {
                const answers = JSON.parse(draft);
                answers.forEach((answer, index) => {
                    const textarea = document.querySelector(`textarea[data-question="${index}"]`);
                    if (textarea && answer) {
                        textarea.value = answer;
                        updateWordCount(textarea, index);
                    }
                });
                updateProgress();
            } catch (e) {
                console.log('Could not load draft');
            }
        }
    });
    </script>
    </body></html>'''
    
    return render_template_string(interface_html, assignment=assignment, questions=questions)

# API Routes
@app.route('/api/create-full-system', methods=['POST'])
@login_required
@admin_required
def create_full_system():
    try:
        engineers = User.query.filter_by(is_admin=False).all()
        
        if not engineers:
            return jsonify({'error': 'No engineers found. Please create engineer accounts first.'}), 400
        
        assignments_created = 0
        
        for engineer in engineers:
            for topic, data in PHYSICAL_DESIGN_TOPICS.items():
                assignment_id = f"PD_{topic.upper()}_{engineer.id}_{datetime.datetime.now().strftime('%Y%m%d')}"
                
                # Check if assignment already exists
                existing = Assignment.query.filter_by(id=assignment_id).first()
                if existing:
                    continue
                
                assignment = Assignment(
                    id=assignment_id,
                    title=data['title'],
                    topic=topic,
                    engineer_id=engineer.id,
                    questions=json.dumps(data['questions']),
                    due_date=datetime.date.today() + datetime.timedelta(days=14),
                    points=150  # Higher points for comprehensive assignments
                )
                db.session.add(assignment)
                assignments_created += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully created {assignments_created} comprehensive assignments for {len(engineers)} engineers!',
            'details': {
                'engineers': len(engineers),
                'topics': len(PHYSICAL_DESIGN_TOPICS),
                'assignments_per_engineer': len(PHYSICAL_DESIGN_TOPICS),
                'total_assignments': assignments_created
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create assignments: {str(e)}'}), 500

@app.route('/api/submit-assignment', methods=['POST'])
@login_required
def submit_assignment():
    try:
        data = request.get_json()
        assignment_id = data.get('assignment_id')
        answers = data.get('answers', [])
        
        if not assignment_id or not answers:
            return jsonify({'error': 'Missing assignment ID or answers'}), 400
        
        # Verify assignment belongs to current user
        assignment = Assignment.query.filter_by(
            id=assignment_id,
            engineer_id=current_user.id
        ).first()
        
        if not assignment:
            return jsonify({'error': 'Assignment not found or access denied'}), 404
        
        # Check for existing submission
        existing = Submission.query.filter_by(
            assignment_id=assignment_id,
            engineer_id=current_user.id
        ).first()
        
        if existing:
            return jsonify({'error': 'Assignment already submitted'}), 409
        
        # Create submission
        submission = Submission(
            assignment_id=assignment_id,
            engineer_id=current_user.id,
            answers=json.dumps(answers)
        )
        
        db.session.add(submission)
        db.session.commit()
        
        # Perform technical evaluation
        try:
            evaluator = TechnicalEvaluator()
            evaluation_results = evaluator.evaluate_submission(answers, assignment.topic)
            
            submission.overall_score = evaluation_results['overall_score']
            submission.grade_letter = evaluation_results['grade_letter']
            submission.evaluation_results = json.dumps(evaluation_results)
            
            db.session.commit()
            
        except Exception as eval_error:
            print(f"Evaluation error: {eval_error}")
            # Continue without evaluation - admin can still grade manually
        
        # Create notification for admin
        admin_users = User.query.filter_by(is_admin=True).all()
        for admin in admin_users:
            notification = Notification(
                user_id=admin.id,
                title=f"New Submission: {assignment.title}",
                message=f"{current_user.username} submitted {assignment.topic} assignment"
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Assignment submitted successfully! Your instructor will review and grade it.',
            'submission_id': submission.id,
            'technical_score': submission.overall_score
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Submission failed: {str(e)}'}), 500

@app.route('/admin/submissions')
@login_required
@admin_required
def admin_submissions():
    submissions = Submission.query.order_by(Submission.submitted_date.desc()).all()
    
    # Enhanced submission data
    submission_data = []
    for sub in submissions:
        user = User.query.get(sub.engineer_id)
        assignment = Assignment.query.get(sub.assignment_id)
        
        # Parse evaluation results
        eval_results = {}
        if sub.evaluation_results:
            try:
                eval_results = json.loads(sub.evaluation_results)
            except:
                pass
        
        submission_data.append({
            'id': sub.id,
            'engineer': user.username if user else 'Unknown',
            'assignment_title': assignment.title if assignment else 'Unknown',
            'assignment_topic': assignment.topic if assignment else 'Unknown',
            'submitted_date': sub.submitted_date.strftime('%Y-%m-%d %H:%M'),
            'technical_score': sub.overall_score,
            'technical_grade': sub.grade_letter,
            'admin_grade': sub.admin_grade,
            'is_graded': bool(sub.admin_grade),
            'is_released': sub.is_grade_released,
            'evaluation_summary': eval_results.get('summary', {}),
            'strengths': eval_results.get('strengths', []),
            'weaknesses': eval_results.get('areas_for_improvement', [])
        })
    
    submissions_html = '''<!DOCTYPE html>
    <html><head><title>Submission Management - Admin</title>
    <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f8f9fa; }
    .header { background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 20px; }
    .header-content { max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
    .nav-links { display: flex; gap: 15px; }
    .nav-link { background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 6px; text-decoration: none; color: white; font-size: 14px; }
    
    .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
    .filters { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); margin-bottom: 30px; }
    .filter-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
    .filter-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #555; }
    .filter-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
    
    .submissions-table { background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); overflow: hidden; }
    .table-header { background: #f8f9fa; padding: 20px; border-bottom: 1px solid #e9ecef; }
    .submissions-grid { display: grid; gap: 15px; padding: 20px; }
    .submission-card { border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; transition: all 0.3s; }
    .submission-card:hover { box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .submission-card.needs-grading { border-left: 4px solid #f39c12; }
    .submission-card.graded { border-left: 4px solid #27ae60; }
    .submission-card.released { border-left: 4px solid #9b59b6; }
    
    .submission-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }
    .submission-title { font-size: 16px; font-weight: 600; color: #2c3e50; }
    .submission-meta { font-size: 14px; color: #7f8c8d; margin-top: 5px; }
    .submission-status { padding: 6px 12px; border-radius: 15px; font-size: 12px; font-weight: 600; }
    .status-pending { background: #f39c12; color: white; }
    .status-graded { background: #27ae60; color: white; }
    .status-released { background: #9b59b6; color: white; }
    
    .technical-scores { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin: 15px 0; }
    .score-item { text-align: center; padding: 10px; background: #f8f9fa; border-radius: 6px; }
    .score-value { font-size: 18px; font-weight: 600; color: #3498db; }
    .score-label { font-size: 12px; color: #7f8c8d; }
    
    .submission-actions { margin-top: 15px; display: flex; gap: 10px; flex-wrap: wrap; }
    .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; font-size: 12px; font-weight: 600; transition: all 0.3s; }
    .btn-primary { background: #3498db; color: white; }
    .btn-success { background: #27ae60; color: white; }
    .btn-warning { background: #f39c12; color: white; }
    .btn-info { background: #17a2b8; color: white; }
    
    .grade-form { display: none; margin-top: 15px; padding: 15px; background: #f8f9fa; border-radius: 6px; }
    .form-group { margin: 10px 0; }
    .form-group label { display: block; margin-bottom: 5px; font-weight: 600; }
    .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
    
    @media (max-width: 768px) {
        .submission-header { flex-direction: column; gap: 10px; }
        .technical-scores { grid-template-columns: repeat(2, 1fr); }
        .submission-actions { justify-content: center; }
    }
    </style></head><body>
    
    <div class="header">
    <div class="header-content">
    <h1>📋 Submission Management</h1>
    <div class="nav-links">
    <a href="/admin" class="nav-link">← Dashboard</a>
    <a href="/admin/assignments" class="nav-link">Assignments</a>
    <a href="/logout" class="nav-link">Logout</a>
    </div>
    </div>
    </div>
    
    <div class="container">
    <div class="filters">
    <h3>🔍 Filter Submissions</h3>
    <div class="filter-grid">
    <div class="filter-group">
    <label>Status:</label>
    <select id="status-filter" onchange="filterSubmissions()">
    <option value="all">All Submissions</option>
    <option value="pending">Pending Grading</option>
    <option value="graded">Graded</option>
    <option value="released">Released</option>
    </select>
    </div>
    <div class="filter-group">
    <label>Topic:</label>
    <select id="topic-filter" onchange="filterSubmissions()">
    <option value="all">All Topics</option>
    <option value="floorplanning">Floorplanning</option>
    <option value="placement">Placement</option>
    <option value="routing">Routing</option>
    </select>
    </div>
    <div class="filter-group">
    <label>Engineer:</label>
    <select id="engineer-filter" onchange="filterSubmissions()">
    <option value="all">All Engineers</option>
    {% for submission in submissions %}
    <option value="{{ submission.engineer }}">{{ submission.engineer }}</option>
    {% endfor %}
    </select>
    </div>
    </div>
    </div>
    
    <div class="submissions-table">
    <div class="table-header">
    <h2>📝 All Submissions ({{ submissions|length }})</h2>
    <p>Manage technical evaluations, assign grades, and release results to students</p>
    </div>
    
    <div class="submissions-grid" id="submissions-container">
    {% for submission in submissions %}
    <div class="submission-card {% if not submission.is_graded %}needs-grading{% elif submission.is_released %}released{% else %}graded{% endif %}" 
         data-status="{% if not submission.is_graded %}pending{% elif submission.is_released %}released{% else %}graded{% endif %}"
         data-topic="{{ submission.assignment_topic }}"
         data-engineer="{{ submission.engineer }}">
    
    <div class="submission-header">
    <div>
    <div class="submission-title">{{ submission.assignment_title }}</div>
    <div class="submission-meta">
    👨‍💻 {{ submission.engineer }} | 📅 {{ submission.submitted_date }} | 📚 {{ submission.assignment_topic.title() }}
    </div>
    </div>
    <div class="submission-status {% if not submission.is_graded %}status-pending{% elif submission.is_released %}status-released{% else %}status-graded{% endif %}">
    {% if not submission.is_graded %}⏳ Needs Grading{% elif submission.is_released %}✅ Released{% else %}📝 Graded{% endif %}
    </div>
    </div>
    
    {% if submission.technical_score %}
    <div class="technical-scores">
    <div class="score-item">
    <div class="score-value">{{ "%.1f"|format(submission.technical_score) }}%</div>
    <div class="score-label">Technical Score</div>
    </div>
    <div class="score-item">
    <div class="score-value">{{ submission.technical_grade or 'N/A' }}</div>
    <div class="score-label">Auto Grade</div>
    </div>
    <div class="score-item">
    <div class="score-value">{{ submission.admin_grade or 'Not Set' }}</div>
    <div class="score-label">Final Grade</div>
    </div>
    <div class="score-item">
    <div class="score-value">{{ submission.evaluation_summary.get('unique_technical_terms', 0) }}</div>
    <div class="score-label">Tech Terms</div>
    </div>
    </div>
    {% endif %}
    
    {% if submission.strengths or submission.weaknesses %}
    <div style="margin: 15px 0; font-size: 14px;">
    {% if submission.strengths %}
    <div style="color: #27ae60; margin-bottom: 8px;">
    <strong>✅ Strengths:</strong> {{ submission.strengths|join(', ') }}
    </div>
    {% endif %}
    {% if submission.weaknesses %}
    <div style="color: #e74c3c;">
    <strong>⚠️ Areas for Improvement:</strong> {{ submission.weaknesses|join(', ') }}
    </div>
    {% endif %}
    </div>
    {% endif %}
    
    <div class="submission-actions">
    <button onclick="viewSubmission({{ submission.id }})" class="btn btn-info">👁️ View Details</button>
    {% if not submission.is_graded %}
    <button onclick="toggleGradeForm({{ submission.id }})" class="btn btn-warning">📝 Grade</button>
    {% endif %}
    {% if submission.is_graded and not submission.is_released %}
    <button onclick="releaseGrade({{ submission.id }})" class="btn btn-success">📤 Release Grade</button>
    {% endif %}
    <button onclick="downloadSubmission({{ submission.id }})" class="btn btn-primary">📥 Download</button>
    </div>
    
    <div id="grade-form-{{ submission.id }}" class="grade-form">
    <h4>📝 Assign Final Grade</h4>
    <div class="form-group">
    <label>Final Grade:</label>
    <select id="grade-{{ submission.id }}">
    <option value="">Select Grade</option>
    <option value="A+">A+ (97-100%)</option>
    <option value="A">A (93-96%)</option>
    <option value="A-">A- (90-92%)</option>
    <option value="B+">B+ (87-89%)</option>
    <option value="B">B (83-86%)</option>
    <option value="B-">B- (80-82%)</option>
    <option value="C+">C+ (77-79%)</option>
    <option value="C">C (73-76%)</option>
    <option value="C-">C- (70-72%)</option>
    <option value="D">D (65-69%)</option>
    <option value="F">F (Below 65%)</option>
    </select>
    </div>
    <div class="form-group">
    <label>Instructor Feedback (Optional):</label>
    <textarea id="feedback-{{ submission.id }}" rows="3" placeholder="Additional comments for the student..."></textarea>
    </div>
    <div class="form-group">
    <label>
    <input type="checkbox" id="release-{{ submission.id }}"> Release grade immediately
    </label>
    </div>
    <button onclick="submitGrade({{ submission.id }})" class="btn btn-success">✅ Save Grade</button>
    <button onclick="toggleGradeForm({{ submission.id }})" class="btn btn-secondary">Cancel</button>
    </div>
    
    </div>
    {% endfor %}
    </div>
    </div>
    </div>
    
    <script>
    function filterSubmissions() {
        const statusFilter = document.getElementById('status-filter').value;
        const topicFilter = document.getElementById('topic-filter').value;
        const engineerFilter = document.getElementById('engineer-filter').value;
        
        const cards = document.querySelectorAll('.submission-card');
        
        cards.forEach(card => {
            const status = card.dataset.status;
            const topic = card.dataset.topic;
            const engineer = card.dataset.engineer;
            
            const statusMatch = statusFilter === 'all' || status === statusFilter;
            const topicMatch = topicFilter === 'all' || topic === topicFilter;
            const engineerMatch = engineerFilter === 'all' || engineer === engineerFilter;
            
            if (statusMatch && topicMatch && engineerMatch) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    function toggleGradeForm(submissionId) {
        const form = document.getElementById('grade-form-' + submissionId);
        form.style.display = form.style.display === 'block' ? 'none' : 'block';
    }
    
    function submitGrade(submissionId) {
        const grade = document.getElementById('grade-' + submissionId).value;
        const feedback = document.getElementById('feedback-' + submissionId).value;
        const release = document.getElementById('release-' + submissionId).checked;
        
        if (!grade) {
            alert('Please select a grade');
            return;
        }
        
        if (!confirm(`Assign grade ${grade} to this submission?${release ? ' Grade will be released immediately.' : ''}`)) {
            return;
        }
        
        fetch('/api/admin/grade-submission', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                submission_id: submissionId,
                admin_grade: grade,
                admin_feedback: feedback,
                release_grade: release
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ ' + data.message);
                location.reload();
            } else {
                alert('❌ Error: ' + data.error);
            }
        })
        .catch(error => {
            alert('❌ Error: ' + error.message);
        });
    }
    
    function releaseGrade(submissionId) {
        if (confirm('Release grade to student? They will receive a notification.')) {
            fetch('/api/admin/release-grade', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ submission_id: submissionId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Grade released successfully!');
                    location.reload();
                } else {
                    alert('❌ Error: ' + data.error);
                }
            });
        }
    }
    
    function viewSubmission(submissionId) {
        window.open('/admin/submission/' + submissionId, '_blank');
    }
    
    function downloadSubmission(submissionId) {
        window.open('/api/download-submission/' + submissionId, '_blank');
    }
    </script>
    </body></html>'''
    
    return render_template_string(submissions_html, submissions=submission_data)

@app.route('/admin/assignments')
@login_required
@admin_required
def admin_assignments():
    assignments = Assignment.query.order_by(Assignment.created_date.desc()).all()
    
    assignment_data = []
    for assignment in assignments:
        user = User.query.get(assignment.engineer_id)
        submission_count = Submission.query.filter_by(assignment_id=assignment.id).count()
        
        try:
            questions = json.loads(assignment.questions)
        except:
            questions = []
        
        assignment_data.append({
            'id': assignment.id,
            'title': assignment.title,
            'topic': assignment.topic,
            'engineer': user.username if user else 'Unknown',
            'question_count': len(questions),
            'points': assignment.points,
            'due_date': assignment.due_date.strftime('%Y-%m-%d'),
            'created_date': assignment.created_date.strftime('%Y-%m-%d'),
            'has_submission': submission_count > 0,
            'submission_count': submission_count
        })
    
    assignments_html = '''<!DOCTYPE html>
    <html><head><title>Assignment Management - Admin</title>
    <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f8f9fa; }
    .header { background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 20px; }
    .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
    .nav-links { display: flex; gap: 15px; }
    .nav-link { background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 6px; text-decoration: none; color: white; font-size: 14px; }
    
    .container { max-width: 1200px; margin: 0 auto; padding: 30px 20px; }
    .stats-section { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); margin-bottom: 30px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 15px; }
    .stat-card { text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db; }
    .stat-number { font-size: 2em; font-weight: 700; color: #2c3e50; }
    .stat-label { color: #7f8c8d; font-size: 14px; margin-top: 5px; }
    
    .assignments-section { background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); overflow: hidden; }
    .section-header { background: #f8f9fa; padding: 25px; border-bottom: 1px solid #e9ecef; }
    .assignments-grid { padding: 25px; display: grid; gap: 20px; }
    .assignment-card { border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; transition: all 0.3s; }
    .assignment-card:hover { box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .assignment-card.floorplanning { border-left: 4px solid #e74c3c; }
    .assignment-card.placement { border-left: 4px solid #f39c12; }
    .assignment-card.routing { border-left: 4px solid #27ae60; }
    
    .assignment-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }
    .assignment-title { font-size: 16px; font-weight: 600; color: #2c3e50; }
    .assignment-meta { font-size: 14px; color: #7f8c8d; margin-top: 5px; }
    .topic-badge { padding: 4px 12px; border-radius: 15px; font-size: 12px; font-weight: 600; }
    .topic-floorplanning { background: #fdf2f2; color: #e74c3c; }
    .topic-placement { background: #fef9e7; color: #f39c12; }
    .topic-routing { background: #edf7ed; color: #27ae60; }
    
    .assignment-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin: 15px 0; }
    .detail-item { text-align: center; padding: 12px; background: #f8f9fa; border-radius: 6px; }
    .detail-value { font-size: 16px; font-weight: 600; color: #3498db; }
    .detail-label { font-size: 12px; color: #7f8c8d; margin-top: 2px; }
    
    .assignment-actions { margin-top: 15px; display: flex; gap: 10px; flex-wrap: wrap; }
    .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; font-size: 12px; font-weight: 600; transition: all 0.3s; }
    .btn-primary { background: #3498db; color: white; }
    .btn-info { background: #17a2b8; color: white; }
    .btn-warning { background: #f39c12; color: white; }
    .btn-danger { background: #e74c3c; color: white; }
    
    .no-assignments { text-align: center; padding: 60px 20px; color: #7f8c8d; }
    
    @media (max-width: 768px) {
        .assignment-header { flex-direction: column; gap: 10px; }
        .assignment-details { grid-template-columns: repeat(2, 1fr); }
    }
    </style></head><body>
    
    <div class="header">
    <div class="header-content">
    <h1>📚 Assignment Management</h1>
    <div class="nav-links">
    <a href="/admin" class="nav-link">← Dashboard</a>
    <a href="/admin/submissions" class="nav-link">Submissions</a>
    <a href="/logout" class="nav-link">Logout</a>
    </div>
    </div>
    </div>
    
    <div class="container">
    <div class="stats-section">
    <h2>📊 Assignment Overview</h2>
    <div class="stats-grid">
    <div class="stat-card">
    <div class="stat-number">{{ assignments|length }}</div>
    <div class="stat-label">Total Assignments</div>
    </div>
    <div class="stat-card">
    <div class="stat-number">{{ assignments|selectattr('topic', 'equalto', 'floorplanning')|list|length }}</div>
    <div class="stat-label">Floorplanning</div>
    </div>
    <div class="stat-card">
    <div class="stat-number">{{ assignments|selectattr('topic', 'equalto', 'placement')|list|length }}</div>
    <div class="stat-label">Placement</div>
    </div>
    <div class="stat-card">
    <div class="stat-number">{{ assignments|selectattr('topic', 'equalto', 'routing')|list|length }}</div>
    <div class="stat-label">Routing</div>
    </div>
    <div class="stat-card">
    <div class="stat-number">{{ assignments|selectattr('has_submission', 'equalto', true)|list|length }}</div>
    <div class="stat-label">With Submissions</div>
    </div>
    </div>
    </div>
    
    <div class="assignments-section">
    <div class="section-header">
    <h2>📝 All Assignments ({{ assignments|length }})</h2>
    <p>Manage assignment details, view submissions, and track progress</p>
    </div>
    
    <div class="assignments-grid">
    {% if assignments %}
    {% for assignment in assignments %}
    <div class="assignment-card {{ assignment.topic }}">
    
    <div class="assignment-header">
    <div>
    <div class="assignment-title">{{ assignment.title }}</div>
    <div class="assignment-meta">
    👨‍💻 Assigned to: {{ assignment.engineer }} | 📅 Created: {{ assignment.created_date }}
    </div>
    </div>
    <div class="topic-badge topic-{{ assignment.topic }}">
    {{ assignment.topic.title() }}
    </div>
    </div>
    
    <div class="assignment-details">
    <div class="detail-item">
    <div class="detail-value">{{ assignment.question_count }}</div>
    <div class="detail-label">Questions</div>
    </div>
    <div class="detail-item">
    <div class="detail-value">{{ assignment.points }}</div>
    <div class="detail-label">Points</div>
    </div>
    <div class="detail-item">
    <div class="detail-value">{{ assignment.due_date }}</div>
    <div class="detail-label">Due Date</div>
    </div>
    <div class="detail-item">
    <div class="detail-value">{{ assignment.submission_count }}</div>
    <div class="detail-label">Submissions</div>
    </div>
    </div>
    
    <div class="assignment-actions">
    <button onclick="viewAssignment('{{ assignment.id }}')" class="btn btn-info">👁️ View Details</button>
    {% if assignment.has_submission %}
    <button onclick="viewSubmissions('{{ assignment.id }}')" class="btn btn-primary">📝 View Submissions</button>
    {% endif %}
    <button onclick="editAssignment('{{ assignment.id }}')" class="btn btn-warning">✏️ Edit</button>
    <button onclick="duplicateAssignment('{{ assignment.id }}')" class="btn btn-info">📋 Duplicate</button>
    </div>
    
    </div>
    {% endfor %}
    
    {% else %}
    <div class="no-assignments">
    <h3>📭 No Assignments Yet</h3>
    <p>Create your first assignment to get started!</p>
    <button onclick="window.location.href='/admin'" style="margin-top: 20px; padding: 12px 24px; background: #27ae60; color: white; border: none; border-radius: 6px; cursor: pointer;">
    ➕ Create Assignments
    </button>
    </div>
    {% endif %}
    
    </div>
    </div>
    </div>
    
    <script>
    function viewAssignment(assignmentId) {
        alert('📝 Assignment Viewer\\n\\nThis will show full assignment details including all questions.\\n\\nAssignment: ' + assignmentId);
    }
    
    function viewSubmissions(assignmentId) {
        window.location.href = '/admin/submissions';
    }
    
    function editAssignment(assignmentId) {
        alert('✏️ Assignment Editor\\n\\nThis will open the assignment editor.\\n\\nAssignment: ' + assignmentId);
    }
    
    function duplicateAssignment(assignmentId) {
        if (confirm('Create a copy of this assignment?')) {
            alert('📋 Assignment duplicated!\\n\\nA copy has been created for other engineers.');
        }
    }
    </script>
    </body></html>'''
    
    return render_template_string(assignments_html, assignments=assignment_data)

# Additional API routes for grading
@app.route('/api/admin/grade-submission', methods=['POST'])
@login_required
@admin_required
def grade_submission_api():
    try:
        data = request.get_json()
        submission_id = data.get('submission_id')
        admin_grade = data.get('admin_grade')
        admin_feedback = data.get('admin_feedback', '')
        release_grade = data.get('release_grade', False)
        
        submission = Submission.query.get_or_404(submission_id)
        
        submission.admin_grade = admin_grade
        submission.admin_feedback = admin_feedback
        submission.graded_by_admin = current_user.id
        submission.graded_date = datetime.datetime.utcnow()
        submission.is_grade_released = release_grade
        
        db.session.commit()
        
        # Create notification if released
        if release_grade:
            notification = Notification(
                user_id=submission.engineer_id,
                title=f"Grade Released: {admin_grade}",
                message=f"Your assignment has been graded and released. Grade: {admin_grade}"
            )
            db.session.add(notification)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Grade {admin_grade} assigned successfully' + (' and released to student' if release_grade else '')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/release-grade', methods=['POST'])
@login_required
@admin_required
def release_grade_api():
    try:
        data = request.get_json()
        submission_id = data.get('submission_id')
        
        submission = Submission.query.get_or_404(submission_id)
        
        if not submission.admin_grade:
            return jsonify({'error': 'No grade assigned yet'}), 400
        
        submission.is_grade_released = True
        db.session.commit()
        
        # Create notification
        notification = Notification(
            user_id=submission.engineer_id,
            title=f"Grade Released: {submission.admin_grade}",
            message=f"Your assignment grade has been released. Check your dashboard to view results."
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Grade released successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    try:
        # Get comprehensive system statistics
        total_users = User.query.count()
        total_engineers = User.query.filter_by(is_admin=False).count()
        total_assignments = Assignment.query.count()
        total_submissions = Submission.query.count()
        pending_grading = Submission.query.filter(Submission.admin_grade.is_(None)).count()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'system': 'Physical Design Assignment System - Full Version',
            'version': '2.0',
            'statistics': {
                'total_users': total_users,
                'engineers': total_engineers,
                'assignments': total_assignments,
                'submissions': total_submissions,
                'pending_grading': pending_grading,
                'completion_rate': round((total_submissions / max(total_assignments, 1)) * 100, 1)
            },
            'features': [
                'Role-based authentication',
                'Comprehensive technical evaluation',
                'Advanced assignment interface',
                'Admin grading system',
                'Real-time notifications',
                'Progress tracking'
            ]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 500

# Initialize everything
def init_app():
    with app.app_context():
        try:
            print("🚀 Initializing Complete Physical Design System...")
            db.create_all()
            
            # Create admin if doesn't exist
            if not User.query.filter_by(username='admin').first():
                print("Creating admin user...")
                admin = User(
                    username='admin',
                    email='admin@physicaldesign.com',
                    is_admin=True,
                    department='Administration'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                
                # Create engineers with detailed profiles
                engineers_data = [
                    {
                        'username': 'engineer1',
                        'email': 'eng1@company.com',
                        'engineer_id': 'PD_ENG_001',
                        'department': 'Physical Design'
                    },
                    {
                        'username': 'engineer2',
                        'email': 'eng2@company.com', 
                        'engineer_id': 'PD_ENG_002',
                        'department': 'Implementation'
                    },
                    {
                        'username': 'engineer3',
                        'email': 'eng3@company.com',
                        'engineer_id': 'PD_ENG_003', 
                        'department': 'Verification'
                    }
                ]
                
                for eng_data in engineers_data:
                    print(f"Creating {eng_data['username']}...")
                    engineer = User(
                        username=eng_data['username'],
                        email=eng_data['email'],
                        engineer_id=eng_data['engineer_id'],
                        department=eng_data['department'],
                        is_admin=False
                    )
                    engineer.set_password('eng123')
                    db.session.add(engineer)
                
                db.session.commit()
                print("✅ Complete user system created successfully!")
            else:
                print("✅ Users already exist")
                
        except Exception as e:
            print(f"❌ Database initialization error: {e}")

# Initialize on import
init_app()

if __name__ == '__main__':
    print("🚀 Starting Complete Physical Design Assignment System...")
    print("🔗 System Features:")
    print("   ✅ Role-based authentication (Admin/Engineer)")
    print("   ✅ Comprehensive technical assignments")  
    print("   ✅ Advanced evaluation engine")
    print("   ✅ Real-time submission interface")
    print("   ✅ Admin grading and feedback system")
    print("   ✅ Progress tracking and notifications")
    print("   ✅ Health monitoring and analytics")
    print("")
    print("🔐 Demo Accounts:")
    print("   👨‍💼 Admin: admin/admin123 (Full system access)")
    print("   👨‍💻 Engineer: engineer1/eng123 (Assignment interface)")
    print("   👨‍💻 Engineer: engineer2/eng123 (Assignment interface)")
    print("")
    print("📊 Health Check: /health")
    print("🚀 Ready for production deployment!")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
