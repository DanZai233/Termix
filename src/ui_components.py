"""
UI组件模块 - 全新响应式游戏界面
"""

import asyncio
from typing import Dict, List

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Button, Label
from textual.message import Message
from textual.events import Key
from rich.table import Table
from rich.panel import Panel
from rich.align import Align

from .character import BunnyGirl
from .glass_system import (
    GLASSES, render_glass, render_empty_glass, render_pouring_frame,
    IngredientLayer, COLOR_MAP, get_glass_list,
)


# ──────────────── 消息类 ────────────────

class StartMixingMessage(Message):
    def __init__(self, ingredients):
        super().__init__()
        self.ingredients = ingredients

class StartRecipeMixingMessage(Message):
    def __init__(self, recipe):
        super().__init__()
        self.recipe = recipe

class ShowRecipeDetailsMessage(Message):
    def __init__(self, recipe, details):
        super().__init__()
        self.recipe = recipe
        self.details = details


# ──────────────── 欢迎界面 ────────────────

class WelcomeScreen(Container):
    def compose(self) -> ComposeResult:
        bunny = BunnyGirl()
        art = bunny.get_ascii_art("happy", 0)
        yield Static(Align.center(art), id="welcome-art")
        yield Static(Align.center("🍸 [bold cyan]Termix[/bold cyan] 🍸"), id="welcome-title")
        yield Static(Align.center("[italic]终端调酒游戏 ─ 与可爱的兔女郎一起调酒[/italic]"), id="welcome-subtitle")
        yield Static(Align.center(
            "🐰 与调酒师小兔互动  🍹 18种经典鸡尾酒配方\n"
            "✨ 选择杯型 & 调酒动画  ⌨️  全键盘操作支持"
        ), id="welcome-intro")
        yield Button("🚀 开始游戏", variant="success", id="start_game")


# ──────────────── 材料选择视图 ────────────────

