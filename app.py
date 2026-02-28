import streamlit as st
import pandas as pd
import re
import io
import requests
import datetime
import os
import time

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
BPS_BG_2 = "#07070a"
BPS_CARD = "rgba(255,255,255,0.06)"
BPS_BORDER = "rgba(255,111,0,0.32)"
BPS_BORDER_SOFT = "rgba(255,111,0,0.18)"
BPS_TEXT_MUTED = "rgba(245,245,245,0.78)"
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
# THEME / CSS (Premium Orange Glass)
# ======================================================================================
st.markdown(
    f"""
<style>
/* =========================== Base + Typography =========================== */
html, body, [class*="css"] {{
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
}}
code, pre {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace !important;
}}
a {{
    color: {BPS_AMBER} !important;
    text-decoration: none;
}}
a:hover {{
    text-decoration: underline;
}}

[data-testid="stAppViewContainer"] {{
    background:
      radial-gradient(900px 520px at 12% 10%, rgba(255,111,0,.42) 0%, rgba(255,111,0,0) 64%),
      radial-gradient(760px 520px at 88% 18%, rgba(255,193,7,.30) 0%, rgba(255,193,7,0) 58%),
      radial-gradient(1000px 700px at 50% 110%, rgba(255,111,0,.18) 0%, rgba(255,111,0,0) 60%),
      linear-gradient(135deg, {BPS_BG_2} 0%, {BPS_DARK} 55%, {BPS_BG_2} 100%) !important;
    background-attachment: fixed !important;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0) !important;
}}

.block-container {{
    padding-top: 1.0rem;
    padding-bottom: 2.2rem;
    max-width: 1400px;
}}

/* Top glow */
.block-container::before {{
    content: "";
    display: block;
    height: 7px;
    width: 100%;
    border-radius: 999px;
    margin: 4px 0 16px 0;
    background: linear-gradient(90deg,
        rgba(255,111,0,0) 0%,
        rgba(255,111,0,.96) 25%,
        rgba(255,193,7,.92) 55%,
        rgba(255,111,0,.96) 82%,
        rgba(255,111,0,0) 100%);
    box-shadow: 0 10px 46px rgba(255,111,0,.23);
}}

/* =========================== Sidebar =========================== */
[data-testid="stSidebar"] {{
    background:
      radial-gradient(680px 420px at 15% 8%, rgba(255,111,0,.30) 0%, rgba(255,111,0,0) 62%),
      radial-gradient(680px 420px at 90% 22%, rgba(255,193,7,.18) 0%, rgba(255,193,7,0) 62%),
      linear-gradient(180deg, rgba(14,14,16,.99) 0%, rgba(10,10,12,.99) 55%, rgba(8,8,9,.995) 100%) !important;
    border-right: 1px solid rgba(255,111,0,.45);
    box-shadow: 12px 0 50px rgba(0,0,0,.45);
}}
[data-testid="stSidebar"] * {{
    color: #f4f4f4 !important;
}}
/* Sidebar title */
.sidebar-title {{
    font-weight: 950;
    font-size: 1.05rem;
    letter-spacing: .2px;
    margin-bottom: 2px;
}}
.sidebar-sub {{
    opacity: .78;
    font-size: .86rem;
    margin-bottom: 10px;
}}

/* =========================== Cards / Containers =========================== */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {BPS_CARD};
    border: 1px solid {BPS_BORDER} !important;
    border-radius: 20px;
    padding: 18px 18px;
    box-shadow:
      0 16px 44px rgba(0,0,0,.30),
      0 0 0 1px rgba(255,111,0,.06) inset;
    backdrop-filter: blur(14px);
}}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: rgba(255,193,7,.50) !important;
    box-shadow:
      0 20px 56px rgba(0,0,0,.35),
      0 0 0 1px rgba(255,193,7,.10) inset,
      0 26px 90px rgba(255,111,0,.12);
}}

/* =========================== Hero Banner =========================== */
.bps-hero {{
    border-radius: 22px;
    padding: 26px 28px;
    margin: 2px 0 18px 0;
    background:
      radial-gradient(980px 380px at 14% 0%, rgba(255,111,0,.44) 0%, rgba(255,111,0,0) 64%),
      radial-gradient(980px 420px at 86% 8%, rgba(255,193,7,.26) 0%, rgba(255,193,7,0) 62%),
      linear-gradient(135deg, rgba(255,111,0,.16) 0%, rgba(255,193,7,.10) 40%, rgba(255,255,255,.04) 100%);
    border: 1px solid rgba(255,111,0,.34);
    box-shadow: 0 20px 62px rgba(0,0,0,.36);
    backdrop-filter: blur(16px);
}}
.hero-kicker {{
    letter-spacing: 2.2px;
    text-transform: uppercase;
    font-weight: 900;
    font-size: .78rem;
    color: rgba(255,193,7,.98);
    margin-bottom: 8px;
}}
.hero-title {{
    font-size: 2.2rem;
    font-weight: 1000;
    margin: 0 0 8px 0;
    color: #ffffff;
    line-height: 1.12;
}}
.hero-sub {{
    margin: 0;
    color: rgba(240,240,240,.90);
    font-size: 1.03rem;
}}
.hero-badges {{
    margin-top: 14px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}}
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 999px;
    border: 1px solid {BPS_BORDER_SOFT};
    background: rgba(0,0,0,.20);
    box-shadow: 0 10px 30px rgba(0,0,0,.25);
    font-size: .88rem;
    color: rgba(248,248,248,.92);
}}
.badge i {{
    opacity: .92;
}}

/* =========================== Section Titles =========================== */
.section-title {{
    font-size: 1.18rem;
    font-weight: 950;
    margin: 0 0 6px 0;
}}
.section-sub {{
    color: {BPS_TEXT_MUTED};
    margin: 0 0 10px 0;
    font-size: .92rem;
}}
.hr-glow {{
    height: 1px;
    border: none;
    margin: 12px 0 4px 0;
    background: linear-gradient(90deg, rgba(255,111,0,0), rgba(255,111,0,.55), rgba(255,193,7,.38), rgba(255,111,0,0));
}}

/* =========================== Metrics =========================== */
div[data-testid="metric-container"] {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,111,0,0.28);
    border-left: 8px solid {BPS_OREN_UTAMA};
    border-radius: 18px;
    padding: 14px 16px;
    box-shadow:
      0 12px 36px rgba(0,0,0,.28),
      0 0 0 1px rgba(255,111,0,.06) inset;
    backdrop-filter: blur(12px);
    transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
}}
div[data-testid="metric-container"]:hover {{
    transform: translateY(-3px);
    border-color: rgba(255,193,7,.58);
    box-shadow:
      0 18px 52px rgba(0,0,0,.32),
      0 0 0 1px rgba(255,193,7,.10) inset,
      0 34px 100px rgba(255,111,0,.12);
}}
div[data-testid="metric-container"] label {{
    color: rgba(240,240,240,.86) !important;
    font-weight: 850;
    letter-spacing: .2px;
}}

/* =========================== Tabs =========================== */
.stTabs [data-baseweb="tab-list"] {{
    gap: 10px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,111,0,.22);
    padding: 10px;
    border-radius: 18px;
    backdrop-filter: blur(14px);
}}
.stTabs [data-baseweb="tab"] {{
    height: 46px;
    border-radius: 14px;
    padding: 0 16px;
    background: rgba(255,255,255,0.03);
    color: rgba(245,245,245,.86);
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, rgba(255,111,0,.98) 0%, rgba(255,193,7,.92) 100%) !important;
    color: #111 !important;
    font-weight: 1000;
    box-shadow: 0 16px 52px rgba(255,111,0,.24);
}}

/* =========================== Buttons =========================== */
div[data-testid="stDownloadButton"] button,
.stButton > button {{
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    background: linear-gradient(135deg, rgba(255,111,0,.95) 0%, rgba(255,193,7,.88) 100%) !important;
    color: #111 !important;
    font-weight: 1000 !important;
    height: 50px !important;
    box-shadow: 0 18px 55px rgba(255,111,0,.22);
    transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
}}
div[data-testid="stDownloadButton"] button:hover,
.stButton > button:hover {{
    transform: translateY(-1px);
    filter: brightness(1.05);
    box-shadow: 0 24px 70px rgba(255,111,0,.28);
}}
button[kind="secondary"] {{
    background: rgba(255,255,255,.08) !important;
    border: 1px solid rgba(255,111,0,.28) !important;
    color: #f2f2f2 !important;
}}

/* =========================== Inputs =========================== */
[data-baseweb="input"] > div {{
    border-radius: 14px !important;
}}
[data-baseweb="select"] > div {{
    border-radius: 14px !important;
}}
textarea {{
    border-radius: 14px !important;
}}

/* =========================== Dataframe =========================== */
[data-testid="stDataFrame"] {{
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(255,111,0,.18);
}}
/* Scrollbar (webkit) */
::-webkit-scrollbar {{
    height: 10px;
    width: 10px;
}}
::-webkit-scrollbar-thumb {{
    background: rgba(255,111,0,.35);
    border-radius: 999px;
}}
::-webkit-scrollbar-track {{
    background: rgba(255,255,255,.06);
    border-radius: 999px;
}}

/* =========================== Footer =========================== */
.footer {{
    margin-top: 22px;
    padding: 14px 16px;
    border-radius: 16px;
    border: 1px solid rgba(255,111,0,.18);
    background: rgba(255,255,255,.03);
    color: rgba(245,245,245,.78);
}}
</style>
""",
    unsafe_allow_html=True,
)


