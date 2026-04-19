"""
Book search via Open Library API + Google Books API (fallback).
Both run in background threads to keep the UI responsive.
"""
import threading
import requests


OL_SEARCH   = "https://openlibrary.org/search.json"
OL_ISBN     = "https://openlibrary.org/api/books"
GB_SEARCH   = "https://www.googleapis.com/books/v1/volumes"
TIMEOUT     = 8


def _ol_by_isbn(isbn: str) -> dict | None:
    try:
        r = requests.get(OL_ISBN, params={
            "bibkeys": f"ISBN:{isbn}",
            "format":  "json",
            "jscmd":   "data",
        }, timeout=TIMEOUT)
        data = r.json().get(f"ISBN:{isbn}")
        if not data:
            return None
        authors = [a["name"] for a in data.get("authors", [])]
        cover   = data.get("cover", {}).get("large") or \
                  data.get("cover", {}).get("medium") or ""
        return {
            "title":         data.get("title", ""),
            "author":        ", ".join(authors),
            "isbn":          isbn,
            "total_pages":   data.get("number_of_pages", 0),
            "publisher":     ", ".join(p["name"] for p in data.get("publishers", [])),
            "year_published": int(data.get("publish_date", "0")[-4:] or 0),
            "cover_url":     cover,
            "description":   data.get("excerpts", [{}])[0].get("text", ""),
        }
    except Exception:
        return None


def _gb_by_isbn(isbn: str) -> dict | None:
    try:
        r = requests.get(GB_SEARCH, params={"q": f"isbn:{isbn}"}, timeout=TIMEOUT)
        items = r.json().get("items", [])
        if not items:
            return None
        return _parse_gb_item(items[0], isbn)
    except Exception:
        return None


def _gb_by_title(query: str) -> list[dict]:
    try:
        r = requests.get(GB_SEARCH, params={"q": query, "maxResults": 10}, timeout=TIMEOUT)
        items = r.json().get("items", [])
        return [_parse_gb_item(it) for it in items]
    except Exception:
        return []


def _parse_gb_item(item: dict, isbn: str = "") -> dict:
    vi = item.get("volumeInfo", {})
    isbns = {i["type"]: i["identifier"] for i in vi.get("industryIdentifiers", [])}
    real_isbn = isbn or isbns.get("ISBN_13") or isbns.get("ISBN_10") or ""
    thumbnail = vi.get("imageLinks", {}).get("thumbnail", "")
    if thumbnail:
        thumbnail = thumbnail.replace("http://", "https://").replace("zoom=1", "zoom=3")
    try:
        year = int(vi.get("publishedDate", "0")[:4])
    except ValueError:
        year = 0
    return {
        "title":          vi.get("title", ""),
        "author":         ", ".join(vi.get("authors", [])),
        "isbn":           real_isbn,
        "total_pages":    vi.get("pageCount", 0),
        "publisher":      vi.get("publisher", ""),
        "year_published": year,
        "cover_url":      thumbnail,
        "description":    vi.get("description", "")[:500],
        "genre":          vi.get("categories", ["Diğer"])[0] if vi.get("categories") else "Diğer",
    }


def search_by_isbn(isbn: str, callback):
    """Call callback(result_dict | None) on a background thread."""
    def run():
        result = _ol_by_isbn(isbn) or _gb_by_isbn(isbn)
        callback(result)
    threading.Thread(target=run, daemon=True).start()


def search_by_title(query: str, callback):
    """Call callback(list[dict]) on a background thread."""
    def run():
        results = _gb_by_title(query)
        callback(results)
    threading.Thread(target=run, daemon=True).start()
