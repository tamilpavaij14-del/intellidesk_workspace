from services.llm import complete, stream

print(complete("Say hi in one word"))

for chunk in stream("Count from 1 to 5"):
	print(chunk, end="", flush=True)
