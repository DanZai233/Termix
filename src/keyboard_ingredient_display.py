"""
全键盘操作的材料显示组件
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Label, Select
from textual.reactive import reactive
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from typing import Dict, List


class KeyboardIngredientDisplay(Container):
    """全键盘操作的材料选择器"""
    
    def __init__(self, cocktail_system, **kwargs):
        super().__init__(**kwargs)
        self.cocktail_system = cocktail_system
        self.selected_ingredients = {}
        self.current_page = 0
        self.ingredients_per_page = 6
        self.focused_ingredient = 0  # 当前聚焦的材料索引 (0-5)
        
    def compose(self) -> ComposeResult:
        """构建材料选择界面"""
        
        yield Label("🧪 选择调酒材料 (键盘操作)", classes="section-title")
        
        # 材料显示区域
        yield Static("", id="ingredients-display")
        
        # 翻页控制
        with Horizontal(classes="page-controls"):
            yield Button("⬅️ 上页 (A)", id="prev-page")
            yield Static("", id="page-info")
            yield Button("➡️ 下页 (D)", id="next-page")
        
        # 材料选择按钮 (1-6)
        with Horizontal(classes="ingredient-buttons"):
            for i in range(self.ingredients_per_page):
                yield Button("", id=f"ingredient-{i}", classes="ingredient-select-btn")
        
        # 当前选择显示
        yield Label("📊 当前选择:", classes="section-title")
        yield Static("", id="selected-display")
        
        # 操作按钮
        with Horizontal(classes="action-buttons"):
            yield Button("🗑️ 清空 (C)", variant="error", id="clear-selection")
            yield Button("🍸 开始调酒 (Enter)", variant="success", id="start-mixing")
    
    def on_mount(self):
        """初始化"""
        self._update_display()
    
    def _update_display(self):
        """更新材料显示"""
        ingredients = self.cocktail_system.get_available_ingredients()
        total_pages = (len(ingredients) + self.ingredients_per_page - 1) // self.ingredients_per_page
        
        # 更新页面信息
        page_info = self.query_one("#page-info", Static)
        page_info.update(f"第 {self.current_page + 1} 页 / 共 {total_pages} 页")
        
        # 获取当前页的材料
        start_idx = self.current_page * self.ingredients_per_page
        end_idx = min(start_idx + self.ingredients_per_page, len(ingredients))
        current_ingredients = ingredients[start_idx:end_idx]
        
        # 创建材料表格
        table = Table(title=f"材料清单 (第 {self.current_page + 1} 页)", show_header=True, header_style="bold magenta")
        table.add_column("编号", style="cyan", width=3)
        table.add_column("材料", style="green", width=15)
        table.add_column("类型", style="blue", width=8)
        table.add_column("酒精度", style="yellow", width=6)
        table.add_column("风味", style="red", width=20)
        
        for i, ingredient in enumerate(current_ingredients):
            # 高亮当前聚焦的材料
            if i == self.focused_ingredient:
                style = "bold white on blue"
            else:
                style = "default"
            
            table.add_row(
                f"{i+1}",
                f"{ingredient.emoji} {ingredient.name}",
                ingredient.type.value,
                f"{ingredient.alcohol_content}%",
                ", ".join(ingredient.flavor_profile),
                style=style
            )
        
        # 更新显示
        display = self.query_one("#ingredients-display", Static)
        display.update(table)
        
        # 更新选择按钮
        for i in range(self.ingredients_per_page):
            button = self.query_one(f"#ingredient-{i}", Button)
            if i < len(current_ingredients):
                ingredient = current_ingredients[i]
                # 高亮当前聚焦的按钮
                if i == self.focused_ingredient:
                    button.variant = "primary"
                else:
                    button.variant = "default"
                
                button.label = f"{i+1}. {ingredient.emoji} {ingredient.name[:8]}"
                button.display = True
            else:
                button.display = False
        
        # 更新翻页按钮状态
        prev_btn = self.query_one("#prev-page", Button)
        next_btn = self.query_one("#next-page", Button)
        prev_btn.disabled = (self.current_page == 0)
        next_btn.disabled = (self.current_page >= total_pages - 1)
        
        # 更新选择显示
        self._update_selection_display()
    
    def _update_selection_display(self):
        """更新选择显示"""
        if not self.selected_ingredients:
            content = "还没有选择任何材料\n\n[bold cyan]键盘操作提示:[/bold cyan]\n• [yellow]1-6[/yellow] 选择材料\n• [yellow]A/D[/yellow] 翻页\n• [yellow]C[/yellow] 清空选择\n• [yellow]Enter[/yellow] 开始调酒\n• [yellow]Tab[/yellow] 切换焦点"
        else:
            content = "[bold green]已选择的材料:[/bold green]\n"
            total_alcohol = 0
            total_volume = 0
            
            for name, amount in self.selected_ingredients.items():
                if name in self.cocktail_system.ingredients:
                    ingredient = self.cocktail_system.ingredients[name]
                    alcohol = ingredient.alcohol_content * amount / 100
                    total_alcohol += alcohol
                    total_volume += amount
                
                content += f"• {name}: {amount}ml\n"
            
            if total_volume > 0:
                avg_alcohol = total_alcohol / total_volume * 100
                content += f"\n[bold]总量:[/bold] {total_volume}ml\n"
                content += f"[bold]平均酒精度:[/bold] {avg_alcohol:.1f}%"
        
        display = self.query_one("#selected-display", Static)
        display.update(content)
    
    def _get_current_ingredient(self):
        """获取当前聚焦的材料"""
        ingredients = self.cocktail_system.get_available_ingredients()
        start_idx = self.current_page * self.ingredients_per_page
        current_ingredients = ingredients[start_idx:start_idx + self.ingredients_per_page]
        
        if self.focused_ingredient < len(current_ingredients):
            return current_ingredients[self.focused_ingredient]
        return None
    
    def _toggle_ingredient(self, ingredient):
        """切换材料选择状态"""
        if ingredient.name in self.selected_ingredients:
            # 如果已选择，增加用量
            current_amount = self.selected_ingredients[ingredient.name]
            new_amount = current_amount + 15  # 每次增加15ml
            if new_amount > 200:  # 最大200ml
                del self.selected_ingredients[ingredient.name]
            else:
                self.selected_ingredients[ingredient.name] = new_amount
        else:
            # 如果未选择，添加默认用量
            self.selected_ingredients[ingredient.name] = 30  # 默认30ml
        
        self._update_display()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        if event.button.id == "prev-page":
            if self.current_page > 0:
                self.current_page -= 1
                self.focused_ingredient = 0  # 重置聚焦
                self._update_display()
        elif event.button.id == "next-page":
            ingredients = self.cocktail_system.get_available_ingredients()
            total_pages = (len(ingredients) + self.ingredients_per_page - 1) // self.ingredients_per_page
            if self.current_page < total_pages - 1:
                self.current_page += 1
                self.focused_ingredient = 0  # 重置聚焦
                self._update_display()
        elif event.button.id and event.button.id.startswith("ingredient-"):
            # 选择材料
            idx = int(event.button.id.split("-")[1])
            self.focused_ingredient = idx
            ingredient = self._get_current_ingredient()
            if ingredient:
                self._toggle_ingredient(ingredient)
        elif event.button.id == "clear-selection":
            self.selected_ingredients.clear()
            self._update_display()
        elif event.button.id == "start-mixing":
            if self.selected_ingredients:
                # 发送调酒消息
                from .ui_components import StartMixingMessage
                self.post_message(StartMixingMessage(self.selected_ingredients.copy()))
    
    def on_key(self, event) -> None:
        """处理键盘事件"""
        if event.key == "1":
            self.focused_ingredient = 0
            self._select_ingredient()
        elif event.key == "2":
            self.focused_ingredient = 1
            self._select_ingredient()
        elif event.key == "3":
            self.focused_ingredient = 2
            self._select_ingredient()
        elif event.key == "4":
            self.focused_ingredient = 3
            self._select_ingredient()
        elif event.key == "5":
            self.focused_ingredient = 4
            self._select_ingredient()
        elif event.key == "6":
            self.focused_ingredient = 5
            self._select_ingredient()
        elif event.key == "a" or event.key == "left":
            # 上一页
            if self.current_page > 0:
                self.current_page -= 1
                self.focused_ingredient = 0
                self._update_display()
        elif event.key == "d" or event.key == "right":
            # 下一页
            ingredients = self.cocktail_system.get_available_ingredients()
            total_pages = (len(ingredients) + self.ingredients_per_page - 1) // self.ingredients_per_page
            if self.current_page < total_pages - 1:
                self.current_page += 1
                self.focused_ingredient = 0
                self._update_display()
        elif event.key == "c":
            # 清空选择
            self.selected_ingredients.clear()
            self._update_display()
        elif event.key == "enter":
            # 开始调酒
            if self.selected_ingredients:
                from .ui_components import StartMixingMessage
                self.post_message(StartMixingMessage(self.selected_ingredients.copy()))
        elif event.key == "up":
            # 上一个材料
            if self.focused_ingredient > 0:
                self.focused_ingredient -= 1
                self._update_display()
        elif event.key == "down":
            # 下一个材料
            ingredients = self.cocktail_system.get_available_ingredients()
            start_idx = self.current_page * self.ingredients_per_page
            current_ingredients = ingredients[start_idx:start_idx + self.ingredients_per_page]
            if self.focused_ingredient < len(current_ingredients) - 1:
                self.focused_ingredient += 1
                self._update_display()
    
    def _select_ingredient(self):
        """选择当前聚焦的材料"""
        ingredient = self._get_current_ingredient()
        if ingredient:
            self._toggle_ingredient(ingredient)
