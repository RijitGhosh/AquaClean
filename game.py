"""
game.py
-------
The Game class ties everything together: it manages screen/state switching
(menu, instructions, about, playing, paused, level complete, game over),
runs the main loop, handles input, updates gameplay objects, checks
collisions, and draws everything each frame.
"""

import random
import pygame
import os

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE, HUD_HEIGHT,
    RIVER_LEFT, RIVER_RIGHT, RIVER_TOP, RIVER_BOTTOM,
    COLOR_WHITE, COLOR_BLACK, COLOR_DARK_BLUE, COLOR_RED, COLOR_GREEN,
    COLOR_BUBBLE, COLOR_WATER_DARK, COLOR_YELLOW,
    FONT_TITLE, FONT_SUBTITLE, FONT_LARGE, FONT_MEDIUM, FONT_SMALL,
    WATER_QUALITY_START, WATER_QUALITY_MIN, WATER_QUALITY_MAX,
    LEVEL_TIME_SECONDS, LEVEL_CONFIG, TOTAL_LEVELS,
    POLLUTION_TYPES, FISH_HIT_SCORE_PENALTY, FISH_HIT_QUALITY_PENALTY,
    EDUCATIONAL_TIPS, RATING_MESSAGES,
    IMAGES_DIR, SOUNDS_DIR,
    PLAYER_SPEED_MIN, PLAYER_SPEED_MAX, PLAYER_SPEED_STEP, PLAYER_SPEED_DEFAULT,
    FISH_SPEED_MULT_MIN, FISH_SPEED_MULT_MAX, FISH_SPEED_MULT_STEP, FISH_SPEED_MULT_DEFAULT,
    BOAT_SCALE_MIN, BOAT_SCALE_MAX, BOAT_SCALE_STEP, BOAT_SCALE_DEFAULT,
    FISH_SCALE_MIN, FISH_SCALE_MAX, FISH_SCALE_STEP, FISH_SCALE_DEFAULT,
    OIL_SCALE_MIN, OIL_SCALE_MAX, OIL_SCALE_STEP, OIL_SCALE_DEFAULT,
    DIRT_SCALE_MIN, DIRT_SCALE_MAX, DIRT_SCALE_STEP, DIRT_SCALE_DEFAULT,
    ALGAE_SCALE_MIN, ALGAE_SCALE_MAX, ALGAE_SCALE_STEP, ALGAE_SCALE_DEFAULT,
)
from ui import Button, draw_text, draw_hud, draw_panel, draw_water_quality_meter
from player import Player
from pollution import Pollution, spawn_pollution
from fish import Fish
from level import Level
from data_manager import (
    safe_load_image, safe_load_sound, safe_play_sound, safe_load_music,
    load_highscore, update_highscore_if_needed,
    load_settings, save_setting,
)

# ---------------------------------------------------------------------------
# GAME STATES
# ---------------------------------------------------------------------------
STATE_MENU = "menu"
STATE_INSTRUCTIONS = "instructions"
STATE_ABOUT = "about"
STATE_LEVEL_SELECT = "level_select"
STATE_SETTINGS = "settings"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_GAME_OVER = "game_over"


class Bubble:
    """A small decorative bubble used on the main menu background animation."""

    def __init__(self, image=None):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.radius = random.randint(3, 9)
        self.speed = random.uniform(0.4, 1.4)
        self.image = image
        self.scaled_image = None
        if self.image:
            size = self.radius * 2
            self.scaled_image = pygame.transform.smoothscale(self.image, (size, size))

    def update(self):
        self.y -= self.speed
        if self.y < -10:
            self.y = SCREEN_HEIGHT + 10
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        if self.scaled_image:
            rect = self.scaled_image.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.scaled_image, rect)
        else:
            pygame.draw.circle(surface, COLOR_BUBBLE, (int(self.x), int(self.y)), self.radius, width=1)


