# generador_codigo.py

import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk  # Se utiliza PIL para manejar la imagen del AST
import diagram  # Módulo de visualización de AST (diagram.py)

# Estructuras globales para contar temporales y etiquetas (usadas en generación TAC)
_temp_counter = 0
_label_counter = 0

def _nueva_temporal():
    """Genera un nuevo nombre de variable temporal único."""
    global _temp_counter
    _temp_counter += 1
    return f"t{_temp_counter}"

def _nueva_etiqueta():
    """Genera una nueva etiqueta (label) única para código de salto."""
    global _label_counter
    _label_counter += 1
    return f"L{_label_counter}"

def _generar_TAC_desde_AST(ast):
    """
    Recorre recursivamente el AST y genera la lista de instrucciones en
    Código de Tres Direcciones (TAC). Cada instrucción se representa como una cadena.
    """
    tac = []  # Lista resultante de instrucciones TAC

    def gen_expr(node):
        """
        Genera TAC para una expresión y retorna el nombre del temporal o variable
        que contiene el resultado de evaluar dicha expresión.
        Al generar el código, las instrucciones necesarias se agregan a 'tac'.
        """
        # Si el nodo es una tupla, identifica el tipo de expresión por el primer elemento.
        if isinstance(node, tuple):
            nodo_tipo = node[0]
            # Normalizar etiqueta de tipo eliminando detalles adicionales (p.ej., ", =" en asignaciones).
            etiqueta = nodo_tipo.split(',')[0]

            # Operaciones aritméticas y lógicas binarias (+, -, *, /, ||, &&, ==, !=, etc.)
            if etiqueta == "operation":
                # node = ('operation', operador, operando_izq, operando_der)
                op = node[1]
                izq = node[2]
                der = node[3]
                # Generar código para operandos
                res_izq = gen_expr(izq)
                res_der = gen_expr(der)
                # Asignar resultado de la operación a un nuevo temporal
                temp_res = _nueva_temporal()
                tac.append(f"{temp_res} = {res_izq} {op} {res_der}")
                return temp_res

            elif etiqueta == "comparison":
                # node = ('comparison', operador, operando_izq, operando_der)
                op = node[1]
                izq = node[2]
                der = node[3]
                res_izq = gen_expr(izq)
                res_der = gen_expr(der)
                temp_res = _nueva_temporal()
                tac.append(f"{temp_res} = {res_izq} {op} {res_der}")
                return temp_res

            elif etiqueta == "not":
                # node = ('not', expresion)
                expr = node[1]
                res_expr = gen_expr(expr)
                temp_res = _nueva_temporal()
                # Operador lógico NOT unario. Se representa con '!' en TAC.
                tac.append(f"{temp_res} = ! {res_expr}")
                return temp_res

            elif etiqueta == "ternary":
                # node = ('ternary', condicion, expr_true, expr_false)
                condicion = node[1]
                expr_true = node[2]
                expr_false = node[3]
                # Generar código para la condición
                cond_res = gen_expr(condicion)
                # Crear temporales y etiquetas para el resultado y los saltos
                resultado_temp = _nueva_temporal()
                etiqueta_false = _nueva_etiqueta()
                etiqueta_fin = _nueva_etiqueta()
                # Instrucción condicional: si la condición es falsa, saltar a rama false
                tac.append(f"ifFalse {cond_res} goto {etiqueta_false}")
                # Rama true: evaluar expresión verdadera y asignar a resultado_temp
                valor_true = gen_expr(expr_true)
                tac.append(f"{resultado_temp} = {valor_true}")
                tac.append(f"goto {etiqueta_fin}")
                # Rama false: etiqueta de inicio
                tac.append(f"{etiqueta_false}:")
                valor_false = gen_expr(expr_false)
                tac.append(f"{resultado_temp} = {valor_false}")
                # Etiqueta fin
                tac.append(f"{etiqueta_fin}:")
                return resultado_temp

            elif etiqueta in ("assignment", "assignment"):  # Asignación en expresión (ID = expr)
                # node = ('assignment', var, expr)
                var = node[1]
                expr = node[2]
                valor = gen_expr(expr)
                tac.append(f"{var} = {valor}")
                # El valor de una expresión de asignación es el valor asignado (ubicado en la variable)
                return var

            elif etiqueta == "increment":
                # node = ('increment', var)  -> i++ (post-incremento como expresión)
                var = node[1]
                # Guardar valor actual en un temporal (para valor de la expresión)
                temp_valor = _nueva_temporal()
                tac.append(f"{temp_valor} = {var}")
                # Incrementar la variable en 1
                tac.append(f"{var} = {var} + 1")
                # Retornar el valor original (post-incremento produce el valor antes de incrementar)
                return temp_valor

            elif etiqueta == "increment_by":
                # node = ('increment_by', var, cantidad)  -> i += n
                var = node[1]
                cantidad = node[2]
                valor_cant = gen_expr(cantidad)
                tac.append(f"{var} = {var} + {valor_cant}")
                # En este caso, la expresión i += n produce el nuevo valor de var
                return var

            elif etiqueta == "increment_assign":
                # node = ('increment_assign', var, var, cantidad)  -> i = i + n
                var = node[1]
                cantidad = node[3]
                valor_cant = gen_expr(cantidad)
                tac.append(f"{var} = {var} + {valor_cant}")
                return var

            elif etiqueta == "id":
                # node = ('id', nombre_var)
                return node[1]  # devuelve el nombre de la variable para usarla en TAC

            elif etiqueta == "number":
                # node = ('number', valor_numerico)
                return str(node[1])  # devuelve el número como texto

            elif etiqueta == "string":
                # node = ('string', valor_cadena_sin_comillas)
                # Agregar comillas para representarlo como literal de cadena
                return f"\"{node[1]}\""

            elif etiqueta == "bool_true":
                return "true"

            elif etiqueta == "bool_false":
                return "false"

            elif etiqueta == "declaracion_asignacion" or etiqueta == "declaration":
                # Declaración con asignación (tipo, id, expr) – se maneja al nivel de statement.
                # Si aparece aquí, procesarla como asignación normal.
                tipo = node[1]
                var = node[2]
                expr = node[3]
                valor = gen_expr(expr)
                # Incluir instrucción de declaración explícita antes de la asignación
                tac.append(f"DECL {tipo} {var}")
                tac.append(f"{var} = {valor}")
                return var

            # Cualquier otro tipo de nodo en expresión (no previsto explícitamente)
            # se retorna como cadena para su uso directo.
            return str(node)
        else:
            # Si el nodo no es tupla (puede ser lista u atómico):
            if isinstance(node, list):
                # Si se recibe una lista en contexto de expresión, procesar elemento único (caso particular).
                if len(node) == 1:
                    return gen_expr(node[0])
                # Lista no esperada en expresión (podría ser error de AST); devolver cadena representativa.
                return str(node)
            else:
                # Caso de valor atómico (p.ej., un tipo o identificador fuera de tupla).
                return str(node)

    def gen_stmt(node):
        """
        Genera TAC para un nodo de tipo sentencia (statement).
        Agrega las instrucciones resultantes a la lista 'tac'.
        """
        if node is None:
            return
        if isinstance(node, list):
            # Lista de sentencias: procesar secuencialmente
            for stmt in node:
                gen_stmt(stmt)
        elif isinstance(node, tuple):
            nodo_tipo = node[0]
            etiqueta = nodo_tipo.split(',')[0]

            if etiqueta == "program":
                # Programa completo: su hijo es la lista de sentencias
                gen_stmt(node[1])

            elif etiqueta == "declaracion_asignacion":
                # Declaración con asignación (tipo, id, expr)
                tipo = node[1]; var = node[2]; expr = node[3]
                valor = gen_expr(expr)
                tac.append(f"DECL {tipo} {var}")
                tac.append(f"{var} = {valor}")

            elif etiqueta == "declaracion":
                # Declaración simple (tipo, id) sin asignación inicial
                tipo = node[1]; var = node[2]
                tac.append(f"DECL {tipo} {var}")
                # Sin valor asignado, se declara la variable (podría asumir valor por defecto aparte, no representado en TAC)

            elif etiqueta == "assignment":
                # Asignación de valor a variable (id = expr)
                var = node[1]; expr = node[2]
                valor = gen_expr(expr)
                tac.append(f"{var} = {valor}")

            elif etiqueta == "increment_stmt":
                # Sentencia de incremento (ID++)
                var = node[1]
                tac.append(f"{var} = {var} + 1")

            elif etiqueta == "expr":
                # Sentencia expuesta (expresión seguida de ';'). Procesar la expresión y descartar el resultado.
                expr = node[1]
                gen_expr(expr)
                # (El resultado de la expresión, si lo hay, no se almacena porque es una sentencia aislada)

            elif etiqueta == "if":
                # Sentencia if (sin else)
                condicion = node[1]; bloque_then = node[2]
                cond_res = gen_expr(condicion)
                etiqueta_fin = _nueva_etiqueta()
                tac.append(f"ifFalse {cond_res} goto {etiqueta_fin}")
                gen_stmt(bloque_then)
                tac.append(f"{etiqueta_fin}:")

            elif etiqueta == "if-else":
                # Sentencia if-else
                condicion = node[1]; bloque_then = node[2]; bloque_else = node[3]
                cond_res = gen_expr(condicion)
                etiqueta_else = _nueva_etiqueta()
                etiqueta_fin = _nueva_etiqueta()
                tac.append(f"ifFalse {cond_res} goto {etiqueta_else}")
                gen_stmt(bloque_then)
                tac.append(f"goto {etiqueta_fin}")
                tac.append(f"{etiqueta_else}:")
                gen_stmt(bloque_else)
                tac.append(f"{etiqueta_fin}:")

            elif etiqueta == "while":
                # Sentencia while
                condicion = node[1]; cuerpo = node[2]
                etiqueta_inicio = _nueva_etiqueta()
                etiqueta_fin = _nueva_etiqueta()
                tac.append(f"{etiqueta_inicio}:")
                cond_res = gen_expr(condicion)
                tac.append(f"ifFalse {cond_res} goto {etiqueta_fin}")
                gen_stmt(cuerpo)
                tac.append(f"goto {etiqueta_inicio}")
                tac.append(f"{etiqueta_fin}:")

            elif etiqueta == "for":
                # Sentencia for (init; cond; update) { cuerpo }
                init = node[1]; condicion = node[2]; actualizacion = node[3]; cuerpo = node[4]
                # Inicialización (puede ser declaración o asignación)
                gen_stmt(init)
                etiqueta_inicio = _nueva_etiqueta()
                etiqueta_fin = _nueva_etiqueta()
                tac.append(f"{etiqueta_inicio}:")
                # Condición de continuidad del for
                if condicion is not None:
                    cond_res = gen_expr(condicion)
                    tac.append(f"ifFalse {cond_res} goto {etiqueta_fin}")
                else:
                    # Si la condición es None (bucle for sin condición explícita), asumir siempre verdadero
                    pass
                # Cuerpo del for
                gen_stmt(cuerpo)
                # Actualización (ejecutada al final de cada iteración)
                if actualizacion is not None:
                    gen_expr(actualizacion)
                tac.append(f"goto {etiqueta_inicio}")
                tac.append(f"{etiqueta_fin}:")

            elif etiqueta == "block":
                # Bloque de código (agrupación de sentencias entre llaves)
                bloque = node[1]
                gen_stmt(bloque)

            else:
                # Cualquier otro tipo de nodo de sentencia no contemplado explícitamente
                # (Incluyendo casos como 'increment', 'increment_by' en contexto de sentencia)
                gen_expr(node)
        else:
            # Nodo que no es lista ni tupla (posible caso atípico)
            return

    # Iniciar la generación de TAC recorriendo el AST completo
    gen_stmt(ast)
    return tac

