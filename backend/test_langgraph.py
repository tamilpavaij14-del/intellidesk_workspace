from langgraph.graph import StateGraph, END
from typing import TypedDict


class State(TypedDict):
    message: str


def hello_node(state: State) -> State:
    return {"message": state["message"] + " -> processed"}


graph = StateGraph(State)

graph.add_node("hello", hello_node)

graph.set_entry_point("hello")

graph.add_edge("hello", END)

app = graph.compile()


result = app.invoke({"message": "test"})

print(result)