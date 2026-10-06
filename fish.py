"""
fish.py
-------
Defines the Fish class. Fish swim around the river and change direction
randomly. Colliding with a fish is bad for the player (it represents
harming aquatic life). Supports an optional pair of image frames for a
simple tail-flap swimming animation, with a shape-based fallback.
"""

import random
import pygame
from settings import RIVER_LEFT, RIVER_RIGHT, RIVER_TOP, RIVER_BOTTOM, FISH_SIZE


class Fish:
    """A fish swimming inside the river, moving smoothly and changing direction occasionally."""

    def __init__(self, x, y, speed, images=None, scale=1.0):
        base_w, base_h = FISH_SIZE
        self.width, self.height = int(base_w * scale), int(base_h * scale)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)

        self.speed = speed
        self.dx = speed * random.choice([-1, 1])
        self.dy = speed * random.uniform(-0.5, 0.5)
        self.direction_timer = random.randint(60, 180)  # frames until next direction change
        self.tail_wag = random.randint(0, 29)

        self.images = None
        if images and all(images):
            self.images = [pygame.transform.smoothscale(img, (self.width, self.height)) for img in images]

    def _pick_new_direction(self):
        self.dx = self.speed * random.choice([-1, 1])
        self.dy = self.speed * random.uniform(-0.7, 0.7)
        self.direction_timer = random.randint(60, 180)

    def update(self):
        """Move the fish, bounce off river banks, and occasionally change direction."""
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.left <= RIVER_LEFT or self.rect.right >= RIVER_RIGHT:
            self.dx *= -1
            self.rect.left = max(self.rect.left, RIVER_LEFT)
            self.rect.right = min(self.rect.right, RIVER_RIGHT)
        if self.rect.top <= RIVER_TOP or self.rect.bottom >= RIVER_BOTTOM:
            self.dy *= -1
            self.rect.top = max(self.rect.top, RIVER_TOP)
            self.rect.bottom = min(self.rect.bottom, RIVER_BOTTOM)

        self.direction_timer -= 1
        if self.direction_timer <= 0:
            self._pick_new_direction()

        self.tail_wag = (self.tail_wag + 1) % 30

    def draw(self, surface):
        facing_right = self.dx >= 0

        if self.images:
            frame_index = 0 if (self.tail_wag // 15) % 2 == 0 else 1
            img = self.images[frame_index]
            # Sprite art faces right by default (eye/head on the right side);
            # flip horizontally when swimming left.
            if not facing_right:
                img = pygame.transform.flip(img, True, False)
            surface.blit(img, self.rect.topleft)
            return

        # --- Placeholder shape drawing (used only when image assets are missing) ---
        body_color = (250, 170, 60)
        body_rect = pygame.Rect(0, 0, self.width * 0.7, self.height)
        body_rect.center = self.rect.center
        pygame.draw.ellipse(surface, body_color, body_rect)

        wag_offset = 3 if (self.tail_wag // 15) % 2 == 0 else -3
        if facing_right:
            tail_points = [
                (body_rect.left, body_rect.centery - 6 + wag_offset),
                (body_rect.left - 10, body_rect.centery),
                (body_rect.left, body_rect.centery + 6 - wag_offset),
            ]
            eye_pos = (body_rect.right - 6, body_rect.centery - 2)
        else:
            tail_points = [
                (body_rect.right, body_rect.centery - 6 + wag_offset),
                (body_rect.right + 10, body_rect.centery),
                (body_rect.right, body_rect.centery + 6 - wag_offset),
            ]
            eye_pos = (body_rect.left + 6, body_rect.centery - 2)

        pygame.draw.polygon(surface, body_color, tail_points)
        pygame.draw.circle(surface, (30, 30, 30), eye_pos, 2)
