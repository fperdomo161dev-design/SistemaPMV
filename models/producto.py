from dataclasses import dataclass


@dataclass
class Producto:

    numReferencia: int
    marca: str
    talla: str
    color: str
    cantidadStock: int
    valor: int
    ubicacion: str