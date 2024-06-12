from typing import TypedDict, Annotated

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint import MemorySaver
from langgraph.graph import StateGraph

llm = ChatOpenAI()

_debug = False


def concat(original: list, new: list) -> list:
    if _debug:
        print(f"left: {original}\nright:{new}")
    return original + new


class ChatState(TypedDict):
    messages: Annotated[list, concat]


def chat(state: ChatState):
    answer = llm.invoke(state["messages"])
    return {"messages": [answer]}


workflow = StateGraph(ChatState)
workflow.add_node(chat)
workflow.set_entry_point("chat")
workflow.add_edge("chat", "__end__")
graph = workflow.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "1"}}
while True:
    user_input = input(">>> ")
    r = graph.invoke(
        {"messages": [HumanMessage(user_input)]},
        config=config
    )
    print("AI: " + r["messages"][-1].content)

    if _debug:
        print("-------------")
        for h in graph.get_state_history(config):
            print(h, end="\n\n")
        print("-------------")
