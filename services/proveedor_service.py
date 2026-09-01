from datetime import datetime
from bson import ObjectId
from pymongo.errors import PyMongoError


class ProveedorService:
    """Servicio para la gestión de proveedores, cuentas por pagar y abonos en MongoDB."""

    def __init__(self, db):
        self.db = db
        self.collection = self.db["proveedores"] if db is not None else None

    # ============================================================
    # UTILIDADES INTERNAS
    # ============================================================

    def _object_id(self, proveedor_id):
        """Convierte un id a ObjectId de forma segura."""
        try:
            if isinstance(proveedor_id, ObjectId):
                return proveedor_id

            if proveedor_id is None:
                return None

            return ObjectId(str(proveedor_id))
        except Exception:
            return None

    def _numero(self, valor, defecto=0.0):
        """Convierte un valor a float de forma segura."""
        try:
            if valor is None or valor == "":
                return defecto
            return float(valor)
        except (ValueError, TypeError):
            return defecto

    def _normalizar_factura(self, factura):
        """Normaliza una referencia de factura para comparar."""
        if factura is None:
            return ""

        return str(factura).strip().lower()

    def _obtener_proveedor(self, proveedor_id):
        """Obtiene un proveedor usando un id válido."""
        if self.collection is None:
            return None

        oid = self._object_id(proveedor_id)

        if oid is None:
            return None

        return self.collection.find_one({"_id": oid})

    def _recalcular_totales(self, proveedor):
        """
        Recalcula los acumulados globales del proveedor.

        monto_deuda = suma de todas las facturas/pedidos.
        abonos = suma de todos los abonos.
        saldo_restante = deuda total - abonos totales.
        """

        pedidos = proveedor.get("historial_pedidos", []) or []
        abonos = proveedor.get("historial_abonos", []) or []

        monto_deuda = sum(
            self._numero(pedido.get("monto", 0))
            for pedido in pedidos
        )

        total_abonos = sum(
            self._numero(abono.get("monto", 0))
            for abono in abonos
        )

        saldo_restante = max(0.0, monto_deuda - total_abonos)

        return monto_deuda, total_abonos, saldo_restante

    def _guardar_totales(self, proveedor_id, proveedor):
        """Recalcula y guarda los totales globales."""
        if self.collection is None:
            return False

        oid = self._object_id(proveedor_id)

        if oid is None:
            return False

        monto_deuda, total_abonos, saldo_restante = self._recalcular_totales(
            proveedor
        )

        resultado = self.collection.update_one(
            {"_id": oid},
            {
                "$set": {
                    "monto_deuda": monto_deuda,
                    "abonos": total_abonos,
                    "saldo_restante": saldo_restante,
                    "historial_pedidos": proveedor.get(
                        "historial_pedidos", []
                    ),
                    "historial_abonos": proveedor.get(
                        "historial_abonos", []
                    ),
                }
            },
        )

        return resultado.matched_count > 0

    # ============================================================
    # CREAR PROVEEDOR
    # ============================================================

    def crear_proveedor(self, proveedor):
        """Registra un nuevo proveedor en la base de datos."""

        try:
            if self.collection is None:
                return False

            nombre = str(getattr(proveedor, "nombre", "")).strip()
            nit = str(getattr(proveedor, "nit_cedula", "")).strip()

            if not nombre:
                return False

            # Evitar NIT/Cédula duplicado
            if nit:
                existente = self.collection.find_one(
                    {"nit_cedula": nit}
                )

                if existente:
                    return False

            monto_deuda = self._numero(
                getattr(proveedor, "monto_deuda", 0)
            )

            abonos_iniciales = self._numero(
                getattr(proveedor, "abonos", 0)
            )

            if monto_deuda < 0:
                return False

            if abonos_iniciales < 0:
                return False

            if abonos_iniciales > monto_deuda:
                return False

            historial_pedidos = []
            historial_abonos = []

            # ----------------------------------------------------
            # Si nace con deuda inicial, usamos UNA MISMA
            # referencia para que el abono inicial quede asociado.
            # ----------------------------------------------------

            referencia_inicial = "Factura Inicial / Deuda"

            if monto_deuda > 0:
                historial_pedidos.append(
                    {
                        "_id": str(ObjectId()),
                        "fecha": datetime.now().strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "monto": monto_deuda,
                        "factura": referencia_inicial,
                    }
                )

            if abonos_iniciales > 0:
                historial_abonos.append(
                    {
                        "_id": str(ObjectId()),
                        "fecha": datetime.now().strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "monto": abonos_iniciales,
                        "factura": referencia_inicial,
                    }
                )

            doc = {
                "nombre": nombre,
                "nit_cedula": nit,
                "telefono": str(
                    getattr(proveedor, "telefono", "")
                ).strip(),
                "email": str(
                    getattr(proveedor, "email", "")
                ).strip(),
                "direccion": str(
                    getattr(proveedor, "direccion", "")
                ).strip(),
                "monto_deuda": monto_deuda,
                "abonos": abonos_iniciales,
                "saldo_restante": max(
                    0.0,
                    monto_deuda - abonos_iniciales
                ),
                "fecha_creacion": datetime.now().strftime(
                    "%Y-%m-%d"
                ),
                "historial_abonos": historial_abonos,
                "historial_pedidos": historial_pedidos,
            }

            self.collection.insert_one(doc)

            return True

        except PyMongoError as e:
            print(f"Error al crear proveedor: {e}")
            return False

        except Exception as e:
            print(f"Error inesperado al crear proveedor: {e}")
            return False

    # ============================================================
    # OBTENER PROVEEDORES
    # ============================================================

    def obtener_todos(
        self,
        f_inicio=None,
        f_fin=None,
        busqueda=None
    ):
        """Obtiene proveedores aplicando filtros opcionales."""

        try:
            if self.collection is None:
                return []

            query = {}

            if busqueda:
                busqueda = str(busqueda).strip()

                query["$or"] = [
                    {
                        "nombre": {
                            "$regex": busqueda,
                            "$options": "i"
                        }
                    },
                    {
                        "nit_cedula": {
                            "$regex": busqueda,
                            "$options": "i"
                        }
                    },
                ]

            if f_inicio and f_fin:
                query["fecha_creacion"] = {
                    "$gte": f_inicio,
                    "$lte": f_fin
                }

            elif f_inicio:
                query["fecha_creacion"] = {
                    "$gte": f_inicio
                }

            elif f_fin:
                query["fecha_creacion"] = {
                    "$lte": f_fin
                }

            proveedores = list(
                self.collection.find(query)
            )

            for proveedor in proveedores:
                proveedor["_id"] = str(
                    proveedor["_id"]
                )

                # Garantizar estructuras aunque sean datos antiguos
                if not isinstance(
                    proveedor.get("historial_pedidos"),
                    list
                ):
                    proveedor["historial_pedidos"] = []

                if not isinstance(
                    proveedor.get("historial_abonos"),
                    list
                ):
                    proveedor["historial_abonos"] = []

            return proveedores

        except PyMongoError as e:
            print(f"Error al obtener proveedores: {e}")
            return []

        except Exception as e:
            print(f"Error inesperado al obtener proveedores: {e}")
            return []

    # ============================================================
    # OBTENER ABONOS
    # ============================================================

    def obtener_abonos(self, proveedor_id):
        """Retorna todos los abonos de un proveedor."""

        try:
            proveedor = self._obtener_proveedor(proveedor_id)

            if not proveedor:
                return []

            abonos = proveedor.get(
                "historial_abonos",
                []
            )

            return abonos if isinstance(abonos, list) else []

        except Exception as e:
            print(f"Error al obtener abonos: {e}")
            return []

    # ============================================================
    # OBTENER PEDIDOS
    # ============================================================

    def obtener_pedidos(self, proveedor_id):
        """Retorna todas las facturas/pedidos de un proveedor."""

        try:
            proveedor = self._obtener_proveedor(proveedor_id)

            if not proveedor:
                return []

            pedidos = proveedor.get(
                "historial_pedidos",
                []
            )

            return pedidos if isinstance(pedidos, list) else []

        except Exception as e:
            print(f"Error al obtener pedidos: {e}")
            return []

    # ============================================================
    # REGISTRAR ABONO
    # ============================================================

    def registrar_abono(
        self,
        proveedor_id,
        monto,
        nro_factura
    ):
        """
        Registra un abono asociado a una factura específica.

        El abono no puede superar el saldo pendiente de esa factura.
        """

        try:
            if self.collection is None:
                return False

            monto = self._numero(monto)

            if monto <= 0:
                return False

            referencia = (
                str(nro_factura).strip()
                if nro_factura is not None
                else ""
            )

            if not referencia:
                referencia = "Sin Referencia"

            proveedor = self._obtener_proveedor(
                proveedor_id
            )

            if not proveedor:
                return False

            pedidos = proveedor.get(
                "historial_pedidos",
                []
            ) or []

            abonos = proveedor.get(
                "historial_abonos",
                []
            ) or []

            # Buscar factura
            pedido = next(
                (
                    p
                    for p in pedidos
                    if self._normalizar_factura(
                        p.get("factura")
                    )
                    == self._normalizar_factura(
                        referencia
                    )
                ),
                None
            )

            # Si existe una factura específica,
            # validar su saldo.
            if pedido:

                monto_factura = self._numero(
                    pedido.get("monto", 0)
                )

                abonado_factura = sum(
                    self._numero(abono.get("monto", 0))
                    for abono in abonos
                    if self._normalizar_factura(
                        abono.get("factura")
                    )
                    == self._normalizar_factura(
                        referencia
                    )
                )

                saldo_factura = max(
                    0.0,
                    monto_factura - abonado_factura
                )

                if monto > saldo_factura:
                    return False

            # ----------------------------------------------------
            # Crear abono
            # ----------------------------------------------------

            nuevo_abono = {
                "_id": str(ObjectId()),
                "fecha": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "monto": monto,
                "factura": referencia,
            }

            abonos.append(nuevo_abono)

            proveedor["historial_abonos"] = abonos

            return self._guardar_totales(
                proveedor_id,
                proveedor
            )

        except PyMongoError as e:
            print(f"Error al registrar abono: {e}")
            return False

        except Exception as e:
            print(f"Error inesperado al registrar abono: {e}")
            return False

    # ============================================================
    # ACTUALIZAR ABONO
    # ============================================================

    def actualizar_abono(
        self,
        proveedor_id,
        abono_id,
        nuevo_monto,
        nueva_factura
    ):
        """Actualiza un abono específico y recalcula los saldos."""

        try:
            if self.collection is None:
                return False

            nuevo_monto = self._numero(
                nuevo_monto
            )

            if nuevo_monto <= 0:
                return False

            proveedor = self._obtener_proveedor(
                proveedor_id
            )

            if not proveedor:
                return False

            abonos = proveedor.get(
                "historial_abonos",
                []
            ) or []

            pedidos = proveedor.get(
                "historial_pedidos",
                []
            ) or []

            nueva_factura = (
                str(nueva_factura).strip()
                if nueva_factura is not None
                else ""
            )

            if not nueva_factura:
                nueva_factura = "Sin Referencia"

            abono_encontrado = None

            for abono in abonos:

                if str(abono.get("_id")) == str(abono_id):
                    abono_encontrado = abono
                    break

            if abono_encontrado is None:
                return False

            # ----------------------------------------------------
            # Validar que la nueva factura exista.
            # ----------------------------------------------------

            pedido_destino = next(
                (
                    p
                    for p in pedidos
                    if self._normalizar_factura(
                        p.get("factura")
                    )
                    == self._normalizar_factura(
                        nueva_factura
                    )
                ),
                None
            )

            if pedido_destino:

                monto_factura = self._numero(
                    pedido_destino.get("monto", 0)
                )

                abonado_otros = sum(
                    self._numero(ab.get("monto", 0))
                    for ab in abonos
                    if str(ab.get("_id")) != str(abono_id)
                    and self._normalizar_factura(
                        ab.get("factura")
                    )
                    == self._normalizar_factura(
                        nueva_factura
                    )
                )

                saldo_disponible = max(
                    0.0,
                    monto_factura - abonado_otros
                )

                if nuevo_monto > saldo_disponible:
                    return False

            # Actualizar
            abono_encontrado["monto"] = nuevo_monto
            abono_encontrado["factura"] = nueva_factura

            proveedor["historial_abonos"] = abonos

            return self._guardar_totales(
                proveedor_id,
                proveedor
            )

        except PyMongoError as e:
            print(f"Error al actualizar abono: {e}")
            return False

        except Exception as e:
            print(f"Error inesperado al actualizar abono: {e}")
            return False

    # ============================================================
    # ELIMINAR ABONO
    # ============================================================

    def eliminar_abono(
        self,
        proveedor_id,
        abono_id
    ):
        """Elimina un abono específico y recalcula los totales."""

        try:
            if self.collection is None:
                return False

            proveedor = self._obtener_proveedor(
                proveedor_id
            )

            if not proveedor:
                return False

            abonos = proveedor.get(
                "historial_abonos",
                []
            ) or []

            abonos_filtrados = [
                abono
                for abono in abonos
                if str(abono.get("_id"))
                != str(abono_id)
            ]

            if len(abonos) == len(abonos_filtrados):
                return False

            proveedor["historial_abonos"] = (
                abonos_filtrados
            )

            return self._guardar_totales(
                proveedor_id,
                proveedor
            )

        except PyMongoError as e:
            print(f"Error al eliminar abono: {e}")
            return False

        except Exception as e:
            print(f"Error inesperado al eliminar abono: {e}")
            return False

    # ============================================================
    # ELIMINAR PROVEEDOR
    # ============================================================

    def eliminar_proveedor(self, proveedor_id):
        """Elimina completamente un proveedor."""

        try:
            if self.collection is None:
                return False

            oid = self._object_id(proveedor_id)

            if oid is None:
                return False

            resultado = self.collection.delete_one(
                {"_id": oid}
            )

            return resultado.deleted_count > 0

        except PyMongoError as e:
            print(f"Error al eliminar proveedor: {e}")
            return False

        except Exception as e:
            print(f"Error inesperado al eliminar proveedor: {e}")
            return False

    # ============================================================
    # REGISTRAR PEDIDO / FACTURA
    # ============================================================

    def registrar_pedido(
        self,
        proveedor_id,
        monto,
        nro_factura
    ):
        """
        Registra una nueva factura/pedido.

        La deuda total se recalcula a partir del historial
        de facturas, evitando inconsistencias acumulativas.
        """

        try:
            if self.collection is None:
                return False

            monto = self._numero(monto)

            if monto <= 0:
                return False

            referencia = (
                str(nro_factura).strip()
                if nro_factura is not None
                else ""
            )

            if not referencia:
                return False

            proveedor = self._obtener_proveedor(
                proveedor_id
            )

            if not proveedor:
                return False

            pedidos = proveedor.get(
                "historial_pedidos",
                []
            ) or []

            # ----------------------------------------------------
            # Evitar dos facturas iguales para el mismo proveedor.
            # ----------------------------------------------------

            factura_ya_existe = any(
                self._normalizar_factura(
                    pedido.get("factura")
                )
                == self._normalizar_factura(
                    referencia
                )
                for pedido in pedidos
            )

            if factura_ya_existe:
                return False

            nuevo_pedido = {
                "_id": str(ObjectId()),
                "fecha": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "monto": monto,
                "factura": referencia,
            }

            pedidos.append(nuevo_pedido)

            proveedor["historial_pedidos"] = pedidos

            return self._guardar_totales(
                proveedor_id,
                proveedor
            )

        except PyMongoError as e:
            print(f"Error al registrar pedido: {e}")
            return False

        except Exception as e:
            print(f"Error inesperado al registrar pedido: {e}")
            return False