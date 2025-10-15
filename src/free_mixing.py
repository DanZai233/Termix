"""
自由调酒模块 - 用户自选材料调酒
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Button, Label, Input, Select
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from typing import Dict, List
import random


class FreeMixingScreen(Container):
    """自由调酒界面"""
    
    def __init__(self, cocktail_system, bunny_girl, **kwargs):
        super().__init__(**kwargs)
        self.cocktail_system = cocktail_system
        self.bunny_girl = bunny_girl
        self.selected_ingredients = {}
        self.show_ingredients_panel = True
        self.show_recipes_panel = True
    
    def compose(self) -> ComposeResult:
        """构建自由调酒界面"""
        
        with Horizontal(id="free-mixing-layout"):
            # 左侧：材料和配方面板
            with Vertical(classes="side-panels", id="side-panels"):
                # 材料面板
                with Container(id="ingredients-panel", classes="info-panel"):
                    yield Label("🧪 材料清单", classes="panel-title")
                    yield ScrollableContainer(
                        self._create_ingredients_list(),
                        id="ingredients-scroll"
                    )
                
                # 配方面板
                with Container(id="recipes-panel", classes="info-panel"):
                    yield Label("📖 配方参考", classes="panel-title")
                    yield ScrollableContainer(
                        self._create_recipes_list(),
                        id="recipes-scroll"
                    )
            
            # 右侧：调酒区域
            with Vertical(classes="mixing-area", id="mixing-area"):
                yield Label("🍸 自由调酒台", classes="section-title")
                
                # 材料选择区
                with Container(id="ingredient-selector"):
                    yield Label("选择材料和用量:", classes="sub-title")
                    
                    # 材料选择下拉框
                    ingredient_options = [(ing.name, ing.name) for ing in self.cocktail_system.get_available_ingredients()]
                    yield Select(
                        options=ingredient_options,
                        prompt="选择材料...",
                        id="ingredient-select"
                    )
                    
                    # 用量输入
                    with Horizontal(classes="amount-input"):
                        yield Label("用量(ml):")
                        yield Input(
                            placeholder="30",
                            id="amount-input",
                            max_length=4
                        )
                        yield Button("➕ 添加", variant="success", id="add-ingredient")
                
                # 当前配方显示
                yield Label("🍹 当前配方:", classes="sub-title")
                yield Static("", id="current-recipe")
                
                # 控制按钮
                with Horizontal(classes="control-buttons"):
                    yield Button("🗑️ 清空", variant="error", id="clear-recipe")
                    yield Button("🍸 开始调酒", variant="primary", id="start-mixing")
                    yield Button("👁️ 切换面板", variant="default", id="toggle-panels")
    
    def _create_ingredients_list(self):
        """创建材料列表"""
        table = Table(title="材料清单")
        table.add_column("材料", style="cyan", width=12)
        table.add_column("类型", style="magenta", width=8)
        table.add_column("度数", style="yellow", width=6)
        table.add_column("风味", style="green", width=15)
        
        # 按类型分组显示材料
        ingredients_by_type = {}
        for ingredient in self.cocktail_system.get_available_ingredients():
            type_name = ingredient.type.value
            if type_name not in ingredients_by_type:
                ingredients_by_type[type_name] = []
            ingredients_by_type[type_name].append(ingredient)
        
        for type_name, ingredients in ingredients_by_type.items():
            # 添加类型标题行
            table.add_row(f"[bold]{type_name}[/bold]", "", "", "")
            
            for ingredient in ingredients:
                flavor_str = ", ".join(ingredient.flavor_profile[:2])  # 只显示前两个风味
                table.add_row(
                    f"{ingredient.emoji} {ingredient.name}",
                    "",
                    f"{ingredient.alcohol_content}%",
                    flavor_str
                )
        
        return Static(table)
    
    def _create_recipes_list(self):
        """创建配方列表"""
        content = ""
        
        for recipe in self.cocktail_system.get_unlocked_recipes()[:5]:  # 只显示前5个配方
            content += f"\n{recipe.emoji} [bold]{recipe.name}[/bold]\n"
            content += f"[italic]{recipe.description}[/italic]\n"
            content += f"难度: {'⭐' * recipe.difficulty}\n"
            
            # 显示主要材料
            main_ingredients = list(recipe.ingredients.items())[:3]
            for name, amount in main_ingredients:
                content += f"• {name}: {amount}ml\n"
            
            if len(recipe.ingredients) > 3:
                content += f"• ... 等{len(recipe.ingredients) - 3}种材料\n"
            content += "\n"
        
        return Static(content)
    
    def _update_current_recipe(self):
        """更新当前配方显示"""
        if not self.selected_ingredients:
            content = "[dim]还没有添加任何材料...[/dim]"
        else:
            table = Table()
            table.add_column("材料", style="cyan")
            table.add_column("用量", style="magenta")
            table.add_column("类型", style="green")
            
            total_alcohol = 0
            total_volume = 0
            
            for name, amount in self.selected_ingredients.items():
                ingredient = self.cocktail_system.ingredients[name]
                table.add_row(
                    f"{ingredient.emoji} {name}",
                    f"{amount}ml",
                    ingredient.type.value
                )
                total_alcohol += ingredient.alcohol_content * amount / 100
                total_volume += amount
            
            # 计算平均酒精度
            avg_alcohol = total_alcohol / total_volume * 100 if total_volume > 0 else 0
            
            content = f"{table}\n\n"
            content += f"[bold]总量:[/bold] {total_volume}ml\n"
            content += f"[bold]酒精度:[/bold] {avg_alcohol:.1f}%\n"
            
            # 尝试匹配已知配方
            matched_recipe = self._find_matching_recipe()
            if matched_recipe:
                content += f"\n🎯 [green]匹配配方: {matched_recipe}[/green]"
        
        recipe_display = self.query_one("#current-recipe", Static)
        recipe_display.update(content)
    
    def _find_matching_recipe(self) -> str:
        """查找匹配的配方"""
        for recipe_name, recipe in self.cocktail_system.recipes.items():
            if self._recipes_match(self.selected_ingredients, recipe.ingredients):
                return recipe_name
        return ""
    
    def _recipes_match(self, recipe1: Dict[str, float], recipe2: Dict[str, float]) -> bool:
        """检查两个配方是否匹配（允许一定误差）"""
        if set(recipe1.keys()) != set(recipe2.keys()):
            return False
        
        for ingredient, amount1 in recipe1.items():
            amount2 = recipe2[ingredient]
            # 允许20%的误差
            if abs(amount1 - amount2) / amount2 > 0.2:
                return False
        
        return True
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "add-ingredient":
            self._add_ingredient()
        elif event.button.id == "clear-recipe":
            self.selected_ingredients.clear()
            self._update_current_recipe()
        elif event.button.id == "start-mixing":
            if self.selected_ingredients:
                self.post_message(StartFreeMixingMessage(self.selected_ingredients.copy()))
        elif event.button.id == "toggle-panels":
            self._toggle_side_panels()
    
    def _add_ingredient(self):
        """添加材料到配方"""
        select_widget = self.query_one("#ingredient-select", Select)
        amount_input = self.query_one("#amount-input", Input)
        
        if select_widget.value and amount_input.value:
            try:
                amount = float(amount_input.value)
                if amount > 0:
                    ingredient_name = str(select_widget.value)
                    
                    # 如果材料已存在，累加用量
                    if ingredient_name in self.selected_ingredients:
                        self.selected_ingredients[ingredient_name] += amount
                    else:
                        self.selected_ingredients[ingredient_name] = amount
                    
                    # 清空输入框
                    amount_input.value = ""
                    
                    # 更新显示
                    self._update_current_recipe()
                    
                    # 显示提示
                    ingredient = self.cocktail_system.ingredients[ingredient_name]
                    self.app.bell()  # 播放提示音
                    
            except ValueError:
                pass  # 忽略无效输入
    
    def _toggle_side_panels(self):
        """切换侧边面板显示"""
        side_panels = self.query_one("#side-panels")
        if side_panels.display:
            side_panels.display = False
        else:
            side_panels.display = True
    
    def on_mount(self):
        """界面挂载时的初始化"""
        self._update_current_recipe()


class StartFreeMixingMessage(Message):
    """开始自由调酒消息"""
    def __init__(self, ingredients: Dict[str, float]):
        super().__init__()
        self.ingredients = ingredients
