"""
CobbleSeer - RAG检索服务

负责从参考库中检索相似内容：
- 向量化文本（sentence-transformers）
- 存储到ChromaDB
- 语义搜索
- 返回Top-K相似结果

参考库来源：
- 技能参考：官方Showdown技能代码
- 特性参考：官方特性代码
- 宝可梦参考：官方宝可梦配置
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger


class RAGService:
    """RAG检索服务"""
    
    def __init__(self, config: dict):
        """
        初始化RAG服务
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.enabled = config.get("rag", {}).get("enabled", True)
        
        if not self.enabled:
            logger.warning("⚠️  RAG服务已禁用")
            return
        
        self.collection_name = config.get("rag", {}).get("collection_name", "cobblemon_reference")
        self.top_k = config.get("rag", {}).get("top_k", 5)
        
        # 初始化ChromaDB和嵌入模型
        self._init_chroma()
        self._init_embedding_model()
        
        logger.info(f"✅ RAG服务初始化完成（集合：{self.collection_name}）")
    
    def _init_chroma(self):
        """初始化ChromaDB"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # 数据目录
            data_dir = Path(__file__).parent.parent / "data" / "chroma_db"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建客户端
            self.chroma_client = chromadb.PersistentClient(
                path=str(data_dir),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # 获取或创建集合
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Cobblemon reference data"}
            )
            
            logger.info(f"✅ ChromaDB初始化成功（路径：{data_dir}）")
        
        except ImportError:
            logger.error("❌ chromadb库未安装，请运行：pip install chromadb")
            self.chroma_client = None
            self.collection = None
        except Exception as e:
            logger.error(f"❌ ChromaDB初始化失败：{e}")
            self.chroma_client = None
            self.collection = None
    
    def _init_embedding_model(self):
        """初始化嵌入模型"""
        try:
            from sentence_transformers import SentenceTransformer
            
            model_name = self.config.get("rag", {}).get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
            
            logger.info(f"🔄 加载嵌入模型：{model_name}...")
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"✅ 嵌入模型加载成功")
        
        except ImportError:
            logger.error("❌ sentence-transformers库未安装，请运行：pip install sentence-transformers")
            self.embedding_model = None
        except Exception as e:
            logger.error(f"❌ 嵌入模型加载失败：{e}")
            self.embedding_model = None
    
    async def search_moves(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        搜索相似技能
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
        
        Returns:
            相似技能列表
        """
        if not self.enabled or not self.collection:
            logger.warning("⚠️  RAG服务不可用，返回空结果")
            return []
        
        k = top_k or self.top_k
        
        try:
            logger.debug(f"🔍 搜索技能：{query[:50]}...")
            
            # 向量化查询
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # 搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where={"type": "move"}  # 过滤技能类型
            )
            
            # 解析结果
            moves = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else 0
                    
                    moves.append({
                        "name": metadata.get("name", "Unknown"),
                        "basePower": metadata.get("basePower", 0),
                        "accuracy": metadata.get("accuracy", 100),
                        "type": metadata.get("move_type", "Normal"),
                        "category": metadata.get("category", "Physical"),
                        "content": doc,
                        "similarity": 1 - distance  # 距离转相似度
                    })
            
            logger.debug(f"✅ 找到 {len(moves)} 个相似技能")
            return moves
        
        except Exception as e:
            logger.error(f"❌ 技能搜索失败：{e}")
            return []
    
    async def search_abilities(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        搜索相似特性
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
        
        Returns:
            相似特性列表
        """
        if not self.enabled or not self.collection:
            logger.warning("⚠️  RAG服务不可用，返回空结果")
            return []
        
        k = top_k or self.top_k
        
        try:
            logger.debug(f"🔍 搜索特性：{query[:50]}...")
            
            # 向量化查询
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # 搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where={"type": "ability"}  # 过滤特性类型
            )
            
            # 解析结果
            abilities = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else 0
                    
                    abilities.append({
                        "name": metadata.get("name", "Unknown"),
                        "content": doc,
                        "similarity": 1 - distance
                    })
            
            logger.debug(f"✅ 找到 {len(abilities)} 个相似特性")
            return abilities
        
        except Exception as e:
            logger.error(f"❌ 特性搜索失败：{e}")
            return []
    
    def index_reference_data(self, data_type: str, items: List[Dict[str, Any]]):
        """
        索引参考数据到向量数据库
        
        Args:
            data_type: 数据类型（move/ability/pokemon）
            items: 数据项列表
        """
        if not self.enabled or not self.collection:
            logger.warning("⚠️  RAG服务不可用，无法索引")
            return
        
        try:
            logger.info(f"📚 索引{data_type}数据：{len(items)}项...")
            
            documents = []
            metadatas = []
            ids = []
            
            for i, item in enumerate(items):
                # 提取文本内容
                content = item.get("content", "")
                if not content:
                    continue
                
                # 生成ID
                item_id = f"{data_type}_{item.get('name', i)}"
                
                # 元数据
                metadata = {
                    "type": data_type,
                    "name": item.get("name", ""),
                    **{k: v for k, v in item.items() if k != "content" and isinstance(v, (str, int, float, bool))}
                }
                
                documents.append(content)
                metadatas.append(metadata)
                ids.append(item_id)
            
            # 批量添加
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"✅ 索引完成：{len(documents)}项")
            
        except Exception as e:
            logger.error(f"❌ 索引失败：{e}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        获取集合统计信息
        
        Returns:
            统计信息字典
        """
        if not self.collection:
            return {"error": "Collection not initialized"}
        
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "enabled": self.enabled
            }
        except Exception as e:
            return {"error": str(e)}

