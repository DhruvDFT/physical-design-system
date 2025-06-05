# app.py - Physical Design Interview System (Clean Version)
import os
import random
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
import logging

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage
assignments_store = {}
assignment_counter = 0

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Physical Design Interview System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; text-align: center; }
        .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #45a049; }
        .message { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Physical Design Interview System</h1>
        
        <div class="card">
            <h2>Create New Assignment</h2>
            <div id="message"></div>
            <form id="createForm">
                <div class="form-group">
                    <label>Engineer ID:</label>
                    <input type="text" id="engineerId" required>
                </div>
                <div class="form-group">
                    <label>Topic:</label>
                    <select id="topic" required>
                        <option value="">Select topic</option>
                        <option value="floorplanning">Floorplanning</option>
                        <option value="placement">Placement</option>
                        <option value="routing">Routing</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Experience Years:</label>
                    <select id="experience" required>
                        <option value="3">3-4 Years</option>
                        <option value="5">5-7 Years</option>
                        <option value="8">8+ Years</option>
                    </select>
                </div>
                <button type="submit">Create Assignment</button>
            </form>
        </div>
        
        <div class="card">
            <h2>API Endpoints</h2>
            <ul>
                <li>POST /api/assignments/create - Create assignment</li>
                <li>GET /api/assignments - List assignments</li>
                <li>GET /api/questions/{topic} - Get sample questions</li>
                <li>GET /api/analytics - View analytics</li>
            </ul>
        </div>
    </div>
    
    <script>
        document.getElementById('createForm').onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                engineer_id: document.getElementById('engineerId').value,
                topic: document.getElementById('topic').value,
                experience_years: parseInt(document.getElementById('experience').value)
            };
            
            try {
                const response = await fetch('/api/assignments/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                const msg = document.getElementById('message');
                if (result.success) {
                    msg.className = 'message success';
                    msg.textContent = 'Assignment created successfully!';
                    e.target.reset();
                } else {
                    msg.className = 'message error';
                    msg.textContent = result.error || 'Failed to create assignment';
                }
            } catch (error) {
                document.getElementById('message').className = 'message error';
                document.getElementById('message').textContent = 'Error: ' + error.message;
            }
        };
    </script>
</body>
</html>
"""

# Question Data
QUESTIONS = {
    "floorplanning": [
        "You have a 5mm x 5mm die with 4 hard macros. Describe your placement strategy.",
        "Your design has timing violations. How would you reorganize the floorplan?",
        "Design has 2 voltage domains. Plan floorplan to minimize level shifters.",
        "Routing congestion in center. What techniques would you use?",
        "3 clock domains at different frequencies. How to minimize skew?",
        "Place 8 memory instances optimally. What factors to consider?",
        "IR drop violations detected. Describe your fix approach.",
        "Reduce die area by 10%. What modifications would you make?",
        "Mixed-signal blocks need isolation. How to handle placement?",
        "How to estimate routing congestion early?",
        "Hierarchical design approach for 3 major blocks?",
        "DFT impact on floorplan decisions?",
        "Power gating techniques for sensitive design?",
        "Planning for late ECOs - what flexibility needed?",
        "Floorplan validation methodology?"
    ],
    "placement": [
        "Fix timing violations on 20 paths with -50ps slack.",
        "Routing congestion hotspots after placement. Solutions?",
        "Handle high-fanout nets (>500) during placement.",
        "Global vs detailed placement - when to use each?",
        "Reduce leakage power through placement techniques.",
        "Multi-voltage design placement strategy?",
        "Fix hold violations without affecting setup timing.",
        "Identify and fix long route issues during placement.",
        "Clock gating cell placement strategy?",
        "Placement for high-performance and low-power modes?",
        "Fix uneven cell density distribution.",
        "Multi-corner optimization approach?",
        "Place redundant logic for reliability.",
        "Balance area vs timing in placement.",
        "Placement impact on signal integrity?"
    ],
    "routing": [
        "Resolve 500 DRC violations systematically.",
        "Route 10 differential pairs maintaining impedance.",
        "Fix timing degradation after detailed routing.",
        "Achieve 100% routing with congestion issues.",
        "Power/ground routing for low IR drop.",
        "Handle layer-specific routing constraints.",
        "Minimize crosstalk on critical nets.",
        "Clock routing for controlled skew.",
        "Fix electromigration violations.",
        "Double patterning routing challenges.",
        "Prevent antenna violations during routing.",
        "ECO routing with minimal disruption.",
        "Control routing parasitics for timing.",
        "7nm/5nm specific routing challenges?",
        "Routing verification methodology?"
    ]
}

# Routes
@app.route('/')
def index():
    """Serve web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({"status": "healthy", "time": datetime.now().isoformat()})

@app.route('/api')
def api_info():
    """API information"""
    return jsonify({
        "name": "Physical Design Interview System",
        "version": "1.0",
        "topics": list(QUESTIONS.keys()),
        "total_questions": sum(len(q) for q in QUESTIONS.values())
    })

@app.route('/api/assignments/create', methods=['POST'])
def create_assignment():
    """Create new assignment"""
    try:
        data = request.get_json()
        engineer_id = data.get('engineer_id', 'eng001')
        topic = data.get('topic', 'floorplanning')
        experience = data.get('experience_years', 3)
        
        if topic not in QUESTIONS:
            return jsonify({"success": False, "error": "Invalid topic"}), 400
        
        # Get questions
        questions = random.sample(QUESTIONS[topic], min(15, len(QUESTIONS[topic])))
        
        # Create assignment
        global assignment_counter
        assignment_counter += 1
        assignment_id = f"PD_{topic}_{assignment_counter}_{datetime.now().strftime('%Y%m%d')}"
        
        points = 150 if experience < 5 else (175 if experience < 8 else 200)
        due_days = 10 if experience < 5 else (14 if experience < 8 else 21)
        
        assignment = {
            'id': assignment_id,
            'engineer_id': engineer_id,
            'topic': topic,
            'questions': questions,
            'points': points,
            'due_date': (datetime.now() + timedelta(days=due_days)).isoformat(),
            'created': datetime.now().isoformat(),
            'status': 'active'
        }
        
        assignments_store[assignment_id] = assignment
        
        return jsonify({
            "success": True,
            "assignment_id": assignment_id,
            "points": points,
            "due_date": assignment['due_date']
        })
        
    except Exception as e:
        logger.error(f"Error creating assignment: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/assignments')
def list_assignments():
    """List all assignments"""
    try:
        assignments = list(assignments_store.values())
        return jsonify({
            "success": True,
            "count": len(assignments),
            "assignments": [{
                'id': a['id'],
                'engineer_id': a['engineer_id'],
                'topic': a['topic'],
                'status': a['status'],
                'created': a['created']
            } for a in assignments]
        })
    except Exception as e:
        logger.error(f"Error listing assignments: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/questions/<topic>')
def get_questions(topic):
    """Get sample questions"""
    if topic not in QUESTIONS:
        return jsonify({"success": False, "error": "Invalid topic"}), 400
    
    sample = random.sample(QUESTIONS[topic], min(5, len(QUESTIONS[topic])))
    return jsonify({
        "success": True,
        "topic": topic,
        "sample_questions": sample,
        "total_available": len(QUESTIONS[topic])
    })

@app.route('/api/analytics')
def analytics():
    """Get analytics"""
    by_topic = {}
    for a in assignments_store.values():
        topic = a['topic']
        by_topic[topic] = by_topic.get(topic, 0) + 1
    
    return jsonify({
        "success": True,
        "total_assignments": len(assignments_store),
        "by_topic": by_topic,
        "timestamp": datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
