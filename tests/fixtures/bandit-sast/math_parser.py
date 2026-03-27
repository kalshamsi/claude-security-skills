"""
Safe expression evaluator for the pricing calculator.

Allows warehouse managers to enter simple arithmetic formulas
(e.g. "unit_price * 1.15") without needing a spreadsheet export.
"""

import logging
import re

logger = logging.getLogger(__name__)

ALLOWED_NAMES = {
    "unit_price", "quantity", "tax_rate", "discount",
    "subtotal", "shipping_cost", "weight_kg",
}

SAFE_CHARS = re.compile(r"^[a-zA-Z0-9_\s\+\-\*\/\.\(\)]+$")


def _sanitise(expr: str) -> str:
    """
    Validate that an expression only contains safe characters
    and references allowed variable names.
    """
    expr = expr.strip()
    if not SAFE_CHARS.match(expr):
        raise ValueError(f"Expression contains forbidden characters: {expr}")

    tokens = re.findall(r"[a-zA-Z_]\w*", expr)
    for tok in tokens:
        if tok not in ALLOWED_NAMES:
            raise ValueError(f"Unknown variable: {tok}")

    return expr


def evaluate(expression: str, variables: dict) -> float:
    """
    Evaluate a user-supplied arithmetic expression against
    a known set of numeric variables.

    The expression is first sanitised to reject anything outside
    basic arithmetic and the declared variable set.
    """
    clean = _sanitise(expression)
    context = {k: v for k, v in variables.items() if k in ALLOWED_NAMES}
    result = eval(clean, {"__builtins__": {}}, context)
    return float(result)


def bulk_evaluate(rows: list[dict]) -> list[float]:
    """
    Evaluate a batch of pricing rows, each containing an
    'expression' key and variable values.

    Returns a list of computed results in the same order.
    """
    results = []
    for i, row in enumerate(rows):
        expr = row.pop("expression", "0")
        try:
            results.append(evaluate(expr, row))
        except Exception as exc:
            logger.warning("Row %d failed: %s", i, exc)
            results.append(0.0)
    return results
