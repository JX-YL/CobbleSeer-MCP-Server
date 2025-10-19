"""
模板库服务
从参考数据中提取和管理技能/特性模板
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger


class TemplateLibrary:
    """技能和特性模板库"""
    
    def __init__(self, reference_dir: str):
        """
        初始化模板库
        
        Args:
            reference_dir: 参考数据目录路径
        """
        self.reference_dir = Path(reference_dir)
        self.moves_cache = None
        self.abilities_cache = None
        
        logger.info(f"📚 初始化模板库：{self.reference_dir}")
    
    def parse_showdown_js(self, file_path: Path) -> Dict[str, Any]:
        """
        解析Showdown格式的JS文件
        
        Args:
            file_path: JS文件路径
            
        Returns:
            解析后的数据字典
        """
        logger.info(f"📖 解析文件：{file_path.name}")
        
        content = file_path.read_text(encoding='utf-8')
        
        # 查找主对象定义
        # 支持两种格式：
        # 1. const Moves = {...}
        # 2. exports.Moves = {...}
        pattern = r'(?:const|exports\.)\s+(Moves|Abilities)\s*=\s*(\{[\s\S]*?\n\};)'
        match = re.search(pattern, content)
        
        if not match:
            logger.warning(f"⚠️ 未找到对象定义")
            return {}
        
        obj_name = match.group(1)
        obj_str = match.group(2)
        
        logger.info(f"  找到对象：{obj_name}")
        
        # 解析每个条目
        items = {}
        
        # 使用栈匹配每个顶层条目
        lines = obj_str.split('\n')
        current_item = None
        current_lines = []
        brace_count = 0
        in_item = False
        
        for line in lines:
            # 检测条目开始：  itemname: {
            if not in_item:
                match = re.match(r'^\s+([a-z0-9_]+):\s*\{', line, re.IGNORECASE)
                if match:
                    current_item = match.group(1)
                    current_lines = [line]
                    brace_count = 1
                    in_item = True
            else:
                current_lines.append(line)
                # 计数大括号
                brace_count += line.count('{') - line.count('}')
                
                # 条目结束
                if brace_count == 0:
                    # 解析这个条目
                    item_str = '\n'.join(current_lines)
                    try:
                        item_data = self._parse_item(item_str)
                        if item_data:
                            items[current_item] = item_data
                    except Exception as e:
                        logger.debug(f"  跳过条目 {current_item}：{e}")
                    
                    # 重置
                    in_item = False
                    current_item = None
                    current_lines = []
        
        logger.info(f"✅ 成功解析 {len(items)} 个条目")
        return items
    
    def _parse_item(self, item_str: str) -> Dict[str, Any]:
        """
        解析单个条目的字符串
        提取基础字段（忽略函数）
        
        Args:
            item_str: 条目字符串
            
        Returns:
            条目数据字典
        """
        data = {}
        
        # 提取简单字段
        patterns = {
            'num': r'num:\s*(-?\d+)',
            'accuracy': r'accuracy:\s*(\w+)',
            'basePower': r'basePower:\s*(\d+)',
            'category': r'category:\s*["\'](\w+)["\']',
            'name': r'name:\s*["\']([^"\']+)["\']',
            'pp': r'pp:\s*(\d+)',
            'priority': r'priority:\s*(-?\d+)',
            'target': r'target:\s*["\'](\w+)["\']',
            'type': r'type:\s*["\'](\w+)["\']',
            'rating': r'rating:\s*([\d.]+)',
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, item_str)
            if match:
                value = match.group(1)
                # 转换类型
                if field in ['num', 'basePower', 'pp', 'priority']:
                    data[field] = int(value)
                elif field == 'rating':
                    data[field] = float(value)
                elif field == 'accuracy':
                    data[field] = True if value == 'true' else int(value) if value.isdigit() else value
                else:
                    data[field] = value
        
        # 提取flags对象
        flags_match = re.search(r'flags:\s*\{([^}]+)\}', item_str)
        if flags_match:
            flags_str = flags_match.group(1)
            flags = {}
            for flag_match in re.finditer(r'(\w+):\s*1', flags_str):
                flags[flag_match.group(1)] = 1
            data['flags'] = flags
        
        # 提取secondary对象（简化版）
        if 'secondary: null' in item_str:
            data['secondary'] = None
        elif 'secondary: {' in item_str:
            secondary = {}
            
            # 概率
            chance_match = re.search(r'chance:\s*(\d+)', item_str)
            if chance_match:
                secondary['chance'] = int(chance_match.group(1))
            
            # 状态
            status_match = re.search(r'status:\s*["\'](\w+)["\']', item_str)
            if status_match:
                secondary['status'] = status_match.group(1)
            
            # 能力变化
            boosts_match = re.search(r'boosts:\s*\{([^}]+)\}', item_str)
            if boosts_match:
                boosts_str = boosts_match.group(1)
                boosts = {}
                for boost_match in re.finditer(r'(\w+):\s*(-?\d+)', boosts_str):
                    boosts[boost_match.group(1)] = int(boost_match.group(2))
                secondary['boosts'] = boosts
            
            if secondary:
                data['secondary'] = secondary
        
        # 提取特殊效果
        if 'drain:' in item_str:
            drain_match = re.search(r'drain:\s*\[(\d+),\s*(\d+)\]', item_str)
            if drain_match:
                data['drain'] = [int(drain_match.group(1)), int(drain_match.group(2))]
        
        if 'recoil:' in item_str:
            recoil_match = re.search(r'recoil:\s*\[(\d+),\s*(\d+)\]', item_str)
            if recoil_match:
                data['recoil'] = [int(recoil_match.group(1)), int(recoil_match.group(2))]
        
        if 'multihit:' in item_str:
            multihit_match = re.search(r'multihit:\s*(\[[\d,\s]+\]|\d+)', item_str)
            if multihit_match:
                data['multihit'] = multihit_match.group(1)
        
        return data
    
    def load_moves(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        加载所有技能数据
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            技能数据字典
        """
        if self.moves_cache is not None and not force_reload:
            return self.moves_cache
        
        moves_file = self.reference_dir / "moves.js"
        if not moves_file.exists():
            logger.error(f"❌ 技能文件不存在：{moves_file}")
            return {}
        
        self.moves_cache = self.parse_showdown_js(moves_file)
        logger.info(f"✅ 已加载 {len(self.moves_cache)} 个技能模板")
        
        return self.moves_cache
    
    def load_abilities(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        加载所有特性数据
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            特性数据字典
        """
        if self.abilities_cache is not None and not force_reload:
            return self.abilities_cache
        
        abilities_file = self.reference_dir / "abilities.js"
        if not abilities_file.exists():
            logger.error(f"❌ 特性文件不存在：{abilities_file}")
            return {}
        
        self.abilities_cache = self.parse_showdown_js(abilities_file)
        logger.info(f"✅ 已加载 {len(self.abilities_cache)} 个特性模板")
        
        return self.abilities_cache
    
    def search_moves(
        self,
        type: Optional[str] = None,
        category: Optional[str] = None,
        power_min: int = 0,
        power_max: int = 999,
        has_priority: Optional[bool] = None,
        has_secondary: Optional[bool] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索技能模板
        
        Args:
            type: 属性类型
            category: 分类（Physical/Special/Status）
            power_min: 最小威力
            power_max: 最大威力
            has_priority: 是否有优先度
            has_secondary: 是否有追加效果
            limit: 返回数量限制
            
        Returns:
            符合条件的技能列表
        """
        moves = self.load_moves()
        results = []
        
        for move_id, move_data in moves.items():
            # 过滤条件
            if type and move_data.get('type') != type:
                continue
            
            if category and move_data.get('category') != category:
                continue
            
            power = move_data.get('basePower', 0)
            if power < power_min or power > power_max:
                continue
            
            if has_priority is not None:
                move_priority = move_data.get('priority', 0)
                if has_priority and move_priority == 0:
                    continue
                if not has_priority and move_priority != 0:
                    continue
            
            if has_secondary is not None:
                has_sec = 'secondary' in move_data and move_data['secondary'] is not None
                if has_secondary != has_sec:
                    continue
            
            results.append({
                'id': move_id,
                **move_data
            })
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_move_by_effect(self, effect_type: str) -> Optional[Dict[str, Any]]:
        """
        根据效果类型获取参考技能
        
        Args:
            effect_type: 效果类型（paralyze, burn, drain等）
            
        Returns:
            参考技能数据
        """
        moves = self.load_moves()
        
        # 状态异常映射
        status_map = {
            'paralyze': 'par',
            'burn': 'brn',
            'poison': 'psn',
            'sleep': 'slp',
            'freeze': 'frz'
        }
        
        # 搜索对应效果的技能
        for move_id, move_data in moves.items():
            secondary = move_data.get('secondary')
            
            if effect_type in status_map:
                # 状态异常
                target_status = status_map[effect_type]
                if secondary and secondary.get('status') == target_status:
                    return move_data
            
            elif effect_type == 'drain':
                if 'drain' in move_data:
                    return move_data
            
            elif effect_type == 'recoil':
                if 'recoil' in move_data:
                    return move_data
            
            elif effect_type.startswith('boost_') or effect_type.startswith('lower_'):
                # 能力变化
                if secondary and 'boosts' in secondary:
                    return move_data
        
        return None

