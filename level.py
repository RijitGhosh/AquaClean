"""
level.py
--------
Defines the Level class, which stores the configuration for the current
level (from settings.LEVEL_CONFIG) and draws the river environment:
water, banks, trees, rocks, algae obstacles, and animated waves.

Each level has its own background color scheme - the water gets murkier
and more ominous-looking as the difficulty rises (Easy -> Medium -> Hard),
to give a "more dangerous" feeling as pollution increases.
"""

import math
import random
import pygame
from settings import (
    LEVEL_CONFIG, SCREEN_WIDTH, SCREEN_HEIGHT,
    RIVER_LEFT, RIVER_RIGHT, RIVER_TOP, RIVER_BOTTOM,
    COLOR_TREE, COLOR_ROCK,
)
from algae import Algae


class Level:
    """Holds the configuration, decorations, and obstacles for one level."""

    def __init__(self, level_number, tree_image=None, rock_image=None,
                 algae_image=None, algae_scale=1.0, existing_rects=None):
        self.level_number = level_number
        self.config = LEVEL_CONFIG[level_number]

        self.tree_image = tree_image
        self.rock_image = rock_image

        # Pre-compute fixed decoration positions once per level so they don't
        # jump around every frame (trees/rocks on the banks, not in the water).
        self.trees = self._generate_bank_decorations(count=8)
        self.rocks = self._generate_bank_decorations(count=6)

        # Algae / water plant obstacles - placed inside the water, avoiding
        # anything already spawned there (passed in via existing_rects).
        self.algae_list = self._generate_algae(algae_image, algae_scale, existing_rects or [])

        # Wave animation state (two layers moving at slightly different
        # speeds gives a more natural flowing-water look than a single layer)
        self.wave_offset = 0
        self.wave_offset_2 = 0

    def _generate_bank_decorations(self, count):
        """Place small decoration anchor points along the top and bottom banks."""
        decorations = []
        for _ in range(count):
            x = random.randint(20, SCREEN_WIDTH - 20)
            if random.random() < 0.5:
                y = random.randint(14, RIVER_TOP - 6)
            else:
                y = random.randint(RIVER_BOTTOM + 6, SCREEN_HEIGHT - 14)
            decorations.append((x, y))
        return decorations

    def _generate_algae(self, algae_image, algae_scale, existing_rects):
        """Place algae obstacles inside the river, avoiding overlap with existing objects."""
        algae_list = []
        placed_rects = list(existing_rects)
        count = self.config.get("algae_count", 3)

        for _ in range(count):
            placed = False
            for _ in range(25):
                x = random.randint(RIVER_LEFT + 40, RIVER_RIGHT - 40)
                y = random.randint(RIVER_TOP + 40, RIVER_BOTTOM - 40)
                candidate = pygame.Rect(0, 0, 50, 40)
                candidate.center = (x, y)
                too_close = any(
                    candidate.inflate(20, 20).colliderect(r) for r in placed_rects
                )
                if not too_close:
                    algae = Algae(x, y, image=algae_image, scale=algae_scale)
                    algae_list.append(algae)
                    placed_rects.append(algae.rect)
                    placed = True
                    break
            if not placed:
                # Fallback placement so we never skip an obstacle entirely
                x = random.randint(RIVER_LEFT + 40, RIVER_RIGHT - 40)
                y = random.randint(RIVER_TOP + 40, RIVER_BOTTOM - 40)
                algae = Algae(x, y, image=algae_image, scale=algae_scale)
                algae_list.append(algae)
                placed_rects.append(algae.rect)

        return algae_list

    def update(self, dt):
        """Advance the wave animation and algae sway."""
        self.wave_offset = (self.wave_offset + 1.4) % 360
        self.wave_offset_2 = (self.wave_offset_2 - 0.9) % 360
        for algae in self.algae_list:
            algae.update(dt)

    def draw_environment(self, surface):
        """Draw river banks, water, waves, and decorations (background layer)."""
        bank_color = self.config.get("bank_color", (86, 140, 70))
        bank_dark = self.config.get("bank_color_dark", (66, 110, 55))
        water_color = self.config.get("water_color", (25, 110, 165))
        water_dark = self.config.get("water_color_dark", (18, 85, 135))
        wave_color = self.config.get("wave_color", (80, 175, 220))

        # Banks (top and bottom strips)
        surface.fill(bank_color)
        pygame.draw.rect(surface, bank_dark, (0, RIVER_TOP - 10, SCREEN_WIDTH, 10))
        pygame.draw.rect(surface, bank_dark, (0, RIVER_BOTTOM, SCREEN_WIDTH, 10))

        # Water area - base fill, then a subtle darker gradient band for depth
        water_rect = pygame.Rect(RIVER_LEFT, RIVER_TOP, RIVER_RIGHT - RIVER_LEFT, RIVER_BOTTOM - RIVER_TOP)
        pygame.draw.rect(surface, water_color, water_rect)
        gradient_band = pygame.Rect(RIVER_LEFT, RIVER_TOP, RIVER_RIGHT - RIVER_LEFT, 18)
        pygame.draw.rect(surface, water_dark, gradient_band)

        # Two layers of flowing wave lines moving at different speeds/directions
        # for a more realistic sense of moving water than a single static layer.
        for i, y in enumerate(range(RIVER_TOP + 15, RIVER_BOTTOM - 10, 26)):
            shift1 = int(9 * math.sin(math.radians(self.wave_offset + i * 42)))
            pygame.draw.line(
                surface, wave_color,
                (RIVER_LEFT + shift1, y), (RIVER_RIGHT + shift1, y), 2
            )
            shift2 = int(5 * math.sin(math.radians(self.wave_offset_2 + i * 65)))
            pygame.draw.line(
                surface, water_dark,
                (RIVER_LEFT + shift2, y + 10), (RIVER_RIGHT + shift2, y + 10), 1
            )

        # Trees and rocks on the banks (image if available, else drawn shape)
        for x, y in self.trees:
            if self.tree_image:
                rect = self.tree_image.get_rect(midbottom=(x, y + 20))
                surface.blit(self.tree_image, rect)
            else:
                pygame.draw.circle(surface, COLOR_TREE, (x, y), 14)
                pygame.draw.rect(surface, (90, 60, 30), (x - 2, y, 4, 8))

        for x, y in self.rocks:
            if self.rock_image:
                rect = self.rock_image.get_rect(center=(x, y))
                surface.blit(self.rock_image, rect)
            else:
                pygame.draw.circle(surface, COLOR_ROCK, (x, y), 8)

        # Algae obstacles inside the water
        for algae in self.algae_list:
            algae.draw(surface)

        # River border outline
        pygame.draw.rect(surface, (255, 255, 255), water_rect, width=2)

    def check_algae_collision(self, player_rect):
        """Return True if the player's rect overlaps any algae obstacle."""
        return any(player_rect.colliderect(algae.rect) for algae in self.algae_list)
