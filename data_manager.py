"""
data_manager.py
----------------
Handles everything related to files on disk:
- Safely loading images (falls back to None if missing -> caller draws a shape)
- Safely loading sounds (falls back to None if missing -> caller skips playing)
- Loading and saving the high score file

All functions here are defensive: a missing/broken asset must NEVER crash
the game. This is a core requirement of the project.
"""

import os
import pygame
from settings import (
    HIGHSCORE_FILE, SETTINGS_FILE, DATA_DIR,
    PLAYER_SPEED_DEFAULT, FISH_SPEED_MULT_DEFAULT,
    BOAT_SCALE_DEFAULT, FISH_SCALE_DEFAULT, OIL_SCALE_DEFAULT,
    DIRT_SCALE_DEFAULT, ALGAE_SCALE_DEFAULT,
)


def safe_load_image(path, size=None, colorkey=None):
    """
    Try to load an image from disk.
    Returns a pygame.Surface if successful, or None if the file
    does not exist or fails to load. Callers must handle the
    None case by drawing a placeholder shape instead.
    """
    if not path or not os.path.isfile(path):
        return None
    try:
        image = pygame.image.load(path)
        image = image.convert_alpha() if pygame.display.get_surface() else image
        if size:
            image = pygame.transform.smoothscale(image, size)
        if colorkey is not None:
            image.set_colorkey(colorkey)
        return image
    except (pygame.error, OSError):
        # Corrupt or unreadable file -> treat as missing
        return None


def safe_load_sound(path):
    """
    Try to load a sound effect from disk.
    Returns a pygame.mixer.Sound if successful, or None otherwise.
    Callers must check for None before calling .play().
    """
    if not path or not os.path.isfile(path):
        return None
    try:
        return pygame.mixer.Sound(path)
    except (pygame.error, OSError):
        return None


def safe_play_sound(sound, volume=1.0):
    """Play a sound only if it was loaded successfully."""
    if sound is not None:
        try:
            sound.set_volume(volume)
            sound.play()
        except pygame.error:
            pass


def safe_load_music(path, volume=0.4):
    """
    Try to load and start looping background music.
    Silently does nothing if the file is missing or playback fails.
    """
    if not path or not os.path.isfile(path):
        return False
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        return True
    except pygame.error:
        return False


def ensure_data_folder():
    """Create the data/ folder if it does not already exist."""
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def load_highscore():
    """
    Read the high score from data/highscore.txt.
    If the file or folder does not exist, create it with a default of 0.
    Any corrupt/unreadable content is treated as a high score of 0.
    """
    ensure_data_folder()
    if not os.path.isfile(HIGHSCORE_FILE):
        save_highscore(0)
        return 0
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            content = f.read().strip()
            return int(content) if content else 0
    except (ValueError, OSError):
        return 0


def save_highscore(score):
    """Write the given score to data/highscore.txt, creating the folder if needed."""
    ensure_data_folder()
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(int(score)))
    except OSError:
        # If saving fails (e.g. read-only filesystem), fail silently.
        pass


def update_highscore_if_needed(score):
    """Update the saved high score only if the new score beats it. Returns the current high score."""
    current = load_highscore()
    if score > current:
        save_highscore(score)
        return score
    return current


def load_player_speed():
    """Read the saved boat speed setting (first value)."""
    return load_settings()["player_speed"]


def load_fish_speed_multiplier():
    """Read the saved fish speed multiplier setting."""
    return load_settings()["fish_speed_mult"]


# Default settings, in the fixed order they are written to the file.
_SETTINGS_KEYS = [
    ("player_speed", PLAYER_SPEED_DEFAULT, int),
    ("fish_speed_mult", FISH_SPEED_MULT_DEFAULT, float),
    ("boat_scale", BOAT_SCALE_DEFAULT, float),
    ("fish_scale", FISH_SCALE_DEFAULT, float),
    ("oil_scale", OIL_SCALE_DEFAULT, float),
    ("dirt_scale", DIRT_SCALE_DEFAULT, float),
    ("algae_scale", ALGAE_SCALE_DEFAULT, float),
]


def _default_settings_dict():
    return {key: default for key, default, _ in _SETTINGS_KEYS}


def load_settings():
    """
    Read all adjustable settings (boat/fish speed and every size scale)
    from data/settings.txt as a dictionary. One value per line, in the
    fixed order defined by _SETTINGS_KEYS. Missing or corrupt lines fall
    back to their default value individually, so an older settings file
    (from before a new option was added) still loads safely.
    """
    ensure_data_folder()
    defaults = _default_settings_dict()
    if not os.path.isfile(SETTINGS_FILE):
        save_settings_dict(defaults)
        return defaults

    try:
        with open(SETTINGS_FILE, "r") as f:
            lines = [line.strip() for line in f.readlines()]
    except OSError:
        return defaults

    result = {}
    for i, (key, default, cast) in enumerate(_SETTINGS_KEYS):
        try:
            result[key] = cast(lines[i]) if i < len(lines) and lines[i] != "" else default
        except ValueError:
            result[key] = default
    return result


def save_settings_dict(settings_dict):
    """Write a full settings dictionary to data/settings.txt, one value per line."""
    ensure_data_folder()
    try:
        with open(SETTINGS_FILE, "w") as f:
            lines = [str(settings_dict.get(key, default)) for key, default, _ in _SETTINGS_KEYS]
            f.write("\n".join(lines))
    except OSError:
        pass


def save_setting(key, value):
    """Update a single setting by key, keeping every other saved value unchanged."""
    current = load_settings()
    current[key] = value
    save_settings_dict(current)


# Kept for backward compatibility with any older code that saved just two values.
def save_settings(player_speed, fish_mult):
    save_setting("player_speed", player_speed)
    save_setting("fish_speed_mult", fish_mult)
