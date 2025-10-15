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
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

from src.character import BunnyGirl
from src.cocktail_system import CocktailSystem
from src.ui_components import WelcomeScreen, GameScreen


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
    
    def compose(self) -> ComposeResult:
        """构建应用界面"""
        yield Header()
        yield WelcomeScreen(id="welcome")
        yield GameScreen(id="game", bunny_girl=self.bunny_girl, cocktail_system=self.cocktail_system)
        yield Footer()
    
    def on_mount(self) -> None:
        """应用挂载时的初始化"""
        self.show_welcome_screen()
    
    def show_welcome_screen(self):
        """显示欢迎界面"""
        welcome = self.query_one("#welcome", WelcomeScreen)
        game = self.query_one("#game", GameScreen)
        welcome.display = True
        game.display = False
    
    def show_game_screen(self):
        """显示游戏界面"""
        welcome = self.query_one("#welcome", WelcomeScreen)
        game = self.query_one("#game", GameScreen)
        welcome.display = False
        game.display = True
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "start_game":
            self.show_game_screen()


def main():
    """主函数"""
    app = TermixApp()
    app.run()


if __name__ == "__main__":
    main()
