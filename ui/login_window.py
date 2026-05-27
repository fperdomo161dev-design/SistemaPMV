import tkinter as tk
from tkinter import ttk, messagebox

from services.empleado_service import validar_credenciales
from ui.main_window import MainWindow

COLOR_BG = "#050509"
COLOR_CARD = "#0b0f19"
COLOR_TEXT = "#e5e7eb"
COLOR_GOLD = "#f5d26b"
COLOR_INPUT_BG = "#050509"
COLOR_SIDEBAR = "#020814"
COLOR_TOPBAR = "#050b16"


class LoginWindow(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("PMV - Login")
        self.configure(bg=COLOR_BG)

        try:
            self.state("zoomed")
        except Exception:
            self.attributes("-zoomed", True)

        self.var_usuario = tk.StringVar()
        self.var_clave = tk.StringVar()

        self._configurar_estilos()
        self._build_ui()

    # ESTILOS

    def _configurar_estilos(self):

        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Selah.Bg.TFrame",
            background=COLOR_BG
        )

        style.configure(
            "Selah.Card.TFrame",
            background=COLOR_CARD
        )

        style.configure(
            "Selah.Title.TLabel",
            background=COLOR_CARD,
            foreground=COLOR_GOLD,
            font=("Segoe UI", 22, "bold")
        )

        style.configure(
            "Selah.Label.TLabel",
            background=COLOR_CARD,
            foreground=COLOR_TEXT,
            font=("Segoe UI", 11)
        )

        style.configure(
            "Selah.Info.TLabel",
            background=COLOR_CARD,
            foreground="#9ca3af",
            font=("Segoe UI", 10)
        )

        style.configure(
            "Selah.Button.TButton",
            background=COLOR_SIDEBAR,
            foreground=COLOR_TEXT,
            font=("Segoe UI", 11, "bold"),
            padding=(18, 10),
            relief="flat",
            borderwidth=0
        )

        style.map(
            "Selah.Button.TButton",
            background=[("active", COLOR_GOLD)],
            foreground=[("active", "#111827")]
        )

    def _build_ui(self):

        outer = ttk.Frame(
            self,
            style="Selah.Bg.TFrame"
        )

        outer.pack(fill="both", expand=True)

        outer.rowconfigure(0, weight=1)
        outer.rowconfigure(1, weight=0)
        outer.rowconfigure(2, weight=1)

        outer.columnconfigure(0, weight=1)
        # CARD CENTRAL
        card = ttk.Frame(
            outer,
            style="Selah.Card.TFrame",
            padding=35
        )

        card.grid(
            row=1,
            column=0
        )
        # TITULOS
        ttk.Label(
            card,
            text="PMV",
            style="Selah.Title.TLabel"
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            card,
            text="Sistema de inventario de calzado",
            style="Selah.Info.TLabel"
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 25)
        )
        # USUARIO
        ttk.Label(
            card,
            text="Usuario",
            style="Selah.Label.TLabel"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=(0, 6)
        )

        entry_usuario = tk.Entry(
            card,
            textvariable=self.var_usuario,
            width=32,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
            relief="flat",
            font=("Segoe UI", 11),
            highlightthickness=1,
            highlightbackground=COLOR_TOPBAR,
            highlightcolor=COLOR_GOLD
        )

        entry_usuario.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            ipady=8,
            pady=(0, 15)
        )
        # CLAVE
        ttk.Label(
            card,
            text="Clave",
            style="Selah.Label.TLabel"
        ).grid(
            row=4,
            column=0,
            sticky="w",
            pady=(0, 6)
        )

        entry_clave = tk.Entry(
            card,
            textvariable=self.var_clave,
            width=32,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
            relief="flat",
            font=("Segoe UI", 11),
            show="*",
            highlightthickness=1,
            highlightbackground=COLOR_TOPBAR,
            highlightcolor=COLOR_GOLD
        )

        entry_clave.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="ew",
            ipady=8,
            pady=(0, 22)
        )

        # =========================
        # BOTON LOGIN
        # =========================

        btn_login = ttk.Button(
            card,
            text="Ingresar",
            style="Selah.Button.TButton",
            command=self._login
        )

        btn_login.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="ew"
        )
        # FOOTER
        ttk.Label(
            card,
            text="© PMV",
            style="Selah.Info.TLabel"
        ).grid(
            row=7,
            column=0,
            columnspan=2,
            pady=(20, 0)
        )

        self.bind(
            "<Return>",
            lambda e: self._login()
        )

        entry_usuario.focus_set()

    # LOGIN
    def _login(self):

        usuario = self.var_usuario.get().strip()
        clave = self.var_clave.get().strip()

        if not usuario or not clave:

            messagebox.showwarning(
                "Login",
                "Debes ingresar usuario y clave."
            )

            return

        empleado = validar_credenciales(
            usuario,
            clave
        )

        if not empleado:

            messagebox.showerror(
                "Login",
                "Usuario o clave incorrectos."
            )

            return

        self.withdraw()

        main = MainWindow(
            self,
            empleado
        )

        def al_cerrar_main():

            if self.winfo_exists():
                self.deiconify()

            try:
                main.destroy()
            except Exception:
                pass

        main.protocol(
            "WM_DELETE_WINDOW",
            al_cerrar_main
        )

    # RUN
    def run(self):

        self.mainloop()