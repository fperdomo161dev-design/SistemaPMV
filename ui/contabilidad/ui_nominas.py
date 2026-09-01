from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from models.nomina import Nomina

try:
  from tkcalendar import DateEntry
except ImportError:
  DateEntry = None

COLOR_BG = "#0B111E"
COLOR_CARD = "#111827"
COLOR_INPUT_BG = "#1F2937"
COLOR_TEXT = "#E5E7EB"
COLOR_ACCENT = "#F59E0B"
COLOR_DANGER = "#EF4444"
COLOR_SUCCESS = "#10B981"
COLOR_BTN_ROJO = "#DC2626"
COLOR_BTN_ROJO_HOVER = "#B91C1C"


class VentanaEditarNomina(tk.Toplevel):
  """Ventana emergente independiente para editar un pago de nómina."""

  def __init__(self, parent, service, registro, callback_actualizar):
    super().__init__(parent)
    self.title("Editar Pago de Nómina")
    self.geometry("450x480")
    self.configure(bg=COLOR_BG)
    self.transient(parent)
    self.grab_set()

    self.service = service
    self.registro = registro 
    self.callback_actualizar = callback_actualizar

    self._build_ui()

  def _build_ui(self):
    tk.Label(
        self,
        text="✏️ Modificar Pago de Nómina",
        bg=COLOR_BG,
        fg=COLOR_TEXT,
        font=("Segoe UI", 12, "bold"),
    ).pack(anchor="w", padx=20, pady=(20, 10))

    frame_form = tk.Frame(self, bg=COLOR_CARD, padx=15, pady=15)
    frame_form.pack(fill="both", expand=True, padx=20, pady=5)

    # Cédula (Solo lectura informativa)
    tk.Label(frame_form, text="Cédula:", bg=COLOR_CARD, fg="#9CA3AF", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=5)
    tk.Label(frame_form, text=self.registro.get("cedula"), bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", pady=5)

    # Empleado (Solo lectura informativa)
    tk.Label(frame_form, text="Empleado:", bg=COLOR_CARD, fg="#9CA3AF", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=5)
    tk.Label(frame_form, text=self.registro.get("empleado"), bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 9, "bold")).grid(row=1, column=1, sticky="w", pady=5)

    # Período (Editable)
    tk.Label(frame_form, text="Período:", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=5)
    self.cb_periodo_edit = ttk.Combobox(
        frame_form, values=["Mensual", "Quincenal 1", "Quincenal 2", "Por Días", "Otro"], state="readonly", width=22
    )
    self.cb_periodo_edit.grid(row=2, column=1, sticky="w", pady=5)
    if self.registro.get("periodo") in self.cb_periodo_edit["values"]:
      self.cb_periodo_edit.set(self.registro.get("periodo"))
    else:
      self.cb_periodo_edit.current(0)

    # Salario Base (Editable)
    tk.Label(frame_form, text="Salario/Pago Base ($):", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", pady=5)
    self.entry_base = tk.Entry(frame_form, bg=COLOR_INPUT_BG, fg=COLOR_TEXT, insertbackground="white", width=25)
    self.entry_base.grid(row=3, column=1, sticky="w", pady=5)
    self.entry_base.insert(0, str(int(self.registro.get("salario_base", 0))))

    # Subsidio de Transporte (Editable)
    tk.Label(frame_form, text="Sub. Transporte ($):", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 9)).grid(row=4, column=0, sticky="w", pady=5)
    self.entry_transporte = tk.Entry(frame_form, bg=COLOR_INPUT_BG, fg=COLOR_TEXT, insertbackground="white", width=25)
    self.entry_transporte.grid(row=4, column=1, sticky="w", pady=5)
    self.entry_transporte.insert(0, str(int(self.registro.get("sub_transporte", 0))))

    # Desc. Salud (Editable - ideal para trabajadores por días)
    tk.Label(frame_form, text="Desc. Salud ($):", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 9)).grid(row=5, column=0, sticky="w", pady=5)
    self.entry_salud = tk.Entry(frame_form, bg=COLOR_INPUT_BG, fg=COLOR_TEXT, insertbackground="white", width=25)
    self.entry_salud.grid(row=5, column=1, sticky="w", pady=5)
    self.entry_salud.insert(0, str(int(self.registro.get("desc_salud", 0))))

    # Desc. Pensión (Editable - ideal para trabajadores por días)
    tk.Label(frame_form, text="Desc. Pensión ($):", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 9)).grid(row=6, column=0, sticky="w", pady=5)
    self.entry_pension = tk.Entry(frame_form, bg=COLOR_INPUT_BG, fg=COLOR_TEXT, insertbackground="white", width=25)
    self.entry_pension.grid(row=6, column=1, sticky="w", pady=5)
    self.entry_pension.insert(0, str(int(self.registro.get("desc_pension", 0))))

    # Botones de acción
    frame_btns = tk.Frame(self, bg=COLOR_BG)
    frame_btns.pack(fill="x", padx=20, pady=15)

    tk.Button(
        frame_btns,
        text="💾 Guardar Cambios",
        bg=COLOR_SUCCESS,
        fg="white",
        font=("Segoe UI", 9, "bold"),
        bd=0,
        padx=12,
        pady=6,
        cursor="hand2",
        command=self.guardar_cambios,
    ).pack(side="right", padx=5)

    tk.Button(
        frame_btns,
        text="❌ Cancelar",
        bg="#4B5563",
        fg="white",
        font=("Segoe UI", 9),
        bd=0,
        padx=12,
        pady=6,
        cursor="hand2",
        command=self.destroy,
    ).pack(side="right", padx=5)

  def guardar_cambios(self):
    try:
      nuevo_base = float(self.entry_base.get().strip())
      nuevo_transporte = float(self.entry_transporte.get().strip())
      desc_salud = float(self.entry_salud.get().strip())
      desc_pension = float(self.entry_pension.get().strip())
      nuevo_periodo = self.cb_periodo_edit.get()
    except ValueError:
      messagebox.showerror("Error", "Todos los campos numéricos deben ser valores válidos.", parent=self)
      return

    # Cálculo del neto utilizando directamente las deducciones ingresadas ideal para pagos por días
    nuevo_neto = (nuevo_base + nuevo_transporte) - (desc_salud + desc_pension)

    actualizado = False
    if hasattr(self.service, "actualizar_pago_nomina"):
      actualizado = self.service.actualizar_pago_nomina(
          cedula=self.registro.get("cedula"),
          fecha_original=self.registro.get("fecha"),
          periodo_original=self.registro.get("periodo"),
          nuevo_periodo=nuevo_periodo,
          nuevo_salario_base=nuevo_base,
          nuevo_sub_transporte=nuevo_transporte,
          nuevo_desc_salud=desc_salud,
          nuevo_desc_pension=desc_pension,
          nuevo_neto=nuevo_neto
      )
    else:
      messagebox.showerror("Error", "El método de actualización no está definido en el servicio.", parent=self)
      return

    if actualizado:
      messagebox.showinfo("Éxito", "Pago actualizado correctamente.", parent=self)
      self.callback_actualizar()
      self.destroy()
    else:
      messagebox.showerror("Error", "No se pudo actualizar el registro en la base de datos.", parent=self)


