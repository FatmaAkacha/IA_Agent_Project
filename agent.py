from typing import TypedDict
from langgraph.graph import StateGraph, END
from pypdf import PdfReader
from docx import Document
import requests


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

def pdf_reader(chemin_fichier):
    lecteur = PdfReader(
    chemin_fichier)
    contenu = ""
    for page in lecteur.pages:
        contenu += (page.extract_text())
    return contenu

def docx_reader(chemin_fichier):
    doc = Document(
    chemin_fichier)
    contenu = ""
    for paragraphe in doc.paragraphs:
        contenu += (paragraphe.text + "\n")
    return contenu

def analyse_node(state):
    print("Analyse de la question...")
    return state

def decision_node(state):
    question = state["question"].lower()
    if "bonjour" in question:
        state["type_question"] = ("salutation")
    elif ("+" in question or "-" in question or "*" in question or "/" in question):
        state["type_question"] = ("calcul")
    elif ".pdf" in question:
        state["type_question"] = ("pdf")
    elif ".docx" in question:
        state["type_question"] = ("docx")
    elif ".txt" in question:
        state["type_question"] = ("txt")
    else:
        state["type_question"] = ("documentation")
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


def llm_local(prompt):
    url = ("http://localhost:11434/api/generate")
    data = {
            "model": "phi3",
            "prompt": prompt,
            "stream": False
            }
    response = requests.post(url,json=data)
    return response.json()["response"]

def txt_reader_node(state):
    contenu = txt_reader("documents/rh.txt")
    question = state["question"]
    prompt = f"""Contexte :{contenu}
    Question :{question}
    Réponse :
    """ 
    state["reponse"] = llm_local(prompt)
    return state

def pdf_reader_node(state):
    contenu = pdf_reader("documents/formation.pdf" )
    question = state["question"]
    prompt = f""" Contexte :{contenu}
    Question :{question}
    Réponse :
    """
    state["reponse"] = llm_local(prompt)
    return state
def docx_reader_node(state):
    contenu = docx_reader("documents/procedure.docx")
    question = state["question"]
    prompt = f"""Contexte :{contenu}
    Question :{question}
    Réponse :
    """
    state["reponse"] = llm_local(prompt)
    return state

def documentation_node(state):
    question = state["question"]
    prompt = f"""Réponds à cette question :{question}"""
    reponse = llm_local(prompt)
    state["reponse"] = reponse
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
workflow.add_node("pdf_reader",pdf_reader_node)
workflow.add_node("docx_reader",docx_reader_node)

workflow.set_entry_point("analyse")

workflow.add_edge("analyse", "decision")

workflow.add_conditional_edges(
    "decision",
    route_question,
    {
        "salutation": "salutation",
        "calcul": "calculatrice",
        "pdf":"pdf_reader",
        "docx":"docx_reader",
        "txt": "txt_reader",
        "documentation": "documentation",
    },
)

workflow.add_edge("calculatrice", END)
workflow.add_edge("txt_reader", END)
workflow.add_edge("documentation", END)
workflow.add_edge("salutation", END)
workflow.add_edge("pdf_reader", END)
workflow.add_edge("docx_reader", END)



agent = workflow.compile()

questions = [
    "Lis formation.pdf",
    "Quels sujets sont étudiés ?",
    "Lis procedure.docx",
    "Que dit la procédure RH ?"
]

for q in questions:
    resultat = agent.invoke({"question": q})
    print("\nQuestion :", q)
    print("Réponse :", resultat["reponse"])

#print(pdf_reader("documents/formation.pdf"))
#print(docx_reader("documents/procedure.docx"))

#resultat = agent.invoke({"question":"What is Agent IA ?"})
#print(resultat["reponse"])

#print(llm_local("Bonjour"))