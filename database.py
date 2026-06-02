import sqlite3
from pathlib import Path
from models import Article

DB_PATH = Path(__file__).parent / "data" / "articles.db"


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            url         TEXT UNIQUE NOT NULL,
            source      TEXT NOT NULL,
            published   TEXT NOT NULL,
            summary     TEXT DEFAULT '',
            language    TEXT DEFAULT 'ko',
            sector      TEXT DEFAULT 'defense',
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def _similar_title_exists(conn: sqlite3.Connection, title: str, threshold: float = 0.5) -> bool:
    """최근 48시간 내 유사한 제목이 있으면 True."""
    rows = conn.execute(
        "SELECT title FROM articles WHERE created_at > datetime('now', '-48 hours')"
    ).fetchall()
    new_words = set(title.lower().split())
    if not new_words:
        return False
    for (existing,) in rows:
        existing_words = set(existing.lower().split())
        if not existing_words:
            continue
        overlap = len(new_words & existing_words) / len(new_words | existing_words)
        if overlap >= threshold:
            return True
    return False


def insert_article(article: Article) -> bool:
    """URL 중복 또는 유사 제목이면 무시. 새로 삽입되면 True 반환."""
    try:
        conn = sqlite3.connect(DB_PATH)
        if _similar_title_exists(conn, article.title):
            return False
        conn.execute(
            """INSERT INTO articles (title, url, source, published, summary, language, sector)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (article.title, article.url, article.source, article.published,
             article.summary, article.language, article.sector),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_articles(source: str = None, language: str = None, limit: int = 200) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    query = "SELECT * FROM articles WHERE 1=1"
    params: list = []

    if source:
        query += " AND source = ?"
        params.append(source)
    if language:
        query += " AND language = ?"
        params.append(language)

    query += " ORDER BY published DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_sources() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT DISTINCT source, language FROM articles ORDER BY language, source"
    ).fetchall()
    conn.close()
    return [{"source": r[0], "language": r[1]} for r in rows]


def get_stats() -> dict:
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    last = conn.execute("SELECT MAX(created_at) FROM articles").fetchone()[0]
    conn.close()
    return {"total": total, "last_crawled": last}
