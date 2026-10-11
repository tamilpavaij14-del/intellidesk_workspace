from google.genai import types

from services.llm import DEFAULT_MODEL, _client
from services.mcp_client import call_tool, list_tools

MAX_ROUNDS = 3


def _to_gemini_tools(mcp_tools) -> types.Tool:
	return types.Tool(
	    function_declarations=[
	        types.FunctionDeclaration(
	            name=t.name,
	            description=t.description or "",
	            parameters_json_schema=t.input_schema,
					)
	        for t in mcp_tools
				]
			)


async def run_agent(prompt: str, max_rounds: int = MAX_ROUNDS) -> str:
	gemini_tools = _to_gemini_tools(await list_tools())
	contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]

	for _ in range(max_rounds):
		response = _client.models.generate_content(
			model=DEFAULT_MODEL,
			contents=contents,
			config=types.GenerateContentConfig(tools=[gemini_tools]),
				)
		candidate = response.candidates[0]
		calls = [p.function_call for p in candidate.content.parts if p.function_call]

		if not calls:
			return response.text

		response_parts = []
		for call in calls:
			try:
				payload = {"result": await call_tool(call.name, dict(call.args))}
			except Exception as e:
				payload = {"error": str(e)}
			response_parts.append(
				types.Part.from_function_response(name=call.name, response=payload)
					)

		contents.append(candidate.content)
		contents.append(types.Content(role="user", parts=response_parts))

	return "I could not finish this within the allowed number of tool calls."
