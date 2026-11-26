import os

from .parser import get_exhibits_cached
from .search import semantic_search


def _describe(e) -> str:
    return f"«{e['name']}» — {e['author']}, {e['year']}, {e['style']}. {e['description']}"


def answer_question(question: str) -> dict:
    hits = semantic_search(question, top_k=3)
    by_id = {e['id']: e for e in get_exhibits_cached()}
    exhibits = [by_id[h['id']] for h in hits if h['id'] in by_id]

    # Если есть ключ LLM, используем его
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and exhibits:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key, base_url=os.getenv('OPENAI_BASE_URL') or None)
            context = '\n\n'.join(f"{e['name']}:\n{_describe(e)}\n{e['body']}" for e in exhibits)
            resp = client.chat.completions.create(
                model=os.getenv('LLM_MODEL', 'gpt-4o-mini'),
                messages=[{
                    'role': 'user',
                    'content': (
                        'Ты музейный гид. Ответь на вопрос, используя только описания экспонатов ниже. '
                        'Если ответа в них нет, так и скажи.\n\n'
                        f'Экспонаты:\n{context}\n\nВопрос: {question}'
                    ),
                }],
            )
            return {
                'answer': resp.choices[0].message.content,
                'sources': [e['name'] for e in exhibits],
            }
        except Exception as exc:  # noqa: BLE001
            # Не роняем запрос, если LLM недоступна
            print(f'[rag] LLM недоступна, используется fallback: {exc}')

    # Fallback без LLM: показываем найденные экспонаты
    if not exhibits:
        return {'answer': 'Ничего не найдено по вашему запросу. Попробуйте указать автора, эпоху, стиль или тему.', 'sources': []}

    answer = f'Лучше всего подходит {_describe(exhibits[0])}'
    if len(exhibits) > 1:
        others = ', '.join(f"«{e['name']}»" for e in exhibits[1:])
        answer += f' Также по вашему запросу: {others}. Откройте экспонат, чтобы увидеть подробности.'
    return {'answer': answer, 'sources': [e['name'] for e in exhibits]}
