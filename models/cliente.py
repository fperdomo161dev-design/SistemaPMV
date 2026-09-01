from dataclasses import dataclass

@dataclass
class Cliente:
    cedula: str
    nombre: str
    apellido: str
    correo: str
    celular: str
    direccion: str = ""  
    puntos: int = 0      