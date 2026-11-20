// visual-check: screenshot + console errors + failed requests + horizontal overflow + axe a11y.
// Usage: node check.mjs <file.html|url> [out-dir] [label]
// Writes: <out>/<label>-<width>.png (light), <label>-1280-dark.png, <out>/report.json
import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs';
import path from 'node:path';

const target = process.argv[2];
const outDir = process.argv[3] || 'shots';
const label = process.argv[4] || 'page';
if (!target) { console.error('Usage: node check.mjs <file.html|url> [out-dir] [label]'); process.exit(1); }

const url = target.startsWith('http') || target.startsWith('file://')
  ? target
  : 'file://' + path.resolve(target);

fs.mkdirSync(outDir, { recursive: true });
const report = { url, label, widths: {}, errors: [], failedRequests: [], overflow: {}, dark: null, a11y: null };

const exe = process.env.CHROME_PATH || new URL('./chrome-headless-shell-linux64/chrome-headless-shell', import.meta.url).pathname;
const launchArgs = ['--no-sandbox'];
const launchOpts = { executablePath: exe, args: launchArgs };
const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy;
if (proxyUrl) {
  try {
    const u = new URL(proxyUrl);
    launchOpts.proxy = { server: u.protocol + '//' + u.host, username: decodeURIComponent(u.username), password: decodeURIComponent(u.password) };
  } catch { /* no proxy */ }
}
const browser = await chromium.launch(launchOpts);
const widths = [360, 768, 1280];

for (const w of widths) {
  const context = await browser.newContext({ viewport: { width: w, height: 900 } });
  const page = await context.newPage();
  const errors = [], failed = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push(String(e)));
  page.on('requestfailed', r => failed.push(r.url() + ' :: ' + (r.failure()?.errorText || '')));
  page.on('response', r => { if (r.status() >= 400) failed.push(r.url() + ' :: HTTP ' + r.status()); });
  await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 }).catch(e => errors.push('NAV: ' + e.message));
  await page.waitForTimeout(1200); // let counters/animations settle
  const overflow = await page.evaluate(() => {
    const de = document.documentElement;
    const wide = [];
    document.querySelectorAll('body *').forEach(el => {
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      if (cs.position === 'fixed' && (el.id === 'toast' || el.classList.contains('overlay'))) return; // hidden overlays
      if (r.width > de.clientWidth + 1) wide.push(el.tagName + '.' + (el.className?.toString().split(' ')[0] || '') + ' w=' + Math.round(r.width));
      else if (r.right > de.clientWidth + 1 || r.left < -1) wide.push(el.tagName + '.' + (el.className?.toString().split(' ')[0] || '') + ' left=' + Math.round(r.left) + ' right=' + Math.round(r.right));
    });
    return { docScrollW: de.scrollWidth, clientW: de.clientWidth, hOverflow: de.scrollWidth > de.clientWidth + 1, wideEls: wide.slice(0, 10) };
  });
  const shot = path.join(outDir, `${label}-${w}.png`);
  await page.screenshot({ path: shot, fullPage: false });
  report.widths[w] = { shot, errors, failedRequests: failed };
  report.errors.push(...errors.map(e => `[${w}] ${e}`));
  report.failedRequests.push(...failed.map(f => `[${w}] ${f}`));
  report.overflow[w] = overflow;
  if (w === 1280) {
    try {
      const axe = await new AxeBuilder({ page }).analyze();
      report.a11y = {
        violations: axe.violations.length,
        top: axe.violations.slice(0, 10).map(v => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help })),
      };
    } catch (e) { report.a11y = { error: String(e) }; }
  }
  await page.close();
  await context.close();
}

// dark mode at desktop width
const darkCtx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const dark = await darkCtx.newPage();
await dark.goto(url, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
await dark.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
await dark.waitForTimeout(600);
const darkShot = path.join(outDir, `${label}-1280-dark.png`);
await dark.screenshot({ path: darkShot });
try {
  const axeDark = await new AxeBuilder({ page: dark }).analyze();
  report.a11y.dark = {
    violations: axeDark.violations.length,
    top: axeDark.violations.slice(0, 10).map(v => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help })),
  };
} catch (e) { report.a11y.dark = { error: String(e) }; }
report.dark = { shot: darkShot };
await dark.close();
await darkCtx.close();

await browser.close();
fs.writeFileSync(path.join(outDir, `${label}-report.json`), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ label, errors: report.errors.length, failed: report.failedRequests.length, overflow: Object.fromEntries(Object.entries(report.overflow).map(([k, v]) => [k, v.hOverflow])), a11yViolations: report.a11y?.violations ?? null }, null, 2));
