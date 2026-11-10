"""M32 R2 — Correntes etéreas com advecção visível, sem pulsação global.

A R1 mantinha curvas quase imóveis (deriva de ~2 px num widget pequeno).
Esta revisão desloca continuamente os véus e os destaques ao longo dos caminhos,
com energia de base PERMANENTE e massa luminosa normalizada por corrente.
O QWidget não recebe pintura opaca: cada quadro é RGBA premultiplicado num QLabel.
Somente visual. Não toca banco, combo, mérito, QSettings ou posicionamento.
"""
from __future__ import annotations

import math

from PySide6.QtCore import Qt, QPointF, QElapsedTimer, QTimer
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QLabel


# Filamentos sempre presentes em torno do cristal, livro e base.
# Coordenadas relativas à área segura que a Bateria já calcula para o overlay.
_CANAIS = (
    ((.45, .64), (.08, .88), (.00, .36), (.28, .12)),
    ((.40, .60), (.06, .64), (.12, .28), (.36, .10)),
    ((.42, .57), (.15, .55), (.04, .24), (.42, .09)),
    ((.54, .64), (.91, .89), (1.00, .33), (.74, .12)),
    ((.58, .60), (.95, .68), (.88, .26), (.64, .08)),
    ((.57, .55), (.83, .53), (.98, .24), (.56, .08)),
    ((.43, .66), (.15, .98), (.64, .94), (.83, .59)),
    ((.56, .67), (.90, .98), (.35, .94), (.17, .54)),
)


def _bezier(canal, u):
    v = 1.0 - u
    pesos = (v*v*v, 3*v*v*u, 3*v*u*u, u*u*u)
    return (sum(canal[i][0]*pesos[i] for i in range(4)),
            sum(canal[i][1]*pesos[i] for i in range(4)))


def amostrar_emissao(tempo, canal_indice, quantidade=45):
    """Posições físicas de uma corrente gasosa, continuamente em movimento.

    As extremidades ficam no lugar (envelope nulo nas pontas), enquanto a
    turbulência percorre o comprimento do veio. Amplitude perceptível também
    no tamanho real de ~150-180 px da Bateria, sem escalar o próprio brasão.
    """
    if int(quantidade) < 2:
        raise ValueError("A trilha precisa de ao menos dois pontos")
    canal_indice = int(canal_indice) % len(_CANAIS)
    canal = _CANAIS[canal_indice]
    tempo = float(tempo)
    pts = []
    for i in range(int(quantidade)):
        u = i/(quantidade - 1)
        x, y = _bezier(canal, u)
        envelope = math.sin(math.pi * u)
        # A FASE CAMINHA: de ~0,9 a 1,15 radianos por segundo.
        # Diferença da R1: amplitude local 4 a 8 px, mais deslocamento de luz
        # por advecção (abaixo). Não há modulação de brilho da figura inteira.
        fase = 7.3*u - tempo*(.90 + canal_indice*.032) + canal_indice*1.29
        x += .047 * envelope * math.sin(fase)
        y += .037 * envelope * math.cos(fase*.89 + .31)
        pts.append((x, y, 1.0))
    return pts


def densidades_adveccao(tempo, canal_indice, quantidade=44):
    """Véus mais brilhantes VIAJAM pela corrente sem variação total de energia.

    Duas ondulações de brilho movimentam-se no sentido da emissão; a soma das
    densidades de cada canal é invariável, eliminando o efeito de respiração.
    Retorna um valor por segmento, não por vértice.
    """
    if int(quantidade) < 2:
        raise ValueError("São necessários ao menos dois segmentos")
    n = int(quantidade)
    deslocamento = float(tempo)*(.31 + (int(canal_indice)%8)*.009)
    fase = (int(canal_indice)%8)*.19
    crus = [
        .30 + .70*(.5 + .5*math.cos(2.0*math.pi*(2.0*(i+.5)/n - deslocamento + fase)))
        for i in range(n)
    ]
    media = sum(crus)/n
    return [v/media for v in crus]


