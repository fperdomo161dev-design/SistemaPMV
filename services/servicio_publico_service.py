from bson import ObjectId
from database.conexion import get_db
from models.servicio_publico import ServicioPublico

db = get_db()
coleccion_servicios = db["servicios_publicos"]
coleccion_egresos = db["egresos"]

class ServicioPublicoService:
    def __init__(self):
        self.coleccion = coleccion_servicios

    def registrar_pago_servicio(self, servicio: ServicioPublico) -> bool:
        try:
            datos = servicio.to_dict()
            # 1. Registrar en servicios_publicos
            res = self.coleccion.insert_one(datos)
            
            # 2. Registrar automáticamente como un egreso general
            coleccion_egresos.insert_one({
                "concepto": f"Pago Servicio: {servicio.tipo_servicio} (Ref: {servicio.referencia or 'N/A'})",
                "monto": servicio.monto,
                "categoria": "Servicios Públicos",
                "metodo_pago": servicio.metodo_pago,
                "origen_id": str(res.inserted_id),
                "fecha": datos["fecha"],
                "hora": datos["hora"]
            })
            return True
        except Exception as e:
            print(f"Error al registrar servicio público: {e}")
            return False

    def obtener_servicios(self, fecha_inicio=None, fecha_fin=None, busqueda="") -> list:
        try:
            query = {}
            if fecha_inicio and fecha_fin:
                query["fecha"] = {"$gte": fecha_inicio, "$lte": fecha_fin}
            elif fecha_inicio:
                query["fecha"] = fecha_inicio

            if busqueda:
                query["$or"] = [
                    {"tipo_servicio": {"$regex": busqueda, "$options": "i"}},
                    {"referencia": {"$regex": busqueda, "$options": "i"}}
                ]

            servicios = list(self.coleccion.find(query).sort("_id", -1))
            for s in servicios:
                s["_id"] = str(s["_id"])
            return servicios
        except Exception as e:
            print(f"Error al obtener servicios: {e}")
            return []

    def eliminar_servicio(self, id_servicio: str) -> bool:
        try:
            self.coleccion.delete_one({"_id": ObjectId(id_servicio)})
            # Eliminar el egreso vinculado si existe
            coleccion_egresos.delete_one({"origen_id": id_servicio})
            return True
        except Exception as e:
            print(f"Error al eliminar servicio: {e}")
            return False