class IngredientsView(Container):
    """材料浏览和选择"""

    def __init__(self, cocktail_system, **kwargs):
        super().__init__(**kwargs)
        self.cs = cocktail_system
        self.selected: Dict[str, float] = {}
        self.page = 0
        self.per_page = 6
        self.focus_idx = 0

    def compose(self) -> ComposeResult:
        yield Label("🧪 选择调酒材料  [dim](1-6选择 A/D翻页 C清空 Enter调酒)[/dim]", classes="section-title")
        with ScrollableContainer(id="ingredients-table-area"):
            yield Static("", id="ing-table")
        with Horizontal(classes="page-nav"):
            yield Button("⬅ 上页(A)", id="ing-prev")
            yield Static("", id="ing-page-info")
            yield Button("➡ 下页(D)", id="ing-next")
        with Horizontal(classes="ingredient-btns"):
            for i in range(6):
                yield Button("", id=f"ing-btn-{i}")
        yield Label("📊 当前选择:", classes="section-title")
        with ScrollableContainer(id="selected-area"):
            yield Static("", id="ing-selected")
        with Horizontal(classes="action-row"):
            yield Button("🗑️ 清空(C)", variant="error", id="ing-clear")
            yield Button("🍸 去调酒台(Enter)", variant="success", id="ing-go-mix")

    def on_mount(self):
        self._refresh()

    def _total_pages(self):
        return max(1, (len(self.cs.get_available_ingredients()) + self.per_page - 1) // self.per_page)

    def _current_items(self):
        items = self.cs.get_available_ingredients()
        start = self.page * self.per_page
        return items[start:start + self.per_page]

    def _refresh(self):
        items = self._current_items()
        total = self._total_pages()

        tbl = Table(show_header=True, header_style="bold magenta", expand=True)
        tbl.add_column("#", width=2)
        tbl.add_column("材料", min_width=10)
        tbl.add_column("类型", width=6)
        tbl.add_column("度数", width=5)
        tbl.add_column("风味", min_width=10)

        for i, ing in enumerate(items):
            style = "bold white on dark_blue" if i == self.focus_idx else ""
            tbl.add_row(
                str(i + 1),
                f"{ing.emoji} {ing.name}",
                ing.type.value,
                f"{ing.alcohol_content:.0f}%",
                ", ".join(ing.flavor_profile[:3]),
                style=style,
            )

        self.query_one("#ing-table", Static).update(tbl)
        self.query_one("#ing-page-info", Static).update(f"第 {self.page + 1} 页 / 共 {total} 页")

        for i in range(6):
            btn = self.query_one(f"#ing-btn-{i}", Button)
            if i < len(items):
                ing = items[i]
                btn.label = f"{i+1}. {ing.emoji}{ing.name[:6]}"
                btn.display = True
                btn.variant = "primary" if i == self.focus_idx else "default"
            else:
                btn.display = False

        self.query_one("#ing-prev", Button).disabled = self.page <= 0
        self.query_one("#ing-next", Button).disabled = self.page >= total - 1

        self._refresh_selection()

    def _refresh_selection(self):
        if not self.selected:
            txt = "[dim]还未选择材料\n\n快捷键: 1-6选择  A/D翻页  C清空  Enter调酒[/dim]"
        else:
            parts = []
            vol = 0
            alc = 0
            for name, amount in self.selected.items():
                ing = self.cs.ingredients.get(name)
                if ing:
                    parts.append(f"  {ing.emoji} {name}: {amount:.0f}ml")
                    vol += amount
                    alc += ing.alcohol_content * amount / 100
                else:
                    parts.append(f"  {name}: {amount:.0f}ml")
                    vol += amount
            avg = alc / vol * 100 if vol > 0 else 0
            txt = "[bold]已选材料:[/bold]\n" + "\n".join(parts)
            txt += f"\n\n总量: {vol:.0f}ml  酒精度: {avg:.1f}%"
        self.query_one("#ing-selected", Static).update(txt)

    def _toggle(self, idx: int):
        items = self._current_items()
        if idx >= len(items):
            return
        ing = items[idx]
        if ing.name in self.selected:
            self.selected[ing.name] += 15
            if self.selected[ing.name] > 200:
                del self.selected[ing.name]
        else:
            self.selected[ing.name] = 30
        self.focus_idx = idx
        self._refresh()

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id
        if bid == "ing-prev" and self.page > 0:
            self.page -= 1
            self.focus_idx = 0
            self._refresh()
        elif bid == "ing-next" and self.page < self._total_pages() - 1:
            self.page += 1
            self.focus_idx = 0
            self._refresh()
        elif bid and bid.startswith("ing-btn-"):
            self._toggle(int(bid.split("-")[-1]))
        elif bid == "ing-clear":
            self.selected.clear()
            self._refresh()
        elif bid == "ing-go-mix":
            if self.selected:
                self.app.query_one("#game", GameScreen)._show_view("mixing")
                mixing = self.app.query_one("#mixing-view", MixingStationView)
                mixing.import_ingredients(self.selected.copy())

    def on_key(self, event: Key):
        key = event.key
        if key in ("1", "2", "3", "4", "5", "6"):
            self._toggle(int(key) - 1)
        elif key in ("a", "left"):
            if self.page > 0:
                self.page -= 1
                self.focus_idx = 0
                self._refresh()
        elif key in ("d", "right"):
            if self.page < self._total_pages() - 1:
                self.page += 1
                self.focus_idx = 0
                self._refresh()
        elif key == "c":
            self.selected.clear()
            self._refresh()
        elif key == "up":
            if self.focus_idx > 0:
                self.focus_idx -= 1
                self._refresh()
        elif key == "down":
            items = self._current_items()
            if self.focus_idx < len(items) - 1:
                self.focus_idx += 1
                self._refresh()
        elif key == "enter":
            if self.selected:
                self.app.query_one("#game", GameScreen)._show_view("mixing")
                mixing = self.app.query_one("#mixing-view", MixingStationView)
                mixing.import_ingredients(self.selected.copy())


# ──────────────── 配方视图 ────────────────

class RecipesView(Container):
    """配方浏览"""

    def __init__(self, cocktail_system, **kwargs):
        super().__init__(**kwargs)
        self.cs = cocktail_system
        self.page = 0
        self.per_page = 4

    def compose(self) -> ComposeResult:
        yield Label("📖 配方图鉴  [dim](1-4查看详情 A/D翻页)[/dim]", classes="section-title")
        with ScrollableContainer(id="recipe-list-area"):
            yield Static("", id="recipe-list")
        with Horizontal(classes="recipe-nav"):
            yield Button("⬅ 上页(A)", id="rcp-prev")
            yield Static("", id="rcp-page")
            yield Button("➡ 下页(D)", id="rcp-next")

    def on_mount(self):
        self._refresh()

    def _total_pages(self):
        return max(1, (len(self.cs.get_unlocked_recipes()) + self.per_page - 1) // self.per_page)

    def _refresh(self):
        recipes = self.cs.get_unlocked_recipes()
        total = self._total_pages()
        start = self.page * self.per_page
        current = recipes[start:start + self.per_page]

        content = ""
        for i, r in enumerate(current, 1):
            ingredients_str = ", ".join(
                [f"{n}({a}ml)" for n, a in list(r.ingredients.items())[:4]]
            )
            if len(r.ingredients) > 4:
                ingredients_str += f" +{len(r.ingredients)-4}种"
            content += f"\n[bold cyan]{i}. {r.emoji} {r.name}[/bold cyan]  {'⭐' * r.difficulty}\n"
            content += f"   {r.description}\n"
            content += f"   [dim]风味: {', '.join(r.flavor_tags)}[/dim]\n"
            content += f"   材料: {ingredients_str}\n"

        self.query_one("#recipe-list", Static).update(content or "[dim]没有配方[/dim]")
        self.query_one("#rcp-page", Static).update(f"第 {self.page + 1}/{total} 页")
        self.query_one("#rcp-prev", Button).disabled = self.page <= 0
        self.query_one("#rcp-next", Button).disabled = self.page >= total - 1

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id
        if bid == "rcp-prev" and self.page > 0:
            self.page -= 1
            self._refresh()
        elif bid == "rcp-next" and self.page < self._total_pages() - 1:
            self.page += 1
            self._refresh()

    def on_key(self, event: Key):
        key = event.key
        if key in ("a", "left") and self.page > 0:
            self.page -= 1
            self._refresh()
        elif key in ("d", "right") and self.page < self._total_pages() - 1:
            self.page += 1
            self._refresh()
        elif key in ("1", "2", "3", "4"):
            idx = int(key) - 1
            recipes = self.cs.get_unlocked_recipes()
            start = self.page * self.per_page
            if start + idx < len(recipes):
                recipe = recipes[start + idx]
                self._use_recipe(recipe)

    def _use_recipe(self, recipe):
        """将配方导入调酒台"""
        self.app.query_one("#game", GameScreen)._show_view("mixing")
        mixing = self.app.query_one("#mixing-view", MixingStationView)
        mixing.import_ingredients(dict(recipe.ingredients))
        self.app.notify(f"已导入配方: {recipe.emoji} {recipe.name}", title="📖 配方导入")


# ──────────────── 调酒台视图 ────────────────

class MixingStationView(Container):
    """调酒台 - 杯型选择 + 可视化调酒"""

    def __init__(self, cocktail_system, bunny_girl, **kwargs):
        super().__init__(**kwargs)
        self.cs = cocktail_system
        self.bunny = bunny_girl
        self.glass_key = "highball"
        self.ingredients: Dict[str, float] = {}
        self.is_mixing = False
        self.ing_page = 0
        self.ing_per_page = 6

    def compose(self) -> ComposeResult:
        yield Label("🍸 调酒台  [dim](选杯→加材料→调酒)[/dim]", classes="section-title")
        with Horizontal(classes="glass-bar"):
            for key, g in get_glass_list():
                yield Button(f"{g.emoji} {g.name}", id=f"glass-{key}")
        with Horizontal(id="mixing-layout"):
            with ScrollableContainer(id="mixing-left"):
                yield Label("[bold]📋 已加材料[/bold]")
                yield Static("", id="mix-recipe-display")
            with Vertical(id="mixing-center"):
                yield Static("", id="glass-display")
                yield Static("", id="mixing-character")
                yield Static("", id="mixing-dialogue")
            with ScrollableContainer(id="mixing-right"):
                yield Label("[bold]🧪 添加材料[/bold]  [dim]1-6选 A/D翻页[/dim]")
                yield Static("", id="mix-ing-table")
                with Horizontal(classes="page-nav"):
                    yield Button("⬅(A)", id="mix-prev")
                    yield Static("", id="mix-page")
                    yield Button("➡(D)", id="mix-next")
        with Horizontal(classes="mixing-actions"):
            yield Button("🗑️ 清空", variant="error", id="mix-clear")
            yield Button("🍸 开始调酒!", variant="success", id="mix-start")

    def on_mount(self):
        self._refresh_all()

    def import_ingredients(self, ingredients: Dict[str, float]):
        self.ingredients = ingredients
        self._refresh_all()

    def _refresh_all(self):
        self._refresh_glass()
        self._refresh_recipe()
        self._refresh_ing_list()
        self._refresh_character("happy", "glass_select")
        self._highlight_glass_buttons()

    def _highlight_glass_buttons(self):
        for key, _ in get_glass_list():
            btn = self.query_one(f"#glass-{key}", Button)
            btn.variant = "primary" if key == self.glass_key else "default"

    def _refresh_glass(self):
        layers = self._build_layers()
        garnishes = self._build_garnishes()
        art = render_glass(self.glass_key, layers, garnishes)
        glass_info = GLASSES[self.glass_key]
        header = f"[bold]{glass_info.emoji} {glass_info.name}[/bold]  容量: {glass_info.capacity_ml}ml"
        self.query_one("#glass-display", Static).update(f"{header}\n\n{art}")

    def _build_layers(self) -> List[IngredientLayer]:
        layers = []
        for name, amount in self.ingredients.items():
            ing = self.cs.ingredients.get(name)
            if ing and ing.type.value not in ("装饰",):
                layers.append(IngredientLayer(name, amount, ing.color, ing.emoji))
        return layers

    def _build_garnishes(self) -> List[str]:
        garnishes = []
        for name in self.ingredients:
            ing = self.cs.ingredients.get(name)
            if ing and ing.type.value == "装饰":
                garnishes.append(ing.emoji)
        return garnishes

    def _refresh_recipe(self):
        if not self.ingredients:
            txt = "[dim]还没有添加材料\n从右侧选择材料添加[/dim]"
        else:
            parts = []
            vol = 0
            alc = 0
            for name, amount in self.ingredients.items():
                ing = self.cs.ingredients.get(name)
                emoji = ing.emoji if ing else "?"
                parts.append(f"{emoji} {name}: {amount:.0f}ml")
                vol += amount
                if ing:
                    alc += ing.alcohol_content * amount / 100
            avg = alc / vol * 100 if vol > 0 else 0
            txt = "\n".join(parts)
            txt += f"\n\n[bold]总量:[/bold] {vol:.0f}ml\n[bold]酒精度:[/bold] {avg:.1f}%"
        self.query_one("#mix-recipe-display", Static).update(txt)

    def _refresh_ing_list(self):
        items = self.cs.get_available_ingredients()
        total = max(1, (len(items) + self.ing_per_page - 1) // self.ing_per_page)
        start = self.ing_page * self.ing_per_page
        current = items[start:start + self.ing_per_page]

        tbl = Table(show_header=True, header_style="bold", expand=True)
        tbl.add_column("#", width=2)
        tbl.add_column("材料", min_width=8)
        tbl.add_column("类型", width=4)

        for i, ing in enumerate(current):
            mark = "✓" if ing.name in self.ingredients else ""
            tbl.add_row(
                str(i + 1),
                f"{ing.emoji} {ing.name} {mark}",
                ing.type.value[:2],
            )

        self.query_one("#mix-ing-table", Static).update(tbl)
        self.query_one("#mix-page", Static).update(f"{self.ing_page + 1}/{total}")
        self.query_one("#mix-prev", Button).disabled = self.ing_page <= 0
        self.query_one("#mix-next", Button).disabled = self.ing_page >= total - 1

    def _refresh_character(self, mood="happy", context="greeting"):
        art = self.bunny.get_ascii_art(mood)
        self.query_one("#mixing-character", Static).update(art)
        dialogue = self.bunny.get_dialogue(context)
        self.query_one("#mixing-dialogue", Static).update(f"💬 {dialogue}")

    def _add_ingredient(self, idx: int):
        if self.is_mixing:
            return
        items = self.cs.get_available_ingredients()
        start = self.ing_page * self.ing_per_page
        if start + idx >= len(items):
            return
        ing = items[start + idx]
        if ing.name in self.ingredients:
            self.ingredients[ing.name] += 15
            if self.ingredients[ing.name] > 200:
                del self.ingredients[ing.name]
                self._refresh_all()
                return
        else:
            self.ingredients[ing.name] = 30

        self._refresh_character("pouring", "pouring")
        self._refresh_glass()
        self._refresh_recipe()
        self._refresh_ing_list()
        self.app.notify(f"添加了 {ing.emoji} {ing.name}", severity="information", timeout=2)

    async def _run_mixing_animation(self):
        """调酒动画"""
        self.is_mixing = True
        self._refresh_character("working", "working")

        steps = [
            ("🧊 准备冰块...", 0),
            ("🥃 倒入基酒...", 1),
            ("🍋 添加调和剂...", 2),
            ("🥄 搅拌混合...", 3),
            ("🌿 装饰点缀...", 4),
            ("✨ 完成调制！", 5),
        ]

        layers = self._build_layers()
        garnishes = self._build_garnishes()
        glass = GLASSES[self.glass_key]

        for step_text, frame in steps:
            if not self.is_mixing:
                break
            self.query_one("#mixing-dialogue", Static).update(f"💬 {step_text}")

            partial_count = min(len(layers), (frame + 1) * len(layers) // len(steps) + 1)
            partial_layers = layers[:partial_count]
            partial_garnish = garnishes if frame >= 4 else []
            art = render_glass(self.glass_key, partial_layers, partial_garnish)
            header = f"[bold]{glass.emoji} {glass.name}[/bold]  🍸 调酒中..."
            self.query_one("#glass-display", Static).update(f"{header}\n\n{art}")

            char_art = self.bunny.get_ascii_art("working", frame)
            self.query_one("#mixing-character", Static).update(char_art)

            await asyncio.sleep(0.8)

        self.is_mixing = False
        self._show_result()

    def _show_result(self):
        """显示调酒结果"""
        matched_name = None
        for rname, recipe in self.cs.recipes.items():
            if set(recipe.ingredients.keys()) == set(self.ingredients.keys()):
                matched_name = rname
                break

        if matched_name:
            score, evaluation = self.cs.calculate_score(matched_name, self.ingredients)
            title = f"🍸 {matched_name}"
        else:
            score = self._calc_free_score()
            evaluation = "创意鸡尾酒！" if score >= 60 else "继续尝试～"
            title = "🍹 创意调酒"

        self._refresh_character("excited", "success")
        layers = self._build_layers()
        garnishes = self._build_garnishes()
        art = render_glass(self.glass_key, layers, garnishes)
        glass = GLASSES[self.glass_key]

        result = f"[bold green]✨ {title} ✨[/bold green]\n\n"
        result += f"{art}\n\n"
        result += f"[bold]评分: {score}/100  {evaluation}[/bold]\n"
        result += f"杯型: {glass.emoji} {glass.name}"

        self.query_one("#glass-display", Static).update(result)
        self.app.notify(f"{title} — {score}分 {evaluation}", title="🎉 调酒完成!", severity="information")

    def _calc_free_score(self):
        score = 0
        count = len([v for v in self.ingredients.values() if v > 0])
        score += min(count * 15, 60)
        bases = ["伏特加", "白朗姆酒", "威士忌", "龙舌兰酒", "金酒", "白兰地", "黑朗姆酒"]
        if any(b in self.ingredients for b in bases):
            score += 20
        mixers = ["青柠汁", "柠檬汁", "橙汁", "蔓越莓汁", "苏打水", "汤力水", "可乐", "菠萝汁"]
        if any(m in self.ingredients for m in mixers):
            score += 15
        garnishes = ["薄荷叶", "柠檬片", "樱桃", "橄榄", "橙片", "盐边", "糖边"]
        if any(g in self.ingredients for g in garnishes):
            score += 5
        return min(score, 100)

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id
        if not bid:
            return

        if bid.startswith("glass-"):
            gkey = bid[6:]
            if gkey in GLASSES:
                self.glass_key = gkey
                self._refresh_all()
                self.app.notify(f"选择了 {GLASSES[gkey].emoji} {GLASSES[gkey].name}", timeout=2)
        elif bid == "mix-clear":
            self.ingredients.clear()
            self._refresh_all()
        elif bid == "mix-start":
            if self.ingredients and not self.is_mixing:
                asyncio.create_task(self._run_mixing_animation())
        elif bid == "mix-prev" and self.ing_page > 0:
            self.ing_page -= 1
            self._refresh_ing_list()
        elif bid == "mix-next":
            items = self.cs.get_available_ingredients()
            total = max(1, (len(items) + self.ing_per_page - 1) // self.ing_per_page)
            if self.ing_page < total - 1:
                self.ing_page += 1
                self._refresh_ing_list()

    def on_key(self, event: Key):
        if self.is_mixing:
            return
        key = event.key
        if key in ("1", "2", "3", "4", "5", "6"):
            self._add_ingredient(int(key) - 1)
        elif key in ("a",):
            if self.ing_page > 0:
                self.ing_page -= 1
                self._refresh_ing_list()
        elif key in ("d",):
            items = self.cs.get_available_ingredients()
            total = max(1, (len(items) + self.ing_per_page - 1) // self.ing_per_page)
            if self.ing_page < total - 1:
                self.ing_page += 1
                self._refresh_ing_list()
        elif key == "c":
            self.ingredients.clear()
            self._refresh_all()
        elif key == "enter":
            if self.ingredients and not self.is_mixing:
                asyncio.create_task(self._run_mixing_animation())


# ──────────────── 帮助覆盖层 ────────────────

class HelpScreen(Container):
    def __init__(self, current_module="main", **kwargs):
        super().__init__(**kwargs)
        self.current_module = current_module

    def compose(self) -> ComposeResult:
        with Vertical(id="help-content"):
            yield Label("🆘 Termix 帮助", classes="help-title")
            with ScrollableContainer(id="help-scroll"):
                yield Static(self._text(), id="help-text")
            with Horizontal(classes="help-close"):
                yield Button("❌ 关闭 (Esc)", id="close-help", variant="error")

    def _text(self):
        return """\
[bold cyan]⌨️  全局快捷键[/bold cyan]

  F1 / 1️  材料选择      F2 / 2️  配方图鉴
  F3 / 3️  调酒台        F8       帮助
  Esc      返回欢迎界面

[bold cyan]🧪 材料选择界面[/bold cyan]

  1-6    选择当前页材料 (再按增加用量, 超过200ml移除)
  A / D  翻页            C    清空选择
  Enter  跳转到调酒台

[bold cyan]📖 配方图鉴[/bold cyan]

  1-4    查看并导入配方到调酒台
  A / D  翻页

[bold cyan]🍸 调酒台[/bold cyan]

  点击杯型按钮选择杯子
  1-6    从右侧列表添加材料 (再按增加用量)
  A / D  翻页材料列表    C    清空杯中材料
  Enter  开始调酒动画!

[bold cyan]💡 调酒技巧[/bold cyan]

  • 每杯鸡尾酒至少需要一种基酒
  • 调和剂平衡口感, 装饰提升颜值
  • 材料匹配经典配方可获得高分
  • 不同杯型适合不同类型的鸡尾酒
"""

    def update_module(self, module_name: str):
        self.current_module = module_name

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "close-help":
            self.post_message(CloseHelpMessage())


class CloseHelpMessage(Message):
    pass


# ──────────────── 游戏主界面 ────────────────

class GameScreen(Container):
    """游戏主界面 - 选项卡式导航"""

    def __init__(self, bunny_girl, cocktail_system, **kwargs):
        super().__init__(**kwargs)
        self.bunny_girl = bunny_girl
        self.cocktail_system = cocktail_system
        self.current_view = "ingredients"

    def compose(self) -> ComposeResult:
        with Horizontal(classes="nav-bar"):
            yield Button("🧪 材料", id="nav-ingredients", variant="primary")
            yield Button("📖 配方", id="nav-recipes")
            yield Button("🍸 调酒台", id="nav-mixing")
            yield Button("❓ 帮助", id="nav-help")

        with Container(id="game-content"):
            yield IngredientsView(self.cocktail_system, id="ingredients-view")
            yield RecipesView(self.cocktail_system, id="recipes-view")
            yield MixingStationView(self.cocktail_system, self.bunny_girl, id="mixing-view")

    def on_mount(self):
        self._show_view("ingredients")

    def _show_view(self, name: str):
        self.current_view = name
        views = {
            "ingredients": "#ingredients-view",
            "recipes": "#recipes-view",
            "mixing": "#mixing-view",
        }
        for vname, vid in views.items():
            self.query_one(vid).display = vname == name

        nav_map = {
            "ingredients": "#nav-ingredients",
            "recipes": "#nav-recipes",
            "mixing": "#nav-mixing",
        }
        for vname, nid in nav_map.items():
            self.query_one(nid, Button).variant = "primary" if vname == name else "default"

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id
        if bid == "nav-ingredients":
            self._show_view("ingredients")
        elif bid == "nav-recipes":
            self._show_view("recipes")
        elif bid == "nav-mixing":
            self._show_view("mixing")
        elif bid == "nav-help":
            self.app._toggle_help()

    def on_key(self, event: Key):
        if event.key == "f1":
            self._show_view("ingredients")
            event.prevent_default()
        elif event.key == "f2":
            self._show_view("recipes")
            event.prevent_default()
        elif event.key == "f3":
            self._show_view("mixing")
            event.prevent_default()
        elif event.key == "f8":
            self.app._toggle_help()
            event.prevent_default()
