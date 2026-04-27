#!/usr/bin/env python3
"""
Static site generator for yt-monitor-site.

Reads:  content/*.md  (frontmatter + markdown body written by yt-monitor pipeline)
Writes: _site/
          .nojekyll
          style.css
          index.html
          data.json
          v/YYYY-MM-DD-{channel}-{slug}.html

Usage:
    python build.py              # outputs to _site/ relative to CWD
    python build.py --out /path  # custom output directory
"""
import argparse
import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

import markdown as md_lib
import yaml

HU_MONTHS = [
    'január', 'február', 'március', 'április', 'május', 'június',
    'július', 'augusztus', 'szeptember', 'október', 'november', 'december',
]

DIRECTION_LABELS = {
    "liberal": "Liberális",
    "centrist": "Centrista",
    "conservative": "Konzervatív",
    "far-right": "Szélsőjobb",
}

AFFILIATION_LABELS = {
    "independent": "Független",
    "fidesz-aligned": "Fidesz-közeli",
    "tisza-aligned": "Tisza-közeli",
}

DIRECTION_ORDER = ["liberal", "centrist", "conservative", "far-right"]
AFFILIATION_ORDER = ["independent", "fidesz-aligned", "tisza-aligned"]

GITHUB_REPO_URL = "https://github.com/critic4lcode/roviden"
ISSUES_URL = f"{GITHUB_REPO_URL}/issues"


def _fmt_date(date_str: str) -> str:
    try:
        d = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
        return f"{d.year}. {HU_MONTHS[d.month - 1]} {d.day}."
    except Exception:
        return str(date_str)


def _fmt_duration(sec) -> str:
    try:
        sec = int(sec)
    except (TypeError, ValueError):
        return ""
    if not sec:
        return ""
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


# ── Markdown parsing ──────────────────────────────────────────────────────────

def _parse_file(path: Path) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_text) for a content .md file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        print(f"WARN: YAML parse failed in {path}: {e}")
        fm = {}
    return fm, parts[2].strip()


