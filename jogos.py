import random
from functools import lru_cache
from string import Template
import time
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QRectF, QSize, QEvent, QPointF
from PySide6.QtGui import (
    QPainter, QPalette, QColor, QPen, QBrush, QIcon, QPixmap,
    QPainterPath, QLinearGradient, QRadialGradient, QFont,
)
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QFrame,
    QSpinBox,
    QSizePolicy,
    QMessageBox,
    QScrollArea,
    QButtonGroup,
    QSplitter,
    QGraphicsDropShadowEffect,
)

from banco import registrar_resultado_jogo, obter_recordes_jogos
from ui.arena_premium_stats_f15 import obter_indicadores_reais

# Lote 03: registra recursos decorativos no executavel PyInstaller; sem renderizar ainda.
from ui import arena_premium_art as _arena_premium_art
# F04/18: paisagem cinematografica isolada, com fallback para a arte do Lote 03.
from ui import arena_premium_hero_f04 as _arena_hero_f04
from ui import arena_premium_forest_f10 as _arena_forest_f10
from ui import arena_chimp_bg01_arte as _arena_chimp_bg01_arte



# F02/18 — Tokens visuais LOCAIS da Arena Premium 2.0.
# Não alterar tema.py, QSS global ou cores dos cinco motores de jogo.
# As proporções dos controles ficam para F03; a iluminação cênica para F04/F16.
ARENA_F02_TOKENS = {
    "canvas": "#061122",
    "panel_start": "#082941",
    "panel_middle": "#091C32",
    "panel_end": "#0C2040",
    "surface": "#091F38",
    "surface_hover": "#133D5B",
    "stroke": "#347EAE",
    "stroke_bright": "#64DEFF",
    "cyan": "#26DCFA",
    "cyan_bright": "#90EEFF",
    "cyan_active": "#08BCEB",
    "violet": "#A787F5",
    "gold": "#F4C96B",  # reservado ao card de trofeu real do F12
    "text_main": "#F2FAFF",
    "text_sub": "#BDD9E9",
    "text_muted": "#9FC4D9",
    "disabled": "#7897AC",
    "shadow_alpha": 60,
    "shadow_blur": 13,
    "radius_large": 13,
    "radius_button": 9,
    "focus_px": 2,
}


def _arena_f02_qss(regiao):
    """QSS sempre restringido a objectName; regras tipadas preservam foco e estados."""
    t = ARENA_F02_TOKENS
    estilos = {
        "header": r"""
            QFrame#pauseHubPremiumHeader {
                background: transparent; border: none; border-radius: ${radius_large}px;
            }
            QFrame#pauseHubPremiumHeader QLabel#pauseHubTitle {
                color: #F7FCFF; font-size: 26px; font-weight: 800;
                background: transparent; border: none; padding: 0px;
            }
            QFrame#pauseHubPremiumHeader QLabel#pauseHubSubtitle {
                color: ${text_sub}; font-size: 11px;
                background: transparent; border: none; padding: 0px;
            }
            QFrame#pauseHubPremiumHeader QPushButton#pauseBackButton {
                color: #F3FBFF; font-size: 12px; font-weight: 700;
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #0D3357, stop:0.5 #082644, stop:1 #051A33);
                border: 1px solid ${stroke_bright};
                border-radius: ${radius_button}px; padding: 7px 14px;
                min-height: 25px;
            }
            QFrame#pauseHubPremiumHeader QPushButton#pauseBackButton:hover:!disabled {
                background: ${surface_hover}; border: 1px solid ${cyan_bright};
            }
            QFrame#pauseHubPremiumHeader QPushButton#pauseBackButton:pressed {
                background: #0B324B;
            }
            QFrame#pauseHubPremiumHeader QPushButton#pauseBackButton:focus {
                border: ${focus_px}px solid ${cyan_bright};
            }
            QFrame#pauseHubPremiumHeader QPushButton#pauseBackButton:disabled {
                color: ${disabled}; border-color: ${stroke};
            }
        """,
        "timer": r"""
            QFrame#pauseTimerPanel {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0A3453, stop:0.34 #081C35,
                    stop:0.78 #092039, stop:1 #0B2A48);
                border: 1px solid #329FCA; border-radius: ${radius_large}px;
            }
            QFrame#pauseTimerPanel QLabel { background: transparent; border: 0px; }
            QFrame#pauseTimerPanel QLabel#pauseTimerHeading {
                color: ${text_main}; font-size: 15px; font-weight: 800;
            }
            QFrame#pauseTimerPanel QLabel#pauseTimerStatus {
                color: ${text_sub}; font-size: 11px;
            }
            QFrame#pauseTimerPanel QFrame#pausePresetCluster {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #0C2B45, stop:0.42 #091D35, stop:1 #06162C);
                border: 1px solid #2B81AC; border-radius: 12px;
            }
            QFrame#pauseTimerPanel QPushButton[pausePreset="true"] {
                background: transparent; color: #BAD9EC;
                border: 1px solid transparent; border-radius: 9px;
                font-size: 12px; font-weight: 700; padding: 5px 4px;
            }
            QFrame#pauseTimerPanel QPushButton[pausePreset="true"]:checked {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #1CDCF9, stop:0.46 #08AFE7, stop:1 #067FC4);
                color: #FFFFFF; border: 1px solid #68E9FF;
            }
            QFrame#pauseTimerPanel QPushButton[pausePreset="true"]:hover:!disabled {
                background-color: #164160; border: 1px solid #90EEFF;
            }
            QFrame#pauseTimerPanel QPushButton[pausePreset="true"]:checked:hover:!disabled {
                background-color: #168DBF;
            }
            QFrame#pauseTimerPanel QPushButton[pausePreset="true"]:focus {
                border: 2px solid #B2F5FF;
            }
            QFrame#pauseTimerPanel QFrame#pauseClockFocus {
                background: transparent; border: none;
                border-left: 1px solid #245D81;
            }
            QFrame#pauseTimerPanel QLabel#pauseTimeCaption {
                color: #B8D7E9; font-size: 11px;
            }
            QFrame#pauseTimerPanel QLabel#pauseTimerValue {
                color: #30ECFF; font-size: 27px; font-weight: 800;
            }
            QFrame#pauseTimerPanel QPushButton#pausePrimaryButton {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #55EFFF, stop:0.24 #1AD7F6,
                    stop:0.62 #069DCB, stop:1 #066EAA);
                color: #FFFFFF; border: 1px solid #83F3FF;
                border-radius: 11px; padding: 6px 12px;
                font-size: 12px; font-weight: 800;
            }
            QFrame#pauseTimerPanel QPushButton#pausePrimaryButton:hover:!disabled {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #76EEFF, stop:1 #089BD2);
                border: 1px solid #FFFFFF;
            }
            QFrame#pauseTimerPanel QPushButton#pausePrimaryButton:pressed {
                background-color: #075B91;
            }
            QFrame#pauseTimerPanel QPushButton#pausePrimaryButton:focus {
                border: 2px solid #C0F7FF;
            }
            QFrame#pauseTimerPanel QPushButton#pauseSecondaryButton {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #0B2A49, stop:1 #061B33);
                color: ${text_main}; border: 1px solid #286D99;
                border-radius: 10px; padding: 6px 9px;
                font-size: 12px; font-weight: 700;
            }
            QFrame#pauseTimerPanel QPushButton#pauseSecondaryButton:hover:!disabled {
                background-color: #123F5E; border-color: #90EEFF;
            }
            QFrame#pauseTimerPanel QPushButton#pauseSecondaryButton:focus {
                border: 2px solid #B2F5FF;
            }
            QFrame#pauseTimerPanel QPushButton#pauseTimerSettingsButton {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #0D2A49, stop:1 #07172E);
                border: 1px solid #2D709C; border-radius: 11px;
            }
            QFrame#pauseTimerPanel QPushButton#pauseTimerSettingsButton:hover:!disabled {
                border: 1px solid #90EEFF; background-color: #123E5A;
            }
            QFrame#pauseTimerPanel QPushButton#pauseTimerSettingsButton:focus {
                border: 2px solid #B2F5FF;
            }
            QFrame#pauseTimerPanel QPushButton:disabled {
                color: #7390A6; border-color: #31576D;
            }
            QFrame#pauseTimerPanel QSpinBox#pauseCustomMinutes {
                background: ${canvas}; color: ${text_main};
                border: 1px solid #58D8F6; border-radius: 7px;
                padding: 3px; font-size: 11px;
            }
            QFrame#pauseTimerPanel QSpinBox#pauseCustomMinutes:focus {
                border: 2px solid #B2F5FF;
            }
        """,
        "navigation": r"""
            /* F07: somente os cinco seletores Premium, sem efeitos globais. */
            QFrame#pausePremiumGamesNav { background: transparent; border: none; }
            QFrame#pausePremiumGamesNav QPushButton[premiumNav="yes"] {
                color: #CDE4F5;
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #15385A, stop:0.24 #102B4D,
                    stop:0.76 #0A1D39, stop:1 #07162B);
                border: 1px solid #346A91;
                border-top: 1px solid #487EA5;
                border-bottom: 2px solid #24648A;
                border-radius: 13px;
                font-size: 13px; font-weight: 700;
                padding: 4px 7px;
            }
            QFrame#pausePremiumGamesNav QPushButton[premiumNav="yes"]:hover:!checked {
                color: #F1FBFF;
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #17466B, stop:0.55 #10365A, stop:1 #0A2648);
                border: 1px solid #6FC8F2;
                border-bottom: 2px solid #52A8E3;
            }
            QFrame#pausePremiumGamesNav QPushButton[premiumNav="yes"]:checked {
                color: #E9FEFF;
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #1A6988, stop:0.20 #105077,
                    stop:0.68 #092F54, stop:1 #081F3C);
                border: 1px solid #9EEDFF;
                border-top: 1px solid #AEB9FF;
                border-bottom: 3px solid #00DFFF;
                font-weight: 800;
            }
            QFrame#pausePremiumGamesNav QPushButton[premiumNav="yes"]:checked:hover {
                color: #B7FCFF;
                border: 1px solid #BCF9FF;
                border-bottom: 3px solid #4EF8FF;
            }
            QFrame#pausePremiumGamesNav QPushButton[premiumNav="yes"]:focus {
                border: 2px solid #B7F4FF;
                border-bottom: 3px solid #5DEBFF;
            }
            QFrame#pausePremiumGamesNav QPushButton[premiumNav="yes"]:pressed {
                background-color: #0A496A;
                color: #FFFFFF;
            }
            QFrame#pausePremiumGamesNav QPushButton[premiumNav="yes"]:disabled {
                color: #7495B2;
                border-color: #29445F;
            }
        """,
    }
    return Template(estilos[regiao]).substitute(t)


def _arena_f02_glow_discreto(botao):
    """Sombra leve só em um CTA; não afeta layouts, eventos ou jogos."""
    efeito = QGraphicsDropShadowEffect(botao)
    efeito.setBlurRadius(ARENA_F02_TOKENS["shadow_blur"])
    efeito.setOffset(0, 0)
    efeito.setColor(QColor(15, 190, 250, ARENA_F02_TOKENS["shadow_alpha"]))
    botao.setGraphicsEffect(efeito)



# F03/18 — perfis PROPORCIONAIS de geometria (pixels lógicos Qt).
# Valores de reserva, não alteram regras, conteúdo ou estado dos jogos.
# F08-F11 adicionarão componentes reais ao espaço disponível.
ARENA_F03_PERFIS = {
    # faixa : margens H/V, gap geral, altura hero/pausa/navegação/botões e altura mínima da arena
    3: dict(margem_h=22, margem_v=16, gap=11, hero=108, pausa=88, nav=62, tab=58, arena_min=445),  # >=1580
    0: dict(margem_h=18, margem_v=13, gap=9, hero=86, pausa=78, nav=54, tab=52, arena_min=420),    # 1140-1579
    1: dict(margem_h=12, margem_v=10, gap=8, hero=76, pausa=74, nav=50, tab=48, arena_min=420),    # 990-1139
    2: dict(margem_h=10, margem_v=8,  gap=7, hero=68, pausa=72, nav=48, tab=46, arena_min=425),    # 900-989
}

def _arena_f17_faixa_por_largura(largura):
    """Breakpoint em pixels LÓGICOS Qt; DPR não multiplica a largura novamente.

    A função é pura e auditável nas resoluções 1706/1366/1050/900.
    Preserva exatamente as quatro faixas homologadas desde o F03.
    """
    largura = int(largura)
    if largura >= 1580:
        return 3
    if largura >= 1140:
        return 0
    if largura >= 990:
        return 1
    return 2


def _formatar_tempo(segundos):
    try:
        segundos = max(0, int(segundos or 0))
    except Exception:
        segundos = 0
    minutos, resto = divmod(segundos, 60)
    return f"{minutos:02d}:{resto:02d}"


def _repolir(widget):
    try:
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()
    except Exception:
        pass


def _normalizar_forma(forma):
    """Remove linhas/colunas vazias para comparar formas sem depender de translação."""
    linhas = [list(map(int, linha)) for linha in (forma or ())]
    if not linhas:
        return tuple()

    while linhas and not any(linhas[0]):
        linhas.pop(0)
    while linhas and not any(linhas[-1]):
        linhas.pop()
    if not linhas:
        return tuple()

    colunas_ativas = [
        coluna
        for coluna in range(len(linhas[0]))
        if any(linha[coluna] for linha in linhas)
    ]
    if not colunas_ativas:
        return tuple()
    inicio, fim = min(colunas_ativas), max(colunas_ativas) + 1
    return tuple(tuple(linha[inicio:fim]) for linha in linhas)


def _rotacionar_forma_90(forma):
    forma = _normalizar_forma(forma)
    if not forma:
        return forma
    return _normalizar_forma(tuple(zip(*forma[::-1])))


def _espelhar_forma_horizontal(forma):
    """Espelha esquerda <-> direita."""
    forma = _normalizar_forma(forma)
    return _normalizar_forma(tuple(tuple(reversed(linha)) for linha in forma))


def _espelhar_forma_vertical(forma):
    """Espelha cima <-> baixo."""
    forma = _normalizar_forma(forma)
    return _normalizar_forma(tuple(reversed(forma)))


def _aplicar_operacao_forma(forma, operacao):
    if operacao == "rot90":
        return _rotacionar_forma_90(forma)
    if operacao == "rot180":
        return _rotacionar_forma_90(_rotacionar_forma_90(forma))
    if operacao == "rot270":
        return _rotacionar_forma_90(
            _rotacionar_forma_90(_rotacionar_forma_90(forma))
        )
    if operacao == "mirror_h":
        return _espelhar_forma_horizontal(forma)
    if operacao == "mirror_v":
        return _espelhar_forma_vertical(forma)
    return _normalizar_forma(forma)


def _aplicar_sequencia_forma(forma, operacoes):
    resultado = _normalizar_forma(forma)
    for operacao in operacoes:
        resultado = _aplicar_operacao_forma(resultado, operacao)
    return resultado


def _variantes_dihedrais(forma):
    """Retorna as orientações distintas obtidas por rotações e espelhamentos."""
    forma = _normalizar_forma(forma)
    variantes = set()
    atual = forma
    for _ in range(4):
        variantes.add(_normalizar_forma(atual))
        variantes.add(_espelhar_forma_horizontal(atual))
        atual = _rotacionar_forma_90(atual)
    return list(variantes)


def _gerar_forma_assimetrica(tamanho=4):
    """Gera uma pequena forma conectada com ao menos 8 orientações distintas."""
    tamanho = max(4, min(5, int(tamanho or 4)))
    minimo = 6 if tamanho == 4 else 7
    maximo = 8 if tamanho == 4 else 10

    for _ in range(250):
        alvo = random.randint(minimo, maximo)
        centro = tamanho // 2
        celulas = {(centro, centro)}
        tentativas = 0
        while len(celulas) < alvo and tentativas < 400:
            tentativas += 1
            linha, coluna = random.choice(tuple(celulas))
            dl, dc = random.choice(((-1, 0), (1, 0), (0, -1), (0, 1)))
            nl, nc = linha + dl, coluna + dc
            if 0 <= nl < tamanho and 0 <= nc < tamanho:
                celulas.add((nl, nc))

        matriz = tuple(
            tuple(1 if (linha, coluna) in celulas else 0 for coluna in range(tamanho))
            for linha in range(tamanho)
        )
        matriz = _normalizar_forma(matriz)
        if len(_variantes_dihedrais(matriz)) == 8:
            return matriz

    # Fallback determinístico e assimétrico.
    return (
        (1, 0, 0, 0),
        (1, 1, 1, 0),
        (0, 0, 1, 1),
        (0, 0, 1, 0),
    )


_ROTACAO_ROTULOS = {
    "rot90": "rotação de 90° no sentido horário",
    "rot180": "rotação de 180°",
    "rot270": "rotação de 270° no sentido horário",
    "mirror_h": "espelhamento esquerda ↔ direita",
    "mirror_v": "espelhamento cima ↔ baixo",
}


def _sequencias_rotacao_por_nivel(nivel):
    nivel = max(1, min(5, int(nivel or 1)))
    simples = [
        ("rot90",),
        ("rot180",),
        ("rot270",),
        ("mirror_h",),
        ("mirror_v",),
    ]
    duplas = [
        ("rot90", "mirror_h"),
        ("rot90", "mirror_v"),
        ("rot180", "mirror_h"),
        ("rot180", "mirror_v"),
        ("rot270", "mirror_h"),
        ("rot270", "mirror_v"),
        ("mirror_h", "rot90"),
        ("mirror_v", "rot90"),
    ]
    triplas = [
        ("rot90", "mirror_h", "rot90"),
        ("mirror_h", "rot90", "mirror_v"),
        ("rot270", "mirror_v", "rot90"),
        ("mirror_v", "rot180", "mirror_h"),
        ("rot90", "mirror_v", "rot180"),
        ("mirror_h", "rot270", "mirror_v"),
    ]

    if nivel == 1:
        return simples
    if nivel == 2:
        return simples + duplas
    if nivel == 3:
        return duplas
    return duplas + triplas


class _FormaMatrizWidget(QWidget):
    """Desenha formas como matrizes, sem imagens externas."""

    def __init__(self, forma=None, parent=None):
        super().__init__(parent)
        self.forma = _normalizar_forma(forma)
        self.setMinimumSize(84, 64)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    def set_forma(self, forma):
        self.forma = _normalizar_forma(forma)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.forma:
            return

        linhas = len(self.forma)
        colunas = len(self.forma[0]) if linhas else 0
        if not linhas or not colunas:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        cor = self.palette().color(QPalette.Highlight)
        if not self.isEnabled():
            cor.setAlpha(155)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(cor)

        # A margem acompanha o tamanho real do canvas. Não há lado mínimo
        # artificial: assim a forma sempre cabe inteira, mesmo quando o
        # layout é comprimido verticalmente.
        menor_dimensao = max(1.0, float(min(self.width(), self.height())))
        margem = min(10.0, max(4.0, menor_dimensao * 0.08))
        largura = max(1.0, self.width() - (margem * 2))
        altura = max(1.0, self.height() - (margem * 2))
        lado = min(largura / colunas, altura / linhas)
        if lado <= 0.0:
            painter.end()
            return
        total_largura = lado * colunas
        total_altura = lado * linhas
        x0 = (self.width() - total_largura) / 2.0
        y0 = (self.height() - total_altura) / 2.0
        folga = min(max(1.0, lado * 0.10), lado * 0.24)

        for linha, valores in enumerate(self.forma):
            for coluna, preenchido in enumerate(valores):
                if not preenchido:
                    continue
                x = x0 + (coluna * lado) + (folga / 2.0)
                y = y0 + (linha * lado) + (folga / 2.0)
                tamanho = max(2.0, lado - folga)
                painter.drawRoundedRect(QRectF(x, y, tamanho, tamanho), 2.5, 2.5)

        painter.end()


class _BaseJogo(QWidget):
    jogo_id = ""

    def __init__(self, ao_registrar=None, parent=None):
        super().__init__(parent)
        self.ao_registrar = ao_registrar

    def registrar_resultado(self, pontuacao=0, nivel=None, duracao=None, movimentos=None):
        try:
            registrar_resultado_jogo(
                self.jogo_id,
                pontuacao=pontuacao,
                nivel=nivel,
                duracao_segundos=duracao,
                movimentos=movimentos,
            )
            if callable(self.ao_registrar):
                self.ao_registrar()
        except Exception:
            # O jogo continua utilizável mesmo que o histórico não possa ser salvo.
            pass


