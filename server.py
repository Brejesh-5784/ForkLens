import uvicorn
from forklens.api import app

if __name__ == "__main__":
    uvicorn.run("forklens.api:app", host="0.0.0.0", port=8000, reload=True)