_TLDR_RE = re.compile(r"^#\s+tl;dr\s*$", re.MULTILINE | re.IGNORECASE)
_DETAILS_RE = re.compile(
    r"^#\s+Részletes\s+(?:összefoglaló|elemzés)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
_DETAILS_BLOCK_RE = re.compile(r"<details\b[^>]*>(.*?)</details>", re.DOTALL | re.IGNORECASE)
_SUMMARY_TAG_RE = re.compile(r"<summary\b[^>]*>.*?</summary>", re.DOTALL | re.IGNORECASE)
_HR_RE = re.compile(r"^\s*-{3,}\s*$", re.MULTILINE)


def _extract_uncertain(summary: str) -> tuple[str, str]:
    """Pull out any <details> block referencing 'Értelmezhetetlen'.

    Also strips an optional preceding `## (⚠️ )?Értelmezhetetlen…` heading
    that some LLM outputs include redundantly above the <details>.
    Returns (uncertain_md, summary_without_block).
    """
    for m in _DETAILS_BLOCK_RE.finditer(summary):
        if "Értelmezhetetlen" not in m.group(0):
            continue
        inner = _SUMMARY_TAG_RE.sub("", m.group(1)).strip()
        start, end = m.start(), m.end()
        preceding = summary[:start]
        heading = re.search(
            r"^#{1,3}\s+[^\n]*Értelmezhetetlen[^\n]*\n+\s*\Z",
            preceding, re.MULTILINE,
        )
        if heading:
            start = heading.start()
        return inner, summary[:start] + summary[end:]
    return "", summary


def _extract_sections(body: str) -> tuple[str, str, str, str]:
    """Split body into (tldr_md, details_md, uncertain_md, transcript_block)."""
    idx = body.find("## Átirat")
    if idx == -1:
        summary, transcript_block = body, ""
    else:
        summary = body[:idx]
        transcript_block = body[idx + len("## Átirat"):].strip()

    uncertain_md, summary = _extract_uncertain(summary)
    summary = _HR_RE.sub("", summary)

    tldr_match = _TLDR_RE.search(summary)
    details_match = _DETAILS_RE.search(summary)

    if tldr_match and details_match and tldr_match.start() < details_match.start():
        tldr_md = summary[tldr_match.end():details_match.start()].strip()
        details_md = summary[details_match.end():].strip()
    elif tldr_match:
        tldr_md = summary[tldr_match.end():].strip()
        details_md = ""
    elif details_match:
        tldr_md = summary[:details_match.start()].strip()
        details_md = summary[details_match.end():].strip()
    else:
        tldr_md = summary.strip()
        details_md = ""

    return tldr_md, details_md, uncertain_md, transcript_block


def _transcript_to_html(block: str) -> str:
    """
    Parse [HH:MM:SS](url) text lines (produced by markdown_writer.py)
    into clickable timestamp paragraphs.
    """
    lines = []
    for line in block.splitlines():
        line = line.strip()
        m = re.match(r'\[(\d+:\d+:\d+)\]\(([^)]+)\)\s+(.+)', line)
        if not m:
            continue
        ts, url, text = m.groups()
        lines.append(
            f'<p><a class="ts" href="{html.escape(url)}" target="_blank">[{ts}]</a>'
            f'{html.escape(text)}</p>'
        )
    return "\n".join(lines)


# ── URL derivation ────────────────────────────────────────────────────────────

def _page_url(md_path: Path, content_dir: Path) -> str:
    """Derive video page URL preserving the content subdir structure."""
    rel = md_path.relative_to(content_dir)
    return f"v/{rel.with_suffix('.html')}"


def _root_prefix(page_url: str) -> str:
    """Return '../' repeated enough times to reach the site root from page_url."""
    depth = len(Path(page_url).parts) - 1  # exclude filename itself
    return "/".join([".."] * depth)


# ── HTML templates ────────────────────────────────────────────────────────────

_VIDEO_TMPL = """\
<!doctype html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{desc}">
<title>{title} - Röviden</title>
<link rel="stylesheet" href="{root}/style.css">
</head>
<body>
<nav class="nav"><a href="{root}/">← Röviden</a></nav>
<article class="vp">
  <header class="vp-head">
    <div class="vp-meta">
      <span class="badge-ch">{channel_name}</span>
      <time>{date_display}</time>
      {duration_span}
    </div>
    <h1>{title_esc}</h1>
    <div class="tag-row">{tags_html}</div>
    {channel_meta_block}
  </header>

  <a class="thumb-link" href="{video_url}" target="_blank" rel="noopener noreferrer">
    <div class="thumb-wrap">
      <img src="https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
           alt="{title_esc}" loading="lazy">
      <span class="play-btn" aria-hidden="true">&#9654;</span>
    </div>
  </a>
  <aside class="ai-disclaimer" role="note">
    <strong>AI-generált összefoglaló.</strong>
    Hiba esetén <a href="{edit_url}" target="_blank" rel="noopener noreferrer">javítsd közvetlenül a forrásfájlt</a>
    (a ceruza ikon a GitHubon), vagy <a href="{issues_url}" target="_blank" rel="noopener noreferrer">jelezd hibajegyben
  </a>.
  </aside>

  {tldr_block}
  {details_block}
  {uncertain_block}

  <section class="transcript">
    <details>
      <summary>Teljes átirat megjelenítése</summary>
      <div class="transcript-inner">
        {transcript_html}
      </div>
    </details>
  </section>

  <footer class="vp-foot">
    Forrás: <strong>{source_label}</strong> &middot;
    Modell: <strong>{summary_model}</strong> &middot;
    <a href="{video_url}" target="_blank" rel="noopener noreferrer">YouTube&nbsp;&#8599;</a>
  </footer>
</article>
</body>
</html>
"""


def _build_video_page(fm: dict, tldr_md: str, details_md: str, uncertain_md: str, transcript_block: str, root: str = "..", source_rel: str = "") -> str:
    video_id = html.escape(str(fm.get("video_id", "")))
    video_url = html.escape(str(fm.get("video_url", f"https://www.youtube.com/watch?v={video_id}")))
    title = str(fm.get("title", ""))
    title_esc = html.escape(title)
    channel_name = html.escape(str(fm.get("channel_name", "")))
    date_display = html.escape(_fmt_date(str(fm.get("published_at", fm.get("date", "")))))
    tags = fm.get("tags", []) or []
    tags_html = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in tags)
    duration_sec = fm.get("duration_sec", 0) or 0
    dur = _fmt_duration(duration_sec)
    duration_span = f'<span class="badge-src">{html.escape(dur)}</span>' if dur else ""
    source_label = html.escape(
        "YouTube felirat" if fm.get("transcript_source") == "youtube_subtitle" else "Whisper ASR"
    )
    summary_model = html.escape(str(fm.get("summary_model", "")))
    affiliation = str(fm.get("affiliation", "") or "").strip()
    direction = str(fm.get("direction", "") or "").strip()
    notes = str(fm.get("notes", "") or "").strip()
    notes_attr = f' data-notes="{html.escape(notes)}" title="{html.escape(notes)}"' if notes else ""
    notes_class = " has-notes" if notes else ""
    meta_chips = []
    if direction:
        dir_label = DIRECTION_LABELS.get(direction, direction)
        meta_chips.append(
            f'<span class="ch-meta ch-meta-dir ch-meta-dir-{html.escape(direction)}{notes_class}"{notes_attr}>'
            f'Irányultság: {html.escape(dir_label)}</span>'
        )
    if affiliation:
        aff_label = AFFILIATION_LABELS.get(affiliation, affiliation)
        meta_chips.append(
            f'<span class="ch-meta ch-meta-aff ch-meta-aff-{html.escape(affiliation)}{notes_class}"{notes_attr}>'
            f'Kötődés: {html.escape(aff_label)}</span>'
        )
    channel_meta_block = (
        f'<div class="ch-meta-row">{"".join(meta_chips)}</div>' if meta_chips else ""
    )
    tldr_html = md_lib.markdown(tldr_md, extensions=["nl2br", "tables", "md_in_html"]) if tldr_md else ""
    details_html = md_lib.markdown(details_md, extensions=["nl2br", "tables", "md_in_html"]) if details_md else ""
    uncertain_html = md_lib.markdown(uncertain_md, extensions=["nl2br", "tables", "md_in_html"]) if uncertain_md else ""
    tldr_block = f'<section class="tldr">\n    <div class="tldr-label">tl;dr</div>\n    {tldr_html}\n  </section>' if tldr_html else ""
    details_block = f'<section class="summary">\n    {details_html}\n  </section>' if details_html else ""
    uncertain_block = (
        f'<section class="uncertain">\n'
        f'    <details>\n'
        f'      <summary>⚠️ Értelmezhetetlen vagy bizonytalan szakaszok</summary>\n'
        f'      <div class="uncertain-inner">{uncertain_html}</div>\n'
        f'    </details>\n'
        f'  </section>'
    ) if uncertain_html else ""
    transcript_html = _transcript_to_html(transcript_block)
    plain_summary = re.sub(r"<[^>]+>", "", tldr_html or details_html).strip()
    desc = html.escape(plain_summary[:160])

    edit_url = html.escape(f"{GITHUB_REPO_URL}/blob/main/content/{source_rel}") if source_rel else html.escape(GITHUB_REPO_URL)
    issues_url = html.escape(ISSUES_URL)

    return _VIDEO_TMPL.format(
        root=root,
        edit_url=edit_url,
        issues_url=issues_url,
        title=title,
        title_esc=title_esc,
        desc=desc,
        channel_name=channel_name,
        date_display=date_display,
        duration_span=duration_span,
        tags_html=tags_html,
        video_id=video_id,
        video_url=video_url,
        tldr_block=tldr_block,
        details_block=details_block,
        uncertain_block=uncertain_block,
        transcript_html=transcript_html,
        source_label=source_label,
        summary_model=summary_model,
        channel_meta_block=channel_meta_block,
    )


