import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import tkinter.messagebox as msgbox

import semantico
from lexico import lexer
from sintactico import parser
import diagram as dg
import generador_codigo as gc


# Diccionario para la tabla de símbolos
tabla_simbolos = {}


def agregar_a_tabla(token, tipo, valor=None):
    """
    Agrega un token a la tabla de símbolos con su tipo y valor.
    """
    tabla_simbolos[token] = {"tipo": tipo}


def limpiar_resultados():
    """
        limpiar toda la pantalla
    """
    editor.delete("1.0", tk.END)
    resultado_tokens.delete("1.0", tk.END)
    resultado_arbol.delete("1.0", tk.END)
    resultado_errores.delete("1.0", tk.END)
    tabla_simbolos.clear()

    # Limpiar la tabal de simbolos en la interfaz
    for item in tree_tabla_simbolos.get_children():
        tree_tabla_simbolos.delete(item)


def realizar_analisis_lexico():
    """
    Realiza el análisis léxico del código ingresado en el editor.
    """
    codigo = editor.get("1.0", tk.END).strip()
    lexer.input(codigo)
    resultado_tokens.delete("1.0", tk.END)
    tabla_simbolos.clear()
    # Limpiar la tabla
    for item in tree_tabla_simbolos.get_children():
        tree_tabla_simbolos.delete(item)
    resultado_tokens.insert(tk.END, "--- Tokens ---\n")
    for token in lexer:
        resultado_tokens.insert(tk.END, f"{token}\n")
        agregar_a_tabla(token.value, token.type)
    # Actualizar la tabla de símbolos
    actualizar_tabla_simbolos()


def realizar_analisis_sintactico():
    codigo = editor.get("1.0", tk.END).strip()
    resultado_arbol.delete("1.0", tk.END)
    resultado_errores.delete("1.0", tk.END)  # limpiar el panel de errores al iniciar

    try:
        resultado = parser.parse(codigo)  # Generar AST a partir del código
    except Exception as e:
        # Si hay error sintáctico, se muestra en el área de árbol y se aborta
        resultado_arbol.insert(tk.END, f"Error en análisis sintáctico: {e}")
        return

    # Analizar semánticamente el AST y obtener lista de errores (si los hay)
    errores_sem = semantico.analizar_semantica(resultado, tabla_simbolos)
    if errores_sem:
        # Poblar el panel de errores con los mensajes
        resultado_errores.insert(tk.END, "--- Errores Semánticos ---\n")
        for err in errores_sem:
            resultado_errores.insert(tk.END, err + "\n")
        # No continuar con generación de árbol si hubo errores
        return

    # Si no hubo errores semánticos, mostrar el AST en texto
    resultado_arbol.insert(tk.END, f"--- Árbol Sintáctico ---\n{resultado}\n")
    # Generar y mostrar visualmente el árbol sintáctico
    dot = dg.dibujar_arbol_completo(resultado)
    dot.render("Arbol_Sintactico", format="png", view=True)



def actualizar_tabla_simbolos():
    """
    Actualiza la tabla de símbolos en la interfaz.
    """
    for simbolo, datos in tabla_simbolos.items():
        tree_tabla_simbolos.insert("", "end", values=(simbolo, datos["tipo"]))

def realizar_generador_codigo_intermedio():
    """
    Esta función se invoca cuando el usuario hace clic en el botón "Generar Código Intermedio".
    Llama al generador de código intermedio, que genera TAC y SSA, y muestra los resultados en una ventana emergente.
    """
    codigo = editor.get("1.0", tk.END).strip()
    resultado_arbol.delete("1.0", tk.END)
    # Verificar si hay errores semánticos pendientes
    if resultado_errores.get("1.0", "end-1c").strip() != "":
        # Abortamos la generación de código lanzando una excepción controlada
        msgbox.showerror("Errores Semánticos", "Existen errores semánticos sin resolver.")
        return
    try:
        # Reutilizar el parser para obtener/validar el AST
        resultado = parser.parse(codigo)
        # Generar código intermedio solo si no hubo errores
        gc.generar_codigo_intermedio(resultado)
    except Exception as e:
        resultado_arbol.insert(tk.END, f"Error al generar código intermedio: {e}\n")


# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Analizador Léxico y Sintáctico")
ventana.geometry("1600x800")

# Marco principal
frame_principal = tk.Frame(ventana, bg="#1e1e1e")
frame_principal.pack(fill=tk.BOTH, expand=True)

