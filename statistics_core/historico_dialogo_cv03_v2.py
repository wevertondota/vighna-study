"""Visualização adicional do Histórico V2; protótipo integrado à base CV03.

Não altera os painéis antigos. Sem funções de exclusão, exportação ou gravação.
Depende de PySide6 no Windows; os testes deste checkpoint não executam Qt.
"""
from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QLabel, QPushButton, QComboBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea,
)

from .historico_validacao_exibicao_t_v1 import validar_exibicao_historica
from .historico_integracao_cv03_v2 import (
    consultar_historico_v2, PERIODOS_TELA, linhas_fontes,
    numero, percentual, pontos_percentuais,
)


class JanelaHistoricoAcademicoV2(QDialog):
    def __init__(self, caminho_banco, concurso_id: int, nome_concurso: str, parent=None):
        super().__init__(parent)
        self.caminho_banco = caminho_banco
        self.concurso_id = concurso_id
        self.setWindowTitle('Histórico acadêmico completo — VighnaStudy')
        self.resize(1020, 690)
        self.setMinimumSize(830, 570)
        self.setObjectName('historicoAcademicoV2')
        self.setStyleSheet('''
            QDialog#historicoAcademicoV2 { background: #071b2b; color: #e6f2fa; }
            QLabel { color: #dcebf5; }
            QFrame#historicoResumoCard { background: #0d293f;
                border: 1px solid #285875; border-radius: 9px; }
            QLabel#historicoNumero { font-size: 21px; font-weight: 700; color: #e7f7ff; }
            QLabel#historicoTitulo { font-size: 18px; font-weight: 700; color: #eef8ff; }
            QLabel#historicoAviso { color: #9fbccf; }
            QTableWidget { background: #0a2235; alternate-background-color: #102b41;
                color: #e6f2fa; gridline-color: #25445a; }
            QHeaderView::section { background: #11364f; color: #c9e8f7;
                border: 0; padding: 5px; }
            QPushButton { background: #155a7b; color: white;
                border-radius: 5px; padding: 5px 12px; }
            QComboBox, QDateEdit { background: #0e3048; color: #eff8ff;
                border: 1px solid #326680; padding: 4px; }
        ''')
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(17, 15, 17, 15)
        raiz.setSpacing(11)
        linha_titulo = QHBoxLayout()
        titulo = QLabel('Histórico acadêmico — visão consolidada')
        titulo.setObjectName('historicoTitulo')
        linha_titulo.addWidget(titulo)
        linha_titulo.addStretch()
        perfil_rotulo = QLabel(f'Perfil: {nome_concurso}')
        perfil_rotulo.setTextFormat(Qt.PlainText)
        linha_titulo.addWidget(perfil_rotulo)
        raiz.addLayout(linha_titulo)
        self.informativo = QLabel(
            'Histórico armazenado ≠ período analisado. O acumulado apresenta os registros existentes desde o início.'
        )
        self.informativo.setWordWrap(True)
        self.informativo.setObjectName('historicoAviso')
        raiz.addWidget(self.informativo)

        filtro = QHBoxLayout()
        filtro.addWidget(QLabel('Período'))
        self.combo = QComboBox()
        self.combo.addItems(list(PERIODOS_TELA))
        self.combo.setCurrentText('30 dias')
        filtro.addWidget(self.combo)
        self.rotulo_inicio = QLabel('De')
        filtro.addWidget(self.rotulo_inicio)
        self.inicio = QDateEdit(QDate.currentDate().addDays(-29))
        self.inicio.setCalendarPopup(True)
        self.inicio.setDisplayFormat('dd/MM/yyyy')
        filtro.addWidget(self.inicio)
        self.rotulo_fim = QLabel('Até')
        filtro.addWidget(self.rotulo_fim)
        self.fim = QDateEdit(QDate.currentDate())
        self.fim.setCalendarPopup(True)
        self.fim.setDisplayFormat('dd/MM/yyyy')
        filtro.addWidget(self.fim)
        botao = QPushButton('Consultar')
        botao.clicked.connect(self.atualizar)
        filtro.addWidget(botao)
        filtro.addStretch()
        raiz.addLayout(filtro)
        self.combo.currentTextChanged.connect(self._alterar_periodo)
        self._alterar_periodo(self.combo.currentText())

        resumo = QGridLayout()
        self.indicadores = {}
        for i, chave, nome in [
            (0, 'periodo', 'Acerto no período'),
            (1, 'acumulado', 'Acerto acumulado'),
            (2, 'variacao', 'Variação ante período anterior'),
            (3, 'respostas', 'Tentativas respondidas no período'),
        ]:
            card = QFrame()
            card.setObjectName('historicoResumoCard')
            lay = QVBoxLayout(card)
            rot = QLabel(nome)
            rot.setWordWrap(True)
            lay.addWidget(rot)
            val = QLabel('—')
            val.setObjectName('historicoNumero')
            lay.addWidget(val)
            self.indicadores[chave] = val
            resumo.addWidget(card, 0, i)
        raiz.addLayout(resumo)

        raiz.addWidget(QLabel('Fontes históricas — período × acumulado'))
        self.tabela = QTableWidget(0, 4)
        self.tabela.setHorizontalHeaderLabels(['Indicador', 'Período', 'Acumulado', 'Escopo'])
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        cab = self.tabela.horizontalHeader()
        cab.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in (1, 2, 3):
            cab.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.tabela.setMinimumHeight(185)
        raiz.addWidget(self.tabela, 3)

        raiz.addWidget(QLabel('Evolução mensal de tentativas — histórico completo do perfil'))
        self.mensal = QTableWidget(0, 4)
        self.mensal.setHorizontalHeaderLabels(['Mês', 'Respondidas', 'Acertos', 'Desempenho'])
        self.mensal.setAlternatingRowColors(True)
        self.mensal.setEditTriggers(QTableWidget.NoEditTriggers)
        self.mensal.verticalHeader().setVisible(False)
        self.mensal.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        raiz.addWidget(self.mensal, 2)
        self.aviso = QLabel('')
        self.aviso.setObjectName('historicoAviso')
        self.aviso.setWordWrap(True)
        raiz.addWidget(self.aviso)
        rodape = QHBoxLayout()
        self.status = QLabel('')
        rodape.addWidget(self.status)
        rodape.addStretch()
        fechar = QPushButton('Fechar')
        fechar.clicked.connect(self.accept)
        rodape.addWidget(fechar)
        raiz.addLayout(rodape)
        # Filtros modificados invalidam visualmente a consulta anterior.
        # Evita apresentar resultados de 30 dias com o seletor em 365 dias.
        self.inicio.dateChanged.connect(self._alteracao_data)
        self.fim.dateChanged.connect(self._alteracao_data)
        # Carrega após a janela ficar visível (sem acessar banco durante criação).
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self.atualizar)

    def _limpar_resultados(self):
        """Nunca manter indicadores de um filtro anterior na tela."""
        for item in self.indicadores.values():
            item.setText('—')
        self.tabela.setRowCount(0)
        self.mensal.setRowCount(0)
        self.aviso.setText('')

    def _marcar_consulta_pendente(self, *_):
        if not hasattr(self, 'status'):
            return  # O layout ainda pode estar em construção.
        self._limpar_resultados()
        self.status.setText('Período alterado. Clique em Consultar para atualizar.')

    def _alteracao_data(self, *_):
        """Datas ocultas nao invalidam uma consulta de janela fixa."""
        if self.combo.currentText() == 'Personalizado':
            self._marcar_consulta_pendente()

    @staticmethod
    def _preparar_exibicao(dados, *, escolha=None, concurso_id=None):
        """Confere e formata todo o retorno ANTES de alterar qualquer widget.

        Uma consulta parcialmente compativel nao pode deixar indicadores
        atualizados e tabelas antigas, ou mostrar um subconjunto enganoso.
        """
        validar_exibicao_historica(dados, escolha=escolha, concurso_id=concurso_id)
        modelo = dados['modelo']
        tent = modelo['indicadores_do_perfil']['tentativas']
        indicadores = {
            'periodo': percentual(tent['taxa_periodo_pct']),
            'acumulado': percentual(tent['taxa_acumulada_pct']),
            'variacao': pontos_percentuais(tent['variacao_pp']),
            'respostas': numero(tent['periodo']),
        }
        fontes = linhas_fontes(modelo)
        if not isinstance(fontes, (tuple, list)):
            raise TypeError('Indicadores das fontes invalidos')
        fontes = [tuple(str(c) for c in linha) for linha in fontes]
        if any(len(linha) != 4 for linha in fontes):
            raise ValueError('Numero de colunas das fontes invalido')
        meses = dados['meses']
        if not isinstance(meses, (tuple, list)):
            raise TypeError('Serie mensal invalida')
        mensal = [(
            str(item['mes']), numero(item['respondidas']),
            numero(item['acertos']), percentual(item['desempenho']),
        ) for item in meses]
        avisos = modelo.get('avisos') or []
        if not isinstance(avisos, (tuple, list)):
            raise TypeError('Avisos invalidos')
        return indicadores, fontes, mensal, '  •  '.join(str(x) for x in avisos[:3])

    def _alterar_periodo(self, texto):
        livre = texto == 'Personalizado'
        for widget in (self.inicio, self.fim, self.rotulo_inicio, self.rotulo_fim):
            widget.setVisible(livre)
        self._marcar_consulta_pendente()

    def atualizar(self):
        escolha = self.combo.currentText()
        a = self.inicio.date().toString('yyyy-MM-dd') if escolha == 'Personalizado' else None
        b = self.fim.date().toString('yyyy-MM-dd') if escolha == 'Personalizado' else None
        self._limpar_resultados()
        if escolha == 'Personalizado' and (a > b or b > date.today().isoformat()):
            self.status.setText('Período inválido. Verifique as datas.')
            return
        self.status.setText('Consultando histórico…')
        try:
            dados = consultar_historico_v2(
                self.caminho_banco, self.concurso_id, escolha,
                data_inicio=a, data_fim=b,
            )
            indicadores, linhas, mensal, avisos = self._preparar_exibicao(dados, escolha=escolha, concurso_id=self.concurso_id)
        except Exception:
            # Nunca exibir detalhes de SQLite/caminhos locais ao usuario.
            self.aviso.setText(
                'Nao foi possivel apresentar os dados. Verifique o diagnostico '
                'de integridade no clone antes de tentar novamente.'
            )
            self.status.setText('Histórico indisponível. Consulta não realizada.')
            return

        self.tabela.setUpdatesEnabled(False)
        self.mensal.setUpdatesEnabled(False)
        try:
            for chave, valor in indicadores.items():
                self.indicadores[chave].setText(valor)
            self.tabela.setRowCount(len(linhas))
            for row, dados_linha in enumerate(linhas):
                for col, campo in enumerate(dados_linha):
                    self.tabela.setItem(row, col, QTableWidgetItem(campo))
            self.mensal.setRowCount(len(mensal))
            for row, dados_linha in enumerate(mensal):
                for col, campo in enumerate(dados_linha):
                    self.mensal.setItem(row, col, QTableWidgetItem(campo))
            self.aviso.setText(avisos)
        except Exception:
            self._limpar_resultados()
            self.status.setText('Histórico indisponível. Falha ao apresentar resultados.')
            return
        finally:
            self.tabela.setUpdatesEnabled(True)
            self.mensal.setUpdatesEnabled(True)
        self.status.setText('Somente leitura · Sem expiração aplicada pelo módulo analítico')
