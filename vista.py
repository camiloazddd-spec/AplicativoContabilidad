import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk  
from modelo import FinanzasModelo

# Configuración del estilo moderno
ctk.set_appearance_mode("Light")  
ctk.set_default_color_theme("blue")  


class FinanzasApp:
    """Clase encargada de la interfaz gráfica estilizada y moderna."""

    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.root.title("Mis Finanzas Diarias")
        self.root.geometry("800x700")
        self.root.resizable(False, False)

        self.modelo = FinanzasModelo()
        self._crear_componentes()
        self._actualizar_interfaz()

    def _crear_componentes(self) -> None:
        # --- TÍTULO ---
        lbl_titulo = ctk.CTkLabel(
            self.root, 
            text="🌸 Mi Control de Finanzas Hogar 🌸", 
            font=("Segoe UI", 22, "bold"), 
            text_color="#2c3e50"
        )
        lbl_titulo.pack(pady=15)

        # --- PANEL DE REGISTRO (Bordes Curvos) ---
        frame_registro = ctk.CTkFrame(self.root, corner_radius=15)
        frame_registro.pack(fill="x", padx=20, pady=10)

        lbl_tipo = ctk.CTkLabel(frame_registro, text="Tipo:", font=("Segoe UI", 12, "bold"))
        lbl_tipo.grid(row=0, column=0, padx=10, pady=15, sticky="w")
        
        self.combo_tipo = ctk.CTkComboBox(frame_registro, values=["Ingreso", "Egreso"], state="readonly", width=110)
        self.combo_tipo.set("Ingreso")
        self.combo_tipo.grid(row=0, column=1, padx=10, pady=15)

        lbl_monto = ctk.CTkLabel(frame_registro, text="Monto ($):", font=("Segoe UI", 12, "bold"))
        lbl_monto.grid(row=0, column=2, padx=10, pady=15, sticky="w")
        
        self.entry_monto = ctk.CTkEntry(frame_registro, placeholder_text="Ej: 5000", width=110)
        self.entry_monto.grid(row=0, column=3, padx=10, pady=15)

        lbl_desc = ctk.CTkLabel(frame_registro, text="Detalle:", font=("Segoe UI", 12, "bold"))
        lbl_desc.grid(row=0, column=4, padx=10, pady=15, sticky="w")
        
        self.entry_desc = ctk.CTkEntry(frame_registro, placeholder_text="¿En qué se gastó o ganó?", width=200)
        self.entry_desc.grid(row=0, column=5, padx=10, pady=15)

        btn_guardar = ctk.CTkButton(
            frame_registro, text="Guardar", fg_color="#2ecc71", hover_color="#27ae60", 
            font=("Segoe UI", 13, "bold"), width=100, command=self._ejecutar_guardado
        )
        btn_guardar.grid(row=0, column=6, padx=15, pady=15)

        # --- TARJETAS DE COLORES (Dashboard) ---
        frame_totales = ctk.CTkFrame(self.root, fg_color="transparent")
        frame_totales.pack(fill="x", padx=20, pady=10)

        card_ingresos = ctk.CTkFrame(frame_totales, fg_color="#e8f8f5", corner_radius=10, height=70)
        card_ingresos.pack(side="left", expand=True, fill="both", padx=5)
        self.lbl_ingresos = ctk.CTkLabel(card_ingresos, text="Ingresos: $0.00", font=("Segoe UI", 14, "bold"), text_color="#117a65")
        self.lbl_ingresos.pack(expand=True)

        card_egresos = ctk.CTkFrame(frame_totales, fg_color="#fdedec", corner_radius=10, height=70)
        card_egresos.pack(side="left", expand=True, fill="both", padx=5)
        self.lbl_egresos = ctk.CTkLabel(card_egresos, text="Egresos: $0.00", font=("Segoe UI", 14, "bold"), text_color="#922b21")
        self.lbl_egresos.pack(expand=True)

        card_saldo = ctk.CTkFrame(frame_totales, fg_color="#ebf5fb", corner_radius=10, height=70)
        card_saldo.pack(side="left", expand=True, fill="both", padx=5)
        self.lbl_saldo = ctk.CTkLabel(card_saldo, text="Saldo: $0.00", font=("Segoe UI", 14, "bold"), text_color="#2471a3")
        self.lbl_saldo.pack(expand=True)

        # --- TABLAS DE DATOS ---
        frame_tablas = ctk.CTkFrame(self.root, fg_color="transparent")
        frame_tablas.pack(fill="both", expand=True, padx=20, pady=10)

        lbl_tabla_act = ctk.CTkLabel(frame_tablas, text="📋 Movimientos del Mes Actual", font=("Segoe UI", 13, "bold"), text_color="#34495e")
        lbl_tabla_act.pack(anchor="w", pady=(5, 2))
        
        style = tk.ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=25, background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#d5dbdb", foreground="#2c3e50")

        self.tabla_actual = tk.ttk.Treeview(frame_tablas, columns=("tipo", "monto", "desc", "fecha"), show="headings", height=5)
        self.tabla_actual.heading("tipo", text="Tipo")
        self.tabla_actual.heading("monto", text="Monto")
        self.tabla_actual.heading("desc", text="Detalle o Descripción")
        self.tabla_actual.heading("fecha", text="Fecha")
        self.tabla_actual.column("tipo", width=100, anchor="center")
        self.tabla_actual.column("monto", width=120, anchor="e")
        self.tabla_actual.column("desc", width=380, anchor="w")
        self.tabla_actual.column("fecha", width=120, anchor="center")
        self.tabla_actual.pack(fill="x", pady=5)

        lbl_tabla_hist = ctk.CTkLabel(frame_tablas, text="📊 Comparativa de Meses Anteriores", font=("Segoe UI", 13, "bold"), text_color="#34495e")
        lbl_tabla_hist.pack(anchor="w", pady=(10, 2))

        self.tabla_historial = tk.ttk.Treeview(frame_tablas, columns=("mes", "ing", "egr", "sal"), show="headings", height=4)
        self.tabla_historial.heading("mes", text="Mes Evaluado")
        self.tabla_historial.heading("ing", text="Total Ingresos")
        self.tabla_historial.heading("egr", text="Total Egresos")
        self.tabla_historial.heading("sal", text="Saldo Guardado")
        self.tabla_historial.column("mes", width=150, anchor="center")
        self.tabla_historial.column("ing", width=170, anchor="e")
        self.tabla_historial.column("egr", width=170, anchor="e")
        self.tabla_historial.column("sal", width=170, anchor="e")
        self.tabla_historial.pack(fill="x", pady=5)

        # --- BOTONES DE ACCIÓN ---
        frame_acciones = ctk.CTkFrame(self.root, fg_color="transparent")
        frame_acciones.pack(fill="x", padx=20, pady=20)

        btn_descargar = ctk.CTkButton(
            frame_acciones, text="📥 Guardar Reporte para Excel", fg_color="#34495e", 
            hover_color="#2c3e50", font=("Segoe UI", 12, "bold"), command=self._ejecutar_exportacion
        )
        btn_descargar.pack(side="left")

        btn_cerrar_mes = ctk.CTkButton(
            frame_acciones, text="🔒 Cerrar Mes y Archivar", fg_color="#e74c3c", 
            hover_color="#c0392b", font=("Segoe UI", 12, "bold"), command=self._ejecutar_gierre_mes
        )
        btn_cerrar_mes.pack(side="right")

    def _actualizar_interfaz(self) -> None:
        for item in self.tabla_actual.get_children():
            self.tabla_actual.delete(item)
        for item in self.tabla_historial.get_children():
            self.tabla_historial.delete(item)

        for _, tipo, monto, desc, fecha in self.modelo.obtener_transacciones_actuales():
            self.tabla_actual.insert("", "end", values=(tipo, f"${monto:,.2f}", desc, fecha))

        self.tabla_historial.tag_configure("saldo_positivo", foreground="#27ae60", font=("Segoe UI", 11, "bold"))
        self.tabla_historial.tag_configure("saldo_negativo", foreground="#c0392b", font=("Segoe UI", 11, "bold"))

        for mes, ing, egr, sal in self.modelo.obtener_historico():
            tag_color = "saldo_positivo" if sal >= 0 else "saldo_negativo"
            self.tabla_historial.insert("", "end", values=(mes, f"${ing:,.2f}", f"${egr:,.2f}", f"${sal:,.2f}"), tags=(tag_color,))

        ing, egr, sal = self.modelo.calcular_totales_actuales()
        self.lbl_ingresos.configure(text=f"Total Ingresos:\n${ing:,.2f}")
        self.lbl_egresos.configure(text=f"Total Egresos:\n${egr:,.2f}")
        
        if sal >= 0:
            self.lbl_saldo.configure(text=f"Saldo Neto (A Favor):\n${sal:,.2f}", text_color="#1f618d")
        else:
            self.lbl_saldo.configure(text=f"Saldo Neto (En Contra):\n${sal:,.2f}", text_color="#922b21")

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

    def _ejecutar_gierre_mes(self) -> None:
        periodo_sugerido = datetime.date.today().strftime("%Y-%m")
        mes_año = simpledialog.askstring("Cerrar Período", "¿Qué mes deseas archivar? (Año-Mes):\nEjemplo: 2026-05", initialvalue=periodo_sugerido, parent=self.root)
        
        if not mes_año:
            return  

        partes = mes_año.split("-")
        if len(partes) != 2 or not (partes[0].isdigit() and partes[1].isdigit()) or len(partes[0]) != 4:
            messagebox.showerror("Fecha Incorrecta", "Usa el formato Año-Mes. Ejemplo: 2026-05")
            return

        if messagebox.askyesno("Confirmar Cierre", f"¿Estás segura de que deseas cerrar y archivar los datos de {mes_año}?\n\nLa pantalla actual se reiniciará para el próximo mes.", parent=self.root):
            self.modelo.cerrar_mes_actual(mes_año)
            self._actualizar_interfaz()
            messagebox.showinfo("Proceso Completo", f"Los datos de {mes_año} han sido archivados correctamente.")

    def _ejecutar_exportacion(self) -> None:
        try:
            ruta = self.modelo.exportar_a_csv()
            messagebox.showinfo("Reporte Guardado", f"¡Excelente! Tu archivo Excel se ha guardado en la siguiente ruta:\n\n{ruta}")
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))