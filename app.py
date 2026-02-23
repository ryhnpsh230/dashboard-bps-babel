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
    page_title="BPS · Portal UMKM Babel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7fb !important; }
    
    .header-shopee {
        background: linear-gradient(135deg, #061e45 0%, #0d3b7a 60%, #1565c0 100%);
        padding: 30px 40px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(6,30,69,0.15); color: white !important;
    }
    .header-shopee h1 { color: white !important; font-weight: 800; margin-bottom: 5px; }
    
    .header-tokped {
        background: linear-gradient(135deg, #064e3b 0%, #047857 60%, #10b981 100%);
        padding: 30px 40px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(6,78,59,0.15); color: white !important;
    }
    .header-tokped h1 { color: white !important; font-weight: 800; margin-bottom: 5px; }
    
    div[data-testid="metric-container"] {
        background-color: #ffffff !important; border-left: 5px solid #1565c0 !important;
        padding: 20px !important; border-radius: 10px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1565c0 0%, #00b4d8 100%) !important;
        color: white !important; border-radius: 8px !important; font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "data_shopee" not in st.session_state: st.session_state.data_shopee = None
if "audit_shopee" not in st.session_state: st.session_state.audit_shopee = {}

if "data_tokped" not in st.session_state: st.session_state.data_tokped = None
if "audit_tokped" not in st.session_state: st.session_state.audit_tokped = {}

# --- 4. SIDEBAR MENU ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
        
    st.markdown("### 🧭 Menu Navigasi")
    halaman = st.radio("Pilih Platform E-Commerce:", ["🟠 Shopee", "🟢 Tokopedia"])
    st.divider()

# ==============================================================================
#                             HALAMAN SHOPEE
# ==============================================================================
if halaman == "🟠 Shopee":
    st.markdown("""
    <div class="header-shopee">
        <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">🏛️ BADAN PUSAT STATISTIK</span>
        <h1>Portal Integrasi Data E-Commerce - Shopee</h1>
        <p>Sistem ekstraksi, pembersihan, dan penggabungan multi-file otomatis</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Shopee")
        files_shopee = st.file_uploader("Unggah CSV Shopee", type=["csv"], accept_multiple_files=True, key="file_shp")
        mode_api_shp = st.checkbox("🔍 Deteksi Nama Toko via API", key="api_shp")
        
        if st.button("🚀 Mulai Pemrosesan Shopee", use_container_width=True):
            if not files_shopee:
                st.error("⚠️ Unggah file CSV Shopee terlebih dahulu!")
            else:
                with st.spinner("Menjalankan algoritma standarisasi BPS..."):
                    try:
                        hasil, total_baris, err_h = [], 0, 0
                        bar = st.progress(0)
                        
                        for idx, file in enumerate(files_shopee):
                            df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                            total_baris += len(df_raw)
                            
                            col_link = next((c for c in df_raw.columns if 'href' in c.lower()), df_raw.columns[0])
                            col_nama = next((c for c in df_raw.columns if 'whitespace-normal' in c.lower()), df_raw.columns[3])
                            col_harga = next((c for c in df_raw.columns if 'font-medium 2' in c.lower()), df_raw.columns[4])
                            col_wilayah = next((c for c in df_raw.columns if 'ml-[3px]' in c.lower()), df_raw.columns[7])

                            for i in range(len(df_raw)):
                                row = df_raw.iloc[i]
                                link = str(row[col_link])
                                nama = str(row[col_nama])
                                harga_str = str(row[col_harga])
                                lokasi_shopee = str(row[col_wilayah]).title()
                                
                                try: val_h = int(re.sub(r"[^\d]", "", harga_str))
                                except: val_h, err_h = 0, err_h + 1
                                
                                toko = "Tidak Dilacak"
                                if mode_api_shp:
                                    match = re.search(r"i\.(\d+)\.", link)
                                    if match:
                                        try:
                                            res = requests.get(f"https://shopee.co.id/api/v4/shop/get_shop_base?shopid={match.group(1)}", headers={"User-Agent":"Mozilla/5.0"}, timeout=2)
                                            if res.status_code == 200: toko = res.json().get("data",{}).get("name", "Anonim")
                                        except: pass

                                hasil.append({"Nama Toko": toko, "Nama Produk": nama, "Harga": val_h, "Wilayah": lokasi_shopee, "Link": link})
                            bar.progress((idx + 1) / len(files_shopee))
                        
                        bar.empty()
                        st.session_state.data_shopee = pd.DataFrame(hasil)
                        st.session_state.audit_shopee = {"total": total_baris, "valid": len(hasil), "file_count": len(files_shopee), "error_harga": err_h}
                        st.success(f"✅ Selesai! {len(hasil):,} data Shopee tervalidasi.".replace(",", "."))
                    except Exception as e:
                        st.error(f"❌ Terjadi kesalahan! Detail: {e}")

    df_shp = st.session_state.data_shopee
    if df_shp is not None and not df_shp.empty:
        st.markdown("### 🔎 Filter Data Shopee")
        col_f1, col_f2 = st.columns(2)
        with col_f1: f_wil = st.multiselect("Pilih Wilayah:", options=sorted(df_shp["Wilayah"].unique()), default=sorted(df_shp["Wilayah"].unique()), key="f_wil_shp")
        with col_f2: 
            max_h = int(df_shp["Harga"].max()) if df_shp["Harga"].max() > 0 else 1000000
            f_hrg = st.slider("Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_shp")

        df_f = df_shp[df_shp["Wilayah"].isin(f_wil) & (df_shp["Harga"] >= f_hrg[0]) & (df_shp["Harga"] <= f_hrg[1])]
        
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🗄️ Database & Export Excel", "📑 Audit Data"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("🏪 Total UMKM", f"{len(df_f):,}".replace(",", "."))
            k2.metric("💰 Rata-rata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",", ".") if not df_f.empty else "Rp 0")
            k3.metric("📈 Harga Tertinggi", f"Rp {df_f['Harga'].max():,.0f}".replace(",", ".") if not df_f.empty else "Rp 0")
            k4.metric("🗺️ Cakupan Wilayah", f"{df_f['Wilayah'].nunique()} Lokasi")
            
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.pie(df_f, names="Wilayah", title="Distribusi UMKM per Lokasi", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
                with g2: st.plotly_chart(px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Total Usaha per Wilayah", color="Wilayah", color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
        
        with tab2:
            st.markdown("#### 📋 Tabel Data Tervalidasi")
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=350)
            
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer: df_f.to_excel(writer, index=False, sheet_name="Data Shopee")
                st.download_button("⬇️ Download Excel Shopee", data=buf.getvalue(), file_name=f"Laporan_BPS_Shopee.xlsx")
        
        with tab3:
            audit = st.session_state.audit_shopee
            st.success(f"File Diproses: {audit.get('file_count')} | Data Mentah: {audit.get('total')} | Valid: {audit.get('valid')}")

# ==============================================================================
#                             HALAMAN TOKOPEDIA
# ==============================================================================
elif halaman == "🟢 Tokopedia":
    st.markdown("""
    <style>
    .stTabs [aria-selected="true"] { color: #059669 !important; border-bottom-color: #059669 !important; }
    div[data-testid="metric-container"] { border-left-color: #059669 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="header-tokped">
        <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">🏛️ BADAN PUSAT STATISTIK</span>
        <h1>Portal Integrasi Data E-Commerce - Tokopedia</h1>
        <p>Sistem Deep Scanner dengan perbaikan filter Lokasi vs Judul</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Tokopedia")
        files_tokped = st.file_uploader("Unggah CSV Tokopedia", type=["csv"], accept_multiple_files=True, key="file_tkp")
        
        st.markdown('<style>div[data-testid="stButton"] button {background: linear-gradient(135deg, #064e3b 0%, #10b981 100%) !important;}</style>', unsafe_allow_html=True)
        if st.button("🚀 Mulai Pemrosesan Tokopedia", use_container_width=True):
            if not files_tokped:
                st.error("⚠️ Unggah file CSV Tokopedia terlebih dahulu!")
            else:
                with st.spinner("Memisahkan Babi Panggang dari Nama Kota..."):
                    try:
                        hasil, total_baris, err_h = [], 0, 0
                        bar = st.progress(0)
                        
                        for idx, file in enumerate(files_tokped):
                            df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                            total_baris += len(df_raw)
                            
                            for _, row in df_raw.iterrows():
                                links, names, prices, locs, shops = [], [], [], [], []
                                
                                for col in df_raw.columns:
                                    val = str(row[col]).strip()
                                    if val == 'nan' or val == '': continue
                                    
                                    # LOGIKA BARU: MEMBEDAKAN LOKASI DAN NAMA PRODUK DARI PANJANG TEKS
                                    val_lower = val.lower()
                                    
                                    # Deteksi Link
                                    if 'tokopedia.com/' in val_lower and 'extparam' in val_lower: links.append(val)
                                    # Deteksi Harga
                                    elif 'rp' in val_lower and any(c.isdigit() for c in val): prices.append(val)
                                    # Deteksi Nama Toko (Tidak mengandung spasi banyak atau nama pendek)
                                    elif len(val) <= 20 and 'terjual' not in val_lower and 'rp' not in val_lower and 'http' not in val_lower:
                                        # Kemungkinan Nama Toko atau Lokasi
                                        if any(k in val_lower for k in ['pangkal', 'bangka', 'belitung', 'jakarta', 'bogor', 'mojokerto', 'tangerang', 'bandung', 'bekasi', 'medan', 'surabaya', 'semarang', 'palembang']):
                                            locs.append(val)
                                        else:
                                            if not any(c.isdigit() for c in val): shops.append(val)
                                    # Deteksi Nama Produk (Pasti teksnya panjang > 20 huruf)
                                    elif len(val) > 20 and 'http' not in val_lower:
                                        names.append(val)

                                # Menyatukan (Unrolling) baris menyamping
                                for k in range(len(links)):
                                    try:
                                        h_raw = prices[k] if k < len(prices) else "0"
                                        h_fix = int(re.sub(r"[^\d]", "", h_raw))
                                        if h_fix == 0: continue
                                        
                                        hasil.append({
                                            "Nama Toko": shops[k] if k < len(shops) else "Toko Tokopedia",
                                            "Nama Produk": names[k] if k < len(names) else "Produk Tokopedia",
                                            "Harga": h_fix,
                                            "Wilayah": locs[k].title() if k < len(locs) else "Tidak Terdeteksi",
                                            "Link": links[k]
                                        })
                                    except: continue
                            bar.progress((idx + 1) / len(files_tokped))
                        
                        bar.empty()
                        df_final = pd.DataFrame(hasil).drop_duplicates()
                        st.session_state.data_tokped = df_final
                        st.session_state.audit_tokped = {"total": total_baris, "valid": len(df_final), "file_count": len(files_tokped), "error_harga": err_h}
                        st.success(f"✅ Berhasil memisahkan data! {len(df_final):,} produk ditarik.")
                    except Exception as e:
                        st.error(f"❌ Terjadi kesalahan Tokopedia! Detail: {e}")

    df_tkp = st.session_state.data_tokped
    if df_tkp is not None and not df_tkp.empty:
        st.markdown("### 🔎 Filter Data Tokopedia")
        col_f1, col_f2 = st.columns(2)
        with col_f1: f_wil = st.multiselect("Pilih Wilayah:", options=sorted(df_tkp["Wilayah"].unique()), default=sorted(df_tkp["Wilayah"].unique()), key="f_wil_tkp")
        with col_f2: 
            max_h = int(df_tkp["Harga"].max()) if df_tkp["Harga"].max() > 0 else 1000000
            f_hrg = st.slider("Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_tkp")

        df_f = df_tkp[df_tkp["Wilayah"].isin(f_wil) & (df_tkp["Harga"] >= f_hrg[0]) & (df_tkp["Harga"] <= f_hrg[1])]
        
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Audit Scan"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("🛒 Total Produk", f"{len(df_f):,}".replace(",", "."))
            k2.metric("💰 Rata-rata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",", ".") if not df_f.empty else "Rp 0")
            k3.metric("📈 Harga Tertinggi", f"Rp {df_f['Harga'].max():,.0f}".replace(",", ".") if not df_f.empty else "Rp 0")
            k4.metric("🗺️ Cakupan Wilayah", f"{df_f['Wilayah'].nunique()} Lokasi")
            
            if not df_f.empty:
                st.markdown("<hr style='border:1px solid #e2e8f0;'>", unsafe_allow_html=True)
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.pie(df_f, names="Wilayah", title="Distribusi Produk per Lokasi", hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
                with g2: st.plotly_chart(px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Total Produk per Wilayah", color="Wilayah", color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
        
        with tab2:
            st.markdown("#### 📋 Tabel Database (Babi Panggang di Kolom yang Benar!)")
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=350)
            
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer: df_f.to_excel(writer, index=False, sheet_name="Data Tokopedia")
                st.markdown('<style>div[data-testid="stDownloadButton"] button {background: linear-gradient(135deg, #064e3b 0%, #10b981 100%) !important;}</style>', unsafe_allow_html=True)
                st.download_button("⬇️ Download Excel Resmi (.xlsx)", data=buf.getvalue(), file_name=f"Laporan_BPS_Tokopedia.xlsx")
        
        with tab3:
            audit = st.session_state.audit_tokped
            st.success(f"File Diproses: {audit.get('file_count')} | Baris Diekstrak: {audit.get('valid')}")
