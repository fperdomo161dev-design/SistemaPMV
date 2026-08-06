import tkinter as tk
from tkinter import messagebox, simpledialog, ttk


class FacturaModal:
    #Ventana emergente (Modal)  para editar los datos y productos de una factura

    def __init__(self, parent, factura, al_confirmar_cb=None):
        self.parent = parent
        self.factura = factura or {}
        self.al_confirmar_cb = al_confirmar_cb  # Callback opcional
        self.items_editables = list(self.factura.get("items", []))

        self._crear_ventana()

    def _crear_ventana(self):
        self.modal = tk.Toplevel(self.parent)
        num_fac = self.factura.get("numero_factura", "")
        self.modal.title(f"Editar Factura {num_fac}".strip())
        self.modal.geometry("600x520")
        self.modal.configure(bg="#1e293b")
        self.modal.transient(self.parent)
        self.modal.grab_set()

        # Título
        tk.Label(
            self.modal,
            text="✏️ EDITAR FACTURA (DATOS Y ELEMENTOS)",
            font=("Helvetica", 12, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
        ).pack(pady=10)

        # Frame Cliente
        frame_cli = tk.LabelFrame(
            self.modal,
            text="Datos del Comprador",
            fg="#f8fafc",
            bg="#1e293b",
            font=("Helvetica", 10, "bold"),
        )
        frame_cli.pack(fill="x", padx=15, pady=5)

        cliente = self.factura.get("cliente", {})
        if not isinstance(cliente, dict):
            cliente = {}

        tk.Label(frame_cli, text="Cédula:", fg="white", bg="#1e293b").grid(
            row=0, column=0, sticky="w", padx=5, pady=4
        )
        self.ent_cedula = tk.Entry(frame_cli, width=15)
        self.ent_cedula.insert(0, str(cliente.get("cedula", "")))
        self.ent_cedula.grid(row=0, column=1, padx=5, pady=4)

        tk.Label(frame_cli, text="Nombre:", fg="white", bg="#1e293b").grid(
            row=0, column=2, sticky="w", padx=5, pady=4
        )
        self.ent_nombre = tk.Entry(frame_cli, width=25)
        self.ent_nombre.insert(0, str(cliente.get("nombre", "")))
        self.ent_nombre.grid(row=0, column=3, padx=5, pady=4)

        tk.Label(frame_cli, text="Correo:", fg="white", bg="#1e293b").grid(
            row=1, column=0, sticky="w", padx=5, pady=4
        )
        self.ent_correo = tk.Entry(frame_cli, width=35)
        self.ent_correo.insert(0, str(cliente.get("correo", "")))
        self.ent_correo.grid(
            row=1, column=1, columnspan=3, sticky="w", padx=5, pady=4
        )

        # Frame Tabla de Productos
        frame_items = tk.LabelFrame(
            self.modal,
            text="Elementos / Productos",
            fg="#f8fafc",
            bg="#1e293b",
            font=("Helvetica", 10, "bold"),
        )
        frame_items.pack(fill="both", expand=True, padx=15, pady=5)

        self.tabla = ttk.Treeview(
            frame_items,
            columns=("codigo", "nombre", "cantidad", "precio"),
            show="headings",
            height=5,
        )
        self.tabla.heading("codigo", text="Ref/Cód")
        self.tabla.heading("nombre", text="Producto")
        self.tabla.heading("cantidad", text="Cant.")
        self.tabla.heading("precio", text="Precio Unit.")
        self.tabla.column("codigo", width=90)
        self.tabla.column("nombre", width=220)
        self.tabla.column("cantidad", width=60, anchor="center")
        self.tabla.column("precio", width=90, anchor="e")
        self.tabla.pack(fill="both", expand=True, padx=5, pady=5)

        self._recargar_tabla()

        tk.Button(
            frame_items,
            text="✏️ Cambiar Cantidad del Producto",
            bg="#0284c7",
            fg="white",
            font=("Helvetica", 9, "bold"),
            command=self._cambiar_cantidad,
        ).pack(pady=4)

        tk.Button(
            self.modal,
            text="✅ Cargar Cambios a la Factura",
            bg="#8b5cf6",
            fg="white",
            font=("Helvetica", 10, "bold"),
            command=self._confirmar,
        ).pack(pady=8)

    def _extraer_float(self, valor):
        #Convierte valores numéricos o cadenas con formato de moneda a float
        if isinstance(valor, (int, float)):
            return float(valor)
        if isinstance(valor, str):
            limpio = (
                valor.replace("$", "").replace(",", "").replace(" ", "").strip()
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

        # Ejecutamos el callback solo si fue proporcionado
        if callable(self.al_confirmar_cb):
            self.al_confirmar_cb(datos_cliente, self.items_editables)

        self.modal.destroy()