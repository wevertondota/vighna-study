"""T01: observador contínuo de travamento na bateria (somente diagnóstico).

Nenhuma chamada Qt, SQLite ou leitura de questões ocorre na thread observadora.
Um QTimer da GUI, controlado em main.py, chama pulso() periodicamente. Quando
o pulso para por 5 segundos, a thread grava as pilhas Python no log local.
"""
from __future__ import annotations

import faulthandler
import os
import re
import tempfile
import threading
import time
from pathlib import Path


class MonitorTravamentoBateria:
    LIMIAR_SEGUNDOS = 5.0
    INTERVALO_VERIFICACAO = 0.3
    TAMANHO_MAXIMO_LOG = 1_500_000

    def __init__(self):
        self._lock = threading.Lock()
        self._encerrar = threading.Event()
        self._ultimo_pulso = time.monotonic()
        self._etapa = 'sessao_iniciada'
        self._em_bloqueio = False
        self._thread = threading.Thread(
            target=self._vigiar,
            name='VighnaT01BateriaWatchdog',
            daemon=True,
        )
        self._log_evento('monitor_iniciado')
        self._thread.start()

    @staticmethod
    def caminho_log():
        base = os.environ.get('LOCALAPPDATA') or tempfile.gettempdir()
        return Path(base) / 'VighnaStudy' / 'diagnosticos' / 'bateria_travamentos_t01.log'

    @staticmethod
    def _limpar_evento(nome):
        # Somente etiquetas técnicas explícitas; nunca conteúdo da questão.
        return re.sub(r'[^a-zA-Z0-9:_-]', '_', str(nome))[:90]

    def _abrir_log(self):
        path = self.caminho_log()
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_file() and path.stat().st_size >= self.TAMANHO_MAXIMO_LOG:
            anterior = path.with_suffix('.1.log')
            os.replace(path, anterior)
        return path.open('a', encoding='utf-8', buffering=1)

    def _log_evento(self, evento):
        try:
            with self._abrir_log() as saida:
                instante = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                saida.write(f'{instante} | {self._limpar_evento(evento)}\n')
        except (OSError, ValueError, RuntimeError):
            # Falha do diagnóstico nunca deve interromper uma sessão.
            pass

    def registrar(self, evento):
        evento = self._limpar_evento(evento)
        with self._lock:
            self._etapa = evento
        self._log_evento(evento)

    def marcar(self, etapa):
        with self._lock:
            self._etapa = self._limpar_evento(etapa)

    def pulso(self):
        agora = time.monotonic()
        recuperado = False
        with self._lock:
            self._ultimo_pulso = agora
            if self._em_bloqueio:
                self._em_bloqueio = False
                recuperado = True
        if recuperado:
            self._log_evento('interface_recuperada')

    def parar(self):
        if self._encerrar.is_set():
            return
        self._encerrar.set()
        self._log_evento('monitor_encerrado')

    def _vigiar(self):
        while not self._encerrar.wait(self.INTERVALO_VERIFICACAO):
            with self._lock:
                sem_pulso = time.monotonic() - self._ultimo_pulso
                if sem_pulso < self.LIMIAR_SEGUNDOS or self._em_bloqueio:
                    continue
                self._em_bloqueio = True
                etapa = self._etapa
            try:
                with self._abrir_log() as saida:
                    instante = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                    saida.write('\n=== T01 POSSIVEL BLOQUEIO DE INTERFACE ===\n')
                    saida.write(f'UTC: {instante} | sem pulso: {sem_pulso:.2f}s | etapa: {etapa}\n')
                    saida.write('Pilhas das threads Python:\n')
                    saida.flush()
                    faulthandler.dump_traceback(file=saida, all_threads=True)
                    saida.write('=== FIM T01 ===\n')
            except (OSError, RuntimeError, ValueError):
                pass
