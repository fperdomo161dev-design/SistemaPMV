# ui/ui_productos.py

import tkinter as tk
from tkinter import ttk, messagebox

from services.producto_service import (
    listar_productos,
    crear_producto,
    actualizar_producto,
    eliminar_producto
)

from models.producto import Producto


COLOR_INPUT_BG = "#050509"
COLOR_TEXT = "#e5e7eb"


class ProductosFrame(ttk.Frame):

    def __init__(self, master, *args, **kwargs):

        super().__init__(master, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_ui()

        self.cargar_productos()

        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_producto)

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

        # encabezado de tabla

        self.tree.heading("ref", text="Referencia")
        self.tree.heading("marca", text="Marca")
        self.tree.heading("talla", text="Talla")
        self.tree.heading("color", text="Color")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("valor", text="Valor")
        self.tree.heading("ubicacion", text="Ubicación")

        self.tree.grid(row=0, column=0, sticky="nsew")

         # FORMULARIO
        formulario = ttk.Frame(outer)

        formulario.grid(
            row=2,
            column=0,
            pady=20,
            sticky="w"
        )

        # VARIABLES
        self.var_ref = tk.StringVar()
        self.var_marca = tk.StringVar()
        self.var_talla = tk.StringVar()
        self.var_color = tk.StringVar()
        self.var_stock = tk.StringVar()
        self.var_valor = tk.StringVar()
        self.var_ubicacion = tk.StringVar()

        ttk.Label(formulario, text="Referencia").grid(row=0, column=0)
        tk.Entry(formulario, textvariable=self.var_ref).grid(row=0, column=1)

        ttk.Label(formulario, text="Marca").grid(row=1, column=0)
        tk.Entry(formulario, textvariable=self.var_marca).grid(row=1, column=1)

        ttk.Label(formulario, text="Talla").grid(row=2, column=0)
        tk.Entry(formulario, textvariable=self.var_talla).grid(row=2, column=1)

        ttk.Label(formulario, text="Color").grid(row=3, column=0)
        tk.Entry(formulario, textvariable=self.var_color).grid(row=3, column=1)

        ttk.Label(formulario, text="Stock").grid(row=4, column=0)
        tk.Entry(formulario, textvariable=self.var_stock).grid(row=4, column=1)

        ttk.Label(formulario, text="Valor").grid(row=5, column=0)
        tk.Entry(formulario, textvariable=self.var_valor).grid(row=5, column=1)

        ttk.Label(formulario, text="Ubicación").grid(row=6, column=0)
        tk.Entry(formulario, textvariable=self.var_ubicacion).grid(row=6, column=1)

          # botones
        botones_frame = ttk.Frame(formulario)

        botones_frame.grid(
            row=7,
            column=0,
            columnspan=2,
            pady=15
        )

        # boton guardar
        ttk.Button(
            botones_frame,
            text="Guardar",
            command=self.guardar_producto
        ).grid(row=0, column=0)

        # boton actualizar
        ttk.Button(
            botones_frame,
            text="Actualizar",
            command=self.actualizar_producto_ui
        ).grid(row=0, column=1)

        # boton eliminar
        ttk.Button(
            botones_frame,
            text="Eliminar",
            command=self.eliminar_producto_ui
        ).grid(row=0, column=2)

        # boton limpiar formulario
        ttk.Button(
           botones_frame,
            text="Limpiar",
            command=self.limpiar_formulario
            ).grid(row=0, column=3)

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