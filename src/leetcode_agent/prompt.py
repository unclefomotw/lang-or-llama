import re
from typing import Optional


MAIN_CODE_GEN_SYSTEM_PROMPT = """\
You are an excellent python programmer that writes python to solve coding competition problems.
You will be given a problem description, input / output examples, and the interface of the function that will follow.
Your job is to complete the implementation of the interface to solve the problem.
You implement the interface and only the interface.
Avoid writing code that tests your implementation.

The output protocol:
While you can output your thoughts, you should enclose your codes with "===code-start===" and "===code-end===",
so that I can understand which part is your code and I can grep to execute.  Here's an illustration:

<your thoughts>

===code-start===
# The python code of your solution goes here
===code-end===

<your conclusion if any>
"""

TEST_CODE_GEN_SYSTEM_PROMPT = """\
You are an excellent QA that creates testing examples for a python coding problem.
You will be given a problem description, input / output examples,
and the interface of the function that a student attempts to solve the problem.

Your job is write a code snippet that executes the student's function with more input examples.

The code snippet must use `assert` to test whether a case is failed or not.
You only output the testing code without implementing the solution.

The output protocol: 
While you can output your thoughts, you should enclose your testing code with "===test-start===" and "===test-end===",
so that I can understand which part is your code and I can grep to execute.  Here's an illustration:

<your thoughts>

===test-start===
# The python code that tests the student's code goes here
===test-end===

<your conclusion if any>
"""

_problem_description = """\
Problem description:
```
{problem_description}
```

Input/output examples:
```
{example_description}
```

The interface for you to implement:
```
{solution_interface}
```
"""

MAIN_CODE_GEN_USER_PROMPT = f"""\
Generate python code to solve the following problem

{_problem_description}
"""

TEST_CODE_GEN_USER_PROMPT = f"""\
Generate python code for testing purpose

{_problem_description}
"""

TEST_CODE_VALIDATION_PROMPT = """\
Given a coding problem:
```
{problem_description}
```

You mission is to validate this testing code from QA.  Check whether this code is reasonable or not:
```
{test_code}
```

You can output your reasoning and thoughts concisely.  Output the result in the last line in this fixed format:
* `Validation result: yes` , if it's reasonable.
* `Validation result: no` , if it's not reasonable.
"""

TEST_CODE_VALIDATION_WITH_ERRORS_PROMPT = """\
Given a coding problem:
```
{problem_description}
```

and a code that attempts to solve the problem:
```
{main_code}
```

When executing the main code together with this testing code from QA, an error occurred
```
# QA code
{test_code}
```
Error:
```
{ai_test_result_stderr}
```

You mission is to validate the testing code from QA.  Check whether the QA code itself is reasonable or not

You can output your reasoning and thoughts concisely.  Output the result in the last line in this fixed format:
* `Validation result: yes` , if it's reasonable.
* `Validation result: no` , if it's not reasonable.
"""


def extract_code(content: str, head_sep: str, tail_sep: str) -> Optional[str]:
    """Get the string between two separators within the content."""

    escaped_head_sep = re.escape(head_sep)
    escaped_tail_sep = re.escape(tail_sep)
    pattern = f'{escaped_head_sep}(.*?){escaped_tail_sep}'

    m = re.search(pattern, content, re.DOTALL)
    if m:
        return m.group(1)
    else:
        return None
