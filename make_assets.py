"""Generate app icon and presplash for FitTrack AI.

Outputs:
  icon.png        1024x1024  (required by Buildozer)
  presplash.png   1448x1448  (recommended by Buildozer)
  icon-512.png    512x512    (optional, alternate size)
  icon-256.png    256x256    (optional, alternate size)
  icon-128.png    128x128    (optional, alternate size)

Design: dark rounded square, white monogram, small cyan dot accent
        = matches the in-app Kotlin theme.
"""

from PIL import Image, ImageDraw, ImageFont

# Colour palette (matches the app's in-app look)
BG       = (17,  17,  17,  255)   # #111111
PANEL    = (27,  27,  27,  255)   # #1B1B1B
ACCENT   = (51,  153, 204, 255)   # #3399CC   (close to app's cyan)
ACCENT_D = (31,  92,  122, 255)   # #1F5C7A   (darker shade)
WHITE    = (255, 255, 255, 255)
GRAY     = (130, 130, 130, 255)


def find_font(size):
    """Pick a font that actually exists on this Windows box."""
    for name in [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Outer rounded square (the app icon shape)
    pad = int(size * 0.04)
    d.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=int(size * 0.22),
        fill=BG,
    )

    # Inner cyan panel — slightly inset
    inner_pad = int(size * 0.12)
    d.rounded_rectangle(
        [inner_pad, inner_pad, size - inner_pad, size - inner_pad],
        radius=int(size * 0.18),
        fill=PANEL,
    )

    # Accent bar at the top of the inner panel
    bar_h = int(size * 0.06)
    bar_pad = int(size * 0.20)
    d.rounded_rectangle(
        [bar_pad, inner_pad + int(size * 0.04),
         size - bar_pad, inner_pad + int(size * 0.04) + bar_h],
        radius=int(bar_h / 2),
        fill=ACCENT,
    )

    # Monogram — bold "FT"
    f_big = find_font(int(size * 0.42))
    text = "FT"
    # Centre the text
    bbox = d.textbbox((0, 0), text, font=f_big)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (size - tw) / 2 - bbox[0]
    ty = (size - th) / 2 - bbox[1] + int(size * 0.04)
    d.text((tx, ty), text, font=f_big, fill=WHITE)

    # Small cyan dot accent — bottom-right of inner panel
    dot_r = int(size * 0.06)
    dot_cx = size - inner_pad - int(size * 0.12)
    dot_cy = size - inner_pad - int(size * 0.12)
    d.ellipse(
        [dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r],
        fill=ACCENT,
    )

    return img


def draw_presplash(size):
    img = Image.new("RGBA", (size, size), BG)
    d = ImageDraw.Draw(img)

    # Same monogram, centred
    f = find_font(int(size * 0.16))
    text = "FITTRACK AI"
    bbox = d.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]),
           text, font=f, fill=WHITE)

    # Cyan underline
    line_w = int(size * 0.18)
    line_h = max(4, int(size * 0.008))
    line_y = int(size * 0.55)
    d.rounded_rectangle(
        [(size - line_w) / 2, line_y,
         (size + line_w) / 2, line_y + line_h],
        radius=line_h // 2,
        fill=ACCENT,
    )
    return img


def main():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    sizes = [128, 256, 512, 1024]
    for s in sizes:
        img = draw_icon(s)
        path = os.path.join(here, f"icon-{s}.png" if s != 1024 else "icon.png")
        img.save(path, "PNG")
        print(f"  wrote {path}  ({s}x{s})")

    splash = draw_presplash(1448)
    splash.save(os.path.join(here, "presplash.png"), "PNG")
    print("  wrote presplash.png  (1448x1448)")


if __name__ == "__main__":
    main()