"""
Color/font themes for the native dashboard. This is a color/font port
of a few hand-built artifact styles, not a full structural port: bespoke
flourishes some of those styles had in their original chat-generated
form (clipped corners, framed art windows, scanline textures, and the
like) aren't replicated here - one shared, clean card structure carries
every theme's coloring and typography instead. Add more themes here
following the same pattern if you want a wider bench.
"""

import random

THEMES = {
    "vaporwave": {
        "google_font": "Orbitron:wght@600;800",
        "page_bg": "#0d0d0d",
        "card_bg": "linear-gradient(160deg, #1a0b2e 0%, #351856 55%, #1a0b2e 100%)",
        "card_border": "1px solid rgba(255,110,199,0.35)",
        "title_font": "'Orbitron', system-ui, sans-serif",
        "title_color": "#ff8ed4",
        "basis_color": "#b79ce0",
        "text_primary": "#f4e9ff",
        "text_secondary": "#b79ce0",
        "donut_hole": "#1a0b2e",
        "slice_label_color": "#1a0b2e",
        "footer_color": "#9a84c2",
        "border_soft": "rgba(255,110,199,0.2)",
        "slice_colors": ["#ff6ec7", "#21e6ff", "#b967ff", "#5ffbf1"],
        "accent": "#b967ff",
        "bar_over_color": "#b967ff",
        "bar_base_color": "#ff6ec7",
        "kcal_font_size": "18px",
    },
    "jrpg": {
        "google_font": "Press+Start+2P",
        "page_bg": "#0d1440",
        "card_bg": "linear-gradient(180deg, #24378f 0%, #0d1440 100%)",
        "card_border": "3px solid #dbe8ff",
        "title_font": "'Press Start 2P', system-ui, sans-serif",
        "title_color": "#ffe9a8",
        "basis_color": "#9db4f0",
        "text_primary": "#eef1ff",
        "text_secondary": "#9db4f0",
        "donut_hole": "#0d1440",
        "slice_label_color": "#0d1440",
        "footer_color": "#7f93c9",
        "border_soft": "rgba(219,232,255,0.2)",
        "slice_colors": ["#f4c542", "#4fd8e0", "#e0527a", "#8c7ae6"],
        "accent": "#ffd76a",
        # Distinct from slice_colors[0] (#f4c542, also gold) - the two
        # golds were too close to tell "over target" from "under" at a
        # glance on the multi-day bar chart.
        "bar_over_color": "#e8792e",
        "bar_base_color": "#f4c542",
        # Press Start 2P is a wide pixel font - 18px reads oversized,
        # especially on the 30-day view's bigger numbers.
        "kcal_font_size": "13px",
    },
    "trading-card": {
        "google_font": "Baloo+2:wght@600;800",
        "page_bg": "#f4ecd8",
        "card_bg": "#fff8ea",
        "card_border": "8px solid #e8b923",
        "title_font": "'Baloo 2', system-ui, sans-serif",
        "title_color": "#2b2b2b",
        "basis_color": "#6b6355",
        "text_primary": "#2b2b2b",
        "text_secondary": "#8a8067",
        "donut_hole": "#fff8ea",
        "slice_label_color": "#ffffff",
        "footer_color": "#8a8067",
        "border_soft": "#e6d9ab",
        "slice_colors": ["#e0402a", "#4a90d9", "#f5c842", "#4caf50"],
        "accent": "#d43425",
        "bar_over_color": "#d43425",
        # Keep red for overage; slice_colors[0] is also red (#e0402a),
        # too close to tell an over-target bar from a normal one - use
        # the palette's blue for the normal bars instead.
        "bar_base_color": "#4a90d9",
        "kcal_font_size": "18px",
    },
    "cassette-futurism": {
        "google_font": "VT323",
        "page_bg": "#0d0d0d",
        "card_bg": "linear-gradient(160deg, #1c1410 0%, #100b08 100%)",
        "card_border": "1.5px solid #ffb000",
        "title_font": "'VT323', monospace",
        "title_color": "#ffb000",
        "basis_color": "#c98a3d",
        "text_primary": "#ffd699",
        "text_secondary": "#c98a3d",
        "donut_hole": "#100b08",
        "slice_label_color": "#100b08",
        "footer_color": "#a8722f",
        "border_soft": "rgba(255,176,0,0.2)",
        "slice_colors": ["#ffd699", "#ffb000", "#cc5500", "#8c5a1f"],
        "accent": "#ffb000",
        "bar_over_color": "#ffb000",
        "bar_base_color": "#ffd699",
        "kcal_font_size": "18px",
    },
    # The two plain, non-novelty defaults - no Google Font, system-ui
    # throughout, the same blue/orange/aqua categorical trio the very
    # first (pre-style-bank) macro-split chart used.
    "light": {
        "google_font": None,
        "page_bg": "#f9f9f7",
        "card_bg": "#fcfcfb",
        "card_border": "1px solid rgba(11,11,11,0.10)",
        "title_font": "system-ui, sans-serif",
        "title_color": "#0b0b0b",
        "basis_color": "#52514e",
        "text_primary": "#0b0b0b",
        "text_secondary": "#52514e",
        "donut_hole": "#fcfcfb",
        "slice_label_color": "#ffffff",
        "footer_color": "#898781",
        "border_soft": "rgba(11,11,11,0.10)",
        "slice_colors": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"],
        "accent": "#2a78d6",
        # Was the same blue as bar_base_color - no visible difference
        # between an over-target bar and a normal one. Red for overage.
        "bar_over_color": "#e34948",
        "bar_base_color": "#2a78d6",
        "kcal_font_size": "18px",
    },
    "dark": {
        "google_font": None,
        "page_bg": "#0d0d0d",
        "card_bg": "#1a1a19",
        "card_border": "1px solid rgba(255,255,255,0.10)",
        "title_font": "system-ui, sans-serif",
        "title_color": "#ffffff",
        "basis_color": "#c3c2b7",
        "text_primary": "#ffffff",
        "text_secondary": "#c3c2b7",
        "donut_hole": "#1a1a19",
        "slice_label_color": "#0b0b0b",
        "footer_color": "#898781",
        "border_soft": "rgba(255,255,255,0.10)",
        "slice_colors": ["#3987e5", "#d95926", "#199e70", "#c98500"],
        "accent": "#3987e5",
        "bar_over_color": "#e66767",
        "bar_base_color": "#3987e5",
        "kcal_font_size": "18px",
    },
}

THEME_LABELS = {
    "vaporwave": "Vaporwave",
    "jrpg": "JRPG",
    "trading-card": "Trading Card",
    "cassette-futurism": "Cassette Futurism",
    "dark": "Dark",
    "light": "Light",
}


def random_theme_name():
    return random.choice(list(THEMES.keys()))
