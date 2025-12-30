"""
添加大语言模型，通过用户输入的自然语言，来判定是否需要人工介入，把大象装进冰箱
介入条件: 只有当大象尺寸过大时候，才会介入
"""

from langgraph.graph import START, END, StateGraph
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver



# 定义状态
class ElephantInFridgeState(TypedDict):
    fridge_open: bool
    elephant_inside: bool

    user_input: str
    model_response: str
    human_decision: str


llm = ChatOpenAI(
    model="qwen3-4b",
    base_url="http://10.10.77.203:18006/v1",
    api_key="sk-makemoney"
)

# 定义图节点
def open_fridge(state: ElephantInFridgeState) -> ElephantInFridgeState:
    """
    第一步打开冰箱
    """
    print("正在打开冰箱门...")
    # 执行当前节点业务处理逻辑
    print("冰箱门已经打开")

    # 更新状态
    state['fridge_open'] = True
    return state


# 定义大模型交互节点
def put_elephant(state: ElephantInFridgeState)->ElephantInFridgeState:

    if not state["fridge_open"]:
        raise ValueError("冰箱门未打开，无法放入大象！")

    messages = state["user_input"]

    if "放入" in state["user_input"]:
        state["human_decision"] = f"用户输入的指令是: {state["user_input"]}"
    else:
        response = llm.invoke(messages)
        state["human_decision"] = "不放"
        state["model_response"] = response.content

    return state

def close_fridge(state: ElephantInFridgeState) -> ElephantInFridgeState:
    """
    关闭冰箱门
    """

    
    if state["human_decision"] == "是":
        state["model_response"] = "大象已经放入冰箱"
        state["elephant_inside"] = True
        print("大象已经放入冰箱")
    elif state["human_decision"] == "否":
        state["model_response"] = "Don't put"
        state["elephant_inside"] = False
        print("大象没有放入冰箱")
    else:
        print("state['human_decision']", state["human_decision"])
    
    if not state["elephant_inside"]:
        print("警告: 冰箱内没有大象，是否确认关闭")
    print("正在关闭冰箱门...")
    print('冰箱门已经关闭')

    state["fridge_open"] = False
    return state


def build_graph():
    graph_builder = StateGraph(ElephantInFridgeState)
    graph_builder.add_node("open_fridge", open_fridge)
    graph_builder.add_node("put_elephant", put_elephant)
    graph_builder.add_node("close_fridge", close_fridge)

    graph_builder.add_edge(START, "open_fridge")
    graph_builder.add_edge("open_fridge", "put_elephant")
    graph_builder.add_edge("put_elephant", "close_fridge")
    graph_builder.add_edge("close_fridge", END)

    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory, interrupt_before=["close_fridge"])

    # 可以把图画出来
    with open("graph_put_elephant.png", "wb") as f:
        try:
            f.write(graph.get_graph().draw_mermaid_png())
        except Exception:
            pass

    return graph


def run_workflow():
    graph = build_graph()

    config = {"configurable": {"thread_id": "1"}}
    input_data ={
        "open_fridge": False,
        "elephant_inside": False,
        "user_input": "把大象放入冰箱",
        "model_response": None
    }

    for chunk in graph.stream(input_data, config, stream_mode="values"):
        print("user")
        print(chunk)
        print("user")

    snapshot = graph.get_state(config)
    snapshot.values["human_decision"] = "否"
    graph.update_state(config, snapshot.values)

    for chunk in graph.stream(None, config, stream_mode="values"):
        print(chunk)


if __name__ == "__main__":
    run_workflow()