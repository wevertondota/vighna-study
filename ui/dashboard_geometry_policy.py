"""M1-D1 — política pura de geometria do Dashboard Futurista.

PROTÓTIPO NÃO INTEGRADO. Não importa Qt, não conhece a janela principal,
não altera widgets, estilos, banco ou sinais. Valores mínimos são hipóteses
de projeto: precisam ser calibrados com sizeHint/minimumSizeHint medidos no
Windows antes de qualquer aplicação real.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Mode(str, Enum):
    HERO_SIDE_PAIR = "hero_side_pair"
    HERO_FULLWIDTH_PAIR = "hero_fullwidth_pair"
    SINGLE_COLUMN = "single_column"


@dataclass(frozen=True)
class CardMinimums:
    recommendation_w: int = 410
    recommendation_h: int = 340
    focus_w: int = 320
    focus_h: int = 160
    progress_w: int = 300
    progress_h: int = 210
    planning_w: int = 340
    planning_h: int = 225

    def __post_init__(self):
        for name, value in vars(self).items():
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} deve ser inteiro positivo")


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y + self.height

    def overlaps(self, other: "Rect") -> bool:
        return (self.x < other.right and self.right > other.x and
                self.y < other.bottom and self.bottom > other.y)


@dataclass(frozen=True)
class Plan:
    mode: Mode
    available_width: int
    available_height: int | None
    cards: dict[str, Rect]
    content_height: int
    needs_vertical_scroll: bool
    reasons: tuple[str, ...]

    def validate(self):
        if set(self.cards) != {"recommendation", "focus", "progress", "planning"}:
            raise AssertionError("O plano deve conservar os quatro cards")
        for name, card in self.cards.items():
            if card.width <= 0 or card.height <= 0:
                raise AssertionError(f"Dimensão inválida: {name}")
            if card.x < 0 or card.y < 0 or card.right > self.available_width:
                raise AssertionError(f"Card fora da largura útil: {name}")
        for a, ra in self.cards.items():
            for b, rb in self.cards.items():
                if a < b and ra.overlaps(rb):
                    raise AssertionError(f"Sobreposição: {a} × {b}")
        if self.content_height != max(c.bottom for c in self.cards.values()):
            raise AssertionError("Altura inconsistente")
        return True


class DashboardGeometryPolicy:
    """Define APENAS geometria externa e a escolha da composição.

    A implementação Qt futura é responsável por medir os tamanhos mínimos
    efetivos e traduzir `Plan` em layouts gerenciados por um único proprietário.
    Os `Rect`s são um ORÁCULO GEOMÉTRICO DE TESTE, não uma ordem de setGeometry.
    """

    def __init__(self, minimums: CardMinimums | None = None, gap: int = 12,
                 side_right_percent: int = 54):
        self.minimums = minimums or CardMinimums()
        if not (0 <= gap <= 64):
            raise ValueError("gap fora da faixa permitida")
        if not (40 <= side_right_percent <= 70):
            raise ValueError("Participação da coluna direita inválida")
        self.gap = gap
        self.side_right_percent = side_right_percent

    def _pair_side_columns(self, width: int) -> tuple[int, int]:
        usable = width - self.gap
        right = usable * self.side_right_percent // 100
        return usable - right, right

    def _can_side_pair(self, width: int) -> bool:
        m = self.minimums
        if width <= self.gap:
            return False
        left, right = self._pair_side_columns(width)
        return (left >= m.recommendation_w and
                right >= max(m.focus_w, m.progress_w + self.gap + m.planning_w))

    def _can_fullwidth_pair(self, width: int) -> bool:
        m = self.minimums
        if width <= self.gap:
            return False
        # Composição superior tem dois cards; inferior distribui Progresso/Plano
        # pela largura total. Não utilizamos um breakpoint de tela arbitrário.
        return (width >= m.recommendation_w + self.gap + m.focus_w and
                width >= m.progress_w + self.gap + m.planning_w)

    def choose_mode(self, content_width: int) -> Mode:
        if content_width <= 0:
            raise ValueError("Largura útil deve ser positiva")
        if self._can_side_pair(content_width):
            return Mode.HERO_SIDE_PAIR
        if self._can_fullwidth_pair(content_width):
            return Mode.HERO_FULLWIDTH_PAIR
        return Mode.SINGLE_COLUMN

    def plan(self, content_width: int, content_height: int | None = None) -> Plan:
        if not isinstance(content_width, int) or content_width <= 0:
            raise ValueError("content_width deve ser inteiro positivo")
        if content_height is not None and (not isinstance(content_height, int) or content_height <= 0):
            raise ValueError("content_height deve ser positivo ou None")
        m, g = self.minimums, self.gap
        mode = self.choose_mode(content_width)
        cards = {}
        reasons = []
        if mode == Mode.HERO_SIDE_PAIR:
            lw, rw = self._pair_side_columns(content_width)
            cards['recommendation'] = Rect(0, 0, lw, m.recommendation_h)
            cards['focus'] = Rect(lw + g, 0, rw, m.focus_h)
            pw = max(m.progress_w, (rw - g) // 2)
            plw = rw - g - pw
            if plw < m.planning_w:
                plw = m.planning_w
                pw = rw - g - plw
            y = m.focus_h + g
            cards['progress'] = Rect(lw + g, y, pw, m.progress_h)
            cards['planning'] = Rect(lw + 2 * g + pw, y, plw, m.planning_h)
            reasons.append('Coluna direita comporta Foco e dupla compacta com larguras mínimas.')
        elif mode == Mode.HERO_FULLWIDTH_PAIR:
            top_w = content_width - g
            lw = max(m.recommendation_w, top_w * 54 // 100)
            rw = top_w - lw
            if rw < m.focus_w:
                rw = m.focus_w
                lw = top_w - rw
            cards['recommendation'] = Rect(0, 0, lw, m.recommendation_h)
            cards['focus'] = Rect(lw + g, 0, rw, m.focus_h)
            y = m.recommendation_h + g
            pw = max(m.progress_w, (content_width - g) // 2)
            plw = content_width - g - pw
            if plw < m.planning_w:
                plw = m.planning_w
                pw = content_width - g - plw
            cards['progress'] = Rect(0, y, pw, m.progress_h)
            cards['planning'] = Rect(pw + g, y, plw, m.planning_h)
            reasons.append('Dupla de baixo usa a largura total para evitar compressão.')
        else:
            y = 0
            for name, height in (
                ('recommendation', m.recommendation_h),
                ('focus', m.focus_h),
                ('progress', m.progress_h),
                ('planning', m.planning_h),
            ):
                cards[name] = Rect(0, y, content_width, height)
                y += height + g
            reasons.append('Largura insuficiente: quatro cards empilhados; não comprimir conteúdo.')
            if content_width < max(m.recommendation_w, m.focus_w, m.progress_w, m.planning_w):
                reasons.append('Largura menor que um ou mais mínimos: exige ajuste interno ou rolagem horizontal.')
        used_h = max(r.bottom for r in cards.values())
        scroll = content_height is not None and used_h > content_height
        if scroll:
            reasons.append('Altura insuficiente: habilitar rolagem vertical, não truncar cards.')
        result = Plan(mode, content_width, content_height, cards, used_h, scroll, tuple(reasons))
        result.validate()
        return result
