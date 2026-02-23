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
    page_title="BPS · Data UMKM Babel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS (ANTI BLANK / ANTI BENTROK TEMA) ---
st.markdown("""
    <style>
    /* Kunci warna dasar aplikasi agar mengabaikan Dark Mode bawaan laptop */
    .stApp {
        background-color: #f4f7fb !important;
    }
    
    /* Header Utama */
    .premium-header {
        background: linear-gradient(135deg, #061e45 0%, #0d3b7a 60%, #1565c0 100%);
        padding: 30px 40px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(6,30,69,0.15);
        color: white !important;
    }
    .premium-header h1 {
        color: white !important;
        font-weight: 800;
        margin-bottom: 5px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .premium-header p {
        color: #e0f2fe !important;
        font-size: 1.1rem;
        margin: 0;
    }
    
    /* Kartu Metrik (Angka-angka di Dashboard) */
    div[data-testid="metric-container"] {
        background-color: #ffffff !important;
        border-left: 5px solid #1565c0 !important;
        padding: 20px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #475569 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 0.85rem !important;
    }
    div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    /* Tombol Utama */
    .stButton > button {
        background: linear-gradient(135deg, #1565c0 0%, #00b4d8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        height: 3.2em !important;
        font-weight: bold !important;
        box-shadow: 0 4px 12px rgba(0,100,200,0.2) !important;
    }
    
    /* Tombol Download */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #166534 0%, #22c55e 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    
    /* Tab Menu */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff !important;
        border-radius: 10px 10px 0 0;
        padding: 5px 10px 0 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #64748b !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1565c0 !important;
        border-bottom-color: #1565c0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "data_bersih" not in st.session_state:
    st.session_state.data_bersih = None
if "audit_data" not in st.session_state:
    st.session_state.audit_data = {}

# --- 4. HEADER MEWAH ---
st.markdown("""
<div class="premium-header">
    <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">🏛️ BADAN PUSAT STATISTIK</span>
    <h1>Portal Integrasi Data E-Commerce UMKM</h1>
    <p>Sistem ekstraksi, pembersihan, dan standarisasi pelaporan statistik Prov. Kep. Bangka Belitung</p>
</div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR (PANEL KIRI) ---
with st.sidebar:
    # Mengecek apakah file logo.png ada di dalam folder
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.info("💡 Taruh gambar 'logo.png' di folder aplikasi untuk menampilkan logo BPS.")
    
    st.markdown("---")
    st.markdown("### 📥 Input Data")
    uploaded_file = st.file_uploader("Upload CSV Shopee", type=["csv"])
    
    st.markdown("### ⚙️ Konfigurasi")
    mode_api = st.checkbox("🔍 Deteksi Nama Toko via API", help="Mengambil nama asli toko dari database Shopee. Butuh internet lancar.")
    
    st.write("---")
    if st.button("🚀 Mulai Pemrosesan Data", use_container_width=True):
        if uploaded_file is None:
            st.error("⚠️ Silakan upload file CSV terlebih dahulu!")
        else:
            with st.spinner("Menjalankan algoritma standarisasi BPS..."):
                try:
                    df_raw = pd.read_csv(uploaded_file, on_bad_lines="skip", dtype=str)
                    hasil = []
                    kota_bangka = ["Bangka", "Pangkal Pinang", "Pangkalpinang", "Sungailiat", "Toboali", "Mentok", "Koba"]
                    
                    total_baris = len(df_raw)
                    luar_wilayah = 0
                    error_harga = 0
                    
                    bar = st.progress(0)
                    
                    for i in range(total_baris):
                        # Ekstraksi aman
                        link        = str(df_raw.iloc[i, 0]) if len(df_raw.columns) > 0 else "-"
                        nama_produk = str(df_raw.iloc[i, 3]) if len(df_raw.columns) > 3 else "Tidak Diketahui"
                        harga_raw   = str(df_raw.iloc[i, 5]) if len(df_raw.columns) > 5 else "0"
                        wilayah_raw = str(df_raw.iloc[i, 11]) if len(df_raw.columns) > 11 else "-"
                        
                        # Fix Harga
                        try:
                            angka = re.sub(r"[^\d]", "", harga_raw)
                            harga = int(angka) if angka else 0
                            if 0 < harga < 1000:
                                harga *= 1000
                        except:
                            harga = 0
                            error_harga += 1
                            
                        # Filter Wilayah
                        wilayah_final = "Luar Wilayah"
                        for k in kota_bangka:
                            if k.lower() in wilayah_raw.lower():
                                wilayah_final = "Kota Pangkalpinang" if "pangkal" in k.lower() else f"Kab. {k.title()}"
                                break
                                
                        if wilayah_final == "Luar Wilayah":
                            luar_wilayah += 1
                            continue
                            
                        # API Nama Toko
                        nama_toko = "Tidak Dilacak"
                        if mode_api:
                            m = re.search(r"i\.(\d+)\.", link)
                            if m:
                                try:
                                    r = requests.get(f"https://shopee.co.id/api/v4/shop/get_shop_base?shopid={m.group(1)}", headers={"User-Agent": "Mozilla/5.0"}, timeout=2)
                                    if r.status_code == 200:
                                        nama_toko = r.json().get("data", {}).get("name", "Nama Disembunyikan")
                                except:
                                    pass
                                    
                        hasil.append({
                            "Nama Toko": nama_toko, 
                            "Nama Produk": nama_produk, 
                            "Harga": harga, 
                            "Wilayah": wilayah_final, 
                            "Link": link
                        })
                        
                        bar.progress((i + 1) / total_baris)
                    
                    bar.empty()
                    st.session_state.data_bersih = pd.DataFrame(hasil)
                    st.session_state.audit_data = {"total": total_baris, "valid": len(hasil), "luar": luar_wilayah, "error_harga": error_harga}
                    st.success(f"✅ Selesai! {len(hasil):,} data tervalidasi.".replace(",", "."))
                    
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan! Pastikan file CSV sesuai. Detail: {e}")

    st.caption(f"🗓️ Update: {datetime.datetime.now().strftime('%d %b %Y %H:%M')}")

# --- 6. JIKA BELUM ADA DATA ---
if st.session_state.data_bersih is None:
    st.markdown("""
    <div style="background: white; border: 2px dashed #cbd5e1; border-radius: 15px; padding: 60px 20px; text-align: center; margin-top: 20px;">
        <h1 style="font-size: 3rem; margin: 0;">📊</h1>
        <h3 style="color: #0f172a; font-family: sans-serif;">Workspace Kosong</h3>
        <p style="color: #64748b;">Silakan unggah file CSV Shopee di panel sebelah kiri untuk melihat keajaiban sistem ini.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- 7. DASHBOARD UTAMA (JIKA ADA DATA) ---
df = st.session_state.data_bersih

st.markdown("### 🔎 Filter Data")
col_f1, col_f2 = st.columns(2)
with col_f1:
    filter_wilayah = st.multiselect("Pilih Wilayah (Kab/Kota)", options=sorted(df["Wilayah"].unique()), default=sorted(df["Wilayah"].unique()))
with col_f2:
    max_h = int(df["Harga"].max()) if not df.empty and df["Harga"].max() > 0 else 1000000
    filter_harga = st.slider("Rentang Harga (Rp)", 0, max_h, (0, max_h))

df_f = df[df["Wilayah"].isin(filter_wilayah) & (df["Harga"] >= filter_harga[0]) & (df["Harga"] <= filter_harga[1])]

tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database & Export Excel", "📑 Audit Data"])

# ============ TAB 1: GRAFIK ============
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    rata = df_f["Harga"].mean() if not df_f.empty else 0
    maks = df_f["Harga"].max()  if not df_f.empty else 0
    
    k1.metric("🏪 Total UMKM", f"{len(df_f):,}".replace(",", "."))
    k2.metric("💰 Rata-rata Harga", f"Rp {rata:,.0f}".replace(",", "."))
    k3.metric("📈 Harga Tertinggi", f"Rp {maks:,.0f}".replace(",", "."))
    k4.metric("🗺️ Cakupan Wilayah", f"{df_f['Wilayah'].nunique()} Kab/Kota")
    
    if not df_f.empty:
        st.markdown("<hr style='border:1px solid #e2e8f0;'>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            fig_d = px.pie(df_f, names="Wilayah", title="Distribusi UMKM per Wilayah", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig_d, use_container_width=True)
        with g2:
            fig_b = px.box(df_f, x="Wilayah", y="Harga", title="Statistik Sebaran Harga", color="Wilayah", color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig_b, use_container_width=True)

# ============ TAB 2: EXPORT EXCEL ============
with tab2:
    st.markdown("#### 📋 Tabel Data Tervalidasi")
    
    # Format Rupiah di layar
    df_show = df_f.copy()
    df_show["Harga"] = df_show["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
    st.dataframe(df_show, use_container_width=True, height=350, hide_index=True)

    if not df_f.empty:
        # LOGIKA EXCEL SULTAN
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            df_f.to_excel(writer, index=False, sheet_name="Data UMKM")
            
            workbook = writer.book
            worksheet = writer.sheets["Data UMKM"]
            
            # Format
            header_format = workbook.add_format({'bold': True, 'bg_color': '#061E45', 'font_color': 'white', 'border': 1, 'align': 'center'})
            cell_format = workbook.add_format({'border': 1})
            currency_format = workbook.add_format({'border': 1, 'num_format': '#,##0'})
            
            # Tulis Header
            for col_num, value in enumerate(df_f.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Lebar Kolom
            worksheet.set_column("A:A", 25, cell_format)
            worksheet.set_column("B:B", 50, cell_format)
            worksheet.set_column("C:C", 15, currency_format) # Ini bikin harga pakai titik otomatis di Excel
            worksheet.set_column("D:D", 25, cell_format)
            worksheet.set_column("E:E", 50, cell_format)
            worksheet.autofilter(0, 0, len(df_f), len(df_f.columns) - 1)
            
        st.download_button(
            label="⬇️ Download Excel Resmi (.xlsx)", 
            data=buf.getvalue(), 
            file_name=f"Laporan_BPS_UMKM_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ============ TAB 3: AUDIT DATA ============
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    audit = st.session_state.audit_data
    
    # Ekstraksi data dengan aman
    total = int(audit.get('total', 0))
    valid = int(audit.get('valid', 0))
    luar = int(audit.get('luar', 0))
    err_h = int(audit.get('error_harga', 0))
    
    # Hitung persentase kebersihan data
    valid_pct = (valid / total * 100) if total > 0 else 0
    
    # Format angka menjadi format Indonesia (Pakai titik) di luar f-string agar tidak error
    total_str = f"{total:,}".replace(",", ".")
    valid_str = f"{valid:,}".replace(",", ".")
    luar_str = f"{luar:,}".replace(",", ".")
    err_str = f"{err_h:,}".replace(",", ".")
    
    st.markdown("#### 📑 Laporan Kualitas Data (Data Quality Audit)")
    st.info("Laporan ini menunjukkan tingkat integritas dan kebersihan data setelah melewati algoritma standarisasi BPS.")
    
    # --- 1. KOTAK METRIK AUDIT ---
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("📥 Total Data Mentah", f"{total_str}")
    a2.metric("🚫 Luar Wilayah (Dibuang)", f"{luar_str}")
    a3.metric("⚠️ Error Harga (Fix ke 0)", f"{err_str}")
    a4.metric("✅ Data Valid (Siap Ekspor)", f"{valid_str}")
    
    st.write("---")
    
    # --- 2. VISUALISASI & LOG DETAIL ---
    col_g1, col_g2 = st.columns([1, 1], gap="large")
    
    with col_g1:
        st.markdown("<h5 style='text-align: center; color: #475569;'>📈 Tingkat Validitas Data (Yield Rate)</h5>", unsafe_allow_html=True)
        
        # Grafik Meteran (Gauge Chart) menggunakan Plotly
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = valid_pct,
            number = {'suffix': "%", 'valueformat': '.1f', 'font': {'size': 45, 'color': '#0f172a'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#16a34a"}, 
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#e2e8f0",
                'steps': [
                    {'range': [0, 50], 'color': '#fee2e2'},   
                    {'range': [50, 80], 'color': '#fef08a'},  
                    {'range': [80, 100], 'color': '#dcfce3'}  
                ],
                'threshold': {
                    'line': {'color': "#1565c0", 'width': 4},
                    'thickness': 0.75,
                    'value': 80 
                }
            }
        ))
        fig_gauge.update_layout(height=280, margin=dict(t=30, b=10, l=30, r=30), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with col_g2:
        st.markdown("<h5 style='color: #475569;'>📋 Detail Log Pembersihan Otomatis</h5>", unsafe_allow_html=True)
        st.write("") # Memberi sedikit jarak
        
        # Menggunakan kotak pesan bawaan Streamlit (Pasti aman dari error UI)
        st.info(f"**📥 Data Awal Masuk:** Menerima **{total_str}** baris data mentah dari hasil ekstraksi file CSV Shopee.")
        
        st.error(f"**📍 Filter Geospasial:** Sistem menghapus **{luar_str}** baris data karena terdeteksi berada di luar cakupan Provinsi Kepulauan Bangka Belitung.")
        
        st.warning(f"**💰 Standarisasi Harga:** Mendeteksi **{err_str}** baris dengan anomali format harga teks. Sistem telah membersihkan dan merapikannya ke format numerik.")
        
        st.success(f"**✅ Status Akhir Data:** **{valid_str}** baris berhasil lolos uji validasi dan 100% siap untuk diekspor ke Excel resmi BPS.")