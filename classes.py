from OpenGL.GL import * 
from OpenGL.GLUT import * 
from OpenGL.GLU import * 

class character():
    def __init__(self, x, y, width, height):
        self.center = (x, y)
        self.size   = (width, height)
        
        self.right = x + width/2
        self.left  = x - width/2
        self.top   = y + height/2
        self.bot   = y - height/2

    def draw(self):
        glLoadIdentity()

        glBegin(GL_QUADS)
        glVertex(self.left, self.bot, 0)
        glVertex(self.left, self.top, 0)
        glVertex(self.right, self.top, 0)
        glVertex(self.right, self.bot, 0)
        glEnd()


if __name__ == "__main__":
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = int(WINDOW_WIDTH * .6)
    INTERVAL = 5

    def init():
        glClearColor(0,0,0,0)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, 0, 1)

        glMatrixMode(GL_MODELVIEW)

    def display():
        glClear(GL_COLOR_BUFFER_BIT)
        
        glLoadIdentity()
        glColor(0,1,0)
        ped = character(200, 200, 100, 100)
        ped.draw()
        
        glutSwapBuffers()

    def game_timer(v):
        display()
        glutTimerFunc(INTERVAL, game_timer, 1)
        
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowPosition(100,100)
    glutInitWindowSize(WINDOW_WIDTH,WINDOW_HEIGHT)
    glutCreateWindow(b"Ball bat game")
    glutDisplayFunc(display)
    # glutKeyboardFunc(keyboard_callback)
    # glutSpecialFunc(keyboard2_callback)
    # glutPassiveMotionFunc(mouse_callback)
    glutTimerFunc(INTERVAL, game_timer, 1)
    init()
    glutMainLoop()