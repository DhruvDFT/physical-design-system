# app.py - Physical Design Interview System (Fixed Version)
import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pd-secret-2024')

# In-memory storage
users = {}
assignments = {}
notifications = {}
assignment_counter = 0

# Initialize default users
def init_users():
    # Admin
    users['admin'] = {
        'id': 'admin',
        'username': 'admin',
        'password': generate_password_hash('admin123'),
        'is_admin': True,
        'experience_years': 3  # Fixed to 3 years
    }
    
    # Students - all with 3 years experience
    for i in range(1, 4):
        user_id = f'eng00{i}'
        users[user_id] = {
            'id': user_id,
            'username': user_id,
            'password': generate_password_hash('password123'),
            'is_admin': False,
            'experience_years': 3  # Fixed to 3 years
        }

# All 45 Questions (15 per topic) - 3+ Years Experience Only
QUESTIONS = {
    "floorplanning": [
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

# Helper functions
def create_assignment(engineer_id, topic):
    global assignment_counter
    
    user = users.get(engineer_id)
    if not user or topic not in QUESTIONS:
        return None
    
    # Fixed parameters for 3 years experience
    difficulty = "3+ Years"
    points = 150
    due_days = 3  # Changed from 10 to 3 days for refresh
    
    assignment_counter += 1
    assignment_id = f"PD_{topic.upper()}_{engineer_id}_{assignment_counter}"
    
    assignment = {
        'id': assignment_id,
        'engineer_id': engineer_id,
        'topic': topic,
        'questions': QUESTIONS[topic],  # All 15 questions
        'answers': {},  # New: Store answers
        'difficulty': difficulty,
        'points': points,
        'status': 'pending',
        'created_date': datetime.now().isoformat(),
        'due_date': (datetime.now() + timedelta(days=due_days)).isoformat(),
        'score': None,  # New: Admin scoring
        'scored_by': None,
        'scored_date': None
    }
    
    assignments[assignment_id] = assignment
    
    # Create notification
    if engineer_id not in notifications:
        notifications[engineer_id] = []
    
    notifications[engineer_id].append({
        'title': f'New {topic} Assignment',
        'message': f'15 questions for 3+ years experience, due in {due_days} days',
        'created_at': datetime.now().isoformat()
    })
    
    return assignment

def auto_refresh_assignments():
    """Auto-refresh assignments after 3 days"""
    refreshed = 0
    for assignment_id, assignment in list(assignments.items()):
        due_date = datetime.fromisoformat(assignment['due_date'])
        if datetime.now() > due_date and assignment['status'] != 'refreshed':
            # Create new assignment
            new_assignment = create_assignment(assignment['engineer_id'], assignment['topic'])
            if new_assignment:
                assignment['status'] = 'refreshed'
                refreshed += 1
    return refreshed

# HTML Templates
def get_base_html():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PD Interview System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }
            .header { background: #4CAF50; color: white; padding: 20px; }
            .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
            .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            textarea { min-height: 100px; resize: vertical; }
            button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #45a049; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f5f5f5; }
            .question { background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }
            .answer-box { margin-top: 10px; }
            .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
            .badge-pending { background: #FFC107; color: #333; }
            .badge-submitted { background: #2196F3; color: white; }
            .badge-scored { background: #4CAF50; color: white; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
            .stat { text-align: center; }
            .stat h2 { margin: 0; color: #4CAF50; }
            .error { color: red; }
            .success { color: green; }
            .score-input { width: 60px; }
        </style>
    </head>
    <body>
    '''

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        if session.get('is_admin'):
            return redirect('/admin')
        else:
            return redirect('/student')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users.get(username)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user.get('is_admin', False)
            session['experience_years'] = 3  # Fixed to 3 years
            
            if user.get('is_admin'):
                return redirect('/admin')
            else:
                return redirect('/student')
        else:
            error = 'Invalid credentials'
    
    html = get_base_html() + f'''
        <div style="max-width: 400px; margin: 100px auto;">
            <div class="card">
                <h1 style="text-align: center;">Physical Design Interview System</h1>
                <p style="text-align: center; color: #666;">3+ Years Experience Questions</p>
                <p style="background: #e3f2fd; padding: 10px; border-radius: 4px;">
                    <strong>Demo Credentials:</strong><br>
                    Admin: admin / admin123<br>
                    Student: eng001 / password123
                </p>
                {f'<p class="error">{error}</p>' if error else ''}
                <form method="POST">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" style="width: 100%;">Login</button>
                </form>
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
    pending_review = [a for a in all_assignments if a.get('answers') and len(a['answers']) == 15 and not a.get('score')]
    
    html = get_base_html() + f'''
        <div class="header">
            <h1>Admin Dashboard - {session["username"]} <a href="/logout" style="float: right; color: white;">Logout</a></h1>
        </div>
        
        <div class="container">
            <div class="stats">
                <div class="stat card">
                    <h2>{len(engineers)}</h2>
                    <p>Engineers</p>
                </div>
                <div class="stat card">
                    <h2>{len(assignments)}</h2>
                    <p>Assignments</p>
                </div>
                <div class="stat card">
                    <h2>{len(pending_review)}</h2>
                    <p>Pending Review</p>
                </div>
                <div class="stat card">
                    <h2>45</h2>
                    <p>Questions (3+ Years)</p>
                </div>
            </div>
            
            <div class="card">
                <h2>Create Assignment</h2>
                <form method="POST" action="/admin/create">
                    <div class="form-group">
                        <label>Engineer</label>
                        <select name="engineer_id" required>
                            <option value="">Select...</option>
    '''
    
    for eng in engineers:
        html += f'<option value="{eng["id"]}">{eng["username"]} (3+ years)</option>'
    
    html += '''
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Topic</label>
                        <select name="topic" required>
                            <option value="">Select...</option>
                            <option value="floorplanning">Floorplanning</option>
                            <option value="placement">Placement</option>
                            <option value="routing">Routing</option>
                        </select>
                    </div>
                    <button type="submit">Create Assignment</button>
                    <button type="button" onclick="refreshAssignments()">Refresh Expired (3+ days)</button>
                </form>
            </div>
            
            <div class="card">
                <h2>Assignments Pending Review</h2>
    '''
    
    if pending_review:
        for a in pending_review:
            html += f'''
                <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
                    <h4>{a["id"]} - {a["engineer_id"]} - {a["topic"].title()}</h4>
                    <p>Submitted: {len(a.get("answers", {}))} / 15 answers</p>
                    <a href="/admin/review/{a["id"]}"><button>Review & Score</button></a>
                </div>
            '''
    else:
        html += '<p>No assignments pending review</p>'
    
    html += '''
            </div>
            
            <div class="card">
                <h2>All Assignments</h2>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Engineer</th>
                        <th>Topic</th>
                        <th>Status</th>
                        <th>Answers</th>
                        <th>Score</th>
                    </tr>
    '''
    
    for a in all_assignments[-20:]:  # Last 20
        answers_count = len(a.get('answers', {}))
        status = 'scored' if a.get('score') is not None else ('submitted' if answers_count == 15 else a['status'])
        html += f'''
            <tr>
                <td>{a["id"]}</td>
                <td>{a["engineer_id"]}</td>
                <td>{a["topic"]}</td>
                <td><span class="badge badge-{status}">{status}</span></td>
                <td>{answers_count}/15</td>
                <td>{a.get("score", "-")}/150</td>
            </tr>
        '''
    
    html += '''
                </table>
            </div>
        </div>
        
        <script>
        function refreshAssignments() {
            fetch('/admin/refresh', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    alert('Refreshed ' + data.count + ' assignments');
                    location.reload();
                });
        }
        </script>
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

@app.route('/admin/refresh', methods=['POST'])
def admin_refresh():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    count = auto_refresh_assignments()
    return jsonify({'count': count})

@app.route('/admin/review/<assignment_id>', methods=['GET', 'POST'])
def admin_review(assignment_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')
    
    assignment = assignments.get(assignment_id)
    if not assignment:
        return redirect('/admin')
    
    if request.method == 'POST':
        # Save scores
        total_score = 0
        for i in range(15):
            score = request.form.get(f'score_{i}', '0')
            try:
                total_score += int(score)
            except:
                pass
        
        assignment['score'] = total_score
        assignment['scored_by'] = session['username']
        assignment['scored_date'] = datetime.now().isoformat()
        
        return redirect('/admin')
    
    # Show review form
    html = get_base_html() + f'''
        <div class="header">
            <h1>Review Assignment - {assignment_id}</h1>
        </div>
        
        <div class="container">
            <div class="card">
                <h3>Engineer: {assignment["engineer_id"]} | Topic: {assignment["topic"].title()}</h3>
                <form method="POST">
    '''
    
    for i, question in enumerate(assignment['questions']):
        answer = assignment.get('answers', {}).get(str(i), 'No answer provided')
        html += f'''
            <div class="question">
                <strong>Q{i+1}:</strong> {question}
                <div class="answer-box">
                    <strong>Answer:</strong><br>
                    <div style="background: white; padding: 10px; border: 1px solid #ddd; margin: 10px 0;">
                        {answer}
                    </div>
                    <label>Score (0-10):</label>
                    <input type="number" name="score_{i}" class="score-input" min="0" max="10" value="0">
                </div>
            </div>
        '''
    
    html += '''
                    <button type="submit" style="margin-top: 20px;">Submit Scores</button>
                    <a href="/admin"><button type="button">Cancel</button></a>
                </form>
            </div>
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
    my_assignments = [a for a in assignments.values() if a['engineer_id'] == user_id]
    my_notifications = notifications.get(user_id, [])[-5:]
    
    html = get_base_html() + f'''
        <div class="header">
            <h1>Student Dashboard - {session["username"]} (3+ years) <a href="/logout" style="float: right; color: white;">Logout</a></h1>
        </div>
        
        <div class="container">
    '''
    
    if my_notifications:
        html += '<div class="card"><h2>Notifications</h2>'
        for n in my_notifications:
            html += f'<p><strong>{n["title"]}</strong><br>{n["message"]}<br><small>{n["created_at"][:16]}</small></p>'
        html += '</div>'
    
    html += '<h2>My Assignments</h2>'
    
    if my_assignments:
        for a in my_assignments:
            status = 'scored' if a.get('score') is not None else ('submitted' if len(a.get('answers', {})) == 15 else a['status'])
            html += f'''
                <div class="card">
                    <h3>{a["topic"].title()} Assignment 
                        <span class="badge badge-{status}">{status}</span>
                    </h3>
                    <p>Points: {a["points"]} | Due: {a["due_date"][:10]}</p>
            '''
            
            if a.get('score') is not None:
                html += f'<p><strong>Score: {a["score"]}/150</strong> (Scored by: {a.get("scored_by", "Admin")})</p>'
            
            if status != 'scored':
                html += f'<a href="/student/assignment/{a["id"]}"><button>Answer Questions</button></a>'
            else:
                html += f'<a href="/student/assignment/{a["id"]}"><button>View Submission</button></a>'
            
            html += '</div>'
    else:
        html += '<div class="card"><p>No assignments yet.</p></div>'
    
    html += '''
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
    
    if request.method == 'POST' and not assignment.get('score'):
        # Save answers
        answers = {}
        for i in range(15):
            answer = request.form.get(f'answer_{i}', '').strip()
            if answer:
                answers[str(i)] = answer
        
        assignment['answers'] = answers
        return redirect('/student')
    
    # Show assignment
    html = get_base_html() + f'''
        <div class="header">
            <h1>{assignment["topic"].title()} Assignment - {assignment_id}</h1>
        </div>
        
        <div class="container">
            <div class="card">
                <p>Due: {assignment["due_date"][:10]} | Points: {assignment["points"]}</p>
    '''
    
    if assignment.get('score') is not None:
        html += f'<p><strong>Score: {assignment["score"]}/150</strong></p>'
    
    html += '<form method="POST">'
    
    for i, question in enumerate(assignment['questions']):
        existing_answer = assignment.get('answers', {}).get(str(i), '')
        disabled = 'disabled' if assignment.get('score') is not None else ''
        
        html += f'''
            <div class="question">
                <strong>Q{i+1}:</strong> {question}
                <div class="answer-box">
                    <textarea name="answer_{i}" placeholder="Type your answer here..." {disabled}>{existing_answer}</textarea>
                </div>
            </div>
        '''
    
    if assignment.get('score') is None:
        html += '<button type="submit" style="margin-top: 20px;">Submit All Answers</button>'
    
    html += '''
                    <a href="/student"><button type="button">Back to Dashboard</button></a>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'users': len(users), 'assignments': len(assignments)})

# Initialize
init_users()

# Create demo assignments
if len(assignments) == 0:
    create_assignment('eng001', 'floorplanning')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) techniques would you use to reduce power while maintaining timing?",
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

# Helper functions
def create_assignment(engineer_id, topic):
    global assignment_counter
    
    user = users.get(engineer_id)
    if not user or topic not in QUESTIONS:
        return None
    
    experience = user.get('experience_years', 3)
    
    # Determine difficulty (original logic)
    if experience >= 8:
        difficulty = "Expert"
        points = 200
        due_days = 21
    elif experience >= 5:
        difficulty = "Advanced"
        points = 175
        due_days = 14
    else:
        difficulty = "Intermediate"
        points = 150
        due_days = 10
    
    assignment_counter += 1
    assignment_id = f"PD_{topic.upper()}_{engineer_id}_{assignment_counter}"
    
    assignment = {
        'id': assignment_id,
        'engineer_id': engineer_id,
        'topic': topic,
        'questions': QUESTIONS[topic],  # All 15 questions
        'difficulty': difficulty,
        'points': points,
        'status': 'pending',
        'created_date': datetime.now().isoformat(),
        'due_date': (datetime.now() + timedelta(days=due_days)).isoformat()
    }
    
    assignments[assignment_id] = assignment
    
    # Create notification
    if engineer_id not in notifications:
        notifications[engineer_id] = []
    
    notifications[engineer_id].append({
        'title': f'New {topic} Assignment',
        'message': f'{difficulty} level - {len(QUESTIONS[topic])} questions, due in {due_days} days',
        'created_at': datetime.now().isoformat()
    })
    
    return assignment

# HTML Templates
def get_base_html():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PD Interview System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }
            .header { background: #4CAF50; color: white; padding: 20px; }
            .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
            .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #45a049; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f5f5f5; }
            .question { background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }
            .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
            .badge-intermediate { background: #2196F3; color: white; }
            .badge-advanced { background: #9C27B0; color: white; }
            .badge-expert { background: #F44336; color: white; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
            .stat { text-align: center; }
            .stat h2 { margin: 0; color: #4CAF50; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
    '''

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        if session.get('is_admin'):
            return redirect('/admin')
        else:
            return redirect('/student')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users.get(username)
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
            error = 'Invalid credentials'
    
    html = get_base_html() + f'''
        <div style="max-width: 400px; margin: 100px auto;">
            <div class="card">
                <h1 style="text-align: center;">Physical Design Interview System</h1>
                <p style="background: #e3f2fd; padding: 10px; border-radius: 4px;">
                    <strong>Demo Credentials:</strong><br>
                    Admin: admin / admin123<br>
                    Student: eng001 / password123
                </p>
                {f'<p class="error">{error}</p>' if error else ''}
                <form method="POST">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" style="width: 100%;">Login</button>
                </form>
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
    recent_assignments = list(assignments.values())[-10:][::-1]
    
    html = get_base_html() + f'''
        <div class="header">
            <h1>Admin Dashboard - {session["username"]} <a href="/logout" style="float: right; color: white;">Logout</a></h1>
        </div>
        
        <div class="container">
            <div class="stats">
                <div class="stat card">
                    <h2>{len(engineers)}</h2>
                    <p>Engineers</p>
                </div>
                <div class="stat card">
                    <h2>{len(assignments)}</h2>
                    <p>Assignments</p>
                </div>
                <div class="stat card">
                    <h2>{sum(1 for a in assignments.values() if a["status"] == "pending")}</h2>
                    <p>Pending</p>
                </div>
                <div class="stat card">
                    <h2>45</h2>
                    <p>Questions</p>
                </div>
            </div>
            
            <div class="card">
                <h2>Create Assignment</h2>
                <form method="POST" action="/admin/create">
                    <div class="form-group">
                        <label>Engineer</label>
                        <select name="engineer_id" required>
                            <option value="">Select...</option>
    '''
    
    for eng in engineers:
        html += f'<option value="{eng["id"]}">{eng["username"]} ({eng["experience_years"]} years)</option>'
    
    html += '''
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Topic</label>
                        <select name="topic" required>
                            <option value="">Select...</option>
                            <option value="floorplanning">Floorplanning</option>
                            <option value="placement">Placement</option>
                            <option value="routing">Routing</option>
                        </select>
                    </div>
                    <button type="submit">Create Assignment</button>
                </form>
            </div>
            
            <div class="card">
                <h2>Recent Assignments</h2>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Engineer</th>
                        <th>Topic</th>
                        <th>Difficulty</th>
                        <th>Points</th>
                        <th>Status</th>
                    </tr>
    '''
    
    for a in recent_assignments:
        html += f'''
            <tr>
                <td>{a["id"]}</td>
                <td>{a["engineer_id"]}</td>
                <td>{a["topic"]}</td>
                <td><span class="badge badge-{a["difficulty"].lower()}">{a["difficulty"]}</span></td>
                <td>{a["points"]}</td>
                <td>{a["status"]}</td>
            </tr>
        '''
    
    html += '''
                </table>
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

@app.route('/student')
def student_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    my_assignments = [a for a in assignments.values() if a['engineer_id'] == user_id]
    my_notifications = notifications.get(user_id, [])[-5:]
    
    html = get_base_html() + f'''
        <div class="header">
            <h1>Student Dashboard - {session["username"]} ({session["experience_years"]} years) <a href="/logout" style="float: right; color: white;">Logout</a></h1>
        </div>
        
        <div class="container">
    '''
    
    if my_notifications:
        html += '<div class="card"><h2>Notifications</h2>'
        for n in my_notifications:
            html += f'<p><strong>{n["title"]}</strong><br>{n["message"]}<br><small>{n["created_at"][:16]}</small></p>'
        html += '</div>'
    
    html += '<h2>My Assignments</h2>'
    
    if my_assignments:
        for a in my_assignments:
            html += f'''
                <div class="card">
                    <h3>{a["topic"].title()} Assignment 
                        <span class="badge badge-{a["difficulty"].lower()}">{a["difficulty"]}</span>
                    </h3>
                    <p>Points: {a["points"]} | Due: {a["due_date"][:10]} | Status: {a["status"]}</p>
                    <h4>Questions (15):</h4>
            '''
            
            for i, q in enumerate(a['questions'], 1):
                html += f'<div class="question"><strong>Q{i}:</strong> {q}</div>'
            
            html += '</div>'
    else:
        html += '<div class="card"><p>No assignments yet.</p></div>'
    
    html += '''
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'users': len(users), 'assignments': len(assignments)})

# Initialize
init_users()

# Create demo assignments
if len(assignments) == 0:
    create_assignment('eng001', 'floorplanning')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
