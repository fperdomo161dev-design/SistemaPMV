from datetime import datetime

class Proveedor:
    def __init__(self, nombre, nit_cedula="", telefono="", direccion="", email="", monto_deuda=0.0, abonos=0.0, id_proveedor=None):
        self.id_proveedor = id_proveedor
        self.nombre = nombre
        self.nit_cedula = nit_cedula
        self.telefono = telefono
        self.direccion = direccion
        self.email = email
        self.monto_deuda = float(monto_deuda)
        self.abonos = float(abonos)

    def to_dict(self):
        saldo_restante = max(0.0, self.monto_deuda - self.abonos)
        estado = "PAGADO" if saldo_restante == 0 and self.monto_deuda > 0 else "PENDIENTE"
        
        return {
            "nombre": self.nombre,
            "nit_cedula": self.nit_cedula,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "email": self.email,
            "monto_deuda": self.monto_deuda,
            "abonos": self.abonos,
            "saldo_restante": saldo_restante,
            "estado": estado,
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
        }