class _ArenaPremiumChimpBoard(QFrame):
    """F10 scene reused in C02 as a shared environmental Qt stage.

    The nested viewport holds the same 25 QPushButtons. The stage paints
    the F10 forest behind all bands without intercepting clicks.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("gameBoardPanel")
        self._imagem, self._imagem_valida = _arena_premium_art.carregar_pixmap(
            "floresta_chimpanze", tamanho_fallback=(1400, 840)
        )
        self._imagem_redimensionada = None
        self._dimensao_cache = None
        self._gorila = _arena_forest_f10.carregar_gorila()
        self._gorila_redimensionado = None
        self._dimensao_gorila_cache = None
        # BG01: arte PNG imutável em memória; grade/CTA são widgets sobrepostos.
        self._bg01_imagem = _arena_chimp_bg01_arte.carregar_pixmap()
        self._bg01_redimensionada = None
        self._bg01_dimensao_cache = None
        # E02: vegetacao lateral vetorial pre-renderizada por dimensoes da cena.
        # Nao adiciona widgets e nunca interfere na grade Qt ou nos cliques.
        self._e02_vegetacao_cache = None
        self._e02_dimensao_cache = None
        # E03: planos de profundidade rasterizados somente se o palco mudar.
        self._e03_planos_cache = None
        self._e03_dimensao_cache = None
        # E04: atmosfera atras da silhueta e vegetacao discreta na base da rocha.
        # QPixmaps reutilizados por dimensao; nenhum novo widget ou evento.
        self._e04_integracao_cache = None
        self._e04_dimensao_cache = None
        # E05: dois planos de iluminacao atmosferica em cache por tamanho.
        # Nao altera widgets, eventos nem coordenadas do gorila/grade.
        self._e05_luz_cache = None
        self._e05_dimensao_cache = None
        # C02: child board viewport is bound after layout creation. The gorilla
        # stays positioned and sized relative to this viewport, not full stage.
        self._gorila_viewport = None

    def resizeEvent(self, event):
        self._imagem_redimensionada = None
        self._dimensao_cache = None
        self._bg01_redimensionada = None
        self._bg01_dimensao_cache = None
        # C09: preservar o cache do gorila entre resizes se a altura-alvo
        # permanecer igual. A posição ainda é calculada a cada pintura.
        super().resizeEvent(event)

    def _e02_criar_vegetacao_esquerda(self, largura, altura):
        """Camadas naturais no fundo esquerdo: arte vetorial, sem assets extras.

        Recria somente quando a geometria da cena muda. A area central do
        tabuleiro e deliberadamente escura para manter contraste funcional.
        """
        chave = (int(largura), int(altura))
        if (self._e02_vegetacao_cache is not None
                and self._e02_dimensao_cache == chave):
            return self._e02_vegetacao_cache
        w, h = chave
        if w < 1 or h < 1:
            return QPixmap()
        arte = QPixmap(w, h)
        arte.fill(Qt.transparent)
        q = QPainter(arte)
        q.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        q.setPen(Qt.NoPen)

        # E02 A: nevoa profunda azul, concentrada atras da vegetacao.
        aura = QRadialGradient(w * 0.085, h * 0.53, max(1., w * 0.39))
        aura.setColorAt(0.0, QColor(14, 103, 139, 39))
        aura.setColorAt(0.54, QColor(10, 68, 111, 20))
        aura.setColorAt(1.0, QColor(5, 30, 65, 0))
        q.fillRect(QRectF(0, 0, w * 0.50, h), QBrush(aura))

        # Silhuetas de troncos e galhos em dois planos, sem mosaicos repetidos.
        def galho(pontos, tonalidade, espessura):
            path = QPainterPath()
            path.moveTo(w * pontos[0][0], h * pontos[0][1])
            for a, b, c in pontos[1:]:
                path.cubicTo(w * a[0], h * a[1], w * b[0], h * b[1],
                             w * c[0], h * c[1])
            q.setPen(QPen(QColor(*tonalidade), max(0.8, espessura * w)))
            q.setBrush(Qt.NoBrush)
            q.drawPath(path)
            q.setPen(Qt.NoPen)

        galho(((0.014, 1.02), ((0.025, 0.83), (0.035, 0.43), (0.055, 0.22)),
               ((0.066, 0.09), (0.092, 0.045), (0.145, -0.035))),
              (5, 37, 55, 149), 0.010)
        galho(((-0.02, 0.19), ((0.038, 0.14), (0.098, 0.20), (0.195, 0.07))),
              (8, 53, 75, 113), 0.004)
        galho(((0.01, 1.04), ((0.038, 0.86), (0.112, 0.72), (0.212, 0.60))),
              (4, 37, 52, 135), 0.006)
        galho(((0.018, 0.99), ((0.082, 0.86), (0.158, 0.82), (0.244, 0.71))),
              (8, 62, 80, 91), 0.0026)

        # Folhas lanceoladas com curvatura organica, sem desenhar sobre
        # as bordas e os numeros dos botoes (widgets sao pintados depois).
        def folha(x, y, dx, dy, largura_folha, cor, veia=False):
            distancia = max(0.001, (dx * dx + dy * dy) ** 0.5)
            px, py = -dy / distancia, dx / distancia
            mx, my = x + dx * 0.47, y + dy * 0.47
            ponta_x, ponta_y = x + dx, y + dy
            path = QPainterPath()
            path.moveTo(x, y)
            path.cubicTo(x + dx * .18 + px * largura_folha * .72,
                         y + dy * .18 + py * largura_folha * .72,
                         mx + px * largura_folha, my + py * largura_folha,
                         ponta_x, ponta_y)
            path.cubicTo(mx - px * largura_folha * .80,
                         my - py * largura_folha * .80,
                         x + dx * .13 - px * largura_folha * .30,
                         y + dy * .13 - py * largura_folha * .30,
                         x, y)
            path.closeSubpath()
            q.setPen(Qt.NoPen)
            q.setBrush(QColor(*cor))
            q.drawPath(path)
            if veia:
                q.setPen(QPen(QColor(49, 157, 165, 30), 0.7))
                q.drawLine(QPointF(x + dx * .12, y + dy * .12),
                           QPointF(x + dx * .83, y + dy * .83))
                q.setPen(Qt.NoPen)

        # E02 B: copa ao alto, principalmente sobre a faixa esquerda livre.
        # Limite horizontal de aprox. 0.30 da cena; centro fica protegido.
        copas = [
            (.012, .035, .107, .141, .024, (12, 86, 102, 135)),
            (.011, .012, .158, .059, .027, (9, 64, 82, 145)),
            (.045, .000, .158, .143, .031, (8, 61, 83, 120)),
            (.005, .091, .117, .159, .026, (12, 83, 98, 142)),
            (.044, .041, .198, .090, .029, (5, 60, 79, 113)),
            (.024, .125, .178, .145, .019, (15, 93, 111, 99)),
            (.105, .008, .125, .144, .023, (9, 70, 88, 108)),
            (.015, .200, .101, .140, .020, (5, 49, 69, 135)),
            (.066, .190, .149, .106, .018, (7, 63, 77, 102)),
            (.135, .026, .135, .075, .019, (11, 73, 88, 115)),
        ]
        for nx, ny, ndx, ndy, nw, rgba in copas:
            folha(w * nx, h * ny, w * ndx, h * ndy, w * nw, rgba)

        # E02 C: samambaias / sub-bosque na base esquerda.
        # Folhas curvas criam planos sobrepostos sem invadir o gorila.
        ramos = [
            (.012, .96, .183, -.41, (9, 79, 89, 158)),
            (.005, .99, .132, -.54, (9, 67, 83, 140)),
            (.050, 1.025, .224, -.35, (13, 87, 100, 112)),
            (.018, .96, .286, -.17, (8, 63, 80, 132)),
            (.016, .88, .181, -.34, (8, 66, 86, 122)),
        ]
        for nx, ny, tx, ty, cor in ramos:
            x, y = w * nx, h * ny
            tip_x, tip_y = w * tx, h * (ny + ty)
            espinha = QPainterPath(QPointF(x, y))
            espinha.quadTo((x + tip_x) * .39, (y + tip_y) * .34,
                           tip_x, tip_y)
            q.setBrush(Qt.NoBrush)
            q.setPen(QPen(QColor(cor[0], cor[1], cor[2], 112), 1.15))
            q.drawPath(espinha)
            q.setPen(Qt.NoPen)
            for j in range(1, 7):
                t = j / 7.5
                base_x = x + (tip_x - x) * t
                base_y = y + (tip_y - y) * (2 * t - t * t)
                comprimento = w * (.030 + .011 * (1.0 - t))
                for side in (-1, 1):
                    folha(base_x, base_y,
                          comprimento * (1.0 - t * .38),
                          -h * (.022 + .018 * (1.0 - t)) * side,
                          w * .009 * (1.0 - t * .35), cor)

        # E02 D: primeiro plano na borda, propositalmente mais escuro.
        for nx, ny, ndx, ndy, nw in [
            (-.018, .69, .153, -.154, .028),
            (-.025, .82, .125, -.114, .026),
            (-.018, .91, .172, -.065, .030),
            (.010, .97, .204, -.113, .025),
            (-.016, .42, .111, -.156, .022),
        ]:
            folha(w * nx, h * ny, w * ndx, h * ndy, w * nw,
                  (3, 40, 57, 146), True)

        q.end()
        self._e02_vegetacao_cache = arte
        self._e02_dimensao_cache = chave
        return arte

    def _e03_criar_planos_profundidade(self, largura, altura):
        """Floresta em planos suaves por toda a cena (E03), sem itens Qt novos.

        A distancia usa alfa muito baixo; copas e troncos aparecem sob os
        widgets reais. Transicoes nunca dependem do x final da grade, evitando
        uma nova emenda retangular entre floresta e o gorila.
        """
        chave = (int(largura), int(altura))
        if (self._e03_planos_cache is not None
                and self._e03_dimensao_cache == chave):
            return self._e03_planos_cache
        w, h = chave
        if w < 1 or h < 1:
            return QPixmap()
        arte = QPixmap(w, h)
        arte.fill(Qt.transparent)
        q = QPainter(arte)
        q.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        q.setPen(Qt.NoPen)
        W, H = float(w), float(h)

        # Plano distante: uma massa vegetal irregular com borda orgânica.
        # Nenhuma barra vertical ou corte abrupto em torno da grade.
        horizonte = QPainterPath()
        horizonte.moveTo(-W * .02, H * .46)
        horizonte.cubicTo(W * .08, H * .28, W * .13, H * .38, W * .19, H * .34)
        horizonte.cubicTo(W * .31, H * .21, W * .39, H * .40, W * .48, H * .30)
        horizonte.cubicTo(W * .59, H * .21, W * .65, H * .37, W * .76, H * .28)
        horizonte.cubicTo(W * .87, H * .23, W * .96, H * .38, W * 1.03, H * .33)
        horizonte.lineTo(W * 1.03, H * .86)
        horizonte.lineTo(-W * .02, H * .86)
        horizonte.closeSubpath()
        cor_horizonte = QLinearGradient(0, H * .27, 0, H * .86)
        cor_horizonte.setColorAt(0.0, QColor(16, 84, 111, 9))
        cor_horizonte.setColorAt(0.45, QColor(11, 60, 88, 29))
        cor_horizonte.setColorAt(1.0, QColor(5, 35, 61, 9))
        q.setBrush(QBrush(cor_horizonte))
        q.drawPath(horizonte)

        # Troncos recuados em posições não equidistantes, com ramificações.
        # São sombras de fundo, não novos controles ou obstáculos.
        def ramificacao(p0, p1, p2, p3, cor, grossura):
            desenho = QPainterPath(QPointF(W * p0[0], H * p0[1]))
            desenho.cubicTo(QPointF(W * p1[0], H * p1[1]),
                             QPointF(W * p2[0], H * p2[1]),
                             QPointF(W * p3[0], H * p3[1]))
            q.setPen(QPen(QColor(*cor), max(.8, W * grossura)))
            q.setBrush(Qt.NoBrush)
            q.drawPath(desenho)
            q.setPen(Qt.NoPen)

        ramificacao((.30, 1.02),(.32,.72),(.30,.40),(.35,-.10), (9, 72, 89, 31), .004)
        ramificacao((.35,.30),(.29,.21),(.23,.19),(.19,.13), (12, 79, 91, 28), .0018)
        ramificacao((.49,1.05),(.51,.77),(.53,.34),(.58,-.05), (8, 57, 78, 40), .006)
        ramificacao((.53,.40),(.60,.30),(.63,.30),(.68,.24), (10, 73, 95, 30), .0024)
        ramificacao((.71,1.04),(.71,.77),(.67,.38),(.75,-.09), (7, 53, 76, 36), .005)
        ramificacao((.69,.39),(.65,.30),(.59,.24),(.55,.22), (9, 72, 93, 25), .002)
        ramificacao((.89,1.06),(.86,.72),(.85,.36),(.88,-.07), (7, 54, 73, 25), .005)

        # Fitas de névoa com extremos suaves: nenhuma emenda vertical.
        # Baixa opacidade para que os pontos das 25 células sigam nítidos.
        for cx, cy, rx, alpha in (
                (.40, .37, .35, 24),
                (.59, .65, .43, 22),
                (.77, .48, .26, 17),
                (.29, .85, .33, 15)):
            nevoa = QRadialGradient(W * cx, H * cy, max(1.0, W * rx))
            nevoa.setColorAt(0.0, QColor(25, 119, 153, alpha))
            nevoa.setColorAt(.37, QColor(17, 88, 134, int(alpha * .55)))
            nevoa.setColorAt(1.0, QColor(7, 35, 72, 0))
            q.fillRect(QRectF(0, 0, W, H), QBrush(nevoa))

        # Sub-bosque distante: contorno livre que atravessa a composição e
        # dissolve gradualmente na parte inferior, inclusive atrás da grade.
        base = QPainterPath()
        base.moveTo(-W * .02, H * .94)
        base.cubicTo(W * .10, H * .78, W * .19, H * .92, W * .31, H * .83)
        base.cubicTo(W * .41, H * .91, W * .48, H * .82, W * .58, H * .88)
        base.cubicTo(W * .69, H * .77, W * .77, H * .89, W * .88, H * .82)
        base.cubicTo(W * .97, H * .87, W * 1.00, H * .83, W * 1.02, H * .81)
        base.lineTo(W * 1.02, H * 1.03)
        base.lineTo(-W * .02, H * 1.03)
        base.closeSubpath()
        cor_base = QLinearGradient(0, H * .78, 0, H)
        cor_base.setColorAt(0.0, QColor(6, 53, 74, 9))
        cor_base.setColorAt(.65, QColor(6, 48, 67, 36))
        cor_base.setColorAt(1.0, QColor(3, 24, 47, 28))
        q.setBrush(QBrush(cor_base))
        q.drawPath(base)
        q.end()
        self._e03_planos_cache = arte
        self._e03_dimensao_cache = chave
        return arte

    def _e04_criar_integracao_gorila(self, largura, altura):
        """Dois planos cênicos em cache para unir floresta, rocha e gorila.

        O plano distante suaviza a passagem de luz à direita; o primeiro
        plano cobre apenas a base da rocha com folhas translúcidas. A grade,
        o gorila e seus limites físicos não são movidos ou redimensionados.
        """
        chave = (int(largura), int(altura))
        if (self._e04_integracao_cache is not None
                and self._e04_dimensao_cache == chave):
            return self._e04_integracao_cache
        w, h = chave
        if w < 1 or h < 1:
            return QPixmap(), QPixmap()
        W, H = float(w), float(h)
        fundo = QPixmap(w, h)
        fundo.fill(Qt.transparent)
        p = QPainter(fundo)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(Qt.NoPen)

        # O halo não possui retângulo visível: desaparece antes de atingir
        # o centro do tabuleiro. Liga a luz da floresta à rocha do gorila.
        for cx, cy, raio, intensidade in (
                (.79, .36, .35, 35),
                (.90, .67, .31, 27),
                (.71, .76, .30, 18)):
            nevoa = QRadialGradient(W * cx, H * cy, max(1.0, W * raio))
            nevoa.setColorAt(0.0, QColor(25, 125, 157, intensidade))
            nevoa.setColorAt(.45, QColor(15, 85, 124, int(intensidade * .50)))
            nevoa.setColorAt(1.0, QColor(5, 32, 62, 0))
            p.fillRect(QRectF(0, 0, W, H), QBrush(nevoa))

        # Copa recuada irregular: sem alinhamento com a borda da grade ou
        # da imagem do gorila; as formas se dissolvem no cenário existente.
        copa = QPainterPath()
        copa.moveTo(W*.58, H*.43)
        copa.cubicTo(W*.65, H*.29, W*.71, H*.37, W*.76, H*.27)
        copa.cubicTo(W*.83, H*.20, W*.88, H*.32, W*.95, H*.22)
        copa.cubicTo(W*1.02, H*.21, W*1.03, H*.30, W*1.03, H*.36)
        copa.lineTo(W*1.03, H*.83)
        copa.cubicTo(W*.88, H*.73, W*.77, H*.80, W*.59, H*.73)
        copa.closeSubpath()
        profundidade = QLinearGradient(0, H*.24, 0, H*.84)
        profundidade.setColorAt(0.0, QColor(8, 52, 75, 1))
        profundidade.setColorAt(.52, QColor(8, 60, 80, 22))
        profundidade.setColorAt(1.0, QColor(3, 33, 51, 4))
        p.setBrush(QBrush(profundidade))
        p.drawPath(copa)

        # Ramos finos sem destaque sobre a figura; incorporados à floresta.
        for pontos, opacidade, espessura in (
            (((.71,1.02),(.69,.78),(.75,.51),(.72,.20)),32,.0035),
            (((.83,1.04),(.83,.82),(.89,.52),(.91,.10)),28,.0040),
            (((.96,.96),(.94,.71),(.99,.53),(1.04,.33)),33,.0045),
        ):
            linha = QPainterPath(QPointF(W*pontos[0][0],H*pontos[0][1]))
            linha.cubicTo(*(QPointF(W*x,H*y) for x,y in pontos[1:]))
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(7, 53, 65, opacidade), max(.8,W*espessura)))
            p.drawPath(linha)
        p.end()

        # Primeiro plano: folhas pequenas só na parte inferior DIREITA,
        # entre a rocha e a borda. Não cobrem cabeça, rosto ou células.
        frente = QPixmap(w, h)
        frente.fill(Qt.transparent)
        q = QPainter(frente)
        q.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        q.setPen(Qt.NoPen)
        for px, py, dx, dy, largura_folha, alpha in (
            (.79,.97,.090,-.17,.013,55),
            (.82,1.00,.102,-.10,.014,63),
            (.88,.99,.085,-.20,.015,61),
            (.94,1.00,.060,-.14,.016,66),
            (.96,.89,.073,-.08,.012,46),
            (.73,1.00,.098,-.09,.012,39),
        ):
            x0,y0=W*px,H*py
            dx0,dy0=W*dx,H*dy
            largura0=W*largura_folha
            folha=QPainterPath(QPointF(x0,y0))
            folha.cubicTo(QPointF(x0+dx0*.20-largura0,y0+dy0*.30),
                          QPointF(x0+dx0*.50-largura0,y0+dy0*.83),
                          QPointF(x0+dx0,y0+dy0))
            folha.cubicTo(QPointF(x0+dx0*.68+largura0,y0+dy0*.84),
                          QPointF(x0+dx0*.22+largura0,y0+dy0*.24),
                          QPointF(x0,y0))
            folha.closeSubpath()
            q.setBrush(QColor(4, 46, 55, alpha))
            q.drawPath(folha)
        q.end()
        self._e04_integracao_cache = (fundo, frente)
        self._e04_dimensao_cache = chave
        return self._e04_integracao_cache

    def _e05_criar_luz_atmosferica(self, largura, altura):
        """Luz de floresta suave em duas camadas, sem afetar geometria Qt.

        A camada de fundo ilumina a vegetacao esquerda, o corredor central
        e o contra-luz da rocha. A camada frontal aplica um reflexo tenue
        junto ao gorila. Ambas se dissolvem em alpha 0 e sao reutilizadas
        enquanto o viewport conservar as mesmas dimensoes.
        """
        chave = (int(largura), int(altura))
        if (self._e05_luz_cache is not None
                and self._e05_dimensao_cache == chave):
            return self._e05_luz_cache
        w, h = chave
        if w <= 0 or h <= 0:
            return QPixmap(), QPixmap()
        W, H = float(w), float(h)
        fundo = QPixmap(w, h)
        fundo.fill(Qt.transparent)
        p = QPainter(fundo)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(Qt.NoPen)

        # Fontes difusas sem circulos recortados nem linha vertical divisoria.
        # Intensidades baixas: os 25 botoes sao pintados pelo Qt por cima.
        luzes = (
            (.095, .17, .34, (26, 141, 170, 48), (14, 89, 139, 18)),
            (.42, .07, .48, (23, 116, 172, 29), (12, 80, 125, 11)),
            (.79, .24, .39, (39, 150, 190, 37), (17, 99, 145, 15)),
            (.97, .48, .34, (32, 162, 194, 54), (17, 95, 148, 18)),
        )
        for cx, cy, raio, centro, meio in luzes:
            luz = QRadialGradient(W * cx, H * cy, max(1., W * raio))
            luz.setColorAt(0.0, QColor(*centro))
            luz.setColorAt(0.46, QColor(*meio))
            luz.setColorAt(1.0, QColor(6, 36, 73, 0))
            p.fillRect(QRectF(0, 0, W, H), QBrush(luz))

        # Tres feixes de luz de copa: bordas dissolvidas no fundo e na nevoa.
        # Saem do alto, com deslocamentos organicos, sem linhas definidas.
        for topo, base, abertura, alpha in (
            (.16, .30, .075, 13),
            (.65, .59, .065, 11),
            (.91, .81, .075, 15),
        ):
            feixe = QPainterPath()
            feixe.moveTo(W*(topo-abertura*.34), -H*.06)
            feixe.lineTo(W*(topo+abertura*.34), -H*.06)
            feixe.cubicTo(W*(topo+abertura*.40), H*.28,
                          W*(base+abertura), H*.57,
                          W*(base+abertura*1.25), H*.80)
            feixe.lineTo(W*(base-abertura*1.25), H*.80)
            feixe.cubicTo(W*(base-abertura), H*.51,
                          W*(topo-abertura*.4), H*.26,
                          W*(topo-abertura*.34), -H*.06)
            feixe.closeSubpath()
            cor = QLinearGradient(0, 0, 0, H*.83)
            cor.setColorAt(0., QColor(39, 149, 186, alpha))
            cor.setColorAt(.24, QColor(33, 135, 180, int(alpha*.72)))
            cor.setColorAt(.70, QColor(18, 100, 152, int(alpha*.25)))
            cor.setColorAt(1., QColor(8, 53, 94, 0))
            p.setBrush(QBrush(cor))
            p.drawPath(feixe)

        # Nevoa iluminada no sub-bosque. Dissolve progressivamente acima
        # da base e preserva a transparencia de cada folha E02-E04.
        bruma = QLinearGradient(0, H*.52, 0, H)
        bruma.setColorAt(0., QColor(10, 75, 112, 0))
        bruma.setColorAt(.58, QColor(22, 113, 148, 10))
        bruma.setColorAt(1., QColor(27, 121, 159, 19))
        p.fillRect(QRectF(0, H*.50, W, H*.50), QBrush(bruma))
        p.end()

        # Realce frontal minimo no alto da rocha / ombro do gorila.
        # Nao aplica Screen em toda a figura e nao cria linhas na grade.
        frente = QPixmap(w, h)
        frente.fill(Qt.transparent)
        q = QPainter(frente)
        q.setPen(Qt.NoPen)
        toque = QRadialGradient(W*.94, H*.35, max(1., W*.23))
        toque.setColorAt(0., QColor(53, 174, 200, 22))
        toque.setColorAt(.54, QColor(32, 118, 171, 8))
        toque.setColorAt(1., QColor(6, 44, 83, 0))
        q.fillRect(QRectF(W*.67, 0, W*.33, H*.82), QBrush(toque))
        q.end()
        self._e05_luz_cache = (fundo, frente)
        self._e05_dimensao_cache = chave
        return self._e05_luz_cache

    def paintEvent(self, event):
        """C06: profundidade e exposição localizadas na floresta, sem widgets falsos.

        A cena é exclusivamente decorativa; Qt desenha os botões reais depois.
        Conserva a arte F10 e evita interferir em cliques, foco ou layout.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        area = QRectF(self.rect()).adjusted(0.7, 0.7, -0.7, -0.7)
        contorno = QPainterPath()
        contorno.addRoundedRect(area, 13.0, 13.0)
        painter.setClipPath(contorno)
        painter.fillPath(contorno, QColor("#061727"))

        # BG01: substitui APENAS a composição artística antiga do quadrante.
        # PNG original 1774x887 (sem reduzir nem recomprimir). KeepAspectRatioByExpanding
        # cobre todo o palco: o corte excedente ocorre somente nas bordas,
        # preservando proporções. Células e CTA são widgets Qt desenhados depois.
        if not self._bg01_imagem.isNull():
            tamanho = self.size()
            if (self._bg01_redimensionada is None
                    or self._bg01_dimensao_cache != tamanho):
                self._bg01_redimensionada = self._bg01_imagem.scaled(
                    tamanho, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                )
                self._bg01_dimensao_cache = tamanho
            imagem = self._bg01_redimensionada
            painter.drawPixmap(
                (self.width() - imagem.width()) // 2,
                (self.height() - imagem.height()) // 2,
                imagem
            )
            # Proteção de contraste leve e uniforme sob o tabuleiro;
            # não desenha número, botão nem grade em pixels.
            sombra_bg01 = QLinearGradient(0, 0, self.width(), 0)
            sombra_bg01.setColorAt(0.0, QColor(3, 15, 28, 28))
            sombra_bg01.setColorAt(0.50, QColor(3, 15, 28, 41))
            sombra_bg01.setColorAt(1.0, QColor(3, 15, 28, 0))
            painter.fillRect(self.rect(), QBrush(sombra_bg01))
            painter.setClipping(False)
            painter.setBrush(Qt.NoBrush)
            # Preserva moldura D04, sem duplicar a figura antiga do F10.
            painter.setPen(QPen(QColor(15, 136, 184, 31), 3.0))
            painter.drawPath(contorno)
            borda_gradual = QLinearGradient(0, 0, self.width(), self.height())
            borda_gradual.setColorAt(0.0, QColor(75, 215, 245, 186))
            borda_gradual.setColorAt(0.42, QColor(25, 146, 190, 169))
            borda_gradual.setColorAt(1.0, QColor(26, 112, 162, 125))
            painter.setPen(QPen(QBrush(borda_gradual), 1.15))
            painter.drawPath(contorno)
            aro_interno = QPainterPath()
            aro_interno.addRoundedRect(area.adjusted(2.5, 2.5, -2.5, -2.5), 10.8, 10.8)
            brilho_interno = QLinearGradient(0, 0, 0, max(1, self.height()))
            brilho_interno.setColorAt(0.0, QColor(48, 190, 228, 47))
            brilho_interno.setColorAt(0.40, QColor(19, 105, 153, 13))
            brilho_interno.setColorAt(1.0, QColor(12, 71, 119, 0))
            painter.setPen(QPen(QBrush(brilho_interno), 0.8))
            painter.drawPath(aro_interno)
            painter.end()
            return

        # Fundo-base F10: fallback preservado caso o novo PNG fique nulo.
        if self._imagem_valida and not self._imagem.isNull():
            tamanho = self.size()
            if self._imagem_redimensionada is None or self._dimensao_cache != tamanho:
                self._imagem_redimensionada = self._imagem.scaled(
                    tamanho, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                )
                self._dimensao_cache = tamanho
            fundo = self._imagem_redimensionada
            x = (self.width() - fundo.width()) // 2
            y = (self.height() - fundo.height()) // 2
            painter.setOpacity(0.64)
            painter.drawPixmap(x, y, fundo)
            painter.setOpacity(1.0)

        # Iluminação em dois planos: halo amplo + reflexo ciano à direita.
        # A região sob as 25 células mantém proteção contra perda de contraste.
        viewport = self._gorila_viewport
        if viewport is not None and viewport.width() > 0 and viewport.height() > 0:
            largura_cena = max(1, viewport.width())
            altura_cena = max(1, viewport.height())
            origem_x, origem_y = viewport.x(), viewport.y()
        else:
            largura_cena = max(1, self.width())
            altura_cena = max(1, self.height())
            origem_x, origem_y = 0, 0

        painter.save()
        painter.setClipRect(QRectF(origem_x, origem_y, largura_cena, altura_cena), Qt.IntersectClip)
        # E03: planos distantes e nevoa contínua sob a vegetacao E02.
        # A luz não delimita a grade por retangulos ou barras verticais.
        profundidade = self._e03_criar_planos_profundidade(largura_cena, altura_cena)
        if not profundidade.isNull():
            painter.drawPixmap(origem_x, origem_y, profundidade)
        # E02: sub-bosque vetorial em planos na margem esquerda. O cache
        # elimina custo de criar 60+ folhas nas repinturas de cada rodada.
        # Os 25 QPushButtons Qt continuam sendo desenhados acima da arte.
        vegetacao = self._e02_criar_vegetacao_esquerda(largura_cena, altura_cena)
        if not vegetacao.isNull():
            painter.drawPixmap(origem_x, origem_y, vegetacao)
        # E04: atmosfera de ligação ANTES do gorila; sem emenda reta ou
        # alteração do recorte aprovado. O plano frontal será desenhado após.
        e04_fundo, e04_frente = self._e04_criar_integracao_gorila(largura_cena, altura_cena)
        if not e04_fundo.isNull():
            painter.drawPixmap(origem_x, origem_y, e04_fundo)
        # E05: luz de copa e atmosfera ANTES da protecao de contraste D03;
        # a vegetacao/celulas continuam visiveis e a borda do gorila se dissolve.
        e05_fundo, e05_frente = self._e05_criar_luz_atmosferica(largura_cena, altura_cena)
        if not e05_fundo.isNull():
            painter.drawPixmap(origem_x, origem_y, e05_fundo)
        # D03: a grade agora está centralizada (D02). A iluminação do
        # cenário também precisa alcançar o lado esquerdo, onde antes havia
        # uma região escura quase uniforme. Gradiente suave, sem novos assets.
        nevoa_esquerda = QRadialGradient(
            origem_x + largura_cena * 0.18, origem_y + altura_cena * 0.40,
            max(1.0, largura_cena * 0.49)
        )
        nevoa_esquerda.setColorAt(0.0, QColor(20, 107, 165, 68))
        nevoa_esquerda.setColorAt(0.52, QColor(10, 66, 121, 35))
        nevoa_esquerda.setColorAt(1.0, QColor(7, 34, 69, 0))
        painter.fillRect(QRectF(origem_x, origem_y, largura_cena, altura_cena), QBrush(nevoa_esquerda))

        halo = QRadialGradient(
            origem_x + largura_cena * 0.81, origem_y + altura_cena * 0.41,
            max(1.0, largura_cena * 0.39)
        )
        halo.setColorAt(0.0, QColor(21, 133, 189, 111))
        halo.setColorAt(0.54, QColor(13, 83, 143, 57))
        halo.setColorAt(1.0, QColor(6, 29, 58, 0))
        painter.fillRect(QRectF(origem_x, origem_y, largura_cena, altura_cena), QBrush(halo))

        reflexo = QRadialGradient(
            origem_x + largura_cena * 0.92, origem_y + altura_cena * 0.76,
            max(1.0, largura_cena * 0.29)
        )
        reflexo.setColorAt(0.0, QColor(15, 139, 191, 78))
        reflexo.setColorAt(0.62, QColor(10, 78, 128, 38))
        reflexo.setColorAt(1.0, QColor(6, 26, 48, 0))
        painter.fillRect(QRectF(origem_x, origem_y, largura_cena, altura_cena), QBrush(reflexo))

        # D03: proteção de contraste centrada NA GRADE REAL, e não na
        # antiga metade esquerda do viewport C04. Isso evita a grande mancha
        # escura lateral depois do alinhamento simétrico aprovado no D02.
        grade_visual = getattr(viewport, "_c04_grade", None) if viewport is not None else None
        if grade_visual is not None and grade_visual.width() > 0:
            posicao_grade = grade_visual.mapTo(self, grade_visual.rect().topLeft())
            inicio = (posicao_grade.x() - origem_x) / largura_cena
            fim = (posicao_grade.x() + grade_visual.width() - origem_x) / largura_cena
            inicio = max(0.0, min(1.0, inicio))
            fim = max(inicio, min(1.0, fim))
        else:
            # Fallback: durante a primeira pintura os layouts podem ainda
            # não ter geometria calculada; nenhuma largura fixa é presumida.
            inicio, fim = 0.0, 1.0
        # Quatro pontos de transição garantem máscara suave nos dois lados;
        # nunca forma uma fronteira vertical opaca no final do tabuleiro.
        margem = min(0.075, 38.0 / largura_cena)
        pontos = [(0.0, 0), (max(0.0, inicio - margem), 0),
                  (inicio, 42), (fim, 42),
                  (min(1.0, fim + margem), 0), (1.0, 0)]
        protecao = QLinearGradient(origem_x, 0, origem_x + largura_cena, 0)
        for fracao, alfa in pontos:
            protecao.setColorAt(fracao, QColor(3, 16, 31, alfa))
        painter.fillRect(QRectF(origem_x, origem_y, largura_cena, altura_cena), QBrush(protecao))

        # D04: terceiro plano de profundidade, suave e proporcional a cena.
        # Refina a passagem do ambiente escuro para a zona iluminada;
        # nunca pinta sobre o texto nem cria novos widgets na grade.
        claridade_alta = QRadialGradient(
            origem_x + largura_cena * 0.54,
            origem_y + altura_cena * 0.20,
            max(1.0, largura_cena * 0.52)
        )
        claridade_alta.setColorAt(0.0, QColor(47, 151, 203, 27))
        claridade_alta.setColorAt(0.52, QColor(23, 96, 158, 13))
        claridade_alta.setColorAt(1.0, QColor(8, 37, 69, 0))
        painter.fillRect(QRectF(origem_x, origem_y, largura_cena, altura_cena), QBrush(claridade_alta))

        # Bruma azul em segundo plano, concentrada no terco inferior da floresta.
        # A transparencia baixa preserva numeros, contraste e arte originais.
        bruma_inferior = QLinearGradient(
            origem_x, origem_y + altura_cena * 0.48,
            origem_x, origem_y + altura_cena
        )
        bruma_inferior.setColorAt(0.0, QColor(10, 47, 78, 0))
        bruma_inferior.setColorAt(0.65, QColor(16, 79, 118, 13))
        bruma_inferior.setColorAt(1.0, QColor(8, 46, 78, 22))
        painter.fillRect(QRectF(origem_x, origem_y, largura_cena, altura_cena), QBrush(bruma_inferior))
        painter.restore()

        # Gorila F10 ampliado apenas na área livre da grade C04.
        # O recurso original (266x346) segue embutido e sem nova compressão.
        if not self._gorila.isNull():
            dimensoes = (largura_cena, altura_cena)
            grade = getattr(viewport, '_c04_grade', None) if viewport is not None else None
            largura_grade = grade.width() if grade is not None and grade.width() > 0 else 0
            area_livre = max(0, largura_cena - largura_grade)
            if area_livre >= 140:
                altura_desejada = max(1, int(altura_cena * 1.26))
                # Nunca invadir a grade em janelas compactas.
                altura_limite = max(1, int(
                    (area_livre + 7) * self._gorila.height() / max(1, self._gorila.width())
                ))
                altura_alvo = min(altura_desejada, altura_limite)
                opacidade_gorila = 0.98
            else:
                # Em janela estreita priorizar os botões sobre o cenário.
                altura_alvo = max(1, int(altura_cena * 0.90))
                opacidade_gorila = 0.58
            # Apenas a altura-alvo altera os pixels do gorila escalonado.
            # Largura/posição da área livre não devem invalidar a mesma imagem.
            cache_gorila = altura_alvo
            if self._gorila_redimensionado is None or self._dimensao_gorila_cache != cache_gorila:
                self._gorila_redimensionado = self._gorila.scaledToHeight(
                    altura_alvo, Qt.SmoothTransformation
                )
                self._dimensao_gorila_cache = cache_gorila
            cena = self._gorila_redimensionado
            x = origem_x + largura_cena - cena.width() + 2
            # Ancoragem inferior expõe um gorila maior sem deslocar sua posição lateral.
            y = origem_y + altura_cena - cena.height() + 3
            painter.save()
            painter.setClipRect(QRectF(origem_x, origem_y, largura_cena, altura_cena), Qt.IntersectClip)
            painter.setOpacity(opacidade_gorila)
            painter.drawPixmap(x, y, cena)
            # O modo Screen recupera luz nas folhas e no corpo sem alterar a fonte.
            painter.setCompositionMode(QPainter.CompositionMode_Screen)
            painter.setOpacity(0.17 if area_livre >= 140 else 0.07)
            painter.drawPixmap(x, y, cena)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.restore()

        # E05: tenue luz ambiente na parte direita, desenhada depois do gorila
        # e antes da folhagem frontal E04. Sem alterar recorte ou escala F10.
        if not e05_frente.isNull():
            painter.save()
            painter.setClipRect(QRectF(origem_x, origem_y, largura_cena, altura_cena), Qt.IntersectClip)
            painter.drawPixmap(origem_x, origem_y, e05_frente)
            painter.restore()

        # E04: vegetação frontal integrada à base da rocha, sob os botões Qt.
        # A máscara é transparente e não cria regiões interativas.
        if not e04_frente.isNull():
            painter.save()
            painter.setClipRect(QRectF(origem_x, origem_y, largura_cena, altura_cena), Qt.IntersectClip)
            painter.drawPixmap(origem_x, origem_y, e04_frente)
            painter.restore()

        # Vinheta final levemente reduzida à direita; preserva texto e números.
        sombra = QLinearGradient(0, 0, 0, max(1, self.height()))
        sombra.setColorAt(0.0, QColor(3, 14, 28, 30))
        sombra.setColorAt(0.54, QColor(5, 20, 36, 16))
        sombra.setColorAt(1.0, QColor(2, 10, 23, 54))
        painter.fillRect(self.rect(), QBrush(sombra))
        painter.setClipping(False)
        painter.setBrush(Qt.NoBrush)

        # D04: contorno em dois planos. Brilho externo tenue e filete
        # ciano graduado no topo; no rodape a moldura volta ao azul escuro.
        painter.setPen(QPen(QColor(15, 136, 184, 31), 3.0))
        painter.drawPath(contorno)
        borda_gradual = QLinearGradient(0, 0, self.width(), self.height())
        borda_gradual.setColorAt(0.0, QColor(75, 215, 245, 186))
        borda_gradual.setColorAt(0.42, QColor(25, 146, 190, 169))
        borda_gradual.setColorAt(1.0, QColor(26, 112, 162, 125))
        painter.setPen(QPen(QBrush(borda_gradual), 1.15))
        painter.drawPath(contorno)

        aro_interno = QPainterPath()
        aro_interno.addRoundedRect(area.adjusted(2.5, 2.5, -2.5, -2.5), 10.8, 10.8)
        brilho_interno = QLinearGradient(0, 0, 0, max(1, self.height()))
        brilho_interno.setColorAt(0.0, QColor(48, 190, 228, 47))
        brilho_interno.setColorAt(0.40, QColor(19, 105, 153, 13))
        brilho_interno.setColorAt(1.0, QColor(12, 71, 119, 0))
        painter.setPen(QPen(QBrush(brilho_interno), 0.8))
        painter.drawPath(aro_interno)
        painter.end()

