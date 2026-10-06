# AquaClean

**Water Pollution Management & Awareness Game**

## Project Description

AquaClean is a 2D top-down educational game built with Python and Pygame.
The player controls a small cleaning boat on a polluted river. The goal is
to collect floating pollution (plastic bottles, plastic bags, garbage)
while avoiding fish and harmful oil spills, in order to raise the river's
**Water Quality** score. The game is designed to raise awareness about
water pollution and responsible waste management in an interactive way.

## Objectives

- Demonstrate the environmental impact of pollution and cleanup through gameplay.
- Encourage players to associate waste collection with a positive outcome
  (higher score, higher water quality) and harming aquatic life with a
  negative outcome (lower score, lower water quality).
- Present short educational tips after every level.

## Features

- Animated main menu with waves and floating bubbles
- Instructions and About Project screens
- **Level Select screen** — jump directly into Level 1, 2, or 3, any time
- **Settings screen** — adjust Boat Speed, Fish Speed, and the SIZE of the
  boat, fish, oil spills, dirt (bottles/bags/garbage), and algae, all
  independently with +/- buttons; every choice is saved automatically to
  `data/settings.txt` and remembered the next time you launch the game
- A realistic small wooden fishing boat sprite (hull, outboard motor,
  fishing rod, catch bucket, cleaning net) instead of a plain cartoon boat
- **Algae / water-plant obstacles** floating in the river that block the
  boat's path and must be steered around, with more of them at higher
  difficulty
- Each level has its own background color scheme that gets more ominous
  as pollution rises: calm blue (Level 1) -> murky green (Level 2) ->
  dangerous dark red-brown (Level 3)
- Two-layer flowing wave animation for a more realistic sense of moving water
- Three levels of increasing difficulty (Easy, Medium, Hard)
- Score system and a 0-100% Water Quality meter (red / yellow / green)
- 60-second countdown timer per level
- Collectible pollution objects with different point values
- Moving fish with simple direction-changing AI that must be avoided
- Level Complete screen with a performance rating and educational tip
- Game Over and Pause screens
- Locally saved high score (`data/highscore.txt`)
- Safe asset loading: the game runs and shows placeholder shapes even if
  image/sound files are missing, so it never crashes due to missing assets
- Optional sound effects and background music (skipped silently if absent)

## Technology Used

- Python 3
- Pygame
- Object-Oriented Programming (Player, Pollution, Fish, Level, Button, Game classes)

## Controls

| Action        | Keys              |
|---------------|-------------------|
| Move Up       | Up Arrow / W      |
| Move Down     | Down Arrow / S    |
| Move Left     | Left Arrow / A    |
| Move Right    | Right Arrow / D   |
| Pause / Resume| P                 |

## How to Install

1. Make sure Python 3.8 or newer is installed.
2. Install the required packages:

   ```bash
   pip install pygame pillow numpy
   ```

   (`pygame` runs the game; `pillow` and `numpy` are only needed once, to
   generate the image and sound asset files.)

## How to Run

All image and sound assets are already generated and included in
`assets/images/` and `assets/sounds/`, so you can run the game immediately:

```bash
python main.py
```

The game will open directly to the main menu.

### Regenerating assets (optional)

If you ever delete or want to regenerate the art/sound files, run these
once from inside the `AquaClean` folder:

```bash
python generate_assets.py
python generate_sounds.py
```

`generate_assets.py` draws all sprites (boat, fish, bottle, bag, garbage,
oil spill, trees, rocks, bubbles) as original PNG images using Pillow.
`generate_sounds.py` synthesizes all sound effects and the background
music as WAV files using simple waveform generation (no copyrighted
audio, no internet access required). Both are original, programmatically
generated assets — safe to include and explain in an academic project.

## Game Rules

- Collecting pollution increases your Score and Water Quality.
  - Plastic Bottle: +10 Score, +5 Water Quality
  - Plastic Bag: +15 Score, +7 Water Quality
  - Garbage: +20 Score, +10 Water Quality
  - Oil Spill: -15 Score, -10 Water Quality (avoid it!)
- Colliding with a fish reduces Score by 20 and Water Quality by 5, and
  shows the warning "Protect Aquatic Life!".
- Water Quality is always kept between 0% and 100%. Score is never allowed
  to fall below 0.
- Each level lasts 60 seconds. When time runs out, a rating is calculated:
  - 90-100 = Excellent
  - 70-89 = Good
  - 50-69 = Moderate
  - 0-49 = Poor
- There are three levels of increasing difficulty. After Level 3, final
  results are shown instead of a "Next Level" option.

## Educational Purpose

Water Quality in this game is a **gameplay indicator for awareness
purposes only** — it is not a scientific water-quality measurement. The
project is meant to demonstrate, in a simple and engaging way, how
pollution damages rivers and how proper waste management and protecting
aquatic life can help restore them.

## Future Improvements

- IoT-based real-time water-quality sensors
- Real-time water monitoring integration
- More pollution types and river environments
- Multiplayer mode
- Database-backed leaderboard / score history
- Mobile version

## Project Structure

```
AquaClean/
├── main.py              Entry point - starts the game
├── settings.py          All constants: colors, sizes, levels, tuning values
├── game.py              Game class - state machine, main loop, all screens
├── player.py            Player (cleaning boat) class, animated
├── pollution.py         Pollution class + safe spawning logic
├── fish.py              Fish class with simple movement AI, animated
├── level.py             Level class - environment drawing and level config
├── ui.py                Button class, text/HUD/meter drawing helpers
├── data_manager.py      Safe asset loading + high score save/load
├── generate_assets.py   Builds all PNG sprites (run once, already done)
├── generate_sounds.py   Builds all WAV sound effects + music (already done)
├── README.md
├── assets/
│   ├── images/          Generated PNG sprites (boat, fish, trash, scenery)
│   ├── sounds/          Generated WAV sound effects + background music
│   └── fonts/           Optional custom fonts
└── data/
    └── highscore.txt    Auto-created; stores the saved high score
```

The game still works perfectly even if any of these image/sound files are
deleted — `data_manager.py` safely falls back to drawn shapes and silence,
exactly as required for a crash-proof student project.
