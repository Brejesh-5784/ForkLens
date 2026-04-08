# 🚀 ForkLens Quick Start Guide

Get ForkLens running in 5 minutes!

## 📋 Prerequisites

- Python 3.8+
- Git
- 2GB free disk space

## ⚡ Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/Brejesh-5784/phase2.git
cd phase2
```

### 2. Run Setup Script
```bash
python setup_models.py
```

### 3. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 6. Add Your API Keys

**HuggingFace Token:**
1. Go to https://huggingface.co/settings/tokens
2. Create new token
3. Add to `.env`: `HF_TOKEN=hf_your_token_here`

**Qdrant Database:**
1. Sign up at https://cloud.qdrant.io/
2. Create cluster
3. Add credentials to `.env`

### 7. Test Setup
```bash
python test_api.py
```

### 8. Run ForkLens
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser!

## 🎭 Adding Models

### Emotion Model
Place your trained emotion detection model in:
```
final_models/emotion_model/
├── config.json
├── pytorch_model.bin
└── tokenizer files
```

### Literary Texts
Add classic literature files to:
```
gutenberg_books_text/
├── book1.txt
├── book2.txt
└── ...
```

## 🆘 Need Help?

- Check `README.md` for detailed documentation
- Run `python diagnose_qdrant.py` for connection issues
- Ensure all API keys are correctly set in `.env`

## 🎉 You're Ready!

ForkLens is now ready to provide literary wisdom for life's crossroads!