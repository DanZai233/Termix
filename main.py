#!/usr/bin/env python3
"""
Termix - 终端调酒游戏
一个美观的终端调酒应用，让你体验调酒的乐趣
"""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button
from textual.reactive import reactive
from textual.events import Key, Resize
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

from src.character import BunnyGirl
from src.cocktail_system import CocktailSystem
from src.ui_components import WelcomeScreen, GameScreen, StartMixingMessage, StartRecipeMixingMessage, ShowRecipeDetailsMessage
from src.free_mixing import StartFreeMixingMessage
from src.help_system import HelpScreen, CloseHelpMessage


class TermixApp(App):
    """Termix 主应用程序"""
    
    CSS_PATH = "styles.css"
    TITLE = "Termix - 终端调酒游戏"
    SUB_TITLE = "🍸 让我们一起调制美味的鸡尾酒吧！"
    
    current_screen = reactive("welcome")
    
    def __init__(self):
        super().__init__()
        self.bunny_girl = BunnyGirl()
        self.cocktail_system = CocktailSystem()
        self.help_visible = False
        self.current_module = "main"
    
    def compose(self) -> ComposeResult:
        """构建应用界面"""
        yield Header()
        yield WelcomeScreen(id="welcome")
        yield GameScreen(id="game", bunny_girl=self.bunny_girl, cocktail_system=self.cocktail_system)
        yield HelpScreen(id="help", current_module=self.current_module)
        yield Footer()
    
    def on_mount(self) -> None:
        """应用挂载时的初始化"""
        self.show_welcome_screen()
    
    def show_welcome_screen(self):
        """显示欢迎界面"""
        welcome = self.query_one("#welcome", WelcomeScreen)
        game = self.query_one("#game", GameScreen)
        help_screen = self.query_one("#help", HelpScreen)
        welcome.display = True
        game.display = False
        help_screen.display = False
        self.current_module = "main"
    
    def show_game_screen(self):
        """显示游戏界面"""
        welcome = self.query_one("#welcome", WelcomeScreen)
        game = self.query_one("#game", GameScreen)
        help_screen = self.query_one("#help", HelpScreen)
        welcome.display = False
        game.display = True
        help_screen.display = False
        self.current_module = "ingredients"  # 默认显示材料界面
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "start_game":
            self.show_game_screen()
    
    def on_resize(self, event: Resize) -> None:
        """处理窗口大小变化事件"""
        # 自动调整布局
        try:
            game_screen = self.query_one("#game", GameScreen)
            # 根据终端大小自动选择布局
            if event.size.width < 100:  # 窄屏幕使用垂直布局
                if game_screen.layout_mode == "horizontal":
                    game_screen._apply_vertical_layout()
                    game_screen.layout_mode = "vertical"
            else:  # 宽屏幕使用水平布局
                if game_screen.layout_mode == "vertical":
                    game_screen._apply_horizontal_layout()
                    game_screen.layout_mode = "horizontal"
        except:
            pass  # 如果游戏界面还没有加载，忽略错误
    
    def on_key(self, event: Key) -> None:
        """处理全局键盘事件"""
        # F1 显示帮助
        if event.key == "f1":
            self._show_help()
            event.prevent_default()
        # Escape 返回欢迎界面
        elif event.key == "escape":
            self.show_welcome_screen()
            event.prevent_default()
        # F11 切换布局
        elif event.key == "f11":
            try:
                game_screen = self.query_one("#game", GameScreen)
                game_screen._toggle_layout()
                event.prevent_default()
            except:
                pass
    
    def _show_help(self):
        """显示帮助界面"""
        help_screen = self.query_one("#help", HelpScreen)
        
        if self.help_visible:
            # 如果帮助已显示，隐藏它
            help_screen.display = False
            self.help_visible = False
        else:
            # 显示帮助界面
            help_screen.update_module(self.current_module)
            help_screen.display = True
            self.help_visible = True
    
    def on_close_help_message(self, message: CloseHelpMessage) -> None:
        """处理关闭帮助消息"""
        help_screen = self.query_one("#help", HelpScreen)
        help_screen.display = False
        self.help_visible = False
    
    def on_start_mixing_message(self, message: StartMixingMessage) -> None:
        """处理开始调酒消息"""
        # 切换到调酒界面并开始调酒
        game_screen = self.query_one("#game", GameScreen)
        game_screen._show_view("mixing")
        self.current_module = "mixing"
        
        # 启动调酒动画
        asyncio.create_task(self._start_mixing_process(message.ingredients))
    
    def on_start_free_mixing_message(self, message: StartFreeMixingMessage) -> None:
        """处理开始自由调酒消息"""
        # 切换到自由调酒界面并开始调酒
        game_screen = self.query_one("#game", GameScreen)
        game_screen._show_view("free-mixing")
        self.current_module = "free-mixing"
        
        # 启动自由调酒过程
        asyncio.create_task(self._start_free_mixing_process(message.ingredients))
    
    def on_start_recipe_mixing_message(self, message: StartRecipeMixingMessage) -> None:
        """处理开始按配方调制消息"""
        recipe = message.recipe
        
        # 显示配方信息
        self.notify(
            f"开始调制 {recipe.emoji} {recipe.name}...",
            title="🍸 按配方调制",
            severity="information"
        )
        
        # 启动按配方调酒过程
        asyncio.create_task(self._start_recipe_mixing_process(recipe))
    
    def on_show_recipe_details_message(self, message: ShowRecipeDetailsMessage) -> None:
        """处理显示配方详细信息消息"""
        # 显示详细的配方信息
        self.notify(
            message.details,
            title=f"📖 {message.recipe.emoji} {message.recipe.name} - 详细信息",
            severity="information"
        )
    
    async def _start_mixing_process(self, ingredients):
        """启动调酒过程"""
        try:
            # 显示调酒动画（简化版）
            await self._show_mixing_animation(ingredients)
            
            # 计算分数
            recipe_name = self.cocktail_system.find_matching_recipe(ingredients)
            if recipe_name:
                score, evaluation = self.cocktail_system.calculate_score(recipe_name, ingredients)
            else:
                # 如果没有匹配的配方，使用自由调酒评分
                score = self._calculate_free_mixing_score(ingredients)
                evaluation = "创意鸡尾酒"
            
            # 显示结果
            await self._show_mixing_result(score, recipe_name or "创意鸡尾酒", ingredients)
            
        except Exception as e:
            # 显示错误信息
            self.notify(f"调酒过程中出现错误: {str(e)}", severity="error")
    
    async def _start_free_mixing_process(self, ingredients):
        """启动自由调酒过程"""
        try:
            # 显示调酒动画
            await self._show_mixing_animation(ingredients)
            
            # 计算分数
            recipe_name = self.cocktail_system.find_matching_recipe(ingredients)
            if recipe_name:
                score, evaluation = self.cocktail_system.calculate_score(recipe_name, ingredients)
            else:
                # 如果没有匹配的配方，使用自由调酒评分
                score = self._calculate_free_mixing_score(ingredients)
                evaluation = "创意鸡尾酒"
            
            # 显示结果
            await self._show_mixing_result(score, recipe_name or "创意鸡尾酒", ingredients)
            
        except Exception as e:
            # 显示错误信息
            self.notify(f"调酒过程中出现错误: {str(e)}", severity="error")
    
    async def _start_recipe_mixing_process(self, recipe):
        """启动按配方调制过程"""
        try:
            # 显示调酒动画
            await self._show_mixing_animation(recipe.ingredients)
            
            # 按配方调制应该得到满分
            score = 100
            recipe_name = recipe.name
            
            # 显示结果
            await self._show_mixing_result(score, recipe_name, recipe.ingredients)
            
        except Exception as e:
            # 显示错误信息
            self.notify(f"按配方调制过程中出现错误: {str(e)}", severity="error")
    
    def _calculate_free_mixing_score(self, ingredients):
        """计算自由调酒的分数"""
        # 基于材料数量和搭配的简单评分系统
        score = 0
        
        # 基础分数
        ingredient_count = len([ing for ing in ingredients.values() if ing > 0])
        score += min(ingredient_count * 15, 60)  # 最多60分
        
        # 检查是否有基酒
        base_spirits = ["伏特加", "白朗姆酒", "威士忌", "龙舌兰酒", "金酒", "白兰地"]
        has_base = any(ing in ingredients and ingredients[ing] > 0 for ing in base_spirits)
        if has_base:
            score += 20
        
        # 检查是否有果汁或调酒器
        mixers = ["青柠汁", "柠檬汁", "橙汁", "蔓越莓汁", "苏打水", "汤力水", "可乐"]
        has_mixer = any(ing in ingredients and ingredients[ing] > 0 for ing in mixers)
        if has_mixer:
            score += 15
        
        # 检查是否有装饰
        garnishes = ["薄荷叶", "柠檬片", "樱桃", "橄榄", "盐", "糖浆"]
        has_garnish = any(ing in ingredients and ingredients[ing] > 0 for ing in garnishes)
        if has_garnish:
            score += 5
        
        return min(score, 100)
    
    async def _show_mixing_animation(self, ingredients):
        """显示调酒动画"""
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
            # 显示当前步骤
            self.notify(step, title="🍸 调酒中...", severity="information", timeout=1)
            await asyncio.sleep(1)
    
    async def _show_mixing_result(self, score: int, recipe_name: str, ingredients):
        """显示调酒结果"""
        # 获取配方信息和ASCII艺术
        ascii_art = ""
        if recipe_name:
            recipe = None
            for r in self.cocktail_system.get_unlocked_recipes():
                if r.name == recipe_name:
                    recipe = r
                    break
            
            if recipe and hasattr(recipe, 'ascii_art') and recipe.ascii_art:
                ascii_art = recipe.ascii_art
        
        # 创建结果界面
        if recipe_name:
            title = f"🍸 成功调制: {recipe_name}"
            content = f"""
🎉 恭喜！你成功调制了 {recipe_name}！

📊 调酒评分: {score}/100

🧪 使用材料:
{chr(10).join([f"• {name}: {amount}ml" for name, amount in ingredients.items()])}

{ascii_art}

💡 提示: 继续尝试其他配方来获得更高分数！
"""
        else:
            title = "🍹 创意调酒"
            content = f"""
🎨 很棒的创意！你调制了一杯独特的鸡尾酒！

📊 调酒评分: {score}/100

🧪 使用材料:
{chr(10).join([f"• {name}: {amount}ml" for name, amount in ingredients.items()])}

    ╭─────────────────╮
   ╱                 ╲
  ╱       🍹         ╲
 ╱     创意鸡尾酒      ╲
│                       │
│      🧊 🧊 🧊       │
│     🧊 🧊 🧊 🧊     │
│    🧊 🧊 🧊 🧊 🧊   │
│   🧊 🧊 🧊 🧊 🧊 🧊  │
│  🧊 🧊 🧊 🧊 🧊 🧊 🧊 │
│ 🧊 🧊 🧊 🧊 🧊 🧊 🧊 🧊│
│  🧊 🧊 🧊 🧊 🧊 🧊 🧊 │
│   🧊 🧊 🧊 🧊 🧊 🧊  │
│    🧊 🧊 🧊 🧊 🧊   │
│     🧊 🧊 🧊 🧊     │
│      🧊 🧊 🧊       │
│        🧊 🧊        │
│         🧊          │
│                     │
╲                     ╱
 ╲                   ╱
  ╲_________________╱

💡 提示: 尝试按照经典配方调酒来获得更高分数！
"""
        
        # 显示结果通知
        self.notify(content, title=title, severity="information")
        
        # 更新角色状态
        game_screen = self.query_one("#game", GameScreen)
        character = game_screen.query_one("#character", Container)
        if score >= 80:
            character.update_character("excited")
        elif score >= 60:
            character.update_character("happy")
        else:
            character.update_character("thinking")


def main():
    """主函数"""
    app = TermixApp()
    app.run()


if __name__ == "__main__":
    main()
