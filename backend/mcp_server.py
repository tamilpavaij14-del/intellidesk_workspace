import ast
import operator

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("IntelliDesk Tools")
MAX_EXPRESSION_LENGTH = 100
MAX_EXPONENT = 100

_ALLOWED_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY = {ast.USub: operator.neg, ast.UAdd: operator.pos}


def _safe_eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINARY:
        left, right = _safe_eval(node.left), _safe_eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise ValueError("Exponent too large")
        return _ALLOWED_BINARY[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression")


@mcp.tool()
def calculator(expression: str) -> float:
	"""Evaluate a basic arithmetic expression such as '840 * 15 / 100'.
    Supports + - * / ** and parentheses. Use this for any maths instead of guessing."""
	if len(expression) > MAX_EXPRESSION_LENGTH:
		raise ValueError("Expression too long")
	tree = ast.parse(expression, mode="eval")
	return float(_safe_eval(tree.body)) 

@mcp.tool()
def web_search(query: str) -> str:
	"""Search the web for current information or facts about the outside world.
	Do NOT use this for questions about the user's own uploaded documents."""
	from ddgs import DDGS
	with DDGS() as ddgs:
		results = list(ddgs.text(query, max_results=3))
	return "\n\n".join(f"{r['title']}: {r['body']}" for r in results)
