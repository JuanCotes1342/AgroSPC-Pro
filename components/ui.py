import streamlit as st


def apply_theme() -> None:
    st.session_state.setdefault("ui_theme", "Light")
    st.set_page_config(
        page_title="SPC Agroindustrial",
        page_icon="SPC",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    dark_css = """
        .stApp { background: linear-gradient(180deg, #071426 0%, #0f172a 100%); color:#e5eefb; }
        [data-testid="stSidebar"] { background:#0b1220; border-right:1px solid #1e293b; }
        [data-testid="stSidebar"] * { color:#dbeafe !important; }
        .brand-name { color:#f8fafc !important; }
        .side-section { color:#94a3b8 !important; }
        .side-card { background:#10233f; border-color:#1d4ed8; color:#dbeafe !important; }
        .kpi, .panel, div[data-testid="stMetric"] { background:#111c2f !important; border-color:#243653 !important; color:#e5eefb !important; }
        .kpi .value { color:#f8fafc; }
    """ if st.session_state.ui_theme == "Dark" else """
    """
    st.markdown(
        """
        <style>
        :root { --primary:#2f6f3e; --accent:#67b26f; --deep:#234f2c; --mint:#edf8ef; --card:#ffffff; --text:#132018; --line:#dbe8dd; }
        .stApp { background: linear-gradient(180deg, #f6fbf7 0%, #edf8ef 100%); color: var(--text); }
        [data-testid="stSidebar"] { background: #fbfdfb; border-right: 1px solid var(--line); }
        [data-testid="stSidebar"] * { color: #172033 !important; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { margin-bottom: .25rem; }
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] [data-testid="stRadio"] label { color:#64748b !important; font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; }
        [data-testid="stSidebar"] div[role="radiogroup"] label {
            border-radius: 10px; padding: .42rem .55rem; margin: .08rem 0;
            transition: background .15s ease, color .15s ease;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover { background:#eef2ff; }
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background:#e6e8ee; font-weight:700; }
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { color:#0b2545 !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label div:first-child { display:none; }
        [data-testid="stSidebar"] [data-testid="stSelectbox"] > div { background:white; border-radius:12px; }
        [data-testid="stSidebar"] .stButton > button {
            width:100%; justify-content:flex-start; border:0; border-radius:10px; padding:.65rem .75rem;
            background:transparent; color:#1e293b !important; font-weight:500; box-shadow:none;
            text-align:left;
        }
        [data-testid="stSidebar"] .stButton { width:100%; }
        [data-testid="stSidebar"] .stButton > button > div,
        [data-testid="stSidebar"] .stButton > button p { width:100%; text-align:left; justify-content:flex-start; margin:0; }
        [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stElementContainer"] { width:100%; }
        [data-testid="stSidebar"] .stButton > button:hover { background:#e8f4ea; color:#234f2c !important; border:0; }
        [data-testid="stSidebar"] .nav-active .stButton > button,
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background:#dfeee2 !important; color:#234f2c !important; font-weight:750; border:0;
        }
        .brand-row { display:flex; align-items:center; gap:.75rem; padding:.4rem 0 1rem; }
        .brand-logo { width:40px; height:40px; display:grid; place-items:center; border-radius:12px; background:linear-gradient(135deg,#2f6f3e,#67b26f); color:white !important; font-size:1.3rem; box-shadow:0 8px 20px rgba(47,111,62,.22); }
        .brand-name { font-size:1.25rem; font-weight:800; letter-spacing:-.03em; color:#0f172a !important; }
        .side-section { margin:.95rem 0 .35rem; color:#64748b !important; font-size:.78rem; text-transform:uppercase; letter-spacing:.09em; }
        .side-card { margin-top:1rem; padding:1rem; border-radius:14px; background:#eaf2ff; border:1px solid #dbeafe; color:#1e3a8a !important; line-height:1.45; }
        .catalog-shell { padding:1.25rem; border-radius:22px; background:#eef8ff; border:1px solid #dbeafe; }
        .catalog-hint { padding:1rem 1.15rem; border-radius:14px; background:#e8f4ff; border:1px solid #b9ddff; color:#17446d; margin-bottom:1.2rem; }
        .catalog-title { margin:1.2rem 0 .85rem; font-size:1.25rem; font-weight:850; color:#172033; }
        .product-card { min-height:138px; padding:1.1rem .8rem; border-radius:16px; background:white; border:1px solid #e8eef6; box-shadow:0 8px 22px rgba(15,76,129,.06); text-align:center; transition:transform .12s ease, box-shadow .12s ease; }
        .product-card:hover { transform:translateY(-2px); box-shadow:0 14px 30px rgba(15,76,129,.12); }
        .product-icon { width:58px; height:58px; margin:0 auto .75rem; display:grid; place-items:center; border-radius:50%; background:#dff3ff; font-size:1.65rem; }
        .product-name { font-weight:800; color:#172033; }
        .product-scientific { margin-top:.25rem; font-size:.76rem; color:#64748b; }
        .detail-panel { margin-top:1.25rem; padding:1.25rem; border-radius:22px; background:white; border:1px solid #e5edf7; box-shadow:0 14px 34px rgba(15,76,129,.08); }
        .detail-head { display:flex; align-items:center; gap:1rem; margin-bottom:1rem; }
        .detail-icon { width:72px; height:72px; display:grid; place-items:center; border-radius:22px; background:linear-gradient(135deg,#dff3ff,#eef7ff); font-size:2rem; }
        .detail-title { font-size:1.55rem; font-weight:900; color:#0b2545; margin:0; }
        .detail-subtitle { color:#64748b; margin-top:.15rem; }
        .detail-desc { padding:1rem; border-radius:16px; background:#f8fbff; border:1px solid #e5edf7; color:#334155; line-height:1.55; margin:.75rem 0 1rem; }
        .chip-wrap { display:flex; flex-wrap:wrap; gap:.55rem; margin:.6rem 0 1rem; }
        .quality-chip { padding:.52rem .72rem; border-radius:999px; background:#eef6ff; border:1px solid #cfe6ff; color:#17446d; font-weight:650; font-size:.88rem; }
        .mini-card-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.8rem; }
        .mini-card { padding:.85rem; border-radius:16px; background:#fbfdff; border:1px solid #e5edf7; }
        .mini-card strong { color:#0b2545; }
        .mini-card span { display:block; color:#64748b; font-size:.86rem; margin-top:.2rem; }
        @media (max-width: 900px) { .mini-card-grid { grid-template-columns:1fr; } }
        .home-shell { max-width:1180px; margin:0 auto; border-radius:22px; overflow:hidden; background:white; box-shadow:0 22px 58px rgba(21,75,34,.18); }
        .home-hero { min-height:430px; display:grid; place-items:center; text-align:center; color:white; background:linear-gradient(rgba(22,70,35,.45),rgba(22,70,35,.55)), url('https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=1600&q=80'); background-size:cover; background-position:center; padding:3rem 2rem; }
        .home-hero h1 { font-size:3.25rem; line-height:1.05; margin:0; text-shadow:0 4px 18px rgba(0,0,0,.35); }
        .home-hero p { max-width:680px; margin:1rem auto 1.5rem; font-size:1.1rem; }
        .home-actions { display:flex; justify-content:center; gap:1rem; flex-wrap:wrap; }
        .home-btn { min-width:190px; padding:.82rem 1.35rem; border-radius:10px; border:1px solid rgba(255,255,255,.9); font-weight:800; color:#102033; background:white; text-decoration:none !important; display:inline-block; box-shadow:0 10px 26px rgba(0,0,0,.16); }
        .home-btn.primary { background:#ff4b4b; border-color:#ff4b4b; color:white; }
        .learn-card { max-width:980px; margin:1.2rem auto 0; padding:1.35rem; border-radius:18px; background:white; border:1px solid #dfe7df; box-shadow:0 16px 38px rgba(21,75,34,.12); }
        .learn-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.9rem; margin-top:1rem; }
        .learn-item { padding:1rem; border-radius:14px; background:#f7fbf7; border:1px solid #dfeee2; }
        .learn-item b { color:#234f2c; }
        .benefits { padding:2.4rem 2rem; text-align:center; }
        .benefit-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; max-width:900px; margin:1.3rem auto 0; text-align:left; }
        .benefit-card { padding:1.1rem; border:1px solid #dfe7df; border-radius:14px; box-shadow:0 10px 26px rgba(0,0,0,.08); background:white; }
        .benefit-icon { width:44px; height:44px; display:grid; place-items:center; background:#e1f0df; border-radius:10px; font-size:1.4rem; margin-bottom:.6rem; }
        .hero { padding: 1.45rem 1.65rem; border-radius: 22px; background: linear-gradient(135deg,#234f2c,#2f6f3e 55%,#67b26f); color: white; box-shadow: 0 16px 40px rgba(47,111,62,.20); margin-bottom:1.15rem; }
        .hero h1 { margin:0; font-size:2rem; letter-spacing:-.03em; }
        .hero p { margin:.35rem 0 0; color:#dbeafe; }
        .kpi { min-height:126px; padding: 1.05rem 1.15rem; border-radius: 18px; background: var(--card); border: 1px solid #e5edf7; box-shadow: 0 10px 28px rgba(15,76,129,.08); display:flex; flex-direction:column; justify-content:space-between; }
        .kpi .label { font-size:.82rem; color:#64748b; text-transform:uppercase; letter-spacing:.06em; }
        .kpi .value { font-size:1.75rem; font-weight:750; color:#0b2545; margin-top:.2rem; }
        .health-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.8rem; margin:1rem 0; }
        .health-card { padding:1rem; border-radius:14px; color:#10170f; min-height:112px; box-shadow:0 8px 22px rgba(27,86,42,.08); border:1px solid rgba(0,0,0,.05); }
        .health-card.good { background:linear-gradient(135deg,#73d58b,#b8efc3); }
        .health-card.warn { background:linear-gradient(135deg,#ffe071,#fff0a3); }
        .health-card.bad { background:linear-gradient(135deg,#ff9b9b,#ffd3d3); }
        .health-label { font-weight:800; font-size:1rem; }
        .health-value { font-size:1.8rem; font-weight:900; margin:.25rem 0; }
        .health-note { font-size:.86rem; }
        .panel { padding: 1rem; border-radius: 18px; background:white; border:1px solid #e5edf7; box-shadow: 0 8px 24px rgba(15,76,129,.06); }
        .page-top { display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; margin:.25rem 0 1.4rem; }
        .page-top h2 { margin:0; color:#172033; font-size:1.45rem; font-weight:900; letter-spacing:-.02em; }
        .page-top p { margin:.25rem 0 0; color:#64748b; font-size:.9rem; }
        .page-actions { display:flex; gap:.55rem; align-items:center; }
        .topbar-chip { padding:.55rem .85rem; border-radius:10px; background:white; border:1px solid #dfe7df; color:#234f2c !important; font-weight:750; box-shadow:0 8px 18px rgba(47,111,62,.08); text-decoration:none !important; }
        .soft-page { padding:1rem; border-radius:22px; background:#eef8f3; border:1px solid #dff1e8; }
        .form-card { padding:1.1rem; border-radius:18px; background:white; border:1px solid #e5edf7; box-shadow:0 10px 28px rgba(15,76,129,.06); margin-bottom:1rem; }
        .info-strip { padding:.85rem 1rem; border-radius:12px; background:#dbeafe; border:1px solid #bfdbfe; color:#17446d; margin:.8rem 0 1rem; }
        .chart-panel { padding:1rem; border-radius:18px; background:white; border:1px solid #dfeaf4; box-shadow:0 10px 26px rgba(15,76,129,.06); margin:1rem 0; }
        div[data-baseweb="tab-list"] { gap:.4rem; background:white; border-radius:16px; padding:.45rem; border:1px solid #e5edf7; }
        button[data-baseweb="tab"] { border-radius:10px; padding:.55rem .85rem; }
        button[data-baseweb="tab"][aria-selected="true"] { background:#0f8f72; color:white; }
        .context-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.85rem; margin:1rem 0; }
        .context-item { padding:.9rem 1rem; border-radius:16px; background:white; border:1px solid #e5edf7; box-shadow:0 8px 20px rgba(15,76,129,.05); }
        .context-label { color:#64748b; font-size:.76rem; text-transform:uppercase; letter-spacing:.07em; margin-bottom:.25rem; }
        .context-value { color:#0b2545; font-weight:800; }
        .ishikawa-grid { display:grid; grid-template-columns:1fr 1fr; gap:1rem; }
        .cause-card { padding:.9rem; border-radius:14px; border:1px solid #dfe7df; background:#fbfdfb; }
        @media (max-width: 900px) { .context-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } .benefit-grid,.health-grid,.ishikawa-grid,.learn-grid { grid-template-columns:1fr; } }
        .alert-ok { border-left: 5px solid #10b981; padding:.75rem; background:#ecfdf5; border-radius:12px; }
        .alert-bad { border-left: 5px solid #ef4444; padding:.75rem; background:#fef2f2; border-radius:12px; }
        .small-muted { color:#64748b; font-size:.9rem; }
        div[data-testid="stMetric"] { background:white; border:1px solid #e5edf7; border-radius:16px; padding:1rem; }
        __DARK_CSS__
        </style>
        """.replace("__DARK_CSS__", dark_css),
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(f"<div class='hero'><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class='page-top'>
            <div><h2>{title}</h2><p>{subtitle}</p></div>
            <div class='page-actions'><a class='topbar-chip' href='?go=data_entry' target='_self'>+ Nuevo Registro</a><a class='topbar-chip' href='?go=export' target='_self'>⬇ Exportar</a></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, help_text: str = "") -> None:
    st.markdown(
        f"<div class='kpi'><div class='label'>{label}</div><div class='value'>{value}</div><div class='small-muted'>{help_text}</div></div>",
        unsafe_allow_html=True,
    )


def status_box(ok: bool, text: str) -> None:
    klass = "alert-ok" if ok else "alert-bad"
    st.markdown(f"<div class='{klass}'>{text}</div>", unsafe_allow_html=True)
