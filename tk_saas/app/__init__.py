import tkinter as tk
from tkinter import ttk
from .ui import DashboardFrame, DataFrame, SettingsFrame
from .db import Database


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tk SaaS — Prototype")
        self.root.geometry("900x600")
        self.style = ttk.Style(self.root)
        # lightweight cross-platform theme
        try:
            self.style.theme_use('clam')
        except Exception:
            pass
        self.db = Database("tk_saas.db")
        self._build_ui()

    def _build_ui(self):
        sidebar = ttk.Frame(self.root, width=200)
        sidebar.pack(side="left", fill="y")
        main = ttk.Frame(self.root)
        main.pack(side="right", expand=True, fill="both")

        btn_dash = ttk.Button(sidebar, text="Dashboard", command=lambda: self.show_frame(DashboardFrame))
        btn_data = ttk.Button(sidebar, text="Data", command=lambda: self.show_frame(DataFrame))
        btn_settings = ttk.Button(sidebar, text="Settings", command=lambda: self.show_frame(SettingsFrame))
        btn_dash.pack(fill='x', padx=10, pady=10)
        btn_data.pack(fill='x', padx=10, pady=10)
        btn_settings.pack(fill='x', padx=10, pady=10)

        self.frames = {}
        for F in (DashboardFrame, DataFrame, SettingsFrame):
            frame = F(main, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)
        self.show_frame(DashboardFrame)

    def show_frame(self, cls):
        frame = self.frames[cls]
        frame.tkraise()

    def run(self):
        self.root.mainloop()
