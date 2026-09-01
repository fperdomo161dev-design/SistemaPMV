from datetime import datetime

class Nomina:
    def __init__(self, cedula, empleado, salario_base, sub_transporte, desc_salud, desc_pension, neto_pagar, periodo="", _id=None, fecha=None, hora=None):
        self._id = _id
        self.cedula = cedula
        self.empleado = empleado
        self.salario_base = float(salario_base)
        self.sub_transporte = float(sub_transporte)
        self.desc_salud = float(desc_salud)
        self.desc_pension = float(desc_pension)
        self.neto_pagar = float(neto_pagar)
        self.periodo = periodo
        
        ahora = datetime.now()
        self.fecha = fecha if fecha else ahora.strftime("%Y-%m-%d")
        self.hora = hora if hora else ahora.strftime("%H:%M:%S")

    def to_dict(self):
        datos = {
            "cedula": self.cedula,
            "empleado": self.empleado,
            "salario_base": self.salario_base,
            "sub_transporte": self.sub_transporte,
            "desc_salud": self.desc_salud,
            "desc_pension": self.desc_pension,
            "neto_pagar": self.neto_pagar,
            "periodo": self.periodo,
            "fecha": self.fecha,
            "hora": self.hora
        }
        if self._id:
            datos["_id"] = self._id
        return datos