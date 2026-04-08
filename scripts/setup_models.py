#!/usr/bin/env python3
"""
ForkLens Setup Script
====================
Automated setup for the ForkLens literary counseling system.
Run this after cloning the repository from GitHub.

Usage: python setup_models.py
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Print ForkLens setup banner."""
    print("""
📚 =============================================== 📚
    ForkLens - Literary Wisdom for Life's Crossroads
📚 =============================================== 📚
    
🚀 Setting up your ForkLens environment...
    """)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_directories():
    """Create necessary directories."""
    directories = [
        "final_models/emotion_model",
        "final_models/super_model", 
        "final_models/tokenizer",
        "gutenberg_books_text"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created: {directory}")

def setup_environment():
    """Setup environment file."""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("📝 Copy .env.example to .env and add your API keys:")
            print("   cp .env.example .env")
        else:
            print("⚠️  .env.example not found. Create .env manually.")
    else:
        print("✅ .env file already exists")

def install_dependencies():
    """Guide user through dependency installation."""
    print("""
📦 INSTALL DEPENDENCIES:
   
   1. Create virtual environment:
      python -m venv venv
      
   2. Activate virtual environment:
      # On macOS/Linux:
      source venv/bin/activate
      # On Windows:
      venv\\Scripts\\activate
      
   3. Install requirements:
      pip install -r requirements.txt
    """)

def setup_models():
    """Guide user through model setup."""
    print("""
🤖 MODEL SETUP REQUIRED:

1. 🎭 EMOTION MODEL:
   - Train your emotion detection model OR
   - Download pre-trained emotion model
   - Place files in: ./final_models/emotion_model/
   - Required: config.json, pytorch_model.bin, tokenizer files

2. 📚 GUTENBERG BOOKS:
   - Download classic literature from Project Gutenberg
   - Place .txt files in: ./gutenberg_books_text/
   - Recommended: 40+ books for best results

3. 🗄️ QDRANT DATABASE:
   - Sign up at: https://cloud.qdrant.io/
   - Create new cluster
   - Upload your literary data using: upload_qdrant.ipynb
    """)

def setup_api_keys():
    """Guide user through API key setup."""
    print("""
🔑 API KEYS SETUP:

1. 🤗 HUGGINGFACE API:
   - Go to: https://huggingface.co/settings/tokens
   - Create new token
   - Add to .env: HF_TOKEN=hf_your_token_here

2. 🗄️ QDRANT DATABASE:
   - Get cluster URL and API key from Qdrant dashboard
   - Add to .env: 
     QDRANT_HOST=https://your-cluster.qdrant.io
     QDRANT_API_KEY=your_api_key_here
    """)

def test_setup():
    """Guide user through testing."""
    print("""
🧪 TEST YOUR SETUP:

1. Test API connections:
   python test_api.py

2. Test full system:
   python anaar.py

3. Run the app:
   streamlit run app.py

4. Open browser: http://localhost:8501
    """)

def main():
    """Main setup function."""
    print_banner()
    
    try:
        check_python_version()
        create_directories()
        setup_environment()
        install_dependencies()
        setup_models()
        setup_api_keys()
        test_setup()
        
        print("""
🎉 SETUP COMPLETE!

📖 Next Steps:
   1. Follow the instructions above
   2. Check README.md for detailed documentation
   3. Join our community for support

🚀 Ready to provide literary wisdom!
        """)
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()