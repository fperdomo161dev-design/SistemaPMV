import tkinter as tk
from tkinter import messagebox, ttk

from models.producto import Producto
from services.producto_service import (
    actualizar_producto,
    crear_producto,
    eliminar_producto,
    listar_productos,
)

# PALETA DE COLORES UI DARK EXECUTIVE
COLOR_BG = "#0B111E"
COLOR_CARD = "#111827"
COLOR_INPUT_BG = "#1F2937"
COLOR_TEXT = "#E5E7EB"
COLOR_ACCENT = "#F59E0B"
COLOR_MUTED = "#9CA3AF"


class ProductosFrame(ttk.Frame):

  def __init__(self, master, usuario_actual=None, *args, **kwargs):
    self.usuario_actual = usuario_actual

    super().__init__(master, *args, **kwargs)

    # Validamos el rol del usuario recibido para saber si es administrador o gerente
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

    self.producto_seleccionado = None

    # Configuración de estilos Tkinter
    self._configurar_estilos()

    self.columnconfigure(0, weight=1)
    self.rowconfigure(0, weight=1)

    self._build_ui()
    self.cargar_productos()

    self.tree.bind("<<TreeviewSelect>>", self.al_seleccionar_producto)

  def _configurar_estilos(self):
    style = ttk.Style()
    style.theme_use("clam")

    # Configuración de Frame principal
    style.configure("Dark.TFrame", background=COLOR_BG)
    style.configure("Card.TFrame", background=COLOR_CARD, relief="flat")

    # Labels
    style.configure(
        "Dark.TLabel",
        background=COLOR_BG,
        foreground=COLOR_TEXT,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Card.TLabel",
        background=COLOR_CARD,
        foreground=COLOR_TEXT,
        font=("Segoe UI", 10),
    )
    style.configure(
        "CardBold.TLabel",
        background=COLOR_CARD,
        foreground=COLOR_ACCENT,
        font=("Segoe UI", 10, "bold"),
    )

    # Botones
    style.configure(
        "Action.TButton",
        font=("Segoe UI", 10, "bold"),
        background="#1E293B",
        foreground=COLOR_TEXT,
        bordercolor="#374151",
        borderwidth=1,
        focusthickness=0,
    )
    style.map(
        "Action.TButton",
        background=[("active", COLOR_ACCENT), ("disabled", "#374151")],
        foreground=[("active", "#000000"), ("disabled", COLOR_MUTED)],
    )

    style.configure(
        "Primary.TButton",
        font=("Segoe UI", 10, "bold"),
        background=COLOR_ACCENT,
        foreground="#000000",
        bordercolor=COLOR_ACCENT,
        borderwidth=1,
    )
    style.map("Primary.TButton", background=[("active", "#D97706")])

    # Tabla / Treeview
    style.configure(
        "Treeview",
        background="#1F2937",
        foreground=COLOR_TEXT,
        fieldbackground="#1F2937",
        rowheight=28,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Treeview.Heading",
        background="#111827",
        foreground=COLOR_ACCENT,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", COLOR_ACCENT)],
        foreground=[("selected", "#000000")],
    )

  def _build_ui(self):
    # Frame contenedor exterior
    outer = ttk.Frame(self, style="Dark.TFrame")
    outer.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    outer.columnconfigure(0, weight=1)
    outer.rowconfigure(1, weight=1)

    # ---------------------------------------------------------
    # 1. BUSCADOR
    # ---------------------------------------------------------
    search_frame = ttk.Frame(outer, style="Dark.TFrame")
    search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))

    ttk.Label(
        search_frame, text="Buscar por Ref:", style="Dark.TLabel"
    ).grid(row=0, column=0, padx=(0, 10))

    self.var_buscar = tk.StringVar()

    entry_buscar = tk.Entry(
        search_frame,
        textvariable=self.var_buscar,
        width=20,
        bg=COLOR_INPUT_BG,
        fg=COLOR_TEXT,
        insertbackground=COLOR_ACCENT,
        bd=1,
        relief="solid",
        font=("Segoe UI", 10),
    )
    entry_buscar.grid(row=0, column=1, padx=(0, 10), ipady=3)
    entry_buscar.bind("<Return>", lambda e: self.buscar_por_ref())

    ttk.Button(
        search_frame,
        text="Buscar",
        style="Primary.TButton",
        command=self.buscar_por_ref,
    ).grid(row=0, column=2, padx=5)

    ttk.Button(
        search_frame,
        text="⚠️ Ver Stock Bajo",
        style="Primary.TButton",
        command=self.mostrar_solo_stock_bajo,
    ).grid(row=0, column=4, padx=5)

    ttk.Button(
        search_frame,
        text="Limpiar",
        style="Action.TButton",
        command=self.limpiar_busqueda,
    ).grid(row=0, column=3, padx=5)

    # ---------------------------------------------------------
    # 2. TABLA (Dinámica según rol)
    # ---------------------------------------------------------
    tabla_frame = ttk.Frame(outer, style="Dark.TFrame")
    tabla_frame.grid(row=1, column=0, sticky="nsew")
    tabla_frame.columnconfigure(0, weight=1)
    tabla_frame.rowconfigure(0, weight=1)

    # Definimos columnas condicionalmente: si es admin incluye 'valorCompra', de lo contrario se omite
    if self.es_admin:
      self.columns = (
          "ref",
          "marca",
          "talla",
          "color",
          "stock",
          "valorCompra",
          "valorVenta",
          "ubicacion",
      )
      headers = [
          ("ref", "Referencia"),
          ("marca", "Marca"),
          ("talla", "Talla"),
          ("color", "Color"),
          ("stock", "Stock"),
          ("valorCompra", "V. Compra"),
          ("valorVenta", "V. Venta"),
          ("ubicacion", "Ubicación"),
      ]
    else:
      self.columns = (
          "ref",
          "marca",
          "talla",
          "color",
          "stock",
          "valorVenta",
          "ubicacion",
      )
      headers = [
          ("ref", "Referencia"),
          ("marca", "Marca"),
          ("talla", "Talla"),
          ("color", "Color"),
          ("stock", "Stock"),
          ("valorVenta", "V. Venta"),
          ("ubicacion", "Ubicación"),
      ]

    self.tree = ttk.Treeview(
        tabla_frame, columns=self.columns, show="headings", height=10
    )

    for col, heading_text in headers:
      self.tree.heading(col, text=heading_text)
      self.tree.column(col, anchor="center", width=110)

    scrollbar = ttk.Scrollbar(
        tabla_frame, orient="vertical", command=self.tree.yview
    )
    self.tree.configure(yscrollcommand=scrollbar.set)

    self.tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    # ---------------------------------------------------------
    # 3. FORMULARIO E INVENTARIO (PANEL INFERIOR CENTRADO)
    # ---------------------------------------------------------
    card_container = ttk.Frame(outer, style="Card.TFrame")
    card_container.grid(row=2, column=0, sticky="ew", pady=(15, 0), ipady=15)

    card_container.columnconfigure(0, weight=1)

    form_center_wrapper = ttk.Frame(card_container, style="Card.TFrame")
    form_center_wrapper.grid(row=0, column=0)

    formulario = ttk.Frame(form_center_wrapper, style="Card.TFrame")
    formulario.grid(row=0, column=0, sticky="nsew", padx=(0, 30))

    # VARIABLES
    self.var_ref = tk.StringVar()
    self.var_marca = tk.StringVar()
    self.var_talla = tk.StringVar()
    self.var_color = tk.StringVar()
    self.var_stock = tk.StringVar()
    self.var_valor_compra = tk.StringVar()
    self.var_valor_venta = tk.StringVar()
    self.var_ubicacion = tk.StringVar()

    # Campos dinámicos del formulario según el rol
    if self.es_admin:
      campos = [
          ("Referencia", self.var_ref, 0, 0),
          ("Marca", self.var_marca, 0, 2),
          ("Talla", self.var_talla, 1, 0),
          ("Color", self.var_color, 1, 2),
          ("Stock", self.var_stock, 2, 0),
          ("V. Compra", self.var_valor_compra, 2, 2),
          ("V. Venta", self.var_valor_venta, 3, 0),
          ("Ubicación", self.var_ubicacion, 3, 2),
      ]
    else:
      campos = [
          ("Referencia", self.var_ref, 0, 0),
          ("Marca", self.var_marca, 0, 2),
          ("Talla", self.var_talla, 1, 0),
          ("Color", self.var_color, 1, 2),
          ("Stock", self.var_stock, 2, 0),
          ("V. Venta", self.var_valor_venta, 2, 2),
          ("Ubicación", self.var_ubicacion, 3, 0),
      ]

    for label_text, var, row, col in campos:
      ttk.Label(formulario, text=label_text, style="CardBold.TLabel").grid(
          row=row, column=col, sticky="e", padx=(10, 5), pady=6
      )

      if label_text == "Referencia":
        entry = tk.Entry(
            formulario,
            textvariable=var,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            insertbackground=COLOR_ACCENT,
            bd=1,
            relief="solid",
            font=("Segoe UI", 10),
            width=16,
            state="disabled",
        )
      else:
        entry = tk.Entry(
            formulario,
            textvariable=var,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            insertbackground=COLOR_ACCENT,
            bd=1,
            relief="solid",
            font=("Segoe UI", 10),
            width=16,
        )

      entry.grid(
          row=row, column=col + 1, sticky="w", padx=(0, 15), pady=6, ipady=3
      )

    # ---------------------------------------------------------
    # 4. BOTONES LATERALES DE ACCIÓN
    # ---------------------------------------------------------
    acciones_frame = ttk.Frame(form_center_wrapper, style="Card.TFrame")
    acciones_frame.grid(row=0, column=1, sticky="ns", padx=(20, 0))

    ttk.Label(
        acciones_frame, text="Acciones", style="CardBold.TLabel"
    ).pack(anchor="w", pady=(0, 6))

    ANCHO_BOTON = 18

    ttk.Button(
        acciones_frame,
        text="➕ Guardar",
        style="Primary.TButton",
        width=ANCHO_BOTON,
        command=self.guardar_producto,
    ).pack(fill="x", pady=3, ipady=2)

    ttk.Button(
        acciones_frame,
        text="✏️ Actualizar",
        style="Action.TButton",
        width=ANCHO_BOTON,
        command=self.actualizar_producto_ui,
    ).pack(fill="x", pady=3, ipady=2)

    ttk.Button(
        acciones_frame,
        text="🗑️ Eliminar",
        style="Action.TButton",
        width=ANCHO_BOTON,
        command=self.eliminar_producto_ui,
    ).pack(fill="x", pady=3, ipady=2)

    ttk.Button(
        acciones_frame,
        text="🧹 Limpiar",
        style="Action.TButton",
        width=ANCHO_BOTON,
        command=self.limpiar_formulario,
    ).pack(fill="x", pady=3, ipady=2)

  # ---------------------------------------------------------
  # LÓGICA DE INTERFAZ
  # ---------------------------------------------------------

  def guardar_producto(self):
    try:
      # Si no es admin, asignamos 0 o un valor por defecto al valor de compra para evitar errores en la BD
      v_compra_val = (
          int(self.var_valor_compra.get())
          if self.es_admin and self.var_valor_compra.get().strip()
          else 0
      )

      producto = Producto(
          numReferencia=0,
          marca=self.var_marca.get(),
          talla=self.var_talla.get(),
          color=self.var_color.get(),
          cantidadStock=int(self.var_stock.get()),
          valorCompra=v_compra_val,
          valorVenta=int(self.var_valor_venta.get()),
          ubicacion=self.var_ubicacion.get(),
      )

      crear_producto(producto)
      self.cargar_productos()
      self.limpiar_formulario()

      messagebox.showinfo("Éxito", "Producto guardado correctamente.")

    except Exception as e:
      messagebox.showerror(
          "Error", f"No se pudo guardar el producto.\nDetalle: {e}"
      )

  def actualizar_producto_ui(self):
    if self.producto_seleccionado is None:
      messagebox.showwarning(
          "Advertencia", "Debes seleccionar un producto para actualizar."
      )
      return

    try:
      datos = {
          "marca": self.var_marca.get(),
          "talla": self.var_talla.get(),
          "color": self.var_color.get(),
          "cantidadStock": int(self.var_stock.get()),
          "valorVenta": int(self.var_valor_venta.get()),
          "ubicacion": self.var_ubicacion.get(),
      }

      # Solo actualizamos el valor de compra si el usuario es administrador
      if self.es_admin and self.var_valor_compra.get().strip():
        datos["valorCompra"] = int(self.var_valor_compra.get())

      actualizar_producto(self.producto_seleccionado, datos)
      self.cargar_productos()

      messagebox.showinfo(
          "Actualizado", "Producto actualizado correctamente."
      )

    except Exception as e:
      messagebox.showerror("Error", f"No se pudo actualizar.\nDetalle: {e}")

  def eliminar_producto_ui(self):
    if self.producto_seleccionado is None:
      messagebox.showwarning(
          "Advertencia", "Debes seleccionar un producto para eliminar."
      )
      return

    try:
      eliminar_producto(self.producto_seleccionado)
      self.cargar_productos()
      self.limpiar_formulario()

      messagebox.showinfo("Eliminado", "Producto eliminado correctamente.")

    except Exception as e:
      messagebox.showerror("Error", f"No se pudo eliminar.\nDetalle: {e}")

  def al_seleccionar_producto(self, event):
    seleccion = self.tree.selection()
    if not seleccion:
      return

    valores = self.tree.item(seleccion[0])["values"]

    if valores:
      self.producto_seleccionado = valores[0]

      self.var_ref.set(valores[0])
      self.var_marca.set(valores[1])
      self.var_talla.set(valores[2])
      self.var_color.set(valores[3])

      # Limpiamos el texto de stock por si tenía la etiqueta de alerta visual
      stock_texto = str(valores[4]).split(" ")[0]
      self.var_stock.set(stock_texto)

      if self.es_admin:
        self.var_valor_compra.set(valores[5])
        self.var_valor_venta.set(valores[6])
        self.var_ubicacion.set(valores[7])
      else:
        self.var_valor_compra.set("")  # El vendedor no maneja este valor en pantalla
        self.var_valor_venta.set(valores[5])
        self.var_ubicacion.set(valores[6])

      # Alerta en pantalla al seleccionar si el stock es bajo
      stock_num = int(stock_texto)
      if stock_num <= 5:
        messagebox.showwarning(
            "¡Alerta de Inventario!",
            f"El producto seleccionado (Ref: {valores[0]} - {valores[1]}) tiene"
            f" stock bajo: {stock_num} unidades disponibles.",
        )

  def cargar_productos(self):
    print("ID FRAME PRODUCTOS:", id(self))
    for item in self.tree.get_children():
      self.tree.delete(item)

    self.tree.tag_configure("stock_bajo", background="#e62323")

    productos = listar_productos()
    print("TOTAL PRODUCTOS:", len(productos))
    
    LIMITE_STOCK_BAJO = 5

    for p in productos:
      print(
         "INSERTANDO:",
         p.numReferencia,
         "STOCK:",
         p.cantidadStock
)
      es_stock_bajo = p.cantidadStock <= LIMITE_STOCK_BAJO

      # Construimos los valores a insertar según los permisos del rol
      if self.es_admin:
        values = (
            p.numReferencia,
            p.marca,
            p.talla,
            p.color,
            f"{p.cantidadStock} (¡BAJO!)" if es_stock_bajo else p.cantidadStock,
            p.valorCompra,
            p.valorVenta,
            p.ubicacion,
        )
      else:
        values = (
            p.numReferencia,
            p.marca,
            p.talla,
            p.color,
            f"{p.cantidadStock} (¡BAJO!)" if es_stock_bajo else p.cantidadStock,
            p.valorVenta,
            p.ubicacion,
        )

      item_id = self.tree.insert("", "end", values=values)

      if es_stock_bajo:
        self.tree.item(item_id, tags=("stock_bajo",))

  def buscar_por_ref(self):
    texto = self.var_buscar.get().strip()

    if not texto:
      self.cargar_productos()
      return

    try:
      ref_buscar = int(texto)
    except ValueError:
      messagebox.showerror("Error", "La referencia debe ser numérica.")
      return

    for row in self.tree.get_children():
      self.tree.delete(row)

    for p in listar_productos():
      if int(p.numReferencia) == ref_buscar:
        es_stock_bajo = p.cantidadStock <= 5

        if self.es_admin:
          values = (
              p.numReferencia,
              p.marca,
              p.talla,
              p.color,
              f"{p.cantidadStock} (¡BAJO!)" if es_stock_bajo else p.cantidadStock,
              p.valorCompra,
              p.valorVenta,
              p.ubicacion,
          )
        else:
          values = (
              p.numReferencia,
              p.marca,
              p.talla,
              p.color,
              f"{p.cantidadStock} (¡BAJO!)" if es_stock_bajo else p.cantidadStock,
              p.valorVenta,
              p.ubicacion,
          )
          
        item_id = self.tree.insert("", "end", values=values)
        if es_stock_bajo:
          self.tree.item(item_id, tags=("stock_bajo",))
        break

  def limpiar_busqueda(self):
    self.var_buscar.set("")
    self.cargar_productos()

  def limpiar_formulario(self):
    self.var_ref.set("")
    self.var_marca.set("")
    self.var_talla.set("")
    self.var_color.set("")
    self.var_stock.set("")
    self.var_valor_compra.set("")
    self.var_valor_venta.set("")
    self.var_ubicacion.set("")

    self.producto_seleccionado = None

  def mostrar_solo_stock_bajo(self):
    for item in self.tree.get_children():
      self.tree.delete(item)

    productos = listar_productos()
    LIMITE_STOCK_BAJO = 5
    encontrados = False

    for p in productos:
      
      if p.cantidadStock <= LIMITE_STOCK_BAJO:
        encontrados = True

        if self.es_admin:
          values = (
              p.numReferencia,
              p.marca,
              p.talla,
              p.color,
              f"{p.cantidadStock} (¡BAJO!)",
              p.valorCompra,
              p.valorVenta,
              p.ubicacion,
          )
        else:
          values = (
              p.numReferencia,
              p.marca,
              p.talla,
              p.color,
              f"{p.cantidadStock} (¡BAJO!)",
              p.valorVenta,
              p.ubicacion,
          )

        item_id = self.tree.insert("", "end", values=values)
        self.tree.item(item_id, tags=("stock_bajo",))

    if not encontrados:
      messagebox.showinfo(
          "Inventario", "No hay productos con stock bajo actualmente."
      )