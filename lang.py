import json
import os

_lang = 'en'
_trans = {}

def load(lang=None):
    """Load translations from locales/<lang>.json. If not found, fall back to keys."""
    global _lang, _trans
    if lang:
        _lang = lang
    path = os.path.join(os.path.dirname(__file__), 'locales', f'{_lang}.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            _trans = json.load(f)
    except Exception:
        _trans = {}

def t(key, **kwargs):
    s = _trans.get(key, key)
    try:
        return s.format(**kwargs)
    except Exception:
        return s
