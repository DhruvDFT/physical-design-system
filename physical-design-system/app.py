# app.py - Complete Physical Design Interview System with All Original Logic
import os
import random
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import logging

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'pd-interview-secret-key-2024')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory database (can be replaced with SQLAlchemy later)
class Database:
    def __init__(self):
        self.users = {}
        self.assignments = {}
        self.notifications = {}
        self.assignment_counter = 0
        self.init_default_users()
    
    def init_default_users(self):
        """Initialize default admin and student users"""
        # Admin user
        self.users['admin'] = {
            'id': 'admin',
            'username': 'admin',
            'password': generate_password_hash('admin123'),
            'email': 'admin@pdis.com',
            'is_admin': True,
            'experience_years': 10,
            'created_at': datetime.now().isoformat()
        }
        
        # Sample student users
        for i in range(1, 4):
            user_id = f'eng00{i}'
            self.users[user_id] = {
                'id': user_id,
                'username': user_id,
                'password': generate_password_hash('password123'),
                'email': f'{user_id}@pdis.com',
                'is_admin': False,
                'experience_years': 3 + i,
                'created_at': datetime.now().isoformat()
            }
        logger.info("Default users initialized")

# Initialize database
db = Database()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        user = db.users.get(session['user_id'])
        if not user or not user.get('is_admin', False):
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

