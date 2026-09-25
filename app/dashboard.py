"""
Assembles the daily/weekly dashboard pages from the workbook. Pulls from
Daily Summary (formula-computed, never a hand-written total, so it can't
go stale the way a prose "day total" note can) and the Food Log tab for
per-item detail.
"""

import datetime
import re
import sys
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent))

from charts import bar_chart_html, donut_panel_html
from effective_date import effective_date
from themes import THEME_LABELS, THEMES, random_theme_name

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKBOOK = PROJECT_ROOT / "project-200-tracker.xlsx"

MEAL_RE = re.compile(r"(breakfast|lunch|dinner|snack)", re.IGNORECASE)
# Strips a leading "Dinner:" / "Standard breakfast 1:" style label off an
# item's text, so the food list doesn't repeat the bucket name it's
# already grouped under.
MEAL_PREFIX_RE = re.compile(
    r"^(?:standard\s+)?(?:breakfast|lunch|dinner|snack)(?:\s+\d+)?\s*:\s*", re.IGNORECASE
)

# Cleanup for the food list footer: strips parentheticals, quantities,
# and pure filler/prep words so it reads as a plain food list ("avocado,
# bacon, chicken breast") instead of the full logged detail. Only strips
# recognizably extraneous tokens (amounts, units, size/prep words) -
# doesn't try to shorten or rename actual food names.
_PARENS_RE = re.compile(r"\([^)]*\)")
_QUANTITY_UNIT_RE = re.compile(
    r"~?\d+[\d/.]*\s*(?:g|kg|oz|tbsps?|tsps?|cups?|lbs?|fl\s?oz|servings?)\b", re.IGNORECASE
)
_LEADING_NUMBER_RE = re.compile(r"^~?\d+[\d/.]*\s+")
_LEADING_FILLER_RE = re.compile(
    r"^(?:spoonful of|a spoonful of|whole|medium|small|large|cooked in|cooked with|with a|with)\s+",
    re.IGNORECASE,
)


def clean_item_text(text: str) -> str:
    text = _PARENS_RE.sub("", text)
    segments = []
    for segment in text.split(","):
        segment = segment.strip()
        segment = _QUANTITY_UNIT_RE.sub("", segment).strip()
        segment = _LEADING_NUMBER_RE.sub("", segment).strip()
        while True:
            stripped = _LEADING_FILLER_RE.sub("", segment)
            if stripped == segment:
                break
            segment = stripped
        segment = re.sub(r"\s+", " ", segment).strip()
        if segment:
            segments.append(segment)
    return ", ".join(segments)


def _load():
    return openpyxl.load_workbook(WORKBOOK, data_only=True)


def daily_summary_row(date: datetime.date):
    wb = _load()
    ws = wb["Daily Summary"]
    for r in range(4, ws.max_row + 1):
        v = ws.cell(row=r, column=1).value
        if v and hasattr(v, "date") and v.date() == date:
            return {
                "calories": ws.cell(row=r, column=2).value or 0,
                "protein": ws.cell(row=r, column=3).value or 0,
                "carbs": ws.cell(row=r, column=4).value or 0,
                "fat": ws.cell(row=r, column=5).value or 0,
                "alcohol": ws.cell(row=r, column=6).value or 0,
                "target_cal": ws.cell(row=r, column=7).value or 2531,
                "target_protein": ws.cell(row=r, column=8).value or 188,
            }
    return None


def food_log_rows_for(date: datetime.date):
    wb = _load()
    ws = wb["Food Log"]
    rows = []
    for r in range(2, ws.max_row + 1):
        v = ws.cell(row=r, column=1).value
        if v and hasattr(v, "date") and v.date() == date:
            rows.append(
                {
                    "item": ws.cell(row=r, column=2).value or "",
                    "calories": ws.cell(row=r, column=3).value or 0,
                }
            )
    return rows


