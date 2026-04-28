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
from datetime import datetime
from pathlib import Path

import markdown as md_lib
import yaml


# ── PostHog snippet (consent-gated) ──────────────────────────────────────────
_POSTHOG_SNIPPET = """\
<script>
(function(){
  try{
    if(localStorage.getItem('ytm_cookie_consent')==='1'){
      !function(t,e){var o,n,p,r;e.__SV||(window.posthog&&window.posthog.__loaded)||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="Ei Ni init zi Gi Nr Ui Xi Vi capture calculateEventProperties tn register register_once register_for_session unregister unregister_for_session an getFeatureFlag getFeatureFlagPayload getFeatureFlagResult isFeatureEnabled reloadFeatureFlags updateFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSurveysLoaded onSessionId getSurveys getActiveMatchingSurveys renderSurvey displaySurvey cancelPendingSurvey canRenderSurvey canRenderSurveyAsync ln identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset setIdentity clearIdentity get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException addExceptionStep captureLog startExceptionAutocapture stopExceptionAutocapture loadToolbar get_property getSessionProperty nn Qi createPersonProfile setInternalOrTestUser sn qi cn opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing get_explicit_consent_status is_capturing clear_opt_in_out_capturing Ji debug Fr rn getPageViewId captureTraceFeedback captureTraceMetric Bi".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
      posthog.init('phc_qjVik3YsYrLt6ZUjQbJZhneSwztCdFUmaZxfihqpjXVi',{api_host:'https://eu.i.posthog.com',defaults:'2026-01-30',person_profiles:'identified_only'});
    }
  }catch(e){}
})();
</script>"""

# Same snippet for use inside Python format strings ({{ }} escaping not needed
# here because _POSTHOG_SNIPPET is inserted via .replace(), not .format()).

# Inline init call used inside the JS ytmCloseWelcome handler (already inside
# a JS context so we only need the bare init logic, not the outer page script tag).
_POSTHOG_INIT_JS = """\
      !function(t,e){var o,n,p,r;e.__SV||(window.posthog&&window.posthog.__loaded)||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="Ei Ni init zi Gi Nr Ui Xi Vi capture calculateEventProperties tn register register_once register_for_session unregister unregister_for_session an getFeatureFlag getFeatureFlagPayload getFeatureFlagResult isFeatureEnabled reloadFeatureFlags updateFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSurveysLoaded onSessionId getSurveys getActiveMatchingSurveys renderSurvey displaySurvey cancelPendingSurvey canRenderSurvey canRenderSurveyAsync ln identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset setIdentity clearIdentity get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException addExceptionStep captureLog startExceptionAutocapture stopExceptionAutocapture loadToolbar get_property getSessionProperty nn Qi createPersonProfile setInternalOrTestUser sn qi cn opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing get_explicit_consent_status is_capturing clear_opt_in_out_capturing Ji debug Fr rn getPageViewId captureTraceFeedback captureTraceMetric Bi".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
      posthog.init('phc_qjVik3YsYrLt6ZUjQbJZhneSwztCdFUmaZxfihqpjXVi',{api_host:'https://eu.i.posthog.com',defaults:'2026-01-30',person_profiles:'identified_only'});"""


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

_SITE_BASE_URL = "https://roviden.jegyezve.com"