def _card_html(entry: dict) -> str:
    teaser = html.escape(entry.get("teaser", "")[:200])
    title_esc = html.escape(entry["title"])
    tags_html = "".join(
        f'<span class="tag">{html.escape(t)}</span>'
        for t in (entry.get("tags") or [])
    )
    src = entry.get("transcript_source", "")
    src_badge = "▶ felirat" if src == "youtube_subtitle" else "🎙 whisper"
    dur = _fmt_duration(entry.get("duration_sec", 0))
    dur_span = f'<span class="dur">{html.escape(dur)}</span>' if dur else ""

    return (
        f'<a class="card" href="{html.escape(entry["page_url"])}"'
        f' data-channel="{html.escape(entry["channel_slug"])}"'
        f' data-direction="{html.escape(entry.get("direction", ""))}"'
        f' data-affiliation="{html.escape(entry.get("affiliation", ""))}"'
        f' data-date="{html.escape(entry["date"])}">\n'
        f'  <div class="card-thumb">\n'
        f'    <img src="https://i.ytimg.com/vi/{html.escape(entry["video_id"])}/hqdefault.jpg"'
        f' alt="" loading="lazy">\n'
        f'    {dur_span}\n'
        f'  </div>\n'
        f'  <div class="card-body">\n'
        f'    <div class="card-badges">\n'
        f'      <span class="badge-ch">{html.escape(entry["channel_name"])}</span>\n'
        f'      <span class="badge-src">{src_badge}</span>\n'
        f'      <time class="card-date">{html.escape(_fmt_date(entry["date"]))}</time>\n'
        f'    </div>\n'
        f'    <div class="card-title">{title_esc}</div>\n'
        f'    {f"<div class=card-teaser>{teaser}&hellip;</div>" if teaser else ""}\n'
        f'    <div class="tag-row">{tags_html}</div>\n'
        f'  </div>\n'
        f'</a>\n'
    )