class _ArenaC04BoardViewport(QFrame):
    """Viewport F10 em largura total, com grade responsiva à esquerda.

    A geometria da cena e a escala do gorila continuam ligadas ao viewport
    inteiro. Redimensionamos só o FILHO que contém os 25 botões Qt reais.
    Nenhum item gráfico ou célula falsa é criado na área reservada à direita.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._c04_grade = None

    @staticmethod
    def largura_grade(area_util):
        """Largura lógica segura; proporção desktop 64%, fallback compacto."""
        area_util = max(0, int(area_util))
        if area_util >= 760:
            proporcao = 0.64
        elif area_util >= 620:
            proporcao = 0.72
        elif area_util >= 540:
            proporcao = 0.80
        else:
            proporcao = 1.0
        if area_util < 300:
            return area_util
        return min(area_util, max(300, int(area_util * proporcao)))

    def vincular_grade(self, grade):
        self._c04_grade = grade
        self._atualizar_largura_grade()

    def _atualizar_largura_grade(self):
        grade = self._c04_grade
        if grade is None:
            return
        # Área útil usa o rect interno do QFrame; não cria overflow lateral.
        largura_util = max(0, int(self.contentsRect().width()))
        destino = self.largura_grade(largura_util)
        if destino > 0 and grade.width() != destino:
            grade.setFixedWidth(destino)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._atualizar_largura_grade()


class _ArenaF09ChimpCell(QPushButton):
    """Celula Qt real: foco ciano apenas para navegacao via teclado.

    Um clique de mouse nao deve deixar borda branca persistente.
    Nao altera o processamento de clique, o texto nem o desenho de estados.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # C08: evita o retangulo branco nativo do QPushButton apos clique,
        # sem remover a navegacao por teclado nem o foco acessivel.
        self.setAutoDefault(False)
        self.setDefault(False)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setProperty("keyboardFocus", False)

    def _marcar_foco_teclado(self, ativo):
        ativo = bool(ativo)
        if bool(self.property("keyboardFocus")) != ativo:
            self.setProperty("keyboardFocus", ativo)
            _repolir(self)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        # Somente Tab/Shift+Tab/atalhos devem mostrar foco acessivel.
        foco_teclado = event.reason() in (
            Qt.TabFocusReason, Qt.BacktabFocusReason, Qt.ShortcutFocusReason,
        )
        self._marcar_foco_teclado(foco_teclado)
        if foco_teclado:
            # C09: Tab em janelas baixas deve trazer a celula para a viewport,
            # sem mover o foco nem rolar a pagina por cliques de mouse.
            janela = self.window()
            rolagem = getattr(janela, "_arena_scroll_vertical", None)
            if isinstance(rolagem, QScrollArea) and rolagem.isVisible():
                rolagem.ensureWidgetVisible(self, 16, 16)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._marcar_foco_teclado(False)

    def mousePressEvent(self, event):
        # Se a celula ja tinha foco de Tab, remove o contorno ao clicar.
        self._marcar_foco_teclado(False)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        # Nunca desenhar por cima dos numeros revelados ou das celulas certas.
        if self.text() or self.property("cellState") == "correct":
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        centro = QRectF(self.rect()).center()
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(26, 153, 210, 34))
        p.drawEllipse(centro, 6.5, 6.5)
        p.setBrush(QColor(65, 192, 237, 196 if self.isEnabled() else 145))
        p.drawEllipse(centro, 3.0, 3.0)
        p.end()