_VIDEO_TMPL = """\
<!doctype html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,maximum-scale=1">
<title>{title} - Röviden</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical_url}">
<!-- Open Graph -->
<meta property="og:type" content="video.other">
<meta property="og:site_name" content="Röviden">
<meta property="og:url" content="{canonical_url}">
<meta property="og:title" content="{title} - Röviden">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://i.ytimg.com/vi/{video_id}/hqdefault.jpg">
<meta property="og:image:width" content="480">
<meta property="og:image:height" content="360">
<meta property="og:locale" content="hu_HU">
<!-- Twitter / X Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title} - Röviden">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://i.ytimg.com/vi/{video_id}/hqdefault.jpg">
<!-- JSON-LD -->
<script type="application/ld+json">{jsonld}</script>
<link rel="stylesheet" href="{root}/style.css">
__POSTHOG_SNIPPET__
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
  {support_block}
  {details_block}
  {uncertain_block}

  <section class="collapsible transcript">
    <details>
      <summary>Teljes átirat megjelenítése</summary>
      <div class="collapsible-inner transcript-inner">
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
    tldr_block = f'<section class="tldr">\n    <div class="tldr-label">tl;dr</div>\n    {tldr_html}\n  </section>' if tldr_html else ""
    support_block = _build_support_block(channel_data or {}, channel_name=str(fm.get("channel_name", "")))
    details_block = (
        f'<section class="collapsible summary">\n'
        f'    <details>\n'
        f'      <summary>Részletes összefoglaló megjelenítése</summary>\n'
        f'      <div class="collapsible-inner summary-inner">{details_html}</div>\n'
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


PAGE_SIZE = 20


_INDEX_TMPL = """\
<!doctype html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,maximum-scale=1">
<title>Röviden - Hosszú beszélgetések, podcastek és interjúk dióhéjban</title>
<meta name="description" content="Hosszú magyar podcastek, interjúk és beszélgetések AI-összefoglalói – gyorsan átláthatod a lényeget.">
<link rel="canonical" href="{site_base_url}/">
<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="Röviden">
<meta property="og:url" content="{site_base_url}/">
<meta property="og:title" content="Röviden - Hosszú beszélgetések, podcastek és interjúk dióhéjban">
<meta property="og:description" content="Hosszú magyar podcastek, interjúk és beszélgetések AI-összefoglalói – gyorsan átláthatod a lényeget.">
<meta property="og:locale" content="hu_HU">
<!-- Twitter / X Card -->
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Röviden - Hosszú beszélgetések, podcastek és interjúk dióhéjban">
<meta name="twitter:description" content="Hosszú magyar podcastek, interjúk és beszélgetések AI-összefoglalói – gyorsan átláthatod a lényeget.">
<!-- JSON-LD -->
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"Röviden","url":"{site_base_url}/","description":"Hosszú magyar podcastek, interjúk és beszélgetések AI-összefoglalói.","inLanguage":"hu"}}</script>
<link rel="stylesheet" href="style.css">
__POSTHOG_SNIPPET__
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
      <li>A csatornák kategorizálása, politikai hovatartozása, irányultsága csak egy kiinduló állapot, alakíthatóak, ezzel kapcsolatban kritikákat, módosítási javaslatokat GitHub-on várjuk!</li>
    </ul>
     <details class="cookie-policy">
      <summary>Videós tartalomkészítőknek</summary>
      <div class="cookie-policy-body">
       <p>Be kell vallanunk, hogy ezzel a projekttel kapcsolatban vannak fenntartásaink. Egyértelmű volt az igény a közönség részéről a többórás videók rövid összefoglalóira, viszont fennáll a veszélye annak, hogy a látogatók csak az AI-összefoglalókat olvassák el, és nem nézik meg magát a videót. Ez hosszú távon <strong>csökkentheti a csatornák nézettségét</strong>, ami egyrészt megnehezíti a médiumok számára, hogy felmérjék a közönségük valós igényeit, másrészt <strong>bevételkiesést</strong> is okozhat számukra.</p>
        <p>Minden olyan csatornánál ahol fellelhető volt a csatornatámoatás valamilyen formája (közvetelen támogatás, patreon, SZJA1%, merch), ott az összefoglalók alatt ezeknek elérhetőségét megjelenítettük minden összefoglaló alatt.</p>
        <p>Amennyiben Ön egy érintett médium képviselője, bármilyen észrevétele, kérése van az oldallal kapcsolatban – kérjük, vegye fel velünk a kapcsolatot az <a href="mailto:info@jegyezve.com">info@jegyezve.com</a> címen.</p>
        <p class="modal-outro">Köszönjük a megértést, és jó olvasást / videózást kívánunk!</p>
      </div>
    </details>
    <details class="cookie-policy">
      <summary>Süti (cookie) tájékoztató</summary>
      <div class="cookie-policy-body">
        <p>Ez az oldal a <strong>PostHog</strong> elemző szolgáltatást használja látogatottsági adatok gyűjtésére. A következő adatokat rögzíthetjük:</p>
        <ul>
          <li>Megtekintett oldalak és videók</li>
          <li>Kattintások és szűrőhasználat</li>
          <li>Böngésző típusa, képernyőfelbontás, hozzávetőleges földrajzi helyzet (ország szintű)</li>
          <li>Munkamenet-azonosító (véletlenszerűen generált, nem kapcsolható személyhez)</li>
        </ul>
        <p>Az adatokat <strong>nem adjuk át harmadik félnek</strong>, kizárólag az oldal fejlesztéséhez és a tartalom minőségének javításához használjuk. A PostHog adatait az EU-ban tároljuk (<code>eu.i.posthog.com</code>).</p>
      </div>
    </details>
    <p>A „Megértettem és elfogadom" gombra kattintva hozzájárulsz a fenti sütik használatához. A „Csak megnézem" gombbal süti nélkül is teljes mértékben használhatod az oldalt – ebben az esetben nem gyűjtünk semmilyen adatot.</p>
    <div class="modal-actions">
      <button class="modal-decline" type="button" onclick="ytmDeclineWelcome()">Csak megnézem, köszönöm</button>
      <button class="modal-btn" type="button" onclick="ytmCloseWelcome()">Megértettem és elfogadom</button>
    </div>
  </div>
</div>
<button id="about-fab" class="about-fab" type="button" onclick="ytmOpenWelcome()" aria-label="Az oldalról">Az oldalról</button>
<div id="tour-overlay" class="tour-overlay" hidden></div>
<div id="tour-tooltip" class="tour-tooltip" hidden role="dialog" aria-modal="true" aria-label="Bemutató">
  <div class="tour-step-indicator" id="tour-step-indicator"></div>
  <div class="tour-body" id="tour-body"></div>
  <div class="tour-actions">
    <button class="tour-btn-skip" type="button" onclick="ytmTourSkip()">Kihagyás</button>
    <button class="tour-btn-next" type="button" id="tour-next-btn" onclick="ytmTourNext()">Következő →</button>
  </div>
