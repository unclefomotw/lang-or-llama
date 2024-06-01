import os

# LangTrace: Must precede any llm module imports
from langtrace_python_sdk import langtrace

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

from src.simple_react.ll_react_custom_prompt import react_system_prompt

langtrace.init(api_key=os.getenv("LANGTRACE_API_KEY"))


def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    print(f"====== FUNC: MULT {a},{b}")
    return a * b


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    print(f"====== FUNC: ADD {a},{b}")
    return a + b


multiply_tool = FunctionTool.from_defaults(fn=multiply)
add_tool = FunctionTool.from_defaults(fn=add)


def main():
    llm = OpenAI(model="gpt-3.5-turbo", temperature=0.001)
    agent = ReActAgent.from_tools(
        [multiply_tool, add_tool],
        llm=llm,
        verbose=True
    )

    agent.update_prompts(
        {"agent_worker:system_prompt": react_system_prompt}
    )

    question = "In 2023, John got 100 dollars each month in the first 5 months, " \
               "and got 150 dollars in the next 7 months. "\
               "How much money did John get in 2023?"
    print(f"\n====== conversation pass 1: {question} ======")
    response = agent.chat(question)
    print(response)

    # Result (AI messages are Thought and Action; Humna messages are Observation)
    # ====== conversation pass 1: In 2023, John got 100 dollars each month in the first 5 months, and got 150 dollars in the next 7 months. How much money did John get in 2023? ======
    # Thought: To calculate the total amount of money John got in 2023, I need to find the sum of the money he received each month. I can break this down into two parts: calculating the total money received in the first 5 months and the total money received in the next 7 months.
    # Action: multiply
    # Action Input: {'a': 100, 'b': 5}
    # ====== FUNC: MULT 100,5
    # Observation: 500
    # Thought: The total amount of money John received in the first 5 months is $500. Now, I need to calculate the total money he received in the next 7 months.
    # Action: multiply
    # Action Input: {'a': 150, 'b': 7}
    # ====== FUNC: MULT 150,7
    # Observation: 1050
    # Thought: The total amount of money John received in the next 7 months is $1050. Now, I need to find the sum of the money he received in the entire year.
    # Action: add
    # Action Input: {'a': 500, 'b': 1050}
    # ====== FUNC: ADD 500,1050
    # Observation: 1550
    # Thought: I can answer without using any more tools. I'll use the user's language to answer
    # Answer: John got a total of 1550 dollars in 2023.
    # John got a total of 1550 dollars in 2023.


if __name__ == '__main__':
    main()
