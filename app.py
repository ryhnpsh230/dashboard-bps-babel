import streamlit as st
import pandas as pd
import re
import io
import requests
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os

st.set_page_config(
    page_title="UMKM Intelligence · BPS Babel",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

:root {
    --shopee:   #FF6B35;
    --tokped:   #00C853;
    --facebook: #1877F2;
    --gabungan: #6C63FF;
    --ink:      #0A0A0A;
    --ink-2:    #3D3D3D;
    --ink-3:    #8A8A8A;
    --paper:    #FAFAF8;
    --line:     #E8E8E4;
    --white:    #FFFFFF;
}

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}

/* ── MAIN BACKGROUND ── */
.main { background: var(--paper); }
.main .block-container {
    padding: 0 2.5rem 4rem 2.5rem;
    max-width: 1440px;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: none;
}
[data-testid="stSidebar"] * { color: #E8E8E4 !important; }
[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    padding: 9px 14px !important;
    border-radius: 6px !important;
    border: 1px solid transparent !important;
    transition: all 0.18s !important;
    cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.12) !important;
}
[data-testid="stSidebar"] .stRadio label[data-testid="stMarkdownContainer"] {
    background: rgba(255,255,255,0.1) !important;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family: 'DM Serif Display', serif !important;
    color: #FAFAF8 !important;
    letter-spacing: -0.01em !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: var(--white) !important;
    color: var(--ink) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    padding: 0.65rem 1rem !important;
    transition: all 0.18s !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #E8E8E4 !important;
    transform: translateY(-1px) !important;
}

/* ── PAGE HEADER ── */
.page-header {
    padding: 3rem 0 2rem 0;
    border-bottom: 2px solid var(--ink);
    margin-bottom: 2.5rem;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
}
.page-header-left {}
.page-eyebrow {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-3);
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.page-eyebrow .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.page-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3.2rem;
    font-weight: 400;
    line-height: 1.05;
    letter-spacing: -0.03em;
    color: var(--ink);
    margin: 0;
}
.page-title em {
    font-style: italic;
    color: var(--platform-color, var(--ink));
}
.page-subtitle {
    font-size: 0.88rem;
    color: var(--ink-3);
    margin-top: 0.75rem;
    font-weight: 400;
    line-height: 1.6;
}
.page-header-right {
    text-align: right;
    flex-shrink: 0;
}
.platform-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--platform-color, var(--ink));
    color: white !important;
    padding: 8px 18px;
    border-radius: 100px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── METRIC CARDS ── */
[data-testid="stMetric"] {
    background: var(--white) !important;
    border: 1.5px solid var(--line) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    transition: border-color 0.2s, transform 0.2s !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]:hover {
    border-color: var(--ink) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--platform-color, var(--ink));
    border-radius: 12px 12px 0 0;
}
[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--ink-3) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2.4rem !important;
    font-weight: 400 !important;
    color: var(--ink) !important;
    line-height: 1.1 !important;
    letter-spacing: -0.03em !important;
}

/* ── SECTION LABEL ── */
.section-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--ink-3);
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--line);
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── TABS ── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1.5px solid var(--line) !important;
    gap: 0 !important;
    background: transparent !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--ink-3) !important;
    padding: 0.7rem 1.4rem !important;
    border-radius: 0 !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1.5px !important;
    background: transparent !important;
    transition: all 0.18s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--ink) !important;
    border-bottom-color: var(--ink) !important;
}
[data-testid="stTabs"] [role="tab"]:hover {
    color: var(--ink) !important;
    background: rgba(0,0,0,0.02) !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border: 1.5px solid var(--line) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] > button {
    background: var(--ink) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    transition: all 0.18s !important;
    padding: 0.7rem 1.5rem !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #2a2a2a !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2) !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border: 1.5px solid !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] > div {
    border: 1.5px dashed rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
    background: rgba(255,255,255,0.04) !important;
}

/* ── SLIDER ── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: var(--ink) !important;
    border-color: var(--ink) !important;
}

/* ── MULTISELECT ── */
[data-baseweb="tag"] {
    background: var(--ink) !important;
    border-radius: 4px !important;
}

/* ── PROGRESS ── */
[data-testid="stProgress"] > div > div > div {
    background: var(--ink) !important;
    border-radius: 99px !important;
}

/* ── HR ── */
hr { border: none !important; border-top: 1.5px solid var(--line) !important; margin: 2rem 0 !important; }

