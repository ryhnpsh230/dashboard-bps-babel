import streamlit as st
import pandas as pd
import re
import io
import requests
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard UMKM BPS",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS PREMIUM REDESIGN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Syne:wght@700;800&display=swap');

    /* ===== GLOBAL RESET & BASE ===== */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main .block-container {
        padding: 2rem 2.5rem 3rem 2.5rem;
        max-width: 1400px;
    }

    /* ===== SIDEBAR REDESIGN ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0f1e 0%, #0d1530 60%, #0a1628 100%);
        border-right: 1px solid rgba(99, 179, 237, 0.12);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.9rem;
        font-weight: 500;
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        transition: all 0.2s ease;
        cursor: pointer;
        display: block;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(99, 179, 237, 0.1);
        color: #63b3ed !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #94a3b8 !important;
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 600;
    }
    [data-testid="stSidebar"] h3 {
        font-family: 'Syne', sans-serif !important;
        font-size: 1rem !important;
        color: #f1f5f9 !important;
        letter-spacing: 0.02em;
    }

    /* ===== HEADER BANNER — SHOPEE ===== */
    .banner-shopee {
        background: linear-gradient(135deg, #0b1c3d 0%, #0d2e6e 50%, #1042a0 100%);
        padding: 32px 40px;
        border-radius: 16px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(99, 179, 237, 0.2);
        box-shadow: 0 20px 60px rgba(10, 30, 80, 0.5), inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .banner-shopee::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(66,135,245,0.25) 0%, transparent 70%);
        border-radius: 50%;
    }
    .banner-shopee::after {
        content: '';
        position: absolute;
        bottom: -40px; left: 30%;
        width: 160px; height: 160px;
        background: radial-gradient(circle, rgba(30,80,200,0.2) 0%, transparent 70%);
        border-radius: 50%;
    }
    .banner-shopee h1 { 
        color: white !important; font-weight: 800; margin-bottom: 6px; 
        font-size: 2.2rem; font-family: 'Syne', sans-serif; 
        letter-spacing: -0.02em; position: relative; z-index: 1;
    }
    .banner-shopee p { 
        color: #93c5fd !important; font-size: 0.95rem; margin: 0; 
        font-weight: 400; position: relative; z-index: 1;
    }
    .banner-label {
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em;
        text-transform: uppercase; margin-bottom: 8px; display: block;
        position: relative; z-index: 1;
    }
    .banner-shopee .banner-label { color: #60a5fa !important; }

    /* ===== HEADER BANNER — TOKOPEDIA ===== */
    .banner-tokped {
        background: linear-gradient(135deg, #022518 0%, #054a2e 50%, #076344 100%);
        padding: 32px 40px;
        border-radius: 16px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(52, 211, 153, 0.2);
        box-shadow: 0 20px 60px rgba(5, 40, 25, 0.5), inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .banner-tokped::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(52,211,153,0.2) 0%, transparent 70%);
        border-radius: 50%;
    }
    .banner-tokped h1 { 
        color: white !important; font-weight: 800; margin-bottom: 6px; 
        font-size: 2.2rem; font-family: 'Syne', sans-serif; 
        letter-spacing: -0.02em; position: relative; z-index: 1;
    }
    .banner-tokped p { 
        color: #a7f3d0 !important; font-size: 0.95rem; margin: 0; 
        font-weight: 400; position: relative; z-index: 1;
    }
    .banner-tokped .banner-label { color: #6ee7b7 !important; }

    /* ===== HEADER BANNER — FACEBOOK ===== */
    .banner-fb {
        background: linear-gradient(135deg, #0a1628 0%, #0f2757 50%, #1a3a7a 100%);
        padding: 32px 40px;
        border-radius: 16px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(96, 165, 250, 0.2);
        box-shadow: 0 20px 60px rgba(8, 20, 60, 0.5), inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .banner-fb::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(59,130,246,0.25) 0%, transparent 70%);
        border-radius: 50%;
    }
    .banner-fb h1 { 
        color: white !important; font-weight: 800; margin-bottom: 6px; 
        font-size: 2.2rem; font-family: 'Syne', sans-serif;
        letter-spacing: -0.02em; position: relative; z-index: 1;
    }
    .banner-fb p { 
        color: #bfdbfe !important; font-size: 0.95rem; margin: 0; 
        font-weight: 400; position: relative; z-index: 1;
    }
    .banner-fb .banner-label { color: #93c5fd !important; }

    /* ===== HEADER BANNER — GABUNGAN ===== */
    .banner-gabungan {
        background: linear-gradient(135deg, #07090f 0%, #0f1523 50%, #161e33 100%);
        padding: 32px 40px;
        border-radius: 16px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.15);
        box-shadow: 0 20px 60px rgba(5, 8, 20, 0.6), inset 0 1px 0 rgba(255,255,255,0.04);
    }
    .banner-gabungan::before {
        content: '';
        position: absolute;
        top: -50px; right: -50px;
        width: 200px; height: 200px;
        background: radial-gradient(circle, rgba(148,163,184,0.12) 0%, transparent 70%);
        border-radius: 50%;
    }
    .banner-gabungan h1 { 
        color: white !important; font-weight: 800; margin-bottom: 6px; 
        font-size: 2.2rem; font-family: 'Syne', sans-serif;
        letter-spacing: -0.02em; position: relative; z-index: 1;
    }
    .banner-gabungan p { 
        color: #94a3b8 !important; font-size: 0.95rem; margin: 0; 
        font-weight: 400; position: relative; z-index: 1;
    }
    .banner-gabungan .banner-label { color: #64748b !important; }

    /* ===== METRIC CARDS ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #f8fafc, #f1f5f9);
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem 1.5rem !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: #64748b !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        line-height: 1.1 !important;
    }

    /* ===== TABS ===== */
    [data-testid="stTabs"] [role="tablist"] {
        border-bottom: 2px solid #e2e8f0;
        gap: 0.25rem;
        padding-bottom: 0;
    }
    [data-testid="stTabs"] [role="tab"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 600;
        font-size: 0.875rem;
        color: #64748b;
        padding: 0.6rem 1.2rem;
        border-radius: 8px 8px 0 0;
        border: none;
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
        transition: all 0.2s ease;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: #1e40af;
        border-bottom-color: #1e40af;
        background: rgba(30, 64, 175, 0.05);
    }
    [data-testid="stTabs"] [role="tab"]:hover {
        color: #1e40af;
        background: rgba(30, 64, 175, 0.04);
    }

    /* ===== FILTER SECTION ===== */
    .filter-section-label {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .filter-section-label::before {
        content: '';
        display: inline-block;
        width: 3px;
        height: 14px;
        background: #1e40af;
        border-radius: 2px;
    }

    /* ===== BUTTONS ===== */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 0.9rem;
        padding: 0.65rem 1.5rem;
        letter-spacing: 0.01em;
        transition: all 0.2s ease;
        box-shadow: 0 4px 14px rgba(30, 64, 175, 0.35);
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(30, 64, 175, 0.45);
        background: linear-gradient(135deg, #1d3fa8 0%, #1d4ed8 100%);
    }

    /* ===== DOWNLOAD BUTTON ===== */
    [data-testid="stDownloadButton"] > button {
        border-radius: 10px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.15) !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.22) !important;
    }

    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(99, 179, 237, 0.3);
        border-radius: 12px;
        padding: 0.5rem;
        background: rgba(255,255,255,0.03);
        transition: border-color 0.2s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(99, 179, 237, 0.6);
    }

    /* ===== DATAFRAME ===== */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04) !important;
    }

    /* ===== ALERTS & MESSAGES ===== */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border-left-width: 4px !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }

    /* ===== SECTION HEADING ===== */
    .section-heading {
        font-family: 'Syne', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        margin: 1.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-heading::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, #e2e8f0, transparent);
        margin-left: 0.75rem;
    }

    /* ===== PROGRESS BAR ===== */
    [data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, #1e40af, #3b82f6) !important;
        border-radius: 99px !important;
    }

    /* ===== DIVIDER ===== */
    hr {
        border: none !important;
        border-top: 1px solid #e2e8f0 !important;
        margin: 1.5rem 0 !important;
    }

    /* ===== MULTISELECT ===== */
    [data-testid="stMultiSelect"] [data-baseweb="select"] {
        border-radius: 10px !important;
    }

    /* ===== SPINNER ===== */
    [data-testid="stSpinner"] {
        color: #2563eb !important;
    }

    /* ===== SIDEBAR HEADER ===== */
    [data-testid="stSidebar"] .stFileUploader label,
    [data-testid="stSidebar"] .stCheckbox label {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #cbd5e1 !important;
    }
    [data-testid="stSidebar"] h2 {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #e2e8f0 !important;
        letter-spacing: 0.01em;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1rem !important;
    }

    /* ===== MAIN BG ===== */
    .main {
        background: #f8fafd;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "data_shopee" not in st.session_state: st.session_state.data_shopee = None
if "audit_shopee" not in st.session_state: st.session_state.audit_shopee = {}

if "data_tokped" not in st.session_state: st.session_state.data_tokped = None
if "audit_tokped" not in st.session_state: st.session_state.audit_tokped = {}

if "data_fb" not in st.session_state: st.session_state.data_fb = None
if "audit_fb" not in st.session_state: st.session_state.audit_fb = {}

# --- 4. FUNGSI DETEKSI TIPE USAHA (AI HEURISTIK) ---
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

# --- 5. SIDEBAR MENU ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    st.markdown("""
        <div style="padding: 1rem 0 0.5rem 0;">
            <span style="font-size:0.7rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#64748b;">
                🏛️ Badan Pusat Statistik
            </span>
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:800; color:#f1f5f9; margin-top:4px; line-height:1.3;">
                Dashboard<br>UMKM
            </div>
        </div>
        <div style="height:1px; background:linear-gradient(90deg, rgba(99,179,237,0.3), transparent); margin: 0.75rem 0 1.25rem 0;"></div>
    """, unsafe_allow_html=True)

    st.markdown("### 🧭 Menu Navigasi")
    halaman = st.radio("Pilih Fitur:", ["🟠 Shopee", "🟢 Tokopedia", "🔵 Facebook FB", "📊 Export Gabungan"])
    
    st.markdown("""
        <div style="margin-top:2rem; padding-top:1rem; border-top:1px solid rgba(255,255,255,0.07);">
            <p style="font-size:0.7rem; color:#475569; text-align:center; margin:0;">
                Versi 2.0 · Bangka Belitung<br>
                <span style="color:#334155;">© 2025 BPS Indonesia</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

babel_keys = ["pangkal", "bangka", "belitung", "sungailiat", "mentok", "muntok", "koba", "toboali", "manggar", "tanjung pandan", "tanjungpandan"]

# ==============================================================================
#                             HALAMAN SHOPEE
# ==============================================================================
if halaman == "🟠 Shopee":
    st.markdown("""
    <div class="banner-shopee">
        <span class="banner-label">🏛️ Badan Pusat Statistik · Bangka Belitung</span>
        <h1>Dashboard UMKM — Shopee</h1>
        <p>Ekstraksi & Analisis Data UMKM dari Shopee Marketplace Wilayah Bangka Belitung</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Shopee")
        files_shopee = st.file_uploader("Unggah CSV Shopee", type=["csv"], accept_multiple_files=True, key="file_shp")
        mode_api_shp = st.checkbox("🔍 Deteksi Nama Toko via API", key="api_shp", value=True, help="Wajib dicentang agar sistem bisa mendeteksi Tipe Usaha!")
        
        if st.button("🚀 Proses Shopee", type="primary", use_container_width=True):
            if not files_shopee:
                st.error("⚠️ Unggah file CSV Shopee dulu!")
            elif not mode_api_shp:
                st.warning("⚠️ Untuk deteksi Toko Fisik/Murni Online, Centang kotak 'Deteksi Nama Toko via API'!")
            else:
                with st.spinner("Membaca file CSV..."):
                    try:
                        total_semua_baris = 0
                        for f in files_shopee:
                            df_temp = pd.read_csv(f, dtype=str, on_bad_lines="skip")
                            total_semua_baris += len(df_temp)
                            f.seek(0)
                            
                        hasil, total_baris, err_h, luar_wilayah = [], 0, 0, 0
                        baris_diproses = 0
                        
                        status_text = st.empty()
                        progress_bar = st.progress(0)
                        
                        for idx, file in enumerate(files_shopee):
                            df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                            total_baris += len(df_raw)
                            
                            if "Link" in df_raw.columns and "Nama Produk" in df_raw.columns:
                                col_link = "Link"
                                col_nama = "Nama Produk"
                                col_harga = "Harga"
                                col_wilayah = "Wilayah"
                            else:
                                col_link = next((c for c in df_raw.columns if 'href' in c.lower()), df_raw.columns[0])
                                col_nama = next((c for c in df_raw.columns if 'whitespace-normal' in c.lower()), df_raw.columns[3])
                                col_harga = next((c for c in df_raw.columns if 'font-medium 2' in c.lower()), df_raw.columns[4])
                                idx_wilayah = 7 if len(df_raw.columns) > 7 else len(df_raw.columns) - 1
                                col_wilayah = next((c for c in df_raw.columns if 'ml-[3px]' in c.lower()), df_raw.columns[idx_wilayah])

                            for i in range(len(df_raw)):
                                row = df_raw.iloc[i]
                                link = str(row[col_link])
                                nama = str(row[col_nama])
                                harga_str = str(row[col_harga])
                                lokasi_shopee = str(row[col_wilayah]).title()
                                
                                if not any(k in lokasi_shopee.lower() for k in babel_keys):
                                    luar_wilayah += 1
                                    baris_diproses += 1
                                    continue
                                
                                try: 
                                    harga_bersih = harga_str.replace('.', '').replace(',', '')
                                    angka_list = re.findall(r'\d+', harga_bersih)
                                    if angka_list:
                                        val_h = int(angka_list[0])
                                        if val_h > 1000000000: val_h = 0
                                    else:
                                        val_h = 0
                                except: 
                                    val_h, err_h = 0, err_h + 1
                                
                                toko = "Tidak Dilacak"
                                if mode_api_shp:
                                    match = re.search(r"i\.(\d+)\.", link)
                                    if match:
                                        try:
                                            res = requests.get(f"https://shopee.co.id/api/v4/shop/get_shop_base?shopid={match.group(1)}", headers={"User-Agent":"Mozilla/5.0"}, timeout=2)
                                            if res.status_code == 200: toko = res.json().get("data",{}).get("name", "Anonim")
                                        except: pass
                                
                                tipe_usaha = deteksi_tipe_usaha(toko)
                                hasil.append({"Nama Toko": toko, "Nama Produk": nama, "Harga": val_h, "Wilayah": lokasi_shopee, "Tipe Usaha": tipe_usaha, "Link": link})
                                
                                baris_diproses += 1
                                if baris_diproses % 5 == 0 or baris_diproses == total_semua_baris:
                                    pct = min(baris_diproses / total_semua_baris, 1.0)
                                    progress_bar.progress(pct)
                                    status_text.markdown(f"**⏳ Mengekstrak:** {baris_diproses} / {total_semua_baris} baris ({int(pct*100)}%)")
                        
                        status_text.empty()
                        progress_bar.empty()
                        
                        st.session_state.data_shopee = pd.DataFrame(hasil)
                        st.session_state.audit_shopee = {"total": total_baris, "valid": len(hasil), "file_count": len(files_shopee), "error_harga": err_h, "luar": luar_wilayah}
                        st.success(f"✅ {len(hasil)} data Shopee berhasil diproses!")
                    except Exception as e:
                        st.error(f"Error Sistem: {e}")

    df_shp = st.session_state.data_shopee
    if df_shp is not None and not df_shp.empty:
        st.markdown('<div class="section-heading">🔎 Filter Data Pintar</div>', unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1: f_wil = st.multiselect("Pilih Wilayah:", options=sorted(df_shp["Wilayah"].unique()), default=sorted(df_shp["Wilayah"].unique()), key="f_wil_shp")
        with col_f2: f_tipe = st.multiselect("Pilih Tipe Usaha:", options=sorted(df_shp["Tipe Usaha"].unique()), default=sorted(df_shp["Tipe Usaha"].unique()), key="f_tipe_shp")
        with col_f3: 
            max_h = int(df_shp["Harga"].max()) if df_shp["Harga"].max() > 0 else 1000000
            f_hrg = st.slider("Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_shp")

        df_f = df_shp[df_shp["Wilayah"].isin(f_wil) & df_shp["Tipe Usaha"].isin(f_tipe) & (df_shp["Harga"] >= f_hrg[0]) & (df_shp["Harga"] <= f_hrg[1])]
        
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Audit"])
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Data Tampil", f"{len(df_f):,}".replace(",", "."))
            c2.metric("Murni Online (Ditampilkan)", f"{len(df_f[df_f['Tipe Usaha'] == 'Murni Online (Rumahan)']):,}".replace(",", "."))
            c3.metric("Titik Lokasi", f"{df_f['Wilayah'].nunique()}")
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.pie(df_f, names="Tipe Usaha", title="Komposisi Model Bisnis UMKM", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
                with g2: st.plotly_chart(px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Total Usaha per Wilayah", color="Wilayah", color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=350)
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_f.to_excel(writer, index=False, sheet_name="Data Shopee")
                    wb, ws = writer.book, writer.sheets["Data Shopee"]
                    for col_num, value in enumerate(df_f.columns.values): ws.write(0, col_num, value, wb.add_format({'bold': True, 'bg_color': '#022a5e', 'font_color': 'white'}))
                    ws.set_column('A:A', 25); ws.set_column('B:B', 50); ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'})); ws.set_column('D:D', 20); ws.set_column('E:E', 25); ws.set_column('F:F', 50)
                st.download_button("⬇️ Download Excel Shopee", data=buf.getvalue(), file_name=f"UMKM_Shopee_{datetime.date.today()}.xlsx", type="primary")
        with tab3:
            audit = st.session_state.audit_shopee
            st.info(f"**📂 Jumlah File Diproses:** {audit.get('file_count',0)} File CSV")
            st.success(f"**📥 Total Data Valid:** {audit.get('valid',0)} Baris")

# ==============================================================================
#                             HALAMAN TOKOPEDIA
# ==============================================================================
elif halaman == "🟢 Tokopedia":
    st.markdown("""
    <div class="banner-tokped">
        <span class="banner-label">🏛️ Badan Pusat Statistik · Bangka Belitung</span>
        <h1>Dashboard UMKM — Tokopedia</h1>
        <p>Ekstraksi & Analisis Data UMKM dari Tokopedia Wilayah Bangka Belitung</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Tokopedia")
        files_tokped = st.file_uploader("Unggah CSV Tokopedia", type=["csv"], accept_multiple_files=True, key="file_tkp")
        
        if st.button("🚀 Proses Tokopedia", type="primary", use_container_width=True):
            if not files_tokped:
                st.error("⚠️ Unggah file CSV Tokopedia dulu!")
            else:
                with st.spinner("Membaca file CSV..."):
                    try:
                        total_semua_baris = 0
                        for f in files_tokped:
                            df_temp = pd.read_csv(f, dtype=str, on_bad_lines="skip")
                            total_semua_baris += len(df_temp)
                            f.seek(0)
                            
                        hasil, total_baris, err_h, luar_wilayah = [], 0, 0, 0
                        baris_diproses = 0
                        
                        status_text = st.empty()
                        progress_bar = st.progress(0)
                        
                        for idx, file in enumerate(files_tokped):
                            df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                            total_baris += len(df_raw)
                            
                            if "Link" in df_raw.columns and "Nama Produk" in df_raw.columns:
                                col_links = ["Link"]
                                col_namas = ["Nama Produk"]
                                col_hargas = ["Harga"]
                                col_lokasis = ["Wilayah"]
                                col_tokos = ["Nama Toko"]
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
                                            luar_wilayah += 1
                                            continue
                                            
                                        try: 
                                            harga_bersih = harga_str.replace('.', '').replace(',', '')
                                            angka_list = re.findall(r'\d+', harga_bersih)
                                            if angka_list:
                                                val_h = int(angka_list[0])
                                                if val_h > 1000000000: val_h = 0
                                            else:
                                                val_h = 0
                                        except: 
                                            val_h, err_h = 0, err_h + 1
                                        
                                        if val_h > 0:
                                            tipe_usaha = deteksi_tipe_usaha(toko)
                                            hasil.append({"Nama Toko": toko, "Nama Produk": nama, "Harga": val_h, "Wilayah": lokasi_tokped, "Tipe Usaha": tipe_usaha, "Link": link})
                                            
                                    except Exception: continue
                                
                                baris_diproses += 1
                                if baris_diproses % 5 == 0 or baris_diproses == total_semua_baris:
                                    pct = min(baris_diproses / total_semua_baris, 1.0)
                                    progress_bar.progress(pct)
                                    status_text.markdown(f"**⏳ Mengekstrak:** {baris_diproses} / {total_semua_baris} baris ({int(pct*100)}%)")
                        
                        status_text.empty()
                        progress_bar.empty()
                        
                        df_final = pd.DataFrame(hasil).drop_duplicates()
                        st.session_state.data_tokped = df_final
                        st.session_state.audit_tokped = {"total": total_baris, "valid": len(df_final), "file_count": len(files_tokped), "error_harga": err_h, "luar": luar_wilayah}
                        st.success(f"✅ {len(df_final)} data Tokopedia berhasil diekstrak!")
                    except Exception as e:
                        st.error(f"Error Sistem Tokopedia: {e}")

    df_tkp = st.session_state.data_tokped
    if df_tkp is not None and not df_tkp.empty:
        st.markdown('<div class="section-heading">🔎 Filter Data Pintar</div>', unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1: f_wil = st.multiselect("Pilih Wilayah:", options=sorted(df_tkp["Wilayah"].unique()), default=sorted(df_tkp["Wilayah"].unique()), key="f_wil_tkp")
        with col_f2: f_tipe = st.multiselect("Pilih Tipe Usaha:", options=sorted(df_tkp["Tipe Usaha"].unique()), default=sorted(df_tkp["Tipe Usaha"].unique()), key="f_tipe_tkp")
        with col_f3: 
            max_h = int(df_tkp["Harga"].max()) if df_tkp["Harga"].max() > 0 else 1000000
            f_hrg = st.slider("Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_tkp")

        df_f = df_tkp[df_tkp["Wilayah"].isin(f_wil) & df_tkp["Tipe Usaha"].isin(f_tipe) & (df_tkp["Harga"] >= f_hrg[0]) & (df_tkp["Harga"] <= f_hrg[1])]
        
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Audit"])
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Data Tampil", f"{len(df_f):,}".replace(",", "."))
            c2.metric("Murni Online (Ditampilkan)", f"{len(df_f[df_f['Tipe Usaha'] == 'Murni Online (Rumahan)']):,}".replace(",", "."))
            c3.metric("Titik Lokasi", f"{df_f['Wilayah'].nunique()}")
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.pie(df_f, names="Tipe Usaha", title="Komposisi Model Bisnis UMKM", hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
                with g2: st.plotly_chart(px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Total Usaha per Wilayah", color="Wilayah", color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=350)
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_f.to_excel(writer, index=False, sheet_name="Data Tokopedia")
                    wb, ws = writer.book, writer.sheets["Data Tokopedia"]
                    for col_num, value in enumerate(df_f.columns.values): ws.write(0, col_num, value, wb.add_format({'bold': True, 'bg_color': '#064e3b', 'font_color': 'white'}))
                    ws.set_column('A:A', 25); ws.set_column('B:B', 50); ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'})); ws.set_column('D:D', 20); ws.set_column('E:E', 25); ws.set_column('F:F', 50)
                st.markdown('<style>div[data-testid="stDownloadButton"] button {background-color: #059669; color: white; border:none;}</style>', unsafe_allow_html=True)
                st.download_button("⬇️ Download Excel Tokopedia", data=buf.getvalue(), file_name=f"UMKM_Tokopedia_{datetime.date.today()}.xlsx")
        with tab3:
            audit = st.session_state.audit_tokped
            st.info(f"**📂 Jumlah File Diproses:** {audit.get('file_count',0)} File CSV")


# ==============================================================================
#                             HALAMAN FACEBOOK MARKETPLACE
# ==============================================================================
elif halaman == "🔵 Facebook FB":
    st.markdown("""
    <div class="banner-fb">
        <span class="banner-label">🏛️ Badan Pusat Statistik · Bangka Belitung</span>
        <h1>Dashboard UMKM — Facebook</h1>
        <p>Ekstraksi & Analisis Data UMKM dari Facebook Marketplace Wilayah Bangka Belitung</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Facebook")
        files_fb = st.file_uploader("Unggah CSV Facebook FB", type=["csv"], accept_multiple_files=True, key="file_fb")
        
        if st.button("🚀 Proses Facebook FB", type="primary", use_container_width=True):
            if not files_fb:
                st.error("⚠️ Unggah file CSV Facebook FB dulu!")
            else:
                with st.spinner("Membaca file CSV..."):
                    try:
                        total_semua_baris = 0
                        for f in files_fb:
                            df_temp = pd.read_csv(f, dtype=str, on_bad_lines="skip")
                            total_semua_baris += len(df_temp)
                            f.seek(0)
                            
                        hasil, total_baris, err_h, luar_wilayah = [], 0, 0, 0
                        baris_diproses = 0
                        status_text = st.empty()
                        progress_bar = st.progress(0)
                        
                        for idx, file in enumerate(files_fb):
                            df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                            total_baris += len(df_raw)
                            
                            if "Link" in df_raw.columns and "Nama Produk" in df_raw.columns:
                                col_link, col_nama, col_harga, col_wilayah, col_toko = "Link", "Nama Produk", "Harga", "Wilayah", "Nama Toko"
                            else:
                                col_toko, col_nama, col_wilayah, col_harga, col_link = df_raw.columns[0], df_raw.columns[1], df_raw.columns[2], df_raw.columns[4], df_raw.columns[5]

                            for i in range(len(df_raw)):
                                row = df_raw.iloc[i]
                                link = str(row[col_link])
                                nama = str(row[col_nama])
                                harga_str = str(row[col_harga])
                                lokasi_fb = str(row[col_wilayah]).title()
                                toko = str(row.get(col_toko, "FB Seller"))
                                
                                if not any(k in lokasi_fb.lower() for k in babel_keys):
                                    luar_wilayah += 1
                                    baris_diproses += 1
                                    continue
                                
                                try: 
                                    harga_bersih = harga_str.replace('.', '').replace(',', '')
                                    angka_list = re.findall(r'\d+', harga_bersih)
                                    if angka_list:
                                        val_h = int(angka_list[0])
                                        if val_h > 1000000000: val_h = 0
                                    else:
                                        val_h = 0
                                except: 
                                    val_h, err_h = 0, err_h + 1
                                
                                if val_h > 0:
                                    tipe_usaha = deteksi_tipe_usaha(toko)
                                    hasil.append({"Nama Toko": toko, "Nama Produk": nama, "Harga": val_h, "Wilayah": lokasi_fb, "Tipe Usaha": tipe_usaha, "Link": link})
                                
                                baris_diproses += 1
                                if baris_diproses % 5 == 0 or baris_diproses == total_semua_baris:
                                    pct = min(baris_diproses / total_semua_baris, 1.0)
                                    progress_bar.progress(pct)
                                    status_text.markdown(f"**⏳ Mengekstrak:** {baris_diproses} / {total_semua_baris} baris ({int(pct*100)}%)")
                        
                        status_text.empty()
                        progress_bar.empty()
                        
                        df_final = pd.DataFrame(hasil).drop_duplicates()
                        st.session_state.data_fb = df_final
                        st.session_state.audit_fb = {"total": total_baris, "valid": len(df_final), "file_count": len(files_fb), "error_harga": err_h, "luar": luar_wilayah}
                        st.success(f"✅ {len(df_final)} data Facebook FB berhasil diekstrak!")
                    except Exception as e:
                        st.error(f"Error Sistem FB: {e}")

    df_fb = st.session_state.data_fb
    if df_fb is not None and not df_fb.empty:
        st.markdown('<div class="section-heading">🔎 Filter Data Pintar</div>', unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1: f_wil = st.multiselect("Pilih Wilayah:", options=sorted(df_fb["Wilayah"].unique()), default=sorted(df_fb["Wilayah"].unique()), key="f_wil_fb")
        with col_f2: f_tipe = st.multiselect("Pilih Tipe Usaha:", options=sorted(df_fb["Tipe Usaha"].unique()), default=sorted(df_fb["Tipe Usaha"].unique()), key="f_tipe_fb")
        with col_f3: 
            max_h = int(df_fb["Harga"].max()) if df_fb["Harga"].max() > 0 else 1000000
            f_hrg = st.slider("Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_fb")

        df_f = df_fb[df_fb["Wilayah"].isin(f_wil) & df_fb["Tipe Usaha"].isin(f_tipe) & (df_fb["Harga"] >= f_hrg[0]) & (df_fb["Harga"] <= f_hrg[1])]
        
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Audit"])
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Data Tampil", f"{len(df_f):,}".replace(",", "."))
            c2.metric("Perorangan (Ditampilkan)", f"{len(df_f[df_f['Tipe Usaha'] == 'Perorangan (Facebook)']):,}".replace(",", "."))
            c3.metric("Titik Lokasi", f"{df_f['Wilayah'].nunique()}")
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.pie(df_f, names="Tipe Usaha", title="Komposisi Model Bisnis FB", hole=0.4, color_discrete_sequence=px.colors.sequential.Plotly3), use_container_width=True)
                with g2: st.plotly_chart(px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Total Usaha per Wilayah FB", color="Wilayah", color_discrete_sequence=px.colors.sequential.Plotly3), use_container_width=True)
        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=350)
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_f.to_excel(writer, index=False, sheet_name="Data FB")
                    wb, ws = writer.book, writer.sheets["Data FB"]
                    for col_num, value in enumerate(df_f.columns.values): ws.write(0, col_num, value, wb.add_format({'bold': True, 'bg_color': '#1877f2', 'font_color': 'white'}))
                    ws.set_column('A:A', 25); ws.set_column('B:B', 50); ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'})); ws.set_column('D:D', 20); ws.set_column('E:E', 25); ws.set_column('F:F', 50)
                st.markdown('<style>div[data-testid="stDownloadButton"] button {background-color: #0866ff; color: white; border:none;}</style>', unsafe_allow_html=True)
                st.download_button("⬇️ Download Excel Facebook", data=buf.getvalue(), file_name=f"UMKM_Facebook_{datetime.date.today()}.xlsx")
        with tab3:
            audit = st.session_state.audit_fb
            st.info(f"**📂 Jumlah File Diproses:** {audit.get('file_count',0)} File CSV")

# ==============================================================================
#                             HALAMAN EXPORT GABUNGAN
# ==============================================================================
elif halaman == "📊 Export Gabungan":
    st.markdown("""
    <div class="banner-gabungan">
        <span class="banner-label">🏛️ Badan Pusat Statistik · Bangka Belitung</span>
        <h1>Export Master Data Gabungan</h1>
        <p>Dilengkapi dengan Kolom Analisis 'Tipe Usaha' (Fisik vs Murni Online) · Format Tab Terpisah & Auto Filter</p>
    </div>
    """, unsafe_allow_html=True)
    
    df_shp_ready = st.session_state.data_shopee is not None and not st.session_state.data_shopee.empty
    df_tkp_ready = st.session_state.data_tokped is not None and not st.session_state.data_tokped.empty
    df_fb_ready = st.session_state.data_fb is not None and not st.session_state.data_fb.empty
    
    if not df_shp_ready and not df_tkp_ready and not df_fb_ready:
        st.warning("⚠️ Belum ada data yang diproses. Silakan upload dan proses data di menu Shopee, Tokopedia, atau Facebook terlebih dahulu.")
    else:
        st.success("✅ Data siap untuk digabungkan menjadi file Master Excel 3-in-1!")
        
        c1, c2, c3 = st.columns(3)
        if df_shp_ready: c1.metric("📦 Produk Shopee", f"{len(st.session_state.data_shopee):,}".replace(",", "."))
        if df_tkp_ready: c2.metric("📦 Produk Tokopedia", f"{len(st.session_state.data_tokped):,}".replace(",", "."))
        if df_fb_ready: c3.metric("📦 Produk Facebook", f"{len(st.session_state.data_fb):,}".replace(",", "."))
            
        st.write("---")
        st.markdown("Klik tombol di bawah ini untuk mengunduh Excel dengan **Format Tab Terpisah** dan **Auto Filter**.")
        
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            wb = writer.book
            currency_fmt = wb.add_format({'num_format': '#,##0'})
            
            if df_shp_ready:
                df_shp = st.session_state.data_shopee
                df_shp.to_excel(writer, index=False, sheet_name="Data Shopee")
                ws_shp = writer.sheets["Data Shopee"]
                header_fmt_shp = wb.add_format({'bold': True, 'bg_color': '#022a5e', 'font_color': 'white'})
                for col_num, value in enumerate(df_shp.columns.values): ws_shp.write(0, col_num, value, header_fmt_shp)
                ws_shp.set_column('A:A', 25); ws_shp.set_column('B:B', 50); ws_shp.set_column('C:C', 18, currency_fmt); ws_shp.set_column('D:D', 20); ws_shp.set_column('E:E', 25); ws_shp.set_column('F:F', 50)
                ws_shp.autofilter(0, 0, len(df_shp), len(df_shp.columns) - 1)
                
            if df_tkp_ready:
                df_tkp = st.session_state.data_tokped
                df_tkp.to_excel(writer, index=False, sheet_name="Data Tokopedia")
                ws_tkp = writer.sheets["Data Tokopedia"]
                header_fmt_tkp = wb.add_format({'bold': True, 'bg_color': '#064e3b', 'font_color': 'white'})
                for col_num, value in enumerate(df_tkp.columns.values): ws_tkp.write(0, col_num, value, header_fmt_tkp)
                ws_tkp.set_column('A:A', 25); ws_tkp.set_column('B:B', 50); ws_tkp.set_column('C:C', 18, currency_fmt); ws_tkp.set_column('D:D', 20); ws_tkp.set_column('E:E', 25); ws_tkp.set_column('F:F', 50)
                ws_tkp.autofilter(0, 0, len(df_tkp), len(df_tkp.columns) - 1)

            if df_fb_ready:
                df_fb = st.session_state.data_fb
                df_fb.to_excel(writer, index=False, sheet_name="Data Facebook")
                ws_fb = writer.sheets["Data Facebook"]
                header_fmt_fb = wb.add_format({'bold': True, 'bg_color': '#1877f2', 'font_color': 'white'})
                for col_num, value in enumerate(df_fb.columns.values): ws_fb.write(0, col_num, value, header_fmt_fb)
                ws_fb.set_column('A:A', 25); ws_fb.set_column('B:B', 50); ws_fb.set_column('C:C', 18, currency_fmt); ws_fb.set_column('D:D', 20); ws_fb.set_column('E:E', 25); ws_fb.set_column('F:F', 50)
                ws_fb.autofilter(0, 0, len(df_fb), len(df_fb.columns) - 1)
                
        st.markdown('<style>div[data-testid="stDownloadButton"] button {background-color: #0f172a; color: white; border:none; height: 3.5rem; font-size: 1.1rem;}</style>', unsafe_allow_html=True)
        st.download_button(
            label="⬇️ DOWNLOAD EXCEL MASTER 3-IN-1",
            data=buf.getvalue(),
            file_name=f"Master_UMKM_BPS_{datetime.date.today()}.xlsx",
            use_container_width=True
        )
