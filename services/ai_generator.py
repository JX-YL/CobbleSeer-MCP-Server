"""
CobbleSeer - AI生成服务

支持三种模式：
1. 云端模式（Claude API）- 推荐
2. 本地模式（Ollama + Qwen3）- 需要高配硬件
3. 混合模式（智能切换）- 灵活

负责：
- 生成技能代码（Showdown格式）
- 生成特性代码
- 根据描述生成配置
"""

from typing import List, Optional, Dict, Any
from loguru import logger


class AIGenerator:
    """
    AI生成服务
    
    支持三种模式：
    1. 云端模式（Claude API）
    2. 本地模式（Ollama + Qwen3）
    3. 混合模式（智能切换）
    """
    
    def __init__(self, config: dict, rag_service=None):
        """
        初始化AI生成器
        
        Args:
            config: 配置字典
            rag_service: RAG服务实例（可选）
        """
        self.config = config
        self.mode = config.get("ai", {}).get("mode", "local")
        self.rag_service = rag_service
        
        # 初始化云端客户端
        if self.mode in ["cloud", "hybrid"]:
            self._init_cloud_client()
        
        # 初始化本地客户端
        if self.mode in ["local", "hybrid"]:
            self._init_local_client()
        
        logger.info(f"✅ AI生成器初始化完成（模式：{self.mode}）")
    
    def _init_cloud_client(self):
        """初始化云端AI客户端（Claude）"""
        try:
            from anthropic import AsyncAnthropic
            
            api_key = self.config.get("ai", {}).get("cloud", {}).get("api_key", "")
            if not api_key:
                logger.warning("⚠️  未配置Claude API Key，云端模式将不可用")
                self.cloud_client = None
                return
            
            self.cloud_client = AsyncAnthropic(api_key=api_key)
            self.cloud_model = self.config.get("ai", {}).get("cloud", {}).get("model", "claude-3-5-sonnet-20241022")
            
            logger.info(f"✅ 云端AI客户端初始化成功（模型：{self.cloud_model}）")
        
        except ImportError:
            logger.error("❌ anthropic库未安装，请运行：pip install anthropic")
            self.cloud_client = None
        except Exception as e:
            logger.error(f"❌ 云端AI客户端初始化失败：{e}")
            self.cloud_client = None
    
    def _init_local_client(self):
        """初始化本地AI客户端（Ollama）"""
        try:
            from ollama import AsyncClient
            
            ollama_host = self.config.get("ai", {}).get("local", {}).get("ollama_host", "http://localhost:11434")
            self.local_client = AsyncClient(host=ollama_host)
            self.local_model = self.config.get("ai", {}).get("local", {}).get("model", "qwen3:7b")
            
            logger.info(f"✅ 本地AI客户端初始化成功（模型：{self.local_model}）")
        
        except ImportError:
            logger.error("❌ ollama库未安装，请运行：pip install ollama")
            self.local_client = None
        except Exception as e:
            logger.error(f"❌ 本地AI客户端初始化失败：{e}")
            self.local_client = None
    
    async def generate_move(
        self, 
        description: str, 
        auto_reference: bool = True
    ) -> Dict[str, Any]:
        """
        生成技能代码（自动选择最佳AI + RAG检索）
        
        混合模式逻辑：
        - 简单描述（<50字）→ 尝试本地AI
        - 复杂描述（≥50字）→ 使用云端AI
        - 本地失败 → 自动降级云端
        
        Args:
            description: 技能描述
            auto_reference: 是否自动RAG检索参考
        
        Returns:
            包含生成结果的字典
        """
        # 获取参考技能
        references = []
        if auto_reference and self.rag_service:
            try:
                references = await self.rag_service.search_moves(description, top_k=3)
            except Exception as e:
                logger.warning(f"RAG检索失败：{e}")
        
        try:
            if self.mode == "cloud":
                code = await self._generate_cloud(description, references)
            elif self.mode == "local":
                code = await self._generate_local(description, references)
            elif self.mode == "hybrid":
                if len(description) < 50:
                    try:
                        logger.info("  使用本地AI...")
                        code = await self._generate_local(description, references)
                    except Exception as e:
                        logger.warning(f"  本地AI失败，切换云端：{e}")
                        code = await self._generate_cloud(description, references)
                else:
                    logger.info("  使用云端AI...")
                    code = await self._generate_cloud(description, references)
            else:
                raise ValueError(f"未知的AI模式: {self.mode}")
            
            # 解析代码提取字段
            return self._parse_move_code(code, description)
            
        except Exception as e:
            logger.error(f"生成技能失败：{e}")
            return {
                "success": False,
                "error": str(e),
                "code": ""
            }
    
    async def _generate_cloud(
        self, 
        description: str, 
        references: List[dict]
    ) -> str:
        """云端AI生成（Claude）"""
        
        if not self.cloud_client:
            raise RuntimeError("云端AI客户端未初始化，请检查API Key配置")
        
        # 构建Prompt
        prompt = self._build_move_prompt(description, references)
        
        try:
            # 调用Claude API
            response = await self.cloud_client.messages.create(
                model=self.cloud_model,
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            code = response.content[0].text
            
            # 提取代码
            return self._extract_code(code)
        
        except Exception as e:
            logger.error(f"❌ 云端AI生成失败：{e}")
            raise
    
    async def _generate_local(
        self, 
        description: str, 
        references: List[dict]
    ) -> str:
        """本地AI生成（Ollama + Qwen3）"""
        
        if not self.local_client:
            raise RuntimeError("本地AI客户端未初始化，请检查Ollama配置")
        
        # 构建Prompt
        prompt = self._build_move_prompt(description, references)
        
        try:
            # 调用Ollama
            response = await self.local_client.chat(
                model=self.local_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个Cobblemon技能设计师。生成JavaScript代码，Showdown格式。只输出代码，不要解释。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.7,
                    "num_predict": 1000
                }
            )
            
            code = response["message"]["content"]
            
            # 提取代码
            return self._extract_code(code)
        
        except Exception as e:
            logger.error(f"❌ 本地AI生成失败：{e}")
            raise
    
    def _build_move_prompt(
        self, 
        description: str, 
        references: List[dict]
    ) -> str:
        """构建生成Prompt"""
        
        ref_text = ""
        if references:
            ref_text = "\n\n参考以下相似技能：\n"
            for ref in references[:3]:
                ref_text += f"- {ref.get('name', '')}: 威力{ref.get('basePower', 0)}，命中{ref.get('accuracy', 100)}\n"
        
        return f"""基于以下描述生成Cobblemon技能（Showdown格式JavaScript）。

用户需求：
{description}
{ref_text}

要求：
1. 返回完整的JavaScript对象（不要exports语句）
2. 必须包含：num（负数）、accuracy、basePower、category、name、pp、priority、flags、target、type
3. 数值合理平衡
4. 直接输出代码，不要任何解释

示例格式：
{{
  num: -10001,
  accuracy: 100,
  basePower: 90,
  category: "Physical",
  name: "Flame Strike",
  pp: 15,
  priority: 0,
  flags: {{contact: 1, protect: 1, mirror: 1}},
  secondary: {{chance: 10, status: "brn"}},
  target: "normal",
  type: "Fire",
  shortDesc: "10% chance to burn the target."
}}

请生成：
"""
    
    def _extract_code(self, response: str) -> str:
        """从响应中提取代码"""
        # 移除Markdown代码块标记
        if "```javascript" in response:
            code = response.split("```javascript")[1].split("```")[0].strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0].strip()
        else:
            code = response.strip()
        
        return code
    
    def _parse_move_code(self, code: str, description: str) -> Dict[str, Any]:
        """
        解析生成的技能代码，提取关键字段
        
        Args:
            code: 生成的JavaScript代码
            description: 原始描述
        
        Returns:
            包含解析结果的字典
        """
        import re
        
        try:
            result = {
                "success": True,
                "code": code,
                "description": description
            }
            
            # 提取 name
            name_match = re.search(r'name:\s*["\']([^"\']+)["\']', code)
            if name_match:
                result["name"] = name_match.group(1)
            
            # 提取 type
            type_match = re.search(r'type:\s*["\']([^"\']+)["\']', code)
            if type_match:
                result["type"] = type_match.group(1)
            
            # 提取 category
            cat_match = re.search(r'category:\s*["\']([^"\']+)["\']', code)
            if cat_match:
                result["category"] = cat_match.group(1)
            
            # 提取 basePower
            power_match = re.search(r'basePower:\s*(\d+)', code)
            if power_match:
                result["basePower"] = int(power_match.group(1))
            
            return result
            
        except Exception as e:
            logger.error(f"解析技能代码失败：{e}")
            return {
                "success": True,
                "code": code,
                "description": description,
                "name": "Unknown",
                "type": "Normal",
                "category": "Physical",
                "basePower": 0
            }
    
    async def generate_ability(
        self, 
        description: str, 
        auto_reference: bool = True
    ) -> Dict[str, Any]:
        """
        生成特性代码（自动选择最佳AI + RAG检索）
        
        Args:
            description: 特性描述
            auto_reference: 是否自动RAG检索参考
        
        Returns:
            包含生成结果的字典
        """
        # 获取参考特性
        references = []
        if auto_reference and self.rag_service:
            try:
                references = await self.rag_service.search_abilities(description, top_k=3)
            except Exception as e:
                logger.warning(f"RAG检索失败：{e}")
        
        try:
            # 构建特性生成的Prompt
            prompt = self._build_ability_prompt(description, references)
            
            if self.mode == "local":
                code = await self._generate_local_ability(prompt)
            else:
                # 云端模式暂未实现，返回错误
                logger.warning("特性生成暂只支持本地模式")
                return {
                    "success": False,
                    "error": "特性生成暂只支持本地模式",
                    "code": ""
                }
            
            # 解析代码提取字段
            return self._parse_ability_code(code, description)
            
        except Exception as e:
            logger.error(f"生成特性失败：{e}")
            return {
                "success": False,
                "error": str(e),
                "code": ""
            }
    
    def _build_ability_prompt(
        self, 
        description: str, 
        references: List[dict]
    ) -> str:
        """构建特性生成Prompt"""
        
        ref_text = ""
        if references:
            ref_text = "\n\n参考以下相似特性：\n"
            for ref in references[:3]:
                ref_text += f"- {ref.get('name', '')}: {ref.get('content', '')}\n"
        
        return f"""基于以下描述生成Cobblemon特性（Showdown格式JavaScript）。

用户需求：
{description}
{ref_text}

要求：
1. 返回完整的JavaScript对象（不要exports语句）
2. 必须包含：num（负数）、name、rating、shortDesc
3. 数值合理平衡
4. 直接输出代码，不要任何解释

示例格式：
{{
  num: -10001,
  name: "adaptability",
  rating: 4,
  shortDesc: "This Pokemon's moves that match its types have 1.5x power."
}}

请生成：
"""
    
    async def _generate_local_ability(self, prompt: str) -> str:
        """本地AI生成特性"""
        
        if not self.local_client:
            raise RuntimeError("本地AI客户端未初始化")
        
        try:
            response = await self.local_client.chat(
                model=self.local_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个Cobblemon特性设计师。生成JavaScript代码，Showdown格式。只输出代码，不要解释。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.7,
                    "num_predict": 500
                }
            )
            
            code = response["message"]["content"]
            return self._extract_code(code)
        
        except Exception as e:
            logger.error(f"本地AI生成特性失败：{e}")
            raise
    
    def _parse_ability_code(self, code: str, description: str) -> Dict[str, Any]:
        """
        解析生成的特性代码，提取关键字段
        
        Args:
            code: 生成的JavaScript代码
            description: 原始描述
        
        Returns:
            包含解析结果的字典
        """
        import re
        
        try:
            result = {
                "success": True,
                "code": code,
                "description": description
            }
            
            # 提取 name
            name_match = re.search(r'name:\s*["\']([^"\']+)["\']', code)
            if name_match:
                result["name"] = name_match.group(1)
            
            # 提取 rating
            rating_match = re.search(r'rating:\s*(\d+)', code)
            if rating_match:
                result["rating"] = int(rating_match.group(1))
            
            return result
            
        except Exception as e:
            logger.error(f"解析特性代码失败：{e}")
            return {
                "success": True,
                "code": code,
                "description": description,
                "name": "Unknown",
                "rating": 0
            }