</div>
<header class="site-header">
  <div class="site-header-inner">
    <div class="site-header-left">
      <h1>Röviden</h1>
      <p class="site-sub">Hosszú beszélgetések, podcastek és interjúk dióhéjban</p>
    </div>
    <div class="site-header-right">
      <button class="filter-clear" id="filter-clear" type="button" onclick="ytmClearFilters()" hidden>Szűrők törlése &times;</button>
      <button class="filter-toggle" id="filter-toggle" type="button" aria-expanded="false" aria-controls="filter-groups" onclick="ytmToggleFilters()">
        <span class="filter-toggle-hamburger" aria-hidden="true">
          <span></span><span></span><span></span>
        </span>
        <span class="filter-toggle-label">Szűrők</span>
        <span class="filter-active-badge" id="filter-badge" aria-live="polite"></span>
        <span class="filter-toggle-icon" aria-hidden="true">▾</span>
      </button>
      <input class="filter-search" id="search-input" type="search"
             placeholder="Cím, csatorna, tartalom…" autocomplete="off">
    </div>
  </div>
  <div class="filter-bar">
    <div class="filter-groups" id="filter-groups" hidden>
      <div class="filter-row filter-row-combined">
        <span class="filter-label">Csatorna:</span>
        <div class="ch-dropdown" id="ch-dropdown">
          <button class="ch-dropdown-btn" id="ch-dropdown-btn" type="button" aria-haspopup="listbox" aria-expanded="false">
            <span class="ch-dropdown-label" id="ch-dropdown-label">Összes csatorna</span>
            <span class="ch-dropdown-arrow" aria-hidden="true">▾</span>
          </button>
          <div class="ch-dropdown-panel" id="ch-dropdown-panel" hidden role="listbox" aria-multiselectable="true">
            <div class="ch-dropdown-search-wrap">
              <input class="ch-dropdown-search" id="ch-dropdown-search" type="search" placeholder="Csatorna keresése…" autocomplete="off" spellcheck="false">
            </div>
            <ul class="ch-dropdown-list" id="ch-dropdown-list">
              <li class="ch-dropdown-item ch-dropdown-all active" data-slug="" id="ch-all-item">
                <span class="ch-dropdown-all-btn">Összes ({total})</span>
              </li>
              {channel_options}
            </ul>
          </div>
        </div>
        <span class="filter-label filter-label-mid">Címke:</span>
        <div class="ch-dropdown" id="tag-dropdown">
          <button class="ch-dropdown-btn" id="tag-dropdown-btn" type="button" aria-haspopup="listbox" aria-expanded="false">
            <span class="ch-dropdown-label" id="tag-dropdown-label">Összes címke</span>
            <span class="ch-dropdown-arrow" aria-hidden="true">▾</span>
          </button>
          <div class="ch-dropdown-panel" id="tag-dropdown-panel" hidden role="listbox" aria-multiselectable="true">
            <div class="ch-dropdown-search-wrap">
              <input class="ch-dropdown-search" id="tag-dropdown-search" type="search" placeholder="Címke keresése…" autocomplete="off" spellcheck="false">
            </div>
            <ul class="ch-dropdown-list" id="tag-dropdown-list">
              <li class="ch-dropdown-item ch-dropdown-all active" data-slug="" id="tag-all-item">
                <span class="ch-dropdown-all-btn">Összes</span>
              </li>
              {tag_options}
            </ul>
          </div>
        </div>
        <span class="filter-label-group"><span class="filter-label filter-label-mid">Irányultság:</span>
        <span class="chip-group" data-group="direction">
          <button class="chip active" data-group="direction" data-f="">Összes</button>
          {direction_chips}
        </span></span>
        <span class="filter-label-group"><span class="filter-label filter-label-mid">Kötődés:</span>
        <span class="chip-group" data-group="affiliation">
          <button class="chip active" data-group="affiliation" data-f="">Összes</button>
          {affiliation_chips}
        </span></span>
      </div>
    </div>
  </div>