class JogoChimpanze(_BaseJogo):
    jogo_id = "chimpanze"

    def __init__(self, ao_registrar=None, parent=None):
        super().__init__(ao_registrar, parent)

        self.nivel = 4
        self.maior_nivel_concluido = 0
        self.mapa = {}
        self.esperado = 1
        self.ativo = False
        self.inicio = None
        self.token_rodada = 0

        # L08: visual local do Chimpanze, sem tocar nas regras do motor.
        self.setObjectName("arenaPremiumChimpanze")
        self.setStyleSheet("""
            QWidget#arenaPremiumChimpanze {
                background: transparent;
            }
            /* C03: texto, status e nivel ocupam uma faixa superior unificada.
               Floresta C02 permanece no palco ambiental ao fundo. */
            QWidget#arenaPremiumChimpanze QFrame#chimpPremiumTitleCard {
                background-color: rgba(5, 25, 43, 175);
                border: 1px solid rgba(36, 115, 152, 130);
                border-radius: 11px;
            }
            QWidget#arenaPremiumChimpanze QFrame#chimpPremiumBoardViewport {
                background: transparent;
                border: 1px solid rgba(37, 139, 181, 130);
                border-radius: 11px;
            }
            /* BG02: contêiner real da grade sem painel sólido. Os botões
               recebem seu próprio estado, mas a paisagem atravessa os vazios. */
            QWidget#arenaPremiumChimpanze QWidget#chimpC04GridArea {
                background: transparent;
                background-color: transparent;
                border: none;
            }
            QWidget#arenaPremiumChimpanze QLabel#chimpPremiumIcon {
                background: #063853;
                border: 1px solid #1BB5DC;
                border-radius: 9px;
            }
            QWidget#arenaPremiumChimpanze QLabel#gameTitle {
                background: transparent; border: none;
                color: #EFFBFF; font-size: 19px; font-weight: 800;
            }
            QWidget#arenaPremiumChimpanze QLabel#gameHint {
                background: transparent; border: none;
                color: #A8CBDC; font-size: 11px;
            }
            /* Etiqueta de nivel REAL, nao um seletor interativo falso. */
            QWidget#arenaPremiumChimpanze QLabel#gameMetric {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 rgba(7, 66, 101, 238), stop:1 rgba(4, 29, 55, 230));
                color: #59EEFF;
                border: 1px solid #22A9CC; border-radius: 9px;
                padding: 5px 9px; font-size: 15px; font-weight: 800;
            }
            QWidget#arenaPremiumChimpanze QLabel#gameStatus {
                background: transparent; border: none;
                color: #B9DBEA; font-size: 11px;
            }
            QWidget#arenaPremiumChimpanze QPushButton#gamePrimaryButton {
                background: #079EC7; color: #FFFFFF;
                border: 1px solid #3DEAFF; border-radius: 8px;
                font-size: 12px; font-weight: 750; padding: 6px 16px;
                min-height: 27px;
            }
            QWidget#arenaPremiumChimpanze QPushButton#gamePrimaryButton:hover {
                background: #08BBDE; border-color: #95F3FF;
            }
            QWidget#arenaPremiumChimpanze QPushButton#gamePrimaryButton:focus {
                border: 2px solid #BEF9FF;
            }
            /* C07: um unico CTA real ocupa o centro do palco, iluminacao premium. */
            QWidget#arenaPremiumChimpanze QFrame#chimpPremiumActionBand {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 rgba(4, 25, 48, 144),
                    stop:0.24 rgba(10, 53, 84, 163),
                    stop:0.5 rgba(8, 48, 84, 178),
                    stop:0.76 rgba(10, 53, 84, 163),
                    stop:1 rgba(5, 24, 48, 144));
                border: 1px solid rgba(47, 125, 166, 137);
                border-radius: 11px;
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpPremiumStartCTA {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #85F5FF, stop:0.18 #30E4FC,
                    stop:0.45 #09AFE7, stop:0.72 #087DBB, stop:1 #07518E);
                color: #FFFFFF; border: 1px solid #9EF6FF;
                border-top: 1px solid #C5FBFF;
                border-radius: 15px; font-size: 17px; font-weight: 800;
                padding: 6px 15px; min-height: 38px;
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpPremiumStartCTA:hover:enabled {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #A1FCFF, stop:0.22 #4BEAF8,
                    stop:0.65 #0EACDB, stop:1 #086B9D);
                border: 2px solid #C1FAFF;
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpPremiumStartCTA:pressed:enabled {
                background: #086D97; border: 1px solid #51CDFA;
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpPremiumStartCTA:focus {
                border: 2px solid #7CEBFF;
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpPremiumStartCTA:disabled {
                background: #18445E; color: #9CC3D6;
                border: 1px solid #356880;
            }
            /* F09 + C05: cantos mais proximos da referencia, sem mudar estados. */
            QWidget#arenaPremiumChimpanze QPushButton#chimpCellButton {
                /* BG02: 0% de opacidade no estado neutro; a pintura de
                   floresta BG01 passa a aparecer atrás de cada botão. */
                background: transparent;
                border: 1px solid #337DA5;
                border-radius: 9px;
                color: #F5FDFF;
                font-size: 18px; font-weight: 800;
                padding: 1px;
                outline: none;
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpCellButton:hover:enabled {
                border: 2px solid #45DBFF;
                background: rgba(8, 82, 118, 42);
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpCellButton:pressed:enabled {
                background: rgba(18, 103, 134, 96);
                border: 2px solid #9AEDFF;
            }
            /* C08: foco de mouse nao herda contorno branco nativo;
               o foco acessivel por teclado continua destacado em ciano. */
            QWidget#arenaPremiumChimpanze QPushButton#chimpCellButton:focus {
                outline: none;
                border: 1px solid #337DA5;
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpCellButton:hover:enabled:focus {
                border: 2px solid #45DBFF;
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpCellButton:pressed:enabled:focus {
                border: 2px solid #9AEDFF;
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpCellButton[keyboardFocus="true"]:focus {
                border: 2px solid #58DFFF;
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpCellButton[cellState="number"] {
                color: #FFFFFF;
                border: 1px solid #59D9FA;
                background-color: rgba(8, 81, 113, 241);
                font-size: 19px;
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpCellButton[cellState="correct"] {
                background-color: rgba(7, 98, 96, 202);
                border: 1px solid #3ECFC5;
            }
            QWidget#arenaPremiumChimpanze QPushButton#chimpCellButton:disabled {
                color: #C8E6F1;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 11, 12, 12)
        layout.setSpacing(8)

        # C04: unico palco de floresta conservado. Mudanca somente na largura
        # do widget das celulas; CTA, titulo e area do gorila permanecem.
        palco = _ArenaPremiumChimpBoard(self)
        palco.setObjectName("chimpUnifiedStage")
        palco.setAccessibleName("Cenario unificado do desafio do Chimpanze")
        palco_layout = QVBoxLayout(palco)
        palco_layout.setContentsMargins(0, 0, 0, 0)
        palco_layout.setSpacing(8)

        # D01: remocao visual integral da faixa superior solicitada.
        # Metadados permanecem como QLabels filhos invisiveis para:
        # 1) preservar os metodos originais que atualizam status/nivel;
        # 2) manter a busca de gameHint pelo cartao lateral "Como jogar".
        # O contêiner de metadados nao ocupa espaco em qualquer layout.
        metadados = QWidget(self)
        metadados.setObjectName("chimpInvisibleMetadata")
        metadados.hide()

        dica = QLabel(
            "Memorize as posições. Clique no 1; os demais números desaparecem. "
            "Depois continue 2, 3, 4... pelas posições corretas.",
            metadados,
        )
        dica.setObjectName("gameHint")
        dica.setWordWrap(True)

        self.status = QLabel("Clique em Iniciar.", metadados)
        self.status.setObjectName("gameStatus")
        self.status.setAccessibleName("Estado atual do desafio")

        self.nivel_label = QLabel("Nível 4", metadados)
        self.nivel_label.setObjectName("gameMetric")
        self.nivel_label.setAccessibleName("Nivel atual do desafio")
        # A area liberada passa integralmente ao viewport da grade/floresta;
        # os 25 botoes e o CTA original seguem inalterados.

        # F11: the same single button remains in the lower action band.
        self.iniciar_btn = QPushButton("▶  Iniciar desafio")
        self.iniciar_btn.setObjectName("chimpPremiumStartCTA")
        self.iniciar_btn.setAccessibleName("Iniciar ou recomecar desafio do Chimpanze")
        self.iniciar_btn.setToolTip("Inicia uma partida ou reinicia o desafio atual")
        # C07: politica expansivel; o HBox divide a faixa em 19%/62%/19%.
        # Nao altera o mesmo botao nem sua conexao unica com iniciar_partida.
        self.iniciar_btn.setMinimumWidth(200)
        self.iniciar_btn.setMaximumWidth(840)
        self.iniciar_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.iniciar_btn.clicked.connect(self.iniciar_partida)

        # C04: o viewport e a cena do gorila permanecem em LARGURA TOTAL;
        # apenas os 25 botoes ocupam um filho estreito a esquerda.
        # A area direita e pintura de floresta, sem widgets ou cliques falsos.
        grade_container = _ArenaC04BoardViewport(palco)
        grade_container.setObjectName("chimpPremiumBoardViewport")
        palco._gorila_viewport = grade_container
        linha_grade = QHBoxLayout(grade_container)
        linha_grade.setContentsMargins(0, 0, 0, 0)
        linha_grade.setSpacing(0)
        area_grade = QWidget(grade_container)
        area_grade.setObjectName("chimpC04GridArea")
        # BG02: widget contêiner não deve preencher o cenário com o fundo
        # herdado do tema. Mantém foco, eventos e dimensões intactos.
        area_grade.setAutoFillBackground(False)
        area_grade.setAttribute(Qt.WA_TranslucentBackground, True)
        area_grade.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        # C05: referencia ~2,4:1 em desktop; mantem 5x5 sem escala falsa.
        # Ganhamos altura para os botões reduzindo apenas as margens internas
        # e os vazios verticais, sem modificar altura da cena ou do CTA.
        grade = QGridLayout(area_grade)
        grade.setContentsMargins(9, 7, 9, 7)
        grade.setHorizontalSpacing(7)
        grade.setVerticalSpacing(5)
        for indice in range(5):
            grade.setColumnStretch(indice, 1)
            grade.setRowStretch(indice, 1)
        # D02: centralizacao REAL dos 25 botoes no viewport cinematografico.
        # Dois espacadores simetricos dividem igualmente a largura livre,
        # sem alterar o tamanho do tabuleiro nem a geometria vertical.
        # A floresta/gorila seguem pintados ao fundo e podem ficar encobertos.
        linha_grade.addStretch(1)
        linha_grade.addWidget(area_grade, 0)
        linha_grade.addStretch(1)
        grade_container.vincular_grade(area_grade)
        self.botoes = []
        for i in range(25):
            botao = _ArenaF09ChimpCell("")
            botao.setObjectName("chimpCellButton")
            # C05: minimo logico sem forcar overflow em alturas compactas;
            # a celula cresce igualmente com a area disponivel.
            botao.setMinimumSize(44, 43)
            botao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # C09: a descricao anuncia a posicao sem sobrepor o texto dinamico
            # dos numeros ou falsear os estados mostrados pelo QPushButton.
            botao.setAccessibleDescription(
                f"Linha {i // 5 + 1}, coluna {i % 5 + 1} do tabuleiro 5 por 5."
            )
            botao.clicked.connect(lambda _=False, idx=i: self.clicar(idx))
            botao.setEnabled(False)
            grade.addWidget(botao, i // 5, i % 5)
            self.botoes.append(botao)

        palco_layout.addWidget(grade_container, 1)

        # F11: CTA abaixo da grade, sem sobreposicao de celulas.
        # A Arena possui QScrollArea externa (L14), garantindo acesso em janela baixa.
        faixa_acao = QFrame(palco)
        faixa_acao.setObjectName("chimpPremiumActionBand")
        botoes_acao = QHBoxLayout(faixa_acao)
        botoes_acao.setContentsMargins(8, 4, 8, 4)
        botoes_acao.setSpacing(0)
        # C07: 2 : 6 : 2 = 60% aproximadamente; sem geometria absoluta.
        # O botão ocupa a faixa útil, respeitando limites Qt em janelas menores.
        botoes_acao.addStretch(2)
        botoes_acao.addWidget(self.iniciar_btn, 6)
        botoes_acao.addStretch(2)
        faixa_acao.setAccessibleName("Faixa inferior para iniciar ou recomecar o desafio")
        palco_layout.addWidget(faixa_acao, 0)
        layout.addWidget(palco, 1)

    def _estado_botao(self, botao, estado):
        botao.setProperty("cellState", estado)
        _repolir(botao)

    def iniciar_partida(self):
        self.token_rodada += 1
        self.nivel = 4
        self.maior_nivel_concluido = 0
        self.inicio = datetime.now()
        self.ativo = True
        self.iniciar_btn.setText("Recomeçar")
        self.preparar_nivel()

    def preparar_nivel(self):
        if not self.ativo:
            return

        self.token_rodada += 1
        self.nivel_label.setText(f"Nível {self.nivel}")
        self.status.setText("Memorize e clique primeiro no número 1.")
        self.esperado = 1

        quantidade = min(self.nivel, len(self.botoes))
        posicoes = random.sample(range(len(self.botoes)), quantidade)
        self.mapa = {posicao: numero for numero, posicao in enumerate(posicoes, 1)}

        for i, botao in enumerate(self.botoes):
            botao.setEnabled(True)
            numero = self.mapa.get(i)
            botao.setText(str(numero) if numero is not None else "")
            self._estado_botao(botao, "number" if numero is not None else "blank")

    def clicar(self, indice):
        if not self.ativo:
            return

        numero = self.mapa.get(indice)
        if numero != self.esperado:
            self.encerrar_falha()
            return

        botao = self.botoes[indice]
        botao.setText("")
        botao.setEnabled(False)
        self._estado_botao(botao, "correct")

        if self.esperado == 1:
            # Depois do primeiro acerto, os números ainda não tocados desaparecem.
            for posicao, numero_posicao in self.mapa.items():
                if numero_posicao > 1:
                    self.botoes[posicao].setText("")

        self.esperado += 1

        if self.esperado > len(self.mapa):
            self.maior_nivel_concluido = max(self.maior_nivel_concluido, self.nivel)
            for item_botao in self.botoes:
                item_botao.setEnabled(False)
            if self.nivel >= 20:
                self.encerrar_vitoria()
                return
            self.status.setText("Sequência correta. Próximo nível...")
            self.nivel += 1
            token = self.token_rodada
            QTimer.singleShot(
                650,
                lambda: self.preparar_nivel() if self.ativo and token == self.token_rodada else None,
            )

    def encerrar_falha(self):
        if not self.ativo:
            return
        self.ativo = False
        duracao = int((datetime.now() - self.inicio).total_seconds()) if self.inicio else 0
        nivel_alcancado = max(self.nivel, self.maior_nivel_concluido)
        self.status.setText(
            f"Falhou no nível {self.nivel}. Melhor nível concluído: "
            f"{self.maior_nivel_concluido or 'nenhum'}."
        )
        for botao in self.botoes:
            botao.setEnabled(False)
        self.registrar_resultado(
            pontuacao=self.maior_nivel_concluido,
            nivel=nivel_alcancado,
            duracao=duracao,
        )

    def encerrar_vitoria(self):
        self.ativo = False
        duracao = int((datetime.now() - self.inicio).total_seconds()) if self.inicio else 0
        self.status.setText("Você concluiu o nível máximo desta versão: 20.")
        for botao in self.botoes:
            botao.setEnabled(False)
        self.registrar_resultado(pontuacao=20, nivel=20, duracao=duracao)


class _ArenaPremiumMemoryBoard(QFrame):
    """Paisagem decorativa local, desenhada por tras das 16 cartas Qt reais."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("memoryPremiumBoard")
        self._imagem, self._imagem_valida = _arena_premium_art.carregar_pixmap(
            "ambiente_memoria", tamanho_fallback=(1400, 820)
        )
        self._imagem_cache = None
        self._dimensao_cache = None

    def resizeEvent(self, event):
        self._imagem_cache = None
        self._dimensao_cache = None
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        borda = QPainterPath()
        borda.addRoundedRect(QRectF(self.rect()).adjusted(0.7, 0.7, -0.7, -0.7), 13.0, 13.0)
        painter.setClipPath(borda)
        painter.fillPath(borda, QColor("#08182F"))
        if self._imagem_valida and not self._imagem.isNull():
            tamanho = self.size()
            if self._imagem_cache is None or self._dimensao_cache != tamanho:
                self._imagem_cache = self._imagem.scaled(
                    tamanho, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                )
                self._dimensao_cache = tamanho
            pm = self._imagem_cache
            painter.drawPixmap((self.width() - pm.width()) // 2,
                               (self.height() - pm.height()) // 2, pm)
        sombra = QLinearGradient(0, 0, 0, max(1, self.height()))
        sombra.setColorAt(0.0, QColor(4, 12, 32, 75))
        sombra.setColorAt(0.52, QColor(5, 14, 32, 65))
        sombra.setColorAt(1.0, QColor(4, 12, 30, 104))
        painter.fillRect(self.rect(), QBrush(sombra))
        painter.setClipping(False)
        painter.setPen(QPen(QColor("#365DAA"), 1.2))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(borda)
        painter.end()


class JogoMemoria(_BaseJogo):
    jogo_id = "memoria"

    def __init__(self, ao_registrar=None, parent=None):
        super().__init__(ao_registrar, parent)

        self.valores = []
        self.abertas = []
        self.encontradas = set()
        self.movimentos = 0
        self.bloqueado = False
        self.inicio = None
        self.token_partida = 0

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.atualizar_tempo)

        # L09: exclusivamente apresentação do jogo Memoria; motor preservado.
        self.setObjectName("arenaPremiumMemoria")
        self.setStyleSheet("""
            QWidget#arenaPremiumMemoria { background: transparent; }
            QWidget#arenaPremiumMemoria QFrame#memoryPremiumTitleCard {
                background-color: #101F3A; border: 1px solid #42578A;
                border-radius: 11px;
            }
            QWidget#arenaPremiumMemoria QLabel#memoryPremiumIcon {
                background: #1D2A59; border: 1px solid #7180E0; border-radius: 9px;
            }
            QWidget#arenaPremiumMemoria QLabel#gameTitle {
                background: transparent; border: 0px;
                color: #F4F6FF; font-size: 19px; font-weight: 800;
            }
            QWidget#arenaPremiumMemoria QLabel#gameHint {
                background: transparent; border: 0px;
                color: #B9C8EF; font-size: 11px;
            }
            QWidget#arenaPremiumMemoria QFrame#memoryPremiumStatusStrip {
                background: #0A1C37; border: 1px solid #354F81;
                border-radius: 9px;
            }
            QWidget#arenaPremiumMemoria QLabel#gameMetric {
                background: #18274F; color: #C7D1FF;
                border: 1px solid #5C77B8; border-radius: 7px;
                padding: 6px 10px; font-size: 12px; font-weight: 800;
            }
            QWidget#arenaPremiumMemoria QLabel#gameStatus {
                background: transparent; border: none;
                color: #C5D5EB; font-size: 11px;
            }
            QWidget#arenaPremiumMemoria QPushButton#gamePrimaryButton {
                background: #157CA9; color: #F7FCFF;
                border: 1px solid #45D8F0; border-radius: 8px;
                padding: 7px 12px; font-size: 12px; font-weight: 750;
                min-height: 27px;
            }
            QWidget#arenaPremiumMemoria QPushButton#gamePrimaryButton:hover {
                background: #0C9BBD; border-color: #A3EDFF;
            }
            QWidget#arenaPremiumMemoria QPushButton#gamePrimaryButton:focus {
                border: 2px solid #C4F4FF;
            }
            QWidget#arenaPremiumMemoria QPushButton#memoryCardButton {
                background-color: rgba(10, 29, 57, 183);
                border: 1px solid #526CAD;
                border-radius: 10px;
                color: #CAD7FF;
                font-size: 23px; font-weight: 800;
                padding: 1px;
            }
            QWidget#arenaPremiumMemoria QPushButton#memoryCardButton:hover:enabled {
                background-color: rgba(32, 49, 101, 217);
                border: 2px solid #8EADFF;
            }
            QWidget#arenaPremiumMemoria QPushButton#memoryCardButton:focus {
                border: 2px solid #E0E8FF;
            }
            QWidget#arenaPremiumMemoria QPushButton#memoryCardButton[cardState="open"] {
                background-color: rgba(75, 49, 143, 238);
                border: 2px solid #B8A3FF;
                color: #FFFFFF;
            }
            QWidget#arenaPremiumMemoria QPushButton#memoryCardButton[cardState="matched"] {
                background-color: rgba(9, 103, 111, 237);
                border: 1px solid #48DCCF;
                color: #F4FFFF;
            }
            QWidget#arenaPremiumMemoria QPushButton#memoryCardButton[cardState="matched"]:disabled {
                background-color: rgba(9, 103, 111, 237);
                border: 1px solid #48DCCF;
                color: #F4FFFF;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 11, 12, 12)
        layout.setSpacing(8)

        topo = QFrame(self)
        topo.setObjectName("memoryPremiumTitleCard")
        topo_layout = QHBoxLayout(topo)
        topo_layout.setContentsMargins(11, 7, 12, 7)
        topo_layout.setSpacing(10)
        icone = QLabel(topo)
        icone.setObjectName("memoryPremiumIcon")
        icone.setAlignment(Qt.AlignCenter)
        icone.setFixedSize(43, 43)
        icone.setPixmap(_arena_premium_icone_aba(1).pixmap(QSize(27, 27)))
        icone.setAccessibleName("Icone do jogo da Memoria")
        topo_layout.addWidget(icone)
        textos = QVBoxLayout()
        textos.setContentsMargins(0, 0, 0, 0)
        textos.setSpacing(2)
        titulo = QLabel("Jogo da Memória")
        titulo.setObjectName("gameTitle")
        textos.addWidget(titulo)
        dica = QLabel(
            "Encontre os oito pares com o menor número de movimentos possível. "
            "As cartas usam letras para manter o jogo leve e rápido."
        )
        dica.setObjectName("gameHint")
        dica.setWordWrap(True)
        textos.addWidget(dica)
        topo_layout.addLayout(textos, 1)
        layout.addWidget(topo)

        faixa = QFrame(self)
        faixa.setObjectName("memoryPremiumStatusStrip")
        barra = QHBoxLayout(faixa)
        barra.setContentsMargins(10, 5, 10, 5)
        barra.setSpacing(9)
        self.movimentos_label = QLabel("Movimentos: 0")
        self.movimentos_label.setObjectName("gameMetric")
        self.tempo_label = QLabel("Tempo: 00:00")
        self.tempo_label.setObjectName("gameMetric")
        self.status = QLabel("Nova partida pronta.")
        self.status.setObjectName("gameStatus")
        self.status.setWordWrap(True)
        barra.addWidget(self.movimentos_label)
        barra.addWidget(self.tempo_label)
        barra.addWidget(self.status, 1)
        novo = QPushButton("Nova partida")
        novo.setObjectName("gamePrimaryButton")
        novo.clicked.connect(self.nova_partida)
        barra.addWidget(novo)
        layout.addWidget(faixa)

        painel = _ArenaPremiumMemoryBoard(self)
        grade = QGridLayout(painel)
        grade.setContentsMargins(13, 13, 13, 13)
        grade.setSpacing(8)
        self.botoes = []
        for i in range(16):
            botao = QPushButton("?")
            botao.setObjectName("memoryCardButton")
            botao.setMinimumSize(64, 64)
            botao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            botao.clicked.connect(lambda _=False, idx=i: self.virar(idx))
            grade.addWidget(botao, i // 4, i % 4)
            self.botoes.append(botao)
        layout.addWidget(painel, 1)
        self.nova_partida()

    def _estado(self, botao, estado):
        botao.setProperty("cardState", estado)
        _repolir(botao)

    def nova_partida(self):
        self.token_partida += 1
        self.timer.stop()
        pares = list("ABCDEFGH") * 2
        random.shuffle(pares)
        self.valores = pares
        self.abertas = []
        self.encontradas = set()
        self.movimentos = 0
        self.bloqueado = False
        self.inicio = None
        self.movimentos_label.setText("Movimentos: 0")
        self.tempo_label.setText("Tempo: 00:00")
        self.status.setText("Clique em uma carta para iniciar o tempo.")
        for botao in self.botoes:
            botao.setText("?")
            botao.setEnabled(True)
            self._estado(botao, "hidden")

    def atualizar_tempo(self):
        if not self.inicio:
            return
        duracao = int((datetime.now() - self.inicio).total_seconds())
        self.tempo_label.setText(f"Tempo: {_formatar_tempo(duracao)}")

    def virar(self, indice):
        if self.bloqueado or indice in self.encontradas or indice in self.abertas:
            return

        if self.inicio is None:
            self.inicio = datetime.now()
            self.timer.start()
            self.status.setText("Encontre os pares.")

        botao = self.botoes[indice]
        botao.setText(self.valores[indice])
        self._estado(botao, "open")
        self.abertas.append(indice)

        if len(self.abertas) < 2:
            return

        self.movimentos += 1
        self.movimentos_label.setText(f"Movimentos: {self.movimentos}")
        primeiro, segundo = self.abertas

        if self.valores[primeiro] == self.valores[segundo]:
            self.encontradas.update(self.abertas)
            for idx in self.abertas:
                self.botoes[idx].setEnabled(False)
                self._estado(self.botoes[idx], "matched")
            self.abertas = []
            if len(self.encontradas) == len(self.botoes):
                self.concluir()
            return

        self.bloqueado = True
        token = self.token_partida
        QTimer.singleShot(650, lambda: self.esconder_par(token))

    def esconder_par(self, token):
        if token != self.token_partida:
            return
        for idx in self.abertas:
            if idx not in self.encontradas:
                self.botoes[idx].setText("?")
                self._estado(self.botoes[idx], "hidden")
        self.abertas = []
        self.bloqueado = False

    def concluir(self):
        self.timer.stop()
        duracao = int((datetime.now() - self.inicio).total_seconds()) if self.inicio else 0
        self.status.setText(
            f"Concluído em {self.movimentos} movimentos e {_formatar_tempo(duracao)}."
        )
        pontuacao = max(1, 1500 - (self.movimentos * 35) - duracao)
        self.registrar_resultado(
            pontuacao=pontuacao,
            nivel=8,
            duracao=duracao,
            movimentos=self.movimentos,
        )


class _ArenaPremiumSequenceBoard(QFrame):
    """Fundo ambiental sem interacao; nove botoes Qt continuam acima da arte."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sequencePremiumBoard")
        self._imagem, self._imagem_valida = _arena_premium_art.carregar_pixmap(
            "ambiente_sequencia", tamanho_fallback=(1400, 820)
        )
        self._imagem_cache = None
        self._dimensao_cache = None

    def resizeEvent(self, event):
        self._imagem_cache = None
        self._dimensao_cache = None
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        contorno = QPainterPath()
        contorno.addRoundedRect(QRectF(self.rect()).adjusted(0.7, 0.7, -0.7, -0.7), 13.0, 13.0)
        painter.setClipPath(contorno)
        painter.fillPath(contorno, QColor("#061B30"))
        if self._imagem_valida and not self._imagem.isNull():
            tamanho = self.size()
            if self._imagem_cache is None or self._dimensao_cache != tamanho:
                self._imagem_cache = self._imagem.scaled(
                    tamanho, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                )
                self._dimensao_cache = tamanho
            imagem = self._imagem_cache
            painter.drawPixmap((self.width() - imagem.width()) // 2,
                               (self.height() - imagem.height()) // 2, imagem)
        sombra = QLinearGradient(0, 0, 0, max(1, self.height()))
        sombra.setColorAt(0.0, QColor(3, 13, 30, 93))
        sombra.setColorAt(0.55, QColor(5, 16, 33, 75))
        sombra.setColorAt(1.0, QColor(3, 13, 28, 105))
        painter.fillRect(self.rect(), QBrush(sombra))
        painter.setClipping(False)
        painter.setPen(QPen(QColor("#1D90C3"), 1.2))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(contorno)
        painter.end()


class JogoSequenciaVisual(_BaseJogo):
    jogo_id = "sequencia"

    def __init__(self, ao_registrar=None, parent=None):
        super().__init__(ao_registrar, parent)

        self.sequencia = []
        self.indice_usuario = 0
        self.melhor_concluida = 0
        self.ativo = False
        self.reproduzindo = False
        self.inicio = None
        self.token_partida = 0

        # L10: mudanca exclusivamente visual, com motor temporal intocado.
        self.setObjectName("arenaPremiumSequencia")
        self.setStyleSheet("""
            QWidget#arenaPremiumSequencia { background: transparent; }
            QWidget#arenaPremiumSequencia QFrame#sequencePremiumTitleCard {
                background-color: #0A233A; border: 1px solid #24688B;
                border-radius: 11px;
            }
            QWidget#arenaPremiumSequencia QLabel#sequencePremiumIcon {
                background-color: #0D3B56; border: 1px solid #39ACDC;
                border-radius: 9px;
            }
            QWidget#arenaPremiumSequencia QLabel#gameTitle {
                background: transparent; border: none;
                color: #F0FAFF; font-size: 19px; font-weight: 800;
            }
            QWidget#arenaPremiumSequencia QLabel#gameHint {
                background: transparent; border: none;
                color: #B7DBF0; font-size: 11px;
            }
            QWidget#arenaPremiumSequencia QFrame#sequencePremiumStatusStrip {
                background-color: #071D32; border: 1px solid #215374;
                border-radius: 9px;
            }
            QWidget#arenaPremiumSequencia QLabel#gameMetric {
                background-color: #0A3650; color: #76E9FF;
                border: 1px solid #237C9D; border-radius: 7px;
                padding: 6px 10px; font-size: 12px; font-weight: 800;
            }
            QWidget#arenaPremiumSequencia QLabel#gameStatus {
                background: transparent; border: none;
                color: #C2DEF0; font-size: 11px;
            }
            QWidget#arenaPremiumSequencia QPushButton#gamePrimaryButton {
                background-color: #0B89B4; color: #F9FEFF;
                border: 1px solid #42CBF5; border-radius: 8px;
                padding: 7px 13px; min-height: 27px;
                font-size: 12px; font-weight: 750;
            }
            QWidget#arenaPremiumSequencia QPushButton#gamePrimaryButton:hover {
                background-color: #12A9CF; border-color: #A1EFFF;
            }
            QWidget#arenaPremiumSequencia QPushButton#gamePrimaryButton:focus {
                border: 2px solid #DEF9FF;
            }
            QWidget#arenaPremiumSequencia QPushButton#sequenceCellButton {
                background-color: rgba(8, 37, 62, 200);
                border: 1px solid #297C9F; border-radius: 12px;
                padding: 1px;
            }
            QWidget#arenaPremiumSequencia QPushButton#sequenceCellButton:hover:enabled {
                background-color: rgba(16, 75, 106, 227);
                border: 2px solid #61D8F6;
            }
            QWidget#arenaPremiumSequencia QPushButton#sequenceCellButton:focus {
                border: 2px solid #E2FBFF;
            }
            QWidget#arenaPremiumSequencia QPushButton#sequenceCellButton[lit="true"] {
                background-color: rgba(40, 220, 255, 250);
                border: 3px solid #F0FFFF;
            }
            QWidget#arenaPremiumSequencia QPushButton#sequenceCellButton[lit="true"]:disabled {
                background-color: rgba(40, 220, 255, 250);
                border: 3px solid #F0FFFF;
            }
            QWidget#arenaPremiumSequencia QPushButton#sequenceCellButton[lit="false"]:disabled {
                background-color: rgba(8, 37, 62, 200);
                border: 1px solid #297C9F;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 11, 12, 12)
        layout.setSpacing(8)

        topo = QFrame(self)
        topo.setObjectName("sequencePremiumTitleCard")
        topo_layout = QHBoxLayout(topo)
        topo_layout.setContentsMargins(11, 7, 12, 7)
        topo_layout.setSpacing(10)
        icone = QLabel(topo)
        icone.setObjectName("sequencePremiumIcon")
        icone.setAlignment(Qt.AlignCenter)
        icone.setFixedSize(43, 43)
        icone.setPixmap(_arena_premium_icone_aba(2).pixmap(QSize(27, 27)))
        icone.setAccessibleName("Icone do jogo Sequencia Visual")
        topo_layout.addWidget(icone)
        textos = QVBoxLayout()
        textos.setContentsMargins(0, 0, 0, 0)
        textos.setSpacing(2)
        titulo = QLabel("Sequência Visual")
        titulo.setObjectName("gameTitle")
        textos.addWidget(titulo)
        dica = QLabel(
            "Observe os quadrados que acendem e repita a sequência na mesma ordem. "
            "A cada rodada, um novo passo é acrescentado."
        )
        dica.setObjectName("gameHint")
        dica.setWordWrap(True)
        textos.addWidget(dica)
        topo_layout.addLayout(textos, 1)
        layout.addWidget(topo)

        faixa = QFrame(self)
        faixa.setObjectName("sequencePremiumStatusStrip")
        barra = QHBoxLayout(faixa)
        barra.setContentsMargins(10, 5, 10, 5)
        barra.setSpacing(9)
        self.nivel_label = QLabel("Sequência: 3")
        self.nivel_label.setObjectName("gameMetric")
        self.status = QLabel("Clique em Iniciar.")
        self.status.setObjectName("gameStatus")
        self.status.setWordWrap(True)
        barra.addWidget(self.nivel_label)
        barra.addWidget(self.status, 1)
        iniciar = QPushButton("Iniciar")
        iniciar.setObjectName("gamePrimaryButton")
        iniciar.clicked.connect(self.iniciar_partida)
        barra.addWidget(iniciar)
        layout.addWidget(faixa)

        painel = _ArenaPremiumSequenceBoard(self)
        grade = QGridLayout(painel)
        grade.setContentsMargins(14, 14, 14, 14)
        grade.setSpacing(11)

        self.botoes = []
        for i in range(9):
            botao = QPushButton("")
            botao.setObjectName("sequenceCellButton")
            botao.setProperty("lit", False)
            botao.setMinimumSize(74, 74)
            botao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            botao.clicked.connect(lambda _=False, idx=i: self.clicar(idx))
            botao.setEnabled(False)
            grade.addWidget(botao, i // 3, i % 3)
            self.botoes.append(botao)

        layout.addWidget(painel, 1)

    def _lit(self, indice, aceso):
        botao = self.botoes[indice]
        botao.setProperty("lit", bool(aceso))
        _repolir(botao)

    def iniciar_partida(self):
        self.token_partida += 1
        self.sequencia = [random.randrange(9) for _ in range(3)]
        self.indice_usuario = 0
        self.melhor_concluida = 0
        self.ativo = True
        self.inicio = datetime.now()
        self.nivel_label.setText("Sequência: 3")
        self.reproduzir()

    def reproduzir(self):
        if not self.ativo:
            return
        self.token_partida += 1
        token = self.token_partida
        self.reproduzindo = True
        self.indice_usuario = 0
        self.status.setText("Observe a sequência...")
        for botao in self.botoes:
            botao.setEnabled(False)
            botao.setProperty("lit", False)
            _repolir(botao)
        self._reproduzir_passo(token, 0)

    def _reproduzir_passo(self, token, posicao):
        if token != self.token_partida or not self.ativo:
            return
        if posicao >= len(self.sequencia):
            self.reproduzindo = False
            self.status.setText("Sua vez.")
            for botao in self.botoes:
                botao.setEnabled(True)
            return

        indice = self.sequencia[posicao]
        self._lit(indice, True)

        def apagar():
            if token != self.token_partida or not self.ativo:
                return
            self._lit(indice, False)
            QTimer.singleShot(170, lambda: self._reproduzir_passo(token, posicao + 1))

        QTimer.singleShot(340, apagar)

    def clicar(self, indice):
        if not self.ativo or self.reproduzindo:
            return

        self._lit(indice, True)
        QTimer.singleShot(130, lambda: self._lit(indice, False))

        if indice != self.sequencia[self.indice_usuario]:
            self.encerrar()
            return

        self.indice_usuario += 1
        if self.indice_usuario < len(self.sequencia):
            return

        self.melhor_concluida = max(self.melhor_concluida, len(self.sequencia))
        self.status.setText("Correto. A sequência vai aumentar.")
        for botao in self.botoes:
            botao.setEnabled(False)
        self.sequencia.append(random.randrange(9))
        self.nivel_label.setText(f"Sequência: {len(self.sequencia)}")
        token = self.token_partida
        QTimer.singleShot(
            650,
            lambda: self.reproduzir() if self.ativo and token == self.token_partida else None,
        )

    def encerrar(self):
        if not self.ativo:
            return
        self.ativo = False
        self.token_partida += 1
        duracao = int((datetime.now() - self.inicio).total_seconds()) if self.inicio else 0
        for botao in self.botoes:
            botao.setEnabled(False)
            botao.setProperty("lit", False)
            _repolir(botao)
        self.status.setText(
            f"Sequência incorreta. Melhor sequência concluída: {self.melhor_concluida}."
        )
        self.registrar_resultado(
            pontuacao=self.melhor_concluida,
            nivel=self.melhor_concluida,
            duracao=duracao,
        )


class _ArenaPremiumRotationBoard(QFrame):
    """Ambiente de rotacao: somente pintura; as seis opcoes reais ficam acima."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("rotationPremiumBoard")
        self._imagem, self._imagem_valida = _arena_premium_art.carregar_pixmap(
            "ambiente_rotacao", tamanho_fallback=(1400, 820)
        )
        self._cache = None
        self._cache_size = None

    def resizeEvent(self, event):
        self._cache = None
        self._cache_size = None
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        caminho = QPainterPath()
        caminho.addRoundedRect(QRectF(self.rect()).adjusted(0.7, 0.7, -0.7, -0.7), 12, 12)
        painter.setClipPath(caminho)
        painter.fillPath(caminho, QColor("#08182E"))
        if self._imagem_valida and not self._imagem.isNull():
            tamanho = self.size()
            if self._cache is None or self._cache_size != tamanho:
                self._cache = self._imagem.scaled(
                    tamanho, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                )
                self._cache_size = tamanho
            fundo = self._cache
            painter.drawPixmap((self.width() - fundo.width()) // 2,
                               (self.height() - fundo.height()) // 2, fundo)
        # A arte nunca interfere com as figuras e botoes Qt.
        sombra = QLinearGradient(0, 0, 0, max(1, self.height()))
        sombra.setColorAt(0.0, QColor(3, 12, 30, 78))
        sombra.setColorAt(0.55, QColor(4, 13, 33, 72))
        sombra.setColorAt(1.0, QColor(3, 12, 30, 94))
        painter.fillRect(self.rect(), QBrush(sombra))
        painter.setClipping(False)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("#7765BF"), 1.2))
        painter.drawPath(caminho)
        painter.end()


class JogoRotacaoVisual(_BaseJogo):
    jogo_id = "rotacao_visual"

    def __init__(self, ao_registrar=None, parent=None):
        super().__init__(ao_registrar, parent)

        self.nivel = 1
        self.pontuacao = 0
        self.acertos = 0
        self.sequencia_acertos = 0
        self.ativo = False
        self.bloqueado = True
        self.inicio = None
        self.fim_questao = None
        self.token_rodada = 0
        self.forma_original = tuple()
        self.resposta_correta = tuple()
        self.operacoes = tuple()
        self.formas_opcoes = [tuple()] * 6

        self.timer_questao = QTimer(self)
        self.timer_questao.setInterval(100)
        self.timer_questao.timeout.connect(self.atualizar_tempo_questao)

        # L11: estilos locais; os temporizadores, opcoes, algoritmos e banco nao mudam.
        self.setObjectName("arenaPremiumRotacao")
        self.setStyleSheet("""
            QWidget#arenaPremiumRotacao { background: transparent; }
            QWidget#arenaPremiumRotacao QScrollArea#rotationScrollArea {
                background: transparent; border: none;
            }
            QWidget#arenaPremiumRotacao QWidget#rotationScrollContent {
                background: transparent;
            }
            QWidget#arenaPremiumRotacao QFrame#rotationPremiumTitleCard {
                background-color: #131F3D; border: 1px solid #565C9C;
                border-radius: 11px;
            }
            QWidget#arenaPremiumRotacao QLabel#rotationPremiumIcon {
                background: #292F60; border: 1px solid #8387E7;
                border-radius: 9px;
            }
            QWidget#arenaPremiumRotacao QLabel#gameTitle {
                background: transparent; border: none;
                color: #F4F2FF; font-size: 19px; font-weight: 800;
            }
            QWidget#arenaPremiumRotacao QLabel#gameHint {
                background: transparent; border: none;
                color: #C9C9EC; font-size: 11px;
            }
            QWidget#arenaPremiumRotacao QFrame#rotationPremiumStatusStrip {
                background-color: #111B35; border: 1px solid #4B4D87;
                border-radius: 9px;
            }
            QWidget#arenaPremiumRotacao QLabel#gameMetric {
                background-color: #232E55; border: 1px solid #525FA1;
                border-radius: 7px; color: #D8D3FF;
                padding: 5px 8px; font-size: 11px; font-weight: 750;
            }
            QWidget#arenaPremiumRotacao QLabel#gameStatus {
                background: transparent; border: none;
                color: #D1D7FA; font-size: 11px;
            }
            QWidget#arenaPremiumRotacao QPushButton#gamePrimaryButton {
                background-color: #6558CB; border: 1px solid #ADA5FF;
                border-radius: 8px; padding: 6px 11px; min-height: 27px;
                color: #FFFFFF; font-weight: 750;
            }
            QWidget#arenaPremiumRotacao QPushButton#gamePrimaryButton:hover {
                background-color: #8071EA; border-color: #E2DCFF;
            }
            QWidget#arenaPremiumRotacao QPushButton#gamePrimaryButton:focus {
                border: 2px solid #F3EFFF;
            }
            QWidget#arenaPremiumRotacao QLabel#rotationOriginalLabel {
                background: transparent; border: none;
                color: #D0C9FF; font-weight: 750;
            }
            QWidget#arenaPremiumRotacao QLabel#rotationQuestionLabel {
                background-color: rgba(15, 26, 50, 216);
                color: #EDE9FF; border: 1px solid #504E86;
                border-radius: 8px; padding: 9px;
                font-size: 12px; font-weight: 650;
            }
            QWidget#arenaPremiumRotacao QWidget#rotationOptionsContainer {
                background: transparent; border: none;
            }
            QWidget#arenaPremiumRotacao QPushButton#rotationOptionButton {
                background-color: rgba(12, 27, 53, 229);
                border: 1px solid #595B9E; border-radius: 10px;
            }
            QWidget#arenaPremiumRotacao QPushButton#rotationOptionButton:hover:enabled {
                background-color: rgba(35, 48, 88, 238);
                border: 2px solid #A8A1FF;
            }
            QWidget#arenaPremiumRotacao QPushButton#rotationOptionButton:focus {
                border: 2px solid #E8E3FF;
            }
            QWidget#arenaPremiumRotacao QPushButton#rotationOptionButton[answerState="correct"] {
                background-color: rgba(12, 73, 72, 237);
                border: 3px solid #67F2CD;
            }
            QWidget#arenaPremiumRotacao QPushButton#rotationOptionButton[answerState="wrong"] {
                background-color: rgba(98, 28, 63, 237);
                border: 3px solid #FF8CB2;
            }
            QWidget#arenaPremiumRotacao QPushButton#rotationOptionButton[answerState="correct"]:disabled {
                background-color: rgba(12, 73, 72, 237);
                border: 3px solid #67F2CD;
            }
            QWidget#arenaPremiumRotacao QPushButton#rotationOptionButton[answerState="wrong"]:disabled {
                background-color: rgba(98, 28, 63, 237);
                border: 3px solid #FF8CB2;
            }
        """)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        # O conteúdo do minijogo fica dentro de uma área rolável. Em janelas
        # altas, tudo aparece de uma vez; em alturas menores, os cartões
        # preservam seu tamanho e a aba ganha rolagem vertical em vez de
        # comprimir ou recortar a segunda linha de alternativas.
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("rotationScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.viewport().setAutoFillBackground(False)

        conteudo_scroll = QWidget()
        conteudo_scroll.setObjectName("rotationScrollContent")
        conteudo_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QVBoxLayout(conteudo_scroll)
        layout.setContentsMargins(12, 11, 12, 14)
        layout.setSpacing(8)

        self.scroll_area.setWidget(conteudo_scroll)
        raiz.addWidget(self.scroll_area, 1)

        cabecalho = QFrame(conteudo_scroll)
        cabecalho.setObjectName("rotationPremiumTitleCard")
        cabecalho_linha = QHBoxLayout(cabecalho)
        cabecalho_linha.setContentsMargins(11, 7, 12, 7)
        cabecalho_linha.setSpacing(10)
        icone = QLabel(cabecalho)
        icone.setObjectName("rotationPremiumIcon")
        icone.setFixedSize(43, 43)
        icone.setAlignment(Qt.AlignCenter)
        icone.setPixmap(_arena_premium_icone_aba(3).pixmap(QSize(27, 27)))
        icone.setAccessibleName("Icone do jogo Rotacao Visual")
        cabecalho_linha.addWidget(icone)
        textos = QVBoxLayout()
        textos.setContentsMargins(0, 0, 0, 0)
        textos.setSpacing(2)
        titulo = QLabel("Rotação & Espelho")
        titulo.setObjectName("gameTitle")
        textos.addWidget(titulo)
        dica = QLabel(
            "Transforme mentalmente a forma e escolha o resultado correto. "
            "As alternativas são outras rotações/espelhamentos da mesma figura."
        )
        dica.setObjectName("gameHint")
        dica.setWordWrap(True)
        textos.addWidget(dica)
        cabecalho_linha.addLayout(textos, 1)
        layout.addWidget(cabecalho)

        faixa = QFrame(conteudo_scroll)
        faixa.setObjectName("rotationPremiumStatusStrip")
        barra = QHBoxLayout(faixa)
        barra.setContentsMargins(9, 5, 9, 5)
        barra.setSpacing(7)
        self.nivel_label = QLabel("Nível: 1")
        self.nivel_label.setObjectName("gameMetric")
        self.pontos_label = QLabel("Pontos: 0")
        self.pontos_label.setObjectName("gameMetric")
        self.sequencia_label = QLabel("Sequência: 0")
        self.sequencia_label.setObjectName("gameMetric")
        self.tempo_label = QLabel("Tempo: --")
        self.tempo_label.setObjectName("gameMetric")
        self.status = QLabel("Clique em Iniciar desafio.")
        self.status.setObjectName("gameStatus")
        self.status.setWordWrap(True)

        barra.addWidget(self.nivel_label)
        barra.addWidget(self.pontos_label)
        barra.addWidget(self.sequencia_label)
        barra.addWidget(self.tempo_label)
        barra.addStretch()
        barra.addWidget(self.status, 1)

        self.iniciar_btn = QPushButton("Iniciar desafio")
        self.iniciar_btn.setObjectName("gamePrimaryButton")
        self.iniciar_btn.clicked.connect(self.iniciar_partida)
        barra.addWidget(self.iniciar_btn)
        layout.addWidget(faixa)

        painel = _ArenaPremiumRotationBoard()
        painel.setObjectName("gameBoardPanel")
        painel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(14, 10, 14, 12)
        painel_layout.setSpacing(7)

        topo = QHBoxLayout()
        topo.setContentsMargins(0, 0, 0, 2)
        topo.setSpacing(16)

        # A forma original deixa de ocupar uma coluna estreita. O bloco recebe
        # 1/3 da largura do cabeçalho e o próprio canvas centraliza a peça,
        # aproximando-a do centro visual do painel sem roubar altura das opções.
        original_bloco = QVBoxLayout()
        original_bloco.setContentsMargins(0, 0, 0, 0)
        original_bloco.setSpacing(4)
        original_rotulo = QLabel("Forma original")
        original_rotulo.setObjectName("rotationOriginalLabel")
        original_rotulo.setAlignment(Qt.AlignCenter)
        self.preview_original = _FormaMatrizWidget(parent=painel)
        self.preview_original.setMinimumSize(180, 96)
        self.preview_original.setMaximumHeight(116)
        self.preview_original.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        original_bloco.addWidget(original_rotulo)
        paleta_original = self.preview_original.palette()
        paleta_original.setColor(QPalette.Highlight, QColor("#82DFF6"))
        self.preview_original.setPalette(paleta_original)
        original_bloco.addWidget(self.preview_original, 1)

        self.pergunta = QLabel("A transformação aparecerá aqui.")
        self.pergunta.setObjectName("rotationQuestionLabel")
        self.pergunta.setAlignment(Qt.AlignCenter)
        self.pergunta.setWordWrap(True)
        self.pergunta.setMinimumHeight(58)

        topo.addLayout(original_bloco, 1)
        topo.addWidget(self.pergunta, 2)
        painel_layout.addLayout(topo)

        # A grade recebe um contêiner próprio com altura mínima suficiente
        # para duas linhas completas. Isso impede que o QTabWidget comprima a
        # segunda linha quando a janela tem pouca altura.
        altura_opcao = 112
        espacamento_vertical = 10
        margem_grade_superior = 4
        margem_grade_inferior = 4

        self.opcoes_container = QWidget(painel)
        self.opcoes_container.setObjectName("rotationOptionsContainer")
        self.opcoes_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.opcoes_container.setMinimumHeight(
            (altura_opcao * 2)
            + espacamento_vertical
            + margem_grade_superior
            + margem_grade_inferior
        )

        self.opcoes_layout = QGridLayout(self.opcoes_container)
        self.opcoes_layout.setContentsMargins(0, margem_grade_superior, 0, margem_grade_inferior)
        self.opcoes_layout.setHorizontalSpacing(10)
        self.opcoes_layout.setVerticalSpacing(espacamento_vertical)
        for coluna in range(3):
            self.opcoes_layout.setColumnStretch(coluna, 1)
        for linha in range(2):
            self.opcoes_layout.setRowMinimumHeight(linha, altura_opcao)
            self.opcoes_layout.setRowStretch(linha, 1)

        self.opcoes = []
        for indice in range(6):
            botao = QPushButton("")
            botao.setObjectName("rotationOptionButton")
            botao.setMinimumSize(150, altura_opcao)
            botao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            botao.setProperty("answerState", "idle")
            conteudo = QVBoxLayout(botao)
            conteudo.setContentsMargins(10, 8, 10, 8)
            conteudo.setSpacing(0)
            desenho = _FormaMatrizWidget(parent=botao)
            desenho.setMinimumSize(110, 88)
            desenho.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            paleta = desenho.palette()
            paleta.setColor(QPalette.Highlight, QColor("#B8BDFF"))
            desenho.setPalette(paleta)
            botao.setAccessibleName(f"Alternativa {indice + 1} de Rotação Visual")
            conteudo.addWidget(desenho, 1)
            botao.clicked.connect(lambda _=False, idx=indice: self.responder(idx))
            self.opcoes_layout.addWidget(botao, indice // 3, indice % 3)
            self.opcoes.append((botao, desenho))

        painel_layout.addWidget(self.opcoes_container, 0)
        layout.addWidget(painel, 0)
        layout.addStretch(1)

        # O mínimo do conteúdo é maior que a área útil típica da aba em
        # resoluções mais baixas. Assim o QScrollArea assume a rolagem e não
        # permite que o QTabWidget esmague os cartões inferiores.
        conteudo_scroll.setMinimumHeight(520)

        self._limpar_opcoes()

    def _limite_tempo(self):
        return {1: 18.0, 2: 16.0, 3: 14.0, 4: 12.0, 5: 10.0}.get(self.nivel, 10.0)

    def _tamanho_forma(self):
        return 5 if self.nivel >= 4 else 4

    def _limpar_opcoes(self):
        for botao, desenho in self.opcoes:
            botao.setEnabled(False)
            botao.setProperty("answerState", "idle")
            desenho.set_forma(tuple())
            _repolir(botao)

    def iniciar_partida(self):
        self.token_rodada += 1
        self.timer_questao.stop()
        self.nivel = 1
        self.pontuacao = 0
        self.acertos = 0
        self.sequencia_acertos = 0
        self.ativo = True
        self.bloqueado = False
        self.inicio = datetime.now()
        self.iniciar_btn.setText("Nova partida")
        self.status.setText("Resolva antes do tempo acabar.")
        self._atualizar_metricas()
        self.preparar_desafio()

    def _atualizar_metricas(self):
        self.nivel_label.setText(f"Nível: {self.nivel}")
        self.pontos_label.setText(f"Pontos: {self.pontuacao}")
        self.sequencia_label.setText(f"Sequência: {self.sequencia_acertos}")

    def _escolher_sequencia(self, forma):
        candidatas = list(_sequencias_rotacao_por_nivel(self.nivel))
        random.shuffle(candidatas)
        for operacoes in candidatas:
            resultado = _aplicar_sequencia_forma(forma, operacoes)
            if resultado != forma:
                return operacoes, resultado
        operacoes = ("rot90",)
        return operacoes, _aplicar_sequencia_forma(forma, operacoes)

    def preparar_desafio(self):
        if not self.ativo:
            return

        self.token_rodada += 1
        self.bloqueado = False
        self.forma_original = _gerar_forma_assimetrica(self._tamanho_forma())
        self.operacoes, self.resposta_correta = self._escolher_sequencia(self.forma_original)

        variantes = [
            forma for forma in _variantes_dihedrais(self.forma_original)
            if forma != self.resposta_correta
        ]
        random.shuffle(variantes)
        alternativas = [self.resposta_correta] + variantes[:5]
        random.shuffle(alternativas)

        self.preview_original.set_forma(self.forma_original)
        if len(self.operacoes) == 1:
            texto = f"Qual forma resulta de {_ROTACAO_ROTULOS[self.operacoes[0]]}?"
        else:
            nomes = " → ".join(_ROTACAO_ROTULOS[op] for op in self.operacoes)
            texto = f"Aplique nesta ordem: {nomes}. Qual é o resultado?"
        self.pergunta.setText(texto)

        for indice, (botao, desenho) in enumerate(self.opcoes):
            forma = alternativas[indice]
            desenho.set_forma(forma)
            self.formas_opcoes[indice] = forma
            botao.setProperty("answerState", "idle")
            botao.setEnabled(True)
            _repolir(botao)

        limite = self._limite_tempo()
        self.fim_questao = time.monotonic() + limite
        self.tempo_label.setText(f"Tempo: {limite:.1f}s")
        self.status.setText("Escolha a transformação correta.")
        self.timer_questao.start()
        self._atualizar_metricas()

    def atualizar_tempo_questao(self):
        if not self.ativo or self.bloqueado or self.fim_questao is None:
            return
        restante = max(0.0, self.fim_questao - time.monotonic())
        self.tempo_label.setText(f"Tempo: {restante:.1f}s")
        if restante <= 0.0:
            self._encerrar_por_erro("Tempo esgotado.")

    def responder(self, indice):
        if not self.ativo or self.bloqueado:
            return
        if not (0 <= indice < len(self.opcoes)):
            return

        botao, _ = self.opcoes[indice]
        forma_escolhida = self.formas_opcoes[indice]
        if forma_escolhida == self.resposta_correta:
            self._acertar(indice)
        else:
            botao.setProperty("answerState", "wrong")
            _repolir(botao)
            self._encerrar_por_erro("Transformação incorreta.")

    def _marcar_resposta_correta(self):
        for indice, (botao, _) in enumerate(self.opcoes):
            if self.formas_opcoes[indice] == self.resposta_correta:
                botao.setProperty("answerState", "correct")
                _repolir(botao)
                return

    def _acertar(self, indice):
        self.bloqueado = True
        self.timer_questao.stop()
        restante = max(0.0, (self.fim_questao or 0) - time.monotonic())
        botao, _ = self.opcoes[indice]
        botao.setProperty("answerState", "correct")
        _repolir(botao)
        ganho = 100 + (self.nivel * 25) + int(restante * 6)
        self.pontuacao += ganho
        self.acertos += 1
        self.sequencia_acertos += 1
        novo_nivel = min(5, 1 + (self.acertos // 3))
        subiu = novo_nivel > self.nivel
        self.nivel = novo_nivel
        self._atualizar_metricas()
        self.status.setText(
            f"Correto. +{ganho} pontos" + (" • nível aumentado" if subiu else "") + "."
        )

        token = self.token_rodada
        QTimer.singleShot(
            620,
            lambda: self.preparar_desafio()
            if self.ativo and token == self.token_rodada
            else None,
        )

    def _encerrar_por_erro(self, motivo):
        if not self.ativo or self.bloqueado:
            return
        self.bloqueado = True
        self.ativo = False
        self.timer_questao.stop()
        self._marcar_resposta_correta()

        duracao = int((datetime.now() - self.inicio).total_seconds()) if self.inicio else 0
        self.tempo_label.setText("Tempo: --")
        self.status.setText(
            f"{motivo} Resultado: {self.pontuacao} pontos • {self.acertos} acerto(s)."
        )
        self.registrar_resultado(
            pontuacao=self.pontuacao,
            nivel=self.nivel,
            duracao=duracao,
        )

    def closeEvent(self, evento):
        self.timer_questao.stop()
        super().closeEvent(evento)


class _ArenaPremiumPuzzleBoard(QFrame):
    """Arte local L03 apenas atras das nove pecas Qt, sem areas clicaveis falsas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("puzzlePremiumBoard")
        self._imagem, self._imagem_valida = _arena_premium_art.carregar_pixmap(
            "ambiente_quebra_cabeca", tamanho_fallback=(1400, 820)
        )
        self._cache = None
        self._dimensao_cache = None

    def resizeEvent(self, event):
        self._cache = None
        self._dimensao_cache = None
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        contorno = QPainterPath()
        contorno.addRoundedRect(QRectF(self.rect()).adjusted(0.7, 0.7, -0.7, -0.7), 12, 12)
        painter.setClipPath(contorno)
        painter.fillPath(contorno, QColor("#071A30"))
        if self._imagem_valida and not self._imagem.isNull():
            tamanho = self.size()
            if self._cache is None or self._dimensao_cache != tamanho:
                self._cache = self._imagem.scaled(
                    tamanho, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                )
                self._dimensao_cache = tamanho
            imagem = self._cache
            painter.drawPixmap((self.width() - imagem.width()) // 2,
                               (self.height() - imagem.height()) // 2, imagem)
        # Sem informacoes de jogo na imagem; o overlay protege a legibilidade.
        sombra = QLinearGradient(0, 0, 0, max(1, self.height()))
        sombra.setColorAt(0.0, QColor(4, 16, 36, 85))
        sombra.setColorAt(0.5, QColor(4, 18, 40, 70))
        sombra.setColorAt(1.0, QColor(3, 14, 33, 106))
        painter.fillRect(self.rect(), QBrush(sombra))
        painter.setClipping(False)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("#268EB5"), 1.2))
        painter.drawPath(contorno)
        painter.end()


class JogoQuebraCabeca(_BaseJogo):
    jogo_id = "quebra_cabeca"

    def __init__(self, ao_registrar=None, parent=None):
        super().__init__(ao_registrar, parent)

        self.estado = list(range(1, 9)) + [0]
        self.movimentos = 0
        self.inicio = None
        self.concluido = False

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.atualizar_tempo)

        # L12: apresentação apenas; embaralhamento, regras, timer e persistência intocados.
        self.setObjectName("arenaPremiumQuebraCabeca")
        self.setStyleSheet("""
            QWidget#arenaPremiumQuebraCabeca { background: transparent; }
            QWidget#arenaPremiumQuebraCabeca QFrame#puzzlePremiumTitleCard {
                background-color: #0A2339; border: 1px solid #277EAA;
                border-radius: 11px;
            }
            QWidget#arenaPremiumQuebraCabeca QLabel#puzzlePremiumIcon {
                background-color: #11435C; border: 1px solid #4AB6E1;
                border-radius: 9px;
            }
            QWidget#arenaPremiumQuebraCabeca QLabel#gameTitle {
                background: transparent; border: none;
                color: #F2FBFF; font-size: 19px; font-weight: 800;
            }
            QWidget#arenaPremiumQuebraCabeca QLabel#gameHint {
                background: transparent; border: none;
                color: #B9DBEE; font-size: 11px;
            }
            QWidget#arenaPremiumQuebraCabeca QFrame#puzzlePremiumStatusStrip {
                background-color: #0B1C33; border: 1px solid #2B6185;
                border-radius: 9px;
            }
            QWidget#arenaPremiumQuebraCabeca QLabel#gameMetric {
                background-color: #103C5A; color: #9CEDFF;
                border: 1px solid #3E8FB5; border-radius: 7px;
                padding: 5px 9px; font-size: 12px; font-weight: 800;
            }
            QWidget#arenaPremiumQuebraCabeca QLabel#gameStatus {
                background: transparent; border: none;
                color: #CBDFEB; font-size: 11px;
            }
            QWidget#arenaPremiumQuebraCabeca QPushButton#gamePrimaryButton {
                background-color: #087FA7; color: #F5FDFF;
                border: 1px solid #49D7F5; border-radius: 8px;
                padding: 7px 12px; min-height: 27px;
                font-size: 12px; font-weight: 750;
            }
            QWidget#arenaPremiumQuebraCabeca QPushButton#gamePrimaryButton:hover {
                background-color: #0D9EBF; border-color: #A9F1FF;
            }
            QWidget#arenaPremiumQuebraCabeca QPushButton#gamePrimaryButton:focus {
                border: 2px solid #DDFBFF;
            }
            QWidget#arenaPremiumQuebraCabeca QPushButton#puzzleTileButton {
                background-color: rgba(8, 33, 58, 228);
                border: 1px solid #4A9EC1; border-radius: 11px;
                color: #EBFAFF; font-size: 24px; font-weight: 850;
                padding: 1px;
            }
            QWidget#arenaPremiumQuebraCabeca QPushButton#puzzleTileButton[tileState="normal"]:disabled {
                background-color: rgba(13, 38, 66, 226);
                color: #BCD8E8; border: 1px solid #39718F;
            }
            QWidget#arenaPremiumQuebraCabeca QPushButton#puzzleTileButton[tileState="movable"] {
                background-color: rgba(16, 73, 103, 237);
                border: 2px solid #55D7F5;
                color: #F8FEFF;
            }
            QWidget#arenaPremiumQuebraCabeca QPushButton#puzzleTileButton[tileState="movable"]:hover {
                background-color: rgba(21, 108, 140, 246);
                border: 2px solid #B7F5FF;
            }
            QWidget#arenaPremiumQuebraCabeca QPushButton#puzzleTileButton:focus {
                border: 3px solid #EBFFFF;
            }
            QWidget#arenaPremiumQuebraCabeca QPushButton#puzzleTileButton[tileState="blank"]:disabled {
                background-color: rgba(2, 17, 32, 90);
                border: 1px dashed #4C829E;
                color: transparent;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 11, 12, 12)
        layout.setSpacing(8)

        topo = QFrame(self)
        topo.setObjectName("puzzlePremiumTitleCard")
        cabecalho = QHBoxLayout(topo)
        cabecalho.setContentsMargins(11, 7, 12, 7)
        cabecalho.setSpacing(10)
        icone = QLabel(topo)
        icone.setObjectName("puzzlePremiumIcon")
        icone.setAlignment(Qt.AlignCenter)
        icone.setFixedSize(43, 43)
        icone.setPixmap(_arena_premium_icone_aba(4).pixmap(QSize(27, 27)))
        icone.setAccessibleName("Icone do jogo Quebra-cabeca")
        cabecalho.addWidget(icone)
        textos = QVBoxLayout()
        textos.setContentsMargins(0, 0, 0, 0)
        textos.setSpacing(2)
        titulo = QLabel("Quebra-cabeça 8 Peças")
        titulo.setObjectName("gameTitle")
        textos.addWidget(titulo)
        dica = QLabel(
            "Organize os números de 1 a 8. Clique em uma peça vizinha ao espaço vazio para movê-la. "
            "Toda nova partida é embaralhada por movimentos válidos, portanto sempre há solução."
        )
        dica.setObjectName("gameHint")
        dica.setWordWrap(True)
        textos.addWidget(dica)
        cabecalho.addLayout(textos, 1)
        layout.addWidget(topo)

        faixa = QFrame(self)
        faixa.setObjectName("puzzlePremiumStatusStrip")
        barra = QHBoxLayout(faixa)
        barra.setContentsMargins(10, 5, 10, 5)
        barra.setSpacing(8)
        self.movimentos_label = QLabel("Movimentos: 0")
        self.movimentos_label.setObjectName("gameMetric")
        self.tempo_label = QLabel("Tempo: 00:00")
        self.tempo_label.setObjectName("gameMetric")
        self.status = QLabel("Organize de 1 a 8.")
        self.status.setObjectName("gameStatus")
        self.status.setWordWrap(True)
        barra.addWidget(self.movimentos_label)
        barra.addWidget(self.tempo_label)
        barra.addStretch()
        barra.addWidget(self.status, 1)
        novo = QPushButton("Embaralhar")
        novo.setObjectName("gamePrimaryButton")
        novo.clicked.connect(self.nova_partida)
        barra.addWidget(novo)
        layout.addWidget(faixa)

        painel = _ArenaPremiumPuzzleBoard(self)
        grade = QGridLayout(painel)
        grade.setContentsMargins(14, 14, 14, 14)
        grade.setSpacing(9)

        self.botoes = []
        for i in range(9):
            botao = QPushButton("")
            botao.setObjectName("puzzleTileButton")
            botao.setMinimumSize(82, 82)
            botao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            botao.clicked.connect(lambda _=False, idx=i: self.mover(idx))
            grade.addWidget(botao, i // 3, i % 3)
            self.botoes.append(botao)

        layout.addWidget(painel, 1)
        self.nova_partida()

    def nova_partida(self):
        self.timer.stop()
        self.estado = list(range(1, 9)) + [0]
        vazio = 8
        anterior = None
        for _ in range(140):
            vizinhos = self._vizinhos(vazio)
            if anterior in vizinhos and len(vizinhos) > 1:
                vizinhos.remove(anterior)
            escolha = random.choice(vizinhos)
            self.estado[vazio], self.estado[escolha] = self.estado[escolha], self.estado[vazio]
            anterior, vazio = vazio, escolha

        if self.estado == list(range(1, 9)) + [0]:
            # Um movimento extra mantém a configuração solucionável e evita iniciar resolvido.
            escolha = random.choice(self._vizinhos(8))
            self.estado[8], self.estado[escolha] = self.estado[escolha], self.estado[8]

        self.movimentos = 0
        self.inicio = None
        self.concluido = False
        self.movimentos_label.setText("Movimentos: 0")
        self.tempo_label.setText("Tempo: 00:00")
        self.status.setText("Faça o primeiro movimento para iniciar o tempo.")
        self.atualizar_grade()

    def _vizinhos(self, indice):
        linha, coluna = divmod(indice, 3)
        resultado = []
        for dl, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            l, c = linha + dl, coluna + dc
            if 0 <= l < 3 and 0 <= c < 3:
                resultado.append(l * 3 + c)
        return resultado

    def atualizar_grade(self):
        vazio = self.estado.index(0)
        vizinhos = set(self._vizinhos(vazio))
        for i, valor in enumerate(self.estado):
            botao = self.botoes[i]
            botao.setText(str(valor) if valor else "")
            botao.setEnabled(not self.concluido and i in vizinhos and valor != 0)
            botao.setProperty("tileState", "blank" if valor == 0 else ("movable" if i in vizinhos else "normal"))
            _repolir(botao)

    def atualizar_tempo(self):
        if not self.inicio or self.concluido:
            return
        duracao = int((datetime.now() - self.inicio).total_seconds())
        self.tempo_label.setText(f"Tempo: {_formatar_tempo(duracao)}")

    def mover(self, indice):
        if self.concluido:
            return
        vazio = self.estado.index(0)
        if indice not in self._vizinhos(vazio):
            return
        if self.inicio is None:
            self.inicio = datetime.now()
            self.timer.start()
            self.status.setText("Organize de 1 a 8.")
        self.estado[vazio], self.estado[indice] = self.estado[indice], self.estado[vazio]
        self.movimentos += 1
        self.movimentos_label.setText(f"Movimentos: {self.movimentos}")
        if self.estado == list(range(1, 9)) + [0]:
            self.concluir()
        else:
            self.atualizar_grade()

    def concluir(self):
        self.concluido = True
        self.timer.stop()
        duracao = int((datetime.now() - self.inicio).total_seconds()) if self.inicio else 0
        self.tempo_label.setText(f"Tempo: {_formatar_tempo(duracao)}")
        self.status.setText(
            f"Resolvido em {self.movimentos} movimentos e {_formatar_tempo(duracao)}."
        )
        self.atualizar_grade()
        pontuacao = max(1, 3000 - (self.movimentos * 20) - duracao)
        self.registrar_resultado(
            pontuacao=pontuacao,
            nivel=8,
            duracao=duracao,
            movimentos=self.movimentos,
        )


class _ArenaPremiumGamepadIcon(QWidget):
    """F05: emblema HERO vetorial escalável, sem eventos de interação."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(64, 64)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAccessibleName("Emblema decorativo da Arena")
        self.setFocusPolicy(Qt.NoFocus)

    def paintEvent(self, event):
        if self.width() < 2 or self.height() < 2:
            return
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing, True)
        pintor.save()
        pintor.scale(self.width() / 72.0, self.height() / 72.0)
        # Três camadas: brilho externo, moldura de vidro e centro escuro.
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QColor(0, 198, 255, 28))
        pintor.drawRoundedRect(QRectF(1, 1, 70, 70), 17, 17)
        moldura = QLinearGradient(0, 0, 72, 72)
        moldura.setColorAt(0.0, QColor("#0D476A"))
        moldura.setColorAt(0.52, QColor("#061F3F"))
        moldura.setColorAt(1.0, QColor("#061A31"))
        pintor.setBrush(QBrush(moldura))
        pintor.setPen(QPen(QColor(45, 218, 255, 230), 1.4))
        pintor.drawRoundedRect(QRectF(3.5, 3.5, 65, 65), 15, 15)
        pintor.setPen(QPen(QColor(130, 224, 255, 90), 0.9))
        pintor.drawLine(15, 7, 56, 7)
        # Gamepad: peça somente visual, sem botões ou números rasterizados.
        controle = QLinearGradient(13, 25, 57, 55)
        controle.setColorAt(0.0, QColor("#4AF4FF"))
        controle.setColorAt(1.0, QColor("#0699EB"))
        pintor.setBrush(QBrush(controle))
        pintor.setPen(Qt.NoPen)
        pintor.drawRoundedRect(QRectF(14, 26, 44, 27), 13, 13)
        pintor.setPen(QPen(QColor("#053152"), 3.1, Qt.SolidLine, Qt.RoundCap))
        pintor.drawLine(28, 33, 28, 44)
        pintor.drawLine(23, 39, 34, 39)
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QColor("#053152"))
        pintor.drawEllipse(QRectF(43, 34, 4.6, 4.6))
        pintor.drawEllipse(QRectF(48, 41, 4.6, 4.6))
        pintor.restore()
        pintor.end()


def _arena_f05_icone_casa():
    """Ícone Home vetorial sobre o botão Voltar REAL (clicked permanece)."""
    imagem = QPixmap(24, 24)
    imagem.fill(Qt.transparent)
    pintor = QPainter(imagem)
    pintor.setRenderHint(QPainter.Antialiasing, True)
    caneta = QPen(QColor("#48E4FF"), 1.9)
    caneta.setJoinStyle(Qt.RoundJoin)
    caneta.setCapStyle(Qt.RoundCap)
    pintor.setPen(caneta)
    pintor.setBrush(Qt.NoBrush)
    pintor.drawLine(4, 11, 12, 4)
    pintor.drawLine(12, 4, 20, 11)
    pintor.drawLine(7, 10, 7, 20)
    pintor.drawLine(17, 10, 17, 20)
    pintor.drawLine(7, 20, 17, 20)
    pintor.drawLine(10, 20, 10, 14)
    pintor.drawLine(10, 14, 14, 14)
    pintor.drawLine(14, 14, 14, 20)
    pintor.end()
    return QIcon(imagem)


class _ArenaPremiumStopwatchIcon(QWidget):
    """F06: cronômetro cênico vetorial, sem cliques, timers nem foco."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAccessibleName("Ícone decorativo de pausa")

    def paintEvent(self, event):
        if self.width() < 2 or self.height() < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.save()
        painter.scale(self.width() / 52.0, self.height() / 52.0)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 203, 246, 28))
        painter.drawEllipse(QRectF(1, 1, 50, 50))
        fundo = QLinearGradient(2, 2, 49, 49)
        fundo.setColorAt(0.0, QColor("#0B3A58"))
        fundo.setColorAt(1.0, QColor("#06172E"))
        painter.setBrush(QBrush(fundo))
        painter.setPen(QPen(QColor("#207B9D"), 1.2))
        painter.drawEllipse(QRectF(3.8, 3.8, 44.4, 44.4))
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("#15D7FF"), 2.8, Qt.SolidLine, Qt.RoundCap))
        painter.drawEllipse(QRectF(13, 14, 26, 26))
        painter.drawLine(26, 19, 26, 27)
        painter.drawLine(26, 27, 32, 31)
        painter.setPen(QPen(QColor("#3BE6FF"), 2.8, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(22, 10, 30, 10)
        painter.drawLine(26, 10, 26, 13)
        painter.drawLine(38, 14, 41, 11)
        painter.restore()
        painter.end()


def _arena_f06_icone_ajustes():
    """Ícone vetorial: o botão real abre o mesmo modo 'Outro'."""
    imagem = QPixmap(28, 28)
    imagem.fill(Qt.transparent)
    pintor = QPainter(imagem)
    pintor.setRenderHint(QPainter.Antialiasing, True)
    pintor.setPen(QPen(QColor("#B6E7FF"), 2.0, Qt.SolidLine, Qt.RoundCap))
    pintor.setBrush(Qt.NoBrush)
    pintor.drawEllipse(QRectF(7.5, 7.5, 13.0, 13.0))
    for x1, y1, x2, y2 in (
        (14, 2, 14, 6), (14, 22, 14, 26), (2, 14, 6, 14), (22, 14, 26, 14),
        (5.3, 5.3, 8.2, 8.2), (19.8, 19.8, 22.7, 22.7),
        (5.3, 22.7, 8.2, 19.8), (19.8, 8.2, 22.7, 5.3),
    ):
        pintor.drawLine(int(x1), int(y1), int(x2), int(y2))
    pintor.setBrush(QColor("#25D7FB"))
    pintor.setPen(Qt.NoPen)
    pintor.drawEllipse(QRectF(11.5, 11.5, 5.0, 5.0))
    pintor.end()
    return QIcon(imagem)


def _arena_premium_icone_aba(indice):
    """Cinco pictogramas vetoriais locais; nenhum ativo externo nem controle falso."""
    cores = ("#16E0F8", "#90A6F6", "#70C8FF", "#A999FC", "#B3A5FC")
    imagem = QPixmap(28, 28)
    imagem.fill(Qt.transparent)
    pincel = QPainter(imagem)
    pincel.setRenderHint(QPainter.Antialiasing)
    linha = QPen(QColor(cores[indice]))
    linha.setWidthF(2.2)
    linha.setCapStyle(Qt.RoundCap)
    linha.setJoinStyle(Qt.RoundJoin)
    pincel.setPen(linha)
    pincel.setBrush(Qt.NoBrush)

    if indice == 0:  # Chimpanzé (face e orelhas)
        pincel.drawEllipse(QRectF(3, 11, 5, 8))
        pincel.drawEllipse(QRectF(20, 11, 5, 8))
        pincel.drawRoundedRect(QRectF(7, 5, 15, 19), 7, 7)
        pincel.drawEllipse(QRectF(11, 12, 1.5, 1.5))
        pincel.drawEllipse(QRectF(16, 12, 1.5, 1.5))
        pincel.drawArc(QRectF(10, 13, 9, 7), 205 * 16, 130 * 16)
    elif indice == 1:  # Memória (duas cartas)
        pincel.drawRoundedRect(QRectF(4, 6, 15, 18), 3, 3)
        pincel.drawRoundedRect(QRectF(9, 3, 15, 18), 3, 3)
        pincel.drawLine(12, 11, 20, 11)
        pincel.drawLine(16, 7, 16, 15)
    elif indice == 2:  # Sequência visual (4 células)
        for y in (5, 16):
            for x in (5, 16):
                pincel.drawRoundedRect(QRectF(x, y, 8, 8), 2, 2)
    elif indice == 3:  # Rotação visual (arco de giro)
        pincel.drawArc(QRectF(5, 5, 18, 18), 70 * 16, 285 * 16)
        pincel.drawLine(19, 5, 23, 6)
        pincel.drawLine(19, 5, 19, 10)
    else:  # Quebra-cabeça (peça abstrata)
        pincel.drawRoundedRect(QRectF(5, 5, 18, 18), 4, 4)
        pincel.drawLine(14, 5, 14, 10)
        pincel.drawLine(5, 14, 10, 14)
        pincel.drawEllipse(QRectF(11.5, 11.5, 5, 5))
    pincel.end()
    return QIcon(imagem)




def _arena_f12_desenhar_trofeu(p, area):
    """Desenha um troféu vetorial dourado, sem depender de arquivos externos."""
    p.save()
    p.setRenderHint(QPainter.Antialiasing, True)
    ouro = QLinearGradient(area.left(), area.top(), area.right(), area.bottom())
    ouro.setColorAt(0.0, QColor('#FFF2B0'))
    ouro.setColorAt(0.45, QColor('#FFD76A'))
    ouro.setColorAt(1.0, QColor('#C8871F'))
    contorno = QPen(QColor('#FFE8A6'))
    contorno.setWidthF(max(1.2, area.width() * 0.035))
    contorno.setJoinStyle(Qt.RoundJoin)
    contorno.setCapStyle(Qt.RoundCap)
    p.setPen(contorno)
    p.setBrush(QBrush(ouro))

    x = area.left()
    y = area.top()
    w = area.width()
    h = area.height()
    cx = x + w / 2.0

    bowl = QPainterPath()
    bowl.moveTo(x + w * 0.24, y + h * 0.20)
    bowl.lineTo(x + w * 0.76, y + h * 0.20)
    bowl.quadTo(x + w * 0.72, y + h * 0.47, x + w * 0.58, y + h * 0.58)
    bowl.lineTo(x + w * 0.42, y + h * 0.58)
    bowl.quadTo(x + w * 0.28, y + h * 0.47, x + w * 0.24, y + h * 0.20)
    bowl.closeSubpath()
    p.drawPath(bowl)

    alca_esq = QPainterPath()
    alca_esq.moveTo(x + w * 0.23, y + h * 0.26)
    alca_esq.cubicTo(x + w * 0.04, y + h * 0.25,
                     x + w * 0.05, y + h * 0.55,
                     x + w * 0.24, y + h * 0.48)
    p.drawPath(alca_esq)
    alca_dir = QPainterPath()
    alca_dir.moveTo(x + w * 0.77, y + h * 0.26)
    alca_dir.cubicTo(x + w * 0.96, y + h * 0.25,
                     x + w * 0.95, y + h * 0.55,
                     x + w * 0.76, y + h * 0.48)
    p.drawPath(alca_dir)

    p.drawRoundedRect(QRectF(cx - w * 0.06, y + h * 0.58, w * 0.12, h * 0.16), 2.5, 2.5)
    p.drawRoundedRect(QRectF(cx - w * 0.20, y + h * 0.76, w * 0.40, h * 0.10), 3.5, 3.5)
    p.restore()


@lru_cache(maxsize=4)
def _arena_f12_trofeu_mini_pixmap(tamanho=30):
    pix = QPixmap(tamanho, tamanho)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)
    fundo = QLinearGradient(0, 0, tamanho, tamanho)
    fundo.setColorAt(0.0, QColor(15, 54, 93, 220))
    fundo.setColorAt(1.0, QColor(7, 21, 43, 245))
    p.setPen(QPen(QColor('#39CDED'), 1.3))
    p.setBrush(QBrush(fundo))
    p.drawRoundedRect(QRectF(1.2, 1.2, tamanho - 2.4, tamanho - 2.4), 8, 8)
    _arena_f12_desenhar_trofeu(p, QRectF(tamanho * 0.18, tamanho * 0.16, tamanho * 0.64, tamanho * 0.68))
    p.end()
    return pix


@lru_cache(maxsize=4)
def _arena_f12_trofeu_emblema_pixmap(tamanho=84):
    pix = QPixmap(tamanho, tamanho)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)
    centro = QPointF(tamanho / 2.0, tamanho / 2.0)
    fundo = QRadialGradient(centro, tamanho * 0.50)
    fundo.setColorAt(0.0, QColor(81, 45, 8, 230))
    fundo.setColorAt(0.55, QColor(36, 21, 9, 215))
    fundo.setColorAt(1.0, QColor(11, 17, 29, 0))
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(fundo))
    p.drawEllipse(QRectF(3, 3, tamanho - 6, tamanho - 6))

    anel = QLinearGradient(0, 0, tamanho, tamanho)
    anel.setColorAt(0.0, QColor('#FFF2B1'))
    anel.setColorAt(0.4, QColor('#FFD56A'))
    anel.setColorAt(1.0, QColor('#A56A12'))
    p.setPen(QPen(QBrush(anel), max(2.2, tamanho * 0.06)))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QRectF(tamanho * 0.09, tamanho * 0.09, tamanho * 0.82, tamanho * 0.82))

    brilho = QRadialGradient(centro.x(), centro.y(), tamanho * 0.38)
    brilho.setColorAt(0.0, QColor(255, 222, 110, 85))
    brilho.setColorAt(1.0, QColor(255, 222, 110, 0))
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(brilho))
    p.drawEllipse(QRectF(tamanho * 0.18, tamanho * 0.18, tamanho * 0.64, tamanho * 0.64))

    _arena_f12_desenhar_trofeu(p, QRectF(tamanho * 0.27, tamanho * 0.22, tamanho * 0.46, tamanho * 0.50))
    p.end()
    return pix


