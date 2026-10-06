"""
settings.py
-----------
Central place for all constants used across the AquaClean project:
screen size, colors, fonts, gameplay tuning values, and file paths.

Keeping these in one file makes the game easy to tune without
hunting through gameplay code.
"""

import os

# ---------------------------------------------------------------------------
# BASE PATHS
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
DATA_DIR = os.path.join(BASE_DIR, "data")
HIGHSCORE_FILE = os.path.join(DATA_DIR, "highscore.txt")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.txt")

# ---------------------------------------------------------------------------
# SCREEN / DISPLAY
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60
GAME_TITLE = "AquaClean - Water Pollution Management & Awareness Game"

# Playable river area (leaves space at top for HUD and a bank border)
HUD_HEIGHT = 60
RIVER_TOP = HUD_HEIGHT + 10
RIVER_BOTTOM = SCREEN_HEIGHT - 20
RIVER_LEFT = 40
RIVER_RIGHT = SCREEN_WIDTH - 40

# ---------------------------------------------------------------------------
# COLORS (blue/green environmental theme)
# ---------------------------------------------------------------------------
COLOR_WATER_DARK = (20, 90, 150)
COLOR_WATER_LIGHT = (40, 130, 190)
COLOR_WATER_WAVE = (70, 160, 210)
COLOR_BANK = (86, 140, 70)
COLOR_BANK_DARK = (66, 110, 55)
COLOR_TREE = (40, 100, 45)
COLOR_ROCK = (120, 120, 120)

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (20, 20, 20)
COLOR_YELLOW = (250, 200, 40)
COLOR_ORANGE = (240, 140, 30)
COLOR_RED = (210, 60, 50)
COLOR_GREEN = (60, 170, 90)
COLOR_DARK_GREEN = (30, 110, 60)
COLOR_GRAY = (200, 200, 200)
COLOR_DARK_BLUE = (10, 40, 70)
COLOR_BUBBLE = (210, 240, 250)

BUTTON_COLOR = (255, 255, 255)
BUTTON_HOVER_COLOR = (220, 240, 255)
BUTTON_TEXT_COLOR = (15, 60, 90)
BUTTON_BORDER_COLOR = (20, 90, 150)

# ---------------------------------------------------------------------------
# FONT SIZES (uses default system font if no custom font file supplied)
# ---------------------------------------------------------------------------
FONT_NAME = None  # None = pygame default font
FONT_TITLE = 52
FONT_SUBTITLE = 22
FONT_LARGE = 36
FONT_MEDIUM = 26
FONT_SMALL = 20
FONT_HUD = 22

# ---------------------------------------------------------------------------
# GAMEPLAY TUNING
# ---------------------------------------------------------------------------
LEVEL_TIME_SECONDS = 60
PLAYER_SPEED = 4
PLAYER_SIZE = (60, 38)
FISH_SIZE = (42, 25)

# Adjustable boat speed settings (changeable from the in-game Settings screen)
PLAYER_SPEED_MIN = 2
PLAYER_SPEED_MAX = 8
PLAYER_SPEED_DEFAULT = 4
PLAYER_SPEED_STEP = 1

# Adjustable fish speed multiplier (applied on top of each level's base fish speed)
FISH_SPEED_MULT_MIN = 0.5
FISH_SPEED_MULT_MAX = 2.5
FISH_SPEED_MULT_DEFAULT = 1.0
FISH_SPEED_MULT_STEP = 0.25

# ---------------------------------------------------------------------------
# ADJUSTABLE SIZE SCALES (changeable from the in-game Settings screen)
# Each scale is a multiplier applied on top of the base sizes below.
# ---------------------------------------------------------------------------
BOAT_SCALE_MIN = 0.6
BOAT_SCALE_MAX = 1.8
BOAT_SCALE_DEFAULT = 1.0
BOAT_SCALE_STEP = 0.2

FISH_SCALE_MIN = 0.6
FISH_SCALE_MAX = 1.8
FISH_SCALE_DEFAULT = 1.0
FISH_SCALE_STEP = 0.2

