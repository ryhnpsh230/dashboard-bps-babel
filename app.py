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
    /* Kunci warna dasar aplikasi agar mengabaikan Dark Mode bawaan laptop */
    .stApp {
        background-color: #f4f7fb !important;
    }
    
    /* Header Utama Shopee */
    .header-shopee {
        background: linear-gradient(135deg, #061e45 0%, #0d3b7a 60%, #1565c0 100%);
        padding: 30px 40px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(6,30,69,0.15);
        color: white !important;
    }
    .header-shopee h1 { color: white !important; font-weight: 800; margin-bottom: 5px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .header-shopee p { color: #e0f2fe !important; font-size: 1.1rem; margin: 0; }

    /* Header Utama Tokopedia */
    .header-tokped {
        background: linear-gradient(135deg, #064e3b 0%, #047857 60%, #10b981 100%);
        padding: 30px 40px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(6,78,59,0.15);
        color: white !important;
    }
    .header-tokped h1 { color: white !important; font-weight: 800; margin-bottom: 5px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .header-tokped p { color: #d1fae5 !important; font-size: 1.1rem; margin: 0; }
    
    /* Kartu Metrik (Angka-angka di Dashboard) */
    div[data-testid="metric-container"] {
        background-color: #ffffff !important;
        border-left: 5px solid #1565c0 !important;
        padding: 20px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stMetricLabel"] p { color: #475569 !important; font-weight: 700 !important; text-transform: uppercase; font-size: 0.85rem !important; }
    div[data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 800 !important; }

    /* Tombol Utama */
    .stButton > button {
        background: linear-gradient(135deg, #1565c0 0%, #00b4d8 100%) !important;
        color: white !important; border: none !important; border-radius: 8px !important;
        height: 3.2em !important; font-weight: bold !important;
        box-shadow: 0 4px 12px rgba(0,100,200,0.2) !important;
    }
    
    /* Tab Menu */
    .stTabs [data-baseweb="tab-list"] { background-color: #ffffff !important; border-radius: 10px 10px 0 0; padding: 5px 10px 0 10px; }
    .stTabs [data-baseweb="tab"] { color: #64748b !important; font-weight: 600 !important; }
    .stTabs [aria-selected="true"] { color: #1565c0 !important; border-bottom-color: #1565c0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE (Terpisah untuk Shopee & Tokopedia) ---
if "data_shopee" not in st.session_state: st.session_state.data_shopee = None
if "audit_shopee" not in st.session_state: st.session_state.audit_shopee = {}

if "data_tokped" not in st.session_state: st.session_state.data_tokped = None
if "audit_tokped" not in st.session_state: st.session_state.audit_tokped = {}

# --- 4. SIDEBAR MENU ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.info("💡 Taruh gambar 'logo.png' di folder aplikasi untuk menampilkan logo BPS.")
        
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
        mode_api_shp = st.checkbox("🔍 Deteksi Nama Toko via API", key="api_shp", help="Mengambil nama asli toko. Butuh internet lancar.")
        
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
                        st.success(f"✅ Selesai! {len(hasil):,} data tervalidasi.".replace(",", "."))
                    except Exception as e:
                        st.error(f"❌ Terjadi kesalahan! Detail: {e}")

    # TAMPILAN DASHBOARD SHOPEE
    df_shp = st.session_state.data_shopee
    if df_shp is None:
        st.markdown("""
        <div style="background: white; border: 2px dashed #cbd5e1; border-radius: 15px; padding: 60px 20px; text-align: center; margin-top: 20px;">
            <h1 style="font-size: 3rem; margin: 0;">📊</h1>
            <h3 style="color: #0f172a; font-family: sans-serif;">Workspace Kosong</h3>
            <p style="color: #64748b;">Silakan unggah file CSV Shopee di panel sebelah kiri untuk melihat keajaiban sistem ini.</p>
        </div>
        """, unsafe_allow_html=True)
    elif df_shp.empty:
        st.warning("⚠️ Data kosong. Pastikan file CSV memiliki format yang benar.")
    else:
        st.markdown("### 🔎 Filter Data")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            f_wil = st.multiselect("Pilih Wilayah (Bisa hapus yang tidak relevan):", options=sorted(df_shp["Wilayah"].unique()), default=sorted(df_shp["Wilayah"].unique()), key="f_wil_shp")
        with col_f2:
            max_h = int(df_shp["Harga"].max()) if df_shp["Harga"].max() > 0 else 1000000
            f_hrg = st.slider("Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_shp")

        df_f = df_shp[df_shp["Wilayah"].isin(f_wil) & (df_shp["Harga"] >= f_hrg[0]) & (df_shp["Harga"] <= f_hrg[1])]
        
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database & Export Excel", "📑 Audit Data"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            rata = df_f["Harga"].mean() if not df_f.empty else 0
            maks = df_f["Harga"].max()  if not df_f.empty else 0
            
            k1.metric("🏪 Total UMKM", f"{len(df_f):,}".replace(",", "."))
            k2.metric("💰 Rata-rata Harga", f"Rp {rata:,.0f}".replace(",", "."))
            k3.metric("📈 Harga Tertinggi", f"Rp {maks:,.0f}".replace(",", "."))
            k4.metric("🗺️ Cakupan Wilayah", f"{df_f['Wilayah'].nunique()} Lokasi")
            
            if not df_f.empty:
                st.markdown("<hr style='border:1px solid #e2e8f0;'>", unsafe_allow_html=True)
                g1, g2 = st.columns(2)
                with g1:
                    fig_d = px.pie(df_f, names="Wilayah", title="Distribusi UMKM per Lokasi", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
                    st.plotly_chart(fig_d, use_container_width=True)
                with g2:
                    fig_b = px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Total Usaha per Wilayah", color="Wilayah", color_discrete_sequence=px.colors.sequential.Blues_r)
                    st.plotly_chart(fig_b, use_container_width=True)
        
        with tab2:
            st.markdown("#### 📋 Tabel Data Tervalidasi")
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=350)
            
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_f.to_excel(writer, index=False, sheet_name="Data Shopee")
                    wb, ws = writer.book, writer.sheets["Data Shopee"]
                    header_fmt = wb.add_format({'bold': True, 'bg_color': '#061E45', 'font_color': 'white', 'border': 1, 'align': 'center'})
                    border_fmt = wb.add_format({'border': 1})
                    currency_fmt = wb.add_format({'border': 1, 'num_format': '#,##0'})
                    
                    for col_num, value in enumerate(df_f.columns.values):
                        ws.write(0, col_num, value, header_fmt)
                    
                    ws.set_column('A:A', 25, border_fmt)
                    ws.set_column('B:B', 50, border_fmt)
                    ws.set_column('C:C', 18, currency_fmt)
                    ws.set_column('D:D', 30, border_fmt)
                    ws.set_column('E:E', 50, border_fmt)
                    ws.autofilter(0, 0, len(df_f), len(df_f.columns) - 1)
                st.download_button("⬇️ Download Excel Resmi (.xlsx)", data=buf.getvalue(), file_name=f"Laporan_BPS_Shopee_{datetime.date.today()}.xlsx")
        
        with tab3:
            audit = st.session_state.audit_shopee
            total = int(audit.get('total', 0))
            valid = int(audit.get('valid', 0))
            f_count = int(audit.get('file_count', 0))
            err_h = int(audit.get('error_harga', 0))
            
            valid_pct = (valid / total * 100) if total > 0 else 0
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("Laporan ini menunjukkan hasil penggabungan (bulk upload) data dari berbagai file.")
            
            a1, a2, a3, a4 = st.columns(4)
            a1.metric("📂 File Diproses", f"{f_count:,}".replace(",", "."))
            a2.metric("📥 Total Data Mentah", f"{total:,}".replace(",", "."))
            a3.metric("⚠️ Perbaikan Harga", f"{err_h:,}".replace(",", "."))
            a4.metric("✅ Data Valid", f"{valid:,}".replace(",", "."))
            
            st.write("---")
            col_g1, col_g2 = st.columns([1, 1], gap="large")
            with col_g1:
                st.markdown("<h5 style='text-align: center; color: #475569;'>📈 Tingkat Ekstraksi Data</h5>", unsafe_allow_html=True)
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number", value = valid_pct, number = {'suffix': "%", 'valueformat': '.1f', 'font': {'size': 45, 'color': '#0f172a'}},
                    gauge = { 'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"}, 'bar': {'color': "#16a34a"}, 'bgcolor': "white", 'borderwidth': 2, 'bordercolor': "#e2e8f0",
                              'steps': [ {'range': [0, 50], 'color': '#fee2e2'}, {'range': [50, 80], 'color': '#fef08a'}, {'range': [80, 100], 'color': '#dcfce3'} ],
                              'threshold': { 'line': {'color': "#1565c0", 'width': 4}, 'thickness': 0.75, 'value': 80 } }
                ))
                fig_gauge.update_layout(height=280, margin=dict(t=30, b=10, l=30, r=30), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_gauge, use_container_width=True)
            with col_g2:
                st.markdown("<h5 style='color: #475569;'>📋 Informasi Sistem</h5>", unsafe_allow_html=True)
                st.write("") 
                st.success("Semua data ditarik murni berdasarkan lokasi asli Shopee. Anda dapat membersihkan kota di luar target secara manual menggunakan filter.")

# ==============================================================================
#                             HALAMAN TOKOPEDIA
# ==============================================================================
elif halaman == "🟢 Tokopedia":
    # Custom styling for Tokopedia elements to override default blue button locally
    st.markdown("""
    <style>
    /* Mengubah warna border aktif tab untuk halaman Tokopedia */
    .stTabs [aria-selected="true"] { color: #059669 !important; border-bottom-color: #059669 !important; }
    /* Mengubah metrik bar untuk halaman Tokopedia */
    div[data-testid="metric-container"] { border-left-color: #059669 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="header-tokped">
        <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">🏛️ BADAN PUSAT STATISTIK</span>
        <h1>Portal Integrasi Data E-Commerce - Tokopedia</h1>
        <p>Sistem pemindaian mendalam (Deep Scanner) untuk format data menyamping</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Tokopedia")
        files_tokped = st.file_uploader("Unggah CSV Tokopedia", type=["csv"], accept_multiple_files=True, key="file_tkp")
        
        # Override sidebar button color specifically for Tokopedia
        st.markdown('<style>div[data-testid="stButton"] button {background: linear-gradient(135deg, #064e3b 0%, #10b981 100%) !important;}</style>', unsafe_allow_html=True)
        if st.button("🚀 Mulai Pemrosesan Tokopedia", use_container_width=True):
            if not files_tokped:
                st.error("⚠️ Unggah file CSV Tokopedia terlebih dahulu!")
            else:
                with st.spinner("Menjalankan Deep Scanner Tokopedia..."):
                    try:
                        hasil, total_baris, err_h = [], 0, 0
                        bar = st.progress(0)
                        
                        for idx, file in enumerate(files_tokped):
                            df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                            total_baris += len(df_raw)
                            
                            for _, row in df_raw.iterrows():
                                links, names, prices, locs, shops = [], [], [], [], []
                                
                                for col in df_raw.columns:
                                    val = str(row[col])
                                    if val == 'nan' or val == '': continue
                                    
                                    # Deteksi Pola
                                    if 'tokopedia.com/' in val and 'extParam' in val: links.append(val)
                                    elif 'Rp' in val: prices.append(val)
                                    elif any(k in val for k in ['Pangkal', 'Bangka', 'Belitung', 'Jakarta', 'Bogor', 'Mojokerto', 'Tangerang', 'Bandung', 'Bekasi', 'Medan', 'Surabaya', 'Semarang', 'Palembang']):
                                        if 'terjual' not in val.lower() and 'http' not in val: locs.append(val)
                                    elif len(val) > 15 and ' ' in val and 'http' not in val and 'Rp' not in val: names.append(val)
                                    elif len(val) <= 15 and not any(char.isdigit() for char in val): shops.append(val)

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
                        st.success(f"✅ Selesai! {len(df_final):,} produk tervalidasi.".replace(",", "."))
                    except Exception as e:
                        st.error(f"❌ Terjadi kesalahan! Detail: {e}")

    # TAMPILAN DASHBOARD TOKOPEDIA
    df_tkp = st.session_state.data_tokped
    if df_tkp is None:
        st.markdown("""
        <div style="background: white; border: 2px dashed #cbd5e1; border-radius: 15px; padding: 60px 20px; text-align: center; margin-top: 20px;">
            <h1 style="font-size: 3rem; margin: 0;">📊</h1>
            <h3 style="color: #0f172a; font-family: sans-serif;">Workspace Kosong</h3>
            <p style="color: #64748b;">Silakan unggah file CSV Tokopedia di panel sebelah kiri untuk memulai Deep Scan.</p>
        </div>
        """, unsafe_allow_html=True)
    elif df_tkp.empty:
        st.warning("⚠️ Data kosong. Pastikan file CSV memiliki format yang benar.")
    else:
        st.markdown("### 🔎 Filter Data")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            f_wil = st.multiselect("Pilih Wilayah (Bisa hapus yang tidak relevan):", options=sorted(df_tkp["Wilayah"].unique()), default=sorted(df_tkp["Wilayah"].unique()), key="f_wil_tkp")
        with col_f2:
            max_h = int(df_tkp["Harga"].max()) if df_tkp["Harga"].max() > 0 else 1000000
            f_hrg = st.slider("Rentang Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_tkp")

        df_f = df_tkp[df_tkp["Wilayah"].isin(f_wil) & (df_tkp["Harga"] >= f_hrg[0]) & (df_tkp["Harga"] <= f_hrg[1])]
        
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database & Export Excel", "📑 Audit Deep Scan"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            rata = df_f["Harga"].mean() if not df_f.empty else 0
            maks = df_f["Harga"].max()  if not df_f.empty else 0
            
            k1.metric("🛒 Total Produk", f"{len(df_f):,}".replace(",", "."))
            k2.metric("💰 Rata-rata Harga", f"Rp {rata:,.0f}".replace(",", "."))
            k3.metric("📈 Harga Tertinggi", f"Rp {maks:,.0f}".replace(",", "."))
            k4.metric("🗺️ Cakupan Wilayah", f"{df_f['Wilayah'].nunique()} Lokasi")
            
            if not df_f.empty:
                st.markdown("<hr style='border:1px solid #e2e8f0;'>", unsafe_allow_html=True)
                g1, g2 = st.columns(2)
                with g1:
                    fig_d = px.pie(df_f, names="Wilayah", title="Distribusi Produk per Lokasi", hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
                    st.plotly_chart(fig_d, use_container_width=True)
                with g2:
                    fig_b = px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Total Produk per Wilayah", color="Wilayah", color_discrete_sequence=px.colors.sequential.Greens_r)
                    st.plotly_chart(fig_b, use_container_width=True)
        
        with tab2:
            st.markdown("#### 📋 Tabel Database (Unrolled)")
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=350)
            
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_f.to_excel(writer, index=False, sheet_name="Data Tokopedia")
                    wb, ws = writer.book, writer.sheets["Data Tokopedia"]
                    header_fmt = wb.add_format({'bold': True, 'bg_color': '#064e3b', 'font_color': 'white', 'border': 1, 'align': 'center'})
                    border_fmt = wb.add_format({'border': 1})
                    currency_fmt = wb.add_format({'border': 1, 'num_format': '#,##0'})
                    
                    for col_num, value in enumerate(df_f.columns.values):
                        ws.write(0, col_num, value, header_fmt)
                    
                    ws.set_column('A:A', 25, border_fmt)
                    ws.set_column('B:B', 50, border_fmt)
                    ws.set_column('C:C', 18, currency_fmt)
                    ws.set_column('D:D', 30, border_fmt)
                    ws.set_column('E:E', 50, border_fmt)
                    ws.autofilter(0, 0, len(df_f), len(df_f.columns) - 1)
                
                # Restore button color for export
                st.markdown('<style>div[data-testid="stDownloadButton"] button {background: linear-gradient(135deg, #064e3b 0%, #10b981 100%) !important;}</style>', unsafe_allow_html=True)
                st.download_button("⬇️ Download Excel Resmi (.xlsx)", data=buf.getvalue(), file_name=f"Laporan_BPS_Tokopedia_{datetime.date.today()}.xlsx")
        
        with tab3:
            audit = st.session_state.audit_tokped
            total = int(audit.get('total', 0))
            valid = int(audit.get('valid', 0))
            f_count = int(audit.get('file_count', 0))
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("Scanner ini memecah baris menyamping Tokopedia menjadi deretan data vertikal.")
            
            a1, a2, a3 = st.columns(3)
            a1.metric("📂 File Diproses", f"{f_count:,}".replace(",", "."))
            a2.metric("📥 Total Baris CSV", f"{total:,}".replace(",", "."))
            a3.metric("✅ Total Produk Diekstrak", f"{valid:,}".replace(",", "."))
            
            st.write("---")
            st.success("Sistem telah otomatis membuang duplikat dan produk dengan format harga yang tidak valid (Rp0).")
