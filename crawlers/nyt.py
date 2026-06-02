import requests
from datetime import datetime, timezone
from crawlers.base import BaseCrawler
from models import Article

API_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"


class NYTCrawler(BaseCrawler):
    source_name = "New York Times"
    language = "en"

    def __init__(self, api_key: str, keywords: list[str]):
        self.api_key = api_key
        # 쿼리는 상위 5개 키워드만 사용 (토큰/요청 최소화)
        self.query = " OR ".join(keywords[:5])

    def fetch(self) -> list[Article]:
        if not self.api_key:
            return []
        try:
            resp = requests.get(
                API_URL,
                params={
                    "q": self.query,
                    "api-key": self.api_key,
                    "sort": "newest",
                    "fl": "headline,abstract,web_url,pub_date",
                },
                timeout=10,
            )
            resp.raise_for_status()
            docs = resp.json().get("response", {}).get("docs", [])

            articles = []
            for doc in docs:
                title = doc.get("headline", {}).get("main", "").strip()
                summary = doc.get("abstract", "").strip()
                url = doc.get("web_url", "")
                published = doc.get("pub_date", datetime.now(tz=timezone.utc).isoformat())

                if title and url:
                    articles.append(self._make_article(title, url, published, summary))

            return articles

        except Exception as e:
            print(f"[NYT] API 오류: {e}")
            return []
