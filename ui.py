"""
ui.py
-----
Reusable user-interface building blocks: buttons, text drawing helpers,
the HUD (score/quality/time bar), and the water-quality meter.

Keeping UI code separate from gameplay code keeps each file focused
and easy to explain to a teacher.
"""

import pygame
from settings import (
    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, BUTTON_BORDER_COLOR,
    COLOR_WHITE, COLOR_BLACK, COLOR_RED, COLOR_YELLOW, COLOR_GREEN,
    COLOR_DARK_BLUE, FONT_MEDIUM, FONT_HUD, FONT_NAME,
    WATER_QUALITY_MIN, WATER_QUALITY_MAX,
)

# Cache fonts so we don't recreate them every frame
_font_cache = {}


def get_font(size, bold=False):
    """Return a cached pygame Font object of the requested size."""
    key = (size, bold)
    if key not in _font_cache:
        font = pygame.font.SysFont(FONT_NAME or "arial", size, bold=bold)
        _font_cache[key] = font
    return _font_cache[key]


def draw_text(surface, text, size, color, center=None, topleft=None, bold=False):
    """Render text and blit it either centered at `center` or anchored at `topleft`."""
    font = get_font(size, bold=bold)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = center
    elif topleft:
        rect.topleft = topleft
    surface.blit(rendered, rect)
    return rect


class Button:
    """
    A simple rounded rectangle button with hover highlighting.
    Usage:
        btn = Button("START GAME", (450, 300), (240, 55))
        btn.draw(screen)
        if btn.is_clicked(event):
            ...
    """

    def __init__(self, text, center, size=(240, 55), font_size=FONT_MEDIUM):
        self.text = text
        self.size = size
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center
        self.font_size = font_size
        self.hovered = False

    def update_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        pygame.draw.rect(surface, BUTTON_BORDER_COLOR, self.rect, width=2, border_radius=14)
        draw_text(surface, self.text, self.font_size, BUTTON_TEXT_COLOR, center=self.rect.center, bold=True)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


def draw_water_quality_meter(surface, quality, rect):
    """
    Draw a horizontal meter bar going from red (0%) through yellow (50%)
    to green (100%), with a marker showing the current value.
    `rect` is a pygame.Rect describing where to draw the meter.
    """
    quality = max(WATER_QUALITY_MIN, min(WATER_QUALITY_MAX, quality))

    # Background track
    pygame.draw.rect(surface, (230, 230, 230), rect, border_radius=8)

    # Filled portion, colored based on the value
    fill_width = int(rect.width * (quality / WATER_QUALITY_MAX))
    fill_rect = pygame.Rect(rect.left, rect.top, fill_width, rect.height)

    if quality < 40:
        fill_color = COLOR_RED
    elif quality < 70:
        fill_color = COLOR_YELLOW
    else:
        fill_color = COLOR_GREEN

    if fill_width > 0:
        pygame.draw.rect(surface, fill_color, fill_rect, border_radius=8)

    pygame.draw.rect(surface, COLOR_BLACK, rect, width=2, border_radius=8)


def draw_hud(surface, score, quality, time_left, high_score, screen_width, hud_height):
    """Draw the top HUD bar showing score, water quality meter, and time remaining."""
    hud_rect = pygame.Rect(0, 0, screen_width, hud_height)
    pygame.draw.rect(surface, COLOR_DARK_BLUE, hud_rect)
    pygame.draw.line(surface, COLOR_WHITE, (0, hud_height), (screen_width, hud_height), 2)

    # Score (left)
    draw_text(surface, f"SCORE: {max(score, 0):04d}", FONT_HUD, COLOR_WHITE, topleft=(16, 18), bold=True)

    # High score (small, under score corner) - shown compactly next to score
    draw_text(surface, f"HIGH: {high_score:04d}", 14, (200, 220, 240), topleft=(16, 4))

    # Water quality meter (center)
    meter_rect = pygame.Rect(0, 0, 220, 22)
    meter_rect.center = (screen_width // 2, hud_height // 2)
    draw_water_quality_meter(surface, quality, meter_rect)
    draw_text(surface, f"WATER QUALITY: {int(quality)}%", 14, COLOR_WHITE,
              center=(meter_rect.centerx, meter_rect.top - 10))

    # Time (right)
    draw_text(surface, f"TIME: {int(time_left)}", FONT_HUD, COLOR_WHITE,
              topleft=(screen_width - 130, 18), bold=True)


def draw_panel(surface, rect, color=COLOR_WHITE, border_color=BUTTON_BORDER_COLOR, radius=18):
    """Draw a rounded rectangle panel, useful for pause/menu overlays."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    pygame.draw.rect(surface, border_color, rect, width=3, border_radius=radius)
