import streamlit as st
import pandas as pd
import datetime
import randfacts

# Master list of all available themes and morphism styles
ALL_THEMES = [
    "Latte (Light)",
    "Espresso (Dark)",
    "Matcha (Green)",
    "Caramel Macchiato (Amber)",
    "Strawberry Frappé (Pink)",
    "Taro Boba (Purple)",
    "Midnight Cyber Brew (Dark Neon)",
    "Velvet Mocha (Cocoa)"
]

ALL_STYLES = [
    "Modern Flat",
    "Glassmorphism",
    "Neumorphism"
]

THEME_METADATA = {
    "Latte (Light)": {
        "price": 0,
        "desc": "Classic warm pastel coffee & creamy milk palette.",
        "icon": "☕",
        "swatch": ["#F9F3E3", "#4A3B32", "#E24A00"]
    },
    "Espresso (Dark)": {
        "price": 20,
        "desc": "Deep roasted espresso bean with rich warm dark contrast (Tutorial Unlock).",
        "icon": "🌙",
        "swatch": ["#100A06", "#221610", "#FFA87D"]
    },
    "Matcha (Green)": {
        "price": 600,
        "desc": "Fresh ceremonial Japanese green tea & clean spring vibes.",
        "icon": "🍵",
        "swatch": ["#F3F8F1", "#3B6B35", "#3B6B35"]
    },
    "Caramel Macchiato (Amber)": {
        "price": 600,
        "desc": "Buttery golden caramel drizzle over sweet vanilla foam.",
        "icon": "🍯",
        "swatch": ["#FDF8EE", "#D97706", "#B45309"]
    },
    "Strawberry Frappé (Pink)": {
        "price": 750,
        "desc": "Sweet strawberry puree blended with fresh pastel cream.",
        "icon": "🌸",
        "swatch": ["#FFF2F5", "#DB2777", "#BE185D"]
    },
    "Taro Boba (Purple)": {
        "price": 750,
        "desc": "Creamy purple taro milk tea with royal violet accents.",
        "icon": "🧋",
        "swatch": ["#FAF5FF", "#9333EA", "#7E22CE"]
    },
    "Midnight Cyber Brew (Dark Neon)": {
        "price": 1050,
        "desc": "Obsidian cold brew electrified with glowing neon cyan.",
        "icon": "⚡",
        "swatch": ["#0B0F19", "#131B2E", "#06B6D4"]
    },
    "Velvet Mocha (Cocoa)": {
        "price": 900,
        "desc": "Velvety dark Swiss chocolate & toasted hazelnut warmth.",
        "icon": "🍫",
        "swatch": ["#1A120E", "#281B15", "#E09F67"]
    }
}

