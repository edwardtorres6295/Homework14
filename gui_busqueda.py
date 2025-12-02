# Modificación 2 para Homework 14
print("Modificación 2 ejecutada")

# gui_busqueda.py
# GUI simple para consultar la tabla `marathon_small` en MySQL
# Requiere: pip install sqlalchemy pymysql mysql-connector-python

import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import create_engine, text
from typing import Optional, Dict, Any, List

# ========= CONFIG DB =========
ENGINE_URL = "mysql+pymysql://root:MySQL2025@localhost/DB_MySQL?charset=utf8mb4"
TABLE_NAME = "marathon_small"

# ========= CONEXIÓN GLOBAL =========
engine = create_engine(
    ENGINE_URL,
    pool_pre_ping=True,
)

def run_query(sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Ejecuta una consulta y regresa una lista de diccionarios.
    Cada diccionario = una fila {columna: valor}.
    Compatible con Python 3.9 (sin pandas).
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        cols = result.keys()
        rows = [dict(zip(cols, row)) for row in result.fetchall()]
    return rows

# ========= APP =========
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Filtrando Información (MySQL)")
        self.geometry("860x560")
        self.minsize(860, 560)

        # Marco principal
        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        # Grupo "Consulta por Id"
        grp = ttk.LabelFrame(main, text="Consulta por Id")
        grp.pack(fill="x")

        # Vars
        self.var_id = tk.StringVar(value="")
        self.var_name = tk.StringVar(value="")
        self.var_gender = tk.StringVar(value="")
        self.var_home = tk.StringVar(value="")
        self.var_time = tk.StringVar(value="")

        # Fila 1: Id
        ttk.Label(grp, text="Id:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.ent_id = ttk.Entry(grp, textvariable=self.var_id, width=20)
        self.ent_id.grid(row=0, column=1, sticky="w", padx=6, pady=6)

        # Fila 2: Nombre
        ttk.Label(grp, text="Nombre:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.ent_name = ttk.Entry(grp, textvariable=self.var_name, width=60, state="readonly")
        self.ent_name.grid(row=1, column=1, columnspan=3, sticky="we", padx=6, pady=6)

        # Fila 3: Género
        ttk.Label(grp, text="Género:").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.ent_gender = ttk.Entry(grp, textvariable=self.var_gender, width=10, state="readonly")
        self.ent_gender.grid(row=2, column=1, sticky="w", padx=6, pady=6)

        # Fila 4: Home (Country)
        ttk.Label(grp, text="Ciudad/Home:").grid(row=3, column=0, sticky="e", padx=6, pady=6)
        self.ent_home = ttk.Entry(grp, textvariable=self.var_home, width=15, state="readonly")
        self.ent_home.grid(row=3, column=1, sticky="w", padx=6, pady=6)

        # Fila 5: Tiempo
        ttk.Label(grp, text="Tiempo (min):").grid(row=4, column=0, sticky="e", padx=6, pady=6)
        self.ent_time = ttk.Entry(grp, textvariable=self.var_time, width=15, state="readonly")
        self.ent_time.grid(row=4, column=1, sticky="w", padx=6, pady=6)

        # Botones
        btns = ttk.Frame(grp)
        btns.grid(row=5, column=0, columnspan=4, pady=(8, 4))
        ttk.Button(btns, text="Buscar", command=self.buscar_por_id).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Borrar", command=self.limpiar).grid(row=0, column=1, padx=6)

        for i in range(4):
            grp.columnconfigure(i, weight=1)

        # Separador
        ttk.Separator(main).pack(fill="x", pady=8)

        # Filtro y lista
        tools = ttk.Frame(main)
        tools.pack(fill="x")
        ttk.Label(tools, text="Filtrar género:").pack(side="left")
        self.var_filter = tk.StringVar(value="All")
        cbo = ttk.Combobox(
            tools,
            state="readonly",
            width=5,
            values=["All", "F", "M"],
            textvariable=self.var_filter
        )
        cbo.pack(side="left", padx=6)
        ttk.Button(tools, text="Listar", command=self.listar).pack(side="left", padx=6)

        # Tree
        cols = ("id", "Name", "Gender", "Country", "Finish Time")
        self.tree = ttk.Treeview(main, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120 if c != "Name" else 260, anchor="w")
        self.tree.pack(fill="both", expand=True, pady=(6, 0))

        # Status
        self.status = ttk.Label(main, text="Listo", anchor="w")
        self.status.pack(fill="x", pady=(6, 0))

        # Prueba de conexión
        try:
            _ = run_query(f"SELECT COUNT(*) AS n FROM {TABLE_NAME};")
            self.set_status(f"Conectado a MySQL. Tabla '{TABLE_NAME}' OK.")
        except Exception as e:
            messagebox.showerror("Error de conexión", str(e))
            self.set_status("Error de conexión. Revisa ENGINE_URL/DB.")

    # ====== LÓGICA ======
    def set_status(self, msg: str):
        self.status.config(text=msg)

    def limpiar(self):
        self.var_id.set("")
        self.var_name.set("")
        self.var_gender.set("")
        self.var_home.set("")
        self.var_time.set("")
        for r in self.tree.get_children():
            self.tree.delete(r)
        self.set_status("Campos y tabla limpiados.")

    def buscar_por_id(self):
        raw = self.var_id.get().strip()
        if not raw.isdigit():
            messagebox.showwarning("Dato inválido", "Escribe un Id numérico.")
            self.ent_id.focus()
            return
        rid = int(raw)

        # Nota: `Finish Time` lleva backticks
        sql = f"""
            SELECT id, Name, Gender, Country, `Finish Time`
            FROM {TABLE_NAME}
            WHERE id = :rid
            LIMIT 1
        """
        try:
            rows = run_query(sql, {"rid": rid})
        except Exception as e:
            messagebox.showerror("Error de consulta", str(e))
            return

        if not rows:
            self.var_name.set("")
            self.var_gender.set("")
            self.var_home.set("")
            self.var_time.set("")
            self.set_status(f"Sin resultados para Id {rid}")
            return

        r = rows[0]
        self.var_name.set(r.get("Name", ""))
        self.var_gender.set(r.get("Gender", ""))
        self.var_home.set(r.get("Country", ""))
        self.var_time.set(str(r.get("Finish Time", "")))

        # También lo muestro en la tabla (limpio e inserto solo ese)
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.insert("", "end", values=(
            r.get("id", ""), r.get("Name", ""), r.get("Gender", ""),
            r.get("Country", ""), r.get("Finish Time", "")
        ))
        self.set_status(f"Resultado para Id {rid}")

    def listar(self):
        g = self.var_filter.get()
        if g == "All":
            sql = f"""
                SELECT id, Name, Gender, Country, `Finish Time`
                FROM {TABLE_NAME}
                LIMIT 200
            """
            params = {}
        else:
            sql = f"""
                SELECT id, Name, Gender, Country, `Finish Time`
                FROM {TABLE_NAME}
                WHERE Gender = :g
                LIMIT 200
            """
            params = {"g": g}

        try:
            rows = run_query(sql, params)
        except Exception as e:
            messagebox.showerror("Error de consulta", str(e))
            return

        # Poblar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in rows:
            self.tree.insert("", "end", values=(
                r.get("id", ""), r.get("Name", ""), r.get("Gender", ""),
                r.get("Country", ""), r.get("Finish Time", "")
            ))
        self.set_status(f"{len(rows)} filas listadas (género: {g}).")


if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Error fatal", str(e))