def macro_panels(summary, theme):
    protein, carbs, fat = summary["protein"], summary["carbs"], summary["fat"]
    net_kcal = protein * 4 + carbs * 4 + fat * 9
    gross_kcal = summary["calories"]
    other = max(0, gross_kcal - net_kcal)
    colors = theme["slice_colors"]

    calorie_share = donut_panel_html(
        "Calorie Share",
        "Protein/carb/fat by % of calories",
        [
            {"name": "Protein", "value": protein * 4, "display": f"{protein} g", "color": colors[0]},
            {"name": "Carbs (net)", "value": carbs * 4, "display": f"{carbs} g", "color": colors[1]},
            {"name": "Fat", "value": fat * 9, "display": f"{fat} g", "color": colors[2]},
        ],
        f"{net_kcal:,}",
        "net kcal",
        "Fat runs 9 kcal/g vs. 4 for protein and carbs, so it leads on calories despite fewer grams.",
    )

    total_g = protein + carbs + fat
    weight_share = donut_panel_html(
        "Weight Share",
        "Protein/carb/fat by % of grams",
        [
            {"name": "Protein", "value": protein, "display": f"{protein} g", "color": colors[0]},
            {"name": "Carbs (net)", "value": carbs, "display": f"{carbs} g", "color": colors[1]},
            {"name": "Fat", "value": fat, "display": f"{fat} g", "color": colors[2]},
        ],
        f"{total_g:,} g",
        "macros",
        "Same three macros as Calorie Share weighed instead of by energy.",
    )

    source_slices = [
        {"name": "Protein", "value": protein * 4, "display": f"{protein*4:,} kcal", "color": colors[0]},
        {"name": "Carbs (net)", "value": carbs * 4, "display": f"{carbs*4:,} kcal", "color": colors[1]},
        {"name": "Fat", "value": fat * 9, "display": f"{fat*9:,} kcal", "color": colors[2]},
    ]
    if other > 0:
        source_slices.append(
            {"name": "Other", "value": other, "display": f"{other:,} kcal", "color": colors[3]}
        )
    calorie_source = donut_panel_html(
        "Gross Calorie Source",
        f"Where all {gross_kcal:,} logged kcal came from",
        source_slices,
        f"{gross_kcal:,}",
        "gross kcal",
        "\"Other\" is mostly fiber calories, which the macro math above doesn't count, plus ordinary estimation noise.",
    )
    return calorie_share, weight_share, calorie_source


def daily_page_body(date: datetime.date, theme):
    summary = daily_summary_row(date)
    if summary is None:
        return f"<p style='padding:40px;text-align:center;color:{theme['text_primary']};'>No data logged for {date.isoformat()}.</p>"

    calorie_share, weight_share, calorie_source = macro_panels(summary, theme)

    bucket_order = ["Breakfast", "Lunch", "Dinner", "Snack", "Other"]
    bucket_kcal = {name: 0 for name in bucket_order}
    bucket_items = {name: [] for name in bucket_order}
    for row in food_log_rows_for(date):
        m = MEAL_RE.search(row["item"])
        bucket = m.group(1).capitalize() if m else "Other"
        bucket_kcal[bucket] += row["calories"]
        bucket_items[bucket].append(clean_item_text(MEAL_PREFIX_RE.sub("", row["item"])))
    buckets = {k: v for k, v in bucket_kcal.items() if v > 0}
    colors = theme["slice_colors"] + [theme["accent"]]
    items_panel = donut_panel_html(
        "Kcal by Item Group",
        "Gross kcal by meal keyword this day",
        [
            {"name": name, "value": val, "display": f"{val:,} kcal", "color": colors[i % len(colors)]}
            for i, (name, val) in enumerate(buckets.items())
        ],
        f"{sum(buckets.values()):,}",
        "gross kcal",
        " ".join(
            f"<strong>{name}:</strong> {'; '.join(bucket_items[name])}." for name in bucket_order if bucket_items[name]
        ),
    )

    return calorie_share + weight_share + calorie_source + items_panel


RANGE_LABELS = {"today": "Today", "yesterday": "Yesterday", "7d": "Last 7 Days", "30d": "Last 30 Days"}
RANGE_DAYS = {"today": 1, "yesterday": 1, "7d": 7, "30d": 30}


def notable_facts(daily):
    """A few short, purely-computed facts about the period - highest/
    lowest day, how many days cleared each target, and (for longer
    ranges) whether the second half trended up or down on calories vs
    the first half. Kept terse on purpose."""
    n = len(daily)
    high_date, high = max(daily, key=lambda ds: ds[1]["calories"])
    low_date, low = min(daily, key=lambda ds: ds[1]["calories"])
    over_target = sum(1 for _, s in daily if s["calories"] > s["target_cal"])
    protein_hit = sum(1 for _, s in daily if s["protein"] >= s["target_protein"])

    facts = [
        f"Highest {high_date.strftime('%-m/%-d')} ({high['calories']:,}), lowest {low_date.strftime('%-m/%-d')} ({low['calories']:,}).",
        f"Over target {over_target}/{n} days, protein hit {protein_hit}/{n} days.",
    ]

    if n >= 6:
        half = n // 2
        first_avg = sum(s["calories"] for _, s in daily[:half]) / half
        second_avg = sum(s["calories"] for _, s in daily[-half:]) / half
        delta = round(second_avg - first_avg)
        if abs(delta) >= 50:
            direction = "up" if delta > 0 else "down"
            facts.append(f"Trending {direction} {abs(delta):,} kcal/day vs. the first half.")

    return facts


