import azure.functions as func
from fastapi import FastAPI
from routers import tareas

app = FastAPI()
app.include_router(tareas.router)

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.AsgiMiddleware(app).handle(req, context)