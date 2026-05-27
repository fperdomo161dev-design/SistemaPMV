# ui/ui_productos.py

import tkinter as tk
from tkinter import ttk, messagebox

from services.producto_service import listar_productos


COLOR_INPUT_BG = "#050509"
COLOR_TEXT = "#e5e7eb"


class ProductosFrame(ttk.Frame):

    def __init__(self, master, *args, **kwargs):

        super().__init__(master, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_ui()

        self.cargar_productos()

    def _build_ui(self):

        outer = ttk.Frame(self)

        outer.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20
        )

        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)
 
        # BUSCADOR
        search_frame = ttk.Frame(outer)

        search_frame.grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 10)
        )

        ttk.Label(
            search_frame,
            text="Buscar por Ref:"
        ).grid(
            row=0,
            column=0,
            padx=(0, 8)
        )

        self.var_buscar = tk.StringVar()

        entry_buscar = tk.Entry(
            search_frame,
            textvariable=self.var_buscar,
            width=15,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
        )

        entry_buscar.grid(
            row=0,
            column=1,
            padx=(0, 8)
        )

        entry_buscar.bind(
            "<Return>",
            lambda e: self.buscar_por_ref()
        )

        ttk.Button(
            search_frame,
            text="Buscar",
            command=self.buscar_por_ref
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        ttk.Button(
            search_frame,
            text="Limpiar",
            command=self.limpiar_busqueda
        ).grid(
            row=0,
            column=3,
            padx=5
        )
        # TABLA
        tabla_frame = ttk.Frame(outer)

        tabla_frame.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        tabla_frame.columnconfigure(0, weight=1)
        tabla_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tabla_frame,
            columns=(
                "ref",
                "marca",
                "talla",
                "color",
                "stock",
                "valor",
                "ubicacion",
            ),
            show="headings",
            height=14,
        )

        columnas = [
            ("ref", "Ref", 80),
            ("marca", "Marca", 120),
            ("talla", "Talla", 80),
            ("color", "Color", 120),
            ("stock", "Stock", 80),
            ("valor", "Valor", 120),
            ("ubicacion", "Ubicación", 120),
        ]

        for col, texto, ancho in columnas:

            self.tree.heading(
                col,
                text=texto
            )

            self.tree.column(
                col,
                width=ancho,
                anchor="center"
            )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar = ttk.Scrollbar(
            tabla_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

    # CARGAR PRODUCTOS

    def cargar_productos(self):

        for row in self.tree.get_children():

            self.tree.delete(row)

        productos = listar_productos()

        for p in productos:

            self.tree.insert(
                "",
                "end",
                values=(

                    p.numReferencia,

                    p.marca,

                    p.talla,

                    p.color,

                    p.cantidadStock,

                    p.valor,

                    p.ubicacion,
                ),
            )
    # BUSCAR
    def buscar_por_ref(self):

        texto = self.var_buscar.get().strip()

        if not texto:

            self.cargar_productos()

            return

        try:

            ref_buscar = int(texto)

        except ValueError:

            messagebox.showerror(
                "Error",
                "La referencia debe ser numérica."
            )

            return

        for row in self.tree.get_children():

            self.tree.delete(row)

        for p in listar_productos():

            if int(p.numReferencia) == ref_buscar:

                self.tree.insert(
                    "",
                    "end",
                    values=(

                        p.numReferencia,

                        p.marca,

                        p.talla,

                        p.color,

                        p.cantidadStock,

                        p.valor,

                        p.ubicacion,
                    ),
                )

                break

    # LIMPIAR
    def limpiar_busqueda(self):

        self.var_buscar.set("")

        self.cargar_productos()