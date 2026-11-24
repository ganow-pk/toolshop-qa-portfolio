"""Build the test dashboard: one self-contained HTML page.

What it shows: the latest run per source, a stacked bar chart of passed /
failed / broken / skipped per run (one chart for CI API runs, one for local
full runs), links to the reports, and a table of every recorded run.

The run history is written into the page itself (a JSON block), so the page
works when opened straight from disk (file://). Chart.js comes from cdnjs; if
it can't load, the table below the chart still shows every run.

Usage (from the project folder):
    python scripts/build_dashboard.py --local-history history/local-runs.json \\
        --out report/dashboard.html --link "HTML report=index.html"
    python scripts/build_dashboard.py --ci-history public/history/ci.json \\
        --local-history public/history/local.json --out public/index.html \\
        --link "Daily CI run (API): HTML report=ci-api/" \\
        --site-url https://ganow-pk.github.io/toolshop-qa-portfolio
Each --link is "Label=href" and appears in the order given.
--site-url (the live site's address) adds the social preview tags (og:image
and friends), so a link pasted into LinkedIn, Slack or email shows a picture
card. The image itself, social-preview.png, must sit next to the page.
Without it (the local dashboard) the page has no preview tags.
"""
import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CHART_JS = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"
CHART_JS_SRI = "sha512-CQBWl4fJHWbryGE+Pc7UAxWMUMNMWzWxF4SQo9CgkJIN1kx6djDQZjh3Y8SZ1d+6I+1zze6Z7kHXO7q3UyZAWw=="
REPO_URL = "https://github.com/ganow-pk/toolshop-qa-portfolio"
BUGS_URL = REPO_URL + "/blob/main/docs/BUGS.md"
SOURCES = (("ci", "Daily CI run: API tests"), ("local", "Local full runs: UI + API"))
COUNTS = ("passed", "failed", "broken", "skipped", "retried")
SOCIAL_TITLE = "Toolshop QA Portfolio - Playwright + Python Test Suite"
SOCIAL_DESCRIPTION = ("Playwright, Python and pytest with Page Object Model; ISTQB-tagged tests, "
                      "exploratory sessions, bug reports, and CI on GitHub Actions.")
SOCIAL_IMAGE = "social-preview.png"   # 1200 x 627, copied next to the page by CI
SOCIAL_IMAGE_ALT = "Toolshop QA Portfolio: Playwright + Python test suite and test dashboard"


def build(ci_history, local_history, links: list, site_url=None) -> str:
    """A history of None leaves that source off the page (the local copy has no CI runs).
    site_url (the live site's address) adds the social preview tags; None leaves them out."""
    histories = {source: _clean(history) for source, history in
                 (("ci", ci_history), ("local", local_history)) if history is not None}
    all_links = list(links) + [("Bug list", BUGS_URL), ("Source code and docs", REPO_URL)]
    return PAGE.format(
        social=_social_html(site_url),
        latest=_latest_html(histories),
        charts=_charts_html(histories),
        links="\n".join(f'    <a class="card" href="{_href(href)}">{_e(label)} &rarr;</a>'
                        for label, href in all_links),
        table=_table_html(histories),
        data=_json_for_script(histories),
        chart_js=CHART_JS,
        chart_js_sri=CHART_JS_SRI,
        built=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        repo=REPO_URL,
    )


# ---------- Pieces of the page ----------

def _social_html(site_url) -> str:
    """Preview card tags for LinkedIn, Slack, email. og:image must be an absolute URL."""
    if not site_url:
        return ""
    base = site_url.rstrip("/")
    tags = [("name", "description", SOCIAL_DESCRIPTION),
            ("property", "og:type", "website"),
            ("property", "og:url", base + "/"),
            ("property", "og:title", SOCIAL_TITLE),
            ("property", "og:description", SOCIAL_DESCRIPTION),
            ("property", "og:image", f"{base}/{SOCIAL_IMAGE}"),
            ("property", "og:image:width", "1200"),
            ("property", "og:image:height", "627"),
            ("property", "og:image:alt", SOCIAL_IMAGE_ALT),
            ("name", "twitter:card", "summary_large_image")]
    return "".join(f'\n<meta {attr}="{_e(key)}" content="{_e(value)}">' for attr, key, value in tags)


def _latest_html(histories: dict) -> str:
    lines = []
    for source, title in _shown(histories):
        runs = histories[source]
        if runs:
            run = runs[-1]
            text = (f"{_when(run)} | env {_e(run['env'])} | branch {_e(run['branch'])} @ {_e(run['commit'])}: "
                    f"<strong>{run['passed']} passed, {run['failed']} failed</strong>, "
                    f"{run['broken']} broken, {run['skipped']} skipped")
            if run["retried"]:
                text += f" ({run['retried']} retried)"
        else:
            text = "No runs recorded yet."
        lines.append(f'  <p class="latest"><span>{_e(title)}</span>{text}</p>')
    return "\n".join(lines)


