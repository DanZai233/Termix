"""
UI组件模块 - 游戏界面组件
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid, ScrollableContainer
from textual.widgets import Static, Button, Label, ProgressBar, Select, Input
from textual.reactive import reactive
from textual.message import Message
from textual.events import Key
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.table import Table
import asyncio
from typing import Dict, List

from .free_mixing import FreeMixingScreen
from .ingredient_display import IngredientDisplayNew


class WelcomeScreen(Container):
    """欢迎界面"""
    
    def compose(self) -> ComposeResult:
        """构建欢迎界面"""
        
        # 创建标题
        title_text = Text()
        title_text.append("🍸 ", style="bold magenta")
        title_text.append("Termix", style="bold cyan")
        title_text.append(" 🍸", style="bold magenta")
        
        subtitle_text = Text()
        subtitle_text.append("终端调酒游戏", style="italic yellow")
        
        # 游戏介绍
        intro_text = """
        欢迎来到 Termix！

        🐰 与可爱的兔女郎调酒师一起
        🍹 学习调制经典鸡尾酒
        ✨ 体验精美的终端动画
        🎮 享受互动式游戏乐趣

        准备好开始你的调酒之旅了吗？
        """
        
        yield Static(Align.center(title_text), id="title")
        yield Static(Align.center(subtitle_text), id="subtitle")
        yield Static(Align.center(intro_text), id="intro")
        yield Button("🚀 开始游戏", variant="success", id="start_game")


class CharacterDisplay(Static):
    """角色显示组件"""
    
    def __init__(self, bunny_girl, **kwargs):
        super().__init__(**kwargs)
        self.bunny_girl = bunny_girl
        self.current_mood = "happy"
        self.animation_frame = 0
    
    def update_character(self, mood="happy", dialogue=None):
        """更新角色显示"""
        self.current_mood = mood
        art = self.bunny_girl.get_ascii_art(mood, self.animation_frame)
        
        if dialogue is None:
            dialogue = self.bunny_girl.get_dialogue("greeting")
        
        content = f"{art}\n\n💬 {dialogue}"
        
        panel = Panel(
            Align.center(content),
            title="🐰 调酒师小兔",
            border_style="magenta"
        )
        
        self.update(panel)
    
    def animate_working(self):
        """播放工作动画"""
        self.current_mood = "working"
        # 这里可以添加动画逻辑
        self.animation_frame = (self.animation_frame + 1) % 6
        self.update_character("working", "正在为您精心调制...")


class IngredientSelector(Container):
    """材料选择器"""
    
    def __init__(self, cocktail_system, **kwargs):
        super().__init__(**kwargs)
        self.cocktail_system = cocktail_system
        self.selected_ingredients = {}
        self.ingredient_id_map = {}  # 存储ID到材料名称的映射
        
        # 预先创建ID映射
        for ingredient in self.cocktail_system.get_available_ingredients():
            safe_id = f"ingredient-{hash(ingredient.name) % 10000}"
            self.ingredient_id_map[safe_id] = ingredient.name
    
    def compose(self) -> ComposeResult:
        """构建材料选择界面"""
        
        yield Label("🧪 选择调酒材料", classes="section-title")
        
        # 清空并重新初始化ID映射
        self.ingredient_id_map.clear()
        
        # 创建材料网格
        with Grid(id="ingredients-grid"):
            for ingredient in self.cocktail_system.get_available_ingredients():
                yield self._create_ingredient_card(ingredient)
        
        yield Label("📊 当前选择:", classes="section-title")
        yield Static("", id="selected-display")
        
        yield Horizontal(
            Button("🗑️ 清空", variant="error", id="clear-selection"),
            Button("🍸 开始调酒", variant="success", id="start-mixing"),
            classes="button-row"
        )
    
    def _create_ingredient_card(self, ingredient):
        """创建材料卡片"""
        card_content = f"""
{ingredient.emoji} {ingredient.name}
类型: {ingredient.type.value}
酒精度: {ingredient.alcohol_content}%
风味: {', '.join(ingredient.flavor_profile)}

