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
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .bps-banner {
        background: linear-gradient(90deg, #022a5e 0%, #0056b3 100%);
        padding: 25px 35px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        color: white;
    }
    .bps-banner h1 {
        color: white !important;
        font-family: sans-serif;
        font-weight: 700;
        margin-bottom: 5px;
        font-size: 2.2rem;
    }
    .bps-banner p {
        color: #dbeafe !important;
        font-size: 1.05rem;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "data_bersih" not in st.session_state:
    st.session_state.data_bersih = None
if "audit_data" not in st.session_state:
    st.session_state.audit_data = {}

# --- 4. HEADER UTAMA ---
st.markdown("""
<div class="bps-banner">
    <div style="font-size: 0.85rem; font-weight: bold; letter-spacing: 1px; color: #93c5fd; margin-bottom: 5px;">🏛️ BADAN PUSAT STATISTIK</div>
    <h1>Dashboard Integrasi Data UMKM (Bulk Upload)</h1>
    <p>Pengolahan Data E-Commerce Multi-File Berbasis Lokasi Shopee</p>
</div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR KONTROL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    st.header("📥 Input Data")
    # FITUR BARU: accept_multiple_files=True
    uploaded_files = st.file_uploader("Unggah CSV Shopee (Bisa pilih banyak file)", type=["csv"], accept_multiple_files=True)
    
    mode_api = st.checkbox("🔍 Deteksi Nama Toko via API")
    
    st.divider()
    
    if st.button("🚀 Proses Semua Data", type="primary", use_container_width=True):
        if not uploaded_files:
            st.error("⚠️ Silakan unggah minimal 1 file CSV terlebih dahulu!")
        else:
            with st.spinner(f"Memproses {len(uploaded_files)} file CSV sekaligus..."):
                try:
                    hasil = []
                    total_baris_keseluruhan = 0
                    err_h = 0
                    
                    bar = st.progress(0)
                    
                    # Looping untuk setiap file CSV yang diupload
                    for idx, file in enumerate(uploaded_files):
                        df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                        total_baris_keseluruhan += len(df_raw)
                        
                        # --- DETEKSI KOLOM SCRAPER SHOPEE ---
                        col_link = next((c for c in df_raw.columns if 'href' in c.lower()), df_raw.columns[0])
                        col_nama = next((c for c in df_raw.columns if 'whitespace-normal' in c.lower()), df_raw.columns[3])
                        col_harga = next((c for c in df_raw.columns if 'font-medium 2' in c.lower()), df_raw.columns[4])
                        col_wilayah = next((c for c in df_raw.columns if 'ml-[3px]' in c.lower()), df_raw.columns[7])

                        t_rows = len(df_raw)
                        
                        for i in range(t_rows):
                            row = df_raw.iloc[i]
                            link = str(row[col_link])
                            nama = str(row[col_nama])
                            harga_str = str(row[col_harga])
                            
                            # MENGGUNAKAN LOKASI ASLI SHOPEE (Tidak ada data dibuang)
                            lokasi_shopee = str(row[col_wilayah]).title()
                            
                            # Bersihkan Harga
                            try:
                                val_h = int(re.sub(r"[^\d]", "", harga_str))
                            except:
                                val_h = 0
                                err_h += 1
                            
                            # Ambil Nama Toko
                            toko = "Tidak Dilacak"
                            if mode_api:
                                match = re.search(r"i\.(\d+)\.", link)
                                if match:
                                    try:
                                        res = requests.get(f"https://shopee.co.id/api/v4/shop/get_shop_base?shopid={match.group(1)}", headers={"User-Agent":"Mozilla/5.0"}, timeout=2)
                                        if res.status_code == 200: toko = res.json().get("data",{}).get("name", "Anonim")
                                    except: pass

                            hasil.append({
                                "Nama Toko": toko, 
                                "Nama Produk": nama, 
                                "Harga": val_h, 
                                "Wilayah": lokasi_shopee, 
                                "Link": link
                            })
                        
                        # Update progress bar per file
                        bar.progress((idx + 1) / len(uploaded_files))
                    
                    bar.empty()
                    st.session_state.data_bersih = pd.DataFrame(hasil)
                    st.session_state.audit_data = {
                        "total": total_baris_keseluruhan, 
                        "valid": len(hasil), 
                        "file_count": len(uploaded_files),
                        "error_harga": err_h
                    }
                    st.success(f"✅ Berhasil menggabungkan {len(hasil)} data dari {len(uploaded_files)} file!")
                except Exception as e:
                    st.error(f"Error Sistem: {e}")

# --- 6. KONTEN DASHBOARD UTAMA ---
if st.session_state.data_bersih is not None:
    df = st.session_state.data_bersih
    
    if df.empty:
        st.warning("⚠️ Data kosong. Pastikan file CSV memiliki format yang benar.")
    else:
        st.write("### 🔎 Filter Wilayah (Berdasarkan Lokasi Shopee)")
        
        # Opsi Select All / Deselect All lebih gampang kalau pakai default terisi semua
        f_wil = st.multiselect(
            "Pilih Wilayah (Bisa hapus wilayah yang tidak diinginkan, misal: Mojokerto)", 
            options=sorted(df["Wilayah"].unique()), 
            default=sorted(df["Wilayah"].unique())
        )
        df_f = df[df["Wilayah"].isin(f_wil)]
        
        st.write("---")
        
        # TAB MENU
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Penggabungan"])
        
        # --- TAB 1: DASHBOARD ---
        with tab1:
            st.write("#### Ringkasan Indikator UMKM")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Data Tampil", f"{len(df_f):,}".replace(",", "."))
            c2.metric("Rata-rata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",", ".") if not df_f.empty else "Rp 0")
            c3.metric("Cakupan Wilayah", f"{df_f['Wilayah'].nunique()} Titik Lokasi")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if not df_f.empty:
                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    fig_pie = px.pie(df_f, names="Wilayah", title="Distribusi UMKM per Lokasi", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
                    st.plotly_chart(fig_pie, use_container_width=True)
                with col_chart2:
                    fig_bar = px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), x="Wilayah", y="Jumlah", title="Total Usaha per Wilayah Shopee", color="Wilayah", color_discrete_sequence=px.colors.sequential.Blues_r)
                    st.plotly_chart(fig_bar, use_container_width=True)

        # --- TAB 2: DATABASE EXCEL ---
        with tab2:
            st.write("#### 📋 Tabel Database (Gabungan)")
            
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=350)
            
            if not df_f.empty:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_f.to_excel(writer, index=False, sheet_name="Data UMKM")
                    wb = writer.book
                    ws = writer.sheets["Data UMKM"]
                    
                    header_fmt = wb.add_format({'bold': True, 'bg_color': '#022a5e', 'font_color': 'white', 'border': 1})
                    currency_fmt = wb.add_format({'num_format': '#,##0', 'border': 1})
                    border_fmt = wb.add_format({'border': 1})
                    
                    for col_num, value in enumerate(df_f.columns.values):
                        ws.write(0, col_num, value, header_fmt)
                        
                    ws.set_column('A:A', 25, border_fmt)
                    ws.set_column('B:B', 50, border_fmt)
                    ws.set_column('C:C', 18, currency_fmt)
                    ws.set_column('D:D', 30, border_fmt)
                    ws.set_column('E:E', 50, border_fmt)
                    ws.autofilter(0, 0, len(df_f), len(df_f.columns) - 1)
                
                st.download_button(
                    label="⬇️ Download Excel (Gabungan Multi-File)", 
                    data=buf.getvalue(), 
                    file_name=f"UMKM_Bulk_Shopee_{datetime.date.today()}.xlsx",
                    type="primary" 
                )

        # --- TAB 3: AUDIT PENGGABUNGAN ---
        with tab3:
            audit = st.session_state.audit_data
            
            t_str = f"{audit.get('total', 0):,}".replace(",", ".")
            v_str = f"{audit.get('valid', 0):,}".replace(",", ".")
            f_str = f"{audit.get('file_count', 0):,}".replace(",", ".")
            e_str = f"{audit.get('error_harga', 0):,}".replace(",", ".")
            
            st.write("#### 📑 Log Sistem Penggabungan (Bulk Process)")
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.info(f"**📂 Jumlah File Diproses:** {f_str} File CSV")
                st.success(f"**📥 Total Baris Data Ditarik:** {v_str} Baris")
                st.warning(f"**🛠️ Perbaikan Format Harga:** {e_str} Baris")
            
            with col_b:
                st.markdown("""
                **Info Sistem Baru:**
                - Semua lokasi yang tertera adalah murni hasil deteksi *Scraper* Shopee (tanpa filter/dibuang).
                - Jika ada kota di luar Babel yang masuk (seperti Mojokerto/Jakarta), Anda dapat **menghapusnya melalui Filter Wilayah** di bagian atas Dashboard.
                """)

else:
    st.info("👈 Silakan unggah beberapa file CSV sekaligus (drag & drop) di panel kiri untuk memulai proses penggabungan data otomatis.")
