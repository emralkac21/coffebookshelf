import sqlite3
import os
import calendar
from datetime import datetime, date, timedelta
from utils.constants import DB_PATH

_instance = None


def get_db() -> "DatabaseManager":
    global _instance
    if _instance is None:
        _instance = DatabaseManager()
    return _instance


class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH
        self._conn: sqlite3.Connection | None = None
        self._init_database()

    def _conn_get(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    def _init_database(self):
        c = self._conn_get()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS books (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                title           TEXT    NOT NULL,
                author          TEXT    DEFAULT '',
                isbn            TEXT    DEFAULT '',
                genre           TEXT    DEFAULT 'Diğer',
                total_pages     INTEGER DEFAULT 0,
                current_page    INTEGER DEFAULT 0,
                status          TEXT    DEFAULT 'to_read',
                rating          REAL    DEFAULT 0,
                cover_path      TEXT    DEFAULT '',
                notes           TEXT    DEFAULT '',
                start_date      TEXT    DEFAULT '',
                end_date        TEXT    DEFAULT '',
                added_date      TEXT    DEFAULT '',
                year_published  INTEGER DEFAULT 0,
                publisher       TEXT    DEFAULT '',
                language        TEXT    DEFAULT 'tr',
                description     TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS reading_sessions (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id          INTEGER NOT NULL,
                date             TEXT    NOT NULL,
                duration_seconds INTEGER DEFAULT 0,
                pages_read       INTEGER DEFAULT 0,
                start_page       INTEGER DEFAULT 0,
                end_page         INTEGER DEFAULT 0,
                notes            TEXT    DEFAULT '',
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS quotes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id     INTEGER NOT NULL,
                quote       TEXT    NOT NULL,
                page        INTEGER DEFAULT 0,
                added_date  TEXT    DEFAULT '',
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS goals (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                year          INTEGER NOT NULL UNIQUE,
                books_target  INTEGER DEFAULT 0,
                pages_target  INTEGER DEFAULT 0,
                hours_target  INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT DEFAULT ''
            );
        """)
        c.commit()

        defaults = [
            ("theme", "dark"),
            ("language", "tr"),
            ("reading_speed", "40"),
        ]
        for key, val in defaults:
            c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))
        c.commit()

    # ─── Books ────────────────────────────────────────────────────────────────

    def add_book(self, data: dict) -> int:
        c = self._conn_get()
        cur = c.execute("""
            INSERT INTO books (title, author, isbn, genre, total_pages, current_page,
                status, rating, cover_path, notes, start_date, end_date, added_date,
                year_published, publisher, language, description)
            VALUES (:title,:author,:isbn,:genre,:total_pages,:current_page,
                :status,:rating,:cover_path,:notes,:start_date,:end_date,:added_date,
                :year_published,:publisher,:language,:description)
        """, {
            "title":         data.get("title", ""),
            "author":        data.get("author", ""),
            "isbn":          data.get("isbn", ""),
            "genre":         data.get("genre", "Diğer"),
            "total_pages":   data.get("total_pages", 0),
            "current_page":  data.get("current_page", 0),
            "status":        data.get("status", "to_read"),
            "rating":        data.get("rating", 0),
            "cover_path":    data.get("cover_path", ""),
            "notes":         data.get("notes", ""),
            "start_date":    data.get("start_date", ""),
            "end_date":      data.get("end_date", ""),
            "added_date":    datetime.now().strftime("%Y-%m-%d"),
            "year_published":data.get("year_published", 0),
            "publisher":     data.get("publisher", ""),
            "language":      data.get("language", "tr"),
            "description":   data.get("description", ""),
        })
        c.commit()
        return cur.lastrowid

    def update_book(self, book_id: int, data: dict):
        c = self._conn_get()
        fields = ", ".join(f"{k} = ?" for k in data)
        vals = list(data.values()) + [book_id]
        c.execute(f"UPDATE books SET {fields} WHERE id = ?", vals)
        c.commit()

    def delete_book(self, book_id: int):
        c = self._conn_get()
        c.execute("DELETE FROM books WHERE id = ?", (book_id,))
        c.commit()

    def get_book(self, book_id: int):
        return self._conn_get().execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()

    def get_all_books(self, status=None, genre=None, search=None):
        c = self._conn_get()
        q = "SELECT * FROM books WHERE 1=1"
        p = []
        if status and status not in ("Tümü", "all"):
            from utils.constants import STATUS_KEYS_FROM_LABEL
            real = STATUS_KEYS_FROM_LABEL.get(status, status)
            q += " AND status = ?"; p.append(real)
        if genre and genre != "Tümü":
            q += " AND genre = ?"; p.append(genre)
        if search:
            s = f"%{search}%"
            q += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)"; p += [s, s, s]
        q += " ORDER BY added_date DESC"
        return c.execute(q, p).fetchall()

    def get_currently_reading(self):
        return self._conn_get().execute(
            "SELECT * FROM books WHERE status = 'reading' ORDER BY start_date DESC"
        ).fetchall()

    # ─── Sessions ─────────────────────────────────────────────────────────────

    def add_session(self, data: dict) -> int:
        c = self._conn_get()
        cur = c.execute("""
            INSERT INTO reading_sessions
                (book_id, date, duration_seconds, pages_read, start_page, end_page, notes)
            VALUES (:book_id,:date,:duration_seconds,:pages_read,:start_page,:end_page,:notes)
        """, {
            "book_id":          data["book_id"],
            "date":             data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "duration_seconds": data.get("duration_seconds", 0),
            "pages_read":       data.get("pages_read", 0),
            "start_page":       data.get("start_page", 0),
            "end_page":         data.get("end_page", 0),
            "notes":            data.get("notes", ""),
        })
        c.commit()
        return cur.lastrowid

    def delete_session(self, session_id: int):
        c = self._conn_get()
        c.execute("DELETE FROM reading_sessions WHERE id = ?", (session_id,))
        c.commit()

    def get_sessions_for_book(self, book_id: int):
        return self._conn_get().execute(
            "SELECT * FROM reading_sessions WHERE book_id = ? ORDER BY date DESC, id DESC",
            (book_id,)
        ).fetchall()

    def get_sessions_range(self, start: str, end: str):
        return self._conn_get().execute(
            """SELECT rs.*, b.title, b.author FROM reading_sessions rs
               JOIN books b ON rs.book_id = b.id
               WHERE rs.date BETWEEN ? AND ? ORDER BY rs.date""",
            (start, end)
        ).fetchall()

    def get_today_stats(self):
        today = date.today().strftime("%Y-%m-%d")
        rows = self.get_sessions_range(today, today)
        return {
            "sessions": len(rows),
            "pages":   sum(r["pages_read"] for r in rows),
            "seconds": sum(r["duration_seconds"] for r in rows),
        }

    def get_month_stats(self, year: int, month: int):
        last_day = calendar.monthrange(year, month)[1]
        start = f"{year}-{month:02d}-01"
        end   = f"{year}-{month:02d}-{last_day:02d}"
        rows  = self.get_sessions_range(start, end)
        return {
            "pages":   sum(r["pages_read"] for r in rows),
            "seconds": sum(r["duration_seconds"] for r in rows),
        }

    # ─── Statistics ───────────────────────────────────────────────────────────

    def get_streak(self) -> int:
        rows = self._conn_get().execute(
            "SELECT DISTINCT date FROM reading_sessions ORDER BY date DESC"
        ).fetchall()
        if not rows:
            return 0
        date_set = {datetime.strptime(r["date"], "%Y-%m-%d").date() for r in rows}
        today = date.today()
        start = today if today in date_set else today - timedelta(days=1)
        streak, cur = 0, start
        while cur in date_set:
            streak += 1
            cur -= timedelta(days=1)
        return streak

    def get_total_stats(self) -> dict:
        c = self._conn_get()
        books_read   = c.execute("SELECT COUNT(*) FROM books WHERE status='read'").fetchone()[0]
        total_books  = c.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        total_pages  = c.execute("SELECT COALESCE(SUM(pages_read),0) FROM reading_sessions").fetchone()[0]
        total_secs   = c.execute("SELECT COALESCE(SUM(duration_seconds),0) FROM reading_sessions").fetchone()[0]
        return {
            "books_read":   books_read,
            "total_books":  total_books,
            "total_pages":  total_pages,
            "total_hours":  round(total_secs / 3600, 1),
            "total_seconds":total_secs,
        }

    def get_yearly_monthly(self, year: int) -> list:
        c = self._conn_get()
        result = []
        for m in range(1, 13):
            last = calendar.monthrange(year, m)[1]
            s, e = f"{year}-{m:02d}-01", f"{year}-{m:02d}-{last:02d}"
            row = c.execute(
                """SELECT COALESCE(SUM(pages_read),0) pages,
                          COALESCE(SUM(duration_seconds),0) secs
                   FROM reading_sessions WHERE date BETWEEN ? AND ?""", (s, e)
            ).fetchone()
            result.append({"month": m, "pages": row["pages"], "hours": row["secs"] / 3600})
        return result

    def get_genre_stats(self) -> list:
        return self._conn_get().execute(
            """SELECT genre, COUNT(*) cnt FROM books
               WHERE status='read' AND genre!=''
               GROUP BY genre ORDER BY cnt DESC"""
        ).fetchall()

    def get_daily_pages(self, year: int) -> dict:
        rows = self._conn_get().execute(
            """SELECT date, SUM(pages_read) pages FROM reading_sessions
               WHERE date LIKE ? GROUP BY date""", (f"{year}-%",)
        ).fetchall()
        return {r["date"]: r["pages"] for r in rows}

    def get_finished_per_month(self, year: int) -> dict:
        rows = self._conn_get().execute(
            """SELECT substr(end_date,1,7) mon, COUNT(*) cnt FROM books
               WHERE status='read' AND end_date LIKE ?
               GROUP BY mon ORDER BY mon""", (f"{year}-%",)
        ).fetchall()
        return {r["mon"]: r["cnt"] for r in rows}

    # ─── Quotes ───────────────────────────────────────────────────────────────

    def add_quote(self, book_id: int, quote: str, page: int = 0):
        c = self._conn_get()
        c.execute(
            "INSERT INTO quotes (book_id, quote, page, added_date) VALUES (?,?,?,?)",
            (book_id, quote, page, datetime.now().strftime("%Y-%m-%d"))
        )
        c.commit()

    def get_quotes(self, book_id: int):
        return self._conn_get().execute(
            "SELECT * FROM quotes WHERE book_id=? ORDER BY added_date DESC", (book_id,)
        ).fetchall()

    def delete_quote(self, quote_id: int):
        c = self._conn_get()
        c.execute("DELETE FROM quotes WHERE id=?", (quote_id,))
        c.commit()

    # ─── Goals ────────────────────────────────────────────────────────────────

    def get_goal(self, year: int):
        return self._conn_get().execute(
            "SELECT * FROM goals WHERE year=?", (year,)
        ).fetchone()

    def set_goal(self, year: int, books: int, pages: int, hours: int):
        c = self._conn_get()
        c.execute(
            "INSERT OR REPLACE INTO goals (year,books_target,pages_target,hours_target) VALUES (?,?,?,?)",
            (year, books, pages, hours)
        )
        c.commit()

    # ─── Settings ─────────────────────────────────────────────────────────────

    def get_setting(self, key: str, default: str = "") -> str:
        row = self._conn_get().execute(
            "SELECT value FROM settings WHERE key=?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        c = self._conn_get()
        c.execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (key, value))
        c.commit()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
