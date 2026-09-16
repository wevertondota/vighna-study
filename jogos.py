import random
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
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
