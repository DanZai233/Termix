#!/usr/bin/env python3
"""
Termix - 终端调酒游戏
一个美观的终端调酒应用，让你体验调酒的乐趣
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button
from textual.events import Key, Resize

from src.character import BunnyGirl
from src.cocktail_system import CocktailSystem
from src.ui_components import (
    WelcomeScreen, GameScreen, HelpScreen, CloseHelpMessage,
)


class TermixApp(App):
    """Termix 主应用程序"""

    CSS_PATH = "styles.css"
    TITLE = "Termix - 终端调酒游戏"
    SUB_TITLE = "🍸 让我们一起调制美味的鸡尾酒吧！"

    BINDINGS = [
        ("escape", "go_back", "返回"),
        ("f8", "toggle_help", "帮助"),
    ]

    def __init__(self):
        super().__init__()
        self.bunny_girl = BunnyGirl()
        self.cocktail_system = CocktailSystem()
        self.help_visible = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield WelcomeScreen(id="welcome")
        yield GameScreen(
            id="game",
            bunny_girl=self.bunny_girl,
            cocktail_system=self.cocktail_system,
        )
        yield HelpScreen(id="help")
        yield Footer()

    def on_mount(self) -> None:
        self._show_welcome()

    def _show_welcome(self):
        self.query_one("#welcome").display = True
        self.query_one("#game").display = False
        self.query_one("#help").display = False
        self.help_visible = False

    def _show_game(self):
        self.query_one("#welcome").display = False
        self.query_one("#game").display = True
        self.query_one("#help").display = False
        self.help_visible = False

    def _toggle_help(self):
        help_screen = self.query_one("#help")
        self.help_visible = not self.help_visible
        help_screen.display = self.help_visible

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start_game":
            self._show_game()

    def action_go_back(self):
        if self.help_visible:
            self._toggle_help()
        else:
            self._show_welcome()

    def action_toggle_help(self):
        self._toggle_help()

    def on_close_help_message(self, message: CloseHelpMessage) -> None:
        self.help_visible = False
        self.query_one("#help").display = False


def main():
    app = TermixApp()
    app.run()


if __name__ == "__main__":
    main()
