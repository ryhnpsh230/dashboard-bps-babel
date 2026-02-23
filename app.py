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

# --- 2. CSS CUSTOM (TEMA DINAMIS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Sidebar redesign */
    section[data-testid="stSidebar"] {
        background: #0a0f1e;
        border-right: 1px solid rgba(255,255,255,0.07);
    }
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
        display: block;
        transition: all 0.2s ease;
        border: 1px solid rgba(255,255,255,0.08);
        font-size: 0.9rem;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.1);
        border-color: rgba(255,255,255,0.2);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* ===================== BANNER SHOPEE ===================== */
    .banner-shopee {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #011e45 0%, #013d8a 50%, #0056b3 100%);
        padding: 32px 40px;
        border-radius: 20px;
        margin-bottom: 28px;
        box-shadow: 0 8px 32px rgba(0, 86, 179, 0.35);
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .banner-shopee::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 280px; height: 280px;
        background: radial-gradient(circle, rgba(59,130,246,0.25) 0%, transparent 70%);
        border-radius: 50%;
    }
    .banner-shopee::after {
        content: '';
        position: absolute;
        bottom: -80px; left: 30%;
        width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(96,165,250,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .banner-shopee .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        border-radius: 100px;
        padding: 4px 14px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #93c5fd !important;
        margin-bottom: 14px;
    }
    .banner-shopee h1 {
        color: white !important;
        font-weight: 800;
        margin: 0 0 8px 0;
        font-size: 2.0rem;
        line-height: 1.2;
        letter-spacing: -0.5px;
    }
    .banner-shopee p {
        color: rgba(219,234,254,0.8) !important;
        font-size: 0.95rem;
        margin: 0;
        font-weight: 400;
    }

    /* ===================== BANNER TOKOPEDIA ===================== */
    .banner-tokped {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #022c22 0%, #065f46 50%, #059669 100%);
        padding: 32px 40px;
        border-radius: 20px;
        margin-bottom: 28px;
        box-shadow: 0 8px 32px rgba(5, 150, 105, 0.35);
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .banner-tokped::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 280px; height: 280px;
        background: radial-gradient(circle, rgba(52,211,153,0.2) 0%, transparent 70%);
        border-radius: 50%;
    }
    .banner-tokped::after {
        content: '';
        position: absolute;
        bottom: -80px; left: 30%;
        width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(110,231,183,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .banner-tokped .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        border-radius: 100px;
        padding: 4px 14px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #a7f3d0 !important;
        margin-bottom: 14px;
    }
    .banner-tokped h1 {
        color: white !important;
        font-weight: 800;
        margin: 0 0 8px 0;
        font-size: 2.0rem;
        line-height: 1.2;
        letter-spacing: -0.5px;
    }
    .banner-tokped p {
        color: rgba(209,250,229,0.8) !important;
        font-size: 0.95rem;
        margin: 0;
        font-weight: 400;
    }

    /* ===================== METRIC CARDS ===================== */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #f8faff);
        padding: 20px 22px;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(0,0,0,0.1), 0 2px 6px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetric"] label {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        color: #64748b !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* ===================== METRIC ACCENT COLORS ===================== */
    .metric-blue div[data-testid="stMetric"] {
        border-left: 4px solid #3b82f6;
    }
    .metric-green div[data-testid="stMetric"] {
        border-left: 4px solid #10b981;
    }

    /* ===================== TABS ===================== */
    .stTabs [data-baseweb="tab-list"] {
        background: #f1f5f9;
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        border: none;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 8px 18px;
        color: #64748b !important;
        background: transparent;
        border: none;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #0f172a !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* ===================== DATAFRAME ===================== */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* ===================== MULTISELECT ===================== */
    .stMultiSelect > div {
        border-radius: 10px;
    }

    /* ===================== BUTTONS ===================== */
    .stButton > button, .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.88rem;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
        box-shadow: 0 4px 14px rgba(59,130,246,0.35);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }

    /* ===================== FILE UPLOADER ===================== */
    [data-testid="stFileUploader"] {
        border-radius: 12px;
    }

    /* ===================== ALERTS / INFO ===================== */
    .stAlert {
        border-radius: 12px;
    }

    /* ===================== DIVIDER ===================== */
    hr {
        border-color: #e2e8f0;
        margin: 1.5rem 0;
    }

    /* ===================== SIDEBAR SECTION TITLE ===================== */
    .sidebar-section-title {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #64748b !important;
        margin: 16px 0 8px 0;
    }

    /* ===================== STAT STRIP ===================== */
    .stat-strip {
        display: flex;
        gap: 12px;
        align-items: center;
        background: #f8faff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .stat-strip-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.85rem;
        color: #475569;
    }
    .stat-strip-item strong {
        color: #0f172a;
        font-weight: 700;
    }
    .stat-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: #cbd5e1;
    }

    /* ===================== SECTION HEADER ===================== */
    .section-header {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #94a3b8;
        margin: 20px 0 10px 0;
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
    else:
        st.markdown("""
        <div style="text-align:center; padding: 20px 0 10px 0;">
            <div style="font-size: 2.2rem;">🏛️</div>
            <div style="font-size: 0.65rem; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; color: #64748b; margin-top: 4px;">Badan Pusat Statistik</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="sidebar-section-title">🧭 Platform E-Commerce</div>', unsafe_allow_html=True)
    halaman = st.radio("", ["🟠 Shopee", "🟢 Tokopedia"], label_visibility="collapsed")
    st.divider()

# ==============================================================================
#                             HALAMAN SHOPEE
# ==============================================================================
if halaman == "🟠 Shopee":
    st.markdown("""
    <div class="banner-shopee">
        <div class="badge">🏛️ &nbsp;Badan Pusat Statistik</div>
        <h1>Dashboard UMKM — Shopee</h1>
        <p>Sistem Pengolahan Data Multi-File Berbasis Lokasi Shopee</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="sidebar-section-title">📥 Input Data</div>', unsafe_allow_html=True)
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
        f_wil = st.multiselect("🗺️ Filter Wilayah (Lokasi Asli):", options=sorted(df_shp["Wilayah"].unique()), default=sorted(df_shp["Wilayah"].unique()), key="f_wil_shp")
        df_f = df_shp[df_shp["Wilayah"].isin(f_wil)]
        st.write("---")
        
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Penggabungan"])
        with tab1:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Total Data Tampil", f"{len(df_f):,}".replace(",", "."))
            with c2:
                st.metric("Rata-rata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",", ".") if not df_f.empty else "Rp 0")
            with c3:
                st.metric("Titik Lokasi", f"{df_f['Wilayah'].nunique()}")

            if not df_f.empty:
                st.markdown("")
                g1, g2 = st.columns(2)
                with g1:
                    fig_pie = px.pie(
                        df_f, names="Wilayah",
                        title="Sebaran UMKM per Lokasi",
                        hole=0.5,
                        color_discrete_sequence=px.colors.sequential.Blues_r
                    )
                    fig_pie.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_family="Plus Jakarta Sans",
                        title_font_size=14,
                        title_font_color="#0f172a",
                        legend=dict(font=dict(size=11))
                    )
                    fig_pie.update_traces(textfont_size=12)
                    st.plotly_chart(fig_pie, use_container_width=True)
                with g2:
                    bar_data = df_f.groupby("Wilayah").size().reset_index(name='Jumlah').sort_values('Jumlah', ascending=True)
                    fig_bar = px.bar(
                        bar_data, x="Jumlah", y="Wilayah",
                        title="Total Usaha per Wilayah",
                        orientation='h',
                        color="Jumlah",
                        color_continuous_scale=px.colors.sequential.Blues
                    )
                    fig_bar.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_family="Plus Jakarta Sans",
                        title_font_size=14,
                        title_font_color="#0f172a",
                        coloraxis_showscale=False,
                        yaxis=dict(gridcolor='rgba(0,0,0,0)', title=''),
                        xaxis=dict(gridcolor='#f1f5f9', title='Jumlah Usaha')
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

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
                st.markdown("")
                st.download_button("⬇️ Download Excel Shopee", data=buf.getvalue(), file_name=f"UMKM_Shopee_{datetime.date.today()}.xlsx", type="primary")
        with tab3:
            audit = st.session_state.audit_shopee
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("📂 File Diproses", f"{audit.get('file_count', 0)}")
            col_b.metric("📥 Baris Ditarik", f"{audit.get('valid', 0):,}".replace(",", "."))
            col_c.metric("🛠️ Perbaikan Harga", f"{audit.get('error_harga', 0)}")

# ==============================================================================
#                             HALAMAN TOKOPEDIA
# ==============================================================================
elif halaman == "🟢 Tokopedia":
    st.markdown("""
    <div class="banner-tokped">
        <div class="badge">🏛️ &nbsp;Badan Pusat Statistik</div>
        <h1>Dashboard UMKM — Tokopedia</h1>
        <p>Deep Scanning Data Multi-File Berbasis Lokasi Tokopedia</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="sidebar-section-title">📥 Input Data</div>', unsafe_allow_html=True)
        files_tokped = st.file_uploader("Unggah CSV Tokopedia", type=["csv"], accept_multiple_files=True, key="file_tkp")
        
        if st.button("🚀 Proses Tokopedia", type="primary", use_container_width=True):
            if not files_tokped:
                st.error("⚠️ Unggah file CSV Tokopedia dulu!")
            else:
                with st.spinner("Menjalankan Deep Scanner Tokopedia..."):
                    try:
                        hasil, total_baris, err_h = [], 0, 0
                        bar = st.progress(0)
                        
                        for idx, file in enumerate(files_tokped):
                            df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                            total_baris += len(df_raw)
                            
                            # LOGIKA DEEP SCANNER (Memindai per baris untuk mencari pola data)
                            for _, row in df_raw.iterrows():
                                links, names, prices, locs, shops = [], [], [], [], []
                                
                                for col in df_raw.columns:
                                    val = str(row[col])
                                    if val == 'nan' or val == '': continue
                                    
                                    # Deteksi Link
                                    if 'tokopedia.com/' in val and 'extParam' in val: links.append(val)
                                    # Deteksi Harga
                                    elif 'Rp' in val: prices.append(val)
                                    # Deteksi Wilayah (Kota-kota besar dan keyword regional)
                                    elif any(k in val for k in ['Pangkal', 'Bangka', 'Belitung', 'Jakarta', 'Bogor', 'Mojokerto', 'Tangerang', 'Bandung', 'Bekasi', 'Medan', 'Surabaya']):
                                        if 'terjual' not in val.lower() and 'http' not in val: locs.append(val)
                                    # Deteksi Nama Produk (Teks panjang non-link)
                                    elif len(val) > 15 and ' ' in val and 'http' not in val and 'Rp' not in val: names.append(val)
                                    # Deteksi Nama Toko (Teks pendek non-angka)
                                    elif len(val) <= 15 and not any(char.isdigit() for char in val): shops.append(val)

                                # Menyatukan hasil scanning ke arah bawah (unrolling)
                                for k in range(len(links)):
                                    try:
                                        h_raw = prices[k] if k < len(prices) else "0"
                                        h_fix = int(re.sub(r"[^\d]", "", h_raw))
                                        
                                        # Buang jika harga 0 (Data sampah)
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
                        # Hapus duplikat dan simpan
                        df_final = pd.DataFrame(hasil).drop_duplicates()
                        st.session_state.data_tokped = df_final
                        st.session_state.audit_tokped = {"total": total_baris, "valid": len(df_final), "file_count": len(files_tokped), "error_harga": err_h}
                        st.success(f"✅ {len(df_final)} produk berhasil ditarik!")
                    except Exception as e:
                        st.error(f"Error Sistem Tokopedia: {e}")

    df_tkp = st.session_state.data_tokped
    if df_tkp is not None and not df_tkp.empty:
        f_wil = st.multiselect("🗺️ Filter Wilayah Tokopedia:", options=sorted(df_tkp["Wilayah"].unique()), default=sorted(df_tkp["Wilayah"].unique()), key="f_wil_tkp")
        df_f = df_tkp[df_tkp["Wilayah"].isin(f_wil)]
        st.write("---")
        
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Deep Scan"])
        with tab1:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Total Produk", f"{len(df_f):,}".replace(",", "."))
            with c2:
                st.metric("Rata-rata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",", ".") if not df_f.empty else "Rp 0")
            with c3:
                st.metric("Titik Lokasi", f"{df_f['Wilayah'].nunique()}")

            if not df_f.empty:
                st.markdown("")
                g1, g2 = st.columns(2)
                with g1:
                    fig_pie = px.pie(
                        df_f, names="Wilayah",
                        title="Sebaran UMKM per Lokasi",
                        hole=0.5,
                        color_discrete_sequence=px.colors.sequential.Greens_r
                    )
                    fig_pie.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_family="Plus Jakarta Sans",
                        title_font_size=14,
                        title_font_color="#0f172a",
                        legend=dict(font=dict(size=11))
                    )
                    fig_pie.update_traces(textfont_size=12)
                    st.plotly_chart(fig_pie, use_container_width=True)
                with g2:
                    bar_data = df_f.groupby("Wilayah").size().reset_index(name='Jumlah').sort_values('Jumlah', ascending=True)
                    fig_bar = px.bar(
                        bar_data, x="Jumlah", y="Wilayah",
                        title="Total Usaha per Wilayah",
                        orientation='h',
                        color="Jumlah",
                        color_continuous_scale=px.colors.sequential.Greens
                    )
                    fig_bar.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_family="Plus Jakarta Sans",
                        title_font_size=14,
                        title_font_color="#0f172a",
                        coloraxis_showscale=False,
                        yaxis=dict(gridcolor='rgba(0,0,0,0)', title=''),
                        xaxis=dict(gridcolor='#f1f5f9', title='Jumlah Usaha')
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

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
                st.markdown("")
                st.download_button("⬇️ Download Excel Tokopedia", data=buf.getvalue(), file_name=f"UMKM_Tokopedia_{datetime.date.today()}.xlsx")
        with tab3:
            audit = st.session_state.audit_tokped
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("📂 File Diproses", f"{audit.get('file_count', 0)}")
            col_b.metric("📥 Produk Ditemukan", f"{audit.get('valid', 0):,}".replace(",", "."))
            col_c.metric("ℹ️ Mode", "Deep Scanner")
            st.markdown("")
            st.info("⚙️ **Keterangan:** Mesin memindai kolom secara dinamis karena format file Tokopedia menyamping.")
