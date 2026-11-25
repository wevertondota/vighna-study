"""VighnaTime M2: controle da sessão, preferências e histórico; B21 permanece como fonte única de pausas."""
from __future__ import annotations
import time


def formatar(segundos):
    h, r = divmod(max(0, int(segundos)), 3600)
    m, s = divmod(r, 60)
    return f'{h:02d}:{m:02d}:{s:02d}'


def fotografia(bruto, pausas):
    bruto = max(0, int(bruto))
    pausa = min(bruto, sum(max(0, int(p.get('duracao_segundos', 0) or 0)) for p in pausas))
    return bruto, pausa, bruto - pausa


def duracao_intervalo(inicio_sessao, inicio, fim):
    """Partição da mesma escala inteira do relógio bruto, sem saltos durante a pausa."""
    return max(0, int(max(0, fim-inicio_sessao)) - int(max(0, inicio-inicio_sessao)))


def segmentos_sessao(bruto, pausas):
    """Faixas de estudo/pausa relativas à origem monotônica da bateria."""
    bruto = max(0, int(bruto)); cursor = 0; segmentos = []
    for p in sorted(pausas, key=lambda x: x.get('inicio_relativo_segundos', 0)):
        inicio = min(bruto, max(cursor, int(p.get('inicio_relativo_segundos', cursor))))
        fim = min(bruto, inicio + max(0, int(p.get('duracao_segundos', 0))))
        if inicio > cursor: segmentos.append(('estudo', inicio-cursor))
        if fim > inicio: segmentos.append(('pausa', fim-inicio))
        cursor = fim
    if cursor < bruto: segmentos.append(('estudo', bruto-cursor))
    return segmentos


class PlanoTempo:
    def __init__(self):
        self.modo = 'livre'
        self.estudo, self.descanso = 50, 10
        self.base, self.ciclo = 0, 1
        self.automatico, self.som, self.minimizar = False, True, False
        self.pausar_minimizado = True
        self.avisou = self.descanso_ciclo = False

    def configurar(self, modo, estudo, descanso, liquido, automatico=False, som=True, minimizar=False, pausar_minimizado=True):
        if modo not in ('livre', 'meta', 'ciclos'):
            raise ValueError('Modo inválido')
        if not 1 <= int(estudo) <= 720 or not 1 <= int(descanso) <= 120:
            raise ValueError('Duração fora dos limites')
        mudou_modo = modo != self.modo
        self.modo, self.estudo, self.descanso = modo, int(estudo), int(descanso)
        self.automatico = bool(automatico) and modo == 'ciclos'
        self.som, self.minimizar, self.pausar_minimizado = bool(som), bool(minimizar), bool(pausar_minimizado)
        if mudou_modo:
            self.reiniciar(liquido)
        elif not self.atingiu(liquido):
            self.avisou = False

    def reiniciar(self, liquido):
        self.base = max(0, int(liquido))
        self.ciclo = 1
        self.avisou = self.descanso_ciclo = False

    def restante(self, liquido):
        if self.modo == 'livre':
            return None
        return max(0, self.estudo * 60 - max(0, int(liquido) - self.base))

    def atingiu(self, liquido):
        return self.restante(liquido) == 0

    def iniciar_descanso(self, liquido):
        self.descanso_ciclo = self.modo == 'ciclos' and self.atingiu(liquido)

    def retomar(self, liquido):
        if self.descanso_ciclo:
            self.base = max(0, int(liquido))
            self.ciclo += 1
            self.avisou = False
        self.descanso_ciclo = False

    def preferencias(self):
        return dict(modo=self.modo, estudo=self.estudo, descanso=self.descanso,
                    automatico=self.automatico, som=self.som, minimizar=self.minimizar,
                    pausar_minimizado=self.pausar_minimizado)

    def carregar(self, settings):
        import json
        try:
            d = json.loads(str(settings.value('preferencias_v2', '{}')))
            if d:
                self.configurar(d['modo'], d['estudo'], d['descanso'], 0, d.get('automatico', False),
                    d.get('som', True), d.get('minimizar', False), d.get('pausar_minimizado', True))
        except (ValueError, TypeError, KeyError, AttributeError):
            pass

    def salvar(self, settings):
        import json
        settings.setValue('preferencias_v2', json.dumps(self.preferencias()))
        settings.sync()


class RelogioPausaLivre:
    """Sentinela compatível com o ciclo de pausa existente; não possui prazo."""
    def __init__(self):
        self.inicio = time.monotonic()

    def segundos_decorridos(self):
        return max(0, int(time.monotonic() - self.inicio))

    def segundos_restantes(self):
        # Chamadas antigas que só testam a existência de um prazo não expiram.
        # A apresentação de pausa livre usa segundos_decorridos().
        return 1

    def expirou(self):
        return False

    def adiar(self, minutos):
        return None


