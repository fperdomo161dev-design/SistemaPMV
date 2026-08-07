import os
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk

# Importación del servicio de PDF desde la carpeta services
from services.factura_pdf_service import FacturaPDFService

# Importación de la ventana modal y submódulos de soporte POS
from .factura_modal import FacturaModal
from .panel_carrito import PanelCarrito
from .panel_productos import PanelProductos

# Paleta de colores Dark Theme
COLOR_FONDO_DARK = "#1a2232"
COLOR_CONTAINER_DARK = "#212d40"
COLOR_TEXTO_DARK = "#ffffff"
COLOR_TEXTO_SEC = "#94a3b8"
COLOR_ACCENT_NARANJA = "#f59e0b"
COLOR_VERDE = "#10b981"
COLOR_AZUL = "#3b82f6"
COLOR_ROJO = "#ef4444"
COLOR_MORADO = "#8b5cf6"
COLOR_NEGRO_FACTURA = "#0f172a"


class PosFrame(ttk.Frame):

    def __init__(self, master, usuario_actual=None, *args, **kwargs):
        # Extraer los parámetros propios de la app ANTES del super()
        self.db = kwargs.pop("db", None)
        self.pdf_service = kwargs.pop(
            "pdf_service", FacturaPDFService
        )  # Usa FacturaPDFService por defecto
        self.empleado = kwargs.pop("empleado", None)

        #  Inicializar ttk.Frame limpio
        super().__init__(master, *args, **kwargs)

        #  Guardar variables de estado
        self.usuario_actual = usuario_actual or self.empleado
        self.nombre_vendedor = (
            getattr(self.usuario_actual, "nombre", "Admin")
            if self.usuario_actual
            else "Admin"
        )
        self.carrito = []  # Estructura de ítems en la orden actual
        self.productos_cache = []  # Caché local de productos desde MongoDB
        self.categorias_cache = []  # Caché local de categorías
        self.factura_actual_id = (
            None  # ID o Código (ej: "FAC-000001") al editar/emitir
        )
        self.pagina_actual = 1
        self.productos_por_pagina = 12

        #  Instanciar submódulos de soporte
        self.panel_productos = PanelProductos(self)
        self.panel_carrito = PanelCarrito(self)

        # Inicializar interfaz y cargar datos
        self._configurar_estilos()
        self._inicializar_interfaz()
        self.cargar_productos_iniciales()
        self._conectar_eventos_globales()

    def _configurar_estilos(self):
        """Configuración de temas y estilos para Treeview y controles ttk en modo oscuro."""
        style = ttk.Style()
        style.theme_use("clam")

        # Estilo para Treeview (Carrito)
        style.configure(
            "POSTreeview.Treeview",
            background="#1e293b",
            foreground="#ffffff",
            fieldbackground="#1e293b",
            rowheight=28,
            borderwidth=0,
            font=("Segoe UI", 9),
        )
        style.configure(
            "POSTreeview.Treeview.Heading",
            background="#0f172a",
            foreground="#f59e0b",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
        )
        style.map(
            "POSTreeview.Treeview",
            background=[("selected", "#3b82f6")],
            foreground=[("selected", "#ffffff")],
        )

    def _inicializar_interfaz(self):
        """Maquetación dividida: Carrito principal (Izq 65%) y Panel de Control (Der 35%)."""
        self.columnconfigure(0, weight=75)
        self.columnconfigure(1, weight=25)
        self.rowconfigure(0, weight=1)

        # Contenedores Principales
        self.frame_izquierdo = tk.Frame(self, bg=COLOR_FONDO_DARK)
        self.frame_izquierdo.grid(
            row=0, column=0, sticky="nsew", padx=(5, 2), pady=5
        )

        self.frame_derecho = tk.Frame(self, bg=COLOR_FONDO_DARK)
        self.frame_derecho.grid(
            row=0, column=1, sticky="nsew", padx=(2, 5), pady=5
        )

        self._construir_panel_izquierdo()
        self._construir_panel_derecho()

  
    # SECCIÓN IZQUIERDA: DATO CLIENTE, TABLA Y PROCESAR VENTA
   
    def _construir_panel_izquierdo(self):
        self.frame_izquierdo.rowconfigure(1, weight=1)
        self.frame_izquierdo.columnconfigure(0, weight=1)

        # Cabecera Formulario Cliente
        frame_cli = tk.Frame(
            self.frame_izquierdo,
            bg=COLOR_CONTAINER_DARK,
            bd=1,
            relief="solid",
        )
        frame_cli.grid(
            row=0, column=0, sticky="ew", pady=(0, 5), ipadx=8, ipady=8
        )
        frame_cli.columnconfigure(1, weight=1)

        lbl_titulo = tk.Label(
            frame_cli,
            text="🛒 CARRITO DE VENTA",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_ACCENT_NARANJA,
            font=("Segoe UI", 11, "bold"),
        )
        lbl_titulo.grid(
            row=0, column=0, columnspan=3, sticky="w", padx=5, pady=(0, 8)
        )

        # Cédula , Vendedor
        tk.Label(
            frame_cli,
            text="Cédula:",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 9, "bold"),
        ).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_cli_cedula = ttk.Entry(frame_cli)
        self.entry_cli_cedula.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.entry_cli_cedula.bind(
            "<FocusOut>",
            lambda e: self.panel_carrito.buscar_cliente_por_cedula(e),
        )
        self.entry_cli_cedula.bind(
            "<Return>",
            lambda e: self.panel_carrito.buscar_cliente_por_cedula(e),
        )

        lbl_vend = tk.Label(
            frame_cli,
            text=f"Vendedor: {self.nombre_vendedor}",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 9, "bold"),
        )
        lbl_vend.grid(row=1, column=2, sticky="e", padx=10, pady=2)

        # Nombre
        tk.Label(
            frame_cli,
            text="Nombre:",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 9, "bold"),
        ).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.entry_cli_nombre = ttk.Entry(frame_cli)
        self.entry_cli_nombre.grid(
            row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=2
        )

        # Correo
        tk.Label(
            frame_cli,
            text="Correo:",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 9, "bold"),
        ).grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.entry_cli_correo = ttk.Entry(frame_cli)
        self.entry_cli_correo.grid(
            row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=2
        )

        # Tabla Carrito
        frame_tabla = tk.Frame(self.frame_izquierdo, bg=COLOR_CONTAINER_DARK)
        frame_tabla.grid(row=1, column=0, sticky="nsew", pady=5)
        frame_tabla.rowconfigure(0, weight=1)
        frame_tabla.columnconfigure(0, weight=1)

        columnas = ("producto", "cant", "precio", "subtotal")
        self.tree_cart = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            style="POSTreeview.Treeview",
        )
        self.tree_cart.heading("producto", text="Producto / Descripción")
        self.tree_cart.heading("cant", text="Cant.")
        self.tree_cart.heading("precio", text="Precio Unit.")
        self.tree_cart.heading("subtotal", text="Subtotal")

        self.tree_cart.column(
            "producto", width=250, minwidth=150, stretch=True
        )
        self.tree_cart.column(
            "cant", width=60, minwidth=40, anchor="center", stretch=False
        )
        self.tree_cart.column(
            "precio", width=100, minwidth=70, anchor="e", stretch=False
        )
        self.tree_cart.column(
            "subtotal", width=110, minwidth=80, anchor="e", stretch=False
        )

        self.tree_cart.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(
            frame_tabla, orient="vertical", command=self.tree_cart.yview
        )
        self.tree_cart.configure(yscroll=scroll_y.set)
        scroll_y.grid(row=0, column=1, sticky="ns")

        # 3. Footer de Totales y Procesar Venta
        frame_totales = tk.Frame(self.frame_izquierdo, bg=COLOR_FONDO_DARK)
        frame_totales.grid(row=2, column=0, sticky="ew", pady=(5, 0))

        self.lbl_cant_total = tk.Label(
            frame_totales,
            text="🛍️ Ítems en orden: 0 (Unidades: 0)",
            bg=COLOR_FONDO_DARK,
            fg=COLOR_TEXTO_SEC,
            font=("Segoe UI", 9, "bold"),
        )
        self.lbl_cant_total.pack(side="left", anchor="w", padx=5)

        self.lbl_total_pagar = tk.Label(
            frame_totales,
            text="TOTAL: $ 0.00",
            bg=COLOR_FONDO_DARK,
            fg=COLOR_VERDE,
            font=("Segoe UI", 16, "bold"),
        )
        self.lbl_total_pagar.pack(side="right", anchor="e", padx=5)

        self.btn_procesar = tk.Button(
            self.frame_izquierdo,
            text="💳 PROCESAR VENTA Y EMITIR FACTURA",
            bg=COLOR_ACCENT_NARANJA,
            fg="#000000",
            activebackground="#d97706",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            command=lambda: self.panel_carrito.procesar_pago(),
        )
        self.btn_procesar.grid(
            row=3, column=0, sticky="ew", pady=(8, 0), ipady=8
        )

    
    # SECCIÓN DERECHA: BÚSQUEDA RÁPIDA, ACCIONES Y VISTA PREVIA
   
    def _construir_panel_derecho(self):
        self.frame_derecho.rowconfigure(2, weight=1)
        self.frame_derecho.columnconfigure(0, weight=1)

        # Búsqueda Rápida de Productos
        frame_busc = tk.LabelFrame(
            self.frame_derecho,
            text=" ⚡ Búsqueda Rápida ",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 9, "bold"),
        )
        frame_busc.grid(
            row=0, column=0, sticky="ew", pady=(0, 5), ipadx=5, ipady=5
        )
        frame_busc.columnconfigure(1, weight=1)

        tk.Label(
            frame_busc,
            text="Ref/Prod:",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
        ).grid(row=0, column=0, sticky="w", padx=5)
        self.entry_buscar_prod = ttk.Entry(frame_busc)
        self.entry_buscar_prod.grid(row=0, column=1, sticky="ew", padx=5)
        self.entry_buscar_prod.bind(
            "<KeyRelease>",
            lambda e: self.panel_carrito.filtrar_productos_buscador(e),
        )
        self.entry_buscar_prod.bind(
            "<Return>", lambda e: self.panel_carrito.agregar_desde_buscador()
        )

        tk.Label(
            frame_busc,
            text="Cant:",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
        ).grid(row=0, column=2, sticky="w", padx=2)
        self.entry_cant_prod = ttk.Entry(frame_busc, width=4)
        self.entry_cant_prod.insert(0, "1")
        self.entry_cant_prod.grid(row=0, column=3, padx=5)

        # Botones Añadir / Limpiar
        btn_add = tk.Button(
            frame_busc,
            text="+ Añadir",
            bg=COLOR_VERDE,
            fg="white",
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            cursor="hand2",
            command=lambda: self.panel_carrito.agregar_desde_buscador(),
        )
        btn_add.grid(row=1, column=1, sticky="ew", padx=5, pady=4)

        btn_clean = tk.Button(
            frame_busc,
            text="✏️ Limpiar",
            bg="#475569",
            fg="white",
            font=("Segoe UI", 8),
            relief="flat",
            cursor="hand2",
            command=lambda: self.panel_carrito.limpiar_buscador_carrito(),
        )
        btn_clean.grid(
            row=1, column=2, columnspan=2, sticky="ew", padx=5, pady=4
        )

        # Sugerencias emergentes de búsqueda rápida
        self.listbox_sugerencias = tk.Listbox(
            frame_busc, height=4, bg="#0f172a", fg="#ffffff"
        )
        self.listbox_sugerencias.grid(
            row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=2
        )
        self.listbox_sugerencias.bind(
            "<<ListboxSelect>>",
            lambda e: self.panel_carrito.seleccionar_sugerencia_carrito(e),
        )

        # Atributos de apoyo requeridos por controladores auxiliares
        self.combo_categoria = ttk.Combobox(
            self.frame_derecho, values=["Todas"]
        )
        self.combo_categoria.current(0)
        self.entry_buscar_cat = ttk.Entry(self.frame_derecho)
        self.lbl_paginacion = tk.Label(self.frame_derecho, text="")
        self.frame_cards = tk.Frame(self.frame_derecho)

        #  Gestión / Acciones
        frame_acciones = tk.LabelFrame(
            self.frame_derecho,
            text=" ⚙️ Gestión / Acciones ",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 9, "bold"),
        )
        frame_acciones.grid(
            row=1, column=0, sticky="ew", pady=5, ipadx=5, ipady=5
        )
        frame_acciones.columnconfigure(0, weight=1)

        btn_nueva = tk.Button(
            frame_acciones,
            text="📄 Nueva Factura",
            bg=COLOR_VERDE,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=lambda: self.panel_carrito.limpiar_para_nueva_factura(),
        )
        btn_nueva.grid(row=0, column=0, sticky="ew", padx=5, pady=2)

        btn_editar = tk.Button(
            frame_acciones,
            text="✏️ Buscar / Editar Factura",
            bg=COLOR_AZUL,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self._prompt_editar_factura,
        )
        btn_editar.grid(row=1, column=0, sticky="ew", padx=5, pady=2)

        btn_eliminar = tk.Button(
            frame_acciones,
            text="🗑️ Eliminar / Anular Factura",
            bg=COLOR_ROJO,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self._prompt_anular_factura,
        )
        btn_eliminar.grid(row=2, column=0, sticky="ew", padx=5, pady=2)

        btn_ver_pdf = tk.Button(
            frame_acciones,
            text="👁️ Ver / Abrir PDF",
            bg=COLOR_ACCENT_NARANJA,
            fg="#000000",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self._abrir_pdf_factura,
        )
        btn_ver_pdf.grid(row=3, column=0, sticky="ew", padx=5, pady=2)

        btn_cierre = tk.Button(
            frame_acciones,
            text="🔒 Realizar Cierre de Caja",
            bg=COLOR_MORADO,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=lambda: self.panel_carrito.realizar_cierre_caja(),
        )
        btn_cierre.grid(row=4, column=0, sticky="ew", padx=5, pady=2)

        #  Vista Previa Factura Digital
        frame_fac = tk.LabelFrame(
            self.frame_derecho,
            text=" 📄 Factura Digital Emitida ",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 9, "bold"),
        )
        frame_fac.grid(row=2, column=0, sticky="nsew", pady=(5, 0))

        self.txt_factura_digital = tk.Text(
            frame_fac,
            font=("Consolas", 11),
            bg=COLOR_NEGRO_FACTURA,
            fg="#34d399",
            insertbackground="white",
            bd=0,
            relief="flat",
        )
        self.txt_factura_digital.pack(fill="both", expand=True, padx=5, pady=5)
        self.panel_carrito._mostrar_factura_vacia()

    
    # CARGA DE DATOS Y ASINCRONISMO

    def _conectar_eventos_globales(self):
        self.bind_all("<F5>", lambda e: self.refresh_productos())

    def cargar_productos_iniciales(self):
        """Carga la caché local de productos desde la BD de forma asíncrona."""

        def _hilo_cargar():
            try:
                if self.db is None:
                    from database.conexion import get_db

                    self.db = get_db()

                
                prods = list(
                    self.db["productos"].find({"activo": {"$ne": False}})
                )
                cats = list(self.db["categorias"].find())

                for p in prods:
                    p["_id"] = str(p["_id"])
                   
                    precio = float(
                        p.get("valorVenta", p.get("precio_venta", 0.0))
                    )
                    p["valorVenta"] = precio
                    p["precio_venta"] = precio

                self.productos_cache = prods
                self.categorias_cache = [
                    c.get("nombre", "") for c in cats if c.get("nombre")
                ]

            
                self.after(0, self._post_carga_inicial)
            except Exception as e:
                print(f"Error cargando base de datos en POS: {e}")

        threading.Thread(target=_hilo_cargar, daemon=True).start()

    def _post_carga_inicial(self):
        if hasattr(self, "panel_productos"):
            self.panel_productos.cargar_categorias(self.categorias_cache)

    def refresh_productos(self):
        self.cargar_productos_iniciales()

    def obtener_ventana_principal(self):
        ventana = self

        for i in range(10):
            if not ventana:
               break
 
            print(f"NIVEL {i}:", type(ventana))

            if hasattr(ventana, "refrescar_productos"):
                 
                 return ventana

            ventana = getattr(ventana, "master", None)

        print("NO ENCONTRADO")
        return None

   
    def _build_ui(self):
        """Alias para mantener compatibilidad."""
        pass

    def cargar_productos_disponibles(self):
        """Alias para mantener compatibilidad."""
        self.cargar_productos_iniciales()

    def _on_busqueda_change(self, event=None):
        if hasattr(self, "panel_productos"):
            self.panel_productos._on_busqueda_change(event)

    def _on_filtro_change(self, event=None):
        if hasattr(self, "panel_productos"):
            self.panel_productos._on_filtro_change(event)

    def cambiar_pagina(self, delta):
        if hasattr(self, "panel_productos"):
            self.panel_productos.cambiar_pagina(delta)

    def _prompt_editar_factura(self):
        fac_id = simpledialog.askstring(
            "Editar Factura",
            "Ingrese el número o ID de la Factura (ej: FAC-000001):",
        )
        if fac_id and fac_id.strip():
            fac_id_clean = fac_id.strip()
            if hasattr(self.panel_carrito, "cargar_factura_para_edicion"):
                self.panel_carrito.cargar_factura_para_edicion(fac_id_clean)
            else:
               
                FacturaModal(
                    self,
                    {"numero_factura": fac_id_clean},
                    al_confirmar_cb=None,
                )

    def _prompt_anular_factura(self):
        fac_id = simpledialog.askstring(
            "Anular Factura", "Ingrese el número o ID de la Factura a anular:"
        )
        if fac_id and fac_id.strip():
            fac_id_clean = fac_id.strip()
            if hasattr(self.panel_carrito, "anular_factura"):
                self.panel_carrito.anular_factura(fac_id_clean)

    def _abrir_pdf_factura(self):
     try:
        numero = simpledialog.askstring(
            "Abrir Factura",
            "Ingrese el número de factura:\nEjemplo: FAC-000007",)
        if not numero:
            return
        numero = numero.strip()
        ruta_pdf = os.path.join(
            "facturas",
            f"{numero}.pdf"
        )
        # Si ya existe el PDF
        if os.path.exists(ruta_pdf):
            os.startfile(ruta_pdf)
            return
        # Buscar la factura en MongoDB
        from database.conexion import get_db
        db = get_db()
        factura = db["facturas"].find_one({
            "numero_factura": numero
        })
        if not factura:
            messagebox.showwarning(
                "Factura no encontrada",
                f"No existe la factura {numero}"
            )
            return
        # Regenerar PDF
        ruta_pdf = self.pdf_service.generar_pdf(factura)
        if os.path.exists(ruta_pdf):
            os.startfile(ruta_pdf)
            messagebox.showinfo(
                "PDF generado",
                f"Se generó nuevamente el PDF de la factura {numero}"
            )
        else:
            messagebox.showwarning(
                "Error",
                "No fue posible generar el PDF."
            )
     except Exception as e:
        messagebox.showerror(
            "Error",
            str(e)
        )