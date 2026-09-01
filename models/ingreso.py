from datetime import datetime

class Ingreso:
    def __init__(self, concepto, monto, categoria="Venta", metodo_pago="Efectivo", cliente="", id_ingreso=None):
        self.id_ingreso = id_ingreso
        self.concepto = concepto
        self.monto = float(monto)
        self.categoria = categoria  
        self.metodo_pago = metodo_pago  
        self.cliente = cliente

    def to_dict(self):
        return {
            "concepto": self.concepto,
            "monto": self.monto,
            "categoria": self.categoria,
            "metodo_pago": self.metodo_pago,
            "cliente": self.cliente,
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "hora": datetime.now().strftime("%H:%M:%S")
        }