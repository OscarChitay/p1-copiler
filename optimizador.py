# optimizador.py
def optimizar_tac(lista_tac):
    """
    Aplica optimizaciones básicas a una lista de instrucciones TAC:
    - Elimina asignaciones redundantes (ej: x = x).
    - Realiza plegado de constantes en expresiones aritméticas y lógicas.
    - Simplifica saltos incondicionales innecesarios (goto a la siguiente línea).
    - Remueve etiquetas de salto no utilizadas.
    Devuelve una nueva lista optimizada de instrucciones TAC.
    """
    tac_opt = []
    # 1. Recorrer TAC original y optimizar localmente
    for instr in lista_tac:
        instr = instr.strip()
        if not instr:
            continue
        # Omitir declaraciones, pero mantenerlas en la salida optimizada
        if instr.startswith("DECL"):
            tac_opt.append(instr)
            continue
        # Eliminar asignaciones redundantes del tipo "x = x"
        if "=" in instr:
            partes = instr.split("=")
            if len(partes) >= 2:
                lhs = partes[0].strip()
                rhs = partes[1].strip()
                if rhs == lhs:
                    continue  # saltar "x = x"
        # Plegado de constantes: detectar expresiones const op const
        if "=" in instr and any(
                op in instr for op in ["+", "-", "*", "/", "&&", "||", "==", "!=", ">", "<", ">=", "<="]):
            # Extraer lado derecho
            dest, expr = instr.split("=", 1)
            dest = dest.strip()
            expr = expr.strip()
            tokens = expr.split()
            if len(tokens) == 3:
                a, op, b = tokens
                # Verificar si a y b son constantes numéricas o booleanas
                if a.lstrip('-').isdigit() or a.lower() in {"true", "false"}:
                    if b.lstrip('-').isdigit() or b.lower() in {"true", "false"}:
                        # Convertir "true"/"false" a 1/0 para evaluar
                        def val(x):
                            if x.lower() == "true": return 1
                            if x.lower() == "false": return 0
                            return int(x)

                        A, B = val(a), val(b)
                        resultado = None
                        try:
                            if op == "+":
                                resultado = A + B
                            elif op == "-":
                                resultado = A - B
                            elif op == "*":
                                resultado = A * B
                            elif op == "/":
                                resultado = A // B  # división entera
                            elif op == "&&":
                                resultado = 1 if (A != 0 and B != 0) else 0
                            elif op == "||":
                                resultado = 1 if (A != 0 or B != 0) else 0
                            elif op == "==":
                                resultado = 1 if A == B else 0
                            elif op == "!=":
                                resultado = 1 if A != B else 0
                            elif op == ">":
                                resultado = 1 if A > B else 0
                            elif op == "<":
                                resultado = 1 if A < B else 0
                            elif op == ">=":
                                resultado = 1 if A >= B else 0
                            elif op == "<=":
                                resultado = 1 if A <= B else 0
                        except Exception:
                            resultado = None
                        if resultado is not None:
                            # Reemplazar la instrucción por asignación del resultado constante
                            instr = f"{dest} = {resultado}"
        # Simplificar saltos condicionales con constantes: ifFalse const goto L
        if instr.startswith("ifFalse"):
            partes = instr.split()
            # partes: [ "ifFalse", cond, "goto", etiqueta ]
            if len(partes) >= 4:
                cond = partes[1]
                etiqueta = partes[3]
                valor = None
                if cond.lower() == "true":
                    valor = True
                elif cond.lower() == "false":
                    valor = False
                elif cond.lstrip('-').isdigit():
                    valor = (int(cond) != 0)
                if valor is not None:
                    if valor is True:
                        # ifFalse true ... -> nunca salta (condición siempre verdadera), podemos eliminar
                        continue
                    else:
                        # ifFalse false ... -> siempre salta, reemplazar por goto directo
                        instr = f"goto {etiqueta}"
        tac_opt.append(instr)
    # 2. Remover saltos goto redundantes que van a la siguiente instrucción
    i = 0
    tac_final = []
    while i < len(tac_opt):
        instr = tac_opt[i]
        if instr.startswith("goto"):
            target = instr.split()[1] if len(instr.split()) > 1 else ""
            # Si la siguiente línea es la etiqueta de destino, eliminar el goto
            if i + 1 < len(tac_opt) and tac_opt[i + 1].strip() == f"{target}:":
                i += 1
                continue  # saltar el goto
        tac_final.append(instr)
        i += 1
    # 3. Eliminar etiquetas no utilizadas
    usadas = set()
    for instr in tac_final:
        if instr.startswith("goto"):
            partes = instr.split()
            if len(partes) > 1:
                usadas.add(partes[1].strip(":"))
        if instr.startswith("ifFalse"):
            partes = instr.split()
            if len(partes) > 3:
                usadas.add(partes[3].strip(":"))
    tac_final_2 = []
    for instr in tac_final:
        if instr.endswith(":"):
            etiqueta = instr.strip(":")
            if etiqueta and etiqueta not in usadas:
                continue  # eliminar etiqueta que no es destino de ningún salto
        tac_final_2.append(instr)
    return tac_final_2
