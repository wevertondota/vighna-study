"""Página Início do VighnaStudy: navegação leve, sem acesso ao banco.

Lote 02 — preserva o Dashboard existente e não cria novos motores de estudo.
Os cartões ainda não implementados são desabilitados intencionalmente.
"""

from PySide6.QtCore import Qt, Signal, QTimer, QRect, QRectF, QSettings, QEvent, QPoint
from functools import lru_cache
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen, QPixmap, QRegion
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QAbstractButton, QComboBox, QLineEdit,
    QSizePolicy, QVBoxLayout, QWidget,
)

from ui.design import render_native_qss, render_qss
from tema import normalizar_tema
from ui.portal_background_image import imagem_fundo_inicio_bytes
from ui.portal_background_justica import imagem_justica_holografica_bytes
from ui.portal_animation_frames import (
    NUM_FRAMES, FRAME_DELAY_MS, ART_SIZE, quadro_sobreposicao_png,
)
from ui.portal_head_foreground import (
    ART_SOURCE_RECT, MASK_VISIBLE_SOURCE_RECT, cabeca_holografica_transparente_png,
)
import logging
import os


# Todas as cores provêm de tokens já registrados nos três temas.
ESTILO_PORTAL_INICIO = r"""
QWidget#portalInicioPage { background: {{color:canvas.app}}; }
QScrollArea#portalInicioScroll,
QScrollArea#portalInicioHeaderScroll,
QWidget#portalInicioGradeResponsiva,
QWidget#portalInicioConteudo {
    background: transparent;
    border: none;
}
QFrame#portalInicioCabecalho,
QFrame#portalInicioCard {
    background-color: {{color:surface.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 12px;
}
QFrame#portalInicioCard:hover {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
QWidget#portalInicioCardTopo,
QWidget#portalInicioCardRecursos {
    background: transparent;
    border: none;
}
QLabel#portalInicioNumeroCompacto {
    background: transparent;
    border: none;
    color: {{color:text.muted}};
    font-size: 8pt;
    font-weight: 600;
}
QLabel#portalInicioCardTituloCompacto {
    background: transparent;
    border: none;
    color: {{color:text.primary}};
    font-size: 12pt;
    font-weight: 700;
}
QLabel#portalInicioCardTextoCompacto {
    background: transparent;
    border: none;
    color: {{color:text.secondary}};
    font-size: 9pt;
}
QLabel#portalInicioCardDetalheCompacto {
    background: transparent;
    border: none;
    color: {{color:text.secondary}};
    font-size: 9pt;
}
QPushButton#portalInicioAcessoCompacto {
    background-color: {{color:dashboard.nav_surface}};
    border: 1px solid {{color:border.default}};
    border-radius: 7px;
    color: {{color:dashboard.nav_text}};
    font-size: 9pt;
    font-weight: 700;
    padding: 2px 9px;
    min-height: 28px;
}
QPushButton#portalInicioAcessoCompacto:hover,
QPushButton#portalInicioAcessoCompacto:focus {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
    color: {{color:text.primary}};
}
QPushButton#portalInicioAcessoCompacto:disabled {
    background-color: {{color:surface.disabled}};
    color: {{color:text.disabled}};
    border-color: {{color:border.disabled}};
}
QFrame#portalInicioEditalMiniCard {
    background-color: {{color:surface.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 11px;
}
QFrame#portalInicioEditalMiniCard:hover {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
QFrame#portalInicioEditalMiniCard:focus {
    border: 1px solid {{color:feedback.info_border}};
}
QLabel#portalInicioEditalMiniIcon {
    background: {{color:dashboard.nav_surface}};
    border: 1px solid {{color:border.default}};
    border-radius: 7px;
    color: {{color:dashboard.nav_border}};
    font-size: 17pt;
}
QLabel#portalInicioEditalMiniTitle {
    color: {{color:text.primary}};
    font-size: 10pt;
    font-weight: 700;
}
QLabel#portalInicioEditalMiniProfile {
    color: {{color:text.secondary}};
    font-size: 9pt;
}
QLabel#portalInicioEditalMiniArrow {
    color: {{color:text.secondary}};
    font-size: 15pt;
}
QLabel#portalInicioMarca { color: {{color:text.primary}}; font-size: 16pt; font-weight: 800; }
QLabel#portalInicioTitulo { color: {{color:text.primary}}; font-size: 19pt; font-weight: 800; }
QLabel#portalInicioSubtitulo { color: {{color:text.secondary}}; font-size: 10pt; }
QLabel#portalInicioPerfil { color: {{color:text.secondary}}; font-size: 9pt; }
QLabel#portalInicioEstado { color: {{color:text.muted}}; font-size: 8pt; font-weight: 700; }
QPushButton#portalInicioBusca {
    background-color: {{color:dashboard.nav_surface}};
    color: {{color:dashboard.nav_text}};
    border: 1px solid {{color:dashboard.nav_border}};
    border-radius: 9px;
    min-height: 35px;
    padding: 5px 10px;
    font-size: 9pt;
    font-weight: 700;
}
QPushButton#portalInicioBusca:hover {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
"""


