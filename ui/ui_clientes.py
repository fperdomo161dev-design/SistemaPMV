import tkinter as tk
from tkinter import messagebox, ttk

from models.cliente import Cliente
from services.cliente_service import (
    actualizar_cliente,
    buscar_cliente_por_cedula,
    crear_cliente,
    eliminar_cliente,
    listar_clientes,
)


FONT_FAMILY = "Segoe UI"
FONT_SIZE = 12  

COLOR_BG = "#0B111E"
COLOR_CARD = "#111827"
COLOR_INPUT_BG = "#1F2937"
COLOR_TEXT = "#E5E7EB"
COLOR_MUTED = "#9CA3AF"

COLOR_BTN_GREEN = "#10B981"
COLOR_BTN_BLUE = "#3B82F6"
COLOR_BTN_RED = "#EF4444"
COLOR_BTN_YELLOW = "#F59E0B"


class ClientesFrame(ttk.Frame):

    def __init__(self, master, usuario_actual=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.usuario_actual = usuario_actual
        self.cliente_seleccionado = None

        self._configurar_estilos()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_ui()
        self.cargar_clientes()

        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_cliente)

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Dark.TFrame", background=COLOR_BG)
        style.configure("Card.TFrame", background=COLOR_CARD, relief="flat")

       
        style.configure(
            "Dark.TLabel",
            background=COLOR_BG,
            foreground=COLOR_TEXT,
            font=(FONT_FAMILY, FONT_SIZE),
        )
        style.configure(
            "Card.TLabel",
            background=COLOR_CARD,
            foreground=COLOR_TEXT,
            font=(FONT_FAMILY, FONT_SIZE),
        )
        style.configure(
            "CardBold.TLabel",
            background=COLOR_CARD,
            foreground=COLOR_BTN_YELLOW,
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
        )

        # Botones de acción general
        style.configure(
            "Action.TButton",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            background="#1E293B",
            foreground=COLOR_TEXT,
            bordercolor="#374151",
            borderwidth=1,
            focusthickness=0,
        )
        style.map(
            "Action.TButton",
            background=[("active", "#374151"), ("disabled", "#1E293B")],
            foreground=[("active", "#FFFFFF"), ("disabled", COLOR_MUTED)],
        )

        style.configure(
            "Green.TButton",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            background=COLOR_BTN_GREEN,
            foreground="#FFFFFF",
            bordercolor=COLOR_BTN_GREEN,
            borderwidth=1,
        )
        style.map("Green.TButton", background=[("active", "#059669")])

        style.configure(
            "Blue.TButton",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            background=COLOR_BTN_BLUE,
            foreground="#FFFFFF",
            bordercolor=COLOR_BTN_BLUE,
            borderwidth=1,
        )
        style.map("Blue.TButton", background=[("active", "#2563EB")])

        style.configure(
            "Red.TButton",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            background=COLOR_BTN_RED,
            foreground="#FFFFFF",
            bordercolor=COLOR_BTN_RED,
            borderwidth=1,
        )
        style.map("Red.TButton", background=[("active", "#DC2626")])

        # Estilo de la tabla y encabezados
        style.configure(
            "Treeview",
            background="#1F2937",
            foreground=COLOR_TEXT,
            fieldbackground="#1F2937",
            rowheight=int(FONT_SIZE * 2.8), 
        )
        style.configure(
            "Treeview.Heading",
            background="#111827",
            foreground=COLOR_BTN_YELLOW,
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", COLOR_BTN_YELLOW)],
            foreground=[("selected", "#000000")],
        )

    def _build_ui(self):
        outer = ttk.Frame(self, style="Dark.TFrame")
        outer.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        # 1. BUSCADOR SUPERIOR
        search_frame = ttk.Frame(outer, style="Dark.TFrame")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ttk.Label(
            search_frame, text="Buscar por Cédula:", style="Dark.TLabel"
        ).grid(row=0, column=0, padx=(0, 10))

        self.var_buscar = tk.StringVar()

        entry_buscar = tk.Entry(
            search_frame,
            textvariable=self.var_buscar,
            width=22,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            insertbackground=COLOR_BTN_YELLOW,
            bd=1,
            relief="solid",
            font=(FONT_FAMILY, FONT_SIZE),
        )
        entry_buscar.grid(row=0, column=1, padx=(0, 10), ipady=4)
        entry_buscar.bind("<Return>", lambda e: self.buscar_por_cedula())

        ttk.Button(
            search_frame,
            text="Buscar",
            style="Blue.TButton",
            command=self.buscar_por_cedula,
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            search_frame,
            text="Limpiar",
            style="Action.TButton",
            command=self.limpiar_busqueda,
        ).grid(row=0, column=3, padx=5)

        # 2. TABLA CENTRAL
        tabla_frame = ttk.Frame(outer, style="Dark.TFrame")
        tabla_frame.grid(row=1, column=0, sticky="nsew")
        tabla_frame.columnconfigure(0, weight=1)
        tabla_frame.rowconfigure(0, weight=1)

        columns = (
            "cedula",
            "nombre",
            "apellido",
            "correo",
            "celular",
            "direccion",
            "puntos",
        )

        self.tree = ttk.Treeview(
            tabla_frame, columns=columns, show="headings", height=10
        )

        headers = [
            ("cedula", "Cédula"),
            ("nombre", "Nombre"),
            ("apellido", "Apellido"),
            ("correo", "Correo"),
            ("celular", "Celular"),
            ("direccion", "Dirección"),
            ("puntos", "Puntos"),
        ]

        for col, heading_text in headers:
            self.tree.heading(col, text=heading_text)
            width = 90 if col == "puntos" else 140
            self.tree.column(col, anchor="center", width=width)

        scrollbar = ttk.Scrollbar(
            tabla_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # 3. CONTENEDOR DE FORMULARIO Y ACCIONES
        card_container = ttk.Frame(outer, style="Card.TFrame")
        card_container.grid(row=2, column=0, sticky="ew", pady=(15, 0), ipady=15)
        card_container.columnconfigure(0, weight=1)

        form_center_wrapper = ttk.Frame(card_container, style="Card.TFrame")
        form_center_wrapper.grid(row=0, column=0)

        frame_datos = ttk.LabelFrame(
            form_center_wrapper,
            text=" Información del Cliente ",
            style="Card.TFrame",
        )
        frame_datos.grid(
            row=0, column=0, sticky="nsew", padx=15, pady=5, ipadx=10, ipady=5
        )

        self.var_cedula = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_correo = tk.StringVar()
        self.var_celular = tk.StringVar()
        self.var_direccion = tk.StringVar()
        self.var_puntos = tk.StringVar(value="0")

        campos = [
            ("Cédula", self.var_cedula, 0, 0),
            ("Nombre", self.var_nombre, 0, 2),
            ("Apellido", self.var_apellido, 1, 0),
            ("Correo", self.var_correo, 1, 2),
            ("Celular", self.var_celular, 2, 0),
            ("Dirección", self.var_direccion, 2, 2),
            ("Puntos", self.var_puntos, 3, 0),
        ]

        for label_text, var, row, col in campos:
            ttk.Label(
                frame_datos, text=label_text, style="CardBold.TLabel"
            ).grid(row=row, column=col, sticky="e", padx=(12, 6), pady=8)

            entry = tk.Entry(
                frame_datos,
                textvariable=var,
                bg=COLOR_INPUT_BG,
                fg=COLOR_BTN_YELLOW if label_text == "Puntos" else COLOR_TEXT,
                insertbackground=COLOR_BTN_YELLOW,
                bd=1,
                relief="solid",
                font=(
                    FONT_FAMILY,
                    FONT_SIZE,
                    "bold" if label_text == "Puntos" else "normal",
                ),
                width=20,
            )

            if label_text == "Puntos":
                entry.bind("<Key>", lambda e: "break")

            entry.grid(
                row=row, column=col + 1, sticky="w", padx=(0, 20), pady=8, ipady=3
            )

        # 4. BOTONES LATERALES ESTILO POS
        acciones_frame = ttk.Frame(form_center_wrapper, style="Card.TFrame")
        acciones_frame.grid(row=0, column=1, sticky="nsew", padx=(25, 0), pady=5)

        ttk.Label(
            acciones_frame, text="Gestión / Acciones", style="CardBold.TLabel"
        ).pack(anchor="w", pady=(0, 6))

        ANCHO_BOTON = 20

        ttk.Button(
            acciones_frame,
            text="➕ Guardar Cliente",
            style="Green.TButton",
            width=ANCHO_BOTON,
            command=self.guardar_cliente,
        ).pack(fill="x", pady=5, ipady=3)

        ttk.Button(
            acciones_frame,
            text="✏️ Actualizar Cliente",
            style="Blue.TButton",
            width=ANCHO_BOTON,
            command=self.actualizar_cliente_ui,
        ).pack(fill="x", pady=5, ipady=3)

        ttk.Button(
            acciones_frame,
            text="🗑️ Eliminar Cliente",
            style="Red.TButton",
            width=ANCHO_BOTON,
            command=self.eliminar_cliente_ui,
        ).pack(fill="x", pady=5, ipady=3)

        ttk.Button(
            acciones_frame,
            text="🧹 Limpiar Campos",
            style="Action.TButton",
            width=ANCHO_BOTON,
            command=self.limpiar_formulario,
        ).pack(fill="x", pady=5, ipady=3)

    def guardar_cliente(self):
        try:
            cliente = Cliente(
                cedula=self.var_cedula.get().strip(),
                nombre=self.var_nombre.get().strip(),
                apellido=self.var_apellido.get().strip(),
                correo=self.var_correo.get().strip(),
                celular=self.var_celular.get().strip(),
                direccion=self.var_direccion.get().strip(),
                puntos=0,
            )

            if not cliente.cedula or not cliente.nombre:
                messagebox.showwarning(
                    "Advertencia", "La Cédula y el Nombre son obligatorios."
                )
                return

            ok = crear_cliente(cliente)
            if not ok:
                messagebox.showwarning(
                    "Aviso", "La Cédula ya se encuentra registrada."
                )
                return

            self.cargar_clientes()
            self.limpiar_formulario()
            messagebox.showinfo("Éxito", "Cliente guardado correctamente.")

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo guardar el cliente.\nDetalle: {e}"
            )

    def actualizar_cliente_ui(self):
        if self.cliente_seleccionado is None:
            messagebox.showwarning(
                "Advertencia", "Debes seleccionar un cliente para actualizar."
            )
            return

        try:
            datos = {
                "nombre": self.var_nombre.get().strip(),
                "apellido": self.var_apellido.get().strip(),
                "correo": self.var_correo.get().strip(),
                "celular": self.var_celular.get().strip(),
                "direccion": self.var_direccion.get().strip(),
            }

            actualizar_cliente(self.cliente_seleccionado, datos)
            self.cargar_clientes()
            messagebox.showinfo(
                "Actualizado", "Cliente actualizado correctamente."
            )

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo actualizar.\nDetalle: {e}"
            )

    def eliminar_cliente_ui(self):
        if self.cliente_seleccionado is None:
            messagebox.showwarning(
                "Advertencia", "Debes seleccionar un cliente para eliminar."
            )
            return

        if not messagebox.askyesno(
            "Confirmar", "¿Estás seguro de eliminar este cliente?"
        ):
            return

        try:
            eliminar_cliente(self.cliente_seleccionado)
            self.cargar_clientes()
            self.limpiar_formulario()
            messagebox.showinfo("Eliminado", "Cliente eliminado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar.\nDetalle: {e}")

    def seleccionar_cliente(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return

        valores = self.tree.item(seleccion[0])["values"]
        self.cliente_seleccionado = str(valores[0]).strip()

        cli = buscar_cliente_por_cedula(self.cliente_seleccionado)
        if cli:
            self.var_cedula.set(cli.cedula)
            self.var_nombre.set(cli.nombre)
            self.var_apellido.set(cli.apellido)
            self.var_correo.set(cli.correo)
            self.var_celular.set(cli.celular)
            self.var_direccion.set(cli.direccion)
            self.var_puntos.set(str(getattr(cli, "puntos", 0)))

    def cargar_clientes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for cli in listar_clientes():
            self.tree.insert(
                "",
                "end",
                values=(
                    cli.cedula,
                    cli.nombre,
                    cli.apellido,
                    cli.correo,
                    cli.celular,
                    cli.direccion,
                    getattr(cli, "puntos", 0),
                ),
            )

    def buscar_por_cedula(self):
        texto = self.var_buscar.get().strip()

        if not texto:
            self.cargar_clientes()
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        for cli in listar_clientes():
            if str(cli.cedula).strip() == texto:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        cli.cedula,
                        cli.nombre,
                        cli.apellido,
                        cli.correo,
                        cli.celular,
                        cli.direccion,
                        getattr(cli, "puntos", 0),
                    ),
                )
                break

    def limpiar_busqueda(self):
        self.var_buscar.set("")
        self.cargar_clientes()

    def limpiar_formulario(self):
        self.var_cedula.set("")
        self.var_nombre.set("")
        self.var_apellido.set("")
        self.var_correo.set("")
        self.var_celular.set("")
        self.var_direccion.set("")
        self.var_puntos.set("0")
        self.cliente_seleccionado = None