def range_page_body(end_date: datetime.date, num_days: int, theme):
    if num_days == 1:
        return daily_page_body(end_date, theme)

    dates = [end_date - datetime.timedelta(days=i) for i in range(num_days - 1, -1, -1)]
    daily = [(d, daily_summary_row(d)) for d in dates]
    daily = [(d, s) for d, s in daily if s is not None]
    if not daily:
        return f"<p style='padding:40px;text-align:center;color:{theme['text_primary']};'>No data logged in the {num_days} days ending {end_date.isoformat()}.</p>"

    total = {
        "calories": sum(s["calories"] for _, s in daily),
        "protein": sum(s["protein"] for _, s in daily),
        "carbs": sum(s["carbs"] for _, s in daily),
        "fat": sum(s["fat"] for _, s in daily),
    }
    calorie_share, weight_share, calorie_source = macro_panels(total, theme)

    n = len(daily)
    span_note = f" ({n} of the last {num_days} days logged)" if n < num_days else ""
    target = daily[0][1]["target_cal"]
    labels = [d.strftime("%-m/%-d") for d, _ in daily]
    values = [s["calories"] for _, s in daily]

    avg_line = f"Daily average: {round(sum(values)/len(values)):,} kcal across {n} logged day{'s' if n != 1 else ''}."
    facts = notable_facts(daily)
    by_day = bar_chart_html(
        "Kcal by Day",
        f"Gross kcal logged, each day{span_note}",
        labels,
        values,
        target,
        "<br>".join([avg_line] + facts),
    )

    return calorie_share + weight_share + calorie_source + by_day


