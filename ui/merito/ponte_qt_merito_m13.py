"""M13/M25 — ponte Qt com modos laboratório e produção validada.

NENHUMA consulta SQLite na thread visual. Eventos acionam um QTimer com
singleShot; a apuração M09/M10/M11 roda em QRunnable no QThreadPool; a entrega
é um Signal ligado a métodos de QObject na thread do aplicativo.

Importar este arquivo exige PySide6. No main.py, o import é feito somente
quando o controlador habilita escopo de clone ou de produção validado.
"""
from __future__ import annotations
from PySide6.QtCore import (QObject, QRunnable, QThread, QThreadPool, QTimer,
                            Signal, Slot, QCoreApplication, Qt)
from .despachante_merito_m13 import DespachanteMeritoM13
from .integracao_merito_m11 import EscopoM11
from .fluxo_merito_m13 import apurar_no_worker_m13

class _EmissorResultadosM13(QObject):
    concluiu = Signal(object, object)
    falhou = Signal(object, str)

class _TrabalhoM13(QRunnable):
    """Não acessa QWidget, QSettings nem controlador principal."""
    def __init__(self, requisicao, escopo, emissor):
        super().__init__()
        self.requisicao = requisicao
        self.escopo = escopo
        self.emissor = emissor

    def run(self):
        try:
            resultado = apurar_no_worker_m13(self.escopo)
        except Exception as exc:
            try:
                self.emissor.falhou.emit(self.requisicao, type(exc).__name__)
            except RuntimeError:
                pass  # aplicação fechada; nenhuma publicação posterior
        else:
            try:
                self.emissor.concluiu.emit(self.requisicao, resultado)
            except RuntimeError:
                pass

class PonteMeritoQtM13(QObject):
    """Criar SOMENTE na thread GUI, com escopo certificado previamente.

    O objeto `controlador` oferece os métodos M08 existentes e não deve ser
    modificado pelo worker. É responsável por excluir a ponte no fechamento.
    """
    def __init__(self, controlador, escopo: EscopoM11, *, clone_autorizado=False,
                 debounce_ms=550):
        if not isinstance(escopo, EscopoM11):
            raise RuntimeError('Escopo de mérito inválido')
        if escopo.modo == 'laboratorio':
            if clone_autorizado is not True:
                raise RuntimeError('M13 laboratório exige clone autorizado')
        elif escopo.modo == 'producao':
            if clone_autorizado is True:
                raise RuntimeError('Não confundir clone autorizado com produção')
            from .ativacao_producao_m25 import validar_escopo_producao_m25
            validar_escopo_producao_m25(escopo)
        else:
            raise RuntimeError('Ponte Qt sem escopo ativo')
        app = QCoreApplication.instance()
        if app is None or QThread.currentThread() != app.thread():
            raise RuntimeError('Ponte de mérito precisa ser criada na thread Qt principal')
        if type(debounce_ms) is not int or not 200 <= debounce_ms <= 5000:
            raise ValueError('Debounce M13 fora do intervalo seguro')
        if not callable(getattr(controlador, '_m08_publicar_integracao_auditada', None)) or not callable(
            getattr(controlador, '_m08_invalidar_merito_global', None)):
            raise TypeError('Controlador central M08 incompatível')
        super().__init__(controlador)
        self._controlador = controlador
        self._escopo = escopo
        self._despachante = DespachanteMeritoM13(escopo.perfil_id)
        self._pool = QThreadPool.globalInstance()
        self._emissor = _EmissorResultadosM13(self)
        self._emissor.concluiu.connect(self._ao_concluir, Qt.QueuedConnection)
        self._emissor.falhou.connect(self._ao_falhar, Qt.QueuedConnection)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(debounce_ms)
        self._timer.timeout.connect(self._iniciar_trabalho)
        self._despachante.solicitar_inicial()
        self._agendar()

    def _na_gui(self):
        app = QCoreApplication.instance()
        if app is None or QThread.currentThread() != app.thread():
            raise RuntimeError('Evento M13 fora da thread Qt principal')

    def _agendar(self):
        if self._despachante.tem_pendencias and not self._despachante.ocupado:
            self._timer.start()

    def registrar_tentativa(self, tentativa_id: int, *, simulado_aberto: bool,
                            sem_impacto: bool = False) -> bool:
        self._na_gui()
        mudou = self._despachante.registrar_tentativa(
            tentativa_id, commit_ok=True,
            sem_impacto=sem_impacto, simulado_aberto=simulado_aberto)
        if mudou:
            self._agendar()
        return mudou

    def simulado_entregue(self, *, concluida: bool, commit_ok: bool) -> bool:
        self._na_gui()
        mudou = self._despachante.simulado_entregue(
            concluida=concluida, commit_ok=commit_ok)
        if mudou:
            self._agendar()
        return mudou

    @Slot()
    def _iniciar_trabalho(self):
        self._na_gui()
        requisicao = self._despachante.iniciar()
        if requisicao is not None:
            try:
                self._pool.start(_TrabalhoM13(requisicao, self._escopo, self._emissor))
            except Exception:
                self.revogar('Não foi possível iniciar a apuração de mérito')

    @Slot(object, object)
    def _ao_concluir(self, requisicao, resultado):
        self._na_gui()
        try:
            situacao = self._despachante.concluir(
                requisicao, resultado, self._controlador._m08_publicar_integracao_auditada)
        except Exception:
            self.revogar('Falha ao publicar mérito auditado')
            return
        # Se uma questão foi respondida enquanto o worker lia o banco, o
        # resultado anterior é descartado e um lote novo será calculado.
        if situacao in ('obsoleto', 'publicado'):
            self._agendar()

    @Slot(object, str)
    def _ao_falhar(self, requisicao, classe_erro):
        self._na_gui()
        if self._despachante.falhar(requisicao):
            self.revogar('Histórico de mérito não pôde ser revalidado')

    def revogar(self, motivo='Integração M13 suspensa'):
        self._na_gui()
        self._timer.stop()
        self._despachante.revogar()
        # Nunca alterar dados acadêmicos, nem eliminar conquistas duráveis.
        self._controlador._m08_invalidar_merito_global(motivo)

    @property
    def revogado(self):
        return self._despachante.revogado
