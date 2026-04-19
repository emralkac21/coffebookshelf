import os
import io
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont
import customtkinter as ctk


def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}dk {s:02d}s"
    h, rem = divmod(seconds, 3600)
    m = rem // 60
    return f"{h}s {m:02d}dk"


def format_duration_short(seconds: int) -> str:
    if seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m:02d}:{s:02d}"
    h, rem = divmod(seconds, 3600)
    m = rem // 60
    return f"{h:02d}:{m:02d}:{rem % 60:02d}"


def parse_date(s: str):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def progress_percent(current: int, total: int) -> float:
    if not total:
        return 0.0
    return min(100.0, round(current / total * 100, 1))


def make_default_cover(title: str, author: str, size=(180, 270)) -> Image.Image:
    """Generate a simple colored placeholder cover."""
    import hashlib
    h = int(hashlib.md5(title.encode()).hexdigest()[:6], 16)
    r = (h >> 16) & 0xFF
    g = (h >> 8) & 0xFF
    b = h & 0xFF
    # Desaturate a bit for elegance
    avg = (r + g + b) // 3
    r = (r + avg) // 2
    g = (g + avg) // 2
    b = (b + avg) // 2
    bg = (max(30, r - 60), max(30, g - 60), max(30, b - 60))
    fg = (min(255, r + 80), min(255, g + 80), min(255, b + 80))

    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)

    # Draw decorative border
    draw.rectangle([8, 8, size[0]-9, size[1]-9], outline=fg, width=2)
    draw.rectangle([12, 12, size[0]-13, size[1]-13], outline=(*fg, 80), width=1)

    # Try to draw text
    def wrap(text, max_chars=14):
        words = text.split()
        lines, line = [], ""
        for w in words:
            if len(line) + len(w) + 1 <= max_chars:
                line = (line + " " + w).strip()
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines

    title_lines = wrap(title, 13)
    y = size[1] // 2 - len(title_lines) * 14
    for line in title_lines[:4]:
        tw = len(line) * 7
        draw.text(((size[0] - tw) // 2, y), line, fill=(240, 230, 210))
        y += 18

    if author:
        y += 8
        aw = len(author[:16]) * 5
        draw.text(((size[0] - aw) // 2, y), author[:16], fill=(*fg,))

    return img


def load_cover_image(path: str, size=(120, 180)) -> ctk.CTkImage | None:
    """Load a cover image as CTkImage, return None on failure."""
    try:
        if path and os.path.exists(path):
            img = Image.open(path).convert("RGB")
        else:
            return None
        img = img.resize(size, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        return None


def load_or_generate_cover(path: str, title: str, author: str, size=(120, 180)) -> ctk.CTkImage:
    """Load cover image or generate a placeholder."""
    img_ctk = load_cover_image(path, size)
    if img_ctk:
        return img_ctk
    img = make_default_cover(title, author, size)
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)