PAGE_SHELL = """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{font_link}
<style>
  body {{ margin: 0; background: {page_bg}; font-family: system-ui, -apple-system, sans-serif; }}
  .viz-root {{ padding: 28px 16px 40px; }}
  .topbar {{ max-width: 840px; margin: 0 auto 14px; display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
  .range-tabs {{ display: flex; align-items: center; gap: 4px; }}
  .range-tabs a {{ font-size: 13px; padding: 6px 12px; border-radius: 8px; text-decoration: none; color: {text_secondary}; border: 1px solid {border_soft}; }}
  .range-tabs a.active {{ color: {title_color}; border-color: {accent}; font-weight: 600; }}
  .p200-spinner {{ width: 14px; height: 14px; margin-left: 6px; border: 2px solid {border_soft}; border-top-color: {accent}; border-radius: 50%; animation: p200-spin 0.6s linear infinite; }}
  @media (prefers-reduced-motion: reduce) {{ .p200-spinner {{ animation: none; }} }}
  @keyframes p200-spin {{ to {{ transform: rotate(360deg); }} }}
  .settings-wrap {{ position: relative; }}
  .gear-btn {{ font-size: 24px; line-height: 1; background: none; border: none; padding: 4px; cursor: pointer; color: {text_secondary}; }}
  .settings-panel {{ position: absolute; right: 0; top: 38px; background: {card_bg}; border: {card_border}; border-radius: 10px; padding: 6px; min-width: 160px; z-index: 10; box-shadow: 0 8px 24px rgba(0,0,0,0.25); }}
  .settings-panel a {{ display: block; padding: 7px 10px; font-size: 13px; color: {text_primary}; text-decoration: none; border-radius: 6px; white-space: nowrap; }}
  .settings-panel a:hover {{ background: {border_soft}; }}
  .settings-panel a.active {{ font-weight: 700; color: {accent}; }}
  .settings-panel hr {{ border: none; border-top: 1px solid {border_soft}; margin: 6px 4px; }}
  .page-head {{ max-width: 840px; margin: 0 auto 20px; text-align: center; }}
  .eyebrow {{ font-size: 12px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: {basis_color}; margin: 0 0 4px; }}
  .page-head h1 {{ font-family: {title_font}; font-size: 24px; color: {title_color}; margin: 0 0 2px; }}
  .subline {{ font-size: 13px; color: {basis_color}; margin: 0; }}
  .grid {{ max-width: 840px; margin: 0 auto; display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}
  @media (max-width: 480px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  .card {{ background: {card_bg}; border: {card_border}; border-radius: 16px; padding: 20px 18px 18px; box-sizing: border-box; }}
  .card-title {{ font-family: {title_font}; font-size: 15px; font-weight: 700; color: {title_color}; margin: 0 0 2px; }}
  .card-basis {{ font-size: 11.5px; color: {basis_color}; margin: 0 0 16px; }}
  .donut-wrap {{ position: relative; width: 170px; height: 170px; margin: 0 auto 16px; }}
  .donut {{ width: 100%; height: 100%; border-radius: 50%; position: relative; }}
  .donut::after {{ content: ''; position: absolute; inset: 22%; border-radius: 50%; background: {donut_hole}; }}
  .donut-center {{ position: absolute; inset: 22%; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }}
  .donut-center .kcal {{ font-family: {title_font}; font-size: {kcal_font_size}; font-weight: 700; color: {text_primary}; }}
  .donut-center .kcal-label {{ font-size: 9.5px; color: {basis_color}; margin-top: 2px; }}
  .slice-label {{ position: absolute; transform: translate(-50%, -50%); font-size: 11px; font-weight: 700; color: {slice_label_color}; text-shadow: 0 1px 2px rgba(0,0,0,0.35); pointer-events: none; }}
  .legend {{ display: flex; flex-direction: column; gap: 7px; }}
  .legend-row {{ display: flex; align-items: baseline; gap: 8px; font-size: 12.5px; padding: 6px 0; border-bottom: 1px solid {border_soft}; }}
  .legend-row:last-child {{ border-bottom: none; }}
  .swatch {{ width: 9px; height: 9px; border-radius: 3px; flex: none; align-self: center; }}
  .legend-name {{ font-weight: 600; color: {text_primary}; flex: 1; }}
  .legend-value {{ font-weight: 600; color: {text_primary}; }}
  .legend-pct {{ color: {text_secondary}; min-width: 30px; text-align: right; }}
  .card-foot {{ font-size: 11px; line-height: 1.8; color: {footer_color}; margin: 12px 0 0; padding-top: 10px; border-top: 1px solid {border_soft}; }}
  .chart-plot {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 6px; height: 128px; margin: 26px 4px 0; position: relative; }}
  .target-line {{ position: absolute; left: 0; right: 0; border-top: 1.5px dashed {accent}; }}
  .target-line span {{ position: absolute; right: 0; top: -16px; font-size: 9.5px; color: {accent}; }}
  .bar-col {{ flex: 1; height: 100%; position: relative; display: flex; justify-content: center; align-items: flex-end; }}
  .bar-val {{ position: absolute; left: 50%; transform: translateX(-50%); margin-bottom: 3px; font-size: 9.5px; color: {text_secondary}; white-space: nowrap; }}
  .bar-track {{ width: 100%; max-width: 24px; display: flex; flex-direction: column; }}
  .bar-over {{ background: {bar_over_color}; }}
  .bar-base {{ background: {bar_base_color}; }}
  .bar-days {{ display: flex; justify-content: space-between; gap: 6px; margin: 6px 4px 0; }}
  .bar-days span {{ flex: 1; text-align: center; font-size: 10.5px; color: {text_secondary}; }}
</style>
<script>
  // Remembers the user's explicit THEME choice only (not range) across
  // visits, via localStorage. Absence of a saved theme means "random" -
  // every load with no ?theme= gets a fresh server-picked theme. This
  // runs synchronously in <head> so a redirect (when a saved theme
  // exists but the URL doesn't name one) happens before paint.
  (function() {{
    var params = new URLSearchParams(location.search);
    if (!params.has('theme')) {{
      var saved = localStorage.getItem('p200_theme');
      if (saved) {{
        params.set('theme', saved);
        location.replace(location.pathname + '?' + params.toString());
      }}
    }}
  }})();
  function p200SetTheme(name) {{
    if (name === 'random') {{ localStorage.removeItem('p200_theme'); }}
    else {{ localStorage.setItem('p200_theme', name); }}
  }}
  function p200ToggleSettings() {{
    var el = document.getElementById('p200-settings-panel');
    el.hidden = !el.hidden;
  }}
  function p200ShowSpinner() {{
    var el = document.getElementById('p200-spinner');
    if (el) el.hidden = false;
  }}
  document.addEventListener('click', function(e) {{
    var wrap = document.querySelector('.settings-wrap');
    if (wrap && !wrap.contains(e.target)) {{
      var el = document.getElementById('p200-settings-panel');
      if (el) el.hidden = true;
    }}
  }});
</script>
</head>
<body><div class="viz-root">
  <div class="topbar">
    <div class="range-tabs">{range_tabs}<span class="p200-spinner" id="p200-spinner" hidden></span></div>
    <div class="settings-wrap">
      <button class="gear-btn" onclick="p200ToggleSettings()">&#9881;</button>
      <div class="settings-panel" id="p200-settings-panel" hidden>{theme_links}</div>
    </div>
  </div>
  <div class="page-head">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{heading}</h1>
    <p class="subline">{subline}</p>
  </div>
  <div class="grid">{body}</div>
</div></body></html>
"""


