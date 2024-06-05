import pprint
from enum import Enum
from typing import TypedDict, Annotated, Sequence

import requests
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.leetcode_agent.problem import LeetCodeProblem, PROBLEM_1
from src.leetcode_agent.prompt import (
    MAIN_CODE_GEN_SYSTEM_PROMPT,
    MAIN_CODE_GEN_USER_PROMPT,
    REGEN_BY_COMMENT_USER_PROMPT,
    REGEN_BY_ERROR_USER_PROMPT,
    TEST_CODE_GEN_SYSTEM_PROMPT,
    TEST_CODE_GEN_USER_PROMPT,
    TEST_CODE_VALIDATION_PROMPT,
    TEST_CODE_VALIDATION_WITH_ERRORS_PROMPT,
)
from src.leetcode_agent.util import extract_code, combine_test_with_code


class CodeExecutionResult(BaseModel):
    code: str
    stdout: str
    stderr: str
    has_error: bool


def execute_code(code: str) -> CodeExecutionResult:
    """Runs python code in my sandbox.  See README."""
    r = requests.post("http://127.0.0.1:8000/execute",
                      json={"code": code})
    if r.status_code == 200:
        r_json = r.json()
        return CodeExecutionResult(
            code=code,
            stdout=r_json.get("stdout"),
            stderr=r_json.get("stderr"),
            has_error=(r_json.get("returncode") != 0)
        )
    else:
        return CodeExecutionResult(
            code=code,
            stdout="",
            stderr=f"({r.json().get("detail")})",
            has_error=True
        )


class TestType(Enum):
    AI = 1
    EXAMPLES = 2


class AgentState(TypedDict):
    main_coding_llm_messages: Annotated[list[BaseMessage], add_messages]
    problem: LeetCodeProblem
    main_code: str
    ai_test_code: str
    is_main_code_good: bool
    is_ai_test_code_good: bool
    last_test_result: CodeExecutionResult
    last_test_type: TestType
    human_comment_on_main_code: str


