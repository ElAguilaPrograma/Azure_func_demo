import azure.functions as func
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

class Tarea(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str]

app = FastAPI()

tareas_db: List[Tarea] = [Tarea(id=1, titulo="Tarea 1", descripcion="Descripción de la tarea 1"), 
             Tarea(id=2, titulo="Tarea 2", descripcion="Descripción de la tarea 2")]

@app.get("/tareas", response_model=List[Tarea])
async def get_tareas():
    return tareas_db
    
@app.get("/tareas/{id}")
async def get_tarea(id: int):
    tarea = next((t for t in tareas_db if t.id == id), None)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

@app.post("/tareas", status_code=201)
async def create_tarea(tarea: Tarea):
    if any(t.id == tarea.id for t in tareas_db):
        raise HTTPException(status_code=400, detail="Ya existe una tarea con ese id")

    tareas_db.append(tarea)
    return tarea

@app.put("/tareas/{id}")
async def update_tarea(id: int, tarea: Tarea):
    tarea_encontrada = next((t for t in tareas_db if t.id == id), None)
    if not tarea_encontrada:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    if tarea.id != id:
        raise HTTPException(status_code=400, detail="El id del cuerpo debe coincidir con el de la URL")

    tarea_encontrada.titulo = tarea.titulo
    tarea_encontrada.descripcion = tarea.descripcion
    
    return tarea_encontrada

@app.delete("/tareas/{id}", status_code=204)
async def delete_tarea(id: int):
    tarea_encontrada = next((t for t in tareas_db if t.id == id), None)
    if not tarea_encontrada:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    tareas_db.remove(tarea_encontrada)
    return None