"""Infraestrutura central de ícones do VighnaStudy.

QtAwesome é opcional em tempo de desenvolvimento para que o projeto continue
abrindo mesmo se a dependência ainda não tiver sido instalada. O build oficial
instala QtAwesome e inclui suas fontes no executável.
"""

from pathlib import Path

from PySide6.QtGui import QIcon

from tema import normalizar_tema
from ui.design import qtawesome_color

try:
    import qtawesome as qta
except ImportError:  # fallback seguro para ambientes ainda não preparados
    qta = None


CORES_ICONES = {
    "claro": {
        "acao": "icon.action",
        "destaque": "icon.highlight",
        "configuracao": "icon.configuration",
    },
    "escuro": {
        "acao": "icon.action",
        "destaque": "icon.highlight",
        "configuracao": "icon.configuration",
    },
    "futurista": {
        "acao": "icon.action",
        "destaque": "icon.highlight",
        "configuracao": "icon.configuration",
    },
}


def qtawesome_disponivel():
    return qta is not None


def cor_icone(tema="claro", papel="acao"):
    tema = normalizar_tema(tema)
    token = CORES_ICONES.get(tema, CORES_ICONES["claro"]).get(
        papel,
        CORES_ICONES[tema]["acao"],
    )
    return qtawesome_color(tema, token)


def criar_icone(
    nome,
    *,
    tema="claro",
    papel="acao",
    fallback_path=None,
):
    """Cria um QIcon via QtAwesome, com fallback opcional para arquivo local."""
    if qta is not None:
        try:
            return qta.icon(
                nome,
                color=cor_icone(tema, papel),
            )
        except Exception:
            # Um nome de ícone incompatível não deve impedir a abertura do app.
            pass

    if fallback_path:
        caminho = Path(fallback_path)
        if caminho.exists():
            return QIcon(str(caminho))

    return QIcon()
