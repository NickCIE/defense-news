# ──────────────────────────────────────────────
# 섹터 설정 파일 — 방산(Defense)
# 다른 섹터로 확장 시 이 파일을 복사해 키워드·소스만 교체하면 됨
# ──────────────────────────────────────────────

SECTOR_NAME = "defense"

KEYWORDS_KO = [
    "방산", "방위산업", "국방", "무기", "군사", "미사일", "전투기", "잠수함",
    "방위비", "군비", "육군", "해군", "공군", "국방부", "방위사업청",
    "한화에어로스페이스", "한화시스템", "LIG넥스원", "현대로템", "KAI",
    "한국항공우주산업", "ADD", "국방과학연구소",
    "K9", "K2전차", "FA-50", "천무", "현궁", "해궁", "천검", "레드백",
    "수출형", "방산수출", "군납", "전력화", "전투기도입",
    # 한국경제 등에서 자주 쓰는 표현 추가
    "주한미군", "전작권", "군수", "방위비 분담", "한미동맹", "한미연합",
    "우주발사체", "위성", "무인기", "드론", "사이버전", "전자전",
    "록히드", "보잉 방산", "레이시온", "방산주", "방산펀드",
]

KEYWORDS_EN = [
    "defense", "defence", "military", "weapon", "missile", "fighter jet",
    "submarine", "armament", "Pentagon", "NATO", "artillery", "warship",
    "arms deal", "munitions", "defense contract", "air force", "navy",
    "Lockheed", "Raytheon", "Northrop Grumman", "BAE Systems", "DSEI",
    "K-defense", "Hanwha", "LIG Nex1", "Hyundai Rotem", "KAI",
    "defense budget", "arms export", "defense procurement",
]

# ──────────────────────────────────────────────
# RSS 소스 목록
# type: "rss"  → crawlers/rss.py 사용
# language: "ko" | "en"
# ──────────────────────────────────────────────
RSS_SOURCES = [
    # 외신 — 범용 뉴스 (키워드 필터로 방산 기사 추출)
    # Reuters: 공개 RSS 폐지 + 직접 스크래핑 401 차단 → Google News site: 검색으로 대체
    {
        "name": "Reuters",
        "url": "https://news.google.com/rss/search?q=site:reuters.com+aerospace+defense&hl=en-US&gl=US&ceid=US:en",
        "language": "en",
    },
    {
        "name": "CNBC",
        "url": "https://www.cnbc.com/id/100727362/device/rss/rss.html",
        "language": "en",
    },
    {
        "name": "CNBC World",
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "language": "en",
    },
    # 외신 — 방산 전문 (Google News RSS 백업 포함)
    {
        "name": "Breaking Defense",
        "url": "https://breakingdefense.com/feed/",
        "language": "en",
    },
    {
        "name": "Breaking Defense (GNews)",
        "url": "https://news.google.com/rss/search?q=site:breakingdefense.com&hl=en-US&gl=US&ceid=US:en",
        "language": "en",
    },
    {
        "name": "The War Zone",
        "url": "https://www.thedrive.com/the-war-zone/feed",
        "language": "en",
    },
    {
        "name": "Defense One",
        "url": "https://www.defenseone.com/rss/all/",
        "language": "en",
    },
    {
        "name": "Defense News",
        "url": "https://www.defensenews.com/arc/outboundfeeds/rss/",
        "language": "en",
    },
    # 국내
    {
        "name": "연합뉴스",
        "url": "https://www.yna.co.kr/rss/politics.xml",
        "language": "ko",
    },
    {
        "name": "연합뉴스 경제",
        "url": "https://www.yna.co.kr/rss/economy.xml",
        "language": "ko",
    },
    {
        "name": "뉴시스",
        "url": "https://www.newsis.com/RSS/politics.xml",
        "language": "ko",
    },
    {
        "name": "뉴시스 경제",
        "url": "https://www.newsis.com/RSS/economy.xml",
        "language": "ko",
    },
    {
        "name": "조선비즈",
        "url": "https://news.google.com/rss/search?q=site:biz.chosun.com+%EB%B0%A9%EC%82%B0+OR+%EA%B5%AD%EB%B0%A9+OR+%EA%B5%B0%EC%82%AC&hl=ko&gl=KR&ceid=KR:ko",
        "language": "ko",
    },
    {
        "name": "한국경제",
        "url": "https://www.hankyung.com/feed/all-news",
        "language": "ko",
    },
    {
        "name": "한국경제 정치",
        "url": "https://www.hankyung.com/feed/politics",
        "language": "ko",
    },
    {
        "name": "한국경제 경제",
        "url": "https://www.hankyung.com/feed/economy",
        "language": "ko",
    },
    {
        "name": "한국경제 국제",
        "url": "https://www.hankyung.com/feed/international",
        "language": "ko",
    },
    # 국내 방산 Google News (키워드 검색)
    {
        "name": "방산 뉴스",
        "url": "https://news.google.com/rss/search?q=%EB%B0%A9%EC%82%B0+%EB%B0%A9%EC%9C%84%EC%82%B0%EC%97%85&hl=ko&gl=KR&ceid=KR:ko",
        "language": "ko",
    },
]
