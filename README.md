# FabricAI — Textile Defect Detection

## Quick Deploy to Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fyour-username%2Ffabricai)

## Setup (3 steps)
1. Push weights to Hugging Face Hub
2. Set environment variables in Vercel dashboard
3. Deploy

## Step 1 — Upload model weights to Hugging Face Hub
```python
from huggingface_hub import HfApi
api = HfApi()
api.upload_file(
    path_or_fileobj="D:/GANPRO/textile_dataset/checkpoints/classifier_gan_augmented_best.pth",
    path_in_repo="best_model_augmented.pth",
    repo_id="Asharjun/fabricai-weights",
    repo_type="model",
    token="<YOUR_HUGGINGFACE_TOKEN>"
)
```

## Step 2 — Vercel Environment Variables
| Variable | Value | Required |
|---|---|---|
| HF_MODEL_REPO | your-username/fabricai-weights | Yes |
| HF_TOKEN | hf_xxx... | Only for private repos |

## Step 3 — Deploy
```bash
npm i -g vercel
vercel --prod
```

## Local Development
```bash
pip install -r requirements.txt
vercel dev
# Open http://localhost:3000
```

## Project Structure
```text
fabricai/
├── api/
│   ├── predict.py            ← POST /api/predict (image upload → inference)
│   ├── project_stats.py      ← GET  /api/project-stats (metrics + dataset info)
│   ├── model_info.py         ← GET  /api/model-info (architecture details)
│   └── synthetic_sample.py  ← GET  /api/synthetic-sample (random sample image)
├── public/
│   └── index.html            ← Complete animated single-page frontend
├── data/
│   ├── metrics.json          ← Hardcoded from real experiment results
│   ├── defect_types.json     ← Defect type distribution table data
│   └── training_logs.json    ← Epoch-by-epoch training curves data
├── requirements.txt          ← CPU-only torch, trimmed for 500MB Vercel limit
├── vercel.json               ← Routing, Python runtime, function config
├── .vercelignore             ← Exclude heavy files from bundle
└── README.md                 ← Setup + deploy instructions
```

## Results
| Config | Val Acc | ROC-AUC | Defect Recall |
|---|---|---|---|
| Baseline | 81.51% | 0.8832 | 88.89% |
| GAN-Augmented | **83.19%** | **0.9197** | **94.44%** |
