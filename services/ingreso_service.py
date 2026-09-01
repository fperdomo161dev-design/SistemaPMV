from bson import ObjectId
from database.conexion import get_db
from models.ingreso import Ingreso

db = get_db()
coleccion_ingresos = db["ingresos"]


class IngresoService:

    def __init__(self):
        self.db = db
        self.coleccion = coleccion_ingresos

    def registrar_ingreso(self, ingreso: Ingreso) -> bool:
        try:
            self.coleccion.insert_one(ingreso.to_dict())
            return True
        except Exception as e:
            print(f"Error al registrar ingreso: {e}")
            return False

    def obtener_ingresos(
        self, fecha_inicio=None, fecha_fin=None, busqueda=""
    ) -> list:
        try:
            todos_ingresos = []

            # 1. Traer ventas del POS
            ventas = list(self.db["ventas"].find())
            for v in ventas:
                num_factura = v.get("num_factura", v.get("numero_factura", "S/N"))
                todos_ingresos.append(
                    {
                        "_id": str(v.get("_id", "")),
                        "fecha": str(v.get("fecha_hora") or v.get("fecha", "")),
                        "concepto": f"Venta POS Factura #{num_factura}",
                        "categoria": "Venta POS",
                        "metodo": v.get("metodo_pago", "Efectivo"),
                        "cliente": v.get(
                            "cliente_nombre", v.get("cliente", "Cliente General")
                        ),
                        "monto": float(v.get("total", v.get("monto", 0.0))),
                    }
                )

            # 2. Traer cierres de caja
            cierres = list(self.db["cierres_caja"].find())
            for c in cierres:
                usuario = c.get("usuario", "Cajero")
                todos_ingresos.append(
                    {
                        "_id": str(c.get("_id", "")),
                        "fecha": str(c.get("fecha", c.get("fecha_cierre", ""))),
                        "concepto": f"Cierre de Caja - {usuario}",
                        "categoria": "Cierre de Caja",
                        "metodo": "Efectivo",
                        "cliente": "N/A",
                        "monto": float(
                            c.get("total_ventas", c.get("monto", 0.0))
                        ),
                    }
                )

            # 3. Traer ingresos manuales registrados
            manuales = list(self.coleccion.find())
            for m in manuales:
                todos_ingresos.append(
                    {
                        "_id": str(m.get("_id", "")),
                        "fecha": str(m.get("fecha", m.get("fecha_creacion", ""))),
                        "concepto": m.get("concepto", m.get("descripcion", "")),
                        "categoria": m.get("categoria", "Ingreso Manual"),
                        "metodo": m.get("metodo", m.get("metodo_pago", "Efectivo")),
                        "cliente": m.get("cliente", "N/A"),
                        "monto": float(m.get("monto", 0.0)),
                    }
                )

            # --- FILTROS DE BÚSQUEDA Y FECHA EN MEMORIA ---
            resultado_filtrado = []
            busqueda_lower = busqueda.strip().lower()

            for item in todos_ingresos:
                # Filtrado por rango de fechas (comparación textual de prefijos YYYY-MM-DD)
                fecha_item = item["fecha"][:10]
                if fecha_inicio and fecha_fin:
                    if not (fecha_inicio <= fecha_item <= fecha_fin):
                        continue
                elif fecha_inicio:
                    if fecha_item != fecha_inicio:
                        continue

                # Filtrado por término de búsqueda (concepto, cliente o categoría)
                if busqueda_lower:
                    match_concepto = (
                        busqueda_lower in item["concepto"].lower()
                    )
                    match_cliente = (
                        busqueda_lower in item["cliente"].lower()
                    )
                    match_categoria = (
                        busqueda_lower in item["categoria"].lower()
                    )
                    if not (match_concepto or match_cliente or match_categoria):
                        continue

                resultado_filtrado.append(item)

            # Ordenar por fecha de más reciente a más antigua
            return sorted(
                resultado_filtrado, key=lambda x: x["fecha"], reverse=True
            )

        except Exception as e:
            print(f"Error al obtener ingresos: {e}")
            return []

    def eliminar_ingreso(self, id_ingreso: str) -> bool:
        try:
            self.coleccion.delete_one({"_id": ObjectId(id_ingreso)})
            return True
        except Exception as e:
            print(f"Error al eliminar ingreso: {e}")
            return False