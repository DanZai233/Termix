#!/usr/bin/env python3
"""
Termix 演示版本 - 简化的终端调酒游戏
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.prompt import Prompt, Confirm
import time
import random

from src.character import BunnyGirl
from src.cocktail_system import CocktailSystem


class TermixDemo:
    """Termix 演示版本"""
    
    def __init__(self):
        self.console = Console()
        self.bunny_girl = BunnyGirl()
        self.cocktail_system = CocktailSystem()
    
    def show_title(self):
        """显示标题"""
        title = Text()
        title.append("🍸 ", style="bold magenta")
        title.append("Termix", style="bold cyan")
        title.append(" 🍸", style="bold magenta")
        
        subtitle = "终端调酒游戏 - 与兔女郎一起调酒！"
        
        panel = Panel(
            Align.center(f"{title}\n\n{subtitle}"),
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        time.sleep(2)
    
    def show_character_intro(self):
        """显示角色介绍"""
        self.console.clear()
        self.console.print(self.bunny_girl.show_character("happy"))
        time.sleep(3)
    
    def show_ingredients(self):
        """显示可用材料"""
        self.console.clear()
        
        table = Table(title="🧪 可用调酒材料")
        table.add_column("材料", style="cyan")
        table.add_column("类型", style="magenta")
        table.add_column("描述", style="green")
        table.add_column("酒精度", style="yellow")
        
        for ingredient in self.cocktail_system.get_available_ingredients():
            table.add_row(
                f"{ingredient.emoji} {ingredient.name}",
                ingredient.type.value,
                ingredient.description,
                f"{ingredient.alcohol_content}%"
            )
        
        self.console.print(table)
        self.console.print(f"\n💡 {self.cocktail_system.get_random_recipe_hint()}")
    
    def show_recipes(self):
        """显示配方"""
        self.console.clear()
        
        self.console.print("[bold cyan]📖 配方大全[/bold cyan]\n")
        
        for recipe in self.cocktail_system.get_unlocked_recipes():
            # 创建配方表格
            recipe_table = Table(title=f"{recipe.emoji} {recipe.name}")
            recipe_table.add_column("材料", style="cyan")
            recipe_table.add_column("用量", style="magenta")
            
            for ingredient_name, amount in recipe.ingredients.items():
                recipe_table.add_row(ingredient_name, f"{amount}ml")
            
            self.console.print(recipe_table)
            self.console.print(f"[italic]{recipe.description}[/italic]")
            self.console.print(f"难度: {'⭐' * recipe.difficulty}\n")
    
    def mixing_animation(self, recipe_name):
        """调酒动画"""
        self.console.clear()
        
        steps = [
            "🧊 准备冰块...",
            "🥃 倒入基酒...",
            "🍋 添加果汁...",
            "🍯 加入糖浆...",
            "🥄 搅拌混合...",
            "🌿 装饰点缀...",
            "✨ 完成调制！"
        ]
        
        for step in steps:
            self.console.clear()
            
            # 显示兔女郎工作状态
            art = self.bunny_girl.get_ascii_art("working", random.randint(0, 5))
            dialogue = self.bunny_girl.get_dialogue("working")
            
            panel = Panel(
                Align.center(f"{art}\n\n💬 {dialogue}\n\n{step}"),
                title=f"🍸 正在调制 {recipe_name}",
                border_style="cyan"
            )
            
            self.console.print(panel)
            time.sleep(1.5)
    
    def show_result(self, recipe_name, score, evaluation):
        """显示调酒结果"""
        self.console.clear()
        
        # 显示兴奋状态的兔女郎
        art = self.bunny_girl.get_ascii_art("excited", 0)
        dialogue = self.bunny_girl.get_dialogue("success")
        
        result_text = f"""
{art}

💬 {dialogue}

