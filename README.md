# Röviden

Hosszú beszélgetések, podcastek és interjúk **AI-generált** összefoglalói dióhéjban.

A projekt magyar nyelvű YouTube-csatornákat (közéleti, politikai, gazdasági témák) figyel,
letölti a 30 percnél hosszabb videók átiratát, majd LLM segítségével rövid `tl;dr`-t és
részletesebb összefoglalót készít belőlük. A kimenet egy statikus weboldal: szűrhető lista,
csatornánként/irányultság/kötődés szerint.

> ⚠️ Az összefoglalók **nem helyettesítik** az eredeti tartalmat. A kontextus, az árnyalatok
> és az alkotói munka csak a videó megtekintésével élhető át igazán. Kérünk, támogasd
> az érintett médiumokat: nézd meg az eredeti videót, iratkozz fel, oszd meg.

## Mit csinál pontosan?

- Figyeli a `channels.yaml`-ban felsorolt YouTube-csatornákat (független, Fidesz-közeli,
  Tisza-közeli; liberális, centrista, konzervatív, szélsőjobb tagolásban).
- A 30 percnél hosszabb videókhoz átiratot szerez (YouTube felirat).
- LLM-mel rövid `tl;dr`-t és részletes összefoglalót generál, megjelölve a bizonytalan
  szakaszokat is.
- A `content/` mappába `.md` fájlokat ír YAML frontmatterrel.
- A `scripts/build.py` ezekből statikus HTML oldalt épít a `_site/` könyvtárba.

## Repo szerkezete

```
channels.yaml          – figyelt csatornák listája és metaadatai
content/<csatorna>/…   – generált markdown fájlok (egy fájl = egy videó)
scripts/build.py       – statikus oldal generátor
scripts/style.css      – stíluslap
scripts/manage_channels.py – csatornakezelő segédszkript
```

## Build

```bash
python scripts/build.py              # _site/ mappába
python scripts/build.py --out <dir>  # tetszőleges kimeneti mappa
```

Függőségek: `markdown`, `pyyaml`. (`pip install markdown pyyaml`)

## Hibajelentés és javítás

Minden cikk tetején (a `tl;dr` alatt) található egy figyelmeztetés, hogy a tartalom
AI-generált. Ha hibát találsz, két lehetőséged van:

1. **Javítás közvetlenül a fájlban** (előnyben részesített). A cikk lapján kattints a
   „javítsd közvetlenül a forrásfájlt” linkre — ez a GitHub-on lévő `.md` fájlhoz visz.
   Ott a ceruza/szerkesztés ikonra kattintva küldhetsz módosítási javaslatot
   (pull request).
   Példa: <https://github.com/critic4lcode/roviden/blob/main/content/444/2026/04/2026-04-07-democracy-noir-igy-epitette-le-orban-a-demokraciat.md>
2. **Hibajegy nyitása**: <https://github.com/critic4lcode/roviden/issues>

## Kapcsolat

Médium képviselőként vagy egyéb észrevétellel: `info@pjegyezve.com`.

## Licenc

Az összefoglalók forrása a megjelölt YouTube-csatornák tartalma; minden ott szereplő
jog az eredeti alkotóké. Az itt található AI-generált szövegek tájékoztató jellegűek.
