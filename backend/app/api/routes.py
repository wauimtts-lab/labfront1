from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..schemas import AskRequest, AskResponse, Exhibit
from ..services import graph as graph_service
from ..services.parser import get_exhibits_cached
from ..services.rag import answer_question

router = APIRouter(prefix='/api')


def _to_exhibit(r) -> Exhibit:
    return Exhibit(
        id=r['id'],
        name=r['name'],
        author=r['author'],
        year=r['year'],
        type=r['type'],
        epoch=r['epoch'],
        style=r['style'],
        themes=r['themes'],
        museum=r['museum'],
        hall=r.get('hall'),
        description=r['description'],
    )


def _find(exhibit_id: str):
    for r in get_exhibits_cached():
        if r['id'] == exhibit_id:
            return r
    raise HTTPException(status_code=404, detail='Exhibit not found')


@router.get('/exhibits', response_model=List[Exhibit])
def list_exhibits(
    author: Optional[str] = None,
    epoch: Optional[str] = None,
    style: Optional[str] = None,
    theme: Optional[str] = None,
    museum: Optional[str] = None,
):
    exhibits = get_exhibits_cached()
    if any([author, epoch, style, theme, museum]):
        ids = set(graph_service.filter_ids(author=author, epoch=epoch, style=style, theme=theme, museum=museum))
        exhibits = [r for r in exhibits if r['id'] in ids]
    return [_to_exhibit(r) for r in exhibits]


@router.get('/exhibits/{exhibit_id}', response_model=Exhibit)
def get_exhibit(exhibit_id: str):
    return _to_exhibit(_find(exhibit_id))


@router.get('/exhibits/{exhibit_id}/related', response_model=List[Exhibit])
def get_related(exhibit_id: str, limit: int = Query(3, ge=1, le=10)):
    _find(exhibit_id)
    by_id = {r['id']: r for r in get_exhibits_cached()}
    return [_to_exhibit(by_id[i]) for i in graph_service.related(exhibit_id, limit)]


@router.get('/graph')
def graph_info():
    return graph_service.stats()


@router.post('/ask', response_model=AskResponse)
def ask(payload: AskRequest):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail='Query is empty')
    return answer_question(payload.query)
