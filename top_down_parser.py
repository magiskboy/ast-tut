import sys
import typing as T
from lib import tokenize, Token, TokenType

tokens: T.List[Token] = []
token: Token
i: int = 0
need_closed_bracket: int = 0


def expect(token_type: T.Union[TokenType, T.Set[TokenType]]):
    global token, i
    valid_token_types: T.Container[TokenType] = (
        {token_type} if isinstance(token_type, TokenType) else token_type
    )
    if token.token_type in valid_token_types:
        return
    raise ValueError(
        f"expect({i}): expectd {','.join(map(lambda x: x.name, list(valid_token_types)))}, but received {token.token_type.name}"
    )


def is_break() -> bool:
    global token
    return token.token_type in {TokenType.CLOSE_BRACKET, TokenType.NULL}


def next_token():
    global token, i, need_closed_bracket, tokens
    if i < len(tokens):
        token = tokens[i]
        if token.token_type == TokenType.OPEN_BRACKET:
            need_closed_bracket += 1
        elif token.token_type == TokenType.CLOSE_BRACKET:
            need_closed_bracket -= 1
        if need_closed_bracket < 0:
            raise ValueError("need_closed_bracket")
        i += 1
    else:
        token = Token(TokenType.NULL, "")


def operator():
    global token
    expect(TokenType.OPERATOR)
    next_token()
    expect({TokenType.OPERAND, TokenType.OPEN_BRACKET})


def number():
    global token
    expect(TokenType.OPERAND)
    next_token()
    expect({TokenType.OPERATOR, TokenType.CLOSE_BRACKET})


def expression():
    global token

    if token.token_type == TokenType.OPERAND:
        number()

    elif token.token_type == TokenType.OPEN_BRACKET:
        next_token()
        expression()
        expect(TokenType.CLOSE_BRACKET)
        next_token()

    if is_break():
        return

    # case: ...<expression> <operator> <expression>
    operator()
    expression()


if __name__ == "__main__":
    source: str = sys.argv[1]
    tokens = tokenize(f"({source})")

    try:
        next_token()
        expression()
        print("Valid")
    except ValueError as e:
        print("Invalid:", e)
