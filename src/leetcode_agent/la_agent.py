import pprint
from typing import TypedDict

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel

from src.leetcode_agent.problem import LeetCodeProblem, PROBLEM_1
from src.leetcode_agent.prompt import (
    TEST_CODE_GEN_USER_PROMPT,
    TEST_CODE_GEN_SYSTEM_PROMPT,
    TEST_CODE_VALIDATION_PROMPT,
    TEST_CODE_VALIDATION_WITH_ERRORS_PROMPT,
    MAIN_CODE_GEN_SYSTEM_PROMPT,
    MAIN_CODE_GEN_USER_PROMPT,
    extract_code
)


class CodeExecutionResult(BaseModel):
    stdout: str
    stderr: str
    return_code: str


class AgentState(TypedDict):
    problem: LeetCodeProblem
    main_code: str
    test_code: str
    is_main_code_good: bool
    is_test_code_good: bool
    comment_on_test_code: str
    example_test_result: CodeExecutionResult
    ai_test_result: CodeExecutionResult
    human_comment_on_main_code: str


def get_codegen_workflow() -> StateGraph:
    _llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.001)
    main_coding_llm = _llm
    test_coding_llm = _llm
    test_validation_llm = _llm

    def node_generate_test_code(state: AgentState):
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
            return {"test_code": None}

        code = extract_code(content, "===test-start===", "===test-end===")
        return {"test_code": code}

    def node_validate_test_code(state: AgentState):
        test_code = state["test_code"]
        if not test_code:
            return {"is_test_code_good": False}

        ai_test_result = state["ai_test_result"]
        if ai_test_result and ai_test_result.stderr:
            # Main code is generated and run, but failed to pass the test code
            messages = [
                HumanMessage(content=TEST_CODE_VALIDATION_WITH_ERRORS_PROMPT.format(
                    problem_description=state["problem"].problem_description,
                    main_code=state["main_code"],
                    test_code=state["test_code"],
                    ai_test_result_stderr=ai_test_result.stderr
                ))
            ]
            content = _llm.invoke(messages).content
            if content.find("Validation result: yes") != -1:
                return {"is_test_code_good": True}
            elif content.find("Validation result: no") != -1:
                return {"is_test_code_good": False}
            else:
                # TODO: logging or verbose; say this is unexpected but counted as passed
                print(content)
                return {"is_test_code_good": True}
        else:
            # No main code yet; just asking for opinions about the test code
            messages = [
                HumanMessage(content=TEST_CODE_VALIDATION_PROMPT.format(
                    problem_description=state["problem"].problem_description,
                    test_code=state["test_code"]
                ))
            ]
            content = test_validation_llm.invoke(messages).content
            if content.find("Validation result: yes") != -1:
                return {"is_test_code_good": True}
            elif content.find("Validation result: no") != -1:
                return {"is_test_code_good": False}
            else:
                # TODO: logging or verbose; say this is unexpected but counted as passed
                print(content)
                return {"is_test_code_good": True}

    def node_generate_main_code(state: AgentState):
        problem = state["problem"]
        messages = [
            SystemMessage(content=MAIN_CODE_GEN_SYSTEM_PROMPT),
            HumanMessage(content=MAIN_CODE_GEN_USER_PROMPT.format(
                problem_description=problem.problem_description,
                example_description=problem.example_description,
                solution_interface=problem.solution_interface
            ))
        ]
        content = main_coding_llm.invoke(messages).content

        if not content:
            return {"main_code": None}

        code = extract_code(content, "===code-start===", "===code-end===")
        return {"main_code": code}

    def node_test_main_with_examples():
        pass

    def node_test_main_with_test_code():
        pass

    workflow = StateGraph(AgentState)

    workflow.add_node("generate_test_code", node_generate_test_code)
    workflow.add_node("validate_test_code", node_validate_test_code)
    workflow.add_node("generate_main_code", node_generate_main_code)
    workflow.set_entry_point("generate_test_code")

    workflow.add_edge("generate_test_code", "validate_test_code")
    workflow.add_edge("validate_test_code", "generate_main_code")  # TODO
    workflow.add_edge("generate_main_code", END)  # TODO

    return workflow


def main():
    graph = get_codegen_workflow().compile()
    for s in graph.stream({"problem": PROBLEM_1}):
        pprint.pprint(s, width=120)


if __name__ == '__main__':
    main()
