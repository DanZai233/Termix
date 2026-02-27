"""
角色模块 - 可爱二次元风格的兔女郎调酒师
"""

import random


class BunnyGirl:
    """兔女郎角色类 - 紧凑可爱的二次元风格"""

    def __init__(self):
        self.name = "小兔"
        self.mood = "happy"

    def get_ascii_art(self, mood="happy", frame=0):
        if mood == "working":
            return self._get_working(frame)
        elif mood == "excited":
            return self._get_excited(frame)
        elif mood == "thinking":
            return self._get_thinking()
        elif mood == "pouring":
            return self._get_pouring(frame)
        return self._get_happy(frame)

    def _get_happy(self, frame=0):
        sparkle = ["♡", "✧", "♪"][frame % 3]
        return f"""\
     ╱\\ ╱\\
    ╱  ╲╱  ╲
   │  ◕  ◕  │  {sparkle}
   │   ▽    │
    ╲ ╰▽╯ ╱
     ╲    ╱
    ╱│ 🍸 │╲
   ╱ │    │ ╲
      ╰──╯"""

    def _get_working(self, frame=0):
        eyes = ["◕‿◕", "◕ᴗ◕", "◔‿◔"][frame % 3]
        left, right = eyes[:3], eyes[3:]
        return f"""\
     ╱\\ ╱\\
    ╱  ╲╱  ╲
   │  {left}{right}  │  ✨
   │   ▽    │
    ╲ ╰◡╯ ╱
     ╲  ⌒╱
    ╱│🍸🥄│╲
   ╱ │    │ ╲
      ╰──╯"""

    def _get_excited(self, frame=0):
        sparkle = ["✨✨", "⭐⭐", "💫💫"][frame % 3]
        return f"""\
     ╱\\ ╱\\    {sparkle}
    ╱  ╲╱  ╲
   │  ◕ω◕  │
   │   ▽    │
    ╲ ╰▽╯ ╱
     ╲ ╱╲╱
    ╱│ 🍸 │╲  🎉
   ╱ │    │ ╲
      ╰──╯"""

    def _get_thinking(self):
        return """\
     ╱\\ ╱\\
    ╱  ╲╱  ╲
   │  ◑  ◑  │  ?
   │   ▽    │
    ╲ ╰～╯ ╱
     ╲    ╱
    ╱│    │╲
   ╱ │    │ ╲
      ╰──╯"""

    def _get_pouring(self, frame=0):
        drops = ["  ░", " ░░", "░░░", "▒▒▒"][frame % 4]
        return f"""\
     ╱\\ ╱\\
    ╱  ╲╱  ╲
   │  ◕‿◕  │
   │   ▽    │
    ╲ ╰◡╯ ╱
     ╲    ╱🫗
    ╱│   {drops}╲
   ╱ │    │ ╲
      ╰──╯"""

    def get_dialogue(self, context="greeting"):
        dialogues = {
            "greeting": [
                "欢迎光临～想喝点什么呢？",
                "今天想调制什么鸡尾酒呢？✧",
                "让我们一起调酒吧！🍸",
            ],
            "working": [
                "正在精心调制中…请稍等～",
                "摇一摇、搅一搅…♪",
                "调酒是一门艺术呢！",
            ],
            "success": [
                "太棒了！完美的一杯！✨",
                "好厉害，调得真好看！",
                "这杯一定很好喝～🍸",
            ],
            "encouragement": [
                "再试一次吧，你可以的！",
                "熟能生巧，继续加油～♪",
                "每次都在进步呢！",
            ],
            "glass_select": [
                "选一个喜欢的杯子吧！",
                "不同的杯子有不同的风味哦～",
                "杯子的选择也很重要呢！",
            ],
            "pouring": [
                "小心翼翼地倒入…",
                "看着液体缓缓流入杯中…✧",
                "完美的用量！",
            ],
        }
        return random.choice(dialogues.get(context, dialogues["greeting"]))

    def show_character(self, mood="happy"):
        from rich.panel import Panel
        from rich.align import Align
        art = self.get_ascii_art(mood)
        dialogue = self.get_dialogue("greeting")
        return Panel(
            Align.center(f"{art}\n\n💬 {dialogue}"),
            title="🐰 调酒师小兔",
            border_style="magenta",
        )
