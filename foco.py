import time
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QLineEdit,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QWidget,
    QScrollArea,
    QSizePolicy,
    QApplication,
)

from banco import (
    listar_disciplinas,
    listar_topicos,
    registrar_sessao_foco,
    listar_sessoes_foco,
    obter_resumo_foco,
    tipos_atividade_foco,
    registrar_vinculo_foco_questoes,
    obter_resultado_foco_questoes,
)
from jogos import JanelaPausaDesafios


def _tempo_curto(segundos):
    segundos = max(0, int(segundos or 0))
    horas, resto = divmod(segundos, 3600)
    minutos = resto // 60
    if horas:
        return f"{horas}h {minutos:02d}min"
    return f"{minutos} min"


def _tempo_pos_foco(segundos):
    segundos = max(0, int(round(segundos or 0)))
    if 0 < segundos < 60:
        return f"{segundos}s"
    return _tempo_curto(segundos)


FOCO_MIN_MINUTOS = 1
FOCO_MAX_MINUTOS = 24 * 60


def _normalizar_duracao_foco_minutos(minutos):
    try:
        minutos = int(minutos)
    except (TypeError, ValueError):
        minutos = 50
    return max(FOCO_MIN_MINUTOS, min(FOCO_MAX_MINUTOS, minutos))


def _decompor_duracao_foco(minutos):
    total = _normalizar_duracao_foco_minutos(minutos)
    return divmod(total, 60)


def _relogio(segundos):
    segundos = max(0, int(round(segundos or 0)))
    horas, resto = divmod(segundos, 3600)
    minutos, segundos = divmod(resto, 60)
    if horas:
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    return f"{minutos:02d}:{segundos:02d}"


def trazer_janela_foco_para_frente(janela):
    """Mostra, restaura e ativa a mesma janela de Foco, se ela existir."""
    if janela is None:
        return None
    if janela.isMinimized():
        janela.showNormal()
    elif not janela.isVisible():
        janela.show()
    janela.raise_()
    janela.activateWindow()
    return janela


