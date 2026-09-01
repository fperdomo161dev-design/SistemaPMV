from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk


try:
  from tkcalendar import DateEntry

  HAS_TKCALENDAR = True
except ImportError:
  HAS_TKCALENDAR = False

try:
  from services.servicio_publico_service import ServicioPublicoService
except ImportError:
  ServicioPublicoService = None

try:
  from models.servicio_publico import ServicioPublico
except ImportError:
  ServicioPublico = None

COLOR_BG = "#0B111E"
COLOR_CARD = "#111827"
COLOR_TEXT = "#E5E7EB"
COLOR_BTN_ROJO = "#DC2626"
COLOR_BTN_ROJO_HOVER = "#B91C1C"


class VentanaServiciosPublicos(tk.Toplevel):

  def __init__(self, parent, service_contabilidad=None):
    super().__init__(parent)
    self.title("Gestión de Servicios Públicos")
    self.geometry("980x620")
    self.configure(bg=COLOR_BG)
    self.transient(parent)
    self.grab_set()

    self.service = ServicioPublicoService() if ServicioPublicoService else None

    self._build_ui()
    self.cargar_servicios()

  def _build_ui(self):
    # Header
    frame_header = tk.Frame(self, bg=COLOR_BG)
    frame_header.pack(fill="x", padx=15, pady=(10, 5))

    tk.Label(
        frame_header,
        text="💡 Registro de Servicios Públicos",
        bg=COLOR_BG,
        fg=COLOR_TEXT,
        font=("Segoe UI", 14, "bold"),
    ).pack(side="left")

    # Formulario de Nuevo Registro
    frame_form = tk.LabelFrame(
        self,
        text=" Nuevo Registro ",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 10, "bold"),
        padx=10,
        pady=10,
    )
    frame_form.pack(fill="x", padx=15, pady=5)

    tk.Label(
        frame_form, text="Tipo Servicio:", bg=COLOR_CARD, fg=COLOR_TEXT
    ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    self.cb_tipo = ttk.Combobox(
        frame_form,
        values=["Luz", "Agua", "Gas", "Internet", "Teléfono", "Otro"],
        state="readonly",
        width=15,
    )
    self.cb_tipo.grid(row=0, column=1, padx=5, pady=5)
    if self.cb_tipo["values"]:
      self.cb_tipo.current(0)

    tk.Label(frame_form, text="Monto ($):", bg=COLOR_CARD, fg=COLOR_TEXT).grid(
        row=0, column=2, padx=5, pady=5, sticky="w"
    )
    self.txt_monto = ttk.Entry(frame_form, width=15)
    self.txt_monto.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(
        frame_form, text="Referencia / Nro:", bg=COLOR_CARD, fg=COLOR_TEXT
    ).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    self.txt_ref = ttk.Entry(frame_form, width=15)
    self.txt_ref.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(
        frame_form, text="Método Pago:", bg=COLOR_CARD, fg=COLOR_TEXT
    ).grid(row=1, column=2, padx=5, pady=5, sticky="w")
    self.cb_metodo = ttk.Combobox(
        frame_form,
        values=["Efectivo", "Transferencia", "Tarjeta"],
        state="readonly",
        width=15,
    )
    self.cb_metodo.grid(row=1, column=3, padx=5, pady=5)
    if self.cb_metodo["values"]:
      self.cb_metodo.current(0)

    btn_guardar = tk.Button(
        frame_form,
        text="💾 Registrar Pago",
        bg="#10B981",
        fg="#FFF",
        font=("Segoe UI", 9, "bold"),
        cursor="hand2",
        command=self.guardar_servicio,
    )
    btn_guardar.grid(
        row=0, column=4, rowspan=2, padx=15, pady=5, sticky="nsew"
    )

  
    # SECCIÓN DE FILTROS
    
    frame_filtros = tk.LabelFrame(
        self,
        text=" 🔍 Filtros por Rango de Fechas y Servicio ",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 10, "bold"),
        padx=10,
        pady=8,
    )
    frame_filtros.pack(fill="x", padx=15, pady=5)

    tk.Label(frame_filtros, text="Servicio:", bg=COLOR_CARD, fg=COLOR_TEXT).grid(
        row=0, column=0, padx=5, pady=2, sticky="w"
    )
    self.cb_filtro_tipo = ttk.Combobox(
        frame_filtros,
        values=["Todos", "Luz", "Agua", "Gas", "Internet", "Teléfono", "Otro"],
        state="readonly",
        width=12,
    )
    self.cb_filtro_tipo.grid(row=0, column=1, padx=5, pady=2)
    self.cb_filtro_tipo.current(0)

    # Campos de Fecha (Desde - Hasta) con soporte de Calendario
    tk.Label(
        frame_filtros, text="Desde:", bg=COLOR_CARD, fg="#9CA3AF"
    ).grid(row=0, column=2, padx=(10, 2), pady=2, sticky="w")
    if HAS_TKCALENDAR:
      self.cal_desde = DateEntry(
          frame_filtros,
          date_pattern="yyyy-mm-dd",
          width=11,
          background="#1F2937",
          foreground="white",
          headersbackground="#374151",
      )
      self.cal_desde.grid(row=0, column=3, padx=2, pady=2)
    else:
      self.cal_desde = ttk.Entry(frame_filtros, width=12)
      self.cal_desde.grid(row=0, column=3, padx=2, pady=2)
      self.cal_desde.insert(0, datetime.now().strftime("%Y-%m-01"))

    tk.Label(frame_filtros, text="Hasta:", bg=COLOR_CARD, fg="#9CA3AF").grid(
        row=0, column=4, padx=(10, 2), pady=2, sticky="w"
    )
    if HAS_TKCALENDAR:
      self.cal_hasta = DateEntry(
          frame_filtros,
          date_pattern="yyyy-mm-dd",
          width=11,
          background="#1F2937",
          foreground="white",
          headersbackground="#374151",
      )
      self.cal_hasta.grid(row=0, column=5, padx=2, pady=2)
    else:
      self.cal_hasta = ttk.Entry(frame_filtros, width=12)
      self.cal_hasta.grid(row=0, column=5, padx=2, pady=2)
      self.cal_hasta.insert(0, datetime.now().strftime("%Y-%m-%d"))

    # Botón Buscar en Rojo
    btn_filtrar = tk.Button(
        frame_filtros,
        text="🔍 Buscar",
        bg=COLOR_BTN_ROJO,
        fg="white",
        activebackground=COLOR_BTN_ROJO_HOVER,
        activeforeground="white",
        font=("Segoe UI", 9, "bold"),
        bd=0,
        padx=10,
        pady=4,
        cursor="hand2",
        command=self.aplicar_filtro,
    )
    btn_filtrar.grid(row=0, column=6, padx=(15, 5), pady=2)

    # Botón Ver Todo / Mostrar Todos
    btn_limpiar = tk.Button(
        frame_filtros,
        text="🔄 Ver Todo",
        bg="#374151",
        fg="white",
        font=("Segoe UI", 9),
        bd=0,
        padx=10,
        pady=4,
        cursor="hand2",
        command=self.limpiar_filtros,
    )
    btn_limpiar.grid(row=0, column=7, padx=5, pady=2)

    # Tabla de Registros
    frame_tabla = tk.Frame(self, bg=COLOR_BG)
    frame_tabla.pack(fill="both", expand=True, padx=15, pady=(5, 15))

   
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Servicios.Treeview",
        background="#1F2937",
        foreground=COLOR_TEXT,
        fieldbackground="#1F2937",
        rowheight=26,
        bordercolor="#374151",
        borderwidth=1,
    )
    style.configure(
        "Servicios.Treeview.Heading",
        background="#111827",
        foreground="#9CA3AF",
        font=("Segoe UI", 9, "bold"),
    )
    style.map("Servicios.Treeview", background=[("selected", "#374151")])

    columnas = ("id", "tipo", "monto", "ref", "metodo", "fecha", "hora")
    self.tabla = ttk.Treeview(
        frame_tabla,
        columns=columnas,
        show="headings",
        height=10,
        style="Servicios.Treeview",
    )

    self.tabla.heading("id", text="ID")
    self.tabla.heading("tipo", text="Servicio")
    self.tabla.heading("monto", text="Monto")
    self.tabla.heading("ref", text="Referencia")
    self.tabla.heading("metodo", text="Método Pago")
    self.tabla.heading("fecha", text="Fecha")
    self.tabla.heading("hora", text="Hora")

    self.tabla.column("id", width=0, stretch=False)
    self.tabla.column("tipo", width=120, anchor="center")
    self.tabla.column("monto", width=100, anchor="e")
    self.tabla.column("ref", width=150, anchor="center")
    self.tabla.column("metodo", width=120, anchor="center")
    self.tabla.column("fecha", width=110, anchor="center")
    self.tabla.column("hora", width=90, anchor="center")

    self.tabla.pack(fill="both", expand=True, side="left")

    scrollbar = ttk.Scrollbar(
        frame_tabla, orient="vertical", command=self.tabla.yview
    )
    self.tabla.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

  def guardar_servicio(self):
    if not self.service:
      messagebox.showerror("Error", "Servicio no disponible.")
      return

    try:
      monto = float(self.txt_monto.get().strip())
    except ValueError:
      messagebox.showwarning("Atención", "Ingrese un monto válido.")
      return

    tipo = self.cb_tipo.get()
    ref = self.txt_ref.get().strip()
    metodo = self.cb_metodo.get()
    ahora = datetime.now()

    if ServicioPublico:
      obj_servicio = ServicioPublico(
          tipo_servicio=tipo,
          monto=monto,
          referencia=ref,
          metodo_pago=metodo,
          fecha=ahora.strftime("%Y-%m-%d"),
          hora=ahora.strftime("%H:%M:%S"),
      )
      exito = self.service.registrar_pago_servicio(obj_servicio)
      if exito:
        messagebox.showinfo(
            "Éxito", "Pago de servicio registrado correctamente."
        )
        self.txt_monto.delete(0, tk.END)
        self.txt_ref.delete(0, tk.END)
        self.cargar_servicios()
      else:
        messagebox.showerror("Error", "No se pudo guardar el registro.")
    else:
      messagebox.showerror(
          "Error", "El modelo ServicioPublico no se encuentra cargado."
      )

  def cargar_servicios(
      self, servicio_filtro=None, fecha_inicio=None, fecha_fin=None
  ):
    for item in self.tabla.get_children():
      self.tabla.delete(item)

    if not self.service:
      return

    registros = self.service.obtener_servicios()

    # Filtrado por tipo de servicio
    if servicio_filtro and servicio_filtro != "Todos":
      registros = [
          r for r in registros if r.get("tipo_servicio") == servicio_filtro
      ]

  
    if fecha_inicio and fecha_fin:
      registros_filtrados = []
      for r in registros:
        f_str = str(r.get("fecha", "")).strip()
        if f_str and fecha_inicio <= f_str <= fecha_fin:
          registros_filtrados.append(r)
      registros = registros_filtrados

    for r in registros:
      monto = float(r.get("monto", 0))
      self.tabla.insert(
          "",
          "end",
          values=(
              r.get("_id", ""),
              r.get("tipo_servicio", ""),
              f"${monto:,.2f}",
              r.get("referencia", "N/A"),
              r.get("metodo_pago", ""),
              r.get("fecha", ""),
              r.get("hora", ""),
          ),
      )

  def aplicar_filtro(self):
    tipo_seleccionado = self.cb_filtro_tipo.get()

    
    if HAS_TKCALENDAR:
      f_desde = self.cal_desde.get_date().strftime("%Y-%m-%d")
      f_hasta = self.cal_hasta.get_date().strftime("%Y-%m-%d")
    else:
      f_desde = self.cal_desde.get().strip()
      f_hasta = self.cal_hasta.get().strip()

    if f_desde > f_hasta:
      messagebox.showwarning(
          "Atención", "La fecha 'Desde' no puede ser posterior a 'Hasta'."
      )
      return

    self.cargar_servicios(
        servicio_filtro=tipo_seleccionado,
        fecha_inicio=f_desde,
        fecha_fin=f_hasta,
    )

  def limpiar_filtros(self):
    self.cb_filtro_tipo.current(0)
    self.cargar_servicios()



VentanaServicios = VentanaServiciosPublicos