class Game:
    """Main game class: owns the window, the state machine, and the game loop."""

    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            pass  # No audio device available -> game continues silently

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = STATE_MENU
        self.high_score = load_highscore()

        settings_dict = load_settings()
        self.player_speed = settings_dict["player_speed"]
        self.fish_speed_multiplier = settings_dict["fish_speed_mult"]
        self.boat_scale = settings_dict["boat_scale"]
        self.fish_scale = settings_dict["fish_scale"]
        self.oil_scale = settings_dict["oil_scale"]
        self.dirt_scale = settings_dict["dirt_scale"]
        self.algae_scale = settings_dict["algae_scale"]

        # --- Image assets (all safely loaded; None if missing -> shapes used instead) ---
        self.player_images = [
            safe_load_image(os.path.join(IMAGES_DIR, "boat.png")),
            safe_load_image(os.path.join(IMAGES_DIR, "boat_bob.png")),
        ]
        self.fish_images = [
            safe_load_image(os.path.join(IMAGES_DIR, "fish_a.png")),
            safe_load_image(os.path.join(IMAGES_DIR, "fish_b.png")),
        ]
        self.pollution_images = {
            "bottle": safe_load_image(os.path.join(IMAGES_DIR, "bottle.png")),
            "bag": safe_load_image(os.path.join(IMAGES_DIR, "bag.png")),
            "garbage": safe_load_image(os.path.join(IMAGES_DIR, "garbage.png")),
            "oil": safe_load_image(os.path.join(IMAGES_DIR, "oil.png")),
        }
        self.tree_image = safe_load_image(os.path.join(IMAGES_DIR, "tree.png"))
        self.rock_image = safe_load_image(os.path.join(IMAGES_DIR, "rock.png"))
        self.bubble_image = safe_load_image(os.path.join(IMAGES_DIR, "bubble.png"))
        self.algae_image = safe_load_image(os.path.join(IMAGES_DIR, "algae.png"))

        # --- Sound assets ---
        self.sound_collect = safe_load_sound(os.path.join(SOUNDS_DIR, "collect.wav"))
        self.sound_fish_hit = safe_load_sound(os.path.join(SOUNDS_DIR, "fish_hit.wav"))
        self.sound_click = safe_load_sound(os.path.join(SOUNDS_DIR, "click.wav"))
        self.sound_level_complete = safe_load_sound(os.path.join(SOUNDS_DIR, "level_complete.wav"))
        self.sound_game_over = safe_load_sound(os.path.join(SOUNDS_DIR, "game_over.wav"))
        safe_load_music(os.path.join(SOUNDS_DIR, "background_music.wav"))

        # --- Menu decorations ---
        self.bubbles = [Bubble(self.bubble_image) for _ in range(18)]
        self.wave_offset = 0

        # --- Buttons for each screen (created once, reused) ---
        self._build_menu_buttons()

        # --- Gameplay state (initialized when a level starts) ---
        self.current_level_number = 1
        self.level = None
        self.player = None
        self.pollution_items = []
        self.fish_list = []
        self.score = 0
        self.water_quality = WATER_QUALITY_START
        self.time_left = LEVEL_TIME_SECONDS
        self.last_spawn_time = 0
        self.warning_message = ""
        self.warning_timer = 0
        self.current_tip = ""
        self.rating = ""
        self.rating_message = ""

    # ------------------------------------------------------------------
    # BUTTON SETUP
    # ------------------------------------------------------------------
    def _build_menu_buttons(self):
        cx = SCREEN_WIDTH // 2
        self.menu_buttons = {
            "start": Button("PLAY GAME", (cx, 270)),
            "instructions": Button("INSTRUCTIONS", (cx, 335)),
            "settings": Button("SETTINGS", (cx, 400)),
            "about": Button("ABOUT PROJECT", (cx, 465)),
            "exit": Button("EXIT", (cx, 530)),
        }
        self.back_button = Button("BACK", (cx, SCREEN_HEIGHT - 60), size=(180, 50))

        # Level select screen buttons
        self.level_select_buttons = {
            1: Button("LEVEL 1 - Easy", (cx, 210), size=(360, 60)),
            2: Button("LEVEL 2 - Medium", (cx, 310), size=(360, 60)),
            3: Button("LEVEL 3 - Hard", (cx, 410), size=(360, 60)),
        }

        # Settings screen: 2-column grid of - / value / + controls.
        # Left column = speed settings + algae size, right column = size settings.
        left_x = cx - 220
        right_x = cx + 220
        rows = [190, 280, 370, 460]

        def minus_plus(col_x, row_y):
            return (
                Button("-", (col_x - 90, row_y), size=(56, 50), font_size=FONT_MEDIUM),
                Button("+", (col_x + 90, row_y), size=(56, 50), font_size=FONT_MEDIUM),
            )

        boat_speed_minus, boat_speed_plus = minus_plus(left_x, rows[0])
        fish_speed_minus, fish_speed_plus = minus_plus(right_x, rows[0])
        boat_size_minus, boat_size_plus = minus_plus(left_x, rows[1])
        fish_size_minus, fish_size_plus = minus_plus(right_x, rows[1])
        oil_size_minus, oil_size_plus = minus_plus(left_x, rows[2])
        dirt_size_minus, dirt_size_plus = minus_plus(right_x, rows[2])
        algae_size_minus, algae_size_plus = minus_plus(left_x, rows[3])

        self.settings_rows = rows
        self.settings_columns = (left_x, right_x)
        self.settings_buttons = {
            "boat_speed_minus": boat_speed_minus, "boat_speed_plus": boat_speed_plus,
            "fish_speed_minus": fish_speed_minus, "fish_speed_plus": fish_speed_plus,
            "boat_size_minus": boat_size_minus, "boat_size_plus": boat_size_plus,
            "fish_size_minus": fish_size_minus, "fish_size_plus": fish_size_plus,
            "oil_size_minus": oil_size_minus, "oil_size_plus": oil_size_plus,
            "dirt_size_minus": dirt_size_minus, "dirt_size_plus": dirt_size_plus,
            "algae_size_minus": algae_size_minus, "algae_size_plus": algae_size_plus,
            "reset": Button("RESET ALL", (right_x, rows[3]), size=(180, 50), font_size=FONT_SMALL),
        }

        self.pause_buttons = {
            "resume": Button("RESUME", (cx, 260)),
            "restart": Button("RESTART", (cx, 330)),
            "menu": Button("MAIN MENU", (cx, 400)),
        }

        self.complete_buttons = {
            "next": Button("NEXT LEVEL", (cx - 130, SCREEN_HEIGHT - 90)),
            "retry": Button("PLAY AGAIN", (cx - 130, SCREEN_HEIGHT - 90)),
            "menu": Button("MAIN MENU", (cx + 130, SCREEN_HEIGHT - 90)),
        }

        self.gameover_buttons = {
            "retry": Button("RETRY", (cx - 130, SCREEN_HEIGHT - 90)),
            "menu": Button("MAIN MENU", (cx + 130, SCREEN_HEIGHT - 90)),
        }

    # ------------------------------------------------------------------
    # LEVEL / GAMEPLAY SETUP
    # ------------------------------------------------------------------
    def start_level(self, level_number):
        """Reset gameplay state and begin the given level number (1-3)."""
        self.current_level_number = level_number

        self.player = Player(
            (RIVER_LEFT + RIVER_RIGHT) // 2,
            (RIVER_TOP + RIVER_BOTTOM) // 2,
            images=self.player_images,
            speed=self.player_speed,
            scale=self.boat_scale,
        )

        config = LEVEL_CONFIG[level_number]

        self.pollution_items = []
        existing_rects = [self.player.rect]
        pollution_kinds = ["bottle", "bag", "garbage"]
        for _ in range(config["pollution_count"]):
            kind = random.choice(pollution_kinds)
            item = spawn_pollution(kind, existing_rects, self.player.rect,
                                    image=self.pollution_images.get(kind), scale=self.dirt_scale)
            self.pollution_items.append(item)
            existing_rects.append(item.rect)
        for _ in range(config["oil_count"]):
            item = spawn_pollution("oil", existing_rects, self.player.rect,
                                    image=self.pollution_images.get("oil"), scale=self.oil_scale)
            self.pollution_items.append(item)
            existing_rects.append(item.rect)

        # Algae obstacles are placed avoiding the player and all pollution already spawned
        self.level = Level(
            level_number, tree_image=self.tree_image, rock_image=self.rock_image,
            algae_image=self.algae_image, algae_scale=self.algae_scale,
            existing_rects=existing_rects,
        )

        self.fish_list = []
        effective_fish_speed = config["fish_speed"] * self.fish_speed_multiplier
        for _ in range(config["fish_count"]):
            x = random.randint(RIVER_LEFT + 40, RIVER_RIGHT - 40)
            y = random.randint(RIVER_TOP + 40, RIVER_BOTTOM - 40)
            self.fish_list.append(Fish(x, y, effective_fish_speed, images=self.fish_images, scale=self.fish_scale))

        self.score = 0
        self.water_quality = WATER_QUALITY_START
        self.time_left = LEVEL_TIME_SECONDS
        self.last_spawn_time = pygame.time.get_ticks()
        self.warning_message = ""
        self.warning_timer = 0
        self.level_start_ticks = pygame.time.get_ticks()

        self.state = STATE_PLAYING

    def restart_current_level(self):
        self.start_level(self.current_level_number)

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()

    # ------------------------------------------------------------------
    # EVENT HANDLING
    # ------------------------------------------------------------------
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and self.state == STATE_PLAYING:
                    self.state = STATE_PAUSED
                elif event.key == pygame.K_p and self.state == STATE_PAUSED:
                    self.state = STATE_PLAYING
                elif event.key == pygame.K_ESCAPE and self.state in (
                    STATE_INSTRUCTIONS, STATE_ABOUT, STATE_LEVEL_SELECT, STATE_SETTINGS
                ):
                    self.state = STATE_MENU

            if self.state == STATE_MENU:
                self._handle_menu_events(event)
            elif self.state == STATE_INSTRUCTIONS:
                self._handle_back_only(event)
            elif self.state == STATE_ABOUT:
                self._handle_back_only(event)
            elif self.state == STATE_LEVEL_SELECT:
                self._handle_level_select_events(event)
            elif self.state == STATE_SETTINGS:
                self._handle_settings_events(event)
            elif self.state == STATE_PAUSED:
                self._handle_pause_events(event)
            elif self.state == STATE_LEVEL_COMPLETE:
                self._handle_level_complete_events(event)
            elif self.state == STATE_GAME_OVER:
                self._handle_game_over_events(event)

    def _handle_menu_events(self, event):
        if self.menu_buttons["start"].is_clicked(event):
            safe_play_sound(self.sound_click)
            self.state = STATE_LEVEL_SELECT
        elif self.menu_buttons["instructions"].is_clicked(event):
            safe_play_sound(self.sound_click)
            self.state = STATE_INSTRUCTIONS
        elif self.menu_buttons["settings"].is_clicked(event):
            safe_play_sound(self.sound_click)
            self.state = STATE_SETTINGS
        elif self.menu_buttons["about"].is_clicked(event):
            safe_play_sound(self.sound_click)
            self.state = STATE_ABOUT
        elif self.menu_buttons["exit"].is_clicked(event):
            self.running = False

    def _handle_level_select_events(self, event):
        for level_number, button in self.level_select_buttons.items():
            if button.is_clicked(event):
                safe_play_sound(self.sound_click)
                self.start_level(level_number)
                return
        if self.back_button.is_clicked(event):
            safe_play_sound(self.sound_click)
            self.state = STATE_MENU

    def _handle_settings_events(self, event):
        # (attribute name, settings-file key, min, max, step, round digits)
        controls = [
            ("boat_speed", "player_speed", "player_speed", PLAYER_SPEED_MIN, PLAYER_SPEED_MAX, PLAYER_SPEED_STEP, 0),
            ("fish_speed", "fish_speed_multiplier", "fish_speed_mult", FISH_SPEED_MULT_MIN, FISH_SPEED_MULT_MAX, FISH_SPEED_MULT_STEP, 2),
            ("boat_size", "boat_scale", "boat_scale", BOAT_SCALE_MIN, BOAT_SCALE_MAX, BOAT_SCALE_STEP, 2),
            ("fish_size", "fish_scale", "fish_scale", FISH_SCALE_MIN, FISH_SCALE_MAX, FISH_SCALE_STEP, 2),
            ("oil_size", "oil_scale", "oil_scale", OIL_SCALE_MIN, OIL_SCALE_MAX, OIL_SCALE_STEP, 2),
            ("dirt_size", "dirt_scale", "dirt_scale", DIRT_SCALE_MIN, DIRT_SCALE_MAX, DIRT_SCALE_STEP, 2),
            ("algae_size", "algae_scale", "algae_scale", ALGAE_SCALE_MIN, ALGAE_SCALE_MAX, ALGAE_SCALE_STEP, 2),
        ]

        for prefix, attr_name, save_key, min_v, max_v, step, ndigits in controls:
            minus_btn = self.settings_buttons[f"{prefix}_minus"]
            plus_btn = self.settings_buttons[f"{prefix}_plus"]
            current = getattr(self, attr_name)

            if minus_btn.is_clicked(event):
                new_val = round(max(min_v, current - step), ndigits) if ndigits else max(min_v, current - step)
                setattr(self, attr_name, new_val)
                save_setting(save_key, new_val)
                safe_play_sound(self.sound_click)
                return
            if plus_btn.is_clicked(event):
                new_val = round(min(max_v, current + step), ndigits) if ndigits else min(max_v, current + step)
                setattr(self, attr_name, new_val)
                save_setting(save_key, new_val)
                safe_play_sound(self.sound_click)
                return

        if self.settings_buttons["reset"].is_clicked(event):
            self.player_speed = PLAYER_SPEED_DEFAULT
            self.fish_speed_multiplier = FISH_SPEED_MULT_DEFAULT
            self.boat_scale = BOAT_SCALE_DEFAULT
            self.fish_scale = FISH_SCALE_DEFAULT
            self.oil_scale = OIL_SCALE_DEFAULT
            self.dirt_scale = DIRT_SCALE_DEFAULT
            self.algae_scale = ALGAE_SCALE_DEFAULT
            save_setting("player_speed", self.player_speed)
            save_setting("fish_speed_mult", self.fish_speed_multiplier)
            save_setting("boat_scale", self.boat_scale)
            save_setting("fish_scale", self.fish_scale)
            save_setting("oil_scale", self.oil_scale)
            save_setting("dirt_scale", self.dirt_scale)
            save_setting("algae_scale", self.algae_scale)
            safe_play_sound(self.sound_click)
        elif self.back_button.is_clicked(event):
            safe_play_sound(self.sound_click)
            self.state = STATE_MENU

    def _handle_back_only(self, event):
        if self.back_button.is_clicked(event):
            safe_play_sound(self.sound_click)
            self.state = STATE_MENU

    def _handle_pause_events(self, event):
        if self.pause_buttons["resume"].is_clicked(event):
            self.state = STATE_PLAYING
        elif self.pause_buttons["restart"].is_clicked(event):
            self.restart_current_level()
        elif self.pause_buttons["menu"].is_clicked(event):
            self.state = STATE_MENU

    def _handle_level_complete_events(self, event):
        is_final_level = self.current_level_number >= TOTAL_LEVELS
        if is_final_level:
            if self.complete_buttons["retry"].is_clicked(event):
                self.start_level(1)
            elif self.complete_buttons["menu"].is_clicked(event):
                self.state = STATE_MENU
        else:
            if self.complete_buttons["next"].is_clicked(event):
                self.start_level(self.current_level_number + 1)
            elif self.complete_buttons["menu"].is_clicked(event):
                self.state = STATE_MENU

    def _handle_game_over_events(self, event):
        if self.gameover_buttons["retry"].is_clicked(event):
            self.start_level(self.current_level_number)
        elif self.gameover_buttons["menu"].is_clicked(event):
            self.state = STATE_MENU

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    def _update(self, dt):
        mouse_pos = pygame.mouse.get_pos()

        if self.state == STATE_MENU:
            for bubble in self.bubbles:
                bubble.update()
            self.wave_offset = (self.wave_offset + 1) % 360
            for btn in self.menu_buttons.values():
                btn.update_hover(mouse_pos)

        elif self.state in (STATE_INSTRUCTIONS, STATE_ABOUT):
            self.back_button.update_hover(mouse_pos)

        elif self.state == STATE_LEVEL_SELECT:
            self.back_button.update_hover(mouse_pos)
            for btn in self.level_select_buttons.values():
                btn.update_hover(mouse_pos)

        elif self.state == STATE_SETTINGS:
            self.back_button.update_hover(mouse_pos)
            for btn in self.settings_buttons.values():
                btn.update_hover(mouse_pos)

        elif self.state == STATE_PLAYING:
            self._update_gameplay(dt)

        elif self.state == STATE_PAUSED:
            for btn in self.pause_buttons.values():
                btn.update_hover(mouse_pos)

        elif self.state == STATE_LEVEL_COMPLETE:
            for btn in self.complete_buttons.values():
                btn.update_hover(mouse_pos)

        elif self.state == STATE_GAME_OVER:
            for btn in self.gameover_buttons.values():
                btn.update_hover(mouse_pos)

    def _update_gameplay(self, dt):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.level.update(dt)

        # Algae obstacles block the boat's path - revert movement on collision
        if self.level.check_algae_collision(self.player.rect):
            self.player.revert_position()

        for item in self.pollution_items:
            item.update(dt)
        for fish in self.fish_list:
            fish.update()

        self._check_collisions()
        self._maybe_spawn_more_pollution()

        # Timer countdown
        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self._end_level()

        if self.warning_timer > 0:
            self.warning_timer -= dt

        # Clamp water quality within bounds
        self.water_quality = max(WATER_QUALITY_MIN, min(WATER_QUALITY_MAX, self.water_quality))
        # Score should not go unnecessarily negative
        self.score = max(self.score, 0)

    def _check_collisions(self):
        # Player vs pollution
        remaining_items = []
        for item in self.pollution_items:
            if self.player.rect.colliderect(item.rect):
                self.score += item.score_value
                self.water_quality += item.quality_value
                if item.kind == "oil":
                    self.warning_message = "Oil Spill! Water Quality Damaged!"
                    self.warning_timer = 1.5
                else:
                    safe_play_sound(self.sound_collect)
            else:
                remaining_items.append(item)
        self.pollution_items = remaining_items

        # Player vs fish
        for fish in self.fish_list:
            if self.player.rect.colliderect(fish.rect):
                self.score -= FISH_HIT_SCORE_PENALTY
                self.water_quality -= FISH_HIT_QUALITY_PENALTY
                self.warning_message = "Protect Aquatic Life!"
                self.warning_timer = 1.5
                safe_play_sound(self.sound_fish_hit)
                # Nudge the fish away so the player doesn't get repeatedly punished
                # for a single accidental touch.
                fish.dx *= -1
                fish.dy *= -1

    def _maybe_spawn_more_pollution(self):
        """Keep the river populated with pollution by respawning items over time."""
        now = pygame.time.get_ticks()
        config = self.level.config
        if now - self.last_spawn_time >= config["spawn_interval_ms"]:
            self.last_spawn_time = now
            if len(self.pollution_items) < config["pollution_count"] + config["oil_count"]:
                kind = random.choice(["bottle", "bag", "garbage", "oil"] if random.random() < 0.25
                                      else ["bottle", "bag", "garbage"])
                scale = self.oil_scale if kind == "oil" else self.dirt_scale
                existing_rects = [p.rect for p in self.pollution_items]
                new_item = spawn_pollution(kind, existing_rects, self.player.rect,
                                            image=self.pollution_images.get(kind), scale=scale)
                self.pollution_items.append(new_item)

    def _end_level(self):
        """Called when the timer reaches zero: compute rating and show results."""
        self.rating = self._compute_rating()
        self.rating_message = RATING_MESSAGES[self.rating]
        self.current_tip = random.choice(EDUCATIONAL_TIPS)
        self.high_score = update_highscore_if_needed(self.score)

        if self.rating == "Poor" and self.current_level_number == 1:
            # Gentle handling: even a poor first level still lets the player continue,
            # per "do not make the game frustrating". Game Over is reserved for
            # very low performance combined with zero water quality.
            pass

        if self.water_quality <= WATER_QUALITY_MIN and self.score == 0:
            safe_play_sound(self.sound_game_over)
            self.state = STATE_GAME_OVER
        else:
            safe_play_sound(self.sound_level_complete)
            self.state = STATE_LEVEL_COMPLETE

    def _compute_rating(self):
        # Combine score and water quality into a simple 0-100 performance value
        performance = (self.water_quality * 0.6) + (min(self.score, 200) / 200 * 100 * 0.4)
        if performance >= 90:
            return "Excellent"
        elif performance >= 70:
            return "Good"
        elif performance >= 50:
            return "Moderate"
        return "Poor"

    # ------------------------------------------------------------------
    # DRAWING
    # ------------------------------------------------------------------
    def _draw(self):
        if self.state == STATE_MENU:
            self._draw_menu()
        elif self.state == STATE_INSTRUCTIONS:
            self._draw_instructions()
        elif self.state == STATE_ABOUT:
            self._draw_about()
        elif self.state == STATE_LEVEL_SELECT:
            self._draw_level_select()
        elif self.state == STATE_SETTINGS:
            self._draw_settings()
        elif self.state == STATE_PLAYING:
            self._draw_gameplay()
        elif self.state == STATE_PAUSED:
            self._draw_gameplay()
            self._draw_pause_overlay()
        elif self.state == STATE_LEVEL_COMPLETE:
            self._draw_gameplay()
            self._draw_level_complete_overlay()
        elif self.state == STATE_GAME_OVER:
            self._draw_gameplay()
            self._draw_game_over_overlay()

    def _draw_menu(self):
        self.screen.fill(COLOR_WATER_DARK)

        # Animated wave stripes in the background
        import math
        for i, y in enumerate(range(0, SCREEN_HEIGHT, 40)):
            shift = int(15 * math.sin(math.radians(self.wave_offset + i * 30)))
            pygame.draw.line(self.screen, (30, 110, 165), (0 + shift, y), (SCREEN_WIDTH + shift, y), 3)

        for bubble in self.bubbles:
            bubble.draw(self.screen)

        draw_text(self.screen, "AQUACLEAN", FONT_TITLE, COLOR_WHITE, center=(SCREEN_WIDTH // 2, 110), bold=True)
        draw_text(self.screen, "Water Pollution Management & Awareness Game", FONT_SUBTITLE,
                  (210, 235, 250), center=(SCREEN_WIDTH // 2, 165))

        for btn in self.menu_buttons.values():
            btn.draw(self.screen)

        draw_text(self.screen, f"High Score: {self.high_score}", FONT_SMALL, (210, 235, 250),
                  center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25))

    def _draw_instructions(self):
        self.screen.fill(COLOR_WATER_DARK)
        draw_text(self.screen, "HOW TO PLAY", FONT_LARGE, COLOR_WHITE, center=(SCREEN_WIDTH // 2, 70), bold=True)

        lines = [
            "Use Arrow Keys or WASD to move the boat.",
            "Collect floating pollution to increase your score.",
            "Avoid fish  -  protect aquatic life!",
            "Avoid oil spills  -  they damage water quality.",
            "Collect as much waste as possible before time runs out.",
            "Improve the Water Quality score to do well in each level.",
            "Choose any level directly from the level select screen.",
            "Adjust boat and fish speed anytime from Settings.",
            "",
            "CONTROLS",
            "Up / W        = Move Up",
            "Down / S      = Move Down",
            "Left / A      = Move Left",
            "Right / D     = Move Right",
            "P             = Pause Game",
        ]
        y = 110
        for line in lines:
            bold = line.isupper() and line != ""
            draw_text(self.screen, line, FONT_SMALL, COLOR_WHITE, center=(SCREEN_WIDTH // 2, y), bold=bold)
            y += 27

        self.back_button.draw(self.screen)

    def _draw_about(self):
        self.screen.fill(COLOR_WATER_DARK)
        draw_text(self.screen, "AQUACLEAN", FONT_LARGE, COLOR_WHITE, center=(SCREEN_WIDTH // 2, 70), bold=True)
        draw_text(self.screen, "Water Pollution Management & Awareness Game", FONT_SMALL,
                  (210, 235, 250), center=(SCREEN_WIDTH // 2, 105))

        lines = [
            "",
            "PURPOSE",
            "To spread awareness about water pollution and demonstrate the",
            "importance of proper waste management through interactive gameplay.",
            "",
            "TECHNOLOGY",
            "Python, Pygame, Object-Oriented Programming",
            "",
            "KEY CONCEPTS",
            "Water pollution - Waste management",
            "Aquatic life protection - Environmental awareness",
            "",
            "Developed as an educational technology project.",
        ]
        y = 145
        for line in lines:
            bold = line.isupper() and line != ""
            draw_text(self.screen, line, FONT_SMALL, COLOR_WHITE, center=(SCREEN_WIDTH // 2, y), bold=bold)
            y += 26

        self.back_button.draw(self.screen)

    def _draw_level_select(self):
        self.screen.fill(COLOR_WATER_DARK)
        draw_text(self.screen, "SELECT LEVEL", FONT_LARGE, COLOR_WHITE,
                  center=(SCREEN_WIDTH // 2, 110), bold=True)
        draw_text(self.screen, "Choose any level to play - difficulty increases each level.",
                  FONT_SMALL, (210, 235, 250), center=(SCREEN_WIDTH // 2, 150))

        for btn in self.level_select_buttons.values():
            btn.draw(self.screen)

        subtitles = {
            1: "Clean Start - few pollution items, slow fish",
            2: "Rising Pollution - more waste, faster fish",
            3: "Critical River - heavy pollution, fast fish",
        }
        for level_number, btn in self.level_select_buttons.items():
            draw_text(self.screen, subtitles[level_number], 14, (200, 225, 245),
                      center=(btn.rect.centerx, btn.rect.bottom + 16))

        self.back_button.draw(self.screen)

    def _draw_settings(self):
        self.screen.fill(COLOR_WATER_DARK)
        cx = SCREEN_WIDTH // 2
        left_x, right_x = self.settings_columns
        rows = self.settings_rows

        draw_text(self.screen, "SETTINGS", FONT_LARGE, COLOR_WHITE, center=(cx, 55), bold=True)
        draw_text(self.screen, "Adjust speed and size for boat, fish, oil spills, dirt, and algae.",
                  FONT_SMALL, (210, 235, 250), center=(cx, 90))

        def draw_control(prefix, label, col_x, row_y, value_text):
            draw_text(self.screen, label, FONT_SMALL, COLOR_WHITE, center=(col_x, row_y - 32), bold=True)
            self.settings_buttons[f"{prefix}_minus"].draw(self.screen)
            self.settings_buttons[f"{prefix}_plus"].draw(self.screen)
            draw_text(self.screen, value_text, FONT_MEDIUM, COLOR_YELLOW, center=(col_x, row_y), bold=True)

        draw_control("boat_speed", "BOAT SPEED", left_x, rows[0], str(self.player_speed))
        draw_control("fish_speed", "FISH SPEED", right_x, rows[0], f"x{self.fish_speed_multiplier:.2f}")

        draw_control("boat_size", "BOAT SIZE", left_x, rows[1], f"x{self.boat_scale:.2f}")
        draw_control("fish_size", "FISH SIZE", right_x, rows[1], f"x{self.fish_scale:.2f}")

        draw_control("oil_size", "OIL SPILL SIZE", left_x, rows[2], f"x{self.oil_scale:.2f}")
        draw_control("dirt_size", "DIRT SIZE", right_x, rows[2], f"x{self.dirt_scale:.2f}")

        draw_control("algae_size", "ALGAE SIZE", left_x, rows[3], f"x{self.algae_scale:.2f}")
        self.settings_buttons["reset"].draw(self.screen)

        draw_text(self.screen, "Your choices are saved automatically.", FONT_SMALL, (210, 235, 250),
                  center=(cx, SCREEN_HEIGHT - 90))

        self.back_button.draw(self.screen)

    def _draw_gameplay(self):
        self.level.draw_environment(self.screen)

        for item in self.pollution_items:
            item.draw(self.screen)
        for fish in self.fish_list:
            fish.draw(self.screen)
        self.player.draw(self.screen)

        draw_hud(self.screen, self.score, self.water_quality, self.time_left,
                 self.high_score, SCREEN_WIDTH, HUD_HEIGHT)

        # Level name banner (small, top-left under HUD, unobtrusive)
        draw_text(self.screen, self.level.config["name"], 16, COLOR_WHITE,
                  topleft=(16, HUD_HEIGHT + 4))

        if self.warning_timer > 0 and self.warning_message:
            warn_rect = pygame.Rect(0, 0, 360, 40)
            warn_rect.center = (SCREEN_WIDTH // 2, HUD_HEIGHT + 40)
            draw_panel(self.screen, warn_rect, color=(255, 235, 235), border_color=COLOR_RED, radius=10)
            draw_text(self.screen, self.warning_message, FONT_SMALL, COLOR_RED, center=warn_rect.center, bold=True)

        draw_text(self.screen, "Press P to Pause", 14, (230, 240, 250),
                  topleft=(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 24))

    def _draw_pause_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(0, 0, 360, 300)
        panel_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_panel(self.screen, panel_rect)

        draw_text(self.screen, "GAME PAUSED", FONT_LARGE, COLOR_DARK_BLUE,
                  center=(panel_rect.centerx, panel_rect.top + 50), bold=True)

        for btn in self.pause_buttons.values():
            btn.draw(self.screen)

    def _draw_level_complete_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(0, 0, 520, 340)
        panel_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_panel(self.screen, panel_rect)

        is_final = self.current_level_number >= TOTAL_LEVELS
        title = "FINAL RESULTS" if is_final else "LEVEL COMPLETE!"
        draw_text(self.screen, title, FONT_LARGE, COLOR_DARK_BLUE,
                  center=(panel_rect.centerx, panel_rect.top + 40), bold=True)

        draw_text(self.screen, f"Score: {self.score}", FONT_MEDIUM, COLOR_BLACK,
                  center=(panel_rect.centerx, panel_rect.top + 90))
        draw_text(self.screen, f"Water Quality: {int(self.water_quality)}%", FONT_MEDIUM, COLOR_BLACK,
                  center=(panel_rect.centerx, panel_rect.top + 125))
        draw_text(self.screen, f"Rating: {self.rating}", FONT_MEDIUM, COLOR_GREEN,
                  center=(panel_rect.centerx, panel_rect.top + 160), bold=True)

        # Wrap the educational tip / rating message onto two lines if needed
        self._draw_wrapped_text(self.rating_message, panel_rect.centerx, panel_rect.top + 200,
                                 panel_rect.width - 40)
        self._draw_wrapped_text(f"Tip: {self.current_tip}", panel_rect.centerx, panel_rect.top + 240,
                                 panel_rect.width - 40, color=(30, 100, 150))

        if is_final:
            self.complete_buttons["retry"].draw(self.screen)
        else:
            self.complete_buttons["next"].draw(self.screen)
        self.complete_buttons["menu"].draw(self.screen)

    def _draw_game_over_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(0, 0, 420, 280)
        panel_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_panel(self.screen, panel_rect, border_color=COLOR_RED)

        draw_text(self.screen, "GAME OVER", FONT_LARGE, COLOR_RED,
                  center=(panel_rect.centerx, panel_rect.top + 50), bold=True)
        draw_text(self.screen, f"Final Score: {self.score}", FONT_MEDIUM, COLOR_BLACK,
                  center=(panel_rect.centerx, panel_rect.top + 100))
        draw_text(self.screen, f"Water Quality: {int(self.water_quality)}%", FONT_MEDIUM, COLOR_BLACK,
                  center=(panel_rect.centerx, panel_rect.top + 135))

        self.gameover_buttons["retry"].draw(self.screen)
        self.gameover_buttons["menu"].draw(self.screen)

    def _draw_wrapped_text(self, text, center_x, y, max_width, color=COLOR_BLACK, size=FONT_SMALL):
        """Simple word-wrap so longer tip/rating messages fit inside the panel."""
        from ui import get_font
        font = get_font(size)
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)

        for i, line in enumerate(lines):
            draw_text(self.screen, line, size, color, center=(center_x, y + i * 22))
