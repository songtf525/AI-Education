"""
这是一个langgraph入门教程
1. 搭建图实现'把大象装进冰箱需要几步'
添加了一个条件选择分支 add_conditional_edges: 根据当前图状态路由到不同的节点，接收当前图形状态，返回字符串或者字符串列表，指示下一个要调用的节点
"""

from langgraph.graph import START, END, StateGraph
from typing_extensions import TypedDict, Literal
from typing import Optional

# 定义状态
class ElephantInFridgeState(TypedDict):
    """
    定义状态: 大象在冰箱中
    状态内的参数可以在多个节点间保存和流转
    """
    fridge_open: bool               # 冰箱门是否打开
    elephant_inside: bool           # 大象是否在冰箱内
    elephant_size: int              # 大象的标准尺寸
    human_decision: Optional[str]   # 人工决策结果


# 定义图节点
def open_fridge(state: ElephantInFridgeState) -> ElephantInFridgeState:
    """
    第一步: 打开冰箱门
    """
    print("正在打开冰箱门...")
    # 执行当前节点业务处理逻辑
    print("冰箱门已经打开")

    # 更新状态
    state["fridge_open"] = True
    # 当前节点处理完成，更新状态
    return state

def human_approval(state: ElephantInFridgeState)->ElephantInFridgeState:
    """
    人工决策节点: 是否把大象放进冰箱
    """
    size = state["elephant_size"]

    # 模拟人工决策
    print(f"\n人工决策中... 大象尺寸: {size} (标准阈值: 5)")

    if size <= 3:
        print("提示: 大象很小，建议放入冰箱")
        decision = "put_elephant"
    elif size >= 8:
        print("警告: 大象过大，不建议放入冰箱")
        decision = "close_fridge"
    else:
        user_input = input("是否把大象放入冰箱?(y/n): ").strip().lower()
        decision = "put_elephant" if user_input == "y" else "close_fridge"

    # 保存决策结果到状态
    state['human_decision'] = decision

    print(f"人工决策结果: {'把大象放进冰箱' if decision == 'put_elephant' else "算了，不把大象放入冰箱"}")
    return state


def put_elephant(state: ElephantInFridgeState)->ElephantInFridgeState:
    """
    第二步: 把大象放进去
    """
    # 获取当前状态
    if not state["fridge_open"]:
        raise ValueError("冰箱门未打开，无法放入大象！")
    
    # 执行当前节点业务逻辑
    print("正在把大象放进冰箱...")
    print("大象已经放进冰箱")

    # 更新状态
    state["elephant_inside"]=True
    # 当前节点处理完成，更新状态
    return state

def close_fridge(state: ElephantInFridgeState) -> ElephantInFridgeState:
    """
    第三步: 关闭冰箱门
    """     

    # 获取当前状态
    if not state["elephant_inside"]:
        print("警告: 冰箱内没有大象，是否确认关闭")

    # 执行当前节点业务逻辑
    print("正在关闭冰箱门...")
    print("冰箱门已经关闭")

    # 更新状态
    state["fridge_open"]=False
    # 当前节点处理完成，更新状态
    return state
    

# 构建工作流图
def build_graph():
    """
    构建把大象装进冰箱的工作流图
    """
    graph_builder = StateGraph(ElephantInFridgeState)
    
    graph_builder.add_node("open_fridge", open_fridge)
    graph_builder.add_node("human_approval", human_approval)
    graph_builder.add_node("put_elephant", put_elephant)
    graph_builder.add_node("close_fridge", close_fridge)

    graph_builder.add_edge(START, "open_fridge")
    graph_builder.add_edge("open_fridge", "human_approval")
    
    graph_builder.add_conditional_edges(
        "human_approval",
        lambda state: "put_elephant" if state.get("human_decision") == "put_elephant" else "close_fridge", 
        {
            "put_elephant": "put_elephant",
            "close_fridge": "close_fridge"
        }
    )
    graph_builder.add_edge("put_elephant", "close_fridge")
    graph_builder.add_edge("close_fridge", END)

    graph = graph_builder.compile()

    # 可以把图画出来
    with open("graph_human_put_elephant.png", "wb") as f:
        try:
            f.write(graph.get_graph().draw_mermaid_png())
        except Exception:
            pass

    return graph


# 运行工作流
def run_workflow(elephant_size: int):
    graph = build_graph()
    
    # 定义初始状态, 冰箱门没有打开，大象没在冰箱内
    initial_state = ElephantInFridgeState(fridge_open=False, elephant_inside=False, elephant_size=elephant_size, human_decision=None)
    result = graph.invoke(initial_state)

    # 输出最终状态    
    print("\n工作流执行完毕, 最终状态:")
    print(f"冰箱门状态: {'打开' if result["fridge_open"] else '关闭'}")
    print(f"大象是否在冰箱内: {'是' if result["elephant_inside"] else '否'}")

    return result


if __name__ == "__main__":
    final_state = run_workflow(elephant_size=10)
    print("final_state: ", final_state)