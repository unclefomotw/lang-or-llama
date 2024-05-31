# Simply messing around LangGraph's graph building

import time
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, END


class MyState(TypedDict):
    foo: Annotated[str, lambda x, y: f"{x}+{y}"]


def fn_1(state: MyState) -> None:
    """Function No. 1"""
    print(f"====== FUNC 1: get {state}")


def fn_2(state: MyState) -> MyState:
    """Function No. 2"""
    time.sleep(10)
    print(f"====== FUNC 2: get {state}")
    return {"foo": "fn2"}


def fn_3(state: MyState) -> MyState:
    """Function No. 3"""
    # XXX: try to execute before fn_2, yes... but not what you expect
    time.sleep(6)
    print(f"====== FUNC 3: get {state}")
    return {"foo": "fn3"}


def fn_4(state: MyState) -> MyState:
    """Function No. 4"""
    print(f"====== FUNC 4: get {state}")
    print(id(state))
    # return some unexpected key
    return {"wtf": "fn4"}


def fn_5(state: MyState) -> MyState:
    """Function No. 4"""
    print(f"====== FUNC 5: get {state}")
    print(id(state))
    # XXX: not what you expect
    state["foo"] = "hehe"
    return {"foo": "fn5"}


def main():
    graph = StateGraph(state_schema=MyState)

    graph.add_node("n1", fn_1)
    graph.add_node("n2", fn_2)
    graph.add_node("n3", fn_3)
    graph.add_node("n4", fn_4)
    graph.add_node("n5", fn_5)

    graph.set_entry_point("n1")

    graph.add_edge("n1", "n2")
    graph.add_edge("n1", "n3")
    graph.add_edge("n2", "n4")
    graph.add_edge("n3", "n4")
    graph.add_edge("n4", "n5")
    graph.add_edge("n5", END)

    flow = graph.compile()
    r = flow.invoke({"foo": "bar"})

    print(r)


if __name__ == '__main__':
    main()
