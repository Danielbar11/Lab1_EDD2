from node import Node

class Tree:

    def __init__(self):
        self.root = None

    def search(self, node: Node, average: float, tol: float = 1e-6) -> Node:
        if node is None:
            return None
        
        if abs(node.average - average) <= tol:
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

            parent_suc = sucesor.pad
            child = sucesor.right  # puede ser None
            if parent_suc.left == sucesor:
                parent_suc.left = child
            else:
                parent_suc.right = child
            if child:
                child.pad = parent_suc

            self.update_nodes(parent_suc)
        return True

    def height(self, node: Node) -> int:
        if node is None:
            return 0 
        else:
            return 1 + max(self.height(node.left), self.height(node.right))

    def update_nodes(self, node: Node):
        while node:
            left_tree = self.height(node.left)
            right_tree = self.height(node.right)
            node.bFactor = right_tree - left_tree

            if node.bFactor < -1 or node.bFactor > 1:
                self.balance(node)
        
            node = node.pad

    def balance(self, node: Node):
        if node is None:
            return

        if node.bFactor > 1:
            if node.right and node.right.bFactor < 0:
                self.rotate_right(node.right)
            self.rotate_left(node)
        elif node.bFactor < -1:
            if node.left and node.left.bFactor > 0:
                self.rotate_left(node.left)
            self.rotate_right(node)

    def rotate_left(self, node: Node) -> Node:
        if node is None or node.right is None:
            return node
        aux = node.right
        node.right = aux.left
        if aux.left and aux.left != node:
            aux.left.pad = node

        aux.left = node
        parent = node.pad
        aux.pad = parent
        node.pad = aux

        if parent:
            if parent.left == node:
                parent.left = aux
            else:
                parent.right = aux
        else:
            self.root = aux
        
        node.bFactor = self.height(node.right) - self.height(node.left)
        aux.bFactor = self.height(aux.right) - self.height(aux.left)
        return aux

    def rotate_right(self, node: Node) -> Node:
        if node is None or node.left is None:
            return node
        aux = node.left
        node.left = aux.right
        if aux.right and aux.right != node:
            aux.right.pad = node

        aux.right = node
        parent = node.pad
        aux.pad = parent
        node.pad = aux

        if parent:
            if parent.left == node:
                parent.left = aux
            else:
                parent.right = aux
        else:
            self.root = aux
        
        node.bFactor = self.height(node.right) - self.height(node.left)
        aux.bFactor = self.height(aux.right) - self.height(aux.left)
        return aux
    
    def search_segun_metrica(self, metrica, valor, node = None, results = None):
        if metrica == "iso3":
            return self.search_iso3(valor)
        elif metrica == "nombre":
            return self.search_nombre(valor)
        elif metrica == "promedio":
            try:
                return self.search_promedio(float(valor))
            except ValueError:
                return None
        return None
    
    # Temperatura en un año dado > promedio de todos los paises ese año
    def criterio_a(self, year, df):
        result = []
        if f"F{year}" not in df.columns:
            return result
        year_avg = df[f"F{year}"].mean()

        def inorder(node):
            if not node:
                return
            inorder(node.left)
            row = df[df["ISO3"] == node.iso3]
            if not row.empty and row.iloc[0][f"F{year}"] > year_avg:
                result.append(node)
            inorder(node.right)

        inorder(self.root)
        return result
        

    # Temperatura en un año dado < promedio de todos los años
    def criterio_b(self, year, df):
        result = []
        year_col = f"F{year}"
        if year_col not in df.columns:
            return result
        all_years = [col for col in df.columns if col.startswith("F")]
        global_avg = df[all_years].values.mean()

        def inorder(node):
            if not node:
                return
            inorder(node.left)
            row = df[df["ISO3"] == node.iso3]
            if not row.empty and row.iloc[0][year_col] < global_avg:
                result.append(node)
            inorder(node.right)

        inorder(self.root)
        return result
    
    # promedio >= valor dado
    def criterio_c(self, value):
        result = []
        
        def inorder(node):
            if not node:
                return
            inorder(node.left)
            if node.average >= value:
                result.append(node)
            inorder(node.right)

        inorder(self.root)
        return result
    
    def get_level(self, node:Node) -> int:
        level = 0
        p = node
        while p != self.root:
            if p.pad is None:
                break
            p = p.pad
            level += 1
        return level
    
    def get_node_factor(self, node: Node) -> int: return node.bFactor

    def get_pad(self, node: Node) -> Node: return node.pad
    
    def get_abuelo(self, node: Node) -> Node: return node.pad.pad if node and node.pad else None
    
    def get_tio(self, node: Node) -> Node:
        abuelo = self.get_abuelo(node)
        if abuelo is None:
            return None
        if abuelo.left == node.pad:
            return abuelo.right
        else:
            return abuelo.left
        
    def search_iso3(self, iso3: str, node=None, visited=None) -> Node:
        if visited is None:
            visited = set()
        if node is None:
            node = self.root
        if node is None or id(node) in visited:
            return None
        visited.add(id(node))
    
        if node.iso3 == iso3:
            return node
        left = self.search_iso3(iso3, node.left, visited)
        if left:
            return left
        return self.search_iso3(iso3, node.right, visited)

    def search_nombre(self, nombre: str, node=None, visited=None) -> Node:
        if visited is None:
            visited = set()
        if node is None:
            node = self.root
        if node is None or id(node) in visited:
            return None
        visited.add(id(node))
    
        if node.country == nombre:
            return node
        left = self.search_nombre(nombre, node.left, visited)
        if left:
            return left
        return self.search_nombre(nombre, node.right, visited)
    
    def search_promedio(self, promedio: float) -> Node: return self.search(self.root, promedio)

    def recorrido_por_niveles(self, node: Node):
        if not node:
            return []
        result, q = [], [node]
        while q:
            p = q.pop(0)
            result.append(p.iso3)
            if p.left:
                q.append(p.left)
            if p.right:
                q.append(p.right)
        return result