def _arena_f12_formatar_recorde_destaque(chave, dados_jogo):
    """Formata o card premium preservando os dados reais do banco."""
    dados_jogo = dados_jogo or {}
    try:
        partidas = max(0, int(dados_jogo.get('partidas') or 0))
    except (TypeError, ValueError):
        partidas = 0
    if partidas <= 0:
        return 'Sem recorde', 'Sem partidas registradas'

    if chave == 'chimpanze':
        nivel = int(dados_jogo.get('melhor_nivel') or 0)
        return f'Nível {nivel}', f'{partidas} partida(s) registrada(s)'

    if chave == 'memoria':
        partes = []
        if dados_jogo.get('melhor_movimentos') is not None:
            partes.append(f"{dados_jogo['melhor_movimentos']} mov.")
        if dados_jogo.get('melhor_tempo') is not None:
            partes.append(_formatar_tempo(dados_jogo['melhor_tempo']))
        return (' • '.join(partes) or 'Recorde registrado',
                f'{partidas} partida(s) registrada(s)')

    if chave == 'sequencia':
        nivel = int(dados_jogo.get('melhor_nivel') or 0)
        return f'Sequência {nivel}', f'{partidas} partida(s) registrada(s)'

    if chave == 'rotacao_visual':
        partes = []
        if dados_jogo.get('melhor_nivel') is not None:
            partes.append(f"Nível {dados_jogo['melhor_nivel']}")
        if dados_jogo.get('melhor_pontuacao') is not None:
            partes.append(f"{dados_jogo['melhor_pontuacao']} pts")
        return (' • '.join(partes) or 'Recorde registrado',
                f'{partidas} partida(s) registrada(s)')

    if chave == 'quebra_cabeca':
        partes = []
        if dados_jogo.get('melhor_movimentos') is not None:
            partes.append(f"{dados_jogo['melhor_movimentos']} mov.")
        if dados_jogo.get('melhor_tempo') is not None:
            partes.append(_formatar_tempo(dados_jogo['melhor_tempo']))
        return (' • '.join(partes) or 'Recorde registrado',
                f'{partidas} partida(s) registrada(s)')

    return 'Recorde registrado', f'{partidas} partida(s) registrada(s)'




