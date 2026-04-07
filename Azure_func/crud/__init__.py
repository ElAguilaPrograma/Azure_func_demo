import json
import azure.functions as func

class Tarea:
    def __init__(self, id: int, nombre: str, descripcion: str):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "descripcion": self.descripcion}

tareas_db: list[Tarea] = [
    Tarea(1, "Configurar Azure", "Configurar el entorno de desarrollo inicial"),
    Tarea(2, "Desarrollar funcion", "Crear la funcion HTTP para CRUD"),
]

def obtener_tarea_por_id(tarea_id: int) -> Tarea | None:
    return next((t for t in tareas_db if t.id == tarea_id), None)

def existe_id(tarea_id: int) -> bool:
    return any(t.id == tarea_id for t in tareas_db)

def main(req: func.HttpRequest) -> func.HttpResponse:
    method = req.method
    item_id_param = req.route_params.get("id")
    item_id = None
    if item_id_param is not None:
        try:
            item_id = int(item_id_param)
        except (TypeError, ValueError):
            return func.HttpResponse("ID invalido", status_code=400)

    if method == "GET":
        if item_id is not None:
            tarea = obtener_tarea_por_id(item_id)
            if tarea:
                return func.HttpResponse(json.dumps(tarea.to_dict()), mimetype="application/json")
            return func.HttpResponse("No encontrado", status_code=404)
        return func.HttpResponse(
            json.dumps([tarea.to_dict() for tarea in tareas_db]),
            mimetype="application/json",
        )

    if method == "POST":
        try:
            body = req.get_json()
            nombre = body["nombre"]
            descripcion = body["descripcion"]

            nuevo_id = body.get("id")
            if nuevo_id is None:
                nuevo_id = max((tarea.id for tarea in tareas_db), default=0) + 1
            else:
                nuevo_id = int(nuevo_id)

            if existe_id(nuevo_id):
                return func.HttpResponse("ID repetido", status_code=409)

            nueva_tarea = Tarea(
                id=nuevo_id,
                nombre=nombre,
                descripcion=descripcion,
            )
            tareas_db.append(nueva_tarea)
            return func.HttpResponse(
                json.dumps(nueva_tarea.to_dict()),
                status_code=201,
                mimetype="application/json",
            )
        except (TypeError, ValueError, KeyError):
            return func.HttpResponse("Datos invalidos", status_code=400)

    if method == "PUT":
        if item_id is None:
            return func.HttpResponse("ID requerido", status_code=400)

        try:
            body = req.get_json()
        except ValueError:
            return func.HttpResponse("Datos invalidos", status_code=400)

        tarea = obtener_tarea_por_id(item_id)
        if tarea:
            nuevo_id = body.get("id", tarea.id)
            try:
                nuevo_id = int(nuevo_id)
            except (TypeError, ValueError):
                return func.HttpResponse("ID invalido", status_code=400)

            if nuevo_id != tarea.id and existe_id(nuevo_id):
                return func.HttpResponse("ID repetido", status_code=409)

            if nuevo_id != tarea.id:
                return func.HttpResponse("ID no se puede cambiar", status_code=400)
            tarea.id = nuevo_id
            tarea.nombre = body.get("nombre", tarea.nombre)
            tarea.descripcion = body.get("descripcion", tarea.descripcion)
            return func.HttpResponse(json.dumps(tarea.to_dict()), mimetype="application/json")
        return func.HttpResponse("No encontrado", status_code=404)

    if method == "DELETE":
        if item_id is None:
            return func.HttpResponse("ID requerido", status_code=400)

        tareas_db[:] = [t for t in tareas_db if t.id != item_id]
        return func.HttpResponse(status_code=204)

    return func.HttpResponse("Metodo no permitido", status_code=405)