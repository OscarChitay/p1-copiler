# Analizador Léxico y Sintáctico

Un compilador básico desarrollado en Python que implementa análisis léxico y sintáctico para un lenguaje de programación simplificado, con interfaz gráfica y generación de árboles sintácticos visuales.

![Analizador](https://img.shields.io/badge/Python-3.x-blue.svg)
![PLY](https://img.shields.io/badge/PLY-Lexical%20Analysis-green.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange.svg)
![Graphviz](https://img.shields.io/badge/Visualization-Graphviz-red.svg)

## 📋 Tabla de Contenidos

- [Características](#características)
- [Requisitos del Sistema](#requisitos-del-sistema)
- [Instalación](#instalación)
- [Uso](#uso)
- [Gramática Soportada](#gramática-soportada)
- [Componentes del Proyecto](#componentes-del-proyecto)
- [Ejemplos de Código](#ejemplos-de-código)
- [Análisis Implementado](#análisis-implementado)
- [Contribución](#contribución)
- [Autor](#autor)

## ✨ Características

- **Análisis Léxico Completo**: Reconocimiento de tokens, palabras reservadas, operadores y literales
- **Análisis Sintáctico**: Construcción de árboles sintácticos abstractos (AST)
- **Interfaz Gráfica Moderna**: Editor de código con resaltado y áreas de resultados
- **Visualización de Árboles**: Generación automática de diagramas de árboles sintácticos
- **Tabla de Símbolos**: Seguimiento de identificadores y sus tipos
- **Detección de Errores**: Manejo de errores léxicos y sintácticos
- **Soporte Completo de Operadores**: Aritméticos, lógicos, comparación y ternarios

## 🔧 Requisitos del Sistema

- Python 3.7 o superior
- PLY (Python Lex-Yacc)
- Tkinter (incluido con Python)
- Graphviz
- python-graphviz

## 📦 Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/OscarChitay/p1-copiler.git
cd p1-copiler
```

2. **Instalar dependencias:**
```bash
pip install ply graphviz
```

3. **Instalar Graphviz (sistema):**

   **Windows:**
   - Descargar desde: https://graphviz.org/download/
   - Agregar al PATH del sistema

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt-get install graphviz
   ```

   **macOS:**
   ```bash
   brew install graphviz
   ```

## 🚀 Uso

1. **Ejecutar la aplicación:**
```bash
python main.py
```

2. **Escribir código** en el editor (panel izquierdo)

3. **Realizar análisis:**
   - Clic en "Análisis Léxico" para tokenizar el código
   - Clic en "Análisis Sintáctico" para generar el árbol sintáctico

4. **Ver resultados:**
   - Los tokens aparecen en el panel superior derecho
   - El árbol sintáctico en texto en el panel medio derecho
   - La tabla de símbolos en el panel inferior derecho
   - El diagrama visual se abre automáticamente

## 📝 Gramática Soportada

### Palabras Reservadas
```
if, else, for, while, int, float, string
```

### Tipos de Datos
- **Enteros**: `123`, `456`
- **Flotantes**: `3.14`, `2.5`
- **Cadenas**: `"Hola mundo"`
- **Identificadores**: `variable`, `contador`

### Operadores

#### Aritméticos
```
+  (suma)
-  (resta)
*  (multiplicación)
/  (división)
-- (decremento)
```

#### Lógicos
```
&& (AND lógico)
|| (OR lógico)
```

#### Comparación
```
<  (menor que)
>  (mayor que)
== (igual)
!= (no igual)
```

#### Especiales
```
?  : (operador ternario)
=  (asignación)
```

### Estructuras de Control

#### Condicionales
```c
if (condicion) {
    // código
}

if (condicion) {
    // código
} else {
    // código alternativo
}
```

#### Bucles
```c
for (inicio; condicion; incremento) {
    // código
}

while (condicion) {
    // código
}
```

#### Operador Ternario
```c
resultado = condicion ? valor_si_true : valor_si_false;
```

## 🏗️ Componentes del Proyecto

### 📁 Estructura de Archivos

```
p1-copiler/
│
├── main.py          # Interfaz gráfica principal
├── lexico.py        # Analizador léxico (tokens)
├── sintactico.py    # Analizador sintáctico (gramática)
├── diagram.py       # Generador de diagramas
├── parsetab.py      # Tabla de análisis generada por PLY
├── parser.out       # Información de estados del parser
└── README.md        # Documentación del proyecto
```

### 🔍 `lexico.py`
- Define todos los tokens del lenguaje
- Implementa reglas de reconocimiento léxico
- Maneja palabras reservadas e identificadores
- Procesa literales numéricos y de cadena

### 🌳 `sintactico.py`
- Define la gramática del lenguaje
- Implementa reglas de precedencia de operadores
- Construye árboles sintácticos abstractos
- Maneja estructuras de control y expresiones

### 🎨 `diagram.py`
- Genera diagramas visuales de árboles sintácticos
- Utiliza Graphviz para renderizado
- Crea representaciones jerárquicas claras

### 🖥️ `main.py`
- Interfaz gráfica con Tkinter
- Editor de código con funcionalidades básicas
- Integra análisis léxico y sintáctico
- Muestra resultados y tabla de símbolos

## 📚 Ejemplos de Código

### Ejemplo 1: Declaraciones y Asignaciones
```c
int x;
float y;
string nombre;
x = 10;
y = 3.14;
nombre = "Hola";
```

### Ejemplo 2: Estructuras de Control
```c
int contador;
contador = 0;

if (contador < 10) {
    contador = contador + 1;
}

while (contador > 0) {
    contador--;
}

for (int i = 0; i < 5; i++) {
    // código del bucle
}
```

### Ejemplo 3: Operador Ternario
```c
int a;
int b;
int mayor;
mayor = a > b ? a : b;
```

### Ejemplo 4: Expresiones Complejas
```c
int resultado;
resultado = (a + b) * c && d || e == f;
```

## 🔬 Análisis Implementado

### Análisis Léxico
- ✅ Reconocimiento de tokens
- ✅ Identificación de palabras reservadas
- ✅ Procesamiento de literales
- ✅ Manejo de operadores
- ✅ Detección de errores léxicos

### Análisis Sintáctico
- ✅ Construcción de AST
- ✅ Validación de sintaxis
- ✅ Precedencia de operadores
- ✅ Estructuras de control
- ✅ Expresiones complejas
- ✅ Operador ternario
- ✅ Operadores de decremento

### Características Adicionales
- ✅ Tabla de símbolos
- ✅ Visualización de árboles
- ✅ Interfaz gráfica intuitiva
- ✅ Exportación de diagramas

## 🎯 Casos de Uso

Este compilador es ideal para:

- **Aprendizaje**: Entender conceptos de compiladores
- **Prototipado**: Desarrollo rápido de analizadores
- **Educación**: Enseñanza de análisis léxico/sintáctico
- **Investigación**: Base para extensiones más complejas

## 🐛 Manejo de Errores

### Errores Léxicos
```
Carácter ilegal: @ en la posición 15
```

### Errores Sintácticos
```
Error sintáctico en 'token_problemático'
```

## 🔄 Resolución de Conflictos

El analizador maneja automáticamente:
- Conflictos shift/reduce
- Precedencia de operadores
- Asociatividad de expresiones

## 🚧 Limitaciones Actuales

- No implementa análisis semántico
- No genera código objeto
- Tabla de símbolos básica (sin ámbitos)
- Sin optimizaciones

## 🔮 Extensiones Futuras

- [ ] Análisis semántico completo
- [ ] Generación de código intermedio
- [ ] Manejo de funciones
- [ ] Ámbitos de variables
- [ ] Tipos de datos complejos (arrays, structs)
- [ ] Optimizaciones del compilador

## 🛠️ Desarrollo

### Ejecutar en Modo Desarrollo
```bash
python -u main.py
```

### Limpiar Archivos Generados
```bash
rm -f parser.out parsetab.py
rm -rf __pycache__/
```

### Regenerar Parser
```bash
python sintactico.py
```

## 📊 Estadísticas del Proyecto

- **Tokens soportados**: 25+
- **Reglas gramaticales**: 40+
- **Líneas de código**: ~500
- **Archivos**: 4 principales + generados

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit los cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Autor

**Oscar Chitay**
- GitHub: [@OscarChitay](https://github.com/OscarChitay)
- Email: [tu-email@ejemplo.com]

## 🙏 Agradecimientos

- PLY (Python Lex-Yacc) por las herramientas de análisis
- Graphviz por la visualización de grafos
- Comunidad de Python por las librerías

---

## 📞 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa los [Issues](https://github.com/OscarChitay/p1-copiler/issues) existentes
2. Crea un nuevo Issue si es necesario
3. Proporciona código de ejemplo que reproduzca el problema

---

*Desarrollado como parte del curso de Compiladores - Universidad Mariano Gálvez*
