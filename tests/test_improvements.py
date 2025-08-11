# test_improvements.py
import pandas as pd
from rag_retriever import TopprismRAG
from llm_generator import generate_model_code
from or_solver import solve_visit_scheduling

def test_rag_retriever():
    """测试RAG检索器"""
    print("=== 测试RAG检索器 ===")
    retriever = TopprismRAG()
    
    test_rules = [
        "每个销售每天最多拜访4个客户",
        "医院客户必须在9-12点拜访",
        "A类客户优先安排"
    ]
    
    for rule in test_rules:
        matches = retriever.retrieve(rule, k=1)
        print(f"规则: {rule}")
        if matches:
            print(f"匹配模式: {matches[0]['description']}")
        else:
            print("未找到匹配模式")
        print()

def test_code_generation():
    """测试代码生成"""
    print("=== 测试代码生成 ===")
    retriever = TopprismRAG()
    
    rules = ["每个销售每天最多拜访4个客户"]
    matches = []
    for rule in rules:
        matched = retriever.retrieve(rule, k=1)
        matches.extend(matched)
    
    # 读取数据
    customers = pd.read_csv("data/customers.csv")
    agents = pd.read_csv("data/agents.csv")
    
    # 生成代码
    generated_code = generate_model_code(rules, matches, customers, agents)
    print("生成的代码:")
    print(generated_code)
    print()

def test_solver():
    """测试求解器"""
    print("=== 测试求解器 ===")
    # 读取数据
    customers = pd.read_csv("data/customers.csv")
    agents = pd.read_csv("data/agents.csv")
    
    # 定义规则
    rules = [
        "每个销售每天最多拜访4个客户",
        "医院客户必须在9-12点拜访",
        "A类客户优先安排"
    ]
    
    # 生成代码用于测试
    retriever = TopprismRAG()
    matches = []
    for rule in rules:
        matched = retriever.retrieve(rule, k=1)
        matches.extend(matched)
    
    generated_code = generate_model_code(rules, matches, customers, agents)
    
    # 求解
    result = solve_visit_scheduling(customers, agents, rules, generated_code)
    print("求解结果:")
    print(result["schedule"])

if __name__ == "__main__":
    test_rag_retriever()
    test_code_generation()
    test_solver()