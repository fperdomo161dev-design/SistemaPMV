import os
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk
from services.factura_pdf_service import FacturaPDFService
from .factura_modal import FacturaModal
from .panel_carrito import PanelCarrito
from .panel_productos import PanelProductos

# Paleta de colores 
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
        
        self.db = kwargs.pop("db", None)
        self.pdf_service = kwargs.pop(
            "pdf_service", FacturaPDFService
        ) 
        self.empleado = kwargs.pop("empleado", None)

        
        super().__init__(master, *args, **kwargs)

        #  Guardar variables de estado
        self.usuario_actual = usuario_actual or self.empleado
        self.nombre_vendedor = (
            getattr(self.usuario_actual, "nombre", "Admin")
            if self.usuario_actual
            else "Admin"
        )
        self.carrito = []  
        self.productos_cache = []  
        self.categorias_cache = [] 
        self.factura_actual_id = (
            None  
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
            font=("Segoe UI", 12),
        )
        style.configure(
            "POSTreeview.Treeview.Heading",
            background="#0f172a",
            foreground="#f59e0b",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
        )
        style.map(
            "POSTreeview.Treeview",
            background=[("selected", "#3b82f6")],
            foreground=[("selected", "#ffffff")],
        )

    def _inicializar_interfaz(self):
        """Maquetación dividida: Carrito principal expansivo (Izq) y Panel de Control fijo (Der)."""
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

       
        self.frame_izquierdo = tk.Frame(self, bg=COLOR_FONDO_DARK)
        self.frame_izquierdo.grid(
            row=0, column=0, sticky="nsew", padx=(5, 2), pady=5
        )

     
        self.frame_derecho = tk.Frame(self, bg=COLOR_FONDO_DARK, width=380)
        self.frame_derecho.grid_propagate(False)  # Bloquea expansión por grid
        self.frame_derecho.pack_propagate(False)  # Bloquea expansión por pack
        self.frame_derecho.grid(
            row=0, column=1, sticky="nsew", padx=(2, 5), pady=5
        )

        self._construir_panel_izquierdo()
        self._construir_panel_derecho()

  
    # SECCIÓN IZQUIERDA: DATO CLIENTE, TABLA Y PROCESAR VENTA
    def _construir_panel_izquierdo(self):
        self.frame_izquierdo.rowconfigure(1, weight=1)
        self.frame_izquierdo.columnconfigure(0, weight=1)

        # Cabecera Formulario Cliente y Búsqueda Rápida unificados
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
        frame_cli.columnconfigure(3, weight=1)

        lbl_titulo = tk.Label(
            frame_cli,
            text="🛒 CARRITO DE VENTA",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_ACCENT_NARANJA,
            font=("Segoe UI", 15, "bold"),
        )
        lbl_titulo.grid(
            row=0, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 10)
        )

        entry_kwargs = {
            "bg": COLOR_FONDO_DARK,
            "fg": "#ffffff",
            "insertbackground": "#ffffff",
            "relief": "flat",
            "highlightthickness": 1,
            "highlightbackground": "#334155",
            "highlightcolor": "#3b82f6",
            "font": ("Segoe UI", 11),
        }

        # Cédula
        tk.Label(
            frame_cli,
            text="Cédula:",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 11, "bold"),
        ).grid(row=1, column=0, sticky="w", padx=5, pady=4)

        self.entry_cli_cedula = tk.Entry(frame_cli, width=20, **entry_kwargs)
        self.entry_cli_cedula.grid(row=1, column=1, sticky="w", padx=5, pady=4)
        self.entry_cli_cedula.bind(
            "<FocusOut>",
            lambda e: self.panel_carrito.buscar_cliente_por_cedula(e),
        )
        self.entry_cli_cedula.bind(
            "<Return>",
            lambda e: self.panel_carrito.buscar_cliente_por_cedula(e),
        )

        # Nombre
        tk.Label(
            frame_cli,
            text="Nombre:",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 11, "bold"),
        ).grid(row=2, column=0, sticky="w", padx=5, pady=4)

        self.entry_cli_nombre = tk.Entry(frame_cli, width=25, **entry_kwargs)
        self.entry_cli_nombre.grid(
            row=2, column=1, sticky="w", padx=5, pady=4
        )

        # Correo
        tk.Label(
            frame_cli,
            text="Correo:",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 11, "bold"),
        ).grid(row=3, column=0, sticky="w", padx=5, pady=4)

        self.entry_cli_correo = tk.Entry(frame_cli, width=25, **entry_kwargs)
        self.entry_cli_correo.grid(
            row=3, column=1, sticky="w", padx=5, pady=4
        )

        tk.Label(
            frame_cli,
            text="⚡ Ref/Prod:",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 11, "bold"),
        ).grid(row=1, column=2, sticky="e", padx=(15, 2), pady=4)

        self.entry_buscar_prod = tk.Entry(frame_cli, **entry_kwargs)
        self.entry_buscar_prod.grid(row=1, column=3, sticky="ew", padx=5, pady=4)
        self.entry_buscar_prod.bind(
            "<KeyRelease>",
            lambda e: self.panel_carrito.filtrar_productos_buscador(e),
        )
        self.entry_buscar_prod.bind(
            "<Return>", lambda e: self.panel_carrito.agregar_desde_buscador()
        )

        tk.Label(
            frame_cli,
            text="Cant:",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 11, "bold"),
        ).grid(row=2, column=2, sticky="e", padx=(15, 2), pady=4)

        self.entry_cant_prod = tk.Entry(frame_cli, width=6, **entry_kwargs)
        self.entry_cant_prod.insert(0, "1")
        self.entry_cant_prod.grid(row=2, column=3, sticky="w", padx=5, pady=4)

        # Sugerencias emergentes
        self.listbox_sugerencias = tk.Listbox(
            frame_cli, height=6, bg="#0f172a", fg="#ffffff", font=("Segoe UI", 11),
            relief="solid", bd=1
        )
        self.listbox_sugerencias.place_forget()
        self.listbox_sugerencias.bind(
            "<<ListboxSelect>>",
            lambda e: self.panel_carrito.seleccionar_sugerencia_carrito(e),
        )

        # Tabla Carrito con columnas desglosadas
        frame_tabla = tk.Frame(self.frame_izquierdo, bg=COLOR_CONTAINER_DARK)
        frame_tabla.grid(row=1, column=0, sticky="nsew", pady=5)
        frame_tabla.rowconfigure(0, weight=1)
        frame_tabla.columnconfigure(0, weight=1)

        columnas = ("marca", "color", "talla", "cant", "precio", "subtotal")
        self.tree_cart = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            style="POSTreeview.Treeview",
        )

        # Encabezados de la tabla
        self.tree_cart.heading("marca", text=" Marca", anchor="w")
        self.tree_cart.heading("color", text="Color", anchor="w")
        self.tree_cart.heading("talla", text="Talla", anchor="center")
        self.tree_cart.heading("cant", text="Cant.", anchor="center")
        self.tree_cart.heading("precio", text="Precio Unit.", anchor="e")
        self.tree_cart.heading("subtotal", text="Subtotal", anchor="e")

        self.tree_cart.column(
            "marca", width=200, minwidth=120, anchor="w", stretch=True
        )
        self.tree_cart.column(
            "color", width=90, minwidth=70, anchor="w", stretch=True
        )
        self.tree_cart.column(
            "talla", width=55, minwidth=40, anchor="center", stretch=True
        )
        self.tree_cart.column(
            "cant", width=45, minwidth=35, anchor="center", stretch=True
        )
        self.tree_cart.column(
            "precio", width=115, minwidth=90, anchor="e", stretch=True
        )
        self.tree_cart.column(
            "subtotal", width=130, minwidth=100, anchor="e", stretch=True
        )

        self.tree_cart.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(
            frame_tabla, orient="vertical", command=self.tree_cart.yview
        )
        self.tree_cart.configure(yscroll=scroll_y.set)
        scroll_y.grid(row=0, column=1, sticky="ns")

        # Totales y Procesar Venta
        frame_totales = tk.Frame(self.frame_izquierdo, bg=COLOR_FONDO_DARK)
        frame_totales.grid(row=2, column=0, sticky="ew", pady=(5, 0))

        self.lbl_cant_total = tk.Label(
            frame_totales,
            text="🛍️ Ítems en orden: 0 (Unidades: 0)",
            bg=COLOR_FONDO_DARK,
            fg=COLOR_TEXTO_SEC,
            font=("Segoe UI", 10, "bold"),
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

        # BOTÓN ELIMINAR ITEM
        self.btn_eliminar_item = tk.Button(
            self.frame_izquierdo,
            text="🗑️ Quitar Producto Seleccionado",
            bg=COLOR_ROJO,
            fg="#ffffff",
            activebackground="#dc2626",
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=lambda: self.panel_carrito.eliminar_item_seleccionado(),
        )
        self.btn_eliminar_item.grid(
            row=3, column=0, sticky="ew", pady=(8, 2), ipady=5
        )

        # BOTÓN PROCESAR VENTA
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
            row=4, column=0, sticky="ew", pady=(2, 0), ipady=8
        )
  
    
    # SECCIÓN DERECHA VENDEDOR, ACCIONES Y VISTA PREVIA
    def _construir_panel_derecho(self):
        self.frame_derecho.rowconfigure(2, weight=1)
        self.frame_derecho.columnconfigure(0, weight=1)

       
        frame_vend = tk.Frame(
            self.frame_derecho,
            bg=COLOR_CONTAINER_DARK,
            bd=1,
            relief="solid",
        )
        frame_vend.grid(
            row=0, column=0, sticky="ew", pady=(0, 5), ipadx=8, ipady=8
        )
        frame_vend.columnconfigure(0, weight=1)

        lbl_vend = tk.Label(
            frame_vend,
            text=f"👤 Vendedor: {self.nombre_vendedor}",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 11, "bold"),
        )
        lbl_vend.grid(row=0, column=0, sticky="w", padx=5, pady=2)

        
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
            font=("Segoe UI", 10, "bold"),
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
            font=("Segoe UI", 10, "bold"),
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
            font=("Segoe UI", 10, "bold"),
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
            font=("Segoe UI", 10, "bold"),
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
            font=("Segoe UI", 10, "bold"),
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
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=lambda: self.panel_carrito.realizar_cierre_caja(),
        )
        btn_cierre.grid(row=4, column=0, sticky="ew", padx=5, pady=2)

        # Vista Previa Factura Digital 
        frame_fac = tk.LabelFrame(
            self.frame_derecho,
            text=" 📄 Factura Digital Emitida ",
            bg=COLOR_CONTAINER_DARK,
            fg=COLOR_TEXTO_DARK,
            font=("Segoe UI", 10, "bold"),
        )
        frame_fac.grid(row=2, column=0, sticky="nsew", pady=(5, 0))
        frame_fac.rowconfigure(0, weight=1)
        frame_fac.columnconfigure(0, weight=1)

        container_texto = tk.Frame(frame_fac, bg=COLOR_CONTAINER_DARK)
        container_texto.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        container_texto.rowconfigure(0, weight=1)
        container_texto.columnconfigure(0, weight=1)

        self.txt_factura_digital = tk.Text(
            container_texto,
            font=("Consolas", 11),
            bg=COLOR_NEGRO_FACTURA,
            fg="#34d399",
            insertbackground="white",
            bd=0,
            relief="flat",
        )
        self.txt_factura_digital.grid(row=0, column=0, sticky="nsew")

        scrollbar_factura = ttk.Scrollbar(
            container_texto,
            orient="vertical",
            command=self.txt_factura_digital.yview
        )
        scrollbar_factura.grid(row=0, column=1, sticky="ns")

        self.txt_factura_digital.configure(yscrollcommand=scrollbar_factura.set)
        
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
        if not fac_id or not fac_id.strip():
            return

        fac_id_clean = fac_id.strip()

        #  Buscar la factura en MongoDB desde PosFrame
        if self.db is None:
            from database.conexion import get_db

            self.db = get_db()

        factura_actual = self.db["facturas"].find_one(
            {"numero_factura": fac_id_clean}
        )

        if not factura_actual:
            messagebox.showwarning(
                "No encontrada",
                f"No existe la factura '{fac_id_clean}' en la base de datos.",
            )
            return

        #  Definir Callback de guardado, PDF y Email
        def guardar_y_reexpedir_factura(datos_cliente, items_actualizados):
            try:
                # Recalcular el total
                nuevo_total = sum(
                    item.get("subtotal", 0.0) for item in items_actualizados
                )

                # Actualizar en MongoDB
                self.db["facturas"].update_one(
                    {"numero_factura": factura_actual["numero_factura"]},
                    {
                        "$set": {
                            "cliente": datos_cliente,
                            "items": items_actualizados,
                            "total": nuevo_total,
                            "fecha_actualizacion": datetime.now(),
                        }
                    },
                )

                # Actualizar el diccionario local para el PDF
                factura_actual["cliente"] = datos_cliente
                factura_actual["items"] = items_actualizados
                factura_actual["total"] = nuevo_total

                # Regenerar PDF usando el servicio instanciado en PosFrame
                if callable(getattr(self.pdf_service, "generar_pdf", None)):
                    ruta_pdf = self.pdf_service.generar_pdf(factura_actual)
                else:
                    service = self.pdf_service()
                    ruta_pdf = service.generar_pdf(factura_actual)

                # Enviar correo en segundo plano si hay e-mail
                correo_destino = datos_cliente.get("correo")
                if correo_destino and correo_destino.strip():
                    from services.email_service import EmailService

                    def _hilo_email():
                        try:
                            email_srv = EmailService()
                            email_srv.enviar_factura(
                                correo_destino,
                                datos_cliente.get("nombre", "Cliente"),
                                ruta_pdf,
                                factura_actual["numero_factura"],
                            )
                        except Exception as err_mail:
                            print(f"Error al enviar correo: {err_mail}")

                    threading.Thread(target=_hilo_email, daemon=True).start()

                messagebox.showinfo(
                    "Éxito",
                    f"Factura {factura_actual['numero_factura']} actualizada correctamente.",
                )

            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo guardar la factura: {e}"
                )

        #  Lanzar la ventana modal pasando el callback
        FacturaModal(
            self,
            factura_actual,
            al_confirmar_cb=guardar_y_reexpedir_factura,
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