def _query(range_key, theme_name=None):
    q = f"range={range_key}"
    if theme_name:
        q += f"&theme={theme_name}"
    return q


def _range_tabs_html(current_range, theme_name):
    parts = []
    for key, label in RANGE_LABELS.items():
        cls = " class=\"active\"" if key == current_range else ""
        parts.append(f'<a href="/?{_query(key, theme_name)}" onclick="p200ShowSpinner()"{cls}>{label}</a>')
    return "".join(parts)


def _theme_links_html(current_range, current_theme_name, is_random):
    parts = []
    for key, label in THEME_LABELS.items():
        cls = " class=\"active\"" if (key == current_theme_name and not is_random) else ""
        parts.append(
            f'<a href="/?{_query(current_range, key)}" onclick="p200SetTheme(\'{key}\');p200ShowSpinner()"{cls}>{label}</a>'
        )
    parts.append("<hr>")
    cls = " class=\"active\"" if is_random else ""
    parts.append(
        f'<a href="/?{_query(current_range)}" onclick="p200SetTheme(\'random\');p200ShowSpinner()"{cls}>Random</a>'
    )
    return "".join(parts)


def _project_name() -> str:
    """CLAUDE.md's title line, title-cased, same derivation the hooks use
    (see .claude/hooks/session-start.sh) - so the dashboard's eyebrow
    always matches whatever this instance actually got renamed to during
    onboarding, no separate manual edit required."""
    try:
        first_line = (PROJECT_ROOT / "CLAUDE.md").read_text().splitlines()[0]
    except (OSError, IndexError):
        return "Project"
    return first_line.strip().title() or "Project"


def render_page(heading, subline, body, range_key, theme_name, is_random):
    theme = THEMES[theme_name]
    font_link = ""
    if theme["google_font"]:
        font_link = (
            '<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link href="https://fonts.googleapis.com/css2?family={theme["google_font"]}&display=swap" rel="stylesheet">'
        )
    return PAGE_SHELL.format(
        title=heading,
        body=body,
        heading=heading,
        eyebrow=_project_name(),
        subline=subline,
        font_link=font_link,
        range_tabs=_range_tabs_html(range_key, None if is_random else theme_name),
        theme_links=_theme_links_html(range_key, theme_name, is_random),
        **{k: v for k, v in theme.items() if k not in ("slice_colors", "google_font")},
    )


def _last_complete_date(end_date: datetime.date, num_days: int) -> datetime.date:
    """A multi-day report never includes a day that isn't over yet, even
    if every meal for it is already logged - the day only counts once
    it's past 5am the next day (see app/effective_date.py's day
    boundary). If the requested end date is today's still-open effective
    day (or later), roll the window back to end on the most recent day
    that's actually done, so the report still covers `num_days` complete
    days instead of a short one. Single-day ('today') reports are exempt
    - that view is meant to show today's in-progress numbers."""
    if num_days <= 1:
        return end_date
    today = effective_date()
    if end_date >= today:
        return today - datetime.timedelta(days=1)
    return end_date


def render(range_key: str, end_date: datetime.date, theme_name=None):
    """range_key: one of 'today', '7d', '30d'. theme_name: an explicit
    THEMES key, or None to pick randomly for this load."""
    range_key = range_key if range_key in RANGE_DAYS else "today"
    num_days = RANGE_DAYS[range_key]
    end_date = _last_complete_date(end_date, num_days)
    is_random = theme_name not in THEMES
    actual_theme_name = theme_name if not is_random else random_theme_name()

    body = range_page_body(end_date, num_days, THEMES[actual_theme_name])

    if num_days == 1:
        heading, subline = f"Daily Report {end_date.isoformat()}", end_date.strftime("%B %-d, %Y")
    else:
        start = end_date - datetime.timedelta(days=num_days - 1)
        heading = f"{RANGE_LABELS[range_key]} Report {start.isoformat()} to {end_date.isoformat()}"
        subline = f"{start.strftime('%B %-d')} to {end_date.strftime('%B %-d, %Y')}"

    return render_page(heading, subline, body, range_key, actual_theme_name, is_random)
