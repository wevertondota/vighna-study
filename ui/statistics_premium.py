"""Painel visual das Estatísticas, sem SQL e sem estado acadêmico paralelo.

Os dados são recebidos exclusivamente do motor de histórico existente. O
fundo utiliza a mesma imagem local e o mesmo princípio de overlay da tela
Início. O painel não altera resultados, configurações ou esquema do banco.
"""

from __future__ import annotations

import math
from datetime import datetime

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QPainterPath, QPolygonF, QPixmap
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QScrollArea, QSizePolicy, QProgressBar,
)

from tema import normalizar_tema
from ui.portal_background_image import imagem_fundo_inicio_bytes

CYAN = '#00c9f2'
TEXT = '#e7f1ff'
MUTED = '#a1b6ca'


def _label(text, cls='statLabel', *, wrap=False):
    lab = QLabel(str(text))
    lab.setObjectName(cls)
    lab.setWordWrap(wrap)
    return lab


def _card(title=None, subtitle=None, *, min_height=0):
    frame = QFrame()
    frame.setObjectName('statGlassCard')
    col = QVBoxLayout(frame)
    col.setContentsMargins(13, 11, 13, 11)
    col.setSpacing(7)
    if title:
        head = QHBoxLayout()
        head.setSpacing(7)
        head.addWidget(_label(title, 'statSectionTitle'))
        if subtitle:
            head.addWidget(_label(subtitle, 'statSecondaryCaption'), 1)
        else:
            head.addStretch(1)
        col.addLayout(head)
    if min_height:
        frame.setMinimumHeight(min_height)
    return frame, col


def _metric(parent_layout, title, *, value='—', detail=''):
    frame = QFrame()
    frame.setObjectName('statInnerCard')
    box = QVBoxLayout(frame)
    box.setContentsMargins(12, 10, 12, 10)
    box.setSpacing(4)
    box.addWidget(_label(title, 'statMetricLabel'))
    val = _label(value, 'statMetricValue')
    box.addWidget(val)
    sub = _label(detail, 'statSecondaryCaption', wrap=True)
    box.addWidget(sub)
    parent_layout.addWidget(frame)
    return val, sub


