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
import sys
from datetime import datetime
from pathlib import Path

import markdown as md_lib
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from templates import (  # noqa: E402
    _POSTHOG_SNIPPET,
    _POSTHOG_INIT_JS,
    _TTS_BAR_HTML,
    _SITE_BASE_URL,
    _VIDEO_TMPL,
    PAGE_SIZE,
    _INDEX_TMPL,
)


def _minify_css(css: str) -> str:
    """Basic but effective CSS minifier — no extra dependencies."""
    # Remove /* ... */ comments
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    # Collapse whitespace (spaces, tabs, newlines) to a single space
    css = re.sub(r'\s+', ' ', css)
    # Remove spaces around structural characters
    css = re.sub(r'\s*([{};:,>~+])\s*', r'\1', css)
    # Remove spaces around ! (e.g. !important)
    css = re.sub(r'\s*!\s*', '!', css)
    # Remove trailing semicolons before closing brace
    css = re.sub(r';+\}', '}', css)
    # Remove leading/trailing whitespace
    return css.strip()

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
    "opposition": "Ellenzéki",
}

DIRECTION_ORDER = ["liberal", "centrist", "conservative", "far-right"]
AFFILIATION_ORDER = ["independent", "fidesz-aligned", "tisza-aligned", "opposition"]

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


_SECTION_DIVIDER_RE = re.compile(r"<!-- SECTION:([A-Z]+) -->")


def _extract_sections(body: str) -> tuple[str, str, str, str]:
    """Split body into (tldr_md, details_md, uncertain_md, transcript_block)."""
    idx = body.find("## Átirat")
    if idx == -1:
        summary, transcript_block = body, ""
    else:
        summary = body[:idx]
        transcript_block = body[idx + len("## Átirat"):].strip()

    # New format: <!-- SECTION:NAME --> dividers
    if "<!-- SECTION:TLDR -->" in summary:
        # re.split with capturing group interleaves: [pre, name1, content1, name2, content2, ...]
        parts = _SECTION_DIVIDER_RE.split(summary)
        sections: dict[str, str] = {}
        for name, content in zip(parts[1::2], parts[2::2]):
            sections[name] = content.strip()
        return (
            sections.get("TLDR", ""),
            sections.get("DETAILS", ""),
            sections.get("UNCERTAIN", ""),
            transcript_block,
        )

    # Fallback: old single-prompt format with regex splitting
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



def _build_support_block(channel_support: dict, channel_name: str = "") -> str:
    """Build a prominent support/donate call-to-action block."""
    links = []
    if channel_support.get("donate"):
        links.append(('💛 Támogatás', channel_support["donate"]))
    if channel_support.get("donate_1pct"):
        links.append(('🏛️ 1% felajánlás', channel_support["donate_1pct"]))
    if channel_support.get("patreon"):
        links.append(('🎁 Patreon', channel_support["patreon"]))
    if channel_support.get("merch"):
        links.append(('🛍️ Merch', channel_support["merch"]))
    if not links:
        return ""

    if len(links) == 1:
        label, url = links[0]
        intro = f'Ha tetszett a tartalom, <strong>támogasd a {html.escape(channel_name)} csatornát!</strong>'
        links_html = f'<a class="support-link" href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{label}</a>'
    else:
        intro = f'Ha tetszett a tartalom, <strong>támogasd a {html.escape(channel_name)} csatornát</strong> – több lehetőség is van:'
        links_html = " ".join(
            f'<a class="support-link" href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{label}</a>'
            for label, url in links
        )

    return (
        f'<aside class="support-block">\n'
        f'  <span class="support-icon">🙏</span>\n'
        f'  <div class="support-text">{intro}</div>\n'
        f'  <div class="support-links">{links_html}</div>\n'
        f'</aside>'
    )


