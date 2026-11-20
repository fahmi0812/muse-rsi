# visual-check

Screenshot any page or local HTML file at three widths plus dark mode, and report console errors, failed requests, and horizontal overflow. Use it whenever design work must be judged by looking at it, not by reading code. It closes the look-and-fix loop that `design-taste-frontend` requires: look at screenshots, score them, fix, look again.

## Run it

From `~/workspace/tools/visual-check/`:

```text
node check.mjs <file.html|url> [out-dir] [label]
```

Example:

```text
node check.mjs ~/workspace/your_files/Arus-v2-improved.html shots arus-v2
```

Output per run: `<label>-360.png`, `<label>-768.png`, `<label>-1280.png`, `<label>-1280-dark.png`, and `<label>-report.json` with console errors, failed requests (including HTTP 400+ and blocked external fonts), and horizontal overflow per width.

## Judge the screenshots

Open the PNGs and look at them yourself — do not trust the report alone:

- **Layout:** anything cut off, overlapping, or overflowing at 360 px? Sidebar hidden, bottom nav visible, tables stacked?
- **Hierarchy:** one clear focal point per screen, or everything shouting at once?
- **Colour:** palette restrained (2–3 core + 1 accent), or rainbow? Accent only where it matters?
- **Type:** sizes and weights consistent, nothing too small to read at 360 px?
- **Dark mode:** readable, no invisible text, no washed-out borders?
- **Real data:** numbers and names that add up, no lorem ipsum, no invented vanity numbers?

Score each point pass or fail. Fix the biggest fail first, then re-run and compare the new screenshots against the old ones.

## Rules

- Never claim a page "looks good" without opening its screenshots.
- A failed external request (font, image, script) is a finding, not noise — a "single file" that needs the network is not a single file.
- Keep the tooling free: Playwright + Chromium headless shell, no paid service.
- If the browser binary cannot download, try the headless shell first (`npx playwright install chromium-headless-shell`), then retry the full Chromium once before reporting the block.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills, for example `anti-slop-checklist` and `design-taste-frontend` for the design rules to judge against.