def _charts_html(histories: dict) -> str:
    if not any(histories.values()):
        return ('  <div class="empty">No runs recorded yet. Run the full suite with '
                '<code>pytest</code>, and the first run shows up here.</div>')
    blocks = []
    for source, title in _shown(histories):
        body = (f'<canvas id="chart-{source}"></canvas>' if histories[source]
                else '<p class="muted">No runs recorded yet.</p>')
        blocks.append(f'  <section class="chart"><h2>{_e(title)}</h2>{body}</section>')
    return "\n".join(blocks)


def _table_html(histories: dict) -> str:
    rows = sorted((run for runs in histories.values() for run in runs),
                  key=lambda run: run["timestamp"], reverse=True)
    if not rows:
        return '  <p class="muted">No runs recorded yet.</p>'
    header = "".join(f"<th>{name}</th>" for name in
                     ("Date", "Source", "Env", "Branch", "Passed", "Failed", "Broken",
                      "Skipped", "Retried", "Duration", "Run"))
    body = []
    for run in rows:
        link = (f'<a href="{_href(run["run_url"])}">CI run</a>'
                if run.get("run_url") else "-")
        cells = [_when(run), _e(run["source"]), _e(run["env"]),
                 f'{_e(run["branch"])} <span class="muted">{_e(run["commit"])}</span>',
                 *(f'<span class="n-{name}">{run[name]}</span>' for name in COUNTS),
                 _duration(run["duration_s"]), link]
        body.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")
    return (f'  <div class="table-wrap"><table><thead><tr>{header}</tr></thead>\n'
            f'  <tbody>\n  ' + "\n  ".join(body) + "\n  </tbody></table></div>")


# ---------- Helpers ----------

def _shown(histories: dict) -> list:
    return [(source, title) for source, title in SOURCES if source in histories]


def _clean(history) -> list:
    """Keep only well-formed entries, oldest first, with every field present."""
    runs = []
    for run in history if isinstance(history, list) else []:
        if not isinstance(run, dict) or not isinstance(run.get("timestamp"), str):
            continue
        clean = {key: str(run.get(key, "") or "-") for key in
                 ("timestamp", "source", "env", "branch", "commit")}
        for name in COUNTS + ("total",):
            clean[name] = _int(run.get(name))
        clean["duration_s"] = _number(run.get("duration_s"))
        url = run.get("run_url")
        if isinstance(url, str) and url.startswith("https://"):
            clean["run_url"] = url
        runs.append(clean)
    return sorted(runs, key=lambda run: run["timestamp"])


def _int(value) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0


def _number(value) -> float:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0.0


def _e(text) -> str:
    return html.escape(str(text), quote=True)


def _href(url: str) -> str:
    """Only web links and relative paths become links; anything else is neutralised."""
    lowered = url.strip().lower()
    if ":" in lowered.split("/")[0] and not lowered.startswith(("https:", "http:")):
        return "#"
    return _e(url)


def _when(run: dict) -> str:
    """UTC text that the page's script turns into the viewer's local time."""
    stamp = run["timestamp"]
    try:
        moment = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
        text = moment.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        text = stamp
    return f'<time datetime="{_e(stamp)}">{_e(text)}</time>'


def _duration(seconds: float) -> str:
    minutes, secs = divmod(int(round(seconds)), 60)
    return f"{minutes}m {secs:02d}s" if minutes else f"{secs}s"


def _json_for_script(data) -> str:
    """JSON that can sit inside <script> safely: no "<", ">", or "&" survive as-is."""
    text = json.dumps(data, separators=(",", ":"))
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


