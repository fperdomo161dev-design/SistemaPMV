from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from bson import ObjectId

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None

from models.proveedor import Proveedor
from services.proveedor_service import ProveedorService


COLOR_BG = "#0B111E"
COLOR_CARD = "#111827"
COLOR_INPUT_BG = "#1F2937"
COLOR_TEXT = "#E5E7EB"
COLOR_ACCENT = "#F59E0B"
COLOR_DANGER = "#EF4444"
COLOR_SUCCESS = "#10B981"
COLOR_BTN_ROJO = "#DC2626"
COLOR_BTN_ROJO_HOVER = "#B91C1C"


class VentanaCrearProveedor(tk.Toplevel):
    """Ventana emergente para registrar un nuevo proveedor."""

    def __init__(
        self,
        parent,
        service_proveedor,
        al_guardar_callback
    ):
        super().__init__(parent)

        self.title("Registrar Nuevo Proveedor")
        self.geometry("500x370")
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.service_proveedor = service_proveedor
        self.al_guardar_callback = al_guardar_callback

        self._build_ui()

    def _build_ui(self):

        tk.Label(
            self,
            text="➕ Nuevo Proveedor",
            bg=COLOR_BG,
            fg=COLOR_ACCENT,
            font=("Segoe UI", 13, "bold"),
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 5)
        )

        frame_form = tk.Frame(
            self,
            bg=COLOR_CARD,
            padx=15,
            pady=15
        )

        frame_form.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        campos = [
            ("Nombre / Razón Social *:", "txt_nombre"),
            ("NIT / Cédula:", "txt_nit"),
            ("Teléfono:", "txt_telefono"),
            ("Email:", "txt_email"),
            ("Dirección:", "txt_direccion"),
        ]

        for i, (lbl, attr) in enumerate(campos):

            tk.Label(
                frame_form,
                text=lbl,
                bg=COLOR_CARD,
                fg=COLOR_TEXT
            ).grid(
                row=i,
                column=0,
                sticky="w",
                pady=6
            )

            entry = tk.Entry(
                frame_form,
                bg=COLOR_INPUT_BG,
                fg=COLOR_TEXT
            )

            entry.grid(
                row=i,
                column=1,
                sticky="ew",
                pady=6,
                padx=(10, 0)
            )

            setattr(self, attr, entry)

        frame_form.columnconfigure(
            1,
            weight=1
        )

        tk.Button(
            self,
            text="💾 Guardar Proveedor",
            bg=COLOR_ACCENT,
            fg="#000",
            font=("Segoe UI", 10, "bold"),
            command=self.guardar,
        ).pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

    def guardar(self):

        nombre = self.txt_nombre.get().strip()

        if not nombre:
            messagebox.showwarning(
                "Atención",
                "El nombre del proveedor es obligatorio."
            )
            return

        prov = Proveedor(
            nombre=nombre,
            nit_cedula=self.txt_nit.get().strip(),
            telefono=self.txt_telefono.get().strip(),
            email=self.txt_email.get().strip(),
            direccion=self.txt_direccion.get().strip(),
            monto_deuda=0.0,
            abonos=0.0,
        )

        if self.service_proveedor.crear_proveedor(prov):

            messagebox.showinfo(
                "Éxito",
                f"Proveedor '{nombre}' registrado correctamente."
            )

            self.al_guardar_callback()
            self.destroy()

        else:

            messagebox.showerror(
                "Error",
                "No se pudo registrar el proveedor. "
                "Verifica que el NIT/Cédula no esté repetido."
            )


