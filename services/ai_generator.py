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
    
    def __init__(self, config: dict):
        """
        初始化AI生成器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.mode = config.get("ai", {}).get("mode", "cloud")
        
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
        references: List[dict] = None
    ) -> str:
        """
        生成技能代码（自动选择最佳AI）
        
        混合模式逻辑：
        - 简单描述（<50字）→ 尝试本地AI
        - 复杂描述（≥50字）→ 使用云端AI
        - 本地失败 → 自动降级云端
        
        Args:
            description: 技能描述
            references: 参考技能列表
        
        Returns:
            技能代码（JavaScript对象字符串）
        """
        if self.mode == "cloud":
            return await self._generate_cloud(description, references or [])
        
        elif self.mode == "local":
            return await self._generate_local(description, references or [])
        
        elif self.mode == "hybrid":
            # 智能判断
            if len(description) < 50:
                try:
                    logger.info("  💻 使用本地AI...")
                    return await self._generate_local(description, references or [])
                except Exception as e:
                    logger.warning(f"  ⚠️  本地AI失败，切换云端：{e}")
                    return await self._generate_cloud(description, references or [])
            else:
                logger.info("  ☁️  使用云端AI...")
                return await self._generate_cloud(description, references or [])
        
        else:
            raise ValueError(f"未知的AI模式: {self.mode}")
    
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
    
    async def generate_abilities(
        self, 
        descriptions: List[str]
    ) -> List[dict]:
        """
        生成特性代码
        
        Args:
            descriptions: 特性描述列表
        
        Returns:
            生成的特性代码列表
        """
        # TODO: 实现特性生成（类似generate_move）
        logger.warning("⚠️  特性生成功能开发中")
        
        return [
            {
                "description": desc,
                "code": "// TODO: 实现特性生成",
                "valid": False,
                "errors": ["功能开发中"]
            }
            for desc in descriptions
        ]

