# app.py - Complete Physical Design Interview System with Login
import os
import random
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage (replace with database in production)
users_store = {}
assignments_store = {}
notifications_store = {}
assignment_counter = 0

# Initialize default users
def init_default_users():
    # Admin user
    users_store['admin'] = {
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
        users_store[user_id] = {
            'id': user_id,
            'username': user_id,
            'password': generate_password_hash('password123'),
            'email': f'{user_id}@pdis.com',
            'is_admin': False,
            'experience_years': 3 + i,
            'created_at': datetime.now().isoformat()
        }

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data['email']
        self.is_admin = user_data.get('is_admin', False)
        self.experience_years = user_data.get('experience_years', 3)

@login_manager.user_loader
def load_user(user_id):
    user_data = users_store.get(user_id)
    if engineer_id and topic:
        assignment = create_assignment(engineer_id, topic)
        if assignment:
            message = f"Assignment created successfully for {engineer_id}"
        else:
            message = "Failed to create assignment"
    else:
        message = "Please select both engineer and topic"
    
    return redirect(url_for('admin_dashboard', message=message))

@app.route('/admin/create-all-assignments', methods=['POST'])
@login_required
def admin_create_all_assignments():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    engineers = [u for u in users_store.values() if not u.get('is_admin', False)]
    topics = ['floorplanning', 'placement', 'routing']
    
    created_count = 0
    for engineer in engineers:
        for topic in topics:
            # Check if assignment already exists
            exists = any(
                a['engineer_id'] == engineer['id'] and 
                a['topic'] == topic and 
                a['status'] == 'pending'
                for a in assignments_store.values()
            )
            
            if not exists:
                assignment = create_assignment(engineer['id'], topic)
                if assignment:
                    created_count += 1
    
    return jsonify({
        'success': True,
        'message': f'Created {created_count} assignments for {len(engineers)} engineers'
    })

@app.route('/admin/refresh-assignments', methods=['POST'])
@login_required
def admin_refresh_assignments():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    refreshed_count = auto_refresh_assignments()
    
    return jsonify({
        'success': True,
        'message': f'Auto-refreshed {refreshed_count} expired assignments'
    })

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    # Get student's assignments
    my_assignments = [
        a for a in assignments_store.values() 
        if a['engineer_id'] == current_user.id
    ]
    my_assignments.sort(key=lambda x: x['created_date'], reverse=True)
    
    # Get notifications
    my_notifications = notifications_store.get(current_user.id, [])
    my_notifications.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Mark notifications as read
    for notif in my_notifications:
        notif['is_read'] = True
    
    # Check if should show questions for a specific assignment
    show_assignment_id = request.args.get('show')
    show_questions = False
    selected_assignment = None
    
    if show_assignment_id:
        for a in my_assignments:
            if a['id'] == show_assignment_id:
                show_questions = True
                selected_assignment = show_assignment_id
                break
    
    return render_template_string(
        STUDENT_DASHBOARD_TEMPLATE,
        current_user=current_user,
        assignments=my_assignments,
        notifications=my_notifications[:5],  # Show latest 5 notifications
        show_questions=show_questions,
        selected_assignment=selected_assignment
    )

# API Routes (for programmatic access)
@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'users': len(users_store),
        'assignments': len(assignments_store)
    })

