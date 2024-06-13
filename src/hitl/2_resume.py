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
    workflow.add_node("n5", NodeFunc(5))
    workflow.add_node("n6", NodeFunc(6))
    workflow.set_entry_point("n1")

    workflow.add_edge("n1", "n2")
    workflow.add_edge("n2", "n3")
    workflow.add_edge("n3", "n4")
    workflow.add_edge("n4", "n5")
    workflow.add_edge("n5", "n6")
    workflow.add_edge("n6", END)

    graph = workflow.compile(
        checkpointer=MemorySaver(),
        interrupt_after=["n3"]
    )

    # Example 1: simply resume
    print("## Resume")

    r = graph.invoke({"crew": []}, config=session(1))
    print(f"Result: {r}")  # {'crew': [1, 2, 3]}
    print(graph.get_state(session(1)))

    # Resume by calling with input `None`
    print("\n>> resume")
    r = graph.invoke(None, config=session(1))
    print(f"Result: {r}")  # {'crew': [1, 2, 3, 4, 5, 6]}
    print(graph.get_state(session(1)))

    print("\n")

    # Example 2: Not resume, but start over
    print("## Start over")

    r = graph.invoke({"crew": []}, config=session(2))
    print(f"Result: {r}")
    print(graph.get_state(session(2)))

    # Calling with a new input just starts it over
    print("\n>> start over")
    r = graph.invoke({"crew": [66, 77]}, config=session(2))
    print(f"Result: {r}")  # {'crew': [1, 2, 3, 66, 77, 1, 2, 3]}
    print(graph.get_state(session(2)))


if __name__ == '__main__':
    main()
