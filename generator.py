from parse import Node

MAP_FUNC = {
    "+": "add",
    "-": "sub",
    "*": "mul",
    "/": "div"
}

def generate_source_code(ast: Node) -> str:
    counter = 0
    lines = []
    def travesal(node: Node) -> str:
        nonlocal counter, lines

        if node.is_leaf():
            return node.token.text

        left = travesal(node.left)
        right = travesal(node.right)
        lines.append(f"mov ${counter} {left}")
        lines.append(f"{MAP_FUNC.get(node.token.text)} ${counter} {right}")

        counter += 1
        return f"${counter-1}"

    travesal(ast)
    lines.append(f"ret ${counter-1}")

    return "\n".join(lines)
