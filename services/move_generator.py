"""
技能生成器（规则引擎，无需AI）
基于参数化输入和智能规则生成技能代码
"""
from typing import Optional, Dict, Any
from loguru import logger


class MoveGenerator:
    """技能生成器（规则引擎）"""
    
    # 状态异常映射
    STATUS_MAP = {
        'paralyze': 'par',
        'burn': 'brn',
        'poison': 'psn',
        'toxic': 'tox',
        'sleep': 'slp',
        'freeze': 'frz',
    }
    
    # 能力变化映射
    BOOST_MAP = {
        'boost_attack': {'atk': 1},
        'boost_defense': {'def': 1},
        'boost_special_attack': {'spa': 1},
        'boost_special_defense': {'spd': 1},
        'boost_speed': {'spe': 1},
        'lower_attack': {'atk': -1},
        'lower_defense': {'def': -1},
        'lower_special_attack': {'spa': -1},
        'lower_special_defense': {'spd': -1},
        'lower_speed': {'spe': -1},
        'boost_all': {'atk': 1, 'def': 1, 'spa': 1, 'spd': 1, 'spe': 1},
        'lower_all': {'atk': -1, 'def': -1, 'spa': -1, 'spd': -1, 'spe': -1},
    }
    
    def __init__(self):
        """初始化生成器"""
        logger.info("✅ 技能生成器初始化完成（规则引擎模式）")
    
    def generate(
        self,
        name: str,
        type: str,
        category: str,
        base_power: int = 0,
        accuracy: int = 100,
        pp: int = 10,
        priority: int = 0,
        effect: Optional[str] = None,
        effect_chance: int = 0,
        effect_value: int = 1,
        description: str = "",
        contact: bool = None  # 自动判断
    ) -> Dict[str, Any]:
        """
        生成技能代码
        
        Args:
            name: 技能名称
            type: 属性类型
            category: 分类（Physical/Special/Status）
            base_power: 威力
            accuracy: 命中率
            pp: PP值
            priority: 优先度
            effect: 效果类型
            effect_chance: 效果概率
            effect_value: 效果强度
            description: 描述
            contact: 是否接触技能（None表示自动判断）
            
        Returns:
            生成的技能数据
        """
        logger.info(f"🔧 生成技能：{name} ({type} {category})")
        
        # 基础结构
        move = {
            'num': -10001,  # 自定义技能用负数
            'name': name,
            'type': type,
            'category': category,
            'basePower': base_power,
            'accuracy': accuracy if accuracy <= 100 else True,
            'pp': pp,
            'priority': priority,
            'flags': self._generate_flags(category, contact),
            'target': 'normal',
        }
        
        # 添加效果
        if effect:
            self._add_effect(move, effect, effect_chance, effect_value)
        else:
            move['secondary'] = None
        
        # 添加描述
        if description:
            move['shortDesc'] = description
        else:
            move['shortDesc'] = self._generate_description(
                category, base_power, effect, effect_chance, priority
            )
        
        # 生成JavaScript代码
        code = self._to_javascript(move)
        
        logger.info(f"✅ 生成完成：{name}")
        
        return {
            'success': True,
            'code': code,
            'name': name,
            'type': type,
            'category': category,
            'basePower': base_power
        }
    
    def _generate_flags(self, category: str, contact: Optional[bool]) -> Dict[str, int]:
        """
        生成标志位
        
        Args:
            category: 技能分类
            contact: 是否接触技能
            
        Returns:
            标志位字典
        """
        flags = {
            'protect': 1,
            'mirror': 1,
            'metronome': 1
        }
        
        # 物理攻击通常是接触技能
        if contact is None:
            contact = (category == 'Physical')
        
        if contact:
            flags['contact'] = 1
        
        # 变化技能特殊标志
        if category == 'Status':
            flags['snatch'] = 1
        
        return flags
    
    def _add_effect(
        self,
        move: Dict[str, Any],
        effect: str,
        chance: int,
        value: int
    ):
        """
        添加效果到技能
        
        Args:
            move: 技能字典
            effect: 效果类型
            chance: 概率
            value: 强度
        """
        # 状态异常
        if effect in self.STATUS_MAP:
            move['secondary'] = {
                'chance': chance if chance > 0 else 100,
                'status': self.STATUS_MAP[effect]
            }
        
        # 能力变化
        elif effect in self.BOOST_MAP:
            if move['category'] == 'Status':
                # 变化技能直接提升（不是secondary）
                move['boosts'] = self.BOOST_MAP[effect]
                # 调整能力变化倍数
                if value != 1:
                    move['boosts'] = {k: v * value for k, v in move['boosts'].items()}
            else:
                # 攻击技能作为追加效果
                move['secondary'] = {
                    'chance': chance if chance > 0 else 100,
                    'boosts': self.BOOST_MAP[effect]
                }
        
        # 吸血
        elif effect == 'drain':
            move['drain'] = [value, 100]  # value%吸血
            move['flags']['heal'] = 1
            move['secondary'] = None
        
        # 反伤
        elif effect == 'recoil':
            if value == 33:
                move['recoil'] = [1, 3]
            elif value == 25:
                move['recoil'] = [1, 4]
            elif value == 50:
                move['recoil'] = [1, 2]
            else:
                move['recoil'] = [value, 100]
            move['secondary'] = None
        
        # 畏缩
        elif effect == 'flinch':
            move['secondary'] = {
                'chance': chance if chance > 0 else 30,
                'volatileStatus': 'flinch'
            }
        
        # 混乱
        elif effect == 'confusion':
            move['secondary'] = {
                'chance': chance if chance > 0 else 10,
                'volatileStatus': 'confusion'
            }
        
        # 高会心
        elif effect == 'high_crit':
            move['critRatio'] = value if value > 1 else 2
            move['secondary'] = None
        
        else:
            logger.warning(f"⚠️ 未知效果类型：{effect}")
            move['secondary'] = None
    
    def _generate_description(
        self,
        category: str,
        power: int,
        effect: Optional[str],
        chance: int,
        priority: int
    ) -> str:
        """
        自动生成技能描述
        
        Args:
            category: 分类
            power: 威力
            effect: 效果
            chance: 概率
            priority: 优先度
            
        Returns:
            描述文本
        """
        parts = []
        
        # 优先度
        if priority > 0:
            parts.append("Usually goes first.")
        elif priority < 0:
            parts.append("Goes last.")
        
        # 效果描述
        if effect in self.STATUS_MAP:
            status_name = effect.capitalize()
            if chance < 100:
                parts.append(f"{chance}% chance to {effect}.")
            else:
                parts.append(f"Causes {status_name}.")
        
        elif effect in self.BOOST_MAP:
            boost_desc = effect.replace('_', ' ').title()
            if chance < 100:
                parts.append(f"{chance}% chance to {boost_desc.lower()}.")
            else:
                parts.append(f"{boost_desc}.")
        
        elif effect == 'drain':
            parts.append("User recovers HP equal to damage dealt.")
        
        elif effect == 'recoil':
            parts.append("User takes recoil damage.")
        
        elif effect == 'flinch':
            parts.append(f"{chance}% chance to flinch.")
        
        elif effect == 'high_crit':
            parts.append("High critical hit ratio.")
        
        return ' '.join(parts) if parts else "No additional effect."
    
    def _to_javascript(self, move: Dict[str, Any]) -> str:
        """
        将技能字典转换为JavaScript代码
        
        Args:
            move: 技能字典
            
        Returns:
            JavaScript代码字符串
        """
        lines = ['{']
        
        # 基础字段
        lines.append(f'  num: {move["num"]},')
        lines.append(f'  name: "{move["name"]}",')
        lines.append(f'  type: "{move["type"]}",')
        lines.append(f'  category: "{move["category"]}",')
        
        # 数值字段
        lines.append(f'  basePower: {move["basePower"]},')
        
        if move["accuracy"] is True:
            lines.append(f'  accuracy: true,')
        else:
            lines.append(f'  accuracy: {move["accuracy"]},')
        
        lines.append(f'  pp: {move["pp"]},')
        lines.append(f'  priority: {move["priority"]},')
        
        # 标志位
        flags_str = ', '.join([f'{k}: 1' for k in move['flags'].keys()])
        lines.append(f'  flags: {{{flags_str}}},')
        
        # 特殊效果
        if 'drain' in move:
            drain = move['drain']
            lines.append(f'  drain: [{drain[0]}, {drain[1]}],')
        
        if 'recoil' in move:
            recoil = move['recoil']
            lines.append(f'  recoil: [{recoil[0]}, {recoil[1]}],')
        
        if 'critRatio' in move:
            lines.append(f'  critRatio: {move["critRatio"]},')
        
        if 'boosts' in move:
            boosts = move['boosts']
            boosts_str = ', '.join([f'{k}: {v}' for k, v in boosts.items()])
            lines.append(f'  boosts: {{{boosts_str}}},')
        
        # 追加效果
        if move.get('secondary') is None:
            lines.append(f'  secondary: null,')
        elif move.get('secondary'):
            sec = move['secondary']
            lines.append(f'  secondary: {{')
            
            if 'chance' in sec:
                lines.append(f'    chance: {sec["chance"]},')
            
            if 'status' in sec:
                lines.append(f'    status: "{sec["status"]}"')
            elif 'boosts' in sec:
                boosts_str = ', '.join([f'{k}: {v}' for k, v in sec['boosts'].items()])
                lines.append(f'    boosts: {{{boosts_str}}}')
            elif 'volatileStatus' in sec:
                lines.append(f'    volatileStatus: "{sec["volatileStatus"]}"')
            
            lines.append(f'  }},')
        
        # 目标和描述
        lines.append(f'  target: "{move["target"]}",')
        lines.append(f'  shortDesc: "{move["shortDesc"]}"')
        
        lines.append('}')
        
        return '\n'.join(lines)
