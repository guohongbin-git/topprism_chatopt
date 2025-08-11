# rag_retriever.py
import json
import numpy as np
import faiss
import re
import os

class TopprismRAG:
    """
    Topprism-ChatOpt 的语义检索器
    负责将自然语言规则匹配到建模知识库
    """
    def __init__(self, kb_path=None):
        # 如果没有指定路径，使用默认路径
        if kb_path is None:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            kb_path = os.path.join(current_dir, "knowledge_base.json")
        
        with open(kb_path, encoding='utf-8') as f:
            self.kb = json.load(f)
        self.model = None
        self.index = None
        self.pattern_to_item = []
        self.pattern_strings = []
        self.build_index()

    def _load_model(self):
        """延迟加载模型，避免初始化错误"""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"模型加载失败: {str(e)}")
                print("将使用基于正则表达式的匹配方法")
                self.model = None

    def build_index(self):
        # 加载模型
        self._load_model()
        
        sentences = []
        self.pattern_to_item = []
        self.pattern_strings = []
        for item in self.kb["semantic_patterns"]:
            for p in item["patterns"]:
                sentences.append(p)
                self.pattern_to_item.append(item)
                self.pattern_strings.append(p)
        
        # 如果模型加载成功，构建语义索引
        if self.model is not None and sentences:
            try:
                embeddings = self.model.encode(sentences)
                self.index = faiss.IndexFlatL2(embeddings.shape[1])
                self.index.add(np.array(embeddings))
            except Exception as e:
                print(f"索引构建失败: {str(e)}")
                self.index = None
        else:
            # 模型未加载时，设置索引为None
            self.index = None

    def retrieve(self, query, k=3):
        # 首先尝试精确匹配
        exact_match = self._exact_match(query)
        if exact_match:
            return [exact_match]
        
        # 如果没有精确匹配，且模型可用，使用语义搜索
        if self.index is not None and self.model is not None:
            try:
                query_vec = self.model.encode([query])
                scores, indices = self.index.search(query_vec, k)
                
                # 过滤掉低相似度的结果
                results = []
                for i, score in zip(indices[0], scores[0]):
                    # 相似度阈值，可以根据需要调整
                    if score < 1.0:  # faiss L2距离，越小越相似
                        results.append(self.pattern_to_item[i])
                
                if results:
                    return results
            except Exception as e:
                print(f"语义搜索失败: {str(e)}")
        
        # 如果语义搜索不可用或没有找到结果，使用基于正则表达式的匹配
        regex_match = self._regex_match(query)
        if regex_match:
            return [regex_match]
        
        # 如果没有找到匹配的结果，返回默认匹配
        if self.kb["semantic_patterns"]:
            # 默认返回第一个模式
            return [self.kb["semantic_patterns"][0]]
        
        return []

    def _exact_match(self, query):
        """
        尝试精确匹配规则
        """
        for item, pattern_str in zip(self.pattern_to_item, self.pattern_strings):
            # 将模式中的.*替换为匹配任何字符的正则表达式
            regex_pattern = pattern_str.replace(".*", ".*")
            if re.search(regex_pattern, query):
                return item
        return None

    def _regex_match(self, query):
        """
        使用正则表达式进行模式匹配
        """
        # 为每个模式计算匹配度分值
        best_match = None
        best_score = 0
        
        for item, pattern_str in zip(self.pattern_to_item, self.pattern_strings):
            # 计算匹配度分值
            score = 0
            
            # 如果模式中的关键词在查询中出现，增加分值
            # 简化的评分方法：计算模式中的关键词在查询中出现的次数
            keywords = re.findall(r'[\u4e00-\u9fff]+', pattern_str)  # 提取中文关键词
            for keyword in keywords:
                if keyword in query:
                    score += 1
            
            # 如果当前模式得分更高，更新最佳匹配
            if score > best_score:
                best_score = score
                best_match = item
        
        return best_match if best_score > 0 else None

    def get_all_patterns(self):
        """
        获取所有模式，用于调试
        """
        return self.pattern_strings