import feedparser
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from crawlers.base import BaseCrawler
from models import Article

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


class RSSCrawler(BaseCrawler):
    def __init__(self, source_name: str, rss_url: str, keywords: list[str], language: str = "en"):
        self.source_name = source_name
        self.rss_url = rss_url
        self.keywords = [k.lower() for k in keywords]
        self.language = language

    def fetch(self) -> list[Article]:
        try:
            resp = requests.get(self.rss_url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            if feed.bozo and not feed.entries:
                print(f"[{self.source_name}] RSS 파싱 실패: {self.rss_url}")
                return []

            articles = []
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                raw_summary = entry.get("summary", entry.get("description", ""))
                url = entry.get("link", "")

                if not title or not url:
                    continue

                # HTML 태그 제거
                summary = BeautifulSoup(raw_summary, "html.parser").get_text(separator=" ").strip()

                # 키워드 필터 (제목 + 요약 검색)
                searchable = (title + " " + summary).lower()
                if not any(k in searchable for k in self.keywords):
                    continue

                published = self._parse_date(entry)
                articles.append(self._make_article(title, url, published, summary))

            return articles

        except Exception as e:
            print(f"[{self.source_name}] 오류: {e}")
            return []

    def _parse_date(self, entry) -> str:
        if entry.get("published_parsed"):
            try:
                from time import mktime
                return datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc).isoformat()
            except Exception:
                pass
        return datetime.now(tz=timezone.utc).isoformat()
