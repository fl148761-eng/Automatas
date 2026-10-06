import tkinter as tk
from tkinter import ttk, messagebox

from modelos import AutomataFinito, ManejadorRegex


class AplicacionAutomatas:
    def __init__(self, root):
        self.root = root
        self.root.title("Autómatas y Expresiones Regulares")
        self.root.geometry("1200x750")

        self.automata_actual = AutomataFinito()
        self.manejador_regex = ManejadorRegex()

        self._construir_interfaz()

    def _construir_interfaz(self):
        # Cuaderno de pestañas
        self.cuaderno = ttk.Notebook(self.root)
        self.cuaderno.pack(fill='both', expand=True, padx=5, pady=5)

        self.tab_crear = ttk.Frame(self.cuaderno)
        self.tab_simular = ttk.Frame(self.cuaderno)
        self.tab_conversion = ttk.Frame(self.cuaderno)
        self.tab_regex = ttk.Frame(self.cuaderno)

        self.cuaderno.add(self.tab_crear, text='Crear Autómata')
        self.cuaderno.add(self.tab_simular, text='▶ Simular')
        self.cuaderno.add(self.tab_conversion, text='Conversión')
        self.cuaderno.add(self.tab_regex, text='Regex')

        self._construir_tab_crear()
        self._construir_tab_simular()
        self._construir_tab_conversion()
        self._construir_tab_regex()

        # Panel de logs
        marco_logs = ttk.LabelFrame(self.root, text="Logs", padding=5)
        marco_logs.pack(fill='x', padx=5, pady=5)

        self.texto_logs = tk.Text(marco_logs, height=15, bg='black', fg='white',
                                  font=('Consolas', 9), wrap='word')
        self.texto_logs.pack(fill='both', expand=True)

        scroll = ttk.Scrollbar(marco_logs, command=self.texto_logs.yview)
        self.texto_logs.config(yscrollcommand=scroll.set)

        self.log("Aplicación iniciada")

    # ==================== PESTAÑA: CREAR ====================
    def _construir_tab_crear(self):
        frame = self.tab_crear

        # --- Configuración ---
        cfg = ttk.LabelFrame(frame, text="Configuración del Autómata", padding=10)
        cfg.pack(fill='x', padx=10, pady=5)

        ttk.Label(cfg, text="Nombre:").grid(row=0, column=0, sticky='w', padx=5)
        self.entry_nombre = ttk.Entry(cfg, width=20)
        self.entry_nombre.insert(0, "MiAutomata")
        self.entry_nombre.grid(row=0, column=1, padx=5)

        ttk.Label(cfg, text="Tipo:").grid(row=0, column=2, sticky='w', padx=5)
        self.var_tipo = tk.StringVar(value="DFA")
        ttk.Radiobutton(cfg, text="AFD", variable=self.var_tipo, value="AFD").grid(row=0, column=3)
        ttk.Radiobutton(cfg, text="AFN", variable=self.var_tipo, value="AFN").grid(row=0, column=4)

        ttk.Label(cfg, text="Alfabeto:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_alfabeto = ttk.Entry(cfg, width=20)
        self.entry_alfabeto.insert(0, "a,b")
        self.entry_alfabeto.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(cfg, text="Crear Autómata", command=self._crear_automata).grid(
            row=1, column=3, columnspan=2, pady=5)

        # --- Estados ---
        st_frame = ttk.LabelFrame(frame, text="Estados", padding=10)
        st_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(st_frame, text="ID del estado:").grid(row=0, column=0, padx=5)
        self.entry_estado_id = ttk.Entry(st_frame, width=15)
        self.entry_estado_id.grid(row=0, column=1, padx=5)

        ttk.Button(st_frame, text="Agregar", command=self._agregar_estado).grid(
            row=0, column=2, padx=5)
        ttk.Button(st_frame, text="Eliminar", command=self._eliminar_estado).grid(
            row=0, column=3, padx=5)
        ttk.Button(st_frame, text="Inicial", command=self._marcar_inicial).grid(
            row=0, column=4, padx=5)
        ttk.Button(st_frame, text="Final", command=self._alternar_final).grid(
            row=0, column=5, padx=5)

        # --- Transiciones ---
        tr_frame = ttk.LabelFrame(frame, text="Transiciones", padding=10)
        tr_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(tr_frame, text="Desde:").grid(row=0, column=0, padx=5)
        self.entry_desde = ttk.Entry(tr_frame, width=10)
        self.entry_desde.grid(row=0, column=1, padx=5)

        ttk.Label(tr_frame, text="Símbolo:").grid(row=0, column=2, padx=5)
        self.entry_simbolo = ttk.Entry(tr_frame, width=8)
        self.entry_simbolo.grid(row=0, column=3, padx=5)

        ttk.Label(tr_frame, text="Hacia:").grid(row=0, column=4, padx=5)
        self.entry_hacia = ttk.Entry(tr_frame, width=10)
        self.entry_hacia.grid(row=0, column=5, padx=5)

        ttk.Button(tr_frame, text="Agregar Transición", command=self._agregar_transicion).grid(
            row=0, column=6, padx=10)
        ttk.Label(tr_frame, text="(Use 'ε' para transición épsilon)",
                  foreground='gray').grid(row=1, column=0, columnspan=7, pady=5)

        # --- Lista de Estados ---
        lst_frame = ttk.LabelFrame(frame, text="Lista de Estados", padding=10)
        lst_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.tree_estados = ttk.Treeview(lst_frame, columns=('id', 'inicial', 'final', 'trans'),
                                         show='headings', height=8)
        self.tree_estados.heading('id', text='ID')
        self.tree_estados.heading('inicial', text='Inicial')
        self.tree_estados.heading('final', text='Final')
        self.tree_estados.heading('trans', text='Transiciones')
        self.tree_estados.column('id', width=80)
        self.tree_estados.column('inicial', width=80)
        self.tree_estados.column('final', width=80)
        self.tree_estados.column('trans', width=500)
        self.tree_estados.pack(fill='both', expand=True)

    def _crear_automata(self):
    try:
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            raise ValueError("El nombre del autómata no puede estar vacío")

        tipo_seleccionado = self.var_tipo.get()
        es_afn = (tipo_seleccionado == "AFN")

        texto_alfabeto = self.entry_alfabeto.get().strip()
        if not texto_alfabeto:
            raise ValueError("Debe especificar al menos un símbolo para el alfabeto.")

        simbolos = [s.strip() for s in texto_alfabeto.split(',') if s.strip()]
        for s in simbolos:
            if len(s) != 1:
                raise ValueError(f"El símbolo '{s}' no es válido.")
        if len(simbolos) != len(set(simbolos)):
            raise ValueError("El alfabeto contiene símbolos duplicados")

        self.automata_actual = AutomataFinito(nombre, es_afn)
        self.automata_actual.establecer_alfabeto(simbolos)
        self._refrescar_lista()
        self.log(f"✓ Autómata '{nombre}' creado")
    except ValueError as e:
        messagebox.showerror("Configuración inválida", str(e))
        self.log(f"✗ {e}")

   def _agregar_estado(self):
    try:
        sid = self.entry_estado_id.get().strip()
        if not sid:
            raise ValueError("Debe ingresar un ID para el estado")
        if any(c in sid for c in ' ,;{}()[]'):
            raise ValueError(f"El ID '{sid}' contiene caracteres no permitidos.")
        self.automata_actual.agregar_estado(sid)
        self.entry_estado_id.delete(0, 'end')
        self._refrescar_lista()
        self.log(f"✓ Estado '{sid}' agregado")
    except ValueError as e:
        messagebox.showerror("Estado no válido", str(e))

    def _eliminar_estado(self):
        sel = self.tree_estados.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un estado")
            return
        sid = self.tree_estados.item(sel[0])['values'][0]
        self.automata_actual.eliminar_estado(sid)
        self._refrescar_lista()
        self.log(f"✓ Estado '{sid}' eliminado")

    def _marcar_inicial(self):
        sel = self.tree_estados.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un estado")
            return
        sid = self.tree_estados.item(sel[0])['values'][0]
        self.automata_actual.establecer_inicial(sid)
        self._refrescar_lista()
        self.log(f"✓ Estado inicial: {sid}")

    def _alternar_final(self):
        sel = self.tree_estados.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un estado")
            return
        sid = self.tree_estados.item(sel[0])['values'][0]
        estado = self.automata_actual.obtener_estado(sid)
        self.automata_actual.establecer_final(sid, not estado.es_final)
        self._refrescar_lista()
        self.log(f"✓ Estado '{sid}' {'marcado' if estado.es_final else 'desmarcado'} como final")

    def _agregar_transicion(self):
    try:
        desde = self.entry_desde.get().strip()
        simbolo = self.entry_simbolo.get().strip()
        hacia = self.entry_hacia.get().strip()

        if not (desde and simbolo and hacia):
            raise ValueError("Complete todos los campos")

        if not self.automata_actual.obtener_estado(desde):
            raise ValueError(f"El estado origen '{desde}' no existe")
        if not self.automata_actual.obtener_estado(hacia):
            raise ValueError(f"El estado destino '{hacia}' no existe")

        if simbolo not in ('ε', 'epsilon', ''):
            if len(simbolo) > 1:
                raise ValueError("El símbolo debe ser un único carácter")
            if self.automata_actual.alfabeto and simbolo not in self.automata_actual.alfabeto:
                raise ValueError(f"El símbolo '{simbolo}' no pertenece al alfabeto")

        self.automata_actual.agregar_transicion(desde, simbolo, hacia)

        self.entry_desde.delete(0, 'end')
        self.entry_simbolo.delete(0, 'end')
        self.entry_hacia.delete(0, 'end')

        self._refrescar_lista()
        self.log(f"✓ Transición: {desde} --{simbolo}--> {hacia}")
    except ValueError as e:
        messagebox.showerror("Transición inválida", str(e))

    def _refrescar_lista(self):
        for item in self.tree_estados.get_children():
            self.tree_estados.delete(item)

        for e in self.automata_actual.estados:
            partes = []
            for simbolo, destinos in e.transiciones.items():
                for d in destinos:
                    partes.append(f"{simbolo}→{d.id}")
            for d in e.transiciones_epsilon:
                partes.append(f"ε→{d.id}")

            self.tree_estados.insert('', 'end', values=(
                e.id,
                "✓" if e.es_inicial else "",
                "✓" if e.es_final else "",
                ", ".join(partes) if partes else "(sin transiciones)"
            ))

    # ==================== PESTAÑA: SIMULAR ====================
    def _construir_tab_simular(self):
        frame = self.tab_simular

        info = ttk.LabelFrame(frame, text="Autómata Actual", padding=10)
        info.pack(fill='x', padx=10, pady=5)

        self.label_info = ttk.Label(info, text="No hay autómata cargado",
                                    font=('Arial', 10))
        self.label_info.pack()

        entrada = ttk.LabelFrame(frame, text="Cadena a validar", padding=10)
        entrada.pack(fill='x', padx=10, pady=5)

        ttk.Label(entrada, text="Cadena:").pack(side='left', padx=5)
        self.entry_cadena = ttk.Entry(entrada, width=40, font=('Arial', 12))
        self.entry_cadena.pack(side='left', padx=5)

        ttk.Button(entrada, text="▶ Simular", command=self._simular).pack(side='left', padx=10)

        self.label_resultado = ttk.Label(frame, text="Esperando simulación...",
                                         font=('Arial', 16, 'bold'),
                                         foreground='gray')
        self.label_resultado.pack(pady=20)

        detalle = ttk.LabelFrame(frame, text="Detalles", padding=10)
        detalle.pack(fill='both', expand=True, padx=10, pady=5)

        self.texto_detalle = tk.Text(detalle, font=('Consolas', 10), wrap='word')
        self.texto_detalle.pack(fill='both', expand=True)

    def _simular(self):
        if not self.automata_actual.estados:
            messagebox.showwarning("Aviso", "No hay autómata creado")
            return

        self.label_info.config(
            text=f"{self.automata_actual.nombre} ({'NFA' if self.automata_actual.es_afn else 'DFA'}) - "
                 f"{len(self.automata_actual.estados)} estados"
        )

        cadena = self.entry_cadena.get()
        resultado = self.automata_actual.simular(cadena)

        self.label_resultado.config(
            text="ACEPTADO" if resultado else "RECHAZADO",
            foreground='green' if resultado else 'red'
        )

        self.texto_detalle.delete('1.0', 'end')
        for linea in self.automata_actual.logs_simulacion:
            self.texto_detalle.insert('end', linea + '\n')

        self.log(f"--- Simulación de '{cadena}': {'ACEPTADO' if resultado else 'RECHAZADO'} ---")

    # ==================== PESTAÑA: CONVERSIÓN ====================
    def _construir_tab_conversion(self):
        frame = self.tab_conversion

        ttk.Label(frame, text="Conversión AFN → AFD",
                  font=('Arial', 12, 'bold')).pack(pady=10)
        ttk.Button(frame, text="Convertir AFN a AFD",
                   command=self._convertir_afn_afd).pack(pady=5)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', padx=20, pady=15)

        ttk.Label(frame, text="Minimización de AFD",
                  font=('Arial', 12, 'bold')).pack(pady=10)
        ttk.Button(frame, text="Minimizar AFD",
                   command=self._minimizar).pack(pady=5)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', padx=20, pady=15)

        ttk.Button(frame, text="Mostrar Autómata Actual",
                   command=self._mostrar_actual).pack(pady=5)

    def _convertir_afn_afd(self):
        try:
            if not self.automata_actual.es_afn:
                messagebox.showinfo("Info", "El autómata ya es un AFD")
                return
            self.automata_actual = self.automata_actual.afn_a_afd()
            self._refrescar_lista()
            self.log(f"✓ Conversión AFN → AFD completada ({len(self.automata_actual.estados)} estados)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _minimizar(self):
        try:
            if self.automata_actual.es_afn:
                messagebox.showinfo("Info", "Primero convierta el AFN a AFD")
                return
            self.automata_actual = self.automata_actual.minimizar()
            self._refrescar_lista()
            self.log(f"AFD minimizado ({len(self.automata_actual.estados)} estados)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _mostrar_actual(self):
        texto = self.automata_actual.a_texto()
        for linea in texto.split('\n'):
            self.log(linea)

    # ==================== PESTAÑA: REGEX ====================
    def _construir_tab_regex(self):
        frame = self.tab_regex

        # --- Patrón ---
        p_frame = ttk.LabelFrame(frame, text="Expresión Regular", padding=10)
        p_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(p_frame, text="Patrón:").pack(side='left', padx=5)
        self.entry_patron = ttk.Entry(p_frame, width=40, font=('Arial', 12))
        self.entry_patron.insert(0, "a*b")
        self.entry_patron.pack(side='left', padx=5)

        ttk.Button(p_frame, text="Aplicar", command=self._aplicar_patron).pack(side='left', padx=5)
        ttk.Button(p_frame, text="Generar AFN", command=self._generar_nfa).pack(side='left', padx=5)

        # --- Validar cadena ---
        v_frame = ttk.LabelFrame(frame, text="Validar Cadena", padding=10)
        v_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(v_frame, text="Cadena:").pack(side='left', padx=5)
        self.entry_validar = ttk.Entry(v_frame, width=30, font=('Arial', 12))
        self.entry_validar.pack(side='left', padx=5)

        # NUEVO: Casilla para coincidencia total
        self.var_coincidencia_total = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            v_frame,
            text="Coincidencia total (^...$)",
            variable=self.var_coincidencia_total
        ).pack(side='left', padx=10)

        ttk.Button(v_frame, text="Validar", command=self._validar_cadena).pack(side='left', padx=5)

        # --- Información de ayuda ---
        ayuda = ttk.LabelFrame(frame, text="Ayuda - Símbolos especiales", padding=10)
        ayuda.pack(fill='x', padx=10, pady=5)

        texto_ayuda = (
            "•  a*   → cero o más 'a'      •  a+  → una o más 'a'      •  a?  → cero o una 'a'\n"
            "•  a|b  → 'a' o 'b'            •  .   → cualquier carácter  •  (ab) → agrupar\n"
            "•  ^abc → inicia con 'abc'     •  abc$ → termina con 'abc'"
        )
        ttk.Label(ayuda, text=texto_ayuda, font=('Consolas', 9),
                  justify='left').pack()

        # --- Resultado ---
        self.label_resultado_regex = ttk.Label(frame, text="",
                                               font=('Arial', 16, 'bold'))
        self.label_resultado_regex.pack(pady=20)

    def _aplicar_patron(self):
        patron = self.entry_patron.get()
        if self.manejador_regex.establecer_patron(patron):
            self.log(f"✓ Patrón establecido: {patron}")
        else:
            self.log(f"✗ Patrón inválido: {patron}")
            messagebox.showerror("Error", "Expresión regular inválida")

    def _validar_cadena(self):
        if not self.manejador_regex.patron:
            messagebox.showwarning("Aviso", "Primero aplique un patrón")
            return

        cadena = self.entry_validar.get()
        coincidencia_total = self.var_coincidencia_total.get()

        resultado = self.manejador_regex.validar(cadena, coincidencia_total)

        self.label_resultado_regex.config(
            text="ACEPTADA" if resultado else "RECHAZADA",
            foreground='green' if resultado else 'red'
        )

        for linea in self.manejador_regex.logs:
            self.log(linea)

    def _generar_nfa(self):
        try:
            patron = self.entry_patron.get()
            if not self.manejador_regex.establecer_patron(patron):
                messagebox.showerror("Error", "Regex inválida")
                return

            self.automata_actual = self.manejador_regex.regex_a_afn(patron)
            self._refrescar_lista()
            self.log(f"NFA generado desde regex '{patron}' ({len(self.automata_actual.estados)} estados)")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar NFA: {e}")

    # ==================== LOGS ====================
    def log(self, mensaje):
        self.texto_logs.insert('end', mensaje + '\n')
        self.texto_logs.see('end')
        self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionAutomatas(root)
    root.mainloop()
