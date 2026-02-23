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

# --- 2. CUSTOM CSS PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7fb !important; }
    .premium-header {
        background: linear-gradient(135deg, #061e45 0%, #0d3b7a 60%, #1565c0 100%);
        padding: 30px 40px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(6,30,69,0.15); color: white !important;
    }
    .premium-header h1 { color: white !important; font-weight: 800; margin-bottom: 5px; }
    .premium-header p { color: #e0f2fe !important; margin: 0; }
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
    <p>Sistem ekstraksi dan pembersihan data UMKM Provinsi Kepulauan Bangka Belitung</p>
</div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.info("💡 Taruh 'logo.png' di folder aplikasi.")
    
    st.markdown("---")
    st.markdown("### 📥 Input Data")
    uploaded_file = st.file_uploader("Upload CSV Shopee", type=["csv"])
    
    mode_api = st.checkbox("🔍 Deteksi Nama Toko via API")
    
    if st.button("🚀 Mulai Pemrosesan Data", use_container_width=True):
        if uploaded_file is None:
            st.error("⚠️ Upload file CSV dulu!")
        else:
            with st.spinner("Menjalankan Radar BPS..."):
                try:
                    df_raw = pd.read_csv(uploaded_file, dtype=str, on_bad_lines="skip")
                    
                    # --- RADAR DETEKSI KOLOM (Mendukung Format shopee (5).csv) ---
                    col_link, col_nama, col_harga, col_wilayah = None, None, None, None
                    for c in df_raw.columns:
                        low = c.lower()
                        if 'href' in low and 'contents' in low: col_link = c
                        if 'whitespace-normal' in low: col_nama = c
                        if 'font-medium 2' in low: col_harga = c
                        if 'ml-[3px]' in low: col_wilayah = c
                    
                    # Fallback jika nama kolom standar
                    if not col_link: col_link = df_raw.columns[0]
                    if not col_nama: col_nama = df_raw.columns[3] if len(df_raw.columns) > 3 else df_raw.columns[0]
                    if not col_harga: col_harga = df_raw.columns[4] if len(df_raw.columns) > 4 else df_raw.columns[0]
                    if not col_wilayah: col_wilayah = df_raw.columns[7] if len(df_raw.columns) > 7 else df_raw.columns[-1]

                    hasil = []
                    target_babel = ["bangka", "pangkal pinang", "pangkalpinang", "sungailiat", "toboali", "mentok", "koba", "belitung"]
                    
                    t_rows = len(df_raw)
                    luar, err_h = 0, 0
                    bar = st.progress(0)
                    
                    for i in range(t_rows):
                        link = str(df_raw.iloc[i][col_link])
                        nama = str(df_raw.iloc[i][col_nama])
                        harga_str = str(df_raw.iloc[i][col_harga])
                        wilayah_str = str(df_raw.iloc[i][col_wilayah])
                        
                        # Fix Harga (Hapus titik/Rp)
                        try:
                            val_h = int(re.sub(r"[^\d]", "", harga_str))
                            if 0 < val_h < 1000: val_h *= 1000
                        except:
                            val_h = 0
                            err_h += 1
                        
                        # Filter Wilayah
                        v_final = "Luar Wilayah"
                        for k in target_babel:
                            if k in wilayah_str.lower() or k in nama.lower():
                                v_final = "Kota Pangkalpinang" if "pangkal" in k else f"Kab. {k.title()}"
                                break
                        
                        if v_final == "Luar Wilayah":
                            luar += 1
                            continue
                        
                        # API Nama Toko (Opsional)
                        toko = "Tidak Dilacak"
                        if mode_api:
                            match = re.search(r"i\.(\d+)\.", link)
                            if match:
                                try:
                                    res = requests.get(f"https://shopee.co.id/api/v4/shop/get_shop_base?shopid={match.group(1)}", headers={"User-Agent":"Mozilla/5.0"}, timeout=2)
                                    if res.status_code == 200: toko = res.json().get("data",{}).get("name", "Anonim")
                                except: pass

                        hasil.append({"Nama Toko": toko, "Nama Produk": nama, "Harga": val_h, "Wilayah": v_final, "Link": link})
                        bar.progress((i + 1) / t_rows)
                    
                    bar.empty()
                    st.session_state.data_bersih = pd.DataFrame(hasil)
                    st.session_state.audit_data = {"total": t_rows, "valid": len(hasil), "luar": luar, "error_harga": err_h}
                    st.success(f"Berhasil memproses {len(hasil)} data.")
                except Exception as e:
                    st.error(f"Error: {e}")

# --- 6. DISPLAY ---
if st.session_state.data_bersih is not None:
    df = st.session_state.data_bersih
    if df.empty:
        st.warning("⚠️ Data valid tidak ditemukan.")
    else:
        st.markdown("### 🔎 Filter Data")
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            f_wil = st.multiselect("Wilayah", options=sorted(df["Wilayah"].unique()), default=sorted(df["Wilayah"].unique()))
        with c_f2:
            f_hrg = st.slider("Harga (Rp)", 0, int(df["Harga"].max()), (0, int(df["Harga"].max())))

        df_f = df[df["Wilayah"].isin(f_wil) & (df["Harga"] >= f_hrg[0]) & (df["Harga"] <= f_hrg[1])]
        
        t1, t2, t3 = st.tabs(["📊 Dashboard", "🗄️ Database", "📑 Audit"])
        
        with t1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total UMKM", len(df_f))
            c2.metric("Rata-rata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",","."))
            c3.metric("Cakupan", f"{df_f['Wilayah'].nunique()} Area")
            
            g1, g2 = st.columns(2)
            with g1:
                st.plotly_chart(px.pie(df_f, names="Wilayah", title="Sebaran UMKM", hole=0.4), use_container_width=True)
            with g2:
                st.plotly_chart(px.box(df_f, x="Wilayah", y="Harga", title="Statistik Harga"), use_container_width=True)

        with t2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",","."))
            st.dataframe(df_view, use_container_width=True, hide_index=True)
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                df_f.to_excel(writer, index=False, sheet_name="Data UMKM")
                wb = writer.book
                ws = writer.sheets["Data UMKM"]
                fmt = wb.add_format({'num_format': '#,##0'})
                ws.set_column('C:C', 15, fmt)
            
            st.download_button("⬇️ Download Excel", data=buf.getvalue(), file_name="BPS_Data.xlsx")

        with t3:
            audit = st.session_state.audit_data
            a1, a2, a3 = st.columns(3)
            a1.metric("Total Mentah", audit['total'])
            a2.metric("Dibuang (Luar Babel)", audit['luar'])
            a3.metric("Valid", audit['valid'])
            
            # Gauge Chart
            pct = (audit['valid']/audit['total']*100) if audit['total']>0 else 0
            fig = go.Figure(go.Indicator(mode="gauge+number", value=pct, title={'text': "Tingkat Validitas (%)"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#16a34a"}}))
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"📥 **Log:** Masuk {audit['total']} baris. Terdeteksi {audit['luar']} di luar Babel. {audit['error_harga']} error harga difix.")

else:
    st.info("👈 Silakan upload file CSV di samping.")
