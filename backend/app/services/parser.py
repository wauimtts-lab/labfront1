import os
from functools import lru_cache

import frontmatter

EXHIBITS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'exhibits')


def _first_paragraph(text: str) -> str:
    """Первый абзац без заголовков и списков (запасной вариант описания)."""
    for block in text.split('\n\n'):
        block = block.strip()
        if block and not block.startswith('#') and not block.startswith('-'):
            return block
    return ''


def load_exhibits():
    exhibits = []
    for filename in sorted(os.listdir(EXHIBITS_DIR)):
        if not filename.endswith('.md'):
            continue
        path = os.path.join(EXHIBITS_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        meta = dict(post.metadata)
        meta.setdefault('id', filename[:-3].replace('_', '-'))
        meta.setdefault('themes', [])
        meta.setdefault('hall', None)
        meta['body'] = post.content
        meta.setdefault('description', _first_paragraph(post.content))
        exhibits.append(meta)

    return exhibits


@lru_cache(maxsize=1)
def get_exhibits_cached():
    return load_exhibits()
