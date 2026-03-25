"""Demonstrates dangerous eval() and exec() usage with user input.

Vulnerabilities:
- B307 (eval): CWE-78 - OS Command Injection
- B102 (exec_used): CWE-78 - OS Command Injection
"""

import sys


def calculate_expression(user_input: str) -> float:
    """Evaluate a user-provided mathematical expression."""
    # B307: eval() with user-controlled input allows arbitrary code execution
    result = eval(user_input)
    return float(result)


def run_user_code(code_string: str) -> None:
    """Execute user-provided Python code for a plugin system."""
    # B102: exec() with user-controlled input allows arbitrary code execution
    exec(code_string)


def dynamic_import(module_name: str) -> object:
    """Dynamically import a module based on user request."""
    # B307: eval() used for dynamic import — use importlib.import_module() instead
    module = eval(f"__import__('{module_name}')")
    return module


if __name__ == "__main__":
    user_expr = sys.argv[1] if len(sys.argv) > 1 else "2 + 2"
    print(f"Result: {calculate_expression(user_expr)}")
    run_user_code("print('Hello from user code')")
