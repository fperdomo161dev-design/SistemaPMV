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

        #botones    

        btn = ttk.Frame(form)

        btn.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(btn, text="Guardar", command=self.guardar).grid(row=0, column=0)
        ttk.Button(btn, text="Actualizar", command=self.actualizar).grid(row=0, column=1)
        ttk.Button(btn, text="Eliminar", command=self.eliminar).grid(row=0, column=2)
        ttk.Button(btn, text="Limpiar", command=self.limpiar_formulario).grid(row=0, column=3)

        # instrucciones boton guardar

    def guardar(self):

        try:
            emp = Empleado(
                cedula=self.var_cedula.get(),
                nombre=self.var_nombre.get(),
                cargo=self.var_cargo.get(),
                usuario=self.var_usuario.get(),
                clave=self.var_clave.get()
            )

            ok = crear_empleado(emp)

            if not ok:
                messagebox.showwarning("Aviso", "La cédula ya existe")
                return

            self.cargar_empleados()
            messagebox.showinfo("OK", "Empleado creado correctamente")

        except Exception as e:
            messagebox.showerror("Error", str(e))

            # guardar 
    def guardar(self):

        try:
            emp = Empleado(
                cedula=self.var_cedula.get(),
                nombre=self.var_nombre.get(),
                cargo=self.var_cargo.get(),
                usuario=self.var_usuario.get(),
                clave=self.var_clave.get()
            )

            ok = crear_empleado(emp)

            if not ok:
                messagebox.showwarning("Aviso", "La cédula ya existe")
                return

            self.cargar_empleados()
            messagebox.showinfo("OK", "Empleado creado correctamente")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # instrucciones boton actualizar

    def actualizar(self):

        if not self.empleado_seleccionado:
            messagebox.showwarning("Aviso", "Selecciona un empleado")
            return

        try:
            data = {
                "nombre": self.var_nombre.get(),
                "cargo": self.var_cargo.get(),
                "usuario": self.var_usuario.get(),
                "clave": self.var_clave.get()
            }

            actualizar_empleado(self.empleado_seleccionado, data)

            self.cargar_empleados()
            messagebox.showinfo("OK", "Empleado actualizado correctamente")

        except Exception as e:
            messagebox.showerror("Error", str(e))

# instrucciones boton eliminar
    def eliminar(self):

        if not self.empleado_seleccionado:
            messagebox.showwarning("Aviso", "Selecciona un empleado")
            return

        try:
            eliminar_empleado(self.empleado_seleccionado)

            self.cargar_empleados()
            messagebox.showinfo("OK", "Empleado eliminado correctamente")

        except Exception as e:
            messagebox.showerror("Error", str(e))

            # Seleccion
    def seleccionar_empleado(self, event):

        sel = self.tree.selection()
        if not sel:
              return

        v = self.tree.item(sel[0])["values"]

        self.empleado_seleccionado = v[0]

        self.var_cedula.set(v[0])
        self.var_nombre.set(v[1])
        self.var_cargo.set(v[2])
        self.var_usuario.set(v[3])

    # Cargar empleados

    def cargar_empleados(self):

        for i in self.tree.get_children():
            self.tree.delete(i)

        for e in listar_empleados():
            self.tree.insert("", "end", values=(
                e.cedula,
                e.nombre,
                e.cargo,
                e.usuario
            ))

    # Limpiar formulario

    def limpiar_formulario(self):

        self.var_cedula.set("")
        self.var_nombre.set("")
        self.var_cargo.set("")
        self.var_usuario.set("")
        self.var_clave.set("")
        self.empleado_seleccionado = None

    # Buscar

    def buscar(self):

        txt = self.var_buscar.get().strip()

        if not txt:
            self.cargar_empleados()
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        for e in listar_empleados():
            if e.cedula == txt:
                self.tree.insert("", "end", values=(
                    e.cedula,
                    e.nombre,
                    e.cargo,
                    e.usuario
                ))
                break

    # Limpiar búsqueda
    def limpiar_busqueda(self):

        self.var_buscar.set("")
        self.cargar_empleados()