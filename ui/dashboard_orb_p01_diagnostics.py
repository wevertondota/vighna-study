"""P01: diagnóstico limitado à interação da esfera Planejamento.

Registra somente estados técnicos, sem textos do usuário, conteúdo do banco ou
localização do cursor fora da região do botão. Nunca interrompe a interface.
O ficheiro é criado fora da instalação, em LOCALAPPDATA.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_LOG_NAME = 'P01_planejamento.jsonl'
_MAX_BYTES = 512 * 1024


def _directories():
    candidates = []
    if os.environ.get('LOCALAPPDATA'):
        candidates.append(Path(os.environ['LOCALAPPDATA']) / 'VighnaStudy' / 'diagnosticos')
    if os.environ.get('USERPROFILE'):
        candidates.append(Path(os.environ['USERPROFILE']) / 'VighnaStudy_P01')
    candidates.append(Path(tempfile.gettempdir()) / 'VighnaStudy_P01')
    return candidates


def record(event: str, **fields) -> None:
    """Não gerar erros em eventos de interface; somente campos técnicos simples."""
    try:
        allowed = (bool, int, float, str, type(None))
        payload = {'utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                   'event': str(event)[:48]}
        for key, value in fields.items():
            if isinstance(value, allowed):
                payload[str(key)[:40]] = value[:96] if isinstance(value, str) else value
        data = json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n'
        for folder in _directories():
            try:
                folder.mkdir(parents=True, exist_ok=True)
                target = folder / _LOG_NAME
                if target.exists() and target.stat().st_size > _MAX_BYTES:
                    backup = folder / 'P01_planejamento_anterior.jsonl'
                    target.replace(backup)
                with target.open('a', encoding='utf-8') as log:
                    log.write(data)
                return
            except (OSError, ValueError):
                continue
    except Exception:
        pass  # Falhas do diagnóstico NUNCA afetam a interação Qt.
