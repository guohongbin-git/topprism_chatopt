# utils.py
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

def plot_map(customers_df, schedule_df=None):
    """
    绘制客户分布地图
    如果提供了schedule_df，则绘制路径
    """
    # 基础客户点
    fig = px.scatter_mapbox(
        customers_df,
        lat="lat",
        lon="lon",
        color="priority",
        text="name",
        zoom=10,
        height=400,
        title="客户分布与拜访计划"
    )
    
    # 如果有调度结果，绘制路径
    if schedule_df is not None:
        # 这里可以添加路径绘制逻辑
        # 为了简化，我们只添加一个示例路径
        pass
    
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":25,"l":0,"b":0})
    return fig

def plot_schedule_timeline(schedule_df, customers_df):
    """
    绘制调度时间线
    """
    # 这个函数可以用来绘制每个销售代表的时间安排
    # 当前版本先返回一个简单的占位图
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1, 2], y=[0, 1, 2], mode='lines+markers'))
    fig.update_layout(title="调度时间线 (占位图)")
    return fig