/* ── PLATFORM COLOR CONTEXTS ── */
.ctx-shopee   { --platform-color: var(--shopee); }
.ctx-tokped   { --platform-color: var(--tokped); }
.ctx-facebook { --platform-color: var(--facebook); }
.ctx-gabungan { --platform-color: var(--gabungan); }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
if "data_shopee" not in st.session_state: st.session_state.data_shopee = None
if "audit_shopee" not in st.session_state: st.session_state.audit_shopee = {}
if "data_tokped" not in st.session_state: st.session_state.data_tokped = None
if "audit_tokped" not in st.session_state: st.session_state.audit_tokped = {}
if "data_fb" not in st.session_state: st.session_state.data_fb = None
if "audit_fb" not in st.session_state: st.session_state.audit_fb = {}

# ── FUNGSI DETEKSI TIPE USAHA ──
def deteksi_tipe_usaha(nama_toko):
    if pd.isna(nama_toko) or nama_toko in ["Tidak Dilacak", "Toko CSV", "Anonim", ""]:
        return "Tidak Terdeteksi (Butuh Nama Toko)"
    if str(nama_toko) == "FB Seller":
        return "Perorangan (Facebook)"
    nama_lower = str(nama_toko).lower()
    keyword_fisik = ['toko', 'warung', 'grosir', 'mart', 'apotek', 'cv.', 'pt.', 'official', 'agen', 'distributor', 'kios', 'kedai', 'supermarket', 'minimarket', 'cabang', 'jaya', 'abadi', 'makmur', 'motor', 'mobil', 'bengkel', 'snack', 'store']
    for kata in keyword_fisik:
        if kata in nama_lower:
            return "Ada Toko Fisik"
    return "Murni Online (Rumahan)"

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
        <div style="padding: 1.8rem 0.5rem 1.2rem 0.5rem;">
            <div style="font-size:0.6rem; font-weight:700; letter-spacing:0.2em; text-transform:uppercase; color:#555; margin-bottom:0.8rem;">
                Badan Pusat Statistik
            </div>
            <div style="font-family:'DM Serif Display',serif; font-size:1.6rem; color:#FAFAF8; line-height:1.2; letter-spacing:-0.02em;">
                UMKM<br><em style="color:#aaa; font-style:italic;">Intelligence</em>
            </div>
            <div style="font-size:0.72rem; color:#666; margin-top:0.5rem;">Bangka Belitung</div>
        </div>
        <div style="height:1px; background:#222; margin:0 0 1.2rem 0;"></div>
    """, unsafe_allow_html=True)

    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)

    st.markdown('<div style="font-size:0.62rem; font-weight:700; letter-spacing:0.16em; text-transform:uppercase; color:#555; margin-bottom:0.6rem;">Navigasi</div>', unsafe_allow_html=True)
    halaman = st.radio("", ["🟠 Shopee", "🟢 Tokopedia", "🔵 Facebook FB", "📊 Export Gabungan"], label_visibility="collapsed")

    st.markdown("""
        <div style="height:1px; background:#222; margin:1.5rem 0 1rem 0;"></div>
        <div style="font-size:0.65rem; color:#444; line-height:1.8;">
            Versi 2.0<br>
            © 2025 BPS Indonesia
        </div>
    """, unsafe_allow_html=True)

babel_keys = ["pangkal", "bangka", "belitung", "sungailiat", "mentok", "muntok", "koba", "toboali", "manggar", "tanjung pandan", "tanjungpandan"]

# helper: inject platform color for metric top-border trick via wrapper
def metric_wrap(color):
    st.markdown(f'<style>[data-testid="stMetric"]::before{{background:{color}!important}}</style>', unsafe_allow_html=True)

# ==============================================================================
#  SHOPEE
# ==============================================================================
if halaman == "🟠 Shopee":
    metric_wrap("#FF6B35")
    st.markdown("""
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-eyebrow">
                <span class="dot" style="background:#FF6B35"></span>
                Shopee Marketplace · Bangka Belitung
            </div>
            <h1 class="page-title">Data UMKM<br><em style="color:#FF6B35">Shopee</em></h1>
            <p class="page-subtitle">Ekstraksi & klasifikasi data penjual UMKM<br>dari platform Shopee wilayah Bangka Belitung</p>
        </div>
        <div class="page-header-right">
            <span class="platform-badge" style="background:#FF6B35">🛍 Shopee</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div style="height:1px;background:#222;margin:0.5rem 0 1rem 0"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:#555;margin-bottom:0.8rem">Input Shopee</div>', unsafe_allow_html=True)
        files_shopee = st.file_uploader("Upload CSV Shopee", type=["csv"], accept_multiple_files=True, key="file_shp")
        mode_api_shp = st.checkbox("🔍 Deteksi Nama Toko via API", key="api_shp", value=True)
        st.button("▶ Proses Shopee", type="primary", use_container_width=True, key="btn_shp_dummy")
        run_shp = st.session_state.get("btn_shp_dummy", False)

    if st.sidebar.button("🚀 Proses Shopee", type="primary", use_container_width=True, key="btn_shp"):
        if not files_shopee:
            st.error("⚠️ Unggah file CSV Shopee dulu!")
        elif not mode_api_shp:
            st.warning("⚠️ Centang 'Deteksi Nama Toko via API' untuk klasifikasi tipe usaha.")
        else:
            with st.spinner("Memproses data..."):
                try:
                    total_semua_baris = 0
                    for f in files_shopee:
                        df_temp = pd.read_csv(f, dtype=str, on_bad_lines="skip")
                        total_semua_baris += len(df_temp)
                        f.seek(0)
                    hasil, total_baris, err_h, luar_wilayah, baris_diproses = [], 0, 0, 0, 0
                    status_text = st.empty()
                    progress_bar = st.progress(0)
                    for idx, file in enumerate(files_shopee):
                        df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                        total_baris += len(df_raw)
                        if "Link" in df_raw.columns and "Nama Produk" in df_raw.columns:
                            col_link, col_nama, col_harga, col_wilayah = "Link", "Nama Produk", "Harga", "Wilayah"
                        else:
                            col_link = next((c for c in df_raw.columns if 'href' in c.lower()), df_raw.columns[0])
                            col_nama = next((c for c in df_raw.columns if 'whitespace-normal' in c.lower()), df_raw.columns[3])
                            col_harga = next((c for c in df_raw.columns if 'font-medium 2' in c.lower()), df_raw.columns[4])
                            idx_w = 7 if len(df_raw.columns) > 7 else len(df_raw.columns) - 1
                            col_wilayah = next((c for c in df_raw.columns if 'ml-[3px]' in c.lower()), df_raw.columns[idx_w])
                        for i in range(len(df_raw)):
                            row = df_raw.iloc[i]
                            link = str(row[col_link]); nama = str(row[col_nama])
                            harga_str = str(row[col_harga]); lokasi_shopee = str(row[col_wilayah]).title()
                            if not any(k in lokasi_shopee.lower() for k in babel_keys):
                                luar_wilayah += 1; baris_diproses += 1; continue
                            try:
                                harga_bersih = harga_str.replace('.', '').replace(',', '')
                                angka_list = re.findall(r'\d+', harga_bersih)
                                val_h = int(angka_list[0]) if angka_list else 0
                                if val_h > 1000000000: val_h = 0
                            except: val_h, err_h = 0, err_h + 1
                            toko = "Tidak Dilacak"
                            if mode_api_shp:
                                match = re.search(r"i\.(\d+)\.", link)
                                if match:
                                    try:
                                        res = requests.get(f"https://shopee.co.id/api/v4/shop/get_shop_base?shopid={match.group(1)}", headers={"User-Agent":"Mozilla/5.0"}, timeout=2)
                                        if res.status_code == 200: toko = res.json().get("data",{}).get("name", "Anonim")
                                    except: pass
                            hasil.append({"Nama Toko": toko, "Nama Produk": nama, "Harga": val_h, "Wilayah": lokasi_shopee, "Tipe Usaha": deteksi_tipe_usaha(toko), "Link": link})
                            baris_diproses += 1
                            if baris_diproses % 5 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses / total_semua_baris, 1.0)
                                progress_bar.progress(pct)
                                status_text.markdown(f"**⏳ Mengekstrak** {baris_diproses}/{total_semua_baris} baris ({int(pct*100)}%)")
                    status_text.empty(); progress_bar.empty()
                    st.session_state.data_shopee = pd.DataFrame(hasil)
                    st.session_state.audit_shopee = {"total": total_baris, "valid": len(hasil), "file_count": len(files_shopee), "error_harga": err_h, "luar": luar_wilayah}
                    st.success(f"✅ {len(hasil)} data Shopee berhasil diproses!")
                except Exception as e:
                    st.error(f"Error: {e}")

    df_shp = st.session_state.data_shopee
    if df_shp is not None and not df_shp.empty:
        st.markdown('<div class="section-label">⚙ Filter Data</div>', unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns([1,1,1])
        with col_f1: f_wil = st.multiselect("Wilayah", options=sorted(df_shp["Wilayah"].unique()), default=sorted(df_shp["Wilayah"].unique()), key="f_wil_shp")
        with col_f2: f_tipe = st.multiselect("Tipe Usaha", options=sorted(df_shp["Tipe Usaha"].unique()), default=sorted(df_shp["Tipe Usaha"].unique()), key="f_tipe_shp")
        with col_f3:
            max_h = int(df_shp["Harga"].max()) if df_shp["Harga"].max() > 0 else 1000000
            f_hrg = st.slider("Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_shp")
        df_f = df_shp[df_shp["Wilayah"].isin(f_wil) & df_shp["Tipe Usaha"].isin(f_tipe) & (df_shp["Harga"] >= f_hrg[0]) & (df_shp["Harga"] <= f_hrg[1])]

        tab1, tab2, tab3 = st.tabs(["RINGKASAN", "DATABASE", "AUDIT LOG"])
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Data", f"{len(df_f):,}".replace(",", "."))
            c2.metric("Murni Online", f"{len(df_f[df_f['Tipe Usaha'] == 'Murni Online (Rumahan)']):,}".replace(",", "."))
            c3.metric("Wilayah", f"{df_f['Wilayah'].nunique()}")
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", title="Komposisi Tipe Usaha", hole=0.5,
                                 color_discrete_sequence=["#FF6B35","#FFB299","#FFD9CC","#4A4A4A"])
                    fig.update_layout(font_family="DM Sans", title_font_size=13, title_font_color="#3D3D3D",
                                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                      legend=dict(font=dict(size=11)))
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    fig2 = px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'),
                                  x="Wilayah", y="Jumlah", title="Usaha per Wilayah",
                                  color_discrete_sequence=["#FF6B35"])
                    fig2.update_layout(font_family="DM Sans", title_font_size=13, title_font_color="#3D3D3D",
                                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAF8",
                                       xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#E8E8E4"),
                                       showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)
        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=370)
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_f.to_excel(writer, index=False, sheet_name="Data Shopee")
                    wb, ws = writer.book, writer.sheets["Data Shopee"]
                    for col_num, value in enumerate(df_f.columns.values):
                        ws.write(0, col_num, value, wb.add_format({'bold': True, 'bg_color': '#FF6B35', 'font_color': 'white', 'border': 0}))
                    ws.set_column('A:A', 25); ws.set_column('B:B', 50)
                    ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'}))
                    ws.set_column('D:D', 20); ws.set_column('E:E', 25); ws.set_column('F:F', 50)
                st.download_button("↓ Download Excel Shopee", data=buf.getvalue(), file_name=f"UMKM_Shopee_{datetime.date.today()}.xlsx", type="primary")
        with tab3:
            audit = st.session_state.audit_shopee
            st.info(f"**File diproses:** {audit.get('file_count',0)} CSV")
            st.success(f"**Data valid:** {audit.get('valid',0)} baris")

