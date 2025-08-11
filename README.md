# Topprism-ChatOpt 🎯

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/guohongbin-git/topprism_chatopt/blob/main/LICENSE)
[![Streamlit](https://img.shields.io/badge/streamlit-1.37.0-red)](https://streamlit.io/)
[![OR-Tools](https://img.shields.io/badge/OR--Tools-9.10.4067-orange)](https://developers.google.com/optimization)
[![Last Commit](https://img.shields.io/github/last-commit/guohongbin-git/topprism_chatopt)](https://github.com/guohongbin-git/topprism_chatopt/commits/main)
[![Repo Size](https://img.shields.io/github/repo-size/guohongbin-git/topprism_chatopt)](https://github.com/guohongbin-git/topprism_chatopt)

> 自然语言驱动的智能决策引擎 —— 让业务人员也能做复杂排程。

## 🚀 简介
Topprism-ChatOpt 是一个基于 **LLM + OR-Tools** 的低代码规划平台。  
你只需输入："每个销售每天最多拜访4个客户"，系统自动解析 → 建模 → 求解 → 可视化。

## 🔧 技术栈
- **前端**: Streamlit
- **LLM**: 本地运行 Gemma-3（通过 LM Studio）
- **建模**: Google OR-Tools
- **知识库**: 语义模式 + RAG 增强
- **部署**: 本地运行，数据不出内网

## 📦 安装

### 方法1：直接运行（推荐用于开发）
```bash
git clone https://github.com/yourname/topprism-chatopt.git
cd topprism-chatopt
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 方法2：作为包安装
```bash
git clone https://github.com/yourname/topprism-chatopt.git
cd topprism-chatopt
pip install -e .
```

## ▶️ 运行

### 开发模式
```bash
streamlit run src/topprism_chatopt/app.py
```

### 生产模式
```bash
topprism-chatopt
```

## 🧪 测试
```bash
python -m pytest tests/
```

## 📁 项目结构
```
topprism-chatopt/
├── src/
│   └── topprism_chatopt/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py              # 主应用
│       ├── rag_retriever.py    # 语义检索器
│       ├── llm_generator.py    # LLM代码生成器
│       ├── or_solver.py        # OR-Tools求解器
│       ├── utils.py            # 工具函数
│       ├── knowledge_base.json # 知识库
│       └── data/               # 示例数据
│           ├── customers.csv
│           └── agents.csv
├── tests/                      # 测试文件
├── docs/                       # 文档
├── README.md
├── requirements.txt
├── setup.py
└── pyproject.toml
```

## 🛠️ 配置

### LLM配置
项目默认配置为本地LM Studio服务器：
- 地址：`http://localhost:1234/v1`
- 模型：`gemma-3`

如需修改，请编辑 `src/topprism_chatopt/llm_generator.py` 文件。

## 🤝 贡献
欢迎提交Issue和Pull Request。

## 📄 许可证
MIT