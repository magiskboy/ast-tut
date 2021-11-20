import typing as T
from enum import Enum
from graphviz import Digraph


ADD_OP = "+"
SUB_OP = "-"
MUL_OP = "*"
DIV_OP = "/"
OPEN_BRACKET = "("
CLOSE_BRACKET = ")"
WHITESPACE = " "

MAP_OP = {ADD_OP: "add", SUB_OP: "sub", MUL_OP: "mul", DIV_OP: "div"}

OPERATORS = {ADD_OP, SUB_OP, MUL_OP, DIV_OP}
BRACKETS = {OPEN_BRACKET, CLOSE_BRACKET}


class TokenType(Enum):
    NULL = 0
    OPEN_BRACKET = 1
    CLOSE_BRACKET = 2
    OPERATOR = 3
    OPERAND = 4


class Token:
    LOWER_OPS = {ADD_OP, SUB_OP}
    HIGHER_OPS = {MUL_OP, DIV_OP}

    def __init__(self, token_type: TokenType, text: str):
        self.token_type = token_type
        self.text = text

    def __str__(self) -> str:
        return f"{self.token_type.name:15} {self.text}"

    def __gt__(self, o: "Token") -> bool:
        return self.text in self.HIGHER_OPS and o.text in self.LOWER_OPS

    def __repr__(self) -> str:
        return f"<Token {self.token_type.name} {self.text}>"


class Node:
    def __init__(
        self,
        token: Token,
        left: "Node" = None,
        right: "Node" = None,
    ):
        self.token = token
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    def visit(self, cb: T.Callable[["Node"], None]):
        cb(self)
        if self.left:
            self.left.visit(cb)
        if self.right:
            self.right.visit(cb)


def _get_token(word: str) -> Token:
    token_type: T.Optional[TokenType] = None
    if word == OPEN_BRACKET:
        token_type = TokenType.OPEN_BRACKET
    elif word == CLOSE_BRACKET:
        token_type = TokenType.CLOSE_BRACKET
    elif word in OPERATORS:
        token_type = TokenType.OPERATOR
    elif word.isnumeric():
        token_type = TokenType.OPERAND

    if token_type is None:
        raise ValueError(f"`{word}` is invalid")
    return Token(token_type, word)


def tokenize(expression: str) -> T.List[Token]:
    tokens: T.List[Token] = []
    word = ""
    for char in expression:
        if char == WHITESPACE:
            if word:
                tokens.append(_get_token(word))
            word = ""
        elif char in OPERATORS.union(BRACKETS):
            if word:
                tokens.append(_get_token(word))
            tokens.append(_get_token(char))
            word = ""
        else:
            word += char
    if word:
        tokens.append(_get_token(word))
    return tokens


def generate_source_code(ast: Node) -> str:
    counter: int = -1
    lines: T.List[str] = []

    def travesal(node: Node) -> str:
        nonlocal counter, lines

        if node.is_leaf():
            return node.token.text

        left = travesal(node.left)
        right = travesal(node.right)
        counter += 1
        lines.append(f"mov ${counter} {left}")
        lines.append(f"{MAP_OP.get(node.token.text)} ${counter} {right}")

        return f"${counter}"

    travesal(ast)
    lines.append(f"ret ${counter}")

    return "\n".join(lines)


def view(ast: Node):
    g = Digraph("g", node_attr={"shape": "circle", "height": ".1"})

    def render(node: Node):
        name = str(id(node))
        g.node(name, node.token.text)

        if not node.is_leaf():
            g.edge(name, str(id(node.left)), None, {"dir": "back"})
            g.edge(name, str(id(node.right)), None, {"dir": "back"})

    ast.visit(render)
    g.render("ast", format="png", cleanup=True)
