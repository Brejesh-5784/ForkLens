#!/usr/bin/env python3
"""
Instructions to set up a new Qdrant instance:

1. Go to https://cloud.qdrant.io/
2. Create a new cluster
3. Choose a region close to you (US-East, EU-West, etc.)
4. Get the new URL and API key
5. Update your .env file with new credentials
6. Re-upload your data using upload_qdrant.ipynb

New .env format:
QDRANT_HOST=https://your-new-cluster-url.qdrant.io
QDRANT_API_KEY=your-new-api-key
"""

# Test script for new instance
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

def test_new_instance():
    load_dotenv()
    
    # Update these with your new credentials
    NEW_HOST = input("Enter new Qdrant host URL: ")
    NEW_API_KEY = input("Enter new API key: ")
    
    try:
        client = QdrantClient(url=NEW_HOST, api_key=NEW_API_KEY, timeout=30)
        collections = client.get_collections()
        print(f"✅ New instance working! Collections: {[c.name for c in collections.collections]}")
        
        # Update .env file
        with open('.env', 'r') as f:
            content = f.read()
        
        # Replace old credentials
        content = content.replace(os.getenv('QDRANT_HOST', ''), NEW_HOST)
        content = content.replace(os.getenv('QDRANT_API_KEY', ''), NEW_API_KEY)
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print("✅ .env file updated!")
        
    except Exception as e:
        print(f"❌ New instance test failed: {e}")

if __name__ == "__main__":
    test_new_instance()