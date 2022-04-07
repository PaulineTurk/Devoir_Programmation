from random import choice
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color
from kivy.uix.image import Image
from kivy.core.window import Window


SIZE = 10
GRID = []


class MyLayout(BoxLayout): 

    def random_grid(self):
        """
        Donne aléatoirement une valeur 0/1 à chaque case d'une grille carrée 
        de taille SIZE.
        Un bouton "Restart" lui est associé pour commencer une nouvelle partie.
        """
        global GRID, SIZE
        GRID = [[choice([0, 1]) for x in range(SIZE)] for y in range(SIZE)]
        self.mywidge.color_canvas()



class MyWidget(Widget): 

    def __init__(self, **kwargs):
        super(MyWidget, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(None, self)
        if not self._keyboard:
            return
        self._keyboard.bind(on_key_down=self.on_keyboard_down)
        Window.size = (800, 700)

    def color_canvas(self):   
        """
        Crée une grille à partir de GRID.
        Donne aux cases à valeur 1 la couleur noire.
        Donne aux cases à valeur 0 la couleur blanche.
        Place notre avatar en haut à gauche de la grille.
        """
        global GRID, SIZE
        cellheight = self.height//SIZE
        cellwidth = cellheight

        with self.canvas:
            for line in range(SIZE):
                for column in range(SIZE):
                    if GRID[line][column] == 1:
                        Color(0, 0, 0)
                    else:
                        Color(1, 1, 1)
                    Rectangle(pos=(cellwidth * line, cellheight * column), size=(cellwidth, cellheight))

            self.img = Image(source="pacman.png", pos=(0, cellheight * (SIZE - 1)), size=(cellwidth, cellheight))
            self.grid = GRID


    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """
        Détermine le mode de déplacement de notre avatar.
        S'il est sur une case blanche, il se déplace selon les fléches directionnelles.
        S'il est sur une case noire, il se déplace à l'opposé des flèches directionnelles.
        Empeche le joueur de sortir du plateau.
        """
        global SIZE
        cellheight = self.height//SIZE
        cellwidth = cellheight

        direction_blanc = {'left': (- cellwidth, 0),
                    'right': (cellwidth, 0),
                    'up': (0, cellheight),
                    'down': (0, - cellheight)}

        direction_noir = {'left': (cellwidth, 0),
                    'right': (- cellwidth, 0),
                    'up': (0, - cellheight),
                    'down': (0, cellheight)}

        if self.img.x//cellwidth in range(0, SIZE) and self.img.y//cellheight in range(0, SIZE):
            if self.grid[self.img.x//cellheight][self.img.y//cellwidth] == 1:
                direction = direction_noir
            else:
                direction = direction_blanc

            if keycode[1] in direction:
                if (self.img.x + direction[keycode[1]][0]) // cellwidth in range(0, SIZE) \
                        and (self.img.y + direction[keycode[1]][1]) // cellheight in range(0, SIZE):
                    self.img.x += direction[keycode[1]][0]
                    self.img.y += direction[keycode[1]][1]
                else:
                    print('Vous allez sortir du plateau')
            else:
                return False
            return True
        else:
            print("Sorti du plateau !")
        
 
class Game1App(App):       
    def build(self):
        self.mL = MyLayout()
        return self.mL



if __name__ == '__main__':
    Game1App().run()
    