def _convertir_TAC_a_SSA(tac_instructions):
    """
    Convierte una lista de instrucciones TAC a formato SSA (Static Single Assignment).
    Retorna una lista de instrucciones SSA donde cada variable asignable tiene un nombre único por asignación.
    """
    ssa = []
    # Mapa de versiones actuales por variable (ej.: {"x": 1} indica próxima versión de x a usar será x1)
    version = {}
    # Mapa de nombre actual (última versión usada) por variable para sustitución en operandos
    nombre_actual = {}

    for instr in tac_instructions:
        instr = instr.strip()
        # Manejar etiquetas (etiquetas terminan en ':')
        if instr.endswith(":"):
            # Etiquetas de salto se copian tal cual
            ssa.append(instr)
            continue

        # Manejar instrucciones de salto condicional y absoluto
        if instr.startswith("ifFalse") or instr.startswith("if "):
            # Formato esperado: ifFalse <cond> goto <Etiqueta>
            partes = instr.split()
            # partes[0] = "ifFalse", partes[1] = cond, partes[2] = "goto", partes[3] = etiqueta
            cond_var = partes[1]
            # Reemplazar variable de condición por su nombre SSA actual, si aplica
            if cond_var in nombre_actual:
                cond_ssa = nombre_actual[cond_var]
            else:
                # Si la variable no tiene versión (posible constante o temporal), se deja igual
                cond_ssa = cond_var
            # Reconstruir instrucción con la variable en SSA
            ssa.append(f"{partes[0]} {cond_ssa} {partes[2]} {partes[3]}")
            continue

        if instr.startswith("goto"):
            # Saltos incondicionales se copian directamente
            ssa.append(instr)
            continue

        if instr.startswith("DECL"):
            # Declaración de variable (no es una asignación, solo anuncia tipo y nombre)
            # Se mantiene la declaración, sin versiones, ya que no asigna valor.
            ssa.append(instr)
            # Inicializar contador de versión para esa variable en 0 (indicando declarada sin valor asignado)
            partes = instr.split()
            if len(partes) >= 3:
                var_decl = partes[2]
                version[var_decl] = 0
                nombre_actual[var_decl] = var_decl  # nombre actual es el mismo hasta que sea asignado
            continue

        # Manejar asignaciones (formato general: <dest> = <expr>)
        if "=" in instr:
            # Separar destino y expresión
            dest, expr = instr.split("=", 1)
            dest = dest.strip()
            expr = expr.strip()
            # Reemplazar en la expresión cualquier variable por su nombre SSA actual
            # Se tokeniza la expresión para identificar operandos potenciales
            tokens = expr.replace("(", " ( ").replace(")", " ) ").split()
            expr_tokens_ssa = []
            for tok in tokens:
                # Omitir símbolos que no sean identificadores (operadores, números, comas, paréntesis)
                if tok.isidentifier():  # identifica nombres de variables (letras, dígitos, underscore)
                    if tok in nombre_actual:
                        expr_tokens_ssa.append(nombre_actual[tok])
                    else:
                        # Si el token es un identificador no visto (posible constante booleana 'true/false' o variable no asignada aún)
                        expr_tokens_ssa.append(tok)
                else:
                    # Para literales numéricos o símbolos, usar tal cual
                    expr_tokens_ssa.append(tok)
            expr_ssa = " ".join(expr_tokens_ssa)
            # Asignar nueva versión al destino si es una variable de usuario (no temporal)
            if dest.startswith("t"):
                # Temporales ya son únicos por construcción en TAC, mantener igual
                nuevo_destino = dest
            else:
                # Variable de programa: asignar siguiente versión
                ver = version.get(dest, 0) + 1
                version[dest] = ver
                nuevo_destino = f"{dest}{ver}"
                # Actualizar nombre actual para futuras apariciones de esta variable
                nombre_actual[dest] = nuevo_destino
            # Agregar instrucción SSA resultante
            ssa.append(f"{nuevo_destino} = {expr_ssa}")
    return ssa

