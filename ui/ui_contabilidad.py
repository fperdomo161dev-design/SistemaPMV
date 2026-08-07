# views/ui_contabilidad.py

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

# ==========================================
# PALETA DE COLORES UI DARK EXECUTIVE
# ==========================================
COLOR_BG = "#0B111E"
COLOR_CARD = "#111827"
COLOR_INPUT_BG = "#1F2937"
COLOR_TEXT = "#E5E7EB"
COLOR_ACCENT = "#F59E0B"
COLOR_MUTED = "#9CA3AF"


class ContabilidadFrame(ttk.Frame):

  def __init__(self, master, usuario_actual=None, *args, **kwargs):
    super().__init__(master, *args, **kwargs)
    self.usuario_actual = usuario_actual

    # Validar exclusividad de Administrador
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
        font=("Segoe UI", 12, "bold"),
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

    # Título del Módulo
    ttk.Label(
        outer, text="📊 Módulo de Contabilidad General", style="Dark.TLabel"
    ).grid(row=0, column=0, sticky="w", pady=(0, 20))

    # Contenedor de los 4 Cuadros Seleccionables (Grid de 2x2)
    grid_cuadros = ttk.Frame(outer, style="Dark.TFrame")
    grid_cuadros.grid(row=1, column=0, sticky="nsew")

    grid_cuadros.columnconfigure(0, weight=1)
    grid_cuadros.columnconfigure(1, weight=1)
    grid_cuadros.rowconfigure(0, weight=1)
    grid_cuadros.rowconfigure(1, weight=1)

    # Creación de las 4 tarjetas interactivas
    self._crear_cuadro_seleccionable(
        grid_cuadros,
        "📁 Movimientos",
        (
            "Visualiza el historial completo de todas las transacciones"
            " registradas en caja."
        ),
        0,
        0,
        self.abrir_movimientos,
    )
    self._crear_cuadro_seleccionable(
        grid_cuadros,
        "📈 Ingresos",
        (
            "Gestiona y registra las entradas de dinero y ventas de la"
            " zapatería."
        ),
        0,
        1,
        self.abrir_ingresos,
    )
    self._crear_cuadro_seleccionable(
        grid_cuadros,
        "📉 Egresos",
        (
            "Controla las salidas generales de dinero, pagos y gastos"
            " operativos."
        ),
        1,
        0,
        self.abrir_egresos,
    )
    self._crear_cuadro_seleccionable(
        grid_cuadros,
        "💡 Servicios Públicos",
        (
            "Administra el control y pagos mensuales de agua, luz, gas e"
            " internet."
        ),
        1,
        1,
        self.abrir_servicios,
    )

  def _crear_cuadro_seleccionable(
      self, parent, titulo, descripcion, row, col, comando
  ):
    cuadro = tk.Frame(
        parent, bg=COLOR_CARD, bd=1, relief="solid", highlightbackground="#374151"
    )
    cuadro.grid(
        row=row, column=col, sticky="nsew", padx=15, pady=15, ipadx=10, ipady=10
    )

    cuadro.columnconfigure(0, weight=1)
    cuadro.rowconfigure(2, weight=1)

    lbl_titulo = tk.Label(
        cuadro,
        text=titulo,
        bg=COLOR_CARD,
        fg=COLOR_ACCENT,
        font=("Segoe UI", 14, "bold"),
        anchor="w",
    )
    lbl_titulo.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 5))

    lbl_desc = tk.Label(
        cuadro,
        text=descripcion,
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 10),
        anchor="w",
        justify="left",
        wraplength=320,
    )
    lbl_desc.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

    for widget in (cuadro, lbl_titulo, lbl_desc):
      widget.bind("<Enter>", lambda e, c=cuadro: c.config(bg="#1E293B"))
      widget.bind("<Leave>", lambda e, c=cuadro: c.config(bg=COLOR_CARD))
      widget.bind("<Button-1>", lambda e, cmd=comando: cmd())


  # ACCIONES DE LOS CUADROS

  def abrir_movimientos(self):
    messagebox.showinfo(
        "Movimientos", "Abriendo vista general de transacciones contables..."
    )

  def abrir_ingresos(self):
    messagebox.showinfo(
        "Ingresos", "Abriendo sección de entradas e ingresos..."
    )

  def abrir_egresos(self):
    messagebox.showinfo("Egresos", "Abriendo sección de salidas y gastos...")

  def abrir_servicios(self):
    messagebox.showinfo(
        "Servicios Públicos", "Abriendo gestión de servicios públicos..."
    )