from typing import TypedDict
from langgraph.graph import StateGraph, END
from pypdf import PdfReader
from docx import Document
import requests
import time
class AgentState(TypedDict):
    question: str
    reponse: str
    type_question: str
    historique: str


def calculatrice(expression):
    try:
        return eval(expression)
    except Exception:
        return "Expression invalide"


def txt_reader(chemin_fichier):
    try:
        with open(chemin_fichier,"r",encoding="utf-8") as fichier:
            return fichier.read()
    except:
        return "Fichier introuvable."


def pdf_reader(chemin_fichier):
    try:
        lecteur = PdfReader(chemin_fichier)
        contenu = ""
        for page in lecteur.pages:
            contenu += (page.extract_text())
        return contenu
    except:
        return "Fichier introuvable."


def docx_reader(chemin_fichier):
    try:
        doc = Document(chemin_fichier)
        contenu = ""
        for paragraphe in (doc.paragraphs):
            contenu += (paragraphe.text + "\n")
            return contenu
    except:
        return "Fichier introuvable."


def analyse_node(state):
    question = state["question"]
    print("[LOG] Question reçue :",question)
    return state


def decision_node(state):
    question = state["question"].lower()

    if "bonjour" in question:
        state["type_question"] = "salutation"

    elif ("+" in question or "-" in question or "*" in question or "/" in question):
        state["type_question"] = "calcul"

    elif ".pdf" in question:
        state["type_question"] = "pdf"

    elif ".docx" in question:
        state["type_question"] = "docx"

    elif ".txt" in question:
        state["type_question"] = "txt"

    else:
        state["type_question"] = "documentation"
    print("[LOG] Outil sélectionné :", state["type_question"])

    return state


def calculatrice_node(state):
    expression = (
        state["question"]
        .lower()
        .replace("calcule", "")
        .replace("combien font", "")
        .strip()
    )

    state["reponse"] = str(calculatrice(expression))
    return state


def llm_local(prompt):
    url = "http://localhost:11434/api/generate"

    data = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=data)
    return response.json()["response"]
url = ("http://host.docker.internal:11434/api/generate")


def txt_reader_node(state):
    contenu = txt_reader("documents/rh.txt")
    question = state["question"]
    historique = state.get("historique", "")
    prompt = f"""
        Historique :{historique}
        Contexte :{contenu}
        Question :{question}
        Réponse :
        """
    state["reponse"] = llm_local(prompt)
    return state


def pdf_reader_node(state):
    contenu = pdf_reader("documents/formation.pdf")
    question = state["question"]
    historique = state.get("historique", "")
    prompt = f"""
        Historique :{historique}
        Contexte :{contenu}
        Question :{question}
    Réponse :
    """
    state["reponse"] = llm_local(prompt)
    return state

def docx_reader_node(state):
    contenu = docx_reader("documents/procedure.docx")
    question = state["question"]
    historique = state.get("historique", "")
    prompt = f"""
        Historique :{historique}
        Contexte :{contenu}
        Question :{question}
    Réponse :
    """
    state["reponse"] = llm_local(prompt)
    return state


def documentation_node(state):
    historique = state.get("historique", "")
    question = state["question"]

    prompt = f"""
    Historique :{historique}

    Question :{question}

    Réponse :
    """
    state["reponse"] = llm_local(prompt)
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
workflow.add_node("pdf_reader", pdf_reader_node)
workflow.add_node("docx_reader", docx_reader_node)
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
        "pdf": "pdf_reader",
        "docx": "docx_reader",
        "txt": "txt_reader",
        "documentation": "documentation",
    },
)

workflow.add_edge("calculatrice", END)
workflow.add_edge("txt_reader", END)
workflow.add_edge("pdf_reader", END)
workflow.add_edge("docx_reader", END)
workflow.add_edge("documentation", END)
workflow.add_edge("salutation", END)

agent = workflow.compile()

if __name__ == "__main__":
    memoire = []

    questions = [
    "Quels sont les congés ?",
    "Lis formation.pdf",
    "50+20",
    "Lis procedure.docx"
    ]

    for question in questions:

        if question == "":
            print("Veuillez saisir une question.")
            continue

        historique = "\n".join(memoire)

        debut = time.time()

        resultat = agent.invoke({
            "question": question,
            "historique": historique
        })

        fin = time.time()

        reponse = resultat["reponse"]

        memoire.append(f"Utilisateur : {question}")
        memoire.append(f"Assistant : {reponse}")

        print(reponse)
        print("[LOG] Réponse générée")
        print("Temps :", fin - debut, "secondes")
        print("-------------")

        print("\nQuestion :", question)
        print("Réponse :", resultat["reponse"])

        memoire.append(f"Utilisateur : {question}")
        memoire.append(f"Assistant : {resultat['reponse']}")