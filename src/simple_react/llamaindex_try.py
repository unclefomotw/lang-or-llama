# Simply messing around with LlamaIndex's agent classes
#
# `Task` has `extra_state`; each `TaskStep` has its `step_state`
# `TaskStepOutput` is made of `output`, `task_step`, `next_steps` and `is_last`
#
# One important thing which is not yet studied here is, whether/how to execute
# multi steps at once if they are independent (e.g. diamond shape graph)
#

from typing import Any

from llama_index.core.agent import AgentRunner
from llama_index.core.base.agent.types import BaseAgentWorker, Task, TaskStep, TaskStepOutput
from llama_index.core.chat_engine.types import AgentChatResponse


class MyAgentWorker(BaseAgentWorker):

    def initialize_step(self, task: Task, **kwargs: Any) -> TaskStep:
        task.extra_state["task_state_output"] = []

        return TaskStep(
            task_id=task.task_id,
            step_id="start-n1",
            input=task.input,
            step_state={"at": "n1"},
        )

    def run_step(self, step: TaskStep, task: Task, **kwargs: Any) -> TaskStepOutput:
        _is_last = False
        _at_node = step.step_state.get("at", "__unknown__")

        print(f"=== step_state: {_at_node} , step_id: {step.step_id} ===")
        print(f"task step input {step.input}")

        if _at_node == "n1":
            task.extra_state["task_state_output"].append("N1")
            _next_steps = [
                TaskStep(
                    task_id=task.task_id,
                    step_id="n1-n2",
                    input=step.input+"_fn1",
                    step_state={"at": "n2"}
                ),
                TaskStep(
                    task_id=task.task_id,
                    step_id="n1-n3",
                    input=step.input + "_fn1",
                    step_state={"at": "n3"}
                )
            ]
        elif _at_node == "n2":
            task.extra_state["task_state_output"].append("N2")
            _next_steps = [
                TaskStep(
                    task_id=task.task_id,
                    step_id="n2-n4",
                    input=step.input+"_fn2",
                    step_state={"at": "n4"}
                )
            ]
        elif _at_node == "n3":
            task.extra_state["task_state_output"].append("N3")
            _next_steps = [
                TaskStep(
                    task_id=task.task_id,
                    step_id="n3-n4",
                    input=step.input+"_fn3",
                    step_state={"at": "n4"}
                )
            ]
        else:
            task.extra_state["task_state_output"].append("WHAT")
            _next_steps = []
            # XXX: In the "diamond" shape graph:
            #      If the worker cannot access the runner, it does not know
            #      whether the step_queue ("todo list") is empty or not,
            #      unless the worker maintains its own in Task state (kind of violating the design?)
            #      or we design more subtle flags (e.g. #steps done in n4) in the Task state
            # XXX: In other words, you will see only 1 WHAT, and can't see the step "n3-n4"
            _is_last = True

        if _is_last:
            # agent.chat needs the output be of AgentChatResponse (or the Streaming one)
            _output = step.input + "~" + "-".join(task.extra_state["task_state_output"])
            _output = AgentChatResponse(response=_output)
            return TaskStepOutput(
                output=_output, task_step=step,
                next_steps=_next_steps, is_last=_is_last
            )
        else:
            return TaskStepOutput(
                output="???", task_step=step,
                next_steps=_next_steps, is_last=_is_last
            )

    def finalize_task(self, task: Task, **kwargs: Any) -> None:
        print("======= finalize_task =======")

    async def arun_step(self, step: TaskStep, task: Task, **kwargs: Any) -> TaskStepOutput:
        raise NotImplementedError

    def stream_step(self, step: TaskStep, task: Task, **kwargs: Any) -> TaskStepOutput:
        raise NotImplementedError

    async def astream_step(self, step: TaskStep, task: Task, **kwargs: Any) -> TaskStepOutput:
        raise NotImplementedError


def main():
    agent = AgentRunner(
        agent_worker=MyAgentWorker()
    )
    r = agent.chat("blah")
    print()
    print(type(r))
    print(r)


if __name__ == '__main__':
    main()