OIL_SCALE_MIN = 0.6
OIL_SCALE_MAX = 2.0
OIL_SCALE_DEFAULT = 1.0
OIL_SCALE_STEP = 0.2

DIRT_SCALE_MIN = 0.6
DIRT_SCALE_MAX = 2.0
DIRT_SCALE_DEFAULT = 1.0
DIRT_SCALE_STEP = 0.2

ALGAE_SCALE_MIN = 0.6
ALGAE_SCALE_MAX = 2.0
ALGAE_SCALE_DEFAULT = 1.0
ALGAE_SCALE_STEP = 0.2

WATER_QUALITY_START = 50
WATER_QUALITY_MIN = 0
WATER_QUALITY_MAX = 100

# Pollution types: (score_change, water_quality_change, color, size)
POLLUTION_TYPES = {
    "bottle": {"score": 10, "quality": 5, "color": (180, 220, 230), "size": (28, 28)},
    "bag": {"score": 15, "quality": 7, "color": (230, 230, 150), "size": (30, 25)},
    "garbage": {"score": 20, "quality": 10, "color": (150, 110, 70), "size": (32, 27)},
    "oil": {"score": -15, "quality": -10, "color": (40, 40, 40), "size": (38, 27)},
}

FISH_HIT_SCORE_PENALTY = 20
FISH_HIT_QUALITY_PENALTY = 5

# Algae / water plant obstacles - block the boat's path (do not affect score directly)
ALGAE_BASE_SIZE = (46, 34)

# Level configuration: number of pollution items, number of fish, fish speed,
# algae obstacle count, and a background color scheme that gets more
# ominous / "dangerous" as difficulty rises.
LEVEL_CONFIG = {
    1: {
        "name": "Level 1 - Clean Start",
        "difficulty": "Easy",
        "pollution_count": 6,
        "oil_count": 1,
        "fish_count": 2,
        "fish_speed": 1.5,
        "spawn_interval_ms": 3000,
        "algae_count": 3,
        "water_color": (25, 110, 165),
        "water_color_dark": (18, 85, 135),
        "wave_color": (80, 175, 220),
        "bank_color": (86, 140, 70),
        "bank_color_dark": (66, 110, 55),
    },
    2: {
        "name": "Level 2 - Rising Pollution",
        "difficulty": "Medium",
        "pollution_count": 9,
        "oil_count": 3,
        "fish_count": 4,
        "fish_speed": 2.3,
        "spawn_interval_ms": 2200,
        "algae_count": 5,
        "water_color": (75, 115, 80),
        "water_color_dark": (55, 90, 60),
        "wave_color": (110, 160, 100),
        "bank_color": (110, 120, 60),
        "bank_color_dark": (85, 95, 45),
    },
    3: {
        "name": "Level 3 - Critical River",
        "difficulty": "Hard",
        "pollution_count": 13,
        "oil_count": 5,
        "fish_count": 6,
        "fish_speed": 3.0,
        "spawn_interval_ms": 1600,
        "algae_count": 7,
        "water_color": (95, 55, 45),
        "water_color_dark": (65, 35, 30),
        "wave_color": (140, 80, 60),
        "bank_color": (95, 80, 55),
        "bank_color_dark": (70, 58, 40),
    },
}

TOTAL_LEVELS = 3

# ---------------------------------------------------------------------------
# EDUCATIONAL TIPS (shown after each level)
# ---------------------------------------------------------------------------
EDUCATIONAL_TIPS = [
    "Do not throw plastic waste into rivers and lakes.",
    "Recycling and proper waste disposal can reduce water pollution.",
    "Oil and chemical spills can seriously damage aquatic ecosystems.",
    "Protecting aquatic life is an important part of water pollution management.",
    "Small individual actions like proper waste disposal add up to a big impact.",
]

# Rating messages based on final water quality / score performance
RATING_MESSAGES = {
    "Excellent": "Great job! Removing waste helps protect aquatic ecosystems.",
    "Good": "Well done! Your cleanup efforts are making a real difference.",
    "Moderate": "Good effort. More cleanup is needed to restore this river.",
    "Poor": "The river needs urgent help. Every piece of waste removed matters.",
}