# ==============================================================================
#  TOKOPEDIA
# ==============================================================================
elif halaman == "🟢 Tokopedia":
    metric_wrap("#00C853")
    st.markdown("""
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-eyebrow">
                <span class="dot" style="background:#00C853"></span>
                Tokopedia Marketplace · Bangka Belitung
            </div>
            <h1 class="page-title">Data UMKM<br><em style="color:#00C853">Tokopedia</em></h1>
            <p class="page-subtitle">Ekstraksi & klasifikasi data penjual UMKM<br>dari platform Tokopedia wilayah Bangka Belitung</p>
        </div>
        <div class="page-header-right">
            <span class="platform-badge" style="background:#00C853">🛒 Tokopedia</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div style="height:1px;background:#222;margin:0.5rem 0 1rem 0"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:#555;margin-bottom:0.8rem">Input Tokopedia</div>', unsafe_allow_html=True)
        files_tokped = st.file_uploader("Upload CSV Tokopedia", type=["csv"], accept_multiple_files=True, key="file_tkp")

    if st.sidebar.button("🚀 Proses Tokopedia", type="primary", use_container_width=True):
        if not files_tokped:
            st.error("⚠️ Unggah file CSV Tokopedia dulu!")
        else:
            with st.spinner("Memproses data..."):
                try:
                    total_semua_baris = 0
                    for f in files_tokped:
                        df_temp = pd.read_csv(f, dtype=str, on_bad_lines="skip")
                        total_semua_baris += len(df_temp)
                        f.seek(0)
                    hasil, total_baris, err_h, luar_wilayah, baris_diproses = [], 0, 0, 0, 0
                    status_text = st.empty(); progress_bar = st.progress(0)
                    for idx, file in enumerate(files_tokped):
                        df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                        total_baris += len(df_raw)
                        if "Link" in df_raw.columns and "Nama Produk" in df_raw.columns:
                            col_links, col_namas, col_hargas, col_lokasis, col_tokos = ["Link"], ["Nama Produk"], ["Harga"], ["Wilayah"], ["Nama Toko"]
                        else:
                            col_links = [c for c in df_raw.columns if 'Ui5' in c]
                            col_namas = [c for c in df_raw.columns if '+tnoqZhn' in c]
                            col_hargas = [c for c in df_raw.columns if 'urMOIDHH' in c]
                            col_lokasis = [c for c in df_raw.columns if 'gxi+fs' in c]
                            col_tokos = [c for c in df_raw.columns if 'si3CN' in c]
                        max_items = max(len(col_links), len(col_namas), len(col_hargas), len(col_lokasis), len(col_tokos))
                        if max_items == 0: max_items = 1
                        for i in range(len(df_raw)):
                            for j in range(max_items):
                                try:
                                    link = str(df_raw.iloc[i][col_links[j]]) if j < len(col_links) else "nan"
                                    nama = str(df_raw.iloc[i][col_namas[j]]) if j < len(col_namas) else "nan"
                                    harga_str = str(df_raw.iloc[i][col_hargas[j]]) if j < len(col_hargas) else "0"
                                    lokasi_tokped = str(df_raw.iloc[i][col_lokasis[j]]).title() if j < len(col_lokasis) else "-"
                                    toko = str(df_raw.iloc[i][col_tokos[j]]) if j < len(col_tokos) else "Toko CSV"
                                    if link == 'nan' or nama == 'nan': continue
                                    if not any(k in lokasi_tokped.lower() for k in babel_keys):
                                        luar_wilayah += 1; continue
                                    try:
                                        harga_bersih = harga_str.replace('.', '').replace(',', '')
                                        angka_list = re.findall(r'\d+', harga_bersih)
                                        val_h = int(angka_list[0]) if angka_list else 0
                                        if val_h > 1000000000: val_h = 0
                                    except: val_h, err_h = 0, err_h + 1
                                    if val_h > 0:
                                        hasil.append({"Nama Toko": toko, "Nama Produk": nama, "Harga": val_h, "Wilayah": lokasi_tokped, "Tipe Usaha": deteksi_tipe_usaha(toko), "Link": link})
                                except Exception: continue
                            baris_diproses += 1
                            if baris_diproses % 5 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses / total_semua_baris, 1.0)
                                progress_bar.progress(pct)
                                status_text.markdown(f"**⏳ Mengekstrak** {baris_diproses}/{total_semua_baris} baris ({int(pct*100)}%)")
                    status_text.empty(); progress_bar.empty()
                    df_final = pd.DataFrame(hasil).drop_duplicates()
                    st.session_state.data_tokped = df_final
                    st.session_state.audit_tokped = {"total": total_baris, "valid": len(df_final), "file_count": len(files_tokped), "error_harga": err_h, "luar": luar_wilayah}
                    st.success(f"✅ {len(df_final)} data Tokopedia berhasil diekstrak!")
                except Exception as e:
                    st.error(f"Error: {e}")

    df_tkp = st.session_state.data_tokped
    if df_tkp is not None and not df_tkp.empty:
        st.markdown('<div class="section-label">⚙ Filter Data</div>', unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns([1,1,1])
        with col_f1: f_wil = st.multiselect("Wilayah", options=sorted(df_tkp["Wilayah"].unique()), default=sorted(df_tkp["Wilayah"].unique()), key="f_wil_tkp")
        with col_f2: f_tipe = st.multiselect("Tipe Usaha", options=sorted(df_tkp["Tipe Usaha"].unique()), default=sorted(df_tkp["Tipe Usaha"].unique()), key="f_tipe_tkp")
        with col_f3:
            max_h = int(df_tkp["Harga"].max()) if df_tkp["Harga"].max() > 0 else 1000000
            f_hrg = st.slider("Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_tkp")
        df_f = df_tkp[df_tkp["Wilayah"].isin(f_wil) & df_tkp["Tipe Usaha"].isin(f_tipe) & (df_tkp["Harga"] >= f_hrg[0]) & (df_tkp["Harga"] <= f_hrg[1])]

        tab1, tab2, tab3 = st.tabs(["RINGKASAN", "DATABASE", "AUDIT LOG"])
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Data", f"{len(df_f):,}".replace(",", "."))
            c2.metric("Murni Online", f"{len(df_f[df_f['Tipe Usaha'] == 'Murni Online (Rumahan)']):,}".replace(",", "."))
            c3.metric("Wilayah", f"{df_f['Wilayah'].nunique()}")
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", title="Komposisi Tipe Usaha", hole=0.5,
                                 color_discrete_sequence=["#00C853","#69F0AE","#B9F6CA","#4A4A4A"])
                    fig.update_layout(font_family="DM Sans", title_font_size=13, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    fig2 = px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Usaha per Wilayah", color_discrete_sequence=["#00C853"])
                    fig2.update_layout(font_family="DM Sans", title_font_size=13, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAF8", xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#E8E8E4"), showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)
        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=370)
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_f.to_excel(writer, index=False, sheet_name="Data Tokopedia")
                    wb, ws = writer.book, writer.sheets["Data Tokopedia"]
                    for col_num, value in enumerate(df_f.columns.values):
                        ws.write(0, col_num, value, wb.add_format({'bold': True, 'bg_color': '#00C853', 'font_color': 'white', 'border': 0}))
                    ws.set_column('A:A', 25); ws.set_column('B:B', 50)
                    ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'}))
                    ws.set_column('D:D', 20); ws.set_column('E:E', 25); ws.set_column('F:F', 50)
                st.markdown(f'<style>[data-testid="stDownloadButton"]>button{{background:#00C853!important}}</style>', unsafe_allow_html=True)
                st.download_button("↓ Download Excel Tokopedia", data=buf.getvalue(), file_name=f"UMKM_Tokopedia_{datetime.date.today()}.xlsx")
        with tab3:
            audit = st.session_state.audit_tokped
            st.info(f"**File diproses:** {audit.get('file_count',0)} CSV")

# ==============================================================================
#  FACEBOOK
# ==============================================================================
elif halaman == "🔵 Facebook FB":
    metric_wrap("#1877F2")
    st.markdown("""
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-eyebrow">
                <span class="dot" style="background:#1877F2"></span>
                Facebook Marketplace · Bangka Belitung
            </div>
            <h1 class="page-title">Data UMKM<br><em style="color:#1877F2">Facebook</em></h1>
            <p class="page-subtitle">Ekstraksi & klasifikasi data penjual UMKM<br>dari Facebook Marketplace wilayah Bangka Belitung</p>
        </div>
        <div class="page-header-right">
            <span class="platform-badge" style="background:#1877F2">📘 Facebook</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div style="height:1px;background:#222;margin:0.5rem 0 1rem 0"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:#555;margin-bottom:0.8rem">Input Facebook</div>', unsafe_allow_html=True)
        files_fb = st.file_uploader("Upload CSV Facebook", type=["csv"], accept_multiple_files=True, key="file_fb")

    if st.sidebar.button("🚀 Proses Facebook FB", type="primary", use_container_width=True):
        if not files_fb:
            st.error("⚠️ Unggah file CSV Facebook FB dulu!")
        else:
            with st.spinner("Memproses data..."):
                try:
                    total_semua_baris = 0
                    for f in files_fb:
                        df_temp = pd.read_csv(f, dtype=str, on_bad_lines="skip")
                        total_semua_baris += len(df_temp)
                        f.seek(0)
                    hasil, total_baris, err_h, luar_wilayah, baris_diproses = [], 0, 0, 0, 0
                    status_text = st.empty(); progress_bar = st.progress(0)
                    for idx, file in enumerate(files_fb):
                        df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                        total_baris += len(df_raw)
                        if "Link" in df_raw.columns and "Nama Produk" in df_raw.columns:
                            col_link, col_nama, col_harga, col_wilayah, col_toko = "Link", "Nama Produk", "Harga", "Wilayah", "Nama Toko"
                        else:
                            col_toko, col_nama, col_wilayah, col_harga, col_link = df_raw.columns[0], df_raw.columns[1], df_raw.columns[2], df_raw.columns[4], df_raw.columns[5]
                        for i in range(len(df_raw)):
                            row = df_raw.iloc[i]
                            link = str(row[col_link]); nama = str(row[col_nama])
                            harga_str = str(row[col_harga]); lokasi_fb = str(row[col_wilayah]).title()
                            toko = str(row.get(col_toko, "FB Seller"))
                            if not any(k in lokasi_fb.lower() for k in babel_keys):
                                luar_wilayah += 1; baris_diproses += 1; continue
                            try:
                                harga_bersih = harga_str.replace('.', '').replace(',', '')
                                angka_list = re.findall(r'\d+', harga_bersih)
                                val_h = int(angka_list[0]) if angka_list else 0
                                if val_h > 1000000000: val_h = 0
                            except: val_h, err_h = 0, err_h + 1
                            if val_h > 0:
                                hasil.append({"Nama Toko": toko, "Nama Produk": nama, "Harga": val_h, "Wilayah": lokasi_fb, "Tipe Usaha": deteksi_tipe_usaha(toko), "Link": link})
                            baris_diproses += 1
                            if baris_diproses % 5 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses / total_semua_baris, 1.0)
                                progress_bar.progress(pct)
                                status_text.markdown(f"**⏳ Mengekstrak** {baris_diproses}/{total_semua_baris} baris ({int(pct*100)}%)")
                    status_text.empty(); progress_bar.empty()
                    df_final = pd.DataFrame(hasil).drop_duplicates()
                    st.session_state.data_fb = df_final
                    st.session_state.audit_fb = {"total": total_baris, "valid": len(df_final), "file_count": len(files_fb), "error_harga": err_h, "luar": luar_wilayah}
                    st.success(f"✅ {len(df_final)} data Facebook FB berhasil diekstrak!")
                except Exception as e:
                    st.error(f"Error: {e}")

    df_fb = st.session_state.data_fb
    if df_fb is not None and not df_fb.empty:
        st.markdown('<div class="section-label">⚙ Filter Data</div>', unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns([1,1,1])
        with col_f1: f_wil = st.multiselect("Wilayah", options=sorted(df_fb["Wilayah"].unique()), default=sorted(df_fb["Wilayah"].unique()), key="f_wil_fb")
        with col_f2: f_tipe = st.multiselect("Tipe Usaha", options=sorted(df_fb["Tipe Usaha"].unique()), default=sorted(df_fb["Tipe Usaha"].unique()), key="f_tipe_fb")
        with col_f3:
            max_h = int(df_fb["Harga"].max()) if df_fb["Harga"].max() > 0 else 1000000
            f_hrg = st.slider("Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_fb")
        df_f = df_fb[df_fb["Wilayah"].isin(f_wil) & df_fb["Tipe Usaha"].isin(f_tipe) & (df_fb["Harga"] >= f_hrg[0]) & (df_fb["Harga"] <= f_hrg[1])]

        tab1, tab2, tab3 = st.tabs(["RINGKASAN", "DATABASE", "AUDIT LOG"])
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Data", f"{len(df_f):,}".replace(",", "."))
            c2.metric("Perorangan", f"{len(df_f[df_f['Tipe Usaha'] == 'Perorangan (Facebook)']):,}".replace(",", "."))
            c3.metric("Wilayah", f"{df_f['Wilayah'].nunique()}")
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", title="Komposisi Tipe Usaha", hole=0.5,
                                 color_discrete_sequence=["#1877F2","#64A8F8","#B3D1FC","#4A4A4A"])
                    fig.update_layout(font_family="DM Sans", title_font_size=13, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    fig2 = px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Usaha per Wilayah", color_discrete_sequence=["#1877F2"])
                    fig2.update_layout(font_family="DM Sans", title_font_size=13, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAF8", xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#E8E8E4"), showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)
        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=370)
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_f.to_excel(writer, index=False, sheet_name="Data FB")
                    wb, ws = writer.book, writer.sheets["Data FB"]
                    for col_num, value in enumerate(df_f.columns.values):
                        ws.write(0, col_num, value, wb.add_format({'bold': True, 'bg_color': '#1877F2', 'font_color': 'white', 'border': 0}))
                    ws.set_column('A:A', 25); ws.set_column('B:B', 50)
                    ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'}))
                    ws.set_column('D:D', 20); ws.set_column('E:E', 25); ws.set_column('F:F', 50)
                st.markdown(f'<style>[data-testid="stDownloadButton"]>button{{background:#1877F2!important}}</style>', unsafe_allow_html=True)
                st.download_button("↓ Download Excel Facebook", data=buf.getvalue(), file_name=f"UMKM_Facebook_{datetime.date.today()}.xlsx")
        with tab3:
            audit = st.session_state.audit_fb
            st.info(f"**File diproses:** {audit.get('file_count',0)} CSV")

