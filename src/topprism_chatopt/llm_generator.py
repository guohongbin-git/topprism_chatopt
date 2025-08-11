# llm_generator.py
import json
from typing import List
import re

# 延迟导入OpenAI，避免初始化错误
client = None

def get_openai_client():
    global client
    if client is None:
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="http://localhost:1234/v1",
                api_key="not-needed"
            )
        except Exception as e:
            print(f"OpenAI客户端初始化失败: {str(e)}")
            client = None
    return client

def parse_rule_parameters(rule: str, pattern_item: dict) -> dict:
    """
    解析规则中的参数
    这是一个简化的实现，实际应用中可能需要更复杂的NLP处理
    """
    parameters = {}
    
    # 处理"每个销售每天最多拜访4个客户"这类规则
    if "每个" in rule and "最多" in rule:
        # 提取数字
        numbers = re.findall(r'\d+', rule)
        if numbers:
            parameters["max_count"] = numbers[0]
        else:
            parameters["max_count"] = "4"  # 默认值
    
    # 处理时间窗口规则
    if "医院客户必须在9-12点拜访" in rule:
        parameters["start"] = "9"
        parameters["end"] = "12"
    
    # 处理优先级规则
    if "A类客户优先安排" in rule:
        parameters["penalty"] = "1000"  # 高优先级客户的低惩罚值
    
    return parameters

def generate_model_code_with_knowledge(rules: List[str], context_items: list, customers_df=None, agents_df=None) -> str:
    """
    基于知识库直接生成 OR-Tools 代码，不依赖LLM
    """
    code_lines = [
        "# Topprism-ChatOpt 自动生成的约束代码",
        "import pandas as pd",
        ""
    ]
    
    for rule, context_item in zip(rules, context_items):
        template = context_item.get("or_tools_template", "")
        parameters = parse_rule_parameters(rule, context_item)
        
        # 替换模板中的参数
        for key, value in parameters.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        # 特殊处理时间窗口约束
        if context_item.get("intent") == "service_time_window":
            # 添加时间窗口约束代码
            code_lines.append("# 添加时间窗口约束")
            code_lines.append("for i, customer in customers_df.iterrows():")
            code_lines.append("    if customer['priority'] == 'A':  # 以A类客户为例")
            code_lines.append("        index = manager.NodeToIndex(i)")
            code_lines.append("        if index != -1:")
            code_lines.append("            time_dimension.CumulVar(index).SetRange(int(customer['time_window_start']) * 60, int(customer['time_window_end']) * 60)")
            code_lines.append("")
        # 特殊处理访问次数约束
        elif context_item.get("intent") == "limit_visit_count":
            code_lines.append("# 添加访问次数约束")
            code_lines.append(template)
            code_lines.append("")
        # 特殊处理优先级约束
        elif context_item.get("intent") == "maximize_priority":
            code_lines.append("# 添加优先级约束")
            code_lines.append("# 优先安排A类客户")
            code_lines.append("for i, customer in customers_df.iterrows():")
            code_lines.append("    if customer['priority'] == 'A':")
            code_lines.append("        index = manager.NodeToIndex(i)")
            code_lines.append("        if index != -1:")
            code_lines.append("            routing.AddDisjunction([index], 1000)  # 低惩罚值表示高优先级")
            code_lines.append("")
    
    return "\n".join(code_lines)

def generate_model_code(rules: List[str], context_items: list, customers_df=None, agents_df=None) -> str:
    """
    使用本地模型生成 OR-Tools 建模代码
    支持 Topprism-ChatOpt 知识库增强
    """
    # 首先尝试基于知识库直接生成代码
    if context_items:
        try:
            knowledge_based_code = generate_model_code_with_knowledge(rules, context_items, customers_df, agents_df)
            if knowledge_based_code:
                return knowledge_based_code
        except Exception as e:
            print(f"基于知识库生成代码失败: {str(e)}")
    
    # 如果知识库方法失败，则使用LLM生成
    context = "\n".join([
        f"Pattern: {item['description']}\nTemplate: {item['or_tools_template']}"
        for item in context_items
    ])

    prompt = f"""
你是一个 Topprism-ChatOpt 智能建模助手。
根据以下业务规则和知识库，生成精确的 OR-Tools Python 代码。

业务规则：
{json.dumps(rules, ensure_ascii=False, indent=2)}

参考知识库：
{context}

要求：
- 只输出 Python 代码
- 不要解释
- 使用标准 OR-Tools API
- 仅包含约束定义
- 不要包含导入语句或函数定义
- 直接使用提供的变量：routing, manager, time_dimension, customers_df, agents_df
"""

    # 获取OpenAI客户端
    client = get_openai_client()
    if client is None:
        # 如果LLM不可用，返回基于知识库的简化版本
        fallback_code = generate_fallback_code(rules, context_items)
        return f"# Topprism-ChatOpt: 本地模型不可用，使用简化版本\n{fallback_code}"

    try:
        completion = client.chat.completions.create(
            model="gemma-3",
            messages=[
                {"role": "system", "content": "You are Topprism-ChatOpt, a precise optimization modeling assistant. Output only code. Do not include import statements or function definitions. Use the provided variables directly: routing, manager, time_dimension, customers_df, agents_df."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=512,
            stop=None
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        # 如果LLM调用失败，返回基于知识库的简化版本
        fallback_code = generate_fallback_code(rules, context_items)
        return f"# Topprism-ChatOpt: 本地模型调用失败，使用简化版本\n{fallback_code}"

def generate_fallback_code(rules: List[str], context_items: list) -> str:
    """
    当LLM不可用时的备用代码生成方法
    """
    code_lines = []
    
    for rule, context_item in zip(rules, context_items):
        if not context_item:
            continue
            
        intent = context_item.get("intent", "")
        template = context_item.get("or_tools_template", "")
        
        if intent == "limit_visit_count":
            # 默认每个销售最多拜访4个客户
            code_lines.append("# 每个销售最多拜访4个客户")
            code_lines.append("routing.AddConstantDimension(1, 4, True, 'VisitCount')")
        elif intent == "service_time_window":
            code_lines.append("# 时间窗口约束")
            code_lines.append("# 基于客户数据中的时间窗口")
        elif intent == "maximize_priority":
            code_lines.append("# 优先安排高价值客户")
            code_lines.append("# 通过设置不同的惩罚值来实现优先级")
    
    return "\n".join(code_lines) if code_lines else "# 无约束条件"