def inject_custom_css(theme="Latte (Light)", ui_style="Modern Flat", user=None):
    from feature_flags import get_locked_sidebar_css
    locked_sidebar_css = get_locked_sidebar_css(user)

    # 1. Sanitize inputs
    if theme not in ALL_THEMES:
        theme = "Latte (Light)"
        
    if ui_style not in ALL_STYLES:
        ui_style = "Modern Flat"

    # 2. Complete Theme Token Dictionary
    theme_tokens = {
        "Latte (Light)": {
            "bg_gradient": "linear-gradient(135deg, #F9F3E3 0%, #E8E3D9 100%)",
            "text_color": "#2C1A11",
            "text_muted": "rgba(44, 26, 17, 0.7)",
            "sidebar_bg": "#E8E3D9",
            "border_color": "rgba(74, 59, 50, 0.18)",
            "container_bg": "#F9F3E3",
            "input_bg": "#FFFFFF",
            "input_text": "#2C1A11",
            "tag_bg": "#E8E3D9",
            "button_bg": "#4A3B32",
            "button_hover": "#33251D",
            "button_text": "#FFFFFF",
            "button_border": "1px solid rgba(74, 59, 50, 0.2)",
            "accent_color": "#E24A00",
            "badge_bg": "rgba(226, 74, 0, 0.12)",
            "metric_card_bg": "rgba(249, 243, 227, 0.85)",
            "glass_bg": "rgba(255, 255, 255, 0.5)",
            "glass_border": "rgba(255, 255, 255, 0.75)",
            "glass_shadow": "0 8px 32px 0 rgba(74, 59, 50, 0.1)",
            "neu_bg": "#F2ECE0",
            "neu_dark_shadow": "#D8D0C0",
            "neu_light_shadow": "#FFFFFF",
            "neu_border": "1px solid rgba(255, 255, 255, 0.7)",
        },
        "Espresso (Dark)": {
            "bg_gradient": "linear-gradient(135deg, #100A06 0%, #1F140D 50%, #140C07 100%)",
            "text_color": "#F4E8D3",
            "text_muted": "rgba(244, 232, 211, 0.7)",
            "sidebar_bg": "#180F0A",
            "border_color": "rgba(244, 232, 211, 0.18)",
            "container_bg": "#221610",
            "input_bg": "#2B1B13",
            "input_text": "#F4E8D3",
            "tag_bg": "#442A1D",
            "button_bg": "#5A3E2D",
            "button_hover": "#78533D",
            "button_text": "#FFFFFF",
            "button_border": "1px solid rgba(244, 232, 211, 0.2)",
            "accent_color": "#FFA87D",
            "badge_bg": "rgba(255, 168, 125, 0.15)",
            "metric_card_bg": "rgba(34, 22, 16, 0.75)",
            "glass_bg": "rgba(255, 255, 255, 0.06)",
            "glass_border": "rgba(255, 255, 255, 0.16)",
            "glass_shadow": "0 8px 32px 0 rgba(0, 0, 0, 0.45)",
            "neu_bg": "#1B1009",
            "neu_dark_shadow": "#0B0604",
            "neu_light_shadow": "#2B1A0E",
            "neu_border": "1px solid rgba(255, 255, 255, 0.03)",
        },
        "Matcha (Green)": {
            "bg_gradient": "linear-gradient(135deg, #FFFFFF 0%, #F3F8F1 50%, #DDECD9 100%)",
            "text_color": "#243D21",
            "text_muted": "rgba(36, 61, 33, 0.7)",
            "sidebar_bg": "#DDECD9",
            "border_color": "rgba(46, 74, 43, 0.18)",
            "container_bg": "#FFFFFF",
            "input_bg": "#F6FAF4",
            "input_text": "#243D21",
            "tag_bg": "#E2EFE0",
            "button_bg": "#3B6B35",
            "button_hover": "#2C5227",
            "button_text": "#FFFFFF",
            "button_border": "1px solid rgba(46, 74, 43, 0.2)",
            "accent_color": "#3B6B35",
            "badge_bg": "rgba(59, 107, 53, 0.15)",
            "metric_card_bg": "rgba(255, 255, 255, 0.85)",
            "glass_bg": "rgba(255, 255, 255, 0.65)",
            "glass_border": "rgba(255, 255, 255, 0.8)",
            "glass_shadow": "0 8px 32px 0 rgba(46, 74, 43, 0.12)",
            "neu_bg": "#EBF4E9",
            "neu_dark_shadow": "#CADBC7",
            "neu_light_shadow": "#FFFFFF",
            "neu_border": "1px solid rgba(255, 255, 255, 0.6)",
        },
        "Caramel Macchiato (Amber)": {
            "bg_gradient": "linear-gradient(135deg, #FDF8EE 0%, #F5E9D3 100%)",
            "text_color": "#3D260D",
            "text_muted": "rgba(61, 38, 13, 0.7)",
            "sidebar_bg": "#F5E9D3",
            "border_color": "rgba(217, 119, 6, 0.22)",
            "container_bg": "#FDF8EE",
            "input_bg": "#FFFFFF",
            "input_text": "#3D260D",
            "tag_bg": "#F9E4C5",
            "button_bg": "#D97706",
            "button_hover": "#B45309",
            "button_text": "#FFFFFF",
            "button_border": "1px solid rgba(217, 119, 6, 0.3)",
            "accent_color": "#D97706",
            "badge_bg": "rgba(217, 119, 6, 0.15)",
            "metric_card_bg": "rgba(253, 248, 238, 0.88)",
            "glass_bg": "rgba(255, 255, 255, 0.55)",
            "glass_border": "rgba(255, 255, 255, 0.8)",
            "glass_shadow": "0 8px 32px 0 rgba(217, 119, 6, 0.12)",
            "neu_bg": "#F6EBD7",
            "neu_dark_shadow": "#DBCDB7",
            "neu_light_shadow": "#FFFFFF",
            "neu_border": "1px solid rgba(255, 255, 255, 0.7)",
        },
        "Strawberry Frappé (Pink)": {
            "bg_gradient": "linear-gradient(135deg, #FFF2F5 0%, #FCE2E9 100%)",
            "text_color": "#4A1525",
            "text_muted": "rgba(74, 21, 37, 0.7)",
            "sidebar_bg": "#FCE2E9",
            "border_color": "rgba(219, 39, 119, 0.2)",
            "container_bg": "#FFF2F5",
            "input_bg": "#FFFFFF",
            "input_text": "#4A1525",
            "tag_bg": "#FAD2DE",
            "button_bg": "#DB2777",
            "button_hover": "#BE185D",
            "button_text": "#FFFFFF",
            "button_border": "1px solid rgba(219, 39, 119, 0.3)",
            "accent_color": "#DB2777",
            "badge_bg": "rgba(219, 39, 119, 0.14)",
            "metric_card_bg": "rgba(255, 242, 245, 0.9)",
            "glass_bg": "rgba(255, 255, 255, 0.6)",
            "glass_border": "rgba(255, 255, 255, 0.85)",
            "glass_shadow": "0 8px 32px 0 rgba(219, 39, 119, 0.12)",
            "neu_bg": "#F9E0E7",
            "neu_dark_shadow": "#DEC0C8",
            "neu_light_shadow": "#FFFFFF",
            "neu_border": "1px solid rgba(255, 255, 255, 0.7)",
        },
        "Taro Boba (Purple)": {
            "bg_gradient": "linear-gradient(135deg, #FAF5FF 0%, #F0E6FA 100%)",
            "text_color": "#31144D",
            "text_muted": "rgba(49, 20, 77, 0.7)",
            "sidebar_bg": "#F0E6FA",
            "border_color": "rgba(147, 51, 234, 0.2)",
            "container_bg": "#FAF5FF",
            "input_bg": "#FFFFFF",
            "input_text": "#31144D",
            "tag_bg": "#E8D8F7",
            "button_bg": "#9333EA",
            "button_hover": "#7E22CE",
            "button_text": "#FFFFFF",
            "button_border": "1px solid rgba(147, 51, 234, 0.3)",
            "accent_color": "#9333EA",
            "badge_bg": "rgba(147, 51, 234, 0.14)",
            "metric_card_bg": "rgba(250, 245, 255, 0.9)",
            "glass_bg": "rgba(255, 255, 255, 0.6)",
            "glass_border": "rgba(255, 255, 255, 0.85)",
            "glass_shadow": "0 8px 32px 0 rgba(147, 51, 234, 0.12)",
            "neu_bg": "#EDE2F7",
            "neu_dark_shadow": "#CEC1DC",
            "neu_light_shadow": "#FFFFFF",
            "neu_border": "1px solid rgba(255, 255, 255, 0.7)",
        },
        "Midnight Cyber Brew (Dark Neon)": {
            "bg_gradient": "linear-gradient(135deg, #070A10 0%, #0F172A 50%, #090D16 100%)",
            "text_color": "#E2E8F0",
            "text_muted": "rgba(226, 232, 240, 0.7)",
            "sidebar_bg": "#0B1120",
            "border_color": "rgba(6, 182, 212, 0.25)",
            "container_bg": "#0F172A",
            "input_bg": "#131E35",
            "input_text": "#E2E8F0",
            "tag_bg": "#1E293B",
            "button_bg": "#0891B2",
            "button_hover": "#06B6D4",
            "button_text": "#FFFFFF",
            "button_border": "1px solid rgba(6, 182, 212, 0.4)",
            "accent_color": "#06B6D4",
            "badge_bg": "rgba(6, 182, 212, 0.18)",
            "metric_card_bg": "rgba(15, 23, 42, 0.85)",
            "glass_bg": "rgba(15, 23, 42, 0.55)",
            "glass_border": "rgba(6, 182, 212, 0.28)",
            "glass_shadow": "0 8px 32px 0 rgba(0, 0, 0, 0.6)",
            "neu_bg": "#0D1424",
            "neu_dark_shadow": "#04070D",
            "neu_light_shadow": "#16213B",
            "neu_border": "1px solid rgba(6, 182, 212, 0.1)",
        },
        "Velvet Mocha (Cocoa)": {
            "bg_gradient": "linear-gradient(135deg, #140E0A 0%, #201610 50%, #17100B 100%)",
            "text_color": "#F3EDE8",
            "text_muted": "rgba(243, 237, 232, 0.7)",
            "sidebar_bg": "#19110D",
            "border_color": "rgba(224, 159, 103, 0.22)",
            "container_bg": "#241912",
            "input_bg": "#2F2018",
            "input_text": "#F3EDE8",
            "tag_bg": "#422D22",
            "button_bg": "#A8653A",
            "button_hover": "#BD7648",
            "button_text": "#FFFFFF",
            "button_border": "1px solid rgba(224, 159, 103, 0.3)",
            "accent_color": "#E09F67",
            "badge_bg": "rgba(224, 159, 103, 0.15)",
            "metric_card_bg": "rgba(36, 25, 18, 0.85)",
            "glass_bg": "rgba(255, 255, 255, 0.05)",
            "glass_border": "rgba(224, 159, 103, 0.18)",
            "glass_shadow": "0 8px 32px 0 rgba(0, 0, 0, 0.5)",
            "neu_bg": "#1E140E",
            "neu_dark_shadow": "#0B0705",
            "neu_light_shadow": "#312117",
            "neu_border": "1px solid rgba(224, 159, 103, 0.08)",
        }
    }

    t = theme_tokens[theme]

    # 3. Morphism Card Definitions
    card_targets = 'div[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stForm"], div[data-testid="stMetric"], .app-card'
    card_inner = 'div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"], div[data-testid="stForm"] > div'

    if ui_style == "Modern Flat":
        morphism_css = f"""
        {card_targets} {{
            background-color: var(--container-bg) !important;
            border: 1.5px solid var(--border-color) !important;
            border-radius: 20px !important;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 1.15rem !important;
        }}
        {card_inner} {{
            background: transparent !important;
            border: none !important;
        }}
        div[data-testid="stMetric"] {{
            background-color: var(--metric-card-bg) !important;
        }}
        """
    elif ui_style == "Glassmorphism":
        morphism_css = f"""
        {card_targets} {{
            background: var(--glass-bg) !important;
            backdrop-filter: blur(20px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
            border: 1.5px solid var(--glass-border) !important;
            border-radius: 24px !important;
            box-shadow: var(--glass-shadow) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 1.25rem !important;
        }}
        {card_inner} {{
            background: transparent !important;
            border: none !important;
        }}
        """
    else:  # Neumorphism
        morphism_css = f"""
        {card_targets} {{
            background: var(--neu-bg) !important;
            border: var(--neu-border) !important;
            border-radius: 24px !important;
            box-shadow: 8px 8px 20px var(--neu-dark-shadow), -8px -8px 20px var(--neu-light-shadow) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 1.25rem !important;
        }}
        {card_inner} {{
            background: transparent !important;
            border: none !important;
        }}
        """

    # 4. Master CSS with Clean CSS Custom Properties
    css = f"""
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    @import url('https://cdn.jsdelivr.net/gh/lipis/flag-icons@7.2.3/css/flag-icons.min.css');

    @font-face {{
        font-family: "Twemoji Country Flags";
        src: url("https://cdn.jsdelivr.net/npm/country-flag-emoji-polyfill@0.1.8/dist/TwemojiCountryFlags.woff2") format("woff2");
        font-display: swap;
    }}

    :root {{
        --bg-gradient: {t['bg_gradient']};
        --text-color: {t['text_color']};
        --text-muted: {t['text_muted']};
        --sidebar-bg: {t['sidebar_bg']};
        --border-color: {t['border_color']};
        --container-bg: {t['container_bg']};
        --input-bg: {t['input_bg']};
        --input-text: {t['input_text']};
        --tag-bg: {t['tag_bg']};
        --button-bg: {t['button_bg']};
        --button-hover: {t['button_hover']};
        --button-text: {t['button_text']};
        --button-border: {t['button_border']};
        --accent-color: {t['accent_color']};
        --badge-bg: {t['badge_bg']};
        --metric-card-bg: {t['metric_card_bg']};
        --glass-bg: {t['glass_bg']};
        --glass-border: {t['glass_border']};
        --glass-shadow: {t['glass_shadow']};
        --neu-bg: {t['neu_bg']};
        --neu-dark-shadow: {t['neu_dark_shadow']};
        --neu-light-shadow: {t['neu_light_shadow']};
        --neu-border: {t['neu_border']};
    }}

    /* Global Typography & Font Family with Full Country Flag Support on Windows */
    html, body, .stApp, p, h1, h2, h3, h4, h5, h6, input, label, select, option {{
        font-family: 'Plus Jakarta Sans', 'Twemoji Country Flags', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji', sans-serif !important;
    }}

    /* Preserve Streamlit Material Icons font ligatures (prevent raw ligature text like 'arrow_drop_down') */
    [data-testid="stIconMaterial"],
    [data-testid="stExpanderToggleIcon"],
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    [class*="material-symbols"],
    [class*="material-icons"],
    details summary span[translate="no"],
    details summary [data-testid="stIconMaterial"],
    div[data-testid="stExpander"] details summary span:first-child {{
        font-family: "Material Symbols Rounded", "Material Icons", "Material Symbols Outlined", sans-serif !important;
        font-feature-settings: "liga" 1 !important;
        -webkit-font-feature-settings: "liga" 1 !important;
        text-rendering: optimizeLegibility !important;
    }}

    /* Hide Streamlit default top branding decorations */
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}
    footer {{
        display: none !important;
    }}
    [data-testid="stDecoration"] {{
        display: none !important;
    }}

    /* Page View & Layout */
    .stApp, [data-testid="stAppViewContainer"], .main {{
        background: var(--bg-gradient) !important;
        color: var(--text-color) !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg) !important;
    }}

    /* Typography Hierarchy */
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] h4,
    [data-testid="stAppViewContainer"] h5,
    [data-testid="stAppViewContainer"] h6,
    [data-testid="stAppViewContainer"] li,
    [data-testid="stAppViewContainer"] label,
    div[data-testid="stCaptionContainer"],
    div[data-testid="stCaptionContainer"] p {{
        color: var(--text-color) !important;
    }}

    hr {{
        border-bottom: 2px solid var(--border-color) !important;
        border-top: none !important;
        background: none !important;
        margin: 1.25em 0 !important;
    }}

    .user-highlight {{ 
        color: var(--accent-color) !important; 
        font-weight: 800; 
    }}
    .stats-text {{ 
        color: var(--text-muted) !important; 
        font-size: 0.9em; 
        text-align: center; 
    }}

    /* Header Shell */
    .app-header-shell {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: var(--container-bg);
        border: 1.5px solid var(--border-color);
        border-radius: 20px;
        padding: 0.95rem 1.4rem;
        margin-bottom: 0.6rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        gap: 0.8rem;
    }}
    .app-header-greeting {{
        display: flex;
        flex-direction: column;
        min-width: 0;
    }}
    .app-header-greeting h2 {{
        margin: 0 !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .app-header-greeting span {{
        color: var(--text-muted);
        font-size: 0.82rem;
        font-weight: 600;
        margin-top: 2px;
    }}
    .app-header-badges {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-shrink: 0;
    }}
    .header-pill-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        border: 1.5px solid var(--border-color);
        background: var(--input-bg);
        color: var(--text-color);
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        white-space: nowrap;
    }}

    /* Standalone Daily Fact Quote (Outside the box) */
    .daily-fact-quote {{
        display: flex;
        align-items: flex-start;
        gap: 8px;
        background: var(--input-bg);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 0.55rem 0.9rem;
        font-size: 0.82rem;
        color: var(--text-muted);
        line-height: 1.4;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }}
    .daily-fact-quote strong {{
        color: var(--text-color);
        font-weight: 700;
    }}
    .daily-fact-quote em {{
        color: var(--text-color);
    }}

    /* =========================================================
       MOBILE-FIRST RESPONSIVE ENGINE (@media max-width: 768px)
       ========================================================= */
    @media (max-width: 768px) {{
        /* Optimize viewport canvas */
        .block-container {{
            padding-top: 1.2rem !important;
            padding-bottom: 3.5rem !important;
            padding-left: 0.65rem !important;
            padding-right: 0.65rem !important;
            max-width: 100% !important;
        }}

        /* App Header on Mobile: Executive Column & Full-Width Shelf */
        .app-header-shell {{
            flex-direction: column !important;
            align-items: stretch !important;
            padding: 0.85rem 1rem !important;
            gap: 10px !important;
            border-radius: 18px !important;
        }}
        .app-header-greeting h2 {{
            font-size: 1.15rem !important;
            white-space: normal !important;
        }}
        .app-header-greeting span {{
            font-size: 0.78rem !important;
        }}
        .app-header-badges {{
            display: grid !important;
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 6px !important;
            width: 100% !important;
        }}
        .header-pill-badge {{
            justify-content: center !important;
            padding: 0.35rem 0.4rem !important;
            font-size: 0.75rem !important;
            gap: 3px !important;
        }}
        .header-pill-badge span {{
            font-size: 0.75rem !important;
        }}

        /* Fact Quote on Mobile */
        .daily-fact-quote {{
            font-size: 0.76rem !important;
            padding: 0.45rem 0.7rem !important;
            margin-bottom: 0.9rem !important;
        }}

        /* Mobile Metric Grids (Flow 4 metrics into 2x2 grid) */
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) {{
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 8px !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) > div {{
            width: 100% !important;
            min-width: 0 !important;
        }}
        div[data-testid="stMetric"] {{
            padding: 0.65rem 0.75rem !important;
            border-radius: 14px !important;
        }}
        [data-testid="stMetricValue"] {{
            font-size: 1.25rem !important;
        }}
        [data-testid="stMetricLabel"] {{
            font-size: 0.75rem !important;
        }}

        /* Mobile Button Touch Targets */
        div[data-testid="stButton"] > button,
        div[data-testid="stFormSubmitButton"] > button,
        div[data-testid="stDownloadButton"] > button {{
            padding: 0.65rem 0.85rem !important;
            font-size: 0.88rem !important;
            border-radius: 14px !important;
        }}

        /* Native App Touch Feedback */
        div[data-testid="stButton"] > button:active,
        div[data-testid="stFormSubmitButton"] > button:active,
        div[data-testid*="Segmented"] button:active {{
            transform: scale(0.96) !important;
        }}

        /* Fluid Segmented Control on Mobile */
        div[data-testid*="SegmentedControl"],
        div[data-baseweb="segmented-control"] {{
            width: 100% !important;
            overflow-x: auto !important;
            padding: 3px !important;
        }}
        div[data-testid*="SegmentedControl"] button,
        div[data-baseweb="segmented-control"] button {{
            padding: 0.4rem 0.75rem !important;
            font-size: 0.82rem !important;
            flex: 1 !important;
        }}
    }}

    /* --- Tactile Drink Quick-Tap Cards --- */
    .drink-card-btn {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 1.2rem 1rem;
        background: var(--input-bg);
        border: 1.5px solid var(--border-color);
        border-radius: 20px;
        text-align: center;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        user-select: none;
    }}
    .drink-card-btn:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        border-color: var(--accent-color);
    }}

    /* Metric Cards */
    div[data-testid="stMetric"] {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        border-radius: 18px !important;
        padding: 0.9rem 1.1rem !important;
    }}
    [data-testid="stMetricValue"] {{
        color: var(--text-color) !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }}

    /* Card Hover Motion */
    div[data-testid="stVerticalBlockBorderWrapper"]:hover,
    div[data-testid="stForm"]:hover,
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
    }}

    /* Sidebar Navigation */
    [data-testid="stSidebarNav"] > ul {{
        display: flex;
        flex-direction: column;
        min-height: 60vh;
    }}
    [data-testid="stSidebarNav"] > ul > li:last-child {{
        margin-top: auto;
        border-top: 1px solid var(--border-color);
        padding-top: 10px;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab"] {{
        color: var(--text-muted) !important;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.6rem 1.2rem !important;
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        color: var(--text-color) !important;
        font-weight: 800;
        border-bottom-color: var(--accent-color) !important;
    }}

    /* Chart Background Transparency */
    [data-testid="stFullScreenFrame"],
    div[data-testid="stFullScreenFrame"] > div,
    [data-testid="stVegaLiteChart"],
    .stVegaLiteChart,
    [data-testid="stAltairChart"],
    .stAltairChart,
    .element-container:has(.stVegaLiteChart) {{
        background-color: transparent !important;
        background: transparent !important;
    }}

    /* =========================================================
       FORM INPUTS (Text, Password, Textarea, Number Input)
       ========================================================= */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="textarea"] {{
        background-color: var(--input-bg) !important;
        border: 1.5px solid var(--border-color) !important;
        border-radius: 14px !important;
    }}
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    div[data-baseweb="textarea"] textarea {{
        background: transparent !important;
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
        font-family: inherit !important;
    }}
    div[data-baseweb="input"] input::placeholder,
    div[data-baseweb="textarea"] textarea::placeholder {{
        color: var(--text-muted) !important;
        -webkit-text-fill-color: var(--text-muted) !important;
    }}

    /* =========================================================
       SELECTBOX & MULTISELECT (Field Controls)
       ========================================================= */
    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stMultiSelect"] > div > div,
    div[data-testid="stMultiSelectTagsContainer"],
    div[data-baseweb="select"] > div {{
        background-color: var(--input-bg) !important;
        border: 1.5px solid var(--border-color) !important;
        border-radius: 14px !important;
    }}

    /* Selected Value Text in Selectbox & Multiselect */
    div[data-testid="stSelectbox"] input,
    div[data-testid="stSelectbox"] span,
    div[data-testid="stSelectbox"] [role="combobox"],
    div[data-testid="stMultiSelect"] input,
    div[data-testid="stMultiSelect"] span {{
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
        background: transparent !important;
    }}

    /* Multiselect Tags */
    div[data-testid="stMultiSelect"] [data-tag],
    div[data-baseweb="tag"] {{
        background-color: var(--tag-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 9px !important;
    }}
    div[data-testid="stMultiSelect"] [data-tag] span,
    div[data-testid="stMultiSelect"] [data-tag] div,
    div[data-baseweb="tag"] span {{
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
    }}

    /* =========================================================
       DROPDOWN MENUS (Virtual & Portal Overlays)
       ========================================================= */
    div[data-testid="stSelectboxVirtualDropdown"],
    div[data-testid="stMultiSelectDropdown"],
    div[data-testid*="VirtualDropdown"],
    div[data-testid*="Dropdown"],
    ul[data-baseweb="menu"],
    div[data-baseweb="popover"],
    div[role="listbox"] {{
        background-color: var(--input-bg) !important;
        background: var(--input-bg) !important;
        border: 1.5px solid var(--border-color) !important;
        border-radius: 16px !important;
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.35) !important;
    }}

    /* Dropdown Items Default State */
    div[data-testid="stSelectboxVirtualDropdown"] [data-item-hl],
    div[data-testid="stSelectboxVirtualDropdown"] [role="option"],
    div[data-testid="stSelectboxVirtualDropdown"] span,
    div[data-testid="stMultiSelectDropdown"] [data-item-hl],
    div[data-testid="stMultiSelectDropdown"] [role="option"],
    div[data-testid="stMultiSelectDropdown"] span,
    div[data-testid*="VirtualDropdown"] *,
    li[data-baseweb="menu-item"],
    li[role="option"],
    div[role="listbox"] [role="option"],
    div[role="listbox"] span {{
        background-color: transparent !important;
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
    }}

    /* Dropdown Items Hover & Selected State */
    div[data-testid="stSelectboxVirtualDropdown"] [data-hovered] [data-item-hl],
    div[data-testid="stSelectboxVirtualDropdown"] [data-focused] [data-item-hl],
    div[data-testid="stSelectboxVirtualDropdown"] [aria-selected="true"] [data-item-hl],
    div[data-testid="stMultiSelectDropdown"] [data-hovered] [data-item-hl],
    div[data-testid="stMultiSelectDropdown"] [data-focused] [data-item-hl],
    div[data-testid="stMultiSelectDropdown"] [aria-selected="true"] [data-item-hl],
    li[data-baseweb="menu-item"]:hover,
    li[role="option"]:hover,
    li[aria-selected="true"] {{
        background-color: var(--tag-bg) !important;
        background: var(--tag-bg) !important;
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
    }}

    /* =========================================================
       SEGMENTED CONTROLS, PILLS & PROFILE SELECTORS
       ========================================================= */
    div[data-testid*="SegmentedControl"],
    div[data-testid*="segmented_control"],
    div[data-testid*="segmentedControl"],
    div[data-baseweb="segmented-control"],
    div[data-baseweb="button-group"],
    div[role="radiogroup"]:has(button) {{
        background-color: var(--input-bg) !important;
        background: var(--input-bg) !important;
        border: 1.5px solid var(--border-color) !important;
        border-radius: 16px !important;
        padding: 4px !important;
        gap: 4px !important;
    }}

    /* Reset all button backgrounds in Segmented Controls / Radiogroups */
    div[data-testid*="Segmented"] button,
    div[data-testid*="segmented"] button,
    div[data-baseweb="segmented-control"] button,
    div[data-baseweb="button-group"] button,
    div[role="radiogroup"] button,
    div[data-testid*="Segmented"] [data-testid*="stBaseButton"],
    div[data-testid*="segmented"] [data-testid*="stBaseButton"],
    div[role="radiogroup"] [data-testid*="stBaseButton"],
    div[data-testid*="Segmented"] [data-testid="stBaseButton-secondary"],
    div[data-testid*="segmented"] [data-testid="stBaseButton-secondary"],
    div[role="radiogroup"] [data-testid="stBaseButton-secondary"] {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        outline: none !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}

    /* Unselected button text & inner elements */
    div[data-testid*="Segmented"] button,
    div[data-testid*="Segmented"] button p,
    div[data-testid*="Segmented"] button span,
    div[data-testid*="Segmented"] button div,
    div[data-testid*="segmented"] button,
    div[data-testid*="segmented"] button p,
    div[data-testid*="segmented"] button span,
    div[data-baseweb="segmented-control"] button,
    div[data-baseweb="segmented-control"] button p,
    div[data-baseweb="segmented-control"] button span,
    div[data-baseweb="button-group"] button,
    div[data-baseweb="button-group"] button p,
    div[data-baseweb="button-group"] button span,
    div[role="radiogroup"] button,
    div[role="radiogroup"] button p,
    div[role="radiogroup"] button span,
    div[data-testid*="stBaseButton"] p,
    div[data-testid*="stBaseButton"] span {{
        color: var(--text-color) !important;
        -webkit-text-fill-color: var(--text-color) !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }}

    /* Hover State for Unselected Segments */
    div[data-testid*="Segmented"] button:not([aria-checked="true"]):not([aria-selected="true"]):hover,
    div[data-testid*="segmented"] button:not([aria-checked="true"]):not([aria-selected="true"]):hover,
    div[data-baseweb="segmented-control"] button:not([aria-checked="true"]):not([aria-selected="true"]):hover,
    div[data-baseweb="button-group"] button:not([aria-checked="true"]):not([aria-selected="true"]):hover,
    div[role="radiogroup"] button:not([aria-checked="true"]):not([aria-selected="true"]):hover {{
        background-color: var(--tag-bg) !important;
        background: var(--tag-bg) !important;
    }}

    /* ACTIVE / SELECTED Segment Button */
    div[data-testid*="Segmented"] button[aria-checked="true"],
    div[data-testid*="Segmented"] button[aria-selected="true"],
    div[data-testid*="Segmented"] button[data-state="active"],
    div[data-testid*="segmented"] button[aria-checked="true"],
    div[data-testid*="segmented"] button[aria-selected="true"],
    div[data-testid*="segmented"] button[data-state="active"],
    div[data-baseweb="segmented-control"] button[aria-checked="true"],
    div[data-baseweb="segmented-control"] button[aria-selected="true"],
    div[data-baseweb="button-group"] button[aria-checked="true"],
    div[data-baseweb="button-group"] button[aria-selected="true"],
    div[role="radiogroup"] button[aria-checked="true"],
    div[role="radiogroup"] button[aria-selected="true"],
    div[data-testid*="stBaseButton"][aria-checked="true"],
    div[data-testid*="stBaseButton"][aria-selected="true"] {{
        background-color: var(--button-bg) !important;
        background: var(--button-bg) !important;
        border: var(--button-border) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
    }}

    /* ACTIVE / SELECTED Text */
    div[data-testid*="Segmented"] button[aria-checked="true"] p,
    div[data-testid*="Segmented"] button[aria-checked="true"] span,
    div[data-testid*="Segmented"] button[aria-selected="true"] p,
    div[data-testid*="Segmented"] button[aria-selected="true"] span,
    div[data-testid*="segmented"] button[aria-checked="true"] p,
    div[data-testid*="segmented"] button[aria-checked="true"] span,
    div[data-testid*="segmented"] button[aria-selected="true"] p,
    div[data-testid*="segmented"] button[aria-selected="true"] span,
    div[data-baseweb="segmented-control"] button[aria-checked="true"] p,
    div[data-baseweb="segmented-control"] button[aria-checked="true"] span,
    div[data-baseweb="button-group"] button[aria-checked="true"] p,
    div[data-baseweb="button-group"] button[aria-checked="true"] span,
    div[role="radiogroup"] button[aria-checked="true"] p,
    div[role="radiogroup"] button[aria-checked="true"] span,
    div[role="radiogroup"] button[aria-selected="true"] p,
    div[role="radiogroup"] button[aria-selected="true"] span,
    div[data-testid*="stBaseButton"][aria-checked="true"] p,
    div[data-testid*="stBaseButton"][aria-checked="true"] span {{
        color: var(--button-text) !important;
        -webkit-text-fill-color: var(--button-text) !important;
        font-weight: 800 !important;
    }}

    /* Segmented Control Header Label */
    div[data-testid*="Segmented"] label,
    div[data-testid*="Segmented"] label p,
    div[data-testid*="segmented"] label,
    div[data-testid*="segmented"] label p {{
        color: var(--text-color) !important;
        -webkit-text-fill-color: var(--text-color) !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
    }}

    /* =========================================================
       PILLS & CHIPS (st.pills)
       ========================================================= */
    div[data-testid="stPills"] button,
    div[data-baseweb="pills"] button {{
        background-color: var(--input-bg) !important;
        border: 1.5px solid var(--border-color) !important;
        border-radius: 999px !important;
        color: var(--text-color) !important;
        -webkit-text-fill-color: var(--text-color) !important;
        font-weight: 700 !important;
    }}
    div[data-testid="stPills"] button[aria-checked="true"],
    div[data-testid="stPills"] button[aria-selected="true"] {{
        background-color: var(--accent-color) !important;
        background: var(--accent-color) !important;
        border-color: var(--accent-color) !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 800 !important;
    }}

    /* =========================================================
       RADIO BUTTON GROUPS (st.radio)
       ========================================================= */
    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] span {{
        color: var(--text-color) !important;
        -webkit-text-fill-color: var(--text-color) !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stRadio"] [role="radiogroup"] {{
        background-color: var(--input-bg) !important;
        border: 1.5px solid var(--border-color) !important;
        border-radius: 16px !important;
        padding: 8px 14px !important;
    }}

    /* =========================================================
       ACTION & PRIMARY BUTTONS ONLY (Clean Pill Cards)
       ========================================================= */
    div[data-testid="stButton"] > button,
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stDownloadButton"] > button,
    div[data-testid="stLinkButton"] > a,
    div[data-testid="stPopover"] > div button {{
        background-color: var(--button-bg) !important;
        background: var(--button-bg) !important;
        border: var(--button-border) !important;
        border-radius: 16px !important;
        color: var(--button-text) !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.35rem !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12) !important;
        outline: none !important;
    }}

    div[data-testid="stButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stDownloadButton"] > button:hover,
    div[data-testid="stPopover"] > div button:hover {{
        background-color: var(--button-hover) !important;
        background: var(--button-hover) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.22) !important;
    }}

    div[data-testid="stButton"] > button:active,
    div[data-testid="stFormSubmitButton"] > button:active,
    div[data-testid="stDownloadButton"] > button:active,
    div[data-testid="stPopover"] > div button:active {{
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15) !important;
    }}

    /* Action Button Text & Icon Formatting */
    div[data-testid="stButton"] > button p,
    div[data-testid="stButton"] > button span,
    div[data-testid="stFormSubmitButton"] > button p,
    div[data-testid="stFormSubmitButton"] > button span,
    div[data-testid="stDownloadButton"] > button p,
    div[data-testid="stDownloadButton"] > button span,
    div[data-testid="stPopover"] > div button p,
    div[data-testid="stPopover"] > div button span,
    div[data-testid="stLinkButton"] > a p,
    div[data-testid="stLinkButton"] > a span {{
        color: var(--button-text) !important;
        -webkit-text-fill-color: var(--button-text) !important;
        font-weight: 700 !important;
    }}
    div[data-testid="stButton"] > button svg,
    div[data-testid="stFormSubmitButton"] > button svg,
    div[data-testid="stDownloadButton"] > button svg,
    div[data-testid="stPopover"] > div button svg,
    div[data-testid="stLinkButton"] > a svg {{
        fill: var(--button-text) !important;
    }}

    /* =========================================================
       POPOVER DIALOG CONTENT
       ========================================================= */
    div[data-testid="stPopoverBody"],
    div[data-testid="stPopoverContent"] {{
        background-color: var(--container-bg) !important;
        border: 1.5px solid var(--border-color) !important;
        border-radius: 18px !important;
        color: var(--text-color) !important;
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.35) !important;
    }}
    div[data-testid="stPopoverBody"] p,
    div[data-testid="stPopoverBody"] span,
    div[data-testid="stPopoverBody"] label,
    div[data-testid="stPopoverContent"] p,
    div[data-testid="stPopoverContent"] span,
    div[data-testid="stPopoverContent"] label {{
        color: var(--text-color) !important;
    }}

    /* =========================================================
       WIDGET CONTROLS RESET (Steppers, Chevrons, Clear buttons)
       ========================================================= */
    div[data-testid="stSelectbox"] button,
    div[data-testid="stMultiSelect"] button,
    div[data-testid="stNumberInput"] button,
    div[data-baseweb="select"] button,
    div[data-baseweb="tag"] button {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        padding: 0 !important;
        margin: 0 !important;
        min-width: 0 !important;
        transform: none !important;
    }}
    div[data-testid="stSelectbox"] svg,
    div[data-testid="stMultiSelect"] svg,
    div[data-testid="stNumberInput"] svg,
    div[data-baseweb="select"] svg,
    div[data-baseweb="tag"] svg {{
        fill: var(--input-text) !important;
        stroke: none !important;
    }}
    """

    st.markdown(
        f"<style>\n{css}\n{morphism_css}\n{locked_sidebar_css}\n</style>",
        unsafe_allow_html=True
    )

