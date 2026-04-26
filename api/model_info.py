from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/model-info', methods=['GET'])
def model_info():
    hf_repo = os.environ.get("HF_MODEL_REPO", "")
    return jsonify({
        "demo_mode": not bool(hf_repo),
        "hf_repo_configured": bool(hf_repo),
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
        "hardware": "NVIDIA RTX 3050 Laptop GPU (4GB VRAM)",
        "framework": "PyTorch 2.2.2",
        "groq_enabled": bool(os.environ.get("GROQ_API_KEY", "")),
        "metrics": {
            "val_acc": 83.19,
            "val_roc_auc": 0.9197,
            "test_acc": 71.43,
            "test_roc_auc": 0.5893,
            "defect_recall": 94.44,
            "test_note": "Test set covers 4 of 14 defect categories — distribution shift explains AUC gap from val to test."
        }
    })
