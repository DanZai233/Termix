"""
调酒系统 - 管理调酒材料、配方和评分
"""

import random
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class IngredientType(Enum):
    """材料类型枚举"""
    BASE_SPIRIT = "基酒"
    LIQUEUR = "利口酒"
    MIXER = "调和剂"
    GARNISH = "装饰"
    ICE = "冰块"


@dataclass
class Ingredient:
    """调酒材料"""
    name: str
    type: IngredientType
    color: str
    flavor_profile: List[str]
    alcohol_content: float
    emoji: str
    description: str


@dataclass
class CocktailRecipe:
    """鸡尾酒配方"""
    name: str
    ingredients: Dict[str, float]  # 材料名称 -> 用量(ml)
    description: str
    difficulty: int  # 1-5 难度等级
    emoji: str
    flavor_tags: List[str]


class CocktailSystem:
    """调酒系统主类"""
    
    def __init__(self):
        self.ingredients = self._init_ingredients()
        self.recipes = self._init_recipes()
        self.player_inventory = list(self.ingredients.keys())  # 玩家拥有的材料
        self.unlocked_recipes = ["莫吉托", "玛格丽特", "金汤力", "螺丝刀", "黑俄罗斯"]  # 初始解锁的配方
    
    def _init_ingredients(self) -> Dict[str, Ingredient]:
        """初始化调酒材料"""
        ingredients = {
            # 基酒类
            "白朗姆酒": Ingredient(
                name="白朗姆酒",
                type=IngredientType.BASE_SPIRIT,
                color="clear",
                flavor_profile=["甜", "热带"],
                alcohol_content=40.0,
                emoji="🥃",
                description="来自加勒比海的经典基酒"
            ),
            "黑朗姆酒": Ingredient(
                name="黑朗姆酒",
                type=IngredientType.BASE_SPIRIT,
                color="dark",
                flavor_profile=["浓郁", "焦糖", "香草"],
                alcohol_content=40.0,
                emoji="🥃",
                description="陈年朗姆酒，口感浓郁复杂"
            ),
            "龙舌兰酒": Ingredient(
                name="龙舌兰酒",
                type=IngredientType.BASE_SPIRIT,
                color="clear",
                flavor_profile=["辛辣", "草本"],
                alcohol_content=40.0,
                emoji="🍶",
                description="墨西哥的国酒，带有独特的龙舌兰香味"
            ),
            "伏特加": Ingredient(
                name="伏特加",
                type=IngredientType.BASE_SPIRIT,
                color="clear",
                flavor_profile=["纯净", "中性"],
                alcohol_content=40.0,
                emoji="🍸",
                description="纯净无味的经典基酒"
            ),
            "金酒": Ingredient(
                name="金酒",
                type=IngredientType.BASE_SPIRIT,
                color="clear",
                flavor_profile=["杜松子", "草本", "辛辣"],
                alcohol_content=40.0,
                emoji="🍸",
                description="以杜松子为主要香料的烈酒"
            ),
            "威士忌": Ingredient(
                name="威士忌",
                type=IngredientType.BASE_SPIRIT,
                color="amber",
                flavor_profile=["烟熏", "木桶", "麦芽"],
                alcohol_content=40.0,
                emoji="🥃",
                description="经典的谷物烈酒，口感醇厚"
            ),
            "白兰地": Ingredient(
                name="白兰地",
                type=IngredientType.BASE_SPIRIT,
                color="amber",
                flavor_profile=["果香", "温暖", "优雅"],
                alcohol_content=40.0,
                emoji="🍷",
                description="葡萄蒸馏酒，香气优雅"
            ),
            
            # 利口酒类
            "君度橙酒": Ingredient(
                name="君度橙酒",
                type=IngredientType.LIQUEUR,
                color="clear",
                flavor_profile=["橙香", "甜"],
                alcohol_content=40.0,
                emoji="🍊",
                description="法国橙味利口酒，香甜可口"
            ),
            "咖啡利口酒": Ingredient(
                name="咖啡利口酒",
                type=IngredientType.LIQUEUR,
                color="dark",
                flavor_profile=["咖啡", "甜", "浓郁"],
                alcohol_content=20.0,
                emoji="☕",
                description="浓郁的咖啡香味利口酒"
            ),
            "椰子利口酒": Ingredient(
                name="椰子利口酒",
                type=IngredientType.LIQUEUR,
                color="white",
                flavor_profile=["椰子", "奶香", "热带"],
                alcohol_content=21.0,
                emoji="🥥",
                description="热带风味的椰子利口酒"
            ),
            "桃子利口酒": Ingredient(
                name="桃子利口酒",
                type=IngredientType.LIQUEUR,
                color="peach",
                flavor_profile=["桃子", "甜", "果香"],
                alcohol_content=15.0,
                emoji="🍑",
                description="甜美的桃子风味利口酒"
            ),
            
            # 调和剂类
            "青柠汁": Ingredient(
                name="青柠汁",
                type=IngredientType.MIXER,
                color="green",
                flavor_profile=["酸", "清新"],
                alcohol_content=0.0,
                emoji="🟢",
                description="新鲜的青柠汁，带来清新的酸味"
            ),
            "柠檬汁": Ingredient(
                name="柠檬汁",
                type=IngredientType.MIXER,
                color="yellow",
                flavor_profile=["酸", "明亮"],
                alcohol_content=0.0,
                emoji="🟡",
                description="新鲜柠檬汁，酸甜平衡"
            ),
            "橙汁": Ingredient(
                name="橙汁",
                type=IngredientType.MIXER,
                color="orange",
                flavor_profile=["甜", "果香", "维C"],
                alcohol_content=0.0,
                emoji="🍊",
                description="新鲜橙汁，维生素丰富"
            ),
            "蔓越莓汁": Ingredient(
                name="蔓越莓汁",
                type=IngredientType.MIXER,
                color="red",
                flavor_profile=["酸甜", "果香", "清新"],
                alcohol_content=0.0,
                emoji="🔴",
                description="酸甜的蔓越莓汁，颜色鲜艳"
            ),
            "菠萝汁": Ingredient(
                name="菠萝汁",
                type=IngredientType.MIXER,
                color="yellow",
                flavor_profile=["甜", "热带", "果香"],
                alcohol_content=0.0,
                emoji="🍍",
                description="热带风味的菠萝汁"
            ),
            "糖浆": Ingredient(
                name="糖浆",
                type=IngredientType.MIXER,
                color="clear",
                flavor_profile=["甜"],
                alcohol_content=0.0,
                emoji="🍯",
                description="简单糖浆，增加甜味"
            ),
            "石榴糖浆": Ingredient(
                name="石榴糖浆",
                type=IngredientType.MIXER,
                color="red",
                flavor_profile=["甜", "果香", "浓郁"],
                alcohol_content=0.0,
                emoji="🍒",
                description="红色的石榴糖浆，增色增味"
            ),
            "苏打水": Ingredient(
                name="苏打水",
                type=IngredientType.MIXER,
                color="clear",
                flavor_profile=["气泡", "清爽"],
                alcohol_content=0.0,
                emoji="💧",
                description="带气泡的苏打水"
            ),
            "汤力水": Ingredient(
                name="汤力水",
                type=IngredientType.MIXER,
                color="clear",
                flavor_profile=["苦", "气泡", "奎宁"],
                alcohol_content=0.0,
                emoji="💧",
                description="含奎宁的气泡水，微苦清爽"
            ),
            "姜汁汽水": Ingredient(
                name="姜汁汽水",
                type=IngredientType.MIXER,
                color="clear",
                flavor_profile=["辛辣", "姜味", "气泡"],
                alcohol_content=0.0,
                emoji="💧",
                description="带有姜味的气泡饮料"
            ),
            "椰浆": Ingredient(
                name="椰浆",
                type=IngredientType.MIXER,
                color="white",
                flavor_profile=["椰香", "奶香", "浓郁"],
                alcohol_content=0.0,
                emoji="🥥",
                description="浓郁的椰子浆，热带风味"
            ),
            "鲜奶油": Ingredient(
                name="鲜奶油",
                type=IngredientType.MIXER,
                color="white",
                flavor_profile=["奶香", "丝滑", "浓郁"],
                alcohol_content=0.0,
                emoji="🥛",
                description="丝滑的鲜奶油，增加口感层次"
            ),
            
            # 装饰类
            "薄荷叶": Ingredient(
                name="薄荷叶",
                type=IngredientType.GARNISH,
                color="green",
                flavor_profile=["清凉", "草本"],
                alcohol_content=0.0,
                emoji="🌿",
                description="新鲜薄荷叶，带来清凉感"
            ),
            "盐边": Ingredient(
                name="盐边",
                type=IngredientType.GARNISH,
                color="white",
                flavor_profile=["咸"],
                alcohol_content=0.0,
                emoji="🧂",
                description="杯口装饰用盐"
            ),
            "糖边": Ingredient(
                name="糖边",
                type=IngredientType.GARNISH,
                color="white",
                flavor_profile=["甜"],
                alcohol_content=0.0,
                emoji="🍯",
                description="杯口装饰用糖"
            ),
            "柠檬片": Ingredient(
                name="柠檬片",
                type=IngredientType.GARNISH,
                color="yellow",
                flavor_profile=["柠檬香", "装饰"],
                alcohol_content=0.0,
                emoji="🍋",
                description="新鲜柠檬片装饰"
            ),
            "橙片": Ingredient(
                name="橙片",
                type=IngredientType.GARNISH,
                color="orange",
                flavor_profile=["橙香", "装饰"],
                alcohol_content=0.0,
                emoji="🍊",
                description="新鲜橙片装饰"
            ),
            "樱桃": Ingredient(
                name="樱桃",
                type=IngredientType.GARNISH,
                color="red",
                flavor_profile=["甜", "果香", "装饰"],
                alcohol_content=0.0,
                emoji="🍒",
                description="马拉斯奇诺樱桃装饰"
            ),
            "橄榄": Ingredient(
                name="橄榄",
                type=IngredientType.GARNISH,
                color="green",
                flavor_profile=["咸", "橄榄香"],
                alcohol_content=0.0,
                emoji="🫒",
                description="经典马提尼装饰橄榄"
            ),
            
            # 冰块类
            "冰块": Ingredient(
                name="冰块",
                type=IngredientType.ICE,
                color="clear",
                flavor_profile=["冰凉"],
                alcohol_content=0.0,
                emoji="🧊",
                description="标准冰块"
            ),
            "碎冰": Ingredient(
                name="碎冰",
                type=IngredientType.ICE,
                color="clear",
                flavor_profile=["冰凉", "细腻"],
                alcohol_content=0.0,
                emoji="❄️",
                description="细碎的冰块，冷却效果更佳"
            ),
            
            # 其他材料
            "干味美思": Ingredient(
                name="干味美思",
                type=IngredientType.LIQUEUR,
                color="clear",
                flavor_profile=["草本", "干净", "复杂"],
                alcohol_content=18.0,
                emoji="🍷",
                description="干型味美思，马提尼的经典配料"
            ),
            "蓝柑橘利口酒": Ingredient(
                name="蓝柑橘利口酒",
                type=IngredientType.LIQUEUR,
                color="blue",
                flavor_profile=["柑橘", "甜", "蓝色"],
                alcohol_content=23.0,
                emoji="🔵",
                description="蓝色的柑橘利口酒，增加梦幻色彩"
            ),
            "杏仁糖浆": Ingredient(
                name="杏仁糖浆",
                type=IngredientType.MIXER,
                color="clear",
                flavor_profile=["杏仁", "甜", "坚果"],
                alcohol_content=0.0,
                emoji="🌰",
                description="杏仁风味糖浆"
            ),
            "咖啡": Ingredient(
                name="咖啡",
                type=IngredientType.MIXER,
                color="black",
                flavor_profile=["咖啡", "苦", "香浓"],
                alcohol_content=0.0,
                emoji="☕",
                description="新鲜煮制的咖啡"
            ),
            "番茄汁": Ingredient(
                name="番茄汁",
                type=IngredientType.MIXER,
                color="red",
                flavor_profile=["番茄", "咸鲜", "维生素"],
                alcohol_content=0.0,
                emoji="🍅",
                description="新鲜番茄汁"
            ),
            "辣椒酱": Ingredient(
                name="辣椒酱",
                type=IngredientType.MIXER,
                color="red",
                flavor_profile=["辣", "刺激"],
                alcohol_content=0.0,
                emoji="🌶️",
                description="增加辛辣味的调料"
            ),
            "盐": Ingredient(
                name="盐",
                type=IngredientType.GARNISH,
                color="white",
                flavor_profile=["咸"],
                alcohol_content=0.0,
                emoji="🧂",
                description="调味用盐"
            ),
            "可乐": Ingredient(
                name="可乐",
                type=IngredientType.MIXER,
                color="dark",
                flavor_profile=["甜", "气泡", "焦糖"],
                alcohol_content=0.0,
                emoji="🥤",
                description="经典可乐饮料"
            )
        }
        return ingredients
    
    def _init_recipes(self) -> Dict[str, CocktailRecipe]:
        """初始化鸡尾酒配方"""
        recipes = {
            # 经典系列
            "莫吉托": CocktailRecipe(
                name="莫吉托",
                ingredients={
                    "白朗姆酒": 50,
                    "青柠汁": 20,
                    "糖浆": 15,
                    "薄荷叶": 8,
                    "苏打水": 100,
                    "冰块": 150
                },
                description="古巴经典鸡尾酒，清爽怡人",
                difficulty=2,
                emoji="🍃",
                flavor_tags=["清爽", "薄荷", "热带"]
            ),
            "玛格丽特": CocktailRecipe(
                name="玛格丽特",
                ingredients={
                    "龙舌兰酒": 50,
                    "君度橙酒": 25,
                    "青柠汁": 25,
                    "盐边": 1,
                    "冰块": 150
                },
                description="墨西哥经典鸡尾酒，酸甜平衡",
                difficulty=3,
                emoji="🌵",
                flavor_tags=["酸甜", "经典", "墨西哥"]
            ),
            "马提尼": CocktailRecipe(
                name="马提尼",
                ingredients={
                    "金酒": 60,
                    "干味美思": 10,
                    "橄榄": 1,
                    "冰块": 120
                },
                description="经典干马提尼，优雅的鸡尾酒之王",
                difficulty=4,
                emoji="🍸",
                flavor_tags=["经典", "优雅", "干净"]
            ),
            "金汤力": CocktailRecipe(
                name="金汤力",
                ingredients={
                    "金酒": 50,
                    "汤力水": 150,
                    "青柠汁": 10,
                    "冰块": 120
                },
                description="英式经典，金酒与汤力水的完美结合",
                difficulty=1,
                emoji="🍸",
                flavor_tags=["清爽", "经典", "英式"]
            ),
            "威士忌酸": CocktailRecipe(
                name="威士忌酸",
                ingredients={
                    "威士忌": 60,
                    "柠檬汁": 30,
                    "糖浆": 20,
                    "樱桃": 1,
                    "冰块": 150
                },
                description="经典威士忌鸡尾酒，酸甜平衡",
                difficulty=2,
                emoji="🥃",
                flavor_tags=["酸甜", "经典", "威士忌"]
            ),
            
            # 热带系列
            "椰林飘香": CocktailRecipe(
                name="椰林飘香",
                ingredients={
                    "白朗姆酒": 45,
                    "椰子利口酒": 30,
                    "菠萝汁": 90,
                    "椰浆": 30,
                    "碎冰": 180
                },
                description="热带风情鸡尾酒，仿佛置身椰林海滩",
                difficulty=2,
                emoji="🥥",
                flavor_tags=["热带", "椰香", "甜美"]
            ),
            "蓝色夏威夷": CocktailRecipe(
                name="蓝色夏威夷",
                ingredients={
                    "白朗姆酒": 40,
                    "伏特加": 20,
                    "蓝柑橘利口酒": 20,
                    "菠萝汁": 60,
                    "椰浆": 30,
                    "碎冰": 150
                },
                description="蓝色的热带梦幻鸡尾酒",
                difficulty=3,
                emoji="🌺",
                flavor_tags=["热带", "梦幻", "果香"]
            ),
            "迈泰": CocktailRecipe(
                name="迈泰",
                ingredients={
                    "白朗姆酒": 30,
                    "黑朗姆酒": 30,
                    "君度橙酒": 15,
                    "杏仁糖浆": 15,
                    "青柠汁": 20,
                    "菠萝汁": 60,
                    "碎冰": 180
                },
                description="波利尼西亚风情的复杂热带鸡尾酒",
                difficulty=4,
                emoji="🌴",
                flavor_tags=["热带", "复杂", "果香"]
            ),
            
            # 果味系列
            "性感海滩": CocktailRecipe(
                name="性感海滩",
                ingredients={
                    "伏特加": 40,
                    "桃子利口酒": 20,
                    "蔓越莓汁": 60,
                    "菠萝汁": 60,
                    "冰块": 150
                },
                description="粉红色的浪漫果味鸡尾酒",
                difficulty=2,
                emoji="🍑",
                flavor_tags=["果味", "浪漫", "甜美"]
            ),
            "大都会": CocktailRecipe(
                name="大都会",
                ingredients={
                    "伏特加": 45,
                    "君度橙酒": 15,
                    "蔓越莓汁": 30,
                    "青柠汁": 15,
                    "冰块": 120
                },
                description="都市女性最爱的粉红鸡尾酒",
                difficulty=3,
                emoji="💖",
                flavor_tags=["时尚", "果味", "都市"]
            ),
            "螺丝刀": CocktailRecipe(
                name="螺丝刀",
                ingredients={
                    "伏特加": 50,
                    "橙汁": 120,
                    "冰块": 150
                },
                description="简单的伏特加橙汁鸡尾酒",
                difficulty=1,
                emoji="🍊",
                flavor_tags=["简单", "果味", "清爽"]
            ),
            
            # 咖啡系列
            "白俄罗斯": CocktailRecipe(
                name="白俄罗斯",
                ingredients={
                    "伏特加": 50,
                    "咖啡利口酒": 25,
                    "鲜奶油": 25,
                    "冰块": 120
                },
                description="奶香浓郁的咖啡鸡尾酒",
                difficulty=2,
                emoji="☕",
                flavor_tags=["咖啡", "奶香", "浓郁"]
            ),
            "黑俄罗斯": CocktailRecipe(
                name="黑俄罗斯",
                ingredients={
                    "伏特加": 50,
                    "咖啡利口酒": 25,
                    "冰块": 120
                },
                description="简洁的咖啡味鸡尾酒",
                difficulty=1,
                emoji="☕",
                flavor_tags=["咖啡", "简洁", "浓烈"]
            ),
            "爱尔兰咖啡": CocktailRecipe(
                name="爱尔兰咖啡",
                ingredients={
                    "威士忌": 40,
                    "咖啡": 120,
                    "糖浆": 15,
                    "鲜奶油": 30
                },
                description="温暖的咖啡鸡尾酒，适合寒冷天气",
                difficulty=3,
                emoji="☕",
                flavor_tags=["温暖", "咖啡", "奶香"]
            ),
            
            # 创意系列
            "莫斯科骡子": CocktailRecipe(
                name="莫斯科骡子",
                ingredients={
                    "伏特加": 50,
                    "青柠汁": 15,
                    "姜汁汽水": 120,
                    "冰块": 150
                },
                description="清爽的姜味鸡尾酒，传统用铜杯盛装",
                difficulty=2,
                emoji="🐴",
                flavor_tags=["清爽", "姜味", "传统"]
            ),
            "血腥玛丽": CocktailRecipe(
                name="血腥玛丽",
                ingredients={
                    "伏特加": 50,
                    "番茄汁": 120,
                    "柠檬汁": 15,
                    "辣椒酱": 2,
                    "盐": 1,
                    "冰块": 150
                },
                description="经典的早餐鸡尾酒，口感丰富",
                difficulty=3,
                emoji="🍅",
                flavor_tags=["咸鲜", "辛辣", "早餐"]
            ),
            "长岛冰茶": CocktailRecipe(
                name="长岛冰茶",
                ingredients={
                    "伏特加": 15,
                    "金酒": 15,
                    "白朗姆酒": 15,
                    "龙舌兰酒": 15,
                    "君度橙酒": 15,
                    "柠檬汁": 25,
                    "糖浆": 20,
                    "可乐": 60,
                    "冰块": 180
                },
                description="多种烈酒混合的强力鸡尾酒",
                difficulty=5,
                emoji="🍃",
                flavor_tags=["强烈", "复杂", "经典"]
            )
        }
        return recipes
    
    def get_available_ingredients(self) -> List[Ingredient]:
        """获取玩家可用的材料"""
        return [self.ingredients[name] for name in self.player_inventory]
    
    def get_unlocked_recipes(self) -> List[CocktailRecipe]:
        """获取已解锁的配方"""
        return [self.recipes[name] for name in self.unlocked_recipes if name in self.recipes]
    
    def calculate_score(self, recipe_name: str, player_ingredients: Dict[str, float]) -> Tuple[int, str]:
        """
        计算调酒得分
        返回: (得分, 评价)
        """
        if recipe_name not in self.recipes:
            return 0, "未知配方"
        
        recipe = self.recipes[recipe_name]
        score = 100
        feedback = []
        
        # 检查每个材料的用量
        for ingredient_name, correct_amount in recipe.ingredients.items():
            player_amount = player_ingredients.get(ingredient_name, 0)
            
            if player_amount == 0:
                score -= 20
                feedback.append(f"缺少 {ingredient_name}")
            else:
                # 计算用量偏差
                deviation = abs(player_amount - correct_amount) / correct_amount
                if deviation > 0.5:
                    score -= 15
                    feedback.append(f"{ingredient_name} 用量偏差较大")
                elif deviation > 0.2:
                    score -= 8
                    feedback.append(f"{ingredient_name} 用量略有偏差")
        
        # 检查多余材料
        for ingredient_name in player_ingredients:
            if ingredient_name not in recipe.ingredients and player_ingredients[ingredient_name] > 0:
                score -= 10
                feedback.append(f"多余的 {ingredient_name}")
        
        # 确保得分不为负
        score = max(0, score)
        
        # 生成评价
        if score >= 90:
            evaluation = "完美！🌟"
        elif score >= 80:
            evaluation = "很棒！👏"
        elif score >= 70:
            evaluation = "不错！👍"
        elif score >= 60:
            evaluation = "还可以 😊"
        else:
            evaluation = "需要改进 😅"
        
        return score, evaluation
    
    def get_random_recipe_hint(self) -> str:
        """获取随机配方提示"""
        hints = [
            "💡 莫吉托需要薄荷叶来增加清香",
            "💡 玛格丽特的杯口需要用盐装饰",
            "💡 冰块的用量会影响饮品的口感",
            "💡 柑橘类果汁要新鲜现榨才好喝",
            "💡 基酒的选择决定了鸡尾酒的主要风味"
        ]
        return random.choice(hints)
    
    def unlock_recipe(self, recipe_name: str) -> bool:
        """解锁新配方"""
        if recipe_name in self.recipes and recipe_name not in self.unlocked_recipes:
            self.unlocked_recipes.append(recipe_name)
            return True
        return False


# 测试代码
if __name__ == "__main__":
    cocktail_system = CocktailSystem()
    
    # 测试配方
    print("可用材料:")
    for ingredient in cocktail_system.get_available_ingredients():
        print(f"  {ingredient.emoji} {ingredient.name} - {ingredient.description}")
    
    print("\n已解锁配方:")
    for recipe in cocktail_system.get_unlocked_recipes():
        print(f"  {recipe.emoji} {recipe.name} - {recipe.description}")
    
    # 测试评分
    test_mojito = {
        "白朗姆酒": 50,
        "青柠汁": 20,
        "糖浆": 15,
        "薄荷叶": 8,
        "苏打水": 100,
        "冰块": 150
    }
    
    score, evaluation = cocktail_system.calculate_score("莫吉托", test_mojito)
    print(f"\n莫吉托评分: {score}/100 - {evaluation}")
