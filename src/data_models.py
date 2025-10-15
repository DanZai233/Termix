"""
数据模型 - 定义游戏中的数据结构
"""

from typing import Dict, List
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
