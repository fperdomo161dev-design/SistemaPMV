# services/cliente_service.py

from typing import List, Optional
from dataclasses import asdict

from database.conexion import get_db
from models.cliente import Cliente

db = get_db()
coleccion = db["clientes"]

# CONVERTIR DOCUMENTO A CLIENTE
def _doc_a_cliente(doc):
    return Cliente(
        cedula=str(doc.get("cedula", "")),
        nombre=str(doc.get("nombre", "")),
        apellido=str(doc.get("apellido", "")),
        correo=str(doc.get("correo", "")),
        celular=str(doc.get("celular", "")),
        direccion=str(doc.get("direccion", "")),
        puntos=int(doc.get("puntos", 0))  # <-- CONVERTIR PUNTOS
    )

def acumular_puntos_por_compra(cedula: str, total_compra: float) -> bool:
    """
    Calcula 10 puntos por cada 50,000 en compras y los suma al cliente.
    Ejemplo: 100,000 = 20 puntos.
    """
  #bloque puntos 
    bloques_de_cincuenta_mil = int(total_compra // 50000)
    puntos_ganados = bloques_de_cincuenta_mil * 10

    if puntos_ganados <= 0:
        return False

    # Actualizamos sumando los puntos existentes en la base de datos
    res = coleccion.update_one(
        {"cedula": str(cedula).strip()},
        {"$inc": {"puntos": puntos_ganados}}
    )

    return res.modified_count > 0

# LISTAR
def listar_clientes() -> List[Cliente]:
    clientes = []
    for doc in coleccion.find().sort("nombre", 1):
        clientes.append(_doc_a_cliente(doc))
    return clientes

# CREAR
def crear_cliente(cliente_data) -> bool:
    if isinstance(cliente_data, Cliente):
        data = asdict(cliente_data)
    else:
        data = cliente_data

    # Validar si ya existe el cliente por cédula
    existe = coleccion.find_one({"cedula": data.get("cedula")})
    if existe:
        return False

    res = coleccion.insert_one(data)
    return bool(res.inserted_id)

# BUSCAR POR CÉDULA
def buscar_cliente_por_cedula(cedula: str) -> Optional[Cliente]:
    doc = coleccion.find_one({"cedula": cedula})
    if not doc:
        return None
    return _doc_a_cliente(doc)

# ACTUALIZAR
def actualizar_cliente(cedula: str, data: dict) -> bool:
    cedula = str(cedula).strip()

    res = coleccion.update_one(
        {"cedula": cedula},
        {"$set": data},
    )

    return res.matched_count > 0

# ELIMINAR
def eliminar_cliente(cedula: str) -> bool:
    cedula = str(cedula).strip()
    res = coleccion.delete_one({"cedula": cedula})
    return res.deleted_count > 0