def _build_video_page(fm: dict, tldr_md: str, details_md: str, uncertain_md: str, transcript_block: str, root: str = "..", source_rel: str = "", channel_data: dict | None = None) -> str:
    # channel_support also carries affiliation/direction/notes from channels.yaml (canonical)
    video_id = html.escape(str(fm.get("video_id", "")))
    video_url = html.escape(str(fm.get("video_url", f"https://www.youtube.com/watch?v={video_id}")))
    title = str(fm.get("title", ""))
    title_esc = html.escape(title)
    channel_name = html.escape(str(fm.get("channel_name", "")))
    date_display = html.escape(_fmt_date(str(fm.get("published_at", fm.get("date", "")))))
    ch = channel_data or {}
    tags = list(fm.get("tags", []) or [])
    for dt in (ch.get("default_tags") or []):
        if dt and dt not in tags:
            tags.append(dt)
    tags_html = "".join(f'<span class="tag" data-tag="{html.escape(t)}">{html.escape(t)}</span>' for t in tags)
    duration_sec = fm.get("duration_sec", 0) or 0
    dur = _fmt_duration(duration_sec)
    duration_span = f'<span class="badge-src">{html.escape(dur)}</span>' if dur else ""
    source_label = html.escape(
        "YouTube felirat" if fm.get("transcript_source") == "youtube_subtitle" else "Whisper ASR"
    )
    summary_model = html.escape(str(fm.get("summary_model", "")))
    affiliation = str(ch.get("affiliation") or fm.get("affiliation") or "").strip()
    direction = str(ch.get("direction") or fm.get("direction") or "").strip()
    notes = str(ch.get("notes") or fm.get("notes") or "").strip()
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
    tldr_block = (
        f'<section class="tldr">\n'
        f'    <div class="tldr-header">\n'
        f'      <div class="tldr-label">tl;dr</div>\n'
        f'      <button class="tts-btn" data-tts-content="tldr-content" data-tts-reading="tldr-reading" data-tts-label="tl;dr">&#9654; Felolvasás</button>\n'
        f'    </div>\n'
        f'    <div id="tldr-content">{tldr_html}</div>\n'
        f'    <div id="tldr-reading" class="tts-reading-view" style="display:none"></div>\n'
        f'  </section>'
    ) if tldr_html else ""
    support_block = _build_support_block(channel_data or {}, channel_name=str(fm.get("channel_name", "")))
    details_block = (
        f'<section class="collapsible summary">\n'
        f'    <details id="details-details">\n'
        f'      <summary>Részletes összefoglaló megjelenítése'
        f'<button class="tts-btn tts-btn-summary" data-tts-content="details-content" data-tts-reading="details-reading" data-tts-details="details-details" data-tts-label="Részletes összefoglaló">&#9654; Felolvasás</button></summary>\n'
        f'      <div class="collapsible-inner summary-inner" id="details-content">{details_html}</div>\n'
        f'      <div id="details-reading" class="tts-reading-view collapsible-inner" style="display:none"></div>\n'
        f'    </details>\n'
        f'  </section>'
    ) if details_html else ""
    uncertain_block = (
        f'<section class="collapsible uncertain">\n'
        f'    <details>\n'
        f'      <summary>⚠️ Értelmezhetetlen vagy bizonytalan szakaszok</summary>\n'
        f'      <div class="collapsible-inner uncertain-inner">{uncertain_html}</div>\n'
        f'    </details>\n'
        f'  </section>'
    ) if uncertain_html else ""
    transcript_html = _transcript_to_html(transcript_block)
    plain_summary = re.sub(r"<[^>]+>", "", tldr_html or details_html).strip()
    desc = html.escape(plain_summary[:160])

    edit_url = html.escape(f"{GITHUB_REPO_URL}/blob/main/content/{source_rel}") if source_rel else html.escape(GITHUB_REPO_URL)
    issues_url = html.escape(ISSUES_URL)

    # Canonical URL (page_url is relative like "v/channel/date-slug.html")
    _page_rel = fm.get("_page_url_rel", "")
    canonical_url = html.escape(f"{_SITE_BASE_URL}/{_page_rel}" if _page_rel else _SITE_BASE_URL)

    # JSON-LD VideoObject
    published_iso = str(fm.get("published_at", fm.get("date", "")))
    _jsonld = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": title,
        "description": plain_summary[:300],
        "thumbnailUrl": f"https://i.ytimg.com/vi/{fm.get('video_id', '')}/hqdefault.jpg",
        "uploadDate": published_iso,
        "embedUrl": f"https://www.youtube.com/embed/{fm.get('video_id', '')}",
        "url": str(fm.get("video_url", f"https://www.youtube.com/watch?v={fm.get('video_id', '')}")),
        "publisher": {
            "@type": "Organization",
            "name": str(fm.get("channel_name", "")),
        },
    }
    if duration_sec:
        h, m, s = duration_sec // 3600, (duration_sec % 3600) // 60, duration_sec % 60
        _jsonld["duration"] = f"PT{h}H{m}M{s}S" if h else f"PT{m}M{s}S"
    jsonld_str = html.escape(json.dumps(_jsonld, ensure_ascii=False), quote=False)

    return (
        _VIDEO_TMPL.format(
            root=root,
            edit_url=edit_url,
            issues_url=issues_url,
            title=title,
            title_esc=title_esc,
            desc=desc,
            canonical_url=canonical_url,
            jsonld=jsonld_str,
            channel_name=channel_name,
            date_display=date_display,
            duration_span=duration_span,
            tags_html=tags_html,
            video_id=video_id,
            video_url=video_url,
            tldr_block=tldr_block,
            support_block=support_block,
            details_block=details_block,
            uncertain_block=uncertain_block,
            transcript_html=transcript_html,
            source_label=source_label,
            summary_model=summary_model,
            channel_meta_block=channel_meta_block,
        )
        .replace("__POSTHOG_SNIPPET__", _POSTHOG_SNIPPET)
        .replace("__TTS_BAR__", _TTS_BAR_HTML)
    )


