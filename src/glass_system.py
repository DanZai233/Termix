"""
杯子系统 - 杯型选择、杯子渲染和调酒动画
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ingredient color -> Rich color name
COLOR_MAP = {
    "clear": "bright_white",
    "dark": "rgb(139,90,43)",
    "amber": "dark_orange",
    "green": "green",
    "yellow": "yellow",
    "orange": "dark_orange3",
    "red": "red",
    "blue": "dodger_blue2",
    "white": "grey93",
    "black": "grey30",
    "peach": "light_salmon1",
}


@dataclass
class GlassType:
    name: str
    emoji: str
    description: str
    capacity_ml: int
    template: List[str]
    inner_width: int
    fill_start_row: int
    fill_end_row: int


GLASSES = {
    "martini": GlassType(
        name="马提尼杯",
        emoji="🍸",
        description="经典V形鸡尾酒杯",
        capacity_ml=300,
        template=[
            "   ╲           ╱",
            "    ╲         ╱ ",
            "     ╲       ╱  ",
            "      ╲     ╱   ",
            "       ╲   ╱    ",
            "        ╲ ╱     ",
            "         │      ",
            "         │      ",
            "      ───┴───   ",
        ],
        inner_width=11,
        fill_start_row=0,
        fill_end_row=5,
    ),
    "highball": GlassType(
        name="高球杯",
        emoji="🥃",
        description="经典高杯，适合长饮",
        capacity_ml=400,
        template=[
            "   ┌─────────┐",
            "   │         │",
            "   │         │",
            "   │         │",
            "   │         │",
            "   │         │",
            "   │         │",
            "   │         │",
            "   └─────────┘",
        ],
        inner_width=9,
        fill_start_row=1,
        fill_end_row=7,
    ),
    "rocks": GlassType(
        name="岩杯",
        emoji="🥃",
        description="矮胖的威士忌杯",
        capacity_ml=300,
        template=[
            "  ╲           ╱",
            "   │         │ ",
            "   │         │ ",
            "   │         │ ",
            "   │         │ ",
            "   └─────────┘ ",
        ],
        inner_width=9,
        fill_start_row=1,
        fill_end_row=4,
    ),
    "hurricane": GlassType(
        name="飓风杯",
        emoji="🍹",
        description="热带鸡尾酒专用杯",
        capacity_ml=450,
        template=[
            "    ╲       ╱ ",
            "     │     │  ",
            "     │     │  ",
            "    ╱       ╲ ",
            "   │         │",
            "   │         │",
            "   │         │",
            "    ╲       ╱ ",
            "      │   │   ",
            "    ──┴───┴── ",
        ],
        inner_width=9,
        fill_start_row=1,
        fill_end_row=7,
    ),
    "shot": GlassType(
        name="烈酒杯",
        emoji="🥃",
        description="小巧的烈酒杯",
        capacity_ml=60,
        template=[
            "   ╲       ╱",
            "    │     │ ",
            "    │     │ ",
            "    │     │ ",
            "    └─────┘ ",
        ],
        inner_width=5,
        fill_start_row=1,
        fill_end_row=3,
    ),
}


@dataclass
class IngredientLayer:
    name: str
    amount_ml: float
    color: str
    emoji: str


def render_glass(glass_key: str, layers: List[IngredientLayer], garnishes: List[str] = None) -> str:
    """渲染杯子，包含液体层和装饰"""
    if glass_key not in GLASSES:
        glass_key = "highball"
    glass = GLASSES[glass_key]

    liquid_layers = [l for l in layers if l.amount_ml > 0]

    lines = list(glass.template)

    fill_rows = glass.fill_end_row - glass.fill_start_row + 1
    if liquid_layers and fill_rows > 0:
        total_liquid_ml = sum(l.amount_ml for l in liquid_layers)
        if total_liquid_ml <= 0:
            total_liquid_ml = 1

        fill_ratio = min(1.0, total_liquid_ml / (glass.capacity_ml * 0.5))
        filled_rows = min(fill_rows, max(1, round(fill_rows * fill_ratio)))
        row_assignments: List[Tuple[str, str]] = []

        remaining_rows = filled_rows
        for layer in liquid_layers:
            layer_rows = max(1, int(filled_rows * layer.amount_ml / total_liquid_ml))
            layer_rows = min(layer_rows, remaining_rows)
            color = COLOR_MAP.get(layer.color, "white")
            for _ in range(layer_rows):
                row_assignments.append((color, "█"))
            remaining_rows -= layer_rows
            if remaining_rows <= 0:
                break

        while len(row_assignments) < filled_rows:
            if liquid_layers:
                color = COLOR_MAP.get(liquid_layers[-1].color, "white")
            else:
                color = "white"
            row_assignments.append((color, "█"))

        row_assignments.reverse()

        for i, (color, char) in enumerate(row_assignments):
            row_idx = glass.fill_end_row - i
            if glass.fill_start_row <= row_idx <= glass.fill_end_row:
                line = lines[row_idx]
                inner_start = -1
                inner_end = -1
                for ci, c in enumerate(line):
                    if c in ("│", "╲", "╱"):
                        if inner_start == -1:
                            inner_start = ci + 1
                        else:
                            inner_end = ci
                            break
                if inner_start >= 0 and inner_end > inner_start:
                    w = inner_end - inner_start
                    fill = f"[{color}]{'█' * w}[/{color}]"
                    lines[row_idx] = line[:inner_start] + fill + line[inner_end:]

    garnish_text = ""
    if garnishes:
        garnish_text = " ".join(garnishes)

    result = ""
    if garnish_text:
        result += f"      {garnish_text}\n"
    result += "\n".join(lines)
    return result


def render_empty_glass(glass_key: str) -> str:
    """渲染空杯子"""
    return render_glass(glass_key, [])


def render_pouring_frame(glass_key: str, layers: List[IngredientLayer],
                         pouring_ingredient: IngredientLayer, frame: int) -> str:
    """渲染倒酒动画帧"""
    glass_art = render_glass(glass_key, layers)
    color = COLOR_MAP.get(pouring_ingredient.color, "white")

    drops = [
        f"     {pouring_ingredient.emoji}  🫗",
        f"       [{color}]░[/{color}]",
        f"       [{color}]▒[/{color}]",
        f"       [{color}]▓[/{color}]",
    ]

    frame_idx = frame % len(drops)
    pour_lines = drops[:frame_idx + 1]

    return "\n".join(pour_lines) + "\n" + glass_art


def get_glass_list() -> List[Tuple[str, GlassType]]:
    """获取所有杯型"""
    return list(GLASSES.items())