@lru_cache(maxsize=4)
def _arena_f13_icone_ajuda(tamanho=42):
    """Ícone vetorial discreto, sem dependências ou widgets interativos."""
    pm = QPixmap(tamanho, tamanho)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    externo = QLinearGradient(0, 0, tamanho, tamanho)
    externo.setColorAt(0.0, QColor('#11416A'))
    externo.setColorAt(1.0, QColor('#08182F'))
    p.setPen(QPen(QColor('#44D8FF'), 1.5))
    p.setBrush(QBrush(externo))
    p.drawRoundedRect(QRectF(1.3, 1.3, tamanho - 2.6, tamanho - 2.6), 10, 10)
    p.setPen(QPen(QColor('#24D8FF'), 2.0))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QRectF(tamanho * .20, tamanho * .20, tamanho * .60, tamanho * .60))
    p.setPen(QPen(QColor('#8EEBFF')))
    fonte = QFont('Segoe UI')
    fonte.setBold(True)
    fonte.setPixelSize(max(14, int(tamanho * .47)))
    p.setFont(fonte)
    p.drawText(QRectF(0, -1, tamanho, tamanho), Qt.AlignCenter, '?')
    p.end()
    return pm


class _ArenaF13HelpPanel(QFrame):
    """Card decorativo: desenha apenas anéis difusos atrás dos filhos Qt."""
    def paintEvent(self, evento):
        super().paintEvent(evento)
        if self.width() < 140 or self.height() < 45:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setClipRect(self.rect().adjusted(4, 4, -4, -4))
        # Discos concêntricos à direita, sem texto, botões ou zonas de clique.
        x = float(self.width()) - 12.0
        y = float(self.height()) * .54
        for i, alpha in enumerate((26, 20, 14)):
            raio = 24.0 + i * 19.0
            p.setPen(QPen(QColor(55, 184, 240, alpha), 1.1))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QRectF(x - raio, y - raio, raio * 2, raio * 2))
        p.end()