class FundoEstatisticasPremium(QWidget):
    """Plano de fundo fotográfico com overlay forte, usando a imagem do Início."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('statisticsModernPage')
        self._origem = None
        self._cache = None
        self._tamanho = None

    def paintEvent(self, event):
        super().paintEvent(event)
        tema = normalizar_tema(getattr(self.window(), 'tema_atual', 'claro'))
        if tema not in ('escuro', 'futurista'):
            return
        if self._origem is None:
            image = QPixmap()
            if not image.loadFromData(imagem_fundo_inicio_bytes(), 'JPG'):
                return
            self._origem = image
        if self._tamanho != self.size() or self._cache is None:
            self._cache = self._origem.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            self._tamanho = self.size()
        painter = QPainter(self)
        painter.drawPixmap(
            (self.width() - self._cache.width()) // 2,
            (self.height() - self._cache.height()) // 2,
            self._cache,
        )
        painter.fillRect(self.rect(), QColor(3, 9, 19, 194))
        painter.end()


class GraficoHistoricoPremium(QWidget):
    """Histórico real de acertos, questões e revisões em eixos legíveis."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.serie = []
        self.setMinimumHeight(180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def definir_serie(self, serie):
        self.serie = list(serie or [])
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        is_light = normalizar_tema(getattr(self.window(), 'tema_atual', 'claro')) == 'claro'
        fg = QColor('#41576e') if is_light else QColor('#a7c2db')
        grid = QColor(116, 159, 195, 42)
        area_left, area_right, area_top, area_bottom = 43, 10, 17, 27
        width = max(1, self.width() - area_left - area_right)
        height = max(1, self.height() - area_top - area_bottom)
        p.setFont(QFont('Segoe UI', 8))
        p.setPen(QPen(fg, 1))
        for v in (0, 25, 50, 75, 100):
            y = area_top + (100 - v) / 100 * height
            p.drawText(2, int(y + 4), f'{v}%')
            p.setPen(QPen(grid, 1))
            p.drawLine(area_left, int(y), area_left + width, int(y))
            p.setPen(QPen(fg, 1))
        data = self.serie
        if not data:
            p.drawText(self.rect(), Qt.AlignCenter, 'Sem dados de evolução no período')
            p.end()
            return
        n = len(data)
        gap = width / max(1, n - 1)
        max_vol = max([int(s.get('questoes') or 0) for s in data] + [1])
        for i, item in enumerate(data):
            x = area_left + gap * i
            vol = max(0, int(item.get('questoes') or 0))
            h = max(1, int(height * vol / max_vol * 0.43))
            p.fillRect(int(x - max(1.5, min(7, gap * .23))), int(area_top + height - h),
                       max(2, int(min(14, gap * .45))), h, QColor(17, 124, 184, 65))
        path = QPainterPath()
        for i, item in enumerate(data):
            val = item.get('desempenho')
            if val is None:
                continue
            x = area_left + gap * i
            y = area_top + (100 - min(100, max(0, float(val)))) / 100 * height
            if path.elementCount() == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        p.setPen(QPen(QColor('#05d2fa'), 2.3))
        p.drawPath(path)
        for i, item in enumerate(data):
            val = item.get('desempenho')
            if val is None:
                continue
            x = area_left + gap * i
            y = area_top + (100 - min(100, max(0, float(val)))) / 100 * height
            p.setBrush(QColor('#05d2fa'))
            p.drawEllipse(QPointF(x, y), 2.5, 2.5)
        step = max(1, (n + 5) // 6)
        p.setPen(QPen(fg, 1))
        for i in range(0, n, step):
            try:
                dt = datetime.strptime(str(data[i].get('data')), '%Y-%m-%d')
                label = dt.strftime('%d/%m')
            except (ValueError, TypeError):
                label = ''
            p.drawText(int(area_left + gap * i - 21), int(area_top + height + 19), 42, 15,
                       Qt.AlignCenter, label)
        p.end()


class CircularIndicadorPremium(QWidget):
    def __init__(self):
        super().__init__()
        self.valor = None
        self.setMinimumSize(104, 104)
        self.setMaximumHeight(160)

    def definir_valor(self, valor):
        self.valor = valor
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        tamanho = min(self.width(), self.height()) - 19
        box = self.rect().adjusted((self.width() - tamanho) // 2, 8,
                                    -(self.width() - tamanho) // 2, -(self.height() - tamanho) // 2)
        painter.setPen(QPen(QColor('#294b65'), 10, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(box, 0, 360 * 16)
        if self.valor is not None:
            painter.setPen(QPen(QColor('#00d0f4'), 10, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(box, 90 * 16, int(-360 * 16 * max(0, min(100, float(self.valor))) / 100))
        light = normalizar_tema(getattr(self.window(), 'tema_atual', 'claro')) == 'claro'
        painter.setPen(QColor('#203c53') if light else QColor('#f4fbff'))
        font = QFont('Segoe UI', 17, QFont.Bold)
        painter.setFont(font)
        txt = '—' if self.valor is None else f'{float(self.valor):.1f}%'.replace('.', ',')
        painter.drawText(self.rect(), Qt.AlignCenter, txt)
        painter.end()


class RadarDominiosPremium(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.valores = []
        self.setMinimumHeight(155)

    def definir(self, valores):
        self.valores = list(valores or [])[:6]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if len(self.valores) < 3:
            painter.setPen(QColor('#9cb7cf'))
            painter.drawText(self.rect(), Qt.AlignCenter, 'Base insuficiente para o mapa')
            painter.end()
            return
        size = min(self.width() - 120, self.height() - 20)
        radius = max(28, size / 2)
        center = QPointF(self.width() / 2, self.height() / 2)
        n = len(self.valores)
        def coord(i, pct):
            ang = -math.pi / 2 + 2 * math.pi * i / n
            return QPointF(center.x() + math.cos(ang) * radius * pct,
                           center.y() + math.sin(ang) * radius * pct)
        for t in (.25, .5, .75, 1):
            polygon = QPolygonF([coord(i, t) for i in range(n)])
            painter.setPen(QPen(QColor(86, 138, 171, 75), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawPolygon(polygon)
        polygon = QPolygonF([coord(i, max(0, min(1, float(v) / 100))) for i, (_, v) in enumerate(self.valores)])
        painter.setPen(QPen(QColor('#00d5ef'), 2))
        painter.setBrush(QBrush(QColor(0, 190, 233, 45)))
        painter.drawPolygon(polygon)
        painter.setPen(QColor('#a9c0d6'))
        painter.setFont(QFont('Segoe UI', 8))
        for i, (name, _) in enumerate(self.valores):
            point = coord(i, 1.16)
            text = str(name)
            if len(text) > 18:
                text = text[:17] + '…'
            painter.drawText(int(point.x() - 58), int(point.y() - 10), 116, 20,
                             Qt.AlignCenter, text)
        painter.end()


class PainelEstatisticasPremium(QWidget):
    """Apresentação de histórico + recortes, sem gravar nada no banco."""

    def __init__(self, *, ao_periodo, abrir_aba, detalhes, parent=None):
        super().__init__(parent)
        self.setObjectName('statisticsPremiumOverview')
        self._ao_periodo = ao_periodo
        self._abrir_aba = abrir_aba
        self._detalhes = detalhes

        base = QVBoxLayout(self)
        base.setContentsMargins(0, 0, 0, 0)
        base.setSpacing(0)
        self.scroll = QScrollArea(self)
        self.scroll.setObjectName('statisticsPremiumScroll')
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        base.addWidget(self.scroll)

        content = QWidget()
        content.setObjectName('statisticsPremiumContent')
        root = QVBoxLayout(content)
        root.setContentsMargins(4, 9, 4, 10)
        root.setSpacing(11)

        # Painel principal: cronologia + taxa visual + volumes auditáveis.
        hero, hero_l = _card()
        hd = QHBoxLayout()
        hd.addWidget(_label('↗', 'statAccentSymbol'))
        hd.addWidget(_label('Evolução histórica', 'statSectionTitle'))
        hd.addWidget(_label('Questões, sessões, revisões e foco no período', 'statSecondaryCaption'), 1)
        hd.addWidget(_label('Período', 'statSecondaryCaption'))
        self.periodo = QComboBox()
        self.periodo.addItems(['7 dias', '30 dias', '60 dias', '90 dias'])
        self.periodo.setCurrentText('30 dias')
        self.periodo.setFixedWidth(105)
        self.periodo.currentTextChanged.connect(self._ao_periodo)
        hd.addWidget(self.periodo)
        hero_l.addLayout(hd)

        self.hero_row = QBoxLayout(QBoxLayout.LeftToRight)
        self.hero_row.setSpacing(10)
        chart_wrap = QFrame()
        chart_wrap.setObjectName('statInnerCard')
        chart_l = QVBoxLayout(chart_wrap)
        chart_l.setContentsMargins(9, 7, 9, 6)
        chart_l.setSpacing(3)
        self.chart = GraficoHistoricoPremium()
        chart_l.addWidget(self.chart, 1)
        chart_l.addWidget(_label('● Taxa de acerto       ▥ Questões por dia', 'statSecondaryCaption'))
        self.hero_row.addWidget(chart_wrap, 6)

        rate, rate_l = _card()
        rate.setObjectName('statInnerCard')
        rate_l.addWidget(_label('Taxa de acerto no período', 'statMetricLabel'))
        self.ring = CircularIndicadorPremium()
        rate_l.addWidget(self.ring, 1)
        self.tentativas_ring = _label('—', 'statSecondaryCaption')
        self.tentativas_ring.setAlignment(Qt.AlignCenter)
        rate_l.addWidget(self.tentativas_ring)
        self.hero_row.addWidget(rate, 2)

        totals, totals_l = _card()
        totals.setObjectName('statInnerCard')
        self.hero_numbers = {}
        for title, key in [('Tentativas', 'questoes'), ('Questões únicas', 'questoes_unicas'),
                           ('Sessões de questões', 'sessoes'), ('Revisões qualificadas', 'revisoes')]:
            r = QHBoxLayout()
            r.addWidget(_label(title, 'statMetricLabel'))
            r.addStretch(1)
            value = _label('—', 'statMetricValueSmall')
            r.addWidget(value)
            self.hero_numbers[key] = value
            totals_l.addLayout(r)
        totals_l.addStretch(1)
        self.hero_row.addWidget(totals, 2)
        hero_l.addLayout(self.hero_row)
        root.addWidget(hero)

        # Foco, constância e prazos possuem fontes oficiais distintas.
        self.middle_row = QBoxLayout(QBoxLayout.LeftToRight)
        self.middle_row.setSpacing(10)
        foco, fc = _card('◷  Foco e constância', 'Tempo e frequência de estudo', min_height=133)
        fgrid = QHBoxLayout()
        self.foco_val, self.foco_detalhe = _metric(fgrid, 'Foco efetivo (global)')
        self.consistencia_val, self.consistencia_detalhe = _metric(fgrid, 'Dias com foco (global)')
        fc.addLayout(fgrid)
        self.middle_row.addWidget(foco, 1)

        prazo, pc = _card('▣  Pontualidade das revisões', 'Somente prazos conhecidos', min_height=133)
        pgrid = QHBoxLayout()
        self.prazo = {}
        for title, key in [('No prazo', 'pct'), ('Prazo conhecido', 'total'),
                           ('Atraso médio', 'atraso'), ('Concluídas atrasadas', 'atrasadas')]:
            val, det = _metric(pgrid, title)
            self.prazo[key] = val
        pc.addLayout(pgrid)
        self.middle_row.addWidget(prazo, 1)
        root.addLayout(self.middle_row)

        # A síntese inferior também é preenchida apenas com dados reais.
        self.bottom_row = QBoxLayout(QBoxLayout.LeftToRight)
        self.bottom_row.setSpacing(10)
        disc, dc = _card('▥  Desempenho por disciplina')
        hb = QHBoxLayout()
        hb.addStretch()
        bt = QPushButton('Ver todas  →')
        bt.setObjectName('statLinkButton')
        bt.clicked.connect(lambda: self._abrir_aba('Disciplinas'))
        hb.addWidget(bt)
        dc.addLayout(hb)
        self.disc_box = QVBoxLayout()
        self.disc_box.setSpacing(7)
        self.disc_linhas = []
        for _ in range(5):
            line = QHBoxLayout()
            name = _label('—', 'statMiniRowLabel')
            name.setMinimumWidth(92)
            bar = QProgressBar()
            bar.setObjectName('statMiniProgress')
            bar.setRange(0, 100)
            bar.setTextVisible(False)
            bar.setFixedHeight(7)
            percent = _label('—', 'statMiniRowValue')
            percent.setFixedWidth(50)
            line.addWidget(name, 2)
            line.addWidget(bar, 2)
            line.addWidget(percent)
            self.disc_box.addLayout(line)
            self.disc_linhas.append((name, bar, percent))
        dc.addLayout(self.disc_box)
        self.bottom_row.addWidget(disc, 1)

        radar, rc = _card('◎  Mapa de domínio')
        rb = QHBoxLayout()
        rb.addStretch(1)
        b = QPushButton('Ver mapa  →')
        b.setObjectName('statLinkButton')
        b.clicked.connect(lambda: self._abrir_aba('Mapa de domínio'))
        rb.addWidget(b)
        rc.addLayout(rb)
        self.radar = RadarDominiosPremium()
        rc.addWidget(self.radar, 1)
        self.bottom_row.addWidget(radar, 1)

        weak, wc = _card('⚠  Pontos fracos')
        wb = QHBoxLayout()
        wb.addStretch(1)
        b2 = QPushButton('Ver todos  →')
        b2.setObjectName('statLinkButton')
        b2.clicked.connect(lambda: self._abrir_aba('Pontos fracos'))
        wb.addWidget(b2)
        wc.addLayout(wb)
        self.weak_rows = []
        for _ in range(5):
            row = QHBoxLayout()
            name = _label('—', 'statMiniRowLabel')
            name.setMinimumWidth(90)
            bar = QProgressBar()
            bar.setObjectName('statWeakProgress')
            bar.setRange(0, 100)
            bar.setTextVisible(False)
            bar.setFixedHeight(7)
            pct = _label('—', 'statMiniRowValue')
            pct.setFixedWidth(48)
            row.addWidget(name, 2)
            row.addWidget(bar, 2)
            row.addWidget(pct)
            wc.addLayout(row)
            self.weak_rows.append((name, bar, pct))
        self.bottom_row.addWidget(weak, 1)
        root.addLayout(self.bottom_row)

        bottom = QHBoxLayout()
        bottom.addWidget(_label('Os indicadores exibem dados reais do perfil ativo; amostras ausentes aparecem como —.',
                               'statSecondaryCaption', wrap=True), 1)
        details_btn = QPushButton('Histórico detalhado  →')
        details_btn.setObjectName('statLinkButton')
        details_btn.clicked.connect(self._detalhes)
        bottom.addWidget(details_btn)
        root.addLayout(bottom)
        self.scroll.setWidget(content)

    def atualizar(self, dados, *, pontos_fracos=None):
        dados = dados or {}
        resumo = dados.get('resumo') or {}
        serie = dados.get('serie') or []
        desempenho = resumo.get('desempenho')
        self.chart.definir_serie(serie)
        self.ring.definir_valor(desempenho)
        self.tentativas_ring.setText(
            f"{int(resumo.get('questoes') or 0):,} tentativa(s) · {int(resumo.get('dias_ativos') or 0)} dia(s) ativo(s)".replace(',', '.')
        )
        vals = {
            'questoes': resumo.get('questoes'),
            'questoes_unicas': resumo.get('questoes_unicas'),
            'sessoes': resumo.get('sessoes'),
            'revisoes': dados.get('revisoes_periodo'),
        }
        for key, label in self.hero_numbers.items():
            val = vals.get(key)
            label.setText('—' if val is None else f'{int(val):,}'.replace(',', '.'))

        foco = dados.get('foco') or {}
        segundos = foco.get('segundos')
        segundos = int(segundos or 0)
        self.foco_val.setText(f'{segundos // 3600}h {segundos % 3600 // 60:02d}min')
        self.foco_detalhe.setText('Métrica global · tempo efetivo registrado')
        dias = int(''.join(ch for ch in self.periodo.currentText() if ch.isdigit()) or 30)
        dias_ativos = int(foco.get('dias_ativos') or 0)
        self.consistencia_val.setText(f'{dias_ativos}/{dias} dias')
        self.consistencia_detalhe.setText(f"{float(dados.get('consistencia_percentual') or 0):.0f}% do período")

        prazo = dados.get('prazos_revisao') or {}
        pct = prazo.get('percentual_no_prazo')
        atraso = prazo.get('atraso_medio_dias')
        self.prazo['pct'].setText('—' if pct is None else f'{float(pct):.0f}%')
        self.prazo['total'].setText(str(prazo.get('total_com_prazo', 0)))
        self.prazo['atraso'].setText('—' if atraso is None else f'{float(atraso):.1f} d'.replace('.', ','))
        self.prazo['atrasadas'].setText(str(int(prazo.get('atrasadas') or 0)))

        disciplinas = dados.get('disciplinas') or []
        disc_validos = [d for d in disciplinas if d.get('desempenho') is not None]
        disc_validos.sort(key=lambda d: int(d.get('questoes') or 0), reverse=True)
        for i, (name, bar, label) in enumerate(self.disc_linhas):
            if i < len(disc_validos):
                item = disc_validos[i]
                pct = max(0, min(100, float(item['desempenho'])))
                name.setText(str(item.get('disciplina') or '—'))
                name.setToolTip(name.text())
                bar.setValue(round(pct))
                label.setText(f'{pct:.0f}%')
            else:
                name.setText('—'); bar.setValue(0); label.setText('—')

        radar_values = [
            (str(d.get('disciplina') or '—'), float(d['dominio']))
            for d in disciplinas if d.get('dominio') is not None
        ]
        radar_values.sort(key=lambda x: x[1], reverse=True)
        self.radar.definir(radar_values[:6])

        # Reutiliza o ranking real do módulo Pontos fracos (sem estimativas).
        # Tupla do repositório: id, disciplina, tópico, questões, desempenho,
        # data última, data próxima, evidência.
        fracos = list(pontos_fracos or [])
        for i, (name, bar, label) in enumerate(self.weak_rows):
            if i < len(fracos) and len(fracos[i]) > 4 and fracos[i][4] is not None:
                item = fracos[i]
                pct = max(0, min(100, float(item[4])))
                name.setText(str(item[2] or '—'))
                name.setToolTip(
                    f"{item[1]} · {name.text()}" +
                    (' · evidência provisória' if len(item) > 7 and item[7] == 'low' else '')
                )
                bar.setValue(round(pct)); label.setText(f'{pct:.0f}%')
            else:
                name.setText('—'); bar.setValue(0); label.setText('—')

    def definir_periodo(self, text):
        if self.periodo.currentText() != text:
            self.periodo.blockSignals(True)
            self.periodo.setCurrentText(text)
            self.periodo.blockSignals(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Reorganiza sem recortes em monitores menores; nunca cria rolagem horizontal.
        w = self.width()
        direction = QBoxLayout.LeftToRight if w >= 1030 else QBoxLayout.TopToBottom
        if self.hero_row.direction() != direction:
            self.hero_row.setDirection(direction)
        direction_middle = QBoxLayout.LeftToRight if w >= 1040 else QBoxLayout.TopToBottom
        if self.middle_row.direction() != direction_middle:
            self.middle_row.setDirection(direction_middle)
        direction_bottom = QBoxLayout.LeftToRight if w >= 970 else QBoxLayout.TopToBottom
        if self.bottom_row.direction() != direction_bottom:
            self.bottom_row.setDirection(direction_bottom)


def aplicar_estilo_estatisticas_premium(pagina: QWidget, tema='futurista'):
    claro = normalizar_tema(tema) == 'claro'
    bg = 'rgba(248,251,255,235)' if claro else 'rgba(6,23,39,206)'
    inner = 'rgba(234,244,254,219)' if claro else 'rgba(8,29,48,211)'
    border = '#b9cfde' if claro else 'rgba(52,149,192,153)'
    main = '#19394e' if claro else TEXT
    sub = '#4f6b82' if claro else MUTED
    tab_base = '#e7f1f8' if claro else 'rgba(12,33,52,219)'
    qss = f'''
    QFrame#statsTopIndicator {{ background: {bg}; border: 1px solid {border}; border-radius: 11px; }}
    QFrame#statsTopIndicator QLabel {{ border: none; background: transparent; }}
    QFrame#statsTopIndicator QLabel#miniStatLabel {{ color: {sub}; font-size: 11px; }}
    QFrame#statsTopIndicator QLabel#miniStatValue {{ color: {main}; font-size: 19px; font-weight: 700; }}
    QLabel#statsTopIndicatorIcon {{ color: #00c9ef; font-size: 16px; font-weight: bold; }}
    QTabWidget#statisticsTabs::pane {{ background: rgba(4,14,26,18); border: 0; }}
    QTabBar::tab {{ background: {tab_base}; color: {sub}; border: 1px solid {border}; padding: 8px 12px; min-width: 74px; }}
    QTabBar::tab:selected {{ background: #054c7e; color: #ffffff; border-bottom: 2px solid #00d3f7; }}
    QTabBar::tab:hover {{ border-color: #00b9e3; }}
    QWidget#statisticsPremiumContent, QScrollArea#statisticsPremiumScroll, QWidget#statisticsHistoryTab, QWidget#statisticsPremiumOverview {{ background: transparent; border: none; }}
    QFrame#statGlassCard {{ background: {bg}; border: 1px solid {border}; border-radius: 13px; }}
    QFrame#statInnerCard {{ background: {inner}; border: 1px solid rgba(68,126,164,100); border-radius: 10px; }}
    QLabel#statSectionTitle {{ color: {main}; font-size: 14px; font-weight: 700; border: none; background: transparent; }}
    QLabel#statAccentSymbol {{ color: #00bee9; font-size: 20px; font-weight: 700; border: none; background: transparent; }}
    QLabel#statSecondaryCaption {{ color: {sub}; font-size: 11px; border: none; background: transparent; }}
    QLabel#statMetricLabel {{ color: {sub}; font-size: 11px; border: none; background: transparent; }}
    QLabel#statMetricValue {{ color: {main}; font-size: 20px; font-weight: 700; border: none; background: transparent; }}
    QLabel#statMetricValueSmall {{ color: {main}; font-size: 15px; font-weight: 700; border: none; background: transparent; }}
    QLabel#statMiniRowLabel, QLabel#statMiniRowValue {{ color: {main}; font-size: 11px; border: none; background: transparent; }}
    QPushButton#statLinkButton {{ background: transparent; color: #14c4ee; font-size: 11px; border: 1px solid {border}; border-radius: 8px; padding: 5px 10px; }}
    QPushButton#statLinkButton:hover {{ color: #ffffff; background: #126186; }}
    QProgressBar#statMiniProgress, QProgressBar#statWeakProgress {{ background: #26465c; border: none; border-radius: 3px; }}
    QProgressBar#statMiniProgress::chunk {{ background: #00cee9; border-radius: 3px; }}
    QProgressBar#statWeakProgress::chunk {{ background: #eb766e; border-radius: 3px; }}
    QComboBox {{ min-height: 26px; background: {inner}; color: {main}; border: 1px solid {border}; border-radius: 7px; padding: 0 6px; }}
    '''
    # Local stylesheet, sem tocar no estilo compartilhado do Vighna.
    pagina.setStyleSheet(qss)
