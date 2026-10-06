"""
pollution.py
------------
Defines the Pollution class (plastic bottles, plastic bags, garbage, and
oil spills) and a helper function to spawn them at safe random locations.
Each item can use a generated PNG image if available, otherwise it falls
back to a simple recognizable drawn shape.
"""

import math
import random
import pygame
from settings import (
    POLLUTION_TYPES, RIVER_LEFT, RIVER_RIGHT, RIVER_TOP, RIVER_BOTTOM,
)


class Pollution:
    """A single piece of pollution floating in the river."""

    def __init__(self, kind, x, y, image=None, scale=1.0):
        self.kind = kind  # "bottle", "bag", "garbage", or "oil"
        data = POLLUTION_TYPES[kind]
        self.score_value = data["score"]
        self.quality_value = data["quality"]
        self.color = data["color"]
        base_w, base_h = data["size"]
        self.width, self.height = int(base_w * scale), int(base_h * scale)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)

        self.image = None
        if image:
            self.image = pygame.transform.smoothscale(image, (self.width, self.height))

        # Small floating (bobbing) animation
        self.bob_timer = random.uniform(0, 6.28)
        self.base_y = y

    def update(self, dt):
        """Make the pollution gently bob up and down to look like it's floating."""
        self.bob_timer += dt * 2
        self.rect.centery = int(self.base_y + math.sin(self.bob_timer) * 3)

    def draw(self, surface):
        """Draw the pollution item using its image if available, else a simple shape."""
        if self.image:
            surface.blit(self.image, self.rect.topleft)
            return

        # --- Placeholder shape drawing (used only when image assets are missing) ---
        if self.kind == "bottle":
            pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
            neck = pygame.Rect(0, 0, self.width * 0.4, 6)
            neck.midbottom = (self.rect.centerx, self.rect.top)
            pygame.draw.rect(surface, self.color, neck)
        elif self.kind == "bag":
            pygame.draw.ellipse(surface, self.color, self.rect)
        elif self.kind == "garbage":
            pygame.draw.polygon(surface, self.color, [
                (self.rect.left, self.rect.bottom),
                (self.rect.left + 4, self.rect.top),
                (self.rect.centerx, self.rect.top + 4),
                (self.rect.right - 4, self.rect.top),
                (self.rect.right, self.rect.bottom),
            ])
        elif self.kind == "oil":
            pygame.draw.ellipse(surface, self.color, self.rect)
            pygame.draw.ellipse(surface, (10, 10, 10), self.rect, width=2)

        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=1, border_radius=4)


def is_far_enough(x, y, existing_rects, min_distance=45):
    """Check that a new spawn point isn't too close to existing objects (or the player)."""
    for rect in existing_rects:
        dx = x - rect.centerx
        dy = y - rect.centery
        if (dx * dx + dy * dy) ** 0.5 < min_distance:
            return False
    return True


def spawn_pollution(kind, existing_rects, player_rect, max_attempts=20, image=None, scale=1.0):
    """
    Create a Pollution object at a random location inside the river,
    avoiding the player's current position and other existing objects.
    Returns a Pollution instance (spawn always succeeds after max_attempts,
    just with looser spacing, so the game never freezes trying to place one).
    """
    for _ in range(max_attempts):
        x = random.randint(RIVER_LEFT + 30, RIVER_RIGHT - 30)
        y = random.randint(RIVER_TOP + 30, RIVER_BOTTOM - 30)
        candidate_rect = pygame.Rect(0, 0, 20, 20)
        candidate_rect.center = (x, y)

        too_close_to_player = candidate_rect.colliderect(player_rect.inflate(80, 80))
        overlaps_others = not is_far_enough(x, y, existing_rects)

        if not too_close_to_player and not overlaps_others:
            return Pollution(kind, x, y, image=image, scale=scale)

    # Fallback: place it anyway so gameplay never stalls
    x = random.randint(RIVER_LEFT + 30, RIVER_RIGHT - 30)
    y = random.randint(RIVER_TOP + 30, RIVER_BOTTOM - 30)
    return Pollution(kind, x, y, image=image, scale=scale)
