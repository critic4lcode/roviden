# roviden — repo map

Hungarian political media aggregator. Static site generator.

## Structure

```
roviden/
├── scripts/
│   ├── build.py          # main build: reads content/, outputs _site/
│   ├── templates.py      # HTML templates (inline CSS/JS, Discord invite modal)
│   ├── app.js            # frontend JS (TTS, player, Discord popup logic)
│   ├── style.css         # main stylesheet
│   ├── manage_channels.py# Textual TUI for editing channels.yaml
│   └── pyproject.toml    # deps: markdown, pyyaml, textual
├── channels.yaml         # channel registry (slug, display name, etc.)
├── content/
│   └── <channel-slug>/
│       └── <year>/<month>/<date-slug>.md  # frontmatter + transcript
├── benchmark/            # LLM benchmark result markdowns
├── _site/                # build output (gitignored)
└── .github/workflows/deploy.yml  # GH Pages deploy: uv install → build.py → upload
```

## Content channels (~55)

24-hu, 444, atlatszo, atv, azigazidopemantv, bayer-show, bohar-daniel, bunvadaszok,
direkt36, fekete-rita, fokuszcsoport, friderikusz-podcast, hir-fm, hir-tv, hit-radio,
hvg, index, inforadio, jelen, jolvanezigy, klasszis-media, klikktv, klubradio,
kokusz-plusz, kontextus, kontroll, kozter, lmp, magyar-hang, magyar-nemzet,
magyar-peter, mandiner, merce, mi-hazank, momentum, nepszava, origo, otpontban,
partizan, patriota, pogatsa-zoltan, politikai-hobbista, puzser-robert, ridikul,
sajtoklub-hirtv, szelsokozep, szinen-tul, telex-hu, the-fair-right, tisza-europa,
toroczkai, ultrahang, ultrahang-plusz, valasz-online, valsagtab, virag-gulyas

## Key facts

- Build: `python scripts/build.py` → writes to `_site/`
- Channel management: `python scripts/manage_channels.py` (Textual TUI)
- Deploy: push to main → GH Actions → GH Pages
