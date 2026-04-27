from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json, logging

logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)

SYSTEM_PROMPT = """You are a textile quality control AI assistant.
Given an EfficientNet-B0 defect detection result, return ONLY a valid
JSON object with exactly these three keys:
  "explanation"    : 1 sentence — what the defect likely is
  "likely_cause"   : 1 sentence — probable manufacturing root cause
  "recommendation" : 1 sentence — recommended QC action
Keep each value under 20 words. No markdown, no extra text, just JSON."""

FALLBACK_RESPONSES = {
    "DEFECT": {
        "explanation": "High-confidence defect detected — likely surface contamination or structural fiber irregularity.",
        "likely_cause": "Possible foreign particle introduction or tension inconsistency during weaving.",
        "recommendation": "Flag batch for manual inspection before downstream processing.",
        "demo_mode": True
    },
    "NORMAL": {
        "explanation": "Fabric sample appears structurally uniform with no visible anomalies detected.",
        "likely_cause": "N/A — no defect signatures identified in this sample.",
        "recommendation": "Approve batch; proceed to next quality checkpoint.",
        "demo_mode": True
    }
}

@app.route('/api/explain', methods=['POST'])
def explain():
    body = request.get_json(silent=True) or {}
    verdict    = body.get('verdict', 'NORMAL')
    confidence = float(body.get('confidence', 0.85))
    filename   = body.get('filename', 'image.jpg')

    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key:
        return jsonify({"error": "GROQ_API_KEY not configured"}), 503

    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        user_msg = (
            f"Detection result: {verdict}\n"
            f"Confidence: {confidence * 100:.1f}%\n"
            f"Filename: {filename}\n"
            "Provide the textile QC analysis as JSON."
        )

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg}
            ],
            max_tokens=180,
            temperature=0.25,
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)

        # Validate expected keys exist
        for key in ("explanation", "likely_cause", "recommendation"):
            if key not in result:
                raise ValueError(f"Missing key: {key}")

        result["demo_mode"] = False
        return jsonify(result)

    except Exception as e:
        logger.error(f"Groq explain failed: {e}")
        fallback = FALLBACK_RESPONSES.get(verdict, FALLBACK_RESPONSES["NORMAL"]).copy()
        fallback["demo_mode"] = True
        return jsonify(fallback)
