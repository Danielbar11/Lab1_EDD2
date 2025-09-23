from node import Node

class Tree:

    def __init__(self):
        self.root = None

    def search(self, node: Node, average: float) -> Node:
        if node is None:
            return None
        
        if node.average == average:
            return node
        elif average < node.average:
            return self.search(node.left, average)
        else:
            return self.search(node.right, average)

    def insert(self, iso3, average: float, country) -> bool:
        node = Node(iso3, average, country)
        if self.root is None:
            self.root = node
            self.update_nodes(node)
        else:
            if self.search(self.root, node.average) is not None:
                return False
            else:
                self.insert_node(self.root, node)
        
        return True

    def insert_node(self, actual: Node, nuevo: Node):
        if nuevo.average < actual.average:
            if actual.left is None:
                actual.left = nuevo
                nuevo.pad = actual
            else:
                self.insert_node(actual.left, nuevo)
        else:
            if actual.right is None:
                actual.right = nuevo
                nuevo.pad = actual
            else:
                self.insert_node(actual.right, nuevo)
        
        self.update_nodes(actual)

    def delete(self, value: float) -> bool:
        node = self.search(self.root, value)
        if node is None:
            return False
        
        if node.left is None and node.right is None:
            pad = node.pad
            if pad:
                if pad.left == node:
                    pad.left = None
                else:
                    pad.right = None
                self.update_nodes(pad)
            else:
                self.root = None
        elif node.left is None or node.right is None:
            son = node.left if node.left else node.right
            pad = node.pad
            son.pad = pad
            if pad:
                if pad.left == node:
                    pad.left = son
                else:
                    pad.right = son
                self.update_nodes(pad)
            else:
                self.root = son
                self.update_nodes(son)
        else:
            sucesor = node.right
            while sucesor.left:
                sucesor = sucesor.left
            node.iso3 = sucesor.iso3
            node.average = sucesor.average
            node.country = sucesor.country
            self.delete(sucesor.average)
        return True

    def height(self, node: Node) -> int:
        if node is None:
            return 0 
        else:
            return 1 + max(self.height(node.left), self.height(node.right))

    def update_nodes(self, node: Node):
        if node is None:
            return
        
        left_tree = self.height(node.left)
        right_tree = self.height(node.right)
        node.bFactor = right_tree - left_tree

        if node.bFactor < -1 or node.bFactor > 1:
            self.balance(node)
        
        self.update_nodes(node.pad)

    def balance(self, node: Node):
        if node.bFactor > 1:
            if node.right and node.right.bFactor < 0:
                self.rotate_right(node.right)
            self.rotate_left(node)
        elif node.bFactor < -1:
            if node.left and node.left.bFactor > 0:
                self.rotate_left(node.left)
            self.rotate_right(node)

    def rotate_left(self, node: Node) -> Node:
        aux = node.right
        node.right = aux.left
        if aux.left:
            aux.left.pad = node
        aux.left = node
        aux.pad = node.pad
        node.pad = aux
        node.bFactor = self.height(node.right) - self.height(node.left)
        aux.bFactor = self.height(aux.right) - self.height(aux.left)
        return aux
            
    def rotate_right(self, node: Node):
        aux = node.left
        node.left = aux.right
        if aux.right:
            aux.right.pad = node
        aux.right = node
        aux.pad = node.pad
        node.pad = aux
        node.bFactor = self.height(node.right) - self.height(node.left)
        aux.bFactor = self.height(aux.right) - self.height(aux.left)
        return aux
    
    def search_segun(self, funcion, node = None, results = None):
        if results is None:
            results = []
        if node is None:
            node = self.root
        if node is None:
            return results
        
        if funcion(node):
            results.append(node)

        if node.left:
            self.search_segun(funcion, node.left, results)
        if node.right:
            self.search_segun(funcion, node.right, results)
        
        return results
    
    # Temperatura en un año dado > promedio de todos los paises ese año
    @staticmethod
    def criterio_a(node, year, df) -> bool:
        year_ubi = f"F{year}"
        year_prom = df[year_ubi].mean()
        return node.data[year_ubi] > year_prom

    # Temperatura en un año dado < promedio de todos los años
    @staticmethod
    def criterio_b(node, year, df) -> bool:
        prom = df[[f"F{y}" for y in range(1961,2023)]].mean().mean()
        year_ubi = f"F{year}"
        return node.data[year_ubi] < prom
    
    # Temperatura media >= que un valor dado
    @staticmethod
    def criterio_c(node, value) -> bool:
        return node.average >= value
    
    # niveld el nodo
    def get_level(self, node:Node) -> int:
        level = 0
        p = node
        while p != self.root:
            if p.pad is None:
                break
            p = p.pad
            level += 1
        return level
    
    def get_node_factor(self, node: Node) -> int:
        return node.bFactor

    def get_pad(self, node: Node) -> Node:
        return node.pad
    
    def get_abuelo(self, node: Node) -> Node:
        if node.pad:
            return node.pad.pad
        return None
    
    def get_tio(self, node: Node) -> Node:
        abuelo = self.get_abuelo(node)
        if abuelo is None:
            return None
        if abuelo.left == node.pad:
            return abuelo.right
        else:
            return abuelo.left
        
    def search_iso3(self, iso3: str, node=None) -> Node:
        if node is None:
            node = self.root
        if node is None:
            return None
        if node.iso3 == iso3:
            return node
        left = self.search_iso3(iso3, node.left)
        if left:
            return left
        return self.search_iso3(iso3, node.right)

    def search_nombre(self, nombre: str, node=None) -> Node:
        if node is None:
            node = self.root
        if node is None:
            return None
        if node.country == nombre:
            return node
        left = self.search_nombre(nombre, node.left)
        if left:
            return left
        return self.search_nombre(nombre, node.right)

    def search_promedio(self, promedio: float) -> Node:
        return self.search(self.root, promedio)