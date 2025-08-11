# or_solver.py
# Topprism-ChatOpt | OR-Tools 求解引擎
import pandas as pd
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import json

def solve_visit_scheduling(customers_df, agents_df, rules, generated_code=""):
    n_customers = len(customers_df)
    n_agents = len(agents_df)

    manager = pywrapcp.RoutingIndexManager(n_customers, n_agents, 0)
    routing = pywrapcp.RoutingModel(manager)

    # 距离回调（简化）
    def distance_callback(from_index, to_index):
        # 简化的距离计算，实际应根据经纬度计算真实距离
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        if from_node == to_node:
            return 0
        return 1

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 添加时间维度（用于时间窗口约束）
    def service_time_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        if from_node < len(customers_df):
            return int(customers_df.iloc[from_node]["service_time_minutes"])
        return 0

    service_time_callback_index = routing.RegisterUnaryTransitCallback(service_time_callback)
    
    # 添加时间维度
    horizon = 24 * 60  # 一天的分钟数
    time = "Time"
    routing.AddDimension(
        service_time_callback_index,
        horizon,  # allow waiting time
        horizon,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time
    )
    time_dimension = routing.GetDimensionOrDie(time)

    # 根据LLM生成的代码动态添加约束
    if generated_code and not generated_code.startswith("# Topprism-ChatOpt: 本地模型调用失败"):
        try:
            # 准备命名空间
            namespace = {
                "routing": routing,
                "manager": manager,
                "time_dimension": time_dimension,
                "customers_df": customers_df,
                "agents_df": agents_df
            }
            
            # 执行生成的代码
            exec(generated_code, namespace)
        except Exception as e:
            print(f"执行生成代码时出错: {str(e)}")
            # 添加默认约束
            add_default_constraints(routing, agents_df)

    # 如果没有生成代码或执行失败，添加默认约束
    else:
        add_default_constraints(routing, agents_df)

    # 添加时间窗口约束（基于数据）
    add_time_window_constraints(routing, manager, time_dimension, customers_df)

    # 求解
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(30)
    search_parameters.log_search = True

    solution = routing.SolveWithParameters(search_parameters)
    schedule = []

    if solution:
        for vehicle_id in range(n_agents):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                customer_id = manager.IndexToNode(index)
                if customer_id < len(customers_df):
                    route.append(customers_df.iloc[customer_id]["name"])
                index = solution.Value(routing.NextVar(index))
            if len(route) > 0:
                schedule.append({"销售代表": agents_df.iloc[vehicle_id]["name"], "拜访客户": " → ".join(route)})
            else:
                schedule.append({"销售代表": agents_df.iloc[vehicle_id]["name"], "拜访客户": "无"})
    else:
        schedule.append({"销售代表": "无", "拜访客户": "求解失败"})

    return {"status": "success", "schedule": pd.DataFrame(schedule)}

def add_default_constraints(routing, agents_df):
    """添加默认约束"""
    # 默认约束：每个销售最多访问4个客户
    if len(agents_df) > 0 and "max_visits_per_day" in agents_df.columns:
        max_visits = agents_df["max_visits_per_day"].max()
        routing.AddConstantDimension(
            1, max_visits, True, "VisitCount"
        )
    else:
        routing.AddConstantDimension(
            1, 4, True, "VisitCount"
        )

def add_time_window_constraints(routing, manager, time_dimension, customers_df):
    """添加时间窗口约束"""
    for i, customer in customers_df.iterrows():
        index = manager.NodeToIndex(i)
        if index != -1:  # 确保索引有效
            start_time = int(customer["time_window_start"]) * 60  # 转换为分钟
            end_time = int(customer["time_window_end"]) * 60
            time_dimension.CumulVar(index).SetRange(start_time, end_time)