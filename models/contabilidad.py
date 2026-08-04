from datetime import datetime


class TransaccionContable:

  def __init__(
      self,
      tipo,
      categoria,
      monto,
      descripcion,
      fecha=None,
      referencia_id=None,
  ):
    """Modelo unificado para la contabilidad del negocio (Ingresos, Egresos,

    Servicios y Nómina).
    """
    self.tipo = (
        tipo  # "INGRESO", "EGRESO", "SERVICIO", o "MOVIMIENTO" general
    )
    self.categoria = (
        categoria  # Ej. "Venta", "Nómina", "Agua", "Luz", "Internet", etc.
    )
    self.monto = float(monto or 0.0)
    self.descripcion = descripcion
    self.fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self.referencia_id = (
        referencia_id  # ID opcional vinculado (ej. cédula de empleado o factura)
    )

  def to_dict(self):
    """Convierte el objeto a un diccionario compatible con MongoDB."""
    return {
        "tipo": self.tipo,
        "categoria": self.categoria,
        "monto": self.monto,
        "descripcion": self.descripcion,
        "fecha": self.fecha,
        "referencia_id": self.referencia_id,
    }