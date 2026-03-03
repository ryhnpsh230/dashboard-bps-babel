import streamlit as st
import pandas as pd
import re
import io
import requests
import datetime
import os
import time
from urllib.parse import urlparse

def section_header(title: str, subtitle: str = "", badge: str = "MODULE"):
    """Premium section header (international look)."""
    st.markdown(
        f"""
<div class="bps-section">
  <div class="left">
    <div class="bps-badge">{badge}</div>
    <h2 class="bps-h">{title}</h2>
    {f'<p class="bps-sub">{subtitle}</p>' if subtitle else ''}
    <div class="bps-divider"></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def goto_menu(label: str):
    """Jump navigation safely (cannot mutate widget state after creation)."""
    st.session_state["nav_target"] = label
    st.session_state["show_sidebar"] = True
    st.rerun()


import plotly.express as px

import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium


# ======================================================================================
# CONFIG
# ======================================================================================
APP_TITLE = "Dashboard UMKM BPS"
APP_ICON = "🏛️"

BPS_OREN_UTAMA = "#FF6F00"
BPS_AMBER = "#FFC107"
BPS_DARK = "#0b0b0c"
BPS_PAPER = "rgba(0,0,0,0)"

BPS_PALETTE = ["#FF6F00", "#FFA000", "#FFB300", "#FFC107", "#263238", "#37474F", "#455A64"]

BABEL_KEYS = [
    "pangkal", "bangka", "belitung", "sungailiat", "mentok", "muntok",
    "koba", "toboali", "manggar", "tanjung pandan", "tanjungpandan"
]

PLACEHOLDER = "Pemilik tidak mencantumkan"
PHONE_EMPTY = "Pemilik belum meletakkan nomor"


# ======================================================================================
# PAGE SETUP
# ======================================================================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = BPS_PALETTE


# ======================================================================================
# THEME / CSS (Orange-heavy modern glass)
# ======================================================================================
# ======================================================================================
# THEME / CSS (Original + Polished Add-ons)
# ======================================================================================
CSS_THEME = r"""@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap");

/* ===================== BPS UMKM — LIGHT ORANGE THEME ===================== */
:root{
  --bg: #ffffff;
  --bg2: #fff7ed;          /* orange-50 */
  --card: #ffffff;
  --card2: #fff7ed;
  --stroke: rgba(15,23,42,.10);
  --stroke2: rgba(249,115,22,.25);
  --text: #0f172a;         /* slate-900 */
  --muted: #475569;        /* slate-600 */
  --orange: #f97316;       /* orange-500 */
  --orange2:#fb923c;       /* orange-400 */
  --amber: #f59e0b;        /* amber-500 */
  --shadow: 0 10px 30px rgba(15,23,42,.08);
  --shadow2: 0 18px 40px rgba(249,115,22,.14);
}

/* App background */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"]{
  background:
    radial-gradient(1200px 700px at 8% 10%, rgba(249,115,22,.14) 0%, rgba(249,115,22,0) 60%),
    radial-gradient(900px 650px at 92% 18%, rgba(245,158,11,.14) 0%, rgba(245,158,11,0) 58%),
    linear-gradient(180deg, var(--bg) 0%, var(--bg2) 100%) !important;
  background-attachment: fixed !important;
  color: var(--text) !important;
}

[data-testid="stHeader"]{ background: rgba(0,0,0,0) !important; }

/* Page padding + top accent bar */
.block-container{ padding-top: 1.0rem; padding-bottom: 2.0rem; max-width: 1180px; }
.block-container::before{
  content:"";
  display:block;
  height: 6px;
  width: 100%;
  border-radius: 999px;
  margin-bottom: 14px;
  background: linear-gradient(90deg,
    rgba(249,115,22,0) 0%,
    rgba(249,115,22,.85) 28%,
    rgba(245,158,11,.85) 56%,
    rgba(249,115,22,.85) 80%,
    rgba(249,115,22,0) 100%);
  box-shadow: 0 10px 28px rgba(249,115,22,.18);
}

