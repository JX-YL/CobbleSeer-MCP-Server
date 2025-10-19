"""
CobbleSeer - 文件构建服务

负责生成 Cobblemon 资源包的各类文件：
- species.json: 物种配置
- spawn.json: 生成规则
- poser.json: 模型配置
- resolver.json: 资源定位
- lang_zh.json / lang_en.json: 多语言
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
import re
from datetime import datetime
from loguru import logger


class Builder:
    """文件构建器"""
    
    @staticmethod
    def format_text_for_display(text: str, is_chinese: bool = True, max_length: int = 20) -> str:
        """
        格式化文本，添加软换行点以实现游戏内自动换行
        
        游戏会在空格处自动换行，所以需要在适当的位置添加空格作为换行点。
        
        Args:
            text: 原始文本
            is_chinese: 是否为中文文本
            max_length: 建议的最大连续字符数（用于添加换行点）
        
        Returns:
            格式化后的文本
        """
        if not text:
            return text
        
        if is_chinese:
            # 1. 先在标点后添加空格
            punctuation = ['。', '，', '！', '？', '；', '：']
            for p in punctuation:
                text = re.sub(rf'{re.escape(p)}(?=[^\s])', f'{p} ', text)
            
            # 2. 在长句中添加额外的软换行点
            # 在特定词后添加空格（常见的语义断点）
            break_words = [
                # 动词后
                '攻击', '进行', '提高', '降低', '回复', '给予', '使出', '发射', '释放',
                # 介词/连词后
                '从而', '并且', '同时', '然后', '接着', '之后',
                # 其他常见断点
                '对手', '自己', '宝可梦', '招式', '能力', '伤害', '状态'
            ]
            
            for word in break_words:
                # 在词后添加空格（如果后面不是标点或空格）
                text = re.sub(rf'{re.escape(word)}(?=[^。，！？；：\s])', f'{word} ', text)
        
        else:
            # 英文：在标点后添加双空格
            text = re.sub(r'\. (?=\S)', '.  ', text)
            text = re.sub(r'\.(?=\S)', '.  ', text)
            text = re.sub(r', (?=\S)', ',  ', text)
            text = re.sub(r',(?=\S)', ',  ', text)
            text = re.sub(r'! (?=\S)', '!  ', text)
            text = re.sub(r'!(?=\S)', '!  ', text)
            text = re.sub(r'\? (?=\S)', '?  ', text)
            text = re.sub(r'\?(?=\S)', '?  ', text)
        
        # 移除行尾多余空格
        text = text.rstrip()
        
        return text
    
    def __init__(self, config: dict):
        """
        初始化构建器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.namespace = config.get("builder", {}).get("defaults", {}).get("namespace", "cobbleseer")
        self.pack_format = config.get("builder", {}).get("defaults", {}).get("pack_format", 48)
        
        # 确保使用绝对路径
        output_dir = config.get("builder", {}).get("output_dir", "output")
        if not Path(output_dir).is_absolute():
            # 相对于 server.py 所在目录
            self.output_dir = Path(__file__).parent.parent / output_dir
        else:
            self.output_dir = Path(output_dir)
        
        logger.info(f"✅ Builder初始化完成（命名空间: {self.namespace}，输出目录: {self.output_dir}）")
    
    def build_species(self, data: dict) -> dict:
        """
        构建 species.json
        
        Args:
            data: 宝可梦数据
        
        Returns:
            species.json 内容
        """
        logger.debug(f"构建 species.json: {data.get('name')}")
        
        species = {
            "implemented": True,
            "name": data["name"],
            "nationalPokedexNumber": data["dex"],
            "primaryType": data["primary_type"],
            "baseStats": data["stats"],
            "behaviour": {
                "moving": {
                    "walk": {
                        "canWalk": True,
                        "walkSpeed": 0.35
                    }
                },
                "resting": {
                    "canSleep": True,
                    "willSleepOnBed": False,
                    "depth": "normal",
                    "light": "0-4"
                }
            },
            "baseScale": 1.0,
            "hitbox": {
                "width": 1.0,
                "height": 1.0,
                "fixed": False
            },
            "baseFriendship": data.get("base_friendship", 70),
            "evYield": {
                "hp": 0,
                "attack": 0,
                "defence": 0,
                "special_attack": 0,
                "special_defence": 0,
                "speed": 0
            },
            "catchRate": 45,
            "maleRatio": 0.5,
            "shoulderMountable": False,
            "forms": []
        }
        
        # 添加副属性
        if data.get("secondary_type"):
            species["secondaryType"] = data["secondary_type"]
        
        # 添加身高体重
        if data.get("height"):
            species["height"] = data["height"]
        if data.get("weight"):
            species["weight"] = data["weight"]
        
        # 添加技能表（根据属性智能生成）
        species["moves"] = self._generate_default_moves(
            data.get("primary_type"),
            data.get("secondary_type")
        )
        
        return species
    
    def build_spawn(self, data: dict) -> dict:
        """
        构建 spawn.json（生成规则）
        
        Args:
            data: 宝可梦数据
        
        Returns:
            spawn.json 内容
        """
        logger.debug(f"构建 spawn.json: {data.get('name')}")
        
        # 根据属性推断生成群系
        biomes = self._infer_biomes(data.get("primary_type"), data.get("secondary_type"))
        
        spawn = {
            "enabled": True,
            "context": "grounded",
            "bucket": "common",
            "level": "10-30",
            "weight": 10,
            "condition": {
                "canSeeSky": True,
                "minY": 60,
                "maxY": 120,
                "biomes": biomes
            }
        }
        
        return spawn
    
    def build_poser(self, data: dict) -> dict:
        """
        构建 poser.json（模型配置）
        
        Args:
            data: 宝可梦数据
        
        Returns:
            poser.json 内容
        """
        logger.debug(f"构建 poser.json: {data.get('name')}")
        
        poser = {
            "portraitScale": 1.0,
            "portraitTranslation": [0, 0, 0],
            "profileScale": 1.0,
            "profileTranslation": [0, 0.5, 0],
            "animations": {
                "ground_idle": "bedrock(cobblemon, idle)",
                "ground_walk": "bedrock(cobblemon, walk)",
                "water_idle": "bedrock(cobblemon, water_idle)",
                "water_swim": "bedrock(cobblemon, swim)",
                "sleep": "bedrock(cobblemon, sleep)"
            }
        }
        
        return poser
    
    def build_resolver(self, data: dict) -> dict:
        """
        构建 resolver.json（资源定位）
        
        Args:
            data: 宝可梦数据
        
        Returns:
            resolver.json 内容
        """
        logger.debug(f"构建 resolver.json: {data.get('name')}")
        
        name = data["name"]
        
        resolver = {
            "model": f"{self.namespace}:pokemon/{name}/model",
            "texture": f"{self.namespace}:textures/pokemon/{name}.png",
            "poser": f"{self.namespace}:pokemon/{name}/poser",
            "animations": [
                f"bedrock(cobblemon, {name})"
            ]
        }
        
        return resolver
    
    def build_lang_zh(self, data: dict) -> dict:
        """
        构建 lang_zh.json（中文语言文件，自动添加换行空格）
        
        Args:
            data: 宝可梦数据
        
        Returns:
            lang_zh.json 内容
        """
        logger.debug(f"构建 lang_zh.json: {data.get('name')}")
        
        name = data["name"]
        # 语言文件的键名：移除下划线，全小写
        lang_key = name.replace("_", "").lower()
        display_name = data.get("display_name_zh", name.replace("_", " ").title())
        
        # 格式化描述文本，添加智能换行空格
        desc = data.get("description_zh", "一只神秘的宝可梦")
        desc_formatted = self.format_text_for_display(desc, is_chinese=True)
        
        lang = {
            f"cobblemon.species.{lang_key}.name": display_name,
            f"cobblemon.species.{lang_key}.desc": desc_formatted
        }
        
        return lang
    
    def build_lang_en(self, data: dict) -> dict:
        """
        构建 lang_en.json（英文语言文件，自动添加换行空格）
        
        Args:
            data: 宝可梦数据
        
        Returns:
            lang_en.json 内容
        """
        logger.debug(f"构建 lang_en.json: {data.get('name')}")
        
        name = data["name"]
        # 语言文件的键名：移除下划线，全小写
        lang_key = name.replace("_", "").lower()
        display_name = data.get("display_name_en", name.replace("_", " ").title())
        
        # 格式化描述文本，添加智能换行空格
        desc = data.get("description_en", "A mysterious Pokemon")
        desc_formatted = self.format_text_for_display(desc, is_chinese=False)
        
        lang = {
            f"cobblemon.species.{lang_key}.name": display_name,
            f"cobblemon.species.{lang_key}.desc": desc_formatted
        }
        
        return lang
    
    def build_all(self, data: dict) -> Dict[str, Any]:
        """
        构建所有文件
        
        Args:
            data: 宝可梦数据
        
        Returns:
            所有文件的字典
        """
        logger.info(f"🔨 构建所有文件: {data.get('name')}")
        
        files = {
            "species": self.build_species(data),
            "spawn": self.build_spawn(data),
            "poser": self.build_poser(data),
            "resolver": self.build_resolver(data),
            "lang_zh": self.build_lang_zh(data),
            "lang_en": self.build_lang_en(data)
        }
        
        logger.info("✅ 所有文件构建完成")
        
        return files
    
    def detect_dependencies(self, files: Dict[str, Any]) -> list:
        """
        自动检测数据包所需模组
        
        Args:
            files: 文件字典
        
        Returns:
            所需模组列表
        """
        required_mods = ["Cobblemon"]
        
        # 检测是否包含自定义技能或特性（需要 Mega Showdown）
        has_custom_moves = any("moves" in str(key) for key in files.keys() if isinstance(key, str))
        has_custom_abilities = any("abilities" in str(key) for key in files.keys() if isinstance(key, str))
        
        # 检测文件路径中是否包含 mega_showdown
        has_mega_showdown = any("mega_showdown" in str(key) for key in files.keys() if isinstance(key, str))
        
        if has_custom_moves or has_custom_abilities or has_mega_showdown:
            required_mods.append("Mega Showdown")
        
        return required_mods
    
    def build_package(
        self,
        project_name: str,
        files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        构建资源包（仅文件夹格式）
        
        Args:
            project_name: 项目名称
            files: 文件字典
        
        Returns:
            构建结果
        """
        logger.info(f"📦 构建资源包: {project_name}")
        
        # 使用已初始化的绝对路径
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检测依赖
        dependencies = self.detect_dependencies(files)
        
        pokemon_name = files.get("species", {}).get("name", project_name)
        output_path = self.output_dir / project_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 创建文件夹格式的资源包
        self._create_folder_package(output_path, pokemon_name, files, dependencies)
        
        # 计算目录大小（递归统计所有文件）
        total_size = sum(f.stat().st_size for f in output_path.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)
        
        logger.info(f"✅ 资源包已生成: {output_path} ({size_mb:.2f} MB)")
        
        return {
            "success": True,
            "output_path": str(output_path),
            "format": "folder",
            "size_mb": round(size_mb, 2),
            "dependencies": dependencies
        }
    
    def _create_folder_package(self, output_path: Path, pokemon_name: str, files: Dict[str, Any], dependencies: list = None):
        """
        创建文件夹格式的资源包（按照结构树.txt标准）
        
        Args:
            output_path: 输出路径
            pokemon_name: 宝可梦名称
            files: 文件字典
            dependencies: 依赖的模组列表
        """
        if dependencies is None:
            dependencies = ["Cobblemon"]
        # pack.mcmeta
        pack_mcmeta = {
            "pack": {
                "pack_format": self.pack_format,
                "description": f"Custom Pokemon: {pokemon_name}"
            }
        }
        (output_path / "pack.mcmeta").write_text(
            json.dumps(pack_mcmeta, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        # ========== DATA 目录 ==========
        data_dir = output_path / "data" / "cobblemon"
        
        # species.json (在 data/cobblemon/species/custom/)
        if "species" in files:
            species_dir = data_dir / "species" / "custom"
            species_dir.mkdir(parents=True, exist_ok=True)
            (species_dir / f"{pokemon_name}.json").write_text(
                json.dumps(files["species"], indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        
        # spawn.json (在 data/cobblemon/spawn_pool_world/)
        if "spawn" in files:
            spawn_dir = data_dir / "spawn_pool_world"
            spawn_dir.mkdir(parents=True, exist_ok=True)
            (spawn_dir / f"{pokemon_name}.json").write_text(
                json.dumps(files["spawn"], indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        
        # ========== 自定义技能/特性（Mega Showdown）==========
        # 处理所有以 data/mega_showdown 开头的文件
        for file_path, file_content in files.items():
            if isinstance(file_path, str) and file_path.startswith("data/mega_showdown/"):
                # 解析路径
                full_path = output_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                # 写入文件（JavaScript 代码直接写入，不用JSON）
                if file_path.endswith('.js'):
                    full_path.write_text(file_content, encoding="utf-8")
                else:
                    full_path.write_text(
                        json.dumps(file_content, indent=2, ensure_ascii=False) if isinstance(file_content, dict) else file_content,
                        encoding="utf-8"
                    )
        
        # ========== ASSETS 目录 ==========
        assets_dir = output_path / "assets" / "cobblemon"
        bedrock_dir = assets_dir / "bedrock" / "pokemon"
        
        # poser.json (在 assets/cobblemon/bedrock/pokemon/posers/，直接放置)
        if "poser" in files:
            poser_dir = bedrock_dir / "posers"
            poser_dir.mkdir(parents=True, exist_ok=True)
            (poser_dir / f"{pokemon_name}.json").write_text(
                json.dumps(files["poser"], indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        
        # resolver.json (在 assets/cobblemon/bedrock/pokemon/resolvers/，0_name_base.json)
        if "resolver" in files:
            resolver_dir = bedrock_dir / "resolvers"
            resolver_dir.mkdir(parents=True, exist_ok=True)
            (resolver_dir / f"0_{pokemon_name}_base.json").write_text(
                json.dumps(files["resolver"], indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        
        # 模型占位符 (assets/cobblemon/bedrock/pokemon/models/pokemon-name/)
        model_dir = bedrock_dir / "models" / pokemon_name
        model_dir.mkdir(parents=True, exist_ok=True)
        model_placeholder = {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": f"geometry.{pokemon_name}",
                    "texture_width": 64,
                    "texture_height": 64
                },
                "bones": []
            }]
        }
        (model_dir / f"{pokemon_name}.geo.json").write_text(
            json.dumps(model_placeholder, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        # 动画占位符 (assets/cobblemon/bedrock/pokemon/animations/pokemon-name/)
        animation_dir = bedrock_dir / "animations" / pokemon_name
        animation_dir.mkdir(parents=True, exist_ok=True)
        animation_placeholder = {
            "format_version": "1.8.0",
            "animations": {
                f"animation.{pokemon_name}.ground_idle": {
                    "loop": True,
                    "animation_length": 1.0,
                    "bones": {}
                }
            }
        }
        (animation_dir / f"{pokemon_name}.animation.json").write_text(
            json.dumps(animation_placeholder, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        # 纹理占位符说明 (assets/cobblemon/textures/pokemon/pokemon-name/)
        texture_dir = assets_dir / "textures" / "pokemon" / pokemon_name
        texture_dir.mkdir(parents=True, exist_ok=True)
        texture_readme = f"""# 纹理文件占位符

请将以下纹理文件放置在此目录：

1. {pokemon_name}.png - 普通纹理（64x64 推荐）
2. {pokemon_name}_shiny.png - 闪光纹理（可选）

纹理格式：PNG
推荐分辨率：64x64 或 128x128
"""
        (texture_dir / "README.txt").write_text(texture_readme, encoding="utf-8")
        
        # lang_zh.json (在 assets/cobblemon/lang/)
        if "lang_zh" in files:
            lang_dir = assets_dir / "lang"
            lang_dir.mkdir(parents=True, exist_ok=True)
            (lang_dir / "zh_cn.json").write_text(
                json.dumps(files["lang_zh"], indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        
        # lang_en.json (在 assets/cobblemon/lang/)
        if "lang_en" in files:
            lang_dir = assets_dir / "lang"
            lang_dir.mkdir(parents=True, exist_ok=True)
            (lang_dir / "en_us.json").write_text(
                json.dumps(files["lang_en"], indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        
        # README（按照结构树.txt标准，包含依赖信息）
        dex_number = files.get("species", {}).get("nationalPokedexNumber", 9999)
        
        # 构建依赖信息部分
        dependencies_text = "\n".join(f"- **{mod}**" for mod in dependencies)
        needs_mega_showdown = "Mega Showdown" in dependencies
        warning_text = ""
        if needs_mega_showdown:
            warning_text = """
**⚠️ 重要提示**：此数据包包含自定义技能或特性，必须安装 [Mega Showdown](https://modrinth.com/mod/mega-showdown) 模组才能正常使用！
"""
        
        readme = f"""# {pokemon_name.upper()} Resource Pack

## 📦 所需模组

{dependencies_text}
{warning_text}

## 📁 文件结构（按照结构树.txt标准）

```
{pokemon_name}/
├── pack.mcmeta
├── data/cobblemon/
│   ├── species/custom/{pokemon_name}.json                 ✅ 种族配置
│   └── spawn_pool_world/{pokemon_name}.json               ✅ 生成规则
└── assets/cobblemon/
    ├── bedrock/pokemon/
    │   ├── models/{pokemon_name}/{pokemon_name}.geo.json            🔧 模型占位符
    │   ├── animations/{pokemon_name}/{pokemon_name}.animation.json  🔧 动画占位符
    │   ├── posers/{pokemon_name}.json                     ✅ 姿势配置
    │   └── resolvers/0_{pokemon_name}_base.json           ✅ 外观解析
    ├── textures/pokemon/{pokemon_name}/                   ⚠️  纹理目录（需补充）
    └── lang/
        ├── zh_cn.json                                     ✅ 中文翻译
        └── en_us.json                                     ✅ 英文翻译
```

## ✅ 已完成的配置

- **种族数据** (`species/custom/{pokemon_name}.json`) - 基础属性、能力值、行为等
- **生成规则** (`spawn_pool_world/{pokemon_name}.json`) - 生成地点、条件、概率等
- **姿势配置** (`posers/{pokemon_name}.json`) - 显示姿势、缩放、动画绑定
- **外观解析** (`resolvers/0_{pokemon_name}_base.json`) - 资源定位、形态解析
- **多语言支持** - 中文和英文翻译

## ⚠️ 待补充内容

### 1. 3D 模型文件 🎨
**位置**: `assets/cobblemon/bedrock/pokemon/models/{pokemon_name}/{pokemon_name}.geo.json`

当前是占位符模型，需要使用 Blockbench 创建完整的 3D 模型。

**推荐工具**: [Blockbench](https://www.blockbench.net/)
- 格式: Bedrock Entity
- 纹理尺寸: 64x64 或 128x128

### 2. 纹理贴图 🖼️
**位置**: `assets/cobblemon/textures/pokemon/{pokemon_name}/`

需要添加：
- `{pokemon_name}.png` - 普通形态纹理
- `{pokemon_name}_shiny.png` - 闪光形态纹理（可选）

**推荐分辨率**: 64x64 或 128x128 PNG

### 3. 动画文件 🎬 (可选)
**位置**: `assets/cobblemon/bedrock/pokemon/animations/{pokemon_name}/{pokemon_name}.animation.json`

当前是基础占位符，可以添加更复杂的动画：
- `ground_idle` - 地面待机
- `ground_walk` - 地面行走
- `water_idle` - 水中待机
- `water_swim` - 游泳
- `sleep` - 睡觉

## 🎮 使用方法

### 安装
1. 将此资源包文件夹放入 `.minecraft/datapacks/`
2. 启动或重启游戏
3. 在游戏中输入 `/reload` 重载数据包

### 生成宝可梦
```
/pokespawn {pokemon_name}
```

### 查看宝可梦信息
打开宝可梦图鉴，找到 #{dex_number:04d}

## 📝 制作信息

- **生成工具**: CobbleSeer MCP Server
- **图鉴号**: #{dex_number:04d}
- **物种名**: {pokemon_name}
- **生成日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🔗 相关资源

- [Cobblemon 官方文档](https://cobblemon.com/)
- [Blockbench 教程](https://www.blockbench.net/wiki/)
- [结构树参考](结构树.txt)

---
*Generated by CobbleSeer MCP Server v1.0.0*
*Structure based on 结构树.txt by 籌橾*
"""
        (output_path / "README.md").write_text(readme, encoding="utf-8")
    
    def _infer_biomes(self, primary_type: str, secondary_type: Optional[str] = None) -> list:
        """
        根据属性推断生成群系
        
        Args:
            primary_type: 主属性
            secondary_type: 副属性
        
        Returns:
            群系列表
        """
        # 简单的属性->群系映射
        type_biome_map = {
            "fire": ["minecraft:desert", "minecraft:badlands", "minecraft:savanna"],
            "water": ["minecraft:ocean", "minecraft:river", "minecraft:beach"],
            "grass": ["minecraft:forest", "minecraft:plains", "minecraft:jungle"],
            "electric": ["minecraft:savanna", "minecraft:plains"],
            "ice": ["minecraft:snowy_taiga", "minecraft:ice_spikes", "minecraft:frozen_ocean"],
            "rock": ["minecraft:mountains", "minecraft:stony_peaks"],
            "ground": ["minecraft:desert", "minecraft:badlands"],
            "flying": ["minecraft:mountains", "minecraft:windswept_hills"],
            "psychic": ["minecraft:plains", "minecraft:flower_forest"],
            "bug": ["minecraft:forest", "minecraft:jungle"],
            "ghost": ["minecraft:dark_forest", "minecraft:deep_dark"],
            "dark": ["minecraft:dark_forest"],
            "dragon": ["minecraft:mountains", "minecraft:end_highlands"],
            "steel": ["minecraft:mountains", "minecraft:stony_peaks"],
            "fairy": ["minecraft:flower_forest", "minecraft:meadow"]
        }
        
        biomes = type_biome_map.get(primary_type.lower(), ["minecraft:plains"])
        
        # 如果有副属性，合并群系
        if secondary_type:
            secondary_biomes = type_biome_map.get(secondary_type.lower(), [])
            biomes = list(set(biomes + secondary_biomes))
        
        return biomes[:3]  # 最多返回3个群系
    
    def _generate_default_moves(self, primary_type: str, secondary_type: Optional[str] = None) -> list:
        """
        根据属性智能生成默认技能表（Cobblemon 字符串格式）
        
        Args:
            primary_type: 主属性
            secondary_type: 副属性
        
        Returns:
            技能表字符串列表（格式："level:move_name" 或 "egg:move_name" 或 "tm:move_name"）
        """
        # 属性对应的核心技能库（Cobblemon 常用技能，使用小写+下划线）
        type_moves = {
            "Fire": ["ember", "flamethrower", "fireblast", "flamecharge", "firefang", "heatwave"],
            "Water": ["watergun", "bubblebeam", "surf", "hydropump", "aquatail", "waterfall"],
            "Grass": ["vinewhip", "razorleaf", "solarbeam", "energyball", "leafblade", "seedbomb"],
            "Electric": ["thundershock", "spark", "thunderbolt", "thunder", "volttackle", "wildcharge"],
            "Ice": ["powdersnow", "iceshard", "icebeam", "blizzard", "iciclecrash", "freezedry"],
            "Fighting": ["lowkick", "karatechop", "brickbreak", "closecombat", "hammerarm", "aurasphere"],
            "Poison": ["poisonsting", "acid", "sludgebomb", "poisonjab", "gunkshot", "toxic"],
            "Ground": ["mudslap", "bulldoze", "earthquake", "earthpower", "drillrun", "stompingtantrum"],
            "Flying": ["peck", "wingattack", "airslash", "aerialace", "bravebird", "hurricane"],
            "Psychic": ["confusion", "psybeam", "psychic", "psyshock", "zenheadbutt", "futuresight"],
            "Bug": ["bugbite", "furycutter", "xscissor", "bugbuzz", "uturn", "leechlife"],
            "Rock": ["rockthrow", "rockslide", "stoneedge", "powergem", "rockblast", "headsmash"],
            "Ghost": ["lick", "shadowsneak", "shadowball", "shadowclaw", "phantomforce", "hex"],
            "Dragon": ["dragonrage", "dragonbreath", "dragonclaw", "dragonpulse", "outrage", "dracometeor"],
            "Dark": ["bite", "feintattack", "crunch", "darkpulse", "knockoff", "foulplay"],
            "Steel": ["metalclaw", "ironhead", "flashcannon", "steelwing", "irontail", "meteormash"],
            "Fairy": ["fairywind", "disarmingvoice", "dazzlinggleam", "moonblast", "playrough", "moonlight"],
            "Normal": ["tackle", "quickattack", "bodyslam", "hyperbeam", "slash", "takedown"]
        }
        
        # 构建技能表（Cobblemon 格式：字符串数组）
        moves = []
        
        # 1. 初始技能（1级）- 所有宝可梦都会撞击和叫声
        moves.append("1:tackle")
        moves.append("1:growl")
        
        # 2. 获取主属性技能
        primary_moves = type_moves.get(primary_type, type_moves["Normal"])
        
        # 3. 早期技能（5-15级）
        moves.append(f"5:{primary_moves[0]}")   # 第一个基础技能
        moves.append(f"10:{primary_moves[1]}")  # 第二个技能
        moves.append("15:tailwhip")              # 辅助技能
        
        # 4. 中期技能（20-30级）
        moves.append(f"20:{primary_moves[2]}")  # 第三个技能（更强）
        
        # 如果有副属性，添加副属性技能
        if secondary_type:
            secondary_moves = type_moves.get(secondary_type, [])
            if secondary_moves:
                moves.append(f"25:{secondary_moves[0]}")  # 副属性技能
                if len(secondary_moves) > 1:
                    moves.append(f"35:{secondary_moves[1]}")  # 副属性第二个技能
        
        moves.append(f"30:{primary_moves[3]}")  # 第四个技能（高级）
        
        # 5. 后期技能（40-50级）
        if not secondary_type or len(type_moves.get(secondary_type, [])) <= 1:
            moves.append(f"35:{primary_moves[4]}")  # 第五个技能
        
        moves.append(f"40:{primary_moves[4]}")  # 更强的技能
        moves.append(f"45:{primary_moves[5]}")  # 终极技能
        
        # 6. 蛋技能
        moves.extend([
            "egg:charm",
            "egg:sweetkiss",
            "egg:leer"
        ])
        
        # 7. TM技能（通用强力技能）
        moves.extend([
            "tm:protect",
            "tm:rest",
            "tm:substitute",
            "tm:hyperbeam",
            "tm:facade",
            "tm:sleeptalk",
            "tm:swift"
        ])
        
        return moves