def proporcao_estudo(bruto, liquido):
    """Read-only display metric; no data persistence or performance scoring."""
    return None if bruto <= 0 else min(1.0, max(0.0, liquido / bruto))


def abrir_painel(bateria):
    import json
    from PySide6.QtCore import QTimer, QSettings, QRectF, Qt, QPointF, QSize
    from PySide6.QtGui import QShortcut, QKeySequence, QPainter, QColor, QPainterPath, QPen, QPixmap, QIcon, QBrush
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
        QComboBox, QSpinBox, QCheckBox, QPushButton, QFormLayout, 
        QTabBar, QWidget, QProgressBar, QTableWidget, QTableWidgetItem,
        QHeaderView, QAbstractItemView, QMessageBox, QInputDialog, QScrollArea, QFrame, QStackedWidget, QStyle, QStyleOptionComboBox, QStyleOptionSpinBox)
    plano = bateria._vtime_plano
    janela = QDialog(bateria)
    janela.setObjectName('vtimeM2')
    janela.setWindowTitle('VighnaTime · Central de Controle Temporal')
    # Local styles take precedence over inherited application QSS. Keep native title bar.
    janela.resize(620, 600); janela.setMinimumSize(490, 490)
    janela.setStyleSheet(''' 
        QDialog#vtimeM2 { background: #081522; color: #E5F0F7; font-family: "Segoe UI"; font-size: 13px; }
        QDialog#vtimeM2 QWidget { color: #E5F0F7; font-family: "Segoe UI"; font-size: 13px; }
        QDialog#vtimeM2 QWidget#vtPage, QDialog#vtimeM2 QWidget#vtConfig, QDialog#vtimeM2 QWidget#vtHistory { background: #081522; border: none; }
        QDialog#vtimeM2 QLabel { background: transparent; border: none; color: #E5F0F7; padding: 0; }
        QDialog#vtimeM2 QLabel[muted="true"] { color: #94B2C5; }
        QDialog#vtimeM2 QLabel#vtTitle { font-size: 24px; font-weight: 700; color: #F1F7FB; }
        QDialog#vtimeM2 QLabel#vtCaption { font-size: 11px; font-weight: 600; color: #93B0C1; }
        QDialog#vtimeM2 QLabel#vtHeading { font-size: 12px; font-weight: 700; color: #A8C7D8; }
        QDialog#vtimeM2 QLabel#vtClock { font-family: "Consolas"; font-size: 48px; font-weight: 700; color: #77E5F4; }
        QDialog#vtimeM2 QLabel#vtValue { font-family: "Consolas"; font-size: 21px; font-weight: 700; color: #EEF6FA; }
        QDialog#vtimeM2 QLabel#vtState { font-size: 12px; font-weight: 700; color: #77E5F4; }
        QDialog#vtimeM2 QLabel#vtState[paused="true"] { color: #F0C780; }
        QDialog#vtimeM2 QLabel#vtClock[paused="true"] { color: #F0C780; }
        QDialog#vtimeM2 QFrame#vtHero { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #102E42,stop:1 #0D2032); border: 1px solid #2D667D; border-radius: 14px; }
        QDialog#vtimeM2 QFrame#vtCard { background: #102437; border: 1px solid #254258; border-radius: 10px; }
        QDialog#vtimeM2 QFrame#vtInfo { background: #0C2030; border: 1px solid #243E53; border-radius: 8px; }
        QDialog#vtimeM2 QFrame#vtLine { background: #243D50; border: 0; max-height: 1px; }
        QDialog#vtimeM2 QTabBar, QDialog#vtimeM2 QStackedWidget#vtPages { border: 0; background: #081522; }
        QDialog#vtimeM2 QTabBar::base { border: 0; background: #081522; }
        QDialog#vtimeM2 QTabBar::tab:focus { color: #FFFFFF; }
        QDialog#vtimeM2 QTabBar::tab { background: #0D2133; color: #9DB9C9; padding: 8px 18px; border: none; border-bottom: 2px solid #243F53; margin-right: 3px; font-weight: 600; border-top-left-radius: 7px; border-top-right-radius: 7px; }
        QDialog#vtimeM2 QTabBar::tab:selected { background: #143247; color: #E7F9FD; border-bottom: 2px solid #67DAE9; }
        QDialog#vtimeM2 QTabBar::tab:hover:!selected { background: #163044; color: #E5F0F7; }
        QDialog#vtimeM2 QPushButton { background: #132C40; color: #E5F0F7; border: 1px solid #36566C; border-radius: 8px; padding: 7px 11px; min-height: 23px; font-weight: 600; }
        QDialog#vtimeM2 QPushButton:hover { background: #1B3B50; border-color: #6BA8BD; }
        QDialog#vtimeM2 QPushButton:pressed { background: #0A1D2E; }
        QDialog#vtimeM2 QPushButton#vtPrimary { background: #146E86; border-color: #63D5E5; color: #FFFFFF; }
        QDialog#vtimeM2 QPushButton#vtPrimary:hover { background: #1B829A; }
        QDialog#vtimeM2 QPushButton:focus, QDialog#vtimeM2 QComboBox:focus, QDialog#vtimeM2 QSpinBox:focus { border: 1px solid #85E4EF; }
        QDialog#vtimeM2 QPushButton:disabled { color: #71899A; background: #102131; border-color: #24394A; }
        QDialog#vtimeM2 QComboBox, QDialog#vtimeM2 QSpinBox { background: #0C1E30; border: 1px solid #345267; border-radius: 7px; padding: 3px 10px; padding-right: 30px; min-height: 21px; color: #E5F0F7; }
        QDialog#vtimeM2 QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 26px; border: none; border-left: 1px solid #345267; }
        QDialog#vtimeM2 QComboBox::down-arrow, QDialog#vtimeM2 QSpinBox::up-arrow, QDialog#vtimeM2 QSpinBox::down-arrow { image: none; width: 10px; height: 7px; }
        QDialog#vtimeM2 QSpinBox::up-button { subcontrol-origin: border; subcontrol-position: top right; width: 26px; border: none; border-left: 1px solid #345267; border-top-right-radius: 7px; }
        QDialog#vtimeM2 QSpinBox::down-button { subcontrol-origin: border; subcontrol-position: bottom right; width: 26px; border: none; border-left: 1px solid #345267; border-bottom-right-radius: 7px; }
        QDialog#vtimeM2 QComboBox::drop-down:hover, QDialog#vtimeM2 QSpinBox::up-button:hover, QDialog#vtimeM2 QSpinBox::down-button:hover { background: #24465A; }
        QDialog#vtimeM2 QComboBox QAbstractItemView { background: #102437; selection-background-color: #24546A; color: #E5F0F7; border: 1px solid #345267; }
        QDialog#vtimeM2 QSpinBox:disabled, QDialog#vtimeM2 QComboBox:disabled { color: #71899A; background: #102131; }
        QDialog#vtimeM2 QCheckBox { background: transparent; spacing: 10px; padding: 0; color: #DCEAF2; }
        QDialog#vtimeM2 QCheckBox:disabled { color: #71899A; }
        QDialog#vtimeM2 QCheckBox::indicator { width: 34px; height: 20px; border: none; background: transparent; }
        QDialog#vtimeM2 QProgressBar { border: none; background: #243F51; border-radius: 4px; min-height: 8px; max-height: 8px; }
        QDialog#vtimeM2 QProgressBar::chunk { background: #65D7E6; border-radius: 4px; }
        QDialog#vtimeM2 QProgressBar#vtRatio::chunk { background: #5CBCCB; }
        QDialog#vtimeM2 QLabel#vtRatioValue { color: #9CDDE6; font-weight: 600; }
        QDialog#vtimeM2 QScrollArea { background: #081522; border: none; }
        QDialog#vtimeM2 QScrollBar:vertical { background: #0C1C2A; width: 8px; margin: 0; }
        QDialog#vtimeM2 QScrollBar::handle:vertical { background: #395B70; min-height: 26px; border-radius: 4px; }
        QDialog#vtimeM2 QScrollBar::handle:vertical:hover { background: #65A4B8; }
        QDialog#vtimeM2 QScrollBar::add-line:vertical, QDialog#vtimeM2 QScrollBar::sub-line:vertical { height: 0; }
        QDialog#vtimeM2 QScrollBar::add-page:vertical, QDialog#vtimeM2 QScrollBar::sub-page:vertical { background: transparent; }
        QDialog#vtimeM2 QTableWidget { background: #0D2031; alternate-background-color: #12293B; color: #E5F0F7; border: 1px solid #29465B; border-radius: 8px; gridline-color: #29465B; }
        QDialog#vtimeM2 QTableWidget::item { padding: 5px; }
        QDialog#vtimeM2 QHeaderView::section { background: #18384B; color: #CDE3EC; border: none; padding: 8px 4px; font-weight: 600; }
    ''')
    def label(text='', size=0, bold=False, muted=False, name=None):
        l=QLabel(text); l.setWordWrap(True)
        if name: l.setObjectName(name)
        f=l.font()
        if size: f.setPointSize(size)
        f.setBold(bold); l.setFont(f)
        if muted: l.setProperty('muted',True)
        return l
    def card(name='vtCard', margins=(13,10,13,10), spacing=6):
        frame=QFrame(); frame.setObjectName(name)
        v=QVBoxLayout(frame); v.setContentsMargins(*margins); v.setSpacing(spacing)
        return frame,v
    def divider():
        line=QFrame(); line.setObjectName('vtLine'); line.setFixedHeight(1); return line
    # Native QCheckBox retains keyboard, accessible name, and existing signals.
    # Override only its painted indicator using local QPainter; no external image assets.
    class Toggle(QCheckBox):
        def paintEvent(self, event):
            super().paintEvent(event)
            from PySide6.QtWidgets import QStyle, QStyleOptionButton
            opt=QStyleOptionButton(); self.initStyleOption(opt)
            r=self.style().subElementRect(QStyle.SE_CheckBoxIndicator,opt,self)
            p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
            rect=QRectF(r).adjusted(1,1,-1,-1)
            on=self.isChecked(); enabled=self.isEnabled()
            p.setPen(QColor('#64CFE0' if on and enabled else '#567184' if enabled else '#334B5D'))
            p.setBrush(QColor('#146E86' if on and enabled else '#172D40'))
            p.drawRoundedRect(rect,rect.height()/2,rect.height()/2)
            d=max(1.0,rect.height()-6); x=rect.right()-d-3 if on else rect.left()+3
            p.setPen(Qt.NoPen); p.setBrush(QColor('#DDF8FC' if enabled else '#71899A'))
            p.drawEllipse(QRectF(x,rect.top()+3,d,d)); p.end()
    # Draw chevrons independently of inherited application QSS and theme assets.
    def chevron(p, rect, up, enabled):
        if not rect.isValid(): return
        x, y = rect.center().x(), rect.center().y()
        d = min(4.0, rect.width()/4, rect.height()/3)
        p.setPen(QPen(QColor('#B7DCE9' if enabled else '#627B8D'), 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        sign = -1 if up else 1
        p.drawLine(QPointF(x-d,y-sign*d/2),QPointF(x,y+sign*d/2))
        p.drawLine(QPointF(x,y+sign*d/2),QPointF(x+d,y-sign*d/2))
    class Selector(QComboBox):
        def paintEvent(self,event):
            super().paintEvent(event)
            opt=QStyleOptionComboBox(); self.initStyleOption(opt)
            r=self.style().subControlRect(QStyle.CC_ComboBox,opt,QStyle.SC_ComboBoxArrow,self)
            p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
            chevron(p,r,False,self.isEnabled()); p.end()
    class Duration(QSpinBox):
        def paintEvent(self,event):
            super().paintEvent(event)
            opt=QStyleOptionSpinBox(); self.initStyleOption(opt)
            p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
            for control,up,allowed in ((QStyle.SC_SpinBoxUp,True,self.value()<self.maximum()),(QStyle.SC_SpinBoxDown,False,self.value()>self.minimum())):
                r=self.style().subControlRect(QStyle.CC_SpinBox,opt,control,self)
                chevron(p,r,up,self.isEnabled() and allowed)
            p.end()
    # Native tab semantics without QTabWidget's inherited pane border.
    class Pages(QWidget):
        def __init__(self):
            super().__init__(); v=QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(0)
            self.bar=QTabBar(); self.bar.setDrawBase(False); self.bar.setExpanding(False); self.bar.setElideMode(Qt.ElideNone)
            self.bar.setAccessibleName('Abas da central temporal'); v.addWidget(self.bar)
            self.stack=QStackedWidget(); self.stack.setObjectName('vtPages'); v.addWidget(self.stack,1)
            self.bar.currentChanged.connect(self.stack.setCurrentIndex)
            self.shortcuts=[]
            for key,step in (('Ctrl+Tab',1),('Ctrl+Shift+Tab',-1)):
                shortcut=QShortcut(QKeySequence(key),self); shortcut.activated.connect(lambda step=step: self.bar.setCurrentIndex((self.bar.currentIndex()+step)%self.bar.count()) if self.bar.count() else None); self.shortcuts.append(shortcut)
        def addTab(self,page,title):
            self.stack.addWidget(page); self.bar.addTab(title)
    def glyph(kind):
        pix=QPixmap(32,32); pix.fill(Qt.transparent)
        p=QPainter(pix); p.setRenderHint(QPainter.Antialiasing); p.scale(2,2)
        p.setPen(QPen(QColor('#CFEAF2'),1.5,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
        if kind=='pause':
            p.drawLine(QPointF(5,3),QPointF(5,13)); p.drawLine(QPointF(11,3),QPointF(11,13))
        elif kind=='play':
            path=QPainterPath(QPointF(5,3)); path.lineTo(13,8); path.lineTo(5,13); path.closeSubpath(); p.drawPath(path)
        elif kind=='clock':
            p.drawEllipse(QRectF(2,2,12,12)); p.drawLine(QPointF(8,4),QPointF(8,8)); p.drawLine(QPointF(8,8),QPointF(11,9))
        p.end(); pix.setDevicePixelRatio(2); return QIcon(pix)
    root=QVBoxLayout(janela); root.setContentsMargins(18,14,18,12); root.setSpacing(10)
    cab=QHBoxLayout(); cab.setSpacing(12); root.addLayout(cab)
    header=QVBoxLayout(); header.setSpacing(1); cab.addLayout(header,1)
    header.addWidget(label('VighnaTime',name='vtTitle')); header.addWidget(label('Central de Controle Temporal',muted=True))
    cab.addWidget(label('BATERIA ATUAL',name='vtCaption'),0,Qt.AlignTop|Qt.AlignRight)
    tabs=Pages(); root.addWidget(tabs,1)
    sessao=QWidget(); sessao.setObjectName('vtPage'); layout=QVBoxLayout(sessao); layout.setContentsMargins(0,12,0,0); layout.setSpacing(10)
    tabs.addTab(sessao,'Sessão')
    hero,hv=card('vtHero',(16,12,16,13),5); layout.addWidget(hero)
    topline=QHBoxLayout(); topline.setSpacing(8); hv.addLayout(topline)
    topline.addWidget(label('TEMPO LÍQUIDO DA SESSÃO',name='vtHeading'),1)
    estado=label('',name='vtState'); estado.setAlignment(Qt.AlignRight|Qt.AlignVCenter); topline.addWidget(estado,1)
    liquido_label=label('00:00:00',name='vtClock'); liquido_label.setWordWrap(False); liquido_label.setAlignment(Qt.AlignCenter); hv.addWidget(liquido_label)
    meta=label('',muted=True); meta.setAlignment(Qt.AlignCenter); hv.addWidget(meta)
    progress=QProgressBar(); progress.setRange(0,1000); progress.setTextVisible(False); hv.addWidget(progress)
    hv.addWidget(divider())
    ratio_line=QHBoxLayout(); hv.addLayout(ratio_line)
    ratio_caption=label('Proporção de estudo',muted=True); ratio_caption.setToolTip('Tempo líquido dividido pelo tempo bruto. Não mede desempenho nem aprendizagem.'); ratio_line.addWidget(ratio_caption)
    ratio_line.addStretch(1); ratio_text=label('—',name='vtRatioValue'); ratio_line.addWidget(ratio_text)
    ratio_bar=QProgressBar(); ratio_bar.setObjectName('vtRatio'); ratio_bar.setRange(0,1000); ratio_bar.setTextVisible(False); ratio_bar.setAccessibleName('Proporção de estudo'); hv.addWidget(ratio_bar)
    indicadores=QHBoxLayout(); indicadores.setSpacing(8); layout.addLayout(indicadores)
    valores=[]
    for nome in ('Tempo bruto','Em pausas','Nº de pausas'):
        g,v=card(); v.addWidget(label(nome,name='vtCaption')); l=label('—',name='vtValue'); l.setWordWrap(False); v.addWidget(l); indicadores.addWidget(g,1); valores.append(l)
    layout.addWidget(label('CONTROLE DA SESSÃO',name='vtHeading'))
    linha=QHBoxLayout(); linha.setSpacing(8); layout.addLayout(linha)
    principal=QPushButton('Pausar agora'); principal.setObjectName('vtPrimary'); linha.addWidget(principal,1)
    programada=QPushButton('Descanso'); linha.addWidget(programada,1)
    pause_icon,play_icon,clock_icon=(glyph(k) for k in ('pause','play','clock')); principal.setIconSize(QSize(16,16)); programada.setIconSize(QSize(16,16)); principal.setIcon(pause_icon); programada.setIcon(clock_icon)
    adiar=QPushButton('+5 min'); linha.addWidget(adiar)
    livre=QPushButton('Sem limite'); linha.addWidget(livre)
    info,iv=card('vtInfo',(12,8,12,8)); iv.addWidget(label('F8  ·  Pausar ou retomar diretamente na Bateria.',muted=True)); layout.addWidget(info)
    layout.addStretch(1)
    # Config actions stay outside the scrolling body; controls are never hidden below the fold.
    config_page=QWidget(); config_page.setObjectName('vtPage'); config_layout=QVBoxLayout(config_page); config_layout.setContentsMargins(0,8,0,0); config_layout.setSpacing(6)
    area=QScrollArea(); area.setWidgetResizable(True); area.setFrameShape(QFrame.NoFrame); area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    config_layout.addWidget(area,1)
    grupo=QWidget(); grupo.setObjectName('vtConfig'); cfg=QVBoxLayout(grupo); cfg.setContentsMargins(0,0,5,1); cfg.setSpacing(5); area.setWidget(grupo)
    tabs.addTab(config_page,'Configurações')
    perfil,pv=card(margins=(12,7,12,7),spacing=4); cfg.addWidget(perfil); pv.addWidget(label('PERFIL DE SESSÃO',name='vtHeading'))
    form=QFormLayout(); form.setContentsMargins(0,0,0,0); form.setHorizontalSpacing(12); form.setVerticalSpacing(4); form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow); pv.addLayout(form)
    settings=QSettings('VighnaStudy','VighnaTime')
    presets={'Estudo livre':('livre',50,10),'Pomodoro · 25/5':('ciclos',25,5),'Concentração · 50/10':('ciclos',50,10),'Prolongado · 90/15':('ciclos',90,15)}
    try:
        custom=json.loads(str(settings.value('presets_v2','{}')))
        if isinstance(custom,dict):
            for nome,d in list(custom.items())[:30]:
                if isinstance(d,list) and len(d)==3 and d[0] in ('livre','meta','ciclos') and 1<=int(d[1])<=720 and 1<=int(d[2])<=120:
                    presets.setdefault(str(nome),(d[0],int(d[1]),int(d[2])))
    except (ValueError,TypeError): pass
    preset=Selector(); preset.addItem('Escolher predefinição…'); preset.addItems(list(presets)); form.addRow('Predefinição',preset)
    modo=Selector()
    for texto,codigo in [('Tempo livre','livre'),('Meta de estudo','meta'),('Ciclos de estudo e descanso','ciclos')]: modo.addItem(texto,codigo)
    modo.setCurrentIndex(modo.findData(plano.modo)); form.addRow('Modo',modo)
    tempos,tv=card(margins=(12,7,12,7),spacing=4); cfg.addWidget(tempos); tv.addWidget(label('DURAÇÕES',name='vtHeading'))
    duracoes=QHBoxLayout(); duracoes.setSpacing(10); tv.addLayout(duracoes)
    estudo=Duration(); estudo.setRange(1,720); estudo.setSuffix(' min'); estudo.setValue(plano.estudo)
    descanso=Duration(); descanso.setRange(1,120); descanso.setSuffix(' min'); descanso.setValue(plano.descanso)
    for nome,campo in (('Estudo',estudo),('Descanso',descanso)):
        bloco=QHBoxLayout(); bloco.setSpacing(6); duracoes.addLayout(bloco,1)
        titulo=label(nome); titulo.setBuddy(campo); campo.setAccessibleName(nome); bloco.addWidget(titulo); bloco.addWidget(campo,1)
    automacao,av=card(margins=(12,7,12,7),spacing=3); cfg.addWidget(automacao); av.addWidget(label('AUTOMAÇÃO E COMPORTAMENTO',name='vtHeading'))
    auto=Toggle('Iniciar descanso automaticamente'); auto.setChecked(plano.automatico); av.addWidget(auto)
    som=Toggle('Avisos sonoros'); som.setChecked(plano.som); av.addWidget(som)
    minimizar=Toggle('Minimizar durante descanso programado'); minimizar.setChecked(plano.minimizar); av.addWidget(minimizar)
    pausa_min=Toggle('Pausar ao minimizar ou ir ao Dashboard'); pausa_min.setChecked(plano.pausar_minimizado); av.addWidget(pausa_min)
    info_cfg,icv=card('vtInfo',(10,5,10,5),2); icv.addWidget(label('Aplicar mantém as preferências para a próxima bateria. Alterar a duração preserva o progresso; mudar o modo inicia nova meta, sem zerar o tempo líquido.',muted=True)); cfg.addWidget(info_cfg); cfg.addStretch(1)
    acoes=QHBoxLayout(); config_layout.addLayout(acoes)
    aplicar=QPushButton('Aplicar'); aplicar.setObjectName('vtPrimary'); acoes.addWidget(aplicar,1)
    salvar_preset=QPushButton('Salvar predefinição'); acoes.addWidget(salvar_preset,1)
    reiniciar=QPushButton('Reiniciar período'); acoes.addWidget(reiniciar,1)
    historico=QWidget(); historico.setObjectName('vtHistory'); h=QVBoxLayout(historico); h.setContentsMargins(0,12,0,0); h.setSpacing(10)
    resumo,rv=card('vtCard',(13,10,13,10)); h.addWidget(resumo)
    rv.addWidget(label('LINHA DO TEMPO DA SESSÃO',name='vtHeading'))
    hist_info=label('',name='vtHeading'); rv.addWidget(hist_info)
    class FaixaTemporal(QWidget):
        def __init__(self):
            super().__init__(); self.segmentos=[]; self.setFixedHeight(14)
            self.setAccessibleName('Linha do tempo: estudo e pausas')
        def atualizar(self, segmentos):
            if self.segmentos != segmentos:
                self.segmentos=segmentos; self.update()
        def paintEvent(self, evento):
            p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
            r=QRectF(self.rect()); trilho=QPainterPath(); trilho.addRoundedRect(r,7,7)
            p.fillPath(trilho,QColor('#243F51')); p.setClipPath(trilho)
            total=sum(d for _,d in self.segmentos)
            if total:
                x=0.0
                for tipo,d in self.segmentos:
                    w=self.width()*d/total
                    p.fillRect(QRectF(x,0,w,self.height()), QColor('#61D2E3' if tipo=='estudo' else '#E8BB73'))
                    x+=w
            p.end()
    faixa=FaixaTemporal(); rv.addWidget(faixa)
    escala=QHBoxLayout(); rv.addLayout(escala)
    ticks=[label('00:00:00',muted=True) for _ in range(3)]
    for tick,align in zip(ticks,(Qt.AlignLeft,Qt.AlignCenter,Qt.AlignRight)):
        tick.setAlignment(align); escala.addWidget(tick,1)
    legenda=QHBoxLayout(); legenda.setSpacing(7); rv.addLayout(legenda)
    for cor,txt in (('#61D2E3','Estudo'),('#E8BB73','Pausa')):
        ponto=QFrame(); ponto.setFixedSize(9,9); ponto.setStyleSheet(f'background:{cor};border:none;border-radius:4px;'); legenda.addWidget(ponto); legenda.addWidget(label(txt,muted=True))
    legenda.addStretch(1)
    h.addWidget(label('PAUSAS REGISTRADAS NESTA BATERIA',name='vtHeading'))
    tabela=QTableWidget(0,4); tabela.setHorizontalHeaderLabels(['Início','Tipo','Previsto','Real']); tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    tabela.verticalHeader().hide(); tabela.setAlternatingRowColors(True); tabela.setShowGrid(False); tabela.verticalHeader().setDefaultSectionSize(32); tabela.setEditTriggers(QAbstractItemView.NoEditTriggers); tabela.setSelectionMode(QAbstractItemView.NoSelection)
    historico_stack=QStackedWidget(); h.addWidget(historico_stack,1)
    vazio,vv=card('vtCard',(16,15,16,15)); vv.addStretch(1); empty=label('Nenhuma pausa registrada',name='vtHeading'); empty.setAlignment(Qt.AlignCenter); vv.addWidget(empty); empty2=label('As pausas desta bateria aparecerão aqui.',muted=True); empty2.setAlignment(Qt.AlignCenter); vv.addWidget(empty2); vv.addStretch(1)
    historico_stack.addWidget(vazio); historico_stack.addWidget(tabela); tabs.addTab(historico,'Histórico')
    root.addWidget(divider()); rodape=QHBoxLayout(); root.addLayout(rodape); foco=QPushButton('Modo Foco'); fechar=QPushButton('Fechar'); rodape.addWidget(foco); rodape.addStretch(1); rodape.addWidget(fechar)
    resultado={'acao':None}; anterior_hist=None
    def escolher(acao):
        resultado['acao']=acao; janela.accept()
    def carregar_preset():
        d=presets.get(preset.currentText())
        if d:
            modo.setCurrentIndex(modo.findData(d[0])); estudo.setValue(d[1]); descanso.setValue(d[2]); auto.setChecked(d[0]=='ciclos')
    def campos():
        estudo.setEnabled(modo.currentData()!='livre'); auto.setEnabled(modo.currentData()=='ciclos')
    preset.currentIndexChanged.connect(carregar_preset); modo.currentIndexChanged.connect(campos); campos()
    def guardar_preset():
        nome,ok=QInputDialog.getText(janela,'Salvar predefinição','Nome da predefinição:'); nome=nome.strip()
        if not ok or not nome: return
        if nome in presets or len(presets)>=34:
            QMessageBox.information(janela,'Predefinição','Use um nome novo (até 30 configurações personalizadas).'); return
        presets[nome]=(modo.currentData(),estudo.value(),descanso.value())
        settings.setValue('presets_v2',json.dumps({k:list(v) for k,v in list(presets.items())[4:]})); settings.sync(); preset.addItem(nome)
    def aplicar_config():
        bateria._vtime_configurar(modo.currentData(),estudo.value(),descanso.value(),auto.isChecked(),som.isChecked(),minimizar.isChecked(),pausa_min.isChecked()); atualizar()
    def resetar():
        if bateria._pausa_relogio is None and QMessageBox.question(janela,'Reiniciar período','Reiniciar a meta atual sem alterar o total líquido?',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)==QMessageBox.Yes:
            if bateria._pausa_relogio is None: plano.reiniciar(bateria._vtime_fotografia()[2]); atualizar()
    def atualizar():
        nonlocal anterior_hist
        if bateria.finalizada: janela.reject(); return
        agora=time.monotonic(); bruto,pausa,liquido=bateria._vtime_fotografia(agora); relogio=bateria._pausa_relogio; pausada=relogio is not None; sem_limite=isinstance(relogio,RelogioPausaLivre)
        if sem_limite: estado.setText('PAUSA LIVRE · '+formatar(relogio.segundos_decorridos()))
        elif pausada: estado.setText('DESCANSO · '+formatar(relogio.segundos_restantes()) if relogio.segundos_restantes()>0 else 'DESCANSO EXPIRADO · aguardando retorno')
        else: estado.setText('ESTUDANDO · CICLO '+str(plano.ciclo) if plano.modo=='ciclos' else 'ESTUDANDO')
        for widget in (estado,liquido_label):
            if widget.property('paused') != pausada:
                widget.setProperty('paused',pausada); widget.style().unpolish(widget); widget.style().polish(widget); widget.update()
        liquido_label.setText(formatar(liquido)); restante=plano.restante(liquido); progress.setVisible(restante is not None)
        if restante is None: meta.setText('Estudo livre · sem limite de duração')
        else:
            total=plano.estudo*60; progress.setValue(int(1000*(total-restante)/total)); meta.setText(f'Período: {formatar(total-restante)} / {formatar(total)} · restam {formatar(restante)}')
        pausas=bateria._b21_fotografia_pausas(agora)
        faixa.atualizar(segmentos_sessao(bruto,pausas))
        proporcao = proporcao_estudo(bruto,liquido)
        ratio_text.setText('—' if proporcao is None else f'{proporcao*100:.1f}%'.replace('.',','))
        ratio_bar.setValue(0 if proporcao is None else round(proporcao*1000))
        for tick,segundos in zip(ticks,(0,bruto//2,bruto)): tick.setText(formatar(segundos))
        for l,v in zip(valores,(formatar(bruto),formatar(pausa),str(len(pausas)))): l.setText(v)
        principal.setText('Retomar estudo' if pausada else 'Pausar agora'); principal.setIcon(play_icon if pausada else pause_icon); programada.setText(f'Descanso de {plano.descanso} min'); programada.setVisible(not pausada)
        adiar.setVisible(pausada and not sem_limite); livre.setVisible(pausada and not sem_limite); grupo.setEnabled(not pausada); foco.setEnabled(not pausada); aplicar.setEnabled(not pausada); salvar_preset.setEnabled(not pausada); reiniciar.setEnabled(not pausada)
        assinatura=tuple((p.get('numero'),p.get('duracao_segundos'),p.get('programado_segundos'),p.get('em_andamento'),p.get('tipo_vtime')) for p in pausas)
        if assinatura!=anterior_hist:
            anterior_hist=assinatura; tabela.setRowCount(len(pausas)); historico_stack.setCurrentWidget(tabela if pausas else vazio)
            for i,p in enumerate(pausas):
                tipo=p.get('tipo_vtime') or ('Programada' if p.get('programado_segundos') else 'Livre')
                if p.get('em_andamento'): tipo+=' · ativa'
                for j,txt in enumerate((p.get('horario_inicio','—'),tipo,formatar(p.get('programado_segundos',0)) if p.get('programado_segundos') else '—',formatar(p.get('duracao_segundos',0)))):
                    item=QTableWidgetItem(str(txt)); item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignLeft if j==1 else Qt.AlignHCenter)); item.setToolTip(str(txt))
                    if j==1:
                        item.setForeground(QBrush(QColor('#F0C780'))); item.setIcon(clock_icon if p.get('programado_segundos') else pause_icon)
                    tabela.setItem(i,j,item)
        hist_info.setText(f'{len(pausas)} pausa(s)  ·  {formatar(pausa)} descontado  ·  {formatar(bruto)} total')
    aplicar.clicked.connect(aplicar_config); salvar_preset.clicked.connect(guardar_preset); reiniciar.clicked.connect(resetar)
    principal.clicked.connect(lambda: escolher('retomar' if bateria._pausa_relogio is not None else 'manual'))
    programada.clicked.connect(lambda: escolher('programada')); adiar.clicked.connect(lambda: escolher('adiar')); livre.clicked.connect(lambda: escolher('livre'))
    foco.clicked.connect(lambda: escolher('foco')); fechar.clicked.connect(janela.reject)
    atalho=QShortcut(QKeySequence('F8'),janela); atalho.setAutoRepeat(False); atalho.activated.connect(principal.click)
    timer=QTimer(janela); timer.timeout.connect(atualizar); timer.start(250); atualizar()
    bateria._vtime_janela_painel=janela
    try: janela.exec()
    finally:
        timer.stop(); bateria._vtime_janela_painel=None
    return resultado['acao']
