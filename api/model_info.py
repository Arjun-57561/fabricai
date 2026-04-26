from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/model-info', methods=['GET', 'OPTIONS'])
def model_info():
    if request.method == 'OPTIONS':
        return '', 200

    hf_repo = os.environ.get("HF_MODEL_REPO")
    is_demo_mode = not bool(hf_repo)

    return jsonify({
      "demo_mode": is_demo_mode,
      "backbone": "EfficientNet-B0",
      "library": "timm 0.9.16",
      "pretrained_on": "ImageNet-1k",
      "classifier_params": 5288548,
      "generator_params": 13297249,
      "critic_params": 11274049,
      "total_gan_params": 24571298,
      "input_size": "256x256",
      "classes": ["normal", "defect"],
      "optimizer": "AdamW",
      "loss_fn": "Focal Loss (alpha=0.75, gamma=2.0)",
      "scheduler": "CosineAnnealingLR",
      "epochs": 40,
      "gan_epochs": 500,
      "batch_size": 64,
      "learning_rate": "3e-4",
      "hardware": "NVIDIA RTX 3050 Laptop GPU (4.3GB VRAM)",
      "framework": "PyTorch 2.2.2"
    })
