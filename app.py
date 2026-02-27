import streamlit as st
import pandas as pd
import re
import io
import requests
import plotly.express as px
import datetime
import os

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
    [data-testid="stHeader"] {{ background: transparent !important; }}

    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(135deg, #FF6F00 0%, #7A3400 35%, #0f0f0f 100%) !important;
        background-attachment: fixed !important;
    }}

    .stApp {{ color: #ffffff; }}
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
    [data-testid="stSidebar"] * {{ color: #ffffff !important; }}

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

# --- 4. FUNGSI DETEKSI TIPE USAHA ---
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


def rp(x):
    try:
        return f"Rp {int(x):,}".replace(",", ".")
    except:
        return str(x)


def buat_ringkasan_toko(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tampilan ringkas: 1 toko = 1 baris, produk tidak dipanjangin.
    """
    if df is None or df.empty:
        return df

    dfx = df.copy()
    dfx["Harga"] = pd.to_numeric(dfx.get("Harga", 0), errors="coerce").fillna(0).astype(int)

    group_cols = [c for c in ["Nama Toko", "Wilayah", "Tipe Usaha"] if c in dfx.columns]

    def uniq_count(s):
        vals = [str(x).strip() for x in s.dropna().tolist() if str(x).strip() not in ["", "nan", "None"]]
        return len(dict.fromkeys(vals))

    out = (
        dfx.groupby(group_cols, dropna=False, as_index=False)
           .agg(
               **{
                   "Jumlah Produk": ("Nama Produk", uniq_count),
                   "Harga Min": ("Harga", "min"),
                   "Harga Max": ("Harga", "max"),
               }
           )
    )
    return out


def excel_export(df_ringkas: pd.DataFrame | None, df_detail: pd.DataFrame | None, filename: str):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        wb = writer.book
        header_fmt = wb.add_format({'bold': True, 'bg_color': BPS_OREN_UTAMA, 'font_color': 'white'})
        currency_fmt = wb.add_format({'num_format': '#,##0'})

        if df_ringkas is not None and not df_ringkas.empty:
            df_ringkas.to_excel(writer, index=False, sheet_name="Ringkas Per Toko")
            ws = writer.sheets["Ringkas Per Toko"]
            for col_num, value in enumerate(df_ringkas.columns.values):
                ws.write(0, col_num, value, header_fmt)
            ws.set_column(0, len(df_ringkas.columns) - 1, 22)
            ws.autofilter(0, 0, len(df_ringkas), len(df_ringkas.columns) - 1)

        if df_detail is not None and not df_detail.empty:
            df_detail.to_excel(writer, index=False, sheet_name="Detail Produk")
            ws = writer.sheets["Detail Produk"]
            for col_num, value in enumerate(df_detail.columns.values):
                ws.write(0, col_num, value, header_fmt)
            # Harga numeric
            if "Harga" in df_detail.columns:
                hidx = list(df_detail.columns).index("Harga")
                ws.set_column(hidx, hidx, 14, currency_fmt)
            ws.set_column(0, len(df_detail.columns) - 1, 22)
            ws.autofilter(0, 0, len(df_detail), len(df_detail.columns) - 1)

    st.download_button(
        label=f"⬇️ Unduh Excel ({filename})",
        data=buf.getvalue(),
        file_name=filename,
        type="primary",
        use_container_width=True
    )

# --- 5. SIDEBAR MENU ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown(f"<h2 style='color:{BPS_OREN_UTAMA} !important; text-align:center;'>🏛️ BPS UMKM</h2>", unsafe_allow_html=True)

    st.markdown("### 🧭 Menu Navigasi")
    halaman = st.radio("Pilih Fitur:", ["🟠 Shopee", "🟢 Tokopedia", "🔵 Facebook FB", "📊 Export Gabungan"])
    st.divider()

babel_keys = ["pangkal", "bangka", "belitung", "sungailiat", "mentok", "muntok", "koba", "toboali", "manggar", "tanjung pandan", "tanjungpandan"]

# ==============================================================================
#                             HALAMAN SHOPEE
# ==============================================================================
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

                            # Deteksi kolom
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
                                    "Nama Toko": toko,
                                    "Nama Produk": nama,
                                    "Harga": val_h,
                                    "Wilayah": lokasi_shopee,
                                    "Tipe Usaha": tipe_usaha,
                                    "Link": link
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
                            "total": total_baris,
                            "valid": len(hasil),
                            "file_count": len(files_shopee),
                            "error_harga": err_h,
                            "luar": luar_wilayah
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

        df_f = df_shp[
            df_shp["Wilayah"].isin(f_wil) &
            df_shp["Tipe Usaha"].isin(f_tipe) &
            (df_shp["Harga"] >= f_hrg[0]) &
            (df_shp["Harga"] <= f_hrg[1])
        ]

        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database (Ringkas + Detail)", "📑 Log Audit"])

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
                    fig_pie = px.pie(df_f, names="Tipe Usaha", title="Komposisi Model Bisnis UMKM", hole=0.4,
                                     color_discrete_sequence=BPS_PALETTE)
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

            st.markdown("### ✅ Tabel Ringkas (1 Toko = 1 Baris)")
            df_ringkas = buat_ringkasan_toko(df_f).copy()
            if df_ringkas is None or df_ringkas.empty:
                st.warning("Tidak ada data setelah filter.")
            else:
                df_ringkas["Harga Min"] = df_ringkas["Harga Min"].apply(rp)
                df_ringkas["Harga Max"] = df_ringkas["Harga Max"].apply(rp)
                st.dataframe(df_ringkas, use_container_width=True, hide_index=True, height=300)

                st.markdown("### 🔍 Detail Produk per Toko (biar kelihatan jelas)")
                toko_opsi = df_ringkas["Nama Toko"].dropna().unique().tolist()
                toko_pilih = st.selectbox("Pilih toko:", options=toko_opsi, key="detail_toko_shp")

                df_detail = df_f[df_f["Nama Toko"] == toko_pilih].copy()
                df_detail = df_detail.sort_values(["Nama Produk"], na_position="last")
                df_detail_view = df_detail.copy()
                df_detail_view["Harga"] = df_detail_view["Harga"].apply(rp)

                st.dataframe(
                    df_detail_view[["Nama Produk", "Harga", "Wilayah", "Tipe Usaha", "Link"]],
                    use_container_width=True,
                    hide_index=True,
                    height=350
                )

                st.markdown("### ⬇️ Export Excel")
                mode_export = st.radio(
                    "Pilih mode export:",
                    ["Ringkas per Toko (sheet ringkas)", "Detail Semua Produk (sheet detail)"],
                    horizontal=True,
                    key="export_mode_shp"
                )

                if mode_export.startswith("Ringkas"):
                    excel_export(df_ringkas, None, f"UMKM_Shopee_RINGKAS_{datetime.date.today()}.xlsx")
                else:
                    excel_export(None, df_detail, f"UMKM_Shopee_DETAIL_{datetime.date.today()}.xlsx")

        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            audit = st.session_state.audit_shopee
            st.info(f"**📂 Dokumen Diproses:** {audit.get('file_count', 0)} File CSV")
            st.success(f"**📥 Data Baris Terekstrak Bersih:** {audit.get('valid', 0)} Baris")
            st.warning(f"**⚠️ Data Diabaikan (Luar Wilayah):** {audit.get('luar', 0)} Baris")

# ==============================================================================
#                             HALAMAN TOKOPEDIA
# ==============================================================================
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
                                col_link, col_nama, col_harga, col_wilayah, col_toko = "Link", "Nama Produk", "Harga", "Wilayah", "Nama Toko"
                            else:
                                col_link = df_raw.columns[0]
                                col_nama = df_raw.columns[1]
                                col_wilayah = df_raw.columns[2]
                                col_toko = df_raw.columns[3]
                                col_harga = df_raw.columns[4] if len(df_raw.columns) > 4 else df_raw.columns[-1]

                            for i in range(len(df_raw)):
                                row = df_raw.iloc[i]
                                link = str(row[col_link])
                                nama = str(row[col_nama])
                                harga_str = str(row[col_harga])
                                lokasi = str(row[col_wilayah]).title()
                                toko = str(row[col_toko]).strip() if col_toko in df_raw.columns else "Toko CSV"

                                if not any(k in lokasi.lower() for k in babel_keys):
                                    luar_wilayah += 1
                                    baris_diproses += 1
                                    continue

                                try:
                                    harga_bersih = harga_str.replace('.', '').replace(',', '')
                                    angka_list = re.findall(r'\d+', harga_bersih)
                                    val_h = int(angka_list[0]) if angka_list else 0
                                    if val_h > 1000000000: val_h = 0
                                except:
                                    val_h, err_h = 0, err_h + 1

                                tipe_usaha = deteksi_tipe_usaha(toko)
                                hasil.append({
                                    "Nama Toko": toko,
                                    "Nama Produk": nama,
                                    "Harga": val_h,
                                    "Wilayah": lokasi,
                                    "Tipe Usaha": tipe_usaha,
                                    "Link": link
                                })

                                baris_diproses += 1
                                if baris_diproses % 5 == 0 or baris_diproses == total_semua_baris:
                                    pct = min(baris_diproses / total_semua_baris, 1.0)
                                    progress_bar.progress(pct)
                                    status_text.markdown(f"**⏳ Mengekstrak:** {baris_diproses} / {total_semua_baris} baris ({int(pct*100)}%)")

                        status_text.empty()
                        progress_bar.empty()

                        st.session_state.data_tokped = pd.DataFrame(hasil)
                        st.session_state.audit_tokped = {
                            "total": total_baris,
                            "valid": len(hasil),
                            "file_count": len(files_tokped),
                            "error_harga": err_h,
                            "luar": luar_wilayah
                        }
                        st.success(f"✅ Berhasil! {len(hasil)} data UMKM Tokopedia siap dianalisis.")
                    except Exception as e:
                        st.error(f"Error Sistem: {e}")

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

        df_f = df_tkp[
            df_tkp["Wilayah"].isin(f_wil) &
            df_tkp["Tipe Usaha"].isin(f_tipe) &
            (df_tkp["Harga"] >= f_hrg[0]) &
            (df_tkp["Harga"] <= f_hrg[1])
        ]

        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database (Ringkas + Detail)", "📑 Log Audit"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("📌 Total Data Ditampilkan", f"{len(df_f):,}".replace(",", "."))
            c2.metric("🏠 Usaha Murni Online", f"{len(df_f[df_f['Tipe Usaha'] == 'Murni Online (Rumahan)']):,}".replace(",", "."))
            c3.metric("🗺️ Sebaran Wilayah", f"{df_f['Wilayah'].nunique()}")

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("### ✅ Tabel Ringkas (1 Toko = 1 Baris)")
            df_ringkas = buat_ringkasan_toko(df_f).copy()
            if df_ringkas is None or df_ringkas.empty:
                st.warning("Tidak ada data setelah filter.")
            else:
                df_ringkas["Harga Min"] = df_ringkas["Harga Min"].apply(rp)
                df_ringkas["Harga Max"] = df_ringkas["Harga Max"].apply(rp)
                st.dataframe(df_ringkas, use_container_width=True, hide_index=True, height=300)

                st.markdown("### 🔍 Detail Produk per Toko")
                toko_opsi = df_ringkas["Nama Toko"].dropna().unique().tolist()
                toko_pilih = st.selectbox("Pilih toko:", options=toko_opsi, key="detail_toko_tkp")

                df_detail = df_f[df_f["Nama Toko"] == toko_pilih].copy()
                df_detail = df_detail.sort_values(["Nama Produk"], na_position="last")
                df_detail_view = df_detail.copy()
                df_detail_view["Harga"] = df_detail_view["Harga"].apply(rp)

                st.dataframe(
                    df_detail_view[["Nama Produk", "Harga", "Wilayah", "Tipe Usaha", "Link"]],
                    use_container_width=True,
                    hide_index=True,
                    height=350
                )

                st.markdown("### ⬇️ Export Excel")
                mode_export = st.radio(
                    "Pilih mode export:",
                    ["Ringkas per Toko (sheet ringkas)", "Detail Semua Produk (sheet detail)"],
                    horizontal=True,
                    key="export_mode_tkp"
                )

                if mode_export.startswith("Ringkas"):
                    excel_export(df_ringkas, None, f"UMKM_Tokopedia_RINGKAS_{datetime.date.today()}.xlsx")
                else:
                    excel_export(None, df_detail, f"UMKM_Tokopedia_DETAIL_{datetime.date.today()}.xlsx")

        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            audit = st.session_state.audit_tokped
            st.info(f"**📂 Dokumen Diproses:** {audit.get('file_count', 0)} File CSV")
            st.success(f"**📥 Data Baris Terekstrak Bersih:** {audit.get('valid', 0)} Baris")
            st.warning(f"**⚠️ Data Diabaikan (Luar Wilayah):** {audit.get('luar', 0)} Baris")

# ==============================================================================
#                             HALAMAN FACEBOOK MARKETPLACE
# ==============================================================================
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
                                toko = str(row[col_toko]).strip() if col_toko in df_raw.columns else "FB Seller"
                                nama = str(row[col_nama])
                                lokasi = str(row[col_wilayah]).title()
                                harga_str = str(row[col_harga])
                                link = str(row[col_link])

                                if not any(k in lokasi.lower() for k in babel_keys):
                                    luar_wilayah += 1
                                    baris_diproses += 1
                                    continue

                                try:
                                    harga_bersih = harga_str.replace('.', '').replace(',', '')
                                    angka_list = re.findall(r'\d+', harga_bersih)
                                    val_h = int(angka_list[0]) if angka_list else 0
                                    if val_h > 1000000000: val_h = 0
                                except:
                                    val_h, err_h = 0, err_h + 1

                                tipe_usaha = deteksi_tipe_usaha(toko)
                                hasil.append({
                                    "Nama Toko": toko,
                                    "Nama Produk": nama,
                                    "Harga": val_h,
                                    "Wilayah": lokasi,
                                    "Tipe Usaha": tipe_usaha,
                                    "Link": link
                                })

                                baris_diproses += 1
                                if baris_diproses % 5 == 0 or baris_diproses == total_semua_baris:
                                    pct = min(baris_diproses / total_semua_baris, 1.0)
                                    progress_bar.progress(pct)
                                    status_text.markdown(f"**⏳ Mengekstrak:** {baris_diproses} / {total_semua_baris} baris ({int(pct*100)}%)")

                        status_text.empty()
                        progress_bar.empty()

                        st.session_state.data_fb = pd.DataFrame(hasil)
                        st.session_state.audit_fb = {
                            "total": total_baris,
                            "valid": len(hasil),
                            "file_count": len(files_fb),
                            "error_harga": err_h,
                            "luar": luar_wilayah
                        }
                        st.success(f"✅ Berhasil! {len(hasil)} data UMKM Facebook siap dianalisis.")
                    except Exception as e:
                        st.error(f"Error Sistem: {e}")

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

        df_f = df_fb[
            df_fb["Wilayah"].isin(f_wil) &
            df_fb["Tipe Usaha"].isin(f_tipe) &
            (df_fb["Harga"] >= f_hrg[0]) &
            (df_fb["Harga"] <= f_hrg[1])
        ]

        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database (Ringkas + Detail)", "📑 Log Audit"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("📌 Total Data Ditampilkan", f"{len(df_f):,}".replace(",", "."))
            c2.metric("🏠 Usaha Murni Online", f"{len(df_f[df_f['Tipe Usaha'] == 'Murni Online (Rumahan)']):,}".replace(",", "."))
            c3.metric("🗺️ Sebaran Wilayah", f"{df_f['Wilayah'].nunique()}")

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("### ✅ Tabel Ringkas (1 Toko = 1 Baris)")
            df_ringkas = buat_ringkasan_toko(df_f).copy()
            if df_ringkas is None or df_ringkas.empty:
                st.warning("Tidak ada data setelah filter.")
            else:
                df_ringkas["Harga Min"] = df_ringkas["Harga Min"].apply(rp)
                df_ringkas["Harga Max"] = df_ringkas["Harga Max"].apply(rp)
                st.dataframe(df_ringkas, use_container_width=True, hide_index=True, height=300)

                st.markdown("### 🔍 Detail Produk per Toko")
                toko_opsi = df_ringkas["Nama Toko"].dropna().unique().tolist()
                toko_pilih = st.selectbox("Pilih toko:", options=toko_opsi, key="detail_toko_fb")

                df_detail = df_f[df_f["Nama Toko"] == toko_pilih].copy()
                df_detail = df_detail.sort_values(["Nama Produk"], na_position="last")
                df_detail_view = df_detail.copy()
                df_detail_view["Harga"] = df_detail_view["Harga"].apply(rp)

                st.dataframe(
                    df_detail_view[["Nama Produk", "Harga", "Wilayah", "Tipe Usaha", "Link"]],
                    use_container_width=True,
                    hide_index=True,
                    height=350
                )

                st.markdown("### ⬇️ Export Excel")
                mode_export = st.radio(
                    "Pilih mode export:",
                    ["Ringkas per Toko (sheet ringkas)", "Detail Semua Produk (sheet detail)"],
                    horizontal=True,
                    key="export_mode_fb"
                )

                if mode_export.startswith("Ringkas"):
                    excel_export(df_ringkas, None, f"UMKM_Facebook_RINGKAS_{datetime.date.today()}.xlsx")
                else:
                    excel_export(None, df_detail, f"UMKM_Facebook_DETAIL_{datetime.date.today()}.xlsx")

        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            audit = st.session_state.audit_fb
            st.info(f"**📂 Dokumen Diproses:** {audit.get('file_count', 0)} File CSV")
            st.success(f"**📥 Data Baris Terekstrak Bersih:** {audit.get('valid', 0)} Baris")
            st.warning(f"**⚠️ Data Diabaikan (Luar Wilayah):** {audit.get('luar', 0)} Baris")

# ==============================================================================
#                             HALAMAN EXPORT GABUNGAN
# ==============================================================================
elif halaman == "📊 Export Gabungan":
    st.markdown("""
    <div class="banner-bps">
        <div class="banner-sub-title">🏛️ BADAN PUSAT STATISTIK</div>
        <h1>Export Master Data Gabungan</h1>
        <p>Konsolidasi Master Data (Shopee, Tokopedia, Facebook) - Ringkas + Detail</p>
    </div>
    """, unsafe_allow_html=True)

    df_shp_ready = st.session_state.data_shopee is not None and not st.session_state.data_shopee.empty
    df_tkp_ready = st.session_state.data_tokped is not None and not st.session_state.data_tokped.empty
    df_fb_ready = st.session_state.data_fb is not None and not st.session_state.data_fb.empty

    if not df_shp_ready and not df_tkp_ready and not df_fb_ready:
        st.warning("⚠️ Belum ada data yang diekstrak. Silakan unggah dan proses dokumen di menu Shopee, Tokopedia, atau Facebook.")
    else:
        mode_master = st.radio(
            "Mode Export Master:",
            ["Ringkas per Toko", "Detail Semua Produk"],
            horizontal=True,
            key="mode_master"
        )

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            wb = writer.book
            header_fmt = wb.add_format({'bold': True, 'bg_color': BPS_OREN_UTAMA, 'font_color': 'white'})
            currency_fmt = wb.add_format({'num_format': '#,##0'})

            def write_sheet(name, df):
                df.to_excel(writer, index=False, sheet_name=name)
                ws = writer.sheets[name]
                for col_num, value in enumerate(df.columns.values):
                    ws.write(0, col_num, value, header_fmt)
                if "Harga" in df.columns:
                    hidx = list(df.columns).index("Harga")
                    ws.set_column(hidx, hidx, 14, currency_fmt)
                ws.set_column(0, len(df.columns) - 1, 22)
                ws.autofilter(0, 0, len(df), len(df.columns) - 1)

            if df_shp_ready:
                df = st.session_state.data_shopee.copy()
                if mode_master == "Ringkas per Toko":
                    df = buat_ringkasan_toko(df)
                write_sheet("Shopee", df)

            if df_tkp_ready:
                df = st.session_state.data_tokped.copy()
                if mode_master == "Ringkas per Toko":
                    df = buat_ringkasan_toko(df)
                write_sheet("Tokopedia", df)

            if df_fb_ready:
                df = st.session_state.data_fb.copy()
                if mode_master == "Ringkas per Toko":
                    df = buat_ringkasan_toko(df)
                write_sheet("Facebook", df)

        st.download_button(
            "⬇️ UNDUH EXCEL MASTER",
            data=buf.getvalue(),
            file_name=f"Master_UMKM_{mode_master.replace(' ', '_')}_{datetime.date.today()}.xlsx",
            type="primary",
            use_container_width=True
        )
