# Kaogong Wiki

The user-facing manual and tutorial site. It is a **static site** generated from
Markdown, served by FastAPI at `/wiki/`.

## Build

```bash
.venv/bin/python wiki/build.py
.venv/bin/python wiki/build.py --base /kaogong-wiki   # GitHub Pages
```

- `--base` prefixes every internal link, for project sites served under `/<repo>/`.
- `--out` writes the site somewhere other than `wiki/site/`.

Outputs to `wiki/site/`:

```text
wiki/site/
  index.html
  <slug>/index.html
  search-index.json
  assets/wiki.css
  assets/wiki.js
  assets/pygments.css
  assets/img/*.png
```

## Add a page

1. Add Markdown under `wiki/content/<slug>.md`.
2. Add the page to `wiki/nav.json` (section, nav label, title, description).
3. Add screenshots to `wiki/assets/img/` (or reference existing ones).
4. Rebuild: `.venv/bin/python wiki/build.py`.
5. Commit the generated `wiki/site/` so the running app serves it without a build step.

## Deploy to GitHub Pages (public wiki, $0)

The application repository stays private. Publish only this folder to a
separate **public** repository, and let GitHub Pages build it:

1. Create an empty **public** repository, e.g. `kaogong-wiki` (no README).
2. Publish the wiki sources once:
   ```bash
   scripts/publish-wiki.sh git@github.com:<owner>/kaogong-wiki.git
   ```
3. In that repository: **Settings → Pages → Source: GitHub Actions**.
4. After the workflow finishes: `https://<owner>.github.io/kaogong-wiki/`.

The workflow (`.github/workflows/pages.yml`) builds with `--base "/<repo>"`
by default; override it with the repository variable `WIKI_BASE`:

- `WIKI_BASE` — mount prefix; set `""` when using a custom domain at the root.
  The site has no "open app" links, so nothing else needs configuring.

Custom domain: set it in **Settings → Pages → Custom domain**, add a `CNAME`
file (the domain name) at the repository root, and set `WIKI_BASE=""`.

## Content rules

- Every tutorial teaches **chemistry + software operations**.
- Examples are data (`packages/matforge/data/examples.json`); never add a tutorial-specific Python branch.
- Use callouts: `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`, `> [!IMPORTANT]`, `> [!CHEMISTRY]`.
- Compress screenshots before committing when possible; keep the wiki under a few MB.
