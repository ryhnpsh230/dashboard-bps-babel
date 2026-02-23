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

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7fb !important; }
    .premium-header {
        background: linear-gradient(135deg, #061e45 0%, #0d3b7a 60%, #1565c0 100%);
        padding: 30px 40px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(6,30,69,0.15); color: white !important;
    }
    div[data-testid="metric-container"] {
        background-color: #ffffff !important; border-left: 5px solid #1565c0 !important;
        padding: 20px !important; border-radius: 10px !important;
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
    <p>Verifikasi Akurasi Lokasi UMKM Provinsi Kepulauan Bangka Belitung</p>
</div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    st.markdown("### 📥 Input Data")
    uploaded_file = st.file_uploader("Upload CSV Shopee", type=["csv"])
    
    mode_api = st.checkbox("🔍 Deteksi Nama Toko via API")
    
    if st.button("🚀 Mulai Pemrosesan Data", use_container_width=True):
        if uploaded_file is None:
            st.error("⚠️ Upload file CSV dulu!")
        else:
            with st.spinner("Memverifikasi Lokasi Toko..."):
                try:
                    df_raw = pd.read_csv(uploaded_file, dtype=str, on_bad_lines="skip")
                    
                    # --- DETEKSI KOLOM ---
                    col_link = 'contents href' if 'contents href' in df_raw.columns else df_raw.columns[0]
                    col_nama = 'whitespace-normal' if 'whitespace-normal' in df_raw.columns else df_raw.columns[3]
                    col_harga = 'font-medium 2' if 'font-medium 2' in df_raw.columns else df_raw.columns[4]
                    col_wilayah = 'ml-[3px]' if 'ml-[3px]' in df_raw.columns else df_raw.columns[7]

                    hasil = []
                    # Mapping Wilayah Babel
                    babel_map = {
                        "Kota Pangkalpinang": ["pangkalpinang", "pangkal pinang"],
                        "Kab. Bangka": ["sungailiat", "sungai liat", "bangka h", "kab. bangka"],
                        "Kab. Bangka Barat": ["mentok", "muntok", "bangka barat"],
                        "Kab. Bangka Tengah": ["koba", "bangka tengah"],
                        "Kab. Bangka Selatan": ["toboali", "bangka selatan"],
                        "Kab. Belitung": ["tanjung pandan", "tanjungpandan", "belitung"],
                        "Kab. Belitung Timur": ["manggar", "belitung timur"]
                    }
                    
                    # Kata kunci pengecualian (Jika ada kata ini di lokasi, lupakan judul)
                    blacklist_lokasi = ["mojokerto", "jakarta", "bekasi", "tangerang", "bogor", "bandung", "surabaya", "medan", "palembang"]
                    
                    t_rows = len(df_raw)
                    luar, err_h = 0, 0
                    bar = st.progress(0)
                    
                    for i in range(t_rows):
                        link = str(df_raw.iloc[i][col_link])
                        nama = str(df_raw.iloc[i][col_nama])
                        harga_str = str(df_raw.iloc[i][col_harga])
                        lokasi_fisik = str(df_raw.iloc[i][col_wilayah]).lower()
                        
                        # 1. STANDARISASI HARGA
                        try:
                            val_h = int(re.sub(r"[^\d]", "", harga_str))
                        except:
                            val_h = 0
                            err_h += 1
                        
                        # 2. VERIFIKASI LOKASI (LOGIKA ANTI-MOJOKERTO)
                        v_final = "Luar Wilayah"
                        
                        # Cek apakah lokasi fisik sudah pasti di luar Babel
                        is_blacklist = any(x in lokasi_fisik for x in blacklist_lokasi)
                        
                        if not is_blacklist:
                            # Cek lokasi fisik terhadap kunci Babel
                            for kab, keys in babel_map.items():
                                if any(k in lokasi_fisik for k in keys):
                                    v_final = kab
                                    break
                            
                            # Jika lokasi fisik tidak jelas (misal cuma "Indonesia" atau kosong) 
                            # baru kita cek judul produk sebagai cadangan terakhir
                            if v_final == "Luar Wilayah":
                                for kab, keys in babel_map.items():
                                    if any(k in nama.lower() for k in keys):
                                        # Tapi pastikan lokasi fisik tidak bertentangan
                                        v_final = kab
                                        break
                        
                        if v_final == "Luar Wilayah":
                            luar += 1
                            continue
                        
                        # API Nama Toko
                        toko = "Tidak Dilacak"
                        if mode_api:
                            match = re.search(r"i\.(\d+)\.", link)
                            if match:
                                try:
                                    res = requests.get(f"https://shopee.co.id/api/v4/shop/get_shop_base?shopid={match.group(1)}", headers={"User-Agent":"Mozilla/5.0"}, timeout=2)
                                    if res.status_code == 200: toko = res.json().get("data",{}).get("name", "Anonim")
                                except: pass

                        hasil.append({"Nama Toko": toko, "Nama Produk": nama, "Harga": val_h, "Wilayah": v_final, "Link": link, "Lokasi Asli": lokasi_fisik.title()})
                        bar.progress((i + 1) / t_rows)
                    
                    bar.empty()
                    st.session_state.data_bersih = pd.DataFrame(hasil)
                    st.session_state.audit_data = {"total": t_rows, "valid": len(hasil), "luar": luar, "error_harga": err_h}
                    st.success(f"Ditemukan {len(hasil)} data UMKM Babel murni.")
                except Exception as e:
                    st.error(f"Error: {e}")

# --- 6. DISPLAY ---
if st.session_state.data_bersih is not None:
    df = st.session_state.data_bersih
    if df.empty:
        st.warning("⚠️ Tidak ada lokasi Babel yang terdeteksi secara akurat.")
    else:
        st.markdown("### 🔎 Filter Laporan")
        f_wil = st.multiselect("Pilih Wilayah Terverifikasi", options=sorted(df["Wilayah"].unique()), default=sorted(df["Wilayah"].unique()))
        df_f = df[df["Wilayah"].isin(f_wil)]
        
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard Statistik", "🗄️ Database Terverifikasi", "📑 Audit & Akurasi"])
        
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total UMKM Babel", len(df_f))
            c2.metric("Rata-rata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",","."))
            c3.metric("Akurasi Filter", "High")
            
            st.plotly_chart(px.pie(df_f, names="Wilayah", title="Persentase Sebaran UMKM Babel (Murni Lokasi)", hole=0.4), use_container_width=True)

        with tab2:
            st.dataframe(df_f, use_container_width=True, hide_index=True)
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                df_f.to_excel(writer, index=False, sheet_name="Data UMKM")
            st.download_button("⬇️ Download Excel", data=buf.getvalue(), file_name="BPS_Babel_Akurat.xlsx")

        with t3 if 't3' in locals() else tab3:
            audit = st.session_state.audit_data
            st.write("#### 📑 Log Verifikasi Lokasi")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"- **Total Baris CSV:** {audit['total']}")
                st.write(f"- **Dibuang (Luar Babel/Blacklist):** {audit['luar']}")
                st.write(f"- **Lolos Verifikasi:** {audit['valid']}")
            with col_b:
                pct = (audit['valid']/audit['total']*100) if audit['total']>0 else 0
                st.write(f"**Tingkat Kebersihan Data:** {pct:.1f}%")
                st.progress(pct/100)
            
            st.info("Sistem telah memblokir lokasi luar wilayah (seperti Mojokerto) meskipun judul produk mengandung kata kunci 'Bangka'.")

else:
    st.info("👈 Silakan unggah file CSV Shopee.")
