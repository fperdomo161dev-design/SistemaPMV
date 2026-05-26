# services/producto_service.py

from typing import List, Optional, Any
from dataclasses import asdict

from database.conexion import get_db
from models.producto import Producto

db = get_db()
coleccion = db["productos"]

def _int(x: Any) -> int:
    try:
        return int(x or 0)
    except Exception:
        return 0

def _doc_a_producto(doc):

    return Producto(
        numReferencia=int(
            doc.get("numReferencia", 0)
        ),
        marca=str(
            doc.get("marca", "")
        ),
        talla=str(
            doc.get("talla", "")
        ),
        color=str(
            doc.get("color", "")
        ),
        cantidadStock=int(
            doc.get("cantidadStock", 0)
        ),
        valor=int(
            doc.get("valor", 0)
        ),
        ubicacion=str(
            doc.get("ubicacion", "")
        ),
    )

# LISTAR

def listar_productos() -> List[Producto]:

    productos: List[Producto] = []

    for doc in coleccion.find().sort("numReferencia", 1):

        productos.append(
            _doc_a_producto(doc)
        )

    return productos
# BUSCAR

def buscar_producto_por_ref(
    ref: int
) -> Optional[Producto]:

    doc = coleccion.find_one(
        {"numReferencia": int(ref)}
    )

    if not doc:
        return None

    return _doc_a_producto(doc)
# CREAR
def crear_producto(
    producto: Producto
) -> bool:

    existe = coleccion.find_one(
        {"numReferencia": int(producto.numReferencia)}
    )

    if existe:
        return False

    data = asdict(producto)

    data.pop("_id", None)

    res = coleccion.insert_one(data)

    return bool(res.inserted_id)

# ACTUALIZAR
def actualizar_producto(
    ref: int,
    data: dict
) -> bool:

    data.pop("numReferencia", None)

    if "cantidadStock" in data:
        data["cantidadStock"] = _int(
            data["cantidadStock"]
        )

    if "valor" in data:
        data["valor"] = _int(
            data["valor"]
        )

    if "iva" in data:
        data["iva"] = _int(
            data["iva"]
        )

    if "costo" in data:
        data["costo"] = _int(
            data["costo"]
        )

    res = coleccion.update_one(
        {"numReferencia": int(ref)},
        {"$set": data},
    )

    return res.modified_count > 0

# ELIMINAR

def eliminar_producto(
    ref: int
) -> bool:

    res = coleccion.delete_one(
        {"numReferencia": int(ref)}
    )

    return res.deleted_count > 0
# DESCONTAR STOCK

def descontar_stock_por_ref(
    ref: int,
    cantidad: int
) -> bool:

    if cantidad <= 0:
        return False

    producto = coleccion.find_one(
        {"numReferencia": int(ref)}
    )

    if not producto:
        return False

    stock_actual = _int(
        producto.get("cantidadStock", 0)
    )

    if stock_actual < cantidad:
        return False

    nuevo_stock = stock_actual - int(cantidad)

    coleccion.update_one(
        {"numReferencia": int(ref)},
        {
            "$set": {
                "cantidadStock": int(nuevo_stock)
            }
        },
    )

    return True

# SUMR STOCK
def sumar_stock_por_ref(
    ref: int,
    cantidad: int
) -> bool:

    if cantidad <= 0:
        return False

    producto = coleccion.find_one(
        {"numReferencia": int(ref)}
    )

    if not producto:
        return False

    stock_actual = _int(
        producto.get("cantidadStock", 0)
    )

    nuevo_stock = stock_actual + int(cantidad)

    coleccion.update_one(
        {"numReferencia": int(ref)},
        {
            "$set": {
                "cantidadStock": int(nuevo_stock)
            }
        },
    )

    return True