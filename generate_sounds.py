"""
generate_sounds.py
-------------------
Generates all sound effects and background music for AquaClean using
simple waveform synthesis (sine/square waves with fade envelopes).
No copyrighted audio, no downloads, no external libraries beyond
numpy and Python's built-in wave module.

Run with:
    python generate_sounds.py
"""

import os
import wave
import struct
import numpy as np

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sounds")
os.makedirs(OUT_DIR, exist_ok=True)

SAMPLE_RATE = 44100


def envelope(n, attack=0.02, release=0.15):
    """Simple linear fade-in/fade-out envelope to avoid clicky sound edges."""
    env = np.ones(n)
    a = int(n * attack)
    r = int(n * release)
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    if r > 0:
        env[-r:] = np.linspace(1, 0, r)
    return env


def tone(freq, duration, volume=0.5, wave_type="sine", fm=None):
    """Generate a single tone as a numpy float array in range [-1, 1]."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    if callable(freq):
        f = freq(t)
    else:
        f = freq
    if wave_type == "sine":
        wave_data = np.sin(2 * np.pi * f * t)
    elif wave_type == "square":
        wave_data = np.sign(np.sin(2 * np.pi * f * t))
    elif wave_type == "triangle":
        wave_data = 2 * np.abs(2 * (t * f - np.floor(t * f + 0.5))) - 1
    else:
        wave_data = np.sin(2 * np.pi * f * t)
    wave_data *= envelope(len(wave_data)) * volume
    return wave_data


def save_wav(samples, filename):
    """Save a numpy float array (range -1..1) as a 16-bit mono WAV file."""
    samples = np.clip(samples, -1, 1)
    int_samples = (samples * 32767).astype(np.int16)
    path = os.path.join(OUT_DIR, filename)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(int_samples.tobytes())
    print("Created:", path)


def concat(*parts, gap=0.0):
    """Join several tone arrays together with an optional silent gap between them."""
    silence = np.zeros(int(SAMPLE_RATE * gap))
    pieces = []
    for i, p in enumerate(parts):
        pieces.append(p)
        if i != len(parts) - 1 and gap > 0:
            pieces.append(silence)
    return np.concatenate(pieces)


# ---------------------------------------------------------------------------
# COLLECT SOUND - short, cheerful upward chime
# ---------------------------------------------------------------------------
def make_collect():
    a = tone(880, 0.07, volume=0.4, wave_type="sine")
    b = tone(1175, 0.09, volume=0.4, wave_type="sine")
    return concat(a, b)


# ---------------------------------------------------------------------------
# FISH HIT - short descending "buzz" warning
# ---------------------------------------------------------------------------
def make_fish_hit():
    freq_fn = lambda t: 300 - 150 * (t / t[-1])
    return tone(freq_fn, 0.25, volume=0.45, wave_type="square")


# ---------------------------------------------------------------------------
# CLICK - very short neutral blip for buttons
# ---------------------------------------------------------------------------
def make_click():
    return tone(700, 0.05, volume=0.3, wave_type="triangle")


# ---------------------------------------------------------------------------
# LEVEL COMPLETE - short rising three-note arpeggio
# ---------------------------------------------------------------------------
def make_level_complete():
    a = tone(523, 0.12, volume=0.4)   # C5
    b = tone(659, 0.12, volume=0.4)   # E5
    c = tone(784, 0.22, volume=0.45)  # G5
    return concat(a, b, c, gap=0.01)


# ---------------------------------------------------------------------------
# GAME OVER - short descending sad tone
# ---------------------------------------------------------------------------
def make_game_over():
    a = tone(392, 0.18, volume=0.4)   # G4
    b = tone(330, 0.18, volume=0.4)   # E4
    c = tone(262, 0.35, volume=0.45)  # C4
    return concat(a, b, c, gap=0.02)


# ---------------------------------------------------------------------------
# BACKGROUND MUSIC - a calm, looping ambient pad (no percussion, no melody
# theft - purely synthesized sustained chords so it loops smoothly)
# ---------------------------------------------------------------------------
def make_background_music():
    duration = 8.0
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

    # A gentle underwater-feeling chord (C major add9-ish, low volume, slow vibrato)
    freqs = [130.8, 164.8, 196.0, 220.0]  # C3, E3, G3, A3
    mix = np.zeros_like(t)
    for f in freqs:
        vibrato = 1 + 0.003 * np.sin(2 * np.pi * 0.15 * t)
        mix += np.sin(2 * np.pi * f * vibrato * t)
    mix /= len(freqs)

    # Slow volume swell so the loop breathes rather than sounding static
    swell = 0.5 + 0.15 * np.sin(2 * np.pi * (1 / duration) * t)
    mix *= swell * 0.35

    # Fade the very start/end so the loop point isn't a click
    fade_len = int(SAMPLE_RATE * 0.5)
    mix[:fade_len] *= np.linspace(0, 1, fade_len)
    mix[-fade_len:] *= np.linspace(1, 0, fade_len)

    return mix


if __name__ == "__main__":
    save_wav(make_collect(), "collect.wav")
    save_wav(make_fish_hit(), "fish_hit.wav")
    save_wav(make_click(), "click.wav")
    save_wav(make_level_complete(), "level_complete.wav")
    save_wav(make_game_over(), "game_over.wav")
    save_wav(make_background_music(), "background_music.wav")
    print("\nAll sound effects generated successfully in assets/sounds/")
