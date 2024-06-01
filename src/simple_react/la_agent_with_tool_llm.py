# Derived from multiple official docs
#
# The graph is about going back and forth between "agent" node and "tools" node:
# "tools" always goes to "agent", and depending on whether the last assistant message is
# to use tools or not, it can go to "tools" or END
#
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint import MemorySaver
from langgraph.prebuilt import create_react_agent


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    print(f"====== FUNC: MULT {a},{b}")
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    print(f"====== FUNC: ADD {a},{b}")
    return a + b


def main():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.001)
    graph = create_react_agent(
        llm,
        tools=[multiply, add],
        checkpointer=MemorySaver()
    )
    # "configurable" and "thread_id" are magic keys in MemorySaver()
    memory_config = {"configurable": {"thread_id": "user-24601-conv-1337"}}

    question = "What is 20+(2*4)? Calculate step by step"
    print(f"\n====== conversation pass 1: {question} ======")
    response = graph.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=memory_config
    )
    for m in response["messages"]:
        print(m)

    question_2 = "Add 3 onto the last question, what is it? Calculate step by step"
    print(f"\n====== conversation pass 2: {question_2} ======")
    response_2 = graph.invoke(
        {"messages": [HumanMessage(content=question_2)]},
        config=memory_config
    )
    for m in response_2["messages"]:
        print(m)

    question_3 = "Assuming `x` is the answer of the last question, what is 2*(x+100)? Calculate step by step"
    print(f"\n====== conversation pass 3: {question_3} ======")
    response_3 = graph.invoke(
        {"messages": [HumanMessage(content=question_3)]},
        config=memory_config
    )
    for m in response_3["messages"]:
        print(m)

    # Langsmith trace: https://smith.langchain.com/public/5273cbc6-d63b-4f0f-b67e-d955b9dd6c35/r


if __name__ == '__main__':
    main()
