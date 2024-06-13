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

    for s in graph.stream(
            input={"crew": []},
            config=session(1),
            stream_mode="values"
    ):
        print(s)
        print(graph.get_state(session(1)))
    print(graph.get_state(session(1)))
    print("\n")

    # Find the config of interests
    for h in graph.get_state_history(session(1)):
        if h.next == ("n2", ):
            past_config = h.config
            break

    # NOTE THAT it contains thread_ts, combination of thread id and the step no.
    print("\n>> Get the past config I want to start from")
    print(past_config, end="\n\n")

    # Rewind: resume from the past
    for s in graph.stream(
            input=None,
            config=past_config,
            stream_mode="values"
    ):
        print(s)

    print("\n>> history (notice the metadata.step)")
    for h in graph.get_state_history(session(1)):
        print(h)


if __name__ == '__main__':
    main()
