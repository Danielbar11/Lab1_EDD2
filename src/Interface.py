import customtkinter as ctk
from treeVisualizer import TreeVisualizer
from PIL import Image, ImageTk
import tree
from treeVisualizer import TreeVisualizer

class Interface(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Promedio cambio de temperatura por países")
        self.geometry("1000x600")
        self.tree_visualizer = TreeVisualizer(tree)
        self.canvas = ctk.CTkCanvas(self, width=700, height=500, bg="white")
        self.canvas.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.sidebar = ctk.CTkFrame(self, width=250)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        self.insert_button = ctk.CTkButton(self.sidebar, text="Insertar nodo", command=self.insert_node)
        self.insert_button.pack(pady=10)
        self.delete_button = ctk.CTkButton(self.sidebar, text="Eliminar nodo", command=self.delete_node)
        self.delete_button.pack(pady=10)
        self.search_button = ctk.CTkButton(self.sidebar, text="Buscar nodo", command=self.search_node)
        self.search_button.pack(pady=10)
        self.tree_image = None
        self.display_tree()

    def display_tree(self):
        img = self.tree_visualizer.generate_image()
        self.tree_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tree_image)