class VentanaNominas(tk.Toplevel):
  """Ventana Principal de Gestión de Nóminas."""

  def __init__(self, parent, service_contabilidad=None):
    super().__init__(parent)
    self.title("Gestión y Pago de Nómina")
    self.geometry("1100x700")
    self.configure(bg=COLOR_BG)
    self.transient(parent)
    self.grab_set()

    self.service = service_contabilidad
    self.empleados_db = self.service.obtener_lista_empleados() if self.service else []
    self.solo_empleado_activo = False

    self._build_ui()
    self.cargar_historial()

  def _build_ui(self):
    tk.Label(
        self,
        text="👥 Liquidación y Pago de Nómina",
        bg=COLOR_BG,
        fg=COLOR_TEXT,
        font=("Segoe UI", 14, "bold"),
    ).pack(anchor="w", padx=15, pady=(15, 5))

    frame_form = tk.LabelFrame(
        self,
        text=" Procesar Pago y Filtrado ",
        bg=COLOR_CARD,
        fg=COLOR_ACCENT,
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=12,
    )
    frame_form.pack(fill="x", padx=15, pady=5)

    # Fila 1 Empleado, Período y Botón Registrar
    frame_row1 = tk.Frame(frame_form, bg=COLOR_CARD)
    frame_row1.pack(fill="x", pady=(0, 6))

    tk.Label(frame_row1, text="Empleado:", bg=COLOR_CARD, fg=COLOR_TEXT).pack(
        side="left", padx=(0, 5)
    )

    lista_nombres = [
        f"{e.get('cedula', '')} - {e.get('nombre', '')} {e.get('apellido', '')}"
        for e in self.empleados_db
    ]
    self.cb_empleado = ttk.Combobox(
        frame_row1, values=lista_nombres, state="readonly", width=30
    )
    self.cb_empleado.pack(side="left", padx=5)
    self.cb_empleado.bind("<<ComboboxSelected>>", self._al_seleccionar_empleado)

    tk.Label(
        frame_row1, text="Período Pago:", bg=COLOR_CARD, fg=COLOR_TEXT
    ).pack(side="left", padx=(15, 5))
    self.cb_periodo = ttk.Combobox(
        frame_row1,
        values=["Mensual", "Quincenal 1", "Quincenal 2", "Por Días"],
        state="readonly",
        width=14,
    )
    self.cb_periodo.pack(side="left", padx=5)
    self.cb_periodo.current(0)

    tk.Button(
        frame_row1,
        text="💵 Registrar Pago",
        bg=COLOR_SUCCESS,
        fg="#FFF",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2",
        command=self.registrar_pago,
    ).pack(side="left", padx=(15, 5))

    # Fila 2 Desglose salarial rápido
    self.lbl_desglose = tk.Label(
        frame_form,
        text="Seleccione un empleado para calcular la nómina.",
        bg=COLOR_CARD,
        fg=COLOR_ACCENT,
        font=("Segoe UI", 9, "bold"),
    )
    self.lbl_desglose.pack(anchor="w", pady=(6, 8))

    # Fila 3: Filtros y Botones de Editar / Eliminar
    frame_row3 = tk.Frame(frame_form, bg=COLOR_CARD)
    frame_row3.pack(fill="x", pady=(4, 0))

    tk.Label(frame_row3, text="Desde:", bg=COLOR_CARD, fg=COLOR_TEXT).pack(
        side="left", padx=(0, 2)
    )
    if DateEntry:
      self.cal_inicio = DateEntry(
          frame_row3, width=11, background="darkblue", foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd"
      )
      self.cal_inicio.pack(side="left", padx=2)
      self.cal_inicio.delete(0, "end")
    else:
      self.cal_inicio = tk.Entry(frame_row3, bg=COLOR_INPUT_BG, fg=COLOR_TEXT, width=10)
      self.cal_inicio.pack(side="left", padx=2)

    tk.Label(frame_row3, text="Hasta:", bg=COLOR_CARD, fg=COLOR_TEXT).pack(
        side="left", padx=(10, 2)
    )
    if DateEntry:
      self.cal_fin = DateEntry(
          frame_row3, width=11, background="darkblue", foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd"
      )
      self.cal_fin.pack(side="left", padx=2)
      self.cal_fin.delete(0, "end")
    else:
      self.cal_fin = tk.Entry(frame_row3, bg=COLOR_INPUT_BG, fg=COLOR_TEXT, width=10)
      self.cal_fin.pack(side="left", padx=2)

    tk.Button(
        frame_row3,
        text="🔍 Buscar",
        bg=COLOR_BTN_ROJO,
        fg="white",
        font=("Segoe UI", 8, "bold"),
        bd=0,
        padx=8,
        pady=4,
        cursor="hand2",
        command=self.cargar_historial,
    ).pack(side="left", padx=8)

    self.btn_filtrar_empleado = tk.Button(
        frame_row3,
        text="👤 Solo Este",
        bg="#374151",
        fg="white",
        font=("Segoe UI", 8, "bold"),
        bd=0,
        padx=8,
        pady=4,
        cursor="hand2",
        command=self.toggle_filtro_empleado,
    )
    self.btn_filtrar_empleado.pack(side="left", padx=4)

    tk.Button(
        frame_row3,
        text="🔄 Limpiar",
        bg="#4B5563",
        fg="white",
        font=("Segoe UI", 8),
        bd=0,
        padx=6,
        pady=4,
        cursor="hand2",
        command=self.limpiar_filtros,
    ).pack(side="left", padx=4)

    # Botones de Acción sobre la tabla (Derecha)
    tk.Button(
        frame_row3,
        text="🗑️ Eliminar",
        bg=COLOR_DANGER,
        fg="white",
        font=("Segoe UI", 8, "bold"),
        bd=0,
        padx=8,
        pady=4,
        cursor="hand2",
        command=self.eliminar_pago,
    ).pack(side="right", padx=5)

    tk.Button(
        frame_row3,
        text="✏️ Editar",
        bg="#2563EB",
        fg="white",
        font=("Segoe UI", 8, "bold"),
        bd=0,
        padx=8,
        pady=4,
        cursor="hand2",
        command=self.abrir_ventana_edicion,
    ).pack(side="right", padx=5)

    # Tabla
    frame_tabla = tk.Frame(self, bg=COLOR_CARD)
    frame_tabla.pack(fill="both", expand=True, padx=15, pady=10)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Nomina.Treeview",
        background="#1F2937",
        foreground=COLOR_TEXT,
        fieldbackground="#1F2937",
        rowheight=26,
        bordercolor="#374151",
        borderwidth=1,
    )
    style.configure(
        "Nomina.Treeview.Heading",
        background=COLOR_CARD,
        foreground="#9CA3AF",
        font=("Segoe UI", 9, "bold"),
    )
    style.map("Nomina.Treeview", background=[("selected", "#374151")])

    cols = ("cedula", "empleado", "periodo", "base", "sub_trans", "descuentos", "neto", "fecha")
    self.tabla = ttk.Treeview(frame_tabla, columns=cols, show="headings", style="Nomina.Treeview")

    self.tabla.heading("cedula", text="Cédula")
    self.tabla.heading("empleado", text="Empleado")
    self.tabla.heading("periodo", text="Período")
    self.tabla.heading("base", text="Salario Base")
    self.tabla.heading("sub_trans", text="Sub. Transp.")
    self.tabla.heading("descuentos", text="Deducciones")
    self.tabla.heading("neto", text="Neto Pagado")
    self.tabla.heading("fecha", text="Fecha Pago")

    self.tabla.column("cedula", width=100, anchor="center")
    self.tabla.column("empleado", width=160, anchor="w")
    self.tabla.column("periodo", width=100, anchor="center")
    self.tabla.column("base", width=100, anchor="e")
    self.tabla.column("sub_trans", width=100, anchor="e")
    self.tabla.column("descuentos", width=100, anchor="e")
    self.tabla.column("neto", width=110, anchor="e")
    self.tabla.column("fecha", width=120, anchor="center")

    scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
    self.tabla.configure(yscrollcommand=scroll.set)

    self.tabla.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

  def _al_seleccionar_empleado(self, event):
    idx = self.cb_empleado.current()
    if idx < 0:
      return
    emp = self.empleados_db[idx]

    salario = float(emp.get("salario", 0) or emp.get("salario_mes", 0))
    sub_trans = float(emp.get("sub_transp", 0))
    pct_salud = float(emp.get("pct_salud", 0.04))
    pct_pension = float(emp.get("pct_pension", 0.04))

    desc_salud = salario * pct_salud
    desc_pension = salario * pct_pension
    total_deducciones = desc_salud + desc_pension
    neto = (salario + sub_trans) - total_deducciones

    self.datos_calculados = {
        "cedula": str(emp.get("cedula")),
        "nombre": f"{emp.get('nombre', '')} {emp.get('apellido', '')}",
        "salario_base": salario,
        "sub_transporte": sub_trans,
        "desc_salud": desc_salud,
        "desc_pension": desc_pension,
        "neto_pagar": neto,
    }

    self.lbl_desglose.config(
        text=(
            f"Base: ${salario:,.0f} | Sub. Transp: ${sub_trans:,.0f} |"
            f" Deducciones: -${total_deducciones:,.0f} | NETO: ${neto:,.0f}"
        )
    )

    if self.solo_empleado_activo:
      self.cargar_historial()

  def toggle_filtro_empleado(self):
    self.solo_empleado_activo = not self.solo_empleado_activo
    if self.solo_empleado_activo:
      self.btn_filtrar_empleado.config(bg="#059669", text="✅ Solo Este")
    else:
      self.btn_filtrar_empleado.config(bg="#374151", text="👤 Solo Este")
    self.cargar_historial()

  def limpiar_filtros(self):
    if DateEntry and hasattr(self.cal_inicio, "delete"):
      try:
        self.cal_inicio.delete(0, "end")
      except Exception:
        pass
    if DateEntry and hasattr(self.cal_fin, "delete"):
      try:
        self.cal_fin.delete(0, "end")
      except Exception:
        pass
    self.solo_empleado_activo = False
    self.btn_filtrar_empleado.config(bg="#374151", text="👤 Solo Este")
    self.cargar_historial()

  def registrar_pago(self):
    if not hasattr(self, "datos_calculados"):
      messagebox.showwarning("Atención", "Seleccione un empleado válido.")
      return

    if not self.service:
      messagebox.showerror("Error", "Servicio contable no disponible.")
      return

    c = self.datos_calculados
    obj_nom = Nomina(
        cedula=c["cedula"],
        empleado=c["nombre"],
        salario_base=c["salario_base"],
        sub_transporte=c["sub_transporte"],
        desc_salud=c["desc_salud"],
        desc_pension=c["desc_pension"],
        neto_pagar=c["neto_pagar"],
        periodo=self.cb_periodo.get(),
    )

    if self.service.registrar_pago_nomina(obj_nom):
      messagebox.showinfo("Éxito", "Pago de nómina registrado correctamente.")
      self.cargar_historial()
    else:
      messagebox.showerror("Error", "No se pudo registrar la nómina.")

  def abrir_ventana_edicion(self):
    """Abre el cuadro emergente para editar el pago seleccionado recuperando sus deducciones exactas."""
    seleccion = self.tabla.selection()
    if not seleccion:
      messagebox.showwarning("Atención", "Seleccione un pago de la tabla para editar.")
      return

    item_id = seleccion[0]
    valores = self.tabla.item(item_id, "values")
    cedula_sel = valores[0]
    periodo_sel = valores[2]
    fecha_sel = valores[7]

    # Buscar el registro completo original para extraer descuentoz salud y pension exactos
    registro_encontrado = None
    if self.service:
      historial = self.service.obtener_historial_nominas()
      for r in historial:
        if str(r.get("cedula")) == str(cedula_sel) and r.get("periodo") == periodo_sel and str(r.get("fecha", ""))[:10] == str(fecha_sel)[:10]:
          registro_encontrado = r
          break

    if not registro_encontrado:
      registro_encontrado = {
          "cedula": cedula_sel,
          "empleado": valores[1],
          "periodo": periodo_sel,
          "salario_base": float(valores[3].replace("$", "").replace(",", "")),
          "sub_transporte": float(valores[4].replace("$", "").replace(",", "")),
          "desc_salud": 0.0,
          "desc_pension": 0.0,
          "fecha": fecha_sel
      }

    VentanaEditarNomina(self, self.service, registro_encontrado, self.cargar_historial)

  def eliminar_pago(self):
    seleccion = self.tabla.selection()
    if not seleccion:
      messagebox.showwarning("Atención", "Seleccione un pago de la tabla para eliminar.")
      return

    if not messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este pago de nómina?"):
      return

    if not self.service:
      return

    valores = self.tabla.item(seleccion[0], "values")
    eliminado = self.service.eliminar_pago_nomina(
        cedula=valores[0], fecha=valores[7], periodo=valores[2]
    )

    if eliminado:
      messagebox.showinfo("Éxito", "Pago eliminado correctamente.")
      self.cargar_historial()
    else:
      messagebox.showerror("Error", "No se pudo eliminar el registro.")

  def cargar_historial(self):
    for item in self.tabla.get_children():
      self.tabla.delete(item)

    if not self.service:
      return

    f_inicio = self.cal_inicio.get().strip() if hasattr(self.cal_inicio, "get") and self.cal_inicio.get() else ""
    f_fin = self.cal_fin.get().strip() if hasattr(self.cal_fin, "get") and self.cal_fin.get() else ""

    cedula_filtro = None
    if self.solo_empleado_activo and self.cb_empleado.get():
      cedula_filtro = self.cb_empleado.get().split(" - ")[0].strip()

    registros = self.service.obtener_historial_nominas()
    if not registros:
      return

    for r in registros:
      cedula_r = str(r.get("cedula", ""))
      fecha_completa = str(r.get("fecha", ""))
      fecha_r = fecha_completa[:10] if len(fecha_completa) >= 10 else fecha_completa

      if cedula_filtro and cedula_r != cedula_filtro:
        continue
      if f_inicio and fecha_r < f_inicio:
        continue
      if f_fin and fecha_r > f_fin:
        continue

      deducciones = r.get("desc_salud", 0) + r.get("desc_pension", 0)
      self.tabla.insert(
          "",
          "end",
          values=(
              cedula_r,
              r.get("empleado", ""),
              r.get("periodo", ""),
              f"${r.get('salario_base', 0):,.0f}",
              f"${r.get('sub_transporte', 0):,.0f}",
              f"${deducciones:,.0f}",
              f"${r.get('neto_pagar', 0):,.0f}",
              fecha_completa,
          ),
      )