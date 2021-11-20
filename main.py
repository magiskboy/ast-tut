import os
import sys
from graphviz import Digraph
from parse import Parser, Node
from generator import generate_source_code

def view(ast: Node):
    g = Digraph("g", filename="ast.gv", node_attr={"shape": "circle", "height": ".1"})
    def render(node: Node):
        name = str(id(node))
        g.node(name, node.token.text)

        if not node.is_leaf():
            g.edge(name, str(id(node.left)), None, {"dir": "back"})
            g.edge(name, str(id(node.right)), None, {"dir": "back"})

    ast.visit(render)
    g.view()


if __name__ == "__main__":
    expression = sys.argv[1]
    viz = sys.argv[2]

    parser = Parser(f'( {expression} )')
    parser.tokenize()
    parser.parse()
        
    if viz == "yes":
        view(parser.ast)

    code = generate_source_code(parser.ast)
    print(code)