🍸 {recipe_name} 调制完成！
📊 得分: {score}/100
⭐ 评价: {evaluation}
        """
        
        panel = Panel(
            Align.center(result_text),
            title="🎉 调酒完成！",
            border_style="green"
        )
        
        self.console.print(panel)
    
    def interactive_mixing(self):
        """交互式调酒"""
        self.console.clear()
        
        # 选择调酒模式
        self.console.print("[bold cyan]选择调酒模式:[/bold cyan]\n")
        self.console.print("1. 📖 按配方调酒")
        self.console.print("2. 🎨 自由调酒")
        
        mode_choice = Prompt.ask("\n请选择模式", choices=["1", "2"])
        
        if mode_choice == "1":
            self._recipe_mixing()
        else:
            self._free_mixing()
    
    def _recipe_mixing(self):
        """按配方调酒"""
        self.console.clear()
        
        # 选择配方
        recipes = self.cocktail_system.get_unlocked_recipes()
        self.console.print("[bold cyan]选择要调制的鸡尾酒:[/bold cyan]\n")
        
        for i, recipe in enumerate(recipes, 1):
            self.console.print(f"{i}. {recipe.emoji} {recipe.name} - {recipe.description}")
        
        while True:
            try:
                choice = int(Prompt.ask("\n请选择配方编号")) - 1
                if 0 <= choice < len(recipes):
                    selected_recipe = recipes[choice]
                    break
                else:
                    self.console.print("[red]无效选择，请重试[/red]")
            except ValueError:
                self.console.print("[red]请输入数字[/red]")
        
        # 播放调酒动画
        self.mixing_animation(selected_recipe.name)
        
        # 模拟完美调酒（演示版本）
        score, evaluation = self.cocktail_system.calculate_score(
            selected_recipe.name, 
            selected_recipe.ingredients
        )
        
        # 显示结果
        self.show_result(selected_recipe.name, score, evaluation)
    
    def _free_mixing(self):
        """自由调酒"""
        self.console.clear()
        
        self.console.print("[bold cyan]🎨 自由调酒模式[/bold cyan]\n")
        self.console.print("你可以自由选择材料和用量来创造独特的鸡尾酒！\n")
        
        selected_ingredients = {}
        
        while True:
            # 显示当前配方
            if selected_ingredients:
                self.console.print("\n[bold]当前配方:[/bold]")
                for name, amount in selected_ingredients.items():
                    ingredient = self.cocktail_system.ingredients[name]
                    self.console.print(f"• {ingredient.emoji} {name}: {amount}ml")
            
            self.console.print("\n[bold cyan]选择操作:[/bold cyan]")
            self.console.print("1. 添加材料")
            self.console.print("2. 开始调酒")
            self.console.print("3. 清空配方")
            self.console.print("4. 返回主菜单")
            
            action = Prompt.ask("请选择", choices=["1", "2", "3", "4"])
            
            if action == "1":
                self._add_ingredient_interactive(selected_ingredients)
            elif action == "2":
                if selected_ingredients:
                    self._mix_free_cocktail(selected_ingredients)
                    break
                else:
                    self.console.print("[red]请先添加一些材料！[/red]")
            elif action == "3":
                selected_ingredients.clear()
                self.console.print("[yellow]配方已清空[/yellow]")
            elif action == "4":
                break
    
    def _add_ingredient_interactive(self, selected_ingredients):
        """交互式添加材料"""
        self.console.clear()
        
        # 显示材料列表
        ingredients = self.cocktail_system.get_available_ingredients()
        self.console.print("[bold cyan]可用材料:[/bold cyan]\n")
        
        for i, ingredient in enumerate(ingredients, 1):
            self.console.print(f"{i:2d}. {ingredient.emoji} {ingredient.name} ({ingredient.type.value}) - {ingredient.description}")
        
        while True:
            try:
                choice = int(Prompt.ask("\n请选择材料编号")) - 1
                if 0 <= choice < len(ingredients):
                    selected_ingredient = ingredients[choice]
                    break
                else:
                    self.console.print("[red]无效选择，请重试[/red]")
            except ValueError:
                self.console.print("[red]请输入数字[/red]")
        
        # 输入用量
        while True:
            try:
                amount = float(Prompt.ask(f"请输入 {selected_ingredient.name} 的用量(ml)"))
                if amount > 0:
                    break
                else:
                    self.console.print("[red]用量必须大于0[/red]")
            except ValueError:
                self.console.print("[red]请输入有效数字[/red]")
        
        # 添加到配方
        if selected_ingredient.name in selected_ingredients:
            selected_ingredients[selected_ingredient.name] += amount
        else:
            selected_ingredients[selected_ingredient.name] = amount
        
        self.console.print(f"[green]已添加 {selected_ingredient.emoji} {selected_ingredient.name} {amount}ml[/green]")
        time.sleep(1)
    
    def _mix_free_cocktail(self, selected_ingredients):
        """调制自由鸡尾酒"""
        # 尝试匹配已知配方
        matched_recipe = None
        for recipe_name, recipe in self.cocktail_system.recipes.items():
            if self._recipes_similar(selected_ingredients, recipe.ingredients):
                matched_recipe = recipe_name
                break
        
        # 播放调酒动画
        cocktail_name = matched_recipe or "创意鸡尾酒"
        self.mixing_animation(cocktail_name)
        
        # 计算得分
        if matched_recipe:
            score, evaluation = self.cocktail_system.calculate_score(matched_recipe, selected_ingredients)
        else:
            # 自创鸡尾酒的评分逻辑
            score = self._evaluate_free_cocktail(selected_ingredients)
            if score >= 80:
                evaluation = "创意十足！"
            elif score >= 60:
                evaluation = "不错的尝试！"
            else:
                evaluation = "继续努力！"
        
        # 显示结果
        self.show_result(cocktail_name, score, evaluation)
    
    def _recipes_similar(self, recipe1, recipe2, tolerance=0.3):
        """检查两个配方是否相似"""
        # 检查是否有相同的主要材料
        common_ingredients = set(recipe1.keys()) & set(recipe2.keys())
        if len(common_ingredients) < 2:
            return False
        
        # 检查用量是否相近
        for ingredient in common_ingredients:
            amount1 = recipe1[ingredient]
            amount2 = recipe2[ingredient]
            if abs(amount1 - amount2) / max(amount1, amount2) > tolerance:
                return False
        
        return True
    
    def _evaluate_free_cocktail(self, ingredients):
        """评估自创鸡尾酒"""
        score = 50  # 基础分
        
        # 检查是否有基酒
        has_base_spirit = any(
            self.cocktail_system.ingredients[name].type.value == "基酒" 
            for name in ingredients.keys()
        )
        if has_base_spirit:
            score += 20
        
        # 检查是否有调和剂
        has_mixer = any(
            self.cocktail_system.ingredients[name].type.value == "调和剂" 
            for name in ingredients.keys()
        )
        if has_mixer:
            score += 15
        
        # 检查是否有装饰
        has_garnish = any(
            self.cocktail_system.ingredients[name].type.value == "装饰" 
            for name in ingredients.keys()
        )
        if has_garnish:
            score += 10
        
        # 检查材料数量
        ingredient_count = len(ingredients)
        if 3 <= ingredient_count <= 6:
            score += 10
        elif ingredient_count > 6:
            score -= 5  # 太复杂了
        
        return min(100, max(0, score))
    
    def run(self):
        """运行演示"""
        try:
            # 显示标题
            self.show_title()
            
            # 显示角色介绍
            self.show_character_intro()
            
            while True:
                self.console.clear()
                
                # 主菜单
                menu_text = """
🍸 Termix 主菜单 🍸

1. 📖 查看配方
2. 🧪 查看材料
3. 🍹 开始调酒
4. 🚪 退出游戏
                """
                
                panel = Panel(
                    Align.center(menu_text),
                    border_style="magenta"
                )
                
                self.console.print(panel)
                
                choice = Prompt.ask("请选择选项", choices=["1", "2", "3", "4"])
                
                if choice == "1":
                    self.show_recipes()
                    Prompt.ask("\n按回车继续...")
                elif choice == "2":
                    self.show_ingredients()
                    Prompt.ask("\n按回车继续...")
                elif choice == "3":
                    self.interactive_mixing()
                    Prompt.ask("\n按回车继续...")
                elif choice == "4":
                    self.console.print("\n[cyan]感谢游玩 Termix！🍸[/cyan]")
                    break
        
        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]游戏被中断，再见！👋[/yellow]")


def main():
    """主函数"""
    demo = TermixDemo()
    demo.run()


if __name__ == "__main__":
    main()
