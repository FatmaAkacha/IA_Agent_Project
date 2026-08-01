import mlflow
import time
from agent import agent

debut = time.time()
resultat = agent.invoke({"question": "Quels sont les congés ?"})
fin = time.time()
with mlflow.start_run():
    mlflow.log_param("modele", "phi3")
    mlflow.log_metric("temps_reponse", fin - debut)
print(resultat["reponse"])