"""
generate_assets.py
-------------------
Generates all image assets for AquaClean as original, simple vector-style
PNG art using Pillow. This is a one-time build step (run once before playing
the game) so that the game has real image files instead of only relying on
its built-in shape fallback.

No AI image generation, no external downloads, no copyrighted material —
everything here is drawn programmatically with basic 2D shapes, so it is
safe to include in a student project.

Run with:
    python generate_assets.py
"""

import os
import math
from PIL import Image, ImageDraw, ImageFilter

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images")
os.makedirs(OUT_DIR, exist_ok=True)


def save(img, name):
    path = os.path.join(OUT_DIR, name)
    img.save(path)
    print("Created:", path)


def new_canvas(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def soft_shadow(img, ellipse_box, opacity=70):
    """Draw a soft blurred shadow ellipse under an object for a bit of depth."""
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)
    d.ellipse(ellipse_box, fill=(0, 0, 0, opacity))
    shadow = shadow.filter(ImageFilter.GaussianBlur(3))
    img.alpha_composite(shadow)


# ---------------------------------------------------------------------------
# BOAT (realistic small wooden fishing boat, two frames for gentle bobbing)
# ---------------------------------------------------------------------------
def make_boat(frame=0):
    w, h = 140, 64
    img = new_canvas((w, h))
    draw = ImageDraw.Draw(img)

    bob = -2 if frame == 1 else 0
    wood = (150, 105, 60, 255)
    wood_dark = (110, 75, 40, 255)
    wood_light = (175, 130, 80, 255)

    hull_left = 30
    hull_right = w - 40

    # shadow under the hull
    soft_shadow(img, (hull_left + 4, 44 + bob, hull_right + 4, 52 + bob), opacity=55)

    # hull: flat-bottomed dinghy shape, tapering to a point at the bow (right side)
    top_y = 20 + bob
    bottom_y = 42 + bob
    hull = [
        (hull_left, top_y + 6), (hull_left + 8, top_y), (hull_right - 6, top_y),
        (hull_right + 14, top_y + 10),          # pointed bow
        (hull_right - 6, bottom_y), (hull_left + 4, bottom_y),
    ]
    draw.polygon(hull, fill=wood, outline=wood_dark)

    # plank lines (wood texture) along the hull
    for i in range(3):
        ly = top_y + 6 + i * 6
        draw.line((hull_left + 6, ly, hull_right - 2, ly), fill=wood_dark, width=1)

    # interior (inside of the boat, slightly darker open area)
    interior = [(hull_left + 10, top_y + 4), (hull_right - 4, top_y + 4),
                (hull_right + 6, top_y + 9), (hull_left + 8, top_y + 9)]
    draw.polygon(interior, fill=(95, 65, 35, 255))

    # bench seat
    seat_x = hull_left + 24
    draw.rectangle((seat_x, top_y + 2, seat_x + 20, top_y + 6), fill=wood_light, outline=wood_dark)

    # small outboard motor at the stern (left side)
    motor_body = (hull_left - 10, top_y + 2, hull_left, bottom_y + 4)
    draw.rounded_rectangle(motor_body, radius=2, fill=(60, 60, 65, 255), outline=(30, 30, 35, 255))
    draw.rectangle((hull_left - 7, bottom_y, hull_left - 3, bottom_y + 8), fill=(40, 40, 45, 255))

    # fisherman's rod leaning from the bow, with a line and small hook
    rod_base = (hull_right - 2, top_y + 2)
    rod_tip = (hull_right + 26, top_y - 20)
    draw.line([rod_base, rod_tip], fill=(90, 60, 30, 255), width=2)
    line_end = (rod_tip[0] - 4, rod_tip[1] + 34)
    draw.line([rod_tip, line_end], fill=(220, 220, 220, 200), width=1)
    draw.ellipse((line_end[0] - 2, line_end[1] - 2, line_end[0] + 2, line_end[1] + 2),
                 outline=(80, 80, 80, 255))

    # small catch bucket resting in the middle of the boat
    bucket_x = hull_left + 50
    bucket = (bucket_x, top_y + 1, bucket_x + 12, top_y + 8)
    draw.rounded_rectangle(bucket, radius=1, fill=(70, 130, 150, 255), outline=(40, 90, 110, 255))

    # cleaning net trailing behind the boat (functional gameplay element)
    net_bob = 3 if (frame == 1) else -3
    net_center = (hull_left - 22, (top_y + bottom_y) // 2 + net_bob)
    draw.line((hull_left - 10, (top_y + bottom_y) // 2, net_center[0], net_center[1]),
              fill=(90, 90, 90, 255), width=2)
    draw.ellipse((net_center[0] - 9, net_center[1] - 9, net_center[0] + 9, net_center[1] + 9),
                 outline=(230, 200, 60, 255), width=2)

    return img


# ---------------------------------------------------------------------------
# ALGAE / WATER PLANT OBSTACLE
# ---------------------------------------------------------------------------
def make_algae():
    w, h = 60, 44
    img = new_canvas((w, h))
    draw = ImageDraw.Draw(img)

    dark_green = (35, 95, 50, 255)
    mid_green = (55, 130, 70, 230)
    light_green = (85, 160, 95, 200)

    # cluster of overlapping leafy blobs to read as a thick patch of weeds
    blobs = [
        (6, 14, 30, 40, mid_green),
        (20, 6, 44, 34, dark_green),
        (32, 16, 56, 42, light_green),
        (14, 22, 38, 44, dark_green),
    ]
    for (x0, y0, x1, y1, color) in blobs:
        draw.ellipse((x0, y0, x1, y1), fill=color, outline=(25, 75, 40, 255))

    # a few thin reed strokes poking up for extra texture
    for rx in (14, 28, 42):
        draw.line((rx, 20, rx - 3, 2), fill=(40, 110, 55, 220), width=2)

    return img


# ---------------------------------------------------------------------------
# FISH (two frames: tail up / tail down for a swimming animation)
# ---------------------------------------------------------------------------
def make_fish(frame=0):
    w, h = 64, 36
    img = new_canvas((w, h))
    draw = ImageDraw.Draw(img)

    tail_shift = 6 if frame == 1 else -6

    body_color = (250, 150, 40, 255)
    body_dark = (210, 110, 20, 255)

    # body
    draw.ellipse((16, 6, 52, 30), fill=body_color, outline=body_dark)
    # belly highlight
    draw.ellipse((20, 16, 46, 28), fill=(255, 200, 130, 180))

    # tail (animated)
    draw.polygon([(16, 18), (2, 8 + tail_shift), (2, 28 - tail_shift)], fill=body_color, outline=body_dark)

    # top fin
    draw.polygon([(28, 6), (34, -4), (40, 6)], fill=body_color, outline=body_dark)

    # eye
    draw.ellipse((42, 12, 48, 18), fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
    draw.ellipse((44, 14, 47, 17), fill=(20, 20, 20, 255))

    return img


# ---------------------------------------------------------------------------
# POLLUTION OBJECTS
# ---------------------------------------------------------------------------
def make_bottle():
    w, h = 28, 40
    img = new_canvas((w, h))
    draw = ImageDraw.Draw(img)
    body_color = (180, 225, 235, 230)
    outline = (100, 160, 175, 255)

    draw.rounded_rectangle((6, 12, w - 6, h - 4), radius=6, fill=body_color, outline=outline, width=2)
    draw.rectangle((10, 4, w - 10, 14), fill=body_color, outline=outline)
    draw.rectangle((11, 0, w - 11, 6), fill=(150, 190, 200, 255), outline=outline)  # cap
    draw.line((9, 20, w - 9, 20), fill=(255, 255, 255, 120), width=2)  # label line
    return img


def make_bag():
    w, h = 30, 26
    img = new_canvas((w, h))
    draw = ImageDraw.Draw(img)
    color = (235, 235, 150, 220)
    outline = (170, 170, 90, 255)
    draw.ellipse((0, 4, w, h), fill=color, outline=outline, width=2)
    # handle
    draw.arc((8, -6, 22, 10), start=200, end=340, fill=outline, width=2)
    draw.line((4, 14, w - 4, 10), fill=(255, 255, 255, 130), width=1)
    return img


def make_garbage():
    w, h = 32, 28
    img = new_canvas((w, h))
    draw = ImageDraw.Draw(img)
    colors = [(150, 110, 70, 255), (120, 150, 90, 255), (200, 170, 120, 255)]
    draw.polygon([(2, h - 2), (6, 4), (16, 8), (26, 2), (w - 2, h - 2)], fill=colors[0], outline=(60, 40, 20, 255))
    draw.polygon([(10, h - 2), (14, 10), (22, 14), (24, h - 2)], fill=colors[1], outline=(40, 60, 30, 255))
    draw.ellipse((4, h - 8, 12, h), fill=colors[2], outline=(90, 70, 40, 255))
    return img


def make_oil():
    w, h = 40, 26
    img = new_canvas((w, h))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 4, w, h), fill=(35, 35, 40, 235), outline=(10, 10, 10, 255), width=2)
    draw.ellipse((6, 8, 18, 16), fill=(70, 70, 80, 160))  # sheen highlight
    draw.ellipse((22, 12, 34, 20), fill=(60, 60, 70, 120))
    return img


# ---------------------------------------------------------------------------
# ENVIRONMENT DECORATIONS
# ---------------------------------------------------------------------------
def make_tree():
    w, h = 40, 54
    img = new_canvas((w, h))
    draw = ImageDraw.Draw(img)
    draw.rectangle((17, 30, 23, h), fill=(110, 75, 40, 255))  # trunk
    draw.ellipse((2, 0, w - 2, 36), fill=(46, 120, 55, 255), outline=(25, 80, 35, 255))
    draw.ellipse((8, 6, w - 10, 30), fill=(60, 145, 70, 200))
    return img


def make_rock():
    w, h = 30, 20
    img = new_canvas((w, h))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 4, w, h), fill=(140, 140, 140, 255), outline=(90, 90, 90, 255))
    draw.ellipse((4, 6, w - 12, h - 6), fill=(170, 170, 170, 180))
    return img


