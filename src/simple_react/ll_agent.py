# Derived from https://docs.llamaindex.ai/en/stable/examples/agent/react_agent/
#
# By default ReActAgent, which is a AgentRunner, creates a ReActAgentWorker as its step engine and execute
#
# The system prompt is at llama_index/core/agent/react/templates/system_header_template.md
# and constructed via llama_index.core.agent.react.ReActChatFormatter
# and can be customized via agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
# where react_system_prompt = PromptTemplate(react_system_header_str)
# (See https://docs.llamaindex.ai/en/stable/examples/agent/react_agent/#customizing-the-prompt)
#
# In this example, the tools are not sent to the OpenAI (so it's LLM agnostic).
# Instead, it uses (system) prompt engineering, and hope the LLM outputs in its pre-defined format.
# The default output parser is llama_index.core.agent.react.ReActOutputParser
#
# Both react_chat_formatter and output_parser can be passed when creating ReActAgent.
#
# This example does NOT leverage the "tools" feature natively supported by OpenAI.
# I will make another example if I figure how to leverage it.
#
# BTW the result of this example is not perfect and can lead to error due to inconsistent
# in-context reasoning from the LLM.
#

import os

# LangTrace: Must precede any llm module imports
from langtrace_python_sdk import langtrace

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

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
