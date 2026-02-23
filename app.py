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
    .stApp { background-color: #f8fafc !important; }
    .premium-header {
        background: linear-gradient(135deg, #061e45 0%, #0d3b7a 60%, #1565c0 100%);
        padding: 30px 40px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(6,30,69,0.15); color: white !important;
    }
    .premium-header h1 { color: white !important; font-weight: 800; margin-bottom: 5px; }
    div[data-testid="metric-container"] {
        background-color: #ffffff !important; border-left: 5px solid #1565c0 !important;
        padding: 20px !important; border-radius: 10px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1565c0 0%, #00b4d8 100%) !important;
        color: white !important; border-radius: 8px !important; font-weight: bold !important;
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #166534 0%, #22c55e 100%) !important;
        color: white !important; border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "data_bersih" not in st.session_state:
    st.session_state.data_bersih = None
if "audit_data" not in st.session_state:
    st.session_state.audit_data = {}

# --- 4. HEADER ---
st.markdown("""
<div class="premium-header">
    <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">🏛️ BADAN PUSAT STATISTIK</span>
    <h1>Portal Integrasi Data E-Commerce UMKM</h1>
    <p>Sistem Pembersihan Data Geospasial Murni - Provinsi Kepulauan Bangka Belitung</p>
</div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📥 Input Data")
    uploaded_file = st.file_uploader("Upload CSV Shopee", type=["csv"])
    
    mode_api = st.checkbox("🔍 Deteksi Nama Toko via API")
    
    if st.button("🚀 Proses Data (Strict Mode)", use_container_width=True):
        if uploaded_file is None:
            st.error("⚠️ Upload file CSV dulu bos!")
        else:
            with st.spinner("Memverifikasi Lokasi Fisik Pedagang..."):
                try:
                    df_raw = pd.read_csv(uploaded_file, dtype=str, on_bad_lines="skip")
                    
                    # --- RADAR DETEKSI KOLOM SCRAPER ---
                    # Menyesuaikan dengan format 'shopee (5).csv'
                    col_link = next((c for c in df_raw.columns if 'href' in c.lower()), df_raw.columns[0])
                    col_nama = next((c for c in df_raw.columns if 'whitespace-normal' in c.lower()), df_raw.columns[3])
                    col_harga = next((c for c in df_raw.columns if 'font-medium 2' in c.lower()), df_raw.columns[4])
                    col_wilayah = next((c for c in df_raw.columns if 'ml-[3px]' in c.lower()), df_raw.columns[7])

                    hasil = []
                    # DAFTAR RESMI WILAYAH BABEL (Strict Search)
                    babel_strict = {
                        "Kota Pangkalpinang": ["pangkal pinang", "pangkalpinang"],
                        "Kab. Bangka": ["kab. bangka", "sungailiat", "sungai liat"],
                        "Kab. Bangka Barat": ["bangka barat", "mentok", "muntok"],
                        "Kab. Bangka Tengah": ["bangka tengah", "koba"],
                        "Kab. Bangka Selatan": ["bangka selatan", "toboali"],
                        "Kab. Belitung": ["kab. belitung", "tanjung pandan", "tanjungpandan"],
                        "Kab. Belitung Timur": ["belitung timur", "manggar"]
                    }
                    
                    t_rows = len(df_raw)
                    luar, err_h = 0, 0
                    bar = st.progress(0)
                    
                    for i in range(t_rows):
                        row = df_raw.iloc[i]
                        link = str(row[col_link])
                        nama = str(row[col_nama])
                        harga_str = str(row[col_harga])
                        
                        # AMBIL LOKASI DARI KOLOM LOKASI (BUKAN DARI JUDUL!)
                        lokasi_shopee = str(row[col_wilayah]).lower()
                        
                        # 1. Standarisasi Harga
                        try:
                            val_h = int(re.sub(r"[^\d]", "", harga_str))
                        except:
                            val_h = 0
                            err_h += 1
                        
                        # 2. FILTER LOKASI MURNI (ANTI-MOJOKERTO)
                        v_final = "Luar Wilayah"
                        for kab, keys in babel_strict.items():
                            if any(k in lokasi_shopee for k in keys):
                                v_final = kab
                                break
                        
                        if v_final == "Luar Wilayah":
                            luar += 1
                            continue # Langsung buang kalau lokasinya gak di Babel
                        
                        # 3. API Nama Toko
                        toko = "Sedang Dicari..." if mode_api else "Tidak Dilacak"
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
                            "Wilayah BPS": v_final, 
                            "Lokasi Asli Shopee": lokasi_shopee.title(),
                            "Link": link
                        })
                        bar.progress((i + 1) / t_rows)
                    
                    bar.empty()
                    st.session_state.data_bersih = pd.DataFrame(hasil)
                    st.session_state.audit_data = {"total": t_rows, "valid": len(hasil), "luar": luar, "error_harga": err_h}
                    st.success(f"Ditemukan {len(hasil)} UMKM murni di Bangka Belitung.")
                except Exception as e:
                    st.error(f"Error Sistem: {e}")

# --- 6. DISPLAY DASHBOARD ---
if st.session_state.data_bersih is not None:
    df = st.session_state.data_bersih
    if df.empty:
        st.warning("⚠️ Gak ada data yang lolos sensor! Lokasi semua produk di file ini ada di luar Babel.")
        st.info(f"Log: Dari {st.session_state.audit_data['total']} data, semuanya lokasi luar daerah.")
    else:
        st.markdown("### 🔎 Filter Wilayah")
        f_wil = st.multiselect("Pilih Kabupaten/Kota", options=sorted(df["Wilayah BPS"].unique()), default=sorted(df["Wilayah BPS"].unique()))
        df_f = df[df["Wilayah BPS"].isin(f_wil)]
        
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Terverifikasi", "📑 Audit Kualitas Data"])
        
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total UMKM Terdata", len(df_f))
            c2.metric("Rata-rata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",","."))
            c3.metric("Status Data", "100% Babel Murni")
            
            st.plotly_chart(px.pie(df_f, names="Wilayah BPS", title="Sebaran UMKM per Wilayah Babel", hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)

        with tab2:
            st.write("#### 📋 Tabel Data UMKM Siap Lapor")
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",","."))
            st.dataframe(df_view, use_container_width=True, hide_index=True)
            
            # Export Excel
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                df_f.to_excel(writer, index=False, sheet_name="Data UMKM")
                wb, ws = writer.book, writer.sheets["Data UMKM"]
                ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'}))
                ws.set_column('B:B', 60)
            
            st.download_button("⬇️ Download Excel Resmi BPS", data=buf.getvalue(), file_name=f"UMKM_Babel_Akurat_{datetime.date.today()}.xlsx")

        with tab3:
            audit = st.session_state.audit_data
            st.markdown("#### 📑 Hasil Audit Verifikasi Lokasi")
            a1, a2, a3 = st.columns(3)
            a1.metric("Data Mentah (Input)", audit['total'])
            a2.metric("Lolos Verifikasi", audit['valid'])
            a3.metric("Dibuang (Luar Babel)", audit['luar'])
            
            pct = (audit['valid']/audit['total']*100) if audit['total']>0 else 0
            fig = go.Figure(go.Indicator(mode="gauge+number", value=pct, title={'text': "Akurasi Data Babel (%)"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#061e45"}}))
            st.plotly_chart(fig, use_container_width=True)
            st.info(f"Sistem telah membuang {audit['luar']} baris data yang lokasinya terdeteksi di luar Babel (seperti Mojokerto, Jakarta, dll) meskipun judulnya mengandung kata 'Bangka'.")

else:
    st.info("👈 Silakan unggah file CSV Shopee lu dulu bos, kita filter sampe bersih!")
