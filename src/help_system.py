"""
帮助系统模块 - 动态帮助界面
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Button, Label
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.table import Table


class HelpScreen(Container):
    """帮助界面"""
    
    def __init__(self, current_module="main", **kwargs):
        super().__init__(**kwargs)
        self.current_module = current_module
    
    def compose(self) -> ComposeResult:
        """构建帮助界面"""
        
        with Vertical(id="help-content"):
            # 标题
            yield Label("🆘 Termix 帮助中心", classes="help-title")
            
            # 滚动内容区域
            with ScrollableContainer(id="help-scroll"):
                yield Static(self._get_help_content(), id="help-text")
            
            # 底部按钮
            with Horizontal(classes="help-buttons"):
                yield Button("🔄 刷新", id="refresh-help", variant="primary")
                yield Button("❌ 关闭", id="close-help", variant="error")
    
    def _get_help_content(self) -> str:
        """根据当前模块获取帮助内容"""
        
        if self.current_module == "main":
            return self._get_main_help()
        elif self.current_module == "ingredients":
            return self._get_ingredients_help()
        elif self.current_module == "recipes":
            return self._get_recipes_help()
        elif self.current_module == "mixing":
            return self._get_mixing_help()
        elif self.current_module == "free-mixing":
            return self._get_free_mixing_help()
        else:
            return self._get_general_help()
    
    def _get_main_help(self) -> str:
        """主界面帮助"""
        return """
🎮 [bold cyan]主界面操作指南 (全键盘操作)[/bold cyan]

[bold yellow]全局导航快捷键：[/bold yellow]
• [bold green]F1[/bold green] - 切换到材料界面
• [bold green]F2[/bold green] - 切换到配方界面
• [bold green]F3[/bold green] - 切换到标准调酒界面
• [bold green]F4[/bold green] - 切换到自由调酒界面
• [bold green]F5[/bold green] - 切换到快速参考界面

[bold yellow]导航按钮：[/bold yellow]
• 🧪 材料 - 查看所有可用的调酒材料
• 📖 配方 - 浏览经典鸡尾酒配方
• 🍸 标准调酒 - 按照经典配方调制
• 🎨 自由调酒 - 发挥创意自由调制
• 🔄 切换布局 - 切换水平/垂直布局

[bold yellow]键盘快捷键：[/bold yellow]
• ↑↓←→ - 滚动界面内容
• Page Up/Down - 快速滚动
• Home/End - 滚动到顶部/底部
• F8 - 显示帮助
• F11 - 切换布局模式
• Ctrl+C - 退出游戏
• Escape - 返回欢迎界面
• Tab - 切换焦点

[bold yellow]界面特性：[/bold yellow]
• 自适应布局：根据终端大小自动调整
• 方向键滚动：在界面内滚动，不影响终端
• 实时反馈：操作结果即时显示

💡 [bold green]小贴士：[/bold green]
使用F1-F5可以快速在不同功能模块间切换！
        """
    
    def _get_ingredients_help(self) -> str:
        """材料界面帮助"""
        return """
🧪 [bold cyan]材料选择帮助 (全键盘操作)[/bold cyan]

[bold yellow]键盘快捷键：[/bold yellow]
• [bold green]1-6[/bold green] 选择当前页面的材料
• [bold green]A/←[/bold green] 翻到上一页
• [bold green]D/→[/bold green] 翻到下一页
• [bold green]↑↓[/bold green] 切换聚焦的材料
• [bold green]C[/bold green] 清空所有选择
• [bold green]Enter[/bold green] 开始调酒
• [bold green]F1-F5[/bold green] 切换到其他界面
• [bold green]F8[/bold green] 显示帮助

[bold yellow]材料分类：[/bold yellow]
• 基酒 - 鸡尾酒的主体，如朗姆酒、伏特加等
• 利口酒 - 增加风味的甜酒，如君度橙酒
• 调和剂 - 果汁、糖浆、苏打水等
• 装饰 - 薄荷叶、柠檬片等装饰材料
• 冰块 - 标准冰块或碎冰

[bold yellow]操作方法：[/bold yellow]
• 每页显示6种材料，编号1-6
• 重复按数字键可增加材料用量（每次+15ml）
• 用量超过200ml时会自动移除
• 当前聚焦的材料会高亮显示
• 查看当前选择的总酒精度

[bold yellow]材料选择技巧：[/bold yellow]
• 每杯鸡尾酒至少需要一种基酒
• 适量的调和剂能平衡口感
• 装饰材料能提升视觉效果
• 冰块是大多数鸡尾酒的必需品

💡 [bold green]小贴士：[/bold green]
观察材料的酒精度和风味特点，有助于调制出更好的鸡尾酒！
        """
    
    def _get_recipes_help(self) -> str:
        """配方界面帮助"""
        return """
📖 [bold cyan]配方浏览帮助 (全键盘操作)[/bold cyan]

[bold yellow]键盘快捷键：[/bold yellow]
• [bold green]1-3[/bold green] 查看当前页面的配方详情
• [bold green]A/←[/bold green] 翻到上一页
• [bold green]D/→[/bold green] 翻到下一页
• [bold green]F1-F5[/bold green] 切换到其他界面
• [bold green]F8[/bold green] 显示帮助

