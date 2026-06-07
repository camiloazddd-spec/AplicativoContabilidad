import csv
import datetime
import os
import sqlite3
from typing import List, Tuple


class FinanzasModelo:
    """Maneja la base de datos con cierres diarios y cálculo de ahorro del 10%."""

    def __init__(self, db_name: str = "finanzas_hogar.db") -> None:
        self.db_name = db_name
        self._crear_tablas()

    def _conectar(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_name)

    def _crear_tablas(self) -> None:
        with self._conectar() as conn:
            cursor = conn.cursor()
            # Movimientos del día en curso
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
            # Historial cambiado a formato DIARIO con columna de ahorro
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS historico_diario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_dia TEXT UNIQUE NOT NULL,
                    total_ingresos REAL NOT NULL,
                    total_egresos REAL NOT NULL,
                    saldo_neto REAL NOT NULL,
                    ahorro_diez_porc REAL NOT NULL
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

    def calcular_totales_actuales(self) -> Tuple[float, float, float, float]:
        """Calcula ingresos, egresos, saldo y el 10% de ahorro sobre las ganancias (ingresos)."""
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(monto) FROM transacciones_actuales WHERE tipo = 'Ingreso'")
            ingresos = cursor.fetchone()[0] or 0.0

            cursor.execute("SELECT SUM(monto) FROM transacciones_actuales WHERE tipo = 'Egreso'")
            egresos = cursor.fetchone()[0] or 0.0

            saldo = ingresos - egresos
            # El ahorro se calcula como el 10% de los ingresos totales (ganancia total) del día
            ahorro = ingresos * 0.10
            
            return ingresos, egresos, saldo, ahorro

    def cerrar_dia_actual(self, fecha_dia: str) -> None:
        """Archiva el día actual calculando los totales y el ahorro, luego limpia el tablero."""
        ingresos, egresos, saldo, ahorro = self.calcular_totales_actuales()
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO historico_diario 
                (fecha_dia, total_ingresos, total_egresos, saldo_neto, ahorro_diez_porc) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (fecha_dia, ingresos, egresos, saldo, ahorro),
            )
            cursor.execute("DELETE FROM transacciones_actuales")
            conn.commit()

    def obtener_historico_diario(self) -> List[Tuple[str, float, float, float, float]]:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fecha_dia, total_ingresos, total_egresos, saldo_neto, ahorro_diez_porc FROM historico_diario ORDER BY fecha_dia DESC")
            return cursor.fetchall()

    def exportar_a_csv(self, nombre_archivo: str = "reporte_finanzas_diarias.csv") -> str:
        try:
            with open(nombre_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["--- RESUMEN HISTÓRICO POR DÍAS ---"])
                writer.writerow(["Fecha Día", "Total Ingresos", "Total Egresos", "Saldo Neto", "Ahorro Reservado (10%)"])
                for fila in self.obtener_historico_diario():
                    writer.writerow(fila)
                writer.writerow([])
                writer.writerow(["--- DETALLE DE MOVIMIENTOS EN EL DÍA ACTIVO ---"])
                writer.writerow(["ID", "Tipo", "Monto", "Descripción", "Fecha"])
                for fila in self.obtener_transacciones_actuales():
                    writer.writerow(fila)
            return os.path.abspath(nombre_archivo)
        except IOError as e:
            raise RuntimeError(f"Error al escribir el archivo CSV: {e}")