# ==============================================================================
#  EXPORT GABUNGAN
# ==============================================================================
elif halaman == "📊 Export Gabungan":
    metric_wrap("#6C63FF")
    st.markdown("""
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-eyebrow">
                <span class="dot" style="background:#6C63FF"></span>
                Master Data · Semua Platform
            </div>
            <h1 class="page-title">Export<br><em style="color:#6C63FF">Gabungan</em></h1>
            <p class="page-subtitle">Unduh satu file Excel master berisi data Shopee,<br>Tokopedia, dan Facebook dengan format tab terpisah</p>
        </div>
        <div class="page-header-right">
            <span class="platform-badge" style="background:#6C63FF">📊 3-in-1</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_shp_ready = st.session_state.data_shopee is not None and not st.session_state.data_shopee.empty
    df_tkp_ready = st.session_state.data_tokped is not None and not st.session_state.data_tokped.empty
    df_fb_ready  = st.session_state.data_fb is not None and not st.session_state.data_fb.empty

    if not df_shp_ready and not df_tkp_ready and not df_fb_ready:
        st.warning("⚠️ Belum ada data yang diproses. Silakan proses data di menu Shopee, Tokopedia, atau Facebook terlebih dahulu.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Produk Shopee",    f"{len(st.session_state.data_shopee):,}".replace(",",".") if df_shp_ready else "—")
        c2.metric("Produk Tokopedia", f"{len(st.session_state.data_tokped):,}".replace(",",".") if df_tkp_ready else "—")
        c3.metric("Produk Facebook",  f"{len(st.session_state.data_fb):,}".replace(",",".")  if df_fb_ready  else "—")
        st.write("---")

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            wb = writer.book
            currency_fmt = wb.add_format({'num_format': '#,##0'})
            if df_shp_ready:
                df_shp = st.session_state.data_shopee
                df_shp.to_excel(writer, index=False, sheet_name="Shopee")
                ws = writer.sheets["Shopee"]
                hdr = wb.add_format({'bold': True, 'bg_color': '#FF6B35', 'font_color': 'white', 'border': 0})
                for n, v in enumerate(df_shp.columns.values): ws.write(0, n, v, hdr)
                ws.set_column('A:A', 25); ws.set_column('B:B', 50); ws.set_column('C:C', 18, currency_fmt)
                ws.set_column('D:D', 20); ws.set_column('E:E', 25); ws.set_column('F:F', 50)
                ws.autofilter(0, 0, len(df_shp), len(df_shp.columns) - 1)
            if df_tkp_ready:
                df_tkp = st.session_state.data_tokped
                df_tkp.to_excel(writer, index=False, sheet_name="Tokopedia")
                ws = writer.sheets["Tokopedia"]
                hdr = wb.add_format({'bold': True, 'bg_color': '#00C853', 'font_color': 'white', 'border': 0})
                for n, v in enumerate(df_tkp.columns.values): ws.write(0, n, v, hdr)
                ws.set_column('A:A', 25); ws.set_column('B:B', 50); ws.set_column('C:C', 18, currency_fmt)
                ws.set_column('D:D', 20); ws.set_column('E:E', 25); ws.set_column('F:F', 50)
                ws.autofilter(0, 0, len(df_tkp), len(df_tkp.columns) - 1)
            if df_fb_ready:
                df_fb = st.session_state.data_fb
                df_fb.to_excel(writer, index=False, sheet_name="Facebook")
                ws = writer.sheets["Facebook"]
                hdr = wb.add_format({'bold': True, 'bg_color': '#1877F2', 'font_color': 'white', 'border': 0})
                for n, v in enumerate(df_fb.columns.values): ws.write(0, n, v, hdr)
                ws.set_column('A:A', 25); ws.set_column('B:B', 50); ws.set_column('C:C', 18, currency_fmt)
                ws.set_column('D:D', 20); ws.set_column('E:E', 25); ws.set_column('F:F', 50)
                ws.autofilter(0, 0, len(df_fb), len(df_fb.columns) - 1)

        st.markdown(f'<style>[data-testid="stDownloadButton"]>button{{background:#6C63FF!important;font-size:0.9rem!important;padding:1rem!important}}</style>', unsafe_allow_html=True)
        st.download_button(
            label="↓  DOWNLOAD MASTER EXCEL 3-IN-1",
            data=buf.getvalue(),
            file_name=f"Master_UMKM_BPS_{datetime.date.today()}.xlsx",
            use_container_width=True
        )
