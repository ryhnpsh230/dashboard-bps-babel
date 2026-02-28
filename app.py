import streamlit as st
import pandas as pd
import re
import io
import datetime
import os
import numpy as np
import plotly.express as px

# ======================================================================================
# CONFIG
# ======================================================================================
APP_TITLE = "Dashboard UMKM BPS"
APP_ICON = "🏛️"

BPS_OREN_UTAMA = "#FF6F00"
BPS_PAPER = "rgba(0,0,0,0)"
BPS_PALETTE = ["#FF6F00", "#FFA000", "#FFB300", "#FFC107", "#263238", "#37474F", "#455A64"]

PLACEHOLDER = "Pemilik tidak mencantumkan"
PHONE_EMPTY = "Pemilik belum meletakkan nomor"

# ======================================================================================
# PAGE SETUP
# ======================================================================================
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide", initial_sidebar_state="expanded")

# ======================================================================================
# CSS (Modern glass)
# ======================================================================================
st.markdown(
    f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: radial-gradient(1200px 700px at 10% 10%, rgba(255,111,0,.22) 0%, rgba(255,111,0,0) 60%),
                radial-gradient(900px 600px at 90% 20%, rgba(255,193,7,.16) 0%, rgba(255,193,7,0) 55%),
                linear-gradient(135deg, #0b0b0c 0%, #0f0f12 60%, #080809 100%) !important;
    background-attachment: fixed !important;
}}
[data-testid="stHeader"] {{ background: rgba(0,0,0,0) !important; }}
.block-container {{ padding-top: 1.2rem; padding-bottom: 2.2rem; }}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(14,14,16,.96) 0%, rgba(12,12,13,.98) 55%, rgba(9,9,10,.98) 100%) !important;
    border-right: 1px solid rgba(255,111,0,.35);
    box-shadow: 8px 0 28px rgba(0,0,0,.35);
}}
[data-testid="stSidebar"] * {{ color: #f3f3f3 !important; }}

div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,111,0,0.28) !important;
    border-radius: 16px;
    padding: 18px 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,.28);
    backdrop-filter: blur(10px);
}}

.bps-banner {{
    border-radius: 18px;
    padding: 22px 26px;
    margin: 2px 0 18px 0;
    background: linear-gradient(135deg, rgba(255,111,0,.18) 0%, rgba(255,193,7,.10) 45%, rgba(255,255,255,.035) 100%);
    border: 1px solid rgba(255,111,0,.25);
    box-shadow: 0 14px 40px rgba(0,0,0,.30);
    backdrop-filter: blur(12px);
}}
.bps-kicker {{
    letter-spacing: 2px; text-transform: uppercase; font-weight: 700; font-size: .78rem;
    color: rgba(255,193,7,.95); margin-bottom: 6px;
}}
.bps-title {{ font-size: 2.05rem; font-weight: 900; margin: 0 0 6px 0; color: #ffffff; }}
.bps-subtitle {{ margin: 0; color: rgba(230,230,230,.92); font-size: 1.02rem; }}

div[data-testid="metric-container"] {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,111,0,0.25);
    border-left: 6px solid {BPS_OREN_UTAMA};
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,.22);
    backdrop-filter: blur(10px);
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 10px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,111,0,.18);
    padding: 10px;
    border-radius: 14px;
    backdrop-filter: blur(10px);
}}
.stTabs [data-baseweb="tab"] {{
    height: 46px; border-radius: 12px; padding: 0 16px;
    background: rgba(255,255,255,0.02); color: rgba(235,235,235,.85);
}}
.stTabs [aria-selected="true"] {{
    background: {BPS_OREN_UTAMA} !important;
    color: white !important; font-weight: 900;
    box-shadow: 0 12px 34px rgba(255,111,0,.28);
}}

div[data-testid="stDownloadButton"] button,
.stButton > button {{
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    background: rgba(255,111,0,.85) !important;
    color: white !important;
    font-weight: 800 !important;
    height: 46px !important;
    box-shadow: 0 12px 34px rgba(255,111,0,.20);
}}
div[data-testid="stDownloadButton"] button:hover,
.stButton > button:hover {{
    filter: brightness(1.05);
    box-shadow: 0 18px 46px rgba(255,111,0,.26);
}}

