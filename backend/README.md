# Бэкенд «Культурный гид» (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Проверка: http://localhost:8000/health, http://localhost:8000/docs (Swagger), http://localhost:8000/api/exhibits.

Эндпоинты:

| Метод | Путь | Что делает |
|---|---|---|
| GET | `/health` | проверка работы |
| GET | `/api/exhibits` | список экспонатов; фильтры `?author=&epoch=&style=&theme=&museum=` |
| GET | `/api/exhibits/{id}` | один экспонат |
| GET | `/api/exhibits/{id}/related` | похожие экспонаты (по графу знаний) |
| GET | `/api/graph` | статистика графа |
| POST | `/api/ask` | вопрос на естественном языке, тело `{"query": "..."}` |

Экспонаты лежат в `exhibits/*.md` (YAML front matter + текст). После добавления файла перезапустите сервер (данные кэшируются).
