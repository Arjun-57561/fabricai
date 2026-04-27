"""
FabricAI — Local Dev Server
Serves all API endpoints + public/ HTML pages on http://localhost:5000
Run: python dev_server.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# Load .env for local dev (no-op if python-dotenv not installed)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

from flask import Flask, send_from_directory
from flask_cors import CORS

# ── Import all API apps as blueprints ──────────────────────────
from api.model_info      import app as _mi;   mi_view   = _mi.view_functions['model_info']
from api.project_stats   import app as _ps;   ps_view   = _ps.view_functions['project_stats']
from api.synthetic_sample import app as _ss;  ss_view   = _ss.view_functions['synthetic_sample']
from api.predict         import app as _pr;   pr_view   = _pr.view_functions['predict']
from api.explain         import app as _ex;   ex_view   = _ex.view_functions['explain']

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), 'public')

# ── Wire API routes ────────────────────────────────────────────
app.add_url_rule('/api/model-info',       'model_info',       mi_view, methods=['GET'])
app.add_url_rule('/api/project-stats',    'project_stats',    ps_view, methods=['GET'])
app.add_url_rule('/api/synthetic-sample', 'synthetic_sample', ss_view, methods=['GET'])
app.add_url_rule('/api/predict',          'predict',          pr_view, methods=['POST'])
app.add_url_rule('/api/explain',          'explain',          ex_view, methods=['POST'])

# ── Serve public/ pages ────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory(PUBLIC_DIR, 'index.html')

@app.route('/analytics')
@app.route('/analytics.html')
def analytics():
    return send_from_directory(PUBLIC_DIR, 'analytics.html')

@app.route('/architecture')
@app.route('/architecture.html')
def architecture():
    return send_from_directory(PUBLIC_DIR, 'architecture.html')

if __name__ == '__main__':
    print()
    print('  +--------------------------------------+')
    print('  |   FabricAI Dev Server                |')
    print('  |   http://localhost:5000              |')
    print('  +--------------------------------------+')
    print()
    print('  Pages:')
    print('    http://localhost:5000/               <- Inspect')
    print('    http://localhost:5000/analytics      <- Analytics')
    print('    http://localhost:5000/architecture   <- Architecture')
    print()
    print('  APIs:')
    print('    GET  /api/model-info')
    print('    GET  /api/project-stats')
    print('    GET  /api/synthetic-sample?seed=7')
    print('    POST /api/predict        (multipart, key=image)')
    print('    POST /api/explain        (JSON body)')
    print()
    if os.environ.get('HF_MODEL_REPO'):
        print(f"  Live mode — HF_MODEL_REPO={os.environ.get('HF_MODEL_REPO')}")
    else:
        print('  Running in DEMO mode (no HF_MODEL_REPO set)')
    print('  Press Ctrl+C to stop')
    print()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
