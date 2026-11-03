"""Reconstrução sem perdas dos 200 quadros do GIF Home V9 aprovado.

PNG do quadro 0 mais PNGs RGBA de alterações opacas por quadro.
Não usa QMovie, banco de dados, imagens ou bibliotecas externas.
"""
from __future__ import annotations

import base64
from functools import lru_cache
from struct import unpack_from
import zlib
from threading import Lock, Thread

from ui.home_v9_f00 import PACKED as P00
from ui.home_v9_f01 import PACKED as P01
from ui.home_v9_f02 import PACKED as P02
from ui.home_v9_f03 import PACKED as P03
from ui.home_v9_f04 import PACKED as P04
from ui.home_v9_f05 import PACKED as P05
from ui.home_v9_f06 import PACKED as P06
from ui.home_v9_f07 import PACKED as P07

QUADROS = 200
DURACAO_QUADRO_MS = 100
_LOTE = 25
_DADOS = (P00, P01, P02, P03, P04, P05, P06, P07)

@lru_cache(maxsize=8)
def _lote(numero: int) -> tuple[bytes, ...]:
    if not 0 <= numero < len(_DADOS):
        raise IndexError(numero)
    pacote = zlib.decompress(base64.b85decode(_DADOS[numero]))
    qtd = unpack_from('>H', pacote, 0)[0]
    if qtd != _LOTE:
        raise ValueError('Lote Home V9 incompleto')
    cursor = 2
    imagens = []
    for _ in range(qtd):
        tamanho = unpack_from('>I', pacote, cursor)[0]
        cursor += 4
        imagens.append(pacote[cursor:cursor+tamanho])
        cursor += tamanho
    if cursor != len(pacote):
        raise ValueError('Lote Home V9 com bytes excedentes')
    return tuple(imagens)


def obter_png(quadro: int) -> bytes:
    if not 0 <= quadro < QUADROS:
        raise IndexError(quadro)
    return _lote(quadro//_LOTE)[quadro%_LOTE]


# Preaquece os oito lotes de PNG em thread separada, APOS o quadro zero.
# Todas as operacoes nesta thread trabalham apenas em bytes Python;
# QImage/QPainter permanecem exclusivamente no thread de interface Qt.
_preaquecimento_lock = Lock()
_preaquecimento_iniciado = False
_preaquecimento_thread = None

def iniciar_preaquecimento() -> None:
    global _preaquecimento_iniciado, _preaquecimento_thread
    with _preaquecimento_lock:
        if _preaquecimento_iniciado:
            return
        _preaquecimento_iniciado = True
        _preaquecimento_thread = Thread(
            target=_preparar_lotes,
            name='VighnaHomeV9-Precache',
            daemon=True,
        )
        _preaquecimento_thread.start()

def _preparar_lotes() -> None:
    # O lote zero ja foi carregado por obter_png(0) no construtor da Home.
    for numero in range(1, len(_DADOS)):
        _lote(numero)
