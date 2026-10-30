import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def dibujar_automata(automata, frame_contenedor):
    """Dibuja el autómata en un frame de Tkinter."""
    try:
        # Limpiar frame anterior
        for widget in frame_contenedor.winfo_children():
            widget.destroy()

        # Sin estados: mostrar mensaje
        if not automata.estados:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.text(0.5, 0.5, "Sin estados aún\nCrea un autómata primero",
                    ha='center', va='center', fontsize=12, color='gray')
            ax.axis('off')
            canvas = FigureCanvasTkAgg(fig, master=frame_contenedor)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            plt.close(fig)
            return
# Aquí irá el código para dibujar autómatas con networkx + matplotlib
