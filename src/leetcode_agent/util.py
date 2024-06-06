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
    return f"# Your solution:\n{main_code}\n\n# QA test:\n{test_code}"


def print_node_output(s):
    print(Style.DIM, end="")
    pprint.pprint(s, width=120)
    print(Style.RESET_ALL, end="")
