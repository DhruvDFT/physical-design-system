# Routes
@app.route('/')
def index():
    """Serve the web interface"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Physical Design Interview System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 0; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 40px; }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { font-size: 1.2em; opacity: 0.9; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .card { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: transform 0.3s ease, box-shadow 0.3s ease; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 5px 20px rgba(0,0,0,0.15); }
        .card h2 { color: #667eea; margin-bottom: 15px; font-size: 1.5em; }
        .stats { display: flex; justify-content: space-between; margin-top: 20px; }
        .stat { text-align: center; padding: 10px; }
        .stat-value { font-size: 2em; font-weight: bold; color: #667eea; }
        .stat-label { font-size: 0.9em; color: #666; margin-top: 5px; }
        .form-section { background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 40px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: 600; color: #555; }
        input, select { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 16px; transition: border-color 0.3s ease; }
        input:focus, select:focus { outline: none; border-color: #667eea; }
        button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 30px; border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer; transition: transform 0.2s ease; }
        button:hover { transform: scale(1.05); }
        button:active { transform: scale(0.98); }
        .assignments-list { background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .assignment-item { border-bottom: 1px solid #eee; padding: 20px 0; display: flex; justify-content: space-between; align-items: center; }
        .assignment-item:last-child { border-bottom: none; }
        .assignment-info h3 { color: #333; margin-bottom: 5px; }
        .assignment-meta { color: #666; font-size: 0.9em; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600; }
        .badge-intermediate { background: #e3f2fd; color: #1976d2; }
        .badge-advanced { background: #f3e5f5; color: #7b1fa2; }
        .badge-expert { background: #ffebee; color: #c62828; }
        .loading { text-align: center; padding: 40px; color: #666; }
        .error { background: #ffebee; color: #c62828; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .success { background: #e8f5e9; color: #2e7d32; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .topic-icon { width: 50px; height: 50px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 15px; }
        .icon-floorplanning { background: #e3f2fd; color: #1976d2; }
        .icon-placement { background: #f3e5f5; color: #7b1fa2; }
        .icon-routing { background: #e8f5e9; color: #388e3c; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; }
        .modal-content { background: white; border-radius: 10px; padding: 30px; max-width: 600px; margin: 50px auto; max-height: 80vh; overflow-y: auto; }
        .questions-list { margin-top: 20px; }
        .question { background: #f5f7fa; padding: 15px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #667eea; }
        .close-modal { float: right; font-size: 28px; font-weight: bold; cursor: pointer; color: #999; }
        .close-modal:hover { color: #333; }
    </style>
</head>
<body>
    <header>
        <h1>🎯 Physical Design Interview System</h1>
        <p class="subtitle">Comprehensive Assessment Platform for VLSI Engineers</p>
    </header>
    <div class="container">
        <div class="dashboard">
            <div class="card">
                <div class="topic-icon icon-floorplanning">📐</div>
                <h2>Floorplanning</h2>
                <p>Master the art of chip floorplanning with practical scenarios</p>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">25</div>
                        <div class="stat-label">Questions</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">3</div>
                        <div class="stat-label">Levels</div>
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="topic-icon icon-placement">🎲</div>
                <h2>Placement</h2>
                <p>Optimize cell placement for timing, power, and area</p>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">25</div>
                        <div class="stat-label">Questions</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">3</div>
                        <div class="stat-label">Levels</div>
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="topic-icon icon-routing">🔌</div>
                <h2>Routing</h2>
                <p>Master routing techniques and timing closure strategies</p>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">25</div>
                        <div class="stat-label">Questions</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">3</div>
                        <div class="stat-label">Levels</div>
                    </div>
                </div>
            </div>
        </div>
        <div class="form-section">
            <h2>Create New Assignment</h2>
            <div id="message"></div>
            <form id="createAssignmentForm">
                <div class="form-group">
                    <label for="engineerId">Engineer ID</label>
                    <input type="text" id="engineerId" name="engineerId" placeholder="e.g., eng001" required>
                </div>
                <div class="form-group">
                    <label for="topic">Topic</label>
                    <select id="topic" name="topic" required>
                        <option value="">Select a topic</option>
                        <option value="floorplanning">Floorplanning</option>
                        <option value="placement">Placement</option>
                        <option value="routing">Routing</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="experience">Experience Level (Years)</label>
                    <select id="experience" name="experience" required>
                        <option value="3">3-4 Years (Intermediate)</option>
                        <option value="5">5-7 Years (Advanced)</option>
                        <option value="8">8+ Years (Expert)</option>
                    </select>
                </div>
                <button type="submit">Create Assignment</button>
                <button type="button" onclick="viewSampleQuestions()" style="margin-left: 10px; background: linear-gradient(135deg, #42a5f5 0%, #1e88e5 100%);">View Sample Questions</button>
            </form>
        </div>
        <div class="assignments-list">
            <h2>Recent Assignments</h2>
            <button onclick="refreshAssignments()" style="float: right; margin-top: -40px;">🔄 Refresh Expired</button>
            <div id="assignmentsList" class="loading">Loading assignments...</div>
        </div>
    </div>
    <div id="questionModal" class="modal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal()">&times;</span>
            <h2 id="modalTitle">Sample Questions</h2>
            <div id="modalContent"></div>
        </div>
    </div>
    <script>
        const API_BASE_URL = window.location.origin;
        document.addEventListener("DOMContentLoaded", function() { loadAssignments(); });
        document.getElementById("createAssignmentForm").addEventListener("submit", async function(e) {
            e.preventDefault();
            const formData = {
                engineer_id: document.getElementById("engineerId").value,
                topic: document.getElementById("topic").value,
                experience_years: parseInt(document.getElementById("experience").value)
            };
            try {
                const response = await fetch(API_BASE_URL + "/api/assignments/create", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(formData)
                });
                const data = await response.json();
                if (data.success) {
                    showMessage("success", "Assignment created successfully! ID: " + data.assignment.id);
                    document.getElementById("createAssignmentForm").reset();
                    loadAssignments();
                } else {
                    showMessage("error", data.error || "Failed to create assignment");
                }
            } catch (error) {
                showMessage("error", "Error: " + error.message);
            }
        });
        async function loadAssignments() {
            try {
                const response = await fetch(API_BASE_URL + "/api/assignments");
                const data = await response.json();
                if (data.success) displayAssignments(data.assignments);
            } catch (error) {
                document.getElementById("assignmentsList").innerHTML = "<p class=error>Failed to load assignments</p>";
            }
        }
        function displayAssignments(assignments) {
            const container = document.getElementById("assignmentsList");
            if (assignments.length === 0) {
                container.innerHTML = "<p>No assignments found. Create one above!</p>";
                return;
            }
            container.innerHTML = assignments.map(assignment => {
                const dueDate = new Date(assignment.due_date);
                const difficulty = getDifficultyFromPoints(assignment.points);
                return "<div class=assignment-item><div class=assignment-info><h3>" + assignment.title + "</h3><div class=assignment-meta>Engineer: " + assignment.engineer_id + " | Due: " + dueDate.toLocaleDateString() + " | Points: " + assignment.points + "</div></div><div><span class=badge\\ badge-" + difficulty.toLowerCase() + ">" + difficulty + "</span><button onclick=viewAssignment('" + assignment.id + "') style='margin-left:10px;padding:8px 20px'>View</button></div></div>";
            }).join("");
        }
        async function viewAssignment(assignmentId) {
            try {
                const response = await fetch(API_BASE_URL + "/api/assignments/" + assignmentId);
                const data = await response.json();
                if (data.success) {
                    const assignment = data.assignment;
                    const questions = assignment.questions;
                    document.getElementById("modalTitle").textContent = assignment.title;
                    document.getElementById("modalContent").innerHTML = "<p><strong>Engineer:</strong> " + assignment.engineer_id + "</p><p><strong>Due Date:</strong> " + new Date(assignment.due_date).toLocaleDateString() + "</p><p><strong>Points:</strong> " + assignment.points + "</p><div class=questions-list><h3>Questions:</h3>" + questions.map((q, i) => "<div class=question><strong>Q" + (i + 1) + ":</strong> " + q + "</div>").join("") + "</div>";
                    document.getElementById("questionModal").style.display = "block";
                }
            } catch (error) {
                showMessage("error", "Failed to load assignment details");
            }
        }
        async function viewSampleQuestions() {
            const topic = document.getElementById("topic").value;
            if (!topic) {
                showMessage("error", "Please select a topic first");
                return;
            }
            try {
                const response = await fetch(API_BASE_URL + "/api/questions/" + topic);
                const data = await response.json();
                if (data.success) {
                    document.getElementById("modalTitle").textContent = "Sample Questions: " + topic.charAt(0).toUpperCase() + topic.slice(1);
                    document.getElementById("modalContent").innerHTML = "<div class=questions-list>" + data.sample_questions.map((q, i) => "<div class=question><strong>Sample " + (i + 1) + ":</strong> " + q + "</div>").join("") + "</div><p style='margin-top:20px;color:#666'>These are 5 sample questions from a pool of " + data.total_available + " questions.</p>";
                    document.getElementById("questionModal").style.display = "block";
                }
            } catch (error) {
                showMessage("error", "Failed to load sample questions");
            }
        }
        async function refreshAssignments() {
            try {
                const response = await fetch(API_BASE_URL + "/api/assignments/refresh", { method: "POST" });
                const data = await response.json();
                if (data.success) {
                    showMessage("success", data.message);
                    loadAssignments();
                }
            } catch (error) {
                showMessage("error", "Failed to refresh assignments");
            }
        }
        function closeModal() { document.getElementById("questionModal").style.display = "none"; }
        function showMessage(type, message) {
            const messageDiv = document.getElementById("message");
            messageDiv.className = type;
            messageDiv.textContent = message;
            setTimeout(() => { messageDiv.textContent = ""; messageDiv.className = ""; }, 5000);
        }
        function getDifficultyFromPoints(points) {
            if (points >= 200) return "Expert";
            if (points >= 175) return "Advanced";
            return "Intermediate";
        }
        window.onclick = function(event) {
            const modal = document.getElementById("questionModal");
            if (event.target == modal) modal.style.display = "none";
        }
    </script>
</body>
</html>'''

@app.route('/api')
def api_docs():
    """API documentation endpoint"""
    return jsonify({
        "message": "Physical Design Interview System API",
        "version": "1.0-simple",
        "status": "running",
        "endpoints": {
            "GET /": "Web interface",
            "GET /api": "This API documentation",
            "GET /health": "Health check",
            "POST /api/assignments/create": "Create new assignment",
            "GET /api/assignments": "List all assignments",
            "GET /api/assignments/<id>": "Get specific assignment",
            "GET /api/questions/<topic>": "Get sample questions for topic",
            "POST /api/assignments/refresh": "Refresh expired assignments",
            "GET /api/analytics": "Get system analytics"
        },
        "topics": ["floorplanning", "placement", "routing"],
        "timestamp": datetime.now().isoformat()
    })# app_simple.py - Physical Design Interview System (No Database Version)
# Simplified API that works without database setup

import os
import random
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import logging

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage (for demo purposes)
assignments_store = {}
assignment_counter = 0

# Question Data
PHYSICAL_DESIGN_TOPICS_3PLUS = {
    "floorplanning": {
        "title": "Physical Design: Floorplanning (3+ Years Experience)",
        "questions": [
            "You have a 5mm x 5mm die with 4 hard macros (each 1mm x 0.8mm) and need to achieve 70% utilization. Describe your macro placement strategy considering timing and power delivery.",
            "Your design has setup timing violations on paths crossing from left to right. The floorplan has macros placed randomly. How would you reorganize the floorplan to improve timing?",
            "You're working with a design that has 2 voltage domains (0.9V core, 1.2V IO). Explain how you would plan the floorplan to minimize level shifter count and power grid complexity.",
            "During floorplan, you notice routing congestion in the center region. What are 3 specific techniques you would use to reduce congestion without major timing impact?",
            "Your design has 3 clock domains running at 800MHz, 400MHz, and 100MHz. How would you approach floorplanning to minimize clock tree power and skew?",
            "You need to place 8 memory instances in your design. What factors would you consider for their placement?",
            "Your floorplan review shows IR drop violations in certain regions. Describe your approach to fix this.",
            "You're told to reduce die area by 10% while maintaining timing. What floorplan modifications would you make?",
            "Your design has mixed-signal blocks that need isolation from digital switching noise. How would you handle their placement?",
            "During early floorplan, how would you estimate routing congestion?",
            "You have a hierarchical design with 3 major blocks. Explain your approach to partition-level floorplanning.",
            "Your design requires scan chains for testing. How does DFT impact your floorplan decisions?",
            "You're working on a power-sensitive design. Describe floorplan techniques to enable effective power gating.",
            "Your floorplan needs to accommodate late ECOs. How would you plan for flexibility?",
            "Explain your methodology for floorplan validation."
        ]
    },
    "placement": {
        "title": "Physical Design: Placement Optimization (3+ Years Experience)",
        "questions": [
            "Your placement run shows timing violations on 20 critical paths with negative slack up to -50ps. Describe your systematic approach to fix these violations.",
            "You're seeing routing congestion hotspots after placement in 2-3 regions. What placement adjustments would you make?",
            "Your design has high-fanout nets (>500 fanout) causing placement issues. How would you handle these nets?",
            "Compare global placement vs detailed placement - what specific problems does each solve?",
            "Your placement shows leakage power higher than target. What placement techniques would you use to reduce power?",
            "You have a multi-voltage design with voltage islands. Describe your placement strategy for cells near domain boundaries.",
            "Your timing report shows hold violations scattered across the design. How would you address this through placement?",
            "During placement, you notice that certain instances are creating long routes. What tools help identify and fix such issues?",
            "Your design has clock gating cells. Explain their optimal placement strategy.",
            "You're working with a design that has both high-performance and low-power modes. How does this affect placement?",
            "Your placement review shows uneven cell density distribution. Why is this problematic?",
            "Describe your approach to placement optimization for designs with multiple timing corners.",
            "Your design has redundant logic for reliability. How would you place redundant instances?",
            "You need to optimize placement for both area and timing. Describe the trade-offs.",
            "Explain how placement impacts signal integrity."
        ]
    },
    "routing": {
        "title": "Physical Design: Routing and Timing Closure (3+ Years Experience)",
        "questions": [
            "After global routing, you have 500 DRC violations. Describe your systematic approach to resolve these.",
            "Your design has 10 differential pairs for high-speed signals. Explain your routing strategy.",
            "You're seeing timing degradation after detailed routing. What causes this and how would you recover?",
            "Your router is struggling with congestion leading to routing non-completion. What techniques would you use?",
            "Describe your approach to power/ground routing.",
            "Your design has specific layer constraints. How does this impact your routing strategy?",
            "You have crosstalk violations on critical nets. Explain your routing techniques to minimize crosstalk.",
            "Your clock nets require special routing with controlled skew. Describe clock routing methodology.",
            "During routing, some nets are showing electromigration violations. How would you address this?",
            "You need to route in a design with double patterning constraints. Explain the challenges.",
            "Your design has antenna violations after routing. What causes these?",
            "Describe your ECO routing strategy.",
            "Your timing closure requires specific net delays. How do you control routing parasitics?",
            "You're working with advanced technology nodes (7nm/5nm). What routing challenges are specific to these?",
            "Explain your routing verification methodology."
        ]
    }
}

# Advanced Question Data (5+ and 8+ years)
ADVANCED_QUESTIONS = {
    "floorplanning": {
        "senior": [  # 5+ years
            "Design a floorplan for a multi-die 2.5D package with 3 chiplets. Discuss TSV planning, thermal management, and inter-die timing optimization.",
            "Your project requires 15% area reduction from previous tapeout. Analyze floorplan optimization strategies and associated risks.",
            "Plan floorplan for automotive safety-critical design (ISO 26262). Address redundancy, fault isolation, and diagnostic coverage requirements.",
            "Design hierarchical floorplan for a 50M gate design. Discuss partition strategies, interface planning, and timing budgeting.",
            "Your design has 8 voltage domains with complex power management. Plan advanced power grid architecture and domain interactions."
        ],
        "expert": [  # 8+ years
            "Architect floorplan for breakthrough AI accelerator chip targeting 50x performance improvement. Consider novel architectures and thermal limits.",
            "Design floorplan for space-qualified processor with radiation hardening. Address SEU tolerance, latch-up prevention, and TID effects.",
            "Plan floorplan for next-generation automotive SoC with functional safety requirements. Design for ASIL-D certification.",
            "Architect system-in-package (SiP) floorplan with heterogeneous chiplets. Optimize for bandwidth, latency, and power efficiency.",
            "Design floorplan for quantum-classical hybrid processor. Address unique constraints and interface requirements."
        ]
    },
    "placement": {
        "senior": [  # 5+ years
            "Optimize placement for a 2GHz CPU core with <100ps timing margins. Discuss advanced timing optimization techniques.",
            "Design placement strategy for 3D IC with 4 tiers. Address thermal management, TSV planning, and inter-tier timing.",
            "Your design requires 40% power reduction while maintaining performance. Describe advanced low-power placement techniques.",
            "Implement placement for soft-error resilient design. Address SEU mitigation, spatial redundancy, and error detection.",
            "Optimize placement for yield improvement in 7nm technology. Discuss process variation impact and design margins."
        ],
        "expert": [  # 8+ years
            "Design placement methodology for neuromorphic processor with non-traditional architectures. Address novel optimization objectives.",
            "Implement placement for cryogenic computing applications. Consider unique electrical behavior at low temperatures.",
            "Optimize placement for photonic-electronic integrated circuits. Address optical-electrical interfaces and thermal management.",
            "Design placement for security processor with hardware-based countermeasures. Implement protection against physical attacks.",
            "Architect placement for edge AI chip with extreme power constraints (<1mW). Push boundaries of energy efficiency."
        ]
    },
    "routing": {
        "senior": [  # 5+ years
            "Design routing solution for 100+ differential pairs in high-speed SerDes. Address signal integrity, power delivery, and EMC.",
            "Implement routing for mmWave RF design with strict isolation requirements. Discuss shielding, guard rings, and substrate coupling.",
            "Optimize routing for advanced packaging (fan-out, embedded dies). Address new DRC rules and reliability constraints.",
            "Design routing strategy for harsh environment applications. Address temperature cycling, radiation, and mechanical stress.",
            "Implement routing for security-critical design. Address side-channel attack mitigation and tamper resistance."
        ],
        "expert": [  # 8+ years
            "Design routing for terahertz frequency applications. Address transmission line effects and novel interconnect technologies.",
            "Implement routing for biomedical implantable devices. Consider biocompatibility, power harvesting, and wireless communication.",
            "Optimize routing for space applications with extreme temperature cycles (-180°C to +150°C). Address thermal stress and reliability.",
            "Design routing for quantum computing control electronics. Address ultra-low noise requirements and cryogenic operation.",
            "Implement routing for advanced automotive radar systems. Handle mmWave frequencies and safety-critical requirements."
        ]
    }
}

# Helper functions
def get_questions_for_topic(topic, count=15, experience_years=3):
    """Get random questions for a topic based on experience level"""
    questions = []
    
    # Always include base questions
    if topic in PHYSICAL_DESIGN_TOPICS_3PLUS:
        base_questions = PHYSICAL_DESIGN_TOPICS_3PLUS[topic]["questions"]
        questions.extend(base_questions)
    
    # Add advanced questions based on experience
    if topic in ADVANCED_QUESTIONS:
        if experience_years >= 5:
            questions.extend(ADVANCED_QUESTIONS[topic].get("senior", []))
        if experience_years >= 8:
            questions.extend(ADVANCED_QUESTIONS[topic].get("expert", []))
    
    # Randomly select and return requested count
    if len(questions) > count:
        return random.sample(questions, count)
    return questions

def create_assignment_id():
    """Create unique assignment ID"""
    global assignment_counter
    assignment_counter += 1
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"PD_ASSIGN_{assignment_counter}_{timestamp}"

# Routes
@app.route('/')
def index():
    """Home page with API documentation"""
    return jsonify({
        "message": "Physical Design Interview System API",
        "version": "1.0-simple",
        "status": "running",
        "endpoints": {
            "GET /": "This documentation",
            "GET /health": "Health check",
            "POST /api/assignments/create": "Create new assignment",
            "GET /api/assignments": "List all assignments",
            "GET /api/assignments/<id>": "Get specific assignment",
            "GET /api/questions/<topic>": "Get sample questions for topic",
            "POST /api/assignments/refresh": "Refresh expired assignments",
            "GET /api/analytics": "Get system analytics"
        },
        "topics": ["floorplanning", "placement", "routing"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Physical Design Interview System",
        "timestamp": datetime.now().isoformat(),
        "assignments_count": len(assignments_store)
    })

@app.route('/api/assignments/create', methods=['POST'])
def create_assignment():
    """Create a new assignment"""
    try:
        data = request.get_json() or {}
        
        # Extract parameters with defaults
        engineer_id = data.get('engineer_id', 'eng001')
        topic = data.get('topic', 'floorplanning')
        experience_years = data.get('experience_years', 3)
        
        # Validate topic
        if topic not in PHYSICAL_DESIGN_TOPICS_3PLUS:
            return jsonify({
                'success': False,
                'error': f'Invalid topic. Choose from: {list(PHYSICAL_DESIGN_TOPICS_3PLUS.keys())}'
            }), 400
        
        # Get questions
        questions = get_questions_for_topic(topic, 15, experience_years)
        
        # Add experience-based scenario questions
        scenario_questions = []
        if experience_years >= 5:
            scenario_questions.append(f"You join a project 2 weeks before tapeout with major {topic} issues. Describe your emergency action plan.")
            scenario_questions.append(f"Design automated {topic} quality checks that catch 90% of issues. Include metrics and implementation plan.")
        if experience_years >= 8:
            scenario_questions.append(f"As {topic} lead, define the complete flow and team structure for a 5nm project.")
            scenario_questions.append(f"Lead technical due diligence for acquiring a company with proprietary {topic} technology.")
        
        # Mix in scenario questions if we have them
        if scenario_questions and len(questions) > 12:
            questions[-len(scenario_questions):] = scenario_questions
        
        questions = questions[:15]  # Ensure exactly 15 questions
        
        # Determine parameters based on experience
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
        
        # Create assignment
        assignment_id = create_assignment_id()
        assignment = {
            'id': assignment_id,
            'title': f"{topic.title()} Assessment - {difficulty} Level",
            'topic': topic,
            'engineer_id': engineer_id,
            'experience_years': experience_years,
            'questions': questions,
            'due_date': (datetime.now() + timedelta(days=due_days)).isoformat(),
            'points': points,
            'status': 'active',
            'created_date': datetime.now().isoformat(),
            'difficulty': difficulty
        }
        
        # Store assignment
        assignments_store[assignment_id] = assignment
        
        return jsonify({
            'success': True,
            'message': 'Assignment created successfully',
            'assignment': {
                'id': assignment_id,
                'title': assignment['title'],
                'topic': topic,
                'due_date': assignment['due_date'],
                'points': points,
                'num_questions': len(questions),
                'difficulty': difficulty
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating assignment: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to create assignment: {str(e)}'
        }), 500

@app.route('/api/assignments', methods=['GET'])
def list_assignments():
    """List all assignments with optional filters"""
    try:
        # Get filter parameters
        engineer_id = request.args.get('engineer_id')
        topic = request.args.get('topic')
        status = request.args.get('status')
        
        # Filter assignments
        filtered_assignments = []
        for assignment in assignments_store.values():
            if engineer_id and assignment['engineer_id'] != engineer_id:
                continue
            if topic and assignment['topic'] != topic:
                continue
            if status and assignment['status'] != status:
                continue
            
            # Add summary (without full questions)
            filtered_assignments.append({
                'id': assignment['id'],
                'title': assignment['title'],
                'topic': assignment['topic'],
                'engineer_id': assignment['engineer_id'],
                'due_date': assignment['due_date'],
                'points': assignment['points'],
                'status': assignment['status'],
                'created_date': assignment['created_date']
            })
        
        # Sort by created date (newest first)
        filtered_assignments.sort(key=lambda x: x['created_date'], reverse=True)
        
        return jsonify({
            'success': True,
            'assignments': filtered_assignments,
            'count': len(filtered_assignments),
            'total': len(assignments_store)
        })
        
    except Exception as e:
        logger.error(f"Error listing assignments: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to list assignments: {str(e)}'
        }), 500

@app.route('/api/assignments/<assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    """Get specific assignment with full details"""
    try:
        if assignment_id not in assignments_store:
            return jsonify({
                'success': False,
                'error': 'Assignment not found'
            }), 404
        
        assignment = assignments_store[assignment_id]
        
        return jsonify({
            'success': True,
            'assignment': assignment
        })
        
    except Exception as e:
        logger.error(f"Error getting assignment: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get assignment: {str(e)}'
        }), 500

@app.route('/api/questions/summary', methods=['GET'])
def get_questions_summary():
    """Get summary of all available questions"""
    try:
        summary = {
            'total_questions': 0,
            'by_topic': {},
            'by_experience_level': {
                '3+ years (base)': 0,
                '5+ years (senior)': 0,
                '8+ years (expert)': 0
            }
        }
        
        # Count base questions
        for topic, data in PHYSICAL_DESIGN_TOPICS_3PLUS.items():
            base_count = len(data['questions'])
            summary['by_topic'][topic] = {
                'base': base_count,
                'senior': 0,
                'expert': 0,
                'total': base_count
            }
            summary['total_questions'] += base_count
            summary['by_experience_level']['3+ years (base)'] += base_count
        
        # Count advanced questions
        for topic, levels in ADVANCED_QUESTIONS.items():
            if topic in summary['by_topic']:
                senior_count = len(levels.get('senior', []))
                expert_count = len(levels.get('expert', []))
                
                summary['by_topic'][topic]['senior'] = senior_count
                summary['by_topic'][topic]['expert'] = expert_count
                summary['by_topic'][topic]['total'] += senior_count + expert_count
                
                summary['total_questions'] += senior_count + expert_count
                summary['by_experience_level']['5+ years (senior)'] += senior_count
                summary['by_experience_level']['8+ years (expert)'] += expert_count
        
        return jsonify({
            'success': True,
            'summary': summary,
            'message': f'Total of {summary["total_questions"]} questions available across all topics and experience levels'
        })
        
    except Exception as e:
        logger.error(f"Error getting questions summary: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get questions summary: {str(e)}'
        }), 500

@app.route('/api/questions/<topic>', methods=['GET'])
def get_sample_questions(topic):
    """Get sample questions for a topic"""
    try:
        if topic not in PHYSICAL_DESIGN_TOPICS_3PLUS:
            return jsonify({
                'success': False,
                'error': f'Invalid topic. Choose from: {list(PHYSICAL_DESIGN_TOPICS_3PLUS.keys())}'
            }), 400
        
        # Get 5 sample questions
        sample_questions = get_questions_for_topic(topic, 5)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'title': PHYSICAL_DESIGN_TOPICS_3PLUS[topic]['title'],
            'sample_questions': sample_questions,
            'total_available': len(PHYSICAL_DESIGN_TOPICS_3PLUS[topic]['questions'])
        })
        
    except Exception as e:
        logger.error(f"Error getting questions: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get questions: {str(e)}'
        }), 500

@app.route('/api/assignments/refresh', methods=['POST'])
def refresh_assignments():
    """Refresh expired assignments"""
    try:
        refreshed_count = 0
        now = datetime.now()
        
        for assignment_id, assignment in list(assignments_store.items()):
            due_date = datetime.fromisoformat(assignment['due_date'].replace('Z', '+00:00'))
            
            # Check if assignment is expired (7 days past due)
            if (now - due_date).days >= 7 and assignment['status'] == 'active':
                # Create new refreshed assignment
                new_assignment_id = create_assignment_id()
                new_questions = get_questions_for_topic(assignment['topic'], 15)
                
                new_assignment = assignment.copy()
                new_assignment.update({
                    'id': new_assignment_id,
                    'title': assignment['title'] + ' (Refreshed)',
                    'questions': new_questions,
                    'created_date': now.isoformat(),
                    'due_date': (now + timedelta(days=14)).isoformat(),
                    'status': 'active'
                })
                
                # Mark old assignment as expired
                assignment['status'] = 'expired'
                
                # Store new assignment
                assignments_store[new_assignment_id] = new_assignment
                refreshed_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Refreshed {refreshed_count} expired assignments',
            'refreshed_count': refreshed_count
        })
        
    except Exception as e:
        logger.error(f"Error refreshing assignments: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to refresh assignments: {str(e)}'
        }), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get system analytics"""
    try:
        # Calculate analytics
        total = len(assignments_store)
        by_status = {'active': 0, 'completed': 0, 'expired': 0}
        by_topic = {'floorplanning': 0, 'placement': 0, 'routing': 0}
        by_difficulty = {'Intermediate': 0, 'Advanced': 0, 'Expert': 0}
        
        total_points = 0
        
        for assignment in assignments_store.values():
            # Status
            status = assignment.get('status', 'active')
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
            
            # Points
            total_points += assignment.get('points', 0)
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_assignments': total,
                'by_status': by_status,
                'by_topic': by_topic,
                'by_difficulty': by_difficulty,
                'average_points': total_points / total if total > 0 else 0,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get analytics: {str(e)}'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'Please check the API documentation at /'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Physical Design Interview System on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
