"""
快速参考组件 - 在调酒时快速查看配方和材料
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Button, Label, Select
from textual.reactive import reactive
from rich.table import Table
from rich.panel import Panel
from typing import Dict, List


class QuickReference(Container):
    """快速参考面板"""
    
    def __init__(self, cocktail_system, **kwargs):
        super().__init__(**kwargs)
        self.cocktail_system = cocktail_system
        self.current_view = "recipes"  # recipes 或 ingredients
    
    def compose(self) -> ComposeResult:
        """构建快速参考界面"""
        
        # 切换按钮
        with Horizontal(classes="reference-tabs"):
            yield Button("📖 配方", id="tab-recipes", variant="primary")
            yield Button("🧪 材料", id="tab-ingredients")
        
        # 内容显示区域
        with ScrollableContainer(id="reference-content"):
            yield Static("", id="reference-display")
    
    def on_mount(self):
        """初始化"""
        self._update_display()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        if event.button.id == "tab-recipes":
            self.current_view = "recipes"
            self._update_tabs()
            self._update_display()
        elif event.button.id == "tab-ingredients":
            self.current_view = "ingredients"
            self._update_tabs()
            self._update_display()
    
    def on_key(self, event) -> None:
        """处理键盘事件"""
        if event.key == "1":
            self.current_view = "recipes"
            self._update_tabs()
            self._update_display()
        elif event.key == "2":
            self.current_view = "ingredients"
            self._update_tabs()
            self._update_display()
    
    def _update_tabs(self):
        """更新标签页状态"""
        recipe_btn = self.query_one("#tab-recipes", Button)
        ingredient_btn = self.query_one("#tab-ingredients", Button)
        
        if self.current_view == "recipes":
            recipe_btn.variant = "primary"
            ingredient_btn.variant = "default"
        else:
            recipe_btn.variant = "default"
            ingredient_btn.variant = "primary"
    
    def _update_display(self):
        """更新显示内容"""
        if self.current_view == "recipes":
            content = self._create_recipes_reference()
        else:
            content = self._create_ingredients_reference()
        
        display = self.query_one("#reference-display", Static)
        display.update(content)
    
    def _create_recipes_reference(self):
        """创建配方快速参考"""
        content = "[bold cyan]📖 配方快速参考[/bold cyan]\n\n"
        
        recipes = self.cocktail_system.get_unlocked_recipes()
        
        # 按分类组织配方
        categories = {}
        for recipe in recipes:
            # 从配方的flavor_tags推断分类，或使用默认分类
            category = "其他"
            if "经典" in recipe.flavor_tags:
                category = "经典系列"
            elif "热带" in recipe.flavor_tags:
                category = "热带系列"
            elif "果味" in recipe.flavor_tags:
                category = "果味系列"
            elif "咖啡" in recipe.flavor_tags:
                category = "咖啡系列"
            elif any(tag in ["创意", "复杂", "强烈"] for tag in recipe.flavor_tags):
                category = "创意系列"
            
            if category not in categories:
                categories[category] = []
            categories[category].append(recipe)
        
        for category, recipe_list in categories.items():
            content += f"\n[bold yellow]{category}[/bold yellow]\n"
            for recipe in recipe_list:
                content += f"• {recipe.emoji} [bold]{recipe.name}[/bold] ({'⭐' * recipe.difficulty})\n"
                
                # 显示主要材料（前3个）
                main_ingredients = list(recipe.ingredients.items())[:3]
                ingredients_str = ", ".join([f"{name}({amount}ml)" for name, amount in main_ingredients])
                if len(recipe.ingredients) > 3:
                    ingredients_str += f" +{len(recipe.ingredients)-3}种"
                
                content += f"  材料: {ingredients_str}\n"
                content += f"  {recipe.description}\n\n"
        
        return content
    
    def _create_ingredients_reference(self):
        """创建材料快速参考"""
        content = "[bold cyan]🧪 材料快速参考[/bold cyan]\n\n"
        
        ingredients = self.cocktail_system.get_available_ingredients()
        
        # 按类型组织材料
        by_type = {}
        for ingredient in ingredients:
            type_name = ingredient.type.value
            if type_name not in by_type:
                by_type[type_name] = []
            by_type[type_name].append(ingredient)
        
        for type_name, ingredient_list in by_type.items():
            content += f"\n[bold yellow]{type_name}[/bold yellow]\n"
            for ingredient in ingredient_list:
                content += f"• {ingredient.emoji} [bold]{ingredient.name}[/bold] ({ingredient.alcohol_content}%)\n"
                content += f"  风味: {', '.join(ingredient.flavor_profile)}\n"
                content += f"  {ingredient.description}\n\n"
        
        return content


class QuickRecipeSelector(Container):
    """快速配方选择器"""
    
    def __init__(self, cocktail_system, **kwargs):
        super().__init__(**kwargs)
        self.cocktail_system = cocktail_system
    
    def compose(self) -> ComposeResult:
        """构建快速配方选择界面"""
        
        yield Label("🍸 选择配方调制", classes="section-title")
        
        # 配方选择下拉框
        recipe_options = [(recipe.name, recipe.name) for recipe in self.cocktail_system.get_unlocked_recipes()]
        yield Select(
            options=recipe_options,
            prompt="选择配方...",
            id="recipe-select"
        )
        
        # 配方详情显示
        yield Static("", id="selected-recipe-info")
        
        # 操作按钮
        with Horizontal(classes="quick-actions"):
            yield Button("📋 查看详情", id="view-recipe-details")
            yield Button("🍸 按此配方调制", variant="success", id="mix-selected-recipe")
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """处理配方选择变化"""
        if event.select.id == "recipe-select" and event.value:
            recipe_name = str(event.value)
            recipe = None
            
            for r in self.cocktail_system.get_unlocked_recipes():
                if r.name == recipe_name:
                    recipe = r
                    break
            
            if recipe:
                self._show_recipe_info(recipe)
    
    def _show_recipe_info(self, recipe):
        """显示配方信息"""
        # 创建简化的材料表格
        table = Table(title=f"{recipe.emoji} {recipe.name}")
        table.add_column("材料", style="cyan")
        table.add_column("用量", style="magenta")
        
        for ingredient_name, amount in recipe.ingredients.items():
            table.add_row(ingredient_name, f"{amount}ml")
        
        info = f"{table}\n\n"
        info += f"[bold]描述:[/bold] {recipe.description}\n"
        info += f"[bold]难度:[/bold] {'⭐' * recipe.difficulty}\n"
        info += f"[bold]风味:[/bold] {', '.join(recipe.flavor_tags)}"
        
        info_display = self.query_one("#selected-recipe-info", Static)
        info_display.update(info)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        if event.button.id == "view-recipe-details":
            # 显示详细配方信息
            select_widget = self.query_one("#recipe-select", Select)
            if select_widget.value:
                recipe_name = str(select_widget.value)
                self._show_detailed_recipe(recipe_name)
        elif event.button.id == "mix-selected-recipe":
            # 开始按配方调制
            select_widget = self.query_one("#recipe-select", Select)
            if select_widget.value:
                recipe_name = str(select_widget.value)
                self._start_recipe_mixing(recipe_name)
    
    def _show_detailed_recipe(self, recipe_name: str):
        """显示详细配方信息"""
        recipe = None
        for r in self.cocktail_system.get_unlocked_recipes():
            if r.name == recipe_name:
                recipe = r
                break
        
        if recipe:
            # 计算鸡尾酒的总酒精度
            total_volume = sum(recipe.ingredients.values())
            alcohol_volume = 0
            
            for ingredient_name, amount in recipe.ingredients.items():
                # 从材料系统中获取材料的酒精度
                ingredient = None
                for ing in self.cocktail_system.get_available_ingredients():
                    if ing.name == ingredient_name:
                        ingredient = ing
                        break
                
                if ingredient and hasattr(ingredient, 'alcohol_content'):
                    alcohol_volume += amount * (ingredient.alcohol_content / 100)
            
            alcohol_content = (alcohol_volume / total_volume * 100) if total_volume > 0 else 0
            
            # 创建详细的配方信息
            detailed_info = f"""