# Complete 3+ Years Physical Design Questions (ALL ORIGINAL QUESTIONS)
PHYSICAL_DESIGN_TOPICS_3PLUS = {
    "floorplanning": {
        "title": "Physical Design: Floorplanning (3+ Years Experience)",
        "description": "Practical floorplanning challenges for experienced engineers",
        "difficulty": "intermediate",
        "questions": [
            "You have a 5mm x 5mm die with 4 hard macros (each 1mm x 0.8mm) and need to achieve 70% utilization. Describe your macro placement strategy considering timing and power delivery.",
            "Your design has setup timing violations on paths crossing from left to right. The floorplan has macros placed randomly. How would you reorganize the floorplan to improve timing?",
            "You're working with a design that has 2 voltage domains (0.9V core, 1.2V IO). Explain how you would plan the floorplan to minimize level shifter count and power grid complexity.",
            "During floorplan, you notice routing congestion in the center region. What are 3 specific techniques you would use to reduce congestion without major timing impact?",
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
        ]
    },
    
    "placement": {
        "title": "Physical Design: Placement Optimization (3+ Years Experience)",
        "description": "Hands-on placement challenges for practical experience",
        "difficulty": "intermediate", 
        "questions": [
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
        ]
    },
    
    "routing": {
        "title": "Physical Design: Routing and Timing Closure (3+ Years Experience)", 
        "description": "Real-world routing challenges and DRC resolution",
        "difficulty": "intermediate",
        "questions": [
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
}

# Question Pool Manager (Original Logic)
class QuestionPoolManager:
    def __init__(self):
        self.topics = PHYSICAL_DESIGN_TOPICS_3PLUS
        
    def get_questions_by_experience(self, experience_years, topic):
        """Get appropriate questions based on experience level"""
        if topic in self.topics:
            # For now, return all 15 questions for 3+ years experience
            # Can be extended to add 5+ and 8+ year questions later
            return self.topics[topic]["questions"]
        return []
    
    def get_mixed_difficulty_questions(self, experience_years, topic):
        """Get questions mixed by difficulty based on experience"""
        questions = self.get_questions_by_experience(experience_years, topic)
        
        # Add experience-based bonus questions
        if experience_years >= 5:
            # Can add advanced questions here
            pass
        if experience_years >= 8:
            # Can add expert questions here
            pass
            
        return questions[:15]  # Ensure exactly 15 questions

# Assignment Manager (Original Logic)
class AssignmentManager:
    def __init__(self):
        self.question_manager = QuestionPoolManager()
    
    def create_assignment(self, engineer_id, topic, experience_years=None):
        """Create a new assignment with all original logic"""
        if experience_years is None:
            user = db.users.get(engineer_id)
            experience_years = user.get('experience_years', 3) if user else 3
        
        questions = self.question_manager.get_mixed_difficulty_questions(experience_years, topic)
        
        # Determine difficulty parameters (original logic)
        if experience_years >= 8:
            points = 200
            due_days = 21
            difficulty = "Expert"
        elif experience_years >= 5:
            points = 175
            due_days = 14
            difficulty = "Advanced"
        else:
            points = 150
            due_days = 10
            difficulty = "Intermediate"
        
        db.assignment_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        assignment_id = f"PD_{topic.upper()}_{engineer_id}_{timestamp}"
        
        assignment = {
            'id': assignment_id,
            'title': f"{PHYSICAL_DESIGN_TOPICS_3PLUS[topic]['title']} - {difficulty} Level",
            'topic': topic,
            'engineer_id': engineer_id,
            'questions': questions,
            'due_date': (datetime.now() + timedelta(days=due_days)).isoformat(),
            'points': points,
            'status': 'pending',
            'created_date': datetime.now().isoformat(),
            'completed_date': None,
            'difficulty': difficulty,
            'experience_years': experience_years
        }
        
        db.assignments[assignment_id] = assignment
        
        # Create notification
        self.create_notification(
            engineer_id,
            f"New {topic.title()} Assignment",
            f"You have a new {difficulty} level assignment with {len(questions)} questions. Due in {due_days} days."
        )
        
        return assignment
    
    def create_notification(self, user_id, title, message):
        """Create notification (original logic)"""
        notification_id = f"NOTIF_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        notification = {
            'id': notification_id,
            'user_id': user_id,
            'title': title,
            'message': message,
            'created_at': datetime.now().isoformat(),
            'is_read': False
        }
        
        if user_id not in db.notifications:
            db.notifications[user_id] = []
        
        db.notifications[user_id].append(notification)
        return notification
    
    def should_refresh_assignment(self, assignment):
        """Check if assignment should be refreshed (original logic)"""
        if not assignment.get('due_date'):
            return False
            
        due_date = datetime.fromisoformat(assignment['due_date'])
        days_since_due = (datetime.now() - due_date).days
        return days_since_due >= 7  # Refresh 7 days after deadline
    
    def refresh_assignments(self):
        """Auto-refresh expired assignments (original logic)"""
        refreshed_count = 0
        
        for assignment_id, assignment in list(db.assignments.items()):
            if self.should_refresh_assignment(assignment) and assignment['status'] != 'refreshed':
                # Check if engineer already has recent assignment
                engineer_id = assignment['engineer_id']
                topic = assignment['topic']
                
                recent = any(
                    a['engineer_id'] == engineer_id and 
                    a['topic'] == topic and 
                    a['id'] != assignment_id and
                    datetime.fromisoformat(a['created_date']) > datetime.now() - timedelta(days=30)
                    for a in db.assignments.values()
                )
                
                if not recent:
                    # Create new refreshed assignment
                    new_assignment = self.create_assignment(
                        engineer_id,
                        topic,
                        assignment.get('experience_years', 3)
                    )
                    
                    if new_assignment:
                        assignment['status'] = 'refreshed'
                        refreshed_count += 1
        
        return refreshed_count

# Initialize managers
assignment_manager = AssignmentManager()

# HTML Template (Complete GUI)
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Physical Design Interview System{% endblock %}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #f0f2f5; color: #333; }
        
        /* Header */
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.8rem; }
        .user-info { display: flex; align-items: center; gap: 20px; }
        .logout-btn { background: rgba(255,255,255,0.2); color: white; text-decoration: none; padding: 8px 16px; border-radius: 5px; }
        .logout-btn:hover { background: rgba(255,255,255,0.3); }
        
        /* Container */
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        
        /* Cards */
        .card { background: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 1.5rem; }
        .stat-card { text-align: center; }
        .stat-value { font-size: 2.5rem; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; font-size: 0.9rem; text-transform: uppercase; }
        
        /* Grid */
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        
        /* Forms */
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #555; }
        input, select { width: 100%; padding: 10px; border: 2px solid #e1e4e8; border-radius: 5px; font-size: 1rem; }
        input:focus, select:focus { outline: none; border-color: #667eea; }
        
        /* Buttons */
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 24px; border-radius: 5px; font-size: 1rem; font-weight: 600; cursor: pointer; display: inline-block; text-decoration: none; }
        .btn:hover { transform: translateY(-1px); box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        .btn-secondary { background: #6c757d; margin-left: 10px; }
        
        /* Tables */
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e1e4e8; }
        th { background: #f8f9fa; font-weight: 600; color: #555; }
        
        /* Questions */
        .question { background: #f8f9fa; padding: 1.5rem; margin-bottom: 1rem; border-radius: 8px; border-left: 4px solid #667eea; }
        .question-number { font-weight: 600; color: #667eea; margin-bottom: 0.5rem; }
        
        /* Badges */
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; }
        .badge-pending { background: #ffd93d; color: #856404; }
        .badge-intermediate { background: #e3f2fd; color: #1976d2; }
        .badge-advanced { background: #f3e5f5; color: #7b1fa2; }
        .badge-expert { background: #ffebee; color: #c62828; }
        
        /* Login */
        .login-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .login-box { background: white; padding: 3rem; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); width: 100%; max-width: 400px; }
        
        /* Messages */
        .message { padding: 1rem; border-radius: 5px; margin-bottom: 1rem; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #e3f2fd; color: #1976d2; }
    </style>
    {% block extra_style %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    {% block scripts %}{% endblock %}
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    """Home page - redirect based on login status"""
    if 'user_id' in session:
        user = db.users.get(session['user_id'])
        if user and user.get('is_admin'):
            return redirect('/admin')
        else:
            return redirect('/student')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with original logic"""
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user by username
        user = None
        for u in db.users.values():
            if u['username'] == username:
                user = u
                break
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user.get('is_admin', False)
            session['experience_years'] = user.get('experience_years', 3)
            
            if user.get('is_admin'):
                return redirect('/admin')
            else:
                return redirect('/student')
        else:
            error = 'Invalid username or password'
    
    login_html = '''
    {% extends "base.html" %}
    {% block content %}
    <div class="login-container">
        <div class="login-box">
            <h1 style="text-align: center; margin-bottom: 2rem;">🎯 Physical Design Interview System</h1>
            
            <div class="info">
                <strong>Demo Credentials:</strong><br>
                Admin: admin / admin123<br>
                Student: eng001 / password123
            </div>
            
            {% if error %}
            <div class="message error">{{ error }}</div>
            {% endif %}
            
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required autofocus>
                </div>
                
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                
                <button type="submit" class="btn" style="width: 100%;">Login</button>
            </form>
        </div>
    </div>
    {% endblock %}
    '''
    
    return render_template_string(BASE_TEMPLATE + login_html, error=error)

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    session.clear()
    return redirect('/login')

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with all original features"""
    # Get statistics
    engineers = [u for u in db.users.values() if not u.get('is_admin', False)]
    assignments = sorted(db.assignments.values(), key=lambda x: x['created_date'], reverse=True)[:10]
    
    total_assignments = len(db.assignments)
    pending_assignments = sum(1 for a in db.assignments.values() if a['status'] == 'pending')
    
    admin_html = '''
    {% extends "base.html" %}
    {% block content %}
    <div class="header">
        <div class="header-content">
            <h1>🎯 Admin Dashboard</h1>
            <div class="user-info">
                <span>Welcome, {{ session.username }}</span>
                <a href="/logout" class="logout-btn">Logout</a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <!-- Statistics -->
        <div class="dashboard-grid">
            <div class="card stat-card">
                <div class="stat-value">{{ engineers|length }}</div>
                <div class="stat-label">Total Engineers</div>
            </div>
            <div class="card stat-card">
                <div class="stat-value">{{ total_assignments }}</div>
                <div class="stat-label">Total Assignments</div>
            </div>
            <div class="card stat-card">
                <div class="stat-value">{{ pending_assignments }}</div>
                <div class="stat-label">Pending</div>
            </div>
            <div class="card stat-card">
                <div class="stat-value">45</div>
                <div class="stat-label">Total Questions</div>
            </div>
        </div>
        
        <!-- Create Assignment -->
        <div class="card">
            <h2>Create Assignment</h2>
            {% if request.args.get('message') %}
            <div class="message success">{{ request.args.get('message') }}</div>
            {% endif %}
            
            <form method="POST" action="/admin/create-assignment">
                <div class="form-group">
                    <label>Select Engineer</label>
                    <select name="engineer_id" required>
                        <option value="">Choose engineer...</option>
                        {% for engineer in engineers %}
                        <option value="{{ engineer.id }}">{{ engineer.username }} ({{ engineer.experience_years }} years exp)</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Topic</label>
                    <select name="topic" required>
                        <option value="">Choose topic...</option>
                        <option value="floorplanning">Floorplanning</option>
                        <option value="placement">Placement</option>
                        <option value="routing">Routing</option>
                    </select>
                </div>
                
                <button type="submit" class="btn">Create Assignment</button>
                <button type="button" class="btn btn-secondary" onclick="createForAll()">Create for All Engineers</button>
            </form>
        </div>
        
        <!-- Recent Assignments -->
        <div class="card">
            <h2>Recent Assignments</h2>
            <button onclick="refreshAssignments()" class="btn" style="float: right; margin-top: -40px;">🔄 Auto-Refresh Expired</button>
            
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Engineer</th>
                        <th>Topic</th>
                        <th>Difficulty</th>
                        <th>Status</th>
                        <th>Due Date</th>
                        <th>Points</th>
                    </tr>
                </thead>
                <tbody>
                    {% for assignment in assignments %}
                    <tr>
                        <td>{{ assignment.id }}</td>
                        <td>{{ assignment.engineer_id }}</td>
                        <td>{{ assignment.topic|title }}</td>
                        <td><span class="badge badge-{{ assignment.difficulty|lower }}">{{ assignment.difficulty }}</span></td>
                        <td><span class="badge badge-{{ assignment.status }}">{{ assignment.status }}</span></td>
                        <td>{{ assignment.due_date[:10] }}</td>
                        <td>{{ assignment.points }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
    function createForAll() {
        if (confirm('Create assignments for all engineers?')) {
            fetch('/api/admin/create-all-assignments', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                });
        }
    }
    
    function refreshAssignments() {
        fetch('/api/admin/refresh-assignments', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                location.reload();
            });
    }
    </script>
    {% endblock %}
    '''
    
    return render_template_string(
        BASE_TEMPLATE + admin_html,
        session=session,
        engineers=engineers,
        total_assignments=total_assignments,
        pending_assignments=pending_assignments,
        assignments=assignments,
        request=request
    )

@app.route('/admin/create-assignment', methods=['POST'])
@login_required
@admin_required
def admin_create_assignment():
    """Create assignment (original logic)"""
    engineer_id = request.form.get('engineer_id')
    topic = request.form.get('topic')
    
    if engineer_id and topic:
        assignment = assignment_manager.create_assignment(engineer_id, topic)
        if assignment:
            message = f"Assignment created successfully for {engineer_id}"
        else:
            message = "Failed to create assignment"
    else:
        message = "Please select both engineer and topic"
    
    return redirect(url_for('admin_dashboard', message=message))

@app.route('/student')
@login_required
def student_dashboard():
    """Student dashboard with all features"""
    user_id = session['user_id']
    
    # Get student's assignments
    my_assignments = [
        a for a in db.assignments.values() 
        if a['engineer_id'] == user_id
    ]
    my_assignments.sort(key=lambda x: x['created_date'], reverse=True)
    
    # Get notifications
    my_notifications = db.notifications.get(user_id, [])[-5:]  # Last 5
    
    # Mark notifications as read
    for notif in my_notifications:
        notif['is_read'] = True
    
    student_html = '''
    {% extends "base.html" %}
    {% block content %}
    <div class="header">
        <div class="header-content">
            <h1>🎯 Student Dashboard</h1>
            <div class="user-info">
                <span>{{ session.username }} ({{ session.experience_years }} years exp)</span>
                <a href="/logout" class="logout-btn">Logout</a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <!-- Notifications -->
        {% if notifications %}
        <div class="card">
            <h2>📬 Notifications</h2>
            {% for notification in notifications %}
            <div class="message info">
                <strong>{{ notification.title }}</strong><br>
                {{ notification.message }}<br>
                <small>{{ notification.created_at[:16] }}</small>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <!-- Assignments -->
        <h2>My Assignments</h2>
        {% if assignments %}
            {% for assignment in assignments %}
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3>{{ assignment.topic|title }} Assignment</h3>
                    <div>
                        <span class="badge badge-{{ assignment.difficulty|lower }}">{{ assignment.difficulty }}</span>
                        <span class="badge badge-{{ assignment.status }}">{{ assignment.status }}</span>
                    </div>
                </div>
                
                <p><strong>Due:</strong> {{ assignment.due_date[:10] }} | <strong>Points:</strong> {{ assignment.points }}</p>
                
                <h4 style="margin-top: 1.5rem;">Questions (15):</h4>
                {% for question in assignment.questions %}
                <div class="question">
                    <div class="question-number">Question {{ loop.index }}:</div>
                    {{ question }}
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        {% else %}
            <div class="card">
                <p>No assignments yet. Check back later!</p>
            </div>
        {% endif %}
    </div>
    {% endblock %}
    '''
    
    return render_template_string(
        BASE_TEMPLATE + student_html,
        session=session,
        assignments=my_assignments,
        notifications=my_notifications
    )

# API Routes (all original logic preserved)
@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'users': len(db.users),
        'assignments': len(db.assignments)
    })

@app.route('/api/admin/create-all-assignments', methods=['POST'])
@login_required
@admin_required
def api_create_all_assignments():
    """Create assignments for all engineers (original logic)"""
    engineers = [u for u in db.users.values() if not u.get('is_admin', False)]
    topics = ['floorplanning', 'placement', 'routing']
    
    created_count = 0
    for engineer in engineers:
        for topic in topics:
            # Check if assignment already exists
            exists = any(
                a['engineer_id'] == engineer['id'] and 
                a['topic'] == topic and 
                a['status'] == 'pending'
                for a in db.assignments.values()
            )
            
            if not exists:
                assignment = assignment_manager.create_assignment(engineer['id'], topic)
                if assignment:
                    created_count += 1
    
    return jsonify({
        'success': True,
        'message': f'Created {created_count} assignments for {len(engineers)} engineers'
    })

@app.route('/api/admin/refresh-assignments', methods=['POST'])
@login_required
@admin_required
def api_refresh_assignments():
    """Auto-refresh expired assignments (original logic)"""
    refreshed_count = assignment_manager.refresh_assignments()
    
    return jsonify({
        'success': True,
        'message': f'Auto-refreshed {refreshed_count} expired assignments'
    })

@app.route('/api/assignments', methods=['GET'])
@login_required
def api_list_assignments():
    """List assignments (filtered by user role)"""
    if session.get('is_admin'):
        assignments = list(db.assignments.values())
    else:
        assignments = [
            a for a in db.assignments.values() 
            if a['engineer_id'] == session['user_id']
        ]
    
    return jsonify({
        'success': True,
        'count': len(assignments),
        'assignments': [{
            'id': a['id'],
            'title': a['title'],
            'topic': a['topic'],
            'status': a['status'],
            'points': a['points'],
            'due_date': a['due_date'],
            'questions_count': len(a['questions'])
        } for a in assignments]
    })

@app.route('/api/assignments/<assignment_id>', methods=['GET'])
@login_required
def api_get_assignment(assignment_id):
    """Get specific assignment details"""
    assignment = db.assignments.get(assignment_id)
    
    if not assignment:
        return jsonify({'success': False, 'error': 'Assignment not found'}), 404
    
    # Check access permissions
    if not session.get('is_admin') and assignment['engineer_id'] != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    return jsonify({
        'success': True,
        'assignment': assignment
    })

@app.route('/api/questions/summary', methods=['GET'])
@login_required
def api_questions_summary():
    """Get summary of all available questions"""
    summary = {
        'total_questions': 0,
        'by_topic': {}
    }
    
    for topic, data in PHYSICAL_DESIGN_TOPICS_3PLUS.items():
        count = len(data['questions'])
        summary['by_topic'][topic] = {
            'title': data['title'],
            'count': count,
            'difficulty': data['difficulty']
        }
        summary['total_questions'] += count
    
    return jsonify({
        'success': True,
        'summary': summary,
        'message': f'Total of {summary["total_questions"]} questions available (15 per topic)'
    })

@app.route('/api/analytics', methods=['GET'])
@login_required
@admin_required
def api_analytics():
    """Get system analytics (admin only) - original logic"""
    # Calculate analytics
    total_assignments = len(db.assignments)
    by_status = {'pending': 0, 'completed': 0, 'refreshed': 0}
    by_topic = {'floorplanning': 0, 'placement': 0, 'routing': 0}
    by_difficulty = {'Intermediate': 0, 'Advanced': 0, 'Expert': 0}
    
    for assignment in db.assignments.values():
        # Status
        status = assignment.get('status', 'pending')
        if status in by_status:
            by_status[status] += 1
        
        # Topic
        topic = assignment.get('topic')
        if topic in by_topic:
            by_topic[topic] += 1
        
        # Difficulty
        difficulty = assignment.get('difficulty', 'Intermediate')
        if difficulty in by_difficulty:
            by_difficulty[difficulty] += 1
    
    return jsonify({
        'success': True,
        'analytics': {
            'total_assignments': total_assignments,
            'total_engineers': len([u for u in db.users.values() if not u.get('is_admin', False)]),
            'by_status': by_status,
            'by_topic': by_topic,
            'by_difficulty': by_difficulty,
            'total_questions': 45,  # 15 questions × 3 topics
            'timestamp': datetime.now().isoformat()
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Create some sample assignments for demo
if len(db.assignments) == 0:
    # Create sample assignments for eng001
    assignment_manager.create_assignment('eng001', 'floorplanning')
    assignment_manager.create_assignment('eng001', 'placement')
    logger.info("Sample assignments created")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Physical Design Interview System on port {port}")
    logger.info("Default users: Admin (admin/admin123), Students (eng001-eng003/password123)")
    app.run(host='0.0.0.0', port=port, debug=False)
