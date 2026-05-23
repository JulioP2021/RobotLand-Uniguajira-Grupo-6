#  RoboLang Parser en Python

Proyecto desarrollado en Python que implementa un **analizador léxico y sintáctico (Parser Descendente Recursivo)** para un lenguaje de programación simple llamado **RoboLang**, diseñado para controlar movimientos y acciones de un robot.

El proyecto incluye:

- Análisis léxico (Lexer)
- Análisis sintáctico (Parser)
- Construcción de un Árbol de Sintaxis Abstracta (AST)
- Visualización del AST
- Manejo de errores léxicos y sintácticos
- Suite automática de pruebas

---

#  Características

El lenguaje RoboLang permite:

✅ Mover un robot hacia adelante o atrás  
✅ Girar a izquierda o derecha  
✅ Repetir bloques de instrucciones  
✅ Condicionales  
✅ Bucles  
✅ Control de pluma (dibujar/no dibujar)  
✅ Sensores simulados  

---

#  Estructura del proyecto

```bash
RoboLang/
│
├── robolang.py
├── README.md
```

---

#  Requisitos

Python 3.8 o superior

Verificar versión instalada:

```bash
python --version
```

---

#  Ejecutar el proyecto

Ejecutar el programa con el ejemplo incorporado:

```bash
python robolang.py
```

Salida esperada:

```bash
=== TOKENS ===
Token(PEN_DOWN,'PEN_DOWN',L2:C1)
Token(REPEAT,'REPEAT',L3:C1)
...

=== AST ===
Programa
  Pluma(PEN_DOWN)
  Repeticion(veces=4)
    Movimiento(FORWARD,10)
    Giro(RIGHT,90)
  Pluma(PEN_UP)
```

---

#  Ejecutar un archivo RoboLang

Crear un archivo:

```bash
programa.rl
```

Ejemplo:

```robolang
PEN_DOWN;

REPEAT 4 {
    MOVE FORWARD 10;
    TURN RIGHT 90;
}

PEN_UP;
```

Ejecutarlo:

```bash
python robolang.py programa.rl
```

---

#  Ejecutar pruebas automáticas

El proyecto incluye **20 pruebas automatizadas**

- 10 programas válidos
- 10 programas inválidos

Ejecutar:

```bash
python robolang.py --test
```

Ejemplo de salida:

```bash
======================================================================
SUITE DE PRUEBAS — RoboLang Parser
20 pruebas (10 validas + 10 invalidas)
======================================================================

#1 PASS | Cuadrado básico
#2 PASS | MOVE BACKWARD 5;
...
#20 PASS | Programa vacío
```

---

#  Gramática reconocida

```ebnf
Programa     ::= ListaInstr EOF

ListaInstr   ::= Instruccion+

Instruccion  ::= Movimiento
               | Giro
               | Repeticion
               | Condicional
               | Bucle
               | Pluma

Movimiento   ::= MOVE Direccion ENTERO ;

Giro         ::= TURN Lado ENTERO ;

Repeticion   ::= REPEAT ENTERO
                 {
                     ListaInstr
                 }

Condicional  ::= IF Sensor THEN Instruccion

Bucle        ::= WHILE Sensor
                 {
                     ListaInstr
                 }

Pluma        ::= PEN_DOWN ;
               | PEN_UP ;

Direccion    ::= FORWARD
               | BACKWARD

Lado         ::= LEFT
               | RIGHT

Sensor       ::= OBSTACLE
               | LINE
               | LIGHT
```

---

#  Palabras reservadas

| Categoría | Palabras |
|------------|-----------|
| Movimiento | MOVE, FORWARD, BACKWARD |
| Giro | TURN, LEFT, RIGHT |
| Repetición | REPEAT |
| Condicional | IF, THEN |
| Bucle | WHILE |
| Sensores | OBSTACLE, LINE, LIGHT |
| Pluma | PEN_DOWN, PEN_UP |

---

# Ejemplo del AST generado

Código:

```robolang
PEN_DOWN;

REPEAT 4{
    MOVE FORWARD 10;
    TURN RIGHT 90;
}

PEN_UP;
```

Árbol generado:

```bash
Programa
 ├── Pluma(PEN_DOWN)
 ├── Repeticion(4)
 │     ├── Movimiento(FORWARD,10)
 │     └── Giro(RIGHT,90)
 └── Pluma(PEN_UP)
```

---

# Manejo de errores

El sistema detecta errores como:

### Error léxico

```robolang
JUMP FORWARD 10;
```

Salida:

```bash
ErrorLexico:
Palabra desconocida 'JUMP'
```

### Error sintáctico

```robolang
MOVE FORWARD 10
```

Salida:

```bash
ErrorSintactico:
Se esperaba PTOCOMA
```

---

#  Arquitectura

El flujo interno del programa sigue el siguiente proceso:

```text
Código RoboLang
       ↓
Lexer (Tokenización)
       ↓
Lista de Tokens
       ↓
Parser Descendente Recursivo
       ↓
AST
       ↓
Visualización
```

---

#  Tecnologías utilizadas

- Python
- Dataclasses
- Enum
- Tipado estático (typing)

---

#  Autor

Desarrollado como proyecto académico para implementar conceptos de:

- Compiladores
- Análisis Léxico
- Análisis Sintáctico
- Árboles AST
- Gramáticas formales

---

#  Licencia

Este proyecto puede utilizarse con fines educativos y académicos.
