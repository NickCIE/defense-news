import os
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler

from database import init_db, get_articles, get_sources, get_stats, insert_article
from crawlers.rss import RSSCrawler
from crawlers.nyt import NYTCrawler
from sector_configs.defense import RSS_SOURCES, KEYWORDS_KO, KEYWORDS_EN

load_dotenv()

BASE_DIR = Path(__file__).parent


def run_crawl() -> dict:
    new_count = 0
    fail_count = 0

    crawlers = []
    for src in RSS_SOURCES:
        keywords = KEYWORDS_KO if src["language"] == "ko" else KEYWORDS_EN
        crawlers.append(RSSCrawler(src["name"], src["url"], keywords, src["language"]))

    nyt_key = os.getenv("NYT_API_KEY", "")
    if nyt_key:
        crawlers.append(NYTCrawler(api_key=nyt_key, keywords=KEYWORDS_EN))

    for crawler in crawlers:
        articles = crawler.fetch()
        for article in articles:
            if insert_article(article):
                new_count += 1
            else:
                fail_count += 1  # 중복

    print(f"[크롤링 완료] 신규 {new_count}건 / 중복 {fail_count}건")
    return {"new": new_count, "duplicate": fail_count}


scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    threading.Thread(target=run_crawl, daemon=True).start()

    interval = int(os.getenv("CRAWL_INTERVAL_HOURS", 2))
    scheduler.add_job(run_crawl, "interval", hours=interval, id="crawl")
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(title="방산 뉴스 대시보드", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def root():
    return (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/api/articles")
def api_articles(source: str = None, language: str = None, limit: int = 200):
    return get_articles(source=source, language=language, limit=limit)


@app.get("/api/sources")
def api_sources():
    return get_sources()


@app.get("/api/stats")
def api_stats():
    return get_stats()


@app.post("/api/crawl")
def api_crawl():
    result = run_crawl()
    return result


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