[data-testid="stDataFrame"] {{ border-radius: 14px; overflow: hidden; }}
</style>
""",
    unsafe_allow_html=True,
)

# ======================================================================================
# UI helpers
# ======================================================================================
def banner(title: str, subtitle: str):
    st.markdown(
        f"""
<div class="bps-banner">
  <div class="bps-kicker">🏛️ BADAN PUSAT STATISTIK</div>
  <div class="bps-title">{title}</div>
  <p class="bps-subtitle">{subtitle}</p>
</div>
""",
        unsafe_allow_html=True,
    )

def fmt_int_id(n) -> str:
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return "0"

# ======================================================================================
# Cleaners
# ======================================================================================
def clean_placeholder_to_empty(x: str) -> str:
    s = "" if x is None else str(x).strip()
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

def to_float_safe(v):
    if v is None:
        return np.nan
    s = str(v).strip()
    if not s or s.lower() in ["nan", "none", "null"]:
        return np.nan
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return np.nan

# ======================================================================================
# Google Maps CSV cleaner (tolerant)
# ======================================================================================
def clean_maps_dataframe(df_raw: pd.DataFrame):
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

    # keep numeric
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

def read_csv_files(files):
    dfs = []
    for f in files:
        dfs.append(pd.read_csv(f, dtype=str, on_bad_lines="skip"))
    return (pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame())

# ======================================================================================
# Map builder (100% render mode + optional tile mode)
# ======================================================================================
def _decorate_points(df_plot: pd.DataFrame) -> pd.DataFrame:
    df_plot = df_plot.copy()
    df_plot["has_phone"] = df_plot["No Telepon"].astype(str).fillna("").str.strip().str.len() > 0
    df_plot["has_link"] = df_plot["Link"].astype(str).fillna("").str.strip().str.len() > 0

    def quality(row):
        if row["has_phone"] and row["has_link"]:
            return "Lengkap (Telp+Link)"
        if row["has_phone"]:
            return "Ada Telp"
        if row["has_link"]:
            return "Ada Link"
        return "Minimal"

    df_plot["quality"] = df_plot.apply(quality, axis=1)

    df_plot["marker_size"] = 10
    df_plot.loc[df_plot["has_link"], "marker_size"] = 12
    df_plot.loc[df_plot["has_phone"], "marker_size"] = 14
    df_plot.loc[df_plot["has_phone"] & df_plot["has_link"], "marker_size"] = 16
    return df_plot

def build_map_safe_no_tiles(df_maps: pd.DataFrame):
    """
    100% aman: tidak butuh tiles eksternal -> tidak akan 403.
    """
    df_plot = df_maps.dropna(subset=["Latitude", "Longitude"]).copy()
    df_plot = df_plot[(df_plot["Latitude"].between(-90, 90)) & (df_plot["Longitude"].between(-180, 180))].copy()
    if df_plot.empty:
        return None

    df_plot = _decorate_points(df_plot)

    fig = px.scatter_geo(
        df_plot,
        lat="Latitude",
        lon="Longitude",
        color="quality",
        size="marker_size",
        size_max=18,
        hover_name="Nama Usaha",
        hover_data={
            "Alamat": True,
            "No Telepon": True,
            "Link": True,
            "Latitude": ":.6f",
            "Longitude": ":.6f",
            "quality": True,
            "marker_size": False,
            "has_phone": False,
            "has_link": False,
        },
        projection="natural earth",
        height=590,
        color_discrete_sequence=BPS_PALETTE,
    )

    # fokus ke area data (update geo ranges)
    lat_min, lat_max = float(df_plot["Latitude"].min()), float(df_plot["Latitude"].max())
    lon_min, lon_max = float(df_plot["Longitude"].min()), float(df_plot["Longitude"].max())
    lat_pad = max((lat_max - lat_min) * 0.25, 0.2)
    lon_pad = max((lon_max - lon_min) * 0.25, 0.2)

    fig.update_geos(
        lataxis_range=[lat_min - lat_pad, lat_max + lat_pad],
        lonaxis_range=[lon_min - lon_pad, lon_max + lon_pad],
        showland=True,
        showocean=True,
        showlakes=True,
        showcountries=False,
        showcoastlines=True,
        showframe=False,
        bgcolor="rgba(0,0,0,0)",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=BPS_PAPER,
        plot_bgcolor=BPS_PAPER,
        font=dict(color="white"),
        legend=dict(
            title="Kualitas Data",
            bgcolor="rgba(0,0,0,0.35)",
            bordercolor="rgba(255,255,255,0.15)",
            borderwidth=1,
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
        ),
    )

    fig.update_traces(marker=dict(opacity=0.92, line=dict(width=1)))
    return fig

def build_map_tiles_optional(df_maps: pd.DataFrame, style: str = "carto-darkmatter"):
    """
    Mode tiles (bisa lebih cakep), tapi tergantung jaringan.
    """
    df_plot = df_maps.dropna(subset=["Latitude", "Longitude"]).copy()
    df_plot = df_plot[(df_plot["Latitude"].between(-90, 90)) & (df_plot["Longitude"].between(-180, 180))].copy()
    if df_plot.empty:
        return None

    df_plot = _decorate_points(df_plot)

    lat_min, lat_max = float(df_plot["Latitude"].min()), float(df_plot["Latitude"].max())
    lon_min, lon_max = float(df_plot["Longitude"].min()), float(df_plot["Longitude"].max())
    lat_span = max(lat_max - lat_min, 0.01)
    lon_span = max(lon_max - lon_min, 0.01)
    lat_pad = max(lat_span * 0.15, 0.02)
    lon_pad = max(lon_span * 0.15, 0.02)

    fig = px.scatter_mapbox(
        df_plot,
        lat="Latitude",
        lon="Longitude",
        color="quality",
        size="marker_size",
        size_max=18,
        hover_name="Nama Usaha",
        hover_data={
            "Alamat": True,
            "No Telepon": True,
            "Link": True,
            "Latitude": ":.6f",
            "Longitude": ":.6f",
            "quality": True,
            "marker_size": False,
            "has_phone": False,
            "has_link": False,
        },
        height=590,
        color_discrete_sequence=BPS_PALETTE,
    )

    fig.update_layout(
        mapbox_style=style,  # carto-darkmatter / carto-positron
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=BPS_PAPER,
        plot_bgcolor=BPS_PAPER,
        font=dict(color="white"),
        legend=dict(
            title="Kualitas Data",
            bgcolor="rgba(0,0,0,0.35)",
            bordercolor="rgba(255,255,255,0.15)",
            borderwidth=1,
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
        ),
        mapbox=dict(
            bounds=dict(
                west=lon_min - lon_pad,
                east=lon_max + lon_pad,
                south=lat_min - lat_pad,
                north=lat_max + lat_pad,
            )
        ),
    )
    fig.update_traces(marker=dict(opacity=0.92, line=dict(width=1)))
    return fig

# ======================================================================================
# Excel exporter
# ======================================================================================
def df_to_excel_bytes(sheet_name: str, df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        wb = writer.book
        header_fmt = wb.add_format({"bold": True, "bg_color": BPS_OREN_UTAMA, "font_color": "white"})
        float_fmt = wb.add_format({"num_format": "0.000000"})

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
            if col.lower() in ["latitude", "longitude"]:
                ws.set_column(i, i, 14, float_fmt)

    return buf.getvalue()

# ======================================================================================
# SESSION
# ======================================================================================
if "data_maps" not in st.session_state:
    st.session_state.data_maps = None
if "audit_maps" not in st.session_state:
    st.session_state.audit_maps = {}

# ======================================================================================
# SIDEBAR
# ======================================================================================
with st.sidebar:
    st.markdown(f"### {APP_ICON} {APP_TITLE}")
    st.caption("Modern glass UI • Google Maps cleaner • Map anti-403")
    st.divider()

    menu = st.radio("🧭 Navigasi", ["📍 Google Maps", "📦 Export"], index=0)
    st.divider()
    st.checkbox("Mode cepat (skip render berat)", value=False, key="fast_mode")

# ======================================================================================
# PAGE: GOOGLE MAPS
# ======================================================================================
if menu == "📍 Google Maps":
    banner("Dashboard UMKM — Google Maps", "Upload CSV hasil ekstensi → auto-clean → peta pasti tampil (anti 403)")

    with st.container(border=True):
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV Google Maps", type=["csv"], accept_multiple_files=True, key="file_maps")
            map_mode = st.radio(
                "🗺️ Mode Peta",
                ["✅ Aman (tanpa tile) — 100% jalan", "✨ Tile (lebih realistis) — bisa kena 403"],
                index=0,
            )
            tile_style = "carto-darkmatter"
            if "Tile" in map_mode:
                tile_style = st.selectbox("🎨 Style Tile", ["carto-darkmatter", "carto-positron"], index=0)

            run = st.button("🚀 Proses Data Google Maps", type="primary", use_container_width=True)

        with col2:
            st.subheader("🧾 Format Kolom (disarankan)")
            st.code("foto_url, nama_usaha, alamat, no_telepon, latitude, longitude, link", language="text")
            st.caption("Kalau beda nama kolom, sistem tetap coba mapping otomatis (toleran).")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Google Maps terlebih dahulu.")
        else:
            with st.status("Memproses data Google Maps…", expanded=True) as status:
                try:
                    df_raw = read_csv_files(files)
                    df_clean, audit = clean_maps_dataframe(df_raw)

                    st.session_state.data_maps = df_clean
                    st.session_state.audit_maps = {
                        "file_count": len(files),
                        **audit,
                    }

                    status.update(label="✅ Selesai memproses Google Maps", state="complete", expanded=False)
                    st.toast(f"Google Maps: {fmt_int_id(len(df_clean))} baris siap dianalisis", icon="✅")

                except Exception as e:
                    status.update(label="❌ Gagal memproses Google Maps", state="error", expanded=True)
                    st.exception(e)

    df_maps = st.session_state.data_maps
    if df_maps is not None and not df_maps.empty:
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🧹 Data Bersih", "📑 Audit"])

        with tab1:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📌 Total Data", fmt_int_id(len(df_maps)))
            m2.metric("📍 Koordinat Valid", fmt_int_id(df_maps["Latitude"].notna().sum()))
            m3.metric("🔗 Link Valid", fmt_int_id((df_maps["Link"].astype(str).str.strip().str.len() > 0).sum()))
            m4.metric("☎️ No Telp Valid", fmt_int_id((df_maps["No Telepon"].astype(str).str.strip().str.len() > 0).sum()))

            if not st.session_state.get("fast_mode"):
                # 100% success: safe mode doesn't load external tiles
                if "Aman" in map_mode:
                    fig = build_map_safe_no_tiles(df_maps)
                    if fig is None:
                        st.info("Tidak ada koordinat valid untuk ditampilkan.")
                    else:
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption("Mode Aman: tidak menggunakan tile eksternal → anti 403.")
                else:
                    # tile mode: might 403 depending on network; fallback to safe mode
                    try:
                        fig = build_map_tiles_optional(df_maps, style=tile_style)
                        if fig is None:
                            st.info("Tidak ada koordinat valid untuk ditampilkan.")
                        else:
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        st.warning("Tile gagal (kemungkinan 403). Otomatis fallback ke Mode Aman (tanpa tile).")
                        fig2 = build_map_safe_no_tiles(df_maps)
                        if fig2 is not None:
                            st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            st.dataframe(df_maps, use_container_width=True, hide_index=True, height=460)

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
                st.warning("Kolom tidak ditemukan (diisi kosong): " + ", ".join(a["missing_cols"]))

# ======================================================================================
# PAGE: EXPORT
# ======================================================================================
elif menu == "📦 Export":
    banner("Export Data Google Maps", "Unduh Excel/CSV hasil cleaning")

    df_maps = st.session_state.data_maps
    if df_maps is None or df_maps.empty:
        st.warning("Belum ada data. Silakan upload & proses dulu di menu Google Maps.")
    else:
        with st.container(border=True):
            st.subheader("⬇️ Unduh File")
            excel_bytes = df_to_excel_bytes("Data Google Maps", df_maps)
            st.download_button(
                "⬇️ Unduh Excel (Bersih)",
                data=excel_bytes,
                file_name=f"UMKM_GoogleMaps_Bersih_{datetime.date.today()}.xlsx",
                use_container_width=True,
                type="primary",
            )
            csv_bytes = df_maps.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Unduh CSV (Bersih)",
                data=csv_bytes,
                file_name=f"UMKM_GoogleMaps_Bersih_{datetime.date.today()}.csv",
                use_container_width=True,
            )

# ======================================================================================
# FOOTER
# ======================================================================================
st.markdown(
    "<div style='margin-top:22px; opacity:.75; font-size:.86rem;'>"
    "Built with Streamlit • Map Anti-403 (Safe Geo) • Export Excel/CSV Bersih"
    "</div>",
    unsafe_allow_html=True,
)
