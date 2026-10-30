import asyncio

import pytest
from fastmcp import Client

from mcp_server import mcp
from services.agent import run_agent


def _call_tool(name: str, args: dict):
	async def run():
		async with Client(mcp) as c:
			return await c.call_tool(name, args)
	return asyncio.run(run())


def test_calculator_computes():
	result = _call_tool("calculator", {"expression": "840 * 15 / 100"})
	assert "126" in result.content[0].text


def test_calculator_rejects_code():
	with pytest.raises(Exception):
		_call_tool("calculator", {"expression": "__import__('os').system('echo hi')"})


@pytest.mark.live
def test_agent_uses_calculator_for_maths():
	result = asyncio.run(run_agent("What is 15% of 840?"))
	assert "126" in result