def make_bubble():
    w = h = 20
    img = new_canvas((w, h))
    draw = ImageDraw.Draw(img)
    draw.ellipse((1, 1, w - 1, h - 1), outline=(220, 245, 255, 220), width=2)
    draw.ellipse((4, 4, 9, 9), fill=(255, 255, 255, 160))
    return img


def make_logo_wave_tile():
    """A small seamless-ish horizontal wave tile used for menu background texture."""
    w, h = 120, 40
    img = new_canvas((w, h))
    draw = ImageDraw.Draw(img)
    for i in range(-10, w + 10, 20):
        draw.arc((i, 6, i + 24, 26), start=200, end=340, fill=(70, 160, 210, 200), width=3)
    return img


if __name__ == "__main__":
    save(make_boat(0), "boat.png")
    save(make_boat(1), "boat_bob.png")
    save(make_fish(0), "fish_a.png")
    save(make_fish(1), "fish_b.png")
    save(make_bottle(), "bottle.png")
    save(make_bag(), "bag.png")
    save(make_garbage(), "garbage.png")
    save(make_oil(), "oil.png")
    save(make_algae(), "algae.png")
    save(make_tree(), "tree.png")
    save(make_rock(), "rock.png")
    save(make_bubble(), "bubble.png")
    save(make_logo_wave_tile(), "wave_tile.png")
    print("\nAll images generated successfully in assets/images/")
