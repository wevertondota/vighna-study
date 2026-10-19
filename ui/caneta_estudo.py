"""Caneta de Estudo: traços temporários em superfícies de anotação locais.

Os desenhos existem apenas em RAM. Cada superfície é filha do texto do
 enunciado ou do cartão de uma alternativa. Não existe uma camada de tela inteira
que capture o botão Rabiscar, a navegação ou outras ações do resolvedor.
"""

from dataclasses import dataclass, field
from math import hypot

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


@dataclass(eq=False)
class TracoTemporario:
    ancora: str
    pontos: list = field(default_factory=list)
    cor: str = "#F2C94C"
    espessura: int = 3
    marcador: bool = False


def distancia_ao_segmento(ponto, inicio, fim):
    px, py = ponto
    x0, y0 = inicio
    x1, y1 = fim
    dx, dy = x1 - x0, y1 - y0
    divisor = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((px-x0)*dx+(py-y0)*dy)/divisor)) if divisor else 0.0
    return hypot(px - (x0 + t*dx), py - (y0 + t*dy))


class _SuperficieRabisco(QWidget):
    """Filha apenas da área rabiscável; nunca intercepta o botão de caneta."""

    def __init__(self, controlador, chave, ancora):
        super().__init__(ancora)
        self.controlador = controlador
        self.chave = chave
        self.ancora = ancora
        self.setObjectName("questionStudyInkLocalCanvas")
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)
        self.setFocusPolicy(Qt.NoFocus)
        ancora.installEventFilter(self)
        self.sincronizar()
        self.show()
        self.raise_()

    def sincronizar(self):
        if self.geometry() != self.ancora.rect():
            self.setGeometry(self.ancora.rect())
        self.raise_()
        self.update()

    def aplicar_modo(self, modo):
        self.setAttribute(Qt.WA_TransparentForMouseEvents, modo is None)
        self.setCursor(Qt.CrossCursor if modo in ("caneta", "marcador") else
                       Qt.PointingHandCursor if modo == "borracha" else Qt.ArrowCursor)
        self.sincronizar()

    def eventFilter(self, objeto, evento):
        if objeto is self.ancora and evento.type() in (QEvent.Resize, QEvent.Show):
            self.sincronizar()
        return super().eventFilter(objeto, evento)

    def mousePressEvent(self, evento):
        if evento.button() == Qt.LeftButton and self.controlador._pressionar(
            self.chave, evento.position().toPoint()
        ):
            evento.accept()
        else:
            evento.ignore()

    def mouseMoveEvent(self, evento):
        if self.controlador._mover(self.chave, evento.position().toPoint(), evento.buttons()):
            evento.accept()
        else:
            evento.ignore()

    def mouseReleaseEvent(self, evento):
        if self.controlador._soltar(self.chave, evento.button()):
            evento.accept()
        else:
            evento.ignore()

    def paintEvent(self, evento):
        self.controlador._pintar(self)