def _card_html(entry: dict) -> str:
    teaser = html.escape(entry.get("teaser", "")[:200])
    title_esc = html.escape(entry["title"])
    tags_html = "".join(
        f'<span class="tag" data-tag="{html.escape(t)}">{html.escape(t)}</span>'
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



def _build_index(data: list[dict]) -> str:
    seen: dict[str, str] = {}
    for e in data:
        slug = e["channel_slug"]
        if slug not in seen:
            seen[slug] = e["channel_name"]

    channel_options = "\n              ".join(
        f'<li class="ch-dropdown-item" data-slug="{html.escape(slug)}">'
        f'<label><input type="checkbox" value="{html.escape(slug)}"> {html.escape(name)}</label>'
        f'</li>'
        for slug, name in seen.items()
    )

    # Collect all unique tags across all entries, sorted alphabetically
    all_tags: set[str] = set()
    for e in data:
        for t in (e.get("tags") or []):
            if t:
                all_tags.add(t)
    sorted_tags = sorted(all_tags, key=lambda t: t.lower())

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
    tag_options = "\n              ".join(
        f'<li class="ch-dropdown-item" data-slug="{html.escape(t)}">'
        f'<label><input type="checkbox" value="{html.escape(t)}"> {html.escape(t)}</label>'
        f'</li>'
        for t in sorted_tags
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
    return (
        _INDEX_TMPL.format(
            total=len(data),
            page_size=PAGE_SIZE,
            site_base_url=_SITE_BASE_URL,
            channel_options=channel_options,
            tag_options=tag_options,
            direction_chips=direction_chips,
            affiliation_chips=affiliation_chips,
            cards=cards,
        )
        .replace("__POSTHOG_SNIPPET__", _POSTHOG_SNIPPET)
        .replace("__POSTHOG_INIT_JS__", _POSTHOG_INIT_JS)
    )


# ── Main build ────────────────────────────────────────────────────────────────

def _load_channel_data(site_root: Path) -> dict[str, dict]:
    """Load all channel metadata keyed by channel slug.

    Returns a dict of slug → {affiliation, direction, notes, donate, donate_1pct, patreon, merch}.
    These values are the canonical source of truth and override frontmatter.
    """
    channels_file = site_root / "channels.yaml"
    if not channels_file.exists():
        return {}
    try:
        with channels_file.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"WARN: could not load channels.yaml: {e}")
        return {}
    result = {}
    for idx, ch in enumerate(raw.get("channels", [])):
        slug = ch.get("slug")
        if not slug:
            continue
        entry = {"_order": idx}
        for key in ("affiliation", "direction", "notes", "donate", "donate_1pct", "patreon", "merch", "default_tags"):
            if ch.get(key):
                entry[key] = ch[key]
        result[slug] = entry
    return result


def build(site_root: Path, out_dir: Path) -> None:
    content_dir = site_root / "content"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "v").mkdir(exist_ok=True)

    channel_data_map = _load_channel_data(site_root)

    # Copy static assets (minified)
    style = site_root / "scripts/style.css"
    if style.exists():
        minified = _minify_css(style.read_text(encoding="utf-8"))
        (out_dir / "style.css").write_text(minified, encoding="utf-8")
    app_js = site_root / "scripts/app.js"
    if app_js.exists():
        (out_dir / "scripts").mkdir(exist_ok=True)
        (out_dir / "scripts/app.js").write_text(app_js.read_text(encoding="utf-8"), encoding="utf-8")
    (out_dir / ".nojekyll").touch()

    # robots.txt – allow all crawlers incl. social scrapers; point to sitemap
    robots_txt = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "User-agent: facebookexternalhit\n"
        "Allow: /\n"
        "\n"
        "User-agent: Twitterbot\n"
        "Allow: /\n"
        "\n"
        "User-agent: LinkedInBot\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {_SITE_BASE_URL}/sitemap.xml\n"
    )
    (out_dir / "robots.txt").write_text(robots_txt, encoding="utf-8")

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
        ch_slug = str(fm.get("channel_slug", ""))
        ch_data = channel_data_map.get(ch_slug, {})
        fm["_page_url_rel"] = page_url
        page_html = _build_video_page(fm, tldr_md, details_md, uncertain_md, transcript_block, root=root, source_rel=source_rel, channel_data=ch_data)
        out_page = out_dir / page_url
        out_page.parent.mkdir(parents=True, exist_ok=True)
        out_page.write_text(page_html, encoding="utf-8")

        # Build data.json entry
        teaser_md = tldr_md or details_md
        plain_summary = re.sub(r"<[^>]+>", "", md_lib.markdown(teaser_md)).strip()
        date_iso = str(fm.get("date", ""))[:10]
        duration_sec = int(fm.get("duration_sec") or 0)
        # Merge channel default_tags into article tags (deduplicated, preserving order)
        article_tags = list(fm.get("tags") or [])
        for dt in (ch_data.get("default_tags") or []):
            if dt and dt not in article_tags:
                article_tags.append(dt)
        data.append({
            "video_id": str(fm.get("video_id", "")),
            "title": str(fm.get("title", "")),
            "channel_slug": str(fm.get("channel_slug", "")),
            "channel_name": str(fm.get("channel_name", "")),
            "date": date_iso,
            "date_display": _fmt_date(date_iso),
            "published_at": str(fm.get("published_at", fm.get("date", ""))),
            "tags": article_tags,
            "transcript_source": str(fm.get("transcript_source", "")),
            "summary_model": str(fm.get("summary_model", "")),
            "duration_sec": duration_sec,
            "duration_display": _fmt_duration(duration_sec),
            "page_url": page_url,
            "teaser": plain_summary[:200],
            "affiliation": str(ch_data.get("affiliation") or fm.get("affiliation") or ""),
            "direction": str(ch_data.get("direction") or fm.get("direction") or ""),
            "notes": str(ch_data.get("notes") or fm.get("notes") or ""),
            "channel_order": ch_data.get("_order", 9999),
        })

    # Sort newest-first by date, then within the same day by channel order
    # from channels.yaml (ascending), then by published_at descending as tiebreaker.
    data.sort(
        key=lambda e: (
            -(datetime.fromisoformat(str(e.get("date") or "1970-01-01").replace("Z", "+00:00")).toordinal()),
            e.get("channel_order", 9999),
            # within same channel+date, newest first
            -(datetime.fromisoformat(str(e.get("published_at") or e.get("date") or "1970-01-01")[:19].replace("Z", "+00:00")).timestamp()),
        ),
    )

    # Write sitemap.xml
    _today = datetime.utcnow().strftime("%Y-%m-%d")
    sitemap_urls = [f"  <url><loc>{_SITE_BASE_URL}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>"]
    for entry in data:
        loc = f"{_SITE_BASE_URL}/{entry['page_url']}"
        lastmod = entry.get("date") or _today
        sitemap_urls.append(f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>")
    sitemap_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(sitemap_urls)
        + "\n</urlset>\n"
    )
    (out_dir / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")

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
