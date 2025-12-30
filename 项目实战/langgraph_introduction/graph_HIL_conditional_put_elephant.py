from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode


# 定义工具
def get_weather(location):
    """
    功能: 获取特定地点的天气情况
    参数:
        location: 地点
    """
    return f"获取 {location} 的天气数据"


def delete_weather_from_db(city_name):
    """
    功能: 删除数据库中某个城市的天气数据
    参数:
        city_name: 城市名称
    """
    return f"删除 {city_name} 的天气数据"


tools = [get_weather, delete_weather_from_db]
tool_node = ToolNode(tools)
# 初始化语言模型
llm = ChatOpenAI(
    model="qwen3-4b",
    base_url="http://10.10.77.203:18006/v1",
    api_key="sk-makemoney"
    ).bind_tools(tools)


# 定义状态
class State(dict):
    messages: list


# 节点函数
def call_model(state):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def should_continue(state):
    print("state: ", state)
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "end"
    elif last_message.tool_calls[0]["name"] == "delete_weather_from_db":
        return "run_tool" 
    else:
        return "continue"
# 构建图
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent", 
    should_continue, 
    {
        "continue": "action", 
        "run_tool": "action", 
        "end": END
    })
workflow.add_edge("action", "agent")
# 编译图并设置断点
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory, interrupt_before=["action"])

# 可以把图画出来
with open("graph.png", "wb") as f:
    try:
        f.write(graph.get_graph().draw_mermaid_png())
    except Exception:
        pass
# 测试
config = {"configurable": {"thread_id": "2"}}
for chunk in graph.stream({"messages": ["获取北京的天气数据"]}, config, stream_mode="values"):
    print("chunk", chunk)
