#!/usr/bin/env python3
import os
import glob

print("🔍 Debug: Checking requirements...")
try:
    from flask import Flask, render_template_string
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask import error: {e}")
    exit(1)

try:
    import plotly
    print("✅ Plotly imported successfully")
except ImportError as e:
    print(f"❌ Plotly import error: {e}")
    exit(1)

app = Flask(__name__)

@app.route('/')
def index():
    # Check for JSON files
    json_files = glob.glob("bitcoin_analysis_*.json")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bitcoin Analysis Debug</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>🚀 Bitcoin Analysis Visualizer - Debug Mode</h1>
            
            <div class="alert alert-info">
                <h4>Status Check:</h4>
                <p>✅ Flask is working</p>
                <p>✅ Plotly is available</p>
                <p>📁 Found {len(json_files)} JSON files: {json_files}</p>
            </div>
            
            {'<div class="alert alert-warning">No JSON files found. Run: <code>python3 bitcoin_analysis.py</code> first.</div>' if not json_files else ''}
            
            <div class="card">
                <div class="card-body">
                    <h5>Next Steps:</h5>
                    <ol>
                        <li>Generate JSON data: <code>python3 bitcoin_analysis.py</code></li>
                        <li>Use any Bitcoin address (try: <code>1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa</code>)</li>
                        <li>Refresh this page</li>
                        <li>Switch to main app: <code>python3 app.py</code></li>
                    </ol>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    print("🌐 Starting debug server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)