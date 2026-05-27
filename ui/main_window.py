import tkinter as tk
from tkinter import ttk
from datetime import datetime

from models.empleado import Empleado
from ui.ui_productos import ProductosFrame

# COLORES

COLOR_BG = "#050509"
COLOR_SIDEBAR = "#020814"
COLOR_TOPBAR = "#050b16"
COLOR_CONTENT = "#050509"
COLOR_CARD = "#0b0f19"

COLOR_GOLD = "#f5d26b"
COLOR_TEXT = "#e5e7eb"


class MainWindow(tk.Toplevel):

    def __init__(self, master_root: tk.Tk, empleado: Empleado):

        super().__init__(master_root)

        self.empleado = empleado

        self.title("PMV - Sistema Inventario")

        try:
            self.state("zoomed")
        except Exception:
            self.attributes("-zoomed", True)

        self.configure(bg=COLOR_BG)

        self.nav_buttons = {}
        self.frames_contenido = {}

        self._configurar_grid()
        self._configurar_estilos()

        self._crear_sidebar()
        self._crear_topbar()
        self._crear_contenido()
        self._crear_frames()

        self.cambiar_vista("productos")

    # GRID PRINCIPAL

    def _configurar_grid(self):

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

    # ESTILOS
    def _configurar_estilos(self):

        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except Exception:
            pass

        # SIDEBAR
      

        style.configure(
            "PMV.Sidebar.TFrame",
            background=COLOR_SIDEBAR
        )

        style.configure(
            "PMV.Sidebar.TButton",
            background=COLOR_SIDEBAR,
            foreground=COLOR_TEXT,
            font=("Segoe UI", 11),
            padding=(18, 12),
            relief="flat",
            borderwidth=0,
            anchor="w"
        )

        style.map(
            "PMV.Sidebar.TButton",
            background=[("active", COLOR_GOLD)],
            foreground=[("active", "#111827")]
        )

        style.configure(
            "PMV.SidebarSelected.TButton",
            background=COLOR_GOLD,
            foreground="#111827",
            font=("Segoe UI", 11, "bold"),
            padding=(18, 12),
            relief="flat",
            borderwidth=0,
            anchor="w"
        )
