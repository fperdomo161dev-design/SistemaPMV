import tkinter as tk
from tkinter import ttk, messagebox
from services.contabilidad_service import ContabilidadService 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class VentanaDashboard(tk.Toplevel):
    def __init__(self, parent, service=None):
        super().__init__(parent)
        self.title("Dashboard Contable, Financiero y de Inventario - SistemaPMV")
        self.geometry("1450x900")
        self.config(bg="#1e1e2e")

        self.service = service if service else ContabilidadService()

        self.crear_interfaz()
        self.cargar_datos()

    def crear_interfaz(self):
        #  HEADER / FILTROS DE FECHA 
        frame_top = tk.Frame(self, bg="#2a2a3c", padx=10, pady=10)
        frame_top.pack(fill="x", padx=15, pady=15)

        tk.Label(frame_top, text="📅 Desde:", bg="#2a2a3c", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.txt_f_inicio = tk.Entry(frame_top, width=12, font=("Arial", 10))
        self.txt_f_inicio.pack(side="left", padx=5)
        self.txt_f_inicio.insert(0, "2026-08-01")

        tk.Label(frame_top, text="📅 Hasta:", bg="#2a2a3c", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.txt_f_fin = tk.Entry(frame_top, width=12, font=("Arial", 10))
        self.txt_f_fin.pack(side="left", padx=5)
        self.txt_f_fin.insert(0, "2026-08-30")

        btn_filtrar = tk.Button(frame_top, text="🔍 Aplicar Filtro", bg="#4f46e5", fg="white", font=("Arial", 10, "bold"), command=self.cargar_datos)
        btn_filtrar.pack(side="left", padx=15)

        #  KPIS SUPERIORES 
        frame_kpis = tk.Frame(self, bg="#1e1e2e")
        frame_kpis.pack(fill="x", padx=15, pady=5)

        self.kpi_ingresos = self.crear_tarjeta_kpi(frame_kpis, "Total Ingresos", "$ 0", "#10b981")
        self.kpi_egresos = self.crear_tarjeta_kpi(frame_kpis, "Total Egresos", "$ 0", "#ef4444")
        self.kpi_nomina = self.crear_tarjeta_kpi(frame_kpis, "Gastos Nómina", "$ 0", "#f59e0b")
        self.kpi_balance = self.crear_tarjeta_kpi(frame_kpis, "Balance Neto", "$ 0", "#3b82f6")

        #  CONTENEDOR CENTRAL
        frame_centro = tk.Frame(self, bg="#1e1e2e")
        frame_centro.pack(fill="both", expand=True, padx=15, pady=10)

        # 1. Columna Izquierda: Gráficos
        self.frame_graficos = tk.Frame(frame_centro, bg="#2a2a3c", width=420)
        self.frame_graficos.pack(side="left", fill="both", padx=(0, 10))

        # 2. Columna Central-Izquierda: Detalle de Ingresos
        self.frame_ingresos_det = tk.Frame(frame_centro, bg="#2a2a3c", width=310)
        self.frame_ingresos_det.pack(side="left", fill="both", padx=(0, 10))

        # 3. Columna Central-Derecha: Detalle de Egresos
        self.frame_egresos_det = tk.Frame(frame_centro, bg="#2a2a3c", width=310)
        self.frame_egresos_det.pack(side="left", fill="both", padx=(0, 10))

        # 4. Columna Derecha: Rankings de Zapatos Más y Menos Vendidos
        frame_rankings = tk.Frame(frame_centro, bg="#1e1e2e", width=320)
        frame_rankings.pack(side="right", fill="both", expand=True)

        tk.Label(frame_rankings, text="🔥 Zapatos Más Vendidos", bg="#1e1e2e", fg="#10b981", font=("Arial", 10, "bold")).pack(anchor="w", pady=2)
        self.tree_mas = self.crear_tabla(frame_rankings)

        tk.Label(frame_rankings, text="⚠️ Zapatos Menos Vendidos", bg="#1e1e2e", fg="#ef4444", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.tree_menos = self.crear_tabla(frame_rankings)

    def crear_tarjeta_kpi(self, parent, titulo, valor_inicial, color):
        card = tk.Frame(parent, bg="#2a2a3c", bd=1, relief="solid", padx=15, pady=10)
        card.pack(side="left", expand=True, fill="both", padx=5)

        tk.Label(card, text=titulo, bg="#2a2a3c", fg="#9ca3af", font=("Arial", 9)).pack(anchor="w")
        lbl_valor = tk.Label(card, text=valor_inicial, bg="#2a2a3c", fg=color, font=("Arial", 16, "bold"))
        lbl_valor.pack(anchor="w", pady=5)
        return lbl_valor

    def crear_tabla(self, parent):
        frame_table = tk.Frame(parent, bg="#2a2a3c")
        frame_table.pack(fill="both", expand=True, pady=2)

        tree = ttk.Treeview(frame_table, columns=("Modelo", "Unidades"), show="headings", height=9)
        tree.heading("Modelo", text="Modelo / Referencia")
        tree.heading("Unidades", text="Unidades")
        tree.column("Modelo", width=210)
        tree.column("Unidades", width=80, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tree

    def cargar_datos(self):
        f_inicio = self.txt_f_inicio.get().strip()
        f_fin = self.txt_f_fin.get().strip()

        try:
            totales = self.service.obtener_resumen_dashboard(f_inicio, f_fin)
            mas_vendidos, menos_vendidos = self.service.obtener_ranking_zapatos(f_inicio, f_fin)
        except Exception as e:
            print(f"Error al cargar datos en el dashboard: {e}")
            totales = {"ingresos": 0.0, "egresos": 0.0, "nominas": 0.0, "servicios": 0.0, "proveedores": 0.0}
            mas_vendidos, menos_vendidos = [], []

        balance_neto = totales["ingresos"] - totales["egresos"]

        self.kpi_ingresos.config(text=f"$ {totales['ingresos']:,.0f}")
        self.kpi_egresos.config(text=f"$ {totales['egresos']:,.0f}")
        self.kpi_nomina.config(text=f"$ {totales['nominas']:,.0f}")
        
        color_neto = "#3b82f6" if balance_neto >= 0 else "#ef4444"
        self.kpi_balance.config(text=f"$ {balance_neto:,.0f}", fg=color_neto)

        self.actualizar_graficos(totales)
        self.actualizar_tabla_ingresos(f_inicio, f_fin)
        self.actualizar_tabla_egresos(f_inicio, f_fin)

        for row in self.tree_mas.get_children():
            self.tree_mas.delete(row)
        for row in self.tree_menos.get_children():
            self.tree_menos.delete(row)

        if mas_vendidos:
            for item, cant in mas_vendidos:
                self.tree_mas.insert("", "end", values=(item, cant))
        else:
            self.tree_mas.insert("", "end", values=("Sin ventas en periodo", "-"))

        if menos_vendidos:
            for item, cant in menos_vendidos:
                self.tree_menos.insert("", "end", values=(item, cant))
        else:
            self.tree_menos.insert("", "end", values=("Sin ventas en periodo", "-"))

    def actualizar_graficos(self, totales):
        for widget in self.frame_graficos.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(4.2, 8.2), constrained_layout=True)
        fig.patch.set_facecolor('#2a2a3c')

        # 1. Contraste Financiero
        utilidad = totales['ingresos'] - totales['egresos']
        categorias = ['Ingresos', 'Egresos', 'Utilidad']
        valores = [totales['ingresos'], totales['egresos'], utilidad]
        colores_bar = ['#38bdf8', '#fb7185', '#34d399' if utilidad >= 0 else '#fbbf24']

        ax1.set_facecolor('#1e1e2e')
        
        x_pos = [0, 1, 2]
        barras = ax1.bar(x_pos, valores, bottom=0, color=colores_bar, width=0.42, edgecolor='#ffffff', linewidth=0.6, alpha=0.9)
        
        ax1.set_title("Contraste Financiero y Utilidad", color='white', fontsize=10, fontweight='bold', pad=10)
        ax1.tick_params(colors='white', labelsize=8)
        
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(categorias, color='white', fontsize=8)
        ax1.set_xlim(-0.5, 2.5)

        max_val = max([abs(v) for v in valores]) if valores and max([abs(v) for v in valores]) > 0 else 1.0
        ax1.set_ylim(-max_val * 1.5, max_val * 1.5)

        # --- LÍNEA CENTRAL DE REFERENCIA EN EL EJE CERO ---
        ax1.axhline(0, color='#9ca3af', linewidth=1.2, linestyle='--', alpha=0.7)

        for spine in ax1.spines.values():
            spine.set_color('#4b5563')

        for barra in barras:
            altura = barra.get_height()
            if altura >= 0:
                offset = 6
                va_val = 'bottom'
            else:
                offset = -16
                va_val = 'top'

            ax1.annotate(f'$ {altura:,.0f}',
                         xy=(barra.get_x() + barra.get_width() / 2, altura),
                         xytext=(0, offset),
                         textcoords="offset points",
                         ha='center', va=va_val, color='white', fontsize=7.5, fontweight='bold')

        # 2. Distribución de Egresos (Pastel)
        labels = ['Nómina', 'Proveedores', 'Servicios']
        sizes = [totales['nominas'], totales['proveedores'], totales['servicios']]
        colores_pie = ['#fbbf24', '#f472b6', '#38bdf8']

        datos_filtrados = [(l, s, c) for l, s, c in zip(labels, sizes, colores_pie) if s > 0]
        
        ax2.set_facecolor('#2a2a3c')
        if datos_filtrados:
            labs, sers, cols = zip(*datos_filtrados)
            wedges, texts, autotexts = ax2.pie(
                sers, labels=labs, colors=cols, autopct='%1.1f%%', 
                startangle=140, textprops=dict(color="white", fontsize=8),
                wedgeprops=dict(edgecolor='#2a2a3c', linewidth=1.5)
            )
            for at in autotexts:
                at.set_fontsize(8)
        else:
            ax2.text(0, 0, "Sin egresos registrados", color="white", ha='center', va='center', fontsize=9)

        ax2.set_title("Distribución de Egresos", color='white', fontsize=10, fontweight='bold', pad=10)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        

    def actualizar_tabla_ingresos(self, f_inicio, f_fin):
        for widget in self.frame_ingresos_det.winfo_children():
            widget.destroy()

        tk.Label(self.frame_ingresos_det, text="📋 Detalle Ingresos", bg="#2a2a3c", fg="#10b981", font=("Arial", 9, "bold")).pack(anchor="w", padx=5, pady=(8, 5))

        tree_ingresos = ttk.Treeview(self.frame_ingresos_det, columns=("Fuente", "Monto"), show="headings", height=20)
        tree_ingresos.heading("Fuente", text="Concepto")
        tree_ingresos.heading("Monto", text="Total ($)")
        tree_ingresos.column("Fuente", width=170)
        tree_ingresos.column("Monto", width=110, anchor="e")

        scrollbar_ing = ttk.Scrollbar(self.frame_ingresos_det, orient="vertical", command=tree_ingresos.yview)
        tree_ingresos.configure(yscrollcommand=scrollbar_ing.set)

        tree_ingresos.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar_ing.pack(side="right", fill="y", pady=5)

        lista_ingresos_detalle = self.service.obtener_todos_los_ingresos(f_inicio, f_fin)
        resumen_categorias = {}
        for ing in lista_ingresos_detalle:
            cat = ing.get("categoria", "Otros")
            monto = float(ing.get("monto", 0.0))
            resumen_categorias[cat] = resumen_categorias.get(cat, 0.0) + monto

        if not resumen_categorias:
            tree_ingresos.insert("", "end", values=("Sin registros", "$ 0"))
        else:
            for cat, monto in resumen_categorias.items():
                tree_ingresos.insert("", "end", values=(cat, f"$ {monto:,.0f}"))

    def actualizar_tabla_egresos(self, f_inicio, f_fin):
        for widget in self.frame_egresos_det.winfo_children():
            widget.destroy()

        tk.Label(self.frame_egresos_det, text="📋 Detalle Egresos", bg="#2a2a3c", fg="#ef4444", font=("Arial", 9, "bold")).pack(anchor="w", padx=5, pady=(8, 5))

        tree_egresos = ttk.Treeview(self.frame_egresos_det, columns=("Concepto", "Monto"), show="headings", height=20)
        tree_egresos.heading("Concepto", text="Concepto / Servicio")
        tree_egresos.heading("Monto", text="Total ($)")
        tree_egresos.column("Concepto", width=170)
        tree_egresos.column("Monto", width=110, anchor="e")

        scrollbar_eg = ttk.Scrollbar(self.frame_egresos_det, orient="vertical", command=tree_egresos.yview)
        tree_egresos.configure(yscrollcommand=scrollbar_eg.set)

        tree_egresos.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar_eg.pack(side="right", fill="y", pady=5)

        resumen_egresos = {}
        try:
            transacciones = self.service.coleccion.find({"tipo": {"$in": ["EGRESO", "SERVICIO", "PROVEEDOR"]}})
            for t in transacciones:
                f_trans = str(t.get("fecha", t.get("fecha_creacion", "")))[:10]
                if f_inicio and f_fin and not (f_inicio <= f_trans <= f_fin):
                    continue
                
                concepto = t.get("descripcion") or t.get("categoria") or "Egreso General"
                monto = float(t.get("monto", 0.0))
                resumen_egresos[concepto] = resumen_egresos.get(concepto, 0.0) + monto
        except Exception as e:
            print(f"Error al cargar detalle de egresos: {e}")

        if not resumen_egresos:
            tree_egresos.insert("", "end", values=("Sin registros", "$ 0"))
        else:
            for concepto, monto in resumen_egresos.items():
                tree_egresos.insert("", "end", values=(concepto, f"$ {monto:,.0f}"))