# ======================================================================================
# SESSION STATE
# ======================================================================================
def ensure_state():
    defaults = {
        "data_shopee": None, "audit_shopee": {},
        "data_tokped": None, "audit_tokped": {},
        "data_fb": None,     "audit_fb": {},
        "data_maps": None,   "audit_maps": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ensure_state()


# ======================================================================================
# HELPERS (UI)
# ======================================================================================
def hero(title: str, subtitle: str, badges=None):
    badges = badges or []
    badges_html = "".join([f'<span class="badge"><i>✦</i>{b}</span>' for b in badges])
    st.markdown(
        f"""
<div class="bps-hero">
  <div class="hero-kicker">🏛️ BADAN PUSAT STATISTIK</div>
  <div class="hero-title">{title}</div>
  <p class="hero-sub">{subtitle}</p>
  <div class="hero-badges">{badges_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )

def section(title: str, subtitle: str = ""):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='section-sub'>{subtitle}</div>", unsafe_allow_html=True)
    st.markdown("<hr class='hr-glow'/>", unsafe_allow_html=True)

def fmt_int_id(n: int) -> str:
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return "0"

def safe_title(x: str) -> str:
    if x is None:
        return ""
    s = str(x).strip()
    return s[:1].upper() + s[1:] if s else s


# ======================================================================================
# HELPERS (CLEANERS)
# ======================================================================================
def _to_str(x):
    if pd.isna(x):
        return ""
    return str(x)

def clean_placeholder_to_empty(x: str) -> str:
    s = _to_str(x).strip()
    if not s:
        return ""
    if s.lower() == PLACEHOLDER.lower():
        return ""
    if s.lower() in ["nan", "none", "null"]:
        return ""
    return re.sub(r"\s+", " ", s).strip()

def normalize_phone_id(x: str) -> str:
    s = clean_placeholder_to_empty(x)
    if not s:
        return ""
    s = s.replace(PHONE_EMPTY, "").strip()
    if not s:
        return ""
    s2 = re.sub(r"[^\d+]", "", s)

    if s2.startswith("08"):
        s2 = "+62" + s2[1:]
    if re.fullmatch(r"62\d{7,15}", s2):
        s2 = "+" + s2
    if s2.startswith("+") and re.fullmatch(r"\+\d{8,16}", s2):
        return s2

    digits = re.sub(r"\D", "", s2)
    if digits.startswith("0") and len(digits) >= 9:
        return "+62" + digits[1:]
    if digits.startswith("62") and len(digits) >= 9:
        return "+" + digits
    return s2

def normalize_url(x: str) -> str:
    s = clean_placeholder_to_empty(x)
    if not s:
        return ""
    s = s.strip()

    if s.startswith(("http://", "https://")):
        return s
    if s.startswith("www."):
        return "https://" + s
    if s.startswith("wa.me/"):
        return "https://" + s
    if s.startswith("instagram.com/"):
        return "https://" + s
    if s.startswith("@") and len(s) > 1:
        return "https://instagram.com/" + s[1:]
    return ""

def to_float_safe(x: str):
    s = clean_placeholder_to_empty(x)
    if not s:
        return None
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


# ======================================================================================
# BUSINESS LOGIC
# ======================================================================================
def deteksi_tipe_usaha(nama_toko):
    if pd.isna(nama_toko) or nama_toko in ["Tidak Dilacak", "Toko CSV", "Anonim", ""]:
        return "Tidak Terdeteksi (Butuh Nama Toko)"

    if str(nama_toko) == "FB Seller":
        return "Perorangan (Facebook)"

    nama_lower = str(nama_toko).lower()
    keyword_fisik = [
        "toko", "warung", "grosir", "mart", "apotek", "cv.", "pt.", "official", "agen",
        "distributor", "kios", "kedai", "supermarket", "minimarket", "cabang", "jaya",
        "abadi", "makmur", "motor", "mobil", "bengkel", "snack", "store"
    ]
    for kata in keyword_fisik:
        if kata in nama_lower:
            return "Ada Toko Fisik"
    return "Murni Online (Rumahan)"

def clean_maps_dataframe(df_raw: pd.DataFrame) -> (pd.DataFrame, dict):
    audit = {
        "rows_in": 0,
        "rows_out": 0,
        "missing_cols": [],
        "dedup_removed": 0,
        "invalid_coord": 0,
        "invalid_link": 0,
        "empty_name": 0,
    }

    out_cols = ["Foto URL", "Nama Usaha", "Alamat", "No Telepon", "Latitude", "Longitude", "Link"]
    if df_raw is None or df_raw.empty:
        return pd.DataFrame(columns=out_cols), audit

    audit["rows_in"] = len(df_raw)

    colmap_candidates = {
        "foto_url": ["foto_url", "foto", "photo", "gambar", "image"],
        "nama_usaha": ["nama_usaha", "nama usaha", "nama", "name"],
        "alamat": ["alamat", "address"],
        "no_telepon": ["no_telepon", "telepon", "phone", "no telp", "nomor"],
        "latitude": ["latitude", "lat"],
        "longitude": ["longitude", "lng", "lon", "long"],
        "link": ["link", "website", "url", "wa", "ig"],
    }

    cols_lower = {c.lower(): c for c in df_raw.columns}
    found = {}
    for k, cands in colmap_candidates.items():
        real = None
        for cc in cands:
            if cc.lower() in cols_lower:
                real = cols_lower[cc.lower()]
                break
        if real is None:
            audit["missing_cols"].append(k)
        found[k] = real

    df = pd.DataFrame()
    for k, real in found.items():
        df[k] = "" if real is None else df_raw[real].astype(str)

    df["foto_url"] = df["foto_url"].apply(clean_placeholder_to_empty)
    df["nama_usaha"] = df["nama_usaha"].apply(clean_placeholder_to_empty)
    df["alamat"] = df["alamat"].apply(clean_placeholder_to_empty)
    df["no_telepon"] = df["no_telepon"].apply(normalize_phone_id)
    df["link"] = df["link"].apply(normalize_url)

    df["latitude_f"] = df["latitude"].apply(to_float_safe)
    df["longitude_f"] = df["longitude"].apply(to_float_safe)

    invalid_coord = df["latitude_f"].isna() | df["longitude_f"].isna()
    audit["invalid_coord"] = int(invalid_coord.sum())

    df["latitude"] = df["latitude_f"]
    df["longitude"] = df["longitude_f"]
    df.drop(columns=["latitude_f", "longitude_f"], inplace=True)

    audit["invalid_link"] = int((df["link"] == "").sum())
    audit["empty_name"] = int((df["nama_usaha"] == "").sum())

    def _key(r):
        name = (r["nama_usaha"] or "").lower()
        addr = (r["alamat"] or "").lower()
        lat = "" if pd.isna(r["latitude"]) else f"{r['latitude']:.6f}"
        lng = "" if pd.isna(r["longitude"]) else f"{r['longitude']:.6f}"
        return f"{name}__{addr}__{lat}__{lng}"

    before = len(df)
    df["_k"] = df.apply(_key, axis=1)
    df = df[df["_k"].str.strip() != "__"]
    df = df.drop_duplicates(subset=["_k"], keep="first").drop(columns=["_k"])
    after = len(df)
    audit["dedup_removed"] = int(before - after)

    df_out = pd.DataFrame({
        "Foto URL": df["foto_url"].fillna(""),
        "Nama Usaha": df["nama_usaha"].fillna(""),
        "Alamat": df["alamat"].fillna(""),
        "No Telepon": df["no_telepon"].fillna(""),
        "Latitude": df["latitude"],
        "Longitude": df["longitude"],
        "Link": df["link"].fillna(""),
    })

    audit["rows_out"] = len(df_out)
    return df_out, audit

def df_to_excel_bytes(sheets: dict) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        wb = writer.book
        header_fmt = wb.add_format({"bold": True, "bg_color": BPS_OREN_UTAMA, "font_color": "white"})
        currency_fmt = wb.add_format({"num_format": "#,##0"})
        float_fmt = wb.add_format({"num_format": "0.000000"})

        for sheet_name, df in sheets.items():
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            ws = writer.sheets[sheet_name]

            for col_num, value in enumerate(df.columns.values):
                ws.write(0, col_num, value, header_fmt)

            if len(df) > 0:
                ws.autofilter(0, 0, len(df), len(df.columns) - 1)

            for i, col in enumerate(df.columns):
                sample = df[col].astype(str).head(200).values
                max_len = max([len(str(col))] + [len(x) for x in sample]) if len(sample) else len(str(col))
                width = min(max(12, max_len + 2), 60)
                ws.set_column(i, i, width)

            for i, col in enumerate(df.columns):
                if col.lower() == "harga":
                    ws.set_column(i, i, 18, currency_fmt)
                if col.lower() in ["latitude", "longitude"]:
                    ws.set_column(i, i, 14, float_fmt)

    return buf.getvalue()

def read_csv_files(files) -> (pd.DataFrame, int):
    dfs = []
    total = 0
    for f in files:
        df = pd.read_csv(f, dtype=str, on_bad_lines="skip")
        total += len(df)
        dfs.append(df)
    if not dfs:
        return pd.DataFrame(), 0
    return pd.concat(dfs, ignore_index=True), total

def is_in_babel(wilayah: str) -> bool:
    s = (wilayah or "").lower()
    return any(k in s for k in BABEL_KEYS)


# ======================================================================================
# REAL MAP (FOLIUM) + FALLBACK SAFE (NO TILE)
# ======================================================================================
def render_real_map_folium(df_maps: pd.DataFrame, height: int = 560):
    """Real map (Leaflet/Folium). Jika tile diblok (403), user bisa ganti provider.
    Kalau tetap gagal, otomatis fallback ke peta aman (tanpa tile) via scatter_geo.
    """
    df_plot = df_maps.dropna(subset=["Latitude", "Longitude"]).copy()
    df_plot = df_plot[(df_plot["Latitude"].between(-90, 90)) & (df_plot["Longitude"].between(-180, 180))].copy()
    if df_plot.empty:
        st.info("Tidak ada koordinat valid untuk ditampilkan.")
        return

    tile_choice = st.selectbox(
        "🗺️ Provider Peta (kalau blank/403, ganti ini)",
        [
            "CartoDB DarkMatter (recommended)",
            "CartoDB Positron",
            "OpenStreetMap",
        ],
        index=0,
        key="maps_tile_provider",
    )

    tiles_map = {
        "OpenStreetMap": "OpenStreetMap",
        "CartoDB Positron": "CartoDB positron",
        "CartoDB DarkMatter (recommended)": "CartoDB dark_matter",
    }

    center_lat = float(df_plot["Latitude"].mean())
    center_lon = float(df_plot["Longitude"].mean())

    try:
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles=tiles_map.get(tile_choice, "CartoDB dark_matter"),
            control_scale=True,
        )

        cluster = MarkerCluster(name="UMKM").add_to(m)

        def safe_html(s):
            return "" if s is None else str(s).replace("<", "&lt;").replace(">", "&gt;")

        for _, r in df_plot.iterrows():
            nama = safe_html(r.get("Nama Usaha", ""))
            alamat = safe_html(r.get("Alamat", ""))
            telp = safe_html(r.get("No Telepon", ""))
            link = safe_html(r.get("Link", ""))

            link_html = f'<a href="{link}" target="_blank">Buka Link</a>' if link else "-"

            popup = f"""
            <div style="width:270px;">
              <div style="font-weight:900; font-size:14px; margin-bottom:6px;">{nama}</div>
              <div style="font-size:12px; opacity:.92;">{alamat}</div>
              <hr style="border:none;border-top:1px solid rgba(255,111,0,.28); margin:8px 0;">
              <div style="font-size:12px;">☎️ {telp if telp else "-"}</div>
              <div style="font-size:12px; margin-top:4px;">🔗 {link_html}</div>
            </div>
            """

            folium.CircleMarker(
                location=[float(r["Latitude"]), float(r["Longitude"])],
                radius=7,
                weight=2,
                color=BPS_OREN_UTAMA,
                fill=True,
                fill_color=BPS_OREN_UTAMA,
                fill_opacity=0.85,
                popup=folium.Popup(popup, max_width=360),
            ).add_to(cluster)

        folium.LayerControl(collapsed=True).add_to(m)

        st_folium(m, width=None, height=height)
        st.caption("Jika peta tidak tampil (tile diblok), coba ganti Provider Peta di atas.")
        return

    except Exception:
        st.warning("Provider tile diblok/403. Menampilkan peta aman (tanpa tile) sebagai fallback.")
        fig = px.scatter_geo(
            df_plot,
            lat="Latitude",
            lon="Longitude",
            hover_name="Nama Usaha",
            hover_data={"Alamat": True, "No Telepon": True, "Link": True, "Latitude": ":.6f", "Longitude": ":.6f"},
            projection="mercator",
            height=height,
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor=BPS_PAPER,
            plot_bgcolor=BPS_PAPER,
            font=dict(color="white"),
        )
        st.plotly_chart(fig, use_container_width=True)


# ======================================================================================
# SIDEBAR
# ======================================================================================
with st.sidebar:
    st.markdown(f"<div class='sidebar-title'>{APP_ICON} {APP_TITLE}</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-sub'>Penyedia Data Statistik Berkualitas untuk Indonesia Maju</div>", unsafe_allow_html=True)
    st.divider()

    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)

    menu = st.radio(
        "🧭 Navigasi",
        ["🟠 Shopee", "🟢 Tokopedia", "🔵 Facebook", "📍 Google Maps", "📊 Export Gabungan"],
        index=0,
    )

    st.divider()
    with st.expander("⚙️ Pengaturan Umum", expanded=False):
        st.checkbox("Tampilkan tips cepat", value=True, key="show_tips")
        st.checkbox("Mode cepat (kurangi rendering chart besar)", value=False, key="fast_mode")


# ======================================================================================
# PAGE: SHOPEE
# ======================================================================================
if menu == "🟠 Shopee":
    hero(
        "Dashboard UMKM — Shopee",
        "Ekstraksi data UMKM dari Shopee Marketplace (Bangka Belitung). UI premium + export rapi.",
        badges=["Filter Babel otomatis", "Klasifikasi Tipe Usaha", "Export Excel 1 klik", "Tema Oren BPS"]
    )

    with st.container(border=True):
        section("📥 Input Data", "Upload CSV hasil scraping, lalu proses otomatis.")
        left, right = st.columns([1.2, 1.0], gap="large")

        with left:
            files = st.file_uploader("Unggah CSV Shopee", type=["csv"], accept_multiple_files=True, key="file_shp")

            mode_api = st.toggle(
                "🔎 Deteksi Nama Toko via API Shopee",
                value=True,
                help="Jika ON: sistem mencoba mengambil nama toko dari API shopid di link produk.",
                key="api_shp",
            )

            colA, colB, colC = st.columns(3)
            with colA:
                api_timeout = st.number_input("Timeout API (detik)", min_value=1, max_value=10, value=2, step=1)
            with colB:
                api_sleep = st.number_input("Jeda per request (detik)", min_value=0.0, max_value=2.0, value=0.0, step=0.1)
            with colC:
                max_api_calls = st.number_input("Maks panggilan API", min_value=0, max_value=50000, value=8000, step=500)

            st.caption("Tips: kalau scraping kamu “terdeteksi robot”, naikkan jeda request.")
            run = st.button("🚀 Proses Data Shopee", type="primary", use_container_width=True)

        with right:
            section("🧾 Ringkasan", "Aturan pembersihan & output yang dihasilkan.")
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
                                            df_raw.columns[min(3, len(df_raw.columns) - 1)])
                            col_harga = next((c for c in df_raw.columns if "font-medium" in c.lower()),
                                             df_raw.columns[min(4, len(df_raw.columns) - 1)])
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
                                    f"({int(pct * 100)}%) • API calls: {fmt_int_id(api_calls)}"
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
            section("🔎 Filter Pintar", "Cari cepat dan saring data untuk analisis yang presisi.")
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
    hero(
        "Dashboard UMKM — Tokopedia",
        "Ekstraksi data UMKM dari Tokopedia (Bangka Belitung).",
        badges=["Filter Babel otomatis", "Dashboard ringkas", "Export Excel rapi"]
    )

    with st.container(border=True):
        section("📥 Input Data", "Upload CSV Tokopedia lalu proses.")
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV Tokopedia", type=["csv"], accept_multiple_files=True, key="file_tkp")
            run = st.button("🚀 Proses Data Tokopedia", type="primary", use_container_width=True)
        with col2:
            section("🧾 Catatan", "Sistem toleran walau kolom CSV berubah.")
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
            section("🔎 Filter Pintar", "Cari cepat dan saring data untuk analisis.")
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
elif menu == "🔵 Facebook":
    hero(
        "Dashboard UMKM — Facebook Marketplace",
        "Ekstraksi data UMKM dari Facebook Marketplace (Bangka Belitung).",
        badges=["Filter Babel otomatis", "Deteksi perorangan", "Export Excel rapi"]
    )

    with st.container(border=True):
        section("📥 Input Data", "Upload CSV Facebook lalu proses.")
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV Facebook", type=["csv"], accept_multiple_files=True, key="file_fb")
            run = st.button("🚀 Proses Data Facebook", type="primary", use_container_width=True)
        with col2:
            section("🧾 Catatan", "Nama toko sering kosong; sistem mengisi default dengan aman.")
            st.info("• Nama toko sering kosong → akan diisi default.\n• Tipe Usaha perorangan otomatis bila terdeteksi.")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Facebook terlebih dahulu.")
        else:
            with st.status("Memproses data Facebook…", expanded=True) as status:
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
                            col_link, col_nama, col_harga, col_wilayah, col_toko = "Link", "Nama Produk", "Harga", "Wilayah", "Nama Toko"
                        else:
                            col_toko = df_raw.columns[0]
                            col_nama = df_raw.columns[1] if len(df_raw.columns) > 1 else df_raw.columns[0]
                            col_wilayah = df_raw.columns[2] if len(df_raw.columns) > 2 else df_raw.columns[0]
                            col_harga = df_raw.columns[4] if len(df_raw.columns) > 4 else df_raw.columns[-1]
                            col_link = df_raw.columns[5] if len(df_raw.columns) > 5 else df_raw.columns[-1]

                        for i in range(len(df_raw)):
                            row = df_raw.iloc[i]
                            link = str(row.get(col_link, ""))
                            nama = str(row.get(col_nama, ""))
                            harga_str = str(row.get(col_harga, ""))
                            lokasi = safe_title(str(row.get(col_wilayah, "")))
                            toko = str(row.get(col_toko, "FB Seller")) or "FB Seller"

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

                            if val_h > 0:
                                tipe_usaha = deteksi_tipe_usaha(toko)
                                hasil.append({
                                    "Nama Toko": toko, "Nama Produk": nama, "Harga": val_h,
                                    "Wilayah": lokasi, "Tipe Usaha": tipe_usaha, "Link": link
                                })

                            baris_diproses += 1
                            if baris_diproses % 25 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses / max(total_semua_baris, 1), 1.0)
                                progress.progress(pct)
                                info.markdown(f"**⏳ Progress:** {fmt_int_id(baris_diproses)} / {fmt_int_id(total_semua_baris)} ({int(pct*100)}%)")

                    progress.empty()
                    info.empty()

                    df_final = pd.DataFrame(hasil).drop_duplicates()
                    st.session_state.data_fb = df_final
                    st.session_state.audit_fb = {
                        "file_count": len(files),
                        "total_rows": total_baris,
                        "valid_rows": len(df_final),
                        "luar_wilayah": luar_wilayah,
                        "error_harga": err_h,
                    }

                    status.update(label="✅ Selesai memproses Facebook", state="complete", expanded=False)
                    st.toast(f"Facebook: {fmt_int_id(len(df_final))} baris siap dianalisis", icon="✅")

                except Exception as e:
                    status.update(label="❌ Gagal memproses Facebook", state="error", expanded=True)
                    st.error(f"Error Sistem FB: {e}")

    df_fb = st.session_state.data_fb
    if df_fb is not None and not df_fb.empty:
        with st.container(border=True):
            section("🔎 Filter Pintar", "Cari cepat dan saring data untuk analisis.")
            c1, c2, c3 = st.columns([1.2, 1.2, 1.6], gap="medium")
            with c1:
                f_wil = st.multiselect("📍 Wilayah", options=sorted(df_fb["Wilayah"].unique()),
                                       default=sorted(df_fb["Wilayah"].unique()), key="f_wil_fb")
            with c2:
                f_tipe = st.multiselect("🏢 Tipe Usaha", options=sorted(df_fb["Tipe Usaha"].unique()),
                                        default=sorted(df_fb["Tipe Usaha"].unique()), key="f_tipe_fb")
            with c3:
                q = st.text_input("🔎 Cari (nama toko / produk)", value="", key="q_fb")

            max_h = int(df_fb["Harga"].max()) if df_fb["Harga"].max() > 0 else 1_000_000
            f_hrg = st.slider("💰 Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_fb")

        df_f = df_fb[
            df_fb["Wilayah"].isin(f_wil)
            & df_fb["Tipe Usaha"].isin(f_tipe)
            & (df_fb["Harga"] >= f_hrg[0])
            & (df_fb["Harga"] <= f_hrg[1])
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
            m2.metric("👤 Perorangan", fmt_int_id((df_f["Tipe Usaha"] == "Perorangan (Facebook)").sum()))
            m3.metric("🗺️ Jumlah Wilayah", fmt_int_id(df_f["Wilayah"].nunique()))

            if not st.session_state.get("fast_mode") and not df_f.empty:
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", hole=0.44,
                                 title="Komposisi Model Bisnis (Facebook)")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah")
                    fig = px.bar(grp, x="Wilayah", y="Jumlah",
                                 title="Total Usaha per Wilayah (Facebook)",
                                 color="Wilayah")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {int(x):,}".replace(",", ".") if str(x).isdigit() else f"Rp {x}")
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=420)
            excel_bytes = df_to_excel_bytes({"Data Facebook": df_f})
            st.download_button(
                "⬇️ Unduh Excel — Facebook",
                data=excel_bytes,
                file_name=f"UMKM_Facebook_{datetime.date.today()}.xlsx",
                use_container_width=True,
                type="primary",
            )

        with tab3:
            a = st.session_state.audit_fb or {}
            st.info(f"📂 File diproses: **{fmt_int_id(a.get('file_count', 0))}**")
            st.success(f"✅ Baris valid: **{fmt_int_id(a.get('valid_rows', 0))}**")
            st.warning(f"⚠️ Diabaikan (luar wilayah): **{fmt_int_id(a.get('luar_wilayah', 0))}**")
            st.warning(f"⚠️ Error parsing harga: **{fmt_int_id(a.get('error_harga', 0))}**")


# ======================================================================================
# PAGE: GOOGLE MAPS
# ======================================================================================
elif menu == "📍 Google Maps":
    hero(
        "Dashboard UMKM — Google Maps",
        "Upload CSV hasil ekstensi → auto-clean → REAL MAP (Folium) + export Excel/CSV.",
        badges=["Real Map (Leaflet)", "Cluster marker", "Provider switch (anti 403)", "Export Excel/CSV"]
    )

    with st.container(border=True):
        section("📥 Input Data", "Unggah CSV hasil scraping Google Maps.")
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV Google Maps", type=["csv"], accept_multiple_files=True, key="file_maps")
            _ = st.toggle("✨ Auto-clean (disarankan)", value=True, key="clean_maps")
            run = st.button("🚀 Proses Data Google Maps", type="primary", use_container_width=True)

        with col2:
            section("🧾 Format Kolom", "Sistem toleran walau nama kolom beda.")
            st.code("foto_url, nama_usaha, alamat, no_telepon, latitude, longitude, link", language="text")
            st.caption("Kalau beda nama kolom, sistem tetap coba map otomatis (toleran).")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Google Maps terlebih dahulu.")
        else:
            with st.status("Memproses data Google Maps…", expanded=True) as status:
                try:
                    df_raw, _total_rows = read_csv_files(files)
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
    hero(
        "Export Master Data Gabungan",
        "Konsolidasi (Shopee, Tokopedia, Facebook, Google Maps) → 1 Excel, sheet terpisah.",
        badges=["1 klik export", "Sheet terpisah", "Header rapi", "Autofilter aktif"]
    )

    df_shp_ready = st.session_state.data_shopee is not None and not st.session_state.data_shopee.empty
    df_tkp_ready = st.session_state.data_tokped is not None and not st.session_state.data_tokped.empty
    df_fb_ready = st.session_state.data_fb is not None and not st.session_state.data_fb.empty
    df_maps_ready = st.session_state.data_maps is not None and not st.session_state.data_maps.empty

    if not (df_shp_ready or df_tkp_ready or df_fb_ready or df_maps_ready):
        st.warning("⚠️ Belum ada data. Silakan proses dulu di menu Shopee/Tokopedia/Facebook/Google Maps.")
    else:
        with st.container(border=True):
            section("✅ Data Siap Dikonsolidasi", "Ringkasan jumlah data per sumber.")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📦 Shopee", fmt_int_id(len(st.session_state.data_shopee)) if df_shp_ready else 0)
            c2.metric("📦 Tokopedia", fmt_int_id(len(st.session_state.data_tokped)) if df_tkp_ready else 0)
            c3.metric("📦 Facebook", fmt_int_id(len(st.session_state.data_fb)) if df_fb_ready else 0)
            c4.metric("📦 Google Maps", fmt_int_id(len(st.session_state.data_maps)) if df_maps_ready else 0)
            st.caption("Output: 1 file Excel berisi sheet terpisah per sumber + autofilter + header rapi.")

        sheets = {}
        if df_shp_ready:
            sheets["Data Shopee"] = st.session_state.data_shopee
        if df_tkp_ready:
            sheets["Data Tokopedia"] = st.session_state.data_tokped
        if df_fb_ready:
            sheets["Data Facebook"] = st.session_state.data_fb
        if df_maps_ready:
            sheets["Data Google Maps"] = st.session_state.data_maps

        excel_bytes = df_to_excel_bytes(sheets)

        with st.container(border=True):
            section("⬇️ Unduh File Master", "Klik tombol untuk download Excel gabungan.")
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
    f"""
<div class="footer">
  <b>UMKM Toolkit</b> • Streamlit • Premium Orange Glass • Export Excel Bersih<br/>
  <span style="opacity:.75;">© {datetime.date.today().year} BPS • Dashboard internal</span>
</div>
""",
    unsafe_allow_html=True,
)
