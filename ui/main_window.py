from datetime import datetime
import tkinter as tk
from tkinter import ttk
from database.conexion import get_db
from models.empleado import Empleado
from services.factura_pdf_service import FacturaPDFService
from ui.contabilidad.ui_contabilidad import ContabilidadFrame
from ui.pos import PosFrame
from ui.ui_clientes import ClientesFrame
from ui.ui_configuracion import ConfiguracionFrame
from ui.ui_empleados import EmpleadosFrame
from ui.ui_productos import ProductosFrame


# COLORES DE LA APLICACIÓN

COLOR_BG = "#0A0D14"  
COLOR_SIDEBAR = "#111625"  
COLOR_TOPBAR = "#111625"  
COLOR_CONTENT = "#0A0D14"  
COLOR_CARD = "#1A2035"  
COLOR_BORDER = "#252D47" 

COLOR_GOLD = "#F59E0B"  
COLOR_GOLD_HOVER = "#F59E0B"  
COLOR_TEXT = "#F3F4F6" 
COLOR_TEXT_MUTED = "#9CA3AF"  
COLOR_SUCCESS = "#10B981"  


class MainWindow(tk.Toplevel):

    def __init__(
        self, master_root: tk.Tk, empleado: Empleado, db=None, pdf_service=None
    ):
        super().__init__(master_root)

        self.empleado = empleado
      
        self.db = db if db is not None else get_db()
        self.pdf_service = (
            pdf_service if pdf_service is not None else FacturaPDFService()
        )

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

      
        self._mostrar_bienvenida()

   
    # GRID PRINCIPAL
   
    def _configurar_grid(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

    
    # ESTILOS TTK
   
    def _configurar_estilos(self):
        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except Exception:
            pass

        # SIDEBAR
        style.configure("PMV.Sidebar.TFrame", background=COLOR_SIDEBAR)

        style.configure(
            "PMV.Sidebar.TButton",
            background=COLOR_SIDEBAR,
            foreground=COLOR_TEXT_MUTED,
            font=("Segoe UI", 11),
            padding=(18, 12),
            relief="flat",
            borderwidth=0,
            anchor="w",
        )

        style.map(
            "PMV.Sidebar.TButton",
            background=[("active", COLOR_CARD)],
            foreground=[("active", COLOR_GOLD)],
        )

        style.configure(
            "PMV.SidebarSelected.TButton",
            background=COLOR_GOLD,
            foreground="#22201E",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 12),
            relief="flat",
            borderwidth=0,
            anchor="w",
        )

        style.configure(
            "PMV.Logout.TButton",
            background=COLOR_SIDEBAR,
            foreground="#EF4444",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 10),
            relief="flat",
            anchor="w",
        )

        # TOPBAR
        style.configure("PMV.Topbar.TFrame", background=COLOR_TOPBAR)

        style.configure(
            "PMV.TopbarTitle.TLabel",
            background=COLOR_TOPBAR,
            foreground=COLOR_TEXT,
            font=("Segoe UI", 13, "bold"),
        )

        style.configure(
            "PMV.TopbarUser.TLabel",
            background=COLOR_TOPBAR,
            foreground=COLOR_GOLD,
            font=("Segoe UI", 11, "bold"),
        )

        style.configure(
            "PMV.Clock.TLabel",
            background=COLOR_TOPBAR,
            foreground=COLOR_TEXT_MUTED,
            font=("Segoe UI", 10),
        )

        # CONTENT
        style.configure("PMV.Content.TFrame", background=COLOR_CONTENT)
        style.configure("PMV.Card.TFrame", background=COLOR_CARD)

        # TREEVIEW
        style.configure(
            "Treeview",
            background=COLOR_CARD,
            foreground=COLOR_TEXT,
            fieldbackground=COLOR_CARD,
            borderwidth=0,
            rowheight=34,
            font=("Segoe UI", 10),
        )

        style.configure(
            "Treeview.Heading",
            background=COLOR_SIDEBAR,
            foreground=COLOR_GOLD,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )

        style.map(
            "Treeview",
            background=[("selected", COLOR_GOLD)],
            foreground=[("selected", "#0B0F19")],
        )

    
    # VALIDACIÓN DE ROLES
   
    def _cargo_norm(self):
        return getattr(self.empleado, "cargo", "").strip().lower()

    def _es_admin(self):
        return self._cargo_norm() in ("admin", "administrador", "gerente")

    def _es_auxiliar(self):
        return self._cargo_norm() in ("auxiliar", "aux")

    
    # CREACIÓN DE LA BARRA LATERAL (SIDEBAR)
  
    def _crear_sidebar(self):
        sidebar = ttk.Frame(self, style="PMV.Sidebar.TFrame", width=250)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")
        sidebar.grid_propagate(False)

        # Cargar nombre comercial desde MongoDB
        config_empresa = self.db["config_sistema"].find_one({"tipo": "datos_empresa"})
        nombre_empresa = (
            config_empresa.get("nombre", "PMV Inventario")
            if config_empresa
            else "PMV Inventario"
        )

        # LOGO / NOMBRE COMERCIAL DINÁMICO
        self.lbl_logo = tk.Label(
            sidebar,
            text=nombre_empresa,
            bg=COLOR_SIDEBAR,
            fg=COLOR_GOLD,
            font=("Segoe UI", 16, "bold"),
            justify="left",
            wraplength=210,
        )
        self.lbl_logo.pack(anchor="w", padx=20, pady=(25, 30))

        tk.Frame(sidebar, bg=COLOR_BORDER, height=1).pack(
            fill="x", padx=15, pady=(0, 15)
        )

        # BOTONES DEL MENÚ
        botones = []
        if self._es_admin():
            botones.append(("POS / Ventas", "pos"))

        botones.extend([
            ("Productos", "productos"),
            ("Clientes", "clientes"),
            ("Empleados", "empleados"),
            ("Contabilidad", "contabilidad"),
        ])

        for texto, vista in botones:
            if vista == "empleados" and not self._es_admin():
                continue
            if vista == "clientes" and self._es_auxiliar():
                continue
            if vista in ("pos", "contabilidad") and not self._es_admin():
                continue

            btn = ttk.Button(
                sidebar,
                text=texto,
                style="PMV.Sidebar.TButton",
                command=lambda v=vista: self.cambiar_vista(v),
            )
            btn.pack(fill="x", padx=10, pady=4)
            self.nav_buttons[vista] = btn

        # Espaciador flexible
        tk.Frame(sidebar, bg=COLOR_SIDEBAR).pack(expand=True, fill="both")

        # BOTÓN CONFIGURACIÓN (Solo Administradores)
        if self._es_admin():
            btn_config = tk.Button(
                sidebar,
                text="⚙️ Configuración",
                bg=COLOR_CARD,
                fg=COLOR_GOLD,
                activebackground=COLOR_BORDER,
                activeforeground=COLOR_GOLD,
                font=("Segoe UI", 10, "bold"),
                bd=1,
                relief="flat",
                cursor="hand2",
                command=lambda: self.mostrar_frame("configuracion")
            )
            btn_config.pack(fill="x", padx=10, pady=(0, 10))

        # Tarjeta inferior con datos del usuario logueado
        card_user = tk.Frame(
            sidebar,
            bg=COLOR_CARD,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
        )
        card_user.pack(fill="x", padx=10, pady=(0, 15))

        lbl_status = tk.Label(
            card_user,
            text="●",
            bg=COLOR_CARD,
            fg=COLOR_SUCCESS,
            font=("Segoe UI", 12),
        )
        lbl_status.pack(side="left", padx=(10, 5), pady=8)

        user_info = tk.Frame(card_user, bg=COLOR_CARD)
        user_info.pack(side="left", fill="both", expand=True, pady=6)

        tk.Label(
            user_info,
            text=self.empleado.nombre,
            bg=COLOR_CARD,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            user_info,
            text=self.empleado.cargo.capitalize(),
            bg=COLOR_CARD,
            fg=COLOR_GOLD,
            font=("Segoe UI", 8),
            anchor="w",
        ).pack(fill="x")

        # BOTÓN CERRAR SESIÓN
        ttk.Button(
            sidebar,
            text="Cerrar sesión",
            style="PMV.Logout.TButton",
            command=self._cerrar_sesion,
        ).pack(fill="x", padx=10, pady=(0, 20))

    
    # CREACIÓN DE LA BARRA SUPERIOR (TOPBAR)
  
    def _crear_topbar(self):
        topbar = ttk.Frame(self, style="PMV.Topbar.TFrame", padding=(16, 10))
        topbar.grid(row=0, column=1, sticky="ew")
        topbar.columnconfigure(0, weight=1)

        self.lbl_topbar_title = ttk.Label(
            topbar,
            text="Sistema de Inventario ",
            style="PMV.TopbarTitle.TLabel",
        )
        self.lbl_topbar_title.grid(row=0, column=0, sticky="w")

        frame_right = ttk.Frame(topbar, style="PMV.Topbar.TFrame")
        frame_right.grid(row=0, column=1, sticky="e")

        self.lbl_clock = ttk.Label(
            frame_right, text="", style="PMV.Clock.TLabel"
        )
        self.lbl_clock.pack(side="left")

        self._actualizar_reloj()

        tk.Frame(self, bg=COLOR_BORDER, height=1).grid(
            row=0, column=1, sticky="sew"
        )

   
    # CONTENEDOR DE CONTENIDO PRINCIPAL
  
    def _crear_contenido(self):
        self.content_container = ttk.Frame(self, style="PMV.Content.TFrame")
        self.content_container.grid(
            row=1, column=1, sticky="nsew", padx=10, pady=10
        )

        self.content_container.columnconfigure(0, weight=1)
        self.content_container.rowconfigure(0, weight=1)

  
   # INICIALIZACIÓN DE VISTAS (FRAMES)
    
    def _crear_frames(self):
        # POS / Ventas (Visible para Administradores y Vendedores, oculto para Auxiliares)
        if not self._es_auxiliar():
            frame_pos = PosFrame(
                self.content_container,
                db=self.db,
                usuario_actual=self.empleado,
                pdf_service=self.pdf_service,
            )
            frame_pos.grid(row=0, column=0, sticky="nsew")
            self.frames_contenido["pos"] = frame_pos

        # Productos
        frame_productos = ProductosFrame(
            self.content_container, usuario_actual=self.empleado
        )
        frame_productos.grid(row=0, column=0, sticky="nsew")
        self.frames_contenido["productos"] = frame_productos

        # Clientes (Se crea para todos MENOS el auxiliar)
        if not self._es_auxiliar():
            frame_clientes = ClientesFrame(
                self.content_container, usuario_actual=self.empleado
            )
            frame_clientes.grid(row=0, column=0, sticky="nsew")
            self.frames_contenido["clientes"] = frame_clientes

        # Empleados (Solo Administradores)
        if self._es_admin():
            frame_empleados = EmpleadosFrame(
                self.content_container, usuario_actual=self.empleado
            )
            frame_empleados.grid(row=0, column=0, sticky="nsew")
            self.frames_contenido["empleados"] = frame_empleados

        # Contabilidad (Solo Administradores)
        if self._es_admin():
            frame_contabilidad = ContabilidadFrame(
                self.content_container, usuario_actual=self.empleado
            )
            frame_contabilidad.grid(row=0, column=0, sticky="nsew")
            self.frames_contenido["contabilidad"] = frame_contabilidad

        # Configuración del Sistema y Facturas (Solo Administradores)
        if self._es_admin():
            frame_config = ConfiguracionFrame(
                self.content_container, usuario_actual=self.empleado
            )
            frame_config.grid(row=0, column=0, sticky="nsew")
            self.frames_contenido["configuracion"] = frame_config

    
    # ANUNCIO DE BIENVENIDA PERSONALIZADO
  
    def _mostrar_bienvenida(self):
        for frame in self.frames_contenido.values():
            frame.grid_remove()

        frame_bienvenida = tk.Frame(self.content_container, bg=COLOR_CARD)
        frame_bienvenida.grid(row=0, column=0, sticky="nsew")
        self.frames_contenido["bienvenida"] = frame_bienvenida

        frame_bienvenida.columnconfigure(0, weight=1)
        frame_bienvenida.rowconfigure(0, weight=1)

        contenido_centro = tk.Frame(frame_bienvenida, bg=COLOR_CARD)
        contenido_centro.grid(row=0, column=0)

        tk.Label(
            contenido_centro,
            text="¡Bienvenido a su sistema!",
            bg=COLOR_CARD,
            fg=COLOR_GOLD,
            font=("Segoe UI", 26, "bold"),
        ).pack(pady=(0, 10))

        tk.Label(
            contenido_centro,
            text="Tus pies en nuestras manos",
            bg=COLOR_CARD,
            fg=COLOR_TEXT,
            font=("Segoe UI", 16, "italic"),
        ).pack(pady=(0, 30))

        btn_empezar = tk.Button(
            contenido_centro,
            text="Continuar al Sistema",
            bg=COLOR_GOLD,
            fg="#111827",
            font=("Segoe UI", 12, "bold"),
            bd=0,
            padx=20,
            pady=10,
            command=self._ir_vista_inicial_post_bienvenida,
        )
        btn_empezar.pack()

    def _ir_vista_inicial_post_bienvenida(self):
        if "pos" in self.frames_contenido:
            self.cambiar_vista("pos")
        elif "productos" in self.frames_contenido:
            self.cambiar_vista("productos")
        elif "clientes" in self.frames_contenido:
            self.cambiar_vista("clientes")
        elif "empleados" in self.frames_contenido:
            self.cambiar_vista("empleados")
        elif "contabilidad" in self.frames_contenido:
            self.cambiar_vista("contabilidad")

    
    # CONTROL DE NAVEGACIÓN ENTRE VISTAS
    
    def cambiar_vista(self, vista):
        if vista not in self.frames_contenido:
            return

        for frame in self.frames_contenido.values():
            frame.grid_remove()

        frame = self.frames_contenido[vista]
        frame.grid()

        titulos = {
            "pos": "Punto de Venta y Facturación (POS)",
            "productos": "Gestión de Productos e Inventario",
            "clientes": "Gestión de Clientes",
            "empleados": "Administración de Personal",
            "contabilidad": "Módulo de Contabilidad General",
        }
        if hasattr(self, "lbl_topbar_title"):
            self.lbl_topbar_title.config(
                text=titulos.get(vista, "Sistema de Inventario PMV")
            )

        for nombre, btn in self.nav_buttons.items():
            if nombre == vista:
                btn.configure(style="PMV.SidebarSelected.TButton")
            else:
                btn.configure(style="PMV.Sidebar.TButton")

  
    # REFRESCAR PRODUCTOS
  
    def refrescar_productos(self):
        print(">>> ENTRÓ A REFRESCAR PRODUCTOS MAINWINDOW")

        frame = self.frames_contenido.get("productos")

        print("ID FRAME MAIN:", id(frame))

        if frame:
            try:
                frame.limpiar_busqueda()
                frame.update_idletasks()

                print("REFRESCO FORZADO")
            except Exception as e:
                print("Error refrescando productos:", e)

   
    # RELOJ EN TIEMPO REAL
 
    def _actualizar_reloj(self):
        ahora = datetime.now().strftime("📅 %d/%m/%Y  •  🕒 %H:%M:%S")
        self.lbl_clock.config(text=ahora)
        self.after(1000, self._actualizar_reloj)

    
    # CERRAR SESIÓN
    
    def _cerrar_sesion(self):
        self.destroy()