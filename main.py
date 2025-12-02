"""
Arquivo principal do sistema gráfico
"""
import tkinter as tk
from graphics_system import SistemaGrafico


def main():
    """Função principal"""
    root = tk.Tk()
    app = SistemaGrafico(root)
    root.mainloop()


if __name__ == "__main__":
    main()
