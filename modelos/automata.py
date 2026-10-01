from .estado import Estado


class AutomataFinito:
    """Representa un autómata finito (DFA o NFA)."""

    def __init__(self, nombre="Automata", es_afn=False):
        self.nombre = nombre
        self.es_afn = es_afn
        self.estados = []
        self.estado_inicial = None
        self.estados_finales = []
        self.alfabeto = set()
        self.logs_simulacion = []

    # ---------- GESTIÓN DE ESTADOS ----------
    def agregar_estado(self, id_estado, es_inicial=False, es_final=False):
        if self.obtener_estado(id_estado):
            raise ValueError(f"El estado '{id_estado}' ya existe")
        estado = Estado(id_estado, es_inicial, es_final)
        self.estados.append(estado)
        if es_inicial:
            self.establecer_inicial(id_estado)
        if es_final:
            self.estados_finales.append(estado)
        return estado

    def obtener_estado(self, id_estado):
        for e in self.estados:
            if e.id == id_estado:
                return e
        return None

    def eliminar_estado(self, id_estado):
        estado = self.obtener_estado(id_estado)
        if not estado:
            return
        self.estados.remove(estado)
        if self.estado_inicial == estado:
            self.estado_inicial = None
        if estado in self.estados_finales:
            self.estados_finales.remove(estado)
        # Limpiar referencias
        for e in self.estados:
            for simbolo in list(e.transiciones.keys()):
                if estado in e.transiciones[simbolo]:
                    e.transiciones[simbolo].remove(estado)
            if estado in e.transiciones_epsilon:
                e.transiciones_epsilon.remove(estado)

    def establecer_inicial(self, id_estado):
        estado = self.obtener_estado(id_estado)
        if not estado:
            raise ValueError(f"Estado '{id_estado}' no encontrado")
        if self.estado_inicial:
            self.estado_inicial.es_inicial = False
        estado.es_inicial = True
        self.estado_inicial = estado

    def establecer_final(self, id_estado, es_final=True):
        estado = self.obtener_estado(id_estado)
        if not estado:
            raise ValueError(f"Estado '{id_estado}' no encontrado")
        estado.es_final = es_final
        if es_final and estado not in self.estados_finales:
            self.estados_finales.append(estado)
        elif not es_final and estado in self.estados_finales:
            self.estados_finales.remove(estado)

    def establecer_alfabeto(self, simbolos):
        if isinstance(simbolos, str):
            self.alfabeto = set(c for c in simbolos if c not in ', ')
        else:
            self.alfabeto = set(simbolos)

    # ---------- TRANSICIONES ----------
    def agregar_transicion(self, desde_id, simbolo, hacia_id):
        desde = self.obtener_estado(desde_id)
        hacia = self.obtener_estado(hacia_id)
        if not desde or not hacia:
            raise ValueError("Estados origen o destino no encontrados")

        if simbolo in ('ε', 'epsilon', ''):
            # Transición épsilon: solo válida en NFA
            if not self.es_afn:
                raise ValueError("Un DFA no puede tener transiciones épsilon (ε)")
            desde.agregar_transicion_epsilon(hacia)
        else:
            # Validar que el símbolo esté en el alfabeto
            if self.alfabeto and simbolo not in self.alfabeto:
                alfabeto_ordenado = ', '.join(sorted(self.alfabeto))
                raise ValueError(
                    f"El símbolo '{simbolo}' no pertenece al alfabeto.\n"
                    f"Alfabeto permitido: {{{alfabeto_ordenado}}}"
                )

            if not self.es_afn:
                existentes = desde.obtener_transiciones(simbolo)
                if existentes and existentes[0] != hacia:
                    raise ValueError(
                        f"DFA inválido: '{desde.id}' ya tiene una transición con "
                        f"'{simbolo}' hacia '{existentes[0].id}'.\n"
                        f"Un DFA solo permite una transición por símbolo.\n"
                        f"Use un NFA si necesita varias."
                    )

            # Agregar la transición (esto funciona igual para NFA y DFA)
            desde.agregar_transicion(simbolo, hacia)
            self.alfabeto.add(simbolo)

    # ---------- CIERRE EPSILON ----------
    def cierre_epsilon(self, estados):
        """Calcula el cierre épsilon de un conjunto de estados."""
        cierre = set(estados)
        pila = list(estados)
        while pila:
            actual = pila.pop()
            for destino in actual.transiciones_epsilon:
                if destino not in cierre:
                    cierre.add(destino)
                    pila.append(destino)
        return cierre

    # ---------- SIMULACIÓN ----------
    def simular(self, cadena):
        self.logs_simulacion = []
        self.logs_simulacion.append(f"=== Simulación: '{cadena}' ===")
        self.logs_simulacion.append(f"Autómata: {self.nombre} ({'NFA' if self.es_afn else 'DFA'})")

        if self.es_afn:
            return self._simular_afn(cadena)
        return self._simular_afd(cadena)

    def _simular_afd(self, cadena):
        if not self.estado_inicial:
            self.logs_simulacion.append("✗ No hay estado inicial")
            return False

        actual = self.estado_inicial
        self.logs_simulacion.append(f"Inicio: {actual.id}")

        for simbolo in cadena:
            self.logs_simulacion.append(f"Leyendo: '{simbolo}'")
            destinos = actual.obtener_transiciones(simbolo)
            if not destinos:
                self.logs_simulacion.append(f"  ✗ Sin transición para '{simbolo}'")
                self.logs_simulacion.append("Resultado: RECHAZADO")
                return False
            actual = destinos[0]
            self.logs_simulacion.append(f"  → {actual.id}")

        aceptada = actual.es_final
        self.logs_simulacion.append(f"Estado final alcanzado: {actual.id}")
        self.logs_simulacion.append(f"Resultado: {'ACEPTADO' if aceptada else 'RECHAZADO'}")
        return aceptada

    def _simular_afn(self, cadena):
        if not self.estado_inicial:
            self.logs_simulacion.append("✗ No hay estado inicial")
            return False

        estados_actuales = self.cierre_epsilon({self.estado_inicial})
        self.logs_simulacion.append(f"Inicio (cierre): {{{', '.join(e.id for e in estados_actuales)}}}")

        for simbolo in cadena:
            if simbolo not in self.alfabeto:
                self.logs_simulacion.append(f"  ✗ Símbolo '{simbolo}' no está en el alfabeto")
                self.logs_simulacion.append("Resultado: RECHAZADO")
                return False

            self.logs_simulacion.append(f"Leyendo: '{simbolo}'")
            siguientes = set()
            for e in estados_actuales:
                for destino in e.obtener_transiciones(simbolo):
                    siguientes.add(destino)

            if not siguientes:
                self.logs_simulacion.append("  ✗ Sin transiciones")
                self.logs_simulacion.append("Resultado: RECHAZADO")
                return False

            estados_actuales = self.cierre_epsilon(siguientes)
            self.logs_simulacion.append(f"  → {{{', '.join(e.id for e in estados_actuales)}}}")

        aceptada = any(e.es_final for e in estados_actuales)
        self.logs_simulacion.append(f"Estados alcanzados: {{{', '.join(e.id for e in estados_actuales)}}}")
        self.logs_simulacion.append(f"Resultado: {'ACEPTADO' if aceptada else '❌ RECHAZADA'}")
        return aceptada

    # ---------- CONVERSIÓN NFA → DFA ----------
    def afn_a_afd(self):
        if not self.es_afn:
            raise ValueError("El autómata ya es un DFA")
        if not self.estado_inicial:
            raise ValueError("El NFA no tiene estado inicial")

        dfa = AutomataFinito(f"{self.nombre}_DFA", es_afn=False)
        dfa.establecer_alfabeto(self.alfabeto)

        cierre_inicial = frozenset(self.cierre_epsilon({self.estado_inicial}))

        mapa_estados = {}
        cola = [cierre_inicial]

        id_inicial = self._estados_a_id(cierre_inicial)
        estado_inicial_dfa = dfa.agregar_estado(id_inicial, es_inicial=True)
        mapa_estados[cierre_inicial] = estado_inicial_dfa

        if any(e.es_final for e in cierre_inicial):
            dfa.establecer_final(id_inicial, True)

        while cola:
            conjunto_actual = cola.pop(0)
            estado_actual = mapa_estados[conjunto_actual]

            for simbolo in sorted(self.alfabeto):
                siguiente_conjunto = set()
                for e in conjunto_actual:
                    for destino in e.obtener_transiciones(simbolo):
                        siguiente_conjunto.add(destino)

                if not siguiente_conjunto:
                    continue

                cierre = frozenset(self.cierre_epsilon(siguiente_conjunto))

                if cierre not in mapa_estados:
                    nuevo_id = self._estados_a_id(cierre)
                    nuevo_estado = dfa.agregar_estado(nuevo_id)
                    mapa_estados[cierre] = nuevo_estado
                    cola.append(cierre)

                    if any(e.es_final for e in cierre):
                        dfa.establecer_final(nuevo_id, True)

                estado_actual.agregar_transicion(simbolo, mapa_estados[cierre])

        return dfa

    def _estados_a_id(self, conjunto_estados):
        ids = sorted(e.id for e in conjunto_estados)
        return "{" + ",".join(ids) + "}"

    # ---------- MINIMIZACIÓN DFA ----------
    def minimizar(self):
        if self.es_afn:
            raise ValueError("Primero convierta el NFA a DFA")
        if len(self.estados) <= 1:
            return self

        estados = list(self.estados)
        n = len(estados)
        indice = {e: i for i, e in enumerate(estados)}

        distinguibles = [[False] * n for _ in range(n)]

        # Marcar pares (final, no final)
        for i in range(n):
            for j in range(i + 1, n):
                if estados[i].es_final != estados[j].es_final:
                    distinguibles[i][j] = True
                    distinguibles[j][i] = True

        # Iterar hasta estabilizar
        cambio = True
        while cambio:
            cambio = False
            for i in range(n):
                for j in range(i + 1, n):
                    if distinguibles[i][j]:
                        continue
                    for simbolo in self.alfabeto:
                        ti = estados[i].obtener_transiciones(simbolo)
                        tj = estados[j].obtener_transiciones(simbolo)

                        if ti and tj:
                            ii = indice.get(ti[0])
                            jj = indice.get(tj[0])
                            if ii is not None and jj is not None and distinguibles[ii][jj]:
                                distinguibles[i][j] = True
                                distinguibles[j][i] = True
                                cambio = True
                                break
                        elif ti or tj:
                            distinguibles[i][j] = True
                            distinguibles[j][i] = True
                            cambio = True
                            break

        # Agrupar estados equivalentes
        grupos = []
        visitados = [False] * n
        for i in range(n):
            if visitados[i]:
                continue
            grupo = [i]
            visitados[i] = True
            for j in range(i + 1, n):
                if not visitados[j] and not distinguibles[i][j]:
                    grupo.append(j)
                    visitados[j] = True
            grupos.append(grupo)

        # Crear DFA minimizado
        minimizado = AutomataFinito(f"{self.nombre}_Min", es_afn=False)
        minimizado.establecer_alfabeto(self.alfabeto)

        mapa_grupo = {}
        for idx_g, grupo in enumerate(grupos):
            nuevo_estado = Estado(f"q{idx_g}")
            nuevo_estado.es_final = any(estados[i].es_final for i in grupo)
            minimizado.estados.append(nuevo_estado)

            for i in grupo:
                mapa_grupo[i] = nuevo_estado

            if any(estados[i] == self.estado_inicial for i in grupo):
                nuevo_estado.es_inicial = True
                minimizado.estado_inicial = nuevo_estado

            if nuevo_estado.es_final:
                minimizado.estados_finales.append(nuevo_estado)

        # Reconstruir transiciones
        for grupo in grupos:
            rep = estados[grupo[0]]
            nuevo_estado = mapa_grupo[grupo[0]]
            for simbolo in self.alfabeto:
                destinos = rep.obtener_transiciones(simbolo)
                if destinos:
                    idx_destino = indice.get(destinos[0])
                    if idx_destino is not None:
                        nuevo_estado.agregar_transicion(simbolo, mapa_grupo[idx_destino])

        return minimizado

    # ---------- UTILIDADES ----------
    def a_texto(self):
        lineas = [f"Autómata: {self.nombre} ({'NFA' if self.es_afn else 'DFA'})"]
        lineas.append(f"Alfabeto: {{{', '.join(sorted(self.alfabeto))}}}")
        lineas.append(f"Estados: {{{', '.join(e.id for e in self.estados)}}}")
        if self.estado_inicial:
            lineas.append(f"Estado inicial: {self.estado_inicial.id}")
        lineas.append(f"Estados finales: {{{', '.join(e.id for e in self.estados_finales)}}}")
        lineas.append("Transiciones:")
        for e in self.estados:
            for simbolo, destinos in e.transiciones.items():
                for d in destinos:
                    lineas.append(f"  {e.id} --{simbolo}--> {d.id}")
            for d in e.transiciones_epsilon:
                lineas.append(f"  {e.id} --ε--> {d.id}")
        return "\n".join(lineas)