#!/usr/bin/env python3
"""
spoodle_client.py
highwind

A pygame frontend for spoodle.
"""

import pygame, json
from itertools import count
from enum import Enum

RESOLUTION = 64
SCREEN_WIDTH = 12 * RESOLUTION
SCREEN_HEIGHT = 9 * RESOLUTION
FRAMERATE = 30 # fps
CONFIG_FILE = "assets/config.json"
IMAGE_DIRECTORY = "assets/images/"
SPRITESHEET_DIRECTORY = "assets/spritesheets/"
BACKGROUND_IMAGE = IMAGE_DIRECTORY + "background.png"


class Directions(Enum):
    EAST = 0
    NORTH = 1
    WEST = 2
    SOUTH = 3
    NORTHEAST = 4
    NORTHWEST = 5
    SOUTHWEST = 6
    SOURTHEAST = 7


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

    def set_animator(self, anim):
        """Sets anim as the game object's animator."""
        self.animator = anim

    def update(self, gamestate):
        """Updates the game object's state.

        Params:
            gamestate - an instance of the game"""
        if self.animator and self.animator.playing:
            self.image = self.animator.update(gamestate.time_delta)


class Player(GameObject):
    """Contains all the logic for controlling the player."""
    image = pygame.Surface((RESOLUTION, RESOLUTION))

    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self.speed = 250
        self.facing = Directions.SOUTH

    def update(self, gamestate):
        """Moves the player around.

        Params:
            gamestate - an instance of Game"""
        super(Player, self).update(gamestate)
        keys_pressed = pygame.key.get_pressed()
        movement_delta = (self.speed * gamestate.time_delta) // 1000
        if keys_pressed[pygame.K_a]:
            self.rect.x -= movement_delta
            self.facing = Directions.WEST
            self.animator.play("walk_left")
        if keys_pressed[pygame.K_d]:
            self.rect.x += movement_delta
            self.facing = Directions.EAST
            self.animator.play("walk_right")
        if keys_pressed[pygame.K_w]:
            self.rect.y -= movement_delta
            self.facing = Directions.NORTH
            self.animator.play("walk_up")
        if keys_pressed[pygame.K_s]:
            self.rect.y += movement_delta
            self.facing = Directions.SOUTH
            self.animator.play("walk_down")


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

        # the dictionary of frames for each animation name
        self.animations = animations
        # the name of the animation currently playing
        self.current_animation = None
        # the list of frames for the currently playing animation
        self.playing = None
        # index of the frame in the playing animation
        self.current_frame = 0
        # time since the frame changed (in miliseconds)
        self.time_transpired = 0
        self.miliseconds_per_frame = 1000 // framerate

    def play(self, animation):
        """Plays an animation.

        Params:
            animation - the string name of the animation to play, if None, it
                stops playing an animation"""

        if animation is None:
            self.playing = self.current_animation = None
            return
        elif animation not in self.animations.keys():
            raise ValueError("animation must be one of the animation names")

        # set the animation only if it's not the one already playing
        if animation is not self.current_animation:
            self.current_animation = animation
            self.playing = self.animations[animation]
            self.current_frame = self.time_transpired = 0

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
        self.config = json.loads(open(CONFIG_FILE, "r").read())
        self.player = None

    def load_animation_from_config(self, name):
        """Uses the animations configuration to load and parse a spritesheet.

        Params:
            name - the name of the animation configuration

        Returns: a dictionary that can be used to instantiate a new Animator."""

        if name not in self.config["animations"].keys():
            raise ValueError("Must provide the name of an existing animation configuration")

        anim_config = self.config["animations"][name]
        sprites = slice_sprites(
            SPRITESHEET_DIRECTORY + anim_config["filename"],
            size = anim_config["size"],
            resize_to = anim_config["scale_to"],
            starting_coords = anim_config["starting_coords"],
            padding = anim_config["padding"]
        )
        return name_raw_sliced_sprites(
            sprites,
            anim_config["animation_names"],
            width = anim_config["frames_per_row"],
            spritecounts = anim_config["frames_per_animation"]
        )

    def main(self):
        # Spawn the player at 150, 150
        self.player = Player((150, 150), self.game_objects)
        self.player.set_animator(Animator(self.load_animation_from_config("player")))
        self.player.animator.play("walk_left")
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
