from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router

load_dotenv()

app = FastAPI(title='Cultural Guide API', version='0.1.0')

# CORS: разрешаем запросы от React dev-сервера (и от адресов GitHub Codespaces)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
    ],
    allow_origin_regex=r'https://.*\.app\.github\.dev',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router)


@app.get('/health')
def health():
    return {'status': 'ok'}