{ingredient.description}
        """
        
        # 使用预先创建的安全ID
        safe_id = None
        for existing_id, name in self.ingredient_id_map.items():
            if name == ingredient.name:
                safe_id = existing_id
                break
        
        if safe_id is None:
            # 如果没找到，创建新的安全ID
            safe_id = f"ingredient-{hash(ingredient.name) % 10000}"
            self.ingredient_id_map[safe_id] = ingredient.name
        
        return Button(
            card_content.strip(),
            id=safe_id,
            classes="ingredient-card"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        if event.button.id and event.button.id.startswith("ingredient-"):
            # 从映射中获取真实的材料名称
            ingredient_name = self.ingredient_id_map.get(event.button.id)
            if ingredient_name:
                self._toggle_ingredient(ingredient_name)
        elif event.button.id == "clear-selection":
            self.selected_ingredients.clear()
            self._update_selection_display()
        elif event.button.id == "start-mixing":
            self.post_message(StartMixingMessage(self.selected_ingredients.copy()))
    
    def _toggle_ingredient(self, ingredient_name):
        """切换材料选择状态"""
        if ingredient_name in self.selected_ingredients:
            # 如果已选择，增加用量
            current_amount = self.selected_ingredients[ingredient_name]
            new_amount = current_amount + 10  # 每次增加10ml
            if new_amount > 200:  # 最大200ml
                del self.selected_ingredients[ingredient_name]
            else:
                self.selected_ingredients[ingredient_name] = new_amount
        else:
            # 如果未选择，添加默认用量
            self.selected_ingredients[ingredient_name] = 30  # 默认30ml
        
        self._update_selection_display()
    
    def _update_selection_display(self):
        """更新选择显示"""
        if not self.selected_ingredients:
            content = "还没有选择任何材料"
        else:
            content = "\n".join([
                f"• {name}: {amount}ml" 
                for name, amount in self.selected_ingredients.items()
            ])
        
        display = self.query_one("#selected-display", Static)
        display.update(content)


class RecipeBook(Container):
    """配方书组件"""
    
    def __init__(self, cocktail_system, **kwargs):
        super().__init__(**kwargs)
        self.cocktail_system = cocktail_system
    
    def compose(self) -> ComposeResult:
        """构建配方书界面"""
        
        yield Label("📖 配方大全", classes="section-title")
        
        for recipe in self.cocktail_system.get_unlocked_recipes():
            yield self._create_recipe_card(recipe)
        
        # 显示提示
        hint = self.cocktail_system.get_random_recipe_hint()
        yield Static(f"💡 小贴士: {hint}", classes="hint")
    
    def _create_recipe_card(self, recipe):
        """创建配方卡片"""
        
        # 创建材料表格
        table = Table(title=f"{recipe.emoji} {recipe.name}")
        table.add_column("材料", style="cyan")
        table.add_column("用量", style="magenta")
        
        for ingredient_name, amount in recipe.ingredients.items():
            table.add_row(ingredient_name, f"{amount}ml")
        
        # 添加描述和难度
        description = f"\n{recipe.description}\n难度: {'⭐' * recipe.difficulty}"
        
        return Static(
            Panel(
                f"{table}\n{description}",
                border_style="green"
            ),
            classes="recipe-card"
        )


class MixingAnimation(Container):
    """调酒动画组件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_mixing = False
        self.animation_step = 0
    
    def compose(self) -> ComposeResult:
        """构建动画界面"""
        
        yield Static("", id="mixing-display")
        yield ProgressBar(total=100, show_eta=False, id="mixing-progress")
        yield Static("", id="mixing-status")
    
    async def start_mixing_animation(self, ingredients):
        """开始调酒动画"""
        self.is_mixing = True
        self.animation_step = 0
        
        progress_bar = self.query_one("#mixing-progress", ProgressBar)
        status_display = self.query_one("#mixing-status", Static)
        mixing_display = self.query_one("#mixing-display", Static)
        
        steps = [
            "🧊 准备冰块...",
            "🥃 倒入基酒...",
            "🍋 添加果汁...",
            "🍯 加入糖浆...",
            "🥄 搅拌混合...",
            "🌿 装饰点缀...",
            "✨ 完成调制！"
        ]
        
        for i, step in enumerate(steps):
            if not self.is_mixing:
                break
            
            status_display.update(step)
            progress = int((i + 1) / len(steps) * 100)
            progress_bar.update(progress=progress)
            
            # 显示调酒动画
            animation_frame = self._get_mixing_frame(i)
            mixing_display.update(Panel(
                Align.center(animation_frame),
                title="🍸 调酒中...",
                border_style="cyan"
            ))
            
            await asyncio.sleep(1)
        
        self.is_mixing = False
    
    def _get_mixing_frame(self, step):
        """获取调酒动画帧"""
        frames = [
            "🧊\n冰块准备中...",
            "🥃🧊\n倒入基酒...",
            "🥃🍋🧊\n添加果汁...",
            "🥃🍋🍯🧊\n加入糖浆...",
            "🌪️ 🥄 🌪️\n搅拌中...",
            "🍸🌿\n装饰中...",
            "🍸✨\n调制完成！"
        ]
        
        return frames[min(step, len(frames) - 1)]


