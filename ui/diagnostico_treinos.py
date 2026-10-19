"""Watchdog temporário da navegação Simulados/Treinos (somente diagnóstico).

Não interage com Qt, banco de dados, registro do Windows nem conteúdo de questões.
O temporizador de interface chama ``pulso``. Uma thread daemon registra a pilha
Python caso não exista pulso por cinco segundos durante a janela de observação.
"""
from __future__ import annotations

import faulthandler
import os
from pathlib import Path
import tempfile
import threading
import time


class MonitorNavegacaoTreinos:
    DURACAO = 18.0
    LIMIAR = 5.0

    def __init__(self):
        agora = time.monotonic()
        self._inicio = agora
        self._ultimo_pulso = agora
        self._etapa = "iniciando"
        self._encerrou = threading.Event()
        self._registrou = False
        self._thread = threading.Thread(
            target=self._vigiar, name="VighnaTreinosDiagnostico", daemon=True,
        )
        self._thread.start()

    @property
    def ativo(self):
        return not self._encerrou.is_set() and time.monotonic() - self._inicio < self.DURACAO

    def marcar(self, etapa):
        self._etapa = str(etapa)
        self._ultimo_pulso = time.monotonic()

    def pulso(self):
        self._ultimo_pulso = time.monotonic()

    def encerrar(self):
        self._encerrou.set()

    @staticmethod
    def caminho_log():
        base = os.environ.get("LOCALAPPDATA") or tempfile.gettempdir()
        return Path(base) / "VighnaStudy" / "diagnosticos" / "treinos_travamento.log"

    def _vigiar(self):
        while self.ativo:
            if self._encerrou.wait(0.3):
                return
            agora = time.monotonic()
            sem_resposta = agora - self._ultimo_pulso
            if sem_resposta < self.LIMIAR or self._registrou:
                continue
            self._registrou = True
            try:
                caminho = self.caminho_log()
                caminho.parent.mkdir(parents=True, exist_ok=True)
                # Evita expansão ilimitada do arquivo entre sessões.
                if caminho.exists() and caminho.stat().st_size > 500_000:
                    caminho.unlink()
                with caminho.open("a", encoding="utf-8") as saida:
                    saida.write("\n=== Possível bloqueio na Central de Treinos ===\n")
                    saida.write(f"Data UTC: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}\n")
                    saida.write(f"Sem resposta: {sem_resposta:.2f}s | etapa: {self._etapa}\n")
                    saida.write("Pilhas das threads Python:\n")
                    saida.flush()
                    faulthandler.dump_traceback(file=saida, all_threads=True)
                    saida.write("=== Fim do diagnóstico ===\n")
            except (OSError, RuntimeError, ValueError):
                # O diagnóstico nunca pode interromper a sessão acadêmica.
                pass
