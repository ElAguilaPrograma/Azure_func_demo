from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import StaticPool, create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TareaDB(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    completada = Column(Boolean, default=False)
    
class TareaBase(BaseModel):
    title: str
    description: str
    completada: bool = False
    
class TareaResponse(TareaBase):
    id: int
    class Config:
        orm_mode = True
        
Base.metadata.create_all(bind=engine)
        
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/tareas", response_model=list[TareaResponse])
def get_all(db: Session = Depends(get_db)):
    tareas = db.query(TareaDB).all()
    return tareas

@app.get("/tareas/{tarea_id}", response_model=TareaResponse)
def get_tarea(tarea_id: int, db: Session = Depends(get_db)):
    tarea = db.query(TareaDB).filter(TareaDB.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

@app.post("/tareas", response_model=TareaResponse, status_code=201)
def create_tarea(tarea: TareaBase, db: Session = Depends(get_db)):
    db_item = TareaDB(**tarea.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/tareas/{tarea_id}", response_model=TareaResponse)
def update_tarea(tarea_id: int, tarea: TareaBase, db: Session = Depends(get_db)):
    db_item = db.query(TareaDB).filter(TareaDB.id == tarea_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    db_item.title = tarea.title
    db_item.description = tarea.description
    db_item.completada = tarea.completada
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/tareas/{tarea_id}", status_code=204)
def delete_tarea(tarea_id: int, db: Session = Depends(get_db)):
    db_item = db.query(TareaDB).filter(TareaDB.id == tarea_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    db.delete(db_item)
    db.commit()