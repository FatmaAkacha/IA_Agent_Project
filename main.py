from fastapi import FastAPI
from pydantic import BaseModel
from agent import agent


app = FastAPI()
class QuestionRequest(BaseModel):
    question: str
def utilisateur(nom):
    return {"message": f"Bonjour {nom}"}

@app.get("/")
def accueil():
    return {"message":"Bienvenue dans l'Agent IA"}
@app.get("/bonjour")
def bonjour():
    return {"message": "Bonjour"}
@app.get("/status")
def status():
    return {"etat": "OK"}
@app.get("/info")
def info():
    return {"application": "Agent IA","version": "1.0"}
@app.get("/utilisateur/{nom}")

@app.post("/question")
def poser_question(request: QuestionRequest):
    try:
        resultat = agent.invoke({"question":request.question})
        return {"reponse":resultat["reponse"]}
    except Exception as e:
        return {"erreur": str(e)}
