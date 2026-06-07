import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk  
from modelo import FinanzasModelo

ctk.set_appearance_mode("Light")  
ctk.set_default_color_theme("blue")  


class FinanzasApp:
    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.root.title("Mis Finanzas Diarias")
        self.root.geometry("850x720")
        self.root.resizable(False, False)

        self.modelo = FinanzasModelo()
        self._crear_componentes()
        self._actualizar_interfaz()

    def _crear_componentes(self) -> None:
        # --- TÍTULO ---
        lbl_titulo = ctk.CTkLabel(
            self.root, 
            text="🌸 Mi Control de Finanzas Hogar (Registro Diario) 🌸", 
            font=("Segoe UI", 20, "bold"), 
            text_color="#2c3e50"
        )
        lbl_titulo.pack(pady=12)

        # --- PANEL DE REGISTRO ---
        frame_registro = ctk.CTkFrame(self.root, corner_radius=15)
        frame_registro.pack(fill="x", padx=20, pady=5)

        lbl_tipo = ctk.CTkLabel(frame_registro, text="Tipo:", font=("Segoe UI", 12, "bold"))
        lbl_tipo.grid(row=0, column=0, padx=8, pady=12, sticky="w")
        
        self.combo_tipo = ctk.CTkComboBox(frame_registro, values=["Ingreso", "Egreso"], state="readonly", width=110)
        self.combo_tipo.set("Ingreso")
        self.combo_tipo.grid(row=0, column=1, padx=8, pady=12)

        lbl_monto = ctk.CTkLabel(frame_registro, text="Monto ($):", font=("Segoe UI", 12, "bold"))
        lbl_monto.grid(row=0, column=2, padx=8, pady=12, sticky="w")
        
        self.entry_monto = ctk.CTkEntry(frame_registro, placeholder_text="Ej: 5000", width=110)
        self.entry_monto.grid(row=0, column=3, padx=8, pady=12)

        lbl_desc = ctk.CTkLabel(frame_registro, text="Detalle:", font=("Segoe UI", 12, "bold"))
        lbl_desc.grid(row=0, column=4, padx=8, pady=12, sticky="w")
        
        self.entry_desc = ctk.CTkEntry(frame_registro, placeholder_text="¿En qué se gastó o ganó?", width=210)
        self.entry_desc.grid(row=0, column=5, padx=8, pady=12)

        btn_guardar = ctk.CTkButton(
            frame_registro, text="Guardar", fg_color="#2ecc71", hover_color="#27ae60", 
            font=("Segoe UI", 13, "bold"), width=90, command=self._ejecutar_guardado
        )
        btn_guardar.grid(row=0, column=6, padx=10, pady=12)

        # --- CUATRO TARJETAS DE TOTALES (Añadido Ahorro 10%) ---
        frame_totales = ctk.CTkFrame(self.root, fg_color="transparent")
        frame_totales.pack(fill="x", padx=20, pady=8)

        card_ingresos = ctk.CTkFrame(frame_totales, fg_color="#e8f8f5", corner_radius=10, height=65)
        card_ingresos.pack(side="left", expand=True, fill="both", padx=4)
        self.lbl_ingresos = ctk.CTkLabel(card_ingresos, text="Ingresos:\n$0.00", font=("Segoe UI", 12, "bold"), text_color="#117a65")
        self.lbl_ingresos.pack(expand=True)

        card_egresos = ctk.CTkFrame(frame_totales, fg_color="#fdedec", corner_radius=10, height=65)
        card_egresos.pack(side="left", expand=True, fill="both", padx=4)
        self.lbl_egresos = ctk.CTkLabel(card_egresos, text="Egresos:\n$0.00", font=("Segoe UI", 12, "bold"), text_color="#922b21")
        self.lbl_egresos.pack(expand=True)

        card_saldo = ctk.CTkFrame(frame_totales, fg_color="#ebf5fb", corner_radius=10, height=65)
        card_saldo.pack(side="left", expand=True, fill="both", padx=4)
        self.lbl_saldo = ctk.CTkLabel(card_saldo, text="Saldo Neto:\n$0.00", font=("Segoe UI", 12, "bold"), text_color="#2471a3")
        self.lbl_saldo.pack(expand=True)

        # NUEVA TARJETA: El Ahorro sugerido del día
        card_ahorro = ctk.CTkFrame(frame_totales, fg_color="#fef9e7", corner_radius=10, height=65)
        card_ahorro.pack(side="left", expand=True, fill="both", padx=4)
        self.lbl_ahorro = ctk.CTkLabel(card_ahorro, text="Ahorro (10%):\n$0.00", font=("Segoe UI", 12, "bold"), text_color="#b7950b")
        self.lbl_ahorro.pack(expand=True)

        # --- TABLAS ---
        frame_tablas = ctk.CTkFrame(self.root, fg_color="transparent")
        frame_tablas.pack(fill="both", expand=True, padx=20, pady=5)

        lbl_tabla_act = ctk.CTkLabel(frame_tablas, text="📋 Movimientos del Día Seleccionado", font=("Segoe UI", 13, "bold"), text_color="#34495e")
        lbl_tabla_act.pack(anchor="w", pady=(2, 2))
        
        style = tk.ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=24, background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#d5dbdb", foreground="#2c3e50")

        self.tabla_actual = tk.ttk.Treeview(frame_tablas, columns=("tipo", "monto", "desc", "fecha"), show="headings", height=5)
        self.tabla_actual.heading("tipo", text="Tipo")
        self.tabla_actual.heading("monto", text="Monto")
        self.tabla_actual.heading("desc", text="Detalle o Descripción")
        self.tabla_actual.heading("fecha", text="Fecha")
        self.tabla_actual.column("tipo", width=100, anchor="center")
        self.tabla_actual.column("monto", width=110, anchor="e")
        self.tabla_actual.column("desc", width=420, anchor="w")
        self.tabla_actual.column("fecha", width=120, anchor="center")
        self.tabla_actual.pack(fill="x", pady=4)

        lbl_tabla_hist = ctk.CTkLabel(frame_tablas, text="📊 Historial de Días Archivados y Completados", font=("Segoe UI", 13, "bold"), text_color="#34495e")
        lbl_tabla_hist.pack(anchor="w", pady=(8, 2))

        # Añadida columna de ahorro a la tabla histórica
        self.tabla_historial = tk.ttk.Treeview(frame_tablas, columns=("fecha", "ing", "egr", "sal", "ahr"), show="headings", height=5)
        self.tabla_historial.heading("fecha", text="Fecha del Día")
        self.tabla_historial.heading("ing", text="Total Ingresos")
        self.tabla_historial.heading("egr", text="Total Egresos")
        self.tabla_historial.heading("sal", text="Saldo Diario")
        self.tabla_historial.heading("ahr", text="💰 Ahorro (10%)")
        self.tabla_historial.column("fecha", width=130, anchor="center")
        self.tabla_historial.column("ing", width=140, anchor="e")
        self.tabla_historial.column("egr", width=140, anchor="e")
        self.tabla_historial.column("sal", width=140, anchor="e")
        self.tabla_historial.column("ahr", width=150, anchor="e")
        self.tabla_historial.pack(fill="x", pady=4)

        # --- BOTONES INFERIORES ---
        frame_acciones = ctk.CTkFrame(self.root, fg_color="transparent")
        frame_acciones.pack(fill="x", padx=20, pady=15)

        btn_descargar = ctk.CTkButton(
            frame_acciones, text="📥 Exportar Todo a Excel/CSV", fg_color="#34495e", 
            hover_color="#2c3e50", font=("Segoe UI", 12, "bold"), command=self._ejecutar_exportacion
        )
        btn_descargar.pack(side="left")

        btn_cerrar_dia = ctk.CTkButton(
            frame_acciones, text="🔒 Completar y Cerrar Día", fg_color="#e74c3c", 
            hover_color="#c0392b", font=("Segoe UI", 12, "bold"), command=self._ejecutar_cierre_dia
        )
        btn_cerrar_dia.pack(side="right")

    def _actualizar_interfaz(self) -> None:
        for item in self.tabla_actual.get_children():
            self.tabla_actual.delete(item)
        for item in self.tabla_historial.get_children():
            self.tabla_historial.delete(item)

        for _, tipo, monto, desc, fecha in self.modelo.obtener_transacciones_actuales():
            self.tabla_actual.insert("", "end", values=(tipo, f"${monto:,.2f}", desc, fecha))

        self.tabla_historial.tag_configure("saldo_positivo", foreground="#27ae60", font=("Segoe UI", 11, "bold"))
        self.tabla_historial.tag_configure("saldo_negativo", foreground="#c0392b", font=("Segoe UI", 11, "bold"))

        for fecha, ing, egr, sal, ahr in self.modelo.obtener_historico_diario():
            tag_color = "saldo_positivo" if sal >= 0 else "saldo_negativo"
            self.tabla_historial.insert("", "end", values=(fecha, f"${ing:,.2f}", f"${egr:,.2f}", f"${sal:,.2f}", f"${ahr:,.2f}"), tags=(tag_color,))

        ing, egr, sal, ahr = self.modelo.calcular_totales_actuales()
        self.lbl_ingresos.configure(text=f"Ingresos Hoy:\n${ing:,.2f}")
        self.lbl_egresos.configure(text=f"Egresos Hoy:\n${egr:,.2f}")
        self.lbl_ahorro.configure(text=f"Ahorro Diario (10%):\n${ahr:,.2f}")
        
        if sal >= 0:
            self.lbl_saldo.configure(text=f"Saldo Neto:\n${sal:,.2f}", text_color="#1f618d")
        else:
            self.lbl_saldo.configure(text=f"Saldo Neto:\n${sal:,.2f}", text_color="#922b21")

    def _ejecutar_guardado(self) -> None:
        tipo = self.combo_tipo.get()
        monto_str = self.entry_monto.get().strip()
        desc = self.entry_desc.get().strip()

        if not desc:
            messagebox.showwarning("Faltan datos", "Por favor, escribe un detalle de este movimiento.")
            return

        try:
            monto = float(monto_str)
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Monto Inválido", "Introduce un número válido mayor a 0.")
            return

        self.modelo.registrar_transaccion(tipo, monto, desc)
        self._actualizar_interfaz()
        self.entry_monto.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)

    def _ejecutar_cierre_dia(self) -> None:
        fecha_sugerida = datetime.date.today().strftime("%Y-%m-%d")
        fecha_dia = simpledialog.askstring("Completar Día", "¿Qué fecha deseas cerrar? (Año-Mes-Día):\nEjemplo: 2026-06-07", initialvalue=fecha_sugerida, parent=self.root)
        
        if not fecha_dia:
            return  

        partes = fecha_dia.split("-")
        if len(partes) != 3 or not (partes[0].isdigit() and partes[1].isdigit() and partes[2].isdigit()) or len(partes[0]) != 4:
            messagebox.showerror("Fecha Incorrecta", "Usa el formato Año-Mes-Día. Ejemplo: 2026-06-07")
            return

        if messagebox.askyesno("Confirmar Cierre", f"¿Deseas archivar y completar el día {fecha_dia}?\n\nEsto calculará tu ahorro del 10% y limpiará la pantalla para mañana.", parent=self.root):
            self.modelo.cerrar_dia_actual(fecha_dia)
            self._actualizar_interfaz()
            messagebox.showinfo("Día Completado", f"Los totales y ahorros del día {fecha_dia} se han archivado con éxito.")

    def _ejecutar_exportacion(self) -> None:
        try:
            ruta = self.modelo.exportar_a_csv()
            messagebox.showinfo("Reporte Descargado", f"¡Excelente! Tu archivo Excel de control diario se guardó en:\n\n{ruta}")
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))