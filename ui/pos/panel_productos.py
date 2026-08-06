import tkinter as tk
from tkinter import ttk, messagebox
import math


COLOR_FONDO = "#f4f6f9"
COLOR_BLANCO = "#ffffff"
COLOR_TEXTO = "#1e293b"
COLOR_ACCENT = "#2b580c"

class PanelProductos:
    """
    Controlador y lógica del panel izquierdo:
    Maneja el catálogo, búsqueda en tiempo real, filtrado por categorías,
    renderizado de cards de productos y paginación.
    """
    def __init__(self, pos_frame):
        self.pos = pos_frame

    
    # LÓGICA DE FILTRADO Y BÚSQUEDA
  
    def cargar_categorias(self, categorias):
        #Llena el ComboBox de categorías con los datos recibidos de la BD
        lista_cats = ["Todas"] + sorted(list(set(categorias)))
        self.pos.combo_categoria["values"] = lista_cats
        self.pos.combo_categoria.current(0)

    def _on_busqueda_change(self, event=None):
        #Callback al escribir en la caja de búsqueda del catálogo
        self.pos.pagina_actual = 1
        self.filtrar_productos()

    def _on_filtro_change(self, event=None):
        #Callback al seleccionar una categoría del ComboBox
        self.pos.pagina_actual = 1
        self.filtrar_productos()

    def filtrar_por_categoria(self, categoria):
       #Filtra los productos seleccionando explícitamente una categoría
        if categoria in self.pos.combo_categoria["values"]:
            self.pos.combo_categoria.set(categoria)
            self._on_filtro_change()

    def filtrar_productos(self):
        #Aplica los filtros locales de texto y categoría sobre la caché de productos
        texto_busqueda = self.pos.entry_buscar_cat.get().strip().lower()
        categoria_sel = self.pos.combo_categoria.get()

        productos_filtrados = []
        for p in self.pos.productos_cache:
            # Filtro por texto (Código o Nombre)
            coincide_texto = (
                texto_busqueda in p.get("codigo", "").lower() or
                texto_busqueda in p.get("nombre", "").lower()
            ) if texto_busqueda else True

            # Filtro por Categoría
            coincide_cat = (
                categoria_sel == "Todas" or p.get("categoria", "") == categoria_sel
            )

            if coincide_texto and coincide_cat:
                productos_filtrados.append(p)

        self._actualizar_grid(productos_filtrados)

   
    #  RENDERIZADO Y PAGINACIÓN DEL GRID
   
    def _actualizar_grid(self, productos):
        #Limpia la cuadrícula actual y renderiza la página correspondiente
        
        for child in self.pos.frame_cards.winfo_children():
            child.destroy()

        if not productos:
            lbl_vacio = tk.Label(
                self.pos.frame_cards,
                text="No se encontraron productos.",
                bg=COLOR_FONDO,
                fg="gray",
                font=("Arial", 11, "italic")
            )
            lbl_vacio.pack(expand=True, pady=20)
            self.pos.lbl_paginacion.config(text="Página 0 de 0")
            return

        # Paginación
        total_items = len(productos)
        total_paginas = math.ceil(total_items / self.pos.productos_por_pagina)
        self.pos.pagina_actual = min(self.pos.pagina_actual, total_paginas) or 1

        inicio = (self.pos.pagina_actual - 1) * self.pos.productos_por_pagina
        fin = inicio + self.pos.productos_por_pagina
        items_pagina = productos[inicio:fin]

        # Configurar rejilla (3 columnas)
        cols = 3
        for i, prod in enumerate(items_pagina):
            row = i // cols
            col = i % cols
            self._crear_card_producto(self.pos.frame_cards, prod, row, col)

        # Actualizar indicador de paginación
        self.pos.lbl_paginacion.config(text=f"Página {self.pos.pagina_actual} de {total_paginas}")

    def _crear_card_producto(self, parent, prod, row, col):
        """Crea la tarjeta visual individual para cada producto en la cuadrícula."""
        card = tk.Frame(
            parent,
            bg=COLOR_BLANCO,
            bd=1,
            relief="solid",
            cursor="hand2"
        )
        card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        parent.columnconfigure(col, weight=1)

        # Información del Producto
        nombre = prod.get("nombre", "Sin nombre")
        codigo = prod.get("codigo", "N/A")
        precio = prod.get("precio_venta", 0.0)
        stock = prod.get("stock", 0)

        lbl_nombre = tk.Label(
            card,
            text=nombre[:20] + ("..." if len(nombre) > 20 else ""),
            bg=COLOR_BLANCO,
            font=("Arial", 9, "bold"),
            fg=COLOR_TEXTO,
            anchor="w"
        )
        lbl_nombre.pack(fill="x", padx=5, pady=(5, 0))

        lbl_codigo = tk.Label(
            card,
            text=f"Ref: {codigo}",
            bg=COLOR_BLANCO,
            font=("Arial", 8),
            fg="gray",
            anchor="w"
        )
        lbl_codigo.pack(fill="x", padx=5)

        lbl_precio = tk.Label(
            card,
            text=f"${precio:,.0f}",
            bg=COLOR_BLANCO,
            font=("Arial", 11, "bold"),
            fg=COLOR_ACCENT,
            anchor="e"
        )
        lbl_precio.pack(fill="x", padx=5, pady=(2, 5))

        # Evento Clic en la tarjeta -> Agregar directamente al carrito
        card.bind("<Button-1>", lambda e, p=prod: self._on_card_click(p))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e, p=prod: self._on_card_click(p))

    def _on_card_click(self, producto):
        #Acción al hacer clic en un producto: agregar al carrito en el panel derecho
        if hasattr(self.pos, 'panel_carrito'):
            self.pos.panel_carrito.agregar_item_por_datos(
                codigo=producto.get("codigo", ""),
                nombre=producto.get("nombre", ""),
                precio=producto.get("precio_venta", 0.0),
                cantidad=1
            )

    def cambiar_pagina(self, delta):
       
        texto_busqueda = self.pos.entry_buscar_cat.get().strip().lower()
        categoria_sel = self.pos.combo_categoria.get()

        prods_filtrados = [
            p for p in self.pos.productos_cache
            if (not texto_busqueda or texto_busqueda in p.get("codigo", "").lower() or texto_busqueda in p.get("nombre", "").lower())
            and (categoria_sel == "Todas" or p.get("categoria", "") == categoria_sel)
        ]

        total_paginas = math.ceil(len(prods_filtrados) / self.pos.productos_por_pagina)
        nueva_pagina = self.pos.pagina_actual + delta

        if 1 <= nueva_pagina <= total_paginas:
            self.pos.pagina_actual = nueva_pagina
            self._actualizar_grid(prods_filtrados)