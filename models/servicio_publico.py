from datetime import datetime

class ServicioPublico:
    def __init__(self, tipo_servicio, monto, referencia="", metodo_pago="Efectivo", fecha=None, hora=None, _id=None):
        self._id = _id
        self.tipo_servicio = tipo_servicio
        self.monto = float(monto)
        self.referencia = referencia
        self.metodo_pago = metodo_pago
        
        ahora = datetime.now()
        self.fecha = fecha if fecha else ahora.strftime("%Y-%m-%d")
        self.hora = hora if hora else ahora.strftime("%H:%M:%S")

    def to_dict(self):
        datos = {
            "tipo_servicio": self.tipo_servicio,
            "monto": self.monto,
            "referencia": self.referencia,
            "metodo_pago": self.metodo_pago,
            "fecha": self.fecha,
            "hora": self.hora
        }
        if self._id:
            datos["_id"] = self._id
        return datos

    @classmethod
    def from_dict(cls, datos):
        return cls(
            tipo_servicio=datos.get("tipo_servicio"),
            monto=datos.get("monto", 0.0),
            referencia=datos.get("referencia", ""),
            metodo_pago=datos.get("metodo_pago", "Efectivo"),
            fecha=datos.get("fecha"),
            hora=datos.get("hora"),
            _id=str(datos.get("_id")) if datos.get("_id") else None
        )