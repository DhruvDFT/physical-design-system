# app_minimal.py - Minimal test version
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "message": "Physical Design Interview System",
        "endpoints": ["/", "/health", "/test"]
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/test')
def test():
    return jsonify({"test": "working", "questions": 75})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
