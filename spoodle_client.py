#!/usr/bin/env python3
"""
spoodle_client.py
highwind

A pygame frontend for spoodle.
"""

import pygame
from itertools import count

RESOLUTION = 64
SCREEN_WIDTH = 12 * RESOLUTION
SCREEN_HEIGHT = 9 * RESOLUTION
FRAMERATE = 30 # fps
IMAGE_DIRECTORY = "assets/images/"
BACKGROUND_IMAGE = IMAGE_DIRECTORY + "background.png"


class GameObject(pygame.sprite.Sprite):
    """This class is intended to be subclassed, and 'image' should be defined.
    It will allow you to spawn instances of that image as a solid static object
    in the game at a specified location. The update method can also be overriden,
    in order to define behavior."""
    image = None

    def __init__(self, location, *groups):
        super(GameObject, self).__init__(groups)
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.animator = None

    def update(self, gamestate):
        """Updates the game object's state.

        Params:
            gamestate - an instance of the game"""
        if self.animator:
            self.image = self.animator.update(gamestate.time_delta)


class Player(GameObject):
    """Contains all the logic for controlling the player."""
    image = pygame.Surface((RESOLUTION, RESOLUTION))


class Animator():
    """Keeps track of a collection of images, returning the appropriate image
    for a given animation.

    Params:
        animations - a dictionary containing string keys, which are the names
            of the animations, and lists of surface objects as the values, which
            are the animations themselves
        framerate - number of frames per second"""

    def __init__(self, animations, framerate = 13):
        if any(map(lambda x: len(x) == 0, animations.values())):
            raise ValueError("all animations must have at least one frame")

        self.animations = animations
        self.playing = None
        self.current_frame = 0
        self.time_transpired = 0
        self.miliseconds_per_frame = 1000 // framerate

    def play(self, animation):
        """Plays an animation.

        Params:
            animation - the string name of the animation to play"""
        anim_names = self.animations.keys()
        if animation not in anim_names:
            raise ValueError("animation must be one of the animation names")
        self.current_frame = self.time_transpired = 0
        self.playing = self.animations[animation]

    def update(self, delta_time):
        """Get the appropriate frame for the currently playing animation.

        Params:
            delta_time - the time that has transpired in miliseconds

        Returns: the surface with the appropriate image, or None if no animation
            is playing"""
        if not self.playing:
            return None

        self.time_transpired += delta_time
        if self.time_transpired >= self.miliseconds_per_frame:
            frames_advanced = self.time_transpired // self.miliseconds_per_frame
            self.time_transpired %= self.miliseconds_per_frame # roll over extra time
            self.current_frame = (self.current_frame + frames_advanced) % len(self.playing)

        return self.playing[self.current_frame]


class Game(object):
    """An instance of the game.

    Params:
        screen - a pygame Surface to display the game on"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.time_delta = 0
        self.playing = True
        self.game_objects = pygame.sprite.Group()
        self.background = pygame.image.load(BACKGROUND_IMAGE).convert_alpha()

    def main(self):
        while self.playing:
            self.time_delta = self.clock.tick(FRAMERATE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playing = False

            # update all the game objects
            self.game_objects.update(self)
            # redraw the game to the screen
            self.screen.blit(self.background, (0, 0))
            self.game_objects.draw(self.screen)
            pygame.display.flip()


def slice_sprites(filename, size = (RESOLUTION, RESOLUTION), resize_to = None,
        starting_coords = (0, 0), padding = 0):
    """Divides a spritesheet into an array of images.

    Params:
        filename - the spritesheet
        size - tuple representing the size of the sprite to be sliced
        resize_to - a tuple representing the new dimensions to scale the image to
        starting_coords - tuple representing the coordinates to begin slicing from
        padding - an integer representing the number of pixels between each sprite

    Returns: a list of surfaces"""
    images = []
    spritesheet = pygame.image.load(filename).convert_alpha()
    spritesheet_rect = spritesheet.get_rect()
    x_coord, y_coord = starting_coords
    width, height = size
    for row in range(y_coord, spritesheet_rect.height, height + padding):
        for col in range(x_coord, spritesheet_rect.width, width + padding):
            spritesheet.set_clip(pygame.rect.Rect(col, row, height, width))
            image = spritesheet.subsurface(spritesheet.get_clip())
            if resize_to:
                image = pygame.transform.scale(image, resize_to)
            images.append(image)
    return images

def name_raw_sliced_sprites(images, names, width = 1, spritecounts = None):
    """Formats the raw images returned by slice_sprites so that they can be
    passed directly to the animator.

    Params:
        images - the list of surface objects
        names - names for each animation
        width - the number of frames per row in the processed spritesheet
        spritecounts - an array of integers representing the number of sprites
            present in each row of the spritesheet

        For example, if I had a spritesheet with two rows, and the first row had
            two frames, while the second row had five, I'd want
            spritecounts = [2, 5], width = 5

    Returns: a dict mapping names to their frames."""
    if len(names) > len(images) // width:
        raise ValueError("Cannot have more names than rows of images.")
    if spritecounts == None:
        spritecounts = [width] * len(names)
    else:
        if all(map(lambda x: x > width, spritecounts)):
            raise ValueError("spritecounts cannot exceed the width of a row")
        elif len(spritecounts) < len(names):
            raise ValueError("Cannot have fewer spritecount values than names")

    animations = {}
    for i, name in zip(count(), names):
        animations[name] = images[i*width:(i*width) + spritecounts[i]]
    return animations


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    Game(screen).main()
