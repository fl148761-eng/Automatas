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
            
  # Crear grafo
        G = nx.DiGraph()
        for e in automata.estados:
            G.add_node(e.id)

        # Etiquetas de aristas
        etiquetas = {}
        for e in automata.estados:
            for simbolo, destinos in e.transiciones.items():
                for d in destinos:
                    clave = (e.id, d.id)
                    if clave in etiquetas:
                        etiquetas[clave] += f", {simbolo}"
                    else:
                        etiquetas[clave] = simbolo
            for d in e.transiciones_epsilon:
                clave = (e.id, d.id)
                if clave in etiquetas:
                    etiquetas[clave] += ", ε"
                else:
                    etiquetas[clave] = "ε"

        for (origen, destino) in etiquetas.keys():
            G.add_edge(origen, destino)

        # Colores de nodos según tipo
        colores = []
        for nodo in G.nodes():
            estado = automata.obtener_estado(nodo)
            if estado.es_inicial and estado.es_final:
                colores.append('#ffb84d')  # Naranja
            elif estado.es_inicial:
                colores.append('#66ccff')  # Azul claro
            elif estado.es_final:
                colores.append('#99ff99')  # Verde claro
            else:
                colores.append('#e0e0e0')  # Gris claro

        # Crear figura más grande
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor('#ffffff')

        # Posiciones de los nodos (más separados)
        if len(G.nodes()) == 1:
            pos = {list(G.nodes())[0]: (0, 0)}
        else:
            pos = nx.spring_layout(G, seed=42, k=2.0, iterations=100)