# H05/09 — cards principais da Home (exclusivo do Futurista).
# Aplica alfa somente no preenchimento e nas bordas; não reduz a opacidade
# do widget nem de seus descendentes (títulos, ícones, texto e botões).
# Proporção da figura/GIF e geometria dos três cards permanecem inalteradas.
ESTILO_H05_CARDS_FUTURISTA = r"""
QFrame#portalInicioCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(4, 21, 39, 222), stop:1 rgba(8, 31, 54, 200));
    border: 1px solid rgba(19, 169, 222, 204);
    border-radius: 13px;
}
QFrame#portalInicioCard:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(8, 31, 55, 231), stop:1 rgba(10, 43, 69, 216));
    border: 1px solid rgba(63, 210, 252, 232);
}
QFrame#portalInicioCard QWidget#portalInicioCardTopo,
QFrame#portalInicioCard QWidget#portalInicioCardRecursos {
    background: transparent;
    border: none;
}
QFrame#portalInicioCard QLabel#portalInicioNumeroCompacto {
    color: #b9d0e1;
    background: transparent;
}
QFrame#portalInicioCard QLabel#portalInicioCardTituloCompacto {
    color: #f5faff;
    background: transparent;
}
QFrame#portalInicioCard QLabel#portalInicioCardTextoCompacto,
QFrame#portalInicioCard QLabel#portalInicioCardDetalheCompacto {
    color: #dbeaf6;
    background: transparent;
}
QFrame#portalInicioCard QPushButton#portalInicioAcessoCompacto {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(8, 49, 82, 220), stop:1 rgba(10, 61, 97, 204));
    border: 1px solid rgba(29, 154, 205, 212);
    border-radius: 7px;
    color: #f3faff;
}
QFrame#portalInicioCard QPushButton#portalInicioAcessoCompacto:hover,
QFrame#portalInicioCard QPushButton#portalInicioAcessoCompacto:focus {
    background: rgba(15, 76, 115, 238);
    border: 1px solid #4bd6ff;
    color: #ffffff;
}
QFrame#portalInicioCard QPushButton#portalInicioAcessoCompacto:pressed {
    background: rgba(8, 44, 73, 246);
    border: 1px solid #21afdd;
}
QFrame#portalInicioCard QPushButton#portalInicioAcessoCompacto:disabled {
    background: rgba(17, 35, 53, 214);
    border: 1px solid rgba(84, 105, 120, 176);
    color: #a9b5c1;
}
"""

# H06/09 — Meu Edital e elementos secundários (somente Futurista).
# Somente superfícies recebem alfa. Texto, ícones e controles mantêm opacidade.
ESTILO_H06_EDITAL_FUTURISTA = r"""
QFrame#portalInicioEditalMiniCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(4, 21, 39, 224), stop:0.5 rgba(6, 29, 49, 214),
        stop:1 rgba(8, 36, 60, 207));
    border: 1px solid rgba(19, 169, 222, 203);
    border-radius: 12px;
}
QFrame#portalInicioEditalMiniCard:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(8, 31, 55, 232), stop:1 rgba(12, 50, 78, 217));
    border: 1px solid rgba(76, 211, 249, 235);
}
QFrame#portalInicioEditalMiniCard:focus {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(7, 30, 53, 234), stop:1 rgba(11, 48, 73, 224));
    border: 2px solid rgba(80, 218, 255, 242);
}
QFrame#portalInicioEditalMiniCard[h06Pressionado="true"] {
    background: rgba(5, 33, 57, 241);
    border: 1px solid rgba(26, 183, 228, 238);
}
QFrame#portalInicioEditalMiniCard QLabel#portalInicioEditalMiniIcon {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(5, 66, 102, 212), stop:1 rgba(6, 43, 72, 201));
    border: 1px solid rgba(41, 172, 221, 207);
    border-radius: 8px;
    color: #39d8ff;
}
QFrame#portalInicioEditalMiniCard:hover QLabel#portalInicioEditalMiniIcon {
    background: rgba(8, 75, 117, 225);
    border-color: rgba(95, 223, 255, 238);
}
QFrame#portalInicioEditalMiniCard QLabel#portalInicioEditalMiniTitle {
    background: transparent;
    border: none;
    color: #f5faff;
    font-size: 10pt;
    font-weight: 700;
}
QFrame#portalInicioEditalMiniCard QLabel#portalInicioEditalMiniProfile {
    background: transparent;
    border: none;
    color: #d5e7f3;
    font-size: 9pt;
}
QFrame#portalInicioEditalMiniCard QLabel#portalInicioEditalMiniArrow {
    background: transparent;
    border: none;
    color: #d6f4ff;
    font-size: 15pt;
}
QFrame#portalInicioEditalMiniCard:hover QLabel#portalInicioEditalMiniArrow,
QFrame#portalInicioEditalMiniCard:focus QLabel#portalInicioEditalMiniArrow {
    color: #5ce5ff;
}
QWidget#portalInicioConteudo QLabel#portalInicioTitulo {
    background: transparent;
    border: none;
    color: #f6faff;
}
QWidget#portalInicioConteudo QLabel#portalInicioSubtitulo {
    background: transparent;
    border: none;
    color: #d7e7f5;
}
"""

def _colunas_portal_para_largura(largura: int) -> int:
    """Largura Qt em pixels lógicos; sensível a DPI automaticamente."""
    if largura >= 785:
        return 3
    if largura >= 505:
        return 2
    return 1


