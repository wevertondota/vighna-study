"""Fases visuais do atualizador; não executa nem altera a transação."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class UpdatePhase:
    name: str
    detail: str
    begin_at: int


PHASES = (
    UpdatePhase('Aguardar fechamento', 'O Vighna encerra a sessão anterior com segurança.', 0),
    UpdatePhase('Validar pacote e banco', 'Compatibilidade e integridade são conferidas.', 5),
    UpdatePhase('Criar backup', 'Uma cópia verificada protege seus estudos.', 14),
    UpdatePhase('Preparar arquivos', 'O código é preparado sem copiar o banco para a compilação.', 25),
    UpdatePhase('Compilar nova versão', 'O executável é gerado em uma pasta isolada.', 38),
    UpdatePhase('Validar compilação', 'A saída é conferida antes da substituição.', 73),
    UpdatePhase('Instalar atualização', 'O executável anterior fica disponível para recuperação.', 82),
    UpdatePhase('Verificar instalação', 'Banco, versão e executável são conferidos.', 93),
    UpdatePhase('Concluir atualização', 'A confirmação final libera a reabertura.', 100),
)


def phase_for_progress(progress):
    """Identifica fases a partir dos eventos do motor, não do tempo decorrido."""
    value = max(0, min(100, int(progress)))
    for index in range(len(PHASES) - 1, -1, -1):
        if value >= PHASES[index].begin_at:
            return index
    return 0


class UpdatePhaseState:
    """Modelo monotônico: estados pending/active/done/error, sem progresso fictício."""
    def __init__(self):
        self.current = 0
        self.finished = False
        self.failed = False

    @property
    def completed(self):
        return len(PHASES) if self.finished and not self.failed else self.current

    def observe(self, progress, message=''):
        if self.finished or self.failed:
            return
        # Evento de rollback não deve avançar para a fase de verificação.
        if int(progress) == 95 and 'restaurando' in str(message).lower():
            return
        self.current = max(self.current, phase_for_progress(progress))

    def succeed(self):
        if self.failed:
            raise ValueError('Uma atualização com erro não pode ser concluída.')
        self.current = len(PHASES) - 1
        self.finished = True

    def fail(self):
        if not self.finished:
            self.failed = True

    def state_at(self, index):
        if not 0 <= index < len(PHASES):
            raise IndexError(index)
        if self.finished:
            return 'done'
        if index < self.current:
            return 'done'
        if index == self.current:
            return 'error' if self.failed else 'active'
        return 'pending'