</header>
<main class="feed" id="feed">
{cards}
</main>
<div id="pag"></div>
<script>
// ── Guided tour ──────────────────────────────────────────────────────────
(function(){{
  var TOUR_KEY='ytm_tour_done_v1';
  var tourStep=0;
  var tourActive=false;

  var STEPS=[
    {{
      targetId:'filter-toggle',
      title:'Szűrők',
      body:'Ezzel a gombbal nyithatod meg a szűrőket. Szűrhetsz csatornára, politikai irányultságra és kötődésre is.',
      position:'bottom',
      action: function(){{
        // open the filter panel if not open
        var fg=document.getElementById('filter-groups');
        var btn=document.getElementById('filter-toggle');
        if(fg && fg.hidden){{
          fg.hidden=false;
          if(btn) btn.setAttribute('aria-expanded','true');
          var icon=btn&&btn.querySelector('.filter-toggle-icon');
          if(icon) icon.textContent='▴';
        }}
      }}
    }},
    {{
      targetId:'filter-groups',
      title:'Irányultság',
      body:'Az <strong>Irányultság</strong> szűrővel politikai spektrum szerint szűrhetsz: liberális, centrista, konzervatív vagy szélsőjobb. Egyszerre több is kijelölhető.',
      position:'bottom',
      highlight: function(){{ return document.querySelector('.chip-group[data-group="direction"]'); }}
    }},
    {{
      targetId:'filter-groups',
      title:'Kötődés',
      body:'A <strong>Kötődés</strong> szűrővel a csatorna politikai kötődése szerint szűrhetsz: független, Fidesz-közeli, Tisza-közeli vagy ellenzéki.',
      position:'bottom',
      highlight: function(){{ return document.querySelector('.chip-group[data-group="affiliation"]'); }}
    }},
    {{
      targetId:'ch-dropdown-btn',
      title:'Csatorna szűrő',
      body:'A <strong>Csatorna</strong> legördülőből egy vagy több konkrét csatornát is kiválaszthatsz. A lista a többi aktív szűrő alapján automatikusan rendezi magát.',
      position:'bottom'
    }},
    {{
      targetId:'search-input',
      title:'Szabad szöveges keresés',
      body:'Cím, csatorna neve vagy az összefoglaló tartalma alapján is kereshetsz. A szűrők és a keresés egyszerre is használhatók.',
      position:'bottom'
    }}
  ];

  function getTarget(step){{
    if(step.highlight) return step.highlight();
    return document.getElementById(step.targetId);
  }}

  function positionTooltip(el){{
    var tooltip=document.getElementById('tour-tooltip');
    if(!el||!tooltip) return;
    var rect=el.getBoundingClientRect();
    var tw=tooltip.offsetWidth||320;
    var th=tooltip.offsetHeight||160;
    var margin=12;
    var scrollY=window.scrollY||window.pageYOffset;
    var scrollX=window.scrollX||window.pageXOffset;
    var vw=window.innerWidth;

    // prefer below
    var top=rect.bottom+scrollY+margin;
    var left=rect.left+scrollX+rect.width/2-tw/2;

    // clamp horizontally
    if(left<8) left=8;
    if(left+tw>vw-8) left=vw-tw-8;

    // if would go off bottom, put above
    if(rect.bottom+margin+th>window.innerHeight){{
      top=rect.top+scrollY-th-margin;
    }}

    tooltip.style.top=top+'px';
    tooltip.style.left=left+'px';
  }}

  function highlightEl(el){{
    document.querySelectorAll('.tour-highlight').forEach(function(x){{x.classList.remove('tour-highlight');}});
    if(el) el.classList.add('tour-highlight');
  }}

  function showStep(i){{
    var tooltip=document.getElementById('tour-tooltip');
    var overlay=document.getElementById('tour-overlay');
    var body=document.getElementById('tour-body');
    var indicator=document.getElementById('tour-step-indicator');
    var nextBtn=document.getElementById('tour-next-btn');
    if(!tooltip||!overlay) return;

    var step=STEPS[i];
    if(!step){{ endTour(); return; }}

    // run any action (e.g. open filter panel)
    if(step.action) step.action();

    var target=getTarget(step);
    body.innerHTML='<h3 class="tour-title">'+step.title+'</h3><p>'+step.body+'</p>';
    indicator.textContent=(i+1)+' / '+STEPS.length;
    nextBtn.textContent=(i===STEPS.length-1)?'Befejezés ✓':'Következő →';

    overlay.hidden=false;
    tooltip.hidden=false;

    // position after paint
    requestAnimationFrame(function(){{
      requestAnimationFrame(function(){{
        positionTooltip(target);
        highlightEl(target);
        // scroll target into view
        if(target) target.scrollIntoView({{behavior:'smooth',block:'nearest',inline:'nearest'}});
      }});
    }});
  }}

  function endTour(){{
    var tooltip=document.getElementById('tour-tooltip');
    var overlay=document.getElementById('tour-overlay');
    if(tooltip) tooltip.hidden=true;
    if(overlay) overlay.hidden=true;
    document.querySelectorAll('.tour-highlight').forEach(function(x){{x.classList.remove('tour-highlight');}});
    tourActive=false;
    try{{localStorage.setItem(TOUR_KEY,'1');}}catch(e){{}}
  }}

  window.ytmTourNext=function(){{
    tourStep++;
    if(tourStep>=STEPS.length){{ endTour(); return; }}
    showStep(tourStep);
  }};
  window.ytmTourSkip=function(){{ endTour(); }};

  window.ytmStartTour=function(){{
    try{{ if(localStorage.getItem(TOUR_KEY)) return; }}catch(e){{}}
    tourStep=0;
    tourActive=true;
    // small delay so modal close animation finishes
    setTimeout(function(){{ showStep(0); }},400);
  }};

  // reposition on resize
  window.addEventListener('resize',function(){{
    if(!tourActive) return;
    var step=STEPS[tourStep];
    if(step) positionTooltip(getTarget(step));
  }});
}})();

