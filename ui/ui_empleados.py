from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from models.empleado import Empleado
from services.empleado_service import (
    actualizar_empleado,
    crear_empleado,
    eliminar_empleado,
    listar_empleados,
)

# PALETA DE COLORES UI DARK EXECUTIVE

COLOR_BG = "#0B111E"
COLOR_CARD = "#111827"
COLOR_INPUT_BG = "#1F2937"
COLOR_TEXT = "#E5E7EB"
COLOR_ACCENT = "#F59E0B"
COLOR_MUTED = "#9CA3AF"

# OPCIONES PARA LOS DESPLEGABLES
CARGOS_DISPONIBLES = ["Administrador", "Vendedor", "Cajero", "Auxiliar"]
TIPOS_PAGO_DISPONIBLES = ["FIJO", "DIARIO"]


class EmpleadosFrame(ttk.Frame):

    def __init__(self, master, usuario_actual=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.usuario_actual = usuario_actual
        self.empleado_seleccionado = None  

        
        self.es_admin = False
        if self.usuario_actual:
            rol = getattr(self.usuario_actual, "cargo", "") or getattr(
                self.usuario_actual, "rol", ""
            )
            self.es_admin = str(rol).strip().lower() in [
                "administrador",
                "admin",
                "gerente",
            ]

       
        if not self.es_admin:
            ttk.Label(
                self,
                text=(
                    "Acceso denegado. Este módulo es exclusivo para"
                    " administradores."
                ),
                style="Dark.TLabel",
            ).pack(padx=20, pady=20)
            return

   
        self._configurar_estilos()
        self._build_ui()
        self.cargar_empleados()

    def _configurar_estilos(self):
        """Configura los estilos globales y personalizados para los widgets ttk."""
        style = ttk.Style()
        style.theme_use("clam")

        # Configuración de Frames
        style.configure("Dark.TFrame", background=COLOR_BG)
        style.configure("Card.TFrame", background=COLOR_CARD, relief="flat")

   
        style.configure(
            "Dark.TLabel",
            background=COLOR_BG,
            foreground=COLOR_TEXT,
            font=("Segoe UI", 12),
        )
        style.configure(
            "Card.TLabel",
            background=COLOR_CARD,
            foreground=COLOR_TEXT,
            font=("Segoe UI", 12),
        )
        style.configure(
            "CardBold.TLabel",
            background=COLOR_CARD,
            foreground=COLOR_ACCENT,
            font=("Segoe UI", 12, "bold"),
        )

     
        style.configure(
            "Action.TButton",
            font=("Segoe UI", 12, "bold"),
            background="#1E293B",
            foreground=COLOR_TEXT,
            bordercolor="#374151",
            borderwidth=1,
            focusthickness=0,
        )
        style.map(
            "Action.TButton",
            background=[("active", "#334155"), ("disabled", "#374151")],
            foreground=[("active", "#FFFFFF"), ("disabled", COLOR_MUTED)],
        )

        # Botón Guardar (Verde)
        style.configure(
            "Success.TButton",
            font=("Segoe UI", 12, "bold"),
            background="#10B981",
            foreground="#FFFFFF",
            bordercolor="#10B981",
            borderwidth=1,
            focusthickness=0,
        )
        style.map(
            "Success.TButton",
            background=[("active", "#059669")],
            foreground=[("active", "#FFFFFF")],
        )

        
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 12, "bold"),
            background="#3B82F6",
            foreground="#FFFFFF",
            bordercolor="#3B82F6",
            borderwidth=1,
            focusthickness=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#2563EB")],
            foreground=[("active", "#FFFFFF")],
        )

        # Botón Eliminar (Rojo)
        style.configure(
            "Danger.TButton",
            font=("Segoe UI", 12, "bold"),
            background="#EF4444",
            foreground="#FFFFFF",
            bordercolor="#EF4444",
            borderwidth=1,
            focusthickness=0,
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#DC2626")],
            foreground=[("active", "#FFFFFF")],
        )

      
        style.configure(
            "TCombobox",
            fieldbackground=COLOR_INPUT_BG,
            background=COLOR_INPUT_BG,
            foreground=COLOR_TEXT,
            darkcolor=COLOR_INPUT_BG,
            lightcolor=COLOR_INPUT_BG,
            selectbackground=COLOR_INPUT_BG,
            selectforeground=COLOR_TEXT,
            bordercolor="#374151",
            arrowcolor=COLOR_ACCENT,
        )
        style.map("TCombobox", fieldbackground=[("readonly", COLOR_INPUT_BG)])

        # Tabla / Treeview con fuente en 12
        style.configure(
            "Treeview",
            background="#1F2937",
            foreground=COLOR_TEXT,
            fieldbackground="#1F2937",
            rowheight=32,
            font=("Segoe UI", 12),
        )
        style.configure(
            "Treeview.Heading",
            background="#111827",
            foreground=COLOR_ACCENT,
            font=("Segoe UI", 12, "bold"),
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", COLOR_ACCENT)],
            foreground=[("selected", "#000000")],
        )

    def _build_ui(self):
        """Construye todos los elementos gráficos de la interfaz de empleados."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Frame contenedor exterior con márgenes y expansión completa
        outer = ttk.Frame(self, style="Dark.TFrame")
        outer.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        # SECCIÓN DE BÚSQUEDA
        search_frame = ttk.Frame(outer, style="Dark.TFrame")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ttk.Label(
            search_frame, text="Buscar por Cédula:", style="Dark.TLabel"
        ).grid(row=0, column=0, padx=(0, 10))

        self.var_buscar = tk.StringVar()

        entry_buscar = tk.Entry(
            search_frame,
            textvariable=self.var_buscar,
            width=20,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            insertbackground=COLOR_ACCENT,
            bd=1,
            relief="solid",
            font=("Segoe UI", 12),
        )
        entry_buscar.grid(row=0, column=1, padx=(0, 10), ipady=3)
        entry_buscar.bind("<Return>", lambda e: self.buscar_por_cedula())

        ttk.Button(
            search_frame,
            text="Buscar",
            style="Primary.TButton",
            command=self.buscar_por_cedula,
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            search_frame,
            text="Limpiar",
            style="Action.TButton",
            command=self.limpiar_busqueda,
        ).grid(row=0, column=3, padx=5)

        # SECCIÓN DE TABLA (TREEVIEW)
        tabla_frame = ttk.Frame(outer, style="Dark.TFrame")
        tabla_frame.grid(row=1, column=0, sticky="nsew")
        tabla_frame.columnconfigure(0, weight=1)
        tabla_frame.rowconfigure(0, weight=1)

        columns = (
            "cedula",
            "nombre",
            "apellido",
            "cargo",
            "usuario",
            "tipo_pago",
            "salario",
        )

        self.tree = ttk.Treeview(
            tabla_frame, columns=columns, show="headings", height=10
        )
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_empleado)

        headers = [
            ("cedula", "Cédula"),
            ("nombre", "Nombre"),
            ("apellido", "Apellido"),
            ("cargo", "Cargo"),
            ("usuario", "Usuario"),
            ("tipo_pago", "Tipo Pago"),
            ("salario", "Salario"),
        ]

        for col, heading_text in headers:
            self.tree.heading(col, text=heading_text)
            self.tree.column(col, anchor="center", width=110, stretch=True)

        scrollbar = ttk.Scrollbar(
            tabla_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # 3. SECCIÓN DE FORMULARIO Y NÓMINA
        card_container = ttk.Frame(outer, style="Card.TFrame")
        card_container.grid(row=2, column=0, sticky="nsew", pady=(15, 0), ipady=15)

        card_container.columnconfigure(0, weight=4)
        card_container.columnconfigure(1, weight=4)
        card_container.columnconfigure(2, weight=3)

        # Sub-panel izquierdo: Datos Personales y de Acceso
        frame_personales = ttk.LabelFrame(
            card_container, text=" Datos Personales ", style="Card.TFrame"
        )
        frame_personales.grid(
            row=0, column=0, sticky="nsew", padx=10, pady=5, ipadx=5, ipady=5
        )

        # Sub-panel central: Parámetros de Nómina y Salarios
        frame_nomina = ttk.LabelFrame(
            card_container, text=" Parámetros de Nómina ", style="Card.TFrame"
        )
        frame_nomina.grid(
            row=0, column=1, sticky="nsew", padx=10, pady=5, ipadx=5, ipady=5
        )

        # Sub-panel derecho: Botones de Acción
        acciones_frame = ttk.Frame(card_container, style="Card.TFrame")
        acciones_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=5)

        # DECLARACIÓN DE VARIABLES DE CONTROL DE TKINTER
        self.var_cedula = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_cargo = tk.StringVar()
        self.var_correo = tk.StringVar()
        self.var_celular = tk.StringVar()
        self.var_usuario = tk.StringVar()
        self.var_clave = tk.StringVar()

        self.var_tipo_pago = tk.StringVar(value="FIJO")
        self.var_salario = tk.DoubleVar(value=0.0)
        self.var_tarifa_diaria = tk.DoubleVar(value=0.0)
        self.var_sub_transporte = tk.DoubleVar(value=0.0)
        self.var_pct_salud = tk.DoubleVar(value=0.04)
        self.var_pct_pension = tk.DoubleVar(value=0.04)
        self.var_pct_arl = tk.DoubleVar(value=0.0)
        self.var_pct_parafiscales = tk.DoubleVar(value=0.09)
        self.var_dias_mes = tk.IntVar(value=30)

      
        campos_personales = [
            ("Cédula", self.var_cedula, 0, 0, "entry"),
            ("Nombre", self.var_nombre, 0, 2, "entry"),
            ("Apellido", self.var_apellido, 1, 0, "entry"),
            ("Cargo", self.var_cargo, 1, 2, "combo"),
            ("Correo", self.var_correo, 2, 0, "entry"),
            ("Celular", self.var_celular, 2, 2, "entry"),
            ("Usuario", self.var_usuario, 3, 0, "entry"),
            ("Clave", self.var_clave, 3, 2, "clave"),
        ]

        for label_text, var, row, col, tipo in campos_personales:
            ttk.Label(
                frame_personales, text=label_text, style="CardBold.TLabel"
            ).grid(row=row, column=col, sticky="e", padx=(10, 5), pady=4)

            if tipo == "combo":
                cb = ttk.Combobox(
                    frame_personales,
                    textvariable=var,
                    values=CARGOS_DISPONIBLES,
                    state="readonly",
                    width=15,
                    font=("Segoe UI", 12),
                )
                cb.grid(
                    row=row,
                    column=col + 1,
                    sticky="w",
                    padx=(0, 10),
                    pady=4,
                    ipady=2,
                )
            else:
                entry = tk.Entry(
                    frame_personales,
                    textvariable=var,
                    show="*" if tipo == "clave" else "",
                    bg=COLOR_INPUT_BG,
                    fg=COLOR_TEXT,
                    insertbackground=COLOR_ACCENT,
                    bd=1,
                    relief="solid",
                    font=("Segoe UI", 12),
                    width=15,
                )
                entry.grid(
                    row=row,
                    column=col + 1,
                    sticky="w",
                    padx=(0, 10),
                    pady=4,
                    ipady=2,
                )

        
        campos_nomina = [
            ("Tipo Pago", self.var_tipo_pago, 0, 0, "combo_pago"),
            ("Salario Mes", self.var_salario, 0, 2, "entry"),
            ("Tarifa Día", self.var_tarifa_diaria, 1, 0, "entry"),
            ("Sub. Transp.", self.var_sub_transporte, 1, 2, "entry"),
            ("% Salud", self.var_pct_salud, 2, 0, "entry"),
            ("% Pensión", self.var_pct_pension, 2, 2, "entry"),
            ("% ARL", self.var_pct_arl, 3, 0, "entry"),
            ("% Parafisc.", self.var_pct_parafiscales, 3, 2, "entry"),
            ("Días Mes", self.var_dias_mes, 4, 0, "entry"),
        ]

        for label_text, var, row, col, tipo in campos_nomina:
            ttk.Label(frame_nomina, text=label_text, style="CardBold.TLabel").grid(
                row=row, column=col, sticky="e", padx=(10, 5), pady=4
            )

            if tipo == "combo_pago":
                cb = ttk.Combobox(
                    frame_nomina,
                    textvariable=var,
                    values=TIPOS_PAGO_DISPONIBLES,
                    state="readonly",
                    width=14,
                    font=("Segoe UI", 12),
                )
                cb.grid(
                    row=row,
                    column=col + 1,
                    sticky="w",
                    padx=(0, 10),
                    pady=4,
                    ipady=2,
                )
            else:
                entry = tk.Entry(
                    frame_nomina,
                    textvariable=var,
                    bg=COLOR_INPUT_BG,
                    fg=COLOR_TEXT,
                    insertbackground=COLOR_ACCENT,
                    bd=1,
                    relief="solid",
                    font=("Segoe UI", 12),
                    width=15,
                )
                entry.grid(
                    row=row,
                    column=col + 1,
                    sticky="w",
                    padx=(0, 10),
                    pady=4,
                    ipady=2,
                )

        # BOTONES LATERALES DE ACCIÓN 
        ttk.Label(
            acciones_frame, text="Acciones", style="CardBold.TLabel"
        ).pack(anchor="w", pady=(0, 6))

        ANCHO_BOTON = 18

        ttk.Button(
            acciones_frame,
            text="➕ Guardar",
            style="Success.TButton",
            width=ANCHO_BOTON,
            command=self.guardar_empleado,
        ).pack(fill="x", pady=5, ipady=2)

        ttk.Button(
            acciones_frame,
            text="✏️ Actualizar",
            style="Primary.TButton",
            width=ANCHO_BOTON,
            command=self.actualizar_empleado_ui,
        ).pack(fill="x", pady=5, ipady=2)

        ttk.Button(
            acciones_frame,
            text="🗑️ Eliminar",
            style="Danger.TButton",
            width=ANCHO_BOTON,
            command=self.eliminar_empleado_ui,
        ).pack(fill="x", pady=5, ipady=2)

        ttk.Button(
            acciones_frame,
            text="🧹 Limpiar",
            style="Action.TButton",
            width=ANCHO_BOTON,
            command=self.limpiar_formulario,
        ).pack(fill="x", pady=5, ipady=2)

    # LÓGICA Y CONTROL DE INTERFAZ (CRUD)

    def guardar_empleado(self):
        """Captura los datos del formulario y registra un nuevo empleado."""
        try:
            empleado = Empleado(
                cedula=self.var_cedula.get().strip(),
                nombre=self.var_nombre.get().strip(),
                apellido=self.var_apellido.get().strip(),
                cargo=self.var_cargo.get().strip(),
                correo=self.var_correo.get().strip(),
                celular=self.var_celular.get().strip(),
                usuario=self.var_usuario.get().strip(),
                clave=self.var_clave.get(),
                tipo_pago=self.var_tipo_pago.get(),
                salario=float(self.var_salario.get() or 0.0),
                tarifa_diaria=float(self.var_tarifa_diaria.get() or 0.0),
                sub_transporte=float(self.var_sub_transporte.get() or 0.0),
                pct_salud=float(self.var_pct_salud.get() or 0.0),
                pct_pension=float(self.var_pct_pension.get() or 0.0),
                pct_arl=float(self.var_pct_arl.get() or 0.0),
                pct_parafiscales=float(self.var_pct_parafiscales.get() or 0.0),
                dias_mes=int(self.var_dias_mes.get() or 30),
            )

            ok = crear_empleado(empleado)
            if not ok:
                messagebox.showwarning("Aviso", "La cédula ya existe.")
                return

            self.cargar_empleados()
            self.limpiar_formulario()
            messagebox.showinfo("Éxito", "Empleado guardado correctamente.")

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo guardar el empleado.\nDetalle: {e}"
            )

    def actualizar_empleado_ui(self):
        """Actualiza la información del empleado actualmente seleccionado."""
        if self.empleado_seleccionado is None:
            messagebox.showwarning(
                "Advertencia", "Debes seleccionar un empleado para actualizar."
            )
            return

        try:
            datos = {
                "nombre": self.var_nombre.get().strip(),
                "apellido": self.var_apellido.get().strip(),
                "cargo": self.var_cargo.get().strip(),
                "correo": self.var_correo.get().strip(),
                "celular": self.var_celular.get().strip(),
                "usuario": self.var_usuario.get().strip(),
                "clave": self.var_clave.get(),
                "tipo_pago": self.var_tipo_pago.get(),
                "salario": float(self.var_salario.get() or 0.0),
                "tarifa_diaria": float(self.var_tarifa_diaria.get() or 0.0),
                "sub_transporte": float(self.var_sub_transporte.get() or 0.0),
                "pct_salud": float(self.var_pct_salud.get() or 0.0),
                "pct_pension": float(self.var_pct_pension.get() or 0.0),
                "pct_arl": float(self.var_pct_arl.get() or 0.0),
                "pct_parafiscales": float(
                    self.var_pct_parafiscales.get() or 0.0
                ),
                "dias_mes": int(self.var_dias_mes.get() or 30),
            }

            actualizar_empleado(self.empleado_seleccionado, datos)
            self.cargar_empleados()
            messagebox.showinfo(
                "Actualizado", "Empleado actualizado correctamente."
            )

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar.\nDetalle: {e}")

    def eliminar_empleado_ui(self):
        """Elimina al empleado seleccionado de la base de datos."""
        if self.empleado_seleccionado is None:
            messagebox.showwarning(
                "Advertencia", "Debes seleccionar un empleado para eliminar."
            )
            return

        try:
            eliminar_empleado(self.empleado_seleccionado)
            self.cargar_empleados()
            self.limpiar_formulario()
            messagebox.showinfo("Eliminado", "Empleado eliminado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar.\nDetalle: {e}")

    def seleccionar_empleado(self, event):
        """Carga los datos del empleado seleccionado en la tabla hacia el formulario."""
        seleccion = self.tree.selection()
        if not seleccion:
            return

        valores = self.tree.item(seleccion[0])["values"]
        self.empleado_seleccionado = str(valores[0]).strip()

        from services.empleado_service import buscar_empleado_por_cedula

        emp = buscar_empleado_por_cedula(self.empleado_seleccionado)

        if emp:
            self.var_cedula.set(emp.cedula)
            self.var_nombre.set(emp.nombre)
            self.var_apellido.set(emp.apellido)
            self.var_cargo.set(emp.cargo)
            self.var_correo.set(emp.correo)
            self.var_celular.set(emp.celular)
            self.var_usuario.set(emp.usuario)
            self.var_clave.set("")  # Por seguridad no mostramos la contraseña
            self.var_tipo_pago.set(emp.tipo_pago)
            self.var_salario.set(emp.salario)
            self.var_tarifa_diaria.set(emp.tarifa_diaria)
            self.var_sub_transporte.set(emp.sub_transporte)
            self.var_pct_salud.set(emp.pct_salud)
            self.var_pct_pension.set(emp.pct_pension)
            self.var_pct_arl.set(emp.pct_arl)
            self.var_pct_parafiscales.set(emp.pct_parafiscales)
            self.var_dias_mes.set(emp.dias_mes)

    def cargar_empleados(self):
        """Consulta todos los empleados y los inserta en el Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for emp in listar_empleados():
            self.tree.insert(
                "",
                "end",
                values=(
                    emp.cedula,
                    emp.nombre,
                    emp.apellido,
                    emp.cargo,
                    emp.usuario,
                    emp.tipo_pago,
                    emp.salario,
                ),
            )

    def buscar_por_cedula(self):
        """Filtra la lista de empleados por número de cédula."""
        texto = self.var_buscar.get().strip()

        if not texto:
            self.cargar_empleados()
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        for emp in listar_empleados():
            if str(emp.cedula).strip() == texto:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        emp.cedula,
                        emp.nombre,
                        emp.apellido,
                        emp.cargo,
                        emp.usuario,
                        emp.tipo_pago,
                        emp.salario,
                    ),
                )
                break

    def limpiar_busqueda(self):
        """Limpia el campo de búsqueda y recarga todos los registros."""
        self.var_buscar.set("")
        self.cargar_empleados()

    def limpiar_formulario(self):
        """Restablece los campos del formulario a sus valores por defecto."""
        self.var_cedula.set("")
        self.var_nombre.set("")
        self.var_apellido.set("")
        self.var_cargo.set("")
        self.var_correo.set("")
        self.var_celular.set("")
        self.var_usuario.set("")
        self.var_clave.set("")
        self.var_tipo_pago.set("FIJO")
        self.var_salario.set(0.0)
        self.var_tarifa_diaria.set(0.0)
        self.var_sub_transporte.set(0.0)
        self.var_pct_salud.set(0.04)
        self.var_pct_pension.set(0.04)
        self.var_pct_arl.set(0.0)
        self.var_pct_parafiscales.set(0.09)
        self.var_dias_mes.set(30)
        self.empleado_seleccionado = None