from typing import TypedDict
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    question: str
    reponse: str
    type_question: str

def calculatrice(expression):
    try:
        return eval(expression)
    except Exception:
        return "Expression invalide"

def txt_reader(chemin_fichier):
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as fichier:
            return fichier.read()
    except FileNotFoundError:
        return "Fichier introuvable."

def analyse_node(state):
    print("Analyse de la question...")
    return state

def decision_node(state):
    question = state["question"].lower()
    if "bonjour" in question:
        state["type_question"] = "salutation"
    elif "+" in question or "-" in question or "*" in question or "/" in question:
        state["type_question"] = "calcul"
    elif "lis" in question or "lecture" in question:
        state["type_question"] = "lecture"
    else:
        state["type_question"] = "documentation"
    return state

def calculatrice_node(state):
    expression = state["question"]
    expression = (
        expression.lower()
        .replace("calcule", "")
        .replace("combien font", "")
        .strip()
    )

    resultat = calculatrice(expression)

    state["reponse"] = str(resultat)
    return state


def txt_reader_node(state):
    contenu = txt_reader("documents/rh.txt")
    state["reponse"] = contenu
    return state


def documentation_node(state):
    state["reponse"] = "Réponse documentaire."
    return state


def greeting_node(state):
    state["reponse"] = "Bonjour ! Comment puis-je vous aider ?"
    return state


def route_question(state):
    return state["type_question"]

workflow = StateGraph(AgentState)

workflow.add_node("analyse", analyse_node)
workflow.add_node("decision", decision_node)
workflow.add_node("calculatrice", calculatrice_node)
workflow.add_node("txt_reader", txt_reader_node)
workflow.add_node("documentation", documentation_node)
workflow.add_node("salutation", greeting_node)

workflow.set_entry_point("analyse")

workflow.add_edge("analyse", "decision")

workflow.add_conditional_edges(
    "decision",
    route_question,
    {
        "salutation": "salutation",
        "calcul": "calculatrice",
        "lecture": "txt_reader",
        "documentation": "documentation",
    },
)

workflow.add_edge("calculatrice", END)
workflow.add_edge("txt_reader", END)
workflow.add_edge("documentation", END)
workflow.add_edge("salutation", END)

agent = workflow.compile()

questions = [
    "Bonjour",
    "5+5",
    "50*4",
    "100/2",
    "Calcule 10+25",
    "Lis le fichier RH",
    "Quels sont les congés annuels ?",
]

for q in questions:
    resultat = agent.invoke({"question": q})
    print("\nQuestion :", q)
    print("Réponse :", resultat["reponse"])