PAGE_SIZE = 20


_INDEX_TMPL = """\
<!doctype html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Röviden - Hosszú beszélgetések, podcastek és interjúk dióhéjban</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<div id="welcome-modal" class="modal-overlay" hidden>
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="welcome-title">
    <button class="modal-close" type="button" aria-label="Bezárás" onclick="ytmCloseWelcome()">&times;</button>
    <h2 id="welcome-title">Üdvözöllek!</h2>
    <p>Ez a weboldal <strong>AI által készített összefoglalókat</strong> tartalmaz hosszú videókhoz – kifejezetten azoknak, akik szeretnék gyorsan átlátni egy-egy hosszabb tartalom lényegét.</p>
    <h3>Fontos tudnivalók</h3>
    <ul>
      <li>Csak <strong>30 percnél hosszabb</strong> videókról készítünk összefoglalót.</li>
      <li>Az összefoglalók <strong>nem helyettesítik</strong> az eredeti tartalmat – a kontextus, az árnyalatok és az alkotói munka csak a videó megtekintésével élhető át igazán.</li>
      <li>Kérünk, <strong>támogasd az érintett médiumokat és csatornákat</strong>: nézd meg az eredeti videót, iratkozz fel, oszd meg, vagy támogasd őket anyagilag, ha van rá módod. Az ő munkájuk nélkül ez az oldal sem létezne.</li>
    </ul>
    <h3>Egy őszinte aggály</h3>
    <p>Be kell vallanunk, hogy ezzel a projekttel kapcsolatban vannak fenntartásaink. Egyértelmű volt az igény a közönség részéről a többórás videók rövid összefoglalóira, viszont fennáll a veszélye annak, hogy a látogatók csak az AI-összefoglalókat olvassák el, és nem nézik meg magát a videót. Ez hosszú távon <strong>csökkentheti a csatornák nézettségét</strong>, ami egyrészt megnehezíti a médiumok számára, hogy felmérjék a közönségük valós igényeit, másrészt <strong>bevételkiesést</strong> is okozhat számukra.</p>
    <p>Amennyiben Ön egy érintett médium képviselője, és ezt a problémát valósnak találja – vagy bármilyen észrevétele, kérése van az oldallal kapcsolatban – kérjük, vegye fel velünk a kapcsolatot az <a href="mailto:info@jegyezve.com">info@jegyezve.com</a> címen.</p>
    <p class="modal-outro">Köszönjük a megértést, és jó olvasást / videózást kívánunk!</p>
    <div class="modal-actions">
      <button class="modal-btn" type="button" onclick="ytmCloseWelcome()">Megértettem</button>
    </div>
  </div>
</div>
<button id="about-fab" class="about-fab" type="button" onclick="ytmOpenWelcome()" aria-label="Az oldalról">Az oldalról</button>
<header class="site-header">
  <div class="site-header-inner">
    <h1>Röviden</h1>
    <p class="site-sub">Hosszú beszélgetések, podcastek és interjúk dióhéjban</p>
  </div>
  <div class="filter-groups">
    <div class="filter-row" data-group="channel">
      <span class="filter-label">Csatorna:</span>
      <button class="chip active" data-group="channel" data-f="">Összes ({total})</button>
      {channel_chips}
    </div>
    <div class="filter-row" data-group="direction">
      <span class="filter-label">Irányultság:</span>
      <button class="chip active" data-group="direction" data-f="">Összes</button>
      {direction_chips}
    </div>
    <div class="filter-row" data-group="affiliation">
      <span class="filter-label">Kötődés:</span>
      <button class="chip active" data-group="affiliation" data-f="">Összes</button>
      {affiliation_chips}
    </div>
  </div>
</header>
<main class="feed" id="feed">
{cards}
</main>
<div id="pag"></div>
<script>
(function(){{
  window.ytmOpenWelcome=function(){{
    var m=document.getElementById('welcome-modal');
    if(m){{m.hidden=false;document.body.classList.add('modal-open');}}
  }};
  window.ytmCloseWelcome=function(){{
    var m=document.getElementById('welcome-modal');
    if(m){{m.hidden=true;document.body.classList.remove('modal-open');}}
    try{{localStorage.setItem('ytm_welcome_seen','1');}}catch(e){{}}
  }};
  try{{
    if(!localStorage.getItem('ytm_welcome_seen')){{
      window.ytmOpenWelcome();
    }}
  }}catch(e){{}}
}})();
(function(){{
  var N={page_size},TOTAL={total},page=1,data=null,loading=null;
  var filters={{channel:'',direction:[],affiliation:[]}};
  var MULTI={{direction:true,affiliation:true}};
  var feed=document.getElementById('feed');

  function loadData(){{
    if(data) return Promise.resolve(data);
    if(loading) return loading;
    loading=fetch('data.json',{{cache:'no-cache'}}).then(function(r){{return r.json();}}).then(function(j){{data=j;return j;}});
    return loading;
  }}

  function esc(s){{var d=document.createElement('div');d.textContent=s==null?'':String(s);return d.innerHTML;}}

  function cardHtml(e){{
    var dur=e.duration_display?'<span class="dur">'+esc(e.duration_display)+'</span>':'';
    var srcBadge=e.transcript_source==='youtube_subtitle'?'▶ felirat':'🎙 whisper';
    var tags=(e.tags||[]).map(function(t){{return '<span class="tag">'+esc(t)+'</span>';}}).join('');
    var teaser=e.teaser?'<div class="card-teaser">'+esc(e.teaser)+'&hellip;</div>':'';
    return '<a class="card" href="'+esc(e.page_url)+'" data-channel="'+esc(e.channel_slug)+'" data-direction="'+esc(e.direction||'')+'" data-affiliation="'+esc(e.affiliation||'')+'" data-date="'+esc(e.date)+'">'
      +'<div class="card-thumb"><img src="https://i.ytimg.com/vi/'+esc(e.video_id)+'/hqdefault.jpg" alt="" loading="lazy">'+dur+'</div>'
      +'<div class="card-body">'
        +'<div class="card-badges">'
          +'<span class="badge-ch">'+esc(e.channel_name)+'</span>'
          +'<span class="badge-src">'+srcBadge+'</span>'
          +'<time class="card-date">'+esc(e.date_display||e.date)+'</time>'
        +'</div>'
        +'<div class="card-title">'+esc(e.title)+'</div>'
        +teaser
        +'<div class="tag-row">'+tags+'</div>'
      +'</div>'
    +'</a>';
  }}

  function dayHeaderHtml(e){{
    return '<h2 class="day-header" data-date="'+esc(e.date)+'">'+esc(e.date_display||e.date)+'</h2>';
  }}

  function renderFromData(){{
    var vis=data.filter(function(e){{
      if(filters.channel && e.channel_slug!==filters.channel) return false;
      if(filters.direction.length && filters.direction.indexOf(e.direction||'')===-1) return false;
      if(filters.affiliation.length && filters.affiliation.indexOf(e.affiliation||'')===-1) return false;
      return true;
    }});
    var pages=Math.max(1,Math.ceil(vis.length/N));
    if(page>pages) page=pages;
    var slice=vis.slice((page-1)*N,page*N);
    var html='',last=null;
    slice.forEach(function(e){{
      if(e.date!==last){{last=e.date;html+=dayHeaderHtml(e);}}
      html+=cardHtml(e);
    }});
    feed.innerHTML=html;
    renderPag(pages);
  }}

  function renderPag(pages){{
    var pag=document.getElementById('pag');
    if(pages<=1){{pag.innerHTML='';return;}}
    pag.innerHTML='<div class="pag">'
      +'<button class="pag-btn"'+(page<=1?' disabled':'')+' onclick="ytmPrev()">&#8592; Előző</button>'
      +'<span class="pag-info">'+page+' / '+pages+'</span>'
      +'<button class="pag-btn"'+(page>=pages?' disabled':'')+' onclick="ytmNext()">Következő &#8594;</button>'
      +'</div>';
  }}

  // Initial pagination reflects server-rendered first page; clicking it triggers data.json fetch.
  if(TOTAL>N) renderPag(Math.ceil(TOTAL/N));

  function navigate(){{
    loadData().then(function(){{
      renderFromData();
      window.scrollTo(0,0);
    }});
  }}

  window.ytmPrev=function(){{if(page>1){{page--;navigate();}}}};
  window.ytmNext=function(){{page++;navigate();}};

  var chips=document.querySelectorAll('.chip');
  chips.forEach(function(c){{
    c.addEventListener('click',function(){{
      var group=c.dataset.group;
      var val=c.dataset.f;
      if(MULTI[group]){{
        var allChip=document.querySelector('.chip[data-group="'+group+'"][data-f=""]');
        if(val===''){{
          document.querySelectorAll('.chip[data-group="'+group+'"]').forEach(function(x){{x.classList.remove('active');}});
          c.classList.add('active');
          filters[group]=[];
        }} else {{
          if(allChip) allChip.classList.remove('active');
          c.classList.toggle('active');
          var sel=[];
          document.querySelectorAll('.chip[data-group="'+group+'"].active').forEach(function(x){{
            if(x.dataset.f) sel.push(x.dataset.f);
          }});
          if(sel.length===0 && allChip) allChip.classList.add('active');
          filters[group]=sel;
        }}
      }} else {{
        document.querySelectorAll('.chip[data-group="'+group+'"]').forEach(function(x){{x.classList.remove('active');}});
        c.classList.add('active');
        filters[group]=val;
      }}
      page=1;
      loadData().then(renderFromData);
    }});
  }});
}})();
</script>
</body>
</html>
"""


