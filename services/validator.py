"""
CobbleSeer - 文件验证服务

负责验证生成的文件是否符合 Cobblemon 规范：
- JSON Schema 验证
- 类型检查
- 数值范围检查
- 引用完整性检查
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from loguru import logger


class Validator:
    """文件验证器"""
    
    def __init__(self, config: dict):
        """
        初始化验证器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.strict_mode = config.get("validator", {}).get("strict_mode", True)
        
        logger.info(f"✅ Validator初始化完成（严格模式: {self.strict_mode}）")
    
    def validate_species(self, data: dict) -> Dict[str, Any]:
        """
        验证 species.json
        
        Args:
            data: species数据
        
        Returns:
            验证结果 {"valid": bool, "errors": list, "warnings": list}
        """
        errors = []
        warnings = []
        
        # 必需字段检查
        required_fields = ["name", "nationalPokedexNumber", "primaryType", "baseStats"]
        for field in required_fields:
            if field not in data:
                errors.append(f"缺少必需字段: {field}")
        
        # 图鉴号范围检查
        if "nationalPokedexNumber" in data:
            dex = data["nationalPokedexNumber"]
            if not (1 <= dex <= 9999):
                errors.append(f"图鉴号超出范围: {dex}（应为 1-9999）")
        
        # 属性有效性检查
        valid_types = [
            "normal", "fire", "water", "electric", "grass", "ice",
            "fighting", "poison", "ground", "flying", "psychic", "bug",
            "rock", "ghost", "dragon", "dark", "steel", "fairy"
        ]
        
        if "primaryType" in data:
            ptype = data["primaryType"].lower()
            if ptype not in valid_types:
                errors.append(f"无效的主属性: {data['primaryType']}")
        
        if "secondaryType" in data:
            stype = data["secondaryType"].lower()
            if stype not in valid_types:
                errors.append(f"无效的副属性: {data['secondaryType']}")
        
        # 能力值检查
        if "baseStats" in data:
            stats = data["baseStats"]
            required_stats = ["hp", "attack", "defence", "special_attack", "special_defence", "speed"]
            
            for stat in required_stats:
                if stat not in stats:
                    errors.append(f"缺少能力值: {stat}")
                else:
                    value = stats[stat]
                    if not isinstance(value, int) or value < 1 or value > 255:
                        errors.append(f"能力值无效: {stat}={value}（应为 1-255）")
            
            # 种族值总和检查
            total = sum(stats.get(s, 0) for s in required_stats)
            if total < 180:
                warnings.append(f"种族值总和过低: {total}（一般 ≥ 180）")
            elif total > 720:
                warnings.append(f"种族值总和过高: {total}（一般 ≤ 720）")
        
        is_valid = len(errors) == 0
        
        logger.debug(f"Species验证: {'✅ 通过' if is_valid else '❌ 失败'} ({len(errors)}个错误, {len(warnings)}个警告)")
        
        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_spawn(self, data: dict) -> Dict[str, Any]:
        """
        验证 spawn.json
        
        Args:
            data: spawn数据
        
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        # 必需字段检查
        if "enabled" not in data:
            warnings.append("缺少 enabled 字段，默认为 true")
        
        # 权重检查
        if "weight" in data:
            weight = data["weight"]
            if not isinstance(weight, (int, float)) or weight <= 0:
                errors.append(f"无效的权重: {weight}（应为正数）")
        
        # 等级范围检查
        if "level" in data:
            level_str = data["level"]
            if isinstance(level_str, str):
                if "-" in level_str:
                    try:
                        min_level, max_level = map(int, level_str.split("-"))
                        if min_level > max_level:
                            errors.append(f"等级范围无效: {level_str}")
                        if min_level < 1 or max_level > 100:
                            errors.append(f"等级超出范围: {level_str}（应为 1-100）")
                    except ValueError:
                        errors.append(f"等级格式无效: {level_str}")
        
        is_valid = len(errors) == 0
        
        logger.debug(f"Spawn验证: {'✅ 通过' if is_valid else '❌ 失败'}")
        
        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_move_code(self, code: str) -> Dict[str, Any]:
        """
        验证技能代码（JavaScript对象）
        
        Args:
            code: 技能代码字符串
        
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        try:
            # 简单的语法检查
            if not code.strip():
                errors.append("代码为空")
                return {"valid": False, "errors": errors, "warnings": warnings}
            
            # 检查必需字段（通过文本匹配）
            required_fields = ["num", "accuracy", "basePower", "category", "name", "pp", "type"]
            for field in required_fields:
                if f'"{field}"' not in code and f'{field}:' not in code:
                    errors.append(f"缺少必需字段: {field}")
            
            # 检查num是否为负数（自定义技能）
            if "num:" in code:
                num_str = code.split("num:")[1].split(",")[0].strip()
                try:
                    num = int(num_str)
                    if num >= 0:
                        warnings.append(f"技能ID应为负数（自定义技能），当前: {num}")
                except ValueError:
                    errors.append(f"技能ID格式无效: {num_str}")
            
            # 检查category有效性
            valid_categories = ["Physical", "Special", "Status"]
            for cat in valid_categories:
                if f'"{cat}"' in code or f"'{cat}'" in code:
                    break
            else:
                errors.append(f"category应为: Physical/Special/Status")
            
        except Exception as e:
            errors.append(f"代码解析失败: {str(e)}")
        
        is_valid = len(errors) == 0
        
        logger.debug(f"Move代码验证: {'✅ 通过' if is_valid else '❌ 失败'}")
        
        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_all(self, files: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证所有文件
        
        Args:
            files: 文件字典
        
        Returns:
            总体验证结果
        """
        logger.info("🔍 验证所有文件...")
        
        results = {}
        all_valid = True
        total_errors = []
        total_warnings = []
        
        # 验证species
        if "species" in files:
            result = self.validate_species(files["species"])
            results["species"] = result
            if not result["valid"]:
                all_valid = False
            total_errors.extend([f"[species] {e}" for e in result["errors"]])
            total_warnings.extend([f"[species] {w}" for w in result["warnings"]])
        
        # 验证spawn
        if "spawn" in files:
            result = self.validate_spawn(files["spawn"])
            results["spawn"] = result
            if not result["valid"]:
                all_valid = False
            total_errors.extend([f"[spawn] {e}" for e in result["errors"]])
            total_warnings.extend([f"[spawn] {w}" for w in result["warnings"]])
        
        # 验证自定义技能
        if "custom_moves" in files:
            for i, move in enumerate(files["custom_moves"]):
                if "code" in move:
                    result = self.validate_move_code(move["code"])
                    if not result["valid"]:
                        all_valid = False
                    total_errors.extend([f"[move {i+1}] {e}" for e in result["errors"]])
                    total_warnings.extend([f"[move {i+1}] {w}" for w in result["warnings"]])
        
        logger.info(f"{'✅ 验证通过' if all_valid else '❌ 验证失败'} ({len(total_errors)}个错误, {len(total_warnings)}个警告)")
        
        return {
            "valid": all_valid,
            "errors": total_errors,
            "warnings": total_warnings,
            "details": results
        }

