from tkinter import *
from SecondScreen import Second_Screen

class Screen:
    # Constantes para dimensiones de la ventana y botón
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    BUTTON_WIDTH = 290
    BUTTON_HEIGHT = 90
    x_position=0
    y_position=0

    def __init__(self):
        # Inicialización de la interfaz de usuario
        self.setup_ui()

    def setup_ui(self):
        # Configuración de la ventana principal
        self.root = Tk()

        # Centrar la ventana en la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width - self.WINDOW_WIDTH) // 2
        y_position = (screen_height - self.WINDOW_HEIGHT) // 2
        
        # Configuracion de la ventana
        self.root.geometry(f'{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x_position}+{y_position-40}')
        self.root.title('Tienda de Mascotas')
        self.root.resizable(0, 0)
        self.root.config(bg='#082d44')

        # Creación del botón Comenzar
        self.botonComenzar = Label(
            text='Comenzar',
            bg='#082d44',
            font=('Helvetica', 48),
            fg='white',
            cursor='hand2',
            borderwidth=0,
            highlightthickness=0
        )
        self.botonComenzar.bind("<Button-1>",lambda event: self.comenzar())
        
        # Posicionamiento centrado del botón
        self.place_button_centered()

        self.root.mainloop()

    def place_button_centered(self):
        # Posiciona el botón en el centro de la ventana
        self.botonComenzar.place(
            height=self.BUTTON_HEIGHT,
            width=self.BUTTON_WIDTH,
            x=(self.WINDOW_WIDTH - self.BUTTON_WIDTH) // 2,
            y=(self.WINDOW_HEIGHT - self.BUTTON_HEIGHT) // 2
        )

    def comenzar(self):
        # Cierra la ventana actual y crea la segunda pantalla
        self.root.destroy()
        self.secondScreen = Second_Screen(self.x_position, self.y_position)

if __name__ == "__main__":
    # Llamada a la función 'run' solo si el script es ejecutado directamente
    Screen()