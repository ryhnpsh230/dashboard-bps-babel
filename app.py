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
    page_title="Dashboard Ekstraksi Data BPS",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS CUSTOM (TEMA PROFESIONAL KANTOR & OREN BPS) ---
st.markdown("""
    <style>
    /* Mengatur jarak aman atas dan bawah */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* Desain Banner Platform */
    .banner-shopee { background: linear-gradient(135deg, #022a5e 0%, #0056b3 100%); padding: 25px 35px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: white; border-left: 6px solid #f97316;}
    .banner-shopee h1 { color: white !important; font-weight: 700; margin-bottom: 5px; font-size: 2.2rem; }
    .banner-shopee p { color: #dbeafe !important; font-size: 1.05rem; margin: 0; opacity: 0.9;}
    
    .banner-tokped { background: linear-gradient(135deg, #064e3b 0%, #059669 100%); padding: 25px 35px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: white; border-left: 6px solid #34d399;}
    .banner-tokped h1 { color: white !important; font-weight: 700; margin-bottom: 5px; font-size: 2.2rem; }
    .banner-tokped p { color: #d1fae5 !important; font-size: 1.05rem; margin: 0; opacity: 0.9;}

    .banner-fb { background: linear-gradient(135deg, #1877f2 0%, #0866ff 100%); padding: 25px 35px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: white; border-left: 6px solid #60a5fa;}
    .banner-fb h1 { color: white !important; font-weight: 700; margin-bottom: 5px; font-size: 2.2rem; }
    .banner-fb p { color: #e7f3ff !important; font-size: 1.05rem; margin: 0; opacity: 0.9;}
    
    /* BANNER GOOGLE MAPS & MASTER GABUNGAN (TEMA OREN BPS) */
    .banner-maps, .banner-gabungan { background: linear-gradient(135deg, #ea580c 0%, #f97316 100%); padding: 25px 35px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(234,88,12,0.2); color: white; border-left: 6px solid #ffedd5;}
    .banner-maps h1, .banner-gabungan h1 { color: white !important; font-weight: 700; margin-bottom: 5px; font-size: 2.2rem; }
    .banner-maps p, .banner-gabungan p { color: #ffedd5 !important; font-size: 1.05rem; margin: 0; opacity: 0.9;}
    
    /* Mempercantik Card Metrik */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #ffedd5;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(234,88,12,0.05);
        transition: transform 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(234,88,12,0.15);
        border-color: #fdba74;
    }
    
    @media (prefers-color-scheme: dark) {
        div[data-testid="metric-container"] { background-color: #1e293b; border: 1px solid #334155; }
        div[data-testid="metric-container"]:hover { border-color: #ea580c; }
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 5px 5px 0 0; padding: 0 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "data_shopee" not in st.session_state: st.session_state.data_shopee = None
if "audit_shopee" not in st.session_state: st.session_state.audit_shopee = {}

if "data_tokped" not in st.session_state: st.session_state.data_tokped = None
if "audit_tokped" not in st.session_state: st.session_state.audit_tokped = {}

if "data_fb" not in st.session_state: st.session_state.data_fb = None
if "audit_fb" not in st.session_state: st.session_state.audit_fb = {}

if "data_maps" not in st.session_state: st.session_state.data_maps = None
if "audit_maps" not in st.session_state: st.session_state.audit_maps = {}

# --- 4. FUNGSI BANTUAN ---
def deteksi_tipe_usaha(nama_toko):
    if pd.isna(nama_toko) or nama_toko in ["Tidak Dilacak", "Toko CSV", "Anonim", ""]: return "Tidak Terdeteksi"
    if str(nama_toko) == "FB Seller": return "Perorangan (Facebook)"
    nama_lower = str(nama_toko).lower()
    keyword_fisik = ['toko', 'warung', 'grosir', 'mart', 'apotek', 'cv.', 'pt.', 'official', 'agen', 'distributor', 'kios', 'kedai', 'supermarket', 'minimarket', 'cabang', 'jaya', 'abadi', 'makmur', 'motor', 'mobil', 'bengkel', 'snack', 'store']
    for kata in keyword_fisik:
        if kata in nama_lower: return "Ada Toko Fisik"
    return "Murni Online (Rumahan)"

# Fungsi khusus Maps untuk mengekstrak nomor telepon dari deskripsi
def ekstrak_no_hp(teks):
    if pd.isna(teks): return "-"
    # Regex ini nyari pola angka yang panjangnya 9-14 digit, bisa diawali '0' atau '+62'
    pola = re.search(r'(\+62|0)\s*[-]*\d{2,4}\s*[-]*\d{3,4}\s*[-]*\d{3,4}', str(teks))
    if pola: return pola.group(0)
    return "-"

# --- 5. SIDEBAR MENU ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    st.markdown("### 🧭 Menu Navigasi")
    halaman = st.radio("Pilih Fitur:", ["🟠 Shopee", "🟢 Tokopedia", "🔵 Facebook FB", "📍 Google Maps", "📊 Export Gabungan (4-in-1)"])
    st.divider()

babel_keys = ["pangkal", "bangka", "belitung", "sungailiat", "mentok", "muntok", "koba", "toboali", "manggar", "tanjung pandan", "tanjungpandan"]


# ==============================================================================
#                             HALAMAN GOOGLE MAPS
# ==============================================================================
if halaman == "📍 Google Maps":
    st.markdown("""
    <div class="banner-maps">
        <div style="font-size: 0.85rem; font-weight: bold; letter-spacing: 1px; margin-bottom: 5px;">🏛️ BADAN PUSAT STATISTIK</div>
        <h1>Dashboard Usaha - Google Maps</h1>
        <p>Data Spasial, Koordinat, dan Kontak Usaha Fisik Wilayah Bangka Belitung</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Maps")
        files_maps = st.file_uploader("Unggah CSV Google Maps", type=["csv"], accept_multiple_files=True, key="file_maps")
        
        if st.button("🚀 Proses Data Maps", type="primary", use_container_width=True):
            if not files_maps:
                st.error("⚠️ Silakan unggah file CSV Google Maps hasil ekstensi terlebih dahulu.")
            else:
                with st.spinner("Sedang membaca dan membersihkan data Maps..."):
                    try:
                        total_semua_baris = 0
                        for f in files_maps:
                            df_temp = pd.read_csv(f, dtype=str, on_bad_lines="skip")
                            total_semua_baris += len(df_temp)
                            f.seek(0)
                            
                        hasil, total_baris, luar_wilayah = [], 0, 0
                        baris_diproses = 0
                        status_text = st.empty()
                        progress_bar = st.progress(0)
                        
                        for file in files_maps:
                            df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                            total_baris += len(df_raw)
                            
                            # Kolom CSV Maps dari Ekstensi: Nama Toko, Alamat, Titik Koordinat, Deskripsi, Foto, Link
                            for i in range(len(df_raw)):
                                row = df_raw.iloc[i]
                                nama = str(row.get("Nama Toko", "Tanpa Nama"))
                                alamat = str(row.get("Alamat", "-"))
                                koordinat = str(row.get("Titik Koordinat", "N/A"))
                                deskripsi = str(row.get("Deskripsi", "-"))
                                foto = str(row.get("Foto", "-"))
                                link = str(row.get("Link", "-"))
                                
                                # Filter wilayah Babel dari kolom alamat
                                # Catatan: Jika ingin memasukkan semua data walau tanpa kata bangka/belitung, hapus 3 baris di bawah ini
                                if not any(k in alamat.lower() for k in babel_keys) and alamat != "-" and "Cek di Link" not in alamat:
                                    luar_wilayah += 1
                                    baris_diproses += 1
                                    continue
                                
                                # Ekstrak No Telepon dari Deskripsi
                                no_telp = ekstrak_no_hp(deskripsi)
                                
                                # Pembersihan Deskripsi (Membuang sisa no telp atau tulisan Ulasan biar bersih)
                                deskripsi_bersih = re.sub(r'(\+62|0)\s*[-]*\d{2,4}\s*[-]*\d{3,4}\s*[-]*\d{3,4}', '', deskripsi)
                                deskripsi_bersih = re.sub(r'\d+\s*Ulasan', '', deskripsi_bersih).replace('·', '').strip()
                                
                                hasil.append({
                                    "Nama Toko/Usaha": nama, 
                                    "Kategori Bisnis": deskripsi_bersih if deskripsi_bersih else "Lainnya", 
                                    "Alamat Lengkap": alamat, 
                                    "Koordinat": koordinat,
                                    "No Telepon": no_telp,
                                    "Foto Lokasi": foto, 
                                    "Link Gmaps": link
                                })
                                
                                baris_diproses += 1
                                if baris_diproses % 5 == 0 or baris_diproses == total_semua_baris:
                                    pct = min(baris_diproses / total_semua_baris, 1.0)
                                    progress_bar.progress(pct)
                                    status_text.markdown(f"**⏳ Membersihkan Data:** {baris_diproses} / {total_semua_baris} baris ({int(pct*100)}%)")
                        
                        status_text.empty()
                        progress_bar.empty()
                        
                        df_final = pd.DataFrame(hasil).drop_duplicates()
                        st.session_state.data_maps = df_final
                        st.session_state.audit_maps = {"total": total_baris, "valid": len(df_final), "file_count": len(files_maps), "luar": luar_wilayah}
                        st.success(f"✅ Selesai! {len(df_final)} Data Usaha Fisik Google Maps berhasil dibersihkan.")
                    except Exception as e:
                        st.error(f"Error Sistem Maps: {e}")

    df_maps = st.session_state.data_maps
    if df_maps is not None and not df_maps.empty:
        with st.container(border=True):
            st.markdown("#### 🔎 Filter Data Pintar")
            col_f1, col_f2 = st.columns([1, 1])
            with col_f1: f_kat = st.multiselect("🏷️ Kategori Bisnis:", options=sorted(df_maps["Kategori Bisnis"].unique()), default=sorted(df_maps["Kategori Bisnis"].unique())[:5], key="f_kat_maps")
            with col_f2: 
                punya_telp = st.checkbox("📞 Tampilkan hanya yang memiliki No Telepon")

            df_f = df_maps[df_maps["Kategori Bisnis"].isin(f_kat)]
            if punya_telp: df_f = df_f[df_f["No Telepon"] != "-"]
            
            tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Audit"])
            with tab1:
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                c1.metric("📌 Total Usaha Terdata", f"{len(df_f):,}".replace(",", "."))
                c2.metric("📍 Memiliki Titik Koordinat", f"{len(df_f[df_f['Koordinat'] != 'N/A']):,}".replace(",", "."))
                c3.metric("📞 Memiliki Kontak", f"{len(df_f[df_f['No Telepon'] != '-']):,}".replace(",", "."))
                
                st.markdown("<br>", unsafe_allow_html=True)
                if not df_f.empty:
                    top_kategori = df_f.groupby("Kategori Bisnis").size().reset_index(name='Jumlah').sort_values('Jumlah', ascending=False).head(10)
                    st.plotly_chart(px.bar(top_kategori, x="Kategori Bisnis", y="Jumlah", title="Top 10 Kategori Usaha Terbanyak", color="Kategori Bisnis", color_discrete_sequence=px.colors.sequential.Oranges_r), use_container_width=True)
            with tab2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df_f, use_container_width=True, hide_index=True, height=400)
                
                if not df_f.empty:
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                        df_f.to_excel(writer, index=False, sheet_name="Data Maps")
                        wb, ws = writer.book, writer.sheets["Data Maps"]
                        for col_num, value in enumerate(df_f.columns.values): ws.write(0, col_num, value, wb.add_format({'bold': True, 'bg_color': '#ea580c', 'font_color': 'white'}))
                        ws.set_column('A:A', 35); ws.set_column('B:B', 20); ws.set_column('C:C', 45); ws.set_column('D:D', 25); ws.set_column('E:E', 18); ws.set_column('F:G', 40)
                    st.markdown('<style>div[data-testid="stDownloadButton"] button {background-color: #f97316; color: white; border:none;}</style>', unsafe_allow_html=True)
                    st.download_button("⬇️ Unduh Excel Database Maps", data=buf.getvalue(), file_name=f"UMKM_Maps_{datetime.date.today()}.xlsx")
            with tab3:
                st.markdown("<br>", unsafe_allow_html=True)
                audit = st.session_state.audit_maps
                st.info(f"**📂 Dokumen Diproses:** {audit.get('file_count',0)} File CSV")
                st.success(f"**📥 Data Baris Dibersihkan:** {audit.get('valid',0)} Baris")
                st.warning(f"**⚠️ Data Luar Wilayah:** {audit.get('luar',0)} Baris")

