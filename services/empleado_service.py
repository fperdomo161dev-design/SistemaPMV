# services/empleado_service.py

from dataclasses import asdict
from typing import List, Optional

from database.conexion import get_db
from models.empleado import Empleado
from services.contabilidad_service import \
    registrar_nomina_en_contabilidad  # <- Importamos el servicio de contabilidad
from services.security_service import hash_password, verify_password

db = get_db()

coleccion = db["empleados"]

# CONVERTIR DOCUMENTO A EMPLEADO


def _doc_a_empleado(doc):
  return Empleado(
      cedula=str(doc.get("cedula", "")),
      nombre=str(doc.get("nombre", "")),
      apellido=str(doc.get("apellido", "")),
      cargo=str(doc.get("cargo", "")),
      correo=str(doc.get("correo", "")),
      celular=str(doc.get("celular", "")),
      usuario=str(doc.get("usuario", "")),
      clave=str(doc.get("clave", "")),
      tipo_pago=str(doc.get("tipo_pago", "FIJO")),
      salario=float(doc.get("salario", 0.0)),
      tarifa_diaria=float(doc.get("tarifa_diaria", 0.0)),
      sub_transporte=float(doc.get("sub_transporte", 0.0)),
      pct_salud=float(doc.get("pct_salud", 0.04)),
      pct_pension=float(doc.get("pct_pension", 0.04)),
      pct_arl=float(doc.get("pct_arl", 0.0)),
      pct_parafiscales=float(doc.get("pct_parafiscales", 0.09)),
      dias_mes=int(doc.get("dias_mes", 30)),
  )


# LISTAR


def listar_empleados() -> List[Empleado]:
  empleados = []
  for doc in coleccion.find().sort("nombre", 1):
    empleados.append(_doc_a_empleado(doc))

  return empleados


# CREAR
def crear_empleado(empleado_data) -> bool:
  # Acepta tanto un objeto Empleado como un diccionario directo
  if isinstance(empleado_data, Empleado):
    data = asdict(empleado_data)
    emp_obj = empleado_data
  else:
    data = empleado_data
    # Reconstruimos temporalmente el objeto para usarlo en contabilidad
    emp_obj = Empleado(**data)

  existe = coleccion.find_one({"cedula": data.get("cedula")})
  if existe:
    return False

  if "clave" in data and data["clave"]:
    data["clave"] = hash_password(data["clave"])

  res = coleccion.insert_one(data)
  if res.inserted_id:
    # Registro automático del egreso en contabilidad si tiene un salario asignado
    if emp_obj.salario > 0:
      registrar_nomina_en_contabilidad(emp_obj, emp_obj.salario)
    return True

  return False


# BUSCAR POR CÉDULA
def buscar_empleado_por_cedula(cedula: str) -> Optional[Empleado]:
  doc = coleccion.find_one({"cedula": cedula})

  if not doc:
    return None

  return _doc_a_empleado(doc)


# BUSCAR POR USUARIO


def buscar_empleado_por_usuario(usuario: str) -> Optional[Empleado]:
  doc = coleccion.find_one({"usuario": usuario})

  if not doc:
    return None

  return _doc_a_empleado(doc)


# LOGIN


def validar_credenciales(usuario: str, clave: str) -> Optional[Empleado]:
  empleado = buscar_empleado_por_usuario(usuario)

  if not empleado:
    return None

  if not verify_password(clave, empleado.clave):
    return None

  return empleado


# ACTUALIZAR


def actualizar_empleado(cedula: str, data: dict) -> bool:
  cedula = str(cedula).strip()

  if "clave" in data and data["clave"]:
    data["clave"] = hash_password(data["clave"])

  res = coleccion.update_one(
      {"cedula": cedula},
      {"$set": data},
  )

  return res.matched_count > 0


# ELIMINAR


def eliminar_empleado(cedula: str) -> bool:
  cedula = str(cedula).strip()

  res = coleccion.delete_one({"cedula": cedula})

  return res.deleted_count > 0