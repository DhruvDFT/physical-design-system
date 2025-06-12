<div style="background: #f8fafc; padding: 15px; margin: 10px 0; border-radius: 8px; border: 1px solid ## app.py - Stable PD System with Unique Questions Only
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

# Questions - 10 unique questions per engineer per topic
QUESTIONS = {
    "floorplanning": [
        # Engineer 1 Questions (eng001)
        "You have a 5mm x 5mm die with 4 hard macros (each 1mm x 0.8mm) and need to achieve 70% utilization. Describe your macro placement strategy considering timing and power delivery.",
        "Your design has setup timing violations on paths crossing from left to right. The floorplan has macros placed randomly. How would you reorganize the floorplan to improve timing?",
        "During floorplan, you notice routing congestion in the center region. What are 3 specific techniques you would use to reduce congestion without major timing impact?",
        "Your design has 3 voltage domains (0.9V core, 1.2V IO, 0.7V retention). Explain how you would plan the floorplan to minimize level shifter count and power grid complexity.",
        "You need to place 12 memory instances (8 SRAMs, 4 ROMs) in your design. What factors would you consider for their placement, and how would you verify floorplan quality?",
        "Your floorplan review shows IR drop violations exceeding 50mV in certain regions. Describe your approach to fix this through floorplan changes and power grid improvements.",
        "You're told to reduce die area by 15% while maintaining timing closure. What floorplan modifications would you make and what risks would you monitor?",
        "Your design has mixed-signal blocks requiring 60dB isolation from digital switching noise. How would you handle their placement and what guard techniques would you use?",
        "During early floorplan, how would you estimate routing congestion and what tools/techniques help predict routability issues before placement?",
        "Your hierarchical design has 5 major blocks with complex timing constraints between them. Explain your approach to partition-level floorplanning and interface planning.",
        
        # Engineer 2 Questions (eng002)
        "You need to implement a temperature-aware floorplan for a high-power design (150W) with thermal hotspots. How would you distribute heat-generating blocks and plan thermal vias?",
        "Your floorplan needs to support multiple test modes including scan, JTAG, and functional test. How would you plan test access and controllability in the floorplan?",
        "You're working with a heterogeneous design mixing 7nm logic with 28nm analog blocks. How would you handle the floorplan challenges of different technology nodes?",
        "Your design requires EMI/EMC compliance for automotive applications. What floorplan techniques would you use to minimize electromagnetic interference?",
        "You need to optimize the floorplan for a battery-powered IoT device with strict power budgets. Describe your low-power floorplanning methodology.",
        "Your floorplan must accommodate 8 different clock domains with specific isolation requirements. How would you partition and isolate these domains?",
        "You're implementing a security-critical design requiring hardware isolation between secure and non-secure regions. How would you plan the secure floorplan architecture?",
        "Your design has 200+ power switches for fine-grained power gating. How would you plan the floorplan to optimize power switch placement and power grid design?",
        "You need to create a floorplan for a multi-die 2.5D package with interposer connections. How would you optimize for inter-die communication and thermal management?",
        "Your floorplan must support dynamic frequency scaling across 4 performance levels. How would you plan for variable power delivery and clock distribution?",
        
        # Engineer 3 Questions (eng003)
        "You're designing a floorplan for an AI accelerator with 1024 processing elements. How would you optimize the spatial arrangement for data flow and power efficiency?",
        "Your design requires specific Keep-Out Zones (KOZ) around 12 high-speed analog PLLs. How would you incorporate these constraints into your floorplan optimization?",
        "You need to implement redundancy in a safety-critical automotive design. How would you floorplan duplicate processing units and voting logic?",
        "Your floorplan must accommodate liquid cooling interfaces with micro-channels. How would you optimize block placement for thermal coupling to cooling elements?",
        "You're working with a reconfigurable design that needs runtime floorplan changes. How would you plan for dynamic partial reconfiguration regions?",
        "Your design has 50+ voltage islands with complex dependencies. How would you create a hierarchical floorplan to manage power domain interactions?",
        "You need to optimize floorplan for a quantum processor control chip operating at 10mK. How would you handle ultra-low power and noise constraints?",
        "Your floorplan must support both chiplet integration and monolithic fallback. How would you create a flexible architecture for both scenarios?",
        "You're designing for a radiation-hardened space application. How would you floorplan for SEU mitigation and redundant critical paths?",
        "Your design requires deterministic real-time performance with <1ns jitter. How would you floorplan to minimize timing variability and ensure determinism?",
        
        # Engineer 4 Questions (eng004)
        "You need to create a floorplan for a neuromorphic processor with event-driven architecture. How would you optimize for asynchronous data flow and sparse connectivity?",
        "Your design has 16 independent subsystems that can be power-gated individually. How would you floorplan for optimal power island management?",
        "You're implementing a floorplan for a high-bandwidth memory controller supporting 8 channels. How would you optimize for signal integrity and timing closure?",
        "Your design requires built-in self-repair capabilities with spare rows and columns. How would you incorporate redundancy into your floorplan strategy?",
        "You need to optimize floorplan for a photonic-electronic integrated circuit. How would you handle optical and electrical signal routing constraints?",
        "Your floorplan must support manufacturing test with 10,000+ test points. How would you plan for test access while minimizing area overhead?",
        "You're designing a floorplan for an edge AI chip with dynamic workload adaptation. How would you optimize for varying computational demands?",
        "Your design requires functional safety compliance (ISO 26262 ASIL-D). How would you floorplan for fault detection and fail-safe operation?",
        "You need to create a floorplan for a multi-standard wireless SoC supporting 5G, WiFi, and Bluetooth. How would you handle RF isolation and co-existence?",
        "Your floorplan must accommodate on-chip sensors for temperature, voltage, and aging monitoring. How would you distribute sensors for optimal coverage?",
        
        # Engineer 5 Questions (eng005)
        "You're implementing a floorplan for a cryptocurrency mining ASIC with 10,000 hash engines. How would you optimize for power delivery and thermal management?",
        "Your design requires secure key storage with tamper detection. How would you floorplan security features and anti-tampering mechanisms?",
        "You need to optimize floorplan for a satellite communication processor with radiation tolerance. How would you handle SEE mitigation and error correction?",
        "Your floorplan must support field-upgradeable functionality through e-fuses. How would you plan for post-silicon configuration and feature enabling?",
        "You're designing for a biomedical implant with ultra-low power requirements. How would you floorplan for energy harvesting and power management?",
        "Your design has 32 independent clock domains with complex frequency relationships. How would you floorplan for clock distribution and domain crossing?",
        "You need to create a floorplan for a data center accelerator with 1TB/s memory bandwidth. How would you optimize for high-speed I/O and signal integrity?",
        "Your floorplan must accommodate machine learning inference with dynamic precision scaling. How would you optimize for variable bit-width operations?",
        "You're implementing a floorplan for an autonomous vehicle perception chip. How would you optimize for real-time processing and fault tolerance?",
        "Your design requires compliance with multiple international standards (FCC, CE, VCCI). How would you floorplan for global regulatory requirements?"
    ],
    "placement": [
        # Engineer 1 Questions (eng001)
        "Your placement run shows timing violations on 20 critical paths with negative slack up to -50ps. Describe your systematic approach to fix these violations.",
        "You're seeing routing congestion hotspots after placement in 2-3 regions. What placement adjustments would you make to improve routability?",
        "Your design has high-fanout nets (>500 fanout) causing placement issues. How would you handle these nets during placement optimization?",
        "Compare global placement vs detailed placement - what specific problems does each solve and when would you iterate between them?",
        "Your placement shows leakage power 20% higher than target. What placement techniques would you use to reduce power while maintaining timing?",
        "You have a multi-voltage design with 3 voltage islands. Describe your placement strategy for cells near domain boundaries and level shifter placement.",
        "Your timing report shows 150 hold violations scattered across the design. How would you address this through placement without affecting setup timing?",
        "During placement, you notice certain instances are creating routes longer than 500um. What tools and techniques help identify and fix such placement issues?",
        "Your design has 200+ clock gating cells. Explain their optimal placement strategy and impact on both power and timing closure.",
        "You're working with a design that has both high-performance (1GHz) and low-power (100MHz) modes. How does this affect your placement strategy and optimization targets?",
        
        # Engineer 2 Questions (eng002)
        "Your placement flow needs to handle 50+ million instances with memory constraints. What techniques would you use for large-scale placement optimization?",
        "You need to place analog-sensitive blocks that require specific orientation and spacing from digital switching. How would you handle mixed-signal placement constraints?",
        "Your design has critical timing paths that span across multiple voltage domains. How would you optimize placement to minimize domain crossing delays?",
        "You're implementing placement for a design with 20+ hierarchical blocks that need to be independently optimizable. Describe your hierarchical placement strategy.",
        "Your placement must meet strict thermal constraints with maximum junction temperature of 85°C. How would you incorporate thermal-aware placement techniques?",
        "You need to optimize placement for both area and wirelength while maintaining timing closure. Describe your multi-objective placement optimization approach.",
        "Your design requires specific placement constraints for DFT structures including scan chains and BIST logic. How would you handle test-aware placement?",
        "You're placing a design with 1000+ memory instances of varying sizes. How would you optimize memory placement for timing, power, and routability?",
        "Your placement must accommodate strict EMI/EMC requirements for automotive applications. What placement techniques would you use for noise reduction?",
        "You need to implement placement for a security-critical design with hardware trojan resistance. How would you randomize placement while meeting timing?",
        
        # Engineer 3 Questions (eng003)
        "Your design has 500+ power switches that need optimal placement for power gating efficiency. How would you coordinate placement with power grid design?",
        "You're placing an AI accelerator with systolic array architecture. How would you optimize placement for data flow patterns and computational efficiency?",
        "Your placement must handle runtime reconfigurable regions for FPGA-style functionality. How would you manage dynamic placement constraints?",
        "You need to place a design for 3D IC integration with through-silicon vias (TSVs). How would you optimize placement for inter-tier communication?",
        "Your placement flow must support incremental changes for ECO implementations. How would you maintain placement stability during design iterations?",
        "You're implementing placement for a quantum processor control circuit operating at millikelvin temperatures. How would you handle ultra-low power constraints?",
        "Your design requires placement optimization for aging resilience and lifetime reliability. What techniques would you use for degradation-aware placement?",
        "You need to place a neuromorphic processor with event-driven, asynchronous processing elements. How would you optimize for sparse, dynamic connectivity?",
        "Your placement must accommodate radiation hardening for space applications. How would you implement placement strategies for SEU mitigation?",
        "You're placing a high-bandwidth memory interface with 32 data lanes. How would you optimize placement for signal integrity and timing matching?",
        
        # Engineer 4 Questions (eng004)
        "Your placement flow needs to handle design closure for a 2nm technology node with complex design rules. What advanced placement techniques would you employ?",
        "You're implementing placement for a chiplet-based design with heterogeneous integration. How would you optimize placement across different process technologies?",
        "Your design has 100+ independent power domains with complex switching sequences. How would you coordinate placement with power management requirements?",
        "You need to place a design for photonic integration with optical and electrical signals. How would you handle the unique constraints of photonic placement?",
        "Your placement must support functional safety requirements (ISO 26262) with fault detection and mitigation. How would you implement safety-aware placement?",
        "You're placing a design for in-memory computing with compute-enabled memories. How would you optimize placement for data locality and computational efficiency?",
        "Your placement flow must handle extreme design constraints for aerospace applications. How would you implement placement for harsh environment operation?",
        "You need to implement placement for a reconfigurable computing platform with runtime adaptability. How would you manage dynamic placement optimization?",
        "Your design requires placement optimization for side-channel attack resistance. What placement techniques would you use for security hardening?",
        "You're placing a biomedical implant design with strict power and size constraints. How would you optimize placement for ultra-low power operation?",
        
        # Engineer 5 Questions (eng005)
        "Your placement must accommodate on-chip learning capabilities with synaptic weight updates. How would you optimize placement for adaptive neural networks?",
        "You're implementing placement for a data center accelerator with disaggregated compute and memory. How would you optimize for high-bandwidth interconnects?",
        "Your design requires placement for quantum-classical hybrid computing. How would you handle the interface between quantum and classical processing elements?",
        "You need to place a design for edge AI with dynamic model deployment. How would you optimize placement for varying computational graphs?",
        "Your placement must support real-time adaptation for autonomous vehicle perception. How would you implement placement for deterministic real-time performance?",
        "You're placing a cryptocurrency mining ASIC with thousands of parallel hash engines. How would you optimize placement for maximum throughput and efficiency?",
        "Your design requires placement for distributed ledger processing with consensus mechanisms. How would you optimize placement for parallel validation?",
        "You need to implement placement for a 6G wireless baseband processor. How would you handle placement for massive MIMO and beamforming requirements?",
        "Your placement must accommodate advanced packaging with Fan-Out Wafer Level Packaging (FOWLP). How would you optimize for package-aware placement?",
        "You're placing a design for quantum error correction with syndrome detection and correction. How would you optimize placement for quantum fault tolerance?"
    ],
    "routing": [
        # Engineer 1 Questions (eng001)
        "After global routing, you have 500 DRC violations (spacing, via, width). Describe your systematic approach to resolve these violations efficiently.",
        "Your design has 10 differential pairs for high-speed signals. Explain your routing strategy to maintain 100-ohm impedance and minimize skew.",
        "You're seeing timing degradation after detailed routing compared to placement timing. What causes this and how would you recover the timing?",
        "Your router is struggling with congestion in certain regions leading to 5% routing non-completion. What techniques would you use to achieve 100% routing?",
        "Describe your approach to power/ground routing for a 200A peak current design. How do you ensure adequate current carrying capacity and low IR drop?",
        "Your design has specific layer constraints (no routing on M1 except local connections, M2-M3 for signal, M4-M6 for power). How does this impact your routing strategy?",
        "You have crosstalk violations on 50 critical nets causing functional failures. Explain your routing techniques to minimize crosstalk and meet noise requirements.",
        "Your clock distribution network requires <50ps skew across 10,000 flops. Describe clock routing methodology and skew optimization techniques.",
        "During routing, some power nets are showing electromigration violations. How would you address current density issues through routing changes and via sizing?",
        "You need to route in a 7nm design with double patterning constraints. Explain the challenges and your approach to handle LELE (Litho-Etch-Litho-Etch) decomposition issues.",
        
        # Engineer 2 Questions (eng002)
        "Your high-speed design requires length matching for 32-bit DDR5 interfaces running at 4800 MT/s. Describe your routing methodology for signal integrity.",
        "You need to implement shield routing for sensitive analog signals in a mixed-signal design. How would you plan and execute the shielding strategy?",
        "Your routing must handle 16 different supply voltages with strict isolation requirements. How would you manage multi-rail power routing?",
        "You're routing a design with strict EMI requirements for aerospace applications. What routing techniques would you use to minimize electromagnetic emissions?",
        "Your design has 100+ high-current power domains requiring dedicated power routing. Describe your strategy for hierarchical power grid routing.",
        "You need to route through a design with 200+ IP blocks having different routing restrictions. How would you handle block-level routing constraints?",
        "Your routing flow must handle both fine-pitch BGA and wire-bond packaging constraints. How would you optimize routing for different packaging technologies?",
        "You're routing a neuromorphic processor with sparse, event-driven connectivity. How would you optimize routing for asynchronous signal propagation?",
        "Your design requires routing for quantum processor control signals with picosecond timing precision. How would you handle ultra-precise timing routing?",
        "You need to route a 3D IC design with through-silicon vias (TSVs) connecting multiple tiers. Describe your approach to 3D routing optimization.",
        
        # Engineer 3 Questions (eng003)
        "Your routing must accommodate liquid cooling micro-channels that create routing blockages. How would you optimize routing around thermal management structures?",
        "You're routing a photonic-electronic integrated circuit with optical and electrical signals. How would you handle the unique constraints of hybrid routing?",
        "Your design requires routing for radiation-hardened space applications with SEU tolerance. What routing techniques would you use for error resilience?",
        "You need to implement routing for a reconfigurable computing platform with runtime routing changes. How would you manage dynamic routing optimization?",
        "Your routing must support functional safety (ISO 26262) with fault detection and redundancy. How would you implement safety-aware routing strategies?",
        "You're routing a chiplet-based design with high-bandwidth inter-chiplet links. How would you optimize routing for chiplet integration?",
        "Your design has 1000+ power switches requiring careful routing coordination. How would you manage power switch routing and control signal distribution?",
        "You need to route a biomedical implant with strict EMI/EMC requirements and ultra-low power. Describe your approach to low-power, low-noise routing.",
        "Your routing must accommodate on-chip sensors and monitoring circuits. How would you distribute sensor networks while minimizing routing overhead?",
        "You're routing an AI accelerator with systolic array data flow patterns. How would you optimize routing for regular, high-bandwidth data movement?",
        
        # Engineer 4 Questions (eng004)
        "Your routing flow must handle advanced packaging with redistribution layers (RDL). How would you optimize routing for package-level integration?",
        "You need to route a design for 2nm technology with extreme design rule complexity. What advanced routing techniques would you employ?",
        "Your routing must support security features including side-channel attack resistance. How would you implement security-aware routing strategies?",
        "You're routing a cryptocurrency mining ASIC with massive parallel processing elements. How would you optimize routing for maximum throughput?",
        "Your design requires routing for in-memory computing with compute-enabled memory arrays. How would you handle routing for distributed computation?",
        "You need to implement routing for quantum error correction with syndrome processing. How would you optimize routing for quantum fault tolerance?",
        "Your routing must accommodate field-upgradeable functionality through programmable interconnects. How would you manage reconfigurable routing?",
        "You're routing a 6G wireless baseband with massive MIMO processing. How would you handle routing for high-bandwidth beamforming applications?",
        "Your design requires routing for autonomous vehicle perception with deterministic timing. How would you implement real-time routing constraints?",
        "You need to route a data center accelerator with disaggregated compute and memory. How would you optimize routing for high-bandwidth interconnects?",
        
        # Engineer 5 Questions (eng005)
        "Your routing must support on-chip learning with synaptic weight updates in neuromorphic processors. How would you handle adaptive routing for neural plasticity?",
        "You're routing a quantum-classical hybrid processor with interface requirements. How would you manage routing between quantum and classical domains?",
        "Your design requires routing for edge AI with dynamic model deployment. How would you optimize routing for varying computational graphs?",
        "You need to implement routing for distributed ledger processing with consensus mechanisms. How would you optimize routing for parallel validation?",
        "Your routing must accommodate advanced thermal management with on-chip cooling. How would you integrate routing with thermal optimization?",
        "You're routing a design for space applications with radiation-hardened interconnects. How would you implement routing for harsh environment operation?",
        "Your design requires routing for machine learning inference with dynamic precision scaling. How would you handle routing for variable bit-width operations?",
        "You need to route a design for satellite communication with adaptive beamforming. How would you optimize routing for phased array processing?",
        "Your routing must support compliance with multiple international EMI/EMC standards. How would you implement globally compliant routing strategies?",
        "You're routing a design for implantable medical devices with wireless power transfer. How would you optimize routing for inductive coupling and biocompatibility?"
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
    
    for i in range(1, 6):
        uid = f'eng00{i}'
        users[uid] = {
            'id': uid,
            'username': uid,
            'password': hash_pass('password123'),
            'is_admin': False,
            'exp': 3 + (i % 3)
        }

def create_test(eng_id, topic):
    global counter
    counter += 1
    test_id = f"PD_{topic}_{eng_id}_{counter}"
    
    # Get engineer-specific questions (10 per engineer per topic)
    all_questions = QUESTIONS[topic]
    
    # Map engineer to their specific 10 questions
    engineer_map = {
        'eng001': 0,   # Questions 0-9
        'eng002': 10,  # Questions 10-19  
        'eng003': 20,  # Questions 20-29
        'eng004': 30,  # Questions 30-39
        'eng005': 40   # Questions 40-49
    }
    
    start_idx = engineer_map.get(eng_id, 0)
    
    # Select all 10 questions for this specific engineer
    selected_questions = all_questions[start_idx:start_idx + 10]
    
    test = {
        'id': test_id,
        'engineer_id': eng_id,
        'topic': topic,
        'questions': selected_questions,
        'answers': {},
        'status': 'pending',
        'created': datetime.now().isoformat(),
        'due': (datetime.now() + timedelta(days=3)).isoformat(),
        'score': None
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
    <title>PD Assessment Login</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }
        .box { background: rgba(255,255,255,0.95); padding: 40px; border-radius: 20px; width: 350px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
        h1 { background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 30px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; }
        input:focus { outline: none; border-color: #667eea; }
        button { width: 100%; padding: 14px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
        .info { background: #f0f9ff; border: 1px solid #0ea5e9; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }
    </style>
</head>
<body>
    <div class="box">
        <h1>PD Assessment</h1>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <div class="info">
            <strong>Test Login:</strong><br>
            Engineers: eng001, eng002, eng003, eng004, eng005<br>
            Password: password123
        </div>
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
        eng_options += f'<option value="{eng["id"]}">{eng["username"]} (3+ Experience)</option>'
    
    pending_html = ''
    for p in pending:
        pending_html += f'''
        <div style="background: #f8fafc; padding: 15px; margin: 10px 0; border-radius: 8px; border: 1px solid #e2e8f0;">
            <strong>{p["topic"].title()} - {p["engineer_id"]}</strong><br>
            <small>10 Unique Questions | Max: 100 points</small><br>
            <a href="/admin/review/{p["id"]}" style="background: #10b981; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 8px;">Review</a>
        </div>'''
    
    if not pending_html:
        pending_html = '<p style="text-align: center; color: #64748b; padding: 40px;">No pending reviews</p>'
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <style>
        body {{ font-family: Arial; margin: 0; background: #f8fafc; }}
        .header {{ background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 20px 0; }}
        .container {{ max-width: 1000px; margin: 20px auto; padding: 0 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
        .stat {{ background: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-num {{ font-size: 24px; font-weight: bold; color: #1e40af; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        select, button {{ padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }}
        button {{ background: #3b82f6; color: white; border: none; cursor: pointer; }}
        .logout {{ background: rgba(255,255,255,0.2); color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; float: right; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="max-width: 1000px; margin: 0 auto; padding: 0 20px;">
            <h1>Admin Dashboard
                <a href="/logout" class="logout">Logout</a>
            </h1>
        </div>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat"><div class="stat-num">{len(engineers)}</div><div>Engineers</div></div>
            <div class="stat"><div class="stat-num">{len(all_tests)}</div><div>Tests</div></div>
            <div class="stat"><div class="stat-num">{len(pending)}</div><div>Pending</div></div>
            <div class="stat"><div class="stat-num">150</div><div>Questions</div></div>
        </div>
        
        <div class="card">
            <h2>Create Test</h2>
            <form method="POST" action="/admin/create">
                <select name="engineer_id" required>
                    <option value="">Select Engineer...</option>
                    {eng_options}
                </select>
                <select name="topic" required>
                    <option value="">Select Topic...</option>
                    <option value="floorplanning">Floorplanning</option>
                    <option value="placement">Placement</option>
                    <option value="routing">Routing</option>
                </select>
                <button type="submit">Create</button>
            </form>
        </div>
        
        <div class="card">
            <h2>Pending Reviews</h2>
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
    
    if request.method == 'POST':
        total = 0
        for i in range(10):  # Now 10 questions instead of 3
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
        questions_html += f'''
        <div style="background: white; border-radius: 8px; padding: 20px; margin: 15px 0;">
            <h4>Question {i+1}</h4>
            <div style="background: #f1f5f9; padding: 15px; border-radius: 6px; margin: 10px 0;">
                {q}
            </div>
            <h5>Answer:</h5>
            <div style="background: #fefefe; border: 1px solid #e2e8f0; padding: 15px; border-radius: 6px; font-family: monospace; white-space: pre-wrap;">
                {answer}
            </div>
            <div style="margin: 15px 0;">
                <label><strong>Score:</strong></label>
                <input type="number" name="score_{i}" min="0" max="10" value="7" style="width: 60px; padding: 5px;">
                <span>/10</span>
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
                    <strong>Score: {t["score"]}/100</strong>
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
            <div class="stat"><div style="font-size: 20px; font-weight: bold;">10</div><div>Questions</div></div>
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
        for i in range(10):  # Now 10 questions
            answer = request.form.get(f'answer_{i}', '').strip()
            if answer:
                answers[str(i)] = answer
        
        if len(answers) == 10:  # All 10 questions must be answered
            test['answers'] = answers
            test['status'] = 'submitted'
        
        return redirect('/student')
    
    questions_html = ''
    for i, q in enumerate(test['questions']):
        questions_html += f'''
        <div style="background: rgba(255,255,255,0.95); border-radius: 16px; padding: 24px; margin: 20px 0;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-bottom: 16px;">
                Question {i+1} of {len(test['questions'])}
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
