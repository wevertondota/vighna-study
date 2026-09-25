import random
import time
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QPalette
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
)

from banco import registrar_resultado_jogo, obter_recordes_jogos


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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(10)

        titulo = QLabel("Desafio do Chimpanzé")
        titulo.setObjectName("gameTitle")
        layout.addWidget(titulo)

        dica = QLabel(
            "Memorize as posições. Clique no 1; os demais números desaparecem. "
            "Depois continue 2, 3, 4... pelas posições corretas."
        )
        dica.setObjectName("gameHint")
        dica.setWordWrap(True)
        layout.addWidget(dica)

        barra = QHBoxLayout()
        self.nivel_label = QLabel("Nível 4")
        self.nivel_label.setObjectName("gameMetric")
        self.status = QLabel("Clique em Iniciar.")
        self.status.setObjectName("gameStatus")
        self.status.setWordWrap(True)
        barra.addWidget(self.nivel_label)
        barra.addStretch()
        barra.addWidget(self.status, 1)

        self.iniciar_btn = QPushButton("Iniciar")
        self.iniciar_btn.setObjectName("gamePrimaryButton")
        self.iniciar_btn.clicked.connect(self.iniciar_partida)
        barra.addWidget(self.iniciar_btn)
        layout.addLayout(barra)

        grade_container = QFrame()
        grade_container.setObjectName("gameBoardPanel")
        grade = QGridLayout(grade_container)
        grade.setContentsMargins(12, 12, 12, 12)
        grade.setSpacing(7)

        self.botoes = []
        for i in range(25):
            botao = QPushButton("")
            botao.setObjectName("chimpCellButton")
            botao.setMinimumSize(48, 48)
            botao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            botao.clicked.connect(lambda _=False, idx=i: self.clicar(idx))
            botao.setEnabled(False)
            grade.addWidget(botao, i // 5, i % 5)
            self.botoes.append(botao)

        layout.addWidget(grade_container, 1)

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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(10)

        titulo = QLabel("Jogo da Memória")
        titulo.setObjectName("gameTitle")
        layout.addWidget(titulo)

        dica = QLabel(
            "Encontre os oito pares com o menor número de movimentos possível. "
            "As cartas usam letras para manter o jogo leve e rápido."
        )
        dica.setObjectName("gameHint")
        dica.setWordWrap(True)
        layout.addWidget(dica)

        barra = QHBoxLayout()
        self.movimentos_label = QLabel("Movimentos: 0")
        self.movimentos_label.setObjectName("gameMetric")
        self.tempo_label = QLabel("Tempo: 00:00")
        self.tempo_label.setObjectName("gameMetric")
        self.status = QLabel("Nova partida pronta.")
        self.status.setObjectName("gameStatus")
        self.status.setWordWrap(True)
        barra.addWidget(self.movimentos_label)
        barra.addWidget(self.tempo_label)
        barra.addStretch()
        barra.addWidget(self.status, 1)
        novo = QPushButton("Nova partida")
        novo.setObjectName("gamePrimaryButton")
        novo.clicked.connect(self.nova_partida)
        barra.addWidget(novo)
        layout.addLayout(barra)

        painel = QFrame()
        painel.setObjectName("gameBoardPanel")
        grade = QGridLayout(painel)
        grade.setContentsMargins(14, 14, 14, 14)
        grade.setSpacing(9)

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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(10)

        titulo = QLabel("Sequência Visual")
        titulo.setObjectName("gameTitle")
        layout.addWidget(titulo)

        dica = QLabel(
            "Observe os quadrados que acendem e repita a sequência na mesma ordem. "
            "A cada rodada, um novo passo é acrescentado."
        )
        dica.setObjectName("gameHint")
        dica.setWordWrap(True)
        layout.addWidget(dica)

        barra = QHBoxLayout()
        self.nivel_label = QLabel("Sequência: 3")
        self.nivel_label.setObjectName("gameMetric")
        self.status = QLabel("Clique em Iniciar.")
        self.status.setObjectName("gameStatus")
        self.status.setWordWrap(True)
        barra.addWidget(self.nivel_label)
        barra.addStretch()
        barra.addWidget(self.status, 1)
        iniciar = QPushButton("Iniciar")
        iniciar.setObjectName("gamePrimaryButton")
        iniciar.clicked.connect(self.iniciar_partida)
        barra.addWidget(iniciar)
        layout.addLayout(barra)

        painel = QFrame()
        painel.setObjectName("gameBoardPanel")
        grade = QGridLayout(painel)
        grade.setContentsMargins(20, 20, 20, 20)
        grade.setSpacing(12)

        self.botoes = []
        for i in range(9):
            botao = QPushButton("")
            botao.setObjectName("sequenceCellButton")
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
        layout.setContentsMargins(18, 14, 18, 16)
        layout.setSpacing(8)

        self.scroll_area.setWidget(conteudo_scroll)
        raiz.addWidget(self.scroll_area, 1)

        titulo = QLabel("Rotação & Espelho")
        titulo.setObjectName("gameTitle")
        layout.addWidget(titulo)

        dica = QLabel(
            "Transforme mentalmente a forma e escolha o resultado correto. "
            "As alternativas são outras rotações/espelhamentos da mesma figura."
        )
        dica.setObjectName("gameHint")
        dica.setWordWrap(True)
        layout.addWidget(dica)

        barra = QHBoxLayout()
        barra.setSpacing(12)
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
        layout.addLayout(barra)

        painel = QFrame()
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
        original_rotulo.setObjectName("pauseRecordTitle")
        original_rotulo.setAlignment(Qt.AlignCenter)
        self.preview_original = _FormaMatrizWidget(parent=painel)
        self.preview_original.setMinimumSize(180, 96)
        self.preview_original.setMaximumHeight(116)
        self.preview_original.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        original_bloco.addWidget(original_rotulo)
        original_bloco.addWidget(self.preview_original, 1)

        self.pergunta = QLabel("A transformação aparecerá aqui.")
        self.pergunta.setObjectName("gameStatus")
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(10)

        titulo = QLabel("Quebra-cabeça 8 Peças")
        titulo.setObjectName("gameTitle")
        layout.addWidget(titulo)

        dica = QLabel(
            "Organize os números de 1 a 8. Clique em uma peça vizinha ao espaço vazio para movê-la. "
            "Toda nova partida é embaralhada por movimentos válidos, portanto sempre há solução."
        )
        dica.setObjectName("gameHint")
        dica.setWordWrap(True)
        layout.addWidget(dica)

        barra = QHBoxLayout()
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
        layout.addLayout(barra)

        painel = QFrame()
        painel.setObjectName("gameBoardPanel")
        grade = QGridLayout(painel)
        grade.setContentsMargins(22, 22, 22, 22)
        grade.setSpacing(10)

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


class JanelaPausaDesafios(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Pausa & Desafios — VighnaStudy")
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)

        cabecalho = QHBoxLayout()
        textos = QVBoxLayout()
        titulo = QLabel("Pausa & Desafios")
        titulo.setObjectName("pauseHubTitle")
        subtitulo = QLabel(
            "Jogos curtos para momentos de pausa. Os recordes ficam separados das métricas de estudo."
        )
        subtitulo.setObjectName("pauseHubSubtitle")
        subtitulo.setWordWrap(True)
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)
        cabecalho.addLayout(textos, 1)

        voltar = QPushButton("Voltar aos estudos")
        voltar.setObjectName("pauseBackButton")
        voltar.clicked.connect(self.accept)
        cabecalho.addWidget(voltar, 0, Qt.AlignTop)
        layout.addLayout(cabecalho)

        painel_pausa = QFrame()
        painel_pausa.setObjectName("pauseTimerPanel")
        pausa_layout = QHBoxLayout(painel_pausa)
        pausa_layout.setContentsMargins(14, 10, 14, 10)
        pausa_layout.setSpacing(10)

        pausa_titulo = QLabel("Pausa rápida")
        pausa_titulo.setObjectName("pauseSectionTitle")
        pausa_layout.addWidget(pausa_titulo)

        self.minutos = QSpinBox()
        self.minutos.setRange(1, 60)
        self.minutos.setValue(5)
        self.minutos.setSuffix(" min")
        self.minutos.setFixedWidth(92)
        pausa_layout.addWidget(self.minutos)

        self.iniciar_pausa_btn = QPushButton("Iniciar pausa")
        self.iniciar_pausa_btn.setObjectName("pausePrimaryButton")
        self.iniciar_pausa_btn.clicked.connect(self.iniciar_pausa)
        pausa_layout.addWidget(self.iniciar_pausa_btn)

        self.parar_pausa_btn = QPushButton("Encerrar")
        self.parar_pausa_btn.setObjectName("pauseSecondaryButton")
        self.parar_pausa_btn.clicked.connect(self.encerrar_pausa)
        self.parar_pausa_btn.setEnabled(False)
        pausa_layout.addWidget(self.parar_pausa_btn)

        pausa_layout.addStretch()
        self.pausa_status = QLabel("Defina um tempo se quiser usar o cronômetro.")
        self.pausa_status.setObjectName("pauseTimerStatus")
        self.pausa_status.setWordWrap(True)
        pausa_layout.addWidget(self.pausa_status, 1)

        self.pausa_tempo = QLabel("05:00")
        self.pausa_tempo.setObjectName("pauseTimerValue")
        self.pausa_tempo.setAlignment(Qt.AlignCenter)
        pausa_layout.addWidget(self.pausa_tempo)
        layout.addWidget(painel_pausa)

        recordes = QFrame()
        recordes.setObjectName("pauseRecordsPanel")
        rec_layout = QGridLayout(recordes)
        rec_layout.setContentsMargins(14, 10, 14, 10)
        rec_layout.setHorizontalSpacing(18)
        rec_layout.setVerticalSpacing(4)

        rec_titulo = QLabel("Recordes pessoais")
        rec_titulo.setObjectName("pauseSectionTitle")
        rec_layout.addWidget(rec_titulo, 0, 0, 1, 4)

        self.recorde_labels = {}
        nomes = [
            ("chimpanze", "Chimpanzé"),
            ("memoria", "Memória"),
            ("sequencia", "Sequência visual"),
            ("rotacao_visual", "Rotação visual"),
            ("quebra_cabeca", "Quebra-cabeça"),
        ]
        for coluna, (chave, nome) in enumerate(nomes):
            caixa = QFrame()
            caixa.setObjectName("pauseRecordCard")
            caixa_layout = QVBoxLayout(caixa)
            caixa_layout.setContentsMargins(10, 7, 10, 7)
            caixa_layout.setSpacing(2)
            rotulo = QLabel(nome)
            rotulo.setObjectName("pauseRecordTitle")
            valor = QLabel("Sem recorde")
            valor.setObjectName("pauseRecordValue")
            valor.setWordWrap(True)
            caixa_layout.addWidget(rotulo)
            caixa_layout.addWidget(valor)
            rec_layout.addWidget(caixa, 1, coluna)
            self.recorde_labels[chave] = valor

        layout.addWidget(recordes)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("pauseGamesTabs")
        self.tabs.addTab(JogoChimpanze(self.atualizar_recordes, self), "Chimpanzé")
        self.tabs.addTab(JogoMemoria(self.atualizar_recordes, self), "Memória")
        self.tabs.addTab(JogoSequenciaVisual(self.atualizar_recordes, self), "Sequência visual")
        self.tabs.addTab(JogoRotacaoVisual(self.atualizar_recordes, self), "Rotação visual")
        self.tabs.addTab(JogoQuebraCabeca(self.atualizar_recordes, self), "Quebra-cabeça")
        layout.addWidget(self.tabs, 1)

        self.minutos.valueChanged.connect(self.atualizar_preview_tempo)
        self.atualizar_preview_tempo()
        self.atualizar_recordes()

    def atualizar_preview_tempo(self):
        if self.timer_pausa.isActive():
            return
        self.pausa_tempo.setText(_formatar_tempo(self.minutos.value() * 60))

    def iniciar_pausa(self):
        self.tempo_restante = self.minutos.value() * 60
        self.pausa_tempo.setText(_formatar_tempo(self.tempo_restante))
        self.pausa_status.setText("Pausa em andamento. O cronômetro não bloqueia os jogos.")
        self.minutos.setEnabled(False)
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
        self.pausa_status.setText(
            "Tempo sugerido encerrado. Você pode terminar a partida atual ou voltar aos estudos."
        )
        self.minutos.setEnabled(True)
        self.iniciar_pausa_btn.setEnabled(True)
        self.parar_pausa_btn.setEnabled(False)

    def encerrar_pausa(self):
        self.timer_pausa.stop()
        self.tempo_restante = 0
        self.pausa_status.setText("Pausa encerrada.")
        self.minutos.setEnabled(True)
        self.iniciar_pausa_btn.setEnabled(True)
        self.parar_pausa_btn.setEnabled(False)
        self.atualizar_preview_tempo()

    def atualizar_recordes(self):
        try:
            dados = obter_recordes_jogos()
        except Exception:
            dados = {}

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

    def closeEvent(self, evento):
        self.timer_pausa.stop()
        evento.accept()