def render_app_header(selected_user="Cris", coin_balance=0, streak_days=0, custom_emoji="☕", custom_title="Caffeine Fiend", active_perks=None):
    """Renders a sleek, native app top bar with greeting, Madrid time context, user pill, and coin/streak badges."""
    # Determine Madrid time of day
    try:
        madrid_now = datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=2)))
        hour = madrid_now.hour
    except Exception:
        hour = datetime.datetime.now().hour
        
    if 5 <= hour < 12:
        greeting_text = f"Good morning, {selected_user} ☀️"
        sub_text = "Time to brew your morning fuel!"
    elif 12 <= hour < 18:
        greeting_text = f"Good afternoon, {selected_user} ⚡"
        sub_text = "Powering through the workday slump."
    elif 18 <= hour < 23:
        greeting_text = f"Good evening, {selected_user} 🌙"
        sub_text = "Wind down or prepare the midnight oil."
    else:
        greeting_text = f"Burning Midnight Oil, {selected_user} 🦉"
        sub_text = "Late-night caffeine grinding session."

    html = f"""
    <div class="app-header-shell">
        <div class="app-header-greeting">
            <h2>{greeting_text}</h2>
            <span>{sub_text}</span>
        </div>
        <div class="app-header-badges">
            <div class="header-pill-badge" title="Active Streak">
                <span>🔥</span>
                <span>{streak_days}d Streak</span>
            </div>
            <div class="header-pill-badge" title="Coin Balance" style="border-color: var(--accent-color);">
                <span>🪙</span>
                <span>{coin_balance:,}</span>
            </div>
            <div class="header-pill-badge" title="Active Profile">
                <span>{custom_emoji}</span>
                <span class="user-highlight">{selected_user}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_daily_fact_quote():
    """Renders a standalone, responsive trivia quote banner placed cleanly outside the header card."""
    fact = randfacts.get_fact()
    html = f"""
    <div class="daily-fact-quote">
        <span style="font-size: 1.1rem; line-height: 1;">🧠</span>
        <div><strong>Daily Brew Trivia:</strong> <em>{fact}</em></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_circular_caffeine_gauge(caffeine_mg, max_mg=400):
    """Renders a circular SVG progress dial showing current caffeine velocity with an epic ON FIRE state over 400mg."""
    pct = min(max(caffeine_mg / max_mg, 0.0), 1.0)
    dash_array = 283  # 2 * pi * 45
    dash_offset = int(dash_array * (1.0 - pct))
    
    is_on_fire = caffeine_mg >= 400
    
    if caffeine_mg <= 95:
        stroke_color = "#06B6D4"  # Cyan
        status_label = "Warming Up 🏎️"
        sub_label = f"{int(pct*100)}% Speed &bull; {max_mg - caffeine_mg} mg to Ignition"
        glow_style = ""
    elif caffeine_mg <= 190:
        stroke_color = "#3B82F6"  # Electric Blue
        status_label = "Fast ⚡"
        sub_label = f"{int(pct*100)}% Speed &bull; Accelerating"
        glow_style = ""
    elif caffeine_mg <= 300:
        stroke_color = "#F59E0B"  # Amber / Gold
        status_label = "Faster 🚀"
        sub_label = f"{int(pct*100)}% Speed &bull; Mach 1 Velocity"
        glow_style = ""
    elif caffeine_mg < 400:
        stroke_color = "#FF5722"  # Flame Orange
        status_label = "Supersonic ⚡🔥"
        sub_label = f"{int(pct*100)}% Speed &bull; Approaching Redline!"
        glow_style = ""
    else:
        stroke_color = "#FF2200"  # Fiery Crimson Red
        status_label = "🔥 ON FIRE! 🌋💥"
        sub_label = "⚡ MAXIMUM COMBUSTION &bull; WARP SPEED! ⚡"
        glow_style = "filter: drop-shadow(0 0 12px rgba(255, 69, 0, 0.85)); animation: pulseFlame 1.5s infinite alternate;"

    html = f"""
    <style>
    @keyframes pulseFlame {{
        0% {{ filter: drop-shadow(0 0 8px rgba(255, 69, 0, 0.7)); }}
        100% {{ filter: drop-shadow(0 0 16px rgba(255, 34, 0, 0.95)); transform: scale(1.02); }}
    }}
    </style>
    <div style="display: flex; align-items: center; justify-content: space-around; padding: 0.5rem 0; {'border: 1px solid rgba(255, 69, 0, 0.4); border-radius: 12px; background: rgba(255, 69, 0, 0.06); padding: 0.75rem 0.5rem;' if is_on_fire else ''}">
        <div style="position: relative; width: 110px; height: 110px; flex-shrink: 0; {glow_style}">
            <svg width="110" height="110" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                <circle cx="50" cy="50" r="42" stroke="var(--border-color)" stroke-width="9" fill="none" opacity="0.4" />
                <circle cx="50" cy="50" r="42" stroke="{stroke_color}" stroke-width="9" stroke-linecap="round"
                    stroke-dasharray="{dash_array}" stroke-dashoffset="{dash_offset}" fill="none"
                    style="transition: stroke-dashoffset 0.8s ease-in-out;" />
            </svg>
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; transform: rotate(0deg);">
                <span style="font-size: 1.3rem; font-weight: 900; color: {'#FF3300' if is_on_fire else 'var(--text-color)'}; line-height: 1;">{caffeine_mg}</span>
                <span style="font-size: 0.68rem; color: var(--text-muted); font-weight: 700;">{'mg 🔥' if is_on_fire else f'mg / {max_mg}'}</span>
            </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <span style="font-size: 0.95rem; font-weight: 800; color: var(--text-color);">⚡ Velocity Meter</span>
            <span style="font-size: 0.95rem; font-weight: 800; color: {stroke_color}; text-shadow: {'0 0 8px rgba(255,69,0,0.5)' if is_on_fire else 'none'};">{status_label}</span>
            <span style="font-size: 0.78rem; font-weight: 600; color: {'#FF6600' if is_on_fire else 'var(--text-muted)'};">{sub_label}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_coffee_tea_fuel_bar(coffee_count, tea_count):
    """Renders a dual-colored split bar showing Coffee vs Tea proportion."""
    total = coffee_count + tea_count
    if total == 0:
        c_pct = 50
        t_pct = 50
    else:
        c_pct = int((coffee_count / total) * 100)
        t_pct = 100 - c_pct

    html = f"""
    <div style="padding: 0.5rem 0;">
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700; margin-bottom: 6px; color: var(--text-color);">
            <span>☕ Coffee: {coffee_count} ({c_pct}%)</span>
            <span>🍵 Tea: {tea_count} ({t_pct}%)</span>
        </div>
        <div style="display: flex; height: 14px; width: 100%; border-radius: 999px; overflow: hidden; background: var(--input-bg); border: 1px solid var(--border-color);">
            <div style="width: {c_pct}%; background: #D97706; transition: width 0.6s ease;"></div>
            <div style="width: {t_pct}%; background: #10B981; transition: width 0.6s ease;"></div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
