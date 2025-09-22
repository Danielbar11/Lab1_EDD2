import graphviz
from PIL import Image, ImageTk
import io

class TreeVisualizer:
    def __init__(self, tree):
        self.tree = tree
    
    def add_nodes(self, node, dot):
        if node is not None:
            label = f"{node.iso3}\n{node.average:.3f}"
            dot.node(str(id(node)), label)

        if node.left:
            dot.edge(str(id(node)), str(id(node.left)))
            self.add_nodes(node.left, dot)
        if node.right:
            dot.edge(str(id(node)), str(id(node.right)))
            self.add_nodes(node.right, dot)

    def generate_image(self, canvas):
        if self.tree.root is None:
            return None
        dot = graphviz.Digraph(format = "png")
        dot.attr("node", shape = "circle", style = "filled", color = "lightblue2")

        self.add_nodes(self.tree.root, dot)

        bytes = dot.pipe(format = "png")
        img = Image.open(io.BytesIO(bytes))
        return img