# Marco izquierdo (editor de código)
frame_izquierdo = tk.Frame(frame_principal, bg="#1e1e1e")
frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Etiqueta del editor
tk.Label(frame_izquierdo, text="Editor de Código", bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 14)).pack(anchor="w")

# Editor de texto
frame_editor = tk.Frame(frame_izquierdo, bg="#1e1e1e")
frame_editor.pack(fill=tk.BOTH, expand=True)
editor = tk.Text(frame_editor, height=25, width=60, bg="#1e1e1e", fg="#d4d4d4",
                 insertbackground="#d4d4d4", font=("Consolas", 12), undo=True, wrap="none")
editor.pack(fill=tk.BOTH, expand=True)

# Nueva sección de Errores Semánticos
tk.Label(frame_izquierdo, text="Errores Semánticos", bg="#1e1e1e", fg="#d4d4d4",
         font=("Consolas", 14)).pack(anchor="w")
resultado_errores = scrolledtext.ScrolledText(frame_izquierdo, height=8, bg="#252526",
                                             fg="#d4d4d4", font=("Consolas", 12))
resultado_errores.pack(fill=tk.BOTH, expand=False, pady=(0, 10))

# Scroll horizontal y vertical
scroll_x = tk.Scrollbar(frame_izquierdo, orient="horizontal", command=editor.xview)
scroll_y = tk.Scrollbar(frame_izquierdo, orient="vertical", command=editor.yview)
editor.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

# Botones
frame_botones = tk.Frame(frame_izquierdo, bg="#1e1e1e")
frame_botones.pack(fill=tk.X, pady=10)

# btn_lexico

btn_lexico = tk.Button(frame_botones, text="Análisis Léxico", command=realizar_analisis_lexico, bg="#007acc",
                       fg="white", font=("Consolas", 10))
btn_lexico.pack(side=tk.LEFT, padx=5)

# btn_sintactico
btn_sintactico = tk.Button(frame_botones, text="Análisis Sintáctico & Semantico", command=realizar_analisis_sintactico,
                           bg="#007acc", fg="white", font=("Consolas", 10))
btn_sintactico.pack(side=tk.LEFT, padx=5)

# btn_codigo_intermedio
btn_generador = tk.Button(frame_botones, text="Generador de Código", command=realizar_generador_codigo_intermedio,
                           bg="#007acc", fg="white", font=("Consolas", 10))
btn_generador.pack(side=tk.LEFT, padx=5)

# btn_cls
btn_sintactico = tk.Button(frame_botones, text="clear", command=limpiar_resultados,
                           bg="#007acc", fg="white", font=("Consolas", 10))
btn_sintactico.pack(side=tk.LEFT, padx=5)

# btn_salir
btn_salir = tk.Button(frame_botones, text="Salir", command=ventana.quit, bg="#f14c4c", fg="white",
                      font=("Consolas", 10))
btn_salir.pack(side=tk.RIGHT, padx=5)

# Marco derecho (resultados y tabla de símbolos)
frame_derecho = tk.Frame(frame_principal, bg="#1e1e1e")
frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Área de resultados (tokens)
tk.Label(frame_derecho, text="Resultado Tokens", bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 14)).pack(anchor="w")
resultado_tokens = scrolledtext.ScrolledText(frame_derecho, height=8, bg="#252526", fg="#d4d4d4", font=("Consolas", 12))
resultado_tokens.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

# Área de resultados (árbol sintáctico)
tk.Label(frame_derecho, text="Resultado Árbol Sintáctico", bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 14)).pack(
    anchor="w")
resultado_arbol = scrolledtext.ScrolledText(frame_derecho, height=8, bg="#252526", fg="#d4d4d4", font=("Consolas", 12))
resultado_arbol.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

# Tabla de símbolos
tk.Label(frame_derecho, text="Tabla de Símbolos", bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 14)).pack(anchor="w")
tree_tabla_simbolos = ttk.Treeview(frame_derecho, columns=("Símbolo", "Tipo"), show="headings", height=10)
tree_tabla_simbolos.heading("Símbolo", text="Símbolo")
tree_tabla_simbolos.heading("Tipo", text="Tipo")
tree_tabla_simbolos.pack(fill=tk.BOTH, expand=True)

# Estilo de tabla
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#252526", foreground="#d4d4d4", fieldbackground="#252526",
                font=("Consolas", 12))
style.map("Treeview", background=[("selected", "#007acc")], foreground=[("selected", "white")])

# Iniciar la ventana
ventana.mainloop()
