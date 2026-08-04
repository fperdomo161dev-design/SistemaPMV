from dataclasses import dataclass

@dataclass
class Empleado:
    cedula: str
    nombre: str
    apellido: str = ""
    cargo: str = ""
    correo: str = ""
    celular: str = ""
    usuario: str = ""
    clave: str = ""
    tipo_pago: str = "FIJO"
    salario: float = 0.0
    tarifa_diaria: float = 0.0
    sub_transporte: float = 0.0
    pct_salud: float = 0.04
    pct_pension: float = 0.04
    pct_arl: float = 0.0
    pct_parafiscales: float = 0.09
    dias_mes: int = 30                             #edit