# Compilador 
# Alumno
# RIVERA BUENROSTRO ARAM ELIAS 
# Materia: COMPILADORES
# Profesor: Dr. Luis Efrén Veloz Ortiz
#Primera entrega: 25/04/2023
# Fecha de entregra final: 16/06/2023

import re  # Biblioteca principal

# Definición de los tokens
tokens = [
    ('ENTERO', r'\d+'),
    ('SUMA', r'\+'),
    ('RESTA', r'\-'),
    ('MULTIPLICACION', r'\*'),
    ('DIVISION', r'\/'),
    ('PARENTESIS_IZQUIERDO', r'\('),
    ('PARENTESIS_DERECHO', r'\)'),
    ('VARIABLE', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('ASIGNACION', r'\='),
    ('FIN_SENTENCIA', r'\;'),
    ('ESPACIO', r'\s+'),
    ('COMENTARIO', r'\/\/.*'),
]

# Definimos nuestra tabla de símbolos
tabla_simbolos = {}

# Definimos una clase para representar el árbol sintáctico abstracto (AST)
class Nodo:
    def __init__(self, tipo, valor=None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = []

    def agregar_hijo(self, nodo):
        self.hijos.append(nodo)

# Función de análisis léxico
def lexico(programa):
    # Expresión regular para ignorar los tokens no reconocidos
    ignore = r'.'

    # Concatenar todas las expresiones regulares de los tokens
    tokens_compilados = '|'.join('(?P<%s>%s)' % par for par in tokens)

    # Posición de inicio del análisis
    inicio = 0

    # Recorre el programa y busca los tokens
    for coincidencia in re.finditer(tokens_compilados + '|' + ignore, programa):
        # Obtener el tipo y la cadena del token encontrado
        tipo = coincidencia.lastgroup
        cadena = coincidencia.group()

        # Si es un espacio o comentario, ignorarlo
        if tipo in ['ESPACIO', 'COMENTARIO']:
            continue

        # Si es un token no reconocido, lanzar un error
        if tipo == None:
            raise ValueError('Carácter no reconocido: %s' % cadena)

        # Si es una variable, convertirla a mayúsculas
        if tipo == 'VARIABLE':
            variable = cadena.upper()
            if variable not in tabla_simbolos:
                tabla_simbolos[variable] = 0
                
        # Actualizamos la posición de inicio del análisis
        inicio = coincidencia.end()

        # Devolvemos el tipo y la cadena del token encontrado
        yield tipo, cadena

    # Si no se ha llegado al final del programa, lanzar un error
    if inicio != len(programa):
        raise ValueError('No se pudo analizar completamente el programa')

# Definimos la función de análisis sintáctico
def parsear_factor(tokens, pos):
    # Obtenemos el tipo y la cadena del token en la posición actual
    tipo_actual, cadena_actual = tokens[pos]

    # Si es un número o una variable, crear un nodo numérico o de variable
    if tipo_actual == 'ENTERO':
        return Nodo('ENTERO', int(cadena_actual)), pos + 1
    elif tipo_actual == 'VARIABLE':
        return Nodo('VARIABLE', cadena_actual), pos + 1
    elif tipo_actual == 'PARENTESIS_IZQUIERDO':
        # Si es un paréntesis izquierdo, analizar la expresión
        resultado, pos = parsear_expresion(tokens, pos + 1)

        # Verificar que haya un paréntesis derecho después de la expresión
        tipo_siguiente, cadena_siguiente = tokens[pos]

        if tipo_siguiente != 'PARENTESIS_DERECHO':
            raise ValueError('Se esperaba un paréntesis derecho')

        return resultado, pos + 1
    else:
        raise ValueError('Se esperaba un número, una variable o un paréntesis')

def parsear_termino(tokens, pos):
    factor_izq, pos = parsear_factor(tokens, pos)

    while pos < len(tokens) and tokens[pos][0] in {'MULTIPLICACION', 'DIVISION'}:
        op = tokens[pos][0]
        pos += 1

        factor_der, pos = parsear_factor(tokens, pos)

        if op == 'MULTIPLICACION':
            nuevo_nodo = Nodo('MULTIPLICACION')
        else:
            nuevo_nodo = Nodo('DIVISION')

        nuevo_nodo.agregar_hijo(factor_izq)
        nuevo_nodo.agregar_hijo(factor_der)
        
        factor_izq = nuevo_nodo

    return factor_izq, pos


def parsear_expresion(tokens, pos):
    termino_izq, pos = parsear_termino(tokens, pos)

    while pos < len(tokens) and tokens[pos][0] in {'SUMA', 'RESTA'}:
        op = tokens[pos][0]
        pos += 1

        termino_der, pos = parsear_termino(tokens, pos)

        if op == 'SUMA':
            nuevo_nodo = Nodo('SUMA')
        else:
            nuevo_nodo = Nodo('RESTA')

        nuevo_nodo.agregar_hijo(termino_izq)
        nuevo_nodo.agregar_hijo(termino_der)

        termino_izq = nuevo_nodo

    return termino_izq, pos


def analizar(programa):
    tokens = list(lexico(programa))
    arbol_sintactico, _ = parsear_expresion(tokens, 0)
    return arbol_sintactico

def analizar_semanticamente(nodo):
    if nodo.tipo == 'VARIABLE':
        variable = nodo.valor
        if variable not in tabla_simbolos:
            raise ValueError('Variable no declarada: %s' % variable)
    for hijo in nodo.hijos:
        analizar_semanticamente(hijo)

def generar_codigo_intermedio(nodo):
    codigo_intermedio = ''
    if nodo.tipo == 'ASIGNACION':
        variable = nodo.hijos[0].valor
        expresion = nodo.hijos[1]

        codigo_intermedio = generar_codigo_intermedio(expresion)
        codigo_intermedio += f'STORE {variable}\n'

    elif nodo.tipo in {'SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION'}:
        codigo_intermedio = ''
        for hijo in nodo.hijos:
            codigo_intermedio += generar_codigo_intermedio(hijo)

        if nodo.tipo == 'SUMA':
            codigo_intermedio += 'ADD\n'
        elif nodo.tipo == 'RESTA':
            codigo_intermedio += 'SUB\n'
        elif nodo.tipo == 'MULTIPLICACION':
            codigo_intermedio += 'MUL\n'
        elif nodo.tipo == 'DIVISION':
            codigo_intermedio += 'DIV\n'

    elif nodo.tipo == 'ENTERO':
        valor = nodo.valor
        codigo_intermedio = f'PUSH {valor}\n'

    return codigo_intermedio

def optimizar_codigo(codigo):
    # Realizar optimizaciones aquí (opcional)
    return codigo

def generar_codigo_objeto(codigo_intermedio):
    lineas_codigo = codigo_intermedio.strip().split('\n')
    codigo_objeto = 'Código objeto:\n'
    
    for linea in lineas_codigo:
        codigo_objeto += linea + '\n'

    return "Código objeto:\n" + codigo_intermedio

def imprimir_tabla_simbolos():
    print("Tabla de símbolos:")
    for variable, valor in tabla_simbolos.items():
        print(f"{variable}: {valor}")
    print()


# Obtener la oración desde el usuario
oracion = input("Titulo de lo que desea hacer: ")

# Imprimir la oración ingresada
print("\n",oracion)

# Agregar la variable 'a' a la tabla de símbolos con valor inicial 0
tabla_simbolos['A'] = 0

# Obtener la operación desde el usuario
operacion = input("Ingrese la operación matemática: ")

# Analizar y evaluar la operación
arbol_sintactico = analizar(operacion)
analizar_semanticamente(arbol_sintactico)
codigo_intermedio = generar_codigo_intermedio(arbol_sintactico)
codigo_optimizado = optimizar_codigo(codigo_intermedio)
codigo_objeto = generar_codigo_objeto(codigo_optimizado)

def evaluar_expresion(codigo_intermedio):
    pila = []
    lineas_codigo = codigo_intermedio.strip().split('\n')

    for linea in lineas_codigo:
        if linea.startswith('PUSH'):
            _, valor = linea.split(' ')
            pila.append(int(valor))
        elif linea == 'ADD':
            b = pila.pop()
            a = pila.pop()
            pila.append(a + b)
        elif linea == 'SUB':
            b = pila.pop()
            a = pila.pop()
            pila.append(a - b)
        elif linea == 'MUL':
            b = pila.pop()
            a = pila.pop()
            pila.append(a * b)
        elif linea == 'DIV':
            b = pila.pop()
            a = pila.pop()
            pila.append(a / b)

    return pila[0] if pila else None

resultado = evaluar_expresion(codigo_optimizado)

print("Resultado:", resultado)
print("Código intermedio:")
print(codigo_intermedio)