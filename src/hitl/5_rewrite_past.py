from typing import Annotated, TypedDict

from langgraph.checkpoint import MemorySaver
from langgraph.graph import StateGraph, END


class MyState(TypedDict):
    v: str
    crew: Annotated[list, lambda x, y: x + y]


class NodeFunc:
    def __init__(self, num: int):
        self.num = num

    def __call__(self, state: MyState):
        print(f"Number {self.num} sees {state['v']} coming in")
        return {"crew": [self.num], "v": f"No. {self.num}"}


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

    # Example 1: change the past state, using non-thread_ts config + as_node
    print("## .update_state(<no thread_ts>)")

    r = graph.invoke({"crew": []}, config=session(1))
    print(f"Result: {r}")
    print(graph.get_state(session(1)))

    # Update
    graph.update_state(
        config=session(1),
        values={"crew": [66, 77], "v": "BAD GUY"},
        as_node="n1"
    )
    print("\n>> after update")
    print(graph.get_state(session(1)))

    # Resume
    print("\n>> resume")
    r = graph.invoke(None, config=session(1))
    print(f"Result: {r}")

    print("\n>> history (notice the metadata.step)")
    for h in graph.get_state_history(session(1)):
        print(h)

    print("\n")

    # Example 2: change the past state, by the specific thread_ts config
    print("## .update_state(<thread_ts>)")

    r = graph.invoke({"crew": []}, config=session(2))
    print(f"Result: {r}")
    print(graph.get_state(session(2)))

    for h in graph.get_state_history(session(2)):
        if h.next == ("n2", ):
            past_config = h.config
            break

    # Update
    graph.update_state(
        config=past_config,
        values={"crew": [66, 77], "v": "BAD GUY"}
    )
    print("\n>> after update")
    print(graph.get_state(session(2)))

    # Resume
    print("\n>> resume")
    r = graph.invoke(None, config=session(2))
    print(f"Result: {r}")

    print("\n>> history (notice the metadata.step)")
    for h in graph.get_state_history(session(2)):
        print(h)


if __name__ == '__main__':
    main()