class _GradePortalResponsiva(QWidget):
    """Reposiciona widgets existentes, sem recriar os botões nem seus callbacks.

    Recebe eventos da viewport para impedir que o tamanho mínimo de uma grade
    de três colunas bloqueie a passagem a duas ou uma coluna.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("portalInicioGradeResponsiva")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._colunas = 0
        self._viewport_observada = None
        self._cartoes = []
        self._mini_edital = None
        self._grade = QGridLayout(self)
        self._grade.setContentsMargins(0, 0, 0, 0)
        self._grade.setHorizontalSpacing(12)
        self._grade.setVerticalSpacing(18)

    def configurar(self, cartoes, mini_edital):
        self._cartoes = list(cartoes)
        self._mini_edital = mini_edital
        # Parte de uma coluna para não impor largura mínima antes do primeiro resize.
        self.adaptar_largura(0)

    def adaptar_largura(self, largura_util: int):
        colunas = _colunas_portal_para_largura(max(0, int(largura_util)))
        if colunas == self._colunas:
            return
        self.setUpdatesEnabled(False)
        try:
            while self._grade.count():
                self._grade.takeAt(0)
            for col in range(3):
                self._grade.setColumnStretch(col, 1 if col < colunas else 0)
                self._grade.setColumnMinimumWidth(col, 0)
            for idx, card in enumerate(self._cartoes):
                row, col = divmod(idx, colunas)
                self._grade.addWidget(card, row, col)
            if self._mini_edital is not None:
                idx = len(self._cartoes)
                row, col = divmod(idx, colunas)
                self._grade.addWidget(self._mini_edital, row, col)
            self._colunas = colunas
            self._grade.invalidate()
            self.updateGeometry()
        finally:
            self.setUpdatesEnabled(True)
            self.update()

    def eventFilter(self, objeto, evento):
        if (objeto is self._viewport_observada and
                evento.type() == QEvent.Type.Resize):
            self.adaptar_largura(objeto.width() - 36)
        return super().eventFilter(objeto, evento)

    def observar_viewport(self, scroll):
        self._viewport_observada = scroll.viewport()
        self._viewport_observada.installEventFilter(self)
        self.adaptar_largura(self._viewport_observada.width() - 36)


# H08: evita repetir base85/SHA-256 a cada ciclo da mesma animacao.
# Limite de 47 PNGs COMPRIMIDOS: nao guarda dezenas de QPixmaps RGBA em RAM.
@lru_cache(maxsize=NUM_FRAMES - 1)
def _quadro_png_verificado_em_cache(indice: int) -> bytes:
    return quadro_sobreposicao_png(indice)


class _FundoPortalInicio(QWidget):
    """Home com GIF H03 reconstruído pelos quadros PNG e relógio nativo Qt.

    Sem QMovie: a animação é controlada por QTimer e os PNGs dos 48 quadros
    derivam do GIF aprovado. O fundo estático segue como fallback seguro.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("portalInicioConteudo")
        self._usar_fundo = False
        self._original = None
        self._redimensionada = None
        self._tamanho_cache = None
        self._frame_index = 0
        self._quadro_pintado = -1
        self._overlay = None
        self._overlay_falhou = False
        # Recuperacao limitada: evita ficar parado por falha transitoria do Qt,
        # mas nunca cria ciclos infinitos de tentativas se o recurso corrompeu.
        self._recuperacoes_tentadas = 0
        self._quadros_avancados = 0
        self._reduzir_movimento_ambiente = os.environ.get(
            "VIGHNA_HOME_REDUZIR_MOVIMENTO", ""
        ).strip().lower() in ("1", "true", "sim", "yes", "on")
        self._preferencias = QSettings("VighnaStudy", "Home")
        self._reduzir_movimento = (self._reduzir_movimento_ambiente or
                                  self._preferencias.value(
                                      "acessibilidade/reduzir_movimento", False,
                                      type=bool))
        self._relogio = QTimer(self)
        self._relogio.setInterval(FRAME_DELAY_MS)
        self._relogio.setTimerType(Qt.TimerType.PreciseTimer)
        self._relogio.timeout.connect(self._avancar_quadro)

    def definir_tema(self, tema: str) -> None:
        habilitar = (tema == "futurista" or
                    normalizar_tema(tema) in ("escuro", "futurista"))
        if self._usar_fundo != habilitar:
            self._usar_fundo = habilitar
            self._redimensionada = None
            self._tamanho_cache = None
            self.update()
        self._sincronizar_animacao()
        QTimer.singleShot(0, self._sincronizar_animacao)

    def definir_reducao_movimento(self, reduzir: bool) -> None:
        """Altera apenas a reprodução na Home; não modifica arquivos de estudo."""
        reduzir = bool(reduzir) or self._reduzir_movimento_ambiente
        if self._reduzir_movimento == reduzir:
            return
        self._reduzir_movimento = reduzir
        if reduzir:
            self._relogio.stop()
        if reduzir:
            self._frame_index = 0
            self._quadro_pintado = -1
            self._overlay = None
        self._sincronizar_animacao()
        self.update()

    def _ativo_para_animar(self) -> bool:
        return (self._usar_fundo and self.isVisible() and
                not self._reduzir_movimento and not self._overlay_falhou
                and not self.window().isMinimized())

    def _sincronizar_animacao(self) -> None:
        ativo = self._ativo_para_animar()
        if ativo and not self._relogio.isActive():
            self._relogio.start()
            logging.getLogger(__name__).info(
                "Home H05-R2: relogio de quadros PNG ativo (%s ms, %s quadros)",
                FRAME_DELAY_MS, NUM_FRAMES)
        elif not ativo and self._relogio.isActive():
            self._relogio.stop()
            logging.getLogger(__name__).debug("Home H05-R2: quadros pausados")

    def _avancar_quadro(self) -> None:
        if not self._ativo_para_animar():
            self._sincronizar_animacao()
            return
        self._frame_index = (self._frame_index + 1) % NUM_FRAMES
        self._quadros_avancados += 1
        self.update()

    def showEvent(self, evento):
        super().showEvent(evento)
        # Uma falha de decodificacao pode ser transitoria; recuperar apenas
        # quando a Home volta a ser exibida, no maximo duas vezes por sessao.
        if (self._overlay_falhou and self._recuperacoes_tentadas < 2
                and not self._reduzir_movimento):
            self._recuperacoes_tentadas += 1
            self._overlay_falhou = False
            self._frame_index = 0
            self._quadro_pintado = -1
            self._overlay = None
            logging.getLogger(__name__).info(
                "Home H08: nova tentativa de reproduzir quadros (tentativa %d/2)",
                self._recuperacoes_tentadas)
        self._sincronizar_animacao()
        QTimer.singleShot(0, self._sincronizar_animacao)

    def hideEvent(self, evento):
        super().hideEvent(evento)
        self._sincronizar_animacao()

    def _pixmap_para_area(self):
        if self._original is None:
            imagem = QPixmap()
            try:
                imagem.loadFromData(imagem_justica_holografica_bytes(), "PNG")
            except (ValueError, TypeError, RuntimeError):
                pass
            if imagem.isNull():
                if not imagem.loadFromData(imagem_fundo_inicio_bytes(), "JPG"):
                    return None
            self._original = imagem
        tamanho = self.size()
        if tamanho.width() <= 0 or tamanho.height() <= 0:
            return None
        escala = max(1.0, float(self.devicePixelRatioF()))
        chave = (tamanho.width(), tamanho.height(), round(escala,3))
        if chave != self._tamanho_cache or self._redimensionada is None:
            largura_px = max(1,round(tamanho.width() * escala))
            altura_px = max(1,round(tamanho.height() * escala))
            self._redimensionada = self._original.scaled(
                largura_px, altura_px,
                Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self._redimensionada.setDevicePixelRatio(escala)
            self._tamanho_cache = chave
        return self._redimensionada

    def _overlay_atual(self):
        if self._reduzir_movimento or self._overlay_falhou:
            return None
        if self._frame_index == 0:
            self._quadro_pintado = 0
            self._overlay = None
            return None
        if self._quadro_pintado == self._frame_index:
            return self._overlay
        try:
            conteudo = _quadro_png_verificado_em_cache(self._frame_index)
            pixmap = QPixmap()
            if not pixmap.loadFromData(conteudo,"PNG") or pixmap.isNull():
                raise ValueError("PNG de quadro inválido")
            if (pixmap.width(),pixmap.height()) != ART_SIZE:
                raise ValueError("Dimensões de quadro incompatíveis")
            self._quadro_pintado = self._frame_index
            self._overlay = pixmap
            return pixmap
        except (ValueError, RuntimeError, TypeError) as exc:
            self._overlay_falhou = True
            self._overlay = None
            self._relogio.stop()
            logging.getLogger(__name__).warning(
                "Home H05-R2: quadro PNG indisponível, fundo estático: %s", exc)
            return None

    def paintEvent(self, evento):
        super().paintEvent(evento)
        if not self._usar_fundo:
            return
        base = self._pixmap_para_area()
        if base is None:
            return
        painter = QPainter(self)
        largura = base.width() / base.devicePixelRatioF()
        altura = base.height() / base.devicePixelRatioF()
        x = (self.width() - largura) / 2.0
        y = (self.height() - altura) / 2.0
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawPixmap(round(x), round(y), base)
        overlay = self._overlay_atual()
        if overlay is not None and not overlay.isNull():
            # Mesma área escalada do fundo estático; nenhuma deriva ao redimensionar.
            painter.drawPixmap(
                QRectF(x,y,largura,altura),overlay,
                QRectF(0.0,0.0,float(ART_SIZE[0]),float(ART_SIZE[1])))
        veu = QLinearGradient(0,0,0,max(1,self.height()))
        veu.setColorAt(0.0,QColor(2,10,24,100))
        veu.setColorAt(0.55,QColor(2,10,24,64))
        veu.setColorAt(1.0,QColor(2,10,24,38))
        painter.fillRect(self.rect(),veu)
        painter.end()


# H10-C R1: cabeça da Justiça sobre o VIDRO do cabeçalho (viewport).
# Não altera os 48 quadros, animação, cartões ou configurações.
class _CabecaHolograficaPrimeiroPlano(QWidget):
    """Overlay decorativo do cabeçalho; camada independente e sem mouse.

    H10-C escondia TODA a cabeça caso qualquer controle intersectasse a zona.
    R1 usa viewport real como pai e recorta só o retângulo dos controles.
    """

    def __init__(self, fundo: _FundoPortalInicio, cabecalho: QScrollArea):
        self._viewport = cabecalho.viewport()
        super().__init__(self._viewport)
        self.setObjectName("portalInicioCabecaProfundidadeH10")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.NoFocus)
        self._fundo = fundo
        self._cabecalho = cabecalho
        self._ativo = True
        self._png = QPixmap()
        self._pendente = False
        self._alvo = QRectF()
        self._clip = QRegion()
        # H10-D: a máscara da borda pertence somente ao cabeçalho da Home.
        # Nunca aplicar ao GIF ou aos controles. Guardamos a máscara anterior
        # para restaurá-la quando a página, tema ou overlay forem ocultados.
        self._header_real = cabecalho.widget()
        self._header_mask_original = (self._header_real.mask()
                                      if self._header_real is not None else QRegion())
        self._notch_ativo = False
        self._ultimo_recorte = None
        try:
            self._png.loadFromData(cabeca_holografica_transparente_png(), "PNG")
        except (ValueError, RuntimeError, TypeError):
            pass
        for item in (fundo, cabecalho, self._viewport, cabecalho.widget()):
            if item is not None:
                item.installEventFilter(self)
        cabecalho.horizontalScrollBar().valueChanged.connect(
            lambda _valor: self._agendar()
        )
        self.hide()
        QTimer.singleShot(0, self.sincronizar)
        QTimer.singleShot(220, self.sincronizar)

    def _restaurar_borda(self):
        """Reestabelece pintura original do cabeçalho fora da Home/tema."""
        if not self._notch_ativo:
            return
        header = self._header_real
        self._notch_ativo = False
        self._ultimo_recorte = None
        if header is not None:
            if self._header_mask_original.isEmpty():
                header.clearMask()
            else:
                header.setMask(self._header_mask_original)
            header.update()

    def _recortar_borda_sob_cabeca(self):
        """Abre uma fenda de 3 px *apenas* onde a máscara opaca cruza a borda.

        A fenda é uma exclusão de QRegion no QFrame original do cabeçalho.
        O widget superior (irmão do QFrame no viewport) continua visível;
        o fundo holográfico real aparece pela borda, sem cor inventada.
        """
        header = self._header_real
        if (header is None or not header.isVisible() or self._png.isNull()
                or self._alvo.width() <= 0.0 or self._alvo.height() <= 0.0):
            self._restaurar_borda()
            return
        # A borda inferior está no QFrame, e não no QScrollArea (NoFrame).
        pos_header = header.mapTo(self._viewport, QPoint(0, 0))
        linha_borda = pos_header.y() + header.height() - 1
        if linha_borda < 0 or linha_borda >= self._viewport.height():
            self._restaurar_borda()
            return
        # O PNG da cabeça é 190x126, mapeado para _alvo. Amostramos a
        # opacidade na linha real da borda; o brilho/contorno é respeitado.
        py = round((linha_borda - self._alvo.y()) * self._png.height()
                   / self._alvo.height())
        if py < 0 or py >= self._png.height():
            self._restaurar_borda()
            return
        imagem = self._png.toImage()
        xs = []
        for x in range(imagem.width()):
            if imagem.pixelColor(x, py).alpha() >= 42:
                xv = round(self._alvo.x() + x * self._alvo.width()
                           / float(imagem.width()))
                if 0 <= xv < self._viewport.width():
                    xs.append(xv)
        if not xs:
            self._restaurar_borda()
            return
        # Margem de 3 px nas extremidades, altura de 3 px. Regra
        # defensiva: não abrir o recorte sobre botões/controles.
        inicio = max(0, min(xs) - 3)
        fim = min(self._viewport.width(), max(xs) + 4)
        tira = QRegion(QRect(inicio, linha_borda - 2,
                             max(0, fim - inicio), 3))
        tira = tira.intersected(self._clip)
        if tira.isEmpty():
            self._restaurar_borda()
            return
        # Mapeia viewport -> coordenadas do próprio QFrame, com clipping.
        recorte_header = tira.translated(-pos_header.x(), -pos_header.y())
        recorte_header = recorte_header.intersected(QRegion(header.rect()))
        if recorte_header.isEmpty():
            self._restaurar_borda()
            return
        # Máscara original pode ser vazia (= sem restrição); preservá-la
        # quando existir impede apagar outro recorte definido pelo usuário.
        base = (self._header_mask_original if not self._header_mask_original.isEmpty()
                else QRegion(header.rect()))
        mascara = base.subtracted(recorte_header)
        chave = (inicio, fim, linha_borda, header.width(), header.height())
        if chave != self._ultimo_recorte or not self._notch_ativo:
            header.setMask(mascara)
            self._ultimo_recorte = chave
            self._notch_ativo = True
            header.update()

    def hideEvent(self, evento):
        self._restaurar_borda()
        super().hideEvent(evento)

    def definir_tema(self, tema: str):
        # O tema pode vir normalizado como Escuro devido à base do Futurista.
        nome = normalizar_tema(tema)
        self._ativo = nome in ("futurista", "escuro")
        self._agendar()

    def eventFilter(self, objeto, evento):
        if evento.type() in (
            QEvent.Type.Resize, QEvent.Type.Move,
            QEvent.Type.Show, QEvent.Type.Hide,
            QEvent.Type.LayoutRequest,
        ):
            self._agendar()
        return super().eventFilter(objeto, evento)

    def _agendar(self):
        if not self._pendente:
            self._pendente = True
            QTimer.singleShot(0, self.sincronizar)

    def sincronizar(self):
        self._pendente = False
        if (not self._ativo or self._png.isNull() or
                not self._fundo._usar_fundo or
                not self._fundo.isVisible() or
                self._fundo.width() < 1 or self._fundo.height() < 1 or
                self._viewport.width() < 1 or self._viewport.height() < 1):
            self.hide()
            return
        # O cabeçalho em rolagem muda o alinhamento das ações. Nessa situação
        # compacta o adorno é omitido, em vez de obstruir a navegação.
        if self._cabecalho.horizontalScrollBar().value() != 0:
            self.hide()
            return
        base = self._fundo._pixmap_para_area()
        if base is None or base.isNull():
            self.hide()
            return
        largura = base.width() / base.devicePixelRatioF()
        altura = base.height() / base.devicePixelRatioF()
        origem_x = (self._fundo.width() - largura) / 2.0
        origem_y = (self._fundo.height() - altura) / 2.0
        # H10-C R2: o arquivo de recorte foi extraido do GIF 1304x705,
        # enquanto ART_SIZE representa o motor animado 1706x922.
        # Misturar essas referencias deslocava a copia da cabeca para a
        # esquerda e para cima, perto do botao Gerenciar.
        # Esta referencia e do RECURSO da mascara, independente do GIF.
        largura_referencia_mascara = 1304.0
        altura_referencia_mascara = 705.0
        sx = largura / largura_referencia_mascara
        sy = altura / altura_referencia_mascara
        origem_viewport = self._viewport.mapTo(self._fundo, QPoint(0, 0))
        rx, ry, rw, rh = ART_SOURCE_RECT
        self._alvo = QRectF(
            origem_x + rx*sx - origem_viewport.x(),
            origem_y + ry*sy - origem_viewport.y(),
            rw*sx, rh*sy,
        )
        vx, vy, vw, vh = MASK_VISIBLE_SOURCE_RECT
        area_cabeca = QRectF(
            origem_x + vx*sx - origem_viewport.x(),
            origem_y + vy*sy - origem_viewport.y(),
            vw*sx, vh*sy,
        )
        viewport_rect = QRectF(self._viewport.rect())
        if area_cabeca.intersected(viewport_rect).isEmpty():
            self.hide()
            return
        if self.geometry() != self._viewport.rect():
            self.setGeometry(self._viewport.rect())
        # Não escondemos a cabeça inteira por um único controle.
        # Removemos apenas os pixels diretamente acima das áreas de interação.
        regiao = QRegion(self.rect())
        for tipo in (QAbstractButton, QComboBox, QLineEdit):
            for controle in self._cabecalho.findChildren(tipo):
                if not controle.isVisible() or not controle.isEnabled():
                    continue
                try:
                    pos = controle.mapTo(self._viewport, QPoint(0, 0))
                except RuntimeError:
                    continue
                area = QRect(
                    pos.x()-6, pos.y()-6,
                    controle.width()+12, controle.height()+12,
                )
                regiao = regiao.subtracted(QRegion(area))
        self._clip = regiao
        if self.isHidden():
            self.show()
        self.raise_()
        # Pequena interrupção real da borda por baixo da cabeça; não desenha
        # uma faixa escura e não desloca a máscara já homologada em R2.
        self._recortar_borda_sob_cabeca()
        self.update()

    def paintEvent(self, evento):
        if not self._ativo or self._png.isNull() or self._alvo.isEmpty():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setClipRegion(self._clip)
        painter.drawPixmap(
            self._alvo, self._png,
            QRectF(0.0, 0.0, float(self._png.width()), float(self._png.height())),
        )
        painter.end()