/* Sidebar (force light) */
[data-testid="stSidebar"]{
  background: linear-gradient(180deg, #ffffff 0%, #fff7ed 100%) !important;
  border-right: 1px solid var(--stroke) !important;
  box-shadow: 10px 0 30px rgba(15,23,42,.06);
}
[data-testid="stSidebar"] *{ color: var(--text) !important; }
[data-testid="stSidebar"] .stButton>button{
  width: 100%;
  border-radius: 12px !important;
  border: 1px solid var(--stroke) !important;
  background: #ffffff !important;
  box-shadow: 0 8px 20px rgba(15,23,42,.06) !important;
}
[data-testid="stSidebar"] .stButton>button:hover{
  border-color: var(--stroke2) !important;
  box-shadow: 0 14px 30px rgba(249,115,22,.14) !important;
}

/* Inputs readability */
.stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div, .stMultiSelect div[data-baseweb="select"] > div,
.stFileUploader section{
  background: #ffffff !important;
  color: var(--text) !important;
  border: 1px solid var(--stroke) !important;
  border-radius: 12px !important;
}

/* Buttons */
.stButton>button{
  border-radius: 14px !important;
  border: 1px solid rgba(249,115,22,.35) !important;
  background: linear-gradient(90deg, var(--orange) 0%, var(--amber) 100%) !important;
  color: #111827 !important;
  font-weight: 800 !important;
  box-shadow: var(--shadow2) !important;
}
.stButton>button:hover{
  transform: translateY(-1px);
  filter: brightness(1.02);
}

/* Typography */
h1,h2,h3,h4,h5,h6, p, span, label, div{ font-family: "Inter", system-ui, -apple-system, Segoe UI, Roboto, Arial; }
.bps-h, .bps-section h2, .bps-section h1{ color: var(--text) !important; }
.bps-sub{ color: var(--muted) !important; }

/* Cards */
.bps-card, .bps-hero, .bps-panel{
  background: var(--card) !important;
  border: 1px solid var(--stroke) !important;
  border-radius: 18px !important;
  box-shadow: var(--shadow) !important;
}
.bps-hero{
  border: 1px solid rgba(249,115,22,.25) !important;
  background: linear-gradient(90deg, rgba(249,115,22,.18) 0%, rgba(245,158,11,.12) 60%, rgba(255,255,255,.92) 100%) !important;
}
.bps-badge{
  display:inline-flex;
  gap:.45rem;
  align-items:center;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: .12em;
  color: #7c2d12;
  background: rgba(249,115,22,.18);
  border: 1px solid rgba(249,115,22,.30);
}

/* Fix markdown blocks inside containers */
[data-testid="stMarkdownContainer"] p{ color: var(--text); }
[data-testid="stMarkdownContainer"] small, [data-testid="stMarkdownContainer"] li{ color: var(--muted); }

/* Alerts */
.stAlert > div{
  border-radius: 14px !important;
  border: 1px solid var(--stroke) !important;
  box-shadow: 0 10px 25px rgba(15,23,42,.06) !important;
}
"""

# Inject BPS accent tokens safely (no f-string CSS parsing issues)
CSS_THEME = (CSS_THEME
    .replace("__BPS_OREN__", BPS_OREN_UTAMA)
    .replace("__BPS_AMBER__", BPS_AMBER)
)

EXTRA_CSS = """
/* Dashboard quick-nav buttons */
.bps-hero + div .stButton > button{
  background: linear-gradient(135deg, rgba(255,111,0,.95) 0%, rgba(255,193,7,.88) 100%) !important;
}
.bps-hero + div button[kind="secondary"],
.bps-hero + div .stButton > button:disabled{
  background: rgba(255,255,255,.08) !important;
}
"""

st.markdown("<style>\n" + CSS_THEME + "\n" + EXTRA_CSS + "\n</style>", unsafe_allow_html=True)

# Header row with logo (if exists)
cols = st.columns([0.55, 2.2])
with cols[0]:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
with cols[1]:
    st.markdown('<div class="splash-kicker">BPS BABEL • DASHBOARD UMKM</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="splash-title">{APP_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="splash-sub">Menyiapkan tampilan, memuat modul, dan mengoptimalkan pengalaman penggunaan…</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="splash-row">', unsafe_allow_html=True)
st.markdown('<div class="splash-pill">UI Modern</div>', unsafe_allow_html=True)
st.markdown('<div class="splash-pill">Navigasi Cepat</div>', unsafe_allow_html=True)
st.markdown('<div class="splash-pill">Akurat & Rapi</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

prog = st.progress(0)
status = st.empty()

# Fast, smooth progression (no heavy work; just UX)
for i in range(0, 101, 4):
    prog.progress(i)
    if i < 30:
        status.caption("Menginisialisasi komponen…")
    elif i < 70:
        status.caption("Menyiapkan modul marketplace…")
    else:
        status.caption("Hampir selesai…")
    time.sleep(0.02)

st.markdown("</div>", unsafe_allow_html=True)

# Mark loaded and rerun to enter the main app
st.session_state["__splash_done__"] = True
st.rerun()


if "__splash_done__" not in st.session_state:
    st.session_state["__splash_done__"] = False

if not st.session_state["__splash_done__"]:
    splash_screen()


# ======================================================================================
# SIDEBAR (hidden on Dashboard)
# ======================================================================================
# --- Navigation state (safe) ---
if "__boot__" not in st.session_state:
    # always start clean: Dashboard without sidebar
    st.session_state["__boot__"] = True
    st.session_state["show_sidebar"] = False
    st.session_state["menu_nav"] = "🏠 Dashboard"
    st.session_state["nav_target"] = None

if "show_sidebar" not in st.session_state:
    st.session_state["show_sidebar"] = False  # start without sidebar on Dashboard
if "menu_nav" not in st.session_state:
    st.session_state["menu_nav"] = "🏠 Dashboard"

# Apply pending navigation target BEFORE widget creation
if st.session_state.get("nav_target"):
    st.session_state["menu_nav"] = st.session_state["nav_target"]
    st.session_state["nav_target"] = None

# If we're on Dashboard, force-hide sidebar (even if previous run left it on)
if st.session_state.get("menu_nav") == "🏠 Dashboard" and not st.session_state.get("nav_target"):
    st.session_state["show_sidebar"] = False

# Ensure widget value is valid when sidebar is shown
if st.session_state.get("show_sidebar") and st.session_state.get("menu_nav") == "🏠 Dashboard":
    st.session_state["menu_nav"] = "🟠 Shopee"



menu = "🏠 Dashboard"

if st.session_state["show_sidebar"]:
    with st.sidebar:
        st.markdown(f"### {APP_ICON} {APP_TITLE}")
        st.caption("Penyedia Data Statistik Berkualitas untuk Indonesia Maju")
        st.divider()

        # Premium "Back to Dashboard"
        if st.button("⬅️ Kembali ke Dashboard", key="btn_home", use_container_width=True, type="secondary"):
            st.session_state["show_sidebar"] = False
            st.session_state["menu_nav"] = "🏠 Dashboard"
            st.rerun()

        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)

        menu = st.radio(
            "🧭 Navigasi",
            ["🟠 Shopee", "🟢 Tokopedia", "📍 Google Maps", "📊 Export Gabungan"],
            index=0,
            key="menu_nav",
        )

        st.divider()
        with st.expander("⚙️ Pengaturan Umum", expanded=False):
            st.checkbox("Tampilkan tips cepat", value=True, key="show_tips")
            st.checkbox("Mode cepat (kurangi rendering chart besar)", value=False, key="fast_mode")

# Hide sidebar visually when not used (Dashboard mode)
if not st.session_state.get("show_sidebar", False):
    st.markdown(
        "<style>[data-testid='stSidebar']{display:none !important;} section.main{margin-left:0 !important;}</style>",
        unsafe_allow_html=True,
    )

# ======================================================================================
# PAGE: DASHBOARD (Before entering UMKM modules)
# ======================================================================================
if menu == "🏠 Dashboard":
    # Always hide sidebar on Dashboard
    st.session_state["show_sidebar"] = False

    section_header("Dashboard Utama", "Ringkasan status data & akses cepat ke modul UMKM.", "DASHBOARD")
    banner("Dashboard Utama", "Mulai dari ringkasan cepat, lalu masuk ke modul UMKM yang kamu butuhkan.")

    # Hero / quick actions
    st.markdown(
        """
<div class="bps-hero">
  <div>
    <div class="bps-badge">UMKM • BPS BABEL</div>
    <h1>Kontrol Pusat Analisis UMKM</h1>
    <p>Upload data dari marketplace / maps, cek ringkasan, lalu lanjutkan analisis.</p>
    <div class="cta-row">
      <span class="bps-chip">🟠 Shopee</span>
      <span class="bps-chip">🟢 Tokopedia</span>
      <span class="bps-chip">🔵 </span>
      <span class="bps-chip">📍 Google Maps</span>
      <span class="bps-chip">📊 Export</span>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Data readiness
    df_shp = st.session_state.data_shopee
    df_tkp = st.session_state.data_tokped
    df_maps = st.session_state.data_maps

    shp_n = 0 if df_shp is None else len(df_shp)
    tkp_n = 0 if df_tkp is None else len(df_tkp)
    mp_n  = 0 if df_maps is None else len(df_maps)


    
    # Premium KPI cards (less "kaku" than st.metric)
    st.markdown(
        f"""
<style>
.kpi-grid{{
  display:grid;
  grid-template-columns: repeat(5, minmax(0,1fr));
  gap: 14px;
  margin-top: 6px;
}}
@media (max-width: 1200px){{
  .kpi-grid{{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
}}
.kpi-card{{
  border-radius: 18px;
  border: 1px solid rgba(255,200,120,0.18);
  background: linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.035));
  box-shadow: 0 18px 60px rgba(0,0,0,0.34);
  padding: 14px 14px;
  backdrop-filter: blur(16px);
  position: relative;
  overflow: hidden;
}}
.kpi-card::before{{
  content:"";
  position:absolute; inset:-2px;
  background: radial-gradient(700px 240px at 10% 10%, rgba(255,140,40,0.26), rgba(255,140,40,0));
  opacity:.9;
  pointer-events:none;
}}
.kpi-top{{
  display:flex; align-items:center; justify-content:space-between;
  position: relative;
}}
.kpi-label{{
  font-weight: 800;
  letter-spacing: .2px;
  color: rgba(255,255,255,0.78);
  font-size: .92rem;
}}
.kpi-ico{{
  width: 34px; height: 34px;
  border-radius: 12px;
  display:flex; align-items:center; justify-content:center;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
}}
.kpi-val{{
  position: relative;
  margin-top: 10px;
  font-size: 2.05rem;
  font-weight: 950;
  letter-spacing: -0.03em;
  color: rgba(255,255,255,0.96);
}}
.kpi-sub{{
  position: relative;
  margin-top: 2px;
  color: rgba(255,255,255,0.62);
  font-size: .86rem;
}}
.kpi-accent{{
  position:absolute; left:0; top:0; bottom:0;
  width: 6px;
  background: linear-gradient(180deg, rgba(255,120,0,0.95), rgba(255,210,140,0.65));
}}
</style>

<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-top">
      <div class="kpi-label">📦 Total Data</div>
      <div class="kpi-ico">⚡</div>
    </div>
    <div class="kpi-val">{fmt_int_id(total_all)}</div>
    <div class="kpi-sub">Akumulasi semua sumber</div>
  </div>

  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-top">
      <div class="kpi-label">🟠 Shopee</div>
      <div class="kpi-ico">🛒</div>
    </div>
    <div class="kpi-val">{fmt_int_id(shp_n)}</div>
    <div class="kpi-sub">Siap diproses</div>
  </div>

  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-top">
      <div class="kpi-label">🟢 Tokopedia</div>
      <div class="kpi-ico">🧾</div>
    </div>
    <div class="kpi-val">{fmt_int_id(tkp_n)}</div>
    <div class="kpi-sub">Siap diproses</div>
  </div>

  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-top">
      <div class="kpi-label">🔵 </div>
      <div class="kpi-ico">💬</div>
    </div>
    <div class="kpi-sub">Siap diproses</div>
  </div>

  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-top">
      <div class="kpi-label">📍 Google Maps</div>
      <div class="kpi-ico">🧭</div>
    </div>
    <div class="kpi-val">{fmt_int_id(mp_n)}</div>
    <div class="kpi-sub">Siap divisualisasi</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.subheader("🚦 Status Modul")
        s1, s2 = st.columns([1.1, 0.9], gap="large")

        def _pill(ok: bool, text: str):
            cls = "ok" if ok else "no"
            icon = "✅" if ok else "⏳"
            return f'<span class="dash-pill {cls}">{icon} {text}</span>'

        st.markdown(
            """
<style>
/* Dashboard pills */
.dash-pill{
  display:inline-flex; align-items:center; gap:8px;
  padding: 10px 12px;
  border-radius: 999px;
  margin: 6px 10px 0 0;
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.05);
  font-weight: 800;
}
.dash-pill.ok{
  border-color: rgba(255,193,7,.32);
  background: linear-gradient(135deg, rgba(255,111,0,.26), rgba(255,193,7,.10));
  box-shadow: 0 18px 50px rgba(255,111,0,.10);
}
.dash-pill.no{
  opacity: .82;
}
</style>
""",
            unsafe_allow_html=True,
        )

        with s1:
            st.markdown(
                _pill(shp_n > 0, "Shopee siap dianalisis") +
                _pill(tkp_n > 0, "Tokopedia siap dianalisis") +
                _pill(mp_n > 0, "Google Maps siap divisualisasi"),
                unsafe_allow_html=True,
            )
            st.caption("Tip: Mulai dari modul yang datanya sudah siap. Setelah itu gunakan Export Gabungan untuk konsolidasi.")
        with s2:
            st.subheader("🧭 Navigasi Cepat")

            st.markdown("Klik tombol di bawah untuk mulai mengelola data UMKM. Sidebar akan muncul otomatis.")
            if st.button("🚀 Ayo Upload Data", use_container_width=True):
                goto_menu("🟠 Shopee")



    # Recommendations / tips area
    with st.container(border=True):
        st.subheader("✨ Rekomendasi Cepat")
        t1, t2 = st.columns(2, gap="large")
        with t1:
            st.success("**Workflow ideal:** Upload → Filter → Dashboard Eksekutif → Export.")
            st.write("• Pakai **Mode cepat** kalau file sangat besar.\n• Naikkan **jeda request** API Shopee kalau kena rate limit.")
        with t2:
            st.warning("**Catatan kualitas data:**")
            st.write("• Pastikan kolom lokasi/wilayah benar.\n• Untuk Google Maps, pastikan **lat/lon** valid.\n• Link/telepon kosong akan otomatis dibersihkan.")



# ======================================================================================
# PAGE: SHOPEE
# ======================================================================================
elif menu == "🟠 Shopee":
    section_header("Shopee Marketplace", "Analisis & ekstraksi data UMKM Shopee.", "MARKETPLACE")
    banner("Dashboard UMKM — Shopee", "Ekstraksi data UMKM dari Shopee Marketplace (Bangka Belitung)")

    with st.container(border=True):
        left, right = st.columns([1.2, 1.0], gap="large")

        with left:
            st.subheader("📥 Input Data")
            files = st.file_uploader("Unggah CSV Shopee", type=["csv"], accept_multiple_files=True, key="file_shp")

            mode_api = st.toggle(
                "🔎 Deteksi Nama Toko via API Shopee",
                value=True,
                help="Jika ON: sistem akan mencoba mengambil nama toko dari API shopid di link produk.",
                key="api_shp",
            )

            colA, colB, colC = st.columns(3)
            with colA:
                api_timeout = st.number_input("Timeout API (detik)", min_value=1, max_value=10, value=2, step=1)
            with colB:
                api_sleep = st.number_input("Jeda per request (detik)", min_value=0.0, max_value=2.0, value=0.0, step=0.1)
            with colC:
                max_api_calls = st.number_input("Maks panggilan API", min_value=0, max_value=50000, value=8000, step=500)

            st.caption("Tips: kalau scraping kamu “terdeteksi robot”, coba naikkan jeda request.")
            run = st.button("🚀 Proses Data Shopee", type="primary", use_container_width=True)

        with right:
            st.subheader("🧾 Ringkasan & Aturan")
            st.info(
                "• Data otomatis difilter **Bangka Belitung**.\n"
                "• Harga dibersihkan jadi integer.\n"
                "• Tipe Usaha dihitung pakai heuristik (kata kunci nama toko)."
            )
            if st.session_state.get("show_tips"):
                st.success("Kalau CSV beda struktur, sistem akan coba tebak kolom link/nama/harga/wilayah.")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Shopee terlebih dahulu.")
        else:
            with st.status("Memproses data Shopee…", expanded=True) as status:
                try:
                    total_semua_baris = 0
                    for f in files:
                        df_temp = pd.read_csv(f, dtype=str, on_bad_lines="skip")
                        total_semua_baris += len(df_temp)
                        f.seek(0)

                    hasil = []
                    total_baris = 0
                    err_h = 0
                    luar_wilayah = 0

                    progress = st.progress(0)
                    info = st.empty()
                    baris_diproses = 0
                    api_calls = 0

                    for file in files:
                        df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                        total_baris += len(df_raw)

                        if "Link" in df_raw.columns and "Nama Produk" in df_raw.columns:
                            col_link = "Link"
                            col_nama = "Nama Produk"
                            col_harga = "Harga"
                            col_wilayah = "Wilayah"
                        else:
                            col_link = next((c for c in df_raw.columns if "href" in c.lower()), df_raw.columns[0])
                            col_nama = next((c for c in df_raw.columns if "whitespace-normal" in c.lower()),
                                            df_raw.columns[min(3, len(df_raw.columns)-1)])
                            col_harga = next((c for c in df_raw.columns if "font-medium" in c.lower()),
                                             df_raw.columns[min(4, len(df_raw.columns)-1)])
                            idx_wilayah = 7 if len(df_raw.columns) > 7 else len(df_raw.columns) - 1
                            col_wilayah = next((c for c in df_raw.columns if "ml-[3px]" in c.lower()),
                                               df_raw.columns[idx_wilayah])

                        for i in range(len(df_raw)):
                            row = df_raw.iloc[i]
                            link = str(row.get(col_link, ""))
                            nama_produk = str(row.get(col_nama, ""))
                            harga_str = str(row.get(col_harga, ""))
                            lokasi = safe_title(str(row.get(col_wilayah, "")))

                            if not is_in_babel(lokasi):
                                luar_wilayah += 1
                                baris_diproses += 1
                                continue

                            try:
                                harga_bersih = harga_str.replace(".", "").replace(",", "")
                                angka_list = re.findall(r"\d+", harga_bersih)
                                val_h = int(angka_list[0]) if angka_list else 0
                                if val_h > 1_000_000_000:
                                    val_h = 0
                            except Exception:
                                val_h = 0
                                err_h += 1

                            toko = "Tidak Dilacak"
                            if mode_api and api_calls < int(max_api_calls):
                                match = re.search(r"i\.(\d+)\.", link)
                                if match:
                                    try:
                                        api_calls += 1
                                        res = requests.get(
                                            f"https://shopee.co.id/api/v4/shop/get_shop_base?shopid={match.group(1)}",
                                            headers={"User-Agent": "Mozilla/5.0"},
                                            timeout=float(api_timeout),
                                        )
                                        if res.status_code == 200:
                                            toko = res.json().get("data", {}).get("name", "Anonim")
                                    except Exception:
                                        pass
                                    if api_sleep and api_sleep > 0:
                                        time.sleep(float(api_sleep))

                            tipe_usaha = deteksi_tipe_usaha(toko)
                            hasil.append({
                                "Nama Toko": toko,
                                "Nama Produk": nama_produk,
                                "Harga": val_h,
                                "Wilayah": lokasi,
                                "Tipe Usaha": tipe_usaha,
                                "Link": link,
                            })

                            baris_diproses += 1
                            if baris_diproses % 25 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses / max(total_semua_baris, 1), 1.0)
                                progress.progress(pct)
                                info.markdown(
                                    f"**⏳ Progress:** {fmt_int_id(baris_diproses)} / {fmt_int_id(total_semua_baris)} "
                                    f"({int(pct*100)}%) • API calls: {fmt_int_id(api_calls)}"
                                )

                    progress.empty()
                    info.empty()

                    df = pd.DataFrame(hasil)
                    st.session_state.data_shopee = df
                    st.session_state.audit_shopee = {
                        "file_count": len(files),
                        "total_rows": total_baris,
                        "valid_rows": len(df),
                        "luar_wilayah": luar_wilayah,
                        "error_harga": err_h,
                        "api_calls": api_calls,
                    }

                    status.update(label="✅ Selesai memproses Shopee", state="complete", expanded=False)
                    st.toast(f"Shopee: {fmt_int_id(len(df))} baris siap dianalisis", icon="✅")

                except Exception as e:
                    status.update(label="❌ Gagal memproses Shopee", state="error", expanded=True)
                    st.error(f"Error Sistem Shopee: {e}")

    df_shp = st.session_state.data_shopee
    if df_shp is not None and not df_shp.empty:
        with st.container(border=True):
            st.subheader("🔎 Filter Pintar")
            c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.6, 1.2], gap="medium")
            with c1:
                f_wil = st.multiselect("📍 Wilayah", options=sorted(df_shp["Wilayah"].unique()),
                                       default=sorted(df_shp["Wilayah"].unique()), key="f_wil_shp")
            with c2:
                f_tipe = st.multiselect("🏢 Tipe Usaha", options=sorted(df_shp["Tipe Usaha"].unique()),
                                        default=sorted(df_shp["Tipe Usaha"].unique()), key="f_tipe_shp")
            with c3:
                q = st.text_input("🔎 Cari (nama toko / produk)", value="", key="q_shp")
            with c4:
                max_h = int(df_shp["Harga"].max()) if df_shp["Harga"].max() > 0 else 1_000_000
                f_hrg = st.slider("💰 Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_shp")

        df_f = df_shp[
            df_shp["Wilayah"].isin(f_wil)
            & df_shp["Tipe Usaha"].isin(f_tipe)
            & (df_shp["Harga"] >= f_hrg[0])
            & (df_shp["Harga"] <= f_hrg[1])
        ].copy()

        if q.strip():
            qq = q.strip().lower()
            df_f = df_f[
                df_f["Nama Toko"].astype(str).str.lower().str.contains(qq, na=False)
                | df_f["Nama Produk"].astype(str).str.lower().str.contains(qq, na=False)
            ]

        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database", "📑 Audit"])
        with tab1:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📌 Total Ditampilkan", fmt_int_id(len(df_f)))
            m2.metric("🏠 Murni Online", fmt_int_id((df_f["Tipe Usaha"] == "Murni Online (Rumahan)").sum()))
            m3.metric("🏬 Ada Toko Fisik", fmt_int_id((df_f["Tipe Usaha"] == "Ada Toko Fisik").sum()))
            m4.metric("🗺️ Jumlah Wilayah", fmt_int_id(df_f["Wilayah"].nunique()))

            if not st.session_state.get("fast_mode") and not df_f.empty:
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", hole=0.44,
                                 title="Komposisi Model Bisnis UMKM (Shopee)")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah")
                    fig = px.bar(grp, x="Wilayah", y="Jumlah",
                                 title="Total Usaha per Wilayah (Shopee)",
                                 color="Wilayah")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {int(x):,}".replace(",", ".") if str(x).isdigit() else f"Rp {x}")
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=420)

            excel_bytes = df_to_excel_bytes({"Data Shopee": df_f})
            st.download_button(
                "⬇️ Unduh Excel — Shopee",
                data=excel_bytes,
                file_name=f"UMKM_Shopee_{datetime.date.today()}.xlsx",
                use_container_width=True,
                type="primary",
            )

        with tab3:
            a = st.session_state.audit_shopee or {}
            st.info(f"📂 File diproses: **{fmt_int_id(a.get('file_count', 0))}**")
            st.success(f"✅ Baris valid: **{fmt_int_id(a.get('valid_rows', 0))}**")
            st.warning(f"⚠️ Diabaikan (luar wilayah): **{fmt_int_id(a.get('luar_wilayah', 0))}**")
            st.warning(f"⚠️ Error parsing harga: **{fmt_int_id(a.get('error_harga', 0))}**")
            st.caption(f"API calls: {fmt_int_id(a.get('api_calls', 0))}")


# ======================================================================================
# PAGE: TOKOPEDIA
# ======================================================================================
elif menu == "🟢 Tokopedia":
    section_header("Tokopedia Marketplace", "Workflow Tokopedia dengan UI enterprise dan feedback yang jelas.", "MARKETPLACE")
    banner("Dashboard UMKM — Tokopedia", "Ekstraksi data UMKM dari Tokopedia (Bangka Belitung)")

    with st.container(border=True):
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV Tokopedia", type=["csv"], accept_multiple_files=True, key="file_tkp")
            run = st.button("🚀 Proses Data Tokopedia", type="primary", use_container_width=True)
        with col2:
            st.subheader("🧾 Catatan")
            st.info("• Sistem akan menebak kolom bila struktur CSV berbeda.\n• Data difilter otomatis hanya Babel.")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Tokopedia terlebih dahulu.")
        else:
            with st.status("Memproses data Tokopedia…", expanded=True) as status:
                try:
                    total_semua_baris = 0
                    for f in files:
                        df_temp = pd.read_csv(f, dtype=str, on_bad_lines="skip")
                        total_semua_baris += len(df_temp)
                        f.seek(0)

                    hasil = []
                    total_baris = 0
                    err_h = 0
                    luar_wilayah = 0

                    progress = st.progress(0)
                    info = st.empty()
                    baris_diproses = 0

                    for file in files:
                        df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                        total_baris += len(df_raw)

                        if "Link" in df_raw.columns and "Nama Produk" in df_raw.columns:
                            col_links = ["Link"]
                            col_namas = ["Nama Produk"]
                            col_hargas = ["Harga"]
                            col_lokasis = ["Wilayah"]
                            col_tokos = ["Nama Toko"]
                        else:
                            col_links = [c for c in df_raw.columns if "Ui5" in c]
                            col_namas = [c for c in df_raw.columns if "+tnoqZhn" in c]
                            col_hargas = [c for c in df_raw.columns if "urMOIDHH" in c]
                            col_lokasis = [c for c in df_raw.columns if "gxi+fs" in c]
                            col_tokos = [c for c in df_raw.columns if "si3CN" in c]

                        max_items = max(len(col_links), len(col_namas), len(col_hargas), len(col_lokasis), len(col_tokos))
                        if max_items == 0:
                            max_items = 1

                        for i in range(len(df_raw)):
                            for j in range(max_items):
                                try:
                                    link = str(df_raw.iloc[i][col_links[j]]) if j < len(col_links) else "nan"
                                    nama = str(df_raw.iloc[i][col_namas[j]]) if j < len(col_namas) else "nan"
                                    harga_str = str(df_raw.iloc[i][col_hargas[j]]) if j < len(col_hargas) else "0"
                                    lokasi = safe_title(str(df_raw.iloc[i][col_lokasis[j]])) if j < len(col_lokasis) else "-"
                                    toko = str(df_raw.iloc[i][col_tokos[j]]) if j < len(col_tokos) else "Toko CSV"

                                    if link == "nan" or nama == "nan":
                                        continue
                                    if not is_in_babel(lokasi):
                                        luar_wilayah += 1
                                        continue

                                    try:
                                        harga_bersih = harga_str.replace(".", "").replace(",", "")
                                        angka_list = re.findall(r"\d+", harga_bersih)
                                        val_h = int(angka_list[0]) if angka_list else 0
                                        if val_h > 1_000_000_000:
                                            val_h = 0
                                    except Exception:
                                        val_h = 0
                                        err_h += 1

                                    if val_h > 0:
                                        tipe_usaha = deteksi_tipe_usaha(toko)
                                        hasil.append({
                                            "Nama Toko": toko, "Nama Produk": nama, "Harga": val_h,
                                            "Wilayah": lokasi, "Tipe Usaha": tipe_usaha, "Link": link
                                        })
                                except Exception:
                                    continue

                            baris_diproses += 1
                            if baris_diproses % 25 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses / max(total_semua_baris, 1), 1.0)
                                progress.progress(pct)
                                info.markdown(f"**⏳ Progress:** {fmt_int_id(baris_diproses)} / {fmt_int_id(total_semua_baris)} ({int(pct*100)}%)")

                    progress.empty()
                    info.empty()

                    df_final = pd.DataFrame(hasil).drop_duplicates()
                    st.session_state.data_tokped = df_final
                    st.session_state.audit_tokped = {
                        "file_count": len(files),
                        "total_rows": total_baris,
                        "valid_rows": len(df_final),
                        "luar_wilayah": luar_wilayah,
                        "error_harga": err_h,
                    }

                    status.update(label="✅ Selesai memproses Tokopedia", state="complete", expanded=False)
                    st.toast(f"Tokopedia: {fmt_int_id(len(df_final))} baris siap dianalisis", icon="✅")

                except Exception as e:
                    status.update(label="❌ Gagal memproses Tokopedia", state="error", expanded=True)
                    st.error(f"Error Sistem Tokopedia: {e}")

    df_tkp = st.session_state.data_tokped
    if df_tkp is not None and not df_tkp.empty:
        with st.container(border=True):
            st.subheader("🔎 Filter Pintar")
            c1, c2, c3 = st.columns([1.2, 1.2, 1.6], gap="medium")
            with c1:
                f_wil = st.multiselect("📍 Wilayah", options=sorted(df_tkp["Wilayah"].unique()),
                                       default=sorted(df_tkp["Wilayah"].unique()), key="f_wil_tkp")
            with c2:
                f_tipe = st.multiselect("🏢 Tipe Usaha", options=sorted(df_tkp["Tipe Usaha"].unique()),
                                        default=sorted(df_tkp["Tipe Usaha"].unique()), key="f_tipe_tkp")
            with c3:
                q = st.text_input("🔎 Cari (nama toko / produk)", value="", key="q_tkp")

            max_h = int(df_tkp["Harga"].max()) if df_tkp["Harga"].max() > 0 else 1_000_000
            f_hrg = st.slider("💰 Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_tkp")

        df_f = df_tkp[
            df_tkp["Wilayah"].isin(f_wil)
            & df_tkp["Tipe Usaha"].isin(f_tipe)
            & (df_tkp["Harga"] >= f_hrg[0])
            & (df_tkp["Harga"] <= f_hrg[1])
        ].copy()

        if q.strip():
            qq = q.strip().lower()
            df_f = df_f[
                df_f["Nama Toko"].astype(str).str.lower().str.contains(qq, na=False)
                | df_f["Nama Produk"].astype(str).str.lower().str.contains(qq, na=False)
            ]

        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database", "📑 Audit"])
        with tab1:
            m1, m2, m3 = st.columns(3)
            m1.metric("📌 Total Ditampilkan", fmt_int_id(len(df_f)))
            m2.metric("🏠 Murni Online", fmt_int_id((df_f["Tipe Usaha"] == "Murni Online (Rumahan)").sum()))
            m3.metric("🗺️ Jumlah Wilayah", fmt_int_id(df_f["Wilayah"].nunique()))

            if not st.session_state.get("fast_mode") and not df_f.empty:
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", hole=0.44,
                                 title="Komposisi Model Bisnis UMKM (Tokopedia)")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah")
                    fig = px.bar(grp, x="Wilayah", y="Jumlah",
                                 title="Total Usaha per Wilayah (Tokopedia)",
                                 color="Wilayah")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {int(x):,}".replace(",", ".") if str(x).isdigit() else f"Rp {x}")
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=420)
            excel_bytes = df_to_excel_bytes({"Data Tokopedia": df_f})
            st.download_button(
                "⬇️ Unduh Excel — Tokopedia",
                data=excel_bytes,
                file_name=f"UMKM_Tokopedia_{datetime.date.today()}.xlsx",
                use_container_width=True,
                type="primary",
            )

        with tab3:
            a = st.session_state.audit_tokped or {}
            st.info(f"📂 File diproses: **{fmt_int_id(a.get('file_count', 0))}**")
            st.success(f"✅ Baris valid: **{fmt_int_id(a.get('valid_rows', 0))}**")
            st.warning(f"⚠️ Diabaikan (luar wilayah): **{fmt_int_id(a.get('luar_wilayah', 0))}**")
            st.warning(f"⚠️ Error parsing harga: **{fmt_int_id(a.get('error_harga', 0))}**")


# ======================================================================================
# PAGE: FACEBOOK
# ======================================================================================
elif menu == "📍 Google Maps":
    section_header("Google Maps", "Pencarian lokasi & visualisasi peta dengan tampilan modern.", "LOCATION")
    banner("Dashboard UMKM — Google Maps", "Upload CSV hasil ekstensi → auto-clean → REAL MAP (Folium) + export Excel/CSV")

    with st.container(border=True):
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV Google Maps", type=["csv"], accept_multiple_files=True, key="file_maps")
            do_clean = st.toggle("✨ Auto-clean (disarankan)", value=True, key="clean_maps")
            run = st.button("🚀 Proses Data Google Maps", type="primary", use_container_width=True)

        with col2:
            st.subheader("🧾 Format Kolom (disarankan)")
            st.code("foto_url, nama_usaha, alamat, no_telepon, latitude, longitude, link", language="text")
            st.caption("Kalau beda nama kolom, sistem tetap coba map otomatis (toleran).")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Google Maps terlebih dahulu.")
        else:
            with st.status("Memproses data Google Maps…", expanded=True) as status:
                try:
                    df_raw, total_rows = read_csv_files(files)
                    df_clean, audit = clean_maps_dataframe(df_raw)

                    st.session_state.data_maps = df_clean
                    st.session_state.audit_maps = {
                        "file_count": len(files),
                        "rows_in": audit.get("rows_in", 0),
                        "rows_out": audit.get("rows_out", 0),
                        "dedup_removed": audit.get("dedup_removed", 0),
                        "invalid_coord": audit.get("invalid_coord", 0),
                        "invalid_link": audit.get("invalid_link", 0),
                        "empty_name": audit.get("empty_name", 0),
                        "missing_cols": audit.get("missing_cols", []),
                    }

                    status.update(label="✅ Selesai memproses Google Maps", state="complete", expanded=False)
                    st.toast(f"Google Maps: {fmt_int_id(len(df_clean))} baris siap dianalisis", icon="✅")

                except Exception as e:
                    status.update(label="❌ Gagal memproses Google Maps", state="error", expanded=True)
                    st.error(f"Error Sistem Google Maps: {e}")

    df_maps = st.session_state.data_maps
    if df_maps is not None and not df_maps.empty:
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🧹 Data Bersih", "📑 Audit"])
        with tab1:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📌 Total Data", fmt_int_id(len(df_maps)))
            m2.metric("📍 Koordinat Valid", fmt_int_id(df_maps["Latitude"].notna().sum()))
            m3.metric("🔗 Link Valid", fmt_int_id((df_maps["Link"].astype(str).str.len() > 0).sum()))
            m4.metric("☎️ No Telp Valid", fmt_int_id((df_maps["No Telepon"].astype(str).str.len() > 0).sum()))

            if not st.session_state.get("fast_mode"):
                render_real_map_folium(df_maps, height=560)

        with tab2:
            st.dataframe(df_maps, use_container_width=True, hide_index=True, height=440)

            excel_bytes = df_to_excel_bytes({"Data Google Maps": df_maps})
            st.download_button(
                "⬇️ Unduh Excel — Google Maps (Bersih)",
                data=excel_bytes,
                file_name=f"UMKM_GoogleMaps_Bersih_{datetime.date.today()}.xlsx",
                use_container_width=True,
                type="primary",
            )

            csv_bytes = df_maps.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Unduh CSV — Google Maps (Bersih)",
                data=csv_bytes,
                file_name=f"UMKM_GoogleMaps_Bersih_{datetime.date.today()}.csv",
                use_container_width=True,
            )

        with tab3:
            a = st.session_state.audit_maps or {}
            st.info(f"📂 File diproses: **{fmt_int_id(a.get('file_count', 0))}**")
            st.success(f"📥 Baris masuk: **{fmt_int_id(a.get('rows_in', 0))}**")
            st.success(f"✅ Baris keluar: **{fmt_int_id(a.get('rows_out', 0))}**")
            st.warning(f"🧽 Duplikat dihapus: **{fmt_int_id(a.get('dedup_removed', 0))}**")
            st.warning(f"📍 Koordinat invalid: **{fmt_int_id(a.get('invalid_coord', 0))}**")
            st.warning(f"🔗 Link invalid: **{fmt_int_id(a.get('invalid_link', 0))}**")
            st.warning(f"🏷️ Nama usaha kosong: **{fmt_int_id(a.get('empty_name', 0))}**")
            if a.get("missing_cols"):
                st.warning(f"Kolom tidak ditemukan (diisi kosong): {', '.join(a['missing_cols'])}")


# ======================================================================================
# PAGE: EXPORT MASTER
# ======================================================================================
elif menu == "📊 Export Gabungan":
    section_header("Export Gabungan", "Satukan data lintas platform lalu unduh dalam format rapi.", "EXPORT")
    banner("Export Master Data Gabungan", "Konsolidasi (Shopee, Tokopedia, , Google Maps) → 1 Excel, sheet terpisah")

    df_shp_ready = st.session_state.data_shopee is not None and not st.session_state.data_shopee.empty
    df_tkp_ready = st.session_state.data_tokped is not None and not st.session_state.data_tokped.empty
    df_maps_ready = st.session_state.data_maps is not None and not st.session_state.data_maps.empty

    if not (df_shp_ready or df_tkp_ready or df_maps_ready):
        st.warning("⚠️ Belum ada data. Silakan proses dulu di menu Shopee/Tokopedia/Google Maps.")
    else:
        with st.container(border=True):
            st.subheader("✅ Data Siap Dikonsolidasi")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📦 Shopee", fmt_int_id(len(st.session_state.data_shopee)) if df_shp_ready else 0)
            c2.metric("📦 Tokopedia", fmt_int_id(len(st.session_state.data_tokped)) if df_tkp_ready else 0)
            c4.metric("📦 Google Maps", fmt_int_id(len(st.session_state.data_maps)) if df_maps_ready else 0)
            st.caption("Output: 1 file Excel berisi sheet terpisah per sumber + autofilter + header rapi.")

        sheets = {}
        if df_shp_ready:
            sheets["Data Shopee"] = st.session_state.data_shopee
        if df_tkp_ready:
            sheets["Data Tokopedia"] = st.session_state.data_tokped
        if df_maps_ready:
            sheets["Data Google Maps"] = st.session_state.data_maps

        excel_bytes = df_to_excel_bytes(sheets)

        with st.container(border=True):
            st.subheader("⬇️ Unduh File Master")
            _, col_btn, _ = st.columns([1, 2, 1])
            with col_btn:
                st.download_button(
                    label="⬇️ UNDUH EXCEL MASTER (4-IN-1)",
                    data=excel_bytes,
                    file_name=f"Master_UMKM_BPS_{datetime.date.today()}.xlsx",
                    use_container_width=True,
                    type="primary",
                )


# ======================================================================================
# FOOTER
# ======================================================================================
st.markdown(
    "<div style='margin-top:22px; opacity:.78; font-size:.86rem;'>"
    "Built with Streamlit • Badan Pusat Statistik UMKM Toolkit"
    "</div>",
    unsafe_allow_html=True,
)

# --- FINAL FINAL OVERRIDE (Premium Sunset v3: toned down + vignette) ---
st.markdown(
    """
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"]{
  background:
    radial-gradient(1700px 980px at 7% 12%, rgba(255,140,40,.36) 0%, rgba(255,140,40,.16) 38%, rgba(255,140,40,0) 72%),
    radial-gradient(1500px 980px at 92% 14%, rgba(255,200,90,.22) 0%, rgba(255,200,90,.10) 42%, rgba(255,200,90,0) 78%),
    radial-gradient(1400px 900px at 45% 105%, rgba(255,210,140,.10) 0%, rgba(255,210,140,0) 72%),
    radial-gradient(1200px 820px at 55% 55%, rgba(30,58,138,.10) 0%, rgba(30,58,138,0) 62%),
    linear-gradient(155deg, #1a0f0a 0%, #22110b 20%, #111018 55%, #070a10 100%) !important;
  background-attachment: fixed !important;
}

/* Cinematic vignette to prevent "too bright" look */
[data-testid="stAppViewContainer"]::before{
  content:"";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(1200px 700px at 50% 35%, rgba(0,0,0,0) 0%, rgba(0,0,0,0.28) 60%, rgba(0,0,0,0.52) 100%),
    linear-gradient(180deg, rgba(0,0,0,0.18) 0%, rgba(0,0,0,0.42) 100%);
  mix-blend-mode: multiply;
}

/* Slightly calm the top accent line */
.block-container::before{
  height:5px;
  background: linear-gradient(90deg,
    rgba(255,140,0,0) 0%,
    rgba(255,120,0,.72) 30%,
    rgba(255,200,120,.80) 55%,
    rgba(255,140,0,.72) 75%,
    rgba(255,140,0,0) 100%);
  box-shadow: 0 14px 44px rgba(255,120,0,.26);
}
</style>
""",
    unsafe_allow_html=True,
)

