# Welcome to Spoodle!
Spoodle is a MMORPG, made for fun.

## Configuration
Spoodle's config file has the following options:
```json
{
    // This object is a dictionary of animations
    "animations": {
        // Key is the name of the animation
        "player": {
            // The filename of the spritesheet (game searches in assets/images/)
            "filename": "player.png",
            // The size of each frame in the sheet
            "size": [64, 64],
            // Coordinates to begin slicing at (top left)
            "starting_coords": [0, 0],
            // Padding between the sides of each frame
            "padding": 0,
            // The size to scale the new image to
            "scale_to": [64, 64],
            // Number of frames on each row
            "frames_per_row": 13,
            // Names of each row's animation from top to bottom
            "animation_names": [
                "spellcast_up",
                "spellcast_down"
            ],
            // Number of frames on each row, from top to bottom
            "frames_per_animation": [7, 7]
        }
    }
}
```
