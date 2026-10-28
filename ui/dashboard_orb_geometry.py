"""O02 — geometria pura das 3 regiões do Dashboard (sem PySide6).

Contrato: reproduz o `paintEvent` de `DashboardAmbientCanvas` 0.29.59.
NÃO modifica GIF, widgets, banco, animação, cards ou eventos de mouse.
Alvos recalibrados para o GIF Vighna Tratamento Cromatico A/B, 200 quadros.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h


@dataclass(frozen=True)
class Ellipse:
    cx: float
    cy: float
    rx: float
    ry: float

    def contains(self, x: float, y: float) -> bool:
        return ((x - self.cx) / self.rx) ** 2 + ((y - self.cy) / self.ry) ** 2 <= 1.0


@dataclass(frozen=True)
class Hotspot:
    key: str
    circle: Ellipse
    label: Rect | None
    accessible_name: str

    def contains_source(self, x: float, y: float) -> bool:
        if self.circle.contains(x, y):
            return True
        l = self.label
        return l is not None and l.x <= x <= l.right and l.y <= y <= l.bottom


# Coordenadas de desenho na ARTE original (1300x715), NÃO da janela.
# Planejamento e Foco incluem a etiqueta abaixo do anel; centro contém sua própria legenda.
HOTSPOTS_1300x715 = (
    Hotspot('planejamento', Ellipse(183.0, 260.0, 76.0, 78.0),
            Rect(102.0, 326.0, 170.0, 39.0), 'Abrir Planejamento'),
    Hotspot('recomendacao', Ellipse(464.0, 285.0, 101.0, 101.0),
            None, 'Abrir Recomendação'),
    Hotspot('foco', Ellipse(730.0, 262.0, 77.0, 79.0),
            Rect(651.0, 326.0, 163.0, 39.0), 'Abrir Modo Foco'),
)
ART_WIDTH, ART_HEIGHT = 1300.0, 715.0


@dataclass(frozen=True)
class CoverGeometry:
    source: Rect
    dest: Rect
    art_width: float
    art_height: float
    canvas_width: int
    canvas_height: int

    def to_view(self, source_x: float, source_y: float) -> tuple[float, float]:
        return (
            self.dest.x + (source_x - self.source.x) * self.dest.w / self.source.w,
            self.dest.y + (source_y - self.source.y) * self.dest.h / self.source.h,
        )

    def to_source(self, view_x: float, view_y: float) -> tuple[float, float] | None:
        # Tolerância só para arredondamento de ponto flutuante na borda.
        eps = 1e-9
        if not (self.dest.x - eps <= view_x <= self.dest.right + eps
                and self.dest.y - eps <= view_y <= self.dest.bottom + eps):
            return None
        x = min(self.dest.right, max(self.dest.x, view_x))
        y = min(self.dest.bottom, max(self.dest.y, view_y))
        return (
            self.source.x + (x - self.dest.x) * self.source.w / self.dest.w,
            self.source.y + (y - self.dest.y) * self.source.h / self.dest.h,
        )


def cover_geometry(canvas_width: int, canvas_height: int,
                   art_width: float = ART_WIDTH, art_height: float = ART_HEIGHT) -> CoverGeometry:
    """Reproduz literalmente o cálculo atual do main.py (sem Qt).

    `_altura_painel = min(self.height(), max(690, int(self.width() * 0.55)))`.
    Pixels em coordenadas **lógicas Qt**, nunca screen/global ou físicas do monitor.
    """
    w, h = int(canvas_width), int(canvas_height)
    sw, sh = float(art_width), float(art_height)
    if w < 1 or h < 1 or not (isfinite(sw) and isfinite(sh) and sw > 0 and sh > 0):
        raise ValueError('Canvas e imagem devem ter dimensões positivas.')
    panel_height = min(h, max(690, int(w * 0.55)))
    dest = Rect(0.0, 0.0, float(w), float(panel_height))
    dest_ratio = w / panel_height
    image_ratio = sw / sh
    if image_ratio > dest_ratio:
        cropped_width = sh * dest_ratio
        src = Rect((sw - cropped_width) / 2.0, 0.0, cropped_width, sh)
    else:
        cropped_height = sw / dest_ratio
        src = Rect(0.0, (sh - cropped_height) / 2.0, sw, cropped_height)
    return CoverGeometry(src, dest, sw, sh, w, h)


def region_in_image(hotspot: Hotspot, geom: CoverGeometry,
                    view_x: float, view_y: float) -> bool:
    """Hit-test sem área retangular invisível cobrindo o HUD.

    Alvos são definidos em unidades da arte de referência e convertidos em caso
    de fonte com resolução diferente. O recorte é conferido antes do hit-test.
    """
    coords = geom.to_source(view_x, view_y)
    if coords is None:
        return False
    x, y = coords
    return hotspot.contains_source(x * ART_WIDTH / geom.art_width,
                                   y * ART_HEIGHT / geom.art_height)


def target_center(hotspot: Hotspot, geom: CoverGeometry) -> tuple[float, float]:
    return geom.to_view(hotspot.circle.cx * geom.art_width / ART_WIDTH,
                        hotspot.circle.cy * geom.art_height / ART_HEIGHT)


def visible_circle_fraction(hotspot: Hotspot, geom: CoverGeometry, grid: int = 101) -> float:
    """Amostragem determinística da fração visível da esfera (sem etiquetas).

    Útil ao O03 para propor fallback acessível; não equivale a detecção de
    oclusão por widgets Qt sobrepostos nem considera a visibilidade do viewport
    do QScrollArea, a serem inspecionados no Windows.
    """
    if grid < 2:
        raise ValueError('grid mínimo 2')
    c = hotspot.circle
    src = geom.source
    scale_x, scale_y = geom.art_width / ART_WIDTH, geom.art_height / ART_HEIGHT
    inside = visible = 0
    for yi in range(grid):
        y = c.cy - c.ry + (2.0 * c.ry) * (yi + 0.5) / grid
        for xi in range(grid):
            x = c.cx - c.rx + (2.0 * c.rx) * (xi + 0.5) / grid
            if c.contains(x, y):
                inside += 1
                sx, sy = x * scale_x, y * scale_y
                if src.x <= sx <= src.right and src.y <= sy <= src.bottom:
                    visible += 1
    return visible / inside if inside else 0.0


def all_target_status(canvas_width: int, canvas_height: int) -> dict:
    geom = cover_geometry(canvas_width, canvas_height)
    return {
        'canvas': {'width': canvas_width, 'height': canvas_height},
        'source_rect': vars(geom.source),
        'dest_rect': vars(geom.dest),
        'targets': {
            hs.key: {
                'center_view': [round(v, 2) for v in target_center(hs, geom)],
                'visible_circle_fraction': round(visible_circle_fraction(hs, geom), 4),
                'eligible_for_full_target': visible_circle_fraction(hs, geom) >= 0.80,
                'accessible_name': hs.accessible_name,
            }
            for hs in HOTSPOTS_1300x715
        },
    }