(function(){{
  window.ytmDeclineWelcome=function(){{
    var m=document.getElementById('welcome-modal');
    if(m){{m.hidden=true;document.body.classList.remove('modal-open');}}
    try{{localStorage.setItem('ytm_welcome_seen','1');}}catch(e){{}}
    // no consent set — PostHog will not be initialised
    if(typeof ytmStartTour==='function') ytmStartTour();
  }};
  window.ytmOpenWelcome=function(){{
    var m=document.getElementById('welcome-modal');
    if(m){{m.hidden=false;document.body.classList.add('modal-open');}}
  }};
  window.ytmCloseWelcome=function(){{
    var m=document.getElementById('welcome-modal');
    if(m){{m.hidden=true;document.body.classList.remove('modal-open');}}
    try{{
      localStorage.setItem('ytm_welcome_seen','1');
      localStorage.setItem('ytm_cookie_consent','1');
    }}catch(e){{}}
    // Initialise PostHog now that the user has consented
    try{{
      if(!window.posthog||!window.posthog.__loaded){{
        __POSTHOG_INIT_JS__
      }}
      // Identify the user with a stable anonymous ID
      var uid;
      try{{uid=localStorage.getItem('ytm_uid');}}catch(e){{}}
      if(!uid){{
        uid='u-'+([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g,function(c){{
          return(c^(crypto.getRandomValues(new Uint8Array(1))[0]&(15>>(c/4)))).toString(16);
        }});
        try{{localStorage.setItem('ytm_uid',uid);}}catch(e){{}}
      }}
      if(window.posthog&&window.posthog.identify){{
        window.posthog.identify(uid);
      }}
    }}catch(e){{}}
    if(typeof ytmStartTour==='function') ytmStartTour();
  }};
  try{{
    if(!localStorage.getItem('ytm_welcome_seen')){{
      window.ytmOpenWelcome();
    }}
  }}catch(e){{}}
}})();
(function(){{
  var N={page_size},TOTAL={total},page=1,data=null,loading=null;
  var filters={{channel:[],direction:[],affiliation:[],tag:[],search:''}};
  var MULTI={{direction:true,affiliation:true}};
  var feed=document.getElementById('feed');

  var FILTER_STORAGE_KEY='ytm_filters_v1';

  function saveFilters(){{
    try{{localStorage.setItem(FILTER_STORAGE_KEY,JSON.stringify(filters));}}catch(e){{}}
    try{{localStorage.setItem('ytm_page',String(page));}}catch(e){{}}
  }}

  function loadSavedFilters(){{
    try{{
      var raw=localStorage.getItem(FILTER_STORAGE_KEY);
      if(!raw) return;
      var saved=JSON.parse(raw);
      if(saved.channel!==undefined) filters.channel=saved.channel;
      if(Array.isArray(saved.direction)) filters.direction=saved.direction;
      if(Array.isArray(saved.affiliation)) filters.affiliation=saved.affiliation;
      if(Array.isArray(saved.tag)) filters.tag=saved.tag;
      if(saved.search!==undefined) filters.search=saved.search;
    }}catch(e){{}}
    try{{
      var sp=localStorage.getItem('ytm_page');
      if(sp) page=Math.max(1,parseInt(sp,10)||1);
    }}catch(e){{}}
  }}

  function applyFiltersToUI(){{
    // search input
    var si=document.getElementById('search-input');
    if(si && filters.search) si.value=filters.search;
    // channel checkboxes
    syncChannelCheckboxes();
    updateChannelBtnLabel();
    // tag checkboxes
    syncTagCheckboxes();
    updateTagBtnLabel();
    // chips
    ['direction','affiliation'].forEach(function(group){{
      var arr=filters[group];
      var allChip=document.querySelector('.chip[data-group="'+group+'"][data-f=""]');
      if(!arr || arr.length===0){{
        // ensure "Összes" is active
        document.querySelectorAll('.chip[data-group="'+group+'"]').forEach(function(x){{x.classList.remove('active');}});
        if(allChip) allChip.classList.add('active');
      }} else {{
        if(allChip) allChip.classList.remove('active');
        document.querySelectorAll('.chip[data-group="'+group+'"]').forEach(function(x){{
          x.classList.toggle('active', arr.indexOf(x.dataset.f)!==-1);
        }});
      }}
    }});
  }}

  function syncChannelCheckboxes(){{
    var allItem=document.getElementById('ch-all-item');
    var items=document.querySelectorAll('#ch-dropdown-list .ch-dropdown-item:not(.ch-dropdown-all)');
    var sel=filters.channel;
    if(!sel||sel.length===0){{
      if(allItem) allItem.classList.add('active');
      items.forEach(function(li){{
        var cb=li.querySelector('input[type=checkbox]');
        if(cb) cb.checked=false;
      }});
    }} else {{
      if(allItem) allItem.classList.remove('active');
      items.forEach(function(li){{
        var cb=li.querySelector('input[type=checkbox]');
        if(cb) cb.checked=sel.indexOf(li.dataset.slug)!==-1;
      }});
    }}
  }}

  function updateChannelListAvailability(){{
    if(!data) return;
    // Find which slugs have at least one card matching current direction/affiliation filters (ignoring channel filter)
    var available={{}};
    data.forEach(function(e){{
      if(filters.direction.length && filters.direction.indexOf(e.direction||'')===-1) return;
      if(filters.affiliation.length && filters.affiliation.indexOf(e.affiliation||'')===-1) return;
      if(filters.tag.length){{var et=e.tags||[];if(!filters.tag.some(function(t){{return et.indexOf(t)!==-1;}})) return;}}
      available[e.channel_slug]=true;
    }});
    var list=document.getElementById('ch-dropdown-list');
    if(!list) return;
    var items=Array.from(list.querySelectorAll('.ch-dropdown-item:not(.ch-dropdown-all)'));
    var available_items=[], unavailable_items=[];
    items.forEach(function(li){{
      var slug=li.dataset.slug;
      if(available[slug]){{
        li.classList.remove('ch-dropdown-item-unavailable');
        available_items.push(li);
      }} else {{
        li.classList.add('ch-dropdown-item-unavailable');
        unavailable_items.push(li);
      }}
    }});
    // Re-order: available first, then unavailable
    available_items.concat(unavailable_items).forEach(function(li){{
      list.appendChild(li);
    }});
  }}

  function updateChannelBtnLabel(){{
    var lbl=document.getElementById('ch-dropdown-label');
    if(!lbl) return;
    var sel=filters.channel;
    if(!sel||sel.length===0){{
      lbl.textContent='Összes csatorna';
    }} else if(sel.length===1){{
      // find name
      var item=document.querySelector('#ch-dropdown-list .ch-dropdown-item[data-slug="'+sel[0]+'"]');
      var name=item?item.querySelector('label').textContent.trim():sel[0];
      lbl.textContent=name;
    }} else {{
      lbl.textContent=sel.length+' csatorna kiválasztva';
    }}
  }}

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
    var tags=(e.tags||[]).map(function(t){{return '<span class="tag" data-tag="'+esc(t)+'">'+esc(t)+'</span>';}}).join('');
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

  function fuzzyMatch(query, e){{
    if(!query) return true;
    var haystack=(
      (e.title||'')+' '+(e.teaser||'')+' '+(e.channel_name||'')+' '+(e.tags||[]).join(' ')
    ).toLowerCase();
    var words=query.toLowerCase().split(/\\s+/).filter(Boolean);
    return words.every(function(w){{return haystack.indexOf(w)!==-1;}});
  }}

  function renderFromData(){{
    var vis=data.filter(function(e){{
      if(filters.channel.length && filters.channel.indexOf(e.channel_slug)===-1) return false;
      if(filters.direction.length && filters.direction.indexOf(e.direction||'')===-1) return false;
      if(filters.affiliation.length && filters.affiliation.indexOf(e.affiliation||'')===-1) return false;
      if(filters.tag.length){{var et=e.tags||[];if(!filters.tag.some(function(t){{return et.indexOf(t)!==-1;}})) return false;}}
      if(!fuzzyMatch(filters.search, e)) return false;
      return true;
    }});
    var pages=Math.max(1,Math.ceil(vis.length/N));
    if(page>pages) page=pages;
    // Sort filtered results: by date desc, then channel_order asc, then published_at desc
    vis.sort(function(a,b){{
      if(a.date>b.date) return -1;
      if(a.date<b.date) return 1;
      var oa=(a.channel_order!=null)?a.channel_order:9999;
      var ob=(b.channel_order!=null)?b.channel_order:9999;
      if(oa!==ob) return oa-ob;
      var pa=a.published_at||a.date||'';
      var pb=b.published_at||b.date||'';
      if(pa>pb) return -1;
      if(pa<pb) return 1;
      return 0;
    }});
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

  // Restore saved filters on load
  loadSavedFilters();
  applyFiltersToUI();
  updateFilterBadge();
  var _hasActiveFilters=(filters.search||filters.channel.length||filters.direction.length||filters.affiliation.length||filters.tag.length);
  var _hasNonFirstPage=(page>1);
  if(_hasActiveFilters||_hasNonFirstPage){{
    var fg=document.getElementById('filter-groups');
    var btn=document.getElementById('filter-toggle');
    if(fg){{fg.hidden=false;}}
    if(btn){{btn.setAttribute('aria-expanded','true');btn.querySelector('.filter-toggle-icon').textContent='▴';}}
    loadData().then(function(){{ renderFromData(); updateChannelListAvailability(); }});
  }} else if(TOTAL>N){{
    renderPag(Math.ceil(TOTAL/N));
  }}

  function navigate(){{
    loadData().then(function(){{
      renderFromData();
      window.scrollTo(0,0);
    }});
  }}

  window.ytmPrev=function(){{if(page>1){{page--;saveFilters();navigate();}}}};
  window.ytmNext=function(){{page++;saveFilters();navigate();}};
  function updateFilterBadge(){{
    var badge=document.getElementById('filter-badge');
    if(!badge) return;
    var count=0;
    if(filters.search) count++;
    if(filters.channel && filters.channel.length) count+=filters.channel.length;
    if(filters.direction && filters.direction.length) count+=filters.direction.length;
    if(filters.affiliation && filters.affiliation.length) count+=filters.affiliation.length;
    if(filters.tag && filters.tag.length) count+=filters.tag.length;
    if(count>0){{
      badge.textContent=count;
      badge.classList.add('visible');
    }} else {{
      badge.textContent='';
      badge.classList.remove('visible');
    }}
    var clearBtn=document.getElementById('filter-clear');
    if(clearBtn) clearBtn.hidden=count===0;
  }}

  window.ytmClearFilters=function(){{
    filters={{channel:[],direction:[],affiliation:[],tag:[],search:''}};
    // Reset search input
    var si=document.getElementById('search-input');
    if(si) si.value='';
    // Reset channel dropdown
    syncChannelCheckboxes();
    updateChannelBtnLabel();
    // Reset tag dropdown
    syncTagCheckboxes();
    updateTagBtnLabel();
    // Reset chips
    ['direction','affiliation'].forEach(function(group){{
      document.querySelectorAll('.chip[data-group="'+group+'"]').forEach(function(x){{x.classList.remove('active');}});
      var allChip=document.querySelector('.chip[data-group="'+group+'"][data-f=""]');
      if(allChip) allChip.classList.add('active');
    }});
    page=1;
    updateFilterBadge();
    saveFilters();
    loadData().then(function(){{ renderFromData(); updateChannelListAvailability(); }});
  }};

  window.ytmToggleFilters=function(){{
    var fg=document.getElementById('filter-groups');
    var btn=document.getElementById('filter-toggle');
    if(!fg||!btn) return;
    var open=fg.hidden;
    fg.hidden=!open;
    btn.setAttribute('aria-expanded', open?'true':'false');
    btn.querySelector('.filter-toggle-icon').textContent=open?'▴':'▾';
  }};

  var searchInput=document.getElementById('search-input');
  var searchTimer=null;
  if(searchInput){{
    searchInput.addEventListener('input',function(){{
      clearTimeout(searchTimer);
      searchTimer=setTimeout(function(){{
        filters.search=searchInput.value.trim();
        page=1;
        updateFilterBadge();
        saveFilters();
        loadData().then(renderFromData);
      }},220);
    }});
  }}

  // ── Channel multi-select dropdown ──
  (function(){{
    var btn=document.getElementById('ch-dropdown-btn');
    var panel=document.getElementById('ch-dropdown-panel');
    var searchInput=document.getElementById('ch-dropdown-search');
    var list=document.getElementById('ch-dropdown-list');
    if(!btn||!panel) return;

    function openPanel(){{
      panel.hidden=false;
      btn.setAttribute('aria-expanded','true');
      btn.querySelector('.ch-dropdown-arrow').textContent='▴';
      if(searchInput){{ searchInput.value=''; filterList(''); searchInput.focus(); }}
    }}
    function closePanel(){{
      panel.hidden=true;
      btn.setAttribute('aria-expanded','false');
      btn.querySelector('.ch-dropdown-arrow').textContent='▾';
    }}
    btn.addEventListener('click',function(e){{
      e.stopPropagation();
      if(panel.hidden) openPanel(); else closePanel();
    }});
    document.addEventListener('click',function(e){{
      if(!panel.hidden && !panel.contains(e.target) && e.target!==btn){{
        closePanel();
      }}
    }});
    document.addEventListener('keydown',function(e){{
      if(e.key==='Escape'&&!panel.hidden) closePanel();
    }});

    function filterList(q){{
      var items=list.querySelectorAll('.ch-dropdown-item:not(.ch-dropdown-all)');
      var lq=q.toLowerCase();
      items.forEach(function(li){{
        var name=li.querySelector('label').textContent.toLowerCase();
        li.hidden=lq&&name.indexOf(lq)===-1;
      }});
    }}
    if(searchInput){{
      searchInput.addEventListener('input',function(){{ filterList(searchInput.value.trim()); }});
      searchInput.addEventListener('click',function(e){{ e.stopPropagation(); }});
    }}

    // "Összes" button
    var allItem=document.getElementById('ch-all-item');
    if(allItem){{
      allItem.addEventListener('click',function(){{
        filters.channel=[];
        list.querySelectorAll('.ch-dropdown-item:not(.ch-dropdown-all) input[type=checkbox]').forEach(function(cb){{cb.checked=false;}});
        allItem.classList.add('active');
        page=1; updateFilterBadge(); updateChannelBtnLabel(); saveFilters();
        loadData().then(renderFromData);
      }});
    }}

    // Individual channel checkboxes
    list.querySelectorAll('.ch-dropdown-item:not(.ch-dropdown-all)').forEach(function(li){{
      var cb=li.querySelector('input[type=checkbox]');
      if(!cb) return;
      cb.addEventListener('change',function(){{
        var slug=li.dataset.slug;
        var idx=filters.channel.indexOf(slug);
        if(cb.checked){{
          if(idx===-1) filters.channel.push(slug);
          if(allItem) allItem.classList.remove('active');
        }} else {{
          if(idx!==-1) filters.channel.splice(idx,1);
          if(filters.channel.length===0 && allItem) allItem.classList.add('active');
        }}
        page=1; updateFilterBadge(); updateChannelBtnLabel(); saveFilters();
        loadData().then(renderFromData);
      }});
    }});
  }})();

  // ── Tag multi-select dropdown ──
  function syncTagCheckboxes(){{
    var allItem=document.getElementById('tag-all-item');
    var items=document.querySelectorAll('#tag-dropdown-list .ch-dropdown-item:not(.ch-dropdown-all)');
    var sel=filters.tag;
    if(!sel||sel.length===0){{
      if(allItem) allItem.classList.add('active');
      items.forEach(function(li){{var cb=li.querySelector('input[type=checkbox]');if(cb) cb.checked=false;}});
    }} else {{
      if(allItem) allItem.classList.remove('active');
      items.forEach(function(li){{var cb=li.querySelector('input[type=checkbox]');if(cb) cb.checked=sel.indexOf(li.dataset.slug)!==-1;}});
    }}
  }}
  function updateTagBtnLabel(){{
    var lbl=document.getElementById('tag-dropdown-label');
    if(!lbl) return;
    var sel=filters.tag;
    if(!sel||sel.length===0){{ lbl.textContent='Összes címke'; }}
    else if(sel.length===1){{ lbl.textContent=sel[0]; }}
    else {{ lbl.textContent=sel.length+' címke kiválasztva'; }}
  }}
  (function(){{
    var btn=document.getElementById('tag-dropdown-btn');
    var panel=document.getElementById('tag-dropdown-panel');
    var searchInput=document.getElementById('tag-dropdown-search');
    var list=document.getElementById('tag-dropdown-list');
    if(!btn||!panel) return;
    function openPanel(){{
      panel.hidden=false;btn.setAttribute('aria-expanded','true');
      btn.querySelector('.ch-dropdown-arrow').textContent='▴';
      if(searchInput){{ searchInput.value=''; filterList(''); searchInput.focus(); }}
    }}
    function closePanel(){{
      panel.hidden=true;btn.setAttribute('aria-expanded','false');
      btn.querySelector('.ch-dropdown-arrow').textContent='▾';
    }}
    btn.addEventListener('click',function(e){{ e.stopPropagation(); if(panel.hidden) openPanel(); else closePanel(); }});
    document.addEventListener('click',function(e){{ if(!panel.hidden && !panel.contains(e.target) && e.target!==btn) closePanel(); }});
    document.addEventListener('keydown',function(e){{ if(e.key==='Escape'&&!panel.hidden) closePanel(); }});
    function filterList(q){{
      var items=list.querySelectorAll('.ch-dropdown-item:not(.ch-dropdown-all)');
      var lq=q.toLowerCase();
      items.forEach(function(li){{ var name=li.querySelector('label').textContent.toLowerCase(); li.hidden=lq&&name.indexOf(lq)===-1; }});
    }}
    if(searchInput){{
      searchInput.addEventListener('input',function(){{ filterList(searchInput.value.trim()); }});
      searchInput.addEventListener('click',function(e){{ e.stopPropagation(); }});
    }}
    var allItem=document.getElementById('tag-all-item');
    if(allItem){{
      allItem.addEventListener('click',function(){{
        filters.tag=[];
        list.querySelectorAll('.ch-dropdown-item:not(.ch-dropdown-all) input[type=checkbox]').forEach(function(cb){{cb.checked=false;}});
        allItem.classList.add('active');
        page=1; updateFilterBadge(); updateTagBtnLabel(); saveFilters();
        loadData().then(function(){{ renderFromData(); updateChannelListAvailability(); }});
      }});
    }}
    list.querySelectorAll('.ch-dropdown-item:not(.ch-dropdown-all)').forEach(function(li){{
      var cb=li.querySelector('input[type=checkbox]');
      if(!cb) return;
      cb.addEventListener('change',function(){{
        var slug=li.dataset.slug;
        var idx=filters.tag.indexOf(slug);
        if(cb.checked){{ if(idx===-1) filters.tag.push(slug); if(allItem) allItem.classList.remove('active'); }}
        else {{ if(idx!==-1) filters.tag.splice(idx,1); if(filters.tag.length===0 && allItem) allItem.classList.add('active'); }}
        page=1; updateFilterBadge(); updateTagBtnLabel(); saveFilters();
        loadData().then(function(){{ renderFromData(); updateChannelListAvailability(); }});
      }});
    }});
  }})();

  // ── Tag click on cards → activate tag filter ──
  feed.addEventListener('click',function(ev){{
    var tag=ev.target.closest('[data-tag]');
    if(!tag) return;
    ev.preventDefault();
    ev.stopPropagation();
    var val=tag.dataset.tag;
    if(!val) return;
    // Open filter panel if closed
    var fg=document.getElementById('filter-groups');
    var btn=document.getElementById('filter-toggle');
    if(fg && fg.hidden){{
      fg.hidden=false;
      if(btn){{btn.setAttribute('aria-expanded','true');btn.querySelector('.filter-toggle-icon').textContent='▴';}}
    }}
    // Toggle this tag in the filter
    var idx=filters.tag.indexOf(val);
    if(idx===-1) filters.tag.push(val); else filters.tag.splice(idx,1);
    // Update dropdown UI
    syncTagCheckboxes();
    updateTagBtnLabel();
    page=1;
    updateFilterBadge();
    saveFilters();
    loadData().then(function(){{ renderFromData(); updateChannelListAvailability(); }});
  }});

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
      updateFilterBadge();
      saveFilters();
      loadData().then(function(){{ renderFromData(); updateChannelListAvailability(); }});
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
