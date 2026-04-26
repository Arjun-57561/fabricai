from flask import Flask, jsonify
from flask_cors import CORS
import json, os

app = Flask(__name__)
CORS(app)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_json(filename):
    with open(os.path.join(BASE, 'data', filename), 'r') as f:
        return json.load(f)

@app.route('/api/project-stats', methods=['GET'])
def project_stats():
    try:
        metrics = load_json('metrics.json')
        defects = load_json('defect_types.json')
        logs    = load_json('training_logs.json')
    except Exception as e:
        return jsonify({"error": f"Data load failed: {str(e)}"}), 500

    return jsonify({
        "metrics": metrics,
        "dataset": defects,
        "training_logs": logs,
        "models": {
            "backbone":        "EfficientNet-B0",
            "generator":       "WGAN-GP + Self-Attention (500 epochs)",
            "diffusion":       "DDPM U-Net (300 epochs)",
            "huggingface_repo": os.environ.get("HF_MODEL_REPO", "not-configured")
        }
    })
