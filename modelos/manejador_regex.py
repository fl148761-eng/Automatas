import re
from .automata import AutomataFinito
from .estado import Estado


class ManejadorRegex:
    """Maneja expresiones regulares y su conversión a autómatas."""

    def __init__(self):
        self.patron = ""
        self.logs = []
        self._contador = 0
        self._todos_estados = []

    def establecer_patron(self, patron):
        self.patron = patron
        try:
            re.compile(patron)
            return True
        except re.error:
            return False

    def validar(self, cadena, coincidencia_total=True):
        """
        Valida una cadena contra el patrón.

        Args:
            cadena: la cadena a validar
            coincidencia_total: si es True, la cadena debe coincidir
                               completamente (del inicio al fin).
                               Si es False, basta con que aparezca
                               el patrón en cualquier parte.
        """
        self.logs = []
        if not self.patron:
            self.logs.append("✗ No hay patrón definido")
            return False

        try:
            patron_efectivo = self.patron

            if coincidencia_total:
                # Solo agregar anclas si no las tiene ya
                if not patron_efectivo.startswith('^'):
                    patron_efectivo = '^' + patron_efectivo
                if not patron_efectivo.endswith('$'):
                    patron_efectivo = patron_efectivo + '$'

            compilado = re.compile(patron_efectivo)
            # match() valida desde el inicio; con ^...$ es equivalente a fullmatch
            resultado = bool(compilado.match(cadena))

            self.logs.append(f"Patrón original: {self.patron}")
            self.logs.append(f"Patrón usado: {patron_efectivo}")
            self.logs.append(f"Cadena: '{cadena}'")
            self.logs.append(f"Longitud: {len(cadena)}")
            self.logs.append(f"Resultado: {'ACEPTADO' if resultado else 'RECHAZADO'}")
            return resultado
        except re.error as e:
            self.logs.append(f"✗ Error en la expresión: {e}")
            return False

    # ---------- CONSTRUCCIÓN DE THOMPSON ----------
    def regex_a_afn(self, regex):
        self._contador = 0
        self._todos_estados = []
        self.alfabeto = set()

        tokens = self._tokenizar(regex)
        pos = [0]
        inicio, fin = self._parsear_expr(tokens, pos)

        afn = AutomataFinito(f"Regex_{regex}", es_afn=True)
        afn.establecer_alfabeto(self.alfabeto)

        for e in self._todos_estados:
            afn.estados.append(e)

        afn.estado_inicial = inicio
        inicio.es_inicial = True
        fin.es_final = True
        afn.estados_finales.append(fin)

        return afn

    def _nuevo_estado(self):
        e = Estado(f"q{self._contador}")
        self._contador += 1
        self._todos_estados.append(e)
        return e

    def _tokenizar(self, regex):
        tokens = []
        i = 0
        while i < len(regex):
            c = regex[i]
            if c in '()|*+?.':
                tokens.append(c)
            elif c == '\\' and i + 1 < len(regex):
                tokens.append(regex[i + 1])
                i += 1
            elif c not in ' ':
                tokens.append(c)
            i += 1
        return tokens

    def _parsear_expr(self, tokens, pos):
        izquierda = self._parsear_termino(tokens, pos)
        while pos[0] < len(tokens) and tokens[pos[0]] == '|':
            pos[0] += 1
            derecha = self._parsear_termino(tokens, pos)
            izquierda = self._hacer_union(izquierda, derecha)
        return izquierda

    def _parsear_termino(self, tokens, pos):
        izquierda = self._parsear_factor(tokens, pos)
        while pos[0] < len(tokens) and tokens[pos[0]] not in ')|':
            derecha = self._parsear_factor(tokens, pos)
            izquierda = self._hacer_concat(izquierda, derecha)
        return izquierda

    def _parsear_factor(self, tokens, pos):
        base = self._parsear_base(tokens, pos)
        while pos[0] < len(tokens) and tokens[pos[0]] in '*+?':
            op = tokens[pos[0]]
            pos[0] += 1
            if op == '*':
                base = self._hacer_estrella(base)
            elif op == '+':
                base = self._hacer_mas(base)
            elif op == '?':
                base = self._hacer_opcional(base)
        return base

    def _parsear_base(self, tokens, pos):
        if pos[0] >= len(tokens):
            raise ValueError("Regex mal formada")

        token = tokens[pos[0]]
        pos[0] += 1

        if token == '(':
            inicio, fin = self._parsear_expr(tokens, pos)
            if pos[0] >= len(tokens) or tokens[pos[0]] != ')':
                raise ValueError("Falta paréntesis de cierre")
            pos[0] += 1
            return inicio, fin
        elif token == '.':
            # Comodín: cualquier símbolo del alfabeto
            self.alfabeto.update(['a', 'b'])
            inicio = self._nuevo_estado()
            fin = self._nuevo_estado()
            inicio.agregar_transicion('a', fin)
            inicio.agregar_transicion('b', fin)
            return inicio, fin
        else:
            self.alfabeto.add(token)
            inicio = self._nuevo_estado()
            fin = self._nuevo_estado()
            inicio.agregar_transicion(token, fin)
            return inicio, fin

    def _hacer_concat(self, a, b):
        a[1].agregar_transicion_epsilon(b[0])
        return a[0], b[1]

    def _hacer_union(self, a, b):
        inicio = self._nuevo_estado()
        fin = self._nuevo_estado()
        inicio.agregar_transicion_epsilon(a[0])
        inicio.agregar_transicion_epsilon(b[0])
        a[1].agregar_transicion_epsilon(fin)
        b[1].agregar_transicion_epsilon(fin)
        return inicio, fin

    def _hacer_estrella(self, a):
        inicio = self._nuevo_estado()
        fin = self._nuevo_estado()
        inicio.agregar_transicion_epsilon(a[0])
        inicio.agregar_transicion_epsilon(fin)
        a[1].agregar_transicion_epsilon(a[0])
        a[1].agregar_transicion_epsilon(fin)
        return inicio, fin

    def _hacer_mas(self, a):
        inicio = self._nuevo_estado()
        fin = self._nuevo_estado()
        inicio.agregar_transicion_epsilon(a[0])
        a[1].agregar_transicion_epsilon(a[0])
        a[1].agregar_transicion_epsilon(fin)
        return inicio, fin

    def _hacer_opcional(self, a):
        inicio = self._nuevo_estado()
        fin = self._nuevo_estado()
        inicio.agregar_transicion_epsilon(a[0])
        inicio.agregar_transicion_epsilon(fin)
        a[1].agregar_transicion_epsilon(fin)
        return inicio, fin