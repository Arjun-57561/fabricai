from flask import Flask, request, Response
from flask_cors import CORS
import random, math

app = Flask(__name__)
CORS(app)

@app.route('/api/synthetic-sample', methods=['GET'])
def synthetic_sample():
    seed = request.args.get('seed', type=int,
                            default=random.randint(1, 9999))
    random.seed(seed)

    # Background fabric grid
    lines = ""
    for i in range(0, 200, 5):
        a_h = round(random.uniform(0.03, 0.09), 3)
        a_v = round(random.uniform(0.03, 0.09), 3)
        w_h = round(random.uniform(1.5, 3.0), 2)
        w_v = round(random.uniform(1.5, 3.0), 2)
        lines += (
            f'<line x1="0" y1="{i}" x2="200" y2="{i}" '
            f'stroke="rgba(255,255,255,{a_h})" stroke-width="{w_h}"/>\n'
            f'<line x1="{i}" y1="0" x2="{i}" y2="200" '
            f'stroke="rgba(255,255,255,{a_v})" stroke-width="{w_v}"/>\n'
        )

    # Defect blob — color varies by seed
    palette = [
        ("rgba(255,80,80,0.3)",   "rgba(255,80,80,0.08)"),
        ("rgba(255,200,60,0.3)",  "rgba(255,200,60,0.08)"),
        ("rgba(80,160,255,0.3)",  "rgba(80,160,255,0.08)"),
        ("rgba(180,80,255,0.3)",  "rgba(180,80,255,0.08)"),
    ]
    fill, glow = palette[seed % 4]
    ax = random.randint(40, 160)
    ay = random.randint(40, 160)
    ar = random.randint(12, 28)

    # Noise specks
    specks = ""
    for _ in range(random.randint(2, 6)):
        sx = random.randint(10, 190)
        sy = random.randint(10, 190)
        sr = round(random.uniform(1, 4), 1)
        specks += (f'<circle cx="{sx}" cy="{sy}" r="{sr}" '
                   f'fill="rgba(255,255,255,0.25)"/>\n')

    # Optional weft break line
    weft = ""
    if random.random() > 0.55:
        wy = random.randint(50, 150)
        weft = (f'<line x1="0" y1="{wy}" x2="200" y2="{wy}" '
                f'stroke="rgba(0,0,0,0.45)" stroke-width="2.5"/>\n')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" fill="#0a0a10"/>
  {lines}
  <circle cx="{ax}" cy="{ay}" r="{ar + 10}" fill="{glow}"/>
  <circle cx="{ax}" cy="{ay}" r="{ar}" fill="{fill}"/>
  {specks}
  {weft}
</svg>'''

    return Response(svg, mimetype='image/svg+xml')
