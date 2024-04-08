from tkinter import *
import sqlite3 as sql
from tkinter import messagebox
import re
from tkinter import ttk
from datetime import datetime
class Registro:

    def __init__(self, archivo, tabla_actual, tipo, actualizar_treeview_callback):
        self.archivo = archivo
        self.raza_combobox=None
        self.tabla_actual = tabla_actual
        self.tipo=tipo
        self.actualizar_treeview=actualizar_treeview_callback
        self.entries={}
        

        #Creacion del TopLevel
        self.window = Toplevel() 
        self.window.title(self.tipo)
        self.window.resizable(0, 0)
        self.window.config(bd=10)

        # Título
        self.titulo = Label(self.window, text=f"{self.tipo} Registro {tabla_actual}", fg="black",
                       font=("Comic Sans", 13, "bold"), pady=5).pack()
        # Logo
        # self.imagen_registro = Image.open("src/new.png")
        # self.nueva_imagen = self.imagen_registro.resize((40, 40))
        # self.render = ImageTk.PhotoImage(self.nueva_imagen)
        # self.label_imagen = Label(self.window, image=self.render)
        # self.label_imagen.image = self.render
        # self.label_imagen.pack(pady=5)

        # Marco
        self.marco = LabelFrame(self.window, text="Datos", font=("Comic Sans", 10, "bold"))
        self.marco.config(bd=2, pady=5)
        self.marco.pack()

        # Botones
        self.frame_botones = Frame(self.window)
        self.frame_botones.pack(side='bottom')

        # Se cargan los botones en el TopLevel
        if self.tipo == 'Añadir':

            self.boton_registrar = Button(self.frame_botones, text="REGISTRAR", height=2, width=10, bg="green", fg="black",
                                 font=("Comic Sans", 10, "bold"), command=lambda: self.anadir())
            self.boton_registrar.pack(side='left', padx=3, pady=3)

        elif self.tipo == 'Actualizar':

            self.boton_registrar = Button(self.frame_botones, text="ACTUALIZAR", height=2, width=10, bg="blue", fg="black",
                                 font=("Comic Sans", 10, "bold"), command=lambda: self.actualizar())
            self.boton_registrar.pack(side='left', padx=3, pady=3)        

        self.boton_limpiar = Button(self.frame_botones, text="LIMPIAR",command=lambda: self.limpiar(), height=2, width=10, bg="gray", fg="black",
                               font=("Comic Sans", 10, "bold"))
        self.boton_limpiar.pack(side='left', padx=3, pady=3)

        self.boton_cancelar = Button(self.frame_botones, text="CERRAR", command=lambda: self.window.destroy(), height=2, width=10, bg="red",
                                fg="black", font=("Comic Sans", 10, "bold"))
        self.boton_cancelar.pack(side='left', padx=3, pady=3)
        
        if self.tabla_actual=='inventario':
            self.boton_actualizar = Button(self.frame_botones, text="ACTUALIZAR", command=lambda: self.actualizar_precio(), height=2, width=10, bg="red",
                                    fg="black", font=("Comic Sans", 10, "bold"))
            self.boton_actualizar.pack(side='left', padx=3, pady=3)
        
        
        # Se cargan los atributos de la tabla donde se quiere trabajar
        with sql.connect(self.archivo) as conn:
            self.cursor = conn.cursor()
            self.cursor.execute(f'PRAGMA table_info({tabla_actual})')
            self.atributos = self.cursor.fetchall()
            self.altrua_ventana=len(self.atributos) * 40 + 200
            self.window.geometry(f'500x{self.altrua_ventana}+{self.window.winfo_screenmmwidth()+600}+{0}')

            # Consulta PRAGMA foreign_key_list
            self.cursor.execute(f'PRAGMA foreign_key_list({tabla_actual})')
            self.foraneas = {foranea[3]:(foranea[2],foranea[3],foranea[4]) for foranea in self.cursor.fetchall()}

            self.entries = {}  # Diccionario para almacenar las Entry widgets
            self.identificadores_combobox = {}

            # Se cargan Labels que mostraran los nombres de las llaves foraneas
            for atributo in self.atributos:
                if atributo[1] in self.foraneas:
                    self.label = Label(self.marco, text=atributo[1], font=('Comic Sans', 15))
                    self.label.grid(row=atributo[0], column=0, sticky=W, padx=5, pady=5)

                    # Crear una variable controladora para el combobox
                    codigo_var = StringVar()

                    # Asignar un identificador único al ComboBox
                    identificador_combobox = f"{self.tabla_actual}_{atributo[1]}"
                    self.identificadores_combobox[identificador_combobox] = codigo_var

                    # Consultar los valores del campo 
                    with sql.connect(self.archivo) as conn:
                        cursor = conn.cursor()
                        cursor.execute(f"SELECT nombre FROM {self.foraneas[atributo[1]][0]}")
                        nombres_tablas = [nombre[0] for nombre in cursor.fetchall()]

                    # Crear el combobox con los valores obtenidos
                    combobox = ttk.Combobox(self.marco, values=nombres_tablas, textvariable=codigo_var, width=30, height=10)
                    combobox.grid(row=atributo[0], column=1, padx=5, pady=5, sticky=W)

                    # Al tocar el combobox, actualizar la variable controladora con el código correspondiente
                    combobox.bind("<<ComboboxSelected>>", lambda event, identificador=identificador_combobox: (self.actualizar_codigo_var(identificador))
)
                    # Al tocar el combobox, actualizar la variable controladora y los productos disponibles
                    combobox.bind("<<ComboboxSelected>>", lambda event, identificador=identificador_combobox: (self.actualizar_codigo_var(identificador), self.actualizar_productos_disponibles(identificador)))

                    combobox.bind("<KeyRelease>", lambda event: self.filtrar_opciones(event))
                    #Se impide que se puedan pasar valores por teclado a los Comboboxes
                    if atributo[1] != 'id_producto':
                        combobox['state']='readonly'
                

                    self.entries[atributo[1]] = combobox  # Almacenar el combobox en el diccionario de entries

                #Se muestran los demas atributos que no son llaves foraneas
                else:

                    self.label = Label(self.marco, text=atributo[1], font=('Comic Sans', 15))
                    self.label.grid(row=atributo[0], column=0, sticky=W, padx=5, pady=5)

                    if atributo[1].lower() == 'precio':
                        self.label_precio = Label(self.marco, text="Precio", font=('Comic Sans', 15))
                        self.label_precio.grid(row=atributo[0], column=0, sticky=W, padx=5, pady=5)
                        self.entry_precio = Entry(self.marco, font=('Comic Sans', 15))
                        self.entry_precio.grid(row=atributo[0], column=1, padx=5, pady=5)
                        self.entries[atributo[1]] = self.entry_precio

                    #En caso de que el atributo sea 'sexo' se hacen 2 Radiobuttons para seleccionar una opcion
                    elif atributo[1].lower()=='sexo':
                        self.sexo_var=StringVar()
                        self.radio_masculino=Radiobutton(self.marco, text="M", font=('Cosmic Sans',15), variable=self.sexo_var, value='M')
                        self.radio_femenino=Radiobutton(self.marco, text='F', font=('Cosmic Sans', 15), variable=self.sexo_var, value='F')
                        self.radio_masculino.grid(row=atributo[0], column=1, padx=5, pady=5, sticky=W)
                        self.radio_femenino.grid(row=atributo[0], column=1, padx=5, pady=5, sticky=E)
                        self.marco.rowconfigure(atributo[0],weight=1)
               
                        self.entries[atributo[1]] = self.sexo_var
                        
                    elif atributo[1].lower()=='cantidad_vendida':
                          self.cantidad=Spinbox(self.marco, from_=0, to=100000, width= 10, font=('Comic Sans', 15))
                          self.cantidad.grid(row=atributo[0], column=1, padx=5, pady=5, sticky=W)
                          self.entries[atributo[1]]=self.cantidad
                  
                    else:
                        self.entry = Entry(self.marco, font=('Comic Sans', 15))
                        self.entry.grid(row=atributo[0], column=1, padx=5, pady=5)

                        self.entries[atributo[1]] = self.entry
                
                    # Deshabilitar el Entry correspondiente a la clave primaria en la función actualizar
                    if tipo == 'Actualizar' and atributo[5] == 1:  
                        self.entry.configure(state='readonly')
  
    def limpiar(self):
        #Funcion para eliminar todos los valores en el registro
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set('')  
            elif isinstance(entry, Entry):
                entry.delete(0, END)
            elif isinstance(entry, StringVar):
                entry.set('')
            elif isinstance(entry,Spinbox):
                if entry.cget('state') == 'readonly':
                    entry.config(state='normal')
                    entry.delete(0,END)
                    entry.config(state='readonly')
                else:
                   entry.delete(0,END)
                   entry.insert(0,0)
            
                   
    def anadir(self):
        # Verificar si todos los campos obligatorios están llenos
        for atributo in self.atributos:
            entry_widget = self.entries[atributo[1]]

            if atributo[2] == 1 and entry_widget.get() == "":
                messagebox.showerror("Error", f"El campo '{atributo[1]}' no puede estar vacío.")
                return
        
        
    # Todos los campos obligatorios están llenos, guardar el registro en la base de datos
        self.valores = [entry_widget.get() for entry_widget in self.entries.values()]

        if self.atributos[0][1].lower()=='sexo':
            self.valores[0]=self.sexo_var.get()

        #En caso de estar todos los datos correctos guardar los cambios en la base de datos
        with sql.connect(self.archivo) as conn:
            self.cursor = conn.cursor()
            try:
                self.cursor.execute(f"INSERT INTO {self.tabla_actual} VALUES ({', '.join(['?']*len(self.valores))})", self.valores)
                conn.commit()
                self.actualizar_treeview(self.tabla_actual)
                messagebox.showinfo("Éxito", "Registro guardado exitosamente.")
            except sql.IntegrityError:
                #Si se repite el ID salta este error
                messagebox.showerror('Error','El ID ya existe')
                raise Exception
            self.window.destroy()

    def cargar(self, datos):
        self.datos = datos
        # Carga las Entry widgets con los nuevos datos
        for i, atributo in enumerate(self.atributos):
            entry_widget = self.entries[atributo[1]]

            # Verifica si hay suficientes elementos en la lista datos
            if i < len(datos):
                if isinstance(entry_widget, Entry) or isinstance(entry_widget,Spinbox) :
                    if entry_widget.cget('state') == 'readonly':
                        #Si el entry esta deshabilitado se pasa a modo normal para poder cargar los datos y mostrarlos 
                        entry_widget.config(state='normal')
                        entry_widget.delete(0, END)
                        entry_widget.insert(0, datos[i])
                        entry_widget.config(state='readonly')
                    elif isinstance(entry_widget,ttk.Combobox):
                        #Si el Combobox esta deshabilitado se pasa a modo normal para poder cargar los datos y mostrarlo
                        entry_widget.set(datos[i])

                    else:
                        entry_widget.delete(0, END)
                        entry_widget.insert(0, datos[i])

                else:
                    #Cargar los datos de rangoEdad, tipoPlaza o de sexo
                    self.cargar_demas_valores(atributo, datos[i])

    def cargar_demas_valores(self, atributo, valor):

        if atributo[1].lower() == 'sexo':
            self.sexo_var.set(valor)
    

    def actualizar(self):
        # Obtener la clave primaria y sus índices
        primary_key_index = None
        primary_key_name = None
        for atributo in self.atributos:
            if atributo[5] == 1:  # Comprueba si el atributo es una clave primaria
                primary_key_index = atributo[0] - 1  # Resta 1 porque los índices comienzan desde 0
                primary_key_name = atributo[1]
                break
        
        # guarda el valor de la llave primaria
        primary_key_value = self.entries[primary_key_name].get()

        # Verificar si hay cambios en los valores antes de la actualización
        nuevos_valores = [entry_widget.get() for entry_widget in self.entries.values()]
        if nuevos_valores == list(self.datos):
            messagebox.showinfo("Información", "No hay cambios para actualizar.")
            return
        
        # Construir la sentencia SQL de actualización
        update_sql = f"UPDATE {self.tabla_actual} SET "
        update_sql += ", ".join(f"{atributo[1]} = ?" for atributo in self.atributos)
        update_sql += f" WHERE {primary_key_name} = ?"

        # Ejecutar la sentencia SQL de actualización
        with sql.connect(self.archivo) as conn:
            self.cursor = conn.cursor()
            self.cursor.execute(update_sql, nuevos_valores + [primary_key_value])
            conn.commit()
            self.actualizar_treeview(self.tabla_actual)
            messagebox.showinfo("Éxito", "Registro actualizado exitosamente.")
            self.window.destroy()


    def actualizar_codigo_var(self, identificador):
        try:
            nombre_seleccionado = self.identificadores_combobox[identificador].get()
            try:
                _, atributo = identificador.split('_')
            except ValueError:
                pass
            
            # Consultar las razas asociadas con el animal seleccionado
            with sql.connect(self.archivo) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT nombre FROM razas_animales WHERE categoría = ?", (nombre_seleccionado,))
                razas = [raza[0] for raza in cursor.fetchall()]

            # Actualizar los valores del ComboBox de razas
            self.entries['Raza'].config(values=razas)

        except Exception as e:
            print("Error:", e)

    def actualizar_productos_disponibles(self, identificador_combobox):
        try:
            animal_seleccionado = self.identificadores_combobox[identificador_combobox].get()
            try:
                _, atributo = identificador_combobox.split('_')
            except ValueError:
                pass

            # Consultar los productos disponibles para el animal seleccionado
            with sql.connect(self.archivo) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT nombre FROM productos WHERE categoria = ?", (animal_seleccionado,))
                productos = [producto[0] for producto in cursor.fetchall()]

                # Actualizar los valores del ComboBox de productos
            self.entries['id_producto']['values'] = productos

            # Enlazar la función de filtrado al evento KeyRelease
            self.entries['id_producto'].bind("<KeyRelease>", lambda event: self.filtrar_opciones(event))

        except Exception as e:
            print("Error:", e)
            
    def filtrar_opciones(self, event):
        try:
            
            # Obtener la cadena de búsqueda desde el Combobox
            search_string = event.widget.get().lower()
        
            # Obtener las opciones originales del menú desplegable
            opciones_originales = self.entries['id_producto']['values']

            # Filtrar las opciones que coinciden con la cadena de búsqueda
            opciones_filtradas = [opcion for opcion in opciones_originales if search_string in opcion.lower()]

            # Actualizar los valores del menú desplegable con las opciones filtradas
            self.entries['id_producto']['values'] = opciones_filtradas

        except Exception as e:
            print("Error:", e)
         

    def actualizar_articulos(self, event):
        animal_seleccionado = self.animal_combobox.get()
        producto_seleccionado = self.producto_combobox.get()

        # Aquí deberías consultar tu base de datos para obtener los artículos
        # que corresponden al animal y producto seleccionados
        with sql.connect(self.archivo) as conn:
            cursor = conn.cursor()
            query = f"""
            SELECT articulo FROM productos 
            WHERE categoria = ? AND nombre = ?
            """
            cursor.execute(query, (animal_seleccionado, producto_seleccionado))
            articulos = cursor.fetchall()

        # Actualiza tu combobox de artículos con los nuevos valores
        self.articulo_combobox['values'] = [articulo[0] for articulo in articulos]
        
        # Agrega esta función dentro de la clase Registro
    def actualizar_precio(self):
        # Obtener el nombre del producto seleccionado
        nombre_producto = self.entries['id_producto'].get()

        # Realizar una consulta a la base de datos para obtener el precio del producto
        with sql.connect(self.archivo) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT precio_venta FROM productos WHERE nombre = ?", (nombre_producto,))
            precio_producto = cursor.fetchone()

        # Si se encuentra el precio en la base de datos, actualizar el campo de entrada del precio
        if precio_producto:
            self.entries['precio'].delete(0, END)
            self.entries['precio'].insert(0, precio_producto[0])