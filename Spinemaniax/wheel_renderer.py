import math
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageTk

class WheelRenderer:
    def __init__(self) -> None:
        self.cached_wheel_image: Optional[Image.Image] = None
        self.cached_wheel_options: List[str] = []
        self.cached_pointer_overlay: Optional[Image.Image] = None

    def invalidate_cache(self) -> None:
        self.cached_wheel_image = None
        self.cached_pointer_overlay = None

    def generate_static_wheel(self, width: int, height: int, options: List[str], colors: List[str]) -> Optional[Image.Image]:
        """Pre-render the static wheel image (without rotation) - called once"""
        render_scale = 3
        img_width = width * render_scale
        img_height = height * render_scale

        n = len(options)
        if n == 0:
            return None

        sector_angle = 360.0 / n
        half_sector = sector_angle / 2.0

        cx = img_width // 2
        cy = img_height // 2
        r = min(cx, cy) - 20 * render_scale

        static_wheel = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(static_wheel)

        draw.ellipse([cx - r - 15, cy - r - 15, cx + r + 15, cy + r + 15], outline="#FFD700", width=15)
        draw.ellipse([cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5], outline="#1a1a1a", width=9)

        # Center hub radius (must match pointer overlay)
        center_hub_r = int(75 * render_scale / 3) + 10 * render_scale // 3

        for i in range(n):
            start_angle = 90 - half_sector + (i * sector_angle)
            end_angle = start_angle + sector_angle
            mid_angle = start_angle + half_sector

            color = colors[i % len(colors)]

            bbox = [cx - r, cy - r, cx + r, cy + r]
            draw.pieslice(bbox, start_angle, end_angle, fill=color, outline="#1a1a1a", width=6)

            option_text = options[i] or f"Option {i + 1}"

            # Available radial space for text (between center hub and outer edge with padding)
            inner_limit = center_hub_r + 10 * render_scale // 3
            outer_limit = r - 15 * render_scale // 3
            available_length = outer_limit - inner_limit

            # Load font
            font = None
            font_paths = [
                "C:\\Windows\\Fonts\\arialbd.ttf",
                "C:\\Windows\\Fonts\\arial.ttf",
                "arial.ttf",
                "Arial.ttf"
            ]

            # Start with a base font size, then scale down if text is too long
            if n <= 2:
                base_size = 50
            elif n == 3:
                base_size = 42
            elif n == 4:
                base_size = 36
            elif n == 5:
                base_size = 30
            elif n == 6:
                base_size = 26
            elif n <= 8:
                base_size = 22
            elif n <= 10:
                base_size = 20
            else:
                base_size = 16

            font_size = int(base_size * render_scale)

            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue
            if font is None:
                font = ImageFont.load_default()

            # Measure text and scale down if it exceeds available radial length
            temp_img = Image.new("RGBA", (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            text_bbox = temp_draw.textbbox((0, 0), option_text, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]

            if text_w > 0 and text_w > available_length * 0.9:
                scale_factor = (available_length * 0.9) / text_w
                font_size = max(int(font_size * scale_factor), 8 * render_scale)
                # Reload font at new size
                font = None
                for font_path in font_paths:
                    try:
                        font = ImageFont.truetype(font_path, font_size)
                        break
                    except:
                        continue
                if font is None:
                    font = ImageFont.load_default()
                # Re-measure
                text_bbox = temp_draw.textbbox((0, 0), option_text, font=font)
                text_w = text_bbox[2] - text_bbox[0]
                text_h = text_bbox[3] - text_bbox[1]

            if text_w <= 0 or text_h <= 0:
                continue

            # Position text at the midpoint of the available radial space
            text_radius = (inner_limit + outer_limit) / 2.0

            angle_rad = math.radians(mid_angle)
            text_x = int(cx + text_radius * math.cos(angle_rad))
            text_y = int(cy + text_radius * math.sin(angle_rad))

            # Create text image large enough to hold rotated text
            max_dim = int(math.sqrt(text_w ** 2 + text_h ** 2) * 1.5)
            if max_dim <= 0:
                continue
            text_img = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
            text_draw_img = ImageDraw.Draw(text_img)

            center_pos = (max_dim // 2, max_dim // 2)

            # Draw shadow
            shadow_offset = max(2, render_scale)
            text_draw_img.text((center_pos[0] + shadow_offset, center_pos[1] + shadow_offset),
                               option_text, font=font, fill=(0, 0, 0, 160), anchor="mm")
            # Draw main text
            text_draw_img.text(center_pos, option_text, font=font, fill="white", anchor="mm")

            # Rotate text to align radially along the sector midline
            # In PIL coords (clockwise from right): mid_angle points outward from center
            # We want text to read from center outward
            # PIL rotate is counterclockwise, so negate
            text_rotation = -mid_angle

            # Flip text on left side of wheel so it's always readable (reads outward)
            mid_normalized = mid_angle % 360
            if 90 < mid_normalized < 270:
                text_rotation += 180

            text_rotated = text_img.rotate(text_rotation, resample=Image.BICUBIC, expand=False)
            paste_pos = (text_x - max_dim // 2, text_y - max_dim // 2)

            try:
                static_wheel.paste(text_rotated, paste_pos, text_rotated)
            except Exception as e:
                print(f"Warning: Could not paste text for sector {i}: {e}")

        return static_wheel

    def generate_pointer_overlay(self, img_width: int, img_height: int, render_scale: int) -> Image.Image:
        overlay = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        cx = img_width // 2
        cy = img_height // 2

        center_r = int(75 * render_scale / 3)
        draw.ellipse([cx - center_r - 6, cy - center_r - 6, cx + center_r + 6, cy + center_r + 6], fill="#2a2a2a")
        draw.ellipse([cx - center_r, cy - center_r, cx + center_r, cy + center_r], fill="#1a1a1a", outline="#FFD700", width=int(12 * render_scale / 3))
        draw.ellipse([cx - center_r + 15, cy - center_r + 15, cx + center_r - 15, cy + center_r - 15], fill="#2a2a2a")

        pointer_scale = render_scale
        pointer_w = int(27 * pointer_scale)
        pointer_h = int(48 * pointer_scale)
        pointer_y = int(12 * pointer_scale)

        shadow_offset = int(3 * pointer_scale)
        pointer_shadow = [(cx - pointer_w + shadow_offset, pointer_y + shadow_offset),
                          (cx + pointer_w + shadow_offset, pointer_y + shadow_offset),
                          (cx + shadow_offset, pointer_y + pointer_h + shadow_offset)]
        draw.polygon(pointer_shadow, fill=(0, 0, 0, 100))

        pointer = [(cx - pointer_w, pointer_y), (cx + pointer_w, pointer_y), (cx, pointer_y + pointer_h)]
        draw.polygon(pointer, fill="#FF3333", outline="#8B0000", width=int(4 * pointer_scale))

        pointer_highlight = [(cx - pointer_w // 2, pointer_y + 6), (cx + pointer_w // 2, pointer_y + 6), (cx, pointer_y + pointer_h - 12)]
        draw.polygon(pointer_highlight, fill="#FF5555")

        ellipse_h = int(30 * pointer_scale)
        draw.ellipse([cx - int(15 * pointer_scale), pointer_y - int(4 * pointer_scale), cx + int(15 * pointer_scale), pointer_y + ellipse_h - int(4 * pointer_scale)], fill="#FF4444", outline="#8B0000", width=int(4 * pointer_scale))
        draw.ellipse([cx - int(9 * pointer_scale), pointer_y + int(1 * pointer_scale), cx + int(9 * pointer_scale), pointer_y + ellipse_h - int(10 * pointer_scale)], fill="#FF6666")

        return overlay

    def get_rotated_wheel_image(self, width: int, height: int, rotation: float, options: List[str], colors: List[str], bg_color: str) -> Optional[ImageTk.PhotoImage]:
        if len(options) == 0:
            return None

        if self.cached_wheel_image is None or self.cached_wheel_options != options:
            self.cached_wheel_image = self.generate_static_wheel(width, height, options, colors)
            self.cached_wheel_options = options.copy()
            self.cached_pointer_overlay = None

        if self.cached_wheel_image is None:
            return None

        bg_rgb = tuple(int(bg_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
        render_scale = 2
        img_width = width * render_scale
        img_height = height * render_scale

        cached_size = self.cached_wheel_image.size
        if cached_size != (img_width, img_height):
            resized_cache = self.cached_wheel_image.resize((img_width, img_height), Image.LANCZOS)
        else:
            resized_cache = self.cached_wheel_image

        if self.cached_pointer_overlay is None or self.cached_pointer_overlay.size != (img_width, img_height):
            self.cached_pointer_overlay = self.generate_pointer_overlay(img_width, img_height, render_scale)

        rotated_wheel = resized_cache.rotate(rotation, expand=False, resample=Image.NEAREST)

        wheel_img = Image.new("RGB", (img_width, img_height), bg_rgb)
        wheel_img.paste(rotated_wheel, (0, 0), rotated_wheel)
        wheel_img.paste(self.cached_pointer_overlay, (0, 0), self.cached_pointer_overlay)

        final_img = wheel_img.resize((width, height), Image.BILINEAR)
        return ImageTk.PhotoImage(final_img)
