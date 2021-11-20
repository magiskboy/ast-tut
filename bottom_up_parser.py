import sys
import typing as T
from queue import LifoQueue
from lib import tokenize, generate_source_code, view, Token, TokenType, Node


def parse(tokens: T.List[Token]) -> Node:
    op_stack: LifoQueue[Token] = LifoQueue()
    node_stack: LifoQueue[Node] = LifoQueue()

    for token in tokens:
        if token.token_type == TokenType.OPEN_BRACKET:
            op_stack.put(token)
        elif token.token_type == TokenType.OPERAND:
            node_stack.put(Node(token))
        elif token.token_type == TokenType.OPERATOR:
            top = op_stack.get()
            while top and top > token:
                right = node_stack.get()
                left = node_stack.get()
                node_stack.put(Node(top, left, right))
                top = op_stack.get()
            else:
                op_stack.put(top)
            op_stack.put(token)
        else:
            if op_stack.empty():
                raise ValueError("redundant close bracket")
            top = op_stack.get()
            while top and top.token_type != TokenType.OPEN_BRACKET:
                right = node_stack.get()
                if node_stack.empty():
                    raise ValueError("right operand is missing")
                left = node_stack.get()
                node_stack.put(Node(top, left, right))
                top = op_stack.get()

    if node_stack.qsize() > 1:
        raise ValueError()
    return node_stack.get()


if __name__ == "__main__":
    expression = sys.argv[1]
    viz = sys.argv[2]

    try:
        tokens = tokenize(f"({expression})")
        ast = parse(tokens)

        if viz == "yes":
            view(ast)

        code = generate_source_code(ast)
        print(code)
    except ValueError as e:
        print("Invalid:", e)