@app.route('/api/assignments', methods=['GET'])
@login_required
def api_list_assignments():
    """List assignments (filtered by user role)"""
    if current_user.is_admin:
        assignments = list(assignments_store.values())
    else:
        assignments = [
            a for a in assignments_store.values() 
            if a['engineer_id'] == current_user.id
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
    assignment = assignments_store.get(assignment_id)
    
    if not assignment:
        return jsonify({'success': False, 'error': 'Assignment not found'}), 404
    
    # Check access permissions
    if not current_user.is_admin and assignment['engineer_id'] != current_user.id:
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
def api_analytics():
    """Get system analytics (admin only)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Calculate analytics
    total_assignments = len(assignments_store)
    by_status = {'pending': 0, 'completed': 0, 'refreshed': 0, 'expired': 0}
    by_topic = {'floorplanning': 0, 'placement': 0, 'routing': 0}
    by_difficulty = {'Intermediate': 0, 'Advanced': 0, 'Expert': 0}
    
    for assignment in assignments_store.values():
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
            'total_engineers': len([u for u in users_store.values() if not u.get('is_admin', False)]),
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

# Initialize default users on startup
init_default_users()

# Create some sample assignments for demo
if len(assignments_store) == 0:
    # Create sample assignments for eng001
    for topic in ['floorplanning', 'placement', 'routing']:
        create_assignment('eng001', topic)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Physical Design Interview System on port {port}")
    logger.info("Default users created - Admin: admin/admin123, Students: eng001-eng003/password123")
    app.run(host='0.0.0.0', port=port, debug=False) user_data:
        return User(user_data)
    return None

# Complete 3+ Years Physical Design Questions (ALL 15 questions per topic)
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

# Assignment Management Functions
def create_assignment(engineer_id, topic, experience_years=None):
    """Create a new assignment for an engineer"""
    global assignment_counter
    
    if topic not in PHYSICAL_DESIGN_TOPICS_3PLUS:
        return None
    
    # Get user's experience if not provided
    if experience_years is None:
        user_data = users_store.get(engineer_id)
        experience_years = user_data.get('experience_years', 3) if user_data else 3
    
    # Get all questions for the topic
    all_questions = PHYSICAL_DESIGN_TOPICS_3PLUS[topic]["questions"]
    questions = all_questions.copy()  # Use all 15 questions
    
    # Determine difficulty and parameters based on experience
    if experience_years >= 8:
        difficulty = "Expert"
        points = 200
        due_days = 21
    elif experience_years >= 5:
        difficulty = "Advanced"
        points = 175
        due_days = 14
    else:
        difficulty = "Intermediate"
        points = 150
        due_days = 10
    
    # Create assignment
    assignment_counter += 1
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
    
    assignments_store[assignment_id] = assignment
    
    # Create notification
    create_notification(
        engineer_id,
        f"New {topic.title()} Assignment",
        f"You have a new {difficulty} level assignment with {len(questions)} questions. Due in {due_days} days."
    )
    
    return assignment

def create_notification(user_id, title, message):
    """Create a notification for a user"""
    notification_id = f"NOTIF_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    notification = {
        'id': notification_id,
        'user_id': user_id,
        'title': title,
        'message': message,
        'created_at': datetime.now().isoformat(),
        'is_read': False
    }
    
    if user_id not in notifications_store:
        notifications_store[user_id] = []
    
    notifications_store[user_id].append(notification)
    return notification

def auto_refresh_assignments():
    """Auto-refresh assignments that are 7+ days past deadline"""
    refreshed_count = 0
    current_time = datetime.now()
    
    for assignment_id, assignment in list(assignments_store.items()):
        due_date = datetime.fromisoformat(assignment['due_date'])
        
        # Check if assignment is 7+ days past due and not already refreshed
        if (current_time - due_date).days >= 7 and assignment['status'] != 'refreshed':
            # Check if engineer already has a recent assignment for this topic
            engineer_id = assignment['engineer_id']
            topic = assignment['topic']
            
            # Check for recent assignments
            has_recent = False
            for aid, a in assignments_store.items():
                if (a['engineer_id'] == engineer_id and 
                    a['topic'] == topic and 
                    aid != assignment_id):
                    created = datetime.fromisoformat(a['created_date'])
                    if (current_time - created).days < 30:
                        has_recent = True
                        break
            
            if not has_recent:
                # Create new refreshed assignment
                new_assignment = create_assignment(
                    engineer_id,
                    topic,
                    assignment.get('experience_years', 3)
                )
                
                if new_assignment:
                    # Mark old assignment as refreshed
                    assignment['status'] = 'refreshed'
                    refreshed_count += 1
    
    return refreshed_count

# HTML Templates
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Physical Design Interview System - Login</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            width: 400px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            opacity: 0.9;
        }
        .error {
            color: #d32f2f;
            text-align: center;
            margin-top: 10px;
        }
        .info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🎯 Physical Design Interview System</h1>
        <div class="info">
            <strong>Demo Credentials:</strong><br>
            Admin: admin / admin123<br>
            Student: eng001 / password123
        </div>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST" action="/login">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

ADMIN_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard - Physical Design Interview System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; }
        .header h1 { margin: 0; }
        .nav { float: right; }
        .nav a { color: white; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-value { font-size: 36px; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f5f5f5; font-weight: bold; }
        button { background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
        button:hover { background: #5a67d8; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Admin Dashboard</h1>
        <div class="nav">
            <span>Welcome, {{ current_user.username }}</span>
            <a href="/logout">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <!-- Statistics -->
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{{ total_engineers }}</div>
                <div class="stat-label">Total Engineers</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ total_assignments }}</div>
                <div class="stat-label">Total Assignments</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ pending_assignments }}</div>
                <div class="stat-label">Pending</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">75</div>
                <div class="stat-label">Total Questions</div>
            </div>
        </div>
        
        <!-- Create Assignment -->
        <div class="card">
            <h2>Create Assignment</h2>
            {% if message %}
            <div class="success">{{ message }}</div>
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
                <button type="submit">Create Assignment</button>
                <button type="button" onclick="createForAll()">Create for All Engineers</button>
            </form>
        </div>
        
        <!-- Recent Assignments -->
        <div class="card">
            <h2>Recent Assignments</h2>
            <button onclick="refreshAssignments()" style="float: right; margin-top: -40px;">🔄 Auto-Refresh Expired</button>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Engineer</th>
                        <th>Topic</th>
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
                        <td>{{ assignment.topic }}</td>
                        <td>{{ assignment.status }}</td>
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
                fetch('/admin/create-all-assignments', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        alert(data.message);
                        location.reload();
                    });
            }
        }
        
        function refreshAssignments() {
            fetch('/admin/refresh-assignments', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                });
        }
    </script>
</body>
</html>
"""

STUDENT_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Dashboard - Physical Design Interview System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; }
        .header h1 { margin: 0; }
        .nav { float: right; }
        .nav a { color: white; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .assignment-card { 
            background: white; 
            border-radius: 8px; 
            padding: 20px; 
            margin-bottom: 20px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .assignment-header { 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            margin-bottom: 10px;
        }
        .badge { 
            display: inline-block; 
            padding: 4px 12px; 
            border-radius: 20px; 
            font-size: 14px; 
            font-weight: bold;
        }
        .badge-pending { background: #fff3cd; color: #856404; }
        .badge-completed { background: #d4edda; color: #155724; }
        .badge-expired { background: #f8d7da; color: #721c24; }
        .question {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }
        .question-number {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        button { 
            background: #667eea; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 4px; 
            cursor: pointer; 
        }
        button:hover { background: #5a67d8; }
        .notification {
            background: #e3f2fd;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid #2196f3;
        }
        .notification.unread {
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Student Dashboard</h1>
        <div class="nav">
            <span>Welcome, {{ current_user.username }} ({{ current_user.experience_years }} years exp)</span>
            <a href="/logout">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <!-- Notifications -->
        {% if notifications %}
        <div class="card">
            <h2>📬 Notifications</h2>
            {% for notification in notifications %}
            <div class="notification {% if not notification.is_read %}unread{% endif %}">
                <strong>{{ notification.title }}</strong><br>
                {{ notification.message }}<br>
                <small>{{ notification.created_at[:16] }}</small>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <!-- Active Assignments -->
        <div class="card">
            <h2>My Assignments</h2>
            {% if assignments %}
                {% for assignment in assignments %}
                <div class="assignment-card">
                    <div class="assignment-header">
                        <div>
                            <h3>{{ assignment.title }}</h3>
                            <p>Topic: {{ assignment.topic }} | Due: {{ assignment.due_date[:10] }} | Points: {{ assignment.points }}</p>
                        </div>
                        <span class="badge badge-{{ assignment.status }}">{{ assignment.status }}</span>
                    </div>
                    
                    {% if show_questions and assignment.id == selected_assignment %}
                    <div class="questions-section">
                        <h4>Questions (15):</h4>
                        {% for question in assignment.questions %}
                        <div class="question">
                            <div class="question-number">Question {{ loop.index }}:</div>
                            {{ question }}
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <form method="GET" action="/student/dashboard">
                        <input type="hidden" name="show" value="{{ assignment.id }}">
                        <button type="submit">View Questions</button>
                    </form>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
            <p>No assignments yet. Check back later!</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = users_store.get(username)
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            error = 'Invalid username or password'
    
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('student_dashboard'))
    
    # Get statistics
    engineers = [User(u) for u in users_store.values() if not u.get('is_admin', False)]
    assignments = sorted(assignments_store.values(), key=lambda x: x['created_date'], reverse=True)[:10]
    
    total_assignments = len(assignments_store)
    pending_assignments = sum(1 for a in assignments_store.values() if a['status'] == 'pending')
    
    message = request.args.get('message')
    
    return render_template_string(
        ADMIN_DASHBOARD_TEMPLATE,
        current_user=current_user,
        engineers=engineers,
        total_engineers=len(engineers),
        total_assignments=total_assignments,
        pending_assignments=pending_assignments,
        assignments=assignments,
        message=message
    )

@app.route('/admin/create-assignment', methods=['POST'])
@login_required
def admin_create_assignment():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    engineer_id = request.form.get('engineer_id')
    topic = request.form.get('topic')
    
    ifpp.run(host='0.0.0.0', port=port, debug=False)