class GameScreen(Container):
    """游戏主界面"""
    
    def __init__(self, bunny_girl, cocktail_system, **kwargs):
        super().__init__(**kwargs)
        self.bunny_girl = bunny_girl
        self.cocktail_system = cocktail_system
        self.current_view = "ingredients"
        self.layout_mode = "horizontal"  # horizontal 或 vertical
    
    def compose(self) -> ComposeResult:
        """构建游戏界面"""
        
        # 顶部导航
        yield Horizontal(
            Button("🧪 材料", id="nav-ingredients", variant="primary"),
            Button("📖 配方", id="nav-recipes"),
            Button("🍸 标准调酒", id="nav-mixing"),
            Button("🎨 自由调酒", id="nav-free-mixing"),
            Button("🔄 切换布局", id="toggle-layout"),
            classes="nav-bar"
        )
        
        # 主要内容区域 - 使用ScrollableContainer支持滚动
        with ScrollableContainer(id="main-scroll"):
            with Container(id="main-content"):
                # 角色显示区域
                with Container(classes="character-section", id="character-section"):
                    yield CharacterDisplay(self.bunny_girl, id="character")
                
                # 内容区域
                with Container(classes="content-section", id="content-section"):
                    yield IngredientDisplayNew(self.cocktail_system, id="ingredients-view")
                    yield RecipeBook(self.cocktail_system, id="recipes-view")
                    yield MixingAnimation(id="mixing-view")
                    yield FreeMixingScreen(self.cocktail_system, self.bunny_girl, id="free-mixing-view")
    
    def on_mount(self):
        """界面挂载时的初始化"""
        # 初始显示角色
        character = self.query_one("#character", CharacterDisplay)
        character.update_character("happy")
        
        # 初始显示材料选择界面
        self._show_view("ingredients")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理导航按钮点击"""
        if event.button.id == "nav-ingredients":
            self._show_view("ingredients")
            self.app.current_module = "ingredients"
        elif event.button.id == "nav-recipes":
            self._show_view("recipes")
            self.app.current_module = "recipes"
        elif event.button.id == "nav-mixing":
            self._show_view("mixing")
            self.app.current_module = "mixing"
        elif event.button.id == "nav-free-mixing":
            self._show_view("free-mixing")
            self.app.current_module = "free-mixing"
        elif event.button.id == "toggle-layout":
            self._toggle_layout()
    
    def on_key(self, event: Key) -> None:
        """处理键盘事件"""
        # 方向键控制滚动
        scroll_container = self.query_one("#main-scroll", ScrollableContainer)
        
        if event.key == "up":
            scroll_container.scroll_up()
            event.prevent_default()
        elif event.key == "down":
            scroll_container.scroll_down()
            event.prevent_default()
        elif event.key == "left":
            scroll_container.scroll_left()
            event.prevent_default()
        elif event.key == "right":
            scroll_container.scroll_right()
            event.prevent_default()
        elif event.key == "pageup":
            scroll_container.scroll_page_up()
            event.prevent_default()
        elif event.key == "pagedown":
            scroll_container.scroll_page_down()
            event.prevent_default()
        elif event.key == "home":
            scroll_container.scroll_home()
            event.prevent_default()
        elif event.key == "end":
            scroll_container.scroll_end()
            event.prevent_default()
    
    def _toggle_layout(self):
        """切换布局模式"""
        if self.layout_mode == "horizontal":
            self.layout_mode = "vertical"
            self._apply_vertical_layout()
        else:
            self.layout_mode = "horizontal"
            self._apply_horizontal_layout()
    
    def _apply_horizontal_layout(self):
        """应用水平布局"""
        main_content = self.query_one("#main-content")
        main_content.styles.layout = "horizontal"
        
        character_section = self.query_one("#character-section")
        character_section.styles.width = "40%"
        character_section.styles.height = "100%"
        
        content_section = self.query_one("#content-section")
        content_section.styles.width = "60%"
        content_section.styles.height = "100%"
    
    def _apply_vertical_layout(self):
        """应用垂直布局"""
        main_content = self.query_one("#main-content")
        main_content.styles.layout = "vertical"
        
        character_section = self.query_one("#character-section")
        character_section.styles.width = "100%"
        character_section.styles.height = "30%"
        
        content_section = self.query_one("#content-section")
        content_section.styles.width = "100%"
        content_section.styles.height = "70%"
    
    def _show_view(self, view_name):
        """显示指定视图"""
        self.current_view = view_name
        
        # 隐藏所有视图
        views = ["ingredients-view", "recipes-view", "mixing-view", "free-mixing-view"]
        for view_id in views:
            view = self.query_one(f"#{view_id}")
            view.display = False
        
        # 显示当前视图
        current_view = self.query_one(f"#{view_name}-view")
        current_view.display = True
        
        # 更新导航按钮状态
        nav_buttons = self.query(".nav-bar Button")
        for button in nav_buttons:
            button.variant = "default"
        
        nav_button = self.query_one(f"#nav-{view_name}", Button)
        nav_button.variant = "primary"


# 自定义消息类
class StartMixingMessage(Message):
    """开始调酒消息"""
    def __init__(self, ingredients):
        super().__init__()
        self.ingredients = ingredients
