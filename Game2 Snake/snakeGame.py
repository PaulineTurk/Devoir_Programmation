from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from random import randint
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button 
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color, Line, Ellipse
from kivy.core.window import Window




PLAYER_SIZE = 60    # taille pour l'affichage
SIZE = 12            # nombre de cases sur une ligne
# On impose un plateau carré 
WINDOW_HEIGHT = SIZE*PLAYER_SIZE
WINDOW_WIDTH = SIZE*PLAYER_SIZE


class Fruit(Widget):
    """
    Classe associée au fruit mangé par le serpent 
    """
    def move(self, new_pos):
        """
        Déplace le fruit vers la position donnée en entrée 
        """
        self.pos = new_pos


class SnakeTail(Widget):
    """
    Classe associée au corps du serpent 
    """
    
    def move(self, new_pos):
        """
        Déplace le corps du serpent  vers la position donnée en entrée 
        """
        self.pos = new_pos


class SnakeHead(Widget):
    """
    Classe associée à la tête du serpent 
    """
    
    orientation = (PLAYER_SIZE, 0)

    def reset_pos(self):
        """
        Initialisation de la position du serpent au milieu du plateau de jeu
        """
        self.pos = [int(WINDOW_WIDTH / 2 - (WINDOW_WIDTH / 2 % PLAYER_SIZE)),
                    int(WINDOW_HEIGHT / 2 - (WINDOW_HEIGHT / 2 % PLAYER_SIZE))]
        self.orientation = (PLAYER_SIZE, 0)

    def move(self):
        """
        Fonction qui déplace la tête du serpent selon l'orientation
        """
        self.pos = Vector(*self.orientation) + self.pos


class smartGrid:
    """
    Classe associé au plateau de jeu 
    """

    def __init__(self):
        """
        Grille 2D utilisé pour voir si le serpent rentre en collision 
        avec lui même ou avec un fruit. 
        
        """
        self.grid = [[False for i in range(WINDOW_HEIGHT)]
                     for j in range(WINDOW_WIDTH)]

    def __getitem__(self, coords):
        """
        Récupérer une valeur dans la grille (True ou False)
        """
        return self.grid[coords[0]][coords[1]]

    def __setitem__(self, coords, value):
        """
        Modifier une valeur dans la grille (en True ou False)
        """
        self.grid[coords[0]][coords[1]] = value


