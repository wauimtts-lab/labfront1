"""Граф знаний (NetworkX) по онтологии из docs/ontology.md.

Узлы: exhibit, author, epoch, style, theme, museum.
Связи: создан, относится_к_эпохе, выполнен_в_стиле, посвящён,
находится_в, работал_в_стиле.
"""
from functools import lru_cache

import networkx as nx

from .parser import get_exhibits_cached

# Насколько общий сосед делает два экспоната «похожими»
WEIGHTS = {'author': 3, 'theme': 2, 'style': 2, 'epoch': 1, 'museum': 1}


def _split_authors(value):
    return [a.strip() for a in str(value).split(',') if a.strip()]


def _link(g, src, kind, value, relation):
    node = f'{kind}:{value}'
    if node not in g:
        g.add_node(node, kind=kind, label=value)
    g.add_edge(src, node, relation=relation)
    return node


@lru_cache(maxsize=1)
def get_graph():
    g = nx.DiGraph()
    for e in get_exhibits_cached():
        ex = f"exhibit:{e['id']}"
        g.add_node(ex, kind='exhibit', exhibit_id=e['id'], label=e['name'])

        style_node = _link(g, ex, 'style', e['style'], 'выполнен_в_стиле')
        for author in _split_authors(e['author']):
            author_node = _link(g, ex, 'author', author, 'создан')
            g.add_edge(author_node, style_node, relation='работал_в_стиле')
        _link(g, ex, 'epoch', e['epoch'], 'относится_к_эпохе')
        _link(g, ex, 'museum', e['museum'], 'находится_в')
        for theme in e['themes']:
            _link(g, ex, 'theme', theme, 'посвящён')
    return g


def related(exhibit_id: str, limit: int = 3):
    """id экспонатов, похожих на данный: по общим автору, стилю, теме, эпохе."""
    g = get_graph()
    node = f'exhibit:{exhibit_id}'
    if node not in g:
        return []
    mine = set(g.successors(node))
    scores = {}
    for other, data in g.nodes(data=True):
        if data['kind'] != 'exhibit' or other == node:
            continue
        shared = mine & set(g.successors(other))
        score = sum(WEIGHTS.get(g.nodes[n]['kind'], 0) for n in shared)
        if score:
            scores[data['exhibit_id']] = score
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    return [i for i, _ in ranked[:limit]]


def filter_ids(**criteria):
    """Фильтр по связям: author, epoch, style, theme, museum (подстрока, без регистра)."""
    g = get_graph()
    result = []
    for node, data in g.nodes(data=True):
        if data['kind'] != 'exhibit':
            continue
        ok = True
        for kind, query in criteria.items():
            if not query:
                continue
            q = query.lower()
            if not any(
                g.nodes[s]['kind'] == kind and q in g.nodes[s]['label'].lower()
                for s in g.successors(node)
            ):
                ok = False
                break
        if ok:
            result.append(data['exhibit_id'])
    return result


def stats():
    g = get_graph()
    kinds = {}
    for _, data in g.nodes(data=True):
        kinds[data['kind']] = kinds.get(data['kind'], 0) + 1
    return {'nodes': g.number_of_nodes(), 'edges': g.number_of_edges(), 'by_kind': kinds}
