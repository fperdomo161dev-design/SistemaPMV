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
COLOR_ACCENT = "#34D399"  # Verde para ingresos
COLOR_BTN_ROJO = "#DC2626"
COLOR_BTN_ROJO_HOVER = "#B91C1C"


class VentanaIngresos(tk.Toplevel):

  def __init__(self, parent, service_contabilidad=None):
    super().__init__(parent)
    self.title("Gestión de Ingresos y Entradas de Caja")
    self.geometry("1000x650")
    self.configure(bg=COLOR_BG)
    self.transient(parent)
    self.grab_set()

    self.service = service_contabilidad
    self._build_ui()
    self.cargar_historial_ingresos()

  def _build_ui(self):
    # Cabecera superior
    frame_header = tk.Frame(self, bg=COLOR_BG)
    frame_header.pack(fill="x", padx=20, pady=(15, 5))

    tk.Label(
        frame_header,
        text="💰 Control de Ingresos",
        bg=COLOR_BG,
        fg=COLOR_ACCENT,
        font=("Segoe UI", 14, "bold"),
    ).pack(side="left")

    btn_nuevo = tk.Button(
        frame_header,
        text="+ Registrar Nuevo Ingreso",
        bg="#059669",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2",
        command=self.abrir_registrar_ingreso,
    )
    btn_nuevo.pack(side="right")


    # PANEL DE FILTROS POR FECHA
   
    frame_filtros = tk.Frame(self, bg=COLOR_CARD, bd=1, relief="solid")
    frame_filtros.pack(fill="x", padx=20, pady=5)

    tk.Label(
        frame_filtros,
        text="📅 Rango de Fechas:",
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

    # Botón Buscar 
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

    # Botón Ver Todo
    btn_ver_todo = tk.Button(
        frame_filtros,
        text="🔄 Ver Todo",
        bg="#374151",
        fg="white",
        font=("Segoe UI", 9),
        bd=0,
        padx=10,
        pady=4,
        cursor="hand2",
        command=self.cargar_historial_ingresos,
    )
    btn_ver_todo.pack(side="left", padx=5)

    # Etiqueta de Total Ingresado
    self.lbl_total = tk.Label(
        self,
        text="Total Ingresado en Vista: $0.00",
        bg=COLOR_BG,
        fg=COLOR_ACCENT,
        font=("Segoe UI", 11, "bold"),
    )
    self.lbl_total.pack(anchor="e", padx=20, pady=5)

    # Frame para la tabla de historial
    frame_tabla = tk.Frame(self, bg=COLOR_CARD)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

    # Estilo del Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Ingresos.Treeview",
        background="#1F2937",
        foreground=COLOR_TEXT,
        fieldbackground="#1F2937",
        rowheight=26,
        bordercolor="#374151",
        borderwidth=1,
    )
    style.configure(
        "Ingresos.Treeview.Heading",
        background="#111827",
        foreground="#9CA3AF",
        font=("Segoe UI", 9, "bold"),
    )
    style.map("Ingresos.Treeview", background=[("selected", "#374151")])

    columnas = ("fecha", "concepto", "categoria", "metodo", "cliente", "monto")
    self.tabla = ttk.Treeview(
        frame_tabla,
        columns=columnas,
        show="headings",
        style="Ingresos.Treeview",
    )

    self.tabla.heading("fecha", text="Fecha/Hora")
    self.tabla.heading("concepto", text="Concepto")
    self.tabla.heading("categoria", text="Categoría")
    self.tabla.heading("metodo", text="Método")
    self.tabla.heading("cliente", text="Cliente")
    self.tabla.heading("monto", text="Monto")

    self.tabla.column("fecha", width=140, anchor="center")
    self.tabla.column("concepto", width=220, anchor="w")
    self.tabla.column("categoria", width=130, anchor="center")
    self.tabla.column("metodo", width=110, anchor="center")
    self.tabla.column("cliente", width=130, anchor="center")
    self.tabla.column("monto", width=110, anchor="e")

    scrollbar = ttk.Scrollbar(
        frame_tabla, orient="vertical", command=self.tabla.yview
    )
    self.tabla.configure(yscrollcommand=scrollbar.set)

    self.tabla.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

  def cargar_historial_ingresos(self):
    for item in self.tabla.get_children():
      self.tabla.delete(item)

    if not self.service or not hasattr(
        self.service, "obtener_todos_movimientos"
    ):
      return

    movimientos = self.service.obtener_todos_movimientos()
    ingresos = [
        m for m in movimientos if str(m.get("tipo", "")).upper() == "INGRESO"
    ]
    self._poblar_tabla(ingresos)

  def filtrar_por_fechas(self):
    for item in self.tabla.get_children():
      self.tabla.delete(item)

    if not self.service or not hasattr(
        self.service, "obtener_todos_movimientos"
    ):
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
        self.cargar_historial_ingresos()
        return

      movimientos = self.service.obtener_todos_movimientos()
      ingresos_filtrados = []

      for m in movimientos:
        if str(m.get("tipo", "")).upper() == "INGRESO":
          f_str = str(m.get("fecha", ""))
          f_solo_fecha = f_str.split(" ")[0]
          try:
            dt_mov = datetime.strptime(f_solo_fecha, "%Y-%m-%d").date()
            if dt_inicio <= dt_mov <= dt_fin:
              ingresos_filtrados.append(m)
          except ValueError:
            continue

      self._poblar_tabla(ingresos_filtrados)

    except Exception as e:
      messagebox.showerror(
          "Error", f"Formato de fecha inválido o error en el filtro: {e}"
      )
      self.cargar_historial_ingresos()

  def _poblar_tabla(self, ingresos):
    total = 0.0
    for m in ingresos:
      monto = float(m.get("monto", 0.0))
      total += monto
      self.tabla.insert(
          "",
          "end",
          values=(
              m.get("fecha", ""),
              m.get("concepto", ""),
              m.get("categoria", "Cierre de Caja"),
              m.get("metodo", "None"),
              m.get("cliente", "N/A"),
              f"${monto:,.2f}",
          ),
      )
    self.lbl_total.config(text=f"Total Ingresado en Vista: ${total:,.2f}")

  def abrir_registrar_ingreso(self):
    
    pass