class EnergiaEtereaBrasaoM32(QLabel):
    """Overlay QLabel com pixmap RGBA, não QWidget pintado diretamente.

    Compatível com todos os pontos de chamada do M32: definir_ativo,
    definir_intensidade, setGeometry, show, hide, raise_.
    """

    def __init__(self, parent=None, intensidade=52):
        super().__init__(parent)
        self.setObjectName('energiaEtereaBrasaoM32')
        self.setAlignment(Qt.AlignCenter)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self.setFocusPolicy(Qt.NoFocus)
        # Regra específica: não herdar fundos opacos de QLabel do QSS geral.
        self.setStyleSheet(
            'QLabel#energiaEtereaBrasaoM32 { background: transparent; border: none; }'
        )
        self._intensidade = max(0, min(100, int(intensidade)))
        self._ativo = True
        self._tempo = 0.0
        self._cronometro = QElapsedTimer()
        self._cronometro.start()
        self._ultimo_ms = self._cronometro.elapsed()
        self._timer = QTimer(self)
        self._timer.setInterval(50)  # 20 fps; só desenha overlay, sem recálculo de questões
        self._timer.setTimerType(Qt.PreciseTimer)
        self._timer.timeout.connect(self._atualizar)
        self.hide()

    def definir_intensidade(self, valor):
        self._intensidade = max(0, min(100, int(valor)))
        if not self._intensidade:
            self._timer.stop()
            self.clear()
        elif self.isVisible() and self._ativo:
            self._iniciar_timer()
            self._renderizar_quadro()

    def definir_ativo(self, ativo):
        self._ativo = bool(ativo)
        if not self._ativo:
            self._timer.stop()
            self.clear()
            self.hide()
        elif self._intensidade and self.isVisible():
            self._iniciar_timer()
            self._renderizar_quadro()
        # Layout da Bateria decide quando voltar a exibir: sem concessão local.

    def _iniciar_timer(self):
        if not self._cronometro.isValid():
            self._cronometro.start()
        self._ultimo_ms = self._cronometro.elapsed()
        if not self._timer.isActive():
            self._timer.start()

    def _atualizar(self):
        if not self.isVisible() or not self._ativo or not self._intensidade:
            self._timer.stop()
            return
        agora = self._cronometro.elapsed()
        delta_ms = max(0, agora - self._ultimo_ms)
        self._ultimo_ms = agora
        # Se o PC suspender, não saltar a animação de forma brusca.
        self._tempo += min(delta_ms, 250) / 1000.0
        self._renderizar_quadro()

    def _renderizar_quadro(self):
        if not self._ativo or not self._intensidade:
            self.clear()
            return
        largura, altura = self.width(), self.height()
        if largura < 60 or altura < 50:
            self.clear()
            return
        # UMA nova imagem transparente para CADA quadro. Renderizar na QImage
        # evita a limpeza da superfície nativa do QWidget (retângulo preto M32).
        imagem = QImage(largura, altura, QImage.Format_ARGB32_Premultiplied)
        imagem.fill(0)  # Todos os pixels começam com alpha=0 (inclusive cantos).
        pintor = QPainter(imagem)
        try:
            pintor.setRenderHint(QPainter.Antialiasing, True)
            fator = self._intensidade / 100.0
            escala = min(largura, altura) / 145.0
            # Cada corrente possui dois componentes: emanação constante por
            # TODO o caminho e véus luminosos transportados ao longo dele.
            # As densidades são normalizadas para que o TOTAL não pulse.
            for indice in range(len(_CANAIS)):
                pontos = amostrar_emissao(self._tempo, indice)
                trilha = [((x * largura), (y * altura)) for x, y, _ in pontos]
                trajeto = QPainterPath()
                trajeto.moveTo(*trilha[0])
                for xy in trilha[1:]:
                    trajeto.lineTo(*xy)
                for espessura, alpha, cor in (
                    (11.0, 13, (8, 88, 169)),
                    (5.4, 17, (17, 121, 203)),
                ):
                    pen = QPen(QColor(*cor, max(1, round(alpha * fator))))
                    pen.setWidthF(max(.65, espessura * escala))
                    pen.setCapStyle(Qt.RoundCap)
                    pen.setJoinStyle(Qt.RoundJoin)
                    pintor.setPen(pen)
                    pintor.drawPath(trajeto)
                # Luz que flui pela fumaça, não uma alteração de opacidade
                # de toda a figura. Segmentos sucessivos acendem/deslocam-se.
                densidades = densidades_adveccao(self._tempo, indice, len(trilha)-1)
                for j, forca in enumerate(densidades):
                    ax, ay = trilha[j]
                    bx, by = trilha[j+1]
                    for espessura, alpha, cor in (
                        (7.0, 20, (11, 112, 203)),
                        (2.1, 38, (43, 183, 240)),
                    ):
                        tinta = QColor(*cor, max(1, round(alpha * fator * forca)))
                        pen = QPen(tinta)
                        pen.setWidthF(max(.65, espessura * escala))
                        pen.setCapStyle(Qt.RoundCap)
                        pen.setJoinStyle(Qt.RoundJoin)
                        pintor.setPen(pen)
                        pintor.drawLine(QPointF(ax, ay), QPointF(bx, by))
        finally:
            pintor.end()
        # A QLabel renderiza QPixmap alpha sobre o wallpaper, como já faz o
        # brasão M07. Nenhuma pintura direta na superfície de QWidget.
        self.setPixmap(QPixmap.fromImage(imagem))

    def showEvent(self, evento):
        super().showEvent(evento)
        if self._ativo and self._intensidade:
            self._renderizar_quadro()
            self._iniciar_timer()

    def hideEvent(self, evento):
        self._timer.stop()
        super().hideEvent(evento)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        if self.isVisible() and self._ativo and self._intensidade:
            self._renderizar_quadro()

    def closeEvent(self, evento):
        self._timer.stop()
        super().closeEvent(evento)
