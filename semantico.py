# semantico.py

def analizar_semantica(arbol, tabla_simbolos):
    """
    Recorre el árbol sintáctico 'arbol' y realiza análisis semántico.
    Actualiza la tabla de símbolos 'tabla_simbolos' con los tipos y valores de variables,
    y reporta cualquier error semántico encontrado directamente en consola.
    """
    # Pila de ámbitos (cada elemento es un diccionario de {nombre_var: tipo})
    scope_stack = [ {} ]  # Comenzar con un ámbito global vacío
    # Conjunto de nombres declarados en algún ámbito (para detectar uso fuera de alcance)
    declared_names = set()
    # Indicador de si se encontraron errores (opcional, para posibles usos futuros)
    errors_found = False

    def error(mensaje):
        """Imprime un mensaje de error semántico."""
        nonlocal errors_found
        errors_found = True
        print(f"Error semántico: {mensaje}")

    def find_variable_type(name):
        """
        Busca el tipo de una variable 'name' en la pila de ámbitos.
        Devuelve el tipo si la variable está declarada en el ámbito actual o en algún ámbito externo,
        o None si no está declarada en ninguno.
        """
        for scope in reversed(scope_stack):
            if name in scope:
                return scope[name]
        return None

    def declare_variable(name, var_type, const_value=None):
        """
        Declara una nueva variable en el ámbito actual con nombre 'name' y tipo 'var_type'.
        Si la variable ya existe en este mismo ámbito, reporta un error de redeclaración.
        Opcionalmente asigna un valor constante 'const_value' conocido.
        """
        current_scope = scope_stack[-1]
        if name in current_scope:
            # La variable ya fue declarada en este mismo ámbito
            error(f"La variable '{name}' ya fue declarada en este ámbito")
        else:
            # Añadir la variable al ámbito actual
            current_scope[name] = var_type
            declared_names.add(name)
            # Actualizar la tabla de símbolos global con su tipo
            tabla_simbolos[name] = {"tipo": var_type}
            # Si hay un valor constante disponible, guardarlo en la tabla de símbolos
            if const_value is not None:
                tabla_simbolos[name]["valor"] = const_value

    def types_compatible(var_type, expr_type):
        """
        Verifica si el tipo de una variable 'var_type' es compatible con el tipo de una expresión 'expr_type'.
        En este lenguaje, solo consideramos compatibles los tipos idénticos.
        """
        # Hacer coincidir exactamente los tipos; no se permiten conversiones implícitas por ahora
        return var_type == expr_type

    def evaluate_expression(node):
        """
        Evalúa un nodo de expresión del AST para determinar su tipo resultante.
        También realiza comprobaciones semánticas dentro de la expresión (uso de variables declaradas, etc.).
        Devuelve una tupla (expr_type, const_value), donde expr_type es el tipo deducido de la expresión
        (como string "INT", "FLOAT", "STRING", "BOOL"), y const_value es el valor constante si puede determinarse
        en tiempo de compilación (o None en caso contrario).
        """
        # Caso base: el nodo es un valor constante o identificador
        if not isinstance(node, tuple):
            # En el AST de nuestro parser, las expresiones siempre son tuplas.
            # Si no lo es, no se reconoce (retornar None para tipo).
            return (None, None)

        tag = node[0]

        # Literales numéricos (entero o flotante)
        if tag == 'number':
            # El valor puede ser int o float en Python; determinamos el tipo base
            value = node[1]
            if isinstance(value, int):
                return ("INT", value)   # Número entero
            elif isinstance(value, float):
                return ("FLOAT", value)  # Número de punto flotante
            else:
                # Por seguridad, cualquier otro tipo numérico tratarlo como None
                return (None, None)

        # Literal de cadena de texto
        if tag == 'string':
            value = node[1]
            return ("STRING", value)

        # Literal booleano true/false
        if tag == 'bool_true':
            return ("BOOL", True)
        if tag == 'bool_false':
            return ("BOOL", False)

        # Identificador (variable) usado en expresión
        if tag == 'id':
            name = node[1]
            var_type = find_variable_type(name)
            if var_type is None:
                # Variable no encontrada en ningún ámbito
                if name in declared_names:
                    error(f"La variable '{name}' se utiliza fuera de su ámbito")
                else:
                    error(f"La variable '{name}' no ha sido declarada")
                return (None, None)
            # La variable existe; obtener su tipo
            # No devolvemos valor constante aunque la variable tenga uno,
            # porque no hacemos propagación de constantes de variables (asumimos valor no determinado en compilación)
            return (var_type, None)

        # Operaciones binarias aritméticas, lógicas (AND/OR) o de igualdad (==, !=)
        if tag == 'operation':
            op = node[1]    # operador, por ejemplo '+', '||', '==', etc.
            left_node = node[2]
            right_node = node[3]
            # Evaluar subexpresiones izquierda y derecha
            left_type, left_val = evaluate_expression(left_node)
            right_type, right_val = evaluate_expression(right_node)
            if left_type is None or right_type is None:
                # Si alguna subexpresión tuvo error, abortar esta operación
                return (None, None)

            # Comprobar según el tipo de operador
            if op in ['+', '-', '*', '/']:
                # Ambos operandos deben ser numéricos (INT o FLOAT)
                if not (left_type in ["INT", "FLOAT"] and right_type in ["INT", "FLOAT"]):
                    error(f"Operador '{op}' aplicado a tipos incompatibles: {left_type} y {right_type}")
                    return (None, None)
                # Determinar tipo resultante: si cualquiera es FLOAT, resultado FLOAT; si ambos INT, resultado INT
                result_type = "FLOAT" if (left_type == "FLOAT" or right_type == "FLOAT") else "INT"
                # Para división, si ambos son INT mantendremos INT (división entera)
                if op == '/' and result_type == "INT":
                    # En muchos lenguajes, la división entera produce INT (truncando el resultado si es fraccionario)
                    result_type = "INT"
                # Calcular valor constante si ambos operandos son constantes
                const_val = None
                if left_val is not None and right_val is not None:
                    # Realizar la operación con los valores constantes
                    try:
                        if op == '+':
                            const_val = left_val + right_val
                        elif op == '-':
                            const_val = left_val - right_val
                        elif op == '*':
                            const_val = left_val * right_val
                        elif op == '/':
                            # Evitar división por cero
                            if right_val != 0:
                                const_val = left_val // right_val if result_type == "INT" else left_val / right_val
                            else:
                                const_val = None
                    except Exception:
                        const_val = None
                return (result_type, const_val)

            elif op in ['&&', '||']:
                # Operadores lógicos AND, OR: ambos operandos deben ser booleanos
                if left_type != "BOOL" or right_type != "BOOL":
                    error(f"Operador lógico '{op}' requiere operandos booleanos (BOOL)")
                    return (None, None)
                result_type = "BOOL"
                const_val = None
                if left_val is not None and right_val is not None:
                    # Calcular constante booleana
                    if op == '&&':
                        const_val = left_val and right_val
                    elif op == '||':
                        const_val = left_val or right_val
                return (result_type, const_val)

            elif op in ['==', '!=']:
                # Operadores de igualdad/desigualdad: los operandos deben ser del mismo tipo básico
                if left_type != right_type:
                    # Permitimos comparación de INT vs FLOAT como numéricos compatibles
                    both_numeric = left_type in ["INT", "FLOAT"] and right_type in ["INT", "FLOAT"]
                    if not both_numeric:
                        error(f"No se puede comparar {left_type} con {right_type} usando '{op}'")
                        return (None, None)
                # El resultado de == o != es booleano
                result_type = "BOOL"
                const_val = None
                if left_val is not None and right_val is not None:
                    const_val = (left_val == right_val) if op == '==' else (left_val != right_val)
                return (result_type, const_val)

            else:
                # Cualquier otro operador no contemplado explícitamente (por seguridad)
                return (None, None)

        # Operaciones de comparación (<, >, <=, >=)
        if tag == 'comparison':
            op = node[1]   # '<', '>', '<=', '>='
            left_node = node[2]
            right_node = node[3]
            left_type, left_val = evaluate_expression(left_node)
            right_type, right_val = evaluate_expression(right_node)
            if left_type is None or right_type is None:
                return (None, None)
            # Exigir operandos numéricos para comparaciones
            if not (left_type in ["INT", "FLOAT"] and right_type in ["INT", "FLOAT"]):
                error(f"No se pueden comparar tipos {left_type} y {right_type} con '{op}'")
                return (None, None)
            # Resultado booleano
            result_type = "BOOL"
            const_val = None
            if left_val is not None and right_val is not None:
                # Realizar comparación constante
                if op == '<':
                    const_val = left_val < right_val
                elif op == '>':
                    const_val = left_val > right_val
                elif op == '<=':
                    const_val = left_val <= right_val
                elif op == '>=':
                    const_val = left_val >= right_val
            return (result_type, const_val)

        # Operador unario lógico NOT
        if tag == 'not':
            expr_node = node[1]
            expr_type, expr_val = evaluate_expression(expr_node)
            if expr_type is None:
                return (None, None)
            if expr_type != "BOOL":
                error("Operador '!' aplicado a un tipo no booleano")
                return (None, None)
            result_type = "BOOL"
            const_val = None
            if expr_val is not None:
                const_val = not expr_val
            return (result_type, const_val)

        # Expresión de asignación (como parte de otra expresión): ID = expr
        if tag == 'assignment':
            # Asignación como expresión: actualiza la variable y devuelve su tipo/valor
            var_name = node[1]
            expr_node = node[2]
            # Verificar que la variable exista y obtener su tipo
            var_type = find_variable_type(var_name)
            if var_type is None:
                if var_name in declared_names:
                    error(f"La variable '{var_name}' se utiliza fuera de su ámbito")
                else:
                    error(f"La variable '{var_name}' no ha sido declarada")
                return (None, None)
            # Evaluar la expresión del lado derecho
            expr_type, expr_val = evaluate_expression(expr_node)
            if expr_type is None:
                # Hubo error en la expresión derecha
                return (None, None)
            # Revisar compatibilidad de tipos
            if not types_compatible(var_type, expr_type):
                error(f"Incompatibilidad de tipos en asignación a '{var_name}': se esperaba {var_type} pero se obtuvo {expr_type}")
            else:
                # Actualizar valor constante en la tabla si es conocido, o eliminarlo si deja de ser constante
                if expr_val is not None:
                    tabla_simbolos[var_name]["valor"] = expr_val
                else:
                    # Si se asigna algo no constante, remover cualquier valor previo conocido
                    if "valor" in tabla_simbolos[var_name]:
                        tabla_simbolos[var_name].pop("valor", None)
            # El tipo resultante de la expresión de asignación es el tipo de la variable (asignación produce ese valor)
            return (var_type, expr_val)

        # Expresión de incremento como parte de otra expresión (postfijo i++ o prefijo, según AST)
        if tag == 'increment':
            # Podría tener forma ('increment', var, '++') en caso de post-incremento
            var_name = node[1]
            var_type = find_variable_type(var_name)
            if var_type is None:
                if var_name in declared_names:
                    error(f"La variable '{var_name}' se utiliza fuera de su ámbito")
                else:
                    error(f"La variable '{var_name}' no ha sido declarada")
                return (None, None)
            # Debe ser tipo numérico para incrementar
            if var_type not in ["INT", "FLOAT"]:
                error(f"No se puede aplicar '++' a la variable '{var_name}' de tipo {var_type}")
                return (None, None)
            # Determinar valor constante antes del incremento
            const_val_before = None
            if "valor" in tabla_simbolos.get(var_name, {}):
                const_val_before = tabla_simbolos[var_name]["valor"]
            # Actualizar valor de la variable sumándole 1 si se conoce constante
            if const_val_before is not None:
                # Calcular nuevo valor constante y actualizar la tabla de símbolos
                new_val = const_val_before + 1
                tabla_simbolos[var_name]["valor"] = new_val
            else:
                # Si no se conoce valor actual, eliminamos cualquier valor constante previo
                if var_name in tabla_simbolos and "valor" in tabla_simbolos[var_name]:
                    tabla_simbolos[var_name].pop("valor", None)
            # El resultado de la expresión i++ es el valor de la variable *antes* del incremento
            return (var_type, const_val_before)

        if tag == 'decrement':
            # Similar a 'increment' pero restando 1
            var_name = node[1]
            var_type = find_variable_type(var_name)
            if var_type is None:
                if var_name in declared_names:
                    error(f"La variable '{var_name}' se utiliza fuera de su ámbito")
                else:
                    error(f"La variable '{var_name}' no ha sido declarada")
                return (None, None)
            if var_type not in ["INT", "FLOAT"]:
                error(f"No se puede aplicar '--' a la variable '{var_name}' de tipo {var_type}")
                return (None, None)
            const_val_before = None
            if "valor" in tabla_simbolos.get(var_name, {}):
                const_val_before = tabla_simbolos[var_name]["valor"]
            if const_val_before is not None:
                new_val = const_val_before - 1
                tabla_simbolos[var_name]["valor"] = new_val
            else:
                if var_name in tabla_simbolos and "valor" in tabla_simbolos[var_name]:
                    tabla_simbolos[var_name].pop("valor", None)
            return (var_type, const_val_before)

        # Expresión de incremento compuesto (i += N)
        if tag == 'increment_by':
            var_name = node[1]
            increment_val = node[2]  # valor numérico a incrementar (constante entera según gramática)
            var_type = find_variable_type(var_name)
            if var_type is None:
                if var_name in declared_names:
                    error(f"La variable '{var_name}' se utiliza fuera de su ámbito")
                else:
                    error(f"La variable '{var_name}' no ha sido declarada")
                return (None, None)
            if var_type not in ["INT", "FLOAT"]:
                error(f"No se puede aplicar '+=' a la variable '{var_name}' de tipo {var_type}")
                return (None, None)
            # Determinar tipo del incremento (entero por gramática, pero podría ser considerado INT)
            inc_type = "INT" if isinstance(increment_val, int) else "FLOAT"
            # Si la variable es FLOAT y el incremento es INT, lo consideramos compatible (se convierte a float implícitamente)
            if var_type == "INT" and inc_type != "INT":
                # Asignando float a int -> incompatibilidad
                error(f"Incompatibilidad de tipos en '{var_name} += {increment_val}': {var_type} += {inc_type}")
            # Actualizar valor constante si aplicable
            if "valor" in tabla_simbolos.get(var_name, {}):
                current_val = tabla_simbolos[var_name]["valor"]
            else:
                current_val = None
            new_const = None
            if current_val is not None:
                try:
                    new_const = current_val + increment_val
                except Exception:
                    new_const = None
            if new_const is not None:
                tabla_simbolos[var_name]["valor"] = new_const
            else:
                if var_name in tabla_simbolos and "valor" in tabla_simbolos[var_name]:
                    tabla_simbolos[var_name].pop("valor", None)
            # El resultado de la expresión (i += N) lo tomamos como el tipo de la variable después de asignar
            return (var_type, None if current_val is None else new_const)

        # Expresión de asignación de incremento (forma i = i + N)
        if tag == 'increment_assign':
            # Esta forma se trata como una asignación normal: var_name = (expr)
            var_name = node[1]
            right_var = node[2]
            increment_val = node[3]
            # Construir nodo de expresión equivalente: right_var + increment_val
            expr_node = ('operation', '+', ('id', right_var), ('number', increment_val))
            # Ahora tratar como una asignación normal (esto actualizará la variable var_name)
            if var_name != right_var:
                # Si los identificadores son distintos (caso general), asegurarse de que ambos existen
                if find_variable_type(right_var) is None:
                    if right_var in declared_names:
                        error(f"La variable '{right_var}' se utiliza fuera de su ámbito")
                    else:
                        error(f"La variable '{right_var}' no ha sido declarada")
            # Reutilizar la lógica de assignment como expresión
            return evaluate_expression(('assignment', var_name, expr_node))

        # Operador ternario (condicional) ?:
        if tag == 'ternary':
            condition_node = node[1]
            true_node = node[2]
            false_node = node[3]
            cond_type, cond_val = evaluate_expression(condition_node)
            true_type, true_val = evaluate_expression(true_node)
            false_type, false_val = evaluate_expression(false_node)
            if cond_type is None or true_type is None or false_type is None:
                return (None, None)
            if cond_type != "BOOL":
                error("La expresión condicional del operador ternario debe ser de tipo BOOL")
            # Para el tipo resultante, ambos brazos deben ser compatibles
            result_type = None
            if true_type == false_type:
                result_type = true_type
            else:
                # Permitir unificación de INT y FLOAT a FLOAT
                if {true_type, false_type} <= {"INT", "FLOAT"}:
                    result_type = "FLOAT"
                else:
                    error(f"Los tipos de las expresiones del operador ternario no coinciden: {true_type} vs {false_type}")
            # Determinar valor constante si la condición es constante
            const_val = None
            if cond_val is not None:
                # Si se conoce la condición en tiempo de compilación, elegir la rama correspondiente
                if cond_val is True:
                    const_val = true_val
                else:
                    const_val = false_val
            return (result_type, const_val)

        # Lista (arreglo) literal
        if tag == 'list':
            elements = node[1]  # lista de expresiones
            elem_type = None
            all_same_type = True
            for elem in elements:
                t, v = evaluate_expression(elem)
                if t is None:
                    # Si hay error en un elemento, detener
                    all_same_type = False
                else:
                    if elem_type is None:
                        elem_type = t
                    elif t != elem_type:
                        all_same_type = False
                # No almacenamos valores constantes individuales de cada elemento para la lista
            # Definir un tipo de lista (no existe un tipo de variable lista predefinido en este lenguaje simple)
            list_type = "LIST"
            # Opcionalmente, podríamos señalar error si los tipos internos difieren, pero no es requerido explícitamente.
            return (list_type, None)

        # Si el nodo no coincide con ningún caso manejado
        return (None, None)

    def analyze_statement(node):
        """
        Analiza semánticamente un nodo de tipo 'statement' del AST.
        Maneja declaraciones, asignaciones, estructuras de control y ámbitos.
        """
        if not isinstance(node, tuple):
            return  # En principio, cada sentencia debería ser una tupla etiquetada

        tag = node[0]

        if tag in ('declaracion, =', 'declaracion_asignacion, ='):
            # Declaración de variable (posiblemente con asignación inicial)
            # Formatos posibles:
            # ('declaracion, =', tipo, nombre)
            # ('declaracion_asignacion, =', tipo, nombre, expr_inicial)
            var_type_token = node[1]
            var_name = node[2]
            # Convertir el token de tipo al string del tipo (en mayúsculas)
            # El token puede venir como 'int' o 'INT'; unificar a formato "INT", "FLOAT", etc.
            var_type = str(var_type_token).upper()
            if tag == 'declaracion, =' :
                # Declaración sin asignación inicial
                declare_variable(var_name, var_type)
            else:
                # Declaración con asignación inicial
                init_expr = node[3]
                # Primero, declarar la variable en el ámbito actual
                declare_variable(var_name, var_type)
                # Si la variable se declaró exitosamente, verificar la expresión de inicialización
                # (Incluso si hay error en expr, la variable queda declarada para evitar cascada de errores)
                expr_type, expr_val = evaluate_expression(init_expr)
                if expr_type is None:
                    return
                # Comprobar compatibilidad de tipos entre variable y expresión
                if not types_compatible(var_type, expr_type):
                    error(f"Incompatibilidad de tipos en inicialización de '{var_name}': {var_type} = {expr_type}")
                else:
                    # Asignación inicial válida: guardar valor constante si aplica
                    if expr_val is not None:
                        tabla_simbolos[var_name]["valor"] = expr_val
                    else:
                        # Si la expresión no es constante, asegurarse de no dejar valor previo
                        tabla_simbolos[var_name].pop("valor", None)

        elif tag == 'assignment, =':
            # Asignación de una variable existente: ('assignment, =', nombre, expr)
            var_name = node[1]
            expr_node = node[2]
            # Verificar existencia y tipo de la variable
            var_type = find_variable_type(var_name)
            if var_type is None:
                if var_name in declared_names:
                    error(f"La variable '{var_name}' se utiliza fuera de su ámbito")
                else:
                    error(f"La variable '{var_name}' no ha sido declarada")
                return
            # Evaluar la expresión del lado derecho
            expr_type, expr_val = evaluate_expression(expr_node)
            if expr_type is None:
                return
            # Revisar compatibilidad de tipos
            if not types_compatible(var_type, expr_type):
                error(f"Incompatibilidad de tipos en asignación a '{var_name}': se esperaba {var_type} pero se obtuvo {expr_type}")
            else:
                # Actualizar valor constante si es conocido
                if expr_val is not None:
                    tabla_simbolos[var_name]["valor"] = expr_val
                else:
                    # Si se asigna un valor no constante, remover cualquier valor almacenado previamente
                    tabla_simbolos[var_name].pop("valor", None)

        elif tag == 'increment_stmt':
            # Sentencia de incremento (p.ej., i++;)
            var_name = node[1]
            var_type = find_variable_type(var_name)
            if var_type is None:
                if var_name in declared_names:
                    error(f"La variable '{var_name}' se utiliza fuera de su ámbito")
                else:
                    error(f"La variable '{var_name}' no ha sido declarada")
                return
            if var_type not in ["INT", "FLOAT"]:
                error(f"No se puede aplicar '++' a la variable '{var_name}' de tipo {var_type}")
                return
            # Si la variable tiene valor constante, incrementar en 1
            if "valor" in tabla_simbolos.get(var_name, {}):
                tabla_simbolos[var_name]["valor"] += 1
            else:
                # Eliminar valor constante previo si existía, ya que ahora no se conoce
                if var_name in tabla_simbolos and "valor" in tabla_simbolos[var_name]:
                    tabla_simbolos[var_name].pop("valor", None)
            # (La sentencia i++ no produce un valor utilizado, solo el efecto de lado sobre la variable)

        elif tag == 'decrement_stmt':
            # Sentencia de decremento (p.ej., i--;)
            var_name = node[1]
            var_type = find_variable_type(var_name)
            if var_type is None:
                if var_name in declared_names:
                    error(f"La variable '{var_name}' se utiliza fuera de su ámbito")
                else:
                    error(f"La variable '{var_name}' no ha sido declarada")
                return
            if var_type not in ["INT", "FLOAT"]:
                error(f"No se puede aplicar '--' a la variable '{var_name}' de tipo {var_type}")
                return
            if "valor" in tabla_simbolos.get(var_name, {}):
                tabla_simbolos[var_name]["valor"] -= 1
            else:
                if var_name in tabla_simbolos and "valor" in tabla_simbolos[var_name]:
                    tabla_simbolos[var_name].pop("valor", None)

        elif tag == 'if':
            # Sentencia if sin else: ('if', condición, cuerpo)
            condition_node = node[1]
            body_node = node[2]
            cond_type, cond_val = evaluate_expression(condition_node)
            if cond_type is not None and cond_type != "BOOL":
                error("La condición del 'if' debe ser de tipo BOOL")
            # Analizar la sentencia del cuerpo (posiblemente un bloque o una sola sentencia)
            analyze_statement(body_node)

        elif tag == 'if-else':
            # Sentencia if-else: ('if-else', condición, cuerpo_then, cuerpo_else)
            condition_node = node[1]
            then_node = node[2]
            else_node = node[3]
            cond_type, cond_val = evaluate_expression(condition_node)
            if cond_type is not None and cond_type != "BOOL":
                error("La condición del 'if-else' debe ser de tipo BOOL")
            # Analizar ambos bloques/cuerpos
            analyze_statement(then_node)
            analyze_statement(else_node)

        elif tag == 'while':
            # Bucle while: ('while', condición, cuerpo)
            condition_node = node[1]
            body_node = node[2]
            cond_type, cond_val = evaluate_expression(condition_node)
            if cond_type is not None and cond_type != "BOOL":
                error("La condición del 'while' debe ser de tipo BOOL")
            analyze_statement(body_node)

        elif tag == 'for':
            # Bucle for: ('for', init, condicion, expr_final, cuerpo)
            init_node = node[1]
            cond_node = node[2]
            post_node = node[3]
            body_node = node[4]
            # Nuevo ámbito si la inicialización es una declaración (variable local del for)
            if isinstance(init_node, tuple) and init_node[0] == 'declaration':
                # Push de nuevo ámbito para la variable del for
                scope_stack.append({})
                # El nodo 'declaration' en el AST del for está en formato ('declaration', tipo, nombre, valor_inicial)
                var_type_token = init_node[1]
                var_name = init_node[2]
                init_value_node = init_node[3]
                var_type = str(var_type_token).upper()
                # Declarar variable del for en nuevo ámbito
                declare_variable(var_name, var_type)
                # Procesar inicialización (asignación inicial)
                expr_type, expr_val = evaluate_expression(init_value_node)
                if expr_type is not None:
                    if not types_compatible(var_type, expr_type):
                        error(f"Incompatibilidad de tipos en inicialización de '{var_name}' en el for: se esperaba {var_type} pero se obtuvo {expr_type}")
                    else:
                        if expr_val is not None:
                            tabla_simbolos[var_name]["valor"] = expr_val
                        else:
                            tabla_simbolos[var_name].pop("valor", None)
            else:
                # La inicialización no es declaración (sino una asignación existente)
                # No abrimos nuevo ámbito en este caso
                if init_node is not None:
                    analyze_statement(init_node)
            # Verificar condición del for
            if cond_node is not None:
                cond_type, cond_val = evaluate_expression(cond_node)
                if cond_type is not None and cond_type != "BOOL":
                    error("La condición del 'for' debe ser de tipo BOOL")
            # Expresión final (ejecutada al final de cada iteración, típicamente incremento)
            if post_node is not None:
                analyze_statement(post_node) if isinstance(post_node, tuple) else evaluate_expression(post_node)
            # Analizar el cuerpo del for
            analyze_statement(body_node)
            # Salir del ámbito del for si se creó uno
            if isinstance(init_node, tuple) and init_node[0] == 'declaration':
                scope_stack.pop()

        elif tag == 'block':
            # Bloque de código: ('block', [lista_de_sentencias])
            # Abrir un nuevo ámbito para el bloque
            scope_stack.append({})
            # Recorrer las sentencias dentro del bloque
            statements_list = node[1]
            for stmt in statements_list:
                analyze_statement(stmt)
            # Cerrar el ámbito (los nombres declarados aquí quedan fuera de alcance)
            scope_stack.pop()

        elif tag == 'expr':
            # Sentencia expresión: simplemente evaluar la expresión por sus efectos
            expr_node = node[1]
            evaluate_expression(expr_node)

        else:
            # Cualquier otro tipo de nodo de sentencia no manejado explícitamente
            # Intentar tratarlo como bloque de sentencias o expresión
            if isinstance(node, list):
                # Lista de sentencias
                for stmt in node:
                    analyze_statement(stmt)
            else:
                # Podría ser una expresión solitaria
                evaluate_expression(node)

    # --- Inicio del análisis semántico ---
    if arbol is None:
        return  # Si no hay árbol (posible error sintáctico previo), no hacer nada

    # El AST del programa se espera como ('program', [lista_de_sentencias])
    if isinstance(arbol, tuple) and arbol[0] == 'program':
        for stmt in arbol[1]:
            analyze_statement(stmt)
    else:
        # En caso de que el AST sea directamente una lista de sentencias u otra forma
        if isinstance(arbol, list):
            for stmt in arbol:
                analyze_statement(stmt)
        else:
            analyze_statement(arbol)
