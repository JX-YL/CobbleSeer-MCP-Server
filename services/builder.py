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
import zipfile
from loguru import logger


class Builder:
    """文件构建器"""
    
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
        构建 lang_zh.json（中文语言文件）
        
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
        
        lang = {
            f"cobblemon.species.{lang_key}.name": display_name,
            f"cobblemon.species.{lang_key}.desc": f"一只神秘的宝可梦"
        }
        
        return lang
    
    def build_lang_en(self, data: dict) -> dict:
        """
        构建 lang_en.json（英文语言文件）
        
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
        
        lang = {
            f"cobblemon.species.{lang_key}.name": display_name,
            f"cobblemon.species.{lang_key}.desc": f"A mysterious Pokemon"
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
    
    def build_package(
        self,
        project_name: str,
        files: Dict[str, Any],
        output_format: str = "zip"
    ) -> Dict[str, Any]:
        """
        打包资源包
        
        Args:
            project_name: 项目名称
            files: 文件字典
            output_format: 输出格式（zip/folder）
        
        Returns:
            打包结果
        """
        logger.info(f"📦 打包资源包: {project_name} ({output_format})")
        
        # 使用已初始化的绝对路径
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        pokemon_name = files.get("species", {}).get("name", project_name)
        
        if output_format == "zip":
            output_path = self.output_dir / f"{project_name}.zip"
            self._create_zip_package(output_path, pokemon_name, files)
        else:
            output_path = self.output_dir / project_name
            output_path.mkdir(parents=True, exist_ok=True)
            self._create_folder_package(output_path, pokemon_name, files)
        
        # 计算文件大小
        size_mb = output_path.stat().st_size / (1024 * 1024) if output_path.exists() else 0.0
        
        logger.info(f"✅ 资源包已生成: {output_path} ({size_mb:.2f} MB)")
        
        return {
            "success": True,
            "output_path": str(output_path),
            "size_mb": round(size_mb, 2)
        }
    
    def _create_zip_package(self, output_path: Path, pokemon_name: str, files: Dict[str, Any]):
        """创建 ZIP 格式的资源包（按照结构树.txt标准）"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # pack.mcmeta
            pack_mcmeta = {
                "pack": {
                    "pack_format": self.pack_format,
                    "description": f"Custom Pokemon: {pokemon_name}"
                }
            }
            zipf.writestr("pack.mcmeta", json.dumps(pack_mcmeta, indent=2, ensure_ascii=False))
            
            # ========== DATA 目录 ==========
            
            # species.json (在 data/cobblemon/species/custom/)
            if "species" in files:
                zipf.writestr(
                    f"data/cobblemon/species/custom/{pokemon_name}.json",
                    json.dumps(files["species"], indent=2, ensure_ascii=False)
                )
            
            # spawn.json (在 data/cobblemon/spawn_pool_world/)
            if "spawn" in files:
                zipf.writestr(
                    f"data/cobblemon/spawn_pool_world/{pokemon_name}.json",
                    json.dumps(files["spawn"], indent=2, ensure_ascii=False)
                )
            
            # ========== ASSETS 目录 ==========
            
            # poser.json (直接在 assets/cobblemon/bedrock/pokemon/posers/)
            if "poser" in files:
                zipf.writestr(
                    f"assets/cobblemon/bedrock/pokemon/posers/{pokemon_name}.json",
                    json.dumps(files["poser"], indent=2, ensure_ascii=False)
                )
            
            # resolver.json (直接在 assets/cobblemon/bedrock/pokemon/resolvers/，文件名格式：0_name_base.json)
            if "resolver" in files:
                zipf.writestr(
                    f"assets/cobblemon/bedrock/pokemon/resolvers/0_{pokemon_name}_base.json",
                    json.dumps(files["resolver"], indent=2, ensure_ascii=False)
                )
            
            # 模型占位符 (assets/cobblemon/bedrock/pokemon/models/pokemon-name/)
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
            zipf.writestr(
                f"assets/cobblemon/bedrock/pokemon/models/{pokemon_name}/{pokemon_name}.geo.json",
                json.dumps(model_placeholder, indent=2, ensure_ascii=False)
            )
            
            # 动画占位符 (assets/cobblemon/bedrock/pokemon/animations/pokemon-name/)
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
            zipf.writestr(
                f"assets/cobblemon/bedrock/pokemon/animations/{pokemon_name}/{pokemon_name}.animation.json",
                json.dumps(animation_placeholder, indent=2, ensure_ascii=False)
            )
            
            # 纹理占位符说明 (assets/cobblemon/textures/pokemon/pokemon-name/)
            texture_readme = f"""# 纹理文件占位符

请将以下纹理文件放置在此目录：

1. {pokemon_name}.png - 普通纹理（64x64 推荐）
2. {pokemon_name}_shiny.png - 闪光纹理（可选）

纹理格式：PNG
推荐分辨率：64x64 或 128x128
"""
            zipf.writestr(
                f"assets/cobblemon/textures/pokemon/{pokemon_name}/README.txt",
                texture_readme
            )
            
            # lang_zh.json (在 assets/cobblemon/lang/)
            if "lang_zh" in files:
                zipf.writestr(
                    f"assets/cobblemon/lang/zh_cn.json",
                    json.dumps(files["lang_zh"], indent=2, ensure_ascii=False)
                )
            
            # lang_en.json (在 assets/cobblemon/lang/)
            if "lang_en" in files:
                zipf.writestr(
                    f"assets/cobblemon/lang/en_us.json",
                    json.dumps(files["lang_en"], indent=2, ensure_ascii=False)
                )
            
            # 创建主 README（按照结构树.txt标准）
            dex_number = files.get("species", {}).get("nationalPokedexNumber", 9999)
            readme = f"""# {pokemon_name.upper()} Resource Pack

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
1. 将此资源包文件夹或 ZIP 放入 `.minecraft/datapacks/`
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
- **生成日期**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

---

## 🔗 相关资源

- [Cobblemon 官方文档](https://cobblemon.com/)
- [Blockbench 教程](https://www.blockbench.net/wiki/)
- [结构树参考](结构树.txt)

---
*Generated by CobbleSeer MCP Server v1.0.0*
*Structure based on 结构树.txt by 籌橾*
"""
            zipf.writestr("README.md", readme)
    
    def _create_folder_package(self, output_path: Path, pokemon_name: str, files: Dict[str, Any]):
        """创建文件夹格式的资源包（按照结构树.txt标准）"""
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
        
        # README（按照结构树.txt标准）
        dex_number = files.get("species", {}).get("nationalPokedexNumber", 9999)
        readme = f"""# {pokemon_name.upper()} Resource Pack

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
- **生成日期**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

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

