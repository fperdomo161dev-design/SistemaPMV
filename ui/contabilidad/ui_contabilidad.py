import tkinter as tk
from tkinter import messagebox, ttk

# Importaciones de las subvistas dentro del módulo contable
try:
    from ui.contabilidad.ui_movimientos import VentanaMovimientos
except ImportError:
    VentanaMovimientos = None

try:
    from ui.contabilidad.ui_ingresos import VentanaIngresos
except ImportError:
    VentanaIngresos = None

try:
    from ui.contabilidad.ui_egresos import VentanaEgresos
except ImportError:
    VentanaEgresos = None

try:
    from ui.contabilidad.ui_servicios import (
        VentanaServicios,
        VentanaServiciosPublicos,
    )
except ImportError:
    VentanaServiciosPublicos = None
    VentanaServicios = None

try:
    from ui.contabilidad.ui_proveedores import VentanaProveedores
except ImportError:
    VentanaProveedores = None

try:
    from ui.contabilidad.ui_nominas import VentanaNominas
except ImportError:
    VentanaNominas = None

try:
    from ui.contabilidad.ui_dashboard import VentanaDashboard
except ImportError:
    VentanaDashboard = None

try:
    from services.contabilidad_service import ContabilidadService
except ImportError:
    ContabilidadService = None

COLOR_BG = "#0B111E"
COLOR_CARD = "#111827"
COLOR_TEXT = "#E5E7EB"
COLOR_ACCENT = "#F59E0B"


