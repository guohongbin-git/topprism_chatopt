# app.py
import streamlit as st
import pandas as pd
import os
from .rag_retriever import TopprismRAG
from .llm_generator import generate_model_code
from .or_solver import solve_visit_scheduling
from .utils import plot_map

# 页面配置
st.set_page_config(page_title="Topprism-ChatOpt", layout="wide", page_icon="🎯")
st.title("🎯 Topprism-ChatOpt | 自然语言规划引擎")

# 侧边栏
st.sidebar.header("📝 输入业务规则")
rules_input = st.sidebar.text_area(
    "每行一条规则",
    value="每个销售每天最多拜访4个客户\nA类客户优先安排\n医院客户必须在9-12点拜访",
    height=200
)
rules = [r.strip() for r in rules_input.split('\n') if r.strip()]

st.sidebar.markdown("---")
if st.sidebar.button("🚀 开始求解", key="solve"):
    solving = True
else:
    solving = False

# 主界面
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("⚙️ 建模解析")
    if rules and solving:
        retriever = TopprismRAG()
        matches = []
        for rule in rules:
            matched = retriever.retrieve(rule, k=1)
            matches.extend(matched)

        st.write("✅ 匹配到以下建模模式：")
        for m in matches:
            with st.expander(f"🔹 {m['description']}"):
                st.code(m["or_tools_template"], language="python")

        # 读取数据用于代码生成
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, "data")
        customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
        agents = pd.read_csv(os.path.join(data_dir, "agents.csv"))

        with st.spinner("🧠 Topprism 正在生成模型..."):
            generated_code = generate_model_code(rules, matches, customers, agents)
        st.code(generated_code, language="python")

with col2:
    st.subheader("📊 求解结果")

    if solving:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, "data")
        customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
        agents = pd.read_csv(os.path.join(data_dir, "agents.csv"))

        with st.spinner("🔧 正在求解..."):
            # 将生成的代码传递给求解器
            result = solve_visit_scheduling(customers, agents, rules, generated_code if 'generated_code' in locals() else "")

        st.success("✅ Topprism-ChatOpt 求解完成！")
        st.dataframe(result["schedule"], use_container_width=True)

        # 显示地图可视化
        map_fig = plot_map(customers)
        st.plotly_chart(map_fig, use_container_width=True)
        
        # 可选：显示调度时间线
        # timeline_fig = plot_schedule_timeline(result["schedule"], customers)
        # st.plotly_chart(timeline_fig, use_container_width=True)

def main():
    """主函数"""
    # 页面配置
    st.set_page_config(page_title="Topprism-ChatOpt", layout="wide", page_icon="🎯")
    st.title("🎯 Topprism-ChatOpt | 自然语言规划引擎")

    # 侧边栏
    st.sidebar.header("📝 输入业务规则")
    rules_input = st.sidebar.text_area(
        "每行一条规则",
        value="每个销售每天最多拜访4个客户\nA类客户优先安排\n医院客户必须在9-12点拜访",
        height=200
    )
    rules = [r.strip() for r in rules_input.split('\n') if r.strip()]

    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 开始求解", key="solve"):
        solving = True
    else:
        solving = False

    # 主界面
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("⚙️ 建模解析")
        if rules and solving:
            retriever = TopprismRAG()
            matches = []
            for rule in rules:
                matched = retriever.retrieve(rule, k=1)
                matches.extend(matched)

            st.write("✅ 匹配到以下建模模式：")
            for m in matches:
                with st.expander(f"🔹 {m['description']}"):
                    st.code(m["or_tools_template"], language="python")

            # 读取数据用于代码生成
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, "data")
            customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
            agents = pd.read_csv(os.path.join(data_dir, "agents.csv"))

            with st.spinner("🧠 Topprism 正在生成模型..."):
                generated_code = generate_model_code(rules, matches, customers, agents)
            st.code(generated_code, language="python")

    with col2:
        st.subheader("📊 求解结果")

        if solving:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, "data")
            customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
            agents = pd.read_csv(os.path.join(data_dir, "agents.csv"))

            with st.spinner("🔧 正在求解..."):
                # 将生成的代码传递给求解器
                result = solve_visit_scheduling(customers, agents, rules, generated_code if 'generated_code' in locals() else "")

            st.success("✅ Topprism-ChatOpt 求解完成！")
            st.dataframe(result["schedule"], use_container_width=True)

            # 显示地图可视化
            map_fig = plot_map(customers)
            st.plotly_chart(map_fig, use_container_width=True)
            
            # 可选：显示调度时间线
            # timeline_fig = plot_schedule_timeline(result["schedule"], customers)
            # st.plotly_chart(timeline_fig, use_container_width=True)

if __name__ == "__main__":
    main()