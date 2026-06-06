import customtkinter as ctk
from vista import FinanzasApp


def main() -> None:
    """Punto de entrada principal usando la interfaz moderna."""
    # Lanzamos el motor gráfico moderno
    root = ctk.CTk()
    app = FinanzasApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()