def _label(texto: str, nome: str, *, quebra: bool = True) -> QLabel:
    label = QLabel(texto)
    label.setObjectName(nome)
    label.setWordWrap(quebra)
    return label


class _IconeModulo(QWidget):
    """Ícone vetorial leve, independente de fontes e de bibliotecas opcionais."""

    def __init__(self, papel: str, parent=None):
        super().__init__(parent)
        self.papel = papel
        self._cor = QColor("#27C9ED")
        self.setObjectName("portalInicioCardIcone")
        self.setFixedSize(22, 22)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setToolTip({
            "dashboard": "Dashboard de Estudos",
            "simulados": "Simulados e Treinos",
            "recursos": "Central de Recursos",
        }.get(papel, "Área de estudos"))

    def definir_tema(self, tema: str):
        if tema == "futurista":
            cor = "#00D1FF"  # Identidade visual nativa; sem seleção de tema.
        else:
            cor = {
                "claro": "#087D9E",
                "escuro": "#47BBE0",
                "futurista": "#00D1FF",
            }.get(normalizar_tema(tema), "#47BBE0")
        self._cor = QColor(cor)
        self.update()

    def paintEvent(self, evento):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(self._cor, 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        if self.papel == "dashboard":
            # Colunas e tendência ascendente.
            painter.drawLine(3, 18, 19, 18)
            painter.drawRect(5, 12, 3, 6)
            painter.drawRect(10, 9, 3, 9)
            painter.drawRect(15, 6, 3, 12)
            painter.drawLine(4, 12, 11, 5)
            painter.drawLine(11, 5, 18, 6)
        elif self.papel == "simulados":
            # Prancheta com marca de conferência.
            painter.drawRoundedRect(5, 4, 13, 16, 2, 2)
            painter.drawLine(9, 3, 14, 3)
            painter.drawLine(9, 12, 11, 14)
            painter.drawLine(11, 14, 15, 10)
        else:
            # Grade de recursos.
            painter.drawRoundedRect(3, 3, 7, 7, 1, 1)
            painter.drawRoundedRect(12, 3, 7, 7, 1, 1)
            painter.drawRoundedRect(3, 12, 7, 7, 1, 1)
            painter.drawRoundedRect(12, 12, 7, 7, 1, 1)
        painter.end()


def _criar_cartao(numero: str, titulo: str, descricao: str, recursos: tuple[str, ...],
                  nome_acao: str, acao, papel: str) -> QFrame:
    """Card de acesso compacto, conforme referência visual; conserva o callback."""
    card = QFrame()
    card.setObjectName("portalInicioCard")
    card.setProperty("portalRole", papel)
    card.setAttribute(Qt.WA_Hover, True)
    card.setMinimumWidth(205)
    # Deixe o Qt acomodar fontes/DPI sem cortar textos. O limite superior
    # impede que os cards voltem ao formato alto anterior.
    card.setMinimumHeight(216)
    card.setMaximumHeight(266)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    coluna = QVBoxLayout(card)
    coluna.setContentsMargins(14, 12, 14, 12)
    coluna.setSpacing(7)

    topo = QWidget(card)
    topo.setObjectName("portalInicioCardTopo")
    topo.setFixedHeight(24)
    topo_layout = QHBoxLayout(topo)
    topo_layout.setContentsMargins(0, 0, 0, 0)
    topo_layout.setSpacing(4)
    icone = _IconeModulo(papel, topo)
    topo_layout.addWidget(icone, 0, Qt.AlignVCenter)
    topo_layout.addStretch(1)
    num = _label(numero, "portalInicioNumeroCompacto", quebra=False)
    num.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    topo_layout.addWidget(num, 0, Qt.AlignVCenter)
    coluna.addWidget(topo)

    titulo_label = _label(titulo, "portalInicioCardTituloCompacto", quebra=False)
    titulo_label.setToolTip({
        "dashboard": "Dashboard de Estudos",
        "simulados": "Simulados e Treinos",
        "recursos": "Central de Recursos",
    }.get(papel, titulo))
    titulo_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    coluna.addWidget(titulo_label)

    descricao_label = _label(descricao, "portalInicioCardTextoCompacto")
    descricao_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    coluna.addWidget(descricao_label)
    coluna.addSpacing(2)

    lista = QWidget(card)
    lista.setObjectName("portalInicioCardRecursos")
    lista_layout = QVBoxLayout(lista)
    lista_layout.setContentsMargins(0, 0, 0, 0)
    lista_layout.setSpacing(4)
    for item in recursos:
        rotulo = _label("•  " + item, "portalInicioCardDetalheCompacto", quebra=False)
        lista_layout.addWidget(rotulo)
    coluna.addWidget(lista)
    coluna.addStretch(1)

    if acao is None:
        coluna.addWidget(_label("EM PREPARAÇÃO", "portalInicioEstado"))
    botao = QPushButton(nome_acao)
    botao.setObjectName("portalInicioAcessoCompacto")
    botao.setFixedHeight(32)
    botao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    botao.setCursor(Qt.PointingHandCursor if acao is not None else Qt.ArrowCursor)
    if acao is None:
        botao.setEnabled(False)
        botao.setToolTip("Este módulo será conectado em um lote posterior.")
    else:
        botao.clicked.connect(acao)
    coluna.addWidget(botao)
    return card
class _CartaoEdital(QFrame):
    """Card clicável preservado; acabamento de pressão só visual."""
    clicked = Signal()

    def _indicar_pressao(self, pressionado: bool) -> None:
        if bool(self.property("h06Pressionado")) == pressionado:
            return
        self.setProperty("h06Pressionado", pressionado)
        estilo = self.style()
        estilo.unpolish(self)
        estilo.polish(self)
        self.update()

    def mousePressEvent(self, evento):
        if evento.button() == Qt.LeftButton:
            self._indicar_pressao(True)
            evento.accept()
            return
        super().mousePressEvent(evento)

    def mouseReleaseEvent(self, evento):
        if evento.button() == Qt.LeftButton:
            self._indicar_pressao(False)
            if self.rect().contains(evento.pos()):
                self.clicked.emit()
            evento.accept()
            return
        super().mouseReleaseEvent(evento)

    def leaveEvent(self, evento):
        self._indicar_pressao(False)
        super().leaveEvent(evento)

    def keyPressEvent(self, evento):
        if evento.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.clicked.emit()
            evento.accept()
            return
        super().keyPressEvent(evento)


def _criar_mini_cartao_edital(abrir_edital):
    """Card compacto abaixo das três opções, sem cortes e inteiro clicável."""
    cartao = _CartaoEdital()
    cartao.setObjectName("portalInicioEditalMiniCard")
    cartao.setProperty("h06Pressionado", False)
    # A largura acompanha a coluna Dashboard na grade. Mantém a altura compacta.
    cartao.setFixedHeight(70)
    cartao.setMinimumWidth(215)
    cartao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    cartao.setAttribute(Qt.WA_Hover, True)
    cartao.setCursor(Qt.PointingHandCursor)
    cartao.setFocusPolicy(Qt.StrongFocus)
    cartao.setAccessibleName("Meu Edital — perfil ativo")
    cartao.setToolTip("Abrir a Central do Edital do perfil ativo")
    cartao.clicked.connect(abrir_edital)

    linha = QHBoxLayout(cartao)
    linha.setContentsMargins(12, 8, 12, 8)
    linha.setSpacing(10)

    icone = QLabel("▤", cartao)
    icone.setObjectName("portalInicioEditalMiniIcon")
    icone.setAlignment(Qt.AlignCenter)
    icone.setFixedSize(40, 40)

    textos = QVBoxLayout()
    textos.setContentsMargins(0, 0, 0, 0)
    textos.setSpacing(2)
    titulo = _label("Meu Edital", "portalInicioEditalMiniTitle", quebra=False)
    perfil = _label("Perfil ativo", "portalInicioEditalMiniProfile", quebra=False)
    titulo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    perfil.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    textos.addWidget(titulo)
    textos.addWidget(perfil)

    seta = QLabel("↗", cartao)
    seta.setObjectName("portalInicioEditalMiniArrow")
    seta.setAlignment(Qt.AlignCenter)
    seta.setFixedSize(20, 26)

    # Eventos de mouse e teclado pertencem ao cartão inteiro.
    for rotulo in (icone, titulo, perfil, seta):
        rotulo.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    linha.addWidget(icone, 0, Qt.AlignVCenter)
    linha.addLayout(textos, 1)
    linha.addWidget(seta, 0, Qt.AlignVCenter)
    cartao.portal_edital_perfil_label = perfil
    return cartao


def atualizar_perfil_mini_edital(pagina: QWidget, nome_perfil: str) -> None:
    """Acompanha a seleção do perfil já gerenciada pelo controlador principal."""
    cartao = getattr(pagina, "portal_edital_minicard", None)
    if cartao is None:
        return
    nome = str(nome_perfil or "").strip() or "Nenhum perfil selecionado"
    rotulo = cartao.portal_edital_perfil_label
    rotulo.setText(rotulo.fontMetrics().elidedText(nome, Qt.ElideRight, 218))
    rotulo.setToolTip(nome)
    cartao.setAccessibleName("Meu Edital — " + nome)
    cartao.setToolTip("Abrir a Central do Edital do perfil: " + nome)


def criar_portal_inicio(abrir_dashboard, abrir_busca, abrir_questoes,
                        abrir_simulados=None, abrir_recursos=None,
                        cabecalho_compartilhado=None, abrir_edital=None) -> QWidget:
    """Monta página independente e barata, compartilhada pelos três temas."""
    pagina = QWidget()
    pagina.setObjectName("portalInicioPage")
    pagina.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    base = QVBoxLayout(pagina)
    base.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setObjectName("portalInicioScroll")
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    corpo = _FundoPortalInicio()
    coluna = QVBoxLayout(corpo)
    coluna.setContentsMargins(18, 15, 18, 20)
    coluna.setSpacing(17)

    if cabecalho_compartilhado is not None:
        # Move o MESMO cabeçalho do Dashboard: seletor de perfil, Gerenciar,
        # Central de Questões e Configurações mantêm suas conexões originais.
        # Um único widget possui o seletor: não há duplicação de estado.
        # O cabeçalho compartilhado pode ser mais largo que uma janela compacta.
        # Uma rolagem horizontal só aparece quando necessária: controles e
        # ações Qt originais continuam acessíveis, sem reduzir área de clique.
        faixa_cabecalho = QScrollArea(corpo)
        faixa_cabecalho.setObjectName("portalInicioHeaderScroll")
        faixa_cabecalho.setFrameShape(QFrame.NoFrame)
        faixa_cabecalho.setWidgetResizable(True)
        faixa_cabecalho.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        faixa_cabecalho.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        faixa_cabecalho.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        faixa_cabecalho.setMinimumWidth(0)
        faixa_cabecalho.setFixedHeight(max(105, cabecalho_compartilhado.minimumHeight() + 22))
        faixa_cabecalho.setWidget(cabecalho_compartilhado)
        coluna.addWidget(faixa_cabecalho)
        perfil = None
    else:
        # Fallback para construtores legados e testes isolados do portal.
        cabecalho = QFrame()
        cabecalho.setObjectName("portalInicioCabecalho")
        cabecalho_layout = QHBoxLayout(cabecalho)
        cabecalho_layout.setContentsMargins(18, 13, 18, 13)
        marca = QVBoxLayout()
        marca.setSpacing(4)
        marca.addWidget(_label("VighnaStudy", "portalInicioMarca"))
        perfil = _label("Perfil ativo", "portalInicioPerfil")
        marca.addWidget(perfil)
        cabecalho_layout.addLayout(marca, 1)
        buscar = QPushButton("⌕  Buscar  ·  Ctrl+K")
        buscar.setObjectName("portalInicioBusca")
        buscar.setCursor(Qt.PointingHandCursor)
        buscar.clicked.connect(abrir_busca)
        cabecalho_layout.addWidget(buscar)
        central = QPushButton("Central de Questões")
        central.setObjectName("portalInicioBusca")
        central.setCursor(Qt.PointingHandCursor)
        central.clicked.connect(abrir_questoes)
        cabecalho_layout.addWidget(central)
        coluna.addWidget(cabecalho)

    coluna.addSpacing(5)
    coluna.addWidget(_label("Escolha para onde deseja ir", "portalInicioTitulo"))
    # Movimento controlado em Configurações > Aparência.
    coluna.addWidget(_label(
        "Três áreas para organizar sua rotina de estudos.",
        "portalInicioSubtitulo"))

    cards = [
        _criar_cartao(
            "01", "Dashboard", "Seu desempenho em um só lugar.",
            ("Foco e tempo", "Metas e progresso", "Recomendações"),
            "Acessar  →", abrir_dashboard, "dashboard"),
        _criar_cartao(
            "02", "Simulados", "Pratique e avalie sua evolução.",
            ("Simulados", "Baterias", "Treino adaptativo"),
            "Praticar  →", abrir_simulados, "simulados"),
        _criar_cartao(
            "03", "Recursos", "Suas ferramentas de estudo.",
            ("Disciplinas", "Revisões", "Estatísticas"),
            "Explorar  →", abrir_recursos, "recursos"),
    ]
    mini_edital = _criar_mini_cartao_edital(abrir_edital) if abrir_edital else None
    grade = _GradePortalResponsiva(corpo)
    grade.configurar(cards, mini_edital)
    coluna.addWidget(grade, 0)
    coluna.addStretch(1)
    scroll.setWidget(corpo)
    # Sobreposição decorativa acima do cabeçalho compartilhado (sem layout).
    # Não toca em ações do header, GIF, motor de quadros ou controle de movimento.
    cabeca_h10 = None
    if cabecalho_compartilhado is not None:
        cabeca_h10 = _CabecaHolograficaPrimeiroPlano(corpo, faixa_cabecalho)
    grade.observar_viewport(scroll)
    base.addWidget(scroll)
    pagina.portal_perfil_label = perfil
    pagina.portal_edital_minicard = mini_edital
    pagina.portal_grade_responsiva = grade
    pagina.portal_cabeca_holografica = cabeca_h10
    return pagina


def aplicar_estilo_portal(pagina: QWidget, tema: str) -> None:
    # H05: cards glass apenas no Futurista. O estilo preexistente dos temas
    # Claro/Escuro permanece byte a byte no caminho render_qss.
    if tema == "futurista":
        estilo = (render_native_qss(ESTILO_PORTAL_INICIO) + "\n" +
                  ESTILO_H05_CARDS_FUTURISTA + "\n" +
                  ESTILO_H06_EDITAL_FUTURISTA)
    else:
        estilo = render_qss(tema, ESTILO_PORTAL_INICIO)
    pagina.setStyleSheet(estilo)
    for fundo in pagina.findChildren(_FundoPortalInicio):
        fundo.definir_tema(tema)
        QTimer.singleShot(0, fundo._sincronizar_animacao)
    for cabeca_h10 in pagina.findChildren(_CabecaHolograficaPrimeiroPlano):
        cabeca_h10.definir_tema(tema)
    for icone in pagina.findChildren(_IconeModulo):
        icone.definir_tema(tema)
