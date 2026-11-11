# Educational Compiler Pipeline

A collaborative desktop application that demonstrates the main stages of a compiler for a simplified programming language. The project combines lexical, syntactic, and semantic analysis with intermediate-code generation, optimization, NASM output, and a Tkinter interface.

> This repository is a fork of the original team project maintained by [MonjeBmo](https://github.com/MonjeBmo/p1-copiler). See [Credits and contributions](#credits-and-contributions) for attribution.

## Features

- Tokenization and reserved-word recognition with PLY
- Grammar validation and abstract syntax tree generation
- Semantic checks and symbol table management
- Graphviz-based syntax tree visualization
- Intermediate-code generation and optimization
- NASM assembly output
- Windows executable compilation workflow
- Desktop interface for editing code and inspecting each compiler stage

## Technology

- Python
- [PLY](https://www.dabeaz.com/ply/) for lexical and syntactic analysis
- Tkinter for the desktop interface
- [Graphviz](https://graphviz.org/) for syntax tree visualization
- Pillow for image handling
- NASM and GCC for the optional executable-generation workflow

## Project structure

```text
.
├── main.py              # Desktop interface and workflow orchestration
├── lexico.py            # Lexer and token definitions
├── sintactico.py        # Grammar and parser
├── semantico.py         # Semantic analysis and symbol handling
├── diagram.py           # AST visualization
├── generador_codigo.py  # Intermediate-code generation
├── optimizador.py       # Intermediate-code optimization
└── generador_nasm.py    # NASM output generation
```

## Requirements

- Python 3
- Tkinter, normally included with Python on Windows
- Graphviz installed and available on `PATH`
- NASM and GCC only if you want to generate and run a Windows executable

Install the Python dependencies:

```bash
python -m pip install ply graphviz pillow
```

Graphviz also requires its system application. Download it from [graphviz.org/download](https://graphviz.org/download/) or install it with your operating system's package manager.

## Run locally

```bash
git clone https://github.com/OscarChitay/p1-copiler.git
cd p1-copiler
python main.py
```

Use the interface to enter source code and inspect the output from the lexical, syntactic, semantic, generation, and optimization stages.

## Supported language concepts

The educational language includes:

- Integer, floating-point, string, and boolean values
- Variable declarations and assignments
- Arithmetic, logical, and comparison operators
- `if`/`else`, `for`, and `while` control structures
- Increment, decrement, and ternary expressions
- A `print` instruction

Example:

```c
int counter;
counter = 0;

while (counter < 5) {
    print(counter);
    counter++;
}
```

## Scope and limitations

This is an academic compiler project rather than a production compiler. Its grammar, semantic model, optimizer, and machine-code workflow intentionally support a limited teaching language. The executable-generation path also depends on a Windows toolchain with NASM and GCC configured locally.

## Credits and contributions

This application was developed as a team project for a compilers course at Universidad Mariano Gálvez de Guatemala. The complete project history and contributor list are preserved in the original repository and this fork.

Oscar Chitay's recorded contributions include:

- Decrement operator support
- Ternary operator and colon handling
- Project documentation

Original project: [MonjeBmo/p1-copiler](https://github.com/MonjeBmo/p1-copiler)

This fork: [OscarChitay/p1-copiler](https://github.com/OscarChitay/p1-copiler)
