import tkinter as tk
from tkinter import messagebox, ttk

from models.producto import Producto
from services.producto_service import (
    actualizar_producto,
    crear_producto,
    eliminar_producto,
    listar_productos,
    obtener_siguiente_referencia,
)


COLOR_BG = "#0B111E"
COLOR_CARD = "#111827"
COLOR_INPUT_BG = "#1F2937"
COLOR_TEXT = "#E5E7EB"
COLOR_ACCENT = "#F59E0B"
COLOR_MUTED = "#9CA3AF"


class ProductosFrame(ttk.Frame):

    def __init__(self, master, usuario_actual=None, *args, **kwargs):
        self.usuario_actual = usuario_actual

        super().__init__(master, *args, **kwargs)

        # Validamos el rol del usuario recibido
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

        self.producto_seleccionado = None

        # Configuración de estilos Tkinter
        self._configurar_estilos()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_ui()
        self.cargar_productos()
        self.limpiar_formulario()

        self.tree.bind("<<TreeviewSelect>>", self.al_seleccionar_producto)

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

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

        # Botón Acción / Limpiar 
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

        # Botón Guardar 
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

        # Botón Actualizar / Buscar 
        style.configure(
            "Info.TButton",
            font=("Segoe UI", 12, "bold"),
            background="#3B82F6",
            foreground="#FFFFFF",
            bordercolor="#3B82F6",
            borderwidth=1,
            focusthickness=0,
        )
        style.map(
            "Info.TButton",
            background=[("active", "#2563EB")],
            foreground=[("active", "#FFFFFF")],
        )

        # Botón Eliminar / Stock Bajo 
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
        self.configure(style="Dark.TFrame")

        outer = ttk.Frame(self, style="Dark.TFrame")
        outer.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)
        # 1. BUSCADOR
        search_frame = ttk.Frame(outer, style="Dark.TFrame")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ttk.Label(
            search_frame, text="Buscar por Ref:", style="Dark.TLabel"
        ).grid(row=0, column=0, padx=(0, 10))

        self.var_buscar = tk.StringVar()

        entry_buscar = tk.Entry(
            search_frame,
            textvariable=self.var_buscar,
            width=18,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            insertbackground=COLOR_ACCENT,
            bd=1,
            relief="solid",
            font=("Segoe UI", 12),
            highlightbackground="#374151",
            highlightcolor=COLOR_ACCENT,
        )
        entry_buscar.grid(row=0, column=1, padx=(0, 10), ipady=3)
        entry_buscar.bind("<Return>", lambda e: self.buscar_por_ref())

        ttk.Button(
            search_frame,
            text="Buscar",
            style="Info.TButton",
            command=self.buscar_por_ref,
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            search_frame,
            text="Limpiar",
            style="Action.TButton",
            command=self.limpiar_busqueda,
        ).grid(row=0, column=3, padx=5)

        ttk.Button(
            search_frame,
            text="⚠️ Ver Stock Bajo",
            style="Danger.TButton",
            command=self.mostrar_solo_stock_bajo,
        ).grid(row=0, column=4, padx=5)

        # 2. TABLA
        tabla_frame = ttk.Frame(outer, style="Dark.TFrame")
        tabla_frame.grid(row=1, column=0, sticky="nsew")
        tabla_frame.columnconfigure(0, weight=1)
        tabla_frame.rowconfigure(0, weight=1)

        if self.es_admin:
            self.columns = (
                "ref",
                "marca",
                "talla",
                "color",
                "stock",
                "valorCompra",
                "valorVenta",
                "ubicacion",
            )
            headers = [
                ("ref", "Referencia"),
                ("marca", "Marca"),
                ("talla", "Talla"),
                ("color", "Color"),
                ("stock", "Stock"),
                ("valorCompra", "V. Compra"),
                ("valorVenta", "V. Venta"),
                ("ubicacion", "Ubicación"),
            ]
        else:
            self.columns = (
                "ref",
                "marca",
                "talla",
                "color",
                "stock",
                "valorVenta",
                "ubicacion",
            )
            headers = [
                ("ref", "Referencia"),
                ("marca", "Marca"),
                ("talla", "Talla"),
                ("color", "Color"),
                ("stock", "Stock"),
                ("valorVenta", "V. Venta"),
                ("ubicacion", "Ubicación"),
            ]

        self.tree = ttk.Treeview(
            tabla_frame, columns=self.columns, show="headings", height=10
        )

        for col, heading_text in headers:
            self.tree.heading(col, text=heading_text)
            self.tree.column(col, anchor="center", width=110)

        scrollbar = ttk.Scrollbar(
            tabla_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # 3. FORMULARIO E INVENTARIO

        card_container = ttk.Frame(outer, style="Card.TFrame")
        card_container.grid(row=2, column=0, sticky="ew", pady=(15, 0), ipady=15)
        card_container.columnconfigure(0, weight=1)

        form_center_wrapper = ttk.Frame(card_container, style="Card.TFrame")
        form_center_wrapper.grid(row=0, column=0)

        self.formulario = ttk.Frame(form_center_wrapper, style="Card.TFrame")
        self.formulario.grid(row=0, column=0, sticky="nsew", padx=(0, 30))

        # VARIABLES
        self.var_ref = tk.StringVar()
        self.var_marca = tk.StringVar()
        self.var_talla = tk.StringVar()
        self.var_color = tk.StringVar()
        self.var_stock = tk.StringVar()
        self.var_valor_compra = tk.StringVar()
        self.var_valor_venta = tk.StringVar()
        self.var_ubicacion = tk.StringVar()

        self.construir_formulario()

        # 4. BOTONES LATERALES DE ACCIÓN
        acciones_frame = ttk.Frame(form_center_wrapper, style="Card.TFrame")
        acciones_frame.grid(row=0, column=1, sticky="ns", padx=(20, 0))

        ttk.Label(
            acciones_frame, text="Gestión / Acciones", style="CardBold.TLabel"
        ).pack(anchor="w", pady=(0, 6))

        ANCHO_BOTON = 20

        ttk.Button(
            acciones_frame,
            text="➕ Guardar Producto",
            style="Success.TButton",
            width=ANCHO_BOTON,
            command=self.guardar_producto,
        ).pack(fill="x", pady=3, ipady=3)

        ttk.Button(
            acciones_frame,
            text="✏️ Actualizar Producto",
            style="Info.TButton",
            width=ANCHO_BOTON,
            command=self.actualizar_producto_ui,
        ).pack(fill="x", pady=3, ipady=3)

        ttk.Button(
            acciones_frame,
            text="🗑️ Eliminar Producto",
            style="Danger.TButton",
            width=ANCHO_BOTON,
            command=self.eliminar_producto_ui,
        ).pack(fill="x", pady=3, ipady=3)

        ttk.Button(
            acciones_frame,
            text="🧹 Limpiar Campos",
            style="Action.TButton",
            width=ANCHO_BOTON,
            command=self.limpiar_formulario,
        ).pack(fill="x", pady=3, ipady=3)

    def construir_formulario(self):
        for widget in self.formulario.winfo_children():
            widget.destroy()

        if self.es_admin:
            self.campos_config = [
                ("Referencia", self.var_ref, 0, 0, True),
                ("Marca", self.var_marca, 0, 2, False),
                ("Talla", self.var_talla, 1, 0, False),
                ("Color", self.var_color, 1, 2, False),
                ("Stock", self.var_stock, 2, 0, False),
                ("V. Compra", self.var_valor_compra, 2, 2, False),
                ("V. Venta", self.var_valor_venta, 3, 0, False),
                ("Ubicación", self.var_ubicacion, 3, 2, False),
            ]
        else:
            self.campos_config = [
                ("Referencia", self.var_ref, 0, 0, True),
                ("Marca", self.var_marca, 0, 2, False),
                ("Talla", self.var_talla, 1, 0, False),
                ("Color", self.var_color, 1, 2, False),
                ("Stock", self.var_stock, 2, 0, False),
                ("V. Venta", self.var_valor_venta, 2, 2, False),
                ("Ubicación", self.var_ubicacion, 3, 0, False),
            ]

        for label_text, var, row, col, es_condicional in self.campos_config:
            lbl = ttk.Label(self.formulario, text=label_text, style="CardBold.TLabel")
            
            entry = tk.Entry(
                self.formulario,
                textvariable=var,
                bg=COLOR_INPUT_BG,
                readonlybackground=COLOR_INPUT_BG, 
                fg=COLOR_TEXT,
                insertbackground=COLOR_ACCENT,
                bd=1,
                relief="solid",
                font=("Segoe UI", 12),
                width=16,
                highlightbackground="#374151",
                highlightcolor=COLOR_ACCENT,
            )

            if label_text == "Referencia":
                entry.config(state="readonly")
                self.entry_ref = entry
                self.lbl_ref = lbl
                lbl.grid_remove()
                entry.grid_remove()
            else:
                lbl.grid(row=row, column=col, sticky="e", padx=(10, 5), pady=6)
                entry.grid(row=row, column=col + 1, sticky="w", padx=(0, 15), pady=6, ipady=3)

    # LÓGICA DE INTERFAZ 

    def guardar_producto(self):
        try:
            v_compra_val = (
                int(self.var_valor_compra.get())
                if self.es_admin and self.var_valor_compra.get().strip()
                else 0
            )

            producto = Producto(
                numReferencia=0,
                marca=self.var_marca.get().strip(),
                talla=self.var_talla.get().strip(),
                color=self.var_color.get().strip(),
                cantidadStock=int(self.var_stock.get() or 0),
                valorCompra=v_compra_val,
                valorVenta=int(self.var_valor_venta.get() or 0),
                ubicacion=self.var_ubicacion.get().strip(),
            )

            exito, ref_asignada = crear_producto(producto)

            if exito:
                self.cargar_productos()
                self.limpiar_formulario()
                messagebox.showinfo(
                    "Éxito", f"Producto guardado correctamente con la Referencia: {ref_asignada}"
                )

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo guardar el producto.\nDetalle: {e}"
            )

    def actualizar_producto_ui(self):
        if self.producto_seleccionado is None:
            messagebox.showwarning(
                "Advertencia", "Debes seleccionar un producto para actualizar."
            )
            return

        try:
            datos = {
                "marca": self.var_marca.get(),
                "talla": self.var_talla.get(),
                "color": self.var_color.get(),
                "cantidadStock": int(self.var_stock.get()),
                "valorVenta": int(self.var_valor_venta.get()),
                "ubicacion": self.var_ubicacion.get(),
            }

            if self.es_admin and self.var_valor_compra.get().strip():
                datos["valorCompra"] = int(self.var_valor_compra.get())

            actualizar_producto(self.producto_seleccionado, datos)
            self.cargar_productos()

            messagebox.showinfo(
                "Actualizado", "Producto actualizado correctamente."
            )

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar.\nDetalle: {e}")

    def eliminar_producto_ui(self):
        if self.producto_seleccionado is None:
            messagebox.showwarning(
                "Advertencia", "Debes seleccionar un producto para eliminar."
            )
            return

        try:
            eliminar_producto(self.producto_seleccionado)
            self.cargar_productos()
            self.limpiar_formulario()

            messagebox.showinfo("Eliminado", "Producto eliminado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar.\nDetalle: {e}")

    def al_seleccionar_producto(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return

        valores = self.tree.item(seleccion[0])["values"]

        if valores:
            self.producto_seleccionado = valores[0]

            self.lbl_ref.grid(row=0, column=0, sticky="e", padx=(10, 5), pady=6)
            self.entry_ref.grid(row=0, column=1, sticky="w", padx=(0, 15), pady=6, ipady=3)

            self.entry_ref.config(state="normal")
            self.var_ref.set(valores[0])
            self.entry_ref.config(state="readonly")

            self.var_marca.set(valores[1])
            self.var_talla.set(valores[2])
            self.var_color.set(valores[3])

            stock_texto = str(valores[4]).split(" ")[0]
            self.var_stock.set(stock_texto)

            if self.es_admin:
                self.var_valor_compra.set(valores[5])
                self.var_valor_venta.set(valores[6])
                self.var_ubicacion.set(valores[7])
            else:
                self.var_valor_compra.set("")
                self.var_valor_venta.set(valores[5])
                self.var_ubicacion.set(valores[6])

            stock_num = int(stock_texto)
            if stock_num <= 5:
                messagebox.showwarning(
                    "¡Alerta de Inventario!",
                    f"El producto seleccionado (Ref: {valores[0]} - {valores[1]}) tiene"
                    f" stock bajo: {stock_num} unidades disponibles.",
                )

    def cargar_productos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.tree.tag_configure("stock_bajo", background="#e62323")

        productos = listar_productos()
        LIMITE_STOCK_BAJO = 5

        for p in productos:
            es_stock_bajo = p.cantidadStock <= LIMITE_STOCK_BAJO

            if self.es_admin:
                values = (
                    p.numReferencia,
                    p.marca,
                    p.talla,
                    p.color,
                    f"{p.cantidadStock} (¡BAJO!)" if es_stock_bajo else p.cantidadStock,
                    p.valorCompra,
                    p.valorVenta,
                    p.ubicacion,
                )
            else:
                values = (
                    p.numReferencia,
                    p.marca,
                    p.talla,
                    p.color,
                    f"{p.cantidadStock} (¡BAJO!)" if es_stock_bajo else p.cantidadStock,
                    p.valorVenta,
                    p.ubicacion,
                )

            item_id = self.tree.insert("", "end", values=values)

            if es_stock_bajo:
                self.tree.item(item_id, tags=("stock_bajo",))

    def buscar_por_ref(self):
        texto = self.var_buscar.get().strip()

        if not texto:
            self.cargar_productos()
            return

        try:
            ref_buscar = int(texto)
        except ValueError:
            messagebox.showerror("Error", "La referencia debe ser numérica.")
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in listar_productos():
            if int(p.numReferencia) == ref_buscar:
                es_stock_bajo = p.cantidadStock <= 5

                if self.es_admin:
                    values = (
                        p.numReferencia,
                        p.marca,
                        p.talla,
                        p.color,
                        f"{p.cantidadStock} (¡BAJO!)" if es_stock_bajo else p.cantidadStock,
                        p.valorCompra,
                        p.valorVenta,
                        p.ubicacion,
                    )
                else:
                    values = (
                        p.numReferencia,
                        p.marca,
                        p.talla,
                        p.color,
                        f"{p.cantidadStock} (¡BAJO!)" if es_stock_bajo else p.cantidadStock,
                        p.valorVenta,
                        p.ubicacion,
                    )

                item_id = self.tree.insert("", "end", values=values)
                if es_stock_bajo:
                    self.tree.item(item_id, tags=("stock_bajo",))
                break

    def limpiar_busqueda(self):
        self.var_buscar.set("")
        self.cargar_productos()

    def limpiar_formulario(self):
        if hasattr(self, "lbl_ref") and hasattr(self, "entry_ref"):
            self.lbl_ref.grid_remove()
            self.entry_ref.grid_remove()

        self.var_ref.set("")
        self.var_marca.set("")
        self.var_talla.set("")
        self.var_color.set("")
        self.var_stock.set("")
        self.var_valor_compra.set("")
        self.var_valor_venta.set("")
        self.var_ubicacion.set("")

        self.producto_seleccionado = None

    def mostrar_solo_stock_bajo(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        productos = listar_productos()
        LIMITE_STOCK_BAJO = 5
        encontrados = False

        for p in productos:
            if p.cantidadStock <= LIMITE_STOCK_BAJO:
                encontrados = True

                if self.es_admin:
                    values = (
                        p.numReferencia,
                        p.marca,
                        p.talla,
                        p.color,
                        f"{p.cantidadStock} (¡BAJO!)",
                        p.valorCompra,
                        p.valorVenta,
                        p.ubicacion,
                    )
                else:
                    values = (
                        p.numReferencia,
                        p.marca,
                        p.talla,
                        p.color,
                        f"{p.cantidadStock} (¡BAJO!)",
                        p.valorVenta,
                        p.ubicacion,
                    )

                item_id = self.tree.insert("", "end", values=values)
                self.tree.item(item_id, tags=("stock_bajo",))

        if not encontrados:
            messagebox.showinfo(
                "Inventario", "No hay productos con stock bajo actualmente."
            )