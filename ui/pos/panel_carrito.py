import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from bson import ObjectId
from services.factura_pdf_service import FacturaPDFService
from services.cierre_caja_service import generar_cierre


class PanelCarrito:
    def __init__(self, pos):
        self.pos = pos

    

    # =========================================================================
    # AUXILIAR DE BÚSQUEDA Y CONSECUTIVO DE FACTURA
    # =========================================================================
    def _buscar_factura_en_db(self, identificador):
        #Busca por numero_factura o ObjectId de forma segura
        if getattr(self.pos, "db", None) is None:
            from database.conexion import get_db

            self.pos.db = get_db()

        identificador_clean = str(identificador).strip()

        criterios = [
            {"numero_factura": identificador_clean},
            {"numero_factura": identificador_clean.upper()},
            {"numero": identificador_clean},
            {"_id": identificador_clean},
        ]

        if isinstance(identificador, ObjectId):
            criterios.append({"_id": identificador})
        elif ObjectId.is_valid(identificador_clean):
            criterios.append({"_id": ObjectId(identificador_clean)})

        factura = self.pos.db["facturas"].find_one({"$or": criterios})
        return factura

    def obtener_siguiente_consecutivo(self):
        """Calcula el siguiente consecutivo en formato FAC-XXXXXX."""
        try:
            if getattr(self.pos, "db", None) is None:
                from database.conexion import get_db

                self.pos.db = get_db()

            ultima_factura = self.pos.db["facturas"].find_one(
                {"numero_factura": {"$regex": "^FAC-"}}, sort=[("_id", -1)]
            )

            if ultima_factura and "numero_factura" in ultima_factura:
                num_str = str(ultima_factura["numero_factura"]).replace(
                    "FAC-", ""
                )
                if num_str.isdigit():
                    siguiente_num = int(num_str) + 1
                else:
                    siguiente_num = 1
            else:
                siguiente_num = 1

            return f"FAC-{siguiente_num:06d}"
        except Exception as e:
            print(f"Error generando consecutivo: {e}")
            return "FAC-000001"

    def _obtener_boton_procesar(self):
        #Busca y retorna la referencia al botón principal de venta/procesar
        posibles_nombres = [
            "btn_procesar_venta",
            "btn_procesar",
            "btn_pagar",
            "btn_emitir_factura",
            "btn_guardar_venta",
        ]
        for attr in posibles_nombres:
            if hasattr(self.pos, attr):
                return getattr(self.pos, attr)

        # Buscar recursivamente en los widgets descendientes
        try:
            for widget in self.pos.winfo_children():
                if isinstance(widget, tk.Button):
                    try:
                        texto = str(widget.cget("text")).upper()
                        if "PROCESAR" in texto or "ACTUALIZAR" in texto:
                            return widget
                    except Exception:
                        continue
        except Exception:
            pass
        return None

    
    # BÚSQUEDA Y GESTIÓN DE CLIENTES
    
    def buscar_cliente_por_cedula(self, event=None):
        cedula = self.pos.entry_cli_cedula.get().strip()
        if not cedula:
            return

        try:
            if getattr(self.pos, "db", None) is None:
                from database.conexion import get_db

                self.pos.db = get_db()

            cliente = self.pos.db["clientes"].find_one({"cedula": cedula})
            if cliente:
                nombre_comp = (
                    f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}"
                ).strip()
                self.pos.entry_cli_nombre.delete(0, tk.END)
                self.pos.entry_cli_nombre.insert(0, nombre_comp)

                self.pos.entry_cli_correo.delete(0, tk.END)
                self.pos.entry_cli_correo.insert(0, cliente.get("correo", ""))
        except Exception as e:
            print(f"Error al buscar cliente: {e}")

    
    # BÚSQUEDA Y FILTRADO DE PRODUCTOS
   
    def filtrar_productos_buscador(self, event=None):
        query = self.pos.entry_buscar_prod.get().strip().lower()
        self.pos.listbox_sugerencias.delete(0, tk.END)

        if not query:
            self.pos.listbox_sugerencias.place_forget()
            return

        productos_cache = getattr(self.pos, "productos_cache", []) or []
        coincidencias = []
        for p in productos_cache:
            num_ref = str(p.get("numReferencia", p.get("codigo", ""))).lower()
            nombre = str(
                p.get("nombre", f"{p.get('marca', '')} {p.get('color', '')}")
            ).lower()

            if query in num_ref or query in nombre:
                coincidencias.append(p)

        if coincidencias:
            for p in coincidencias[:5]:
                num_ref = p.get("numReferencia", p.get("codigo", ""))
                nombre_prod = p.get(
                    "nombre",
                    f"{p.get('marca', '')} (Talla {p.get('talla', '')})",
                )
                try:
                    precio = float(p.get("valorVenta", p.get("precio_venta", 0)))
                except (ValueError, TypeError):
                    precio = 0.0

                txt = f"{num_ref} - {nombre_prod} (${precio:,.0f})"
                self.pos.listbox_sugerencias.insert(tk.END, txt)

            self.pos.listbox_sugerencias.place(
                in_=self.pos.entry_buscar_prod, x=0, y=25, relwidth=1.0
            )
            self.pos.listbox_sugerencias.lift()
        else:
            self.pos.listbox_sugerencias.place_forget()

    def seleccionar_sugerencia_carrito(self, event=None):
        seleccion = self.pos.listbox_sugerencias.curselection()
        if not seleccion:
            return

        texto = self.pos.listbox_sugerencias.get(seleccion[0])
        codigo = texto.split(" - ")[0].strip()

        self.pos.entry_buscar_prod.delete(0, tk.END)
        self.pos.entry_buscar_prod.insert(0, codigo)
        self.pos.listbox_sugerencias.place_forget()
        self.agregar_desde_buscador()

    def agregar_desde_buscador(self):
        query = self.pos.entry_buscar_prod.get().strip()
        cant_str = self.pos.entry_cant_prod.get().strip()

        if not query:
            return

        try:
            cantidad = int(cant_str) if cant_str.isdigit() and int(cant_str) > 0 else 1
        except ValueError:
            cantidad = 1

        productos_cache = getattr(self.pos, "productos_cache", []) or []
        prod_encontrado = None
        for p in productos_cache:
            num_ref = str(p.get("numReferencia", p.get("codigo", "")))
            nombre = str(
                p.get("nombre", f"{p.get('marca', '')} {p.get('color', '')}")
            ).lower()

            if num_ref.lower() == query.lower() or nombre == query.lower():
                prod_encontrado = p
                break

        if prod_encontrado:
            self.agregar_producto(prod_encontrado, cantidad)
            self.limpiar_buscador_carrito()
        else:
            messagebox.showwarning(
                "Producto no encontrado",
                f"No se encontró un producto con el código o nombre: '{query}'",
            )

    def limpiar_buscador_carrito(self):
        self.pos.entry_buscar_prod.delete(0, tk.END)
        self.pos.entry_cant_prod.delete(0, tk.END)
        self.pos.entry_cant_prod.insert(0, "1")
        self.pos.listbox_sugerencias.place_forget()

    
    # OPERACIONES DEL CARRITO Y PROCESAMIENTO DE PAGO / ACTUALIZACIÓN
    
    def agregar_producto(self, producto, cantidad=1):
        prod_id = str(producto.get("_id", ""))
        try:
            precio = float(
                producto.get("valorVenta", producto.get("precio_venta", 0.0))
            )
        except (ValueError, TypeError):
            precio = 0.0

        nombre = producto.get("nombre")
        if not nombre:
            marca = producto.get("marca", "")
            talla = producto.get("talla", "")
            color = producto.get("color", "")
            nombre = f"{marca} {color} Talla {talla}".strip() or "Producto"

        for item in self.pos.carrito:
            if str(item.get("_id", "")) == prod_id:
                item["cantidad"] += cantidad
                item["subtotal"] = item["cantidad"] * item["precio"]
                self.actualizar_tabla_carrito()
                return

        self.pos.carrito.append(
            {
                "_id": prod_id,
                "codigo": producto.get(
                    "numReferencia", producto.get("codigo", "")
                ),
                "nombre": nombre,
                "precio": precio,
                "cantidad": cantidad,
                "subtotal": cantidad * precio,
            }
        )

        self.actualizar_tabla_carrito()

    def actualizar_tabla_carrito(self):
        for row in self.pos.tree_cart.get_children():
            self.pos.tree_cart.delete(row)

        total = 0.0
        total_items = 0
        total_unidades = 0

        for item in self.pos.carrito:
            subtotal = item["cantidad"] * item["precio"]
            item["subtotal"] = subtotal

            total += subtotal
            total_items += 1
            total_unidades += item["cantidad"]

            self.pos.tree_cart.insert(
                "",
                tk.END,
                values=(
                    item["nombre"],
                    item["cantidad"],
                    f"$ {item['precio']:,.2f}",
                    f"$ {subtotal:,.2f}",
                ),
            )

        self.pos.lbl_cant_total.config(
            text=f"🛍️ Ítems en orden: {total_items} (Unidades: {total_unidades})"
        )
        self.pos.lbl_total_pagar.config(text=f"TOTAL: $ {total:,.2f}")

    def procesar_pago(self):
        #Procesa la venta o guarda los cambios si se está editando una factura existente
        if not hasattr(self.pos, "carrito") or not self.pos.carrito:
            messagebox.showwarning(
                "Carrito Vacío",
                "No hay productos en el carrito para procesar la venta.",
                parent=self.pos,
            )
            return

        try:
            if getattr(self.pos, "db", None) is None:
                from database.conexion import get_db

                self.pos.db = get_db()

            total_venta = sum(item.get("subtotal", 0.0) for item in self.pos.carrito)
            cliente_info = {
                "cedula": self.pos.entry_cli_cedula.get().strip() or "C.F.",
                "nombre": self.pos.entry_cli_nombre.get().strip() or "CLIENTE GENERAL",
                "correo": self.pos.entry_cli_correo.get().strip(),
            }

            # SI ESTAMOS EN MODO EDICIÓN
            if getattr(self.pos, "factura_actual_id", None):
                num_fac = self.pos.factura_actual_id
                datos_actualizar = {
                    "cliente": cliente_info,
                    "cliente_cedula": cliente_info["cedula"],
                    "cliente_nombre": cliente_info["nombre"],
                    "correo_destino": cliente_info["correo"],
                    "items": list(self.pos.carrito),
                    "total": total_venta,
                    "fecha_modificacion": datetime.now(),
                }

                self.pos.db["facturas"].update_one(
                    {"$or": [{"numero_factura": num_fac}, {"_id": num_fac}]},
                    {"$set": datos_actualizar},
                )

                factura_doc = self._buscar_factura_en_db(num_fac)
                if not factura_doc:
                    factura_doc = datos_actualizar
                    factura_doc["numero_factura"] = num_fac
                    factura_doc["fecha"] = datetime.now()

                self._mostrar_vista_previa_factura(factura_doc)
                messagebox.showinfo(
                    "Factura Actualizada",
                    f"✅ La factura {num_fac} ha sido actualizada con éxito.",
                )

            # SI ES NUEVA VENTA
            else:
                num_fac = self.obtener_siguiente_consecutivo()
                factura_doc = {
                    "numero_factura": num_fac,
                    "fecha": datetime.now(),
                    "estado": "EMITIDA",
                    "cliente": cliente_info,
                    "cliente_cedula": cliente_info["cedula"],
                    "cliente_nombre": cliente_info["nombre"],
                    "correo_destino": cliente_info["correo"],
                    "items": list(self.pos.carrito),
                    "total": total_venta,
                }
                self.pos.db["facturas"].insert_one(factura_doc)

                # DESCONTAR STOCK
                for item in self.pos.carrito:

                    codigo = item.get(
                        "codigo",
                        item.get("numReferencia", "")
                    )

                    cantidad = int(
                        item.get("cantidad", 1)
                    )

                    try:
                      codigo_busqueda = int(codigo)
                    except:
                       codigo_busqueda = codigo

                    
                    resultado = self.pos.db["productos"].update_one(
                       {
                           "numReferencia": codigo_busqueda
                       },
                       {
                             "$inc": {
                               "cantidadStock": -cantidad
                              }
                             }
                           )
                    
                    

                ruta_pdf = FacturaPDFService.generar_pdf(factura_doc)
                print("PDF generado:", ruta_pdf)
                self._mostrar_vista_previa_factura(factura_doc)

                messagebox.showinfo(
                    "Venta Exitosa",
                    f"✅ Venta procesada correctamente.\nFactura generada: {num_fac}",
                )

            self.limpiar_para_nueva_factura()

            if hasattr(self.pos, "refresh_productos"):
                self.pos.refresh_productos()

            if hasattr(self.pos, "cargar_productos_iniciales"):
                self.pos.cargar_productos_iniciales()

            ventana_principal = self.pos.obtener_ventana_principal()

            if ventana_principal:
             ventana_principal.refrescar_productos()

            self._mostrar_vista_previa_factura(factura_doc)
            

        except Exception as e:
            messagebox.showerror(
                "Error al procesar pago", f"Ocurrió un error al guardar la factura: {e}"
            )

    
    # GESTIÓN DE FACTURAS (Cargar, Editar, Anular)
   
    def cargar_factura_para_edicion(self, fac_id):
        """Abre un cuadro emergente modal dedicado para editar la factura adaptado al tema oscuro."""
        try:
            factura = self._buscar_factura_en_db(fac_id)
            if not factura:
                messagebox.showerror(
                    "No Encontrado",
                    f"No se encontró ninguna factura con el ID/Número: '{fac_id}'",
                    parent=self.pos,
                )
                return

            num_factura_real = factura.get("numero_factura") or str(factura.get("_id"))

            # Definición de la paleta de colores del tema oscuro
            COLOR_BG = "#1e293b"        # Fondo principal de la ventana modal
            COLOR_CARD = "#0f172a"      # Fondo de las secciones/frames
            COLOR_TEXT = "#ffffff"      # Texto principal de etiquetas y títulos
            COLOR_ACCENT = "#0284c7"    # Azul para el botón de guardar
            COLOR_ORANGE = "#d97706"    # Naranja para cambiar referencia

            # Crear Ventana Emergente Modal
            modal = tk.Toplevel(self.pos)
            modal.title(f"✏️ Editar Factura - {num_factura_real}")
            modal.geometry("750x620")
            modal.configure(bg=COLOR_BG)
            modal.grab_set()

            #  FRAME 1: DATOS DEL CLIENTE 
            frame_cli = tk.LabelFrame(
                modal,
                text=" Datos del Cliente ",
                bg=COLOR_CARD,
                fg=COLOR_TEXT,
                font=("Arial", 10, "bold"),
                padx=10,
                pady=10,
                bd=1,
                relief="solid"
            )
            frame_cli.pack(fill="x", padx=10, pady=8)

            cliente_doc = factura.get("cliente") or {}
            lbl_opts = {"bg": COLOR_CARD, "fg": COLOR_TEXT, "font": ("Arial", 9, "bold")}

            tk.Label(frame_cli, text="Cédula:", **lbl_opts).grid(row=0, column=0, sticky="e", padx=5, pady=4)
            entry_cedula = ttk.Entry(frame_cli)
            entry_cedula.insert(0, factura.get("cliente_cedula") or cliente_doc.get("cedula", ""))
            entry_cedula.grid(row=0, column=1, padx=5, pady=4)

            tk.Label(frame_cli, text="Nombre:", **lbl_opts).grid(row=0, column=2, sticky="e", padx=5, pady=4)
            entry_nombre = ttk.Entry(frame_cli, width=25)
            entry_nombre.insert(0, factura.get("cliente_nombre") or cliente_doc.get("nombre", ""))
            entry_nombre.grid(row=0, column=3, padx=5, pady=4)

            tk.Label(frame_cli, text="Correo:", **lbl_opts).grid(row=1, column=0, sticky="e", padx=5, pady=4)
            entry_correo = ttk.Entry(frame_cli, width=35)
            entry_correo.insert(0, factura.get("correo_destino") or cliente_doc.get("correo", ""))
            entry_correo.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=4)

            # FRAME 2: PRODUCTOS DE LA FACTURA 
            frame_prods = tk.LabelFrame(
                modal,
                text=" Productos en la Factura ",
                bg=COLOR_CARD,
                fg=COLOR_TEXT,
                font=("Arial", 10, "bold"),
                padx=10,
                pady=10,
                bd=1,
                relief="solid"
            )
            frame_prods.pack(fill="both", expand=True, padx=10, pady=5)

            cols = ("Ref", "Producto", "Cant", "Precio", "Subtotal")
            tree_edit = ttk.Treeview(frame_prods, columns=cols, show="headings", height=8)
            for c in cols:
                tree_edit.heading(c, text=c)
            tree_edit.column("Ref", width=90)
            tree_edit.column("Producto", width=250)
            tree_edit.column("Cant", width=50, anchor="center")
            tree_edit.column("Precio", width=90, anchor="e")
            tree_edit.column("Subtotal", width=100, anchor="e")
            tree_edit.pack(fill="both", expand=True, pady=5)

            # Cargar lista local de ítems
            items_locales = []
            for item in factura.get("items", []):
                try:
                    precio = float(item.get("precio", item.get("valorVenta", item.get("precio_unitario", 0.0))))
                except (ValueError, TypeError):
                    precio = 0.0

                try:
                    cant = int(item.get("cantidad", item.get("cant", 1)))
                except (ValueError, TypeError):
                    cant = 1

                items_locales.append({
                    "_id": str(item.get("_id", item.get("producto_id", ""))),
                    "codigo": item.get("numReferencia", item.get("codigo", "")),
                    "nombre": item.get("nombre", item.get("producto", item.get("descripcion", "Producto"))),
                    "precio": precio,
                    "cantidad": cant,
                    "subtotal": cant * precio,
                })

            def refrescar_tabla_modal():
                for row in tree_edit.get_children():
                    tree_edit.delete(row)
                for item in items_locales:
                    tree_edit.insert("", tk.END, values=(
                        item["codigo"],
                        item["nombre"],
                        item["cantidad"],
                        f"${item['precio']:,.2f}",
                        f"${item['subtotal']:,.2f}",
                    ))

            refrescar_tabla_modal()

            # CAMBIO DE REFERENCIA / TALLA 
            frame_acciones = tk.Frame(frame_prods, bg=COLOR_CARD)
            frame_acciones.pack(fill="x", pady=5)

            def cambiar_referencia_item():
                seleccion = tree_edit.selection()
                if not seleccion:
                    messagebox.showwarning("Selección", "Selecciona un producto de la lista para cambiar.", parent=modal)
                    return

                idx = tree_edit.index(seleccion[0])
                item_actual = items_locales[idx]

                from tkinter import simpledialog
                nueva_ref = simpledialog.askstring(
                    "Cambiar Talla / Referencia",
                    f"Producto: {item_actual['nombre']}\nRef Actual: {item_actual['codigo']}\n\nIngrese la NUEVA referencia/código:",
                    parent=modal
                )

                if nueva_ref:
                    nueva_ref = nueva_ref.strip()
                    productos_cache = getattr(self.pos, "productos_cache", []) or []
                    prod_nuevo = next(
                        (p for p in productos_cache if str(p.get("numReferencia", p.get("codigo", ""))).lower() == nueva_ref.lower()),
                        None
                    )

                    if prod_nuevo:
                        try:
                            precio_nuevo = float(prod_nuevo.get("valorVenta", prod_nuevo.get("precio_venta", item_actual["precio"])))
                        except (ValueError, TypeError):
                            precio_nuevo = item_actual["precio"]

                        nombre_nuevo = prod_nuevo.get("nombre") or f"{prod_nuevo.get('marca', '')} {prod_nuevo.get('color', '')} Talla {prod_nuevo.get('talla', '')}".strip()

                        items_locales[idx]["codigo"] = nueva_ref
                        items_locales[idx]["nombre"] = nombre_nuevo
                        items_locales[idx]["precio"] = precio_nuevo
                        items_locales[idx]["subtotal"] = items_locales[idx]["cantidad"] * precio_nuevo
                        items_locales[idx]["_id"] = str(prod_nuevo.get("_id", ""))

                        refrescar_tabla_modal()
                        messagebox.showinfo("Éxito", "Referencia cambiada correctamente.", parent=modal)
                    else:
                        messagebox.showerror("No Encontrado", f"No se encontró un producto en inventario con la referencia: '{nueva_ref}'", parent=modal)

            btn_cambiar_ref = tk.Button(
                frame_acciones,
                text="🔄 Cambiar Referencia / Talla",
                bg=COLOR_ORANGE, fg="white", font=("Arial", 9, "bold"),
                activebackground="#b45309", activeforeground="white",
                relief="flat", cursor="hand2", padx=10, pady=5,
                command=cambiar_referencia_item
            )
            btn_cambiar_ref.pack(side="left", padx=5)

            # BOTÓN DE GUARDAR CAMBIOS 
            def guardar_cambios_factura():
                try:
                    total_nuevo = sum(it["subtotal"] for it in items_locales)
                    cli_info = {
                        "cedula": entry_cedula.get().strip() or "C.F.",
                        "nombre": entry_nombre.get().strip() or "CLIENTE GENERAL",
                        "correo": entry_correo.get().strip(),
                    }

                    datos_actualizados = {
                        "cliente": cli_info,
                        "cliente_cedula": cli_info["cedula"],
                        "cliente_nombre": cli_info["nombre"],
                        "correo_destino": cli_info["correo"],
                        "items": items_locales,
                        "total": total_nuevo,
                        "fecha_modificacion": datetime.now(),
                    }

                    if getattr(self.pos, "db", None) is None:
                        from database.conexion import get_db
                        self.pos.db = get_db()

                    self.pos.db["facturas"].update_one(
                        {"_id": factura["_id"]},
                        {"$set": datos_actualizados}
                    )

                    factura.update(datos_actualizados)
                    self._mostrar_vista_previa_factura(factura)

                    messagebox.showinfo("Éxito", "✅ Factura actualizada correctamente.", parent=self.pos)
                    modal.destroy()

                except Exception as ex:
                    messagebox.showerror("Error", f"No se pudieron guardar los cambios: {ex}", parent=modal)

            btn_guardar = tk.Button(
                modal,
                text="💾 GUARDAR CAMBIOS EN FACTURA",
                bg=COLOR_ACCENT, fg="white", font=("Arial", 10, "bold"),
                activebackground="#0369a1", activeforeground="white",
                relief="flat", cursor="hand2", pady=8,
                command=guardar_cambios_factura
            )
            btn_guardar.pack(fill="x", padx=10, pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la factura: {e}", parent=self.pos)

   
    # DIÁLOGOS Y POPUPS EMERGENTES
   
    def buscar_o_editar_factura(self):
        #Muestra el cuadro emergente para ingresar la factura a editar/cargar
        from tkinter import simpledialog

        num_factura = simpledialog.askstring(
            "Editar Factura",
            "Ingrese el número o ID de la Factura (ej: FAC-000001):",
            parent=self.pos,
        )

        if num_factura:
            num_factura = num_factura.strip()
            if num_factura:
                self.cargar_factura_para_edicion(num_factura)

    def anular_factura(self, fac_id):
        try:
          factura = self._buscar_factura_en_db(fac_id)

          if not factura:
            messagebox.showerror(
                "Error",
                "Factura no encontrada."
            )
            return

          numero = factura.get("numero_factura", "N/A")

          confirmar = messagebox.askyesno(
            "Confirmar",
            f"¿Desea anular la factura {numero}?"
        )

          if not confirmar:
            return

          if getattr(self.pos, "db", None) is None:
            from database.conexion import get_db
            self.pos.db = get_db()

       
        # DEVOLVER STOCK
        

          for item in factura.get("items", []):

              codigo = item.get(
               "codigo",
               item.get("numReferencia", "")
             )

              cantidad = int(
              item.get("cantidad", 1)
             )

              try:
                codigo_busqueda = int(codigo)
              except:
               codigo_busqueda = codigo

              

              resultado = self.pos.db["productos"].update_one(
            {
                 "numReferencia": codigo_busqueda
            },
            {
                 "$inc": {
                   "cantidadStock": cantidad
            }
            }
            )

              

        
        # ANULAR FACTURA
        

          self.pos.db["facturas"].update_one(
            {"_id": factura["_id"]},
            {
                "$set": {
                    "estado": "ANULADA",
                    "fecha_anulacion": datetime.now()
                }
            }
        )

          messagebox.showinfo(
            "Correcto",
            f"Factura {numero} anulada correctamente.\n\nStock restaurado."
        )

          self.limpiar_para_nueva_factura()

          ventana_principal = self.pos.obtener_ventana_principal()

          if ventana_principal:
           ventana_principal.refrescar_productos()
        

        except Exception as e:
         messagebox.showerror(
            "Error",
            str(e)
        )

    def limpiar_para_nueva_factura(self):
        self.pos.carrito = []
        self.pos.factura_actual_id = None

        self.pos.entry_cli_cedula.delete(0, tk.END)
        self.pos.entry_cli_nombre.delete(0, tk.END)
        self.pos.entry_cli_correo.delete(0, tk.END)

        btn_procesar = self._obtener_boton_procesar()
        if btn_procesar:
            btn_procesar.config(
                text="💳 PROCESAR VENTA Y EMITIR FACTURA", bg="#FF9800"
            )

        self.limpiar_buscador_carrito()
        self.actualizar_tabla_carrito()
        self._mostrar_factura_vacia()

    def realizar_cierre_caja(self):

        try:

         usuario = (
            self.pos.empleado.usuario
            if self.pos.empleado
            else "Sistema"
         )

         cierre_doc = generar_cierre(
            self.pos.db,
            usuario
         )

         self.mostrar_vista_previa_cierre(cierre_doc) 

        except Exception as e:
         messagebox.showerror(
            "Error",
            f"No fue posible generar el cierre.\n\n{e}"
         )

    def mostrar_vista_previa_cierre(self, cierre_doc):

        ventana = tk.Toplevel(self.pos)
        ventana.title(f"Cierre de Caja - {cierre_doc['numero_cierre']}")
        ventana.geometry("600x500")
        ventana.configure(bg="#0f172a")

        texto = tk.Text(
           ventana,
           bg="#050509",
           fg="#39FF14",
           insertbackground="#39FF14",
           font=("Consolas", 12, "bold"),
            bd=0,
            relief="flat"
)

        texto.pack(fill="both", expand=True, padx=10, pady=10)

        contenido = f"""


           CIERRE DE CAJA

Número:
{cierre_doc['numero_cierre']}

Fecha:
{cierre_doc['fecha_cierre']}

Usuario:
{cierre_doc['usuario']}

Facturas Procesadas:
{cierre_doc['cantidad_facturas']}

Total Ventas:
${cierre_doc['total_ventas']:,.0f}

Total Anulaciones:
${cierre_doc['total_anulaciones']:,.0f}

TOTAL NETO:
${cierre_doc['total_neto']:,.0f}

=========================================
"""

        texto.insert("1.0", contenido)
        texto.config(state="disabled")     

    
    # VISTA PREVIA FACTURA DIGITAL
    
    def _mostrar_factura_vacia(self):
        self.pos.txt_factura_digital.config(state="normal")
        self.pos.txt_factura_digital.delete("1.0", tk.END)
        plantilla = (
            "========================================\n"
            "        SISTEMA POS - FACTURA           \n"
            "========================================\n"
            " No hay venta procesada actualmente.   \n"
            " Añada productos al carrito y procese  \n"
            " la compra para emitir comprobante.    \n"
            "========================================\n"
        )
        self.pos.txt_factura_digital.insert(tk.END, plantilla)
        self.pos.txt_factura_digital.config(state="disabled")

    def _mostrar_vista_previa_factura(self, factura):
        self.pos.txt_factura_digital.config(state="normal")
        self.pos.txt_factura_digital.delete("1.0", tk.END)

        num_fac = factura.get("numero_factura", "S/N")
        fecha = factura.get("fecha", datetime.now())
        fecha_str = (
            fecha.strftime("%Y-%m-%d %H:%M")
            if isinstance(fecha, datetime)
            else str(fecha)
        )

        cliente_doc = factura.get("cliente") or {}
        nom_cli = (
            factura.get("cliente_nombre")
            or cliente_doc.get("nombre")
            or "CLIENTE GENERAL"
        )
        ced_cli = (
            factura.get("cliente_cedula") or cliente_doc.get("cedula") or "N/A"
        )

        texto = (
            f"========================================\n"
            f"          FACTURA DE VENTA              \n"
            f" No: {num_fac}\n"
            f" Fecha: {fecha_str}\n"
            f"----------------------------------------\n"
            f" Cliente: {nom_cli}\n"
            f" Cédula:  {ced_cli}\n"
            f"----------------------------------------\n"
            f" CANT    DESCRIPCION            SUBTOTAL \n"
            f"----------------------------------------\n"
        )

        for item in factura.get("items", []):
            try:
                cant = int(item.get("cantidad", item.get("cant", 1)))
            except (ValueError, TypeError):
                cant = 1

            nom = str(
                item.get(
                    "nombre",
                    item.get("producto", item.get("descripcion", "Producto")),
                )
            )[:18].ljust(18)

            try:
                precio_unit = float(
                    item.get(
                        "precio",
                        item.get(
                            "valorVenta", item.get("precio_unitario", 0.0)
                        ),
                    )
                )
            except (ValueError, TypeError):
                precio_unit = 0.0

            try:
                sub = float(item.get("subtotal", cant * precio_unit))
            except (ValueError, TypeError):
                sub = cant * precio_unit

            texto += f" {str(cant).rjust(3)}    {nom} $ {sub:,.2f}\n"

        try:
            total_fac = float(factura.get("total", 0.0))
        except (ValueError, TypeError):
            total_fac = 0.0

        texto += (
            f"----------------------------------------\n"
            f" TOTAL A PAGAR:          $ {total_fac:,.2f}\n"
            f"========================================\n"
            f"        ¡GRACIAS POR SU COMPRA!         \n"
        )

        self.pos.txt_factura_digital.insert(tk.END, texto)
        self.pos.txt_factura_digital.config(state="disabled")