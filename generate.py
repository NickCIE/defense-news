"""
뉴스를 수집해서 standalone HTML 파일로 저장.
생성된 HTML은 Python·서버 없이 브라우저에서 바로 열 수 있음.
"""

import json
import os
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from crawlers.rss import RSSCrawler
from crawlers.nyt import NYTCrawler
from sector_configs.defense import RSS_SOURCES, KEYWORDS_KO, KEYWORDS_EN

load_dotenv()
BASE_DIR = Path(__file__).parent
OUT_PATH = BASE_DIR / "방산뉴스_대시보드.html"


# ── 수집 ──────────────────────────────────────────────────

def collect() -> list[dict]:
    crawlers = []
    for src in RSS_SOURCES:
        keywords = KEYWORDS_KO if src["language"] == "ko" else KEYWORDS_EN
        crawlers.append(RSSCrawler(src["name"], src["url"], keywords, src["language"]))

    nyt_key = os.getenv("NYT_API_KEY", "")
    if nyt_key:
        crawlers.append(NYTCrawler(api_key=nyt_key, keywords=KEYWORDS_EN))

    seen_urls: set[str] = set()
    seen_titles: list[str] = []
    articles: list[dict] = []

    for crawler in crawlers:
        for a in crawler.fetch():
            if a.url in seen_urls:
                continue
            if _is_duplicate_title(a.title, seen_titles):
                continue
            seen_urls.add(a.url)
            seen_titles.append(a.title)
            articles.append({
                "title":     a.title,
                "url":       a.url,
                "source":    a.source,
                "published": a.published,
                "summary":   a.summary,
                "language":  a.language,
            })

    articles.sort(key=lambda x: x["published"], reverse=True)
    print(f"[완료] {len(articles)}건 수집")
    return articles


def _is_duplicate_title(title: str, existing: list[str], threshold: float = 0.5) -> bool:
    words = set(title.lower().split())
    if not words:
        return False
    for ex in existing:
        ex_words = set(ex.lower().split())
        if not ex_words:
            continue
        if len(words & ex_words) / len(words | ex_words) >= threshold:
            return True
    return False


# ── HTML 생성 ─────────────────────────────────────────────

