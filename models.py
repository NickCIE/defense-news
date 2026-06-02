from dataclasses import dataclass, field


@dataclass
class Article:
    title: str
    url: str
    source: str
    published: str
    summary: str = ""
    language: str = "ko"
    sector: str = "defense"

    def __post_init__(self):
        self.title = (self.title or "")[:120]
        self.summary = (self.summary or "")[:300]
