from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

# Intentamos importar DateEntry de tkcalendar para los calendarios desplegables
try:
  from tkcalendar import DateEntry

  USAR_TKCALENDAR = True
except ImportError:
  USAR_TKCALENDAR = False

COLOR_BG = "#0B111E"
COLOR_CARD = "#111827"
COLOR_TEXT = "#E5E7EB"
COLOR_BTN_ROJO = "#DC2626"  
COLOR_BTN_ROJO_HOVER = "#B91C1C"


class VentanaEgresos(tk.Toplevel):

  def __init__(self, parent, service_contabilidad=None):
    super().__init__(parent)
    self.title("Gestión de Egresos")
    self.geometry("950x660")  
    self.configure(bg=COLOR_BG)
    self.transient(parent)
    self.grab_set()

    self.service = service_contabilidad
    self._build_ui()
    self.cargar_historial_egresos()

  def _build_ui(self):
    # Título de la ventana
    tk.Label(
        self,
        text="📉 Control de Gastos Operativos y Egresos",
        bg=COLOR_BG,
        fg="#EF4444",
        font=("Segoe UI", 14, "bold"),
    ).pack(anchor="w", padx=20, pady=(15, 5))

    # Formulario de registro rápido
    frame_form = tk.Frame(self, bg=COLOR_CARD, padx=15, pady=15)
    frame_form.pack(fill="x", padx=20, pady=10)

    tk.Label(
        frame_form, text="Descripción del Gasto:", bg=COLOR_CARD, fg=COLOR_TEXT
    ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    self.txt_concepto = tk.Entry(
        frame_form,
        bg="#1F2937",
        fg=COLOR_TEXT,
        insertbackground="white",
        relief="flat",
    )
    self.txt_concepto.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(
        frame_form, text="Monto ($):", bg=COLOR_CARD, fg=COLOR_TEXT
    ).grid(row=0, column=2, padx=5, pady=5, sticky="w")
    self.txt_monto = tk.Entry(
        frame_form,
        bg="#1F2937",
        fg=COLOR_TEXT,
        insertbackground="white",
        relief="flat",
    )
    self.txt_monto.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    frame_form.columnconfigure(1, weight=1)
    frame_form.columnconfigure(3, weight=1)

    btn_guardar = tk.Button(
        frame_form,
        text="Registrar Egreso",
        bg="#EF4444",
        fg="#FFF",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2",
        command=self.guardar_egreso,
    )
    btn_guardar.grid(row=0, column=4, padx=(15, 0), pady=5)

    
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
        command=self.cargar_historial_egresos,
    )
    btn_ver_todo.pack(side="left", padx=5)

    # Frame para la tabla de historial
    frame_tabla = tk.Frame(self, bg=COLOR_CARD)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

    # Configuración del estilo del Treeview para modo oscuro
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Egresos.Treeview",
        background="#1F2937",
        foreground=COLOR_TEXT,
        fieldbackground="#1F2937",
        rowheight=25,
        bordercolor="#374151",
        borderwidth=1,
    )
    style.configure(
        "Egresos.Treeview.Heading",
        background="#111827",
        foreground="#9CA3AF",
        font=("Segoe UI", 9, "bold"),
    )
    style.map("Egresos.Treeview", background=[("selected", "#374151")])

    # Creación de la tabla
    columnas = ("fecha", "tipo", "concepto", "monto", "usuario")
    self.tabla = ttk.Treeview(
        frame_tabla,
        columns=columnas,
        show="headings",
        style="Egresos.Treeview",
    )

    self.tabla.heading("fecha", text="Fecha")
    self.tabla.heading("tipo", text="Tipo / Categoria")
    self.tabla.heading("concepto", text="Concepto / Descripción")
    self.tabla.heading("monto", text="Monto ($)")
    self.tabla.heading("usuario", text="Registrado Por")

    self.tabla.column("fecha", width=140, anchor="center")
    self.tabla.column("tipo", width=130, anchor="center")
    self.tabla.column("concepto", width=300, anchor="w")
    self.tabla.column("monto", width=110, anchor="e")
    self.tabla.column("usuario", width=110, anchor="center")

    scrollbar = ttk.Scrollbar(
        frame_tabla, orient="vertical", command=self.tabla.yview
    )
    self.tabla.configure(yscrollcommand=scrollbar.set)

    self.tabla.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

  def cargar_historial_egresos(self):
    """Carga y muestra todas las transacciones de egreso en el Treeview."""
    for item in self.tabla.get_children():
      self.tabla.delete(item)

    if not self.service or not hasattr(
        self.service, "obtener_todos_movimientos"
    ):
      return

    movimientos = self.service.obtener_todos_movimientos()
    self._poblar_tabla(movimientos)

  def filtrar_por_fechas(self):
    """Filtra los egresos según el rango de fechas seleccionado."""
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
        self.cargar_historial_egresos()
        return

      movimientos = self.service.obtener_todos_movimientos()
      movs_filtrados = []

      for m in movimientos:
        tipo = str(m.get("tipo", "")).upper()
        if tipo in ["EGRESO", "SERVICIO", "PROVEEDOR"]:
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
      self.cargar_historial_egresos()

  def _poblar_tabla(self, movimientos):
    """Inserta los movimientos de egresos filtrados en el Treeview."""
    for m in movimientos:
      tipo = str(m.get("tipo", "")).upper()
      if tipo in ["EGRESO", "SERVICIO", "PROVEEDOR"]:
        monto = float(m.get("monto", 0.0))
        self.tabla.insert(
            "",
            "end",
            values=(
                m.get("fecha", ""),
                tipo,
                m.get("concepto", ""),
                f"$ {monto:,.0f}",
                m.get("usuario", "Admin"),
            ),
        )

  def guardar_egreso(self):
    concepto = self.txt_concepto.get().strip()
    monto_raw = self.txt_monto.get().strip()

    if not concepto or not monto_raw:
      messagebox.showwarning(
          "Advertencia", "Por favor complete la descripción y el monto."
      )
      return

    try:
      monto = float(monto_raw)
      if monto <= 0:
        raise ValueError
    except ValueError:
      messagebox.showerror(
          "Error", "Ingrese un valor numérico válido mayor a cero."
      )
      return

    if self.service and hasattr(self.service, "registrar_movimiento"):
      exito = self.service.registrar_movimiento(
          tipo="egreso", concepto=concepto, monto=monto
      )
      if exito:
        messagebox.showinfo("Éxito", "Egreso registrado correctamente")
        self.txt_concepto.delete(0, tk.END)
        self.txt_monto.delete(0, tk.END)
        self.cargar_historial_egresos()
      else:
        messagebox.showerror(
            "Error", "No se pudo registrar el egreso en la base de datos."
        )