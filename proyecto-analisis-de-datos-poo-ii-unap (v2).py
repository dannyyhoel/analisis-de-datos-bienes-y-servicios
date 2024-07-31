import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import rcParams
import PyPDF2

class MyApp:
  def __init__(self, root):
    self.root = root
    self.root.title("Analizador de Archivos")
    self.root.geometry("1280x600")
    self.menu_bar = tk.Menu(root)
    root.config(menu=self.menu_bar)
    # Menú Archivo
    self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
    self.menu_bar.add_cascade(label="Archivo", menu=self.file_menu)
    self.file_menu.add_command(label="Importar Archivo", command=self.importar_archivo)
    self.file_menu.add_separator()
    self.file_menu.add_command(label="Salir", command=root.quit)
    # Menú Reporte
    self.report_menu = tk.Menu(self.menu_bar, tearoff=0)
    self.menu_bar.add_cascade(label="Reporte", menu=self.report_menu)
    self.report_menu.add_command(label="Exportar a PDF", command=self.exportar_a_pdf)
    # Ajustar parámetros globales de Matplotlib para el tamaño de la fuente
    rcParams['font.size'] = 6
    # Inicializar variables
    self.data = None
    self.figures = {}
    self.current_figure = None
    self.canvas = []
  def importar_archivo(self):
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
    try:
      if filepath.endswith(".csv"):
        try:
          self.data = pd.read_csv(filepath, delimiter = ",")
        except pd.errors.ParserError:
          self.data = pd.read_csv(filepath, delimiter = ";")
      elif filepath.endswith(".json"):
        self.data = pd.read_json(filepath)
      elif filepath.endswith(".xlsx"):
        self.data = pd.read_excel(filepath)
      else:
        messagebox.showerror("Error", "Formato de archivo no compatible")
        return
      self.mostrar_graficos()
      messagebox.showinfo("Éxito", f"Archivo '{filepath}' importado correctamente.")
    except Exception as e:
      messagebox.showerror("Error", f"No se pudo importar el archivo:\n{str(e)}")
  def mostrar_widgets_fecha(self):
    # Crear entradas de fecha y botón solo si hay datos disponibles
    if self.data is not None:
      # Obtener fechas mínima y máxima del dataset
      fecha_minima = str(self.data['FECHA_ORDEN'].min())
      fecha_maxima = str(self.data['FECHA_ORDEN'].max())
      # Frame para las entradas de fecha y botón
      frame_fecha = tk.Frame(self.root)
      frame_fecha.pack(side=tk.TOP, padx=10, pady=10)
      # Etiqueta y combobox para fecha mínima
      tk.Label(frame_fecha, text="Fecha mínima:").grid(row=0, column=0, padx=5, pady=5)
      self.min_fecha_combobox = ttk.Combobox(frame_fecha, values=pd.date_range(start=fecha_minima, end=fecha_maxima, freq='D').strftime('%Y%m').tolist())
      self.min_fecha_combobox.set(fecha_minima)
      self.min_fecha_combobox.grid(row=0, column=1, padx=5, pady=5)
      # Etiqueta y combobox para fecha máxima
      tk.Label(frame_fecha, text="Fecha máxima:").grid(row=1, column=0, padx=5, pady=5)
      self.max_fecha_combobox = ttk.Combobox(frame_fecha, values=pd.date_range(start=fecha_minima, end=fecha_maxima, freq='D').strftime('%Y%m').tolist())
      self.max_fecha_combobox.set(fecha_maxima)
      self.max_fecha_combobox.grid(row=1, column=1, padx=5, pady=5)
      # Botón para generar gráficos
      self.generar_graficos_button = tk.Button(frame_fecha, text="Generar Gráficos", command=self.generar_graficos)
      self.generar_graficos_button.grid(row=2, columnspan=2, pady=10)
  def generar_graficos(self):
    # Obtener fechas ingresadas por el usuario
    min_fecha = self.min_fecha_entry.get_date()
    max_fecha = self.max_fecha_entry.get_date()
    # Filtrar datos dentro del rango de fechas
    df_filtered = self.data[(self.data['FECHA_ORDEN'] >= min_fecha) & (self.data['FECHA_ORDEN'] <= max_fecha)]
    # Mostrar gráficos con los datos filtrados
    self.mostrar_graficos(df_filtered)
  def mostrar_graficos(self, data = None):
    # Limpiar gráficos previos si existen
    if len(self.canvas) > 0:
      for c in self.canvas:
        c.get_tk_widget().pack_forget()
      self.canvas = []
    # Crear figuras y guardar referencias
    self.figures["Total Monto Órdenes por Mes"] = self.grafico_monto_ordenes_por_mes()
    self.figures["Total Órdenes por Mes"] = self.grafico_ordenes_por_mes()
    self.figures["Cantidad de Bienes y Servicios"] = self.grafico_cantidad_bienes_servicios()
    self.figures["Órdenes por Fuente de Financiamiento"] = self.grafico_ordenes_por_fuente_financiamiento()
    # Crear figuras y guardar referencias
    fig1 = self.figures["Total Monto Órdenes por Mes"]
    fig2 = self.figures["Total Órdenes por Mes"]
    fig3 = self.figures["Cantidad de Bienes y Servicios"]
    fig4 = self.figures["Órdenes por Fuente de Financiamiento"]
    # Crear Frames para agrupar los Canvas
    frame1 = tk.Frame(self.root)
    frame2 = tk.Frame(self.root)
    # Crear los Canvas para cada figura y empaquetar en los Frames correspondientes
    self.canvas1 = FigureCanvasTkAgg(fig1, master=frame1)
    self.canvas2 = FigureCanvasTkAgg(fig2, master=frame1)
    self.canvas3 = FigureCanvasTkAgg(fig3, master=frame2)
    self.canvas4 = FigureCanvasTkAgg(fig4, master=frame2)
    # Empaquetar los Canvas en los Frames
    self.canvas1.get_tk_widget().pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
    self.canvas2.get_tk_widget().pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
    self.canvas3.get_tk_widget().pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
    self.canvas4.get_tk_widget().pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
    # Empaquetar los Frames en la interfaz gráfica principal
    frame1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    frame2.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    # Agregar los Canvas a la lista para su gestión
    self.canvas.extend([self.canvas1, self.canvas2, self.canvas3, self.canvas4])
    # Redibujar los gráficos en los Canvas
    self.canvas1.draw()
    self.canvas2.draw()
    self.canvas3.draw()
    self.canvas4.draw()
  def grafico_monto_ordenes_por_mes(self):
    if self.data is None:
      return
    df = self.data.copy()
    # Convierte la columna 'FECHA_ORDEN' a tipo string
    df['FECHA_ORDEN'] = df['FECHA_ORDEN'].astype(str)
    # Elimina las filas con valores NaN en la columna 'FECHA_ORDEN'
    df = df.dropna(subset=['FECHA_ORDEN'])
    # Extrae el año y el mes de la fecha de orden y crea columnas separadas
    df['Año'] = df['FECHA_ORDEN'].str[:4]
    df['Mes'] = df['FECHA_ORDEN'].str[4:6]
    # Convierte el año y el mes a tipo int, maneja los errores con NaN
    df['Año'] = pd.to_numeric(df['Año'], errors='coerce')
    df['Mes'] = pd.to_numeric(df['Mes'], errors='coerce')
    # Elimina las filas con valores NaN en las columnas 'Año' y 'Mes'
    df = df.dropna(subset=['Año', 'Mes'])
    # Agrupa por año y mes, y calcula la suma de los montos de las órdenes
    total_por_mes = df.groupby(['Año', 'Mes'])['MONTO_REQUERIDO'].sum()
    # Crear figura de Matplotlib
    fig = plt.figure(figsize=(1, 1))
    ax = fig.add_subplot(111)
    total_por_mes.plot(marker='o', linestyle='-', ax=ax)
    ax.set_title('Total de Monto de Órdenes por Mes')
    ax.set_xlabel('Mes')
    ax.set_ylabel('Monto Total de Órdenes')
    ax.grid(True)
    plt.xticks(rotation=10)
    return fig
  def grafico_ordenes_por_mes(self):
    if self.data is None:
      return
    df = self.data.copy()
    # Convierte la columna 'FECHA_ORDEN' a tipo string
    df['FECHA_ORDEN'] = df['FECHA_ORDEN'].astype(str)
    # Elimina las filas con valores NaN en la columna 'FECHA_ORDEN'
    df = df.dropna(subset=['FECHA_ORDEN'])
    # Extrae el año y el mes de la fecha de orden y crea columnas separadas
    df['Año'] = df['FECHA_ORDEN'].str[:4]
    df['Mes'] = df['FECHA_ORDEN'].str[4:6]
    # Convierte el año y el mes a tipo int, maneja los errores con NaN
    df['Año'] = pd.to_numeric(df['Año'], errors='coerce')
    df['Mes'] = pd.to_numeric(df['Mes'], errors='coerce')
    # Elimina las filas con valores NaN en las columnas 'Año' y 'Mes'
    df = df.dropna(subset=['Año', 'Mes'])
    # Agrupa por año y mes, y calcula el número total de las órdenes
    total_por_mes = df.groupby(['Año', 'Mes'])['MONTO_REQUERIDO'].count()
    # Crear figura de Matplotlib
    fig = plt.figure(figsize=(1, 1))
    ax = fig.add_subplot(111)
    total_por_mes.plot(marker='o', linestyle='-', ax=ax)
    ax.set_title('Total de Órdenes por Mes')
    ax.set_xlabel('Mes')
    ax.set_ylabel('Total de Órdenes')
    ax.grid(True)
    plt.xticks(rotation=10)
    return fig
  def grafico_cantidad_bienes_servicios(self):
    if self.data is None:
      return
    df = self.data.copy()
    # Contar la cantidad de registros por tipo
    count_tipo = df['TIPO'].value_counts()
    # Crear figura de Matplotlib
    fig = plt.figure(figsize=(1, 1))
    ax = fig.add_subplot(111)
    count_tipo.plot(kind='bar', ax=ax)
    ax.set_title('Cantidad de Bienes y Servicios')
    ax.set_xlabel('Tipo')
    ax.set_ylabel('Cantidad')
    ax.grid(True)
    plt.xticks(rotation=10)
    return fig
  def grafico_ordenes_por_fuente_financiamiento(self):
    if self.data is None:
      return
    # Mapeo de valores numéricos a nombres descriptivos
    mapping_fuente_financ = {
      0: 'Recursos Ordinarios',
      9: 'Recursos directamente Recaudados',
      13: 'Donaciones y transferencias',
      18: 'Canon y sobrecanon',
      19: 'Recursos por operaciones oficiales de crédito'
    }
    # Reemplazar valores numéricos por nombres descriptivos
    df = self.data.copy()
    df['FUENTE_FINANC'] = df['FUENTE_FINANC'].replace(mapping_fuente_financ)
    # Contar órdenes por cada fuente de financiamiento
    ordenes_por_fuente = df['FUENTE_FINANC'].value_counts()
    # Crear figura de Matplotlib
    fig = plt.figure(figsize=(1, 1))
    ax = fig.add_subplot(111)
    ordenes_por_fuente.plot(kind='bar', ax=ax, color='skyblue')
    # Configuración del gráfico
    ax.set_title('Órdenes de Compra o Servicio por Fuente de Financiamiento')
    ax.set_xlabel('Fuente de Financiamiento')
    ax.set_ylabel('Cantidad de Órdenes')
    ax.grid(True)
    # Mostrar valores en las barras
    for i, v in enumerate(ordenes_por_fuente):
      ax.text(i, v + 1, str(v), ha='center', va='bottom', fontsize=10)
    plt.xticks(rotation=10)
    return fig
  def exportar_a_pdf(self):
    if not self.figures:
      messagebox.showwarning("Advertencia", "No hay gráficos para exportar.")
      return
    try:
      nombre_archivo = "reporte-unap.pdf"
      with PdfPages(nombre_archivo) as pdf:
        for figure_name, figure in self.figures.items():
          figure.savefig(pdf, format='pdf')
      messagebox.showinfo("Éxito", f"Gráficos exportados a PDF correctamente.\nNombre del archivo: {nombre_archivo}")
    except Exception as e:
      messagebox.showerror("Error", f"No se pudo exportar a PDF:\n{str(e)}")

def main():
  root = tk.Tk()
  app = MyApp(root)
  root.mainloop()

if __name__ == "__main__":
  main()