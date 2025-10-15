# Termix 🍸

一个美观的终端调酒游戏，结合了 Terminal 和 Mix 的概念。

## 特性

- 🐰 可爱的ASCII艺术兔女郎角色
- 🍹 丰富的调酒材料和配方系统（30+材料，18个配方）
- ✨ 精美的终端动画效果
- 🎮 互动式调酒小游戏体验
- 🌈 现代化的终端UI界面
- ⌨️ 全键盘操作支持，无需鼠标
- 🔧 外置配置文件，支持自定义材料和配方
- 🆘 动态帮助系统，随时获取操作指导
- 📱 自适应布局，支持不同终端尺寸

## 安装

```bash
# 克隆项目
git clone <your-repo-url>
cd Termix

# 方法1: 使用启动脚本（推荐）
chmod +x run.sh
./run.sh

# 方法2: 手动安装
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 运行完整版游戏
python main.py

# 或运行演示版本
python demo.py
```

## 游戏玩法

### 🍸 标准调酒模式
1. 选择经典鸡尾酒配方
2. 按照配方添加材料
3. 观看精美的调酒动画
4. 获得专业评分和反馈

### 🎨 自由调酒模式
1. 从30+种材料中自由选择
2. 设置每种材料的用量
3. 创造独特的鸡尾酒配方
4. 系统自动识别匹配的经典配方

### ⌨️ 键盘操作
- **1-5** - 快速切换功能模块
- **F1** - 显示帮助
- **F11** - 切换布局
- **↑↓←→** - 界面滚动
- **1-6** - 材料界面选择材料
- **A/D** - 翻页操作
- **C** - 清空选择
- **Enter** - 确认操作

详细操作请参考 [键盘操作指南.md](键盘操作指南.md)

### 🔧 配置管理
```bash
# 使用配置管理工具
python config_manager.py

# 功能包括：
# • 查看当前配置统计
# • 验证配置文件格式
# • 添加新材料和配方
# • 创建示例配置
```

## 技术栈

- Python 3.8+
- Rich - 终端美化库
- Textual - 现代终端UI框架
- PyFiglet - ASCII艺术文字
