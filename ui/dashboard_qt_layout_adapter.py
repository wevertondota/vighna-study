"""M1-D2 — adaptador experimental de composição do Dashboard.

NÃO INTEGRADO AO VIGHNASTUDY. Recebe quatro widgets Qt existentes e um
QGridLayout já anexado a um QWidget dedicado. Seu único propósito é decidir
quais widgets vão a cada célula. Não modifica conteúdo, sinais, QSS, banco,
fontes, text labels nem min/max heights. Nenhuma referência a main.py.

Compatível com testes usando layouts falsos (sem importação obrigatória do Qt).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .dashboard_geometry_policy import DashboardGeometryPolicy, Mode

CARD_NAMES = ("recommendation", "focus", "progress", "planning")

# grid_row, grid_column, rowspan, colspan
POSITIONS = {
    Mode.HERO_SIDE_PAIR: {
        "recommendation": (0, 0, 2, 1),
        "focus": (0, 1, 1, 2),
        "progress": (1, 1, 1, 1),
        "planning": (1, 2, 1, 1),
    },
    Mode.HERO_FULLWIDTH_PAIR: {
        "recommendation": (0, 0, 1, 1),
        "focus": (0, 1, 1, 1),
        "progress": (1, 0, 1, 1),
        "planning": (1, 1, 1, 1),
    },
    Mode.SINGLE_COLUMN: {
        "recommendation": (0, 0, 1, 1),
        "focus": (1, 0, 1, 1),
        "progress": (2, 0, 1, 1),
        "planning": (3, 0, 1, 1),
    },
}

# Qt GridLayout weights; no hard-coded pixels, no setGeometry.
WEIGHTS = {
    Mode.HERO_SIDE_PAIR: (46, 27, 27),
    Mode.HERO_FULLWIDTH_PAIR: (54, 46, 0),
    Mode.SINGLE_COLUMN: (1, 0, 0),
}


@dataclass(frozen=True)
class ApplyResult:
    mode: Mode
    changed: bool
    card_count: int


class DashboardGridAdapter:
    """Somente dono do posicionamento externo dos quatro cards.

    PRECONDIÇÕES de integração:
    - `grid` é QGridLayout de host dedicado e não possui itens estranhos;
    - cada widget já foi retirado de seu layout anterior com removeWidget();
    - alturas fixas legadas são neutralizadas POR OUTRA ETAPA auditada;
    - o host encontra-se dentro de área rolável quando necessário.

    Em modo off-line aceita QGridLayout fake com takeAt(), addWidget(), etc.
    """

    def __init__(self, grid, widgets: Mapping[str, object], *, gap=12,
                 policy: DashboardGeometryPolicy | None = None):
        if set(widgets) != set(CARD_NAMES):
            raise ValueError("São obrigatórios exatamente os quatro cards")
        if len({id(v) for v in widgets.values()}) != 4:
            raise ValueError("Cada card deve ser um QWidget distinto")
        if any(v is None for v in widgets.values()):
            raise ValueError("Cards ausentes")
        self.grid = grid
        self.widgets = dict(widgets)
        self.policy = policy or DashboardGeometryPolicy(gap=gap)
        self.gap = gap
        self._mode = None
        self._history: list[Mode] = []
        self.grid.setSpacing(gap)
        self.grid.setContentsMargins(0, 0, 0, 0)

    @property
    def mode(self):
        return self._mode

    def apply_width(self, content_width: int) -> ApplyResult:
        """Largura útil REAL do host, não largura global da janela."""
        mode = self.policy.choose_mode(content_width)
        return self.apply_mode(mode)

    def apply_mode(self, mode: Mode) -> ApplyResult:
        mode = Mode(mode)
        if self._mode == mode:
            return ApplyResult(mode, False, 4)

        # Não destruir widgets Qt. takeAt() remove os QLayoutItems e apenas
        # devolve as referências já existentes à estrutura visual.
        while self.grid.count():
            self.grid.takeAt(0)
        for name in CARD_NAMES:
            self.grid.addWidget(self.widgets[name], *POSITIONS[mode][name])
        weights = WEIGHTS[mode]
        for col, weight in enumerate(weights):
            self.grid.setColumnStretch(col, weight)
        # Preferir conteúdo no topo, sem esticar espaços verticais vazios.
        for row in range(4):
            self.grid.setRowStretch(row, 0)
        self.grid.invalidate()
        self._mode = mode
        self._history.append(mode)
        return ApplyResult(mode, True, 4)

    def assert_identity(self, original_widgets):
        return all(self.widgets[n] is original_widgets[n] for n in CARD_NAMES)