# ==============================================================================
#                             HALAMAN SHOPEE
# ==============================================================================
elif halaman == "🟠 Shopee":
    st.markdown("""
    <div class="banner-shopee">
        <div style="font-size: 0.85rem; font-weight: bold; letter-spacing: 1px; color: #cbd5e1; margin-bottom: 5px;">🏛️ BADAN PUSAT STATISTIK</div>
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
                                col_link, col_nama, col_harga, col_wilayah = "Link", "Nama Produk", "Harga", "Wilayah"
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
                        st.success(f"✅ Berhasil! {len(hasil)} data UMKM Shopee siap dianalisis.")
                    except Exception as e:
                        st.error(f"Error Sistem: {e}")

    df_shp = st.session_state.data_shopee
    if df_shp is not None and not df_shp.empty:
        with st.container(border=True):
            st.markdown("#### 🔎 Filter Data Pintar")
            col_f1, col_f2, col_f3 = st.columns([1, 1, 1.5])
            with col_f1: f_wil = st.multiselect("📍 Wilayah:", options=sorted(df_shp["Wilayah"].unique()), default=sorted(df_shp["Wilayah"].unique()), key="f_wil_shp")
            with col_f2: f_tipe = st.multiselect("🏢 Tipe Usaha:", options=sorted(df_shp["Tipe Usaha"].unique()), default=sorted(df_shp["Tipe Usaha"].unique()), key="f_tipe_shp")
            with col_f3: 
                max_h = int(df_shp["Harga"].max()) if df_shp["Harga"].max() > 0 else 1000000
                f_hrg = st.slider("💰 Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_shp")

        df_f = df_shp[df_shp["Wilayah"].isin(f_wil) & df_shp["Tipe Usaha"].isin(f_tipe) & (df_shp["Harga"] >= f_hrg[0]) & (df_shp["Harga"] <= f_hrg[1])]
        
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
                    st.plotly_chart(px.pie(df_f, names="Tipe Usaha", title="Komposisi Model Bisnis UMKM", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
                with g2: 
                    st.plotly_chart(px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Total Usaha Berdasarkan Wilayah", color="Wilayah", color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=400)
            
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_f.to_excel(writer, index=False, sheet_name="Data Shopee")
                    wb, ws = writer.book, writer.sheets["Data Shopee"]
                    for col_num, value in enumerate(df_f.columns.values): ws.write(0, col_num, value, wb.add_format({'bold': True, 'bg_color': '#022a5e', 'font_color': 'white'}))
                    ws.set_column('A:A', 25); ws.set_column('B:B', 50); ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'})); ws.set_column('D:D', 20); ws.set_column('E:E', 25); ws.set_column('F:F', 50)
                st.download_button("⬇️ Unduh Excel Database Shopee", data=buf.getvalue(), file_name=f"UMKM_Shopee_{datetime.date.today()}.xlsx", type="primary")
        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            audit = st.session_state.audit_shopee
            st.info(f"**📂 Dokumen Diproses:** {audit.get('file_count',0)} File CSV")
            st.success(f"**📥 Data Baris Terekstrak Bersih:** {audit.get('valid',0)} Baris")
            st.warning(f"**⚠️ Data Diabaikan (Luar Wilayah):** {audit.get('luar',0)} Baris")

# ==============================================================================
#                             HALAMAN TOKOPEDIA
# ==============================================================================
elif halaman == "🟢 Tokopedia":
    st.markdown("""
    <div class="banner-tokped">
        <div style="font-size: 0.85rem; font-weight: bold; letter-spacing: 1px; color: #a7f3d0; margin-bottom: 5px;">🏛️ BADAN PUSAT STATISTIK</div>
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
                        st.success(f"✅ Berhasil! {len(df_final)} data UMKM Tokopedia diekstrak.")
                    except Exception as e:
                        st.error(f"Error Sistem Tokopedia: {e}")

    df_tkp = st.session_state.data_tokped
    if df_tkp is not None and not df_tkp.empty:
        with st.container(border=True):
            st.markdown("#### 🔎 Filter Data Pintar")
            col_f1, col_f2, col_f3 = st.columns([1, 1, 1.5])
            with col_f1: f_wil = st.multiselect("📍 Wilayah:", options=sorted(df_tkp["Wilayah"].unique()), default=sorted(df_tkp["Wilayah"].unique()), key="f_wil_tkp")
            with col_f2: f_tipe = st.multiselect("🏢 Tipe Usaha:", options=sorted(df_tkp["Tipe Usaha"].unique()), default=sorted(df_tkp["Tipe Usaha"].unique()), key="f_tipe_tkp")
            with col_f3: 
                max_h = int(df_tkp["Harga"].max()) if df_tkp["Harga"].max() > 0 else 1000000
                f_hrg = st.slider("💰 Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_tkp")

        df_f = df_tkp[df_tkp["Wilayah"].isin(f_wil) & df_tkp["Tipe Usaha"].isin(f_tipe) & (df_tkp["Harga"] >= f_hrg[0]) & (df_tkp["Harga"] <= f_hrg[1])]
        
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
                    st.plotly_chart(px.pie(df_f, names="Tipe Usaha", title="Komposisi Model Bisnis UMKM", hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
                with g2: 
                    st.plotly_chart(px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Total Usaha Berdasarkan Wilayah", color="Wilayah", color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=400)
            
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_f.to_excel(writer, index=False, sheet_name="Data Tokopedia")
                    wb, ws = writer.book, writer.sheets["Data Tokopedia"]
                    for col_num, value in enumerate(df_f.columns.values): ws.write(0, col_num, value, wb.add_format({'bold': True, 'bg_color': '#064e3b', 'font_color': 'white'}))
                    ws.set_column('A:A', 25); ws.set_column('B:B', 50); ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'})); ws.set_column('D:D', 20); ws.set_column('E:E', 25); ws.set_column('F:F', 50)
                st.markdown('<style>div[data-testid="stDownloadButton"] button {background-color: #059669; color: white; border:none;}</style>', unsafe_allow_html=True)
                st.download_button("⬇️ Unduh Excel Database Tokopedia", data=buf.getvalue(), file_name=f"UMKM_Tokopedia_{datetime.date.today()}.xlsx")
        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            audit = st.session_state.audit_tokped
            st.info(f"**📂 Dokumen Diproses:** {audit.get('file_count',0)} File CSV")
            st.success(f"**📥 Data Baris Terekstrak Bersih:** {audit.get('valid',0)} Baris")
            st.warning(f"**⚠️ Data Diabaikan (Luar Wilayah):** {audit.get('luar',0)} Baris")

# ==============================================================================
#                             HALAMAN FACEBOOK MARKETPLACE
# ==============================================================================
elif halaman == "🔵 Facebook FB":
    st.markdown("""
    <div class="banner-fb">
        <div style="font-size: 0.85rem; font-weight: bold; letter-spacing: 1px; color: #dbeafe; margin-bottom: 5px;">🏛️ BADAN PUSAT STATISTIK</div>
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
                        st.success(f"✅ Berhasil! {len(df_final)} data UMKM Facebook FB diekstrak.")
                    except Exception as e:
                        st.error(f"Error Sistem FB: {e}")

    df_fb = st.session_state.data_fb
    if df_fb is not None and not df_fb.empty:
        with st.container(border=True):
            st.markdown("#### 🔎 Filter Data Pintar")
            col_f1, col_f2, col_f3 = st.columns([1, 1, 1.5])
            with col_f1: f_wil = st.multiselect("📍 Wilayah:", options=sorted(df_fb["Wilayah"].unique()), default=sorted(df_fb["Wilayah"].unique()), key="f_wil_fb")
            with col_f2: f_tipe = st.multiselect("🏢 Tipe Usaha:", options=sorted(df_fb["Tipe Usaha"].unique()), default=sorted(df_fb["Tipe Usaha"].unique()), key="f_tipe_fb")
            with col_f3: 
                max_h = int(df_fb["Harga"].max()) if df_fb["Harga"].max() > 0 else 1000000
                f_hrg = st.slider("💰 Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_fb")

        df_f = df_fb[df_fb["Wilayah"].isin(f_wil) & df_fb["Tipe Usaha"].isin(f_tipe) & (df_fb["Harga"] >= f_hrg[0]) & (df_fb["Harga"] <= f_hrg[1])]
        
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
                    st.plotly_chart(px.pie(df_f, names="Tipe Usaha", title="Komposisi Model Bisnis FB", hole=0.4, color_discrete_sequence=px.colors.sequential.PuBu_r), use_container_width=True)
                with g2: 
                    st.plotly_chart(px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Total Usaha Berdasarkan Wilayah FB", color="Wilayah", color_discrete_sequence=px.colors.sequential.PuBu_r), use_container_width=True)
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=400)
            
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_f.to_excel(writer, index=False, sheet_name="Data FB")
                    wb, ws = writer.book, writer.sheets["Data FB"]
                    for col_num, value in enumerate(df_f.columns.values): ws.write(0, col_num, value, wb.add_format({'bold': True, 'bg_color': '#1877f2', 'font_color': 'white'}))
                    ws.set_column('A:A', 25); ws.set_column('B:B', 50); ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'})); ws.set_column('D:D', 20); ws.set_column('E:E', 25); ws.set_column('F:F', 50)
                st.markdown('<style>div[data-testid="stDownloadButton"] button {background-color: #0866ff; color: white; border:none;}</style>', unsafe_allow_html=True)
                st.download_button("⬇️ Unduh Excel Database Facebook", data=buf.getvalue(), file_name=f"UMKM_Facebook_{datetime.date.today()}.xlsx")
        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            audit = st.session_state.audit_fb
            st.info(f"**📂 Dokumen Diproses:** {audit.get('file_count',0)} File CSV")
            st.success(f"**📥 Data Baris Terekstrak Bersih:** {audit.get('valid',0)} Baris")
            st.warning(f"**⚠️ Data Diabaikan (Luar Wilayah):** {audit.get('luar',0)} Baris")


# ==============================================================================
#                             HALAMAN EXPORT GABUNGAN (4-IN-1)
# ==============================================================================
elif halaman == "📊 Export Gabungan (4-in-1)":
    st.markdown("""
    <div class="banner-gabungan">
        <div style="font-size: 0.85rem; font-weight: bold; letter-spacing: 1px; margin-bottom: 5px;">🏛️ BADAN PUSAT STATISTIK</div>
        <h1>Export Master Data Gabungan</h1>
        <p>Konsolidasi Master Data (Shopee, Tokopedia, Facebook, Maps) - Siap Analisis</p>
    </div>
    """, unsafe_allow_html=True)
    
    df_shp_ready = st.session_state.data_shopee is not None and not st.session_state.data_shopee.empty
    df_tkp_ready = st.session_state.data_tokped is not None and not st.session_state.data_tokped.empty
    df_fb_ready = st.session_state.data_fb is not None and not st.session_state.data_fb.empty
    df_maps_ready = st.session_state.data_maps is not None and not st.session_state.data_maps.empty
    
    if not any([df_shp_ready, df_tkp_ready, df_fb_ready, df_maps_ready]):
        st.warning("⚠️ Belum ada data yang diproses. Silakan unggah dokumen di menu samping terlebih dahulu.")
    else:
        st.success("✅ Seluruh instansi data siap untuk dikonsolidasi menjadi satu file Master Excel!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        if df_shp_ready: c1.metric("📦 Shopee", f"{len(st.session_state.data_shopee):,}".replace(",", "."))
        if df_tkp_ready: c2.metric("📦 Tokopedia", f"{len(st.session_state.data_tokped):,}".replace(",", "."))
        if df_fb_ready: c3.metric("📦 Facebook", f"{len(st.session_state.data_fb):,}".replace(",", "."))
        if df_maps_ready: c4.metric("📍 Google Maps", f"{len(st.session_state.data_maps):,}".replace(",", "."))
            
        st.write("---")
        st.markdown("Dokumen di bawah ini akan diunduh dengan format **Tab Sheet Terpisah** sesuai platform, serta sudah dilengkapi **Auto-Filter** untuk memudahkan penyortiran di Excel.")
        st.markdown("<br>", unsafe_allow_html=True)
        
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
            
            if df_maps_ready:
                df_maps = st.session_state.data_maps
                df_maps.to_excel(writer, index=False, sheet_name="Data Maps")
                ws_maps = writer.sheets["Data Maps"]
                header_fmt_maps = wb.add_format({'bold': True, 'bg_color': '#ea580c', 'font_color': 'white'})
                for col_num, value in enumerate(df_maps.columns.values): ws_maps.write(0, col_num, value, header_fmt_maps)
                ws_maps.set_column('A:A', 35); ws_maps.set_column('B:B', 20); ws_maps.set_column('C:C', 45); ws_maps.set_column('D:D', 25); ws_maps.set_column('E:E', 18); ws_maps.set_column('F:G', 40)
                ws_maps.autofilter(0, 0, len(df_maps), len(df_maps.columns) - 1)
                
        st.markdown('<style>div[data-testid="stDownloadButton"] button {background-color: #ea580c; color: white; border:none; height: 3.5rem; font-size: 1.1rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(234,88,12,0.3); transition: all 0.3s ease;}</style>', unsafe_allow_html=True)
        st.markdown('<style>div[data-testid="stDownloadButton"] button:hover {background-color: #c2410c; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(234,88,12,0.4);}</style>', unsafe_allow_html=True)
        
        _, col_btn, _ = st.columns([1, 2, 1])
        with col_btn:
            st.download_button(
                label="⬇️ UNDUH EXCEL MASTER DATA (GABUNGAN)",
                data=buf.getvalue(),
                file_name=f"Master_Data_BPS_{datetime.date.today()}.xlsx",
                use_container_width=True
            )
