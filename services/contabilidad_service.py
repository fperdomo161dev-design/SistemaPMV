from database.conexion import get_db
from models.contabilidad import TransaccionContable

db = get_db()
coleccion_contabilidad = db["contabilidad"]


def registrar_transaccion(transaccion: TransaccionContable) -> bool:
  """Inserta una nueva transacción contable en la colección 'contabilidad' de MongoDB."""
  try:
    coleccion_contabilidad.insert_one(transaccion.to_dict())
    return True
  except Exception as e:
    print(f"Error al registrar transacción: {e}")
    return False


def listar_transacciones(tipo_filtro=None) -> list:
  """Lista todas las transacciones o las filtra por tipo ('INGRESO', 'EGRESO', 'SERVICIO')."""
  try:
    query = {"tipo": tipo_filtro} if tipo_filtro else {}
    # Obtenemos los registros excluyendo el campo '_id' de mongo
    return list(coleccion_contabilidad.find(query, {"_id": False}))
  except Exception as e:
    print(f"Error al listar transacciones: {e}")
    return []


def registrar_nomina_en_contabilidad(empleado, neto_pagado: float) -> bool:
  """Registra automáticamente el pago de nómina de un empleado como un EGRESO contable."""
  try:
    transaccion = TransaccionContable(
        tipo="EGRESO",
        categoria="Nómina",
        monto=neto_pagado,
        descripcion=(
            f"Pago de nómina - Empleado: {empleado.nombre}"
            f" {empleado.apellido} (Cédula: {empleado.cedula})"
        ),
        referencia_id=str(empleado.cedula),
    )
    return registrar_transaccion(transaccion)
  except Exception as e:
    print(f"Error al registrar nómina en contabilidad: {e}")
    return False