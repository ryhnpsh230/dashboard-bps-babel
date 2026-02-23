import streamlit as st
import pandas as pd
import re
import io
import requests
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os

# --- 1. CONFIG & THEME ---
st.set_page_config(
    page_title="Dashboard UMKM Babel - BPS",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED CSS (CLEAN & MODERN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* Global Style */
    .stApp {
        background-color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Header Panel */
    .main-header {
        background: linear-gradient(135deg, #061e45 0%, #1565c0 100%);
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(6,30,69,0.15);
        color: white;
    }
    .main-header h1 {
        color: white !important;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        letter-spacing: -1px;
    }

    /* Custom Cards for Metrics */
    div[data-testid="metric-container"] {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        padding: 20px !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white !important;
        border-radius: 10px 10px 0 0 !important;
        padding: 0 20px !important;
        font-weight: 600 !important;
        color: #64748b !important;
        border: 1px solid #e2e8f0 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1565c0 !important;
        color: white !important;
        border: none !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px !important;
        background: #1565c0 !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        height: 3rem;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background: #061e45 !important;
        box-shadow: 0 10px 15px -3px rgba(21, 101, 192, 0.4);
    }

    /* Sidebar Fix */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
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
<div class="main-header">
    <div style="display: flex; align-items: center; gap: 20px;">
        <div style="background: rgba(255,255,255,0.2); padding: 10px; border-radius: 12px;">📊</div>
        <div>
            <span style="font-weight: 600; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 2px; opacity: 0.8;">Badan Pusat Statistik</span>
            <h1>Dashboard UMKM Bangka Belitung</h1>
            <p style="opacity: 0.9; font-size: 1rem;">Sistem Integrasi Data E-Commerce & Statistik Ekonomi Regional</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=160)
    st.markdown("### 📥 Pengolahan Data")
    uploaded_file = st.file_uploader("Upload File CSV Shopee", type=["csv"])
    
    st.markdown("### 🛠️ Opsi Lanjutan")
    mode_api = st.checkbox("🔍 Crawl Nama Toko (API)", value=False)
    
    if st.button("🚀 Proses Sekarang", use_container_width=True):
        if uploaded_file is None:
            st.error("Silakan upload file dulu.")
        else:
            with st.spinner("Menganalisis Geospasial..."):
                try:
                    df_raw = pd.read_csv(uploaded_file, dtype=str, on_bad_lines="skip")
                    
                    # Detect Columns
                    col_link = next((c for c in df_raw.columns if 'href' in c.lower()), df_raw.columns[0])
                    col_nama = next((c for c in df_raw.columns if 'whitespace-normal' in c.lower()), df_raw.columns[3])
                    col_harga = next((c for c in df_raw.columns if 'font-medium 2' in c.lower()), df_raw.columns[4])
                    col_wilayah = next((c for c in df_raw.columns if 'ml-[3px]' in c.lower()), df_raw.columns[7])

                    hasil = []
                    # Strict Babel Keys
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
                        lokasi_shopee = str(row[col_wilayah]).lower()
                        
                        # Price Cleanup
                        try:
                            val_h = int(re.sub(r"[^\d]", "", harga_str))
                        except:
                            val_h = 0
                            err_h += 1
                        
                        # Strict Babel Location Filter
                        v_final = "Luar Wilayah"
                        for kab, keys in babel_strict.items():
                            if any(k in lokasi_shopee for k in keys):
                                v_final = kab
                                break
                        
                        if v_final == "Luar Wilayah":
                            luar += 1
                            continue 
                        
                        # Shop API
                        toko = "Anonim"
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
                            "Wilayah": v_final, 
                            "Lokasi Asli": lokasi_shopee.title(),
                            "Link": link
                        })
                        bar.progress((i + 1) / t_rows)
                    
                    bar.empty()
                    st.session_state.data_bersih = pd.DataFrame(hasil)
                    st.session_state.audit_data = {"total": t_rows, "valid": len(hasil), "luar": luar, "error_harga": err_h}
                    st.success(f"Berhasil! Ditemukan {len(hasil)} UMKM.")
                except Exception as e:
                    st.error(f"Error: {e}")

# --- 6. MAIN CONTENT ---
if st.session_state.data_bersih is not None:
    df = st.session_state.data_bersih
    
    # FILTER BAR
    with st.container():
        st.markdown("### 🔍 Filter Data")
        c_f1, c_f2 = st.columns([1, 1])
        with c_f1:
            f_wil = st.multiselect("Filter Wilayah", options=sorted(df["Wilayah"].unique()), default=sorted(df["Wilayah"].unique()))
        with c_f2:
            f_hrg = st.slider("Rentang Harga (Rp)", 0, int(df["Harga"].max() or 1000000), (0, int(df["Harga"].max() or 1000000)))
        
        df_f = df[df["Wilayah"].isin(f_wil) & (df["Harga"] >= f_hrg[0]) & (df["Harga"] <= f_hrg[1])]

    st.markdown("<br>", unsafe_allow_html=True)

    # TABS
    tab1, tab2, tab3 = st.tabs(["📈 Analisis Data", "📋 Database UMKM", "🛡️ Audit Kualitas"])

    # --- TAB 1: ANALYTICS ---
    with tab1:
        st.markdown("#### Ringkasan Statistik Babel")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total UMKM", f"{len(df_f)}")
        m2.metric("Rerata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",","."))
        m3.metric("Harga Tertinggi", f"Rp {df_f['Harga'].max():,.0f}".replace(",","."))
        m4.metric("Kab/Kota", f"{df_f['Wilayah'].nunique()}")

        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            fig_pie = px.pie(df_f, names="Wilayah", hole=0.5, 
                             color_discrete_sequence=px.colors.sequential.Blues_r,
                             title="Persentase Sebaran per Wilayah")
            fig_pie.update_layout(margin=dict(t=50, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)
        with g2:
            fig_bar = px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jumlah'), 
                             x="Wilayah", y="Jumlah", color="Wilayah",
                             color_discrete_sequence=px.colors.sequential.Blues_r,
                             title="Volume Produk per Wilayah")
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- TAB 2: DATABASE ---
    with tab2:
        st.markdown("#### 📋 Data UMKM Terverifikasi")
        df_view = df_f.copy()
        df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",","."))
        st.dataframe(df_view, use_container_width=True, hide_index=True)
        
        # Export
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            df_f.to_excel(writer, index=False, sheet_name="Data UMKM")
            wb, ws = writer.book, writer.sheets["Data UMKM"]
            ws.set_column('C:C', 18, wb.add_format({'num_format': '#,##0'}))
            ws.set_column('B:B', 60)
        
        st.download_button("⬇️ Download Excel Resmi BPS", data=buf.getvalue(), 
                           file_name=f"BPS_UMKM_Babel_{datetime.date.today()}.xlsx",
                           use_container_width=True)

    # --- TAB 3: AUDIT ---
    with tab3:
        audit = st.session_state.audit_data
        st.markdown("#### 📑 Verifikasi Integritas Data")
        
        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.write(f"**Data Mentah:** {audit['total']}")
            st.write(f"**Lolos Babel:** {audit['valid']}")
            st.write(f"**Data Dibuang:** {audit['luar']}")
            
            pct = (audit['valid']/audit['total']*100) if audit['total']>0 else 0
            st.metric("Tingkat Validitas Babel", f"{pct:.1f}%")
        
        with col_b:
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = pct,
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#1565c0"}},
                title = {'text': "Akurasi Wilayah (%)"}
            ))
            fig_gauge.update_layout(height=300, margin=dict(t=50, b=0))
            st.plotly_chart(fig_gauge, use_container_width=True)

        st.success("Audit Selesai: Semua lokasi luar daerah (seperti Mojokerto) telah otomatis difilter keluar.")

else:
    st.markdown("""
    <div style="text-align: center; padding: 100px; color: #94a3b8;">
        <h2 style="color: #cbd5e1;">Silakan Upload Data untuk Memulai</h2>
        <p>Gunakan file CSV hasil scraping Shopee Anda.</p>
    </div>
    """, unsafe_allow_html=True)
