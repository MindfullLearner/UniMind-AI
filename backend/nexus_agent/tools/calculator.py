
import ast
import operator

from langchain_core.tools import tool


# Only these mathematical operations are allowed.
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_calculate(expression: str):
    """Parse and calculate an expression using allowed operations only."""

    if not expression or len(expression) > 100:
        raise ValueError("Expression is empty or too long.")

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            value = evaluate(node.operand)
            return OPERATORS[type(node.op)](value)

        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)

            # Prevent excessively large exponent calculations.
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponent is too large.")

            result = OPERATORS[type(node.op)](left, right)

            if isinstance(result, (int, float)) and abs(result) > 1e100:
                raise ValueError("Result is too large.")

            return result

        raise ValueError("Unsupported mathematical expression.")

    tree = ast.parse(expression, mode="eval")
    return evaluate(tree.body)


@tool
def calculator(expression: str) -> str:
    """Calculate a basic mathematical expression safely.

    Use this tool for arithmetic such as addition, subtraction,
    multiplication, division, powers, and remainders.
    """

    try:
        result = safe_calculate(expression)
        return f"Result: {result}"
    except (ValueError, TypeError, ZeroDivisionError, OverflowError, SyntaxError) as error:
        return f"Calculator error: {error}"
