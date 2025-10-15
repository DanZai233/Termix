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
from src.ui_components import WelcomeScreen, GameScreen
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


def main():
    """主函数"""
    app = TermixApp()
    app.run()


if __name__ == "__main__":
    main()
