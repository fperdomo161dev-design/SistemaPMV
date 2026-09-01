import tkinter as tk
from tkinter import messagebox, simpledialog, ttk


# PALETA DE COLORES DEL SISTEMA

COLOR_BG = "#0A0D14" 
COLOR_CARD = "#1A2035"  
COLOR_BORDER = "#252D47"  
COLOR_TEXT = "#F3F4F6"  
COLOR_TEXT_MUTED = "#9CA3AF"  
COLOR_GOLD = "#F59E0B"  
COLOR_GOLD_HOVER = "#D97706"  
COLOR_ACCENT_BLUE = "#0284C7"  


class FacturaModal:
    """Ventana emergente (Modal) para editar los datos y productos de una factura."""

    def __init__(self, parent, factura, al_confirmar_cb=None):
        self.parent = parent
        self.factura = factura or {}
        self.al_confirmar_cb = al_confirmar_cb  # Callback opcional
        self.items_editables = [
            dict(item) for item in self.factura.get("items", [])
        ]

        self._crear_ventana()

    def _crear_campo_entry(self, padre, variable_txt=None):
        """Genera un campo Entry con los estilos del tema oscuro."""
        return tk.Entry(
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
        )

    def _crear_ventana(self):
        self.modal = tk.Toplevel(self.parent)
        num_fac = self.factura.get("numero_factura", "")
        self.modal.title(f"Editar Factura {num_fac}".strip())
        self.modal.geometry("640x560")
        self.modal.resizable(False, False)
        self.modal.configure(bg=COLOR_BG)

        self.modal.transient(self.parent)
        self.modal.grab_set()

        # Título Principal
        tk.Label(
            self.modal,
            text="✏️ EDITAR FACTURA (DATOS Y ELEMENTOS)",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_GOLD,
            bg=COLOR_BG,
        ).pack(pady=(15, 5))

        # --- FRAME CLIENTE ---
        frame_cli = tk.Frame(
            self.modal,
            bg=COLOR_CARD,
            bd=1,
            relief="solid",
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_BORDER,
            highlightthickness=1,
        )
        frame_cli.pack(fill="x", padx=15, pady=8, ipady=5)

        tk.Label(
            frame_cli,
            text="👤 Datos del Comprador",
            fg=COLOR_GOLD,
            bg=COLOR_CARD,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=(8, 5))

        cliente = self.factura.get("cliente", {})
        if not isinstance(cliente, dict):
            cliente = {}

        # Cédula
        tk.Label(
            frame_cli,
            text="Cédula:",
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD,
            font=("Segoe UI", 9),
        ).grid(row=1, column=0, sticky="w", padx=(10, 2), pady=4)
        self.ent_cedula = self._crear_campo_entry(frame_cli)
        self.ent_cedula.config(width=14)
        self.ent_cedula.insert(0, str(cliente.get("cedula", "")))
        self.ent_cedula.grid(row=1, column=1, padx=(0, 10), pady=4, sticky="w")

        # Nombre
        tk.Label(
            frame_cli,
            text="Nombre:",
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD,
            font=("Segoe UI", 9),
        ).grid(row=1, column=2, sticky="w", padx=(5, 2), pady=4)
        self.ent_nombre = self._crear_campo_entry(frame_cli)
        self.ent_nombre.config(width=26)
        self.ent_nombre.insert(0, str(cliente.get("nombre", "")))
        self.ent_nombre.grid(row=1, column=3, padx=(0, 10), pady=4, sticky="ew")

        # Correo
        tk.Label(
            frame_cli,
            text="Correo:",
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD,
            font=("Segoe UI", 9),
        ).grid(row=2, column=0, sticky="w", padx=(10, 2), pady=(4, 8))
        self.ent_correo = self._crear_campo_entry(frame_cli)
        self.ent_correo.insert(0, str(cliente.get("correo", "")))
        self.ent_correo.grid(
            row=2,
            column=1,
            columnspan=3,
            sticky="ew",
            padx=(0, 10),
            pady=(4, 8),
        )

        frame_cli.columnconfigure(3, weight=1)

        # FRAME PRODUCTOS 
        frame_items = tk.Frame(
            self.modal,
            bg=COLOR_CARD,
            bd=1,
            relief="solid",
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_BORDER,
            highlightthickness=1,
        )
        frame_items.pack(fill="both", expand=True, padx=15, pady=8)

        tk.Label(
            frame_items,
            text="📦 Elementos / Productos",
            fg=COLOR_GOLD,
            bg=COLOR_CARD,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=10, pady=(8, 5))

        # Configuración Treeview estilizado
        style = ttk.Style(self.modal)
        style.configure(
            "Modal.Treeview",
            background=COLOR_BG,
            foreground=COLOR_TEXT,
            fieldbackground=COLOR_BG,
            borderwidth=0,
            rowheight=28,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Modal.Treeview.Heading",
            background=COLOR_CARD,
            foreground=COLOR_GOLD,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
        )
        style.map(
            "Modal.Treeview",
            background=[("selected", COLOR_GOLD)],
            foreground=[("selected", "#000000")],
        )

        self.tabla = ttk.Treeview(
            frame_items,
            columns=("codigo", "nombre", "cantidad", "precio"),
            show="headings",
            height=5,
            style="Modal.Treeview",
        )
        self.tabla.heading("codigo", text="Ref/Cód")
        self.tabla.heading("nombre", text="Producto")
        self.tabla.heading("cantidad", text="Cant.")
        self.tabla.heading("precio", text="Precio Unit.")

        self.tabla.column("codigo", width=100)
        self.tabla.column("nombre", width=240)
        self.tabla.column("cantidad", width=60, anchor="center")
        self.tabla.column("precio", width=110, anchor="e")

        self.tabla.pack(fill="both", expand=True, padx=10, pady=5)

        self._recargar_tabla()

        btn_cambiar = tk.Button(
            frame_items,
            text="✏️ Cambiar Cantidad del Producto",
            bg=COLOR_ACCENT_BLUE,
            fg="white",
            activebackground="#0369A1",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            bd=0,
            cursor="hand2",
            command=self._cambiar_cantidad,
        )
        btn_cambiar.pack(pady=(4, 10))

        # --- BOTÓN CONFIRMAR Y GENERAR ---
        btn_confirmar = tk.Button(
            self.modal,
            text="✅ Cargar Cambios y Actualizar Factura",
            bg=COLOR_GOLD,
            fg="#111827",
            activebackground=COLOR_GOLD_HOVER,
            activeforeground="#111827",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            cursor="hand2",
            command=self._confirmar,
        )
        btn_confirmar.pack(fill="x", padx=15, pady=(5, 15), ipady=5)

    def _extraer_float(self, valor):
        if isinstance(valor, (int, float)):
            return float(valor)
        if isinstance(valor, str):
            limpio = (
                valor.replace("$", "")
                .replace(",", "")
                .replace(" ", "")
                .strip()
            )
            try:
                return float(limpio)
            except ValueError:
                return 0.0
        return 0.0

    def _recargar_tabla(self):
        for r in self.tabla.get_children():
            self.tabla.delete(r)
        for idx, it in enumerate(self.items_editables):
            val_precio = it.get("precio_unitario", it.get("precio", 0))
            p_unit = self._extraer_float(val_precio)
            self.tabla.insert(
                "",
                "end",
                iid=idx,
                values=(
                    it.get("codigo", it.get("referencia", "")),
                    it.get("nombre", it.get("producto", "")),
                    it.get("cantidad", 1),
                    f"${p_unit:,.2f}",
                ),
            )

    def _cambiar_cantidad(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning(
                "Atención",
                "Seleccione un producto para modificar.",
                parent=self.modal,
            )
            return
        idx = int(sel[0])
        item = self.items_editables[idx]
        nueva_cant = simpledialog.askinteger(
            "Editar Cantidad",
            f"Nueva cantidad para '{item.get('nombre', item.get('producto', ''))}':",
            initialvalue=item.get("cantidad", 1),
            parent=self.modal,
        )
        if nueva_cant is not None and nueva_cant > 0:
            val_precio = item.get("precio_unitario", item.get("precio", 0))
            p_unit = self._extraer_float(val_precio)
            item["cantidad"] = nueva_cant
            item["precio_unitario"] = p_unit
            item["precio"] = p_unit
            item["subtotal"] = nueva_cant * p_unit
            self._recargar_tabla()

    def _confirmar(self):
        datos_cliente = {
            "cedula": self.ent_cedula.get().strip(),
            "nombre": self.ent_nombre.get().strip(),
            "correo": self.ent_correo.get().strip(),
        }

        
        if callable(self.al_confirmar_cb):
            self.al_confirmar_cb(datos_cliente, self.items_editables)

        self.modal.destroy()