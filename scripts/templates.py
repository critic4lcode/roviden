# HTML/JS/CSS template strings for the static site generator.
# Kept separate so build.py stays focused on logic.

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

# Inline init — used inside JS ytmCloseWelcome handler (no outer <script> tag needed).
_POSTHOG_INIT_JS = """\
      !function(t,e){var o,n,p,r;e.__SV||(window.posthog&&window.posthog.__loaded)||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="Ei Ni init zi Gi Nr Ui Xi Vi capture calculateEventProperties tn register register_once register_for_session unregister unregister_for_session an getFeatureFlag getFeatureFlagPayload getFeatureFlagResult isFeatureEnabled reloadFeatureFlags updateFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSurveysLoaded onSessionId getSurveys getActiveMatchingSurveys renderSurvey displaySurvey cancelPendingSurvey canRenderSurvey canRenderSurveyAsync ln identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset setIdentity clearIdentity get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException addExceptionStep captureLog startExceptionAutocapture stopExceptionAutocapture loadToolbar get_property getSessionProperty nn Qi createPersonProfile setInternalOrTestUser sn qi cn opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing get_explicit_consent_status is_capturing clear_opt_in_out_capturing Ji debug Fr rn getPageViewId captureTraceFeedback captureTraceMetric Bi".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
      posthog.init('phc_qjVik3YsYrLt6ZUjQbJZhneSwztCdFUmaZxfihqpjXVi',{api_host:'https://eu.i.posthog.com',defaults:'2026-01-30',person_profiles:'identified_only'});"""

