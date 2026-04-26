from flask import Flask, request, jsonify
from flask_cors import CORS
import torch, timm, time, io, os, logging, hashlib, threading
from PIL import Image
from torchvision import transforms

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

TRANSFORM = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

_model_cache = None
_model_lock = threading.Lock()

def load_model():
    global _model_cache
    if _model_cache is not None:
        return _model_cache, False
    
    with _model_lock:
        if _model_cache is not None:
            return _model_cache, False

        hf_repo = os.environ.get("HF_MODEL_REPO")
        hf_token = os.environ.get("HF_TOKEN")
        
        if not hf_repo:
            return None, True
        
        try:
            from huggingface_hub import hf_hub_download
            weight_path = hf_hub_download(
                repo_id=hf_repo,
                filename="best_model_augmented.pth",
                token=hf_token,
                cache_dir="/tmp/hf_cache"
            )
            model = timm.create_model('efficientnet_b0', pretrained=False, num_classes=2)
            state = torch.load(weight_path, map_location='cpu')
            if isinstance(state, dict) and 'model_state_dict' in state:
                state = state['model_state_dict']
            model.load_state_dict(state)
            model.eval()
            _model_cache = model
            return model, False
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            return None, True

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return '', 200
    
    if 'image' not in request.files:
        return jsonify({"error": "No image field in request"}), 400
    
    file = request.files['image']
    
    ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
    MAX_SIZE_MB = 10

    if file.mimetype not in ALLOWED_TYPES:
        return jsonify({"error": f"Unsupported type: {file.mimetype}. Use JPEG/PNG/WebP"}), 415
    
    raw = file.read()
    if len(raw) > MAX_SIZE_MB * 1024 * 1024:
        return jsonify({"error": f"File too large. Max {MAX_SIZE_MB}MB"}), 413
    
    try:
        img = Image.open(io.BytesIO(raw)).convert('RGB')
    except Exception:
        return jsonify({"error": "Invalid image file"}), 400
    
    model, is_demo = load_model()
    start = time.perf_counter()
    
    if is_demo:
        h = int(hashlib.md5(file.filename.encode()).hexdigest(), 16) % 100
        defect_prob = 0.3 + (h % 40) / 100
        normal_prob = 1.0 - defect_prob
        verdict = "DEFECT" if defect_prob > normal_prob else "NORMAL"
        inference_ms = 11.18
    else:
        tensor = TRANSFORM(img).unsqueeze(0)
        with torch.no_grad():
            logits = model(tensor)
            probs = torch.softmax(logits, dim=1)
        normal_prob = float(probs[0][0])
        defect_prob = float(probs[0][1])
        verdict = "DEFECT" if defect_prob > normal_prob else "NORMAL"
        inference_ms = round((time.perf_counter() - start) * 1000, 2)
    
    confidence = max(defect_prob, normal_prob)
    
    logger.info(f"Inference | file={file.filename} | result={verdict} | conf={confidence:.3f} | ms={inference_ms}")
    
    return jsonify({
        "verdict": verdict,
        "confidence": round(confidence, 4),
        "probabilities": {
            "normal": round(normal_prob, 4),
            "defect": round(defect_prob, 4)
        },
        "inference_ms": inference_ms,
        "model": "EfficientNet-B0 (GAN-Augmented)" if not is_demo else "EfficientNet-B0 (DEMO)",
        "demo_mode": is_demo
    })
