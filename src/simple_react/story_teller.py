from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


@tool
def get_protagonists() -> list[str]:
    """Returns the names of the protagonists in the novel."""
    return ['Bell', 'Iris']


@tool
def get_characteristics(person: str) -> str:
    """Returns the characteristics of the protagonist in the novel."""
    if person.lower() == 'bell':
        return "innocent"
    if person.lower() == 'iris':
        return "chaos"
    return "funny"


def main():
    system_prompt = "You are an great novelist who are interested in writing a short story."
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=1.2)
    graph = create_react_agent(
        llm,
        tools=[get_protagonists, get_characteristics],
        messages_modifier=system_prompt
    )
    response = graph.invoke(
        {"messages": [HumanMessage(
            content="Write a short story.  The plot is based on the characteristics of protagonists."
        )]},
    )
    for m in response["messages"]:
        print(type(m))
        print(m)
        print()


if __name__ == '__main__':
    main()
