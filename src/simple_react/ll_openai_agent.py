# Copied from https://docs.llamaindex.ai/en/stable/examples/agent/openai_agent/
#
# In this example, LlamaIndex DOES leverage the tool use supported by OpenAI API,
# despite there's almost no difference is using the agent (see `ll_agent.py`).
# On the other hand, the LLM calls do not contain a system prompt by default
# probably because it's not necessary when OpenAI API supports tool use natively
#
# BTW, it seems langtrace-python-sdk 2.0.13 cannot handle ChatCompletionMessageToolCall
# used by LlamaIndex internally when using openai agent, so I will just turn it off for now
#

import logging
import sys

# LangTrace: Must precede any llm module imports
# from langtrace_python_sdk import langtrace

from llama_index.agent.openai import OpenAIAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

# langtrace.init(api_key=os.getenv("LANGTRACE_API_KEY"))
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


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
    agent = OpenAIAgent.from_tools(
        [multiply_tool, add_tool],
        llm=llm,
        verbose=True
    )

    question = "What is 20+(2*4)? Calculate step by step"
    print(f"\n====== conversation pass 1: {question} ======")
    response = agent.chat(question)
    print(response)

    question_2 = "Add 3 onto the last question, what is it? Calculate step by step"
    print(f"\n====== conversation pass 2: {question_2} ======")
    response_2 = agent.chat(question_2)
    print(response_2)

    question_3 = "Assuming `x` is the answer of the last question, what is 2*(x+100)? Calculate step by step"
    print(f"\n====== conversation pass 3: {question_3} ======")
    response_3 = agent.chat(question_3)
    print(response_3)


if __name__ == '__main__':
    main()
