from database.conexion import get_db
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class FacturaPDFService:

  @staticmethod
  def _obtener_configuracion_bd():
    """Busca la configuración en MongoDB; si no existe, devuelve valores por defecto."""
    try:
      db = get_db()
      config_db = db["config_sistema"].find_one({"tipo": "datos_empresa"})
      if config_db:
        return {
            "empresa_nombre": config_db.get(
                "nombre", "PMV - INVENTARIO Y ZAPATERÍA"
            ),
            "empresa_subtitulo": config_db.get(
                "subtitulo", "Factura Electrónica de Venta"
            ),
            "mensaje_ecologico": config_db.get(
                "mensaje_ecologico",
                "GRACIAS POR CUIDAR EL PLANETA. ESTA FACTURA ES DIGITAL.",
            ),
            "texto_puntos": config_db.get(
                "texto_puntos",
                "Puntos ecológicos otorgados en esta compra: +{puntos} Puntos",
            ),
            "color_encabezado": config_db.get("color_encabezado", "#0A0D12"),
        }
    except Exception:
      pass

    return {
        "empresa_nombre": "PMV - INVENTARIO Y ZAPATERÍA",
        "empresa_subtitulo": "Factura Electrónica de Venta",
        "mensaje_ecologico": (
            "GRACIAS POR CUIDAR EL PLANETA. ESTA FACTURA ES DIGITAL."
        ),
        "texto_puntos": (
            "Puntos ecológicos otorgados en esta compra: +{puntos} Puntos"
        ),
        "color_encabezado": "#0A0D12",
    }

  @staticmethod
  def _hex_a_rgb(hex_str):
    """Convierte un color hexadecimal (ej. #F59E0B) a valores flotantes RGB de 0 a 1."""
    hex_str = hex_str.lstrip("#")
    try:
      if len(hex_str) != 6:
        return (0.04, 0.07, 0.12)
      return tuple(int(hex_str[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    except Exception:
      return (0.04, 0.07, 0.12)

  @staticmethod
  def _dibujar_encabezado(c, width, height, factura_data, config_pdf=None):
    """Dibuja la franja de encabezado superior corporativo con soporte para configuración dinámica y color personalizado."""
    if config_pdf is None:
      config_pdf = FacturaPDFService._obtener_configuracion_bd()

    color_hex = config_pdf.get("color_encabezado", "#0A0D12")
    r, g, b = FacturaPDFService._hex_a_rgb(color_hex)

    c.setFillColorRGB(r, g, b)
    c.rect(0, height - 100, width, 100, fill=1, stroke=0)

    c.setFillColorRGB(0.95, 0.62, 0.04)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(
        40,
        height - 45,
        config_pdf.get("empresa_nombre", "PMV - INVENTARIO Y ZAPATERÍA"),
    )

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica", 10)
    c.drawString(
        40,
        height - 65,
        config_pdf.get("empresa_subtitulo", "Factura Electrónica de Venta"),
    )

    num_fac = factura_data.get("numero_factura") or factura_data.get(
        "numero", "N/A"
    )

    c.drawRightString(width - 40, height - 45, f"Factura N°: {num_fac}")

    fecha = factura_data.get("fecha", "N/A")
    if hasattr(fecha, "strftime"):
      fecha_str = fecha.strftime("%Y-%m-%d %H:%M")
    elif isinstance(fecha, str):
      fecha_str = fecha
    else:
      fecha_str = str(fecha)

    c.drawRightString(width - 40, height - 65, f"Fecha: {fecha_str}")

  @staticmethod
  def generar_pdf(factura_data, ruta_salida=None, config_personalizada=None):
    """Genera el documento PDF consultando siempre los datos más frescos de la BD o usando la config provista."""
    if config_personalizada and isinstance(config_personalizada, dict):
      config_pdf = FacturaPDFService._obtener_configuracion_bd()
      config_pdf.update(config_personalizada)
    else:
      config_pdf = FacturaPDFService._obtener_configuracion_bd()

    if ruta_salida is None:
      os.makedirs("facturas", exist_ok=True)
      numero = factura_data.get("numero_factura", "SIN_NUMERO")
      ruta_salida = os.path.join("facturas", f"{numero}.pdf")

    c = canvas.Canvas(ruta_salida, pagesize=letter)
    width, height = letter

    FacturaPDFService._dibujar_encabezado(
        c, width, height, factura_data, config_pdf
    )

    # --- DATOS CLIENTE ---
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, height - 130, "DATOS DEL CLIENTE:")

    c.setFont("Helvetica", 10)
    nom_cli = (
        factura_data.get("cliente_nombre")
        or factura_data.get("cliente", {}).get("nombre", "Consumidor Final")
    )
    ced_cli = (
        factura_data.get("cliente_cedula")
        or factura_data.get("cliente", {}).get("cedula", "222222222222")
    )

    c.drawString(40, height - 145, f"Nombre: {nom_cli}")
    c.drawString(40, height - 160, f"Cédula/NIT: {ced_cli}")

    # DATOS VENDEDOR 
    c.setFont("Helvetica-Bold", 11)
    c.drawString(320, height - 130, "DATOS DEL VENDEDOR:")

    c.setFont("Helvetica", 10)
    c.drawString(
        320,
        height - 145,
        f"Vendedor: {factura_data.get('vendedor_nombre') or 'Admin'}",
    )
    c.drawString(
        320,
        height - 160,
        f"Cédula: {factura_data.get('vendedor_cedula') or 'N/A'}",
    )

    # TABLA DE PRODUCTOS 
    y = height - 210
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.rect(40, y - 5, width - 80, 20, fill=1, stroke=0)

    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "CÓDIGO")
    c.drawString(130, y, "PRODUCTO")
    c.drawString(320, y, "CANT.")
    c.drawString(390, y, "PRECIO UNIT.")
    c.drawString(490, y, "SUBTOTAL")

    y -= 25
    c.setFont("Helvetica", 9)
    items = factura_data.get("items", [])

    for item in items:
      codigo = str(item.get("codigo", item.get("numReferencia", "")))[:12]
      nombre = str(item.get("nombre", item.get("producto", "Producto")))[:28]

      try:
        cantidad = int(item.get("cantidad", item.get("cant", 1)))
      except (ValueError, TypeError):
        cantidad = 1

      try:
        precio_unit = float(
            item.get(
                "precio_unitario",
                item.get(
                    "precio", item.get("validadorVenta", item.get("valorVenta", 0.0))
                ),
            )
        )
      except (ValueError, TypeError):
        precio_unit = 0.0

      try:
        subtotal = float(item.get("subtotal", cantidad * precio_unit))
      except (ValueError, TypeError):
        subtotal = cantidad * precio_unit

      c.drawString(50, y, codigo)
      c.drawString(130, y, nombre)
      c.drawString(330, y, str(cantidad))
      c.drawString(390, y, f"$ {precio_unit:,.2f}")
      c.drawString(490, y, f"$ {subtotal:,.2f}")

      y -= 20
      if y < 140:
        c.showPage()
        FacturaPDFService._dibujar_encabezado(
            c, width, height, factura_data, config_pdf
        )
        y = height - 140
        c.setFont("Helvetica", 9)

    # TOTAL 
    y -= 10
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(40, y, width - 40, y)

    y -= 25
    c.setFont("Helvetica-Bold", 12)
    try:
      total = float(factura_data.get("total", 0.0))
    except (ValueError, TypeError):
      total = 0.0

    c.drawRightString(width - 40, y, f"TOTAL A PAGAR: $ {total:,.2f}")

    #  BLOQUE ECOLÓGICO / PUNTOS 
    y -= 50
    if y < 60:
      c.showPage()
      y = height - 100

    c.setFillColorRGB(0.06, 0.45, 0.25)
    c.rect(40, y - 10, width - 80, 45, fill=1, stroke=0)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 10)
    msg_eco = config_pdf.get("mensaje_ecologico")
    c.drawString(50, y + 15, msg_eco)

    c.setFont("Helvetica", 9)
    puntos = factura_data.get("puntos_otorgados", 0)
    plantilla_puntos = config_pdf.get("texto_puntos")
    texto_puntos_final = plantilla_puntos.format(puntos=puntos)

    c.drawString(50, y, texto_puntos_final)
    c.save()

    return ruta_salida