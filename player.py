"""
player.py
---------
Defines the Player class: the cleaning boat controlled by arrow keys / WASD.
Supports an optional pair of image frames for a gentle bobbing animation,
and falls back to a hand-drawn shape if no images were supplied/found.
"""

import pygame
from settings import (
    PLAYER_SPEED, PLAYER_SIZE, RIVER_LEFT, RIVER_RIGHT, RIVER_TOP, RIVER_BOTTOM,
    COLOR_WHITE, COLOR_ORANGE, COLOR_YELLOW,
)


class Player:
    """The player-controlled cleaning boat."""

    def __init__(self, x, y, images=None, speed=None, scale=1.0):
        base_w, base_h = PLAYER_SIZE
        self.width, self.height = int(base_w * scale), int(base_h * scale)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.speed = speed if speed is not None else PLAYER_SPEED
        self.prev_pos = self.rect.topleft
        self.facing = "right"
        self.net_wave = 0  # small animation counter for the cleaning net / bobbing

        # images: list of 2 frames (idle, bob) or None -> draw a shape instead
        self.images = None
        if images and all(images):
            self.images = [pygame.transform.smoothscale(img, (self.width, self.height)) for img in images]

        self.moving = False

    def handle_input(self, keys, touch_target=None):
        """
        Move the boat based on currently pressed keys, then clamp to the river area.
        touch_target: optional (x, y) screen position. While a finger / mouse button
        is held down, the boat steers toward that point (this is how phones play,
        since there is no keyboard).
        """
        self.prev_pos = self.rect.topleft
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
            self.facing = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
            self.facing = "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed

        # Touch / mouse-hold steering: move toward the touched point
        if touch_target is not None:
            tx, ty = touch_target
            gap_x = tx - self.rect.centerx
            gap_y = ty - self.rect.centery
            if abs(gap_x) > self.speed:
                dx += self.speed if gap_x > 0 else -self.speed
                self.facing = "right" if gap_x > 0 else "left"
            if abs(gap_y) > self.speed:
                dy += self.speed if gap_y > 0 else -self.speed

        self.moving = (dx != 0 or dy != 0)

        self.rect.x += dx
        self.rect.y += dy

        # Keep the boat inside the playable river area (river banks act as walls)
        self.rect.left = max(self.rect.left, RIVER_LEFT)
        self.rect.right = min(self.rect.right, RIVER_RIGHT)
        self.rect.top = max(self.rect.top, RIVER_TOP)
        self.rect.bottom = min(self.rect.bottom, RIVER_BOTTOM)

        self.net_wave = (self.net_wave + 1) % 40

    def draw(self, surface):
        """Draw the boat. Uses image frames if available, otherwise a simple shape."""
        if self.images:
            frame_index = 1 if (self.net_wave // 20) % 2 == 0 else 0
            img = self.images[frame_index]
            if self.facing == "left":
                img = pygame.transform.flip(img, True, False)
            surface.blit(img, self.rect.topleft)
            return

        # --- Placeholder shape drawing (used only when image assets are missing) ---
        hull_color = COLOR_ORANGE
        pygame.draw.ellipse(surface, hull_color, self.rect)
        pygame.draw.ellipse(surface, (150, 80, 10), self.rect, width=2)

        cabin_rect = pygame.Rect(0, 0, self.width * 0.4, self.height * 0.5)
        cabin_rect.center = (self.rect.centerx, self.rect.top + self.height * 0.25)
        pygame.draw.rect(surface, COLOR_WHITE, cabin_rect, border_radius=4)

        bob = 3 if (self.net_wave // 15) % 2 == 0 else -3
        net_x = self.rect.left - 10 if self.facing == "right" else self.rect.right + 10
        net_center = (net_x, self.rect.centery + bob)
        pygame.draw.circle(surface, COLOR_YELLOW, net_center, 8, width=2)

    def get_center(self):
        return self.rect.center

    def revert_position(self):
        """Undo this frame's movement (used when the boat hits a solid obstacle like algae)."""
        self.rect.topleft = self.prev_pos
