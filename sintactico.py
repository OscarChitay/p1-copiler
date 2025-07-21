import ply.yacc as yacc
from lexico import tokens

# Precedencia de operadores actualizada
precedence = (
    ('left', 'LOR'),          # Operador OR lógico
    ('left', 'LAND'),         # Operador AND lógico
    ('left', 'LT', 'GT', 'LE', 'GE'),     # Comparaciones
    ('left', 'PLUS', 'MINUS'),
    ('left', 'EQ'),
    ('left', 'NE'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'TERNARY'),  # Operador ternario
    ('right', 'DECREMENT'), # Operador de decremento
    ('right', 'INCREMENT'),
    ('right', 'LNOT')
)

# Reglas de gramática
def p_program(p):
    '''program : statements'''
    p[0] = ('program', p[1])

def p_statements(p):
    '''statements : statements statement
                  | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_statement_increment(p):
    'statement : ID INCREMENT SEMICOLON'
    p[0] = ('increment_stmt', p[1])

def p_statement_declaration(p):
    '''statement : INT ID SEMICOLON
                 | FLOAT ID SEMICOLON
                 | STRING ID SEMICOLON
                 | BOOL ID SEMICOLON
                 | INT ID EQUALS expression SEMICOLON
                 | FLOAT ID EQUALS expression SEMICOLON
                 | STRING ID EQUALS STRING_LITERAL SEMICOLON
                 | BOOL ID EQUALS TRUE SEMICOLON
                 | BOOL ID EQUALS FALSE SEMICOLON'''
    if len(p) == 4:  # Solo declaración
        p[0] = ('declaracion, =', p[1], p[2])
    else:  # Declaración con asignación
        p[0] = ('declaracion_asignacion, =', p[1], p[2], p[4])

def p_statement_assignment(p):
    '''statement : ID EQUALS expression SEMICOLON
                 | ID EQUALS STRING_LITERAL SEMICOLON
                 | ID EQUALS TRUE SEMICOLON
                 | ID EQUALS FALSE SEMICOLON'''
    p[0] = ('assignment, =', p[1], p[3])

def p_statement_for(p):
    '''statement : FOR LPAREN INT ID EQUALS NUMBER SEMICOLON expression SEMICOLON expression RPAREN statement
                | FOR LPAREN ID EQUALS NUMBER SEMICOLON expression SEMICOLON expression RPAREN statement'''
    if len(p) == 13:  # Con declaración de variable (int i = 0;)
        p[0] = ('for', ('declaration', p[3], p[4], p[6]), p[8], p[10], p[12])
    else:  # Sin declaración de variable (i = 0;)
        p[0] = ('for', ('assignment', p[3], p[5]), p[7], p[9], p[11])

# También necesitamos asegurarnos que expression pueda manejar incrementos
def p_expression_increment(p):
    '''expression : ID PLUS PLUS
                 | ID PLUS EQUALS NUMBER
                 | ID EQUALS ID PLUS NUMBER'''
    if len(p) == 4:  # i++
        p[0] = ('increment', p[1])
    elif len(p) == 5:  # i += 1
        p[0] = ('increment_by', p[1], p[4])
    else:  # i = i + 1
        p[0] = ('increment_assign', p[1], p[3], p[5])

def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN statement'
    p[0] = ('while', p[3], p[5])

def p_statement_block(p):
    'statement : LBRACE statements RBRACE'
    p[0] = ('block', p[2])

def p_statement_if(p):
    '''statement : IF LPAREN expression RPAREN statement
                 | IF LPAREN expression RPAREN statement ELSE statement'''  
    if len(p) == 6:
        p[0] = ('if', p[3], p[5])
    else:
        p[0] = ('if-else', p[3], p[5], p[7])

def p_statement_expression(p):
    'statement : expression SEMICOLON'
    p[0] = ('expr', p[1])

def p_expression_binop(p):
    '''expression : expression PLUS term
                  | expression PLUS expression
                  | expression MINUS expression
                  | expression MINUS term
                  | expression LOR term
                  | expression LAND term
                  | expression EQ term
                  | expression NE term'''
    p[0] = ('operation', p[2], p[1], p[3])

def p_expression_comparison(p):
    '''expression : expression LT expression
                  | expression GT expression
                  | expression LE expression
                  | expression GE expression'''
    p[0] = ('comparison', p[2], p[1], p[3])

def p_expression_term(p):
    'expression : term'
    p[0] = p[1]

def p_term_binop(p):
    '''term : term TIMES factor
            | term DIVIDE factor'''
    p[0] = ('operation', p[2], p[1], p[3])

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]

def p_factor_num(p):
    '''factor : NUMBER
              | FLOAT'''
    p[0] = ('number', p[1])

def p_factor_string(p):
    'factor : STRING_LITERAL'
    p[0] = ('string', p[1])

def p_factor_id(p):
    'factor : ID'
    p[0] = ('id', p[1])

def p_factor_true_false(p):
    '''factor : TRUE
              | FALSE'''
    # p.slice[1].type, trae la palabra true o false
    if p.slice[1].type == 'TRUE':
        p[0] = ('bool_true', True)
    else:
        p[0] = ('bool_false', False)

def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_equals(p):
    'expression : ID EQUALS expression'
    p[0] = ('assignment', p[1], p[3])

def p_expression_list(p):
    'expression : LBRACKET elements RBRACKET'
    p[0] = ('list', p[2])

def p_elements_multiple(p):
    'elements : elements COMMA expression'
    p[0] = p[1] + [p[3]]

def p_elements_single(p):
    'elements : expression'
    p[0] = [p[1]]

def p_elements_empty(p):
    'elements : '
    p[0] = []

def p_error(p):
    print("Error sintáctico en '%s'" % p.value if p else "Error en entrada")

def p_expression_logical_not(p):
    'expression : LNOT expression'
    p[0] = ('not', p[2])

def p_expression_increment(p):
    'expression : ID INCREMENT'
    p[0] = ('increment', p[1], '++')

def p_statement_increment(p):
    'statement : ID INCREMENT SEMICOLON'
    p[0] = ('decrement_stmt', p[1])


def p_expression_decrement(p):
    'expression : ID DECREMENT'
    p[0] = ('decrement', p[1], '--')  # Agregamos el símbolo para mayor claridad

def p_statement_decrement(p):
    'statement : ID DECREMENT SEMICOLON'
    p[0] = ('decrement_stmt', p[1])  
  
def p_expression_ternary(p):
    'expression : expression TERNARY expression COLON expression'
    p[0] = ('ternary', p[1], p[3], p[5])

def p_statement_print(p):
    'statement : PRINT LPAREN args RPAREN SEMICOLON'
    p[0] = ('print', p[3])   # Nodo AST: ('print', [expr1, expr2, ...])

def p_args_multiple(p):
    'args : args COMMA expression'
    p[0] = p[1] + [p[3]]

def p_args_single(p):
    'args : expression'
    p[0] = [p[1]]


# Construir el analizador sintáctico
parser = yacc.yacc()
