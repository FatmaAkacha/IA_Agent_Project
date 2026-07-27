from typing import TypedDict
from langgraph.graph import (StateGraph,END)

class AgentState(TypedDict):
    question: str

def analyse_node(state):
    print("Analyse de la question...")
    return state
etat = {
"question": "Quels sont les congés annuels ?"
}
analyse_node(etat)

workflow = StateGraph(AgentState)
workflow.add_node("analyse",analyse_node)

workflow.set_entry_point("analyse")
workflow.add_edge("analyse",END)

agent = workflow.compile()
resultat = agent.invoke(
{"question":"Quels sont les congés annuels ?"})
print(resultat)