[bold cyan]{recipe.emoji} {recipe.name}[/bold cyan]

[bold]📝 描述:[/bold] {recipe.description}

[bold]📊 配方信息:[/bold]
• 难度: {'⭐' * recipe.difficulty}
• 风味标签: {', '.join(recipe.flavor_tags)}
• 酒精度: {alcohol_content:.1f}%

[bold]🧪 材料清单:[/bold]
"""
            for ingredient_name, amount in recipe.ingredients.items():
                detailed_info += f"• {ingredient_name}: {amount}ml\n"
            
            detailed_info += f"\n[bold]💡 调制提示:[/bold]\n"
            detailed_info += f"• 按顺序添加材料\n"
            detailed_info += f"• 充分搅拌混合\n"
            detailed_info += f"• 注意用量精确度"
            
            # 发送显示详细信息的消息
            from .ui_components import ShowRecipeDetailsMessage
            self.post_message(ShowRecipeDetailsMessage(recipe, detailed_info))
    
    def _start_recipe_mixing(self, recipe_name: str):
        """开始按配方调制"""
        recipe = None
        for r in self.cocktail_system.get_unlocked_recipes():
            if r.name == recipe_name:
                recipe = r
                break
        
        if recipe:
            # 发送按配方调制的消息
            from .ui_components import StartRecipeMixingMessage
            self.post_message(StartRecipeMixingMessage(recipe))
    
    def on_key(self, event) -> None:
        """处理键盘事件"""
        if event.key == "enter":
            # 开始按配方调制
            select_widget = self.query_one("#recipe-select", Select)
            if select_widget.value:
                recipe_name = str(select_widget.value)
                self._start_recipe_mixing(recipe_name)
