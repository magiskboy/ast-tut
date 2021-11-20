import typing as T
from queue import LifoQueue
from enum import Enum

class Stack(LifoQueue):
    def top(self):
        el = self.get()
        self.put(el)
        return el


class TokenType(Enum):
    OPEN_BRACKET = 1
    CLOSE_BRACKET = 2
    OPERATOR = 3
    OPERAND = 4


class Token:
    def __init__(self, token_type: TokenType, text: str):
        self.token_type = token_type
        self.text = text

    def __str__(self):
        return f"{self.token_type.name:15} {self.text}"

    def __lt__(self, o: "Token") -> bool:
        return self.text in {"+", "-"} and o.text in {"*", "/"}

    def __gt__(self, o: "Token") -> bool:
        return self.text in {"*", "/"} and o.text in {"+", "-"}

    def __eq__(self, o: "Token") -> bool:
        cond1 = {"+", "-"}
        cond2 = {"*", "/"}
        return (self.text in cond1 and o.text in cond1) or (
            self.text in cond2 and o.text in cond2
        )

    def __repr__(self):
        return f"<Token {self.token_type.name} {self.text}>"


class Node:
    def __init__(
        self,
        token: Token,
        left: T.Optional["Node"] = None,
        right: T.Optional["Node"] = None,
    ):
        self.token = token
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None

    def visit(self, cb: T.Callable[["Node"], None]):
        cb(self)
        if self.left:
            self.left.visit(cb)
        if self.right:
            self.right.visit(cb)

class Parser:
    def __init__(self, expression: str):
        self.expression: str = expression
        self.tokens: T.List[Token] = []
        self.ast: T.Optional[Node] = None

    def tokenize(self):
        words = self.expression.split()
        for word in words:
            token_type: T.Optional[TokenType] = None
            if word == "(":
                token_type = TokenType.OPEN_BRACKET
            elif word == ")":
                token_type = TokenType.CLOSE_BRACKET
            elif word in {"+", "-", "*", "/"}:
                token_type = TokenType.OPERATOR
            elif word.isnumeric():
                token_type = TokenType.OPERAND

            if token_type is None:
                raise ValueError("This expression contains invalid token")
            self.tokens.append(Token(token_type, word))

    def parse(self):
        op_stack: Stack = Stack()
        node_stack: Stack = Stack()
        
        for token in self.tokens:
            if token.token_type == TokenType.OPEN_BRACKET:
                op_stack.put(token)
            elif token.token_type == TokenType.OPERAND:
                node_stack.put(Node(token))
            elif token.token_type == TokenType.OPERATOR:
                while not op_stack.empty() and op_stack.top() > token:
                    op = op_stack.get()
                    right = node_stack.get()
                    left = node_stack.get()
                    node_stack.put(Node(op, left, right))
                op_stack.put(token)
            else:
                while not op_stack.empty() and op_stack.top().token_type != TokenType.OPEN_BRACKET:
                    op = op_stack.get()
                    right = node_stack.get()
                    left = node_stack.get()
                    node_stack.put(Node(op, left, right))
                if op_stack.top().token_type == TokenType.OPEN_BRACKET:
                    op_stack.get()
        self.ast = node_stack.get()