def generate_html(articles: list[dict]) -> str:
    generated_at = datetime.now(tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    data_json = json.dumps(articles, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>방산 뉴스 — {generated_at}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background:#0d1117; color:#c9d1d9; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; min-height:100vh; }}

    header {{ background:#161b22; border-bottom:1px solid #30363d; padding:14px 24px; display:flex; align-items:center; gap:12px; position:sticky; top:0; z-index:100; }}
    header h1 {{ font-size:16px; font-weight:700; color:#f0f6fc; }}
    .sector-badge {{ font-size:11px; background:#1f3a5c; color:#79c0ff; padding:2px 8px; border-radius:10px; font-weight:600; }}
    .header-right {{ margin-left:auto; font-size:12px; color:#8b949e; }}
    .header-right span {{ color:#f0f6fc; font-weight:600; }}

    .toolbar {{ padding:12px 24px; display:flex; align-items:center; gap:6px; flex-wrap:wrap; border-bottom:1px solid #21262d; }}
    .filter-btn {{ background:#21262d; border:1px solid #30363d; color:#8b949e; padding:5px 14px; border-radius:20px; cursor:pointer; font-size:12px; font-weight:500; transition:all .15s; }}
    .filter-btn:hover {{ border-color:#58a6ff; color:#c9d1d9; }}
    .filter-btn.active {{ background:#1f6feb; border-color:#1f6feb; color:#fff; }}
    .divider {{ width:1px; height:20px; background:#30363d; margin:0 4px; }}
    .search-wrap {{ margin-left:auto; }}
    .search-wrap input {{ background:#21262d; border:1px solid #30363d; color:#c9d1d9; padding:6px 12px; border-radius:6px; font-size:12px; outline:none; width:220px; }}
    .search-wrap input:focus {{ border-color:#58a6ff; }}
    .search-wrap input::placeholder {{ color:#484f58; }}

    .meta {{ padding:8px 24px; font-size:11px; color:#8b949e; }}
    .meta span {{ color:#f0f6fc; }}

    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:14px; padding:16px 24px 40px; }}

    .card {{ background:#161b22; border:1px solid #30363d; border-radius:10px; padding:16px; display:flex; flex-direction:column; gap:10px; transition:border-color .15s,transform .1s; }}
    .card:hover {{ border-color:#58a6ff; transform:translateY(-1px); }}
    .card-top {{ display:flex; justify-content:space-between; align-items:flex-start; gap:8px; }}
    .badge {{ font-size:10px; font-weight:700; padding:3px 9px; border-radius:10px; white-space:nowrap; letter-spacing:.3px; }}
    .card-date {{ font-size:11px; color:#8b949e; white-space:nowrap; flex-shrink:0; }}
    .card-title {{ font-size:14px; font-weight:600; color:#f0f6fc; line-height:1.45; }}
    .card-title a {{ color:inherit; text-decoration:none; }}
    .card-title a:hover {{ color:#58a6ff; }}
    .card-summary {{ font-size:12px; color:#8b949e; line-height:1.55; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }}
    .card-footer {{ display:flex; justify-content:flex-end; }}
    .card-link {{ font-size:11px; color:#58a6ff; text-decoration:none; }}
    .card-link:hover {{ text-decoration:underline; }}
    .placeholder {{ grid-column:1/-1; text-align:center; padding:80px 0; color:#484f58; font-size:14px; }}

    .b-reuters          {{ background:#7d3c0010; color:#e8a87c; border:1px solid #7d3c0040; }}
    .b-cnbc             {{ background:#00308710; color:#79c0ff; border:1px solid #00308740; }}
    .b-breaking-defense {{ background:#8b000010; color:#ff7b7b; border:1px solid #8b000040; }}
    .b-the-war-zone     {{ background:#4a000010; color:#ffa657; border:1px solid #4a000040; }}
    .b-defense-one      {{ background:#1a3a5c10; color:#79c0ff; border:1px solid #1a3a5c60; }}
    .b-defense-news     {{ background:#2d1b6910; color:#d2a8ff; border:1px solid #2d1b6940; }}
    .b-new-york-times   {{ background:#22222210; color:#c9d1d9; border:1px solid #44444440; }}
    .b-연합뉴스          {{ background:#0066cc10; color:#79c0ff; border:1px solid #0066cc40; }}
    .b-뉴시스            {{ background:#cc000010; color:#ff7b7b; border:1px solid #cc000040; }}
    .b-조선비즈          {{ background:#00339910; color:#a5d6ff; border:1px solid #00339940; }}
    .b-한국경제          {{ background:#ff660010; color:#ffa657; border:1px solid #ff660040; }}
    .b-방산-뉴스         {{ background:#23863610; color:#7ee787; border:1px solid #23863640; }}
    .b-default          {{ background:#21262d; color:#8b949e; border:1px solid #30363d; }}
  </style>
</head>
<body>

<header>
  <h1>방산 뉴스 대시보드</h1>
  <span class="sector-badge">Defense</span>
  <div class="header-right">총 <span id="count">0</span>건 &nbsp;·&nbsp; 수집: {generated_at}</div>
</header>

<div class="toolbar">
  <div id="langFilters" style="display:flex;gap:6px;flex-wrap:wrap;">
    <button class="filter-btn active" data-lang="">전체</button>
    <button class="filter-btn" data-lang="ko">국내</button>
    <button class="filter-btn" data-lang="en">외신</button>
  </div>
  <div class="divider"></div>
  <div id="srcFilters" style="display:flex;gap:6px;flex-wrap:wrap;"></div>
  <div class="search-wrap">
    <input id="q" type="text" placeholder="제목 / 요약 검색..." oninput="render()"/>
  </div>
</div>

<div class="meta" id="meta"></div>
<div class="grid" id="grid"></div>

<script>
const ALL = {data_json};

const BADGE = {{
  "Reuters":"b-reuters","CNBC":"b-cnbc","CNBC World":"b-cnbc",
  "Breaking Defense":"b-breaking-defense","Breaking Defense (GNews)":"b-breaking-defense",
  "The War Zone":"b-the-war-zone","Defense One":"b-defense-one",
  "Defense News":"b-defense-news","New York Times":"b-new-york-times",
  "연합뉴스":"b-연합뉴스","연합뉴스 경제":"b-연합뉴스",
  "뉴시스":"b-뉴시스","뉴시스 경제":"b-뉴시스",
  "조선비즈":"b-조선비즈","한국경제":"b-한국경제",
  "한국경제 정치":"b-한국경제","한국경제 경제":"b-한국경제","한국경제 국제":"b-한국경제",
  "방산 뉴스":"b-방산-뉴스",
}};

let activeLang = "", activeSrc = "";

function esc(s){{ return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }}

function rel(iso){{
  try {{
    const d = (Date.now() - new Date(iso)) / 1000;
    if(d < 3600) return Math.floor(d/60)+"분 전";
    if(d < 86400) return Math.floor(d/3600)+"시간 전";
    if(d < 172800) return "어제";
    const dt = new Date(iso);
    return (dt.getMonth()+1)+"/"+ dt.getDate();
  }} catch{{ return ""; }}
}}

function render(){{
  const q = document.getElementById("q").value.toLowerCase();
  const items = ALL.filter(a => {{
    if(activeLang && a.language !== activeLang) return false;
    if(activeSrc  && a.source  !== activeSrc)  return false;
    if(q && !(a.title+a.summary).toLowerCase().includes(q)) return false;
    return true;
  }});
  document.getElementById("count").textContent = items.length;
  document.getElementById("meta").innerHTML =
    items.length ? `<span>${{items.length}}</span>건 표시 중` : "";
  const grid = document.getElementById("grid");
  if(!items.length){{ grid.innerHTML='<div class="placeholder">표시할 기사가 없습니다.</div>'; return; }}
  grid.innerHTML = items.map(a => `
    <div class="card">
      <div class="card-top">
        <span class="badge ${{BADGE[a.source]||"b-default"}}">${{esc(a.source)}}</span>
        <span class="card-date">${{rel(a.published)}}</span>
      </div>
      <div class="card-title"><a href="${{a.url}}" target="_blank" rel="noopener">${{esc(a.title)}}</a></div>
      ${{a.summary ? `<div class="card-summary">${{esc(a.summary)}}</div>` : ""}}
      <div class="card-footer"><a class="card-link" href="${{a.url}}" target="_blank" rel="noopener">원문 보기 →</a></div>
    </div>`).join("");
}}

function buildSrcFilters(){{
  const sources = [...new Set(ALL.map(a => a.source))].sort();
  document.getElementById("srcFilters").innerHTML = sources.map(s =>
    `<button class="filter-btn" data-src="${{s}}">${{s}}</button>`).join("");
  document.querySelectorAll("#srcFilters .filter-btn").forEach(b => {{
    b.onclick = () => {{
      activeSrc = b.dataset.src === activeSrc ? "" : b.dataset.src;
      document.querySelectorAll("#srcFilters .filter-btn").forEach(x => x.classList.remove("active"));
      if(activeSrc) b.classList.add("active");
      render();
    }};
  }});
}}

document.querySelectorAll("#langFilters .filter-btn").forEach(b => {{
  b.onclick = () => {{
    activeLang = b.dataset.lang;
    document.querySelectorAll("#langFilters .filter-btn").forEach(x => x.classList.remove("active"));
    b.classList.add("active");
    render();
  }};
}});

buildSrcFilters();
render();
</script>
</body>
</html>"""


# ── 진입점 ────────────────────────────────────────────────

if __name__ == "__main__":
    print("뉴스 수집 중...")
    articles = collect()
    html = generate_html(articles)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"저장 완료: {OUT_PATH}")
    if not os.getenv("CI"):
        webbrowser.open(OUT_PATH.as_uri())
