# app.py - Physical Design Interview System (Simplified Working Version)
import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Store assignments in memory
assignments = {}
counter = 0

# Physical Design Questions (3+ Years) - All 15 per topic
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

@app.route('/')
def home():
    """API documentation"""
    return jsonify({
        "message": "Physical Design Interview System API",
        "status": "running",
        "total_questions": 45,
        "topics": list(QUESTIONS.keys()),
        "endpoints": {
            "GET /": "This documentation",
            "GET /health": "Health check",
            "POST /api/create-assignment": "Create new assignment",
            "GET /api/assignments": "List all assignments",
            "GET /api/questions/<topic>": "Get all questions for a topic"
        }
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({"status": "healthy", "assignments": len(assignments)})

@app.route('/api/create-assignment', methods=['POST'])
def create_assignment():
    """Create assignment with all 15 questions"""
    global counter
    
    data = request.get_json() or {}
    engineer_id = data.get('engineer_id', 'eng001')
    topic = data.get('topic', 'floorplanning')
    
    if topic not in QUESTIONS:
        return jsonify({"error": "Invalid topic"}), 400
    
    counter += 1
    assignment_id = f"PD_{topic}_{counter}"
    
    assignments[assignment_id] = {
        'id': assignment_id,
        'engineer_id': engineer_id,
        'topic': topic,
        'questions': QUESTIONS[topic],  # All 15 questions
        'created_at': str(os.environ.get('TIMESTAMP', 'now'))
    }
    
    return jsonify({
        'success': True,
        'assignment_id': assignment_id,
        'questions_count': len(QUESTIONS[topic])
    })

@app.route('/api/assignments')
def list_assignments():
    """List all assignments"""
    return jsonify({
        'count': len(assignments),
        'assignments': list(assignments.values())
    })

@app.route('/api/questions/<topic>')
def get_questions(topic):
    """Get all 15 questions for a topic"""
    if topic not in QUESTIONS:
        return jsonify({"error": "Invalid topic"}), 400
    
    return jsonify({
        'topic': topic,
        'count': len(QUESTIONS[topic]),
        'questions': QUESTIONS[topic]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
