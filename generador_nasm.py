# generador_nasm.py
def generar_codigo_maquina(lista_tac):
    """
    Convierte una lista de instrucciones TAC optimizadas en código ensamblador NASM de 32 bits.
    Genera un archivo "codigo.asm" con la sección de datos (.data/.bss) y código (.text).
    """
    asm_lines = []
    data_lines = []
    string_consts = {}
    temp_vars = set()
    op_tokens = {"+", "-", "*", "/", "&&", "||", "==", "!=", ">", "<", ">=", "<=", "!"}
    # 1. Preparar secciones de datos (.data) y .bss para variables
    variables = {}
    for instr in lista_tac:
        instr = instr.strip()
        if not instr:
            continue
        # Si es declaración, registrar la variable y su tipo
        if instr.startswith("DECL"):
            # Formato: "DECL TIPO nombre"
            parts = instr.split()
            if len(parts) >= 3:
                tipo_var = parts[1]
                nombre = parts[2]
                variables[nombre] = tipo_var
        # Si es asignación u operación TAC, identificar nombres de variables/temporales involucrados
        if "=" in instr:
            izq, der = instr.split("=", 1)
            var_dest = izq.strip()
            if var_dest and var_dest not in variables:
                variables[var_dest] = "INT"  # Asumimos INT por defecto
            # Revisar tokens del lado derecho
            tokens = der.strip().replace(',', ' ').split()
            for token in tokens:
                token = token.strip().strip(";")
                if (not token) or (token in op_tokens) or token.lower() in {"true","false","goto","iffalse"}:
                    continue  # ignorar operadores y palabras clave
                if token.startswith("\"") and token.endswith("\""):
                    # Literal de cadena: asignar etiqueta en .data si no se ha hecho
                    if token not in string_consts:
                        label = f"str_{len(string_consts)+1}"
                        contenido = token.strip("\"")
                        string_consts[token] = label
                        data_lines.append(f'{label} db "{contenido}", 0')
                elif not token.isdigit() and not (token.startswith('-') and token[1:].isdigit()):
                    # Token es una variable temporal o identificador no numérico
                    if token not in variables:
                        variables[token] = "INT"

        # --- NUEVO ---  soportar cadenas en instrucciones PRINT
        if instr.startswith("PRINT"):
            token = instr[5:].strip()          # lo que viene después de PRINT
            if token.startswith("\"") and token.endswith("\""):
                if token not in string_consts:             # aún no registrada
                    label = f"str_{len(string_consts)+1}"
                    contenido = token.strip("\"")
                    string_consts[token] = label
                    data_lines.append(f'{label} db "{contenido}", 0')

    # Construir sección .data y .bss
    usa_fmt_int = any(instr.startswith("PRINT ") and not instr.split()[1].startswith('"')
                      for instr in lista_tac)
    asm_lines.append("section .data")
    asm_lines.extend(data_lines)
    # --- NUEVO ---
    if usa_fmt_int:
        asm_lines.append('fmt_int db "%d", 10, 0')  # "%d\\n"
    # ---------------
    asm_lines.append("section .bss")

    for nombre_var in variables:
        if nombre_var.startswith("L"):
            continue  # omitir etiquetas de salto como variables
        asm_lines.append(f"{nombre_var} resd 1")  # reservar 4 bytes (un entero 32-bit)

    asm_lines.append("extern _printf")
    asm_lines.append("section .text")
    asm_lines.append("global _main")
    asm_lines.append("_main:")
    asm_lines.append("    push ebp")
    asm_lines.append("    mov ebp, esp")
    # 2. Traducir cada instrucción TAC a instrucciones NASM equivalentes
    for instr in lista_tac:
        instr = instr.strip()
        if not instr or instr.startswith("DECL"):
            continue  # omitir declaraciones (ya manejadas en .bss)
        if instr.endswith(":"):
            # Etiqueta de salto (p.ej., L1:)
            asm_lines.append(instr)
            continue
        if instr.startswith("goto"):
            # Salto incondicional
            _, etiqueta = instr.split()
            asm_lines.append(f"    jmp {etiqueta}")
            continue
        if instr.startswith("ifFalse"):
            # Salto condicional ifFalse X goto L -> jump si X es 0
            parts = instr.split()
            _, cond, _, etiqueta = parts
            # Cargar condición en EAX
            if cond.lower() == "true" or cond.lower() == "false":
                valor = "1" if cond.lower() == "true" else "0"
                asm_lines.append(f"    mov eax, {valor}")
            elif cond.lstrip('-').isdigit():
                asm_lines.append(f"    mov eax, {cond}")
            else:
                asm_lines.append(f"    mov eax, [{cond}]")
            asm_lines.append("    cmp eax, 0")
            asm_lines.append(f"    je {etiqueta}")
            continue

        # --- NUEVO ---  traducción de PRINT
        if instr.startswith("PRINT"):
            arg = instr[5:].strip()

            if arg.startswith("\""):                  # imprimir cadena literal
                label = string_consts[arg]            # etiqueta en .data
                asm_lines.append(f"    push {label}") # push dirección de la cadena
                asm_lines.append("    call _printf")
                asm_lines.append("    add esp, 4")    # limpiar la pila
            else:                                     # imprimir variable entera
                asm_lines.append(f"    push dword [{arg}]")   # valor de la variable
                asm_lines.append("    push fmt_int")          # formato "%d\\n"
                asm_lines.append("    call _printf")
                asm_lines.append("    add esp, 8")            # limpiar la pila
            continue

        # Procesar asignación u operación: formato "dest = expr"

        if "=" in instr:
            dest, expr = instr.split("=", 1)
            dest = dest.strip()
            expr = expr.strip().strip(";")
            # Asignación de literal de cadena
            if expr.startswith("\"") and expr.endswith("\""):
                label = string_consts.get(expr)
                if label:
                    asm_lines.append(f"    mov dword [{dest}], {label}")
                continue
            # Asignación de booleano literal
            if expr.lower() == "true" or expr.lower() == "false":
                valor = "1" if expr.lower() == "true" else "0"
                asm_lines.append(f"    mov dword [{dest}], {valor}")
                continue
            tokens = expr.split()
            # Caso 1: asignación simple (dest = var/const)
            if len(tokens) == 1:
                t = tokens[0]
                if t.lstrip('-').isdigit():
                    asm_lines.append(f"    mov dword [{dest}], {t}")
                else:
                    asm_lines.append(f"    mov eax, [{t}]")
                    asm_lines.append(f"    mov dword [{dest}], eax")
                continue
            # Caso 2: operación unaria (¡solo soportamos '!' lógico)
            if tokens[0] == "!":
                opnd = tokens[1]
                if opnd.lstrip('-').isdigit():
                    asm_lines.append(f"    mov eax, {opnd}")
                else:
                    asm_lines.append(f"    mov eax, [{opnd}]")
                asm_lines.append("    cmp eax, 0")
                asm_lines.append("    mov eax, 0")
                asm_lines.append("    sete al")  # AL=1 si opnd era 0, sino AL=0
                asm_lines.append(f"    mov dword [{dest}], eax")
                continue
            # Caso 3: operación binaria o comparación (forma: A op B)
            if len(tokens) == 3:
                A, op, B = tokens
                # Cargar A en EAX
                if A.lstrip('-').isdigit():
                    asm_lines.append(f"    mov eax, {A}")
                else:
                    asm_lines.append(f"    mov eax, [{A}]")
                # Seleccionar instrucción según el operador
                if op == "+":
                    if B.lstrip('-').isdigit():
                        asm_lines.append(f"    add eax, {B}")
                    else:
                        asm_lines.append(f"    add eax, [{B}]")
                    asm_lines.append(f"    mov dword [{dest}], eax")
                elif op == "-":
                    if B.lstrip('-').isdigit():
                        asm_lines.append(f"    sub eax, {B}")
                    else:
                        asm_lines.append(f"    sub eax, [{B}]")
                    asm_lines.append(f"    mov dword [{dest}], eax")
                elif op == "*":
                    if B.lstrip('-').isdigit():
                        asm_lines.append(f"    imul eax, {B}")
                    else:
                        asm_lines.append(f"    imul eax, [{B}]")
                    asm_lines.append(f"    mov dword [{dest}], eax")
                elif op == "/":
                    asm_lines.append("    cdq")  # extender signo (EDX:EAX para idiv)
                    if B.lstrip('-').isdigit():
                        asm_lines.append(f"    mov ebx, {B}")
                    else:
                        asm_lines.append(f"    mov ebx, [{B}]")
                    asm_lines.append("    idiv ebx")
                    asm_lines.append(f"    mov dword [{dest}], eax")
                elif op in ("&&", "||"):
                    # AND/OR lógicos: convertir A y B a 0/1 y combinar
                    asm_lines.append("    cmp eax, 0")
                    asm_lines.append("    mov eax, 0")
                    asm_lines.append("    setne al")  # EAX = 1 si A != 0
                    if B.lstrip('-').isdigit():
                        asm_lines.append(f"    mov ebx, {B}")
                    else:
                        asm_lines.append(f"    mov ebx, [{B}]")
                    asm_lines.append("    cmp ebx, 0")
                    asm_lines.append("    mov ebx, 0")
                    asm_lines.append("    setne bl")  # EBX = 1 si B != 0
                    if op == "&&":
                        asm_lines.append("    and eax, ebx")
                    else:
                        asm_lines.append("    or eax, ebx")
                    asm_lines.append(f"    mov dword [{dest}], eax")
                elif op in ("==", "!=", ">", "<", ">=", "<="):
                    # Comparaciones: usar CMP y saltos condicionales para setear resultado 0/1
                    if B.lstrip('-').isdigit():
                        asm_lines.append(f"    cmp eax, {B}")
                    else:
                        asm_lines.append(f"    cmp eax, [{B}]")
                    asm_lines.append("    mov eax, 0")
                    if op == "==":
                        asm_lines.append("    sete al")
                    elif op == "!=":
                        asm_lines.append("    setne al")
                    elif op == ">":
                        asm_lines.append("    setg al")
                    elif op == "<":
                        asm_lines.append("    setl al")
                    elif op == ">=":
                        asm_lines.append("    setge al")
                    elif op == "<=":
                        asm_lines.append("    setle al")
                    asm_lines.append(f"    mov dword [{dest}], eax")
                else:
                    # Operador no reconocido (fallback a mov)
                    if B.lstrip('-').isdigit():
                        asm_lines.append(f"    mov dword [{dest}], {B}")
                    else:
                        asm_lines.append(f"    mov dword [{dest}], [{B}]")
    # 3. Finalizar función main (retorno al SO)
    asm_lines.append("    mov eax, 0")
    asm_lines.append("    pop ebp")
    asm_lines.append("    ret")
    # Guardar el código ensamblador en archivo
    with open("codigo.asm", "w") as f:
        for line in asm_lines:
            f.write(line + "\n")
    return asm_lines  # opcionalmente retornamos la lista de líneas ASM
