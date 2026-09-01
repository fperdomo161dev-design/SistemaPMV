from database.conexion import get_db
from services.security_service import hash_password
from tkinter import colorchooser, messagebox, ttk
import tkinter as tk

# PALETA DE COLORES DEL SISTEMA 
COLOR_BG = "#111827"
COLOR_CARD = "#1F2937"
COLOR_BORDER = "#374151"
COLOR_TEXT = "#F9FAFB"
COLOR_TEXT_MUTED = "#9CA3AF"
COLOR_GOLD = "#F59E0B"
COLOR_GOLD_HOVER = "#D97706"


class ConfiguracionFrame(tk.Frame):
    def __init__(self, parent, usuario_actual=None):
        super().__init__(parent, bg=COLOR_BG)
        self.parent = parent
        self.usuario_actual = usuario_actual

        self.db = get_db()
        self.color_seleccionado = "#0A0D12" 
        self.crear_interfaz()
        self.cargar_datos()

    def _crear_grupo(self, titulo):
        card = tk.Frame(
            self,
            bg=COLOR_CARD,
            bd=1,
            relief="solid",
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_BORDER,
            highlightthickness=1,
        )
        card.pack(fill="x", padx=20, pady=5, ipady=3)

        lbl_titulo = tk.Label(
            card,
            text=titulo,
            bg=COLOR_CARD,
            fg=COLOR_GOLD,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        lbl_titulo.pack(fill="x", padx=15, pady=(6, 4))
        return card

    def _crear_campo(self, padre, label_text, is_password=False):
        tk.Label(
            padre,
            text=label_text,
            bg=COLOR_CARD,
            fg=COLOR_TEXT_MUTED,
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(3, 1))

        entry = tk.Entry(
            padre,
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
            bd=1,
            relief="flat",
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_GOLD,
            highlightthickness=1,
            font=("Segoe UI", 9),
            show="*" if is_password else "",
        )
        entry.pack(fill="x", padx=15, pady=(0, 5), ipady=2)
        return entry

    def crear_interfaz(self):
        lbl_header = tk.Label(
            self,
            text="Configuración General",
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            font=("Segoe UI", 13, "bold"),
        )
        lbl_header.pack(anchor="w", padx=20, pady=(10, 5))

        # 1. Datos del Negocio y PDF
        card_empresa = self._crear_grupo("🏢 Datos del Negocio y Factura PDF")
        self.txt_nombre_empresa = self._crear_campo(
            card_empresa, "Nombre comercial (Empresa / App):"
        )
        self.txt_subtitulo_factura = self._crear_campo(
            card_empresa, "Subtítulo en Factura (Ej. Factura Electrónica):"
        )
        self.txt_mensaje_ecologico = self._crear_campo(
            card_empresa, "Mensaje ecológico / pie del PDF:"
        )
        self.txt_texto_puntos = self._crear_campo(
            card_empresa, "Formato texto puntos (Usar {puntos}):"
        )

        # Selector de Color Corporativo para el PDF
        tk.Label(
            card_empresa,
            text="Color Principal del Encabezado (PDF):",
            bg=COLOR_CARD,
            fg=COLOR_TEXT_MUTED,
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(3, 1))

        frame_color = tk.Frame(card_empresa, bg=COLOR_CARD)
        frame_color.pack(fill="x", padx=15, pady=(0, 8))

        self.lbl_muestra_color = tk.Label(
            frame_color, text="    ", bg="#0A0D12", width=6, relief="solid", bd=1
        )
        self.lbl_muestra_color.pack(side="left", padx=(0, 10))

        btn_elegir_color = tk.Button(
            frame_color,
            text="🎨 Seleccionar Color",
            bg=COLOR_BORDER,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9),
            command=self.cambiar_color_pdf,
            cursor="hand2",
            bd=0,
            padx=10,
            pady=3,
        )
        btn_elegir_color.pack(side="left")

        # 2. Correo Emisor (SMTP)
        card_correo = self._crear_grupo("✉️ Configuración Correo Emisor (Gmail/SMTP)")
        self.txt_email = self._crear_campo(card_correo, "Correo de envío:")
        self.txt_password = self._crear_campo(
            card_correo, "Contraseña de aplicación (Google):", is_password=True
        )

        # 3. Cambiar Contraseña Admin
        card_admin = self._crear_grupo("🔐 Cambiar Clave de Administrador")
        self.txt_nueva_clave = self._crear_campo(
            card_admin,
            "Nueva clave Admin (Dejar en blanco si no cambia):",
            is_password=True,
        )

        # Botón Guardar Estilizado
        btn_guardar = tk.Button(
            self,
            text="💾 Guardar Cambios",
            bg=COLOR_GOLD,
            fg="#111827",
            activebackground=COLOR_GOLD_HOVER,
            activeforeground="#111827",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            cursor="hand2",
            pady=6,
            command=self.guardar_configuracion,
        )
        btn_guardar.pack(fill="x", padx=20, pady=10)

    def cambiar_color_pdf(self):
        color_rgb, color_hex = colorchooser.askcolor(
            title="Seleccionar Color del Encabezado PDF",
            initialcolor=self.color_seleccionado,
        )
        if color_hex:
            self.color_seleccionado = color_hex
            self.lbl_muestra_color.config(bg=color_hex)

    def cargar_datos(self):
        empresa_config = self.db["config_sistema"].find_one(
            {"tipo": "datos_empresa"}
        )
        if empresa_config:
            self.txt_nombre_empresa.insert(
                0,
                empresa_config.get("nombre", "PMV - INVENTARIO Y ZAPATERÍA"),
            )
            self.txt_subtitulo_factura.insert(
                0,
                empresa_config.get("subtitulo", "Factura Electrónica de Venta"),
            )
            self.txt_mensaje_ecologico.insert(
                0,
                empresa_config.get(
                    "mensaje_ecologico",
                    "GRACIAS POR CUIDAR EL PLANETA. ESTA FACTURA ES DIGITAL.",
                ),
            )
            self.txt_texto_puntos.insert(
                0,
                empresa_config.get(
                    "texto_puntos",
                    "Puntos ecológicos otorgados en esta compra: +{puntos} Puntos",
                ),
            )

            color_guardado = empresa_config.get("color_encabezado", "#0A0D12")
            self.color_seleccionado = color_guardado
            self.lbl_muestra_color.config(bg=color_guardado)
        else:
            self.txt_nombre_empresa.insert(0, "PMV - INVENTARIO Y ZAPATERÍA")
            self.txt_subtitulo_factura.insert(0, "Factura Electrónica de Venta")
            self.txt_mensaje_ecologico.insert(
                0, "GRACIAS POR CUIDAR EL PLANETA. ESTA FACTURA ES DIGITAL."
            )
            self.txt_texto_puntos.insert(
                0, "Puntos ecológicos otorgados en esta compra: +{puntos} Puntos"
            )

        smtp_config = self.db["config_sistema"].find_one({"tipo": "correo_smtp"})
        if smtp_config:
            self.txt_email.insert(0, smtp_config.get("email", ""))
            self.txt_password.insert(0, smtp_config.get("password", ""))

    def guardar_configuracion(self):
        nuevo_nombre = (
            self.txt_nombre_empresa.get().strip() or "PMV - INVENTARIO Y ZAPATERÍA"
        )
        nuevo_subtitulo = (
            self.txt_subtitulo_factura.get().strip() or "Factura Electrónica de Venta"
        )
        nuevo_mensaje = (
            self.txt_mensaje_ecologico.get().strip()
            or "GRACIAS POR CUIDAR EL PLANETA. ESTA FACTURA ES DIGITAL."
        )
        nuevo_puntos_fmt = (
            self.txt_texto_puntos.get().strip()
            or "Puntos ecológicos otorgados en esta compra: +{puntos} Puntos"
        )

        email = self.txt_email.get().strip()
        password = self.txt_password.get().strip()
        nueva_clave = self.txt_nueva_clave.get().strip()

        self.db["config_sistema"].update_one(
            {"tipo": "datos_empresa"},
            {
                "$set": {
                    "nombre": nuevo_nombre,
                    "subtitulo": nuevo_subtitulo,
                    "mensaje_ecologico": nuevo_mensaje,
                    "texto_puntos": nuevo_puntos_fmt,
                    "color_encabezado": self.color_seleccionado,
                }
            },
            upsert=True,
        )

        self.db["config_sistema"].update_one(
            {"tipo": "correo_smtp"},
            {"$set": {"email": email, "password": password}},
            upsert=True,
        )

        if nueva_clave:
            clave_hash = hash_password(nueva_clave)
            self.db["empleados"].update_one(
                {"cedula": "admin"},
                {
                    "$set": {
                        "password": clave_hash,
                        "usuario": "admin",
                        "rol": "Administrador",
                    }
                },
                upsert=True,
            )

        # Actualizar la etiqueta principal 
        main_app = self.winfo_toplevel()
        if hasattr(main_app, "lbl_logo"):
            main_app.lbl_logo.config(text=nuevo_nombre)

        messagebox.showinfo(
            "Éxito", "Configuración y diseño de factura actualizados con éxito."
        )