class CanetaEstudo:
    """Controla superfícies locais, sem camada global e sem gravação em disco."""

    _MODOS = (None, "caneta", "marcador", "borracha")
    _MAX_PONTOS = 1800
    _MAX_TRACOS = 400

    def __init__(self, area_rolagem, enunciado, obter_alternativas):
        self.area = area_rolagem
        self.enunciado = enunciado
        self.obter_alternativas = obter_alternativas
        self.modo = None
        self.cor = "#F2C94C"
        self.espessura = 3
        self.tracos = []
        self.historico = []
        self._superficies = {}
        self._atual = None
        self._arrastando = False
        self.ao_alterar = None  # Notificação visual opcional, nunca persiste dados.
        self.atualizar_alvos()

    def _ancoras(self):
        return {"enunciado": self.enunciado, **self.obter_alternativas()}

    def atualizar_alvos(self):
        """Recria apenas as superfícies cujos cartões mudaram de identidade."""
        ancoras = self._ancoras()
        for chave, superficie in list(self._superficies.items()):
            if ancoras.get(chave) is not superficie.ancora:
                superficie.ancora.removeEventFilter(superficie)
                superficie.hide()
                superficie.deleteLater()
                del self._superficies[chave]
        for chave, widget in ancoras.items():
            if widget is None:
                continue
            superficie = self._superficies.get(chave)
            if superficie is None:
                superficie = _SuperficieRabisco(self, chave, widget)
                self._superficies[chave] = superficie
            superficie.aplicar_modo(self.modo)

    def definir_modo(self, modo):
        if modo not in self._MODOS:
            raise ValueError("Ferramenta de desenho inválida")
        self.modo = modo
        self._atual = None
        self._arrastando = False
        self.atualizar_alvos()

    def definir_cor(self, cor):
        if cor not in ("#F2C94C", "#E64848", "#4096E8", "#32B987"):
            raise ValueError("Cor de caneta inválida")
        self.cor = cor

    def definir_espessura(self, espessura):
        if espessura not in (2, 3, 6):
            raise ValueError("Espessura inválida")
        self.espessura = espessura

    def _avisar_interface(self):
        if callable(self.ao_alterar):
            self.ao_alterar()

    def _repaint(self, chave=None):
        if chave is not None:
            superficie = self._superficies.get(chave)
            if superficie is not None:
                superficie.update()
        else:
            for superficie in self._superficies.values():
                superficie.update()

    def limpar(self):
        """Cada nova questão começa sem marcas, histórico ou gesto ativo."""
        self._atual = None
        self._arrastando = False
        self.tracos.clear()
        self.historico.clear()
        self._repaint()
        self._avisar_interface()

    def limpar_marcacoes(self):
        if self.tracos:
            self._guardar_historico(("limpar", list(self.tracos)))
            self.tracos.clear()
            self._repaint()
            self._avisar_interface()

    def _guardar_historico(self, registro):
        self.historico.append(registro)
        if len(self.historico) > 120:
            del self.historico[0]
        self._avisar_interface()

    def desfazer(self):
        if not self.historico:
            return False
        tipo, *payload = self.historico.pop()
        if tipo == "adicionar":
            traco = payload[0]
            if traco in self.tracos:
                self.tracos.remove(traco)
        elif tipo == "remover":
            indice, traco = payload
            self.tracos.insert(min(indice, len(self.tracos)), traco)
        elif tipo == "limpar":
            self.tracos[:] = payload[0]
        self._repaint()
        self._avisar_interface()
        return True

    def _apagar_proximo(self, chave, pos):
        alvo = (pos.x(), pos.y())
        melhor = None
        for indice, traco in enumerate(self.tracos):
            if traco.ancora != chave or not traco.pontos:
                continue
            raio = 15 + traco.espessura / 2
            if not (min(x for x, _ in traco.pontos)-raio <= alvo[0] <=
                    max(x for x, _ in traco.pontos)+raio and
                    min(y for _, y in traco.pontos)-raio <= alvo[1] <=
                    max(y for _, y in traco.pontos)+raio):
                continue
            segmentos = zip(traco.pontos, traco.pontos[1:])
            distancia = min((distancia_ao_segmento(alvo, p0, p1) for p0,p1 in segmentos),
                            default=float("inf"))
            if len(traco.pontos) == 1:
                distancia = distancia_ao_segmento(alvo, traco.pontos[0], traco.pontos[0])
            if distancia <= raio and (melhor is None or distancia < melhor[0]):
                melhor = (distancia, indice, traco)
        if melhor is not None:
            _, indice, traco = melhor
            self.tracos.pop(indice)
            self._guardar_historico(("remover", indice, traco))
            self._repaint(chave)

    def _pressionar(self, chave, pos):
        if self.modo is None or chave not in self._superficies:
            return False
        if self.modo == "borracha":
            self._arrastando = True
            self._apagar_proximo(chave, pos)
            return True
        if len(self.tracos) >= self._MAX_TRACOS:
            return True
        self._arrastando = True
        traco = TracoTemporario(
            ancora=chave, pontos=[(float(pos.x()), float(pos.y()))],
            cor=self.cor,
            espessura=self.espessura*5 if self.modo == "marcador" else self.espessura,
            marcador=self.modo == "marcador",
        )
        self.tracos.append(traco)
        self._atual = traco
        self._repaint(chave)
        return True

    def _mover(self, chave, pos, botoes):
        if not self._arrastando or not (botoes & Qt.LeftButton):
            return False
        if self.modo == "borracha":
            self._apagar_proximo(chave, pos)
        elif self._atual is not None and self._atual.ancora == chave:
            if len(self._atual.pontos) < self._MAX_PONTOS:
                novo = (float(pos.x()), float(pos.y()))
                if hypot(novo[0]-self._atual.pontos[-1][0],
                         novo[1]-self._atual.pontos[-1][1]) >= 1.5:
                    self._atual.pontos.append(novo)
                    self._repaint(chave)
        return True

    def _soltar(self, chave, botao):
        if not self._arrastando or botao != Qt.LeftButton:
            return False
        if self._atual is not None:
            self._guardar_historico(("adicionar", self._atual))
        self._atual = None
        self._arrastando = False
        return True

    def _pintar(self, superficie):
        tracos = [t for t in self.tracos if t.ancora == superficie.chave and t.pontos]
        if not tracos:
            return
        painter = QPainter(superficie)
        painter.setRenderHint(QPainter.Antialiasing, True)
        for traco in tracos:
            cor = QColor(traco.cor)
            if traco.marcador:
                cor.setAlpha(75)
            painter.setPen(QPen(cor, traco.espessura, Qt.SolidLine,
                                Qt.RoundCap, Qt.RoundJoin))
            if len(traco.pontos) == 1:
                x, y = traco.pontos[0]
                painter.drawPoint(QPoint(round(x), round(y)))
            else:
                path = QPainterPath()
                path.moveTo(*traco.pontos[0])
                for x, y in traco.pontos[1:]:
                    path.lineTo(x, y)
                painter.drawPath(path)
        painter.end()
