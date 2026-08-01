import mlflow
modeles = {
    "phi3": 1.2,
    "mistral": 1.8,
    "gemma": 2.1
        }

for modele, temps in modeles.items():
    with mlflow.start_run():
        mlflow.log_param("modele", modele)
        mlflow.log_metric("temps_reponse", temps)