def _build_index(data: list[dict]) -> str:
    seen: dict[str, str] = {}
    for e in data:
        slug = e["channel_slug"]
        if slug not in seen:
            seen[slug] = e["channel_name"]

    channel_chips = "\n      ".join(
        f'<button class="chip" data-group="channel" data-f="{html.escape(slug)}">'
        f'{html.escape(name)}</button>'
        for slug, name in seen.items()
    )

    present_directions = {e.get("direction") for e in data if e.get("direction")}
    direction_chips = "\n      ".join(
        f'<button class="chip" data-group="direction" data-f="{html.escape(code)}">'
        f'{html.escape(DIRECTION_LABELS[code])}</button>'
        for code in DIRECTION_ORDER if code in present_directions
    )

    present_affiliations = {e.get("affiliation") for e in data if e.get("affiliation")}
    affiliation_chips = "\n      ".join(
        f'<button class="chip" data-group="affiliation" data-f="{html.escape(code)}">'
        f'{html.escape(AFFILIATION_LABELS[code])}</button>'
        for code in AFFILIATION_ORDER if code in present_affiliations
    )
    parts: list[str] = []
    current_date: str | None = None
    for e in data[:PAGE_SIZE]:
        d = e["date"]
        if d != current_date:
            current_date = d
            parts.append(
                f'<h2 class="day-header" data-date="{html.escape(d)}">'
                f'{html.escape(_fmt_date(d))}</h2>'
            )
        parts.append(_card_html(e))
    cards = "\n".join(parts)
    return _INDEX_TMPL.format(
        total=len(data),
        page_size=PAGE_SIZE,
        channel_chips=channel_chips,
        direction_chips=direction_chips,
        affiliation_chips=affiliation_chips,
        cards=cards,
    )


