"""
algae.py
--------
Defines the Algae class: clumps of algae / water plants floating in the
river that act as solid obstacles for the boat to steer around. They sway
gently for visual life but do not move position, and do not affect score
or water quality directly - bumping into one simply blocks the boat's path,
just like a real patch of thick weeds would.
"""

import math
import random
import pygame
from settings import ALGAE_BASE_SIZE


class Algae:
    """A stationary clump of algae / water plants that blocks the boat's movement."""

    def __init__(self, x, y, image=None, scale=1.0):
        base_w, base_h = ALGAE_BASE_SIZE
        self.width, self.height = int(base_w * scale), int(base_h * scale)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)

        self.image = None
        if image:
            self.image = pygame.transform.smoothscale(image, (self.width, self.height))

        self.sway_timer = random.uniform(0, 6.28)

    def update(self, dt):
        """Gentle swaying animation only - algae does not change position."""
        self.sway_timer += dt * 1.5

    def draw(self, surface):
        sway = int(2 * math.sin(self.sway_timer))
        if self.image:
            rect = self.image.get_rect(center=(self.rect.centerx + sway, self.rect.centery))
            surface.blit(self.image, rect)
            return

        # --- Placeholder shape drawing (used only when image assets are missing) ---
        base_color = (50, 130, 70)
        for i in range(3):
            blob_rect = pygame.Rect(0, 0, self.width * 0.5, self.height * 0.6)
            blob_rect.center = (
                self.rect.centerx - self.width * 0.25 + i * self.width * 0.25 + sway,
                self.rect.centery,
            )
            pygame.draw.ellipse(surface, base_color, blob_rect)
        pygame.draw.ellipse(surface, (30, 90, 45), self.rect, width=2)
