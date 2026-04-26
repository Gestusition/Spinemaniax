import random
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageTk

from constants import ADJECTIVES, NOUNS

def generate_random_name() -> str:
    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"

def distribute_probabilities(total: float, num_options: int) -> List[float]:
    base = total / num_options
    probs = [base] * num_options
    probs[-1] = total - sum(probs[:-1])
    return probs

def get_rotated_text_image(text: str, angle: float, font_size: int = 14,
                           text_color: str = "white") -> ImageTk.PhotoImage:
    """Ultra high-DPI text rendering - crystal clear"""
    # ULTRA HIGH DPI - 8x for absolute sharpness
    dpi_scale = 8
    scaled_font_size = font_size * dpi_scale

    # Load best quality font
    font = None
    font_attempts = [
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "arialbd.ttf",
        "arial.ttf"
    ]

    for font_path in font_attempts:
        try:
            font = ImageFont.truetype(font_path, scaled_font_size)
            break
        except:
            continue

    if not font:
        font = ImageFont.load_default()

    # Measure text at high DPI
    temp_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Create high-DPI canvas with padding
    padding = 30 * dpi_scale
    canvas_w = text_w + padding
    canvas_h = text_h + padding

    # Create image with high DPI
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Calculate center position
    text_x = padding // 2
    text_y = padding // 2

    # Draw multiple shadow layers for depth
    shadow_offsets = [(4, 4), (3, 3), (2, 2)]
    shadow_alphas = [220, 180, 140]

    for (dx, dy), alpha in zip(shadow_offsets, shadow_alphas):
        shadow_x = text_x + (dx * dpi_scale)
        shadow_y = text_y + (dy * dpi_scale)
        draw.text((shadow_x, shadow_y), text, font=font, fill=(0, 0, 0, alpha))

    # Draw main text with full opacity
    draw.text((text_x, text_y), text, font=font, fill=text_color)

    # Rotate with highest quality interpolation
    rotated = img.rotate(angle, expand=True, resample=Image.BICUBIC)

    # Downsample for anti-aliasing (this creates the smooth effect)
    final_w = rotated.width // dpi_scale
    final_h = rotated.height // dpi_scale

    # Use LANCZOS for highest quality downsampling
    final_img = rotated.resize((final_w, final_h), Image.LANCZOS)

    return ImageTk.PhotoImage(final_img)
