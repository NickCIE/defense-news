from abc import ABC, abstractmethod
from models import Article


class BaseCrawler(ABC):
    source_name: str = ""
    language: str = "ko"
    sector: str = "defense"

    @abstractmethod
    def fetch(self) -> list[Article]:
        pass

    def _make_article(self, title: str, url: str, published: str, summary: str = "") -> Article:
        return Article(
            title=title,
            url=url,
            source=self.source_name,
            published=published,
            summary=summary,
            language=self.language,
            sector=self.sector,
        )
