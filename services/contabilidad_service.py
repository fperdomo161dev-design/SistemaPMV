from datetime import datetime
from database.conexion import get_db

db = get_db()
coleccion_contabilidad = db["contabilidad"]


class ContabilidadService:

  def __init__(self):
    self.db = db
    self.coleccion = coleccion_contabilidad

  # MÉTODOS BASE DE TRANSACCIONES 

  def registrar_transaccion(
      self, tipo, categoria, monto, descripcion, referencia_id=None
  ) -> bool:
    """Inserta una nueva transacción contable directamente como diccionario en MongoDB."""
    try:
      transaccion_dict = {
          "tipo": tipo,
          "categoria": categoria,
          "monto": float(monto or 0.0),
          "descripcion": descripcion,
          "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          "referencia_id": referencia_id,
      }
      self.coleccion.insert_one(transaccion_dict)
      return True
    except Exception as e:
      print(f"Error al registrar transacción: {e}")
      return False

  def listar_transacciones(self, tipo_filtro=None) -> list:
    """Lista todas las transacciones o las filtra por tipo ('INGRESO', 'EGRESO', 'SERVICIO', 'PROVEEDOR')."""
    try:
      query = {"tipo": tipo_filtro.upper()} if tipo_filtro else {}
      return list(self.coleccion.find(query, {"_id": False}))
    except Exception as e:
      print(f"Error al listar transacciones: {e}")
      return []

  # --- MÉTODOS PARA INGRESOS Y VENTAS UNIFICADOS ---

  def obtener_todos_los_ingresos(self, f_inicio=None, f_fin=None) -> list:
    """Unifica las ventas reales del POS, cierres de caja e ingresos manuales aplicando filtrado robusto de fechas."""
    ingresos_unificados = []

    def fecha_en_rango(f_str):
      if not f_inicio or not f_fin:
        return True
      if not f_str:
        return False
      f_date = str(f_str)[:10]
      return f_inicio <= f_date <= f_fin

    try:
      nombres_colecciones = self.db.list_collection_names()
      col_ventas_nombre = next(
          (c for c in ["ventas", "facturas", "pos"] if c in nombres_colecciones),
          "ventas",
      )
      ventas = list(self.db[col_ventas_nombre].find({}, {"_id": False}))

      for v in ventas:
        fecha_v = (
            v.get("fecha_hora")
            or v.get("fecha")
            or v.get("fecha_creacion", "")
        )
        if fecha_en_rango(fecha_v):
          ingresos_unificados.append({
              "fecha": fecha_v,
              "concepto": f"Venta POS Factura #{v.get('num_factura', v.get('numero_factura', v.get('factura_id', 'S/N')))}",
              "categoria": "Venta POS",
              "metodo": v.get("metodo_pago", "Efectivo"),
              "cliente": v.get("cliente_nombre", v.get("cliente", "General")),
              "monto": float(
                  v.get("total", v.get("monto", v.get("valor", 0.0)))
              ),
              "usuario": v.get("vendedor", v.get("usuario", "Admin")),
          })

      if "cierres_caja" in nombres_colecciones:
        cierres = list(self.db["cierres_caja"].find({}, {"_id": False}))
        for c in cierres:
          fecha_c = c.get("fecha", c.get("fecha_cierre", ""))
          if fecha_en_rango(fecha_c):
            ingresos_unificados.append({
                "fecha": fecha_c,
                "concepto": f"Cierre de Caja - {c.get('usuario', 'Cajero')}",
                "categoria": "Cierre de Caja",
                "metodo": "Efectivo",
                "cliente": "N/A",
                "monto": float(c.get("total_ventas", c.get("monto", 0.0))),
                "usuario": c.get("usuario", "Admin"),
            })

      manuales = self.listar_transacciones("INGRESO")
      for m in manuales:
        f_reg = str(m.get("fecha", m.get("fecha_creacion", "")))
        if fecha_en_rango(f_reg):
          ingresos_unificados.append({
              "fecha": f_reg,
              "concepto": m.get(
                  "descripcion", m.get("concepto", "Ingreso Manual")
              ),
              "categoria": m.get("categoria", "Ingreso"),
              "metodo": m.get("metodo_pago", "Efectivo"),
              "cliente": m.get("cliente", "N/A"),
              "monto": float(m.get("monto", 0.0)),
              "usuario": m.get("referencia_id", m.get("usuario", "Admin")),
          })

    except Exception as e:
      print(f"Error al obtener ingresos unificados: {e}")

    return sorted(
        ingresos_unificados, key=lambda x: str(x.get("fecha")), reverse=True
    )

  #  MÉTODOS PARA NÓMINA Y EMPLEADOS 

  def obtener_lista_empleados(self) -> list:
    try:
      return list(self.db["empleados"].find({}, {"_id": False}))
    except Exception as e:
      print(f"Error al obtener empleados: {e}")
      return []

  def registrar_pago_nomina(self, obj_nomina) -> bool:
    try:
      res = self.db["nominas"].insert_one(obj_nomina.to_dict())
      self.registrar_transaccion(
          tipo="EGRESO",
          categoria="Nómina",
          monto=obj_nomina.neto_pagar,
          descripcion=f"Pago Nómina - {obj_nomina.empleado} ({obj_nomina.periodo})",
          referencia_id=str(obj_nomina.cedula),
      )
      return bool(res.inserted_id)
    except Exception as e:
      print(f"Error al registrar nómina: {e}")
      return False

  def obtener_historial_nominas(self) -> list:
    try:
      return list(self.db["nominas"].find({}, {"_id": False}))
    except Exception as e:
      print(f"Error al obtener nóminas: {e}")
      return []

  def eliminar_pago_nomina(self, cedula, fecha, periodo) -> bool:
    try:
      query_nomina = {"cedula": str(cedula), "periodo": periodo}
      if fecha:
        query_nomina["fecha"] = {"$regex": f"^{str(fecha)[:10]}"}
      resultado = self.db["nominas"].delete_one(query_nomina)
      if resultado.deleted_count == 0:
        self.db["nominas"].delete_one(
            {"cedula": str(cedula), "periodo": periodo}
        )
      self.coleccion.delete_many({
          "tipo": "EGRESO",
          "categoria": "Nómina",
          "referencia_id": str(cedula),
      })
      return True
    except Exception as e:
      print(f"Error al eliminar pago de nómina: {e}")
      return False

  def actualizar_pago_nomina(
      self,
      cedula,
      fecha_original,
      periodo_original,
      nuevo_periodo,
      nuevo_salario_base,
      nuevo_sub_transporte,
      nuevo_desc_salud,
      nuevo_desc_pension,
      nuevo_neto,
  ) -> bool:
    try:
      query = {"cedula": str(cedula), "periodo": periodo_original}
      if fecha_original:
        query["fecha"] = {"$regex": f"^{str(fecha_original)[:10]}"}
      actualizacion = {
          "$set": {
              "periodo": nuevo_periodo,
              "salario_base": float(nuevo_salario_base),
              "sub_transporte": float(nuevo_sub_transporte),
              "desc_salud": float(nuevo_desc_salud),
              "desc_pension": float(nuevo_desc_pension),
              "neto_pagar": float(nuevo_neto),
          }
      }
      resultado = self.db["nominas"].update_one(query, actualizacion)
      if resultado.matched_count == 0:
        self.db["nominas"].update_one(
            {"cedula": str(cedula), "periodo": periodo_original}, actualizacion
        )
      self.coleccion.update_many(
          {
              "tipo": "EGRESO",
              "categoria": "Nómina",
              "referencia_id": str(cedula),
          },
          {
              "$set": {
                  "monto": float(nuevo_neto),
                  "descripcion": f"Pago Nómina - Cédula {cedula} ({nuevo_periodo})",
              }
          },
      )
      return True
    except Exception as e:
      print(f"Error al actualizar pago de nómina: {e}")
      return False

  #  MÉTODOS PARA DASHBOARD Y METRICAS 

  def obtener_resumen_dashboard(self, f_inicio=None, f_fin=None) -> dict:
    totales = {
        "ingresos": 0.0,
        "egresos": 0.0,
        "nominas": 0.0,
        "servicios": 0.0,
        "proveedores": 0.0,
    }
    try:
      todos_ingresos = self.obtener_todos_los_ingresos(f_inicio, f_fin)
      totales["ingresos"] = sum(i["monto"] for i in todos_ingresos)

      transacciones = self.coleccion.find()
      for t in transacciones:
        f_trans = str(t.get("fecha", t.get("fecha_creacion", "")))[:10]
        if f_inicio and f_fin:
          if not (f_inicio <= f_trans <= f_fin):
            continue

        tipo = str(t.get("tipo", "")).upper()
        categoria = str(t.get("categoria", "")).lower()
        descripcion = str(t.get("descripcion", "")).lower()
        monto = float(t.get("monto", 0.0))

        if tipo == "EGRESO":
          totales["egresos"] += monto
          if (
              "nómina" in categoria
              or "nomina" in categoria
              or "nómina" in descripcion
              or "nomina" in descripcion
          ):
            totales["nominas"] += monto
          elif (
              "proveedor" in categoria
              or "proveedor" in descripcion
              or "abono" in descripcion
          ):
            totales["proveedores"] += monto
        elif (
            tipo == "SERVICIO"
            or "servicio" in categoria
            or "servicio" in descripcion
        ):
          totales["egresos"] += monto
          totales["servicios"] += monto
        elif tipo == "PROVEEDOR" or "proveedor" in categoria:
          totales["egresos"] += monto
          totales["proveedores"] += monto
    except Exception as e:
      print(f"Error al calcular resumen del dashboard: {e}")

    return totales

  def obtener_ranking_zapatos(self, f_inicio=None, f_fin=None):
    nombres_colecciones = self.db.list_collection_names()
    col_ventas_nombre = next(
        (c for c in ["ventas", "facturas", "pos"] if c in nombres_colecciones),
        None,
    )

    if not col_ventas_nombre:
      return [], []

    def fecha_en_rango(f_str):
      if not f_inicio or not f_fin:
        return True
      if not f_str:
        return True
      return f_inicio <= str(f_str)[:10] <= f_fin

    conteo_zapatos = {}

    try:
      ventas = list(self.db[col_ventas_nombre].find({}, {"_id": False}))
      for v in ventas:
        fecha_v = (
            v.get("fecha_hora")
            or v.get("fecha")
            or v.get("fecha_creacion", "")
        )
        if not fecha_en_rango(fecha_v):
          continue

        items = (
            v.get("productos")
            or v.get("items")
            or v.get("detalles")
            or v.get("cart")
            or v.get("carrito")
        )

        if not items:
          nombre_directo = (
              v.get("nombre")
              or v.get("modelo")
              or v.get("referencia")
              or v.get("producto")
              or v.get("descripcion")
          )
          if nombre_directo and str(nombre_directo).strip() != "":
            items = [v]

        if not items:
          continue

        for item in items:
          if not isinstance(item, dict):
            continue

          nombre = (
              item.get("nombre")
              or item.get("modelo")
              or item.get("referencia")
              or item.get("producto")
              or item.get("descripcion")
              or "Zapato General"
          )

          try:
            cantidad = float(
                item.get("cantidad", item.get("qty", item.get("unidades", 1)))
            )
          except:
            cantidad = 1.0

          nombre_limpio = str(nombre).strip()
          if nombre_limpio:
            conteo_zapatos[nombre_limpio] = (
                conteo_zapatos.get(nombre_limpio, 0.0) + cantidad
            )

      if not conteo_zapatos:
        return [], []

      ordenados_desc = sorted(
          conteo_zapatos.items(), key=lambda x: x[1], reverse=True
      )
      mas_vendidos = [
          (nombre, int(cant) if cant.is_integer() else cant)
          for nombre, cant in ordenados_desc[:5]
      ]

      ordenados_asc = sorted(conteo_zapatos.items(), key=lambda x: x[1])
      menos_vendidos = [
          (nombre, int(cant) if cant.is_integer() else cant)
          for nombre, cant in ordenados_asc[:5]
      ]

      return mas_vendidos, menos_vendidos
    except Exception as e:
      print(f"Error en ranking de zapatos: {e}")
      return [], []

  # HELPERS Y COMPATIBILIDAD UI 

  def registrar_movimiento(
      self, tipo: str, concepto: str, monto: float, usuario: str = "Admin"
  ) -> bool:
    tipo_map = {
        "ingreso": "INGRESO",
        "egreso": "EGRESO",
        "servicio_publico": "SERVICIO",
        "pago_proveedor": "PROVEEDOR",
    }
    tipo_enum = tipo_map.get(tipo.lower(), tipo.upper())
    return self.registrar_transaccion(
        tipo=tipo_enum,
        categoria=tipo_enum.title(),
        monto=monto,
        descripcion=concepto,
        referencia_id=usuario,
    )

  def obtener_todos_movimientos(self) -> list:
    movimientos = []
    for r in self.listar_transacciones():
      movimientos.append({
          "fecha": r.get("fecha", r.get("fecha_creacion", "")),
          "tipo": r.get("tipo", ""),
          "concepto": r.get("descripcion", r.get("concepto", "")),
          "monto": r.get("monto", 0.0),
          "usuario": r.get("referencia_id", r.get("usuario", "Admin")),
      })
    for ing in self.obtener_todos_los_ingresos():
      movimientos.append({
          "fecha": ing.get("fecha", ""),
          "tipo": "INGRESO",
          "concepto": ing.get("concepto", ""),
          "monto": ing.get("monto", 0.0),
          "usuario": ing.get("usuario", "Admin"),
      })
    return sorted(
        movimientos, key=lambda x: str(x.get("fecha")), reverse=True
    )

  def registrar_nomina_en_contabilidad(self, empleado, neto_pagado: float) -> bool:
    try:
      return self.registrar_transaccion(
          tipo="EGRESO",
          categoria="Nómina",
          monto=neto_pagado,
          descripcion=f"Pago de nómina - Empleado: {empleado.nombre} {empleado.apellido} (Cédula: {empleado.cedula})",
          referencia_id=str(empleado.cedula),
      )
    except Exception as e:
      print(f"Error al registrar nómina en contabilidad: {e}")
      return False


# FUNCIONES INDEPENDIENTES PARA RETROCOMPATIBILIDAD (MÓDULO) 


def registrar_transaccion(
    tipo, categoria, monto, descripcion, referencia_id=None
) -> bool:
  return ContabilidadService().registrar_transaccion(
      tipo, categoria, monto, descripcion, referencia_id
  )


def listar_transacciones(tipo_filtro=None) -> list:
  return ContabilidadService().listar_transacciones(tipo_filtro)


def registrar_nomina_en_contabilidad(empleado, neto_pagado: float) -> bool:
  return ContabilidadService().registrar_nomina_en_contabilidad(
      empleado, neto_pagado
  )


def eliminar_pago_nomina(cedula, fecha, periodo) -> bool:
  return ContabilidadService().eliminar_pago_nomina(cedula, fecha, periodo)


def actualizar_pago_nomina(*args, **kwargs) -> bool:
  return ContabilidadService().actualizar_pago_nomina(*args, **kwargs)