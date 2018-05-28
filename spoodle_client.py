#!/usr/bin/env python3
"""
spoodle_client.py
highwind

A pygame frontend for spoodle.
"""

import pygame

RESOLUTION = 64
SCREEN_WIDTH = 12 * RESOLUTION
SCREEN_HEIGHT = 9 * RESOLUTION
FRAMERATE = 30 # fps
IMAGE_DIRECTORY = "assets/images/"
BACKGROUND_IMAGE = IMAGE_DIRECTORY + "background.png"


class Player(pygame.sprite.Sprite):
    """Contains all the logic for controlling the player."""
    def __init__(self, location, *groups):
        super(StaticGameObject, self).__init__(groups)
        self.rect = pygame.rect.Rect(location, self.image.get_size())


class StaticGameObject(pygame.sprite.Sprite):
    """A game object that does not move.

    This class is intended to be subclassed, and 'image' should be defined.
    It will allow you to spawn instances of that image as a solid static object
    in the game at a specified location."""
    image = None

    def __init__(self, location, *groups):
        super(StaticGameObject, self).__init__(groups)
        self.rect = pygame.rect.Rect(location, self.image.get_size())


class Game(object):
    """An instance of the game.

    Params:
        screen - a pygame Surface to display the game on"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.playing = True
        self.game_objects = pygame.sprite.Group()
        self.background = pygame.image.load(BACKGROUND_IMAGE)

    def main(self):
        while self.playing:
            self.clock.tick(FRAMERATE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playing = False

            # update all the game objects
            self.game_objects.update()
            # redraw the game to the screen
            self.screen.blit(self.background, (0, 0))
            self.game_objects.draw(self.screen)
            pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    Game(screen).main()