# ---------- Page template ----------
# Same look as the earlier landing page (colours, fonts, cards).
# Literal braces in CSS and JS are doubled because this is a str.format template.

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Toolshop QA Portfolio - Test Dashboard</title>{social}
<style>
  :root {{ --ink:#1d2330; --muted:#5b6474; --line:#e3e6ec; --ok:#1f7a4d; --accent:#1d5fa8;
          --fail:#c0392b; --broken:#d68910; --skip:#9aa3b2; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; color:var(--ink); background:#f7f8fa; line-height:1.5; }}
  main {{ max-width:1000px; margin:0 auto; padding:48px 20px; }}
  h1 {{ font-size:1.7rem; margin:0 0 6px; }}
  h2 {{ font-size:1.15rem; margin:0 0 10px; color:var(--accent); }}
  .sub {{ color:var(--muted); margin:0 0 24px; }}
  .latest {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:12px 18px; margin:0 0 10px; }}
  .latest span {{ display:block; font-size:.85rem; color:var(--muted); }}
  .chart {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:18px 22px; margin:16px 0; }}
  .empty {{ background:#fff; border:1px dashed var(--line); border-radius:10px; padding:28px; margin:16px 0; text-align:center; color:var(--muted); }}
  .links {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:12px; margin:16px 0 24px; }}
  .card {{ display:block; background:#fff; border:1px solid var(--line); border-radius:10px; padding:14px 18px; text-decoration:none; color:var(--accent); font-weight:600; }}
  .card:hover {{ border-color:var(--accent); }}
  .table-wrap {{ overflow-x:auto; background:#fff; border:1px solid var(--line); border-radius:10px; }}
  table {{ border-collapse:collapse; width:100%; font-size:.9rem; }}
  th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); white-space:nowrap; }}
  th {{ color:var(--muted); font-weight:600; }}
  .n-passed {{ color:var(--ok); }} .n-failed {{ color:var(--fail); font-weight:600; }}
  .n-broken {{ color:var(--broken); }} .n-skipped, .n-retried {{ color:var(--muted); }}
  .muted {{ color:var(--muted); }}
  .note {{ background:#fff; border-left:4px solid var(--accent); padding:14px 18px; border-radius:6px; color:var(--muted); font-size:.95rem; margin-top:24px; }}
  footer {{ margin-top:32px; font-size:.9rem; color:var(--muted); }}
  a {{ color:var(--accent); }}
</style>
</head>
<body>
<main>
  <h1>Toolshop QA Portfolio</h1>
  <p class="sub">Playwright + Python + pytest (Page Object Model) against the Practice Software Testing "Toolshop" demo store. Results of every recorded run, newest on the right.</p>

{latest}

{charts}

  <h2>Reports</h2>
  <div class="links">
{links}
  </div>

  <h2>All recorded runs</h2>
{table}

  <div class="note">
    <strong>Why the UI tests don't run in CI:</strong> the practice site protects its web pages with a Cloudflare
    "verify you are human" check that blocks cloud-hosted browsers such as GitHub's runners. The API tests
    aren't affected, so they run live in CI. The full suite runs from a local machine, and its report is published here with its date.
    Getting past a bot check would defeat its purpose, so the suite doesn't try.
  </div>

  <footer>Page built {built}. Source and docs: <a href="{repo}">github.com/ganow-pk/toolshop-qa-portfolio</a></footer>
</main>

<script type="application/json" id="run-history">{data}</script>
<script src="{chart_js}" integrity="{chart_js_sri}" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script>
(function () {{
  // Show dates in the viewer's own time zone (the table falls back to UTC).
  document.querySelectorAll("time[datetime]").forEach(function (el) {{
    var d = new Date(el.getAttribute("datetime"));
    if (!isNaN(d)) el.textContent = d.toLocaleString([], {{dateStyle: "medium", timeStyle: "short"}});
  }});
  if (typeof Chart === "undefined") return;   // no chart library: the table still has everything
  var data = JSON.parse(document.getElementById("run-history").textContent);
  var css = getComputedStyle(document.documentElement);
  var series = [["passed", "--ok"], ["failed", "--fail"], ["broken", "--broken"], ["skipped", "--skip"]];
  Object.keys(data).forEach(function (source) {{
    var canvas = document.getElementById("chart-" + source);
    var runs = data[source];
    if (!canvas || !runs.length) return;
    new Chart(canvas, {{
      type: "bar",
      data: {{
        labels: runs.map(function (r) {{
          var d = new Date(r.timestamp);
          var label = isNaN(d) ? r.timestamp : d.toLocaleString([], {{month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"}});
          return r.env === "main" ? label : label + " (" + r.env + ")";
        }}),
        datasets: series.map(function (s) {{
          return {{ label: s[0], data: runs.map(function (r) {{ return r[s[0]]; }}),
                   backgroundColor: css.getPropertyValue(s[1]).trim(), stack: "run" }};
        }})
      }},
      options: {{
        responsive: true,
        aspectRatio: 3.2,
        animation: false,
        scales: {{ x: {{ stacked: true }}, y: {{ stacked: true, beginAtZero: true, ticks: {{ precision: 0 }} }} }},
        plugins: {{ tooltip: {{ callbacks: {{ footer: function (items) {{
          var r = runs[items[0].dataIndex];
          return r.branch + " @ " + r.commit + (r.retried ? " | " + r.retried + " retried" : "");
        }} }} }} }}
      }}
    }});
  }});
}})();
</script>
</body>
</html>
"""


# ---------- Command line ----------

def _read_history(path):
    """No path = source not shown. Missing file = no runs. Invalid JSON stops the build."""
    if not path:
        return None
    file = Path(path)
    return json.loads(file.read_text(encoding="utf-8")) if file.exists() else []


def _parse_link(text: str):
    label, sep, href = text.partition("=")
    if not sep or not label.strip() or not href.strip():
        raise argparse.ArgumentTypeError(f'--link must look like "Label=href", got {text!r}')
    return label.strip(), href.strip()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build the test dashboard page.")
    parser.add_argument("--ci-history", help="JSON list of CI runs")
    parser.add_argument("--local-history", help="JSON list of local runs")
    parser.add_argument("--link", action="append", default=[], type=_parse_link,
                        help='"Label=href", repeatable')
    parser.add_argument("--out", required=True, help="where to write the HTML page")
    parser.add_argument("--site-url", help="the live site's address, for the social preview tags")
    args = parser.parse_args(argv)
    try:
        page = build(_read_history(args.ci_history), _read_history(args.local_history), args.link,
                     site_url=args.site_url)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"Dashboard written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
