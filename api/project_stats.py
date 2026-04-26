from flask import Flask, jsonify, request
from flask_cors import CORS
import json, os

app = Flask(__name__)
CORS(app)

@app.route('/api/project-stats', methods=['GET', 'OPTIONS'])
def project_stats():
    if request.method == 'OPTIONS':
        return '', 200

    base = os.path.dirname(os.path.dirname(__file__))
    
    # Load from data/ directory (always available — committed to repo)
    with open(os.path.join(base, 'data', 'metrics.json')) as f:
        metrics = json.load(f)
    with open(os.path.join(base, 'data', 'defect_types.json')) as f:
        defects = json.load(f)
    with open(os.path.join(base, 'data', 'training_logs.json')) as f:
        logs = json.load(f)
    
    return jsonify({
        "metrics": metrics,
        "dataset": defects,
        "training_logs": logs,
        "models": {
            "backbone": "EfficientNet-B0",
            "generator": "WGAN-GP + Self-Attention",
            "huggingface_repo": os.environ.get("HF_MODEL_REPO", "not-configured")
        }
    })
