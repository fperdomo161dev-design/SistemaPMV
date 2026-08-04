from dataclasses import dataclass




@dataclass
class Producto:
  numReferencia: int
  marca: str
  talla: str
  color: str
  cantidadStock: int
  valorCompra: int  # [CAMBIO]: Añadido atributo para el precio de compra
  valorVenta: int  # [CAMBIO]: Añadido atributo para el precio de venta
  ubicacion: str