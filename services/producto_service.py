from dataclasses import asdict
from typing import Any, List, Optional

from database.conexion import get_db
from models.producto import Producto

db = get_db()
coleccion = db["productos"]
coleccion_config = db["config_sistema"]


# UTILIDADES Y MAPEO DE DATOS



def _int(x: Any) -> int:
    """Convierte un valor a entero de forma segura."""
    try:
        return int(x or 0)
    except Exception:
        return 0


def _doc_a_producto(doc) -> Optional[Producto]:
    """Convierte un documento de MongoDB al modelo Producto."""
    try:
        return Producto(
            numReferencia=_int(
                doc.get("numReferencia", doc.get("referencia", 0))
            ),
            marca=str(doc.get("marca", "")),
            talla=str(doc.get("talla", "")),
            color=str(doc.get("color", "")),
            cantidadStock=_int(doc.get("cantidadStock", doc.get("stock", 0))),
            valorCompra=_int(
                doc.get("valorCompra", doc.get("valor", 0))
            ),
            valorVenta=_int(
                doc.get("valorVenta", doc.get("valor", 0))
            ),
            ubicacion=str(doc.get("ubicacion", "")),
        )
    except Exception as e:
        print(f"❌ Error mapeando documento {doc}: {e}")
        return None



# GESTIÓN DE REFERENCIAS AUTOMÁTICAS



def obtener_siguiente_referencia() -> int:
    """Calcula la primera referencia disponible a partir de 101, rellenando huecos libres."""
    refs_raw = coleccion.distinct("numReferencia", {"numReferencia": {"$exists": True}})
    refs_existentes = set()
    
    for r in refs_raw:
        try:
            val = int(r)
            if val >= 101:
                refs_existentes.add(val)
        except (ValueError, TypeError):
            continue

    siguiente = 101
    while siguiente in refs_existentes:
        siguiente += 1

    return siguiente



# OPERACIONES CRUD (LISTAR, BUSCAR, CREAR, ACTUALIZAR, ELIMINAR)


def listar_productos() -> List[Producto]:
    """Lista todos los productos ordenados de forma ascendente por su referencia."""
    productos: List[Producto] = []
    try:
        # Orden de la consulta directo en MongoDB
        documentos = list(coleccion.find().sort("numReferencia", 1))
        print(f"🔍 Total de documentos encontrados en MongoDB: {len(documentos)}")

        for doc in documentos:
            prod = _doc_a_producto(doc)
            if prod:
                productos.append(prod)
                
        # Asegura ordenamiento estrictamente numérico
        productos.sort(key=lambda p: p.numReferencia)
    except Exception as e:
        print(f"❌ Error al listar productos desde la BD: {e}")
    return productos


def buscar_producto_por_ref(ref: Any) -> Optional[Producto]:
    """Busca un producto únicamente por número de referencia (int o str)."""
    criterio = str(ref).strip()
    if not criterio:
        return None

    try:
        ref_int = int(criterio)
        query = {
            "$or": [
                {"numReferencia": ref_int},
                {"numReferencia": criterio}
            ]
        }
    except ValueError:
        query = {"numReferencia": criterio}

    doc = coleccion.find_one(query)
    if not doc:
        return None
    return _doc_a_producto(doc)


def buscar_producto_por_ref_o_nombre(criterio: str) -> Optional[Producto]:
    """Redirige directamente a la búsqueda exclusiva por referencia."""
    return buscar_producto_por_ref(criterio)


def crear_producto(producto: Producto) -> tuple[bool, Optional[int]]:
    """Crea un nuevo producto asignándole una referencia automática."""
    nueva_ref = obtener_siguiente_referencia()
    producto.numReferencia = nueva_ref

    existe = buscar_producto_por_ref(nueva_ref)
    if existe:
        return False, None

    data = asdict(producto)
    data.pop("_id", None)

    res = coleccion.insert_one(data)
    if res.inserted_id:
        return True, nueva_ref
    return False, None


def actualizar_producto(ref: Any, data: dict) -> bool:
    """Actualiza los datos de un producto existente por número de referencia."""
    data.pop("numReferencia", None)

    if "cantidadStock" in data:
        data["cantidadStock"] = _int(data["cantidadStock"])
    if "valorCompra" in data:
        data["valorCompra"] = _int(data["valorCompra"])
    if "valorVenta" in data:
        data["valorVenta"] = _int(data["valorVenta"])

    if "valor" in data:
        val = _int(data["valor"])
        data["valorVenta"] = val
        data.pop("valor", None)

    try:
        ref_val = int(ref)
        query = {"$or": [{"numReferencia": ref_val}, {"numReferencia": str(ref)}]}
    except ValueError:
        query = {"numReferencia": str(ref)}

    res = coleccion.update_one(query, {"$set": data})
    return res.modified_count > 0


def eliminar_producto(ref: Any) -> bool:
    """Elimina un producto por su número de referencia."""
    try:
        ref_val = int(ref)
        query = {"$or": [{"numReferencia": ref_val}, {"numReferencia": str(ref)}]}
    except ValueError:
        query = {"numReferencia": str(ref)}

    res = coleccion.delete_one(query)
    return res.deleted_count > 0