import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal, TareaDB, TareaBase, TareaResponse, Base, engine

Base.metadata.create_all(bind=engine)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("/status")
def get_status():
    return {"status": "API is running"}

@router.get("/tareas", response_model=list[TareaResponse])
def read_tareas(db: Session = Depends(get_db)):
    tareas = db.query(TareaDB).all()
    return tareas

@router.get("/tareas/{tarea_id}", response_model=TareaResponse)
def read_tarea(tarea_id: int, db: Session = Depends(get_db)):
    tarea = db.query(TareaDB).filter(TareaDB.id == tarea_id).first()
    if tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

@router.post("/tareas", response_model=TareaResponse, status_code=201)
def create_tarea(tarea: TareaBase, db: Session = Depends(get_db)):
    nueva_tarea = TareaDB(**tarea.model_dump())
    db.add(nueva_tarea)
    db.commit()
    db.refresh(nueva_tarea)
    return nueva_tarea

@router.put("/tareas/{tarea_id}", response_model=TareaResponse)
def update_tarea(tarea_id: int, tarea: TareaBase, db: Session = Depends(get_db)):
    tarea_db = db.query(TareaDB).filter(TareaDB.id == tarea_id).first()
    if tarea_db is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    tarea_db.title = tarea.title
    tarea_db.description = tarea.description
    tarea_db.completed = tarea.completed
    db.commit()
    db.refresh(tarea_db)
    return tarea_db

@router.delete("/tareas/{tarea_id}", status_code=204)
def delete_tarea(tarea_id: int, db: Session = Depends(get_db)):
    tarea_db = db.query(TareaDB).filter(TareaDB.id == tarea_id).first()
    if tarea_db is None:
        raise HTTPException(status_code=404, detail="Tarea not found")
    db.delete(tarea_db)
    db.commit()
