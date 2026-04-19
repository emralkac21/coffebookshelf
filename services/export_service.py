"""
Export & import library data (CSV / JSON / DB backup).
"""
import csv
import json
import shutil
import os
from datetime import datetime
from database.db_manager import get_db
from utils.constants import STATUS_LABELS


def export_csv(filepath: str) -> bool:
    db = get_db()
    books = db.get_all_books()
    if not filepath.endswith(".csv"):
        filepath += ".csv"
    try:
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            fieldnames = [
                "title", "author", "isbn", "genre", "status_label",
                "total_pages", "current_page", "rating", "start_date",
                "end_date", "added_date", "year_published", "publisher",
                "notes", "description",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for b in books:
                writer.writerow({
                    "title":         b["title"],
                    "author":        b["author"],
                    "isbn":          b["isbn"],
                    "genre":         b["genre"],
                    "status_label":  STATUS_LABELS.get(b["status"], b["status"]),
                    "total_pages":   b["total_pages"],
                    "current_page":  b["current_page"],
                    "rating":        b["rating"],
                    "start_date":    b["start_date"],
                    "end_date":      b["end_date"],
                    "added_date":    b["added_date"],
                    "year_published":b["year_published"],
                    "publisher":     b["publisher"],
                    "notes":         b["notes"],
                    "description":   b["description"],
                })
        return True
    except Exception as e:
        print(f"CSV export error: {e}")
        return False


def export_json(filepath: str) -> bool:
    db = get_db()
    books = db.get_all_books()
    if not filepath.endswith(".json"):
        filepath += ".json"
    try:
        data = []
        for b in books:
            book_dict = dict(b)
            book_dict["status_label"] = STATUS_LABELS.get(b["status"], b["status"])
            sessions = db.get_sessions_for_book(b["id"])
            book_dict["sessions"] = [dict(s) for s in sessions]
            quotes = db.get_quotes(b["id"])
            book_dict["quotes"] = [dict(q) for q in quotes]
            data.append(book_dict)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"JSON export error: {e}")
        return False


def backup_database(dest_path: str) -> bool:
    from utils.constants import DB_PATH
    try:
        if not dest_path.endswith(".db"):
            dest_path += ".db"
        shutil.copy2(DB_PATH, dest_path)
        return True
    except Exception as e:
        print(f"Backup error: {e}")
        return False


def restore_database(src_path: str) -> bool:
    from utils.constants import DB_PATH
    try:
        shutil.copy2(src_path, DB_PATH)
        return True
    except Exception as e:
        print(f"Restore error: {e}")
        return False
