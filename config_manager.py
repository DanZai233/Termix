#!/usr/bin/env python3
"""
配置管理工具 - 管理Termix的配置文件
"""

import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from src.config_loader import ConfigLoader


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.console = Console()
        self.config_loader = ConfigLoader()
    
    def run(self):
        """运行配置管理器"""
        self.console.print(Panel(
            "[bold cyan]🍸 Termix 配置管理工具 🍸[/bold cyan]\n\n"
            "管理游戏的材料、配方和设置",
            border_style="magenta"
        ))
        
        while True:
            self.console.print("\n[bold cyan]选择操作:[/bold cyan]")
            self.console.print("1. 查看当前配置")
            self.console.print("2. 验证配置文件")
            self.console.print("3. 创建示例配置")
            self.console.print("4. 添加新材料")
            self.console.print("5. 添加新配方")
            self.console.print("6. 退出")
            
            choice = Prompt.ask("请选择", choices=["1", "2", "3", "4", "5", "6"])
            
            if choice == "1":
                self.show_current_config()
            elif choice == "2":
                self.validate_configs()
            elif choice == "3":
                self.create_sample_configs()
            elif choice == "4":
                self.add_ingredient()
            elif choice == "5":
                self.add_recipe()
            elif choice == "6":
                self.console.print("[cyan]再见！[/cyan]")
                break
    
    def show_current_config(self):
        """显示当前配置"""
        self.console.clear()
        
        # 显示材料统计
        ingredients = self.config_loader.load_ingredients()
        self.console.print(f"[bold green]📊 当前配置统计[/bold green]\n")
        self.console.print(f"材料总数: {len(ingredients)}")
        
        # 按类型统计材料
        type_counts = {}
        for ingredient in ingredients.values():
            type_name = ingredient.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        table = Table(title="材料分类统计")
        table.add_column("类型", style="cyan")
        table.add_column("数量", style="magenta")
        
        for type_name, count in type_counts.items():
            table.add_row(type_name, str(count))
        
        self.console.print(table)
        
        # 显示配方统计
        recipes = self.config_loader.load_recipes()
        self.console.print(f"\n配方总数: {len(recipes)}")
        
        # 按难度统计配方
        difficulty_counts = {}
        for recipe in recipes.values():
            difficulty = recipe.difficulty
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
        
        recipe_table = Table(title="配方难度统计")
        recipe_table.add_column("难度", style="cyan")
        recipe_table.add_column("数量", style="magenta")
        
        for difficulty in sorted(difficulty_counts.keys()):
            stars = "⭐" * difficulty
            recipe_table.add_row(f"{difficulty} {stars}", str(difficulty_counts[difficulty]))
        
        self.console.print(recipe_table)
        
        Prompt.ask("\n按回车继续...")
    
    def validate_configs(self):
        """验证配置文件"""
        self.console.clear()
        self.console.print("[bold yellow]🔍 验证配置文件...[/bold yellow]\n")
        
        # 验证材料配置
        try:
            with open(self.config_loader.ingredients_file, 'r', encoding='utf-8') as f:
                ingredients_data = json.load(f)
            
            ingredient_errors = self.config_loader.validate_config("ingredients", ingredients_data)
            if ingredient_errors:
                self.console.print("[bold red]❌ 材料配置错误:[/bold red]")
                for error in ingredient_errors:
                    self.console.print(f"  • {error}")
            else:
                self.console.print("[bold green]✅ 材料配置文件格式正确[/bold green]")
        
        except Exception as e:
            self.console.print(f"[bold red]❌ 材料配置文件读取失败: {e}[/bold red]")
        
        # 验证配方配置
        try:
            with open(self.config_loader.recipes_file, 'r', encoding='utf-8') as f:
                recipes_data = json.load(f)
            
            recipe_errors = self.config_loader.validate_config("recipes", recipes_data)
            if recipe_errors:
                self.console.print("\n[bold red]❌ 配方配置错误:[/bold red]")
                for error in recipe_errors:
                    self.console.print(f"  • {error}")
            else:
                self.console.print("[bold green]✅ 配方配置文件格式正确[/bold green]")
        
        except Exception as e:
            self.console.print(f"[bold red]❌ 配方配置文件读取失败: {e}[/bold red]")
        
        Prompt.ask("\n按回车继续...")
    
    def create_sample_configs(self):
        """创建示例配置"""
        self.console.clear()
        
        if Confirm.ask("这将创建示例配置文件，是否继续？"):
            self.config_loader.create_sample_configs()
            self.console.print("[bold green]✅ 示例配置文件已创建[/bold green]")
        
        Prompt.ask("\n按回车继续...")
    
    def add_ingredient(self):
        """添加新材料"""
        self.console.clear()
        self.console.print("[bold cyan]➕ 添加新材料[/bold cyan]\n")
        
        # 获取材料信息
        name = Prompt.ask("材料名称")
        
        self.console.print("\n材料类型:")
        self.console.print("1. BASE_SPIRIT (基酒)")
        self.console.print("2. LIQUEUR (利口酒)")
        self.console.print("3. MIXER (调和剂)")
        self.console.print("4. GARNISH (装饰)")
        self.console.print("5. ICE (冰块)")
        
        type_choice = Prompt.ask("选择类型", choices=["1", "2", "3", "4", "5"])
        type_map = {
            "1": "BASE_SPIRIT",
            "2": "LIQUEUR", 
            "3": "MIXER",
            "4": "GARNISH",
            "5": "ICE"
        }
        ingredient_type = type_map[type_choice]
        
        color = Prompt.ask("颜色")
        flavor_profile = Prompt.ask("风味特点 (用逗号分隔)").split(",")
        flavor_profile = [f.strip() for f in flavor_profile]
        
        try:
            alcohol_content = float(Prompt.ask("酒精度 (%)"))
        except ValueError:
            alcohol_content = 0.0
        
        emoji = Prompt.ask("表情符号")
        description = Prompt.ask("描述")
        
        # 创建新材料数据
        new_ingredient = {
            "name": name,
            "type": ingredient_type,
            "color": color,
            "flavor_profile": flavor_profile,
            "alcohol_content": alcohol_content,
            "emoji": emoji,
            "description": description
        }
        
        # 加载现有配置
        try:
            with open(self.config_loader.ingredients_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {"ingredients": []}
        
        # 添加新材料
        data["ingredients"].append(new_ingredient)
        
        # 保存配置
        try:
            with open(self.config_loader.ingredients_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.console.print(f"[bold green]✅ 材料 '{name}' 已添加到配置文件[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]❌ 保存失败: {e}[/bold red]")
        
        Prompt.ask("\n按回车继续...")
    
    def add_recipe(self):
        """添加新配方"""
        self.console.clear()
        self.console.print("[bold cyan]➕ 添加新配方[/bold cyan]\n")
        
        # 获取配方信息
        name = Prompt.ask("配方名称")
        category = Prompt.ask("配方分类 (如: 经典系列)")
        description = Prompt.ask("配方描述")
        
        try:
            difficulty = int(Prompt.ask("难度等级 (1-5)"))
            difficulty = max(1, min(5, difficulty))
        except ValueError:
            difficulty = 1
        
        emoji = Prompt.ask("表情符号")
        flavor_tags = Prompt.ask("风味标签 (用逗号分隔)").split(",")
        flavor_tags = [f.strip() for f in flavor_tags]
        
        # 获取材料配方
        self.console.print("\n[bold yellow]添加材料 (输入 'done' 完成):[/bold yellow]")
        ingredients = {}
        
        # 显示可用材料
        available_ingredients = self.config_loader.load_ingredients()
        self.console.print("\n可用材料:")
        for i, ingredient_name in enumerate(available_ingredients.keys(), 1):
            self.console.print(f"{i:2d}. {ingredient_name}")
        
        while True:
            ingredient_name = Prompt.ask("\n材料名称 (或输入 'done' 完成)")
            if ingredient_name.lower() == 'done':
                break
            
            if ingredient_name not in available_ingredients:
                self.console.print(f"[red]材料 '{ingredient_name}' 不存在，请检查拼写[/red]")
                continue
            
            try:
                amount = float(Prompt.ask(f"{ingredient_name} 的用量 (ml)"))
                ingredients[ingredient_name] = amount
                self.console.print(f"[green]已添加: {ingredient_name} {amount}ml[/green]")
            except ValueError:
                self.console.print("[red]请输入有效的数字[/red]")
        
        if not ingredients:
            self.console.print("[red]配方至少需要一种材料[/red]")
            Prompt.ask("\n按回车继续...")
            return
        
        # 创建新配方数据
        new_recipe = {
            "name": name,
            "category": category,
            "ingredients": ingredients,
            "description": description,
            "difficulty": difficulty,
            "emoji": emoji,
            "flavor_tags": flavor_tags
        }
        
        # 加载现有配置
        try:
            with open(self.config_loader.recipes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {"recipes": []}
        
        # 添加新配方
        data["recipes"].append(new_recipe)
        
        # 保存配置
        try:
            with open(self.config_loader.recipes_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.console.print(f"[bold green]✅ 配方 '{name}' 已添加到配置文件[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]❌ 保存失败: {e}[/bold red]")
        
        Prompt.ask("\n按回车继续...")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Termix 配置管理工具

用法:
  python config_manager.py          # 启动交互式配置管理器
  python config_manager.py --help   # 显示此帮助信息

功能:
  • 查看当前配置统计
  • 验证配置文件格式
  • 创建示例配置文件
  • 添加新的材料和配方
        """)
        return
    
    manager = ConfigManager()
    manager.run()


if __name__ == "__main__":
    main()
