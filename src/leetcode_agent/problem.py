from pathlib import Path
from typing import Union

from pydantic import BaseModel


class LeetCodeProblem(BaseModel):
    problem_description: str
    example_description: str
    solution_interface: str
    example_test_code: str


class FileSizeTooLargeError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def read_problem(directory: Union[str, Path]) -> LeetCodeProblem:
    def _read_text(path: Path):
        c = path.read_text()
        if len(c) > 10 * 1024:
            raise FileSizeTooLargeError(f"File {path} is too large; the limit is 10 K")
        return c

    if isinstance(directory, str):
        directory = Path(directory)

    if not directory.is_dir():
        raise ValueError(f"`directory` must be a directory: {directory}")

    problem_description = _read_text(directory / "DESCRIPTION")
    example_description = _read_text(directory / "EXAMPLE")
    solution_interface = _read_text(directory / "INTERFACE")
    example_test_code = _read_text(directory / "TEST")

    return LeetCodeProblem(
        problem_description=problem_description,
        example_description=example_description,
        solution_interface=solution_interface,
        example_test_code=example_test_code
    )


_problem_1 = """\
Given a string `s`, find the length of the longest substring without repeating characters.
"""

_problem_1_examples = """\
Example 1:
Input: s = "abcabcbb"
Output: 3
Explanation: The answer is "abc", with the length of 3.

Example 2:
Input: s = "bbbbb"
Output: 1
Explanation: The answer is "b", with the length of 1.

Example 3:
Input: s = "pwwkew"
Output: 3
Explanation: The answer is "wke", with the length of 3.
Notice that the answer must be a substring, "pwke" is a subsequence and not a substring.
"""

_problem_1_interface = """\
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
"""

_problem_1_example_test = """\
assert Solution().lengthOfLongestSubstring("abcabcbb") == 3
assert Solution().lengthOfLongestSubstring("bbbbb") == 1
assert Solution().lengthOfLongestSubstring("pwwkew") == 3
"""

PROBLEM_1 = LeetCodeProblem(
    problem_description=_problem_1,
    example_description=_problem_1_examples,
    solution_interface=_problem_1_interface,
    example_test_code=_problem_1_example_test
)
