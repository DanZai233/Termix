"""
配置加载器模块 - 从外部文件加载游戏数据
"""

import json
import os
from typing import Dict, List, Any
from pathlib import Path

from .data_models import Ingredient, CocktailRecipe, IngredientType


class ConfigLoader:
    """配置文件加载器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.ingredients_file = self.config_dir / "ingredients.json"
        self.recipes_file = self.config_dir / "recipes.json"
        self.game_config_file = self.config_dir / "game_config.json"
    
    def load_ingredients(self) -> Dict[str, Ingredient]:
        """从JSON文件加载材料数据"""
        try:
            with open(self.ingredients_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            ingredients = {}
            for item in data.get("ingredients", []):
                # 处理枚举类型
                ingredient_type = None
                for enum_type in IngredientType:
                    if enum_type.name == item["type"]:
                        ingredient_type = enum_type
                        break
                
                if ingredient_type is None:
                    print(f"⚠️  未知的材料类型: {item['type']}，跳过材料: {item['name']}")
                    continue
                
                ingredient = Ingredient(
                    name=item["name"],
                    type=ingredient_type,
                    color=item["color"],
                    flavor_profile=item["flavor_profile"],
                    alcohol_content=item["alcohol_content"],
                    emoji=item["emoji"],
                    description=item["description"]
                )
                ingredients[item["name"]] = ingredient
            
            return ingredients
            
        except FileNotFoundError:
            print(f"⚠️  材料配置文件 {self.ingredients_file} 不存在，使用默认配置")
            return self._get_default_ingredients()
        except json.JSONDecodeError as e:
            print(f"❌ 材料配置文件格式错误: {e}")
            return self._get_default_ingredients()
        except Exception as e:
            print(f"❌ 加载材料配置时出错: {e}")
            return self._get_default_ingredients()
    
    def load_recipes(self) -> Dict[str, CocktailRecipe]:
        """从JSON文件加载配方数据"""
        try:
            with open(self.recipes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            recipes = {}
            for item in data.get("recipes", []):
                recipe = CocktailRecipe(
                    name=item["name"],
                    ingredients=item["ingredients"],
                    description=item["description"],
                    difficulty=item["difficulty"],
                    emoji=item["emoji"],
                    flavor_tags=item["flavor_tags"]
                )
                recipes[item["name"]] = recipe
            
            return recipes
            
        except FileNotFoundError:
            print(f"⚠️  配方配置文件 {self.recipes_file} 不存在，使用默认配置")
            return self._get_default_recipes()
        except json.JSONDecodeError as e:
            print(f"❌ 配方配置文件格式错误: {e}")
            return self._get_default_recipes()
        except Exception as e:
            print(f"❌ 加载配方配置时出错: {e}")
            return self._get_default_recipes()
    
    def load_game_config(self) -> Dict[str, Any]:
        """加载游戏配置"""
        try:
            with open(self.game_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  游戏配置文件 {self.game_config_file} 不存在，使用默认配置")
            return self._get_default_game_config()
        except json.JSONDecodeError as e:
            print(f"❌ 游戏配置文件格式错误: {e}")
            return self._get_default_game_config()
        except Exception as e:
            print(f"❌ 加载游戏配置时出错: {e}")
            return self._get_default_game_config()
    
    def _get_default_ingredients(self) -> Dict[str, Ingredient]:
        """获取默认材料配置"""
        return {
            "白朗姆酒": Ingredient(
                name="白朗姆酒",
                type=IngredientType.BASE_SPIRIT,
                color="clear",
                flavor_profile=["甜", "热带"],
                alcohol_content=40.0,
                emoji="🥃",
                description="来自加勒比海的经典基酒"
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
            "青柠汁": Ingredient(
                name="青柠汁",
                type=IngredientType.MIXER,
                color="green",
                flavor_profile=["酸", "清新"],
                alcohol_content=0.0,
                emoji="🟢",
                description="新鲜的青柠汁，带来清新的酸味"
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
            "冰块": Ingredient(
                name="冰块",
                type=IngredientType.ICE,
                color="clear",
                flavor_profile=["冰凉"],
                alcohol_content=0.0,
                emoji="🧊",
                description="标准冰块"
            )
        }
    
    def _get_default_recipes(self) -> Dict[str, CocktailRecipe]:
        """获取默认配方配置"""
        return {
            "简单调酒": CocktailRecipe(
                name="简单调酒",
                ingredients={
                    "伏特加": 50,
                    "青柠汁": 20,
                    "糖浆": 15,
                    "冰块": 150
                },
                description="简单的基础鸡尾酒",
                difficulty=1,
                emoji="🍸",
                flavor_tags=["简单", "清爽"]
            )
        }
    
    def _get_default_game_config(self) -> Dict[str, Any]:
        """获取默认游戏配置"""
        return {
            "game_settings": {
                "initial_unlocked_recipes": ["简单调酒"],
                "difficulty_levels": {
                    "1": "简单",
                    "2": "容易",
                    "3": "中等",
                    "4": "困难",
                    "5": "专家"
                }
            },
            "ui_settings": {
                "items_per_page": 6,
                "auto_layout_threshold": 100
            }
        }
    
    def save_user_config(self, config_data: Dict[str, Any], filename: str = "user_config.json"):
        """保存用户配置"""
        try:
            user_config_file = self.config_dir / filename
            with open(user_config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存用户配置时出错: {e}")
            return False
    
    def load_user_config(self, filename: str = "user_config.json") -> Dict[str, Any]:
        """加载用户配置"""
        try:
            user_config_file = self.config_dir / filename
            with open(user_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"❌ 加载用户配置时出错: {e}")
            return {}
    
    def validate_config(self, config_type: str, config_data: Dict) -> List[str]:
        """验证配置文件格式"""
        errors = []
        
        if config_type == "ingredients":
            if "ingredients" not in config_data:
                errors.append("缺少 'ingredients' 字段")
            else:
                for i, ingredient in enumerate(config_data["ingredients"]):
                    required_fields = ["name", "type", "color", "flavor_profile", 
                                     "alcohol_content", "emoji", "description"]
                    for field in required_fields:
                        if field not in ingredient:
                            errors.append(f"材料 {i+1} 缺少必需字段: {field}")
        
        elif config_type == "recipes":
            if "recipes" not in config_data:
                errors.append("缺少 'recipes' 字段")
            else:
                for i, recipe in enumerate(config_data["recipes"]):
                    required_fields = ["name", "ingredients", "description", 
                                     "difficulty", "emoji", "flavor_tags"]
                    for field in required_fields:
                        if field not in recipe:
                            errors.append(f"配方 {i+1} 缺少必需字段: {field}")
        
        return errors
    
    def create_sample_configs(self):
        """创建示例配置文件"""
        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
        
        # 创建示例材料配置
        if not self.ingredients_file.exists():
            ingredients_data = {
                "ingredients": [
                    {
                        "name": "示例基酒",
                        "type": "BASE_SPIRIT",
                        "color": "clear",
                        "flavor_profile": ["示例风味"],
                        "alcohol_content": 40.0,
                        "emoji": "🍸",
                        "description": "这是一个示例材料"
                    }
                ]
            }
            
            with open(self.ingredients_file, 'w', encoding='utf-8') as f:
                json.dump(ingredients_data, f, ensure_ascii=False, indent=2)
        
        # 创建示例配方配置
        if not self.recipes_file.exists():
            recipes_data = {
                "recipes": [
                    {
                        "name": "示例鸡尾酒",
                        "category": "示例系列",
                        "ingredients": {
                            "示例基酒": 50,
                            "冰块": 150
                        },
                        "description": "这是一个示例配方",
                        "difficulty": 1,
                        "emoji": "🍸",
                        "flavor_tags": ["示例"]
                    }
                ]
            }
            
            with open(self.recipes_file, 'w', encoding='utf-8') as f:
                json.dump(recipes_data, f, ensure_ascii=False, indent=2)


# 全局配置加载器实例
config_loader = ConfigLoader()
