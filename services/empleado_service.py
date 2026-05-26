# services/empleado_service.py

from typing import List, Optional
from dataclasses import asdict

from database.conexion import get_db
from models.empleado import Empleado

db = get_db()

coleccion = db["empleados"]

# CONVERTIR DOCUMENTO A EMPLEADO

def _doc_a_empleado(doc):

    return Empleado(

        cedula=str(
            doc.get("cedula", "")
        ),

        nombre=str(
            doc.get("nombre", "")
        ),

        cargo=str(
            doc.get("cargo", "")
        ),

        usuario=str(
            doc.get("usuario", "")
        ),

        clave=str(
            doc.get("clave", "")
        ),
    )

# LISTAR

def listar_empleados() -> List[Empleado]:
    empleados = []
    for doc in coleccion.find().sort("nombre", 1):
        empleados.append(
            _doc_a_empleado(doc)
        )

    return empleados
# CREAR
def crear_empleado(
    empleado: Empleado
) -> bool:

    existe = coleccion.find_one(
        {"cedula": empleado.cedula}
    )

    if existe:
        return False

    data = asdict(empleado)

    res = coleccion.insert_one(data)

    return bool(res.inserted_id)


# BUSCAR POR CÉDULA
def buscar_empleado_por_cedula(
    cedula: str
) -> Optional[Empleado]:

    doc = coleccion.find_one(
        {"cedula": cedula}
    )

    if not doc:
        return None

    return _doc_a_empleado(doc)

# BUSCAR POR USUARIO

def buscar_empleado_por_usuario(
    usuario: str
) -> Optional[Empleado]:

    doc = coleccion.find_one(
        {"usuario": usuario}
    )

    if not doc:
        return None

    return _doc_a_empleado(doc)

# LOGIN

def validar_credenciales(
    usuario: str,
    clave: str
) -> Optional[Empleado]:

    empleado = buscar_empleado_por_usuario(
        usuario
    )

    if not empleado:
        return None

    if empleado.clave != clave:
        return None

    return empleado

# ACTUALIZAR


def actualizar_empleado(
    cedula: str,
    data: dict
) -> bool:

    res = coleccion.update_one(
        {"cedula": cedula},
        {"$set": data},
    )

    return res.modified_count > 0

# ELIMINAR
def eliminar_empleado(
    cedula: str
) -> bool:

    res = coleccion.delete_one(
        {"cedula": cedula}
    )
    return res.deleted_count > 0