class VentanaProveedores(tk.Toplevel):
    """Ventana principal para gestión de facturas y proveedores."""

    def __init__(
        self,
        parent,
        service_contabilidad=None
    ):
        super().__init__(parent)

        self.title("Gestión de Facturas y Proveedores")
        self.geometry("1250x740")
        self.configure(bg=COLOR_BG)

        self.service_contabilidad = service_contabilidad

        db = None

        if service_contabilidad:

            if hasattr(service_contabilidad, "db"):
                db = service_contabilidad.db

            elif hasattr(
                service_contabilidad,
                "database"
            ):
                db = service_contabilidad.database

            elif hasattr(
                service_contabilidad,
                "mongo_db"
            ):
                db = service_contabilidad.mongo_db

            else:
                db = service_contabilidad

        if db is None:

            try:
                from app import db as global_db
                db = global_db

            except Exception:
                pass

        self.service_proveedor = ProveedorService(db)

        self.id_seleccionado = None
        self.nombre_seleccionado = ""
        self.nit_seleccionado = ""

        self.factura_seleccionada = None

        self.modo_vista = "facturas"

        self.solo_deudores_activo = False

        self.mapa_filas_ids = {}

        self._build_ui()

        self.limpiar_fechas_iniciales()

        self.cargar_tabla_facturas()

    
    # UTILIDADES
    

    def _numero(self, valor, defecto=0.0):

        try:
            if valor is None or valor == "":
                return defecto

            return float(valor)

        except (ValueError, TypeError):
            return defecto

    def _normalizar_factura(self, factura):

        if factura is None:
            return ""

        return str(factura).strip().lower()

    def _obtener_proveedor_seleccionado(self):

        if not self.id_seleccionado:
            return None

        proveedores = self.service_proveedor.obtener_todos()

        return next(
            (
                p
                for p in proveedores
                if str(p.get("_id"))
                == str(self.id_seleccionado)
            ),
            None
        )

    def _obtener_pedido_seleccionado(
        self,
        proveedor=None
    ):

        if proveedor is None:
            proveedor = self._obtener_proveedor_seleccionado()

        if not proveedor:
            return None

        pedidos = proveedor.get(
            "historial_pedidos",
            []
        ) or []

        return next(
            (
                ped
                for ped in pedidos
                if self._normalizar_factura(
                    ped.get("factura")
                )
                == self._normalizar_factura(
                    self.factura_seleccionada
                )
            ),
            None
        )

    def _obtener_abonos_factura(
        self,
        proveedor,
        factura
    ):

        if not proveedor:
            return []

        abonos = proveedor.get(
            "historial_abonos",
            []
        ) or []

        referencia = self._normalizar_factura(
            factura
        )

        return [
            abono
            for abono in abonos
            if self._normalizar_factura(
                abono.get("factura")
            ) == referencia
        ]

    def _calcular_factura(
        self,
        proveedor,
        factura
    ):

        pedido = self._obtener_pedido_seleccionado(
            proveedor
        )

        if not pedido:
            return {
                "monto": 0.0,
                "abonado": 0.0,
                "saldo": 0.0,
                "estado": "SIN FACTURA"
            }

        monto = self._numero(
            pedido.get("monto", 0)
        )

        abonos = self._obtener_abonos_factura(
            proveedor,
            factura
        )

        abonado = sum(
            self._numero(
                abono.get("monto", 0)
            )
            for abono in abonos
        )

        saldo = max(
            0.0,
            monto - abonado
        )

        estado = (
            "PAGADA"
            if saldo <= 0
            else "PENDIENTE"
        )

        return {
            "monto": monto,
            "abonado": abonado,
            "saldo": saldo,
            "estado": estado
        }


    # FECHAS
    

    def limpiar_fechas_iniciales(self):

        if DateEntry:

            try:
                self.cal_inicio.delete(
                    0,
                    "end"
                )

                self.cal_fin.delete(
                    0,
                    "end"
                )

            except Exception:
                pass

    # CONSTRUCCIÓN UI
  

    def _build_ui(self):

        frame_header = tk.Frame(
            self,
            bg=COLOR_BG
        )

        frame_header.pack(
            fill="x",
            padx=20,
            pady=(15, 5)
        )

        self.lbl_titulo = tk.Label(
            frame_header,
            text="🚚 Panel de Facturas de Proveedores",
            bg=COLOR_BG,
            fg=COLOR_ACCENT,
            font=("Segoe UI", 14, "bold"),
        )

        self.lbl_titulo.pack(
            side="left"
        )

        self.btn_volver = tk.Button(
            frame_header,
            text="⬅️ Volver a Lista de Facturas",
            bg="#374151",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=self.ver_lista_facturas,
        )

        
        # BUSCADOR
      

        self.frame_search = tk.Frame(
            self,
            bg=COLOR_CARD,
            padx=12,
            pady=10
        )

        self.frame_search.pack(
            fill="x",
            padx=20,
            pady=10
        )

        tk.Label(
            self.frame_search,
            text="🔍 Proveedor:",
            bg=COLOR_CARD,
            fg=COLOR_TEXT
        ).pack(
            side="left",
            padx=(0, 3)
        )

        self.combo_buscar = ttk.Combobox(
            self.frame_search,
            state="normal",
            width=20,
            font=("Segoe UI", 9)
        )

        self.combo_buscar.pack(
            side="left",
            padx=3
        )

        tk.Button(
            self.frame_search,
            text="Filtrar Proveedor",
            bg="#374151",
            fg="white",
            font=("Segoe UI", 8),
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.cargar_tabla_facturas,
        ).pack(
            side="left",
            padx=2
        )

        tk.Label(
            self.frame_search,
            text="Desde:",
            bg=COLOR_CARD,
            fg=COLOR_TEXT
        ).pack(
            side="left",
            padx=(10, 2)
        )

        if DateEntry:

            self.cal_inicio = DateEntry(
                self.frame_search,
                width=10,
                background="darkblue",
                foreground="white",
                borderwidth=2,
                date_pattern="yyyy-mm-dd",
            )

            self.cal_inicio.pack(
                side="left",
                padx=2
            )

        else:

            self.cal_inicio = tk.Entry(
                self.frame_search,
                bg=COLOR_INPUT_BG,
                fg=COLOR_TEXT,
                width=10
            )

            self.cal_inicio.pack(
                side="left",
                padx=2
            )

        tk.Label(
            self.frame_search,
            text="Hasta:",
            bg=COLOR_CARD,
            fg=COLOR_TEXT
        ).pack(
            side="left",
            padx=(8, 2)
        )

        if DateEntry:

            self.cal_fin = DateEntry(
                self.frame_search,
                width=10,
                background="darkblue",
                foreground="white",
                borderwidth=2,
                date_pattern="yyyy-mm-dd",
            )

            self.cal_fin.pack(
                side="left",
                padx=2
            )

        else:

            self.cal_fin = tk.Entry(
                self.frame_search,
                bg=COLOR_INPUT_BG,
                fg=COLOR_TEXT,
                width=10
            )

            self.cal_fin.pack(
                side="left",
                padx=2
            )

        tk.Button(
            self.frame_search,
            text="📅 Filtrar Fechas",
            bg=COLOR_BTN_ROJO,
            fg="white",
            activebackground=COLOR_BTN_ROJO_HOVER,
            activeforeground="white",
            font=("Segoe UI", 8, "bold"),
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.cargar_tabla_facturas,
        ).pack(
            side="left",
            padx=6
        )

        tk.Button(
            self.frame_search,
            text="🔄 Ver Todo / Limpiar",
            bg="#374151",
            fg="white",
            font=("Segoe UI", 8, "bold"),
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.limpiar_filtros,
        ).pack(
            side="left",
            padx=2
        )

        self.btn_deudores = tk.Button(
            self.frame_search,
            text="⚠️ Solo con Deuda Pendiente",
            bg="#D97706",
            fg="white",
            font=("Segoe UI", 8, "bold"),
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.toggle_solo_deudores,
        )

        self.btn_deudores.pack(
            side="left",
            padx=6
        )

        
        # INFORMACIÓN
    
        frame_info = tk.LabelFrame(
            self,
            text=" Información del Registro ",
            bg=COLOR_CARD,
            fg=COLOR_ACCENT,
            padx=15,
            pady=10,
        )

        frame_info.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.lbl_detalles = tk.Label(
            frame_info,
            text=(
                "💡 Selecciona una factura de la lista para "
                "gestionar sus abonos específicos o haz doble "
                "clic para ver el detalle."
            ),
            bg=COLOR_CARD,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9),
            justify="left",
        )

        self.lbl_detalles.pack(
            anchor="w"
        )


        # BOTONES
        
        frame_actions = tk.Frame(
            self,
            bg=COLOR_BG
        )

        frame_actions.pack(
            fill="x",
            padx=20,
            pady=5
        )

        tk.Button(
            frame_actions,
            text="📦 Nuevo Pedido / Factura",
            bg="#8B5CF6",
            fg="#FFF",
            font=("Segoe UI", 9, "bold"),
            command=self.registrar_nuevo_pedido,
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            frame_actions,
            text="💵 Registrar Abono a Factura",
            bg=COLOR_SUCCESS,
            fg="#FFF",
            font=("Segoe UI", 9, "bold"),
            command=self.registrar_abono,
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            frame_actions,
            text="✏️ Editar Abono",
            bg="#3B82F6",
            fg="#FFF",
            font=("Segoe UI", 9, "bold"),
            command=self.seleccionar_y_editar_abono,
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            frame_actions,
            text="🗑️ Eliminar Abono",
            bg="#D97706",
            fg="#FFF",
            font=("Segoe UI", 9, "bold"),
            command=self.seleccionar_y_eliminar_abono,
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            frame_actions,
            text="🗑️ Eliminar Proveedor",
            bg=COLOR_DANGER,
            fg="#FFF",
            font=("Segoe UI", 9, "bold"),
            command=self.eliminar_proveedor,
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            frame_actions,
            text="➕ Agregar Proveedor Nuevo",
            bg=COLOR_ACCENT,
            fg="#000",
            font=("Segoe UI", 9, "bold"),
            command=self.abrir_ventana_crear,
        ).pack(
            side="left",
            padx=5
        )


        # TABLA
     

        self.tree_frame = tk.Frame(
            self,
            bg=COLOR_BG
        )

        self.tree_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(10, 20)
        )

        # IMPORTANTE:
        # La factura queda como PRIMERA columna.
        self.cols_facturas = (
            "N° Factura / Ref",
            "Fecha Pedido",
            "Proveedor",
            "Monto Factura",
            "Abonado",
            "Saldo Pendiente",
            "Estado",
        )

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=self.cols_facturas,
            show="headings"
        )

        self._configurar_columnas_facturas()

        self.tree.pack(
            fill="both",
            expand=True
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.al_seleccionar_fila
        )

        self.tree.bind(
            "<Double-1>",
            lambda e:
            self.ver_detalle_proveedor_seleccionado()
        )

    
    # COLUMNAS
   

    def _configurar_columnas_facturas(self):

        self.tree["columns"] = self.cols_facturas

        for col in self.cols_facturas:

            self.tree.heading(
                col,
                text=col
            )

            self.tree.column(
                col,
                anchor="center"
            )

        self.tree.column(
            "N° Factura / Ref",
            width=150,
            minwidth=120
        )

        self.tree.column(
            "Fecha Pedido",
            width=125,
            minwidth=110
        )

        self.tree.column(
            "Proveedor",
            width=220,
            minwidth=160
        )

        self.tree.column(
            "Monto Factura",
            width=130,
            minwidth=110
        )

        self.tree.column(
            "Abonado",
            width=120,
            minwidth=100
        )

        self.tree.column(
            "Saldo Pendiente",
            width=140,
            minwidth=120
        )

        self.tree.column(
            "Estado",
            width=100,
            minwidth=90
        )

    def _configurar_columnas_historial(self):

        cols_hist = (
            "Fecha",
            "Tipo",
            "N° Factura / Referencia",
            "Monto",
            "Detalle / Observación"
        )

        self.tree["columns"] = cols_hist

        for col in cols_hist:

            self.tree.heading(
                col,
                text=col
            )

            self.tree.column(
                col,
                anchor="center"
            )

        self.tree.column(
            "Fecha",
            width=130
        )

        self.tree.column(
            "Tipo",
            width=150
        )

        self.tree.column(
            "N° Factura / Referencia",
            width=180
        )

        self.tree.column(
            "Monto",
            width=140
        )

        self.tree.column(
            "Detalle / Observación",
            width=300,
            anchor="w"
        )

   
    # PROVEEDOR NUEVO
    

    def abrir_ventana_crear(self):

        VentanaCrearProveedor(
            self,
            self.service_proveedor,
            self.cargar_tabla_facturas
        )

    
    # FILTROS
  

    def limpiar_filtros(self):

        self.combo_buscar.set("")

        try:
            self.cal_inicio.delete(
                0,
                "end"
            )
        except Exception:
            pass

        try:
            self.cal_fin.delete(
                0,
                "end"
            )
        except Exception:
            pass

        self.solo_deudores_activo = False

        self.btn_deudores.config(
            bg="#D97706",
            text="⚠️ Solo con Deuda Pendiente"
        )

        self.cargar_tabla_facturas()

    def toggle_solo_deudores(self):

        self.solo_deudores_activo = (
            not self.solo_deudores_activo
        )

        if self.solo_deudores_activo:

            self.btn_deudores.config(
                bg="#059669",
                text="✅ Mostrando solo pendientes"
            )

        else:

            self.btn_deudores.config(
                bg="#D97706",
                text="⚠️ Solo con Deuda Pendiente"
            )

        if self.modo_vista == "facturas":
            self.cargar_tabla_facturas()

    
    # CARGAR TABLA
    
    def cargar_tabla_facturas(self):

        self.modo_vista = "facturas"

        self.btn_volver.pack_forget()

        self.lbl_titulo.config(
            text="🚚 Panel de Facturas de Proveedores"
        )

        self.frame_search.pack(
            before=self.tree_frame,
            fill="x",
            padx=20,
            pady=10
        )

        for row in self.tree.get_children():
            self.tree.delete(row)

        self._configurar_columnas_facturas()

        try:

            proveedores = (
                self.service_proveedor.obtener_todos()
            )

        except Exception:

            proveedores = []

        lista_nombres = [
            p.get("nombre")
            for p in proveedores
            if p.get("nombre")
        ]

        self.combo_buscar["values"] = lista_nombres

        busqueda_texto = (
            self.combo_buscar.get()
            .strip()
            .lower()
        )

        f_inicio = None
        f_fin = None

        try:

            val_inicio_str = (
                self.cal_inicio.get()
                .strip()
            )

            if val_inicio_str:
                f_inicio = val_inicio_str

        except Exception:
            pass

        try:

            val_fin_str = (
                self.cal_fin.get()
                .strip()
            )

            if val_fin_str:
                f_fin = val_fin_str

        except Exception:
            pass

        self.mapa_filas_ids = {}


        # RECORRER PROVEEDORES
    

        for proveedor in proveedores:

            nombre_prov = proveedor.get(
                "nombre",
                ""
            )

            if (
                busqueda_texto
                and busqueda_texto
                not in nombre_prov.lower()
            ):
                continue

            pedidos = proveedor.get(
                "historial_pedidos",
                []
            ) or []

            abonos_totales = proveedor.get(
                "historial_abonos",
                []
            ) or []

            # COMPATIBILIDAD CON DATOS ANTIGUOS
        
            if (
                not pedidos
                and self._numero(
                    proveedor.get("monto_deuda", 0)
                ) > 0
            ):

                pedidos = [
                    {
                        "_id": "inicial",
                        "fecha": proveedor.get(
                            "fecha_creacion",
                            datetime.now().strftime(
                                "%Y-%m-%d"
                            )
                        ),
                        "monto": self._numero(
                            proveedor.get(
                                "monto_deuda",
                                0
                            )
                        ),
                        "factura": (
                            "Factura Inicial / Deuda"
                        )
                    }
                ]

            
            # CADA FACTURA ES UNA FILA
          

            for pedido in pedidos:

                num_fact = pedido.get(
                    "factura",
                    "Sin número"
                )

                fecha_ped = pedido.get(
                    "fecha",
                    "-"
                )

                monto_fact = self._numero(
                    pedido.get("monto", 0)
                )

                
                # FILTRO FECHAS
             
                fecha_comparable = str(
                    fecha_ped
                ).strip()

                if (
                    f_inicio
                    and fecha_comparable
                    and fecha_comparable[:10]
                    < f_inicio
                ):
                    continue

                if (
                    f_fin
                    and fecha_comparable
                    and fecha_comparable[:10]
                    > f_fin
                ):
                    continue

             
                # ABONOS DE ESTA FACTURA
             

                referencia_factura = (
                    self._normalizar_factura(
                        num_fact
                    )
                )

                abonos_esta_factura = [
                    ab
                    for ab in abonos_totales
                    if self._normalizar_factura(
                        ab.get("factura")
                    )
                    == referencia_factura
                ]

                abonado = sum(
                    self._numero(
                        ab.get("monto", 0)
                    )
                    for ab in abonos_esta_factura
                )

              
                # COMPATIBILIDAD CON UNA ÚNICA FACTURA ANTIGUA
               
                if (
                    abonado == 0
                    and len(pedidos) == 1
                    and abonos_totales
                ):

                    abonos_sin_referencia = [
                        ab
                        for ab in abonos_totales
                        if self._normalizar_factura(
                            ab.get("factura")
                        )
                        in (
                            "",
                            "sin referencia",
                            "abono inicial"
                        )
                    ]

                    if abonos_sin_referencia:

                        abonado = sum(
                            self._numero(
                                ab.get("monto", 0)
                            )
                            for ab
                            in abonos_sin_referencia
                        )

                    elif not abonos_esta_factura:

                        # Compatibilidad con datos muy antiguos
                        abonado = self._numero(
                            proveedor.get(
                                "abonos",
                                0
                            )
                        )

                saldo_pendiente = max(
                    0.0,
                    monto_fact - abonado
                )

                estado = (
                    "PAGADA"
                    if saldo_pendiente <= 0
                    else "PENDIENTE"
                )

                if (
                    self.solo_deudores_activo
                    and saldo_pendiente <= 0
                ):
                    continue

              
                # FACTURA PRIMERO
            

                item_id = self.tree.insert(
                    "",
                    "end",
                    values=(
                        num_fact,
                        fecha_ped,
                        nombre_prov,
                        f"${monto_fact:,.2f}",
                        f"${abonado:,.2f}",
                        f"${saldo_pendiente:,.2f}",
                        estado,
                    ),
                )

                self.mapa_filas_ids[item_id] = {
                    "id_proveedor": proveedor.get(
                        "_id"
                    ),
                    "factura": num_fact
                }

        self.id_seleccionado = None
        self.factura_seleccionada = None

        self.lbl_detalles.config(
            text=(
                "💡 Selecciona una factura de la lista "
                "para gestionar sus abonos específicos "
                "o haz doble clic para ver el detalle."
            ),
            fg=COLOR_TEXT
        )

  
    # SELECCIONAR FILA


    def al_seleccionar_fila(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        item_id = selected[0]

        if self.modo_vista != "facturas":
            return

        data_dict = (
            self.mapa_filas_ids.get(item_id)
        )

        if not data_dict:
            return

        self.id_seleccionado = (
            data_dict.get("id_proveedor")
        )

        self.factura_seleccionada = (
            data_dict.get("factura")
        )

        proveedor = (
            self._obtener_proveedor_seleccionado()
        )

        if not proveedor:
            return

        self.nombre_seleccionado = proveedor.get(
            "nombre",
            ""
        )

        self.nit_seleccionado = proveedor.get(
            "nit_cedula",
            "N/A"
        )

        datos = self._calcular_factura(
            proveedor,
            self.factura_seleccionada
        )

        info = (
            f"👤 Proveedor: "
            f"{self.nombre_seleccionado}"
            f"    |    "
            f"📄 Factura: "
            f"{self.factura_seleccionada}\n"
            f"💰 Monto Factura: "
            f"${datos['monto']:,.2f}"
            f"    |    "
            f"💵 Abonado: "
            f"${datos['abonado']:,.2f}"
            f"    |    "
            f"⚠️ Saldo Pendiente: "
            f"${datos['saldo']:,.2f}\n"
            f"👉 Usa 'Registrar Abono', "
            f"'Editar Abono' o 'Eliminar Abono' "
            f"para trabajar sobre esta factura."
        )

        self.lbl_detalles.config(
            text=info,
            fg=COLOR_TEXT
        )

  
    # DETALLE DEL PROVEEDOR
  

    def ver_detalle_proveedor_seleccionado(self):

        if not self.id_seleccionado:
            return

        proveedor = (
            self._obtener_proveedor_seleccionado()
        )

        if not proveedor:
            return

        self.modo_vista = "detalles_proveedor"

        self.frame_search.pack_forget()

        self.btn_volver.pack(
            side="right"
        )

        self.lbl_titulo.config(
            text=(
                f"📋 Historial: "
                f"{proveedor.get('nombre', '')}"
            )
        )

        for row in self.tree.get_children():
            self.tree.delete(row)

        self._configurar_columnas_historial()

        pedidos = proveedor.get(
            "historial_pedidos",
            []
        ) or []

        abonos = proveedor.get(
            "historial_abonos",
            []
        ) or []

        if (
            not pedidos
            and self._numero(
                proveedor.get("monto_deuda", 0)
            ) > 0
        ):

            pedidos = [
                {
                    "_id": "inicial",
                    "fecha": proveedor.get(
                        "fecha_creacion",
                        datetime.now().strftime(
                            "%Y-%m-%d"
                        )
                    ),
                    "monto": self._numero(
                        proveedor.get(
                            "monto_deuda",
                            0
                        )
                    ),
                    "factura": (
                        "Factura Inicial / Deuda"
                    )
                }
            ]

        # Facturas
        for ped in pedidos:

            self.tree.insert(
                "",
                "end",
                values=(
                    ped.get(
                        "fecha",
                        "-"
                    ),
                    "📦 PEDIDO / FACTURA",
                    ped.get(
                        "factura",
                        "Sin número"
                    ),
                    f"${self._numero(ped.get('monto', 0)):,.2f}",
                    "Cargo a cuenta por pagar"
                )
            )

        # Abonos
        for ab in abonos:

            self.tree.insert(
                "",
                "end",
                values=(
                    ab.get(
                        "fecha",
                        "-"
                    ),
                    "💵 ABONO / PAGO",
                    ab.get(
                        "factura",
                        "Sin Referencia"
                    ),
                    f"${self._numero(ab.get('monto', 0)):,.2f}",
                    "Abono registrado a la factura"
                )
            )

        self.lbl_detalles.config(
            text=(
                f"📊 Mostrando facturas y abonos de "
                f"{proveedor.get('nombre', '')}. "
                f"Usa el botón 'Volver' para regresar "
                f"a la tabla general."
            ),
            fg=COLOR_ACCENT
        )

    def ver_lista_facturas(self):

        self.cargar_tabla_facturas()


    # NUEVO PEDIDO
  

    def registrar_nuevo_pedido(self):

        ventana_pedido = tk.Toplevel(
            self
        )

        ventana_pedido.title(
            "Registrar Nuevo Pedido / Factura"
        )

        ventana_pedido.geometry(
            "400x420"
        )

        ventana_pedido.configure(
            bg=COLOR_BG
        )

        ventana_pedido.transient(self)
        ventana_pedido.grab_set()

        tk.Label(
            ventana_pedido,
            text="Seleccionar Proveedor *:",
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 0)
        )

        proveedores = (
            self.service_proveedor.obtener_todos()
        )

        nombres_proveedores = [
            p.get("nombre")
            for p in proveedores
        ]

        combo_proveedor = ttk.Combobox(
            ventana_pedido,
            values=nombres_proveedores,
            state="readonly",
            width=36,
            font=("Segoe UI", 10)
        )

        combo_proveedor.pack(
            padx=20,
            pady=5
        )

        if self.id_seleccionado:

            for idx, p in enumerate(proveedores):

                if (
                    str(p.get("_id"))
                    == str(self.id_seleccionado)
                ):

                    combo_proveedor.current(idx)
                    break

        elif nombres_proveedores:

            combo_proveedor.current(0)

        tk.Label(
            ventana_pedido,
            text="N° de Factura / Código emitido *:",
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 0)
        )

        txt_factura = tk.Entry(
            ventana_pedido,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            width=38,
            font=("Segoe UI", 10)
        )

        txt_factura.pack(
            padx=20,
            pady=2
        )

        tk.Label(
            ventana_pedido,
            text="Monto del Pedido ($) *:",
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 0)
        )

        txt_monto_pedido = tk.Entry(
            ventana_pedido,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            width=38,
            font=("Segoe UI", 10)
        )

        txt_monto_pedido.pack(
            padx=20,
            pady=2
        )

        tk.Label(
            ventana_pedido,
            text=(
                "Abono Inicial para este Pedido ($) "
                "[Opcional]:"
            ),
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 0)
        )

        txt_abono_pedido = tk.Entry(
            ventana_pedido,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            width=38,
            font=("Segoe UI", 10)
        )

        txt_abono_pedido.insert(
            0,
            "0"
        )

        txt_abono_pedido.pack(
            padx=20,
            pady=2
        )

        def confirmar_pedido():

            seleccion_idx = (
                combo_proveedor.current()
            )

            if (
                seleccion_idx < 0
                or seleccion_idx >= len(proveedores)
            ):

                messagebox.showwarning(
                    "Atención",
                    "Selecciona un proveedor válido del listado."
                )

                return

            prov_seleccionado = (
                proveedores[seleccion_idx]
            )

            id_prov = (
                prov_seleccionado.get("_id")
            )

            try:

                monto = float(
                    txt_monto_pedido.get().strip()
                )

                monto_abono = float(
                    txt_abono_pedido.get().strip()
                    or 0
                )

                nro_factura = (
                    txt_factura.get().strip()
                )

                if monto <= 0:

                    messagebox.showwarning(
                        "Atención",
                        "El monto del pedido debe ser mayor a cero."
                    )

                    return

                if not nro_factura:

                    messagebox.showwarning(
                        "Atención",
                        "El número de factura es obligatorio."
                    )

                    return

                if monto_abono < 0:

                    messagebox.showwarning(
                        "Atención",
                        "El abono no puede ser negativo."
                    )

                    return

                if monto_abono > monto:

                    messagebox.showwarning(
                        "Atención",
                        "El abono inicial no puede ser "
                        "mayor que el monto de la factura."
                    )

                    return

                # Registrar factura
                registrado = (
                    self.service_proveedor.registrar_pedido(
                        id_prov,
                        monto,
                        nro_factura
                    )
                )

                if not registrado:

                    messagebox.showerror(
                        "Error",
                        "No se pudo registrar el pedido. "
                        "Verifica que el número de factura "
                        "no esté repetido para ese proveedor."
                    )

                    return

                # Registrar abono inicial
                if monto_abono > 0:

                    abono_ok = (
                        self.service_proveedor.registrar_abono(
                            id_prov,
                            monto_abono,
                            nro_factura
                        )
                    )

                    if not abono_ok:

                        messagebox.showwarning(
                            "Advertencia",
                            "La factura fue registrada, "
                            "pero el abono inicial no pudo "
                            "registrarse."
                        )

                    elif (
                        self.service_contabilidad
                        and hasattr(
                            self.service_contabilidad,
                            "registrar_movimiento"
                        )
                    ):

                        concepto_texto = (
                            "Abono inicial a pedido - "
                            f"Factura: {nro_factura}"
                        )

                        self.service_contabilidad.registrar_movimiento(
                            tipo="pago_proveedor",
                            concepto=concepto_texto,
                            monto=monto_abono,
                        )

                messagebox.showinfo(
                    "Éxito",
                    f"Factura '{nro_factura}' "
                    "registrada correctamente."
                )

                ventana_pedido.destroy()

                if (
                    self.modo_vista
                    == "detalles_proveedor"
                    and str(self.id_seleccionado)
                    == str(id_prov)
                ):

                    self.ver_detalle_proveedor_seleccionado()

                else:

                    self.cargar_tabla_facturas()

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Ingresa montos numéricos válidos."
                )

        tk.Button(
            ventana_pedido,
            text="Guardar Pedido y Abono",
            bg="#8B5CF6",
            fg="#FFF",
            font=("Segoe UI", 9, "bold"),
            command=confirmar_pedido,
        ).pack(
            fill="x",
            padx=20,
            pady=15
        )

   
    # REGISTRAR ABONO
   

    def registrar_abono(self):

        if (
            not self.id_seleccionado
            or not self.factura_seleccionada
        ):

            messagebox.showwarning(
                "Atención",
                "Selecciona una factura específica "
                "de la tabla para registrar un abono."
            )

            return

        proveedor = (
            self._obtener_proveedor_seleccionado()
        )

        if not proveedor:
            return

        datos_factura = (
            self._calcular_factura(
                proveedor,
                self.factura_seleccionada
            )
        )

        if datos_factura["saldo"] <= 0:

            messagebox.showinfo(
                "Factura pagada",
                "Esta factura ya está completamente pagada."
            )

            return

        ventana_abono = tk.Toplevel(
            self
        )

        ventana_abono.title(
            "Registrar Abono a Factura"
        )

        ventana_abono.geometry(
            "380x300"
        )

        ventana_abono.configure(
            bg=COLOR_BG
        )

        ventana_abono.transient(self)
        ventana_abono.grab_set()

        tk.Label(
            ventana_abono,
            text=(
                f"Proveedor: "
                f"{self.nombre_seleccionado}\n"
                f"Factura: "
                f"{self.factura_seleccionada}\n"
                f"Saldo disponible: "
                f"${datos_factura['saldo']:,.2f}"
            ),
            bg=COLOR_CARD,
            fg=COLOR_ACCENT,
            font=("Segoe UI", 9, "bold"),
            justify="center",
            padx=10,
            pady=8
        ).pack(
            fill="x",
            padx=15,
            pady=(15, 5)
        )

        tk.Label(
            ventana_abono,
            text="N° de Factura / Referencia:",
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 0)
        )

        txt_factura = tk.Entry(
            ventana_abono,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            width=32,
            font=("Segoe UI", 10)
        )

        txt_factura.insert(
            0,
            self.factura_seleccionada
        )

        txt_factura.config(
            state="readonly"
        )

        txt_factura.pack(
            padx=20,
            pady=2
        )

        tk.Label(
            ventana_abono,
            text="Monto del Abono ($):",
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 0)
        )

        txt_monto_abono = tk.Entry(
            ventana_abono,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            width=32,
            font=("Segoe UI", 10)
        )

        txt_monto_abono.pack(
            padx=20,
            pady=2
        )

        txt_monto_abono.focus()

        def confirmar():

            try:

                monto = float(
                    txt_monto_abono.get().strip()
                )

                if monto <= 0:

                    messagebox.showwarning(
                        "Atención",
                        "El monto debe ser mayor a cero."
                    )

                    return

                if monto > datos_factura["saldo"]:

                    messagebox.showwarning(
                        "Atención",
                        (
                            "El abono no puede superar "
                            f"el saldo pendiente de "
                            f"${datos_factura['saldo']:,.2f}."
                        )
                    )

                    return

                nro_factura = (
                    self.factura_seleccionada
                )

                resultado = (
                    self.service_proveedor.registrar_abono(
                        self.id_seleccionado,
                        monto,
                        nro_factura
                    )
                )

                if not resultado:

                    messagebox.showerror(
                        "Error",
                        "No se pudo registrar el abono."
                    )

                    return

                if (
                    self.service_contabilidad
                    and hasattr(
                        self.service_contabilidad,
                        "registrar_movimiento"
                    )
                ):

                    concepto_texto = (
                        "Abono a proveedor - "
                        f"Factura: {nro_factura}"
                    )

                    self.service_contabilidad.registrar_movimiento(
                        tipo="pago_proveedor",
                        concepto=concepto_texto,
                        monto=monto,
                    )

                messagebox.showinfo(
                    "Éxito",
                    "Abono guardado correctamente."
                )

                ventana_abono.destroy()

                self.cargar_tabla_facturas()

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Ingresa un monto numérico válido."
                )

        tk.Button(
            ventana_abono,
            text="Guardar Abono",
            bg=COLOR_SUCCESS,
            fg="#FFF",
            font=("Segoe UI", 9, "bold"),
            command=confirmar,
        ).pack(
            fill="x",
            padx=20,
            pady=15
        )

  
    # EDITAR ABONO
 

    def seleccionar_y_editar_abono(self):

        if (
            not self.id_seleccionado
            or not self.factura_seleccionada
        ):

            messagebox.showwarning(
                "Atención",
                "Selecciona una factura primero."
            )

            return

        proveedor = (
            self._obtener_proveedor_seleccionado()
        )

        if not proveedor:
            return

    #abonos en factura puntual
        abonos = (
            self._obtener_abonos_factura(
                proveedor,
                self.factura_seleccionada
            )
        )

        if not abonos:

            messagebox.showinfo(
                "Información",
                (
                    "La factura seleccionada "
                    "no tiene abonos registrados."
                )
            )

            return

        self._ventana_seleccionar_abono_editar(
            abonos
        )

    def _ventana_seleccionar_abono_editar(
        self,
        abonos
    ):

        ven_lista = tk.Toplevel(
            self
        )

        ven_lista.title(
            "Seleccionar Abono a Editar"
        )

        ven_lista.geometry(
            "470x340"
        )

        ven_lista.configure(
            bg=COLOR_BG
        )

        ven_lista.transient(self)
        ven_lista.grab_set()

        tk.Label(
            ven_lista,
            text=(
                "Selecciona el abono de la factura "
                f"'{self.factura_seleccionada}' "
                "que deseas editar:"
            ),
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            font=("Segoe UI", 10, "bold"),
            wraplength=420,
            justify="center"
        ).pack(
            pady=10
        )

        cols = (
            "Fecha",
            "Factura",
            "Monto"
        )

        tree_abonos = ttk.Treeview(
            ven_lista,
            columns=cols,
            show="headings",
            height=7
        )

        for col in cols:

            tree_abonos.heading(
                col,
                text=col
            )

            tree_abonos.column(
                col,
                anchor="center",
                width=140
            )

        tree_abonos.pack(
            padx=10,
            pady=5,
            fill="both",
            expand=True
        )

        for idx, abono in enumerate(abonos):

            tree_abonos.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    abono.get(
                        "fecha",
                        "-"
                    ),
                    abono.get(
                        "factura",
                        "-"
                    ),
                    f"${self._numero(abono.get('monto', 0)):,.2f}"
                )
            )

        def editar_seleccionado():

            selected = (
                tree_abonos.selection()
            )

            if not selected:

                messagebox.showwarning(
                    "Atención",
                    "Selecciona un abono de la lista."
                )

                return

            item_idx = int(
                selected[0]
            )

            abono_seleccionado = (
                abonos[item_idx]
            )

            ven_lista.destroy()

            self._ventana_form_editar_abono(
                abono_seleccionado
            )

        tk.Button(
            ven_lista,
            text="✏️ Editar Seleccionado",
            bg="#3B82F6",
            fg="#FFF",
            font=("Segoe UI", 9, "bold"),
            command=editar_seleccionado
        ).pack(
            fill="x",
            padx=20,
            pady=10
        )

    def _ventana_form_editar_abono(
        self,
        abono
    ):

        ven_edit = tk.Toplevel(
            self
        )

        ven_edit.title(
            "Editar Abono"
        )

        ven_edit.geometry(
            "380x300"
        )

        ven_edit.configure(
            bg=COLOR_BG
        )

        ven_edit.transient(self)
        ven_edit.grab_set()

        factura_original = abono.get(
            "factura",
            "Sin Referencia"
        )

        tk.Label(
            ven_edit,
            text="N° de Factura / Referencia:",
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 2)
        )

        txt_factura = tk.Entry(
            ven_edit,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            width=32,
            font=("Segoe UI", 10)
        )

        txt_factura.insert(
            0,
            factura_original
        )

        txt_factura.pack(
            padx=20,
            pady=2
        )

        tk.Label(
            ven_edit,
            text="Nuevo Monto del Abono ($):",
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=20,
            pady=(10, 2)
        )

        txt_monto = tk.Entry(
            ven_edit,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            width=32,
            font=("Segoe UI", 10)
        )

        txt_monto.insert(
            0,
            str(
                self._numero(
                    abono.get(
                        "monto",
                        0
                    )
                )
            )
        )

        txt_monto.pack(
            padx=20,
            pady=2
        )

        def guardar_cambios():

            try:

                nuevo_monto = float(
                    txt_monto.get().strip()
                )

                nueva_factura = (
                    txt_factura.get().strip()
                )

                if nuevo_monto <= 0:

                    messagebox.showwarning(
                        "Atención",
                        "El monto debe ser mayor a cero."
                    )

                    return

                if not nueva_factura:

                    nueva_factura = (
                        "Sin Referencia"
                    )

                resultado = (
                    self.service_proveedor.actualizar_abono(
                        self.id_seleccionado,
                        abono.get("_id"),
                        nuevo_monto,
                        nueva_factura
                    )
                )

                if resultado:

                    messagebox.showinfo(
                        "Éxito",
                        "Abono actualizado correctamente."
                    )

                    ven_edit.destroy()

                    self.cargar_tabla_facturas()

                else:

                    messagebox.showerror(
                        "Error",
                        (
                            "No se pudo actualizar el abono. "
                            "Verifica que el monto no supere "
                            "el saldo disponible de la factura."
                        )
                    )

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Ingresa un monto numérico válido."
                )

        tk.Button(
            ven_edit,
            text="💾 Guardar Cambios",
            bg=COLOR_SUCCESS,
            fg="#FFF",
            font=("Segoe UI", 9, "bold"),
            command=guardar_cambios
        ).pack(
            fill="x",
            padx=20,
            pady=20
        )

   
    # ELIMINAR ABONO
   

    def seleccionar_y_eliminar_abono(self):

        if (
            not self.id_seleccionado
            or not self.factura_seleccionada
        ):

            messagebox.showwarning(
                "Atención",
                "Selecciona una factura primero."
            )

            return

        proveedor = (
            self._obtener_proveedor_seleccionado()
        )

        if not proveedor:
            return

  
        #  abonos de la factura seleccionada.
        abonos = (
            self._obtener_abonos_factura(
                proveedor,
                self.factura_seleccionada
            )
        )

        if not abonos:

            messagebox.showinfo(
                "Información",
                (
                    "La factura seleccionada "
                    "no tiene abonos registrados."
                )
            )

            return

        ven_lista = tk.Toplevel(
            self
        )

        ven_lista.title(
            "Seleccionar Abono a Eliminar"
        )

        ven_lista.geometry(
            "470x340"
        )

        ven_lista.configure(
            bg=COLOR_BG
        )

        tk.Label(
            ven_lista,
            text=(
                "Selecciona el abono que deseas eliminar "
                f"de la factura '{self.factura_seleccionada}':"
            ),
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            font=("Segoe UI", 10, "bold"),
            wraplength=420,
            justify="center"
        ).pack(
            pady=10
        )

        cols = (
            "Fecha",
            "Factura",
            "Monto"
        )

        tree_abonos = ttk.Treeview(
            ven_lista,
            columns=cols,
            show="headings",
            height=7
        )

        for col in cols:

            tree_abonos.heading(
                col,
                text=col
            )

            tree_abonos.column(
                col,
                anchor="center",
                width=140
            )

        tree_abonos.pack(
            padx=10,
            pady=5,
            fill="both",
            expand=True
        )

        for idx, abono in enumerate(abonos):

            tree_abonos.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    abono.get(
                        "fecha",
                        "-"
                    ),
                    abono.get(
                        "factura",
                        "-"
                    ),
                    f"${self._numero(abono.get('monto', 0)):,.2f}"
                )
            )

        def confirmar_eliminacion():

            selected = (
                tree_abonos.selection()
            )

            if not selected:

                messagebox.showwarning(
                    "Atención",
                    "Selecciona un abono de la lista."
                )

                return

            item_idx = int(
                selected[0]
            )

            abono_seleccionado = (
                abonos[item_idx]
            )

            monto_abono = self._numero(
                abono_seleccionado.get(
                    "monto",
                    0
                )
            )

            confirmar = messagebox.askyesno(
                "Confirmar",
                (
                    "¿Estás seguro de eliminar este abono?\n\n"
                    f"Factura: {self.factura_seleccionada}\n"
                    f"Monto: ${monto_abono:,.2f}\n\n"
                    "El saldo de la factura aumentará "
                    "nuevamente con este valor."
                )
            )

            if not confirmar:
                return

            resultado = (
                self.service_proveedor.eliminar_abono(
                    self.id_seleccionado,
                    abono_seleccionado.get("_id")
                )
            )

            if resultado:

                messagebox.showinfo(
                    "Éxito",
                    "Abono eliminado correctamente."
                )

                ven_lista.destroy()

                self.cargar_tabla_facturas()

            else:

                messagebox.showerror(
                    "Error",
                    "No se pudo eliminar el abono."
                )

        tk.Button(
            ven_lista,
            text="🗑️ Eliminar Seleccionado",
            bg=COLOR_DANGER,
            fg="#FFF",
            font=("Segoe UI", 9, "bold"),
            command=confirmar_eliminacion
        ).pack(
            fill="x",
            padx=20,
            pady=10
        )

    
    # ELIMINAR PROVEEDOR
    

    def eliminar_proveedor(self):

        ven_eliminar = tk.Toplevel(
            self
        )

        ven_eliminar.title(
            "Eliminar Proveedor"
        )

        ven_eliminar.geometry(
            "380x220"
        )

        ven_eliminar.configure(
            bg=COLOR_BG
        )

        ven_eliminar.transient(self)
        ven_eliminar.grab_set()

        tk.Label(
            ven_eliminar,
            text="Selecciona el proveedor a eliminar:",
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(
            padx=20,
            pady=(20, 5)
        )

        proveedores = (
            self.service_proveedor.obtener_todos()
        )

        nombres_proveedores = [
            p.get("nombre")
            for p in proveedores
        ]

        if not nombres_proveedores:

            messagebox.showinfo(
                "Información",
                "No hay proveedores registrados."
            )

            ven_eliminar.destroy()

            return

        combo_prov_eliminar = ttk.Combobox(
            ven_eliminar,
            values=nombres_proveedores,
            state="readonly",
            width=36,
            font=("Segoe UI", 10)
        )

        combo_prov_eliminar.pack(
            padx=20,
            pady=10
        )

        combo_prov_eliminar.current(0)

        def confirmar_eliminacion_prov():

            idx = combo_prov_eliminar.current()

            if (
                idx < 0
                or idx >= len(proveedores)
            ):

                messagebox.showwarning(
                    "Atención",
                    "Selecciona un proveedor válido."
                )

                return

            prov_elegido = (
                proveedores[idx]
            )

            id_prov = (
                prov_elegido.get("_id")
            )

            nombre_prov = (
                prov_elegido.get(
                    "nombre",
                    ""
                )
            )

            confirmar = messagebox.askyesno(
                "Confirmar",
                (
                    f"¿Deseas eliminar al proveedor "
                    f"'{nombre_prov}' y todo su historial "
                    "de pedidos y abonos?"
                )
            )

            if not confirmar:
                return

            resultado = (
                self.service_proveedor.eliminar_proveedor(
                    id_prov
                )
            )

            if resultado:

                messagebox.showinfo(
                    "Éxito",
                    "Proveedor eliminado correctamente."
                )

                ven_eliminar.destroy()

                self.id_seleccionado = None
                self.factura_seleccionada = None

                self.cargar_tabla_facturas()

            else:

                messagebox.showerror(
                    "Error",
                    "No se pudo eliminar el proveedor "
                    "de la base de datos."
                )

        tk.Button(
            ven_eliminar,
            text="🗑️ Eliminar Proveedor Seleccionado",
            bg=COLOR_DANGER,
            fg="#FFF",
            font=("Segoe UI", 9, "bold"),
            command=confirmar_eliminacion_prov
        ).pack(
            fill="x",
            padx=20,
            pady=15
        )