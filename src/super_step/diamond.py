import time
from typing import Annotated, TypedDict

from langgraph.checkpoint import MemorySaver
from langgraph.graph import StateGraph, END


class MyState(TypedDict):
    foo: Annotated[str, lambda x, y: f"{x}+{y}"]


def fn_1(state: MyState):
    print(f"====== FUNC 1: get {state} " + time.strftime("%H:%M:%S", time.localtime()))
    return {"foo": "1"}


def fn_2(state: MyState):
    time.sleep(10)
    print(f"====== FUNC 2: get {state} " + time.strftime("%H:%M:%S", time.localtime()))
    return {"foo": "2"}


def fn_3(state: MyState):
    # XXX: try to execute & return before fn_2, but...
    time.sleep(6)
    print(f"====== FUNC 3: get {state} " + time.strftime("%H:%M:%S", time.localtime()))
    return {"foo": "3"}


def fn_4(state: MyState) -> MyState:
    print(f"====== FUNC 4: get {state} " + time.strftime("%H:%M:%S", time.localtime()))
    return {"foo": "4"}


def main():
    graph = StateGraph(state_schema=MyState)

    graph.add_node("n1", fn_1)
    graph.add_node("n2", fn_2)
    graph.add_node("n3", fn_3)  # alt: try to add it earlier
    graph.add_node("n4", fn_4)
    graph.set_entry_point("n1")

    graph.add_edge("n1", "n2")
    graph.add_edge("n1", "n3")
    graph.add_edge("n2", "n4")
    graph.add_edge("n3", "n4")
    graph.add_edge("n4", END)

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
