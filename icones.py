"""Infraestrutura central de ícones do VighnaStudy.

QtAwesome é opcional em tempo de desenvolvimento para que o projeto continue
abrindo mesmo se a dependência ainda não tiver sido instalada. O build oficial
instala QtAwesome e inclui suas fontes no executável.
"""

from pathlib import Path

from PySide6.QtGui import QIcon

from tema import normalizar_tema

try:
    import qtawesome as qta
except ImportError:  # fallback seguro para ambientes ainda não preparados
    qta = None


CORES_ICONES = {
    "claro": {
        "acao": "#355874",
        "destaque": "#FFFFFF",
        "configuracao": "#0F3989",
    },
    "escuro": {
        "acao": "#BED0E1",
        "destaque": "#FFFFFF",
        "configuracao": "#BED0E1",
    },
    "futurista": {
        "acao": "#B6D9E8",
        "destaque": "#FFFFFF",
        "configuracao": "#B6D9E8",
    },
}


def qtawesome_disponivel():
    return qta is not None


def cor_icone(tema="claro", papel="acao"):
    tema = normalizar_tema(tema)
    return CORES_ICONES.get(tema, CORES_ICONES["claro"]).get(
        papel,
        CORES_ICONES[tema]["acao"],
    )


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
