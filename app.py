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

# --- 2. CSS MINIMALIS ---
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    .banner-shopee {
        background: linear-gradient(90deg, #022a5e 0%, #0056b3 100%);
        padding: 25px 35px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); color: white;
    }
    .banner-shopee h1 { color: white !important; font-weight: 700; margin-bottom: 5px; font-size: 2.2rem; }
    .banner-shopee p { color: #dbeafe !important; font-size: 1.05rem; margin: 0; }
    
    .banner-tokped {
        background: linear-gradient(90deg, #064e3b 0%, #059669 100%);
        padding: 25px 35px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); color: white;
    }
    .banner-tokped h1 { color: white !important; font-weight: 700; margin-bottom: 5px; font-size: 2.2rem; }
    .banner-tokped p { color: #d1fae5 !important; font-size: 1.05rem; margin: 0; }
    
    .banner-gabungan {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        padding: 25px 35px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); color: white;
    }
    .banner-gabungan h1 { color: white !important; font-weight: 700; margin-bottom: 5px; font-size: 2.2rem; }
    .banner-gabungan p { color: #cbd5e1 !important; font-size: 1.05rem; margin: 0; }
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
    halaman = st.radio("Pilih Fitur:", ["🟠 Shopee", "🟢 Tokopedia", "📊 Export Gabungan"])
    st.divider()

# ==============================================================================
#                             HALAMAN SHOPEE
# ==============================================================================
if halaman == "🟠 Shopee":
    st.markdown("""
    <div class="banner-shopee">
        <div style="font-size: 0.85rem; font-weight: bold; letter-spacing: 1px; color: #93c5fd; margin-bottom: 5px;">🏛️ BADAN PUSAT STATISTIK</div>
        <h1>Dashboard UMKM - Shopee</h1>
        <p>Pengolahan Data E-Commerce Multi-File Berbasis Lokasi Shopee</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Shopee")
        files_shopee = st.file_uploader("Unggah CSV Shopee", type=["csv"], accept_multiple_files=True, key="file_shp")
        mode_api_shp = st.checkbox("🔍 Deteksi Nama Toko via API", key="api_shp")
        
        if st.button("🚀 Proses Shopee", type="primary", use_container_width=True):
            if not files_shopee:
                st.error("⚠️ Unggah file CSV Shopee dulu!")
            else:
                with st.spinner("Memproses seluruh data Shopee..."):
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
                        st.success(f"✅ {len(hasil)} data Shopee berhasil diekstrak!")
                    except Exception as e:
                        st.error(f"Error Sistem: {e}")

    df_shp = st.session_state.data_shopee
    if df_shp is not None and not df_shp.empty:
        f_wil = st.multiselect("Pilih Wilayah (Lokasi Asli):", options=sorted(df_shp["Wilayah"].unique()), default=sorted(df_shp["Wilayah"].unique()), key="f_wil_shp")
        df_f = df_shp[df_shp["Wilayah"].isin(f_wil)]
        st.write("---")
        
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Penggabungan"])
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Data Tampil", f"{len(df_f):,}".replace(",", "."))
            c2.metric("Rata-rata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",", ".") if not df_f.empty else "Rp 0")
            c3.metric("Titik Lokasi", f"{df_f['Wilayah'].nunique()}")
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.pie(df_f, names="Wilayah", title="Sebaran UMKM per Lokasi", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
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
                    ws.set_column('A:A', 25); ws.set_column('B:B', 50); ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'})); ws.set_column('D:D', 30); ws.set_column('E:E', 50)
                st.download_button("⬇️ Download Excel Shopee", data=buf.getvalue(), file_name=f"UMKM_Shopee_{datetime.date.today()}.xlsx", type="primary")
        with tab3:
            audit = st.session_state.audit_shopee
            st.info(f"**📂 Jumlah File Diproses:** {audit.get('file_count',0)} File CSV")
            st.success(f"**📥 Total Baris Data Ditarik:** {audit.get('valid',0)} Baris")
            st.warning(f"**🛠️ Perbaikan Format Harga:** {audit.get('error_harga',0)} Baris")

# ==============================================================================
#                             HALAMAN TOKOPEDIA
# ==============================================================================
elif halaman == "🟢 Tokopedia":
    st.markdown("""
    <div class="banner-tokped">
        <div style="font-size: 0.85rem; font-weight: bold; letter-spacing: 1px; color: #a7f3d0; margin-bottom: 5px;">🏛️ BADAN PUSAT STATISTIK</div>
        <h1>Dashboard UMKM - Tokopedia</h1>
        <p>Pengolahan Data E-Commerce Multi-File Berbasis Lokasi Tokopedia</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📥 Input Data Tokopedia")
        files_tokped = st.file_uploader("Unggah CSV Tokopedia", type=["csv"], accept_multiple_files=True, key="file_tkp")
        
        if st.button("🚀 Proses Tokopedia", type="primary", use_container_width=True):
            if not files_tokped:
                st.error("⚠️ Unggah file CSV Tokopedia dulu!")
            else:
                with st.spinner("Memindai radar Tokopedia..."):
                    try:
                        hasil, total_baris, err_h = [], 0, 0
                        bar = st.progress(0)
                        
                        for idx, file in enumerate(files_tokped):
                            df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                            total_baris += len(df_raw)
                            
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
                                            
                                        try: val_h = int(re.sub(r"[^\d]", "", harga_str))
                                        except: val_h, err_h = 0, err_h + 1
                                        
                                        if val_h > 0:
                                            hasil.append({"Nama Toko": toko, "Nama Produk": nama, "Harga": val_h, "Wilayah": lokasi_tokped, "Link": link})
                                            
                                    except Exception:
                                        continue
                            bar.progress((idx + 1) / len(files_tokped))
                        
                        bar.empty()
                        df_final = pd.DataFrame(hasil).drop_duplicates()
                        st.session_state.data_tokped = df_final
                        st.session_state.audit_tokped = {"total": total_baris, "valid": len(df_final), "file_count": len(files_tokped), "error_harga": err_h}
                        st.success(f"✅ {len(df_final)} data berhasil diekstrak dari {len(files_tokped)} file Tokopedia!")
                    except Exception as e:
                        st.error(f"Error Sistem Tokopedia: {e}")

    df_tkp = st.session_state.data_tokped
    if df_tkp is not None and not df_tkp.empty:
        f_wil = st.multiselect("Pilih Wilayah (Lokasi Asli):", options=sorted(df_tkp["Wilayah"].unique()), default=sorted(df_tkp["Wilayah"].unique()), key="f_wil_tkp")
        df_f = df_tkp[df_tkp["Wilayah"].isin(f_wil)]
        st.write("---")
        
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Penggabungan"])
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Data Tampil", f"{len(df_f):,}".replace(",", "."))
            c2.metric("Rata-rata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",", ".") if not df_f.empty else "Rp 0")
            c3.metric("Titik Lokasi", f"{df_f['Wilayah'].nunique()}")
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.pie(df_f, names="Wilayah", title="Sebaran UMKM per Lokasi", hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
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
                    ws.set_column('A:A', 25); ws.set_column('B:B', 50); ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'})); ws.set_column('D:D', 30); ws.set_column('E:E', 50)
                st.markdown('<style>div[data-testid="stDownloadButton"] button {background-color: #059669; color: white; border:none;}</style>', unsafe_allow_html=True)
                st.download_button("⬇️ Download Excel Tokopedia", data=buf.getvalue(), file_name=f"UMKM_Tokopedia_{datetime.date.today()}.xlsx")
        with tab3:
            audit = st.session_state.audit_tokped
            st.info(f"**📂 Jumlah File Diproses:** {audit.get('file_count',0)} File CSV")
            st.success(f"**📥 Total Data Berhasil Diekstrak:** {audit.get('valid',0)} Produk")
            st.warning(f"**🛠️ Perbaikan Format Harga:** {audit.get('error_harga',0)} Baris")

# ==============================================================================
#                             HALAMAN EXPORT GABUNGAN
# ==============================================================================
elif halaman == "📊 Export Gabungan":
    st.markdown("""
    <div class="banner-gabungan">
        <div style="font-size: 0.85rem; font-weight: bold; letter-spacing: 1px; color: #94a3b8; margin-bottom: 5px;">🏛️ BADAN PUSAT STATISTIK</div>
        <h1>Export Master Data Gabungan</h1>
        <p>Download Shopee & Tokopedia dalam 1 file Excel (Beda Sheet + Auto Filter)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cek apakah sudah ada data dari Shopee atau Tokopedia
    df_shp_ready = st.session_state.data_shopee is not None and not st.session_state.data_shopee.empty
    df_tkp_ready = st.session_state.data_tokped is not None and not st.session_state.data_tokped.empty
    
    if not df_shp_ready and not df_tkp_ready:
        st.warning("⚠️ Belum ada data yang diproses. Silakan upload dan proses data di menu Shopee atau Tokopedia terlebih dahulu.")
    else:
        st.success("✅ Data siap untuk digabungkan menjadi file Master Excel!")
        
        # Menampilkan indikator angka
        c1, c2 = st.columns(2)
        if df_shp_ready:
            c1.metric("📦 Total Produk Shopee", f"{len(st.session_state.data_shopee):,}".replace(",", "."))
        if df_tkp_ready:
            c2.metric("📦 Total Produk Tokopedia", f"{len(st.session_state.data_tokped):,}".replace(",", "."))
            
        st.write("---")
        st.markdown("Klik tombol di bawah ini untuk mengunduh Excel dengan **Format Tab/Sheet Terpisah** dan sudah terpasang **Fitur Filter otomatis**.")
        
        # Logika Gabung Excel dengan XlsxWriter
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            wb = writer.book
            currency_fmt = wb.add_format({'num_format': '#,##0'})
            
            # --- SHEET SHOPEE ---
            if df_shp_ready:
                df_shp = st.session_state.data_shopee
                df_shp.to_excel(writer, index=False, sheet_name="Data Shopee")
                ws_shp = writer.sheets["Data Shopee"]
                
                header_fmt_shp = wb.add_format({'bold': True, 'bg_color': '#022a5e', 'font_color': 'white'})
                for col_num, value in enumerate(df_shp.columns.values):
                    ws_shp.write(0, col_num, value, header_fmt_shp)
                
                ws_shp.set_column('A:A', 25)
                ws_shp.set_column('B:B', 50)
                ws_shp.set_column('C:C', 18, currency_fmt)
                ws_shp.set_column('D:D', 30)
                ws_shp.set_column('E:E', 50)
                # Menambahkan Auto Filter di dalam Excel
                ws_shp.autofilter(0, 0, len(df_shp), len(df_shp.columns) - 1)
                
            # --- SHEET TOKOPEDIA ---
            if df_tkp_ready:
                df_tkp = st.session_state.data_tokped
                df_tkp.to_excel(writer, index=False, sheet_name="Data Tokopedia")
                ws_tkp = writer.sheets["Data Tokopedia"]
                
                header_fmt_tkp = wb.add_format({'bold': True, 'bg_color': '#064e3b', 'font_color': 'white'})
                for col_num, value in enumerate(df_tkp.columns.values):
                    ws_tkp.write(0, col_num, value, header_fmt_tkp)
                
                ws_tkp.set_column('A:A', 25)
                ws_tkp.set_column('B:B', 50)
                ws_tkp.set_column('C:C', 18, currency_fmt)
                ws_tkp.set_column('D:D', 30)
                ws_tkp.set_column('E:E', 50)
                # Menambahkan Auto Filter di dalam Excel
                ws_tkp.autofilter(0, 0, len(df_tkp), len(df_tkp.columns) - 1)
                
        # Tombol Download Gabungan
        st.markdown('<style>div[data-testid="stDownloadButton"] button {background-color: #0f172a; color: white; border:none; height: 3.5rem; font-size: 1.1rem;}</style>', unsafe_allow_html=True)
        st.download_button(
            label="⬇️ DOWNLOAD EXCEL MASTER (GABUNGAN)",
            data=buf.getvalue(),
            file_name=f"Master_UMKM_BPS_{datetime.date.today()}.xlsx",
            use_container_width=True
        )
