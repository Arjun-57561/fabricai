from flask import Flask, request, jsonify
from flask_cors import CORS
import time, io, os, logging, hashlib, threading
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

ALLOWED_MIMETYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/jpg'}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

_model_cache = None
_model_lock = threading.Lock()


def _get_transform():
    """Lazy-load torchvision transform only when needed."""
    from torchvision import transforms
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])


def load_model():
    global _model_cache
    if _model_cache is not None:
        return _model_cache, False
    with _model_lock:
        if _model_cache is not None:
            return _model_cache, False
        hf_repo = os.environ.get("HF_MODEL_REPO", "")
        if not hf_repo:
            return None, True
        try:
            import torch, timm
            from huggingface_hub import hf_hub_download
            path = hf_hub_download(
                repo_id=hf_repo,
                filename="best_model_augmented.pth",
                token=os.environ.get("HF_TOKEN"),
                cache_dir="/tmp/hf_cache"
            )
            model = timm.create_model('efficientnet_b0',
                                       pretrained=False, num_classes=2)
            state = torch.load(path, map_location='cpu')
            if isinstance(state, dict) and 'model_state_dict' in state:
                state = state['model_state_dict']
            model.load_state_dict(state)
            model.eval()
            _model_cache = model
            logger.info("Model loaded from HuggingFace successfully")
            return model, False
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            return None, True


@app.route('/api/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "Missing 'image' field in form-data"}), 400

    file = request.files['image']

    if file.mimetype not in ALLOWED_MIMETYPES:
        return jsonify({
            "error": f"Unsupported file type: {file.mimetype}. Use JPEG, PNG, or WebP."
        }), 415

    raw = file.read()
    if len(raw) > MAX_SIZE_BYTES:
        return jsonify({"error": "File too large. Max 10MB allowed."}), 413

    try:
        img = Image.open(io.BytesIO(raw)).convert('RGB')
    except Exception:
        return jsonify({"error": "Could not decode image. File may be corrupted."}), 400

    model, is_demo = load_model()
    start = time.perf_counter()

    if is_demo:
        # Balanced deterministic demo: 30-69% defect probability
        h = int(hashlib.md5(raw[:512]).hexdigest(), 16) % 100
        defect_prob = round(0.30 + (h % 40) / 100.0, 4)
        normal_prob = round(1.0 - defect_prob, 4)
        inference_ms = 11.18
    else:
        import torch
        transform = _get_transform()
        tensor = transform(img).unsqueeze(0)
        with torch.no_grad():
            logits = model(tensor)
            probs = torch.softmax(logits, dim=1)
        normal_prob = round(float(probs[0][0]), 4)
        defect_prob = round(float(probs[0][1]), 4)
        inference_ms = round((time.perf_counter() - start) * 1000, 2)

    verdict = "DEFECT" if defect_prob > normal_prob else "NORMAL"
    confidence = round(max(defect_prob, normal_prob), 4)

    logger.info(
        f"Inference | verdict={verdict} | conf={confidence:.3f} | "
        f"ms={inference_ms} | demo={is_demo} | file={file.filename}"
    )

    return jsonify({
        "verdict": verdict,
        "confidence": confidence,
        "probabilities": {
            "normal": normal_prob,
            "defect": defect_prob
        },
        "inference_ms": inference_ms,
        "model": "EfficientNet-B0 (GAN-Augmented)" if not is_demo else "EfficientNet-B0 (Demo)",
        "demo_mode": is_demo
    })
