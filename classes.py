from OpenGL.GL import * 
from OpenGL.GLUT import * 
from OpenGL.GLU import * 

class entity:
    
    def __init__(self, x, y, width, height, speed):
        
        self.center = [x, y]
        self.size   = [width, height]
        self.update_params()
        
        ## Entity transformation ##
        self.move_left = False
        self.move_right = False
        self.jump = False
        self.in_air = False

        self.speed = speed
        self.vel_y = 0
        
    def update_params(self):
        self.right = self.center[0] + self.size[0]/2
        self.left  = self.center[0] - self.size[0]/2
        self.top   = self.center[1] + self.size[1]/2
        self.bot   = self.center[1] - self.size[1]/2
        
    def draw(self):
        
        glLoadIdentity()

        glBegin(GL_QUADS)
        glVertex(self.left, self.bot, 0)
        glVertex(self.left, self.top, 0)
        glVertex(self.right, self.top, 0)
        glVertex(self.right, self.bot, 0)
        
        glEnd()
    
    def move(self):
        # Location
        pos_x, pos_y = self.center
        
        # Movement variables
        dx = 0
        dy = 0
        
        # Checking Flags
        if self.move_left:
            dx = - self.speed
        if self.move_right:
            dx = self.speed
            
        if self.jump and not self.in_air:
            self.jump = False
            self.vel_y = 30
            self.in_air = True
            
        
        # Gravity Physics
        self.vel_y = self.vel_y - GRAVITY
        dy += self.vel_y
        
        if pos_y + dy < 200:
            dy = pos_y - 200
            self.in_air = False
            
        # Changing the center on X Axis
        pos_x += dx
        
        # Changing the center on Y Axis
        pos_y += dy

        
        # Update Attributes
        self.center = pos_x, pos_y
        self.update_params()

class ground:
    def __init__(self, x, y, width):
        self.center = (x,y)
        self.size = width

        self.left = x - width/2
        self.right = x + width/2
        
    def draw(self):
        glLoadIdentity()
        glBegin(GL_LINES)
        glVertex(self.left, self.center[1])
        glVertex(self.right, self.center[1])
        glEnd()
        

        
if __name__ == "__main__":
    
    ### Constants ###
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = int(WINDOW_WIDTH * .6)
    INTERVAL = 10
    GRAVITY = 2.5

    
    ### Variables ###

    ### Initialization ###
    def init():
        glClearColor(0,0,0,0)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, 0, 1)

        glMatrixMode(GL_MODELVIEW)

    ### Set Player ###
    player = entity(200, 200, 50, 50, 10)
    ### Display ###
    def display():
        # Resetting Variables
        glClear(GL_COLOR_BUFFER_BIT)
        
        glLoadIdentity()
        glColor(0,1,0)
        player.draw()
        player.move()
        ground_list = []
        ground_list.append(ground(100, 100, 50))
        ground_list.append(ground(100, 170, 500))
        for item in ground_list:
            item.draw()
        
        glutSwapBuffers()

    ### Callback ###
    def keyUp(key, x, y):
        
        if key == b'a':
            player.move_left = False
            
        if key == b'd':
            player.move_right = False
            
    def keyDown(key, x, y):
        if key == b'q':
            sys.exit()
        if key == b'a':
            player.move_left = True
            
        if key == b'd':
            player.move_right = True

        if key == b'w':
            player.jump = True
    def mouse_callback(x, y):
        pass 
    
    def game_timer(v):
        display()
        glutTimerFunc(INTERVAL, game_timer, 1)
        

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowPosition(100,100)
    glutInitWindowSize(WINDOW_WIDTH,WINDOW_HEIGHT)
    glutCreateWindow(b"Ball bat game")
    glutDisplayFunc(display)
    glutKeyboardFunc(keyDown)
    glutKeyboardUpFunc(keyUp)
    # glutSpecialFunc(keyboard2_callback)
    glutPassiveMotionFunc(mouse_callback)
    glutTimerFunc(INTERVAL, game_timer, 1)
    init()
    glutMainLoop()