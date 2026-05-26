from dataclasses import dataclass


@dataclass
class Empleado:

    cedula: str
    nombre: str
    cargo: str
    usuario: str
    clave: str