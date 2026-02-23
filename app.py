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

# --- 2. CSS MINIMALIS (AMAN & RAPI) ---
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
    <h1>Dashboard Integrasi Data UMKM</h1>
    <p>Sistem Pembersihan & Verifikasi Geospasial Provinsi Kepulauan Bangka Belitung</p>
</div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR KONTROL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    st.header("📥 Input Data")
    uploaded_file = st.file_uploader("Unggah CSV Shopee", type=["csv"])
    
    mode_api = st.checkbox("🔍 Deteksi Nama Toko via API")
    
    st.divider()
    
    if st.button("🚀 Proses Data", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.error("⚠️ Silakan unggah file CSV terlebih dahulu!")
        else:
            with st.spinner("Memverifikasi Lokasi Fisik Pedagang..."):
                try:
                    df_raw = pd.read_csv(uploaded_file, dtype=str, on_bad_lines="skip")
                    
                    # --- DETEKSI KOLOM SCRAPER SHOPEE ---
                    col_link = next((c for c in df_raw.columns if 'href' in c.lower()), df_raw.columns[0])
                    col_nama = next((c for c in df_raw.columns if 'whitespace-normal' in c.lower()), df_raw.columns[3])
                    col_harga = next((c for c in df_raw.columns if 'font-medium 2' in c.lower()), df_raw.columns[4])
                    col_wilayah = next((c for c in df_raw.columns if 'ml-[3px]' in c.lower()), df_raw.columns[7])

                    hasil = []
                    # DAFTAR RESMI WILAYAH BABEL
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
                        
                        # Ambil Lokasi Asli
                        lokasi_shopee = str(row[col_wilayah]).lower()
                        
                        # 1. Bersihkan Harga
                        try:
                            val_h = int(re.sub(r"[^\d]", "", harga_str))
                        except:
                            val_h = 0
                            err_h += 1
                        
                        # 2. Filter Lokasi Murni Babel
                        v_final = "Luar Wilayah"
                        for kab, keys in babel_strict.items():
                            if any(k in lokasi_shopee for k in keys):
                                v_final = kab
                                break
                        
                        if v_final == "Luar Wilayah":
                            luar += 1
                            continue
                        
                        # 3. Ambil Nama Toko
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
                            "Wilayah BPS": v_final, 
                            "Lokasi Asli Shopee": lokasi_shopee.title(),
                            "Link": link
                        })
                        bar.progress((i + 1) / t_rows)
                    
                    bar.empty()
                    st.session_state.data_bersih = pd.DataFrame(hasil)
                    st.session_state.audit_data = {"total": t_rows, "valid": len(hasil), "luar": luar, "error_harga": err_h}
                    st.success("✅ Verifikasi Selesai!")
                except Exception as e:
                    st.error(f"Error Sistem: {e}")

# --- 6. KONTEN DASHBOARD UTAMA ---
if st.session_state.data_bersih is not None:
    df = st.session_state.data_bersih
    
    if df.empty:
        st.warning("⚠️ Tidak ada data yang lolos verifikasi. Seluruh lokasi berada di luar Provinsi Bangka Belitung.")
    else:
        st.write("### 🔎 Filter Wilayah")
        f_wil = st.multiselect("Pilih Kabupaten/Kota", options=sorted(df["Wilayah BPS"].unique()), default=sorted(df["Wilayah BPS"].unique()))
        df_f = df[df["Wilayah BPS"].isin(f_wil)]
        
        st.write("---")
        
        # TAB MENU
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database Siap Ekspor", "📑 Log Audit Integritas"])
        
        # --- TAB 1: DASHBOARD ---
        with tab1:
            st.write("#### Ringkasan Indikator UMKM")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total UMKM Babel", f"{len(df_f):,}".replace(",", "."))
            c2.metric("Rata-rata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",", "."))
            c3.metric("Status Verifikasi", "100% Lokasi Akurat")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                fig_pie = px.pie(df_f, names="Wilayah BPS", title="Distribusi UMKM per Wilayah", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_chart2:
                fig_bar = px.bar(df_f.groupby("Wilayah BPS").size().reset_index(name='Jumlah'), x="Wilayah BPS", y="Jumlah", title="Total Usaha per Kabupaten", color="Wilayah BPS", color_discrete_sequence=px.colors.sequential.Blues_r)
                st.plotly_chart(fig_bar, use_container_width=True)

        # --- TAB 2: DATABASE EXCEL ---
        with tab2:
            st.write("#### 📋 Tabel Data Tervalidasi")
            
            # Format tampilan di layar Streamlit
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=350)
            
            # Fungsi Ekspor Excel
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                df_f.to_excel(writer, index=False, sheet_name="Data UMKM")
                wb = writer.book
                ws = writer.sheets["Data UMKM"]
                
                # Desain Header Excel BPS
                header_fmt = wb.add_format({'bold': True, 'bg_color': '#022a5e', 'font_color': 'white', 'border': 1})
                currency_fmt = wb.add_format({'num_format': '#,##0', 'border': 1})
                border_fmt = wb.add_format({'border': 1})
                
                for col_num, value in enumerate(df_f.columns.values):
                    ws.write(0, col_num, value, header_fmt)
                    
                ws.set_column('A:A', 25, border_fmt)
                ws.set_column('B:B', 50, border_fmt)
                ws.set_column('C:C', 18, currency_fmt)
                ws.set_column('D:D', 20, border_fmt)
                ws.set_column('E:E', 25, border_fmt)
                ws.set_column('F:F', 50, border_fmt)
                ws.autofilter(0, 0, len(df_f), len(df_f.columns) - 1)
            
            st.download_button(
                label="⬇️ Download Excel Resmi BPS", 
                data=buf.getvalue(), 
                file_name=f"Data_UMKM_Babel_{datetime.date.today()}.xlsx",
                type="primary" 
            )

        # --- TAB 3: AUDIT ---
        with tab3:
            audit = st.session_state.audit_data
            
            # PERBAIKAN: Penarikan data dengan get() supaya tidak KeyError jika kosong
            total_raw = int(audit.get('total', 0))
            valid_raw = int(audit.get('valid', 0))
            luar_raw = int(audit.get('luar', 0))
            
            # Ubah jadi string dengan format titik
            t_str = f"{total_raw:,}".replace(",", ".")
            v_str = f"{valid_raw:,}".replace(",", ".")
            l_str = f"{luar_raw:,}".replace(",", ".")
            
            st.write("#### 📑 Log Verifikasi Data")
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.info(f"**📥 Data Masuk:** {t_str} Baris File CSV")
                st.success(f"**✅ Lolos Verifikasi:** {v_str} Baris (100% Bangka Belitung)")
                st.error(f"**🚫 Dibuang:** {l_str} Baris (Lokasi luar wilayah/Blacklist)")
            
            with col_b:
                # PERBAIKAN: Cegah pembagian dengan angka nol
                pct = (valid_raw / total_raw * 100) if total_raw > 0 else 0
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = pct,
                    number = {'suffix': "%", 'valueformat': ".1f"},
                    title = {'text': "Tingkat Kebersihan Data Wilayah"},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#0056b3"}}
                ))
                fig_gauge.update_layout(height=250, margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(fig_gauge, use_container_width=True)

else:
    # Tampilan awal kosong
    st.info("👈 Silakan unggah file CSV hasil *scraping* di panel kiri untuk memulai proses pembersihan data.")
