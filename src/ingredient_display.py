"""
材料显示组件 - 解决中文ID问题的新实现
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Label
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from typing import Dict, List


class IngredientDisplayNew(Container):
    """新的材料显示组件"""
    
    def __init__(self, cocktail_system, **kwargs):
        super().__init__(**kwargs)
        self.cocktail_system = cocktail_system
        self.selected_ingredients = {}
        self.current_page = 0
        
        # 从配置文件获取每页显示数量
        ui_config = cocktail_system.game_config.get("ui_settings", {})
        self.items_per_page = ui_config.get("items_per_page", 6)
    
    def compose(self) -> ComposeResult:
        """构建材料显示界面"""
        
        yield Label("🧪 选择调酒材料", classes="section-title")
        
        # 材料显示区域
        yield Static("", id="ingredients-display")
        
        # 翻页按钮
        with Horizontal(classes="page-controls"):
            yield Button("⬅️ 上页", id="prev-page")
            yield Static("", id="page-info")
            yield Button("➡️ 下页", id="next-page")
        
        # 材料选择按钮
        with Horizontal(classes="ingredient-buttons"):
            for i in range(6):  # 每页最多6个材料
                yield Button("", id=f"select-{i}", classes="ingredient-select-btn")
        
        yield Label("📊 当前选择:", classes="section-title")
        yield Static("", id="selected-display")
        
        with Horizontal(classes="action-buttons"):
            yield Button("🗑️ 清空", variant="error", id="clear-selection")
            yield Button("🍸 开始调酒", variant="success", id="start-mixing")
    
    def on_mount(self):
        """初始化"""
        self._update_display()
    
    def _update_display(self):
        """更新材料显示"""
        ingredients = self.cocktail_system.get_available_ingredients()
        total_pages = (len(ingredients) + self.items_per_page - 1) // self.items_per_page
        
        # 更新页面信息
        page_info = self.query_one("#page-info", Static)
        page_info.update(f"第 {self.current_page + 1} 页 / 共 {total_pages} 页")
        
        # 获取当前页的材料
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(ingredients))
        current_ingredients = ingredients[start_idx:end_idx]
        
        # 创建材料表格
        table = Table(title="可用材料")
        table.add_column("编号", style="cyan", width=4)
        table.add_column("材料", style="magenta", width=15)
        table.add_column("类型", style="green", width=8)
        table.add_column("度数", style="yellow", width=6)
        table.add_column("描述", style="white", width=25)
        
        for i, ingredient in enumerate(current_ingredients):
            table.add_row(
                str(i + 1),
                f"{ingredient.emoji} {ingredient.name}",
                ingredient.type.value,
                f"{ingredient.alcohol_content}%",
                ingredient.description[:25] + "..." if len(ingredient.description) > 25 else ingredient.description
            )
        
        # 更新显示
        display = self.query_one("#ingredients-display", Static)
        display.update(table)
        
        # 更新选择按钮
        for i in range(6):
            button = self.query_one(f"#select-{i}", Button)
            if i < len(current_ingredients):
                ingredient = current_ingredients[i]
                button.label = f"{i+1}. 选择 {ingredient.emoji}"
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
            content = "还没有选择任何材料"
        else:
            content = "\n".join([
                f"• {name}: {amount}ml" 
                for name, amount in self.selected_ingredients.items()
            ])
        
        display = self.query_one("#selected-display", Static)
        display.update(content)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        if event.button.id == "prev-page":
            if self.current_page > 0:
                self.current_page -= 1
                self._update_display()
        elif event.button.id == "next-page":
            ingredients = self.cocktail_system.get_available_ingredients()
            total_pages = (len(ingredients) + self.items_per_page - 1) // self.items_per_page
            if self.current_page < total_pages - 1:
                self.current_page += 1
                self._update_display()
        elif event.button.id and event.button.id.startswith("select-"):
            # 处理材料选择
            idx = int(event.button.id.split("-")[1])
            self._select_ingredient(idx)
        elif event.button.id == "clear-selection":
            self.selected_ingredients.clear()
            self._update_selection_display()
        elif event.button.id == "start-mixing":
            if self.selected_ingredients:
                self.post_message(StartMixingMessage(self.selected_ingredients.copy()))
    
    def _select_ingredient(self, idx):
        """选择材料"""
        ingredients = self.cocktail_system.get_available_ingredients()
        start_idx = self.current_page * self.items_per_page
        
        if start_idx + idx < len(ingredients):
            ingredient = ingredients[start_idx + idx]
            
            # 切换选择状态
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
            
            self._update_selection_display()


class StartMixingMessage(Message):
    """开始调酒消息"""
    def __init__(self, ingredients):
        super().__init__()
        self.ingredients = ingredients