class _ArenaF07NavButton(QPushButton):
    """F07: filetes neon pintados APÓS o estilo, mantendo clique/foco nativos.

    Não há timer, animação infinita ou interceptação de eventos.
    O brilho usa somente 2-3 operações QPainter quando ativo/hover.
    """

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.isEnabled() or self.width() < 24 or self.height() < 20:
            return
        ativo = self.isChecked()
        sobre = self.underMouse()
        if not (ativo or sobre):
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        largura = float(self.width())
        altura = float(self.height())
        # Faixa de luz no topo: a borda principal permanece com o estilo Qt.
        gradiente = QLinearGradient(0, 1, largura, 1)
        gradiente.setColorAt(0.0, QColor(90, 209, 255, 0))
        gradiente.setColorAt(0.22, QColor(132, 163, 255, 115 if ativo else 52))
        gradiente.setColorAt(0.78, QColor(54, 214, 255, 100 if ativo else 48))
        gradiente.setColorAt(1.0, QColor(54, 214, 255, 0))
        p.setPen(QPen(QBrush(gradiente), 1.4, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(14, 2, max(14, int(largura) - 14), 2)
        if ativo:
            # Pequeno brilho de base atrás da linha ciano do QSS.
            fundo = QLinearGradient(0, altura - 10, 0, altura - 1)
            fundo.setColorAt(0.0, QColor(0, 215, 250, 0))
            fundo.setColorAt(1.0, QColor(0, 215, 250, 55))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(fundo))
            p.drawRoundedRect(QRectF(8, altura - 9, largura - 16, 6), 3, 3)
        p.end()


def _arena_f07_icone_navegacao(indice):
    """Ícones Qt reais, ampliados, com estados normal/selecionado embutidos.

    Mantém _arena_premium_icone_aba inalterado para o painel de recordes.
    """
    cores = ('#15E8FF', '#AAA8FF', '#69CBFF', '#BA9AFF', '#B9AAFF')
    base = _arena_premium_icone_aba(indice).pixmap(QSize(26, 26))
    icone = QIcon()
    for ativo in (False, True):
        imagem = QPixmap(42, 42)
        imagem.fill(Qt.transparent)
        p = QPainter(imagem)
        p.setRenderHint(QPainter.Antialiasing, True)
        fundo = QLinearGradient(3, 3, 39, 39)
        fundo.setColorAt(0.0, QColor(16, 58, 94, 228 if ativo else 155))
        fundo.setColorAt(1.0, QColor(7, 21, 44, 240 if ativo else 168))
        p.setPen(QPen(QColor(cores[indice]) if ativo else QColor('#345E83'),
                      1.5 if ativo else 1.0))
        p.setBrush(QBrush(fundo))
        p.drawRoundedRect(QRectF(3.5, 3.5, 35, 35), 10, 10)
        p.drawPixmap(8, 8, base)
        p.end()
        state = QIcon.On if ativo else QIcon.Off
        icone.addPixmap(imagem, QIcon.Normal, state)
        icone.addPixmap(imagem, QIcon.Active, state)
    return icone


class _ArenaPremiumMountainHeader(QFrame):
    """Cabeçalho pintado em Qt. A arte L03 não contém texto ou botões.

    Os widgets filhos mantêm seus eventos, teclado e foco; a imagem só é fundo.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._imagem, self._imagem_valida = _arena_hero_f04.carregar_pixmap()
        if not self._imagem_valida or self._imagem.isNull():
            # Fallback real e local: se o JPEG do F04 nao abrir no Qt, continua a arte L03.
            self._imagem, self._imagem_valida = _arena_premium_art.carregar_pixmap(
                "ceu_montanhas", tamanho_fallback=(1600, 320)
            )
        self._cache = None
        self._cache_tamanho = None

    def resizeEvent(self, event):
        self._cache = None
        self._cache_tamanho = None
        super().resizeEvent(event)

    def paintEvent(self, event):
        if self.width() < 2 or self.height() < 2:
            return
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing, True)
        pintor.setRenderHint(QPainter.SmoothPixmapTransform, True)
        recorte = QPainterPath()
        recorte.addRoundedRect(QRectF(self.rect()).adjusted(0.8, 0.8, -0.8, -0.8), 13, 13)
        pintor.setClipPath(recorte)
        cor_fundo = QLinearGradient(0, 0, self.width(), self.height())
        cor_fundo.setColorAt(0.0, QColor("#07172A"))
        cor_fundo.setColorAt(0.65, QColor("#0B2843"))
        cor_fundo.setColorAt(1.0, QColor("#07192D"))
        pintor.fillPath(recorte, QBrush(cor_fundo))
        if self._imagem_valida and not self._imagem.isNull():
            tamanho = self.size()
            if self._cache is None or self._cache_tamanho != tamanho:
                # Arquivo 1920:125 foi preparado para a faixa HERO (sem
                # deformacao anisotropica, mesmo em janelas compactas).
                self._cache = self._imagem.scaled(
                    tamanho, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                )
                self._cache_tamanho = tamanho
            fundo = self._cache
            pintor.drawPixmap((self.width() - fundo.width()) // 2,
                              (self.height() - fundo.height()) // 2, fundo)
        # Protege titulo à esquerda e botão de retorno à direita.
        pelicula = QLinearGradient(0, 0, max(1, self.width()), 0)
        # F04: alta legibilidade para titulo/subtitulo e botao real,
        # enquanto o pico central e a reflexao violeta permanecem visiveis.
        pelicula.setColorAt(0.0, QColor(3, 13, 27, 238))
        pelicula.setColorAt(0.30, QColor(3, 14, 30, 213))
        pelicula.setColorAt(0.50, QColor(3, 15, 33, 85))
        pelicula.setColorAt(0.76, QColor(3, 15, 31, 65))
        pelicula.setColorAt(1.0, QColor(3, 13, 27, 215))
        pintor.fillPath(recorte, QBrush(pelicula))
        pintor.setClipping(False)
        pintor.setBrush(Qt.NoBrush)
        pintor.setPen(QPen(QColor("#218CAE"), 1.2))
        pintor.drawPath(recorte)
        pintor.setPen(QPen(QColor(27, 210, 248, 185), 1.2))
        pintor.drawLine(17, self.height()-2, max(18, self.width()-17), self.height()-2)
        pintor.end()


class JanelaPausaDesafios(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Pausa & Desafios — VighnaStudy")
        # L13: paleta apenas na janela da Arena. Não altera temas globais.
        self.setObjectName("arenaPremiumDialog")
        self.setStyleSheet("QDialog#arenaPremiumDialog { background-color: #050F20; }")
        self.resize(1050, 780)
        self.setMinimumSize(900, 650)
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowMinMaxButtonsHint
        )

        self.tempo_restante = 0
        self.timer_pausa = QTimer(self)
        self.timer_pausa.setInterval(1000)
        self.timer_pausa.timeout.connect(self.tick_pausa)

        # L14: toda a Arena pode rolar verticalmente em janelas menores.
        # Nenhuma pagina de jogo e recriada; o QSplitter e seus scrolls internos
        # continuam sendo os mesmos widgets dos Lotes 06 e 11.
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        self._arena_scroll_vertical = QScrollArea(self)
        self._arena_scroll_vertical.setObjectName("pausePremiumFullScroll")
        self._arena_scroll_vertical.setWidgetResizable(True)
        self._arena_scroll_vertical.setFrameShape(QFrame.NoFrame)
        self._arena_scroll_vertical.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._arena_scroll_vertical.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._arena_scroll_vertical.setFocusPolicy(Qt.StrongFocus)
        self._arena_scroll_vertical.verticalScrollBar().setSingleStep(28)
        self._arena_scroll_vertical.setAccessibleName("Area principal da Arena com rolagem vertical")
        self._arena_scroll_vertical.setAccessibleDescription(
            "Use a rolagem para alcancar os jogos em janelas menores; as abas e os recordes mantem controles proprios."
        )
        self._arena_scroll_vertical.setStyleSheet(
            "QScrollArea#pausePremiumFullScroll { background: #050F20; border: 0px; }"
        )
        raiz.addWidget(self._arena_scroll_vertical, 1)
        self._arena_conteudo = QWidget()
        self._arena_conteudo.setObjectName("pausePremiumFullContent")
        self._arena_conteudo.setStyleSheet(
            "QWidget#pausePremiumFullContent { background: #050F20; }"
        )
        layout = QVBoxLayout(self._arena_conteudo)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)
        self._arena_layout = layout

        # Arena Premium / Lote 02: somente cabeçalho. O conteúdo inferior
        # mantém as mesmas instâncias, sinais, timers, recordes e layouts.
        self.cabecalho_premium = _ArenaPremiumMountainHeader(self)
        self.cabecalho_premium.setObjectName("pauseHubPremiumHeader")
        self.cabecalho_premium.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cabecalho_premium.setFixedHeight(ARENA_F03_PERFIS[0]["hero"])
        self.cabecalho_premium.setStyleSheet(_arena_f02_qss("header"))
        cabecalho = QHBoxLayout(self.cabecalho_premium)
        cabecalho.setContentsMargins(17, 7, 18, 7)
        cabecalho.setSpacing(13)
        self._cabecalho_premium_layout = cabecalho
        self._icone_cabecalho_premium = _ArenaPremiumGamepadIcon(self.cabecalho_premium)
        cabecalho.addWidget(self._icone_cabecalho_premium, 0, Qt.AlignVCenter)

        textos = QVBoxLayout()
        textos.setContentsMargins(0, 0, 0, 0)
        textos.setSpacing(2)
        titulo = QLabel("Pausa & Desafios")
        titulo.setObjectName("pauseHubTitle")
        subtitulo = QLabel("Uma pausa no estudo. Um desafio para a mente.")
        subtitulo.setObjectName("pauseHubSubtitle")
        subtitulo.setWordWrap(False)
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)
        cabecalho.addLayout(textos, 1)

        voltar = QPushButton("Voltar aos estudos  →")
        voltar.setObjectName("pauseBackButton")
        voltar.setIcon(_arena_f05_icone_casa())
        voltar.setIconSize(QSize(19, 19))
        voltar.setMinimumWidth(175)
        voltar.setAccessibleName("Voltar aos estudos")
        voltar.setToolTip("Fechar Pausa & Desafios e retornar aos estudos")
        voltar.clicked.connect(self.accept)
        cabecalho.addWidget(voltar, 0, Qt.AlignVCenter)
        layout.addWidget(self.cabecalho_premium)

        # Arena Premium / Lote 04: cronometro horizontal, fiel a referencia
        # aprovada 1706x922. Apenas a apresentacao muda; o QTimer e unico.
        painel_pausa = QFrame()
        painel_pausa.setObjectName("pauseTimerPanel")
        painel_pausa.setMinimumHeight(68)
        painel_pausa.setMaximumHeight(112)
        self._painel_pausa_geometria = painel_pausa
        painel_pausa.setStyleSheet(_arena_f02_qss("timer"))
        pausa_layout = QHBoxLayout(painel_pausa)
        pausa_layout.setContentsMargins(15, 8, 15, 8)
        pausa_layout.setSpacing(10)

        self._icone_pausa_premium = _ArenaPremiumStopwatchIcon(painel_pausa)
        pausa_layout.addWidget(self._icone_pausa_premium)
        resumo_pausa = QVBoxLayout()
        resumo_pausa.setContentsMargins(0, 0, 0, 0)
        resumo_pausa.setSpacing(1)
        pausa_titulo = QLabel("Pausa rápida")
        pausa_titulo.setObjectName("pauseTimerHeading")
        resumo_pausa.addWidget(pausa_titulo)
        self.pausa_status = QLabel("Configure seu descanso.")
        self.pausa_status.setObjectName("pauseTimerStatus")
        self.pausa_status.setWordWrap(False)
        self.pausa_status.setToolTip("Escolha 5, 10, 15 minutos ou outro tempo de descanso.")
        resumo_pausa.addWidget(self.pausa_status)
        pausa_layout.addLayout(resumo_pausa, 1)

        # Mesmo QSpinBox do painel anterior: preserva limite de 1 a 60 min,
        # preview e modo personalizado sem abrir segundo temporizador.
        self.minutos = QSpinBox()
        self.minutos.setObjectName("pauseCustomMinutes")
        self.minutos.setRange(1, 60)
        self.minutos.setValue(5)
        self.minutos.setSuffix(" min")
        self.minutos.setFixedWidth(70)
        self.minutos.setFixedHeight(32)
        self.minutos.setAccessibleName("Duração personalizada em minutos")
        self._modo_pausa = 5
        self._minutos_personalizados = 20
        self.grupo_duracoes = QButtonGroup(self)
        self.grupo_duracoes.setExclusive(True)
        self.botoes_duracao = {}
        self._painel_seletores_pausa = QFrame(painel_pausa)
        self._painel_seletores_pausa.setObjectName("pausePresetCluster")
        seletor_pausa = QHBoxLayout(self._painel_seletores_pausa)
        seletor_pausa.setContentsMargins(4, 4, 4, 4)
        seletor_pausa.setSpacing(3)
        for valor, texto in ((5, "5 min"), (10, "10 min"), (15, "15 min"), ("outro", "Outro")):
            botao = QPushButton(texto)
            botao.setObjectName(f"pausePreset{valor}")
            botao.setProperty("pausePreset", "true")
            botao.setCheckable(True)
            botao.setFixedSize(58 if valor != "outro" else 64, 39)
            botao.setAccessibleName(f"Selecionar {texto} de pausa")
            botao.clicked.connect(
                lambda checked=False, duracao=valor: self.selecionar_duracao_pausa(duracao)
            )
            self.grupo_duracoes.addButton(botao)
            self.botoes_duracao[valor] = botao
            seletor_pausa.addWidget(botao)
        self.botoes_duracao[5].setChecked(True)
        pausa_layout.addWidget(self._painel_seletores_pausa, 0, Qt.AlignVCenter)
        self._seletor_pausa_layout = seletor_pausa
        pausa_layout.addWidget(self.minutos)
        self.minutos.hide()

        self._painel_tempo_pausa = QFrame(painel_pausa)
        self._painel_tempo_pausa.setObjectName("pauseClockFocus")
        tempo_box = QVBoxLayout(self._painel_tempo_pausa)
        tempo_box.setContentsMargins(12, 1, 12, 1)
        tempo_box.setSpacing(1)
        tempo_legenda = QLabel("Tempo restante")
        tempo_legenda.setObjectName("pauseTimeCaption")
        tempo_legenda.setAlignment(Qt.AlignCenter)
        tempo_box.addWidget(tempo_legenda)
        self.pausa_tempo = QLabel("05:00")
        self.pausa_tempo.setObjectName("pauseTimerValue")
        self.pausa_tempo.setAlignment(Qt.AlignCenter)
        self.pausa_tempo.setMinimumWidth(94)
        self.pausa_tempo.setAccessibleName("Tempo restante da pausa")
        self.pausa_tempo.setAccessibleDescription(
            "Mostra a contagem regressiva da pausa, sem interromper os jogos."
        )
        tempo_box.addWidget(self.pausa_tempo)
        pausa_layout.addWidget(self._painel_tempo_pausa, 0, Qt.AlignVCenter)

        self.iniciar_pausa_btn = QPushButton("▶  Iniciar pausa")
        self.iniciar_pausa_btn.setObjectName("pausePrimaryButton")
        self.iniciar_pausa_btn.setFixedHeight(44)
        self.iniciar_pausa_btn.setMinimumWidth(135)
        self.iniciar_pausa_btn.setAccessibleName("Iniciar pausa")
        self.iniciar_pausa_btn.clicked.connect(self.iniciar_pausa)
        pausa_layout.addWidget(self.iniciar_pausa_btn)
        _arena_f02_glow_discreto(self.iniciar_pausa_btn)

        self.parar_pausa_btn = QPushButton("Encerrar")
        self.parar_pausa_btn.setObjectName("pauseSecondaryButton")
        self.parar_pausa_btn.setFixedHeight(44)
        self.parar_pausa_btn.setMinimumWidth(87)
        self.parar_pausa_btn.clicked.connect(self.encerrar_pausa)
        self.parar_pausa_btn.setEnabled(False)
        pausa_layout.addWidget(self.parar_pausa_btn)

        # F06: atalho funcional para a duração personalizada EXISTENTE.
        # Não cria um painel de configuração paralelo nem um segundo QTimer.
        self.ajuste_pausa_btn = QPushButton(painel_pausa)
        self.ajuste_pausa_btn.setObjectName("pauseTimerSettingsButton")
        self.ajuste_pausa_btn.setFixedSize(44, 44)
        self.ajuste_pausa_btn.setIcon(_arena_f06_icone_ajustes())
        self.ajuste_pausa_btn.setIconSize(QSize(24, 24))
        self.ajuste_pausa_btn.setToolTip("Personalizar a duração da pausa (1 a 60 minutos)")
        self.ajuste_pausa_btn.setAccessibleName("Configurar duração personalizada da pausa")
        self.ajuste_pausa_btn.clicked.connect(
            lambda: self.selecionar_duracao_pausa("outro")
        )
        pausa_layout.addWidget(self.ajuste_pausa_btn, 0, Qt.AlignVCenter)
        layout.addWidget(painel_pausa)

        # L07: painel contextual real. Reutiliza os mesmos cinco labels de
        # recordes e suas consultas anteriores; nenhum resultado e inventado.
        recordes = QFrame(self)
        recordes.setObjectName("pauseRecordsPanel")
        recordes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        recordes.setStyleSheet("""
            QFrame#pauseRecordsPanel {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #09233C, stop:0.54 #081B32, stop:1 #0A2540);
                border: 1px solid #349AC0; border-radius: 13px;
            }
            QFrame#pauseRecordsPanel QFrame#pauseRecordFocusCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #103E5A, stop:0.37 #0B2B4B,
                    stop:0.78 #0B1D36, stop:1 #121B31);
                border: 1px solid #4DDBF3; border-radius: 12px;
            }
            QFrame#pauseRecordsPanel QLabel#pauseFocusBadge {
                border: none; background: transparent;
            }
            QFrame#pauseRecordsPanel QLabel#pauseFocusEmblem {
                border: none; background: transparent;
            }
            QFrame#pauseRecordsPanel QFrame#pauseHelpCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0E3655, stop:0.55 #0A2743, stop:1 #091C36);
                border: 1px solid #328EBA; border-radius: 11px;
            }
            QFrame#pauseRecordsPanel QFrame#pauseOthersCard {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #0C2A46, stop:0.6 #0A233C, stop:1 #091D35);
                border: 1px solid #337DA2; border-radius: 11px;
            }
            /* F15: linhas do jogo ativo e acesso explícito aos outros 4 jogos. */
            QFrame#pauseRecordsPanel QFrame#pauseF15MetricRow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #123E58, stop:0.58 #0E304E, stop:1 #0C2946);
                border: 1px solid #3B83A5; border-radius: 8px;
            }
            QFrame#pauseRecordsPanel QLabel#pauseF15MetricIcon {
                color: #68DBFF; background: #103E60;
                border: 1px solid #327EA1; border-radius: 7px;
                font-size: 15px; font-weight: 800;
            }
            QFrame#pauseRecordsPanel QLabel#pauseF15MetricTitle {
                color: #AACFE1; background: transparent; border: none;
                font-size: 10px;
            }
            QFrame#pauseRecordsPanel QLabel#pauseF15MetricValue {
                color: #91F6FF; background: transparent; border: none;
                font-size: 12px; font-weight: 800;
            }
            QFrame#pauseRecordsPanel QLabel#pauseF15MetricDate {
                color: #A0B8D0; background: transparent; border: none;
                font-size: 10px;
            }
            QFrame#pauseRecordsPanel QLabel#pauseF15Intro {
                color: #A7CFDF; background: transparent; border: none;
                font-size: 10px;
            }
            QFrame#pauseRecordsPanel QPushButton#pauseF15OtherGamesToggle {
                background: #0B2C49;
                border: 1px solid #2A7796; border-radius: 8px;
                color: #C7E7F7; font-size: 11px; font-weight: 700;
                padding: 6px 8px;
                text-align: left;
            }
            QFrame#pauseRecordsPanel QPushButton#pauseF15OtherGamesToggle:hover,
            QFrame#pauseRecordsPanel QPushButton#pauseF15OtherGamesToggle:focus {
                border: 1px solid #68DDF7; background: #134766;
            }
            QFrame#pauseRecordsPanel QLabel#pauseHelpIcon {
                background: transparent; border: none;
            }
            QFrame#pauseRecordsPanel QLabel#pauseHelpTitle {
                color: #F2FAFF; background: transparent; border: none;
                font-size: 14px; font-weight: 800;
            }
            QFrame#pauseRecordsPanel QLabel#pauseContextHeader {
                color: #F2FAFF; background: transparent; border: none;
                font-size: 14px; font-weight: 800;
            }
            QFrame#pauseRecordsPanel QLabel#pauseContextName {
                color: #CBE4F0; background: transparent; border: none;
                font-size: 11px; letter-spacing: 0.2px;
            }
            QFrame#pauseRecordsPanel QLabel#pauseContextValue {
                color: #57EEFF; background: transparent; border: none;
                font-size: 23px; font-weight: 800;
            }
            QFrame#pauseRecordsPanel QLabel#pauseContextDetail,
            QFrame#pauseRecordsPanel QLabel#pauseHelpText {
                color: #B4D2E4; background: transparent; border: none;
                font-size: 11px;
            }
            QFrame#pauseRecordsPanel QFrame#pauseRecordCard {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #143B55, stop:1 #102D47);
                border: 1px solid #337699;
                border-radius: 8px;
            }
            QFrame#pauseRecordsPanel QLabel#pauseRecordTitle {
                color: #AACDDD; background: transparent; border: none;
                font-size: 10px;
            }
            QFrame#pauseRecordsPanel QLabel#pauseRecordValue {
                color: #C4F7FD; background: transparent; border: none;
                font-size: 11px; font-weight: 700;
            }
            QFrame#pauseRecordsPanel QLabel#pauseContextIcon {
                border: none; background: transparent;
            }
        """)
        rec_layout = QVBoxLayout(recordes)
        rec_layout.setContentsMargins(10, 10, 10, 10)
        rec_layout.setSpacing(9)

        # F12: card premium do Meu recorde. Mantém dados reais do banco, sem
        # simulações, com troféu dourado e emblema à direita.
        self.painel_recorde_ativo = QFrame(recordes)
        self.painel_recorde_ativo.setObjectName("pauseRecordFocusCard")
        foco_layout = QVBoxLayout(self.painel_recorde_ativo)
        foco_layout.setContentsMargins(12, 10, 12, 10)
        foco_layout.setSpacing(6)
        foco_topo = QHBoxLayout()
        foco_topo.setContentsMargins(0, 0, 0, 0)
        foco_topo.setSpacing(9)
        self.recorde_foco_icone = QLabel()
        self.recorde_foco_icone.setObjectName("pauseFocusBadge")
        self.recorde_foco_icone.setFixedSize(34, 34)
        self.recorde_foco_icone.setAccessibleName("Ícone de troféu do card de recorde")
        foco_topo.addWidget(self.recorde_foco_icone, 0, Qt.AlignTop)
        foco_titulo = QLabel("Meu recorde")
        foco_titulo.setObjectName("pauseContextHeader")
        foco_topo.addWidget(foco_titulo, 1, Qt.AlignVCenter)
        foco_layout.addLayout(foco_topo)

        foco_corpo = QHBoxLayout()
        foco_corpo.setContentsMargins(0, 0, 0, 0)
        foco_corpo.setSpacing(8)
        foco_textos = QVBoxLayout()
        foco_textos.setContentsMargins(0, 0, 0, 0)
        foco_textos.setSpacing(2)
        self.recorde_foco_nome = QLabel("Chimpanzé")
        self.recorde_foco_nome.setObjectName("pauseContextName")
        foco_textos.addWidget(self.recorde_foco_nome)
        self.recorde_foco_valor = QLabel("Sem recorde")
        self.recorde_foco_valor.setObjectName("pauseContextValue")
        self.recorde_foco_valor.setWordWrap(True)
        self.recorde_foco_valor.setAccessibleName("Recorde real do jogo selecionado")
        foco_textos.addWidget(self.recorde_foco_valor)
        self.recorde_foco_partidas = QLabel("Sem partidas registradas")
        self.recorde_foco_partidas.setObjectName("pauseContextDetail")
        foco_textos.addWidget(self.recorde_foco_partidas)
        foco_textos.addStretch(1)
        foco_corpo.addLayout(foco_textos, 1)
        self.recorde_foco_emblema = QLabel()
        self.recorde_foco_emblema.setObjectName("pauseFocusEmblem")
        self.recorde_foco_emblema.setFixedSize(82, 82)
        self.recorde_foco_emblema.setAlignment(Qt.AlignCenter)
        self.recorde_foco_emblema.setAccessibleName("Emblema de troféu do card de recorde")
        foco_corpo.addWidget(self.recorde_foco_emblema, 0, Qt.AlignRight | Qt.AlignVCenter)
        foco_layout.addLayout(foco_corpo)
        rec_layout.addWidget(self.painel_recorde_ativo)

        # F13: o card Como jogar utiliza o MESMO QLabel gameHint já obtido
        # por _atualizar_paineis_contextuais(); apenas a apresentação muda.
        self.painel_como_jogar = _ArenaF13HelpPanel(recordes)
        self.painel_como_jogar.setObjectName("pauseHelpCard")
        ajuda_layout = QHBoxLayout(self.painel_como_jogar)
        ajuda_layout.setContentsMargins(12, 10, 12, 10)
        ajuda_layout.setSpacing(10)
        ajuda_icone = QLabel(self.painel_como_jogar)
        ajuda_icone.setObjectName("pauseHelpIcon")
        ajuda_icone.setFixedSize(42, 42)
        ajuda_icone.setPixmap(_arena_f13_icone_ajuda(42))
        ajuda_icone.setAlignment(Qt.AlignCenter)
        ajuda_icone.setFocusPolicy(Qt.NoFocus)
        ajuda_icone.setAccessibleName("Ícone decorativo de instruções")
        ajuda_layout.addWidget(ajuda_icone, 0, Qt.AlignTop)
        ajuda_textos = QVBoxLayout()
        ajuda_textos.setContentsMargins(0, 0, 0, 0)
        ajuda_textos.setSpacing(4)
        ajuda_titulo = QLabel("Como jogar")
        ajuda_titulo.setObjectName("pauseHelpTitle")
        ajuda_textos.addWidget(ajuda_titulo)
        self.como_jogar_texto = QLabel()
        self.como_jogar_texto.setObjectName("pauseHelpText")
        self.como_jogar_texto.setWordWrap(True)
        self.como_jogar_texto.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.como_jogar_texto.setAccessibleName("Instrucoes reais do jogo ativo")
        ajuda_textos.addWidget(self.como_jogar_texto)
        ajuda_layout.addLayout(ajuda_textos, 1)
        rec_layout.addWidget(self.painel_como_jogar)

        # F15: 'Outros recordes' agora aprofunda marcas REAIS do jogo ativo.
        # Os cartões preexistentes dos demais jogos permanecem preservados,
        # mas sob expansão explícita para liberar espaço na lateral direita.
        self.painel_outros_recordes = QFrame(recordes)
        self.painel_outros_recordes.setObjectName("pauseOthersCard")
        outros_layout = QVBoxLayout(self.painel_outros_recordes)
        outros_layout.setContentsMargins(9, 9, 9, 9)
        outros_layout.setSpacing(6)
        outros_titulo = QLabel("Outros recordes")
        outros_titulo.setObjectName("pauseContextHeader")
        outros_layout.addWidget(outros_titulo)
        resumo = QLabel("Indicadores reais do jogo selecionado")
        resumo.setObjectName("pauseF15Intro")
        outros_layout.addWidget(resumo)
        self._f15_linhas_metricas = []
        for numero in range(4):
            linha_metrica = QFrame(self.painel_outros_recordes)
            linha_metrica.setObjectName("pauseF15MetricRow")
            linha_metrica.setMinimumHeight(45)
            layout_metrica = QHBoxLayout(linha_metrica)
            layout_metrica.setContentsMargins(7, 5, 7, 5)
            layout_metrica.setSpacing(7)
            icone = QLabel(("★", "↗", "●", "◷")[numero])
            icone.setObjectName("pauseF15MetricIcon")
            icone.setFixedSize(29, 29)
            icone.setAlignment(Qt.AlignCenter)
            icone.setAccessibleName("Indicador visual de estatística")
            layout_metrica.addWidget(icone)
            texto_metrica = QVBoxLayout()
            texto_metrica.setSpacing(1)
            rotulo = QLabel("—")
            rotulo.setObjectName("pauseF15MetricTitle")
            valor = QLabel("—")
            valor.setObjectName("pauseF15MetricValue")
            texto_metrica.addWidget(rotulo)
            texto_metrica.addWidget(valor)
            layout_metrica.addLayout(texto_metrica, 1)
            data_metrica = QLabel("")
            data_metrica.setObjectName("pauseF15MetricDate")
            data_metrica.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            layout_metrica.addWidget(data_metrica, 0)
            outros_layout.addWidget(linha_metrica)
            self._f15_linhas_metricas.append((linha_metrica, rotulo, valor, data_metrica))
        self._f15_cache = {}
        self._f15_botao_demais = QPushButton("Ver recordes dos outros jogos  ▾")
        self._f15_botao_demais.setObjectName("pauseF15OtherGamesToggle")
        self._f15_botao_demais.setCheckable(True)
        self._f15_botao_demais.setChecked(False)
        self._f15_botao_demais.setAccessibleName("Expandir ou recolher recordes dos outros quatro jogos")
        self._f15_botao_demais.setAccessibleDescription(
            "Pressione Enter ou Espaço para mostrar ou ocultar os recordes dos demais jogos. "
            "Use a rolagem vertical para visualizar os cartões."
        )
        outros_layout.addWidget(self._f15_botao_demais)
        self._f15_conteudo_demais = QWidget(self.painel_outros_recordes)
        demais_layout = QVBoxLayout(self._f15_conteudo_demais)
        demais_layout.setContentsMargins(0, 3, 0, 0)
        demais_layout.setSpacing(5)
        self.recorde_labels = {}
        self.recorde_cards = {}
        nomes = [
            ("chimpanze", "Chimpanzé"),
            ("memoria", "Memória"),
            ("sequencia", "Sequência visual"),
            ("rotacao_visual", "Rotação visual"),
            ("quebra_cabeca", "Quebra-cabeça"),
        ]
        for chave, nome in nomes:
            caixa = QFrame(self._f15_conteudo_demais)
            caixa.setObjectName("pauseRecordCard")
            caixa.setMinimumHeight(48)
            caixa.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            caixa_layout = QVBoxLayout(caixa)
            caixa_layout.setContentsMargins(9, 4, 9, 5)
            caixa_layout.setSpacing(1)
            rotulo = QLabel(nome)
            rotulo.setObjectName("pauseRecordTitle")
            valor = QLabel("Sem recorde")
            valor.setObjectName("pauseRecordValue")
            valor.setWordWrap(True)
            caixa_layout.addWidget(rotulo)
            caixa_layout.addWidget(valor)
            demais_layout.addWidget(caixa)
            self.recorde_cards[chave] = caixa
            self.recorde_labels[chave] = valor
        outros_layout.addWidget(self._f15_conteudo_demais)
        self._f15_conteudo_demais.hide()
        self._f15_botao_demais.toggled.connect(self._f15_expandir_demais)
        rec_layout.addWidget(self.painel_outros_recordes)
        rec_layout.addStretch(1)
        # O contêiner rolável e o QSplitter L06 serão reutilizados adiante.

        # L05: a navegacao passa a ocupar a largura total, como na imagem
        # aprovada. Os CINCO widgets de jogo seguem em um unico QTabWidget,
        # sem reconstruir paginas, manipular estado ou conexoes dos motores.
        self.tabs = QTabWidget()
        self.tabs.setObjectName("pauseGamesTabs")
        self.tabs.addTab(JogoChimpanze(self.atualizar_recordes, self), "Chimpanzé")
        self.tabs.addTab(JogoMemoria(self.atualizar_recordes, self), "Memória")
        self.tabs.addTab(JogoSequenciaVisual(self.atualizar_recordes, self), "Sequência visual")
        self.tabs.addTab(JogoRotacaoVisual(self.atualizar_recordes, self), "Rotação visual")
        self.tabs.addTab(JogoQuebraCabeca(self.atualizar_recordes, self), "Quebra-cabeça")

        self.navegacao_premium = QFrame(self)
        self.navegacao_premium.setObjectName("pausePremiumGamesNav")
        self.navegacao_premium.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.navegacao_premium.setFixedHeight(ARENA_F03_PERFIS[0]["nav"])
        self.navegacao_premium.setStyleSheet(_arena_f02_qss("navigation"))
        linha_navegacao = QHBoxLayout(self.navegacao_premium)
        linha_navegacao.setContentsMargins(0, 0, 0, 0)
        linha_navegacao.setSpacing(9)
        self._botoes_navegacao_premium = []
        self._f15_botao_demais.installEventFilter(self)
        self._grupo_navegacao_premium = QButtonGroup(self)
        self._grupo_navegacao_premium.setExclusive(True)
        nomes_abas = ("Chimpanzé", "Memória", "Sequência visual", "Rotação visual", "Quebra-cabeça")
        for indice, nome in enumerate(nomes_abas):
            botao = _ArenaF07NavButton(nome, self.navegacao_premium)
            botao.setObjectName(f"pausePremiumGameTab{indice}")
            botao.setProperty("premiumNav", "yes")
            botao.setCheckable(True)
            botao.setFixedHeight(ARENA_F03_PERFIS[0]["tab"])
            botao.setMinimumWidth(130)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            botao.setIcon(_arena_f07_icone_navegacao(indice))
            botao.setIconSize(QSize(34, 34))
            botao.setAccessibleName(f"Jogo {nome}")
            botao.setAccessibleDescription(
                "Use as setas esquerda/direita, Inicio e Fim para navegar. Enter ou Espaco ativam a aba."
            )
            botao.setToolTip(f"Abrir jogo {nome}; navegue também com as setas")
            botao.clicked.connect(
                lambda checked=False, i=indice: self.tabs.setCurrentIndex(i)
            )
            botao.installEventFilter(self)
            self._grupo_navegacao_premium.addButton(botao)
            self._botoes_navegacao_premium.append(botao)
            linha_navegacao.addWidget(botao, 1)

        # Uma unica ligacao sincroniza programacao, Ctrl+Tab e cliques.
        self.tabs.currentChanged.connect(self._sincronizar_aba_premium)
        self._sincronizar_aba_premium(self.tabs.currentIndex())
        # Retira apenas a apresentacao da barra nativa; a pilha de jogos,
        # as instancias de cada widget e o sinal currentChanged sao mantidos.
        self.tabs.tabBar().setMaximumHeight(0)
        self.tabs.tabBar().hide()
        # L06: barra de navegacao ocupa a largura total; abaixo, arena 70/30.
        # O QTabWidget e os cinco jogos sao as MESMAS instancias do L05.
        layout.addWidget(self.navegacao_premium)
        self.painel_jogo_premium = QFrame(self)
        self.painel_jogo_premium.setObjectName("pausePremiumArenaLeft")
        self.painel_jogo_premium.setMinimumWidth(560)
        self.painel_jogo_premium.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.painel_jogo_premium.setStyleSheet("""
            QFrame#pausePremiumArenaLeft {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #08243D, stop:0.35 #071C31, stop:1 #08182D);
                border: 1px solid #329FC1;
                border-radius: 13px;
            }
        """)
        jogo_layout = QVBoxLayout(self.painel_jogo_premium)
        jogo_layout.setContentsMargins(2, 2, 2, 2)
        jogo_layout.setSpacing(0)
        jogo_layout.addWidget(self.tabs, 1)

        # Conteudo de recordes inteiro preservado, com rolagem em altura menor.
        self.painel_recordes_scroll = QScrollArea(self)
        self.painel_recordes_scroll.setObjectName("pausePremiumRecordsScroll")
        self.painel_recordes_scroll.setMinimumWidth(235)
        self.painel_recordes_scroll.setWidgetResizable(True)
        self.painel_recordes_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.painel_recordes_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.painel_recordes_scroll.setFrameShape(QFrame.NoFrame)
        self.painel_recordes_scroll.setStyleSheet("""
            QScrollArea#pausePremiumRecordsScroll {
                background-color: #07192E; border: none;
            }
        """)
        self.painel_recordes_scroll.setWidget(recordes)
        self.painel_recordes_scroll.setAccessibleName("Painel lateral rolavel de recordes pessoais")
        self.painel_recordes_scroll.setAccessibleDescription(
            "Recorde do jogo ativo, como jogar e outros recordes; role para acessar todos os registros."
        )
        self.painel_recordes_scroll.setFocusPolicy(Qt.StrongFocus)
        self.painel_recordes_scroll.verticalScrollBar().setSingleStep(26)

        self.divisor_premium = QSplitter(Qt.Horizontal, self)
        self.divisor_premium.setObjectName("pausePremiumMainSplitter")
        self.divisor_premium.setChildrenCollapsible(False)
        self.divisor_premium.setAccessibleName("Divisor ajustavel entre jogo e recordes")
        self.divisor_premium.setHandleWidth(12)
        # Reserva altura real para os cinco tabuleiros; em janelas baixas
        # a rolagem externa L14 expõe conteúdo sem comprimir hitboxes.
        self.divisor_premium.setMinimumHeight(ARENA_F03_PERFIS[0]["arena_min"])
        self.divisor_premium.setOpaqueResize(False)
        self.divisor_premium.setStyleSheet("""
            QSplitter#pausePremiumMainSplitter::handle {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #123F5F, stop:0.5 #1C688F, stop:1 #0D304E);
                border-radius: 4px;
            }
        """)
        self.divisor_premium.addWidget(self.painel_jogo_premium)
        self.divisor_premium.addWidget(self.painel_recordes_scroll)
        self.divisor_premium.setStretchFactor(0, 7)
        self.divisor_premium.setStretchFactor(1, 3)
        self.divisor_premium.setSizes([700, 300])
        layout.addWidget(self.divisor_premium, 1)
        # O widget e instalado uma unica vez; rolagem sem alterar sinais ou QTimers.
        self._arena_scroll_vertical.setWidget(self._arena_conteudo)
        self._densidade_compacta_arena = None
        self._aplicar_densidade_arena()

        self.minutos.valueChanged.connect(self._minutos_pausa_alterados)
        self.atualizar_preview_tempo()
        self.atualizar_recordes()

    def resizeEvent(self, evento):
        # Qt trabalha em pixels logicos: mesmo comportamento sob DPR 1 / 1.25 / 1.5.
        super().resizeEvent(evento)
        if hasattr(self, "_arena_layout") and hasattr(self, "_botoes_navegacao_premium"):
            self._aplicar_densidade_arena()

    def _aplicar_densidade_arena(self):
        """Ajustes de geometria por faixa, sem mexer no estado dos jogos/timers."""
        if not hasattr(self, "_densidade_compacta_arena"):
            return
        largura = self.width()
        # Quatro faixas: referência 1706, desktop 1366, compacta e mínima.
        faixa = _arena_f17_faixa_por_largura(largura)
        if self._densidade_compacta_arena == faixa:
            return  # alterações somente ao cruzar um breakpoint lógico
        self._densidade_compacta_arena = faixa
        perfil = ARENA_F03_PERFIS[faixa]
        compacto = faixa in (1, 2)
        estreito = faixa == 2
        self._arena_layout.setContentsMargins(
            perfil["margem_h"], perfil["margem_v"],
            perfil["margem_h"], perfil["margem_v"]
        )
        self._arena_layout.setSpacing(perfil["gap"])
        # Reserva espacial sem introduzir cartões, botões ou timers falsos.
        self.cabecalho_premium.setFixedHeight(perfil["hero"])
        # F05: tamanho do emblema segue os breakpoints do F03;
        # os controles reais nunca são ocultados.
        tamanho_icone = {3: 76, 0: 64, 1: 52, 2: 44}[faixa]
        self._icone_cabecalho_premium.setFixedSize(tamanho_icone, tamanho_icone)
        self._cabecalho_premium_layout.setSpacing(13 if faixa in (0, 3) else 8)
        self._cabecalho_premium_layout.setContentsMargins(
            17 if faixa in (0, 3) else 10, 6,
            18 if faixa in (0, 3) else 10, 6
        )
        self._painel_pausa_geometria.setFixedHeight(perfil["pausa"])
        self.navegacao_premium.setFixedHeight(perfil["nav"])
        for botao in self._botoes_navegacao_premium:
            botao.setFixedHeight(perfil["tab"])
        self.divisor_premium.setMinimumHeight(perfil["arena_min"])
        self._icone_pausa_premium.setVisible(not estreito)
        self._icone_pausa_premium.setFixedSize(42 if compacto else 50, 42 if compacto else 50)
        # Configuração acessível também no modo estreito pelo seletor Outro.
        self.ajuste_pausa_btn.setVisible(not compacto)
        self.minutos.setFixedWidth(62 if estreito else (66 if compacto else 70))
        self.pausa_tempo.setMinimumWidth(72 if compacto else 94)
        self.iniciar_pausa_btn.setMinimumWidth(88 if estreito else (100 if compacto else 135))
        self.parar_pausa_btn.setMinimumWidth(58 if estreito else (70 if compacto else 87))
        self.iniciar_pausa_btn.setFixedHeight(36 if compacto else 44)
        self.parar_pausa_btn.setFixedHeight(36 if compacto else 44)
        self._painel_tempo_pausa.layout().setContentsMargins(6 if compacto else 12, 1, 6 if compacto else 12, 1)
        self._painel_seletores_pausa.layout().setContentsMargins(2 if compacto else 4, 3 if compacto else 4, 2 if compacto else 4, 3 if compacto else 4)
        self._seletor_pausa_layout.setSpacing(2 if compacto else 3)
        for duracao, botao in self.botoes_duracao.items():
            w = (44 if duracao != "outro" else 49) if estreito else ((48 if duracao != "outro" else 54) if compacto else (58 if duracao != "outro" else 64))
            botao.setFixedWidth(w)
            botao.setFixedHeight(33 if compacto else 39)
        for botao in self._botoes_navegacao_premium:
            botao.setMinimumWidth(100 if compacto else 130)
            botao.setIconSize(QSize(27 if compacto else 34, 27 if compacto else 34))
        self.divisor_premium.setHandleWidth(9 if compacto else 12)
        # C09: passos em pixels logicos para janelas compactas; permanece
        # habilitada a rolagem nativa e os controles de teclado do F17.
        self._arena_scroll_vertical.verticalScrollBar().setSingleStep(
            22 if estreito else (25 if compacto else 28)
        )
        self.painel_recordes_scroll.verticalScrollBar().setSingleStep(
            22 if compacto else 26
        )

    def _sincronizar_aba_premium(self, indice):
        """Sincroniza navegação e, quando criada, a lateral do jogo ativo."""
        if 0 <= indice < len(self._botoes_navegacao_premium):
            self._botoes_navegacao_premium[indice].setChecked(True)
        # Na montagem inicial, o sinal é conectado antes de construir a lateral.
        if hasattr(self, "recorde_foco_valor"):
            self._atualizar_paineis_contextuais()

    def _f15_expandir_demais(self, expandido):
        """Mantém acesso aos cinco cartões já existentes, sem duplicá-los."""
        self._f15_conteudo_demais.setVisible(expandido)
        self._f15_botao_demais.setText(
            "Recolher recordes dos outros jogos  ▴" if expandido
            else "Ver recordes dos outros jogos  ▾"
        )
        # Faz o botão permanecer alcançável mesmo depois do relayout.
        # Não move foco, não cria timer e não reinicializa a aba ativa.
        self.painel_recordes_scroll.ensureWidgetVisible(self._f15_botao_demais, 12, 12)

    def _f15_atualizar_metricas(self, chave):
        """No máximo uma leitura por jogo até novo resultado registrado."""
        if chave not in self._f15_cache:
            try:
                self._f15_cache[chave] = obter_indicadores_reais(chave)
            except Exception:
                # Falha do banco jamais impede navegar/abrir a Arena.
                self._f15_cache[chave] = [("Consulta de recordes", "Dados indisponíveis", None)]
        dados = self._f15_cache[chave]
        for indice, (cartao, rotulo, valor, data) in enumerate(self._f15_linhas_metricas):
            if indice < len(dados):
                nome, numero, quando = dados[indice]
                rotulo.setText(nome)
                valor.setText(numero)
                data.setText(quando or "")
                cartao.setAccessibleName(
                    f"{nome}: {numero}" + (f", registro em {quando}" if quando else "")
                )
                cartao.show()
            else:
                cartao.hide()

    def _atualizar_paineis_contextuais(self):
        """Só exibe dados já obtidos de obter_recordes_jogos() e dicas gameHint."""
        indice = self.tabs.currentIndex()
        chaves = ("chimpanze", "memoria", "sequencia", "rotacao_visual", "quebra_cabeca")
        nomes = ("Chimpanzé", "Memória", "Sequência visual", "Rotação visual", "Quebra-cabeça")
        if not 0 <= indice < len(chaves):
            return
        chave = chaves[indice]
        self.recorde_foco_nome.setText(nomes[indice])
        self.recorde_foco_icone.setPixmap(_arena_f12_trofeu_mini_pixmap(34))
        self.recorde_foco_emblema.setPixmap(_arena_f12_trofeu_emblema_pixmap(82))
        dados = getattr(self, "_recordes_premium_dados", {})
        valor_principal, detalhe = _arena_f12_formatar_recorde_destaque(chave, dados.get(chave))
        self.recorde_foco_valor.setText(valor_principal)
        self.recorde_foco_partidas.setText(detalhe)
        self.recorde_foco_partidas.setVisible(True)
        dica = self.tabs.widget(indice).findChild(QLabel, "gameHint")
        self.como_jogar_texto.setText(dica.text() if dica is not None else "Instruções indisponíveis.")
        for outra_chave, cartao in self.recorde_cards.items():
            cartao.setVisible(outra_chave != chave)
        self._f15_atualizar_metricas(chave)

    def eventFilter(self, observado, evento):
        """Preserva navegação e mantém visíveis os controles focados."""
        if evento.type() == QEvent.FocusIn:
            if observado in self._botoes_navegacao_premium:
                self._arena_scroll_vertical.ensureWidgetVisible(observado, 12, 12)
            elif observado is self._f15_botao_demais:
                self.painel_recordes_scroll.ensureWidgetVisible(observado, 12, 12)
        # As setas continuam atuando APENAS nos cinco botões de navegação.
        if (observado in self._botoes_navegacao_premium
                and evento.type() == QEvent.KeyPress):
            indice = self._botoes_navegacao_premium.index(observado)
            tecla = evento.key()
            if tecla in (Qt.Key_Right, Qt.Key_Left, Qt.Key_Home, Qt.Key_End):
                if tecla == Qt.Key_Right:
                    destino = (indice + 1) % len(self._botoes_navegacao_premium)
                elif tecla == Qt.Key_Left:
                    destino = (indice - 1) % len(self._botoes_navegacao_premium)
                elif tecla == Qt.Key_Home:
                    destino = 0
                else:
                    destino = len(self._botoes_navegacao_premium) - 1
                self.tabs.setCurrentIndex(destino)
                self._botoes_navegacao_premium[destino].setFocus(Qt.TabFocusReason)
                return True
        return super().eventFilter(observado, evento)

    def _minutos_pausa_alterados(self):
        if self._modo_pausa == "outro":
            self._minutos_personalizados = self.minutos.value()
        self.atualizar_preview_tempo()

    def selecionar_duracao_pausa(self, duracao):
        """Alterna o preset sem alterar o QTimer nem um intervalo ativo."""
        if self.timer_pausa.isActive():
            return
        if self._modo_pausa == "outro":
            self._minutos_personalizados = self.minutos.value()
        self._modo_pausa = duracao
        if duracao == "outro":
            self.minutos.setValue(self._minutos_personalizados)
            self.minutos.show()
            self.minutos.setFocus(Qt.OtherFocusReason)
        else:
            self.minutos.setValue(duracao)
            self.minutos.hide()
        self.botoes_duracao[duracao].setChecked(True)
        self.atualizar_preview_tempo()

    def _configuracao_pausa_habilitada(self, habilitada):
        self.minutos.setEnabled(habilitada)
        for botao in self.botoes_duracao.values():
            botao.setEnabled(habilitada)
        self.ajuste_pausa_btn.setEnabled(habilitada)

    def atualizar_preview_tempo(self):
        if self.timer_pausa.isActive():
            return
        self.pausa_tempo.setText(_formatar_tempo(self.minutos.value() * 60))

    def iniciar_pausa(self):
        if self.timer_pausa.isActive():
            return
        self.tempo_restante = self.minutos.value() * 60
        self.pausa_tempo.setText(_formatar_tempo(self.tempo_restante))
        self.pausa_status.setText("Pausa em andamento.")
        self.pausa_status.setToolTip("O cronômetro não bloqueia os jogos.")
        self._configuracao_pausa_habilitada(False)
        self.iniciar_pausa_btn.setEnabled(False)
        self.parar_pausa_btn.setEnabled(True)
        self.timer_pausa.start()

    def tick_pausa(self):
        if self.tempo_restante <= 0:
            self.finalizar_pausa_por_tempo()
            return
        self.tempo_restante -= 1
        self.pausa_tempo.setText(_formatar_tempo(self.tempo_restante))
        if self.tempo_restante <= 0:
            self.finalizar_pausa_por_tempo()

    def finalizar_pausa_por_tempo(self):
        self.timer_pausa.stop()
        self.pausa_tempo.setText("00:00")
        self.pausa_status.setText("Tempo de pausa concluído.")
        self.pausa_status.setToolTip(
            "Você pode terminar a partida atual ou voltar aos estudos."
        )
        self._configuracao_pausa_habilitada(True)
        self.iniciar_pausa_btn.setEnabled(True)
        self.parar_pausa_btn.setEnabled(False)

    def encerrar_pausa(self):
        self.timer_pausa.stop()
        self.tempo_restante = 0
        self.pausa_status.setText("Pausa encerrada.")
        self.pausa_status.setToolTip("Selecione a duração para começar outra pausa.")
        self._configuracao_pausa_habilitada(True)
        self.iniciar_pausa_btn.setEnabled(True)
        self.parar_pausa_btn.setEnabled(False)
        self.atualizar_preview_tempo()

    def atualizar_recordes(self):
        self._f15_cache.clear()  # Novo resultado: recalcular indicadores reais sob demanda.
        try:
            dados = obter_recordes_jogos()
        except Exception:
            dados = {}
        self._recordes_premium_dados = dados

        chimp = dados.get("chimpanze", {})
        if chimp.get("partidas"):
            self.recorde_labels["chimpanze"].setText(
                f"Nível {chimp.get('melhor_nivel') or 0} • {chimp.get('partidas')} partida(s)"
            )
        else:
            self.recorde_labels["chimpanze"].setText("Sem recorde")

        memoria = dados.get("memoria", {})
        if memoria.get("partidas"):
            partes = []
            if memoria.get("melhor_movimentos") is not None:
                partes.append(f"{memoria['melhor_movimentos']} mov.")
            if memoria.get("melhor_tempo") is not None:
                partes.append(_formatar_tempo(memoria["melhor_tempo"]))
            self.recorde_labels["memoria"].setText(" • ".join(partes) or "Recorde registrado")
        else:
            self.recorde_labels["memoria"].setText("Sem recorde")

        sequencia = dados.get("sequencia", {})
        if sequencia.get("partidas"):
            self.recorde_labels["sequencia"].setText(
                f"Sequência {sequencia.get('melhor_nivel') or 0} • {sequencia.get('partidas')} partida(s)"
            )
        else:
            self.recorde_labels["sequencia"].setText("Sem recorde")

        rotacao = dados.get("rotacao_visual", {})
        if rotacao.get("partidas"):
            partes = []
            if rotacao.get("melhor_nivel") is not None:
                partes.append(f"Nível {rotacao['melhor_nivel']}")
            if rotacao.get("melhor_pontuacao") is not None:
                partes.append(f"{rotacao['melhor_pontuacao']} pts")
            partes.append(f"{rotacao.get('partidas', 0)} partida(s)")
            self.recorde_labels["rotacao_visual"].setText(" • ".join(partes))
        else:
            self.recorde_labels["rotacao_visual"].setText("Sem recorde")

        puzzle = dados.get("quebra_cabeca", {})
        if puzzle.get("partidas"):
            partes = []
            if puzzle.get("melhor_movimentos") is not None:
                partes.append(f"{puzzle['melhor_movimentos']} mov.")
            if puzzle.get("melhor_tempo") is not None:
                partes.append(_formatar_tempo(puzzle["melhor_tempo"]))
            self.recorde_labels["quebra_cabeca"].setText(" • ".join(partes) or "Recorde registrado")
        else:
            self.recorde_labels["quebra_cabeca"].setText("Sem recorde")

        self._atualizar_paineis_contextuais()

    def closeEvent(self, evento):
        self.timer_pausa.stop()
        evento.accept()
