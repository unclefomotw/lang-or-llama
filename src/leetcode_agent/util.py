import pprint
import re
from typing import Optional

from colorama import Fore, Style


def extract_code(content: str, head_sep: str, tail_sep: str) -> Optional[str]:
    """Get source code between two separators within the content."""

    escaped_head_sep = re.escape(head_sep)
    escaped_tail_sep = re.escape(tail_sep)
    pattern = f'{escaped_head_sep}(.*?){escaped_tail_sep}'

    m = re.search(pattern, content, re.DOTALL)
    if not m:
        return None

    potential_code = m.group(1)
    stripped_3backslashes_code = re.sub(r"```(.*)", "", potential_code)
    return stripped_3backslashes_code


def combine_test_with_code(main_code: str, test_code: str) -> str:
    """Merge code followed by test, so test can be executed."""
    return f"# Your solution:\n{main_code}\n\n# QA test:\n{test_code}"


def print_node_output(s):
    """Print state from the graph node in less appearing way"""
    print(Style.DIM, end="")
    pprint.pprint(s, width=120)
    print(Style.RESET_ALL, end="")


def multiline_input(prompt: str) -> str:
    """Let the user input multiple lines, end by EOF (ctrl-d)."""
    print(f"{prompt} [double enter to end]")

    lines = []
    num_blank_lines = 0
    while True:
        line = input(">>> ")
        if line == "":
            num_blank_lines += 1
        else:
            num_blank_lines = 0

        if num_blank_lines == 2:
            break
        lines.append(line)

    return "\n".join(lines)
