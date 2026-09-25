"""
Reusable chart math for the native dashboard.

Donut proportions, label positions, and percentage rounding used to be
computed by hand (and hand-checked) in chat, which is exactly the kind
of arithmetic mistake this whole app/ layer exists to eliminate. Here
it's written once, in code, and reused for every dashboard - no more
manual trig per chart.
"""

import math


def round_percentages(fractions):
    """Largest-remainder rounding: individual %s round normally, but the
    display always sums to exactly 100, by giving the leftover point(s)
    to whichever value(s) got shorted most by flooring."""
    raw = [f * 100 for f in fractions]
    floors = [int(x) for x in raw]
    remainder = 100 - sum(floors)
    order = sorted(range(len(raw)), key=lambda i: raw[i] - floors[i], reverse=True)
    result = floors[:]
    for i in order[:remainder]:
        result[i] += 1
    return result


def donut_geometry(fractions, cx=85, cy=85, r=66):
    """fractions: values summing to ~1 (proportions of the whole).
    Returns (conic_gradient_stops, label_positions) - stops as
    (start_pct, end_pct) tuples using the precise (unrounded) fractions,
    positions as (x, y) px for a direct label at each slice's midpoint
    angle."""
    stops = []
    positions = []
    cum = 0.0
    for f in fractions:
        start = cum
        cum += f
        mid = (start + cum) / 2
        theta = math.radians(mid * 360)
        x = cx + r * math.sin(theta)
        y = cy - r * math.cos(theta)
        positions.append((x, y))
        stops.append((start * 100, cum * 100))
    return stops, positions


def donut_panel_html(title, basis, slices, center_value, center_label, footer):
    """slices: list of dicts with keys name, value (numeric, used for
    proportions), display (string shown in the legend), color (hex)."""
    total = sum(s["value"] for s in slices)
    fractions = [s["value"] / total for s in slices] if total else [0] * len(slices)
    stops, positions = donut_geometry(fractions)
    pcts = round_percentages(fractions)

    gradient = ", ".join(
        f"{s['color']} {a:.3f}% {b:.3f}%" for s, (a, b) in zip(slices, stops)
    )
    labels_html = "".join(
        f'<div class="slice-label" style="left:{x:.0f}px; top:{y:.0f}px;">{pct}%</div>'
        for (x, y), pct in zip(positions, pcts)
    )
    legend_html = "".join(
        f'<div class="legend-row"><span class="swatch" style="background:{s["color"]};"></span>'
        f'<span class="legend-name">{s["name"]}</span>'
        f'<span class="legend-value">{s["display"]}</span>'
        f'<span class="legend-pct">{pct}%</span></div>'
        for s, pct in zip(slices, pcts)
    )
    return f"""
    <div class="card">
      <p class="card-title">{title}</p>
      <p class="card-basis">{basis}</p>
      <div class="donut-wrap">
        <div class="donut" style="background: conic-gradient({gradient});"></div>
        {labels_html}
        <div class="donut-center"><div class="kcal">{center_value}</div><div class="kcal-label">{center_label}</div></div>
      </div>
      <div class="legend">{legend_html}</div>
      <p class="card-foot">{footer}</p>
    </div>
    """


def bar_chart_html(title, basis, labels, values, target, footer):
    """One flat-colored bar per label, a dashed target line, and the
    portion of any bar above target rendered in the theme's accent
    color. `values`/`target` in the same units (kcal).

    Past ~10 bars (the 30-day range), per-bar value labels and every
    date label would overlap into noise, so those get thinned out; the
    exact value is still available via a native title="" tooltip on
    hover."""
    compact = len(values) > 10
    scale_max = target
    for v in values:
        scale_max = max(scale_max, v)
    scale_max = math.ceil(scale_max * 1.05 / 100) * 100

    target_pct = target / scale_max * 100
    label_every = max(1, math.ceil(len(labels) / 8)) if compact else 1
    cols = []
    day_labels = []
    for i, (label, value) in enumerate(zip(labels, values)):
        height_pct = value / scale_max * 100
        base = min(value, target)
        over = max(0, value - target)
        over_html = f'<div class="bar-over" style="flex: {over};"></div>' if over else ""
        val_html = "" if compact else f'<span class="bar-val" style="bottom: {height_pct:.1f}%;">{value:,}</span>'
        cols.append(
            f'<div class="bar-col" title="{label}: {value:,} kcal">'
            f"{val_html}"
            f'<div class="bar-track" style="height: {height_pct:.1f}%;">'
            f"{over_html}"
            f'<div class="bar-base" style="flex: {base};"></div>'
            f"</div></div>"
        )
        day_labels.append(f"<span>{label if i % label_every == 0 else ''}</span>")

    return f"""
    <div class="card">
      <p class="card-title">{title}</p>
      <p class="card-basis">{basis}</p>
      <div class="chart-plot">
        <div class="target-line" style="bottom: {target_pct:.1f}%;"><span>Target {target:,}</span></div>
        {''.join(cols)}
      </div>
      <div class="bar-days">{''.join(day_labels)}</div>
      <p class="card-foot">{footer}</p>
    </div>
    """
