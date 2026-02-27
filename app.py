import streamlit as st
import pandas as pd
import re
import io
import requests
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os
from urllib.parse import urlparse

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard UMKM BPS",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DEFINISI PALET WARNA BPS ---
BPS_PALETTE = ['#FF6F00', '#FFA000', '#FFB300', '#FFC107', '#263238', '#37474F', '#455A64']
BPS_OREN_UTAMA = '#FF6F00'

# --- 2. CSS CUSTOM (TEMA OREN-HITAM KEKINIAN / GLASSMORPHISM) ---
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(135deg, #FF6F00 0%, #7A3400 35%, #0f0f0f 100%) !important;
        background-attachment: fixed !important;
    }}

    .stApp {{
        color: #ffffff;
    }}

    .block-container {{ padding-top: 1rem; padding-bottom: 2rem; }}

    .banner-bps {{
        background: rgba(15, 15, 15, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 25px 35px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        color: white;
        border-left: 8px solid #FFC107;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .banner-bps h1 {{ color: white !important; font-weight: 800; margin-bottom: 5px; font-size: 2.2rem; letter-spacing: 0.5px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }}
    .banner-bps p {{ color: #e0e0e0 !important; font-size: 1.05rem; margin: 0; }}
    .banner-sub-title {{ font-size: 0.85rem; font-weight: bold; letter-spacing: 2px; color: #FFC107; margin-bottom: 5px; text-transform: uppercase; }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(20, 20, 20, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 111, 0, 0.4) !important;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}

    div[data-testid="metric-container"] {{
        background: rgba(25, 25, 25, 0.8);
        backdrop-filter: blur(10px);
        border-left: 5px solid {BPS_OREN_UTAMA} !important;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    div[data-testid="metric-container"]:hover {{
        transform: translateY(-4px);
        border-color: #FFC107;
        box-shadow: 0 8px 20px rgba(255, 111, 0, 0.5);
    }}
    div[data-testid="metric-container"] label {{ color: #cccccc !important; font-weight: 600; letter-spacing: 0.5px; }}
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ color: #ffffff !important; font-weight: 800; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; background-color: rgba(10, 10, 10, 0.6); padding: 10px; border-radius: 10px; backdrop-filter: blur(8px); }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        color: #d0d0d0;
        border-radius: 6px;
        padding: 0 20px;
        border: none;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {BPS_OREN_UTAMA} !important;
        color: white !important;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(255, 111, 0, 0.6);
    }}

    [data-testid="stSidebar"] {{
         background: linear-gradient(180deg, #0d0d0d 0%, #331600 100%) !important;
         border-right: 2px solid #FF6F00;
         box-shadow: 4px 0 15px rgba(0,0,0,0.5);
    }}
    [data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}

    h1, h2, h3, h4, p {{ text-shadow: 1px 1px 3px rgba(0,0,0,0.5); }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "data_shopee" not in st.session_state: st.session_state.data_shopee = None
if "audit_shopee" not in st.session_state: st.session_state.audit_shopee = {}

if "data_tokped" not in st.session_state: st.session_state.data_tokped = None
if "audit_tokped" not in st.session_state: st.session_state.audit_tokped = {}

if "data_fb" not in st.session_state: st.session_state.data_fb = None
if "audit_fb" not in st.session_state: st.session_state.audit_fb = {}

# NEW: data google maps
if "data_maps" not in st.session_state: st.session_state.data_maps = None
if "audit_maps" not in st.session_state: st.session_state.audit_maps = {}

# --- 4. FUNGSI DETEKSI TIPE USAHA (AI HEURISTIK) ---
def deteksi_tipe_usaha(nama_toko):
    if pd.isna(nama_toko) or nama_toko in ["Tidak Dilacak", "Toko CSV", "Anonim", ""]:
        return "Tidak Terdeteksi (Butuh Nama Toko)"

    if str(nama_toko) == "FB Seller":
        return "Perorangan (Facebook)"

    nama_lower = str(nama_toko).lower()
    keyword_fisik = [
        'toko', 'warung', 'grosir', 'mart', 'apotek', 'cv.', 'pt.', 'official', 'agen',
        'distributor', 'kios', 'kedai', 'supermarket', 'minimarket', 'cabang', 'jaya',
        'abadi', 'makmur', 'motor', 'mobil', 'bengkel', 'snack', 'store'
    ]

    for kata in keyword_fisik:
        if kata in nama_lower:
            return "Ada Toko Fisik"

    return "Murni Online (Rumahan)"

# ==========================================================
# 5. CLEANER (biar Excel bersih)
# ==========================================================
PLACEHOLDER = "Pemilik tidak mencantumkan"

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
    # buang selain digit + (keep +)
    s2 = re.sub(r"[^\d+]", "", s)

    # kasus "08xxxx" -> "+628xxxx"
    if s2.startswith("08"):
        s2 = "+62" + s2[1:]
    # kasus "628xxx" -> "+628xxx"
    if re.fullmatch(r"62\d{7,15}", s2):
        s2 = "+" + s2
    # case "+62..." ok
    if s2.startswith("+") and re.fullmatch(r"\+\d{8,16}", s2):
        return s2

    # kalau digit doang, coba interpretasi
    digits = re.sub(r"\D", "", s2)
    if digits.startswith("0") and len(digits) >= 9:
        return "+62" + digits[1:]
    if digits.startswith("62") and len(digits) >= 9:
        return "+" + digits
    # fallback, biarkan apa adanya yang sudah dibersihkan
    return s2

def normalize_url(x: str) -> str:
    s = clean_placeholder_to_empty(x)
    if not s:
        return ""
    s = s.strip()

    # izinkan wa.me, instagram, http/https, google maps link
    if s.startswith("http://") or s.startswith("https://"):
        return s
    if s.startswith("www."):
        return "https://" + s
    if s.startswith("wa.me/"):
        return "https://" + s
    if s.startswith("instagram.com/"):
        return "https://" + s

    # kadang user kasih @ig
    if s.startswith("@") and len(s) > 1:
        return "https://instagram.com/" + s[1:]

    # kalau tidak valid, kosongkan
    return ""

def to_float_safe(x: str):
    s = clean_placeholder_to_empty(x)
    if not s:
        return None
    # paksa titik sebagai decimal
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def clean_maps_dataframe(df_raw: pd.DataFrame) -> (pd.DataFrame, dict):
    """
    Expected columns from extension:
    foto_url,nama_usaha,alamat,no_telepon,latitude,longitude,link
    """
    audit = {
        "rows_in": 0,
        "rows_out": 0,
        "missing_cols": [],
        "dedup_removed": 0,
        "invalid_coord": 0,
        "invalid_link": 0,
        "empty_name": 0
    }

    if df_raw is None or df_raw.empty:
        return pd.DataFrame(columns=["Foto URL","Nama Usaha","Alamat","No Telepon","Latitude","Longitude","Link"]), audit

    audit["rows_in"] = len(df_raw)

    # map kolom (toleran)
    colmap_candidates = {
        "foto_url": ["foto_url", "foto", "photo", "gambar", "image"],
        "nama_usaha": ["nama_usaha", "nama usaha", "nama", "name"],
        "alamat": ["alamat", "address"],
        "no_telepon": ["no_telepon", "telepon", "phone", "no telp", "nomor"],
        "latitude": ["latitude", "lat"],
        "longitude": ["longitude", "lng", "lon", "long"],
        "link": ["link", "website", "url", "wa", "ig"]
    }

    found = {}
    cols_lower = {c.lower(): c for c in df_raw.columns}

    for k, cands in colmap_candidates.items():
        real = None
        for cc in cands:
            if cc.lower() in cols_lower:
                real = cols_lower[cc.lower()]
                break
        if real is None:
            audit["missing_cols"].append(k)
        found[k] = real

    # buat df kerja
    df = pd.DataFrame()
    for k, real in found.items():
        if real is None:
            df[k] = ""
        else:
            df[k] = df_raw[real].astype(str)

    # cleaning text
    df["foto_url"] = df["foto_url"].apply(clean_placeholder_to_empty)
    df["nama_usaha"] = df["nama_usaha"].apply(clean_placeholder_to_empty)
    df["alamat"] = df["alamat"].apply(clean_placeholder_to_empty)
    df["no_telepon"] = df["no_telepon"].apply(normalize_phone_id)
    df["link"] = df["link"].apply(normalize_url)

    # koordinat
    df["latitude_f"] = df["latitude"].apply(to_float_safe)
    df["longitude_f"] = df["longitude"].apply(to_float_safe)

    invalid_coord = df["latitude_f"].isna() | df["longitude_f"].isna()
    audit["invalid_coord"] = int(invalid_coord.sum())

    df["latitude"] = df["latitude_f"]
    df["longitude"] = df["longitude_f"]
    df.drop(columns=["latitude_f", "longitude_f"], inplace=True)

    # invalid link count
    audit["invalid_link"] = int((df["link"] == "").sum())

    # empty name
    audit["empty_name"] = int((df["nama_usaha"] == "").sum())

    # Dedupe pintar
    # key: nama + alamat + lat/lng (kalau lat/lng ada)
    def _key(r):
        name = (r["nama_usaha"] or "").lower()
        addr = (r["alamat"] or "").lower()
        lat = "" if pd.isna(r["latitude"]) else f"{r['latitude']:.6f}"
        lng = "" if pd.isna(r["longitude"]) else f"{r['longitude']:.6f}"
        return f"{name}__{addr}__{lat}__{lng}"

    before = len(df)
    df["_k"] = df.apply(_key, axis=1)
    df = df[df["_k"].str.strip() != "__"]  # buang baris yg total kosong
    df = df.drop_duplicates(subset=["_k"], keep="first").drop(columns=["_k"])
    after = len(df)
    audit["dedup_removed"] = int(before - after)

    # Final columns (rapi)
    df_out = pd.DataFrame({
        "Foto URL": df["foto_url"].fillna(""),
        "Nama Usaha": df["nama_usaha"].fillna(""),
        "Alamat": df["alamat"].fillna(""),
        "No Telepon": df["no_telepon"].fillna(""),
        "Latitude": df["latitude"],
        "Longitude": df["longitude"],
        "Link": df["link"].fillna("")
    })

    audit["rows_out"] = len(df_out)
    return df_out, audit

def df_to_excel_bytes(sheets: dict) -> bytes:
    """
    sheets: {sheet_name: dataframe}
    """
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        wb = writer.book
        header_fmt = wb.add_format({'bold': True, 'bg_color': BPS_OREN_UTAMA, 'font_color': 'white'})
        currency_fmt = wb.add_format({'num_format': '#,##0'})
        float_fmt = wb.add_format({'num_format': '0.000000'})

        for sheet_name, df in sheets.items():
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            ws = writer.sheets[sheet_name]

            # header format
            for col_num, value in enumerate(df.columns.values):
                ws.write(0, col_num, value, header_fmt)

            # autofilter
            if len(df) > 0:
                ws.autofilter(0, 0, len(df), len(df.columns) - 1)

            # column width heuristic
            for i, col in enumerate(df.columns):
                max_len = max([len(str(col))] + [len(str(x)) for x in df[col].astype(str).head(200).values])
                width = min(max(12, max_len + 2), 60)
                ws.set_column(i, i, width)

            # format angka
            for i, col in enumerate(df.columns):
                if col.lower() == "harga":
                    ws.set_column(i, i, 18, currency_fmt)
                if col.lower() in ["latitude", "longitude"]:
                    ws.set_column(i, i, 14, float_fmt)

    return buf.getvalue()

# --- 6. SIDEBAR MENU ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown(f"<h2 style='color:{BPS_OREN_UTAMA} !important; text-align:center;'>🏛️ BPS UMKM</h2>", unsafe_allow_html=True)

    st.markdown("### 🧭 Menu Navigasi")
    halaman = st.radio(
        "Pilih Fitur:",
        ["🟠 Shopee", "🟢 Tokopedia", "🔵 Facebook FB", "📍 Google Maps", "📊 Export Gabungan"],
    )
    st.divider()

babel_keys = ["pangkal", "bangka", "belitung", "sungailiat", "mentok", "muntok", "koba", "toboali", "manggar", "tanjung pandan", "tanjungpandan"]

# =================================================================================================
#                                            HALAMAN SHOPEE
# =================================================================================================
if halaman == "🟠 Shopee":
    st.markdown("""
    <div class="banner-bps">
        <div class="banner-sub-title">🏛️ BADAN PUSAT STATISTIK</div>
        <h1>Dashboard UMKM - Shopee</h1>
        <p>Ekstraksi Data UMKM dari Shopee Marketplace Wilayah Bangka Belitung</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Shopee")
        files_shopee = st.file_uploader("Unggah CSV Shopee", type=["csv"], accept_multiple_files=True, key="file_shp")
        mode_api_shp = st.checkbox("🔍 Deteksi Nama Toko (API)", key="api_shp", value=True, help="Wajib dicentang agar sistem bisa mendeteksi Tipe Usaha!")

        if st.button("🚀 Proses Data Shopee", type="primary", use_container_width=True):
            if not files_shopee:
                st.error("⚠️ Silakan unggah file CSV Shopee terlebih dahulu.")
            elif not mode_api_shp:
                st.warning("⚠️ Untuk deteksi Toko Fisik/Murni Online, Centang kotak 'Deteksi Nama Toko (API)'!")
            else:
                with st.spinner("Sedang membaca file CSV..."):
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
                                            res = requests.get(
                                                f"https://shopee.co.id/api/v4/shop/get_shop_base?shopid={match.group(1)}",
                                                headers={"User-Agent": "Mozilla/5.0"},
                                                timeout=2
                                            )
                                            if res.status_code == 200:
                                                toko = res.json().get("data", {}).get("name", "Anonim")
                                        except:
                                            pass

                                tipe_usaha = deteksi_tipe_usaha(toko)
                                hasil.append({
                                    "Nama Toko": toko, "Nama Produk": nama, "Harga": val_h,
                                    "Wilayah": lokasi_shopee, "Tipe Usaha": tipe_usaha, "Link": link
                                })

                                baris_diproses += 1
                                if baris_diproses % 5 == 0 or baris_diproses == total_semua_baris:
                                    pct = min(baris_diproses / total_semua_baris, 1.0)
                                    progress_bar.progress(pct)
                                    status_text.markdown(f"**⏳ Mengekstrak:** {baris_diproses} / {total_semua_baris} baris ({int(pct*100)}%)")

                        status_text.empty()
                        progress_bar.empty()

                        st.session_state.data_shopee = pd.DataFrame(hasil)
                        st.session_state.audit_shopee = {
                            "total": total_baris, "valid": len(hasil), "file_count": len(files_shopee),
                            "error_harga": err_h, "luar": luar_wilayah
                        }
                        st.success(f"✅ Berhasil! {len(hasil)} data UMKM Shopee siap dianalisis.")
                    except Exception as e:
                        st.error(f"Error Sistem: {e}")

    df_shp = st.session_state.data_shopee
    if df_shp is not None and not df_shp.empty:
        with st.container(border=True):
            st.markdown("#### 🔎 Filter Data Pintar")
            col_f1, col_f2, col_f3 = st.columns([1, 1, 1.5])
            with col_f1:
                f_wil = st.multiselect("📍 Wilayah:", options=sorted(df_shp["Wilayah"].unique()),
                                       default=sorted(df_shp["Wilayah"].unique()), key="f_wil_shp")
            with col_f2:
                f_tipe = st.multiselect("🏢 Tipe Usaha:", options=sorted(df_shp["Tipe Usaha"].unique()),
                                        default=sorted(df_shp["Tipe Usaha"].unique()), key="f_tipe_shp")
            with col_f3:
                max_h = int(df_shp["Harga"].max()) if df_shp["Harga"].max() > 0 else 1000000
                f_hrg = st.slider("💰 Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_shp")

        df_f = df_shp[df_shp["Wilayah"].isin(f_wil) & df_shp["Tipe Usaha"].isin(f_tipe) &
                      (df_shp["Harga"] >= f_hrg[0]) & (df_shp["Harga"] <= f_hrg[1])]

        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Audit"])
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("📌 Total Data Ditampilkan", f"{len(df_f):,}".replace(",", "."))
            c2.metric("🏠 Usaha Murni Online", f"{len(df_f[df_f['Tipe Usaha'] == 'Murni Online (Rumahan)']):,}".replace(",", "."))
            c3.metric("🗺️ Sebaran Wilayah", f"{df_f['Wilayah'].nunique()}")

            st.markdown("<br>", unsafe_allow_html=True)
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1:
                    fig_pie = px.pie(df_f, names="Tipe Usaha", title="Komposisi Model Bisnis UMKM", hole=0.4, color_discrete_sequence=BPS_PALETTE)
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                    st.plotly_chart(fig_pie, use_container_width=True)
                with g2:
                    fig_bar = px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'),
                                     x="Wilayah", y="Jumlah", title="Total Usaha Berdasarkan Wilayah",
                                     color="Wilayah", color_discrete_sequence=BPS_PALETTE)
                    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                    st.plotly_chart(fig_bar, use_container_width=True)

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=400)

            if not df_f.empty:
                excel_bytes = df_to_excel_bytes({"Data Shopee": df_f})
                st.markdown(f'<style>div[data-testid="stDownloadButton"] button {{background-color: {BPS_OREN_UTAMA} !important; color: white !important; border:none;}}</style>', unsafe_allow_html=True)
                st.download_button("⬇️ Unduh Excel Database Shopee", data=excel_bytes,
                                   file_name=f"UMKM_Shopee_{datetime.date.today()}.xlsx", type="primary")

        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            audit = st.session_state.audit_shopee
            st.info(f"**📂 Dokumen Diproses:** {audit.get('file_count',0)} File CSV")
            st.success(f"**📥 Data Baris Terekstrak Bersih:** {audit.get('valid',0)} Baris")
            st.warning(f"**⚠️ Data Diabaikan (Luar Wilayah):** {audit.get('luar',0)} Baris")

# =================================================================================================
#                                            HALAMAN TOKOPEDIA
# =================================================================================================
elif halaman == "🟢 Tokopedia":
    st.markdown("""
    <div class="banner-bps">
        <div class="banner-sub-title">🏛️ BADAN PUSAT STATISTIK</div>
        <h1>Dashboard UMKM - Tokopedia</h1>
        <p>Ekstraksi Data UMKM dari Tokopedia Wilayah Bangka Belitung</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Tokopedia")
        files_tokped = st.file_uploader("Unggah CSV Tokopedia", type=["csv"], accept_multiple_files=True, key="file_tkp")

        if st.button("🚀 Proses Data Tokopedia", type="primary", use_container_width=True):
            if not files_tokped:
                st.error("⚠️ Silakan unggah file CSV Tokopedia terlebih dahulu.")
            else:
                with st.spinner("Sedang membaca file CSV..."):
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
                                            hasil.append({
                                                "Nama Toko": toko, "Nama Produk": nama, "Harga": val_h,
                                                "Wilayah": lokasi_tokped, "Tipe Usaha": tipe_usaha, "Link": link
                                            })

                                    except Exception:
                                        continue

                                baris_diproses += 1
                                if baris_diproses % 5 == 0 or baris_diproses == total_semua_baris:
                                    pct = min(baris_diproses / total_semua_baris, 1.0)
                                    progress_bar.progress(pct)
                                    status_text.markdown(f"**⏳ Mengekstrak:** {baris_diproses} / {total_semua_baris} baris ({int(pct*100)}%)")

                        status_text.empty()
                        progress_bar.empty()

                        df_final = pd.DataFrame(hasil).drop_duplicates()
                        st.session_state.data_tokped = df_final
                        st.session_state.audit_tokped = {
                            "total": total_baris, "valid": len(df_final), "file_count": len(files_tokped),
                            "error_harga": err_h, "luar": luar_wilayah
                        }
                        st.success(f"✅ Berhasil! {len(df_final)} data UMKM Tokopedia diekstrak.")
                    except Exception as e:
                        st.error(f"Error Sistem Tokopedia: {e}")

    df_tkp = st.session_state.data_tokped
    if df_tkp is not None and not df_tkp.empty:
        with st.container(border=True):
            st.markdown("#### 🔎 Filter Data Pintar")
            col_f1, col_f2, col_f3 = st.columns([1, 1, 1.5])
            with col_f1:
                f_wil = st.multiselect("📍 Wilayah:", options=sorted(df_tkp["Wilayah"].unique()),
                                       default=sorted(df_tkp["Wilayah"].unique()), key="f_wil_tkp")
            with col_f2:
                f_tipe = st.multiselect("🏢 Tipe Usaha:", options=sorted(df_tkp["Tipe Usaha"].unique()),
                                        default=sorted(df_tkp["Tipe Usaha"].unique()), key="f_tipe_tkp")
            with col_f3:
                max_h = int(df_tkp["Harga"].max()) if df_tkp["Harga"].max() > 0 else 1000000
                f_hrg = st.slider("💰 Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_tkp")

        df_f = df_tkp[df_tkp["Wilayah"].isin(f_wil) & df_tkp["Tipe Usaha"].isin(f_tipe) &
                      (df_tkp["Harga"] >= f_hrg[0]) & (df_tkp["Harga"] <= f_hrg[1])]

        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Audit"])
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("📌 Total Data Ditampilkan", f"{len(df_f):,}".replace(",", "."))
            c2.metric("🏠 Usaha Murni Online", f"{len(df_f[df_f['Tipe Usaha'] == 'Murni Online (Rumahan)']):,}".replace(",", "."))
            c3.metric("🗺️ Sebaran Wilayah", f"{df_f['Wilayah'].nunique()}")

            st.markdown("<br>", unsafe_allow_html=True)
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1:
                    fig_pie = px.pie(df_f, names="Tipe Usaha", title="Komposisi Model Bisnis UMKM", hole=0.4, color_discrete_sequence=BPS_PALETTE)
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                    st.plotly_chart(fig_pie, use_container_width=True)
                with g2:
                    fig_bar = px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'),
                                     x="Wilayah", y="Jumlah", title="Total Usaha Berdasarkan Wilayah",
                                     color="Wilayah", color_discrete_sequence=BPS_PALETTE)
                    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                    st.plotly_chart(fig_bar, use_container_width=True)

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=400)

            if not df_f.empty:
                excel_bytes = df_to_excel_bytes({"Data Tokopedia": df_f})
                st.markdown(f'<style>div[data-testid="stDownloadButton"] button {{background-color: {BPS_OREN_UTAMA} !important; color: white !important; border:none;}}</style>', unsafe_allow_html=True)
                st.download_button("⬇️ Unduh Excel Database Tokopedia", data=excel_bytes,
                                   file_name=f"UMKM_Tokopedia_{datetime.date.today()}.xlsx")

        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            audit = st.session_state.audit_tokped
            st.info(f"**📂 Dokumen Diproses:** {audit.get('file_count',0)} File CSV")
            st.success(f"**📥 Data Baris Terekstrak Bersih:** {audit.get('valid',0)} Baris")
            st.warning(f"**⚠️ Data Diabaikan (Luar Wilayah):** {audit.get('luar',0)} Baris")

# =================================================================================================
#                                            HALAMAN FACEBOOK MARKETPLACE
# =================================================================================================
elif halaman == "🔵 Facebook FB":
    st.markdown("""
    <div class="banner-bps">
        <div class="banner-sub-title">🏛️ BADAN PUSAT STATISTIK</div>
        <h1>Dashboard UMKM - Facebook</h1>
        <p>Ekstraksi Data UMKM dari Facebook Marketplace Wilayah Bangka Belitung</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Facebook")
        files_fb = st.file_uploader("Unggah CSV Facebook", type=["csv"], accept_multiple_files=True, key="file_fb")

        if st.button("🚀 Proses Data Facebook", type="primary", use_container_width=True):
            if not files_fb:
                st.error("⚠️ Silakan unggah file CSV Facebook FB terlebih dahulu.")
            else:
                with st.spinner("Sedang membaca file CSV..."):
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
                                    hasil.append({
                                        "Nama Toko": toko, "Nama Produk": nama, "Harga": val_h,
                                        "Wilayah": lokasi_fb, "Tipe Usaha": tipe_usaha, "Link": link
                                    })

                                baris_diproses += 1
                                if baris_diproses % 5 == 0 or baris_diproses == total_semua_baris:
                                    pct = min(baris_diproses / total_semua_baris, 1.0)
                                    progress_bar.progress(pct)
                                    status_text.markdown(f"**⏳ Mengekstrak:** {baris_diproses} / {total_semua_baris} baris ({int(pct*100)}%)")

                        status_text.empty()
                        progress_bar.empty()

                        df_final = pd.DataFrame(hasil).drop_duplicates()
                        st.session_state.data_fb = df_final
                        st.session_state.audit_fb = {
                            "total": total_baris, "valid": len(df_final), "file_count": len(files_fb),
                            "error_harga": err_h, "luar": luar_wilayah
                        }
                        st.success(f"✅ Berhasil! {len(df_final)} data UMKM Facebook FB diekstrak.")
                    except Exception as e:
                        st.error(f"Error Sistem FB: {e}")

    df_fb = st.session_state.data_fb
    if df_fb is not None and not df_fb.empty:
        with st.container(border=True):
            st.markdown("#### 🔎 Filter Data Pintar")
            col_f1, col_f2, col_f3 = st.columns([1, 1, 1.5])
            with col_f1:
                f_wil = st.multiselect("📍 Wilayah:", options=sorted(df_fb["Wilayah"].unique()),
                                       default=sorted(df_fb["Wilayah"].unique()), key="f_wil_fb")
            with col_f2:
                f_tipe = st.multiselect("🏢 Tipe Usaha:", options=sorted(df_fb["Tipe Usaha"].unique()),
                                        default=sorted(df_fb["Tipe Usaha"].unique()), key="f_tipe_fb")
            with col_f3:
                max_h = int(df_fb["Harga"].max()) if df_fb["Harga"].max() > 0 else 1000000
                f_hrg = st.slider("💰 Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_fb")

        df_f = df_fb[df_fb["Wilayah"].isin(f_wil) & df_fb["Tipe Usaha"].isin(f_tipe) &
                     (df_fb["Harga"] >= f_hrg[0]) & (df_fb["Harga"] <= f_hrg[1])]

        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Audit"])
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("📌 Total Data Ditampilkan", f"{len(df_f):,}".replace(",", "."))
            c2.metric("👤 Usaha Perorangan", f"{len(df_f[df_f['Tipe Usaha'] == 'Perorangan (Facebook)']):,}".replace(",", "."))
            c3.metric("🗺️ Sebaran Wilayah", f"{df_f['Wilayah'].nunique()}")

            st.markdown("<br>", unsafe_allow_html=True)
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1:
                    fig_pie = px.pie(df_f, names="Tipe Usaha", title="Komposisi Model Bisnis FB", hole=0.4, color_discrete_sequence=BPS_PALETTE)
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                    st.plotly_chart(fig_pie, use_container_width=True)
                with g2:
                    fig_bar = px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'),
                                     x="Wilayah", y="Jumlah", title="Total Usaha Berdasarkan Wilayah FB",
                                     color="Wilayah", color_discrete_sequence=BPS_PALETTE)
                    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                    st.plotly_chart(fig_bar, use_container_width=True)

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=400)

            if not df_f.empty:
                excel_bytes = df_to_excel_bytes({"Data Facebook": df_f})
                st.markdown(f'<style>div[data-testid="stDownloadButton"] button {{background-color: {BPS_OREN_UTAMA} !important; color: white !important; border:none;}}</style>', unsafe_allow_html=True)
                st.download_button("⬇️ Unduh Excel Database Facebook", data=excel_bytes,
                                   file_name=f"UMKM_Facebook_{datetime.date.today()}.xlsx")

        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            audit = st.session_state.audit_fb
            st.info(f"**📂 Dokumen Diproses:** {audit.get('file_count',0)} File CSV")
            st.success(f"**📥 Data Baris Terekstrak Bersih:** {audit.get('valid',0)} Baris")
            st.warning(f"**⚠️ Data Diabaikan (Luar Wilayah):** {audit.get('luar',0)} Baris")

# =================================================================================================
#                                            HALAMAN GOOGLE MAPS (UMKM)
# =================================================================================================
elif halaman == "📍 Google Maps":
    st.markdown("""
    <div class="banner-bps">
        <div class="banner-sub-title">🏛️ BADAN PUSAT STATISTIK</div>
        <h1>Dashboard UMKM - Google Maps</h1>
        <p>Upload CSV hasil ekstensi Google Maps → auto-clean → siap ekspor Excel bersih</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Google Maps")
        files_maps = st.file_uploader("Unggah CSV Google Maps", type=["csv"], accept_multiple_files=True, key="file_maps")
        do_clean = st.checkbox("✨ Auto-clean Data (disarankan)", value=True, key="clean_maps")

        if st.button("🚀 Proses Data Google Maps", type="primary", use_container_width=True):
            if not files_maps:
                st.error("⚠️ Silakan unggah file CSV Google Maps terlebih dahulu.")
            else:
                try:
                    dfs = []
                    total_rows = 0
                    for f in files_maps:
                        df_temp = pd.read_csv(f, dtype=str, on_bad_lines="skip")
                        total_rows += len(df_temp)
                        dfs.append(df_temp)

                    df_raw = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
                    if do_clean:
                        df_clean, audit = clean_maps_dataframe(df_raw)
                    else:
                        # kalau user matiin clean, tetap rapikan minimal kolom
                        df_clean, audit = clean_maps_dataframe(df_raw)

                    st.session_state.data_maps = df_clean
                    st.session_state.audit_maps = {
                        "file_count": len(files_maps),
                        "rows_in": audit.get("rows_in", 0),
                        "rows_out": audit.get("rows_out", 0),
                        "dedup_removed": audit.get("dedup_removed", 0),
                        "invalid_coord": audit.get("invalid_coord", 0),
                        "invalid_link": audit.get("invalid_link", 0),
                        "empty_name": audit.get("empty_name", 0),
                        "missing_cols": audit.get("missing_cols", [])
                    }
                    st.success(f"✅ Berhasil! {len(df_clean)} data Google Maps siap dianalisis & diekspor.")
                except Exception as e:
                    st.error(f"Error Sistem Google Maps: {e}")

    df_maps = st.session_state.data_maps
    if df_maps is not None and not df_maps.empty:
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🧹 Data Bersih", "📑 Log Audit"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("📌 Total Data", f"{len(df_maps):,}".replace(",", "."))
            c2.metric("🗺️ Punya Koordinat Valid", f"{df_maps['Latitude'].notna().sum():,}".replace(",", "."))
            c3.metric("🔗 Punya Link Valid", f"{(df_maps['Link'].astype(str).str.len() > 0).sum():,}".replace(",", "."))

            st.markdown("<br>", unsafe_allow_html=True)
            # Map plot kalau koordinat ada
            df_plot = df_maps.dropna(subset=["Latitude", "Longitude"]).copy()
            if not df_plot.empty:
                try:
                    fig_scatter = px.scatter_mapbox(
                        df_plot,
                        lat="Latitude",
                        lon="Longitude",
                        hover_name="Nama Usaha",
                        hover_data={"Alamat": True, "No Telepon": True, "Link": True},
                        zoom=7,
                        height=520
                    )
                    fig_scatter.update_layout(mapbox_style="open-street-map")
                    fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                    st.plotly_chart(fig_scatter, use_container_width=True)
                except Exception:
                    st.info("Peta tidak bisa dirender (plotly mapbox). Data koordinat sudah siap di-export.")

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(df_maps, use_container_width=True, hide_index=True, height=420)

            excel_bytes = df_to_excel_bytes({"Data Google Maps": df_maps})
            st.markdown(f'<style>div[data-testid="stDownloadButton"] button {{background-color: {BPS_OREN_UTAMA} !important; color: white !important; border:none;}}</style>', unsafe_allow_html=True)
            st.download_button(
                "⬇️ Unduh Excel Database Google Maps (Bersih)",
                data=excel_bytes,
                file_name=f"UMKM_GoogleMaps_Bersih_{datetime.date.today()}.xlsx",
                type="primary"
            )

            # optional: download CSV bersih juga
            csv_bytes = df_maps.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Unduh CSV Google Maps (Bersih)",
                data=csv_bytes,
                file_name=f"UMKM_GoogleMaps_Bersih_{datetime.date.today()}.csv",
                use_container_width=True
            )

        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            audit = st.session_state.audit_maps
            st.info(f"**📂 Dokumen Diproses:** {audit.get('file_count',0)} File CSV")
            st.success(f"**📥 Baris Masuk:** {audit.get('rows_in',0)}")
            st.success(f"**✅ Baris Keluar (Bersih):** {audit.get('rows_out',0)}")
            st.warning(f"**🧽 Duplikat Dihapus:** {audit.get('dedup_removed',0)}")
            st.warning(f"**📍 Koordinat Tidak Valid:** {audit.get('invalid_coord',0)}")
            st.warning(f"**🔗 Link Tidak Valid:** {audit.get('invalid_link',0)}")
            st.warning(f"**🏷️ Nama Usaha Kosong:** {audit.get('empty_name',0)}")
            if audit.get("missing_cols"):
                st.warning(f"**Kolom tidak ditemukan (diisi kosong):** {', '.join(audit['missing_cols'])}")

# =================================================================================================
#                                            HALAMAN EXPORT GABUNGAN
# =================================================================================================
elif halaman == "📊 Export Gabungan":
    st.markdown("""
    <div class="banner-bps">
        <div class="banner-sub-title">🏛️ BADAN PUSAT STATISTIK</div>
        <h1>Export Master Data Gabungan</h1>
        <p>Konsolidasi Master Data (Shopee, Tokopedia, Facebook, Google Maps) - Siap Analisis</p>
    </div>
    """, unsafe_allow_html=True)

    df_shp_ready = st.session_state.data_shopee is not None and not st.session_state.data_shopee.empty
    df_tkp_ready = st.session_state.data_tokped is not None and not st.session_state.data_tokped.empty
    df_fb_ready = st.session_state.data_fb is not None and not st.session_state.data_fb.empty
    df_maps_ready = st.session_state.data_maps is not None and not st.session_state.data_maps.empty

    if not df_shp_ready and not df_tkp_ready and not df_fb_ready and not df_maps_ready:
        st.warning("⚠️ Belum ada data yang diekstrak. Silakan unggah dan proses dokumen di menu Shopee, Tokopedia, Facebook, atau Google Maps.")
    else:
        st.success("✅ Data siap dikonsolidasi menjadi satu file Master Excel (4-in-1)!")

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        if df_shp_ready: c1.metric("📦 Shopee", f"{len(st.session_state.data_shopee):,}".replace(",", "."))
        if df_tkp_ready: c2.metric("📦 Tokopedia", f"{len(st.session_state.data_tokped):,}".replace(",", "."))
        if df_fb_ready: c3.metric("📦 Facebook", f"{len(st.session_state.data_fb):,}".replace(",", "."))
        if df_maps_ready: c4.metric("📦 Google Maps", f"{len(st.session_state.data_maps):,}".replace(",", "."))

        st.write("---")
        st.markdown("File akan diunduh dengan format **Sheet Terpisah per sumber**, lengkap dengan **Auto-Filter**, dan kolom rapi (Excel bersih).")

        sheets = {}
        if df_shp_ready: sheets["Data Shopee"] = st.session_state.data_shopee
        if df_tkp_ready: sheets["Data Tokopedia"] = st.session_state.data_tokped
        if df_fb_ready: sheets["Data Facebook"] = st.session_state.data_fb
        if df_maps_ready: sheets["Data Google Maps"] = st.session_state.data_maps

        excel_bytes = df_to_excel_bytes(sheets)

        st.markdown(
            f'<style>div[data-testid="stDownloadButton"] button {{background-color: {BPS_OREN_UTAMA} !important; color: white !important; border:1px solid #ffffff; height: 3.5rem; font-size: 1.1rem; border-radius: 8px; box-shadow: 0 4px 15px rgba(255, 111, 0, 0.5);}}</style>',
            unsafe_allow_html=True
        )

        _, col_btn, _ = st.columns([1, 2, 1])
        with col_btn:
            st.download_button(
                label="⬇️ UNDUH EXCEL MASTER (4-IN-1)",
                data=excel_bytes,
                file_name=f"Master_UMKM_BPS_{datetime.date.today()}.xlsx",
                use_container_width=True
            )
