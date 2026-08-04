from datetime import datetime


class Factura:

  def __init__(
      self,
      numero_factura: str,
      cliente_cedula: str,
      cliente_nombre: str,
      vendedor_cedula: str,
      vendedor_nombre: str,
      items: list,  # Lista de productos comprados
      subtotal: float,
      impuestos: float,
      total: float,
      puntos_otorgados: int,
      correo_destino: str,
      fecha: str = None,
  ):
    self.numero_factura = numero_factura
    self.cliente_cedula = cliente_cedula
    self.cliente_nombre = cliente_nombre
    self.vendedor_cedula = vendedor_cedula
    self.vendedor_nombre = vendedor_nombre
    self.items = items  # [{'codigo', 'nombre', 'cantidad', 'precio_unitario', 'subtotal'}]
    self.subtotal = subtotal
    self.impuestos = impuestos
    self.total = total
    self.puntos_otorgados = puntos_otorgados
    self.correo_destino = correo_destino
    self.fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  def to_dict(self):
    return {
        "numero_factura": self.numero_factura,
        "cliente_cedula": self.cliente_cedula,
        "cliente_nombre": self.cliente_nombre,
        "vendedor_cedula": self.vendedor_cedula,
        "vendedor_nombre": self.vendedor_nombre,
        "items": self.items,
        "subtotal": self.subtotal,
        "impuestos": self.impuestos,
        "total": self.total,
        "puntos_otorgados": self.puntos_otorgados,
        "correo_destino": self.correo_destino,
        "fecha": self.fecha,
    }