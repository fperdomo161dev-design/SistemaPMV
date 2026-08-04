from database.conexion import get_db
from models.contabilidad import TransaccionContable
from models.factura import Factura
from services.contabilidad_service import registrar_transaccion

db = get_db()
coleccion_facturas = db["facturas"]
coleccion_productos = db["productos"]


def generar_numero_factura() -> str:
  """Genera un número de factura consecutivo basado en el conteo actual."""
  try:
    conteo = coleccion_facturas.count_documents({})
    return f"FAC-{conteo + 1:06d}"
  except Exception:
    return "FAC-000001"


def registrar_venta(
    cliente, vendedor, carrito_items: list, total_venta: float, correo_envio: str
) -> tuple[bool, str]:
  """Registra la venta, actualiza inventario, genera contabilidad y retorna (Exito, NumFactura)."""
  try:
    num_fac = generar_numero_factura()
    puntos = int(
        total_venta / 10000
    )  

    # Procesar items y descontar stock del inventario
    items_procesados = []
    for item in carrito_items:
      # item = {'codigo':..., 'nombre':..., 'cantidad':..., 'precio':...}
      sub_item = item["cantidad"] * item["precio"]
      items_procesados.append({
          "codigo": item.get("codigo"),
          "nombre": item.get("nombre"),
          "cantidad": item["cantidad"],
          "precio_unitario": item["precio"],
          "subtotal": sub_item,
      })

      # Descontar del inventario de productos
      coleccion_productos.update_one(
          {"codigo": item.get("codigo")},
          {"$inc": {"stock": -item["cantidad"]}},
      )

    # Crear objeto Factura
    factura = Factura(
        numero_factura=num_fac,
        cliente_cedula=getattr(cliente, "cedula", "CONSUMIDOR_FINAL"),
        cliente_nombre=(
            f"{getattr(cliente, 'nombre', '')} {getattr(cliente, 'apellido', '')}".strip()
            or "Cliente General"
        ),
        vendedor_cedula=getattr(vendedor, "cedula", "000"),
        vendedor_nombre=f"{vendedor.nombre} {vendedor.apellido}",
        items=items_procesados,
        subtotal=total_venta,  # Ajustar impuestos si manejas IVA separado
        impuestos=0.0,
        total=total_venta,
        puntos_otorgados=puntos,
        correo_destino=correo_envio or getattr(cliente, "correo", ""),
    )

    # Guardar factura en MongoDB
    coleccion_facturas.insert_one(factura.to_dict())

    # Registrar automáticamente en Contabilidad como INGRESO
    transaccion_contable = TransaccionContable(
        tipo="INGRESO",
        categoria="Ventas POS",
        monto=total_venta,
        descripcion=(
            f"Venta Factura {num_fac} - Cliente: {factura.cliente_nombre}"
        ),
        referencia_id=num_fac,
    )
    registrar_transaccion(transaccion_contable)

    return True, num_fac

  except Exception as e:
    print(f"Error al registrar venta: {e}")
    return False, str(e)