import tkinter as tk
from tkinter import ttk
from .models import Item


class DashboardFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        ttk.Label(self, text="Dashboard", font=("Segoe UI", 18)).pack(pady=20)
        self.app = app
        self.refresh_btn = ttk.Button(self, text="Refresh", command=self.refresh)
        self.refresh_btn.pack(pady=10)
        self.summary = ttk.Label(self, text="")
        self.summary.pack(pady=10)
        self.refresh()

    def refresh(self):
        items = self.app.db.get_items()
        self.summary.configure(text=f"Items stored: {len(items)}")


class DataFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        ttk.Label(self, text="Data", font=("Segoe UI", 18)).pack(pady=20)
        self.app = app
        form = ttk.Frame(self)
        form.pack(pady=10)
        ttk.Label(form, text="Name").grid(row=0, column=0, sticky='w')
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var).grid(row=0, column=1)
        ttk.Label(form, text="Value").grid(row=1, column=0, sticky='w')
        self.value_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.value_var).grid(row=1, column=1)
        ttk.Button(form, text="Add", command=self.add_item).grid(row=2, column=0, columnspan=2, pady=10)
        self.tree = ttk.Treeview(self, columns=("name","value"), show="headings")
        self.tree.heading("name", text="Name")
        self.tree.heading("value", text="Value")
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)
        self.refresh()

    def add_item(self):
        name = self.name_var.get().strip()
        value = self.value_var.get().strip()
        if not name:
            return
        item = Item(name=name, value=value)
        self.app.db.add_item(item)
        self.name_var.set("")
        self.value_var.set("")
        self.refresh()

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        items = self.app.db.get_items()
        for it in items:
            self.tree.insert("", "end", values=(it['name'], it['value']))


class SettingsFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        ttk.Label(self, text="Settings", font=("Segoe UI", 18)).pack(pady=20)
        ttk.Label(self, text="No settings yet").pack()
