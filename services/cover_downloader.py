"""
Download book cover images and save them locally.
"""
import os
import threading
import hashlib
import requests
from PIL import Image
from io import BytesIO
from utils.constants import COVERS_DIR

TIMEOUT = 10


def _ensure_dir():
    os.makedirs(COVERS_DIR, exist_ok=True)


def _filename_for(url: str, book_id: int | None = None) -> str:
    if book_id:
        return os.path.join(COVERS_DIR, f"cover_{book_id}.jpg")
    h = hashlib.md5(url.encode()).hexdigest()[:12]
    return os.path.join(COVERS_DIR, f"cover_{h}.jpg")


def download_cover(url: str, book_id: int | None = None, callback=None) -> str | None:
    """
    Download cover from URL synchronously. Returns local path or None.
    If callback provided, runs asynchronously and calls callback(path).
    """
    if callback:
        def run():
            path = _do_download(url, book_id)
            callback(path)
        threading.Thread(target=run, daemon=True).start()
        return None
    return _do_download(url, book_id)


def _do_download(url: str, book_id: int | None) -> str | None:
    if not url:
        return None
    _ensure_dir()
    dest = _filename_for(url, book_id)
    try:
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGB")
        img.save(dest, "JPEG", quality=90)
        return dest
    except Exception:
        return None


def cover_path_for_book(book_id: int) -> str:
    return os.path.join(COVERS_DIR, f"cover_{book_id}.jpg")
