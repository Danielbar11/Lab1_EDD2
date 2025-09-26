from tkinter import simpledialog
import tkinter as tk
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
        
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(side="right", fill="both", expand=True)
        self.right_frame.rowconfigure(0, weight=1)
        self.right_frame.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self.right_frame, width=700, height=500, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_y = tk.Scrollbar(self.right_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.scrollbar_x = tk.Scrollbar(self.right_frame, orient="horizontal", command=self.canvas.xview)
        self.scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        self.sidebar = ctk.CTkFrame(self, width=250)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        self.insert_button = ctk.CTkButton(self.sidebar, text="Insertar nodo", command=self.insert_node)
        self.insert_button.pack(pady=10)
        
        self.delete_all_button = ctk.CTkButton(self.sidebar, text="Eliminar todo el árbol", command=self.delete_all_nodes)
        self.delete_all_button.pack(pady=10, fill="x")

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
        
        search_frame = ctk.CTkFrame(self.sidebar)
        search_frame.pack(fill="x", pady=10)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Ingrese valor de búsqueda")
        self.search_entry.pack(pady=5, fill="x")
        self.search_criteria = ctk.CTkComboBox(search_frame, values=["iso3", "nombre", "promedio"], state="readonly")
        self.search_criteria.set("iso3")
        self.search_criteria.pack(pady=5, fill="x")
        self.search_button = ctk.CTkButton(search_frame, text="Buscar", command=self.search_node)
        self.search_button.pack(pady=5, fill="x")
        self.node_combobox = ctk.CTkComboBox(search_frame, values=[], state="readonly")
        self.node_combobox.pack(pady=5, fill="x")

        self.delete_button = ctk.CTkButton(search_frame, text="Eliminar nodo seleccionado", command=self.delete_node)
        self.delete_button.pack(pady=5, fill="x")

        criteria_frame = ctk.CTkFrame(self.sidebar)
        criteria_frame.pack(fill="x", pady=10)
        self.criteria_button = ctk.CTkButton(criteria_frame, text="Buscar por criterio", command=self.search_by_criteria)
        self.criteria_button.pack(pady=5, fill="x")
        self.criteria_cb = ctk.CTkComboBox(criteria_frame, values=[], state="readonly")
        self.criteria_cb.pack(pady=5, fill="x")
        self.delete_criteria_button = ctk.CTkButton(criteria_frame, text="Eliminar nodo de criterios", command=self.delete_node_from_criteria)
        self.delete_criteria_button.pack(pady=5)
        
        self.info_label = ctk.CTkLabel(self.sidebar, text="Selecciona un nodo")
        self.info_label.pack(pady=10, fill="x")

        self.recorrido_button = ctk.CTkButton(self.sidebar, text="Recorridos", command=self.show_recorrido)
        self.recorrido_button.pack(pady=10, fill="x")

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
        else:
            self.canvas.delete("all")
            self.tree_image = None
            self.canvas.config(scrollregion=(0, 0, 0, 0))    

    
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

    def show_recorrido(self):
        if self.tree.root is None:
            mb.showinfo("Recorridos", "El árbol está vacío")
            return
        
        recorrido = self.tree.recorrido_por_niveles(self.tree.root)
        mb.showinfo("Recorrido por niveles", " -> ".join(recorrido))

    def get_selected_node(self):
        select = self.node_combobox.get()
        if not select:
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
            
        criteria_select = self.criteria_cb.get()
        if criteria_select:
            iso3 = criteria_select.split(" - ")[0]
            return self.tree.search_iso3(iso3)
        return None
    
    def search_node(self):
        self.node_combobox.configure(values = [])
        self.node_combobox.set("")
        criterio = self.search_criteria.get()
        valor = self.search_entry.get().strip()

        if not valor:
            mb.showwarning("Advertencia", "Debe ingresar un valor para buscar")
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
                mb.showerror("Error", "Debe ingresar un número válido para promedio")
                return

        if nodo:
            if criterio == "iso3":
                value = nodo.iso3
            elif criterio == "nombre":
                value = nodo.country
            else:
                value = f"{nodo.average}"

            self.node_combobox.configure(values=[value])
            self.node_combobox.set(value)
        else:
            mb.showinfo("Resultado", "No se encontró el nodo")

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
            ok = self.tree.delete(nodo.average)
            if ok:
                self.display_tree()
                self.node_combobox.configure(values=[])
                self.node_combobox.set("")
                mb.showinfo("Eliminación", "Se eliminó el nodo correctamente")
            else:
                mb.showerror("Error", "No se pudo eliminar el nodo")
        else:
            mb.showwarning("Advertencia", "Debe seleccionar un nodo para eliminar")

    def delete_node_from_criteria(self):
        select = self.criteria_cb.get()
        if not select:
            mb.showwarning("Advertencia", "Debe seleccionar un nodo en criterios para eliminar")
            return

        iso3 = select.split(" - ")[0]
        nodo = self.tree.search_iso3(iso3)
        if nodo:
            ok = self.tree.delete(nodo.average)
            if ok:
                self.display_tree()
                self.criteria_cb.configure(values=[])
                self.criteria_cb.set("")
                mb.showinfo("Eliminación", f"Se eliminó el nodo {nodo.iso3}")
            else:
                mb.showerror("Error", "No se pudo eliminar el nodo")
        else:
            mb.showwarning("Advertencia", "No se encontró el nodo seleccionado en criterios")

    def delete_all_nodes(self):
        confirm = mb.askyesno("Confirmar", "¿Está seguro de que desea eliminar todo el árbol?")
        if confirm:
            self.tree = Tree()
            self.tree_visualizer = TreeVisualizer(self.tree)
            self.node_combobox.configure(values=[])
            self.node_combobox.set("")
            self.criteria_cb.configure(values=[])
            self.criteria_cb.set("")
            self.display_tree()
            mb.showinfo("Eliminación", "Se eliminó todo el árbol")

    def search_by_criteria(self):
        options = ["Países con temperatura en año X > promedio global de ese año", "Países con temperatura en año X < promedio global en todos los años", "Países con promedio >= valor dado"]
        choice = simpledialog.askinteger("Selección de criterio", "Seleccione criterio:\n1. Países con temperatura en año X > promedio global de ese año\n2.Países con temperatura en año X < promedio global en todos los años\n3. Países con promedio >= valor dado", minvalue = 1, maxvalue = 3, parent = self)
        if not choice:
            return
        if choice == 1:
            year = simpledialog.askinteger("Año", "Ingrese el año", minvalue = 1961, maxvalue = 2022, parent = self)
            if not year:
                return
            nodes = self.tree.criterio_a(year, self.df)
        elif choice == 2:
            year = simpledialog.askinteger("Año", "Ingrese el año", minvalue = 1961, maxvalue = 2022, parent = self)
            if not year:
                return
            nodes = self.tree.criterio_b(year, self.df)
        else:
            avg = simpledialog.askfloat("Promedio", "Ingrese valor del promedio:", parent = self)
            if avg is None:
                return
            nodes = self.tree.criterio_c(avg)
        
        if not nodes:
            mb.showinfo("Resultado", "No se encontraron países con ese criterio", parent = self)
            return
        
        self.criteria_cb.configure(values = [f"{n.iso3} - {n.country}" for n in nodes])
        self.criteria_cb.current(0)