[bold yellow]配方分类：[/bold yellow]
• 经典系列 - 莫吉托、玛格丽特、马提尼等传统配方
• 热带系列 - 椰林飘香、蓝色夏威夷等热带风味
• 果味系列 - 性感海滩、大都会等果味鸡尾酒
• 咖啡系列 - 白俄罗斯、爱尔兰咖啡等咖啡味
• 创意系列 - 莫斯科骡子、长岛冰茶等创新配方

[bold yellow]配方信息：[/bold yellow]
• 配方名称和描述
• 详细的材料用量表
• 难度等级（1-5星）
• 风味标签

[bold yellow]如何使用配方：[/bold yellow]
1. 浏览配方了解制作方法
2. 记住感兴趣的配方材料
3. 切换到"🍸 标准调酒"模式
4. 或在"🎨 自由调酒"中参考制作

💡 [bold green]小贴士：[/bold green]
初学者建议从1-2星难度的配方开始尝试！
        """
    
    def _get_mixing_help(self) -> str:
        """标准调酒帮助"""
        return """
🍸 [bold cyan]标准调酒帮助[/bold cyan]

[bold yellow]调酒流程：[/bold yellow]
1. 选择要调制的鸡尾酒配方
2. 按照配方添加材料
3. 观看精美的调酒动画
4. 获得评分和专业反馈

[bold yellow]评分标准：[/bold yellow]
• 90-100分：完美！🌟
• 80-89分：很棒！👏
• 70-79分：不错！👍
• 60-69分：还可以 😊
• 0-59分：需要改进 😅

[bold yellow]评分影响因素：[/bold yellow]
• 材料完整性（缺少材料扣20分）
• 用量准确性（偏差大扣15分，略偏差扣8分）
• 多余材料（每种多余材料扣10分）

[bold yellow]调酒技巧：[/bold yellow]
• 严格按照配方用量
• 不要添加配方外的材料
• 注意材料的添加顺序
• 冰块用量影响最终口感

💡 [bold green]小贴士：[/bold green]
完美复制配方是获得高分的关键！
        """
    
    def _get_free_mixing_help(self) -> str:
        """自由调酒帮助"""
        return """
🎨 [bold cyan]自由调酒帮助[/bold cyan]

[bold yellow]创意调酒流程：[/bold yellow]
1. 从材料下拉框选择材料
2. 输入用量（建议15-60ml）
3. 点击"➕ 添加"加入配方
4. 重复添加其他材料
5. 点击"🍸 开始调酒"制作

[bold yellow]侧边面板：[/bold yellow]
• 🧪 材料清单 - 查看所有材料信息
• 📖 配方参考 - 参考经典配方
• 👁️ 切换面板 - 隐藏/显示侧边面板

[bold yellow]智能功能：[/bold yellow]
• 自动配方匹配 - 识别是否匹配已知配方
• 实时酒精度计算 - 显示当前配方的酒精度
• 智能评分 - 根据材料搭配给出评分

[bold yellow]创意调酒技巧：[/bold yellow]
• 选择一种基酒作为主体（40-60ml）
• 添加1-2种调和剂平衡口感（20-40ml）
• 适量装饰材料提升品质（5-15ml）
• 冰块是必需的（100-200ml）
• 总材料数量控制在3-6种

[bold yellow]推荐搭配：[/bold yellow]
• 朗姆酒 + 青柠汁 + 薄荷叶 = 清爽热带风
• 伏特加 + 蔓越莓汁 + 青柠汁 = 果味酸甜
• 威士忌 + 柠檬汁 + 糖浆 = 经典酸甜平衡

💡 [bold green]小贴士：[/bold green]
大胆尝试不同搭配，也许能创造出惊喜的味道！
        """
    
    def _get_general_help(self) -> str:
        """通用帮助"""
        return """
🍸 [bold cyan]Termix 通用帮助[/bold cyan]

[bold yellow]游戏简介：[/bold yellow]
Termix是一个终端调酒游戏，让你与可爱的兔女郎调酒师一起学习调酒技艺。

[bold yellow]主要功能：[/bold yellow]
• 🧪 材料系统 - 30+种真实调酒材料
• 📖 配方系统 - 18种经典鸡尾酒配方
• 🍸 标准调酒 - 按配方学习调酒
• 🎨 自由调酒 - 发挥创意调制
• 🐰 角色互动 - 与兔女郎调酒师互动

[bold yellow]全局快捷键：[/bold yellow]
• F1 - 显示当前模块帮助
• F11 - 切换布局模式
• Escape - 返回上级界面
• ↑↓←→ - 滚动界面
• Tab - 切换焦点

[bold yellow]界面说明：[/bold yellow]
• 左侧/上方：兔女郎角色区域
• 右侧/下方：功能操作区域
• 顶部：导航按钮栏
• 底部：状态栏

💡 [bold green]小贴士：[/bold green]
随时按F1获取当前界面的详细帮助！
        """
    
    def update_module(self, module_name: str):
        """更新当前模块"""
        self.current_module = module_name
        help_text = self.query_one("#help-text", Static)
        help_text.update(self._get_help_content())
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        if event.button.id == "refresh-help":
            self.update_module(self.current_module)
        elif event.button.id == "close-help":
            self.post_message(CloseHelpMessage())


class CloseHelpMessage(Message):
    """关闭帮助消息"""
    pass