# ── Main build ────────────────────────────────────────────────────────────────

def build(site_root: Path, out_dir: Path) -> None:
    content_dir = site_root / "content"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "v").mkdir(exist_ok=True)

    # Copy static assets
    style = site_root / "scripts/style.css"
    if style.exists():
        shutil.copy(style, out_dir / "style.css")
    (out_dir / ".nojekyll").touch()

    # Process each content file (sorted newest-first by filename, recursive)
    md_files = sorted(content_dir.rglob("*.md"), reverse=True)
    data: list[dict] = []

    for md_path in md_files:
        if md_path.name.startswith("."):
            continue
        fm, body = _parse_file(md_path)
        if not fm.get("video_id"):
            continue

        tldr_md, details_md, uncertain_md, transcript_block = _extract_sections(body)
        page_url = _page_url(md_path, content_dir)
        root = _root_prefix(page_url)

        # Generate video page HTML
        source_rel = md_path.relative_to(content_dir).as_posix()
        page_html = _build_video_page(fm, tldr_md, details_md, uncertain_md, transcript_block, root=root, source_rel=source_rel)
        out_page = out_dir / page_url
        out_page.parent.mkdir(parents=True, exist_ok=True)
        out_page.write_text(page_html, encoding="utf-8")

        # Build data.json entry
        teaser_md = tldr_md or details_md
        plain_summary = re.sub(r"<[^>]+>", "", md_lib.markdown(teaser_md)).strip()
        date_iso = str(fm.get("date", ""))[:10]
        duration_sec = int(fm.get("duration_sec") or 0)
        data.append({
            "video_id": str(fm.get("video_id", "")),
            "title": str(fm.get("title", "")),
            "channel_slug": str(fm.get("channel_slug", "")),
            "channel_name": str(fm.get("channel_name", "")),
            "date": date_iso,
            "date_display": _fmt_date(date_iso),
            "published_at": str(fm.get("published_at", fm.get("date", ""))),
            "tags": fm.get("tags") or [],
            "transcript_source": str(fm.get("transcript_source", "")),
            "summary_model": str(fm.get("summary_model", "")),
            "duration_sec": duration_sec,
            "duration_display": _fmt_duration(duration_sec),
            "page_url": page_url,
            "teaser": plain_summary[:200],
            "affiliation": str(fm.get("affiliation", "") or ""),
            "direction": str(fm.get("direction", "") or ""),
            "notes": str(fm.get("notes", "") or ""),
        })

    # Sort newest-first by published_at (falls back to date), so videos appear
    # in date order even when interleaved across channel subfolders.
    data.sort(
        key=lambda e: (e.get("published_at") or e.get("date") or "", e.get("video_id") or ""),
        reverse=True,
    )

    # Write data.json and index.html
    (out_dir / "data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "index.html").write_text(_build_index(data), encoding="utf-8")

    print(f"Built {len(data)} video(s) → {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build yt-monitor-site static HTML")
    parser.add_argument("--out", default="_site", help="Output directory (default: _site)")
    parser.add_argument("--root", default=".", help="Site repo root (default: CWD)")
    args = parser.parse_args()
    build(Path(args.root).resolve(), Path(args.out).resolve())


if __name__ == "__main__":
    main()