def get_codegen_workflow() -> StateGraph:
    _llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.001)

    test_coding_llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1)
    test_validation_llm = _llm

    _system_message = SystemMessage(content=MAIN_CODE_GEN_SYSTEM_PROMPT)
    main_coding_llm = (lambda messages: [_system_message] + messages) | _llm

    def node_generate_ai_test_code(state: AgentState):
        problem = state["problem"]
        messages = [
            SystemMessage(content=TEST_CODE_GEN_SYSTEM_PROMPT),
            HumanMessage(content=TEST_CODE_GEN_USER_PROMPT.format(
                problem_description=problem.problem_description,
                example_description=problem.example_description,
                solution_interface=problem.solution_interface
            ))
        ]
        content = test_coding_llm.invoke(messages).content

        if not content:
            return {"ai_test_code": None}

        code = extract_code(content, "===test-start===", "===test-end===")
        return {
            "ai_test_code": code,
            "last_test_result": None,  # reset due to potential test regeneration
        }

    def node_validate_test_code(state: AgentState):
        test_code = state["ai_test_code"]
        if not test_code:
            return {"is_ai_test_code_good": False}

        last_test_result = state["last_test_result"]
        if last_test_result and last_test_result.has_error and state["last_test_type"] == TestType.AI:
            # Main code is generated and run, but failed to pass the test code
            messages = [
                HumanMessage(content=TEST_CODE_VALIDATION_WITH_ERRORS_PROMPT.format(
                    problem_description=state["problem"].problem_description,
                    code=last_test_result.code,
                    ai_test_result_stderr=last_test_result.stderr
                ))
            ]
            content = _llm.invoke(messages).content
            if content.find("Validation result: yes") != -1:
                return {"is_ai_test_code_good": True}
            elif content.find("Validation result: no") != -1:
                return {"is_ai_test_code_good": False}
            else:
                # TODO: logging or verbose; say this is unexpected but counted as passed
                print(content)
                return {"is_ai_test_code_good": True}
        else:
            # No main code yet; just asking for opinions about the test code
            messages = [
                HumanMessage(content=TEST_CODE_VALIDATION_PROMPT.format(
                    problem_description=state["problem"].problem_description,
                    test_code=state["ai_test_code"]
                ))
            ]
            content = test_validation_llm.invoke(messages).content
            if content.find("Validation result: yes") != -1:
                return {"is_ai_test_code_good": True}
            elif content.find("Validation result: no") != -1:
                return {"is_ai_test_code_good": False}
            else:
                # TODO: logging or verbose; say this is unexpected but counted as passed
                print(content)
                return {"is_ai_test_code_good": True}

    def node_generate_main_code(state: AgentState):
        problem = state["problem"]

        if (not state["main_code"]) or (not state["last_test_result"]):
            # No reflection since no main code is generated, or no (valid) tests were performed
            message = HumanMessage(
                content=MAIN_CODE_GEN_USER_PROMPT.format(
                    problem_description=problem.problem_description,
                    example_description=problem.example_description,
                    solution_interface=problem.solution_interface
                ))
            response = main_coding_llm.invoke([message])
        else:
            # Re-generate main code; reflect the previous error
            history_messages = state["main_coding_llm_messages"]
            last_test_result = state["last_test_result"]
            human_comment = state["human_comment_on_main_code"] or ""
            if last_test_result.has_error:
                message = HumanMessage(
                    content=REGEN_BY_ERROR_USER_PROMPT.format(
                        code=last_test_result.code,
                        error=last_test_result.stderr,
                        human_comment=human_comment
                    ))
            else:
                message = HumanMessage(
                    content=REGEN_BY_COMMENT_USER_PROMPT.format(
                        human_comment=human_comment
                    ))
            response = main_coding_llm.invoke(history_messages + [message])

        content = response.content

        if not content:
            code = None
        else:
            code = extract_code(content, "===code-start===", "===code-end===")
        return {
            "main_coding_llm_messages": [message, response],
            "main_code": code
        }

    def node_test_main_with_examples(state: AgentState):
        main_code = state["main_code"]
        if not main_code:
            return {"is_main_code_good": False}

        example_test_code = state["problem"].example_test_code
        code_result = execute_code(
            combine_test_with_code(main_code, example_test_code)
        )
        return {
            "is_main_code_good": not code_result.has_error,
            "last_test_result": code_result,
            "last_test_type": TestType.EXAMPLES
        }

    def node_test_main_with_ai_tests(state: AgentState):
        main_code = state["main_code"]
        if not main_code:
            return {"is_main_code_good": False}

        code_result = execute_code(
            combine_test_with_code(main_code, state["ai_test_code"])
        )
        return {
            "is_main_code_good": not code_result.has_error,
            "last_test_result": code_result,
            "last_test_type": TestType.AI
        }

    def to_regenerate_ai_test_code(state: AgentState) -> str:
        # TODO: limit the number of generations
        if state.get("is_ai_test_code_good", False):
            return "no"
        else:
            return "yes"

    def to_regenerate_main_code(state: AgentState) -> str:
        # TODO: limit the number of generations
        if state.get("is_main_code_good", False):
            return "no"
        else:
            return "yes"

    workflow = StateGraph(AgentState)

    workflow.add_node("generate_ai_test_code", node_generate_ai_test_code)
    workflow.add_node("validate_test_code", node_validate_test_code)
    workflow.add_node("generate_main_code", node_generate_main_code)
    workflow.add_node("test_with_examples", node_test_main_with_examples)
    workflow.add_node("test_with_ai", node_test_main_with_ai_tests)

    workflow.set_entry_point("generate_ai_test_code")

    workflow.add_edge("generate_ai_test_code", "validate_test_code")
    workflow.add_conditional_edges(
        source="validate_test_code",
        path=to_regenerate_ai_test_code,
        path_map={
            "yes": "generate_ai_test_code",
            "no": "generate_main_code"
        }
    )
    workflow.add_edge("generate_main_code", "test_with_examples")
    workflow.add_conditional_edges(
        source="test_with_examples",
        path=to_regenerate_main_code,
        path_map={
            "yes": "generate_main_code",
            "no": "test_with_ai"
        }
    )
    workflow.add_conditional_edges(
        source="test_with_ai",
        path=to_regenerate_main_code,
        path_map={
            "yes": "validate_test_code",  # can be a mistake in AI test code
            "no": END  # TODO: human-in-the-loop / human node?
        }
    )

    return workflow


def main():
    config = {"configurable": {"thread_id": "user-24601-conv-1337"}}

    graph = get_codegen_workflow().compile(
        checkpointer=MemorySaver()
    )

    for s in graph.stream({"problem": PROBLEM_1}, config):
        pprint.pprint(s, width=120)

    print("=== AI GENERATED SOLUTION ===")
    print(graph.get_state(config).values["main_code"])


if __name__ == '__main__':
    main()
