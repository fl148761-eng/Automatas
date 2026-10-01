class Estado:
    """Representa un estado de un autómata finito."""

    def __init__(self, id_estado, es_inicial=False, es_final=False):
        self.id = id_estado
        self.es_inicial = es_inicial
        self.es_final = es_final
        self.transiciones = {}  # símbolo -> [estados destino]
        self.transiciones_epsilon = []  # transiciones ε (solo NFA)

    def agregar_transicion(self, simbolo, destino):
        """Agrega una transición. Si el símbolo ya existe, agrega el destino
        a la lista (permite múltiples destinos, útil para NFA)."""
        if simbolo not in self.transiciones:
            self.transiciones[simbolo] = []
        if destino not in self.transiciones[simbolo]:
            self.transiciones[simbolo].append(destino)

    def agregar_transicion_epsilon(self, destino):
        if destino not in self.transiciones_epsilon:
            self.transiciones_epsilon.append(destino)

    def obtener_transiciones(self, simbolo):
        return self.transiciones.get(simbolo, [])

    def __repr__(self):
        return f"Estado({self.id})"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, otro):
        return isinstance(otro, Estado) and self.id == otro.id