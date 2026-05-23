"""
RoboLang - Analizador Sintactico Descendente Recursivo (ESQUELETO BASE)
=======================================================================

Tu equipo debe completar las funciones marcadas con TODO para que el parser
reconozca todos los programas validos de RoboLang y rechace los invalidos con
mensajes de error utiles (linea, columna, token esperado).

Ejecutar:
    python robolang_parser.py              # corre el programa de demostracion
    python robolang_parser.py mi_prog.rl   # parsea un archivo
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Union
import sys


# ============================================================
# 1. TIPOS DE TOKENS
# ============================================================

class TipoToken(Enum):
    # Palabras reservadas
    MOVE = auto()
    TURN = auto()
    REPEAT = auto()
    IF = auto()
    THEN = auto()
    WHILE = auto()
    PEN_DOWN = auto()
    PEN_UP = auto()
    FORWARD = auto()
    BACKWARD = auto()
    LEFT = auto()
    RIGHT = auto()
    OBSTACLE = auto()
    LINE = auto()
    LIGHT = auto()
    # Simbolos
    LLAVE_I = auto()   # {
    LLAVE_D = auto()   # }
    PTOCOMA = auto()   # ;
    # Literales
    ENTERO = auto()
    # Especial
    EOF = auto()


PALABRAS_RESERVADAS = {
    "MOVE": TipoToken.MOVE,
    "TURN": TipoToken.TURN,
    "REPEAT": TipoToken.REPEAT,
    "IF": TipoToken.IF,
    "THEN": TipoToken.THEN,
    "WHILE": TipoToken.WHILE,
    "PEN_DOWN": TipoToken.PEN_DOWN,
    "PEN_UP": TipoToken.PEN_UP,
    "FORWARD": TipoToken.FORWARD,
    "BACKWARD": TipoToken.BACKWARD,
    "LEFT": TipoToken.LEFT,
    "RIGHT": TipoToken.RIGHT,
    "OBSTACLE": TipoToken.OBSTACLE,
    "LINE": TipoToken.LINE,
    "LIGHT": TipoToken.LIGHT,
}


@dataclass
class Token:
    tipo: TipoToken
    lexema: str
    linea: int
    columna: int

    def __repr__(self):
        return f"Token({self.tipo.name}, {self.lexema!r}, L{self.linea}:C{self.columna})"


# ============================================================
# 2. ANALIZADOR LEXICO  (ya implementado - NO requiere cambios)
# ============================================================

class ErrorLexico(Exception):
    pass


class Lexer:
    """Tokeniza una cadena de RoboLang."""

    def __init__(self, codigo: str):
        self.codigo = codigo
        self.pos = 0
        self.linea = 1
        self.columna = 1

    def _avanzar(self):
        if self.pos < len(self.codigo):
            if self.codigo[self.pos] == "\n":
                self.linea += 1
                self.columna = 1
            else:
                self.columna += 1
            self.pos += 1

    def _saltar_blancos_y_comentarios(self):
        while self.pos < len(self.codigo):
            c = self.codigo[self.pos]
            if c in " \t\r\n":
                self._avanzar()
            elif c == "#":  # comentarios de linea con #
                while self.pos < len(self.codigo) and self.codigo[self.pos] != "\n":
                    self._avanzar()
            else:
                break

    def tokenizar(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            self._saltar_blancos_y_comentarios()
            if self.pos >= len(self.codigo):
                tokens.append(Token(TipoToken.EOF, "", self.linea, self.columna))
                return tokens

            linea_ini, col_ini = self.linea, self.columna
            c = self.codigo[self.pos]

            # Simbolos de un caracter
            if c == "{":
                tokens.append(Token(TipoToken.LLAVE_I, "{", linea_ini, col_ini))
                self._avanzar(); continue
            if c == "}":
                tokens.append(Token(TipoToken.LLAVE_D, "}", linea_ini, col_ini))
                self._avanzar(); continue
            if c == ";":
                tokens.append(Token(TipoToken.PTOCOMA, ";", linea_ini, col_ini))
                self._avanzar(); continue

            # Enteros
            if c.isdigit():
                inicio = self.pos
                while self.pos < len(self.codigo) and self.codigo[self.pos].isdigit():
                    self._avanzar()
                lexema = self.codigo[inicio:self.pos]
                tokens.append(Token(TipoToken.ENTERO, lexema, linea_ini, col_ini))
                continue

            # Palabras reservadas (RoboLang no admite identificadores libres)
            if c.isalpha() or c == "_":
                inicio = self.pos
                while self.pos < len(self.codigo) and (
                    self.codigo[self.pos].isalnum() or self.codigo[self.pos] == "_"
                ):
                    self._avanzar()
                lexema = self.codigo[inicio:self.pos]
                tipo = PALABRAS_RESERVADAS.get(lexema)
                if tipo is None:
                    raise ErrorLexico(
                        f"[L{linea_ini}:C{col_ini}] Palabra desconocida {lexema!r}. "
                        "RoboLang solo admite palabras reservadas."
                    )
                tokens.append(Token(tipo, lexema, linea_ini, col_ini))
                continue

            raise ErrorLexico(
                f"[L{linea_ini}:C{col_ini}] Caracter ilegal {c!r}"
            )


# ============================================================
# 3. NODOS DEL AST
# ============================================================

@dataclass
class Programa:
    instrucciones: List["Instruccion"]

@dataclass
class Movimiento:
    direccion: str          # "FORWARD" | "BACKWARD"
    distancia: int

@dataclass
class Giro:
    lado: str               # "LEFT" | "RIGHT"
    grados: int

@dataclass
class Repeticion:
    veces: int
    cuerpo: List["Instruccion"]

@dataclass
class Condicional:
    sensor: str
    instruccion: "Instruccion"

@dataclass
class Bucle:
    sensor: str
    cuerpo: List["Instruccion"]

@dataclass
class Pluma:
    accion: str             # "PEN_DOWN" | "PEN_UP"

Instruccion = Union[Movimiento, Giro, Repeticion, Condicional, Bucle, Pluma]


# ============================================================
# 4. ANALIZADOR SINTACTICO DESCENDENTE RECURSIVO
# ============================================================
#
# Gramatica que debe reconocer:
#
#   Programa     ::= ListaInstr EOF
#   ListaInstr   ::= Instruccion ListaInstr | Instruccion
#   Instruccion  ::= Movimiento | Giro | Repeticion
#                  | Condicional | Bucle | Pluma
#   Movimiento   ::= MOVE Direccion ENTERO PTOCOMA
#   Giro         ::= TURN Lado ENTERO PTOCOMA
#   Repeticion   ::= REPEAT ENTERO LLAVE_I ListaInstr LLAVE_D
#   Condicional  ::= IF Sensor THEN Instruccion
#   Bucle        ::= WHILE Sensor LLAVE_I ListaInstr LLAVE_D
#   Pluma        ::= PEN_DOWN PTOCOMA | PEN_UP PTOCOMA
#   Direccion    ::= FORWARD | BACKWARD
#   Lado         ::= LEFT | RIGHT
#   Sensor       ::= OBSTACLE | LINE | LIGHT
#
# ============================================================

class ErrorSintactico(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # -------- utilidades --------

    def _actual(self) -> Token:
        return self.tokens[self.pos]

    def _consumir(self, esperado: TipoToken) -> Token:
        tok = self._actual()
        if tok.tipo != esperado:
            self._error(
                f"Se esperaba {esperado.name} pero se encontro "
                f"{tok.tipo.name} ({tok.lexema!r})", tok)
        self.pos += 1
        return tok

    def _error(self, mensaje: str, tok: Token):
        raise ErrorSintactico(f"[L{tok.linea}:C{tok.columna}] {mensaje}")

    # -------- reglas de produccion --------

    def parsear(self) -> Programa:
        """Programa ::= ListaInstr EOF"""
        instrucciones = self._lista_instr({TipoToken.EOF})
        self._consumir(TipoToken.EOF)
        return Programa(instrucciones)

    def _lista_instr(self, terminadores: set) -> List[Instruccion]:
        """ListaInstr ::= Instruccion+
        Parseamos instrucciones hasta encontrar un token de terminacion
        (EOF para el programa principal, LLAVE_D dentro de un bloque).
        """
        instrucciones = []
        while self._actual().tipo not in terminadores:
            instrucciones.append(self._instruccion())
        if not instrucciones:
            self._error("Se esperaba al menos una instruccion", self._actual())
        return instrucciones

    def _instruccion(self) -> Instruccion:
        """Despacho segun el primer token (FIRST set por alternativa)."""
        tok = self._actual()
        if tok.tipo == TipoToken.MOVE:
            return self._movimiento()
        if tok.tipo == TipoToken.TURN:
            return self._giro()
        # =====================================================
        # TODO 1: agregar el despacho para las demas alternativas
        # de Instruccion: REPEAT, IF, WHILE, PEN_DOWN, PEN_UP.
        # Cada caso debe llamar al metodo correspondiente.
        # =====================================================
        self._error(
            f"Token inesperado {tok.lexema!r} al inicio de una instruccion", tok)

    def _movimiento(self) -> Movimiento:
        """Movimiento ::= MOVE Direccion ENTERO PTOCOMA   (EJEMPLO RESUELTO)"""
        self._consumir(TipoToken.MOVE)
        direccion = self._direccion()
        entero = self._consumir(TipoToken.ENTERO)
        self._consumir(TipoToken.PTOCOMA)
        return Movimiento(direccion=direccion, distancia=int(entero.lexema))

    def _giro(self) -> Giro:
        """Giro ::= TURN Lado ENTERO PTOCOMA"""
        # TODO 2: implementar siguiendo el patron de _movimiento.
        raise NotImplementedError("TODO 2: implementar _giro")

    def _repeticion(self) -> Repeticion:
        """Repeticion ::= REPEAT ENTERO LLAVE_I ListaInstr LLAVE_D"""
        # TODO 3: implementar.
        # Pista: usar self._lista_instr({TipoToken.LLAVE_D}) para el cuerpo.
        raise NotImplementedError("TODO 3: implementar _repeticion")

    def _condicional(self) -> Condicional:
        """Condicional ::= IF Sensor THEN Instruccion"""
        # TODO 4: implementar.
        raise NotImplementedError("TODO 4: implementar _condicional")

    def _bucle(self) -> Bucle:
        """Bucle ::= WHILE Sensor LLAVE_I ListaInstr LLAVE_D"""
        # TODO 5: implementar.
        raise NotImplementedError("TODO 5: implementar _bucle")

    def _pluma(self) -> Pluma:
        """Pluma ::= PEN_DOWN PTOCOMA | PEN_UP PTOCOMA"""
        # TODO 6: implementar.
        raise NotImplementedError("TODO 6: implementar _pluma")

    def _direccion(self) -> str:
        """Direccion ::= FORWARD | BACKWARD   (EJEMPLO RESUELTO)"""
        tok = self._actual()
        if tok.tipo == TipoToken.FORWARD:
            self.pos += 1
            return "FORWARD"
        if tok.tipo == TipoToken.BACKWARD:
            self.pos += 1
            return "BACKWARD"
        self._error(
            f"Se esperaba FORWARD o BACKWARD, se encontro {tok.lexema!r}", tok)

    def _lado(self) -> str:
        """Lado ::= LEFT | RIGHT"""
        # TODO 7: implementar siguiendo el patron de _direccion.
        raise NotImplementedError("TODO 7: implementar _lado")

    def _sensor(self) -> str:
        """Sensor ::= OBSTACLE | LINE | LIGHT"""
        # TODO 8: implementar.
        raise NotImplementedError("TODO 8: implementar _sensor")


# ============================================================
# 5. VISUALIZACION DEL AST
# ============================================================

def imprimir_ast(nodo, indent=0):
    pre = "  " * indent
    if isinstance(nodo, Programa):
        print(f"{pre}Programa")
        for i in nodo.instrucciones:
            imprimir_ast(i, indent + 1)
    elif isinstance(nodo, Movimiento):
        print(f"{pre}Movimiento({nodo.direccion}, {nodo.distancia})")
    elif isinstance(nodo, Giro):
        print(f"{pre}Giro({nodo.lado}, {nodo.grados})")
    elif isinstance(nodo, Repeticion):
        print(f"{pre}Repeticion(veces={nodo.veces})")
        for i in nodo.cuerpo:
            imprimir_ast(i, indent + 1)
    elif isinstance(nodo, Condicional):
        print(f"{pre}Condicional(sensor={nodo.sensor})")
        imprimir_ast(nodo.instruccion, indent + 1)
    elif isinstance(nodo, Bucle):
        print(f"{pre}Bucle(sensor={nodo.sensor})")
        for i in nodo.cuerpo:
            imprimir_ast(i, indent + 1)
    elif isinstance(nodo, Pluma):
        print(f"{pre}Pluma({nodo.accion})")


# ============================================================
# 6. PUNTO DE ENTRADA
# ============================================================

PROGRAMA_DEMO = """
# Dibuja un cuadrado de lado 10
PEN_DOWN;
REPEAT 4 {
    MOVE FORWARD 10;
    TURN RIGHT 90;
}
PEN_UP;
"""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            codigo = f.read()
    else:
        codigo = PROGRAMA_DEMO

    try:
        tokens = Lexer(codigo).tokenizar()
        print("=== TOKENS ===")
        for t in tokens:
            print(t)
        print()

        ast = Parser(tokens).parsear()
        print("=== AST ===")
        imprimir_ast(ast)
    except (ErrorLexico, ErrorSintactico) as e:
        print(f"FALLO: {e}", file=sys.stderr)
        sys.exit(1)
