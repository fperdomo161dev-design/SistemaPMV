import os
import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class FacturaPDFService:

    @staticmethod
    def _dibujar_encabezado(c, width, height, factura_data):
        """Dibuja la franja de encabezado superior corporativo."""
        c.setFillColorRGB(0.04, 0.07, 0.12)
        c.rect(0, height - 100, width, 100, fill=1, stroke=0)

        c.setFillColorRGB(0.95, 0.62, 0.04)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(40, height - 45, "PMV - INVENTARIO Y ZAPATERÍA")

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 65, "Factura Electrónica de Venta")

        num_fac = factura_data.get("numero_factura") or factura_data.get(
            "numero",
            "N/A"
        )

        c.drawRightString(
            width - 40,
            height - 45,
            f"Factura N°: {num_fac}"
        )

        fecha = factura_data.get("fecha", "N/A")

        if hasattr(fecha, "strftime"):
            fecha_str = fecha.strftime("%Y-%m-%d %H:%M")
        elif isinstance(fecha, str):
            fecha_str = fecha
        else:
            fecha_str = str(fecha)

        c.drawRightString(
            width - 40,
            height - 65,
            f"Fecha: {fecha_str}"
        )

    @staticmethod
    def generar_pdf(factura_data, ruta_salida=None):
        """Genera el documento PDF con diseño corporativo y soporte multipágina."""

        if ruta_salida is None:
            os.makedirs("facturas", exist_ok=True)

            numero = factura_data.get(
                "numero_factura",
                "SIN_NUMERO"
            )

            ruta_salida = os.path.join(
                "facturas",
                f"{numero}.pdf"
            )

        c = canvas.Canvas(
            ruta_salida,
            pagesize=letter
        )

        width, height = letter

        FacturaPDFService._dibujar_encabezado(
            c,
            width,
            height,
            factura_data
        )

        # ==========================
        # DATOS CLIENTE
        # ==========================

        c.setFillColorRGB(0.1, 0.1, 0.1)

        c.setFont("Helvetica-Bold", 11)
        c.drawString(
            40,
            height - 130,
            "DATOS DEL CLIENTE:"
        )

        c.setFont("Helvetica", 10)

        nom_cli = factura_data.get("cliente_nombre") or factura_data.get(
            "cliente",
            {}
        ).get(
            "nombre",
            "Consumidor Final"
        )

        ced_cli = factura_data.get("cliente_cedula") or factura_data.get(
            "cliente",
            {}
        ).get(
            "cedula",
            "222222222222"
        )

        c.drawString(
            40,
            height - 145,
            f"Nombre: {nom_cli}"
        )

        c.drawString(
            40,
            height - 160,
            f"Cédula/NIT: {ced_cli}"
        )

        # ==========================
        # DATOS VENDEDOR
        # ==========================

        c.setFont("Helvetica-Bold", 11)

        c.drawString(
            320,
            height - 130,
            "DATOS DEL VENDEDOR:"
        )

        c.setFont("Helvetica", 10)

        c.drawString(
            320,
            height - 145,
            f"Vendedor: {factura_data.get('vendedor_nombre') or 'Admin'}"
        )

        c.drawString(
            320,
            height - 160,
            f"Cédula: {factura_data.get('vendedor_cedula') or 'N/A'}"
        )

        # ==========================
        # TABLA DE PRODUCTOS
        # ==========================

        y = height - 210

        c.setFillColorRGB(
            0.95,
            0.95,
            0.95
        )

        c.rect(
            40,
            y - 5,
            width - 80,
            20,
            fill=1,
            stroke=0
        )

        c.setFillColorRGB(
            0.1,
            0.1,
            0.1
        )

        c.setFont(
            "Helvetica-Bold",
            9
        )

        c.drawString(50, y, "CÓDIGO")
        c.drawString(130, y, "PRODUCTO")
        c.drawString(320, y, "CANT.")
        c.drawString(390, y, "PRECIO UNIT.")
        c.drawString(490, y, "SUBTOTAL")

        y -= 25

        c.setFont(
            "Helvetica",
            9
        )

        items = factura_data.get(
            "items",
            []
        )

        for item in items:

            codigo = str(
                item.get(
                    "codigo",
                    item.get("numReferencia", "")
                )
            )[:12]

            nombre = str(
                item.get(
                    "nombre",
                    item.get("producto", "Producto")
                )
            )[:28]

            try:
                cantidad = int(
                    item.get(
                        "cantidad",
                        item.get("cant", 1)
                    )
                )
            except (ValueError, TypeError):
                cantidad = 1

            try:
                precio_unit = float(
                    item.get(
                        "precio_unitario",
                        item.get(
                            "precio",
                            item.get(
                                "valorVenta",
                                0.0
                            )
                        )
                    )
                )
            except (ValueError, TypeError):
                precio_unit = 0.0

            try:
                subtotal = float(
                    item.get(
                        "subtotal",
                        cantidad * precio_unit
                    )
                )
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
                    c,
                    width,
                    height,
                    factura_data
                )

                y = height - 140

                c.setFont(
                    "Helvetica",
                    9
                )

        # ==========================
        # TOTAL
        # ==========================

        y -= 10

        c.setStrokeColorRGB(
            0.8,
            0.8,
            0.8
        )

        c.line(
            40,
            y,
            width - 40,
            y
        )

        y -= 25

        c.setFont(
            "Helvetica-Bold",
            12
        )

        try:
            total = float(
                factura_data.get(
                    "total",
                    0.0
                )
            )
        except (ValueError, TypeError):
            total = 0.0

        c.drawRightString(
            width - 40,
            y,
            f"TOTAL A PAGAR: $ {total:,.2f}"
        )

        # ==========================
        # BLOQUE ECOLÓGICO
        # ==========================

        y -= 50

        if y < 60:
            c.showPage()
            y = height - 100

        c.setFillColorRGB(
            0.06,
            0.45,
            0.25
        )

        c.rect(
            40,
            y - 10,
            width - 80,
            45,
            fill=1,
            stroke=0
        )

        c.setFillColorRGB(
            1,
            1,
            1
        )

        c.setFont(
            "Helvetica-Bold",
            10
        )

        c.drawString(
            50,
            y + 15,
            "GRACIAS POR CUIDAR EL PLANETA. ESTA FACTURA ES DIGITAL."
        )

        c.setFont(
            "Helvetica",
            9
        )

        puntos = factura_data.get(
            "puntos_otorgados",
            0
        )

        c.drawString(
            50,
            y,
            f"Puntos ecológicos otorgados en esta compra: +{puntos} Puntos"
        )

        c.save()

        return ruta_salida

    @staticmethod
    def enviar_correo_factura(correo_destino, ruta_pdf, numero_factura):
        """Envía la factura en PDF por correo electrónico mediante SMTP."""

        remitente = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PASS")

        if not remitente or not password:
            return (
                False,
                "Configuración SMTP faltante. Defina SMTP_USER y SMTP_PASS."
            )

        if not correo_destino or "@" not in correo_destino:
            return False, "Correo de destino inválido."

        try:
            msg = MIMEMultipart()

            msg["From"] = remitente
            msg["To"] = correo_destino
            msg["Subject"] = (
                f"Factura Electrónica {numero_factura} - PMV"
            )

            cuerpo = (
                "Hola,\n\n"
                "Adjunto encontrarás la factura digital de tu compra en PMV.\n"
                "Gracias por preferirnos y por unirte a nuestra iniciativa de cero papel "
                "para cuidar el medio ambiente.\n\n"
                "¡Has acumulado nuevos puntos ecológicos!\n\n"
                "Saludos cordiales,\n"
                "Equipo PMV"
            )

            msg.attach(
                MIMEText(
                    cuerpo,
                    "plain"
                )
            )

            if os.path.exists(ruta_pdf):

                with open(ruta_pdf, "rb") as f:
                    part = MIMEBase(
                        "application",
                        "octet-stream"
                    )

                    part.set_payload(
                        f.read()
                    )

                encoders.encode_base64(part)

                num_fact_clean = str(
                    numero_factura
                ).replace(
                    " ",
                    "_"
                )

                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename=Factura_{num_fact_clean}.pdf"
                )

                msg.attach(part)

            else:
                return False, f"El archivo PDF en {ruta_pdf} no existe."

            server = None

            try:
                server = smtplib.SMTP(
                    "smtp.gmail.com",
                    587,
                    timeout=10
                )

                server.starttls()
                server.login(
                    remitente,
                    password
                )

                server.sendmail(
                    remitente,
                    correo_destino,
                    msg.as_string()
                )

            finally:
                if server:
                    try:
                        server.quit()
                    except Exception:
                        pass

            return True, "Factura enviada con éxito por correo."

        except Exception as e:
            print(f"Error al enviar correo: {e}")
            return False, str(e)