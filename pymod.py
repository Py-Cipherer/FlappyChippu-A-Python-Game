import pygame
from pygame.locals import *
import sys

"""
def screensize(a,b):
    screen=pygame.display.set_mode(a,b)
    return screen

if _name_ == "_main_":
    screensize(a,b)
"""
# Define our square object and call super to
# give it all the properties and methods of pygame.sprite.Sprite
# Define the class for our square objects
class Square(pygame.sprite.Sprite):
	def __init__(self):
		super(Square, self).__init__()
		
		# Define the dimension of the surface
		# Here we are making squares of side 25px
		self.surf = pygame.Surface((25, 25))
		
		# Define the color of the surface using RGB color coding.
		self.surf.fill((0, 200, 255))
		self.rect = self.surf.get_rect()

class Circle(pygame.sprite.cir):
    def _init_(self):
        super(cir,self)._init_()
        self.surf = pygame.Surface((10,10))
        self.surf.fill((255,255,255))
        self.

# initialize pygame
pygame.init()

# Define the dimensions of screen object
screen = pygame.display.set_mode((800, 600))
player = Circle()

# instantiate all square objects
square1 = Square()
square2 = Square()
square3 = Square()
square4 = Square()

# Variable to keep our game loop running
gameOn = True

# Our game loop
while gameOn:
	# for loop through the event queue
	for event in pygame.event.get():
		
		# Check for KEYDOWN event
		if event.type == KEYDOWN:
                        if event.key
			
			# If the Backspace key has been pressed set
			# running to false to exit the main loop
			if event.key == K_BACKSPACE:
				gameOn = False
				
		# Check for QUIT event
		elif event.type == QUIT:
			gameOn = False

	# Define where the squares will appear on the screen
	# Use blit to draw them on the screen surface
	screen.blit(square1.surf, (40, 40))
	screen.blit(square2.surf, (40, 530))
	screen.blit(square3.surf, (730, 40))
	screen.blit(square4.surf, (730, 530))

	# Update the display using flip
	pygame.display.flip()
