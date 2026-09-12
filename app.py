import os
import uvicorn
from Backend.app.main import app

# Ensure HF spaces use port 7860
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=7860)