class ContabilidadFrame(ttk.Frame):

    def __init__(self, master, usuario_actual=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.usuario_actual = usuario_actual
        self.service_contabilidad = (
            ContabilidadService() if ContabilidadService else None
        )

        self.es_admin = True  # O tu validación habitual de roles
        if self.usuario_actual:
            rol = getattr(self.usuario_actual, "cargo", "") or getattr(
                self.usuario_actual, "rol", ""
            )
            self.es_admin = str(rol).strip().lower() in [
                "administrador",
                "admin",
                "gerente",
            ]

        self._configurar_estilos()

        if not self.es_admin:
            self._mostrar_acceso_denegado()
        else:
            self._build_ui()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("Dark.TFrame", background=COLOR_BG)
        style.configure(
            "Dark.TLabel",
            background=COLOR_BG,
            foreground=COLOR_TEXT,
            font=("Segoe UI", 14, "bold"),
        )

    def _mostrar_acceso_denegado(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        frame_denegado = ttk.Frame(self, style="Dark.TFrame")
        frame_denegado.grid(row=0, column=0, sticky="nsew")

        lbl = tk.Label(
            frame_denegado,
            text=(
                "⚠️ ACCESO DENEGADO\n\nEste módulo contable es exclusivo para"
                " administradores."
            ),
            bg=COLOR_BG,
            fg="#EF4444",
            font=("Segoe UI", 14, "bold"),
            justify="center",
        )
        lbl.pack(expand=True)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        outer = ttk.Frame(self, style="Dark.TFrame")
        outer.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        ttk.Label(
            outer, text="📊 Módulo de Contabilidad General", style="Dark.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 15))

        grid_cuadros = ttk.Frame(outer, style="Dark.TFrame")
        grid_cuadros.grid(row=1, column=0, sticky="nsew")

        # Configuración de 3 columnas de igual ancho
        grid_cuadros.columnconfigure(0, weight=1)
        grid_cuadros.columnconfigure(1, weight=1)
        grid_cuadros.columnconfigure(2, weight=1)

        # Configuración de 3 filas
        grid_cuadros.rowconfigure(0, weight=1)
        grid_cuadros.rowconfigure(1, weight=1)
        grid_cuadros.rowconfigure(2, weight=1)

        # FILA 0: Operaciones de Caja Básicas
        self._crear_cuadro_seleccionable(
            grid_cuadros,
            "📁 Movimientos",
            "Visualiza el historial completo de todas las transacciones"
            " registradas.",
            0,
            0,
            self.abrir_movimientos,
            color_acento="#38BDF8", 
            color_borde="#0284C7",
        )
        self._crear_cuadro_seleccionable(
            grid_cuadros,
            "📈 Ingresos",
            "Gestiona y registra las entradas de dinero y ventas de la"
            " zapatería.",
            0,
            1,
            self.abrir_ingresos,
            color_acento="#34D399",  
            color_borde="#059669",
        )
        self._crear_cuadro_seleccionable(
            grid_cuadros,
            "📉 Egresos",
            "Controla las salidas generales de dinero, pagos y gastos"
            " operativos.",
            0,
            2,
            self.abrir_egresos,
            color_acento="#F87171",  
            color_borde="#DC2626",
        )

        # FILA 1: Gastos Fijos y Obligaciones
        self._crear_cuadro_seleccionable(
            grid_cuadros,
            "💡 Servicios Públicos",
            "Administra el pago mensual de luz, agua, gas e internet.",
            1,
            0,
            self.abrir_servicios,
            color_acento="#FBBF24", 
            color_borde="#D97706",
        )
        self._crear_cuadro_seleccionable(
            grid_cuadros,
            "🚚 Pago Proveedores",
            "Gestiona facturas pendientes y abonos a proveedores registrados.",
            1,
            1,
            self.abrir_proveedores,
            color_acento="#A78BFA", 
            color_borde="#7C3AED",
        )
        self._crear_cuadro_seleccionable(
            grid_cuadros,
            "👥 Pago de Nómina",
            "Procesa y liquida sueldos de empleados con deducciones de ley.",
            1,
            2,
            self.abrir_nominas,
            color_acento="#FB923C", 
            color_borde="#EA580C",
        )

        # FILA 2: Reportes y Métricas Consolidadas
        self._crear_cuadro_seleccionable(
            grid_cuadros,
            "📊 Dashboard & Balances",
            "Consolidado general de caja, balance neto y gráficos comparativos.",
            2,
            0,
            self.abrir_dashboard,
            color_acento="#EC4899",  
            color_borde="#DB2777",
        )

    def _crear_cuadro_seleccionable(
        self,
        parent,
        titulo,
        descripcion,
        row,
        col,
        comando,
        color_acento="#F59E0B",
        color_borde="#374151",
    ):
        cuadro = tk.Frame(
            parent,
            bg=COLOR_CARD,
            bd=1,
            relief="solid",
            highlightbackground=color_borde,
        )
        cuadro.grid(
            row=row, column=col, sticky="nsew", padx=8, pady=8, ipadx=10, ipady=10
        )

       
        cuadro.columnconfigure(0, weight=1)
        cuadro.rowconfigure(0, weight=1)
        cuadro.rowconfigure(1, weight=1)

      
        lbl_titulo = tk.Label(
            cuadro,
            text=titulo,
            bg=COLOR_CARD,
            fg=color_acento,
            font=("Segoe UI", 15, "bold"),
            anchor="center",
            justify="center",
        )
        lbl_titulo.grid(
            row=0, column=0, sticky="nsew", padx=12, pady=(15, 4)
        )  # Usamos sticky="nsew" para centrado perfecto

       
        lbl_desc = tk.Label(
            cuadro,
            text=descripcion,
            bg=COLOR_CARD,
            fg=COLOR_TEXT,
            font=("Segoe UI", 11),
            anchor="center",
            justify="center",
            wraplength=260,
        )
        lbl_desc.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 15))

       
        def on_enter(e):
            cuadro.config(bg="#1E293B")
            lbl_titulo.config(bg="#1E293B")
            lbl_desc.config(bg="#1E293B")

        def on_leave(e):
            cuadro.config(bg=COLOR_CARD)
            lbl_titulo.config(bg=COLOR_CARD)
            lbl_desc.config(bg=COLOR_CARD)

        for widget in (cuadro, lbl_titulo, lbl_desc):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e, cmd=comando: cmd())

    # Métodos que invocan a cada módulo
    def abrir_movimientos(self):
        if VentanaMovimientos:
            VentanaMovimientos(self, self.service_contabilidad)
        else:
            messagebox.showerror("Error", "Vista de Movimientos no disponible.")

    def abrir_ingresos(self):
        if VentanaIngresos:
            VentanaIngresos(self, self.service_contabilidad)
        else:
            messagebox.showerror("Error", "Vista de Ingresos no disponible.")

    def abrir_egresos(self):
        if VentanaEgresos:
            VentanaEgresos(self, self.service_contabilidad)
        else:
            messagebox.showerror("Error", "Vista de Egresos no disponible.")

    def abrir_servicios(self):
        clase_v = VentanaServiciosPublicos or VentanaServicios
        if clase_v:
            clase_v(self, self.service_contabilidad)
        else:
            messagebox.showerror(
                "Error", "Vista de Servicios Públicos no disponible."
            )

    def abrir_proveedores(self):
        if VentanaProveedores:
            VentanaProveedores(self, self.service_contabilidad)
        else:
            messagebox.showerror("Error", "Vista de Proveedores no disponible.")

    def abrir_nominas(self):
        if VentanaNominas:
            VentanaNominas(self, self.service_contabilidad)
        else:
            messagebox.showinfo(
                "Información",
                "Crea la vista 'ui/contabilidad/ui_nominas.py' para abrir este"
                " módulo.",
            )

    def abrir_dashboard(self):
        if VentanaDashboard:
            VentanaDashboard(self, self.service_contabilidad)
        else:
            messagebox.showinfo(
                "Información",
                "Crea la vista 'ui/contabilidad/ui_dashboard.py' para abrir este"
                " módulo.",
            )