# TOPBAR
        style.configure(
            "PMV.Topbar.TFrame",
            background=COLOR_TOPBAR
        )

        style.configure(
            "PMV.TopbarTitle.TLabel",
            background=COLOR_TOPBAR,
            foreground=COLOR_TEXT,
            font=("Segoe UI", 13, "bold")
        )

        style.configure(
            "PMV.TopbarUser.TLabel",
            background=COLOR_TOPBAR,
            foreground=COLOR_GOLD,
            font=("Segoe UI", 11, "bold")
        )

        style.configure(
            "PMV.Clock.TLabel",
            background=COLOR_TOPBAR,
            foreground=COLOR_TEXT,
            font=("Segoe UI", 10)
        )

        # CONTENT
        style.configure(
            "PMV.Content.TFrame",
            background=COLOR_CONTENT
        )

        style.configure(
            "PMV.Card.TFrame",
            background=COLOR_CARD
        )
        # TREEVIEW

        style.configure(
            "Treeview",
            background=COLOR_BG,
            foreground=COLOR_TEXT,
            fieldbackground=COLOR_BG,
            borderwidth=0,
            rowheight=30,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=COLOR_TOPBAR,
            foreground=COLOR_TEXT,
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", COLOR_GOLD)],
            foreground=[("selected", "#111827")]
        )

    # ROLES
    def _cargo_norm(self):

        return (
            getattr(self.empleado, "cargo", "")
            .strip()
            .lower()
        )

    def _es_admin(self):

        return self._cargo_norm() in (
            "admin",
            "administrador",
            "gerente"
        )

    def _crear_sidebar(self):

        sidebar = ttk.Frame(
            self,
            style="PMV.Sidebar.TFrame",
            width=240
        )

        sidebar.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="ns"
        )

        sidebar.grid_propagate(False)

        # LOGO
        lbl_logo = tk.Label(
            sidebar,
            text="PMV\nInventario",
            bg=COLOR_SIDEBAR,
            fg=COLOR_GOLD,
            font=("Segoe UI", 20, "bold"),
            justify="left"
        )

        lbl_logo.pack(
            anchor="w",
            padx=20,
            pady=(25, 40)
        )
        # BOTONES MENU
        botones = [
            ("Productos", "productos"),
        ]

        for texto, vista in botones:

            btn = ttk.Button(
                sidebar,
                text=texto,
                style="PMV.Sidebar.TButton",
                command=lambda v=vista: self.cambiar_vista(v)
            )

            btn.pack(
                fill="x",
                padx=10,
                pady=4
            )

            self.nav_buttons[vista] = btn

        # espacio flexible
        tk.Frame(
            sidebar,
            bg=COLOR_SIDEBAR
        ).pack(
            expand=True,
            fill="both"
        )

      
        # CERRAR SESION
       

        ttk.Button(
            sidebar,
            text="Cerrar sesión",
            style="PMV.Sidebar.TButton",
            command=self._cerrar_sesion
        ).pack(
            fill="x",
            padx=10,
            pady=(0, 20)
        )

    # TOPBAR

    def _crear_topbar(self):

        topbar = ttk.Frame(
            self,
            style="PMV.Topbar.TFrame",
            padding=(16, 10)
        )

        topbar.grid(
            row=0,
            column=1,
            sticky="ew"
        )

        topbar.columnconfigure(0, weight=1)

        ttk.Label(
            topbar,
            text="Sistema de Inventario PMV",
            style="PMV.TopbarTitle.TLabel"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        frame_right = ttk.Frame(
            topbar,
            style="PMV.Topbar.TFrame"
        )

        frame_right.grid(
            row=0,
            column=1,
            sticky="e"
        )

        texto_usuario = (
            f"{self.empleado.nombre} · "
            f"{self.empleado.cargo}"
        )

        ttk.Label(
            frame_right,
            text=texto_usuario,
            style="PMV.TopbarUser.TLabel"
        ).pack(
            side="left",
            padx=(0, 15)
        )

        self.lbl_clock = ttk.Label(
            frame_right,
            text="",
            style="PMV.Clock.TLabel"
        )

        self.lbl_clock.pack(side="left")

        self._actualizar_reloj()

  
    # CONTENIDO


    def _crear_contenido(self):

        self.content_container = ttk.Frame(
            self,
            style="PMV.Content.TFrame"
        )

        self.content_container.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=10,
            pady=10
        )

        self.content_container.columnconfigure(0, weight=1)
        self.content_container.rowconfigure(0, weight=1)

    # FRAMES
   

    def _crear_frames(self):

        frame_productos = ProductosFrame(
            self.content_container
        )

        frame_productos.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.frames_contenido["productos"] = frame_productos

    # CAMBIAR VISTA

    def cambiar_vista(self, vista):

        if vista not in self.frames_contenido:
            return

        for frame in self.frames_contenido.values():
            frame.grid_remove()

        frame = self.frames_contenido[vista]

        frame.grid()

        for nombre, btn in self.nav_buttons.items():

            if nombre == vista:

                btn.configure(
                    style="PMV.SidebarSelected.TButton"
                )

            else:

                btn.configure(
                    style="PMV.Sidebar.TButton"
                )

    # REFRESCAR PRODUCTOS

    def refrescar_productos(self):

        frame = self.frames_contenido.get("productos")

        if frame and hasattr(frame, "cargar_productos"):

            try:
                frame.cargar_productos()
            except Exception as e:
                print("Error refrescando productos:", e)

    # CLOCK

    def _actualizar_reloj(self):

        ahora = datetime.now().strftime(
            "%d/%m/%Y - %H:%M:%S"
        )

        self.lbl_clock.config(text=ahora)

        self.after(
            1000,
            self._actualizar_reloj
        )   
    # CERRAR SESION
    def _cerrar_sesion(self):

        self.destroy()