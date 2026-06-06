import csv
import datetime
import os
import sqlite3
from typing import List, Tuple


class FinanzasModelo:
    """Maneja de forma exclusiva la base de datos y la exportación de archivos."""

    def __init__(self, db_name: str = "finanzas_hogar.db") -> None:
        self.db_name = db_name
        self._crear_tablas()

    def _conectar(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_name)

    def _crear_tablas(self) -> None:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS transacciones_actuales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    monto REAL NOT NULL,
                    descripcion TEXT NOT NULL,
                    fecha TEXT NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS historico_mensual (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mes_año TEXT UNIQUE NOT NULL,
                    total_ingresos REAL NOT NULL,
                    total_egresos REAL NOT NULL,
                    saldo REAL NOT NULL
                )
            """
            )
            conn.commit()

    def registrar_transaccion(self, tipo: str, monto: float, descripcion: str) -> None:
        fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO transacciones_actuales (tipo, monto, descripcion, fecha) VALUES (?, ?, ?, ?)",
                (tipo, monto, descripcion, fecha_hoy),
            )
            conn.commit()

    def obtener_transacciones_actuales(self) -> List[Tuple[int, str, float, str, str]]:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tipo, monto, descripcion, fecha FROM transacciones_actuales ORDER BY id DESC")
            return cursor.fetchall()

    def calcular_totales_actuales(self) -> Tuple[float, float, float]:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(monto) FROM transacciones_actuales WHERE tipo = 'Ingreso'")
            ingresos = cursor.fetchone()[0] or 0.0

            cursor.execute("SELECT SUM(monto) FROM transacciones_actuales WHERE tipo = 'Egreso'")
            egresos = cursor.fetchone()[0] or 0.0

            return ingresos, egresos, (ingresos - egresos)

    def cerrar_mes_actual(self, mes_año: str) -> None:
        ingresos, egresos, saldo = self.calcular_totales_actuales()
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO historico_mensual (mes_año, total_ingresos, total_egresos, saldo) VALUES (?, ?, ?, ?)",
                (mes_año, ingresos, egresos, saldo),
            )
            cursor.execute("DELETE FROM transacciones_actuales")
            conn.commit()

    def obtener_historico(self) -> List[Tuple[str, float, float, float]]:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT mes_año, total_ingresos, total_egresos, saldo FROM historico_mensual ORDER BY mes_año DESC")
            return cursor.fetchall()

    def exportar_a_csv(self, nombre_archivo: str = "reporte_finanzas.csv") -> str:
        try:
            with open(nombre_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["--- RESUMEN HISTÓRICO DE MESES ---"])
                writer.writerow(["Mes/Año", "Total Ingresos", "Total Egresos", "Saldo Neto"])
                for fila in self.obtener_historico():
                    writer.writerow(fila)
                writer.writerow([])
                writer.writerow(["--- DETALLE DE MOVIMIENTOS DEL MES ACTUAL ---"])
                writer.writerow(["ID", "Tipo", "Monto", "Descripción", "Fecha"])
                for fila in self.obtener_transacciones_actuales():
                    writer.writerow(fila)
            return os.path.abspath(nombre_archivo)
        except IOError as e:
            raise RuntimeError(f"Error al escribir el archivo CSV: {e}")