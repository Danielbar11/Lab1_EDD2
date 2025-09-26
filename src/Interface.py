from tkinter import simpledialog
import customtkinter as ctk
from PIL import Image, ImageTk
from tree import Tree,Node
from treeVisualizer import TreeVisualizer
import tkinter.messagebox as mb
import io

class Interface(ctk.CTk):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.title("Promedio cambio de temperatura por países")
        self.geometry("1000x600")
        self.zoom_factor = 1.0
        self.tree = Tree()
        for _, row in df.iterrows():
            self.tree.insert(row["ISO3"], row["average"], row["Country"])
        self.tree_visualizer = TreeVisualizer(self.tree)
        self.canvas = ctk.CTkCanvas(self, width=700, height=500, bg="white")
        self.canvas.pack(side="right", fill="both", expand=True)
        self.scrollbar_y = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.sidebar = ctk.CTkFrame(self, width=250)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        self.insert_button = ctk.CTkButton(self.sidebar, text="Insertar nodo", command=self.insert_node)
        self.insert_button.pack(pady=10)
        self.delete_button = ctk.CTkButton(self.sidebar, text="Eliminar nodo", command=self.delete_node)
        self.delete_button.pack(pady=10)
        self.search_button = ctk.CTkButton(self.sidebar, text="Buscar nodo", command=self.search_node)
        self.search_button.pack(pady=10)
        self.level_button = ctk.CTkButton(self.sidebar, text = "Nivel", command = self.show_level)
        self.level_button.pack(pady = 5)
        self.balance_button = ctk.CTkButton(self.sidebar, text = "Factor de equilibrio", command = self.show_balance_factor)
        self.balance_button.pack(pady = 5)
        self.padre_button = ctk.CTkButton(self.sidebar, text = "Padre", command = self.show_padre)
        self.padre_button.pack(pady = 5)
        self.abuelo_button = ctk.CTkButton(self.sidebar, text = "Abuelo", command = self.show_abuelo)
        self.abuelo_button.pack(pady = 5)
        self.tio_button = ctk.CTkButton(self.sidebar, text = "Tío", command = self.show_tio)
        self.tio_button.pack(pady = 5)
        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Buscar valor...")
        self.search_entry.pack(pady=5)
        self.search_criteria = ctk.CTkComboBox(self.sidebar, values=["iso3", "nombre", "promedio"], state="readonly")
        self.search_criteria.set("iso3")
        self.search_criteria.pack(pady=5)
        self.node_combobox = ctk.CTkComboBox(self.sidebar, values=[])
        self.node_combobox.pack(pady=5)
        self.criteria_cb = ctk.CTkComboBox(self.sidebar, values = [])
        self.criteria_cb.pack(pady = 5)
        self.info_label = ctk.CTkLabel(self.sidebar, text = "")
        self.info_label.pack(pady = 5)
        self.tree_image = None
        self.display_tree()
        self.canvas.bind("<MouseWheel>", self.zoom_tree)
        

    def zoom_tree(self, event):
        if event.delta > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1
        self.zoom_factor = max(0.1, min(5, self.zoom_factor))

        img = self.tree_visualizer.generate_image()
        if img:
            width = int(img.width * self.zoom_factor)
            height = int(img.height * self.zoom_factor)
            img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
            self.tree_image = ImageTk.PhotoImage(img_resized)

            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.tree_image)

            self.canvas.config(scrollregion=(0, 0, width, height))

    def display_tree(self):
        img = self.tree_visualizer.generate_image()
        if img:
            width = int(img.width * self.zoom_factor)
            height = int(img.height * self.zoom_factor)
            img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
            self.tree_image = ImageTk.PhotoImage(img_resized)

            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.tree_image)

            self.canvas.config(scrollregion=(0, 0, width, height))

    
    def show_level(self):
        node = self.get_selected_node()
        if node:
            level = self.tree.get_level(node)
            self.info_label.configure(text = f"Nivel: {level}")
    
    def show_balance_factor(self):
        node = self.get_selected_node()
        if node:
            self.info_label.configure(text = f"Factor de equilibrio: {node.bFactor}")

    def show_padre(self):
        node = self.get_selected_node()
        if node and node.pad:
            self.info_label.configure(text = f"Padre: {node.pad.iso3}")
        else:
            self.info_label.configure(text = "Padre: None")
    
    def show_abuelo(self):
        node = self.get_selected_node()
        if node and node.pad and node.pad.pad:
            self.info_label.configure(text = f"Abuelo: {node.pad.pad.iso3}")
        else:
            self.info_label.configure(text = "Abuelo: None")
    
    def show_tio(self):
        node = self.get_selected_node()
        if node and node.pad and node.pad.pad:
            tio = node.pad.pad.left if node.pad.pad.right == node.pad else node.pad.pad.right
            if tio:
                self.info_label.configure(text = f"Tío: {tio.iso3}")
            else:
                self.info_label.configure(text = "Tío: None")

    def get_selected_node(self):
        select = self.node_combobox.get()
        if not select or select == "No encontrado":
            return None

        criterio = self.search_criteria.get()
        if criterio == "iso3":
            return self.tree.search_iso3(select)
        elif criterio == "nombre":
            return self.tree.search_nombre(select)
        elif criterio == "promedio":
            try:
                promedio = float(select)
                return self.tree.search_promedio(promedio)
            except ValueError:
                return None
        return None
    
    def search_node(self):
        self.node_combobox.configure(values = [])
        self.node_combobox.set("")
        criterio = self.search_criteria.get()
        valor = self.search_entry.get().strip()

        if not valor:
            return

        nodo = None
        if criterio == "iso3":
            nodo = self.tree.search_iso3(valor)
        elif criterio == "nombre":
            nodo = self.tree.search_nombre(valor)
        elif criterio == "promedio":
            try:
                promedio = float(valor)
                nodo = self.tree.search_promedio(promedio)
            except ValueError:
                nodo = None

        if nodo:
            if criterio == "iso3":
                value = nodo.iso3
            elif criterio == "nombre":
                value = nodo.country
            else:
                value = f"{nodo.average:.3f}"

            self.node_combobox.configure(values=[value])
            self.node_combobox.set(value)
        else:
            self.node_combobox.configure(values=["No encontrado"])
            self.node_combobox.set("No encontrado")

    def insert_node(self):
        p = ctk.CTkToplevel(self)
        p.title("Insertar nodo")
        p.geometry("300x300")

        iso3_entry = ctk.CTkEntry(p, placeholder_text="ISO3")
        iso3_entry.pack(pady=5)

        nombre_entry = ctk.CTkEntry(p, placeholder_text="Nombre")
        nombre_entry.pack(pady=5)

        promedio_entry = ctk.CTkEntry(p, placeholder_text="Promedio")
        promedio_entry.pack(pady=5)

        def confirmar():
            iso3 = iso3_entry.get().strip()
            nombre = nombre_entry.get().strip()
            try:
                promedio = float(promedio_entry.get().strip())
            except ValueError:
                mb.showerror("Error", "Promedio inválido")
                return

            if iso3 and nombre:
                self.tree.insert(iso3, promedio, nombre)
                self.display_tree()
                p.destroy()

        confirmar_btn = ctk.CTkButton(p, text="Confirmar", command=confirmar)
        confirmar_btn.pack(pady=10)

    def delete_node(self):
        nodo = self.get_selected_node()
        if nodo:
            self.tree.delete(nodo.average)
            self.display_tree()
            self.node_combobox.configure(values=[])
            self.node_combobox.set("")

    def search_by_criteria(self):
        options = ["Países con temperatura en año X > promedio global de ese año", "Países con temperatura en año X < promedio global en todos los años", "Países con promedio >= valor dado"]
        choice = simpledialog.askinteger("Selección de criterio", "Seleccione criterio:\n1. Países con temperatura en año X > promedio global de ese año\n2.Países con temperatura en año X < promedio global en todos los años\n3. Países con promedio >= valor dado", minvalue = 1, maxvalue = 3)
        if not choice:
            return
        if choice == 1:
            year = simpledialog.askinteger("Año", "Ingrese el año", minvalue = 1961, maxvalue = 2022)
            if not year:
                return
            nodes = self.tree.criterio_a(year, self.df)
        elif choice == 2:
            year = simpledialog.askinteger("Año", "Ingrese el año", minvalue = 1961, maxvalue = 2022)
            if not year:
                return
            nodes = self.tree.criterio_b(year, self.df)
        else:
            avg = simpledialog.askfloat("Promedio", "Ingrese valor del promedio:")
            if avg is None:
                return
            nodes = self.tree.criterio_c(avg)
        
        if not nodes:
            mb.showinfo("Resultado", "No se encontraron países con ese criterio")
            return
        
        self.criteria_cb.configure(values = [f"{n.iso3} - {n.country}" for n in nodes])
        self.criteria_cb.current(0)