import streamlit as st
import pandas as pd
import re
import io
import requests
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os

# --- 1. CONFIG ---
st.set_page_config(page_title="BPS - Multi Platform UMKM", page_icon="🏛️", layout="wide")

# --- 2. CSS ---
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .banner-shopee { background: linear-gradient(90deg, #022a5e 0%, #0056b3 100%); padding: 25px; border-radius: 12px; color: white; margin-bottom: 20px;}
    .banner-tokped { background: linear-gradient(90deg, #064e3b 0%, #059669 100%); padding: 25px; border-radius: 12px; color: white; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
for key in ["data_shopee", "data_tokped", "audit_shopee", "audit_tokped"]:
    if key not in st.session_state: st.session_state[key] = None

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    halaman = st.radio("Pilih Platform:", ["🟠 Shopee", "🟢 Tokopedia"])
    st.divider()

# ==============================================================================
#                             HALAMAN SHOPEE
# ==============================================================================
if halaman == "🟠 Shopee":
    st.markdown('<div class="banner-shopee"><h1>Dashboard UMKM - Shopee</h1><p>BPS Prov. Kepulauan Bangka Belitung</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        files = st.file_uploader("Upload CSV Shopee", accept_multiple_files=True, key="shp")
        if st.button("🚀 Proses Shopee", type="primary"):
            if files:
                all_results = []
                total_rows = 0
                for file in files:
                    df = pd.read_csv(file, dtype=str, on_bad_lines='skip')
                    total_rows += len(df)
                    c_link = next((c for c in df.columns if 'href' in c.lower()), df.columns[0])
                    c_nama = next((c for c in df.columns if 'whitespace-normal' in c.lower()), df.columns[3])
                    c_harga = next((c for c in df.columns if 'font-medium 2' in c.lower()), df.columns[4])
                    c_loc = next((c for c in df.columns if 'ml-[3px]' in c.lower()), df.columns[7])
                    
                    for _, row in df.iterrows():
                        try:
                            h = int(re.sub(r"[^\d]", "", str(row[c_harga])))
                            all_results.append({
                                "Nama Toko": "Toko Shopee",
                                "Nama Produk": str(row[c_nama]),
                                "Harga": h,
                                "Wilayah": str(row[c_loc]).title(),
                                "Link": str(row[c_link])
                            })
                        except: continue
                st.session_state.data_shopee = pd.DataFrame(all_results)
                st.session_state.audit_shopee = {"total": total_rows, "valid": len(all_results)}
                st.success("Data Shopee Berhasil!")

    if st.session_state.data_shopee is not None:
        df = st.session_state.data_shopee
        f_wil = st.multiselect("Filter Wilayah:", options=sorted(df["Wilayah"].unique()), default=sorted(df["Wilayah"].unique()))
        df_f = df[df["Wilayah"].isin(f_wil)]
        t1, t2 = st.tabs(["📊 Dashboard", "🗄️ Database"])
        with t1:
            st.metric("Total Produk", len(df_f))
            st.plotly_chart(px.pie(df_f, names="Wilayah", hole=0.4), use_container_width=True)
        with t2:
            st.dataframe(df_f, use_container_width=True)

# ==============================================================================
#                             HALAMAN TOKOPEDIA
# ==============================================================================
elif halaman == "🟢 Tokopedia":
    st.markdown('<div class="banner-tokped"><h1>Dashboard UMKM - Tokopedia</h1><p>BPS Prov. Kepulauan Bangka Belitung</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        files = st.file_uploader("Upload CSV Tokopedia", accept_multiple_files=True, key="tkp")
        if st.button("🚀 Proses Tokopedia", type="primary"):
            if files:
                all_results = []
                total_in = 0
                for file in files:
                    df = pd.read_csv(file, dtype=str, on_bad_lines='skip')
                    total_in += len(df)
                    
                    # LOGIKA SCANNER TOTAL (Mencari di setiap kolom)
                    for _, row in df.iterrows():
                        links, names, prices, locs, shops = [], [], [], [], []
                        
                        for col in df.columns:
                            val = str(row[col])
                            if val == 'nan' or val == '': continue
                            
                            if 'tokopedia.com/' in val and 'extParam' in val: links.append(val)
                            elif 'Rp' in val: prices.append(val)
                            elif any(k in val for k in ['Pangkal', 'Bangka', 'Belitung', 'Jakarta', 'Bogor', 'Mojokerto', 'Tangerang', 'Bandung']):
                                if 'terjual' not in val.lower() and 'http' not in val: locs.append(val)
                            elif len(val) > 15 and ' ' in val and 'http' not in val and 'Rp' not in val: names.append(val)
                            elif len(val) <= 15 and not any(char.isdigit() for char in val): shops.append(val)

                        # Menyatukan data hasil scan
                        for k in range(len(links)):
                            try:
                                h_raw = prices[k] if k < len(prices) else "0"
                                h_fix = int(re.sub(r"[^\d]", "", h_raw))
                                if h_fix == 0: continue # Jangan masukkan yang harganya nol
                                
                                all_results.append({
                                    "Nama Toko": shops[k] if k < len(shops) else "Toko Tokopedia",
                                    "Nama Produk": names[k] if k < len(names) else "Produk Tokopedia",
                                    "Harga": h_fix,
                                    "Wilayah": locs[k].title() if k < len(locs) else "Tidak Terdeteksi",
                                    "Link": links[k]
                                })
                            except: continue
                
                st.session_state.data_tokped = pd.DataFrame(all_results).drop_duplicates()
                st.session_state.audit_tokped = {"total": total_in, "valid": len(st.session_state.data_tokped)}
                st.success(f"✅ Berhasil menarik {len(st.session_state.data_tokped)} produk Tokopedia!")

    if st.session_state.data_tokped is not None:
        df = st.session_state.data_tokped
        f_wil = st.multiselect("Filter Wilayah Tokopedia:", options=sorted(df["Wilayah"].unique()), default=sorted(df["Wilayah"].unique()))
        df_f = df[df["Wilayah"].isin(f_wil)]
        
        t1, t2, t3 = st.tabs(["📊 Dashboard Statistik", "🗄️ Database Siap Ekspor", "📑 Log Audit"])
        with t1:
            st.write("#### Ringkasan Data Tokopedia")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Produk", f"{len(df_f):,}".replace(",","."))
            c2.metric("Rerata Harga", f"Rp {df_f['Harga'].mean():,.0f}".replace(",","."))
            c3.metric("Titik Lokasi", df_f["Wilayah"].nunique())
            
            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1: st.plotly_chart(px.pie(df_f, names="Wilayah", hole=0.4, title="Sebaran Produk"), use_container_width=True)
                with g2: st.plotly_chart(px.bar(df_f.groupby("Wilayah").size().reset_index(name='Jml'), x="Wilayah", y="Jml", title="Volume per Wilayah"), use_container_width=True)
        
        with t2:
            st.write("#### 📋 Tabel Database")
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_view, use_container_width=True, hide_index=True)
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                df_f.to_excel(writer, index=False, sheet_name="Tokopedia")
            st.download_button("⬇️ Download Excel Tokopedia", data=buf.getvalue(), file_name=f"UMKM_Tokopedia_{datetime.date.today()}.xlsx", type="primary")

        with t3:
            audit = st.session_state.audit_tokped
            st.info(f"Sistem melakukan Deep Scanning pada file. Ditemukan {audit.get('valid',0)} produk valid dari baris yang diunggah.")