_TTS_BAR_HTML = """\
<div id="tts-bar" class="tts-bar" hidden>
  <div class="tts-bar-inner">
    <div class="tts-bar-row-controls">
      <span class="tts-section-label" id="tts-section-name"></span>
      <div class="tts-bar-center">
        <button class="tts-ctrl-btn" id="tts-skip-back" disabled title="-5 szó"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="11 17 6 12 11 7"/><polyline points="18 17 13 12 18 7"/></svg>5</button>
        <button class="tts-ctrl-btn tts-play-btn" id="tts-playpause" disabled title="Lejátszás/Szünet"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg></button>
        <button class="tts-ctrl-btn" id="tts-skip-fwd" disabled title="+5 szó">5<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="13 17 18 12 13 7"/><polyline points="6 17 11 12 6 7"/></svg></button>
      </div>
      <div class="tts-bar-right">
        <select id="tts-voice" class="tts-voice-sel"><option>...</option></select>
        <div class="tts-rate-wrap">
          <input type="range" id="tts-rate" min="0.5" max="2" step="0.1" value="1">
          <span class="tts-rate-val" id="tts-rate-val">1.0×</span>
        </div>
        <div class="tts-close-wrap"><button class="tts-close-btn" id="tts-close" title="Bezárás">&#x2715;</button></div>
      </div>
    </div>
    <div class="tts-progress-wrap">
      <span class="tts-time" id="tts-time-cur">0:00</span>
      <input type="range" class="tts-seek" id="tts-seek" min="0" max="100" value="0" step="1">
      <span class="tts-time" id="tts-time-total">0:00</span>
    </div>
  </div>
</div>"""

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
<script src="{root}/scripts/app.js" defer></script>
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
__TTS_BAR__
</body>
</html>
"""

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
<script>!function(){{var t=localStorage.getItem('ytm_theme');if(t==='dark'||t==='light'){{document.documentElement.setAttribute('data-theme',t);}}else if(window.matchMedia('(prefers-color-scheme: dark)').matches){{document.documentElement.setAttribute('data-theme','dark');}}}}();</script>
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
      <li>Az összefoglalók <strong>AI által generált</strong> szövegek, és <strong>tartalmazhatnak hibákat</strong> – különösen nevek, személyek és helyszínek megnevezésénél, amelyek szövegfelismerési hibákból adódhatnak. Az összefoglalók pontossága <strong>nem garantált</strong>. Minden cikk tetején megjelenik egy hivatkozás: hibát közvetlenül a forrásfájlban javíthatsz (a ceruza ikon a GitHubon), vagy jelezd hibajegyben.</li>
      <li>A csatornák politikai <strong>kötődésének</strong> (független, Fidesz-közeli, Tisza-közeli, ellenzéki) és <strong>irányultságának</strong> (liberális, centrista, konzervatív, szélsőjobb) meghatározásakor törekedtünk az objektivitásra, de ezek a besorolások szükségszerűen szubjektív elemeket tartalmaznak, és finomhangolásra szorulnak. Vitát, észrevételeket és módosítási javaslatokat <a href="https://github.com/critic4lcode/roviden/discussions/1" target="_blank" rel="noopener noreferrer">ezen a GitHub-os vitafórumon</a> várunk.</li>
    </ul>
    <section class="collapsible cookie-policy">
      <details>
        <summary>Tartalomkészítőknek</summary>
        <div class="collapsible-inner">
          <p>Be kell vallanunk, hogy ezzel a projekttel kapcsolatban vannak fenntartásaink. Egyértelmű volt az igény a közönség részéről a többórás videók rövid összefoglalóira, viszont fennáll a veszélye annak, hogy a látogatók csak az AI-összefoglalókat olvassák el, és nem nézik meg magát a videót. Ez hosszú távon <strong>csökkentheti a csatornák nézettségét</strong>, ami egyrészt megnehezíti a médiumok számára, hogy felmérjék a közönségük valós igényeit, másrészt <strong>bevételkiesést</strong> is okozhat számukra.</p>
          <p>Minden olyan csatornánál, ahol fellelhető volt a csatornatámogatás valamilyen formája (közvetlen támogatás, Patreon, SZJA 1%, merch), az összefoglalók alatt megjelenítettük ezek elérhetőségét.</p>
          <p>Amennyiben Ön egy érintett médium képviselője, bármilyen észrevétele, kérése van az oldallal kapcsolatban – kérjük, vegye fel velünk a kapcsolatot az <a href="mailto:info@jegyezve.com">info@jegyezve.com</a> címen.</p>
          <p class="modal-outro">Köszönjük a megértést.</p>
        </div>
      </details>
    </section>
    <section class="collapsible cookie-policy">
      <details>
        <summary>Süti (cookie) tájékoztató</summary>
        <div class="collapsible-inner">
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
    </section>
    <p class="cookie-notice-text">A „Megértettem és elfogadom" gombra kattintva hozzájárulsz a fenti sütik használatához. A „Csak megnézem" gombbal süti nélkül is teljes mértékben használhatod az oldalt, ebben az esetben nem gyűjtünk semmilyen adatot.</p>
    <div class="modal-actions">
      <button class="modal-decline" type="button" onclick="ytmDeclineWelcome()">Csak megnézem, köszönöm</button>
      <button class="modal-btn" type="button" onclick="ytmCloseWelcome()">Megértettem és elfogadom</button>
    </div>
  </div>
</div>
<div id="discord-modal" class="modal-overlay" hidden>
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="discord-title" style="max-width:420px">
    <button class="modal-close" type="button" aria-label="Bezárás" onclick="ytmCloseDiscord()">&times;</button>
    <h2 id="discord-title">Elindult a Discord szerverünk!</h2>
    <p>Várjuk a visszajelzéseket, ötleteket és javaslatokat.</p>
    <div class="modal-actions">
      <button class="modal-decline" type="button" onclick="ytmCloseDiscord()">Bezárás</button>
      <button class="modal-btn" type="button" onclick="window.open('https://discord.gg/3cRZ7Wshy','_blank','noopener,noreferrer');ytmCloseDiscord()">Csatlakozás &rarr;</button>
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
      </button>
      <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Téma váltása" onclick="ytmToggleTheme()"></button>
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
      targetId:'ch-dropdown-btn',
      title:'Csatorna szűrő',
      body:'A <strong>Csatorna</strong> legördülőből egy vagy több konkrét csatornát is kiválaszthatsz. A lista a többi aktív szűrő alapján automatikusan rendezi magát.',
      position:'bottom',
      action: function(){{
        var fg=document.getElementById('filter-groups');
        var btn=document.getElementById('filter-toggle');
        if(fg && fg.hidden){{
          fg.hidden=false;
          if(btn) btn.setAttribute('aria-expanded','true');
        }}
      }}
    }},
    {{
      targetId:'search-input',
      title:'Szabad szöveges keresés',
      body:'Cím, csatorna neve vagy az összefoglaló tartalma alapján is kereshetsz. A szűrők és a keresés egyszerre is használhatók.',
      position:'bottom'
    }},
    {{
      targetId:'tag-dropdown-btn',
      title:'Címke szűrő',
      body:'A <strong>Címke</strong> legördülőből témák szerint szűrhetsz. Egyszerre több is kijelölhető.',
      position:'bottom'
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
      targetId:'theme-toggle',
      title:'Sötét mód',
      body:'Ezzel a gombbal válthatsz a világos és sötét megjelenés között.',
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
    if(typeof ytmShowDiscord==='function') setTimeout(ytmShowDiscord,600);
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
    if(typeof ytmShowDiscord==='function') setTimeout(ytmShowDiscord,600);
  }};
  try{{
    if(!localStorage.getItem('ytm_welcome_seen')){{
      window.ytmOpenWelcome();
    }}
  }}catch(e){{}}
}})();
(function(){{
  var DISCORD_KEY='ytm_discord_seen';
  window.ytmCloseDiscord=function(){{
    var m=document.getElementById('discord-modal');
    if(m) m.hidden=true;
    try{{localStorage.setItem(DISCORD_KEY,'1');}}catch(e){{}}
  }};
  window.ytmShowDiscord=function(){{
    try{{if(localStorage.getItem(DISCORD_KEY)) return;}}catch(e){{return;}}
    var m=document.getElementById('discord-modal');
    if(m) m.hidden=false;
  }};
  try{{
    if(localStorage.getItem('ytm_welcome_seen')){{
      setTimeout(ytmShowDiscord,1200);
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
    if(btn){{btn.setAttribute('aria-expanded','true');}}
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
      if(btn){{btn.setAttribute('aria-expanded','true');}}
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
(function(){{
  var STORAGE_KEY='ytm_theme';
  function applyTheme(t){{
    document.documentElement.setAttribute('data-theme',t);
    var btn=document.getElementById('theme-toggle');
    if(btn) btn.textContent=t==='dark'?'☀':'🌙';
  }}
  function getEffective(){{
    var stored=localStorage.getItem(STORAGE_KEY);
    if(stored==='dark'||stored==='light') return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
  }}
  applyTheme(getEffective());
  window.ytmToggleTheme=function(){{
    var current=document.documentElement.getAttribute('data-theme');
    var next=current==='dark'?'light':'dark';
    localStorage.setItem(STORAGE_KEY,next);
    applyTheme(next);
  }};
}})();
</script>
</body>
</html>
"""