class SnakeGame(Widget):
    """
    Classe principale qui fait appel aux autres classes pour définir les règles du jeu 
    """

    # Initialisation des objets 
    head = ObjectProperty(None)
    fruit = ObjectProperty(None)
    score = NumericProperty(0)
    speed_index = NumericProperty(0)
    player_size = NumericProperty(PLAYER_SIZE)
    game_over = StringProperty("")

    def __init__(self):
        super(SnakeGame, self).__init__()

        Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        Window.clearcolor = (1, 1, 1, 1)
        self._keyboard = Window.request_keyboard(None, self)
        if not self._keyboard:
            return
        self._keyboard.bind(on_key_down=self.on_keyboard_down)


        if PLAYER_SIZE < 3:
            raise ValueError("Player size should be at least 3 px")

        if WINDOW_HEIGHT < 3 * PLAYER_SIZE or WINDOW_WIDTH < 3 * PLAYER_SIZE:
            raise ValueError("Window size must be at least 3 times larger than player size")
        self.count_press_spacebar = 0  # pour le compte de touch space appuyé pause/retour de pause
        self.count_speed = 0 # pour suivre la vitesse de refresh
        self.game_speed = 1
        self.start_interval()
        self.tail = []
        with self.canvas:
            Color(0,0,0)
            for i in range(SIZE+1):
                Line(points=(0, PLAYER_SIZE * i, WINDOW_WIDTH, PLAYER_SIZE * i))    # tracer lignes horizontales sur plateau 
                Line(points=(PLAYER_SIZE*i, 0, PLAYER_SIZE*i, WINDOW_HEIGHT))         # tracer lignes verticales sur plateau
        
        self.restart_game()
        self.speed_index = 0
  
    def start_interval(self, *args):
        """
        Commencer le chronomètre et indiquer l'intervalle de temps du jeu 
        """
        self.timer = Clock.schedule_interval(self.refresh, self.game_speed)


    def stop_interval(self, *args):
        """
        Arrêter le chronomètre 
        """
        self.timer.cancel()

    def restart_game(self):
        """
        Réinitialisation du jeu
        """
        # de la grille
        self.occupied = smartGrid()
        # du comptage d'appuie sur la touche espace
        self.count_press_spacebar = 0
        # du compteur de vitesse
        self.count_speed = 0
        # du score
        self.score = 0

        # de la vitesse de jeu
        self.game_speed = 1
        self.speed_index = 0
        self.stop_interval()      
        self.start_interval()

        # de la position de la tete du serpent
        self.head.reset_pos()
        # de la taille du serpent
        for block in self.tail:
            self.remove_widget(block)
        self.tail = []

        # de la position du fruit
        self.spawn_fruit()

        

    def refresh(self, dt):
        """
        Rafraichir la grille à chaque étape de temps :
            - Recommencer la partie ( si serpent sort de la grille ou si tete du serpent percute son corps )
            - Déplacer la tête et le corps lorsque le mouvement est autorisé 
            - Augmente la taille du serpent si il mange un fruit 
            - modifie la vitesse lorsque la taille du serpent > 5 
        """
        
        print("self.game_speed :", self.game_speed)
        # si le serpent sort de la grille, recommencer une nouvelle partie
        if not (0 <= self.head.pos[0] < WINDOW_WIDTH) or not (0 <= self.head.pos[1] < WINDOW_HEIGHT):
            self.restart_game()
            return

        # si la tete du serpent percute son corps, recommencer une nouvelle partie
        if self.occupied[self.head.pos] is True:
            self.restart_game()
            return

        # bouger le serpent
        # Situation de départ lorsqu'il n'y a que le head 
        if len(self.tail) == 1 :
            self.occupied[self.tail[-1].pos] = False
            self.tail[-1].move(self.head.pos)
        
        # Situation lorsque le snake est au moins de taille 2 (1 (head) + 1 (corps))
        elif len(self.tail) > 1 : 
            self.occupied[self.tail[-1].pos] = False # la dernière pièce se déplace donc n'est plus occupée 
            self.tail[-1].move(self.tail[-2].pos)

            for i in range(2, len(self.tail)): 
                self.tail[-i].move(new_pos=(self.tail[-(i + 1)].pos))

            self.tail[0].move(new_pos=self.head.pos)
            self.occupied[self.tail[0].pos] = True

        #bouger la tête 
        self.head.move()


        # si le fruit a été trouvé
        if self.head.pos == self.fruit.pos:
            # augementer le score de 10 pts
            self.score += 10
            # allonger le corps du serpent 
            self.tail.append(SnakeTail(pos=self.head.pos, size=self.head.size))
            self.add_widget(self.tail[-1])

            # vérifier s'il fuat changer la vitesse
            if len(self.tail) % 5 == 0:
                self.game_speed -= 0.05
                self.speed_index += 1
                self.timer.cancel()
                self.timer = Clock.schedule_interval(self.refresh, self.game_speed)
            # et générer un nouveau fruit
            self.spawn_fruit()


    def spawn_fruit(self):
        """
        Cherche une position pour le nouveau fruit et place le fruit. 
        """
        roll = self.fruit.pos
        found = False
        while not found:
            roll = [PLAYER_SIZE *randint(0, int(WINDOW_WIDTH / PLAYER_SIZE) - 1),
                    PLAYER_SIZE *randint(0, int(WINDOW_HEIGHT / PLAYER_SIZE) - 1)]
            if self.occupied[roll] is True or roll == self.head.pos:
                continue
            found = True
        self.fruit.move(roll)



    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """
        Gère les touches haut, bas, droite, gauche pour avancer et « Space » pour mettre en pause. 
        """
        direction = {'left': (-PLAYER_SIZE, 0),
                          'right': (PLAYER_SIZE, 0),
                          'up': (0, PLAYER_SIZE),
                          'down': (0, -PLAYER_SIZE)}
        if keycode[1] in direction:
            self.head.orientation = direction[keycode[1]]
        elif keycode[1] == 'spacebar':
            self.count_press_spacebar += 1
            print(self.count_press_spacebar)
            if self.count_press_spacebar%2 == 1:
                self.stop_interval()
            else : 
                self.start_interval()
        

class snakeApp(App):
    """
    Classe qui lance le jeu 
    """
    
    def build(self):
        game = SnakeGame()
        return game




if __name__ == '__main__':
    snakeApp().run()
