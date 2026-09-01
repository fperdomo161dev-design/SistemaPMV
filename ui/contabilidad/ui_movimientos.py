from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk


try:
  from tkcalendar import DateEntry

  USAR_TKCALENDAR = True
except ImportError:
  USAR_TKCALENDAR = False

COLOR_BG = "#0B111E"
COLOR_CARD = "#111827"
COLOR_TEXT = "#E5E7EB"
COLOR_ACCENT = "#F59E0B"
COLOR_BTN_ROJO = "#DC2626"  # Rojo para el botón buscar
COLOR_BTN_ROJO_HOVER = "#B91C1C"


class VentanaMovimientos(tk.Toplevel):

  def __init__(self, parent, service_contabilidad=None):
    super().__init__(parent)
    self.title("Historial de Movimientos")
    self.geometry("950x660")  # Ampliamos un poco la altura para los filtros
    self.configure(bg=COLOR_BG)
    self.transient(parent)
    self.grab_set()

    self.service = service_contabilidad

    # Título
    lbl_titulo = tk.Label(
        self,
        text="📁 Historial Unificado de Movimientos",
        bg=COLOR_BG,
        fg=COLOR_ACCENT,
        font=("Segoe UI", 14, "bold"),
    )
    lbl_titulo.pack(anchor="w", padx=20, pady=(15, 5))

   
    # PANEL DE FILTROS POR FECHA
   
    frame_filtros = tk.Frame(self, bg=COLOR_CARD, bd=1, relief="solid")
    frame_filtros.pack(fill="x", padx=20, pady=5)

    tk.Label(
        frame_filtros,
        text="📅 Filtrar por Rango de Fechas:",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 9, "bold"),
    ).pack(side="left", padx=15, pady=10)

    tk.Label(
        frame_filtros, text="Desde:", bg=COLOR_CARD, fg="#9CA3AF"
    ).pack(side="left", padx=(10, 2))

    if USAR_TKCALENDAR:
      self.cal_desde = DateEntry(
          frame_filtros,
          width=12,
          background="darkblue",
          foreground="white",
          borderwidth=2,
          date_pattern="yyyy-mm-dd",
      )
    else:
      
      self.cal_desde = tk.Entry(frame_filtros, width=12)
    self.cal_desde.pack(side="left", padx=5)

    tk.Label(
        frame_filtros, text="Hasta:", bg=COLOR_CARD, fg="#9CA3AF"
    ).pack(side="left", padx=(15, 2))

    if USAR_TKCALENDAR:
      self.cal_hasta = DateEntry(
          frame_filtros,
          width=12,
          background="darkblue",
          foreground="white",
          borderwidth=2,
          date_pattern="yyyy-mm-dd",
      )
    else:
      self.cal_hasta = tk.Entry(frame_filtros, width=12)
    self.cal_hasta.pack(side="left", padx=5)

    # Botón Buscar en Rojo
    btn_buscar = tk.Button(
        frame_filtros,
        text="🔍 Buscar",
        bg=COLOR_BTN_ROJO,
        fg="white",
        activebackground=COLOR_BTN_ROJO_HOVER,
        activeforeground="white",
        font=("Segoe UI", 9, "bold"),
        bd=0,
        padx=12,
        pady=4,
        cursor="hand2",
        command=self.filtrar_por_fechas,
    )
    btn_buscar.pack(side="left", padx=15)

    # Botón Restablecer
    btn_reset = tk.Button(
        frame_filtros,
        text="🔄 Ver Todos",
        bg="#374151",
        fg="white",
        font=("Segoe UI", 9),
        bd=0,
        padx=10,
        pady=4,
        cursor="hand2",
        command=self.cargar_datos,
    )
    btn_reset.pack(side="left", padx=5)

   
    # TABLA
   
    frame_tabla = tk.Frame(self, bg=COLOR_CARD)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Movimientos.Treeview",
        background="#1F2937",
        foreground=COLOR_TEXT,
        fieldbackground="#1F2937",
        rowheight=26,
        bordercolor="#374151",
        borderwidth=1,
    )
    style.configure(
        "Movimientos.Treeview.Heading",
        background="#111827",
        foreground="#9CA3AF",
        font=("Segoe UI", 9, "bold"),
    )
    style.map("Movimientos.Treeview", background=[("selected", "#374151")])

    cols = ("Fecha", "Tipo", "Concepto", "Monto", "Usuario")
    self.tree = ttk.Treeview(
        frame_tabla, columns=cols, show="headings", style="Movimientos.Treeview"
    )

    self.tree.heading("Fecha", text="Fecha / Hora")
    self.tree.heading("Tipo", text="Tipo")
    self.tree.heading("Concepto", text="Concepto / Descripción")
    self.tree.heading("Monto", text="Monto ($)")
    self.tree.heading("Usuario", text="Registrado Por")

    self.tree.column("Fecha", width=140, anchor="center")
    self.tree.column("Tipo", width=110, anchor="center")
    self.tree.column("Concepto", width=320, anchor="w")
    self.tree.column("Monto", width=120, anchor="e")
    self.tree.column("Usuario", width=120, anchor="center")

    scrollbar = ttk.Scrollbar(
        frame_tabla, orient="vertical", command=self.tree.yview
    )
    self.tree.configure(yscrollcommand=scrollbar.set)

    self.tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    self.cargar_datos()

  def cargar_datos(self):
    """Carga todos los movimientos sin filtros."""
    for item in self.tree.get_children():
      self.tree.delete(item)

    if self.service and hasattr(self.service, "obtener_todos_movimientos"):
      movs = self.service.obtener_todos_movimientos()
      self._poblar_tabla(movs)

  def filtrar_por_fechas(self):
    """Filtra los movimientos según el rango de fechas seleccionado."""
    for item in self.tree.get_children():
      self.tree.delete(item)

    if not self.service or not hasattr(self.service, "obtener_todos_movimientos"):
      return

    try:
    
      fecha_ini_str = (
          self.cal_desde.get()
          if USAR_TKCALENDAR
          else self.cal_desde.get().strip()
      )
      fecha_fin_str = (
          self.cal_hasta.get()
          if USAR_TKCALENDAR
          else self.cal_hasta.get().strip()
      )

      
      dt_inicio = datetime.strptime(fecha_ini_str, "%Y-%m-%d").date()
      dt_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()

      if dt_inicio > dt_fin:
        messagebox.showerror(
            "Error de Fechas",
            "La fecha inicial no puede ser mayor que la fecha final.",
        )
        self.cargar_datos()
        return

      movs = self.service.obtener_todos_movimientos()
      movs_filtrados = []

      for m in movs:
        f_str = str(m.get("fecha", ""))
       
        f_solo_fecha = f_str.split(" ")[0]

        try:
          dt_mov = datetime.strptime(f_solo_fecha, "%Y-%m-%d").date()
          if dt_inicio <= dt_mov <= dt_fin:
            movs_filtrados.append(m)
        except ValueError:
          continue  

      self._poblar_tabla(movs_filtrados)

    except Exception as e:
      messagebox.showerror(
          "Error", f"Formato de fecha inválido o error en el filtro: {e}"
      )
      self.cargar_datos()

  def _poblar_tabla(self, movimientos):
    """Inserta una lista de movimientos en el Treeview."""
    for m in movimientos:
      monto = float(m.get("monto", 0))
      tipo = str(m.get("tipo", "")).upper()
      self.tree.insert(
          "",
          "end",
          values=(
              m.get("fecha", ""),
              tipo,
              m.get("concepto", ""),
              f"${monto:,.2f}",
              m.get("usuario", "Admin"),
          ),
      )