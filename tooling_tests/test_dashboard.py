"""scripts/build_dashboard.py: the dashboard page.

The page carries data from history files (branch names, URLs), so it must
never let that data turn into HTML or script.
"""
import json
import subprocess
import sys

from paths import SCRIPTS
import build_dashboard  # noqa: E402  (found through paths.py)

SCRIPT_TAGS_IN_TEMPLATE = 3   # the page's own <script> blocks: data, Chart.js, chart code


def run_entry(**changes):
    entry = {"timestamp": "2026-11-20T10:00:00Z", "source": "ci", "env": "main",
             "branch": "main", "commit": "abc1234", "passed": 7, "failed": 0, "broken": 0,
             "skipped": 0, "retried": 0, "total": 7, "duration_s": 24.0}
    entry.update(changes)
    return entry


def data_block(page):
    """The JSON the page's chart code reads."""
    return page.split('<script type="application/json" id="run-history">')[1].split("</script>")[0]


# ---------- Escaping ----------

def test_script_tag_in_a_branch_name_cannot_break_out():
    evil = run_entry(branch='</script><script>alert(1)</script>&"', commit="<b>x</b>")

    page = build_dashboard.build([evil], None, [])

    assert page.count("</script>") == SCRIPT_TAGS_IN_TEMPLATE
    assert "<script>alert" not in page
    assert "<b>x</b>" not in page


def test_data_in_the_page_reads_back_exactly():
    evil_branch = '</script><script>alert(1)</script>&"'
    page = build_dashboard.build([run_entry(branch=evil_branch)], [run_entry(source="local")], [])

    data = json.loads(data_block(page))

    assert data["ci"][0]["branch"] == evil_branch
    assert data["local"][0]["source"] == "local"


def test_unsafe_links_are_neutralised():
    entry = run_entry(run_url="javascript:alert(1)")

    page = build_dashboard.build([entry], None, [("Bad", "javascript:alert(2)"), ("Ok", "ci-api/")])

    assert "javascript:" not in page
    assert 'href="#"' in page          # the bad report link
    assert 'href="ci-api/"' in page    # the good one stays


def test_https_run_link_is_kept():
    entry = run_entry(run_url="https://github.com/ganow-pk/toolshop-qa-portfolio/actions/runs/1")

    page = build_dashboard.build([entry], None, [])

    assert 'href="https://github.com/ganow-pk/toolshop-qa-portfolio/actions/runs/1"' in page


def test_malformed_entries_are_skipped():
    history = [run_entry(), "not an entry", {"no": "timestamp"}, run_entry(passed="seven")]

    data = json.loads(data_block(build_dashboard.build(history, None, [])))

    assert len(data["ci"]) == 2
    assert data["ci"][1]["passed"] == 0   # a count that isn't a number shows as 0


# ---------- What the page shows ----------

def test_empty_history_shows_the_empty_state():
    page = build_dashboard.build([], [], [])

    assert "No runs recorded yet" in page
    assert "<canvas" not in page


def test_source_not_passed_is_left_off_the_page():
    page = build_dashboard.build(None, [run_entry(source="local")], [])

    assert "Local full runs" in page
    assert "Daily CI run: API tests" not in page
    assert '"ci"' not in data_block(page)


def test_links_appear_in_the_order_given():
    page = build_dashboard.build([], None, [("First", "a/"), ("Second", "b/")])

    assert page.index("First") < page.index("Second")


# ---------- Social preview tags ----------

SITE = "https://ganow-pk.github.io/toolshop-qa-portfolio"


def test_site_url_adds_an_absolute_og_image():
    page = build_dashboard.build([], None, [], site_url=SITE)

    assert f'<meta property="og:image" content="{SITE}/social-preview.png">' in page
    assert f'<meta property="og:url" content="{SITE}/">' in page
    assert '<meta name="twitter:card" content="summary_large_image">' in page


def test_trailing_slash_on_site_url_gives_no_double_slash():
    page = build_dashboard.build([], None, [], site_url=SITE + "/")

    assert f'<meta property="og:image" content="{SITE}/social-preview.png">' in page
    assert "toolshop-qa-portfolio//" not in page


def test_no_site_url_means_no_preview_tags():
    for site_url in (None, ""):
        page = build_dashboard.build([], None, [], site_url=site_url)

        assert "og:" not in page
        assert "twitter:card" not in page


def test_quotes_and_tags_in_site_url_are_escaped():
    page = build_dashboard.build([], None, [], site_url='https://x.test/"><script>alert(1)</script>')

    assert page.count("</script>") == SCRIPT_TAGS_IN_TEMPLATE
    assert "<script>alert" not in page
    assert '"><' not in page.split("<style>")[0]
    assert "https://x.test/&quot;&gt;&lt;script&gt;" in page


# ---------- The command line ----------

def build_command(tmp_path, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / "build_dashboard.py"), *args],
                          capture_output=True, text=True, timeout=30, cwd=tmp_path)


def test_missing_history_file_builds_an_empty_page(tmp_path):
    out = tmp_path / "public" / "index.html"

    run = build_command(tmp_path, "--ci-history", str(tmp_path / "missing.json"),
                        "--out", str(out), "--link", "Report=ci-api/")

    assert run.returncode == 0, run.stderr
    assert "No runs recorded yet" in out.read_text()


def test_invalid_history_file_stops_the_build(tmp_path):
    history = tmp_path / "ci.json"
    history.write_text("<html>oops")
    out = tmp_path / "index.html"

    run = build_command(tmp_path, "--ci-history", str(history), "--out", str(out))

    assert run.returncode == 1
    assert "ERROR" in run.stderr
    assert not out.exists()


def test_link_without_equals_sign_is_rejected(tmp_path):
    run = build_command(tmp_path, "--out", str(tmp_path / "index.html"), "--link", "no-href")

    assert run.returncode == 2   # argparse: bad command line
    assert "Label=href" in run.stderr
