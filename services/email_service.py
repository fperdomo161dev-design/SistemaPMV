from database.conexion import get_db
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class EmailService:

  def __init__(self, db=None):
    self.db = db if db is not None else get_db()

  def enviar_factura(
      self, destinatario, cliente_nombre, pdf_path, numero_factura
  ):
    """Lee la configuración SMTP guardada en MongoDB y envía la factura en PDF."""
    smtp_config = self.db["config_sistema"].find_one({"tipo": "correo_smtp"})
    empresa_config = self.db["config_sistema"].find_one(
        {"tipo": "datos_empresa"}
    )

    if (
        not smtp_config
        or not smtp_config.get("email")
        or not smtp_config.get("password")
    ):
      print("⚠️ No hay credenciales SMTP configuradas en el sistema.")
      return False, "Correo emisor no configurado en el sistema."

    remitente = smtp_config.get("email")
    password = smtp_config.get("password")

    # Nombre de la empresa con respaldo si viene vacío
    nombre_empresa = (
        empresa_config.get("nombre") if empresa_config else None
    )
    if not nombre_empresa:
      nombre_empresa = "Zapatería PMV"

    # Cabecera del correo
    msg = MIMEMultipart()
    msg["From"] = f"{nombre_empresa} <{remitente}>"
    msg["To"] = destinatario
    msg["Subject"] = (
        f"Factura de Compra N° {numero_factura} - {nombre_empresa}"
    )

    cuerpo = (
        f"Hola {cliente_nombre},\n\n"
        f"¡Gracias por tu compra en {nombre_empresa}! 🌿\n\n"
        f"Adjunto encontrarás tu factura digital N° {numero_factura} en formato PDF. Gracias por apoyar las iniciativas digitales y cuidar el medio ambiente.\n\n"
        f"Atentamente,\n"
        f"El equipo de {nombre_empresa}\n\n"
        f"--------------------------------------------------\n"
        f'"Pasa por la vida dejando huellas, no residuos." 👣🍃'
    )

    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    # Adjuntar PDF
    try:
      with open(pdf_path, "rb") as f:
        adjunto = MIMEApplication(f.read(), _subtype="pdf")
        adjunto.add_header(
            "Content-Disposition",
            "attachment",
            filename=f"Factura_{numero_factura}.pdf",
        )
        msg.attach(adjunto)
    except Exception as e:
      return False, f"Error al leer el archivo PDF: {str(e)}"

    # Envío vía servidor SMTP de Gmail (SSL / Puerto 465)
    try:
      with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remitente, password)
        server.send_message(msg)
      return True, "Factura enviada con éxito."
    except Exception as e:
      return (
          False,
          f"Error de autenticación o red al enviar el correo: {str(e)}",
      )