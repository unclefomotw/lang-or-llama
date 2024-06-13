# 1. Demo interruption / Human-in-the-loop
# 2. Show stream mode and how to properly get_state when .stream()
#

from typing import Annotated, TypedDict

from langgraph.checkpoint import MemorySaver
from langgraph.graph import StateGraph, END


class MyState(TypedDict):
    crew: Annotated[list, lambda x, y: x + y]


class NodeFunc:
    def __init__(self, num: int):
        self.num = num

    def __call__(self, state: MyState):
        print(f"Number {self.num} here!")
        return {"crew": [self.num]}


def session(_id):
    return {"configurable": {"thread_id": str(_id)}}


def main():
    workflow = StateGraph(state_schema=MyState)

    workflow.add_node("n1", NodeFunc(1))
    workflow.add_node("n2", NodeFunc(2))
    workflow.add_node("n3", NodeFunc(3))
    workflow.add_node("n4", NodeFunc(4))
    workflow.set_entry_point("n1")

    workflow.add_edge("n1", "n2")
    workflow.add_edge("n2", "n3")
    workflow.add_edge("n3", "n4")
    workflow.add_edge("n4", END)

    graph = workflow.compile(
        checkpointer=MemorySaver(),
        interrupt_after=["n2"]
    )

    print("## .invoke()")
    r = graph.invoke({"crew": []}, config=session(1))
    print(f"Result: {r}")
    print(graph.get_state(session(1)))
    print("\n")

    print("## get_state_history")
    for h in graph.get_state_history(session(1)):
        print(h)
    print("\n")

    print(f"Default stream mode: {graph.stream_mode}\n")

    print("## .stream() , mode 'updates'")
    i = 1
    for s in graph.stream({"crew": []}, config=session(2), stream_mode="updates"):
        print(f"(Stream step {i})")
        print(f"Result: {s}")
        print(graph.get_state(session(2)))
        print()
        i += 1
    print(graph.get_state(session(2)))  # get the state after loop
    print("\n")

    print("## .stream() , mode 'values'")
    i = 1
    for s in graph.stream({"crew": []}, config=session(3), stream_mode="values"):
        print(f"(Stream step {i})")
        print(f"Result: {s}")
        print(graph.get_state(session(3)))
        print()
        i += 1
    print(graph.get_state(session(3)))  # get the state after loop
    print("\n")

    print("## .stream() , mode 'debug'")
    i = 1
    for s in graph.stream({"crew": []}, config=session(4), stream_mode="debug"):
        print(f"(Stream step {i})")
        print(f"Result: {s}")
        print(graph.get_state(session(4)))
        print()
        i += 1
    print(graph.get_state(session(4)))  # get the state after loop
    print("\n")


if __name__ == '__main__':
    main()
