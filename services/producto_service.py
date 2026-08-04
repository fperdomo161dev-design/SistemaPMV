# services/producto_service.py

from typing import List, Optional, Any
from dataclasses import asdict

from database.conexion import get_db
from models.producto import Producto

db = get_db()
coleccion = db["productos"]
coleccion_config = db["config_sistema"]

def _int(x: Any) -> int:
    try:
        return int(x or 0)
    except Exception:
        return 0

def _doc_a_producto(doc) -> Optional[Producto]:
  """Convierte un documento de MongoDB al modelo Producto
  """
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
        ),  # [CAMBIO]: Asigna valorCompra acorde al modelo actualizado
        valorVenta=_int(
            doc.get("valorVenta", doc.get("valor", 0))
        ),  # [CAMBIO]: Asigna valorVenta acorde al modelo actualizado
        ubicacion=str(doc.get("ubicacion", "")),
    )
  except Exception as e:
    print(f"❌ Error mapeando documento {doc}: {e}")
    return None
  
# GESTIÓN DE REFERENCIAS AUTOMÁTICAS

def obtener_siguiente_referencia() -> int:
  """Obtiene la siguiente referencia disponible (reciclando o incrementando)."""
  config = coleccion_config.find_one({"_id": "referencias_libres"})

  if config and config.get("lista"):
    lista_libres = config["lista"]
    ref_reciclada = lista_libres.pop(0)

    coleccion_config.update_one(
        {"_id": "referencias_libres"}, {"$set": {"lista": lista_libres}}
    )
    return int(ref_reciclada)
  else:
    ultimo = coleccion.find_one(sort=[("numReferencia", -1)])
    if not ultimo or "numReferencia" not in ultimo:
      return 1
    return _int(ultimo["numReferencia"]) + 1

#CRUD


# LISTAR

def listar_productos() -> List[Producto]:
  """Lista todos los productos ordenados por su referencia."""
  productos: List[Producto] = []
  try:
    documentos = list(coleccion.find())
    print(f"🔍 Total de documentos encontrados en MongoDB: {len(documentos)}")

    for doc in documentos:
      prod = _doc_a_producto(doc)
      if prod:
        productos.append(prod)
  except Exception as e:
    print(f"❌ Error al listar productos desde la BD: {e}")
  return productos

# BUSCAR

def buscar_producto_por_ref(ref: int) -> Optional[Producto]:
  """Busca un producto específico por su número de referencia."""
  doc = coleccion.find_one({"numReferencia": int(ref)})
  if not doc:
    return None
  return _doc_a_producto(doc)

# CREAR

def crear_producto(producto: Producto) -> tuple[bool, Optional[int]]:
  """Crea un nuevo producto asignándole una referencia automática."""
  nueva_ref = obtener_siguiente_referencia()
  producto.numReferencia = nueva_ref

  existe = coleccion.find_one({"numReferencia": int(producto.numReferencia)})
  if existe:
    return False, None

  data = asdict(producto)
  data.pop("_id", None)

  res = coleccion.insert_one(data)
  if res.inserted_id:
    return True, nueva_ref
  return False, None

# ACTUALIZAR
def actualizar_producto(ref: int, data: dict) -> bool:
  """Actualiza los datos de un producto existente asegurando tipos correctos."""
  data.pop("numReferencia", None)

  if "cantidadStock" in data:
    data["cantidadStock"] = _int(data["cantidadStock"])
  if "valorCompra" in data:
    data["valorCompra"] = _int(data["valorCompra"])
  if "valorVenta" in data:
    data["valorVenta"] = _int(data["valorVenta"])

  if "valor" in data:
    # [CAMBIO]: Si llega 'valor' antiguo en un diccionario de actualización, lo distribuimos o removemos para evitar fallos
    val = _int(data["valor"])
    data["valorVenta"] = val
    data.pop("valor", None)

  res = coleccion.update_one({"numReferencia": int(ref)}, {"$set": data})
  return res.modified_count > 0

# ELIMINAR

def eliminar_producto(ref: int) -> bool:
  """Elimina un producto y recicla su número de referencia."""
  res = coleccion.delete_one({"numReferencia": int(ref)})
  if res.deleted_count > 0:
    ref_num = int(ref)
    coleccion_config.update_one(
        {"_id": "referencias_libres"},
        {"$push": {"lista": ref_num}},
        upsert=True,
    )
    doc = coleccion_config.find_one({"_id": "referencias_libres"})
    if doc and "lista" in doc:
      lista_ordenada = sorted(list(set(doc["lista"])))
      coleccion_config.update_one(
          {"_id": "referencias_libres"}, {"$set": {"lista": lista_ordenada}}
      )
  return res.deleted_count > 0

