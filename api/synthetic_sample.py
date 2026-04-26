from flask import Flask, request, Response
from flask_cors import CORS
import random
import math

app = Flask(__name__)
CORS(app)

@app.route('/api/synthetic-sample', methods=['GET', 'OPTIONS'])
def synthetic_sample():
    if request.method == 'OPTIONS':
        return '', 200

    seed = request.args.get('seed', type=int, default=random.randint(1, 1000))
    random.seed(seed)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
    <rect width="200" height="200" fill="#0f0f13" />'''
    
    for i in range(0, 200, 5):
        h_color = f"rgba(255, 255, 255, {random.uniform(0.02, 0.08)})"
        v_color = f"rgba(255, 255, 255, {random.uniform(0.02, 0.08)})"
        svg += f'<line x1="0" y1="{i}" x2="200" y2="{i}" stroke="{h_color}" stroke-width="{random.uniform(1.5, 3)}" />\n'
        svg += f'<line x1="{i}" y1="0" x2="{i}" y2="200" stroke="{v_color}" stroke-width="{random.uniform(1.5, 3)}" />\n'

    ax = random.randint(30, 170)
    ay = random.randint(30, 170)
    ar = random.randint(10, 25)
    
    if seed % 3 == 0:
        fill_col = "rgba(255, 80, 80, 0.25)"
    elif seed % 3 == 1:
        fill_col = "rgba(255, 200, 80, 0.25)"
    else:
        fill_col = "rgba(100, 100, 255, 0.25)"
        
    svg += f'<circle cx="{ax}" cy="{ay}" r="{ar}" fill="{fill_col}" filter="blur(3px)" />\n'
    
    for _ in range(random.randint(1, 4)):
        kx = random.randint(20, 180)
        ky = random.randint(20, 180)
        svg += f'<circle cx="{kx}" cy="{ky}" r="{random.uniform(1.5, 4)}" fill="rgba(255, 255, 255, 0.3)" />\n'
        
    if random.random() > 0.5:
        wy = random.randint(40, 160)
        svg += f'<line x1="0" y1="{wy}" x2="200" y2="{wy}" stroke="rgba(0,0,0,0.4)" stroke-width="2" />\n'

    svg += '</svg>'
    
    return Response(svg, mimetype='image/svg+xml', headers={"Access-Control-Allow-Origin": "*"})