def generar_codigo_intermedio(ast):
    """
    Función principal para generar las representaciones intermedias (AST visual, TAC, SSA)
    a partir de un AST dado.
    - Genera el AST visual usando diagram.py (Graphviz).
    - Genera las listas de instrucciones TAC y SSA.
    - Guarda TAC y SSA en archivos de texto.
    - Muestra los resultados en una ventana independiente con capacidad de scroll.
    """
    # Generar AST visual con graphviz (diagram.py)

    ruta_imagen = r"C:\Users\monje\PycharmProjects\p1-copiler\Arbol_Sintactico.png"


    # Generar código de tres direcciones (TAC) del AST
    lista_TAC = _generar_TAC_desde_AST(ast)
    # Convertir TAC a Static Single Assignment (SSA)
    lista_SSA = _convertir_TAC_a_SSA(lista_TAC)

    # Guardar las instrucciones TAC y SSA en archivos de texto
    with open("codigo_tac.txt", "w", encoding="utf-8") as file_tac:
        for instr in lista_TAC:
            file_tac.write(instr + "\n")
    with open("codigo_ssa.txt", "w", encoding="utf-8") as file_ssa:
        for instr in lista_SSA:
            file_ssa.write(instr + "\n")

    # Crear una ventana emergente para mostrar los resultados
    ventana_intermedio = tk.Toplevel()
    ventana_intermedio.title("Código Intermedio (AST, TAC, SSA)")
    ventana_intermedio.geometry("1600x1200")  # Tamaño inicial de la ventana

    # Marco para contener la sección del AST visual
    frame_ast = tk.Frame(ventana_intermedio)
    frame_ast.pack(fill=tk.BOTH, expand=True)
    # Si la imagen del AST se generó correctamente, mostrarla; de lo contrario, indicar error.
    if ruta_imagen:
        try:
            img = Image.open(ruta_imagen)
            photo = ImageTk.PhotoImage(img)
            canvas = tk.Canvas(frame_ast)
            canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            canvas.config(scrollregion=canvas.bbox(tk.ALL))
            # Barras de desplazamiento para el canvas de la imagen AST
            scroll_x = tk.Scrollbar(frame_ast, orient=tk.HORIZONTAL, command=canvas.xview)
            scroll_y = tk.Scrollbar(frame_ast, orient=tk.VERTICAL, command=canvas.yview)
            canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
            scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
            scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            # Asociar la imagen al canvas para evitar recolección de basura
            canvas.image = photo
        except Exception as e:
            # En caso de falla al cargar la imagen, mostrar mensaje de error
            label_error = tk.Label(frame_ast, text=f"Error al cargar imagen AST: {e}", fg="red")
            label_error.pack()
    else:
        label_error = tk.Label(frame_ast, text="No se pudo generar la visualización del AST", fg="red")
        label_error.pack()

    # Área de texto con scroll para TAC y SSA
    text_area = scrolledtext.ScrolledText(ventana_intermedio, height=20, width=100, bg="#f0f0f0")
    text_area.pack(fill=tk.BOTH, expand=True)
    # Insertar el contenido de TAC y SSA en el área de texto
    text_area.insert(tk.END, "*** Código de Tres Direcciones (TAC) ***\n")
    for instr in lista_TAC:
        text_area.insert(tk.END, instr + "\n")
    text_area.insert(tk.END, "\n*** Formato Static Single Assignment (SSA) ***\n")
    for instr in lista_SSA:
        text_area.insert(tk.END, instr + "\n")
    # Configurar el texto como solo lectura (deshabilitar edición)
    text_area.config(state=tk.DISABLED)
