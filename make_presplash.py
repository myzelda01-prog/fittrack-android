"""Regenerate presplash.png with plate + fork + knife + caption.

Output:
  presplash.png  (1448x1448)
"""
import os
from PIL import Image, ImageDraw, ImageFont

SIZE = 1448
BG_NAVY   = (15, 22, 35, 255)
WHITE     = (255, 255, 255, 255)
CYAN      = (51, 153, 204, 255)

img = Image.new("RGBA", (SIZE, SIZE), BG_NAVY)
d = ImageDraw.Draw(img)

# Plate (matches the main app icon)
cx, cy = SIZE // 2, SIZE // 2 - 100
plate_r = int(SIZE * 0.18)
d.ellipse([cx - plate_r, cy - plate_r, cx + plate_r, cy + plate_r],
          outline=CYAN, width=int(SIZE * 0.012))
d.ellipse([cx - plate_r + int(SIZE * 0.03), cy - plate_r + int(SIZE * 0.03),
           cx + plate_r - int(SIZE * 0.03), cy + plate_r - int(SIZE * 0.03)],
          fill=WHITE)

# Fork (left)
fx = cx - int(SIZE * 0.08)
fy_top = cy - int(SIZE * 0.09)
fy_bot = cy + int(SIZE * 0.09)
d.rounded_rectangle([fx - int(SIZE*0.006), fy_top + int(SIZE*0.05),
                     fx + int(SIZE*0.006), fy_bot],
                    radius=int(SIZE*0.006), fill=BG_NAVY)
for dx in (-int(SIZE*0.025), 0, int(SIZE*0.025)):
    d.rounded_rectangle([fx + dx - int(SIZE*0.004), fy_top,
                         fx + dx + int(SIZE*0.004), fy_top + int(SIZE*0.07)],
                        radius=int(SIZE*0.004), fill=BG_NAVY)

# Knife (right)
kx = cx + int(SIZE * 0.08)
d.polygon([
    (kx, fy_top),
    (kx + int(SIZE*0.020), fy_top + int(SIZE*0.02)),
    (kx + int(SIZE*0.020), fy_bot - int(SIZE*0.05)),
    (kx - int(SIZE*0.003), fy_bot),
    (kx - int(SIZE*0.003), fy_top + int(SIZE*0.02)),
], fill=BG_NAVY)

# Caption
def find_font(size):
    for name in (r"C:\Windows\Fonts\segoeuib.ttf",
                 r"C:\Windows\Fonts\arialbd.ttf",
                 r"C:\Windows\Fonts\segoeui.ttf",
                 r"C:\Windows\Fonts\arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()

font = find_font(int(SIZE * 0.10))
text = "FITTRACK AI"
bbox = d.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
d.text(((SIZE - tw) / 2 - bbox[0], cy + plate_r + 80),
       text, font=font, fill=WHITE)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presplash.png")
img.save(out, "PNG")
print(f"wrote {out}  ({os.path.getsize(out)} bytes)")