class JanelaPosFoco(QDialog):
    """Pós-Foco V2: tempo, resultado acadêmico e próximo passo no mesmo ciclo."""

    def __init__(self, dados, parent=None):
        super().__init__(parent)
        self.dados = dict(dados or {})
        self.acao_escolhida = "continuar"
        self.setWindowTitle("Sessão finalizada — VighnaStudy")
        self.setMinimumWidth(560)
        self.resize(620, 430)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(22, 20, 22, 20)
        raiz.setSpacing(14)

        topo = QFrame()
        topo.setObjectName("postFocusHero")
        topo_layout = QVBoxLayout(topo)
        topo_layout.setContentsMargins(18, 16, 18, 16)
        topo_layout.setSpacing(5)

        eyebrow = QLabel("SESSÃO REGISTRADA")
        eyebrow.setObjectName("postFocusEyebrow")
        topo_layout.addWidget(eyebrow)

        tempo = QLabel(_tempo_pos_foco(self.dados.get("duracao_efetiva", 0)))
        tempo.setObjectName("postFocusTime")
        topo_layout.addWidget(tempo)

        estado = "Concluída" if self.dados.get("concluida") else "Interrompida"
        atividade = str(self.dados.get("tipo_atividade") or "Estudo livre")
        linha = QLabel(f"{atividade} • {estado}")
        linha.setObjectName("postFocusStatus")
        topo_layout.addWidget(linha)
        raiz.addWidget(topo)

        conteudo_card = QFrame()
        conteudo_card.setObjectName("postFocusContentCard")
        conteudo_layout = QVBoxLayout(conteudo_card)
        conteudo_layout.setContentsMargins(16, 14, 16, 14)
        conteudo_layout.setSpacing(5)

        disciplina = str(self.dados.get("disciplina") or "Livre / sem vínculo")
        topico = str(self.dados.get("topico") or "").strip()
        conteudo = disciplina if not topico else f"{disciplina} › {topico}"

        rotulo = QLabel("CONTEÚDO TRABALHADO")
        rotulo.setObjectName("postFocusEyebrow")
        conteudo_layout.addWidget(rotulo)
        titulo = QLabel(conteudo)
        titulo.setObjectName("postFocusContentTitle")
        titulo.setWordWrap(True)
        conteudo_layout.addWidget(titulo)

        planejado = int(self.dados.get("duracao_planejada") or 0)
        efetivo = int(self.dados.get("duracao_efetiva") or 0)
        diferenca = efetivo - planejado
        if planejado > 0:
            if abs(diferenca) < 60:
                detalhe_tempo = f"Planejado: {_tempo_curto(planejado)} • tempo efetivo dentro do planejado"
            elif diferenca > 0:
                detalhe_tempo = f"Planejado: {_tempo_curto(planejado)} • +{_tempo_curto(diferenca)} além do previsto"
            else:
                detalhe_tempo = f"Planejado: {_tempo_curto(planejado)} • {_tempo_curto(abs(diferenca))} abaixo do previsto"
        else:
            detalhe_tempo = "O Ritmo de estudo foi atualizado com o tempo efetivamente medido."
        detalhe = QLabel(detalhe_tempo)
        detalhe.setObjectName("postFocusDetail")
        detalhe.setWordWrap(True)
        conteudo_layout.addWidget(detalhe)
        raiz.addWidget(conteudo_card)

        resultado_questoes = self.dados.get("resultado_questoes") or {}
        if resultado_questoes and int(resultado_questoes.get("respondidas") or 0) > 0:
            resultado_card = QFrame()
            resultado_card.setObjectName("postFocusResultCard")
            resultado_layout = QVBoxLayout(resultado_card)
            resultado_layout.setContentsMargins(16, 13, 16, 13)
            resultado_layout.setSpacing(5)

            resultado_rotulo = QLabel("RESULTADO DA SESSÃO")
            resultado_rotulo.setObjectName("postFocusEyebrow")
            resultado_layout.addWidget(resultado_rotulo)

            respondidas = int(resultado_questoes.get("respondidas") or 0)
            acertos = int(resultado_questoes.get("acertos") or 0)
            desempenho = resultado_questoes.get("desempenho")
            desempenho_txt = (
                f"{float(desempenho):.0f}%"
                if desempenho is not None else "—"
            )
            resultado_titulo = QLabel(
                f"{acertos}/{respondidas} acertos • {desempenho_txt}"
            )
            resultado_titulo.setObjectName("postFocusResultValue")
            resultado_layout.addWidget(resultado_titulo)

            detalhes_resultado = []
            delta = resultado_questoes.get("delta_dominio")
            antes = resultado_questoes.get("dominio_antes")
            depois = resultado_questoes.get("dominio_depois")
            if antes is not None and depois is not None:
                sinal = "+" if float(delta or 0) >= 0 else ""
                detalhes_resultado.append(
                    f"Domínio: {float(antes):.0f} → {float(depois):.0f} ({sinal}{float(delta or 0):.1f})"
                )
            proxima = str(resultado_questoes.get("proxima_revisao") or "").strip()
            if proxima:
                try:
                    proxima_txt = datetime.strptime(proxima[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
                except Exception:
                    proxima_txt = proxima
                detalhes_resultado.append(f"Próxima revisão: {proxima_txt}")
            if detalhes_resultado:
                resultado_detalhe = QLabel(" • ".join(detalhes_resultado))
                resultado_detalhe.setObjectName("postFocusDetail")
                resultado_detalhe.setWordWrap(True)
                resultado_layout.addWidget(resultado_detalhe)

            raiz.addWidget(resultado_card)

        pergunta = QLabel("Qual é o próximo passo?")
        pergunta.setObjectName("postFocusQuestion")
        raiz.addWidget(pergunta)

        acoes_principais = QHBoxLayout()
        acoes_principais.setSpacing(10)

        ja_respondeu = bool(
            (self.dados.get("resultado_questoes") or {}).get("respondidas")
        )
        self.btn_questoes = QPushButton(
            "Resolver mais questões" if ja_respondeu else "Resolver questões"
        )
        self.btn_questoes.setObjectName("postFocusPrimary")
        self.btn_questoes.setMinimumHeight(42)
        self.btn_questoes.clicked.connect(lambda: self._escolher("questoes"))
        acoes_principais.addWidget(self.btn_questoes, 1)

        self.btn_revisao = QPushButton("Registrar revisão")
        self.btn_revisao.setObjectName("postFocusSecondary")
        self.btn_revisao.setMinimumHeight(42)
        self.btn_revisao.clicked.connect(lambda: self._escolher("revisao"))
        acoes_principais.addWidget(self.btn_revisao, 1)

        raiz.addLayout(acoes_principais)

        if not self.dados.get("topico_id"):
            self.btn_revisao.setEnabled(False)
            self.btn_revisao.setToolTip(
                "Vincule a sessão a um tópico para registrar uma revisão diretamente daqui."
            )

        # Questões podem ser abertas filtradas por disciplina e, quando houver,
        # por tópico. Sem vínculo, o Banco de Questões ainda pode ser aberto,
        # mas não há filtro contextual para aplicar.
        if not self.dados.get("disciplina_id") and not self.dados.get("disciplina"):
            self.btn_questoes.setText("Abrir Banco de Questões")

        rodape = QHBoxLayout()
        rodape.setSpacing(10)

        em_jornada = str(self.dados.get("origem") or "") == "Jornada do Dia"
        if em_jornada:
            proxima = QPushButton("▶ Iniciar próxima")
            proxima.setObjectName("postFocusContinue")
            proxima.clicked.connect(lambda: self._escolher("jornada_proxima"))
            rodape.addWidget(proxima)

            recalcular = QPushButton("Recalcular restante")
            recalcular.setObjectName("postFocusGhost")
            recalcular.clicked.connect(lambda: self._escolher("jornada_recalcular"))
            rodape.addWidget(recalcular)

            pausar_jornada = QPushButton("Pausar jornada")
            pausar_jornada.setObjectName("postFocusGhost")
            pausar_jornada.clicked.connect(lambda: self._escolher("jornada_pausar"))
            rodape.addWidget(pausar_jornada)
        else:
            recomendar = QPushButton("Continuar estudando")
            recomendar.setObjectName("postFocusContinue")
            recomendar.clicked.connect(lambda: self._escolher("recomendar"))
            rodape.addWidget(recomendar)

            outra = QPushButton("Preparar outra sessão")
            outra.setObjectName("postFocusGhost")
            outra.clicked.connect(lambda: self._escolher("continuar"))
            rodape.addWidget(outra)

        rodape.addStretch(1)

        encerrar = QPushButton("Encerrar por hoje")
        encerrar.setObjectName("postFocusGhost")
        encerrar.clicked.connect(
            lambda: self._escolher("jornada_encerrar" if em_jornada else "encerrar")
        )
        rodape.addWidget(encerrar)
        raiz.addLayout(rodape)

        nota = QLabel(
            "O tempo já foi registrado no Ritmo de estudo. Revisões e questões só serão alteradas se você escolher uma ação acima."
        )
        nota.setObjectName("postFocusNote")
        nota.setWordWrap(True)
        raiz.addWidget(nota)

    def _escolher(self, acao):
        self.acao_escolhida = str(acao or "continuar")
        self.accept()


class JanelaModoFoco(QDialog):
    resumo_alterado = Signal()
    estado_alterado = Signal()
    acao_pos_foco = Signal(str, object)
    solicitar_questoes = Signal(object)
    sessao_finalizada = Signal(object)

    def __init__(self, parent=None):
        # O argumento é mantido por compatibilidade com integrações antigas,
        # mas não é usado como parent Qt. O cronômetro precisa ser uma janela
        # top-level real, independente da principal, do tópico e do resolvedor.
        super().__init__(None)
        self.controlador = parent
        self.setWindowTitle("Modo Foco — VighnaStudy")
        # O Foco precisa funcionar também em telas de 768 px de altura e
        # com escala do Windows acima de 100%. O tamanho inicial é calculado
        # a partir da área útil do monitor (descontando barra de tarefas).
        self.setMinimumSize(760, 500)
        self._ajustar_tamanho_ao_monitor()
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowTitleHint
            | Qt.WindowSystemMenuHint
            | Qt.WindowMinMaxButtonsHint
            | Qt.WindowCloseButtonHint
        )
        # Janela deliberadamente não modal: o cronômetro deve continuar
        # ativo enquanto o usuário navega por Questões, Revisões, Simulados
        # e pelo restante do VighnaStudy.
        self.setModal(False)
        self.setWindowModality(Qt.NonModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.sessao_ativa = False
        self.pausada = False
        self.inicio_datetime = None
        self.inicio_segmento = None
        self.acumulado = 0.0
        self.duracao_planejada = 50 * 60
        self.expiracao_aberta = False
        self.meta_questoes_preparada = 0
        self.origem_preparacao = None
        self.origem_sessao_preparacao = None
        self.plano_chave_preparacao = None
        self.abrir_questoes_ao_iniciar = False
        self.contexto_questoes_preparado = None
        self.resultados_questoes = []
        self.questoes_disparadas = False

        self.timer = QTimer(self)
        self.timer.setInterval(250)
        self.timer.timeout.connect(self.atualizar_timer)

        self.atalho_pausa = QShortcut(QKeySequence("F8"), self)
        self.atalho_pausa.setContext(Qt.WindowShortcut)
        self.atalho_pausa.activated.connect(self.alternar_pausa)

        self.atalho_trazer = QShortcut(QKeySequence("Ctrl+Shift+F"), self)
        self.atalho_trazer.setContext(Qt.WindowShortcut)
        self.atalho_trazer.activated.connect(
            lambda: trazer_janela_foco_para_frente(self)
        )

        self.montar_interface()
        self.carregar_disciplinas()
        self.atualizar_campos_opcionais(False)
        self.atualizar_resumo()
        self.carregar_historico()

    def _ajustar_tamanho_ao_monitor(self):
        tela = self.screen()
        if tela is None:
            app = QApplication.instance()
            tela = app.primaryScreen() if app is not None else None

        if tela is None:
            self.resize(1000, 680)
            return

        area = tela.availableGeometry()
        largura = min(1120, max(760, int(area.width() * 0.90)))
        altura = min(760, max(500, int(area.height() * 0.88)))
        self.resize(largura, altura)

    def montar_interface(self):
        # A rolagem externa é uma proteção para monitores mais baixos,
        # notebooks com escala elevada e janelas redimensionadas. Nenhum
        # bloco do cronômetro fica inacessível quando falta altura vertical.
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("focusScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("focusScrollContent")
        self.scroll_content.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred,
        )
        self.scroll_area.setWidget(self.scroll_content)
        raiz.addWidget(self.scroll_area)

        layout = QVBoxLayout(self.scroll_content)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)

        cabecalho = QHBoxLayout()
        textos = QVBoxLayout()
        titulo = QLabel("Modo Foco")
        titulo.setObjectName("focusTitle")
        subtitulo = QLabel(
            "Cronometre o tempo realmente dedicado ao estudo. Pausas não entram na duração efetiva."
        )
        subtitulo.setObjectName("focusSubtitle")
        subtitulo.setWordWrap(True)
        dica = QLabel(
            "Você pode deixar esta janela aberta: o cronômetro continua enquanto usa o restante do Vighna."
        )
        dica.setObjectName("focusWindowHint")
        dica.setWordWrap(True)
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)
        textos.addWidget(dica)
        cabecalho.addLayout(textos, 1)

        pausa = QPushButton("Pausa & Desafios")
        pausa.setObjectName("focusPauseButton")
        pausa.clicked.connect(self.abrir_pausa)
        cabecalho.addWidget(pausa, 0, Qt.AlignTop)
        layout.addLayout(cabecalho)

        # Resumo real de tempo.
        stats = QFrame()
        stats.setObjectName("focusStatsPanel")
        stats.setMinimumHeight(74)
        stats_layout = QGridLayout(stats)
        stats_layout.setContentsMargins(14, 10, 14, 10)
        stats_layout.setHorizontalSpacing(24)
        self.stat_hoje = self._criar_stat(stats_layout, 0, "Hoje")
        self.stat_semana = self._criar_stat(stats_layout, 1, "Esta semana")
        self.stat_sessoes = self._criar_stat(stats_layout, 2, "Sessões na semana")
        self.stat_media = self._criar_stat(stats_layout, 3, "Média por sessão")
        layout.addWidget(stats)

        # Configuração.
        self.config_panel = QFrame()
        self.config_panel.setObjectName("focusConfigPanel")
        self.config_panel.setMinimumHeight(205)
        config = QVBoxLayout(self.config_panel)
        config.setContentsMargins(16, 14, 16, 14)
        config.setSpacing(10)

        sec = QLabel("Preparar sessão")
        sec.setObjectName("focusSectionTitle")
        config.addWidget(sec)

        presets = QHBoxLayout()
        presets.setSpacing(10)
        duracao_label = QLabel("Duração")
        duracao_label.setMinimumWidth(56)
        presets.addWidget(duracao_label)
        for minutos in (25, 50, 90):
            botao = QPushButton(f"{minutos} min")
            botao.setObjectName("focusPresetButton")
            botao.setMinimumSize(72, 34)
            botao.clicked.connect(lambda _=False, m=minutos: self.definir_minutos(m))
            presets.addWidget(botao)
        personalizado = QLabel("Personalizado")
        personalizado.setMinimumWidth(86)
        presets.addWidget(personalizado)

        # A duração personalizada usa horas + minutos para manter a leitura
        # natural mesmo em sessões longas. Internamente tudo continua sendo
        # convertido para minutos/segundos, preservando o restante do fluxo.
        self.horas = QSpinBox()
        self.horas.setRange(0, 24)
        self.horas.setValue(0)
        self.horas.setSuffix(" h")
        self.horas.setFixedSize(82, 34)
        self.horas.setToolTip("Horas da sessão de foco (máximo total: 24 horas)")
        presets.addWidget(self.horas)

        self.minutos = QSpinBox()
        self.minutos.setRange(1, 59)
        self.minutos.setValue(50)
        self.minutos.setSuffix(" min")
        self.minutos.setFixedSize(94, 34)
        self.minutos.setToolTip("Minutos adicionais da sessão de foco")
        presets.addWidget(self.minutos)

        self.horas.valueChanged.connect(self._ajustar_campos_duracao)
        self._ajustar_campos_duracao(self.horas.value())

        presets.addStretch(1)
        config.addLayout(presets)

        self.iniciar_btn = QPushButton("Iniciar foco")
        self.iniciar_btn.setObjectName("focusPrimaryButton")
        self.iniciar_btn.setMinimumSize(220, 46)
        self.iniciar_btn.clicked.connect(self.iniciar)

        acao_layout = QHBoxLayout()
        acao_layout.setContentsMargins(0, 4, 0, 0)
        acao_layout.addStretch(1)
        acao_layout.addWidget(self.iniciar_btn, 0, Qt.AlignCenter)
        acao_layout.addStretch(1)
        config.addLayout(acao_layout)

        self.campos_opcionais_box = QFrame()
        self.campos_opcionais_box.setObjectName("focusOptionalPanel")
        opt_box_layout = QVBoxLayout(self.campos_opcionais_box)
        opt_box_layout.setContentsMargins(12, 10, 12, 10)
        opt_box_layout.setSpacing(8)

        topo_opcional = QHBoxLayout()
        topo_opcional.setSpacing(8)
        self.usar_detalhes = QCheckBox("Quero especificar o que vou estudar (opcional)")
        self.usar_detalhes.toggled.connect(self.atualizar_campos_opcionais)
        topo_opcional.addWidget(self.usar_detalhes)
        topo_opcional.addStretch(1)
        opt_box_layout.addLayout(topo_opcional)

        dica_opcional = QLabel(
            "Você pode iniciar um foco livre normalmente. Ative esta opção apenas se quiser informar atividade, disciplina, tópico ou observação para esta sessão."
        )
        dica_opcional.setObjectName("focusWindowHint")
        dica_opcional.setWordWrap(True)
        opt_box_layout.addWidget(dica_opcional)

        self.campos_opcionais_container = QWidget()
        campos_layout = QVBoxLayout(self.campos_opcionais_container)
        campos_layout.setContentsMargins(0, 0, 0, 0)
        campos_layout.setSpacing(8)

        seletores = QGridLayout()
        seletores.setHorizontalSpacing(12)
        seletores.setVerticalSpacing(8)

        seletores.addWidget(QLabel("Atividade"), 0, 0)
        self.atividade = QComboBox()
        self.atividade.setMinimumHeight(34)
        self.atividade.addItems(tipos_atividade_foco())
        seletores.addWidget(self.atividade, 1, 0)

        seletores.addWidget(QLabel("Disciplina (opcional)"), 0, 1)
        self.disciplina = QComboBox()
        self.disciplina.setMinimumHeight(34)
        self.disciplina.currentIndexChanged.connect(self.carregar_topicos)
        seletores.addWidget(self.disciplina, 1, 1)

        seletores.addWidget(QLabel("Tópico (opcional)"), 0, 2)
        self.topico = QComboBox()
        self.topico.setMinimumHeight(34)
        seletores.addWidget(self.topico, 1, 2)

        seletores.setColumnStretch(0, 1)
        seletores.setColumnStretch(1, 1)
        seletores.setColumnStretch(2, 1)
        campos_layout.addLayout(seletores)

        obs_linha = QHBoxLayout()
        obs_linha.addWidget(QLabel("Observação:"))
        self.observacao = QLineEdit()
        self.observacao.setMinimumHeight(34)
        self.observacao.setPlaceholderText("Opcional — ex.: teoria antes da bateria de questões")
        obs_linha.addWidget(self.observacao, 1)
        campos_layout.addLayout(obs_linha)

        opt_box_layout.addWidget(self.campos_opcionais_container)
        config.addWidget(self.campos_opcionais_box)

        self.aviso_bateria_automatica = QLabel("")
        self.aviso_bateria_automatica.setObjectName("focusAutoQuestionsNotice")
        self.aviso_bateria_automatica.setWordWrap(True)
        self.aviso_bateria_automatica.setAlignment(Qt.AlignCenter)
        self.aviso_bateria_automatica.hide()
        config.addWidget(self.aviso_bateria_automatica)

        layout.addWidget(self.config_panel)

        # Sessão ativa.
        self.active_panel = QFrame()
        self.active_panel.setObjectName("focusActivePanel")
        ativo = QVBoxLayout(self.active_panel)
        ativo.setContentsMargins(18, 16, 18, 16)
        ativo.setSpacing(9)

        self.contexto = QLabel("Sessão de foco")
        self.contexto.setObjectName("focusContextLabel")
        self.contexto.setAlignment(Qt.AlignCenter)
        ativo.addWidget(self.contexto)

        self.relogio = QLabel("50:00")
        self.relogio.setObjectName("focusTimerValue")
        self.relogio.setAlignment(Qt.AlignCenter)
        ativo.addWidget(self.relogio)

        self.progresso = QProgressBar()
        self.progresso.setObjectName("focusProgressBar")
        self.progresso.setTextVisible(False)
        self.progresso.setRange(0, self.duracao_planejada)
        ativo.addWidget(self.progresso)

        self.status = QLabel("Pronto")
        self.status.setObjectName("focusStatusLabel")
        self.status.setAlignment(Qt.AlignCenter)
        ativo.addWidget(self.status)

        navegacao = QLabel(
            "O foco continua contando enquanto você usa o Dashboard e as demais telas do Vighna."
        )
        navegacao.setObjectName("focusWindowHint")
        navegacao.setAlignment(Qt.AlignCenter)
        navegacao.setWordWrap(True)
        ativo.addWidget(navegacao)

        acoes = QHBoxLayout()
        acoes.addStretch()
        self.pausar_btn = QPushButton("Pausar")
        self.pausar_btn.setObjectName("focusSecondaryButton")
        self.pausar_btn.clicked.connect(self.alternar_pausa)
        acoes.addWidget(self.pausar_btn)

        encerrar = QPushButton("Encerrar sessão")
        encerrar.setObjectName("focusDangerButton")
        encerrar.clicked.connect(self.encerrar_manual)
        acoes.addWidget(encerrar)
        acoes.addStretch()
        ativo.addLayout(acoes)

        self.active_panel.hide()
        layout.addWidget(self.active_panel)

        # Histórico recente.
        historico_panel = QFrame()
        historico_panel.setObjectName("focusRecentPanel")
        hist = QVBoxLayout(historico_panel)
        hist.setContentsMargins(14, 12, 14, 12)
        hist.setSpacing(8)
        hist_title = QLabel("Sessões recentes")
        hist_title.setObjectName("focusSectionTitle")
        hist.addWidget(hist_title)

        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels(
            ["Data", "Atividade", "Conteúdo", "Tempo real", "Estado"]
        )
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabela.setMinimumHeight(165)
        self.tabela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hist.addWidget(self.tabela)
        layout.addWidget(historico_panel, 1)

    def _criar_stat(self, layout, coluna, titulo):
        box = QVBoxLayout()
        valor = QLabel("0")
        valor.setObjectName("focusStatValue")
        rotulo = QLabel(titulo)
        rotulo.setObjectName("focusStatLabel")
        box.addWidget(valor)
        box.addWidget(rotulo)
        layout.addLayout(box, 0, coluna)
        return valor

    def _ajustar_campos_duracao(self, horas=None):
        if horas is None:
            horas = int(self.horas.value())
        else:
            horas = int(horas)

        if horas >= 24:
            # 24h é o teto absoluto: não pode haver minutos adicionais.
            self.minutos.blockSignals(True)
            self.minutos.setRange(0, 0)
            self.minutos.setValue(0)
            self.minutos.blockSignals(False)
            self.minutos.setEnabled(False)
        elif horas <= 0:
            # Evita uma duração nula, mantendo o mínimo operacional em 1 min.
            self.minutos.setEnabled(True)
            valor_atual = max(1, int(self.minutos.value()))
            self.minutos.blockSignals(True)
            self.minutos.setRange(1, 59)
            self.minutos.setValue(valor_atual)
            self.minutos.blockSignals(False)
        else:
            self.minutos.setEnabled(True)
            valor_atual = max(0, min(59, int(self.minutos.value())))
            self.minutos.blockSignals(True)
            self.minutos.setRange(0, 59)
            self.minutos.setValue(valor_atual)
            self.minutos.blockSignals(False)

    def _duracao_personalizada_minutos(self):
        total = int(self.horas.value()) * 60 + int(self.minutos.value())
        return _normalizar_duracao_foco_minutos(total)

    def definir_minutos(self, minutos):
        horas, minutos_restantes = _decompor_duracao_foco(minutos)
        self.horas.blockSignals(True)
        self.horas.setValue(int(horas))
        self.horas.blockSignals(False)
        self._ajustar_campos_duracao(horas)
        if horas < 24:
            self.minutos.setValue(int(minutos_restantes))

    def atualizar_campos_opcionais(self, marcado=None):
        if marcado is None:
            marcado = bool(self.usar_detalhes.isChecked())
        self.campos_opcionais_container.setVisible(bool(marcado))
        self.campos_opcionais_container.setEnabled(bool(marcado))
        if not marcado:
            self.disciplina.blockSignals(True)
            self.disciplina.setCurrentIndex(0)
            self.disciplina.blockSignals(False)
            self.carregar_topicos()
            self.topico.setCurrentIndex(0)
            self.observacao.clear()
            indice_livre = self.atividade.findText("Estudo livre", Qt.MatchFixedString)
            if indice_livre >= 0:
                self.atividade.setCurrentIndex(indice_livre)

    def preparar_sessao(
        self,
        minutos=None,
        atividade=None,
        disciplina=None,
        topico_id=None,
        topico=None,
        observacao=None,
        questoes_alvo=None,
        origem=None,
        origem_sessao=None,
        plano_chave=None,
        abrir_questoes_ao_iniciar=None,
    ):
        """Preenche o Modo Foco sem iniciar o cronômetro.

        Usado pelo Plano Automático para transformar uma sugestão em uma
        sessão pronta para confirmação pelo usuário.
        """
        if self.sessao_ativa:
            return False

        if minutos is not None:
            try:
                self.definir_minutos(minutos)
            except Exception:
                pass

        usar_detalhes = any([
            atividade,
            disciplina,
            topico_id not in (None, ""),
            bool(topico),
            observacao not in (None, ""),
        ])
        self.usar_detalhes.setChecked(bool(usar_detalhes))
        self.atualizar_campos_opcionais(bool(usar_detalhes))

        atividade = str(atividade or "").strip()
        if atividade:
            indice = self.atividade.findText(
                atividade,
                Qt.MatchFixedString,
            )
            if indice < 0:
                # Planos antigos podem trazer rótulos que não existiam no
                # combo do Foco. Questões é a aproximação mais segura para
                # atividades baseadas em bateria/treino.
                indice = self.atividade.findText(
                    "Questões",
                    Qt.MatchFixedString,
                )
            if indice >= 0:
                self.atividade.setCurrentIndex(indice)

        disciplina = str(disciplina or "").strip()
        if disciplina and disciplina not in {"—", "Várias"}:
            indice = self.disciplina.findText(
                disciplina,
                Qt.MatchFixedString,
            )
            if indice >= 0:
                self.disciplina.setCurrentIndex(indice)

        if topico_id not in (None, ""):
            try:
                indice_topico = self.topico.findData(int(topico_id))
            except Exception:
                indice_topico = -1
            if indice_topico >= 0:
                self.topico.setCurrentIndex(indice_topico)
        elif topico:
            indice_topico = self.topico.findText(
                str(topico),
                Qt.MatchFixedString,
            )
            if indice_topico >= 0:
                self.topico.setCurrentIndex(indice_topico)

        if observacao is not None:
            self.observacao.setText(str(observacao))

        try:
            self.meta_questoes_preparada = max(0, int(questoes_alvo or 0))
        except Exception:
            self.meta_questoes_preparada = 0
        self.origem_preparacao = str(origem or "").strip() or None
        self.origem_sessao_preparacao = str(origem_sessao or "").strip().lower() or None
        self.plano_chave_preparacao = str(plano_chave or "").strip() or None
        if abrir_questoes_ao_iniciar is None:
            self.abrir_questoes_ao_iniciar = bool(
                self.meta_questoes_preparada > 0
                and self.topico.currentData() is not None
                and self.atividade.currentText() in {
                    "Questões", "Treino adaptativo", "Teste de retenção",
                    "Sessão de controle", "Simulado", "Revisão"
                }
            )
        else:
            self.abrir_questoes_ao_iniciar = bool(abrir_questoes_ao_iniciar)

        self.contexto_questoes_preparado = None
        if (
            self.abrir_questoes_ao_iniciar
            and self.meta_questoes_preparada > 0
            and self.topico.currentData() is not None
        ):
            self.contexto_questoes_preparado = {
                "topico_id": int(self.topico.currentData()),
                "topico": self.topico.currentText(),
                "disciplina_id": self.disciplina.currentData(),
                "disciplina": self.disciplina.currentText(),
                "quantidade": int(self.meta_questoes_preparada),
                "atividade": self.atividade.currentText() or "Questões",
                "origem": self.origem_preparacao,
                "origem_sessao": self.origem_sessao_preparacao,
                "plano_chave": self.plano_chave_preparacao,
            }
            self.aviso_bateria_automatica.setText(
                f"Bateria automática preparada — {self.meta_questoes_preparada} questão(ões) "
                "serão abertas em outra janela assim que você clicar em Iniciar foco."
            )
            self.aviso_bateria_automatica.show()
        else:
            self.aviso_bateria_automatica.clear()
            self.aviso_bateria_automatica.hide()

        self.resultados_questoes = []
        self.questoes_disparadas = False

        self.config_panel.show()
        self.config_panel.setEnabled(True)
        self.active_panel.hide()
        QTimer.singleShot(0, lambda: self.scroll_area.ensureWidgetVisible(
            self.config_panel, 24, 24
        ))
        return True

    def carregar_disciplinas(self):
        self.disciplina.blockSignals(True)
        self.disciplina.clear()
        self.disciplina.addItem("Livre / sem vínculo", None)
        for disciplina_id, nome in listar_disciplinas():
            self.disciplina.addItem(nome, int(disciplina_id))
        self.disciplina.blockSignals(False)
        self.carregar_topicos()

    def carregar_topicos(self):
        self.topico.clear()
        self.topico.addItem("Sem tópico específico", None)
        disciplina_id = self.disciplina.currentData()
        if disciplina_id is None:
            self.topico.setEnabled(False)
            return
        self.topico.setEnabled(True)
        nome_disciplina = self.disciplina.currentText()
        for linha in listar_topicos(nome_disciplina):
            self.topico.addItem(str(linha[1]), int(linha[0]))

    def atualizar_resumo(self):
        resumo = obter_resumo_foco()
        self.stat_hoje.setText(_tempo_curto(resumo["hoje_segundos"]))
        self.stat_semana.setText(_tempo_curto(resumo["semana_segundos"]))
        self.stat_sessoes.setText(str(resumo["semana_sessoes"]))
        self.stat_media.setText(_tempo_curto(resumo["media_sessao_semana"]))

    def carregar_historico(self):
        sessoes = listar_sessoes_foco(12)
        self.tabela.setRowCount(len(sessoes))
        for linha, sessao in enumerate(sessoes):
            data = str(sessao["inicio"] or "")
            try:
                data = datetime.strptime(data[:19], "%Y-%m-%d %H:%M:%S").strftime("%d/%m %H:%M")
            except Exception:
                data = data[:16]
            conteudo = sessao.get("disciplina") or "Livre"
            if sessao.get("topico"):
                conteudo += f" › {sessao['topico']}"
            valores = [
                data,
                sessao.get("tipo_atividade") or "—",
                conteudo,
                _tempo_curto(sessao.get("duracao_efetiva", 0)),
                "Concluída" if sessao.get("concluida") else "Interrompida",
            ]
            for coluna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                if coluna in (3, 4):
                    item.setTextAlignment(Qt.AlignCenter)
                self.tabela.setItem(linha, coluna, item)

    def iniciar(self):
        if self.sessao_ativa:
            return
        minutos = self._duracao_personalizada_minutos()
        self.duracao_planejada = minutos * 60
        self.inicio_datetime = datetime.now()
        self.inicio_segmento = time.monotonic()
        self.acumulado = 0.0
        self.pausada = False
        self.sessao_ativa = True
        self.expiracao_aberta = False

        usar_detalhes = bool(self.usar_detalhes.isChecked())
        if usar_detalhes:
            conteudo = self.disciplina.currentText()
            if self.disciplina.currentData() is None:
                conteudo = "Sessão livre"
            elif self.topico.currentData() is not None:
                conteudo += f" › {self.topico.currentText()}"
            atividade_contexto = self.atividade.currentText()
        else:
            conteudo = "Sessão livre"
            atividade_contexto = "Foco livre"
        self.contexto.setText(f"{atividade_contexto} • {conteudo}")
        self.status.setText("Foco em andamento")
        self.pausar_btn.setText("Pausar")
        self.progresso.setRange(0, self.duracao_planejada)
        self.progresso.setValue(0)
        # Durante uma sessão, a configuração não é necessária. Ocultá-la
        # evita compressão vertical e deixa o cronômetro como elemento central.
        self.config_panel.hide()
        self.active_panel.show()
        self.timer.start()
        self.atualizar_timer()
        self.estado_alterado.emit()

        if (
            self.abrir_questoes_ao_iniciar
            and not self.questoes_disparadas
            and self.meta_questoes_preparada > 0
        ):
            contexto_questoes = None

            # Se o usuário manteve os detalhes ativos, respeitamos eventuais
            # ajustes feitos no tópico antes de iniciar. Caso ele esconda os
            # detalhes, preservamos a recomendação original preparada pelo
            # Motor V5 para não perder a bateria automática.
            if usar_detalhes and self.topico.currentData() is not None:
                contexto_questoes = {
                    "topico_id": int(self.topico.currentData()),
                    "topico": self.topico.currentText(),
                    "disciplina_id": self.disciplina.currentData(),
                    "disciplina": self.disciplina.currentText(),
                    "quantidade": int(self.meta_questoes_preparada),
                    "atividade": self.atividade.currentText() or "Questões",
                    "origem": self.origem_preparacao,
                    "origem_sessao": self.origem_sessao_preparacao,
                    "plano_chave": self.plano_chave_preparacao,
                }
            elif self.contexto_questoes_preparado:
                contexto_questoes = dict(self.contexto_questoes_preparado)

            if contexto_questoes and contexto_questoes.get("topico_id") is not None:
                self.questoes_disparadas = True
                QTimer.singleShot(
                    220,
                    lambda dados=contexto_questoes: self.solicitar_questoes.emit(dados),
                )

        # Se a janela estiver baixa, posiciona suavemente a área rolável no
        # cronômetro sem esconder o cabeçalho definitivamente.
        QTimer.singleShot(0, lambda: self.scroll_area.ensureWidgetVisible(
            self.active_panel, 24, 24
        ))

    def registrar_resultado_questoes(self, resultado):
        """Recebe o resultado do resolvedor enquanto o cronômetro continua ativo."""
        if not resultado:
            return
        self.resultados_questoes.append(dict(resultado))
        resumo = resultado.get("resumo") or {}
        respondidas = int(resumo.get("respondidas") or 0)
        desempenho = resumo.get("desempenho")
        if respondidas > 0:
            desempenho_txt = (
                f"{float(desempenho):.0f}%" if desempenho is not None else "—"
            )
            self.status.setText(
                f"Foco em andamento • {respondidas} questões • {desempenho_txt}"
            )

    def _consolidar_resultados_questoes(self):
        if not self.resultados_questoes:
            return None
        respondidas = 0
        acertos = 0
        erros = 0
        puladas = 0
        dominio_antes = []
        dominio_depois = []
        proxima_revisao = None
        sessoes_ids = []
        for resultado in self.resultados_questoes:
            resumo = resultado.get("resumo") or {}
            respondidas += int(resumo.get("respondidas") or 0)
            acertos += int(resumo.get("acertos") or 0)
            erros += int(resumo.get("erros") or 0)
            puladas += int(resumo.get("puladas") or 0)
            sessao_id = resultado.get("sessao_id") or resumo.get("sessao_id")
            if sessao_id not in (None, ""):
                sessoes_ids.append(int(sessao_id))
            efetividade = resultado.get("efetividade") or {}
            antes = efetividade.get("dominio_medio_antes")
            depois = efetividade.get("dominio_medio_depois")
            if antes is not None:
                dominio_antes.append(float(antes))
            if depois is not None:
                dominio_depois.append(float(depois))
            if resultado.get("proxima_revisao"):
                proxima_revisao = resultado.get("proxima_revisao")
        media_antes = sum(dominio_antes) / len(dominio_antes) if dominio_antes else None
        media_depois = sum(dominio_depois) / len(dominio_depois) if dominio_depois else None
        return {
            "sessoes_questoes_ids": sessoes_ids,
            "respondidas": respondidas,
            "acertos": acertos,
            "erros": erros,
            "puladas": puladas,
            "desempenho": (100.0 * acertos / respondidas) if respondidas else None,
            "dominio_antes": media_antes,
            "dominio_depois": media_depois,
            "delta_dominio": (
                media_depois - media_antes
                if media_antes is not None and media_depois is not None
                else None
            ),
            "proxima_revisao": proxima_revisao,
        }

    def tempo_decorrido(self):
        total = float(self.acumulado)
        if self.sessao_ativa and not self.pausada and self.inicio_segmento is not None:
            total += max(0.0, time.monotonic() - self.inicio_segmento)
        return total

    def alternar_pausa(self):
        if not self.sessao_ativa:
            return
        if self.pausada:
            self.pausada = False
            self.inicio_segmento = time.monotonic()
            self.pausar_btn.setText("Pausar")
            self.status.setText("Foco em andamento")
        else:
            self.acumulado = self.tempo_decorrido()
            self.inicio_segmento = None
            self.pausada = True
            self.pausar_btn.setText("Retomar")
            self.status.setText("Sessão pausada — este tempo não será contado")
        self.atualizar_timer()
        self.estado_alterado.emit()

    def atualizar_timer(self):
        if not self.sessao_ativa:
            return
        decorrido = self.tempo_decorrido()
        restante = max(0.0, self.duracao_planejada - decorrido)
        self.relogio.setText(_relogio(restante))
        self.progresso.setMaximum(max(1, int(self.duracao_planejada)))
        self.progresso.setValue(min(int(decorrido), int(self.duracao_planejada)))
        if restante <= 0.0 and not self.expiracao_aberta:
            self.expiracao_aberta = True
            self.acumulado = decorrido
            self.inicio_segmento = None
            self.pausada = True
            self.timer.stop()
            self.estado_alterado.emit()
            QTimer.singleShot(0, self.tratar_fim_planejado)

    def tratar_fim_planejado(self):
        if not self.sessao_ativa:
            return
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Sessão concluída")
        caixa.setIcon(QMessageBox.Information)
        caixa.setText(
            f"Você completou {_tempo_curto(self.duracao_planejada)} de foco."
        )
        caixa.setInformativeText(
            "Você pode concluir agora, fazer uma pausa ou acrescentar 10 minutos."
        )
        b_pausa = caixa.addButton("Pausa & Desafios", QMessageBox.ButtonRole.ActionRole)
        b_mais = caixa.addButton("+10 min de foco", QMessageBox.ButtonRole.ActionRole)
        b_concluir = caixa.addButton("Concluir", QMessageBox.ButtonRole.AcceptRole)
        caixa.setDefaultButton(b_concluir)
        caixa.exec()
        clicado = caixa.clickedButton()

        if clicado is b_mais:
            self.duracao_planejada += 10 * 60
            self.pausada = False
            self.inicio_segmento = time.monotonic()
            self.expiracao_aberta = False
            self.status.setText("Foco estendido por mais 10 minutos")
            self.pausar_btn.setText("Pausar")
            self.timer.start()
            self.atualizar_timer()
            self.estado_alterado.emit()
            return

        if clicado is b_pausa:
            contexto = self.finalizar(concluida=True, mostrar_pos_foco=False)
            JanelaPausaDesafios(self).exec()
            if contexto:
                self.mostrar_pos_foco(contexto)
        else:
            self.finalizar(concluida=True)

    def encerrar_manual(self):
        if not self.sessao_ativa:
            return
        if not self.pausada:
            self.acumulado = self.tempo_decorrido()
            self.inicio_segmento = None
            self.pausada = True

        decorrido = int(round(self.acumulado))
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Encerrar sessão")
        caixa.setIcon(QMessageBox.Question)
        caixa.setText(f"Tempo efetivo registrado até agora: {_tempo_curto(decorrido)}.")
        caixa.setInformativeText(
            "Marcar esta sessão como concluída? Se escolher 'Interrompida', o tempo continua sendo registrado, mas o estado ficará como interrompido."
        )
        concluida_btn = caixa.addButton("Concluída", QMessageBox.ButtonRole.AcceptRole)
        interrompida_btn = caixa.addButton("Interrompida", QMessageBox.ButtonRole.DestructiveRole)
        cancelar_btn = caixa.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        caixa.exec()
        clicado = caixa.clickedButton()
        if clicado is cancelar_btn:
            self.inicio_segmento = time.monotonic()
            self.pausada = False
            self.pausar_btn.setText("Pausar")
            self.status.setText("Foco em andamento")
            self.estado_alterado.emit()
            return
        self.finalizar(concluida=(clicado is concluida_btn))

    def finalizar(self, concluida, mostrar_pos_foco=True):
        if not self.sessao_ativa:
            return None
        if not self.pausada:
            self.acumulado = self.tempo_decorrido()
        self.timer.stop()
        efetiva = max(0, int(round(self.acumulado)))
        fim = datetime.now()

        usar_detalhes = bool(self.usar_detalhes.isChecked())
        disciplina_id = self.disciplina.currentData() if usar_detalhes else None
        topico_id = self.topico.currentData() if usar_detalhes else None
        disciplina_nome = (
            self.disciplina.currentText()
            if usar_detalhes and disciplina_id is not None else None
        )
        topico_nome = (
            self.topico.currentText()
            if usar_detalhes and topico_id is not None else None
        )
        atividade = self.atividade.currentText() if usar_detalhes else "Foco livre"
        observacao = self.observacao.text() if usar_detalhes else ""
        inicio_texto = (
            self.inicio_datetime.strftime("%Y-%m-%d %H:%M:%S")
            if self.inicio_datetime is not None else None
        )
        fim_texto = fim.strftime("%Y-%m-%d %H:%M:%S")
        sessao_id = None

        if efetiva > 0:
            sessao_id = registrar_sessao_foco(
                inicio=inicio_texto,
                fim=fim_texto,
                duracao_planejada=int(self.duracao_planejada),
                duracao_efetiva=efetiva,
                disciplina_id=disciplina_id,
                topico_id=topico_id,
                tipo_atividade=atividade,
                concluida=bool(concluida),
                observacao=observacao,
                disciplina_nome=disciplina_nome,
                topico_nome=topico_nome,
                meta_questoes=self.meta_questoes_preparada,
                origem=self.origem_preparacao,
                plano_chave=self.plano_chave_preparacao,
            )

        resultado_questoes = self._consolidar_resultados_questoes()
        if sessao_id is not None and resultado_questoes:
            for sessao_questoes_id in resultado_questoes.get("sessoes_questoes_ids") or []:
                try:
                    registrar_vinculo_foco_questoes(sessao_id, sessao_questoes_id)
                except Exception:
                    pass
            try:
                persistido = obter_resultado_foco_questoes(sessao_id)
                if persistido:
                    # Mantém dados contextuais obtidos pelo resolvedor (como a
                    # próxima revisão) e complementa com o agregado persistido.
                    persistido.update({
                        chave: valor
                        for chave, valor in resultado_questoes.items()
                        if valor is not None and chave not in persistido
                    })
                    if resultado_questoes.get("proxima_revisao"):
                        persistido["proxima_revisao"] = resultado_questoes["proxima_revisao"]
                    resultado_questoes = persistido
            except Exception:
                pass

        contexto_pos_foco = None
        if efetiva > 0:
            contexto_pos_foco = {
                "sessao_id": sessao_id,
                "inicio": inicio_texto,
                "fim": fim_texto,
                "duracao_planejada": int(self.duracao_planejada),
                "duracao_efetiva": efetiva,
                "disciplina_id": disciplina_id,
                "topico_id": topico_id,
                "disciplina": disciplina_nome,
                "topico": topico_nome,
                "tipo_atividade": atividade,
                "concluida": bool(concluida),
                "observacao": observacao,
                "meta_questoes": int(self.meta_questoes_preparada or 0),
                "origem": self.origem_preparacao,
                "origem_sessao": self.origem_sessao_preparacao,
                "plano_chave": self.plano_chave_preparacao,
                "resultado_questoes": resultado_questoes,
            }

        self.sessao_ativa = False
        self.pausada = False
        self.inicio_segmento = None
        self.acumulado = 0.0
        self.expiracao_aberta = False
        self.meta_questoes_preparada = 0
        self.origem_preparacao = None
        self.origem_sessao_preparacao = None
        self.plano_chave_preparacao = None
        self.abrir_questoes_ao_iniciar = False
        self.contexto_questoes_preparado = None
        if hasattr(self, "aviso_bateria_automatica"):
            self.aviso_bateria_automatica.clear()
            self.aviso_bateria_automatica.hide()
        self.resultados_questoes = []
        self.questoes_disparadas = False
        self.active_panel.hide()
        self.config_panel.setEnabled(True)
        self.config_panel.show()
        self.status.setText("Pronto")
        QTimer.singleShot(0, lambda: self.scroll_area.ensureWidgetVisible(
            self.config_panel, 24, 24
        ))
        self.atualizar_resumo()
        self.carregar_historico()
        self.resumo_alterado.emit()
        self.estado_alterado.emit()
        if contexto_pos_foco:
            self.sessao_finalizada.emit(dict(contexto_pos_foco))

        if contexto_pos_foco and mostrar_pos_foco:
            self.mostrar_pos_foco(contexto_pos_foco)
        return contexto_pos_foco

    def mostrar_pos_foco(self, dados):
        if not dados:
            return
        janela = JanelaPosFoco(dados, self)
        if janela.exec() != QDialog.Accepted:
            return
        acao = janela.acao_escolhida
        if acao == "encerrar":
            self.close()
            return
        if acao in {"questoes", "revisao", "recomendar"}:
            self.acao_pos_foco.emit(acao, dict(dados))

    def abrir_pausa(self):
        if self.sessao_ativa and not self.pausada:
            self.alternar_pausa()
        JanelaPausaDesafios(self).exec()

    def showEvent(self, event):
        super().showEvent(event)
        # Recalcula no monitor em que a janela realmente abriu e garante
        # que ela permaneça integralmente dentro da área útil.
        self._ajustar_tamanho_ao_monitor()
        tela = self.screen()
        if tela is None:
            return
        area = tela.availableGeometry()
        geo = self.frameGeometry()
        x = max(area.left(), min(geo.x(), area.right() - geo.width() + 1))
        y = max(area.top(), min(geo.y(), area.bottom() - geo.height() + 1))
        self.move(x, y)

    def closeEvent(self, event):
        if not self.sessao_ativa:
            event.accept()
            return
        resposta = QMessageBox.question(
            self,
            "Sessão em andamento",
            "Encerrar a janela e registrar o tempo de foco atual como sessão interrompida?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resposta == QMessageBox.Yes:
            self.finalizar(concluida=False, mostrar_pos_foco=False)
            event.accept()
        else:
            event.ignore()
