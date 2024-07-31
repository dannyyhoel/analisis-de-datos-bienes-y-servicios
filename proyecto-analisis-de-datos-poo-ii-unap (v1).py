import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import json
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io
import sys
import os
from PIL import Image, ImageTk






class AnalizadorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Analizador de Archivos")
        self.master.geometry("800x600")  # Aumentado para acomodar los nuevos elementos
        
        self.menu_bar = tk.Menu(master)
        self.master.config(menu=self.menu_bar)
        
        # Menú Archivo
        self.file = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Archivo", menu=self.file)
        self.file.add_command(label="Importar Archivo", command=self.seleccionar_archivo)
        self.file.add_separator()
        self.file.add_command(label="Salir", command=self.master.quit)  # Use quit en lugar de destroy
        
        # Menú Análisis
        self.analisis_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Análisis", menu=self.analisis_menu)
        self.analisis_menu.add_command(label="Estadísticas Descriptivas", command=self.analizar_estadisticas_descriptivas)
        self.analisis_menu.add_command(label="Descripción de Variables", command=self.analizar_descripcion_de_variables)
        
        # Menú Gráficos
        self.graficos_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Gráficos", menu=self.graficos_menu)
        self.graficos_menu.add_command(label="Ver Total de Monto de Órdenes por Mes", command=self.mostrar_grafico_monto_de_ordenes_por_mes)
        self.graficos_menu.add_command(label="Ver Total de Órdenes por Mes", command=self.mostrar_ordenes_por_mes)

        # Añadir el marco de botones y la barra de búsqueda
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10, fill=tk.X)

        self.print_button = tk.Button(self.button_frame, text="Imprimir", command=self.imprimir_resultado)
        self.print_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.button_frame, text="Guardar", command=self.guardar_resultado)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.exit_button = tk.Button(self.button_frame, text="Salir", command=self.master.quit)  # Use quit en lugar de destroy
        self.exit_button.pack(side=tk.LEFT, padx=5)

        # Barra de búsqueda
        self.search_frame = tk.Frame(master)
        self.search_frame.pack(pady=10, fill=tk.X)

        self.search_label = tk.Label(self.search_frame, text="Buscar:")
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.search_button = tk.Button(self.search_frame, text="Buscar", command=self.buscar_dato)
        self.search_button.pack(side=tk.LEFT, padx=5)

        # Área de salida de texto
        self.text_output = tk.Text(master, wrap=tk.NONE, width=master.winfo_reqwidth() - 100, height=master.winfo_reqheight() - 170)
        self.text_output.pack(pady=(10, 0), padx=10)

    def seleccionar_archivo(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar Archivo",
            filetypes=(
                ("Archivos CSV", "*.csv"),
                ("Archivos JSON", "*.json"),
                ("Archivos Excel", "*.xlsx")
            )
        )
        if filepath:
            self.analizar_archivo(filepath)
    
    def analizar_archivo(self, filepath):
        if filepath.endswith(".csv"):
            self.filetype = "CSV"
            try:
                self.data = pd.read_csv(filepath, delimiter=",")
            except pd.errors.ParserError:
                self.data = pd.read_csv(filepath, delimiter=";")
            self.mostrar_resultado(f"Archivo CSV cargado:\n{filepath}\n")
        elif filepath.endswith(".json"):
            self.filetype = "JSON"
            with open(filepath) as f:
                data = json.load(f)
            self.data = pd.DataFrame(data)
            self.mostrar_resultado(f"Archivo JSON cargado:\n{filepath}\n")
        elif filepath.endswith(".xlsx"):
            self.filetype = "Excel"
            self.data = pd.read_excel(filepath)
            self.mostrar_resultado(f"Archivo Excel cargado:\n{filepath}\n")
        else:
            messagebox.showerror("Error", "Formato de archivo no compatible")
            self.filepath = False

    def mostrar_resultado(self, resultado):
        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, resultado)
    
    def analizar_estadisticas_descriptivas(self):
        if hasattr(self, "data"):
            if hasattr(self, "graph_shown"):
                self.canvas.get_tk_widget().pack_forget()
            resultado = self.data.describe()
            self.mostrar_resultado(f"Estadísticas Descriptivas:\n{resultado}\n")
        else:
            messagebox.showwarning("Advertencia", "Primero importe un archivo para analizar.")
    
    def analizar_descripcion_de_variables(self):
        if hasattr(self, "data"):
            if hasattr(self, "graph_shown"):
                self.canvas.get_tk_widget().pack_forget()
            output = io.StringIO()
            self.data.info(buf=output, verbose=True)
            resultado = output.getvalue()
            self.mostrar_resultado(f"Descripción de Variables:\n{resultado}\n")
        else:
            messagebox.showwarning("Advertencia", "Primero importe un archivo para analizar.")

    def mostrar_grafico_monto_de_ordenes_por_mes(self):
        if hasattr(self, "data"):
            if not hasattr(self, "graph_shown"):
                if hasattr(self, "text_output"):
                    self.text_output.pack_forget()
                self.canvas = FigureCanvasTkAgg(self.grafico_monto_ordenes_por_mes(), master=self.master)
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
                self.graph_shown = True
            else:
                messagebox.showinfo("Información", "El gráfico ya está visible.")
        else:
            messagebox.showwarning("Advertencia", "Primero importe un archivo para analizar.")
    
    def grafico_monto_ordenes_por_mes(self):
        df = self.data.copy()
        df['FECHA_ORDEN'] = df['FECHA_ORDEN'].astype(str)
        df = df.dropna(subset=['FECHA_ORDEN'])
        df['Año'] = df['FECHA_ORDEN'].str[:4]
        df['Mes'] = df['FECHA_ORDEN'].str[4:6]
        df['Año'] = pd.to_numeric(df['Año'], errors='coerce')
        df['Mes'] = pd.to_numeric(df['Mes'], errors='coerce')
        df = df.dropna(subset=['Año', 'Mes'])
        total_por_mes = df.groupby(['Año', 'Mes'])['MONTO_REQUERIDO'].sum()
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111)
        total_por_mes.plot(marker='o', linestyle='-', ax=ax)
        ax.set_title('Total de Monto de Órdenes por Mes')
        ax.set_xlabel('Mes')
        ax.set_ylabel('Monto Total de Órdenes')
        ax.grid(True)
        plt.xticks(rotation=45)
        return fig
    
    def mostrar_ordenes_por_mes(self):
        if hasattr(self, "data"):
            if not hasattr(self, "graph_shown"):
                if hasattr(self, "text_output"):
                    self.text_output.pack_forget()
                self.canvas = FigureCanvasTkAgg(self.grafico_ordenes_por_mes(), master=self.master)
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
                self.graph_shown = True
            else:
                messagebox.showinfo("Información", "El gráfico ya está visible.")
        else:
            messagebox.showwarning("Advertencia", "Primero importe un archivo para analizar.")
    
    def grafico_ordenes_por_mes(self):
        df = self.data.copy()
        df['FECHA_ORDEN'] = df['FECHA_ORDEN'].astype(str)
        df = df.dropna(subset=['FECHA_ORDEN'])
        df['Año'] = df['FECHA_ORDEN'].str[:4]
        df['Mes'] = df['FECHA_ORDEN'].str[4:6]
        df['Año'] = pd.to_numeric(df['Año'], errors='coerce')
        df['Mes'] = pd.to_numeric(df['Mes'], errors='coerce')
        df = df.dropna(subset=['Año', 'Mes'])
        total_por_mes = df.groupby(['Año', 'Mes'])['MONTO_REQUERIDO'].count()
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111)
        total_por_mes.plot(marker='o', linestyle='-', ax=ax)
        ax.set_title('Total de Órdenes por Mes')
        ax.set_xlabel('Mes')
        ax.set_ylabel('Total de Órdenes')
        ax.grid(True)
        plt.xticks(rotation=45)
        return fig
    
    def imprimir_resultado(self):
        if hasattr(self, "text_output"):
            content = self.text_output.get("1.0", tk.END)
            if content.strip():
                try:
                    with open("output.txt", "w") as file:
                        file.write(content)
                    os.startfile("output.txt", "print")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al intentar imprimir: {e}")
            else:
                messagebox.showwarning("Advertencia", "No hay contenido para imprimir.")
        else:
            messagebox.showwarning("Advertencia", "No hay resultado para imprimir.")
    
    def guardar_resultado(self):
        if hasattr(self, "text_output"):
            content = self.text_output.get("1.0", tk.END)
            if content.strip():
                file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de Texto", "*.txt")])
                if file_path:
                    try:
                        with open(file_path, "w") as file:
                            file.write(content)
                        messagebox.showinfo("Información", f"Resultado guardado en {file_path}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Error al guardar el archivo: {e}")
            else:
                messagebox.showwarning("Advertencia", "No hay contenido para guardar.")
        else:
            messagebox.showwarning("Advertencia", "No hay resultado para guardar.")
    
    def buscar_dato(self):
        search_term = self.search_entry.get()
        if hasattr(self, "data") and search_term:
            result = self.data.apply(lambda row: search_term.lower() in row.to_string().lower(), axis=1)
            filtered_data = self.data[result]
            if not filtered_data.empty:
                self.mostrar_resultado(f"Resultados de búsqueda para '{search_term}':\n{filtered_data}")
            else:
                self.mostrar_resultado(f"No se encontraron resultados para '{search_term}'.")
        else:
            messagebox.showwarning("Advertencia", "Primero importe un archivo para analizar y ingrese un término de búsqueda.")

def main():
    root = tk.Tk()
    app = AnalizadorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
