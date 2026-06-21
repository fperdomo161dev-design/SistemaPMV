import tkinter as tk
from tkinter import ttk, messagebox

from services.empleado_service import (
    listar_empleados,
    crear_empleado,
    actualizar_empleado,
    eliminar_empleado
)

from models.empleado import Empleado

COLOR_INPUT_BG = "#050509"
COLOR_TEXT = "#e5e7eb"


class EmpleadosFrame(ttk.Frame):

    def __init__(self, master):

        super().__init__(master)

        self.empleado_seleccionado = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_ui()
        self.cargar_empleados()

        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_empleado)

    def _build_ui(self):

        outer = ttk.Frame(self)

        outer.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        # Buscar
        search = ttk.Frame(outer)
        search.grid(row=0, column=0, sticky="w", pady=10)

        ttk.Label(search, text="Buscar Cédula:").grid(row=0, column=0)

        self.var_buscar = tk.StringVar()

        tk.Entry(
            search,
            textvariable=self.var_buscar,
            width=15,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT
        ).grid(row=0, column=1, padx=5)

        ttk.Button(search, text="Buscar", command=self.buscar).grid(row=0, column=2)
        ttk.Button(search, text="Limpiar", command=self.limpiar_busqueda).grid(row=0, column=3)

        # Tabla de empleados

        frame = ttk.Frame(outer)

        frame.grid(row=1, column=0, sticky="nsew")

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            frame,
            columns=("cedula", "nombre", "cargo", "usuario"),
            show="headings",
            height=14
        )

        self.tree.heading("cedula", text="Cédula")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("cargo", text="Cargo")
        self.tree.heading("usuario", text="Usuario")

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Formulario

        form = ttk.Frame(outer)

        form.grid(row=2, column=0, pady=20, sticky="w")

        self.var_cedula = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_cargo = tk.StringVar()
        self.var_usuario = tk.StringVar()
        self.var_clave = tk.StringVar()

        ttk.Label(form, text="Cédula").grid(row=0, column=0)
        tk.Entry(form, textvariable=self.var_cedula).grid(row=0, column=1)

        ttk.Label(form, text="Nombre").grid(row=1, column=0)
        tk.Entry(form, textvariable=self.var_nombre).grid(row=1, column=1)

        ttk.Label(form, text="Cargo").grid(row=2, column=0)
        tk.Entry(form, textvariable=self.var_cargo).grid(row=2, column=1)

        ttk.Label(form, text="Usuario").grid(row=3, column=0)
        tk.Entry(form, textvariable=self.var_usuario).grid(row=3, column=1)

        ttk.Label(form, text="Clave").grid(row=4, column=0)
        tk.Entry(form, textvariable=self.var_clave, show="*").grid(row=4, column=1)