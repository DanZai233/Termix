# Termix 🍸

一个美观的终端调酒游戏，结合了 Terminal 和 Mix 的概念。

## 特性

- 🐰 可爱的ASCII艺术兔女郎角色
- 🍹 丰富的调酒材料和配方系统
- ✨ 精美的终端动画效果
- 🎮 互动式调酒小游戏体验
- 🌈 现代化的终端UI界面

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

1. 选择调酒材料
2. 观看精美的调酒动画
3. 获得评分和反馈
4. 解锁新的配方和材料

## 技术栈

- Python 3.8+
- Rich - 终端美化库
- Textual - 现代终端UI框架
- PyFiglet - ASCII艺术文字
