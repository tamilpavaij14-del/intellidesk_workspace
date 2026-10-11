from fastmcp import Client

from mcp_server import mcp

_client = Client(mcp)


async def list_tools():
	async with _client:
		return await _client.list_tools()


async def call_tool(name: str, arguments: dict) -> str | None:
	async with _client:
		result = await _client.call_tool(name, arguments)
		return result.content[0].text if result.content else None
