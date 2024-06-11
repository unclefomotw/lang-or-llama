import time
from typing import Annotated, TypedDict

from langgraph.checkpoint import MemorySaver
from langgraph.graph import StateGraph, END


class MyState(TypedDict):
    foo: Annotated[str, lambda x, y: f"{x}+{y}"]


def start(state: MyState):
    print(f"====== start: get {state} " + time.strftime("%H:%M:%S", time.localtime()))
    return {"foo": "s"}


def left_1(state: MyState):
    # time.sleep(3)
    print(f"====== L1: get {state} " + time.strftime("%H:%M:%S", time.localtime()))
    return {"foo": "L1"}


def right_1(state: MyState):
    print(f"====== R1: get {state} " + time.strftime("%H:%M:%S", time.localtime()))
    return {"foo": "R1"}


def right_2(state: MyState):
    print(f"====== R2: get {state} " + time.strftime("%H:%M:%S", time.localtime()))
    return {"foo": "R2"}


def right_3(state: MyState):
    print(f"====== R3: get {state} " + time.strftime("%H:%M:%S", time.localtime()))
    return {"foo": "R3"}


def merge(state: MyState) -> MyState:
    print(f"====== merge: get {state} " + time.strftime("%H:%M:%S", time.localtime()))
    return {"foo": "m"}


def main():
    graph = StateGraph(state_schema=MyState)

    graph.add_node(start)
    graph.add_node(left_1)
    graph.add_node(right_1)  # alt: try to add it earlier
    graph.add_node(right_2)
    graph.add_node(right_3)
    graph.add_node(merge)  # alt: try to add it earlier
    graph.set_entry_point("start")

    graph.add_edge("start", "left_1")
    graph.add_edge("start", "right_1")
    graph.add_edge("right_1", "right_2")
    graph.add_edge("right_2", "right_3")
    graph.add_edge(["left_1", "right_3"], "merge")
    # graph.add_edge("merge", END)
    graph.add_edge("merge", "right_2")

    # "merge" is not triggered second time since
    # there won't be a new version from left_1

    flow = graph.compile(checkpointer=MemorySaver())

    r = flow.invoke({"foo": ""}, config={"configurable": {"thread_id": "1"}})
    print(r["foo"])
    print("~~~~~~~~~~~~~~~~")

    config = {"configurable": {"thread_id": "1337"}}
    i = 1
    for s in flow.stream({"foo": ""}, config=config):
        print(f"---------- Stream step {i}")
        print(flow.get_state(config))
        print(s)
        print()
        i += 1


if __name__ == '__main__':
    main()
