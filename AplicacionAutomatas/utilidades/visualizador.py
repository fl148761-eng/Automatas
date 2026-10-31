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
            
        # Dibujar nodos
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colores,
                               node_size=2500, edgecolors='#333333', linewidths=2)

        # Dibujar textos de los nodos (más grandes)
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=11, font_weight='bold', font_color='#000000')

        # Separar aristas (rectas, curvas y auto-loops)
        aristas_rectas = []
        aristas_curvas = []
        auto_loops = []
        for u, v in G.edges():
            if u == v:
                auto_loops.append((u, v))
            elif G.has_edge(v, u):
                aristas_curvas.append((u, v))
            else:
                aristas_rectas.append((u, v))
                
        # Dibujar aristas más gruesas y oscuras
        if aristas_rectas:
            nx.draw_networkx_edges(G, pos, edgelist=aristas_rectas, ax=ax,
                                   arrows=True, arrowsize=25, edge_color='#555555',
                                   width=2.0, node_size=2500)

        if aristas_curvas:
            nx.draw_networkx_edges(G, pos, edgelist=aristas_curvas, ax=ax,
                                   arrows=True, arrowsize=25, edge_color='#555555',
                                   width=2.0, connectionstyle='arc3,rad=0.2', node_size=2500)

        # Auto-loops
        for u, v in auto_loops:
            x, y = pos[u]
            ax.annotate('', xy=(x + 0.1, y + 0.15), xytext=(x - 0.1, y + 0.15),
                        arrowprops=dict(arrowstyle='->', color='#555555',
                                        lw=2.0, connectionstyle='arc3,rad=1.5'))

        # Etiquetas de aristas (con fondo blanco para que se lean bien)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=etiquetas, ax=ax,
                                     font_size=10, font_color='#cc0000',
                                     bbox=dict(boxstyle='round,pad=0.3',
                                               fc='white', ec='#cccccc', alpha=0.9))

        # Flecha del estado inicial
        if automata.estado_inicial:
            x0, y0 = pos[automata.estado_inicial.id]
            ax.annotate('', xy=(x0 - 0.15, y0), xytext=(x0 - 0.5, y0),
                        arrowprops=dict(arrowstyle='->', color='blue', lw=2.5))
            ax.text(x0 - 0.6, y0 + 0.05, 'inicio',
                    fontsize=9, color='blue', fontweight='bold')
    
