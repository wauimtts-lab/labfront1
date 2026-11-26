"""Поиск: семантический (ChromaDB + sentence-transformers) и запасной по ключевым словам.

Если модель не скачалась или библиотеки недоступны, приложение не падает:
поиск переключается на ключевые слова.
"""
import os
import re

from .parser import get_exhibits_cached

MODEL_NAME = os.getenv('EMBEDDING_MODEL', 'paraphrase-multilingual-MiniLM-L12-v2')

_model = None
_collection = None
_semantic_ok = None  # None = ещё не пробовали

STOP_WORDS = {
    'покажи', 'расскажи', 'какие', 'какой', 'какая', 'что', 'как', 'где', 'есть',
    'про', 'все', 'для', 'мне', 'хочу', 'можно', 'работы', 'работ', 'экспонаты',
    'кто', 'написал', 'картина', 'картины', 'картину', 'картин',
}


def _doc_text(e):
    return (
        f"{e['name']}. {e['author']}, {e['year']}. {e['style']}, {e['epoch']}. "
        f"{', '.join(e['themes'])}. {e['museum']}. {e['body']}"
    )


def _init_semantic():
    global _model, _collection, _semantic_ok
    if _semantic_ok is not None:
        return _semantic_ok
    try:
        from sentence_transformers import SentenceTransformer
        import chromadb

        _model = SentenceTransformer(MODEL_NAME)
        client = chromadb.Client()
        _collection = client.get_or_create_collection('exhibits')
        if _collection.count() == 0:
            for e in get_exhibits_cached():
                text = _doc_text(e)
                _collection.add(
                    ids=[e['id']],
                    embeddings=[_model.encode(text).tolist()],
                    documents=[text],
                    metadatas=[{'name': e['name']}],
                )
        _semantic_ok = True
    except Exception as exc:  # noqa: BLE001
        print(f'[search] семантический поиск недоступен, используется поиск по ключевым словам: {exc}')
        _semantic_ok = False
    return _semantic_ok


def _stem(token: str) -> str:
    """Грубая «основа»: отбрасываем окончание, чтобы «Айвазовского» находило «Айвазовский»."""
    n = len(token)
    cut = 3 if n >= 8 else 2 if n >= 6 else 1 if n >= 4 else 0
    return token[: n - cut]


def keyword_search(query: str, top_k: int = 3):
    tokens = [t for t in re.findall(r'\w+', query.lower()) if len(t) >= 3 and t not in STOP_WORDS]
    scored = []
    for e in get_exhibits_cached():
        hay = _doc_text(e).lower()
        score = sum(1 for t in tokens if _stem(t) in hay)
        if score:
            scored.append((score, e))
    scored.sort(key=lambda x: (-x[0], x[1]['name']))
    return [{'id': e['id'], 'name': e['name']} for _, e in scored[:top_k]]


def semantic_search(query: str, top_k: int = 3):
    if not _init_semantic():
        return keyword_search(query, top_k)
    n = min(top_k, _collection.count())
    if n == 0:
        return []
    emb = _model.encode(query).tolist()
    res = _collection.query(query_embeddings=[emb], n_results=n)
    return [
        {'id': res['ids'][0][i], 'name': res['metadatas'][0][i]['name']}
        for i in range(len(res['ids'][0]))
    ]
