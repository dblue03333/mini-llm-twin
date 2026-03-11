from fastapi import FastAPI
from pydantic import BaseModel, Field
from typin import List, Dict, Any

app = FastAPI(title='mini-llm-twin', version='0.1.0')

@app.get('/health')
def health():
    return {'status': 'ok'}
