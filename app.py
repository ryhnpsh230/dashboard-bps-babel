import streamlit as st
import pandas as pd
import re
import io
import requests
import datetime
import os
import time

import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# ======================================================================================
# CONFIG
# ======================================================================================
APP_TITLE = "Dashboard UMKM BPS"
APP_ICON = "🏛️"

BPS_OREN_UTAMA = "#F55F00"
BPS_AMBER = "#FFB347"
BPS_DARK = "#1A0A00"
BPS_PAPER = "rgba(0,0,0,0)"
BPS_PALETTE = ["#F55F00", "#FF8C42", "#FFB347", "#FFCF82", "#C94A00", "#7A2D00", "#FF6B2B"]

BABEL_KEYS = [
    "pangkal", "bangka", "belitung", "sungailiat", "mentok", "muntok",
    "koba", "toboali", "manggar", "tanjung pandan", "tanjungpandan"
]

PLACEHOLDER = "Pemilik tidak mencantumkan"
PHONE_EMPTY = "Pemilik belum meletakkan nomor"

# ======================================================================================
# PAGE SETUP
# ======================================================================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = BPS_PALETTE

# ======================================================================================
# MASTER CSS — Premium Orange/White + Sidebar + Topbar + Cards
# ======================================================================================
MASTER_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

:root{
  --sun:#F55F00;
  --sun2:#FF8C42;
  --sun3:#FFB347;
  --cream:#FFF9F4;
  --paper:#FFFFFF;
  --ink:#1A0800;
  --ink2:#4A2800;
  --ink3:#7A5040;
  --border:rgba(245,95,0,0.12);
  --border2:rgba(245,95,0,0.24);
  --shadow:0 4px 24px rgba(245,95,0,0.08), 0 1px 4px rgba(0,0,0,0.04);
  --shadow2:0 12px 48px rgba(245,95,0,0.14), 0 2px 8px rgba(0,0,0,0.06);
  --shadow3:0 24px 80px rgba(245,95,0,0.18), 0 4px 16px rgba(0,0,0,0.08);
  --r-sm:10px;
  --r-md:16px;
  --r-lg:22px;
  --r-xl:30px;
}

*,*::before,*::after{ box-sizing:border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"]{
  font-family:'DM Sans', system-ui, sans-serif;
  background:
    radial-gradient(ellipse 1400px 900px at 5% -5%, rgba(245,95,0,0.08) 0%, transparent 60%),
    radial-gradient(ellipse 1000px 700px at 98% 5%, rgba(255,179,71,0.07) 0%, transparent 55%),
    radial-gradient(ellipse 800px 600px at 50% 110%, rgba(245,95,0,0.05) 0%, transparent 60%),
    linear-gradient(175deg, #FFFFFF 0%, #FFF9F4 45%, #FFF5EC 100%) !important;
  background-attachment:fixed !important;
  color:var(--ink) !important;
}

[data-testid="stHeader"]{ background:transparent !important; }
section.main, .main, .block-container{ background:transparent !important; }

.block-container{
  max-width:1200px;
  padding-top:0.6rem !important;
  padding-bottom:3rem !important;
}

.block-container::before{
  content:"";
  display:block;
  height:3px;
  width:100%;
  margin-bottom:18px;
  border-radius:999px;
  background:linear-gradient(90deg, transparent 0%, var(--sun) 20%, var(--sun3) 50%, var(--sun) 80%, transparent 100%);
  opacity:0.55;
}

/* Typography */
h1,h2,h3,h4,h5{
  font-family:'Sora', sans-serif !important;
  letter-spacing:-0.025em;
  color:var(--ink) !important;
}
h1{ font-weight:800 !important; }
h2,h3{ font-weight:700 !important; }
p,li,label{ color:var(--ink2) !important; }

/* Scrollbar */
::-webkit-scrollbar{ width:8px; height:8px; }
::-webkit-scrollbar-track{ background:var(--cream); }
::-webkit-scrollbar-thumb{
  background:rgba(245,95,0,0.22);
  border-radius:999px;
  border:2px solid var(--cream);
}
::-webkit-scrollbar-thumb:hover{ background:rgba(245,95,0,0.38); }

/* Card container styling */
div[data-testid="stVerticalBlockBorderWrapper"]{
  background:rgba(255,255,255,0.86) !important;
  border:1px solid var(--border) !important;
  border-radius:var(--r-lg) !important;
  box-shadow:var(--shadow) !important;
  backdrop-filter: blur(12px) !important;
  transition: box-shadow .22s ease, border-color .22s ease, transform .18s ease !important;
  padding:18px 20px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover{
  border-color:var(--border2) !important;
  box-shadow:var(--shadow2) !important;
  transform: translateY(-1px) !important;
}

/* Section Header */
.bps-section{ margin:8px 0 18px 0; }
.sec-left{ display:flex; flex-direction:column; gap:6px; }
.sec-badge{
  display:inline-flex;
  align-items:center;
  gap:8px;
  font-family:'Sora',sans-serif;
  font-size:.72rem;
  font-weight:800;
  letter-spacing:.18em;
  text-transform:uppercase;
  color:var(--sun);
}
.sec-badge::before{
  content:"";
  width:8px; height:8px;
  border-radius:50%;
  background:linear-gradient(135deg,var(--sun),var(--sun3));
  box-shadow:0 0 0 3px rgba(245,95,0,0.15);
}
.sec-title{
  font-size:1.65rem !important;
  font-weight:800 !important;
  margin:0 !important;
}
.sec-sub{ color:var(--ink3) !important; font-size:.95rem; margin:0 !important; }
.sec-rule{
  height:2px; margin-top:10px; width:100%;
  background:linear-gradient(90deg,var(--sun),var(--sun3),transparent);
  border-radius:999px; opacity:.35;
}

/* Topbar */
.topbar{
  position:relative;
  border-radius:var(--r-xl);
  padding:14px 18px;
  margin:0 0 16px 0;
  background:linear-gradient(135deg, rgba(255,255,255,0.90) 0%, rgba(255,249,244,0.90) 100%);
  border:1px solid var(--border);
  box-shadow:var(--shadow);
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
}
.top-left{
  display:flex; align-items:center; gap:12px;
}
.top-logo{
  width:40px; height:40px;
  border-radius:14px;
  background:linear-gradient(135deg,var(--sun) 0%, var(--sun3) 100%);
  box-shadow:0 10px 28px rgba(245,95,0,0.22);
  display:flex; align-items:center; justify-content:center;
  font-size:1.25rem;
}
.top-title{
  font-family:'Sora',sans-serif;
  font-weight:900;
  letter-spacing:-0.02em;
  line-height:1.1;
  color:var(--ink);
}
.top-sub{
  font-size:.82rem;
  color:var(--ink3);
  margin-top:2px;
}
.breadcrumb{
  font-size:.82rem;
  color:rgba(74,40,0,.70);
}
.kbd{
  display:inline-flex;
  align-items:center;
  padding:3px 8px;
  border-radius:10px;
  border:1px solid rgba(245,95,0,.18);
  background:rgba(255,255,255,.75);
  font-size:.78rem;
  color:rgba(74,40,0,.72);
}

/* Banner + Hero */
.bps-banner{
  position:relative; overflow:hidden;
  border-radius:var(--r-xl);
  padding:24px 28px;
  margin:0 0 18px 0;
  background:linear-gradient(135deg,#FFFFFF 0%, var(--cream) 100%);
  border:1px solid var(--border2);
  box-shadow:var(--shadow2);
}
.bps-banner::before{
  content:"";
  position:absolute; top:-60px; right:-80px;
  width:320px; height:320px; border-radius:50%;
  background:radial-gradient(circle, rgba(245,95,0,0.12), transparent 70%);
}
.bps-kicker{
  font-family:'Sora',sans-serif;
  font-size:.73rem; font-weight:800;
  letter-spacing:.16em; text-transform:uppercase;
  color:var(--sun); margin-bottom:8px;
  position:relative; z-index:1;
}
.bps-title{
  font-family:'Sora',sans-serif;
  font-size:1.85rem; font-weight:900;
  margin:0 0 6px 0;
  position:relative; z-index:1;
}
.bps-subtitle{
  color:var(--ink3);
  font-size:1rem;
  margin:0;
  position:relative; z-index:1;
}

.bps-hero{
  position:relative; overflow:hidden;
  border-radius:var(--r-xl);
  padding:30px 34px;
  margin-bottom:18px;
  background:linear-gradient(135deg,var(--sun) 0%, var(--sun2) 45%, var(--sun3) 100%);
  box-shadow:var(--shadow3);
}
.bps-hero::before{
  content:""; position:absolute; top:-80px; right:-100px;
  width:420px; height:420px; border-radius:50%;
  background:rgba(255,255,255,0.10);
}
.bps-hero h1{
  font-size:2.15rem !important;
  font-weight:900 !important;
  color:#fff !important;
  margin:0 0 10px 0 !important;
  position:relative; z-index:1;
}
.bps-hero p{
  color:rgba(255,255,255,0.86) !important;
  font-size:1.05rem;
  line-height:1.6;
  margin:0;
  position:relative; z-index:1;
}
.bps-badge{
  display:inline-flex; align-items:center; gap:6px;
  font-family:'Sora',sans-serif;
  font-size:.70rem; font-weight:800;
  letter-spacing:.18em; text-transform:uppercase;
  color:rgba(255,255,255,0.88);
  background:rgba(255,255,255,0.16);
  border:1px solid rgba(255,255,255,0.26);
  border-radius:999px;
  padding:5px 12px;
  margin-bottom:14px;
  position:relative; z-index:1;
}
.cta-row{ display:flex; gap:10px; flex-wrap:wrap; margin-top:18px; position:relative; z-index:1; }
.bps-chip{
  display:inline-flex; align-items:center; gap:7px;
  padding:8px 16px; border-radius:999px;
  background:rgba(255,255,255,0.18);
  border:1px solid rgba(255,255,255,0.30);
  color:#fff; font-weight:700;
  font-size:.88rem;
  backdrop-filter: blur(8px);
  transition: background .18s ease;
}
.bps-chip:hover{ background:rgba(255,255,255,0.28); }

/* Metrics */
div[data-testid="metric-container"]{
  background:linear-gradient(135deg,#FFFFFF 0%, var(--cream) 100%) !important;
  border:1px solid var(--border) !important;
  border-top:3px solid var(--sun) !important;
  border-radius:var(--r-md) !important;
  padding:16px 18px !important;
  box-shadow:var(--shadow) !important;
  transition: transform .18s ease, box-shadow .18s ease !important;
}
div[data-testid="metric-container"]:hover{
  transform: translateY(-2px) !important;
  box-shadow:var(--shadow2) !important;
}
div[data-testid="metric-container"] label{
  color:var(--ink3) !important;
  font-weight:700 !important;
  font-size:.82rem !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"]{
  font-family:'Sora',sans-serif !important;
  font-weight:900 !important;
  color:var(--ink) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
  gap:6px;
  background:var(--cream);
  border:1px solid var(--border);
  border-radius:var(--r-md);
  padding:8px;
}
.stTabs [data-baseweb="tab"]{
  height:42px;
  padding:0 20px;
  border-radius:10px;
  background:transparent;
  color:var(--ink3) !important;
  font-family:'Sora',sans-serif;
  font-weight:700;
  font-size:.88rem;
  transition: background .16s ease, color .16s ease;
}
.stTabs [data-baseweb="tab"]:hover{
  background:rgba(245,95,0,0.07);
  color:var(--sun) !important;
}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,var(--sun) 0%, var(--sun2) 100%) !important;
  color:#fff !important;
  font-weight:900 !important;
  box-shadow:0 6px 20px rgba(245,95,0,0.30) !important;
}
.stTabs [data-baseweb="tab-highlight"]{ display:none !important; }

/* Buttons */
.stButton > button,
div[data-testid="stDownloadButton"] button{
  font-family:'Sora',sans-serif !important;
  font-weight:800 !important;
  font-size:.90rem !important;
  border-radius:var(--r-md) !important;
  height:46px !important;
  transition: transform .16s ease, box-shadow .16s ease, filter .16s ease !important;
}
.stButton > button[kind="primary"],
div[data-testid="stDownloadButton"] button{
  background:linear-gradient(135deg,var(--sun) 0%, var(--sun2) 100%) !important;
  color:#fff !important;
  border:none !important;
  box-shadow:0 6px 20px rgba(245,95,0,0.32) !important;
}
.stButton > button[kind="primary"]:hover,
div[data-testid="stDownloadButton"] button:hover{
  transform: translateY(-1px) !important;
  box-shadow:0 12px 32px rgba(245,95,0,0.38) !important;
  filter: brightness(1.04) !important;
}
.stButton > button[kind="secondary"]{
  background:#fff !important;
  color:var(--sun) !important;
  border:1.5px solid var(--border2) !important;
  box-shadow:var(--shadow) !important;
}
.stButton > button[kind="secondary"]:hover{
  background:var(--cream) !important;
  border-color:var(--sun) !important;
  transform: translateY(-1px) !important;
}

/* Inputs */
div[data-baseweb="input"]{
  background:#fff !important;
  border-radius:var(--r-sm) !important;
  border:1.5px solid var(--border) !important;
  transition: border-color .16s ease, box-shadow .16s ease !important;
}
div[data-baseweb="input"]:focus-within{
  border-color:var(--sun) !important;
  box-shadow:0 0 0 3px rgba(245,95,0,0.12) !important;
}
div[data-baseweb="select"] > div{
  background:#fff !important;
  border:1.5px solid var(--border) !important;
  border-radius:var(--r-sm) !important;
}
div[data-baseweb="select"]:focus-within > div{
  border-color:var(--sun) !important;
  box-shadow:0 0 0 3px rgba(245,95,0,0.12) !important;
}
input, textarea{ color:var(--ink) !important; font-family:'DM Sans',sans-serif !important; }

/* DataFrame */
[data-testid="stDataFrame"]{
  border-radius:var(--r-md) !important;
  overflow:hidden !important;
  border:1px solid var(--border) !important;
  box-shadow:var(--shadow) !important;
}

/* Expanders */
details{
  background:#fff;
  border:1px solid var(--border);
  border-radius:var(--r-md);
  padding:4px 12px;
}
details summary{
  font-family:'Sora',sans-serif;
  font-weight:800;
  color:var(--ink);
}
details[open]{ box-shadow:var(--shadow); }

/* Alerts */
div[data-testid="stAlert"]{ border-radius:var(--r-md) !important; border-left-width:4px !important; }

/* Sidebar */
[data-testid="stSidebar"]{
  background:
    radial-gradient(ellipse 520px 420px at 10% 0%, rgba(245,95,0,0.09) 0%, transparent 65%),
    radial-gradient(ellipse 420px 320px at 90% 100%, rgba(255,179,71,0.07) 0%, transparent 60%),
    linear-gradient(180deg, #FFFFFF 0%, #FFF9F4 60%, #FFF5EC 100%) !important;
  border-right:1px solid rgba(245,95,0,0.13) !important;
  box-shadow:6px 0 32px rgba(245,95,0,0.07), 2px 0 8px rgba(0,0,0,0.03) !important;
}
[data-testid="stSidebar"] *{ color:var(--ink) !important; }
[data-testid="stSidebar"] .stMarkdown p{ color:var(--ink3) !important; font-size:0.88rem !important; }
[data-testid="stSidebar"] hr{
  border:none !important;
  border-top:1px solid rgba(245,95,0,0.12) !important;
  margin:8px 0 !important;
}
.sb-brand{ display:flex; align-items:center; gap:12px; padding:4px 0 16px 0; }
.sb-brand-icon{
  width:46px; height:46px; border-radius:14px;
  background:linear-gradient(135deg,var(--sun) 0%, var(--sun3) 100%);
  font-size:1.45rem; line-height:46px; text-align:center;
  box-shadow:0 8px 24px rgba(245,95,0,0.32);
  flex-shrink:0;
}
.sb-brand-name{
  font-family:'Sora',sans-serif !important;
  font-size:1.05rem; font-weight:900;
  color:var(--ink) !important;
  letter-spacing:-0.015em;
  line-height:1.25;
}
.sb-brand-sub{ font-size:0.73rem; font-weight:600; color:var(--ink3) !important; margin-top:1px; }
.sb-nav-label{
  font-family:'Sora',sans-serif;
  font-size:0.67rem; font-weight:900;
  letter-spacing:0.16em;
  text-transform:uppercase;
  color:rgba(245,95,0,0.60) !important;
  padding:8px 2px 5px 2px;
}

/* Radio nav items */
[data-testid="stSidebar"] div[role="radiogroup"]{
  gap:6px !important; display:flex !important; flex-direction:column !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label{
  border-radius:14px !important;
  border:1.5px solid rgba(245,95,0,0.10) !important;
  background:rgba(255,255,255,0.84) !important;
  padding:14px 16px !important;
  cursor:pointer !important;
  transition: all .22s cubic-bezier(.34,1.56,.64,1) !important;
  box-shadow:0 2px 8px rgba(245,95,0,0.05), 0 1px 3px rgba(0,0,0,0.04) !important;
  overflow:hidden !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover{
  border-color:rgba(245,95,0,0.30) !important;
  background:#fff !important;
  box-shadow:0 6px 22px rgba(245,95,0,0.12), 0 2px 6px rgba(0,0,0,0.05) !important;
  transform: translateX(5px) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){
  background:linear-gradient(135deg,var(--sun) 0%, var(--sun2) 100%) !important;
  border-color:transparent !important;
  box-shadow:0 8px 28px rgba(245,95,0,0.34), 0 2px 8px rgba(0,0,0,0.08) !important;
  transform: translateX(5px) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span{
  color:#fff !important; font-weight:900 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"]{ display:none !important; }

/* Sidebar action button */
[data-testid="stSidebar"] .stButton > button{
  border-radius:12px !important;
  background:rgba(245,95,0,0.07) !important;
  border:1.5px solid rgba(245,95,0,0.20) !important;
  color:var(--sun) !important;
  font-weight:900 !important;
  font-size:0.88rem !important;
  height:42px !important;
  box-shadow:none !important;
}
[data-testid="stSidebar"] .stButton > button:hover{
  background:rgba(245,95,0,0.13) !important;
  border-color:var(--sun) !important;
  box-shadow:0 4px 14px rgba(245,95,0,0.16) !important;
}

/* Stat chips */
.sb-stat-grid{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:2px 0 4px 0; }
.sb-stat{
  border-radius:12px; padding:10px 12px;
  background:rgba(255,255,255,0.88);
  border:1px solid rgba(245,95,0,0.10);
  box-shadow:0 2px 8px rgba(245,95,0,0.04);
}
.sb-stat-val{
  font-family:'Sora',sans-serif;
  font-size:1.18rem;
  font-weight:900;
  color:var(--sun) !important;
  line-height:1.1;
}
.sb-stat-lbl{ font-size:0.70rem; font-weight:800; color:var(--ink3) !important; margin-top:2px; }

/* Sidebar footer */
.sb-footer{
  margin-top:10px;
  padding:12px 14px;
  border-radius:14px;
  background:linear-gradient(135deg, rgba(245,95,0,0.06), rgba(255,179,71,0.04));
  border:1px solid rgba(245,95,0,0.10);
  font-size:0.77rem;
  color:var(--ink3) !important;
  line-height:1.6;
  text-align:center;
}
.sb-footer strong{ color:var(--sun) !important; font-weight:900; }

/* Splash screen */
.splash-wrap{
  position:relative; overflow:hidden;
  border-radius:var(--r-xl);
  padding:40px 44px;
  max-width:780px;
  margin:8vh auto 0 auto;
  background:linear-gradient(135deg,var(--sun) 0%, var(--sun2) 45%, var(--sun3) 100%);
  box-shadow:0 32px 100px rgba(245,95,0,0.30), 0 4px 16px rgba(0,0,0,0.08);
}
.splash-wrap::before{
  content:""; position:absolute; top:-100px; right:-120px;
  width:500px; height:500px; border-radius:50%;
  background:rgba(255,255,255,0.10);
}
.splash-kicker{
  font-family:'Sora',sans-serif;
  font-size:.73rem; font-weight:900;
  letter-spacing:.18em; text-transform:uppercase;
  color:rgba(255,255,255,0.86);
  margin-bottom:12px;
  position:relative; z-index:1;
}
.splash-title{
  font-family:'Sora',sans-serif;
  font-size:2.35rem;
  font-weight:900;
  color:#fff;
  margin:0 0 12px 0;
  letter-spacing:-0.03em;
  position:relative; z-index:1;
}
.splash-sub{
  color:rgba(255,255,255,0.82);
  font-size:1.05rem;
  line-height:1.6;
  margin:0 0 20px 0;
  position:relative; z-index:1;
}
.splash-row{ display:flex; gap:10px; flex-wrap:wrap; position:relative; z-index:1; }
.splash-pill{
  padding:8px 18px;
  border-radius:999px;
  background:rgba(255,255,255,0.18);
  border:1px solid rgba(255,255,255,0.30);
  color:#fff;
  font-weight:800;
  font-size:0.88rem;
}

/* Pills */
.dash-pill{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:10px 16px;
  border-radius:999px;
  margin:6px 8px 0 0;
  font-weight:800;
  font-size:0.90rem;
  border:1.5px solid var(--border);
  background:#fff;
  color:var(--ink2);
  box-shadow:var(--shadow);
}
.dash-pill.ok{
  border-color:var(--sun);
  background:linear-gradient(135deg, rgba(245,95,0,0.07), rgba(255,140,66,0.04));
  color:var(--sun);
}

/* Progress bar */
[data-testid="stProgress"] > div > div > div{
  background:linear-gradient(90deg,var(--sun),var(--sun3)) !important;
  border-radius:999px !important;
}

/* Toast */
[data-testid="stToast"]{
  border-radius:var(--r-md) !important;
  border-left:4px solid var(--sun) !important;
}

a{ color:var(--sun) !important; }
a:hover{ color:var(--sun2) !important; }
"""
st.markdown(f"<style>{MASTER_CSS}</style>", unsafe_allow_html=True)

# ======================================================================================
# UI HELPERS
# ======================================================================================
def section_header(title: str, subtitle: str = "", badge: str = "MODULE"):
    st.markdown(
        f"""
<div class="bps-section">
  <div class="sec-left">
    <div class="sec-badge">{badge}</div>
    <h2 class="sec-title">{title}</h2>
    {f'<p class="sec-sub">{subtitle}</p>' if subtitle else ''}
    <div class="sec-rule"></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

def banner(title: str, subtitle: str):
    st.markdown(
        f"""
<div class="bps-banner">
  <div class="bps-kicker">🏛️ BADAN PUSAT STATISTIK</div>
  <div class="bps-title">{title}</div>
  <p class="bps-subtitle">{subtitle}</p>
</div>
""",
        unsafe_allow_html=True,
    )

def topbar(current_page: str, show_sidebar: bool):
    st.markdown(
        f"""
<div class="topbar">
  <div class="top-left">
    <div class="top-logo">🏛️</div>
    <div>
      <div class="top-title">{APP_TITLE}</div>
      <div class="top-sub">BPS Bangka Belitung • Toolkit Analisis UMKM</div>
    </div>
  </div>
  <div style="display:flex; align-items:center; gap:10px;">
    <div class="breadcrumb">📍 <b>{current_page}</b></div>
    <span class="kbd">Sidebar: {"ON" if show_sidebar else "OFF"}</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

def goto_menu(label: str):
    st.session_state["nav_target"] = label
    st.session_state["show_sidebar"] = True
    st.rerun()

def hide_sidebar_css():
    st.markdown(
        "<style>[data-testid='stSidebar']{display:none !important;} section.main{margin-left:0 !important;}</style>",
        unsafe_allow_html=True,
    )

# ======================================================================================
# SESSION STATE
# ======================================================================================
def ensure_state():
    defaults = {
        "data_shopee": None, "audit_shopee": {},
        "data_tokped": None, "audit_tokped": {},
        "data_maps": None,   "audit_maps": {},
        "show_sidebar": False,
        "menu_nav": "🏠 Dashboard",
        "nav_target": None,
        "__boot__": False,
        "__splash_done__": False,
        "show_tips": True,
        "fast_mode": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ensure_state()

# ======================================================================================
# DATA HELPERS
# ======================================================================================
def fmt_int_id(n) -> str:
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return "0"

def safe_title(x: str) -> str:
    if x is None:
        return ""
    s = str(x).strip()
    return s[:1].upper() + s[1:] if s else s

def _to_str(x):
    if pd.isna(x):
        return ""
    return str(x)

def clean_placeholder_to_empty(x) -> str:
    s = _to_str(x).strip()
    if not s:
        return ""
    if s.lower() == PLACEHOLDER.lower():
        return ""
    if s.lower() in ["nan", "none", "null"]:
        return ""
    return re.sub(r"\s+", " ", s).strip()

def normalize_phone_id(x) -> str:
    s = clean_placeholder_to_empty(x)
    if not s:
        return ""
    s = s.replace(PHONE_EMPTY, "").strip()
    if not s:
        return ""
    s2 = re.sub(r"[^\d+]", "", s)
    if s2.startswith("08"):
        s2 = "+62" + s2[1:]
    if re.fullmatch(r"62\d{7,15}", s2):
        s2 = "+" + s2
    if s2.startswith("+") and re.fullmatch(r"\+\d{8,16}", s2):
        return s2
    digits = re.sub(r"\D", "", s2)
    if digits.startswith("0") and len(digits) >= 9:
        return "+62" + digits[1:]
    if digits.startswith("62") and len(digits) >= 9:
        return "+" + digits
    return s2

def normalize_url(x) -> str:
    s = clean_placeholder_to_empty(x)
    if not s:
        return ""
    s = s.strip()
    if s.startswith(("http://", "https://")):
        return s
    if s.startswith("www."):
        return "https://" + s
    if s.startswith("wa.me/"):
        return "https://" + s
    if s.startswith("instagram.com/"):
        return "https://" + s
    if s.startswith("@") and len(s) > 1:
        return "https://instagram.com/" + s[1:]
    return ""

def to_float_safe(x):
    s = clean_placeholder_to_empty(x)
    if not s:
        return None
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def is_in_babel(wilayah: str) -> bool:
    s = (wilayah or "").lower()
    return any(k in s for k in BABEL_KEYS)

def deteksi_tipe_usaha(nama_toko):
    if pd.isna(nama_toko) or nama_toko in ["Tidak Dilacak", "Toko CSV", "Anonim", ""]:
        return "Tidak Terdeteksi (Butuh Nama Toko)"
    if str(nama_toko) == "FB Seller":
        return "Perorangan"
    nama_lower = str(nama_toko).lower()
    keyword_fisik = [
        "toko", "warung", "grosir", "mart", "apotek", "cv.", "pt.", "official", "agen",
        "distributor", "kios", "kedai", "supermarket", "minimarket", "cabang", "jaya",
        "abadi", "makmur", "motor", "mobil", "bengkel", "snack", "store", "jajanan"
    ]
    for kata in keyword_fisik:
        if kata in nama_lower:
            return "Ada Toko Fisik"
    return "Murni Online (Rumahan)"

def clean_maps_dataframe(df_raw):
    audit = {
        "rows_in": 0, "rows_out": 0, "missing_cols": [],
        "dedup_removed": 0, "invalid_coord": 0, "invalid_link": 0, "empty_name": 0,
    }
    out_cols = ["Foto URL", "Nama Usaha", "Alamat", "No Telepon", "Latitude", "Longitude", "Link"]
    if df_raw is None or df_raw.empty:
        return pd.DataFrame(columns=out_cols), audit

    audit["rows_in"] = len(df_raw)

    colmap_candidates = {
        "foto_url": ["foto_url", "foto", "photo", "gambar", "image"],
        "nama_usaha": ["nama_usaha", "nama usaha", "nama", "name"],
        "alamat": ["alamat", "address"],
        "no_telepon": ["no_telepon", "telepon", "phone", "no telp", "nomor"],
        "latitude": ["latitude", "lat"],
        "longitude": ["longitude", "lng", "lon", "long"],
        "link": ["link", "website", "url", "wa", "ig"],
    }

    cols_lower = {c.lower(): c for c in df_raw.columns}
    found = {}
    for k, cands in colmap_candidates.items():
        real = None
        for cc in cands:
            if cc.lower() in cols_lower:
                real = cols_lower[cc.lower()]
                break
        if real is None:
            audit["missing_cols"].append(k)
        found[k] = real

    df = pd.DataFrame()
    for k, real in found.items():
        df[k] = "" if real is None else df_raw[real].astype(str)

    df["foto_url"] = df["foto_url"].apply(clean_placeholder_to_empty)
    df["nama_usaha"] = df["nama_usaha"].apply(clean_placeholder_to_empty)
    df["alamat"] = df["alamat"].apply(clean_placeholder_to_empty)
    df["no_telepon"] = df["no_telepon"].apply(normalize_phone_id)
    df["link"] = df["link"].apply(normalize_url)

    df["latitude_f"] = df["latitude"].apply(to_float_safe)
    df["longitude_f"] = df["longitude"].apply(to_float_safe)

    invalid_coord = df["latitude_f"].isna() | df["longitude_f"].isna()
    audit["invalid_coord"] = int(invalid_coord.sum())

    df["latitude"] = df["latitude_f"]
    df["longitude"] = df["longitude_f"]
    df.drop(columns=["latitude_f", "longitude_f"], inplace=True)

    audit["invalid_link"] = int((df["link"] == "").sum())
    audit["empty_name"] = int((df["nama_usaha"] == "").sum())

    def _key(r):
        name = (r["nama_usaha"] or "").lower()
        addr = (r["alamat"] or "").lower()
        lat = "" if pd.isna(r["latitude"]) else f"{r['latitude']:.6f}"
        lng = "" if pd.isna(r["longitude"]) else f"{r['longitude']:.6f}"
        return f"{name}__{addr}__{lat}__{lng}"

    before = len(df)
    df["_k"] = df.apply(_key, axis=1)
    df = df[df["_k"].str.strip() != "__"]
    df = df.drop_duplicates(subset=["_k"], keep="first").drop(columns=["_k"])
    after = len(df)
    audit["dedup_removed"] = int(before - after)

    df_out = pd.DataFrame({
        "Foto URL": df["foto_url"].fillna(""),
        "Nama Usaha": df["nama_usaha"].fillna(""),
        "Alamat": df["alamat"].fillna(""),
        "No Telepon": df["no_telepon"].fillna(""),
        "Latitude": df["latitude"],
        "Longitude": df["longitude"],
        "Link": df["link"].fillna(""),
    })
    audit["rows_out"] = len(df_out)
    return df_out, audit

def df_to_excel_bytes(sheets: dict) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        wb = writer.book
        header_fmt = wb.add_format({"bold": True, "bg_color": BPS_OREN_UTAMA, "font_color": "white"})
        currency_fmt = wb.add_format({"num_format": "#,##0"})
        float_fmt = wb.add_format({"num_format": "0.000000"})

        for sheet_name, df in sheets.items():
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            ws = writer.sheets[sheet_name]

            for col_num, value in enumerate(df.columns.values):
                ws.write(0, col_num, value, header_fmt)

            if len(df) > 0:
                ws.autofilter(0, 0, len(df), len(df.columns) - 1)

            for i, col in enumerate(df.columns):
                sample = df[col].astype(str).head(200).values
                max_len = max([len(str(col))] + [len(x) for x in sample]) if len(sample) else len(str(col))
                width = min(max(12, max_len + 2), 60)
                ws.set_column(i, i, width)

            for i, col in enumerate(df.columns):
                if col.lower() == "harga":
                    ws.set_column(i, i, 18, currency_fmt)
                if col.lower() in ["latitude", "longitude"]:
                    ws.set_column(i, i, 14, float_fmt)

    return buf.getvalue()

def read_csv_files(files):
    dfs = []
    total = 0
    for f in files:
        df = pd.read_csv(f, dtype=str, on_bad_lines="skip")
        total += len(df)
        dfs.append(df)
    if not dfs:
        return pd.DataFrame(), 0
    return pd.concat(dfs, ignore_index=True), total

# ======================================================================================
# MAP RENDER
# ======================================================================================
def render_real_map_folium(df_maps, height: int = 560):
    df_plot = df_maps.dropna(subset=["Latitude", "Longitude"]).copy()
    df_plot = df_plot[(df_plot["Latitude"].between(-90, 90)) & (df_plot["Longitude"].between(-180, 180))].copy()
    if df_plot.empty:
        st.info("Tidak ada koordinat valid untuk ditampilkan.")
        return

    tile_choice = st.selectbox(
        "🗺️ Provider Peta",
        ["CartoDB Positron", "CartoDB DarkMatter", "OpenStreetMap"],
        index=0,
        key="maps_tile_provider",
    )
    tiles_map = {
        "OpenStreetMap": "OpenStreetMap",
        "CartoDB Positron": "CartoDB positron",
        "CartoDB DarkMatter": "CartoDB dark_matter",
    }

    center_lat = float(df_plot["Latitude"].mean())
    center_lon = float(df_plot["Longitude"].mean())

    try:
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles=tiles_map.get(tile_choice, "CartoDB positron"),
            control_scale=True,
        )
        cluster = MarkerCluster(name="UMKM").add_to(m)

        def safe_html(s):
            return "" if s is None else str(s).replace("<", "&lt;").replace(">", "&gt;")

        for _, r in df_plot.iterrows():
            nama = safe_html(r.get("Nama Usaha", ""))
            alamat = safe_html(r.get("Alamat", ""))
            telp = safe_html(r.get("No Telepon", ""))
            link = safe_html(r.get("Link", ""))

            link_html = f'<a href="{link}" target="_blank" style="color:#F55F00; font-weight:700;">Buka Link →</a>' if link else "-"

            popup = f"""
            <div style="width:260px; font-family:'DM Sans',sans-serif;">
              <div style="font-weight:800; font-size:14px; color:#1A0800; margin-bottom:6px;">{nama}</div>
              <div style="font-size:12px; color:#7A5040;">{alamat}</div>
              <hr style="border:none;border-top:1px solid rgba(245,95,0,0.15); margin:8px 0;">
              <div style="font-size:12px; color:#4A2800;">☎️ {telp if telp else "-"}</div>
              <div style="font-size:12px; margin-top:4px;">{link_html}</div>
            </div>
            """
            folium.CircleMarker(
                location=[float(r["Latitude"]), float(r["Longitude"])],
                radius=7, weight=2,
                color="#F55F00", fill=True,
                fill_color="#FF8C42", fill_opacity=0.85,
                popup=folium.Popup(popup, max_width=320),
            ).add_to(cluster)

        folium.LayerControl(collapsed=True).add_to(m)
        st_folium(m, width=None, height=height)
        st.caption("Jika peta tidak tampil, coba ganti Provider Peta.")
        return

    except Exception:
        st.warning("Provider tile tidak tersedia. Menampilkan peta fallback.")
        fig = px.scatter_geo(
            df_plot, lat="Latitude", lon="Longitude",
            hover_name="Nama Usaha",
            hover_data={"Alamat": True, "No Telepon": True, "Link": True},
            projection="mercator", height=height,
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor=BPS_PAPER)
        st.plotly_chart(fig, use_container_width=True)

# ======================================================================================
# SPLASH SCREEN
# ======================================================================================
def splash_screen():
    st.markdown(
        """<style>
          [data-testid="stSidebar"]{ display:none !important; }
          [data-testid="stHeader"]{ background: transparent !important; }
          .block-container{ padding-top: 0 !important; }
          .block-container::before { display: none !important; }
        </style>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="splash-wrap">', unsafe_allow_html=True)
    cols = st.columns([0.55, 2.45])

    with cols[0]:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.markdown(
                "<div style='height:76px; width:76px; border-radius:22px; background:rgba(255,255,255,.18); "
                "border:1px solid rgba(255,255,255,.25); display:flex; align-items:center; justify-content:center; "
                "font-size:34px; color:white; font-weight:900;'>🏛️</div>",
                unsafe_allow_html=True,
            )

    with cols[1]:
        st.markdown('<div class="splash-kicker">BPS BABEL • DASHBOARD UMKM</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="splash-title">{APP_TITLE}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="splash-sub">Menyiapkan tampilan, memuat modul, dan mengoptimalkan pengalaman penggunaan…</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="splash-row">'
            '<span class="splash-pill">UI Modern</span>'
            '<span class="splash-pill">Navigasi Cepat</span>'
            '<span class="splash-pill">Akurat & Rapi</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    prog = st.progress(0)
    status = st.empty()
    for i in range(0, 101, 4):
        prog.progress(i)
        if i < 30:
            status.caption("Menginisialisasi komponen…")
        elif i < 70:
            status.caption("Menyiapkan modul marketplace…")
        else:
            status.caption("Hampir selesai…")
        time.sleep(0.018)

    st.session_state["__splash_done__"] = True
    st.rerun()

if not st.session_state["__splash_done__"]:
    splash_screen()

# ======================================================================================
# NAVIGATION BOOT
# ======================================================================================
if not st.session_state["__boot__"]:
    st.session_state["__boot__"] = True
    st.session_state["show_sidebar"] = False
    st.session_state["menu_nav"] = "🏠 Dashboard"
    st.session_state["nav_target"] = None

# Apply nav target
if st.session_state.get("nav_target"):
    st.session_state["menu_nav"] = st.session_state["nav_target"]
    st.session_state["nav_target"] = None

# Auto-hide sidebar on Dashboard
if st.session_state.get("menu_nav") == "🏠 Dashboard":
    st.session_state["show_sidebar"] = False

# If sidebar is on but still dashboard, snap to first module
if st.session_state.get("show_sidebar") and st.session_state.get("menu_nav") == "🏠 Dashboard":
    st.session_state["menu_nav"] = "🟠 Shopee"

# ======================================================================================
# SIDEBAR (Premium)
# ======================================================================================
menu = "🏠 Dashboard"
if st.session_state["show_sidebar"]:
    with st.sidebar:
        st.markdown(
            """
<div class="sb-brand">
  <div class="sb-brand-icon">🏛️</div>
  <div>
    <div class="sb-brand-name">Dashboard UMKM</div>
    <div class="sb-brand-sub">BPS Bangka Belitung</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button("⬅️ Kembali ke Dashboard", key="btn_home", use_container_width=True, type="secondary"):
            st.session_state["show_sidebar"] = False
            st.session_state["menu_nav"] = "🏠 Dashboard"
            st.rerun()

        st.divider()

        st.markdown('<div class="sb-nav-label">📂 Modul Data</div>', unsafe_allow_html=True)

        menu = st.radio(
            "",
            ["🟠 Shopee", "🟢 Tokopedia", "📍 Google Maps", "📊 Export Gabungan"],
            index=["🟠 Shopee", "🟢 Tokopedia", "📍 Google Maps", "📊 Export Gabungan"].index(st.session_state["menu_nav"])
            if st.session_state["menu_nav"] in ["🟠 Shopee", "🟢 Tokopedia", "📍 Google Maps", "📊 Export Gabungan"]
            else 0,
            key="menu_nav",
            label_visibility="collapsed",
        )

        st.divider()

        _shp_n = 0 if st.session_state.data_shopee is None else len(st.session_state.data_shopee)
        _tkp_n = 0 if st.session_state.data_tokped is None else len(st.session_state.data_tokped)
        _mp_n  = 0 if st.session_state.data_maps   is None else len(st.session_state.data_maps)
        _total = _shp_n + _tkp_n + _mp_n

        def _fmt(n):
            return f"{int(n):,}".replace(",", ".") if n else "—"

        st.markdown('<div class="sb-nav-label">📊 Ringkasan Data</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
<div class="sb-stat-grid">
  <div class="sb-stat">
    <div class="sb-stat-val">{_fmt(_shp_n)}</div>
    <div class="sb-stat-lbl">🟠 Shopee</div>
  </div>
  <div class="sb-stat">
    <div class="sb-stat-val">{_fmt(_tkp_n)}</div>
    <div class="sb-stat-lbl">🟢 Tokopedia</div>
  </div>
  <div class="sb-stat">
    <div class="sb-stat-val">{_fmt(_mp_n)}</div>
    <div class="sb-stat-lbl">📍 Maps</div>
  </div>
  <div class="sb-stat">
    <div class="sb-stat-val">{_fmt(_total)}</div>
    <div class="sb-stat-lbl">📦 Total</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown('<div class="sb-nav-label">⚙️ Pengaturan</div>', unsafe_allow_html=True)
        with st.expander("Opsi Tampilan & Performa", expanded=False):
            st.checkbox("Tampilkan tips cepat", value=st.session_state.get("show_tips", True), key="show_tips")
            st.checkbox("Mode cepat (kurangi rendering chart)", value=st.session_state.get("fast_mode", False), key="fast_mode")

        st.markdown(
            """
<div class="sb-footer">
  <strong>BPS Bangka Belitung</strong><br>
  Dashboard UMKM v2.1<br>
  <span style="opacity:0.7">Data Statistik Berkualitas</span>
</div>
""",
            unsafe_allow_html=True,
        )
else:
    hide_sidebar_css()

# ======================================================================================
# TOPBAR (always visible)
# ======================================================================================
current_page_label = "Dashboard" if menu == "🏠 Dashboard" else menu.replace("🟠 ", "").replace("🟢 ", "").replace("📍 ", "").replace("📊 ", "")
topbar(current_page_label, st.session_state.get("show_sidebar", False))

# ======================================================================================
# PAGE: DASHBOARD
# ======================================================================================
if menu == "🏠 Dashboard":
    st.session_state["show_sidebar"] = False
    hide_sidebar_css()

    section_header("Dashboard Utama", "Ringkasan status data & akses cepat ke modul UMKM.", "DASHBOARD")
    banner("Dashboard Utama", "Mulai dari ringkasan cepat, lalu masuk ke modul UMKM yang kamu butuhkan.")

    st.markdown(
        """
<div class="bps-hero">
  <div class="bps-badge">UMKM • BPS BABEL</div>
  <h1>Kontrol Pusat Analisis UMKM</h1>
  <p>Upload data dari marketplace / maps, cek ringkasan, lalu lanjutkan analisis mendalam.</p>
  <div class="cta-row">
    <span class="bps-chip">🟠 Shopee</span>
    <span class="bps-chip">🟢 Tokopedia</span>
    <span class="bps-chip">📍 Google Maps</span>
    <span class="bps-chip">📊 Export</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    df_shp = st.session_state.data_shopee
    df_tkp = st.session_state.data_tokped
    df_maps = st.session_state.data_maps
    shp_n = 0 if df_shp is None else len(df_shp)
    tkp_n = 0 if df_tkp is None else len(df_tkp)
    mp_n  = 0 if df_maps is None else len(df_maps)
    total_all = shp_n + tkp_n + mp_n

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    k1.metric("📦 Total Data", fmt_int_id(total_all))
    k2.metric("🟠 Shopee", fmt_int_id(shp_n))
    k3.metric("🟢 Tokopedia", fmt_int_id(tkp_n))
    k4.metric("📍 Google Maps", fmt_int_id(mp_n))

    with st.container(border=True):
        st.subheader("🚦 Status Modul")
        s1, s2 = st.columns([1.35, 0.65], gap="large")

        def _pill(ok: bool, text: str):
            cls = "ok" if ok else "no"
            icon = "✅" if ok else "⏳"
            return f'<span class="dash-pill {cls}">{icon} {text}</span>'

        with s1:
            st.markdown(
                _pill(shp_n > 0, "Shopee siap dianalisis") +
                _pill(tkp_n > 0, "Tokopedia siap dianalisis") +
                _pill(mp_n > 0, "Google Maps siap divisualisasi"),
                unsafe_allow_html=True,
            )
            if st.session_state.get("show_tips", True):
                st.caption("Tip: Mulai dari modul yang datanya sudah siap. Gunakan Export Gabungan untuk konsolidasi akhir.")
        with s2:
            if st.button("🚀 Ayo Upload Data", use_container_width=True, type="primary"):
                goto_menu("🟠 Shopee")

    with st.container(border=True):
        st.subheader("✨ Rekomendasi & Tips")
        t1, t2 = st.columns(2, gap="large")
        with t1:
            st.success("**Workflow ideal:** Upload → Filter → Dashboard Eksekutif → Export.")
            st.write("• Pakai **Mode cepat** kalau file sangat besar.\n• Naikkan **jeda request** API Shopee kalau kena rate limit.")
        with t2:
            st.warning("**Catatan kualitas data:**")
            st.write("• Pastikan kolom lokasi/wilayah benar.\n• Untuk Google Maps, pastikan **lat/lon** valid.\n• Link/telepon kosong akan otomatis dibersihkan.")

# ======================================================================================
# PAGE: SHOPEE
# ======================================================================================
elif menu == "🟠 Shopee":
    section_header("Shopee Marketplace", "Analisis & ekstraksi data UMKM Shopee.", "MARKETPLACE")
    banner("Dashboard UMKM — Shopee", "Ekstraksi data UMKM dari Shopee Marketplace (Bangka Belitung)")

    with st.container(border=True):
        left, right = st.columns([1.25, 0.95], gap="large")
        with left:
            st.subheader("📥 Input Data")
            files = st.file_uploader("Unggah CSV Shopee", type=["csv"], accept_multiple_files=True, key="file_shp")

            mode_api = st.toggle("🔎 Deteksi Nama Toko via API Shopee", value=True, key="api_shp")
            colA, colB, colC = st.columns(3)
            with colA:
                api_timeout = st.number_input("Timeout API (detik)", min_value=1, max_value=10, value=2, step=1)
            with colB:
                api_sleep = st.number_input("Jeda per request (detik)", min_value=0.0, max_value=2.0, value=0.0, step=0.1)
            with colC:
                max_api_calls = st.number_input("Maks panggilan API", min_value=0, max_value=50000, value=8000, step=500)

            if st.session_state.get("show_tips", True):
                st.caption("Tips: kalau scraping terdeteksi robot, naikkan jeda request.")

            run = st.button("🚀 Proses Data Shopee", type="primary", use_container_width=True)

        with right:
            st.subheader("🧾 Aturan")
            st.info("• Data difilter **Bangka Belitung**.\n• Harga dibersihkan jadi integer.\n• Tipe Usaha dihitung pakai heuristik nama toko.")
            st.caption("Jika API Shopee sering timeout, kecilkan max calls atau naikkan timeout sedikit.")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Shopee terlebih dahulu.")
        else:
            with st.status("Memproses data Shopee…", expanded=True) as status:
                try:
                    total_semua_baris = 0
                    for f in files:
                        df_temp = pd.read_csv(f, dtype=str, on_bad_lines="skip")
                        total_semua_baris += len(df_temp)
                        f.seek(0)

                    hasil = []
                    total_baris = 0
                    err_h = 0
                    luar_wilayah = 0
                    progress = st.progress(0)
                    info = st.empty()
                    baris_diproses = 0
                    api_calls = 0

                    for file in files:
                        df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                        total_baris += len(df_raw)

                        if "Link" in df_raw.columns and "Nama Produk" in df_raw.columns:
                            col_link = "Link"
                            col_nama = "Nama Produk"
                            col_harga = "Harga"
                            col_wilayah = "Wilayah"
                        else:
                            col_link = next((c for c in df_raw.columns if "href" in c.lower()), df_raw.columns[0])
                            col_nama = next((c for c in df_raw.columns if "whitespace-normal" in c.lower()), df_raw.columns[min(3, len(df_raw.columns)-1)])
                            col_harga = next((c for c in df_raw.columns if "font-medium" in c.lower()), df_raw.columns[min(4, len(df_raw.columns)-1)])
                            idx_wilayah = 7 if len(df_raw.columns) > 7 else len(df_raw.columns) - 1
                            col_wilayah = next((c for c in df_raw.columns if "ml-[3px]" in c.lower()), df_raw.columns[idx_wilayah])

                        for i in range(len(df_raw)):
                            row = df_raw.iloc[i]
                            link = str(row.get(col_link, ""))
                            nama_produk = str(row.get(col_nama, ""))
                            harga_str = str(row.get(col_harga, ""))
                            lokasi = safe_title(str(row.get(col_wilayah, "")))

                            if not is_in_babel(lokasi):
                                luar_wilayah += 1
                                baris_diproses += 1
                                continue

                            try:
                                harga_bersih = harga_str.replace(".", "").replace(",", "")
                                angka_list = re.findall(r"\d+", harga_bersih)
                                val_h = int(angka_list[0]) if angka_list else 0
                                if val_h > 1_000_000_000:
                                    val_h = 0
                            except Exception:
                                val_h = 0
                                err_h += 1

                            toko = "Tidak Dilacak"
                            if mode_api and api_calls < int(max_api_calls):
                                match = re.search(r"i\.(\d+)\.", link)
                                if match:
                                    try:
                                        api_calls += 1
                                        res = requests.get(
                                            f"https://shopee.co.id/api/v4/shop/get_shop_base?shopid={match.group(1)}",
                                            headers={"User-Agent": "Mozilla/5.0"},
                                            timeout=float(api_timeout),
                                        )
                                        if res.status_code == 200:
                                            toko = res.json().get("data", {}).get("name", "Anonim")
                                    except Exception:
                                        pass
                                    if api_sleep and api_sleep > 0:
                                        time.sleep(float(api_sleep))

                            tipe_usaha = deteksi_tipe_usaha(toko)
                            hasil.append({
                                "Nama Toko": toko,
                                "Nama Produk": nama_produk,
                                "Harga": val_h,
                                "Wilayah": lokasi,
                                "Tipe Usaha": tipe_usaha,
                                "Link": link
                            })

                            baris_diproses += 1
                            if baris_diproses % 25 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses / max(total_semua_baris, 1), 1.0)
                                progress.progress(pct)
                                info.markdown(
                                    f"**⏳ Progress:** {fmt_int_id(baris_diproses)} / {fmt_int_id(total_semua_baris)} "
                                    f"({int(pct*100)}%) • API calls: {fmt_int_id(api_calls)}"
                                )

                    progress.empty()
                    info.empty()

                    df = pd.DataFrame(hasil)
                    st.session_state.data_shopee = df
                    st.session_state.audit_shopee = {
                        "file_count": len(files),
                        "total_rows": total_baris,
                        "valid_rows": len(df),
                        "luar_wilayah": luar_wilayah,
                        "error_harga": err_h,
                        "api_calls": api_calls,
                    }

                    status.update(label="✅ Selesai memproses Shopee", state="complete", expanded=False)
                    st.toast(f"Shopee: {fmt_int_id(len(df))} baris siap dianalisis", icon="✅")

                except Exception as e:
                    status.update(label="❌ Gagal memproses Shopee", state="error", expanded=True)
                    st.error(f"Error Sistem Shopee: {e}")

    df_shp = st.session_state.data_shopee
    if df_shp is not None and not df_shp.empty:
        with st.container(border=True):
            st.subheader("🔎 Filter Pintar")
            c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.6, 1.2], gap="medium")
            with c1:
                f_wil = st.multiselect(
                    "📍 Wilayah",
                    options=sorted(df_shp["Wilayah"].unique()),
                    default=sorted(df_shp["Wilayah"].unique()),
                    key="f_wil_shp",
                )
            with c2:
                f_tipe = st.multiselect(
                    "🏢 Tipe Usaha",
                    options=sorted(df_shp["Tipe Usaha"].unique()),
                    default=sorted(df_shp["Tipe Usaha"].unique()),
                    key="f_tipe_shp",
                )
            with c3:
                q = st.text_input("🔎 Cari (nama toko / produk)", value="", key="q_shp")
            with c4:
                max_h = int(df_shp["Harga"].max()) if df_shp["Harga"].max() > 0 else 1_000_000
                f_hrg = st.slider("💰 Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_shp")

        df_f = df_shp[
            df_shp["Wilayah"].isin(f_wil)
            & df_shp["Tipe Usaha"].isin(f_tipe)
            & (df_shp["Harga"] >= f_hrg[0])
            & (df_shp["Harga"] <= f_hrg[1])
        ].copy()

        if q.strip():
            qq = q.strip().lower()
            df_f = df_f[
                df_f["Nama Toko"].astype(str).str.lower().str.contains(qq, na=False)
                | df_f["Nama Produk"].astype(str).str.lower().str.contains(qq, na=False)
            ]

        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database", "📑 Audit"])

        with tab1:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📌 Total Ditampilkan", fmt_int_id(len(df_f)))
            m2.metric("🏠 Murni Online", fmt_int_id((df_f["Tipe Usaha"] == "Murni Online (Rumahan)").sum()))
            m3.metric("🏬 Ada Toko Fisik", fmt_int_id((df_f["Tipe Usaha"] == "Ada Toko Fisik").sum()))
            m4.metric("🗺️ Jumlah Wilayah", fmt_int_id(df_f["Wilayah"].nunique()))

            if (not st.session_state.get("fast_mode")) and (not df_f.empty):
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", hole=0.44, title="Komposisi Model Bisnis UMKM (Shopee)")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)

                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah")
                    fig = px.bar(grp, x="Wilayah", y="Jumlah", title="Total Usaha per Wilayah (Shopee)", color="Wilayah")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(
                lambda x: f"Rp {int(x):,}".replace(",", ".") if str(x).isdigit() else f"Rp {x}"
            )
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=420)

            excel_bytes = df_to_excel_bytes({"Data Shopee": df_f})
            st.download_button(
                "⬇️ Unduh Excel — Shopee",
                data=excel_bytes,
                file_name=f"UMKM_Shopee_{datetime.date.today()}.xlsx",
                use_container_width=True,
                type="primary",
            )

        with tab3:
            a = st.session_state.audit_shopee or {}
            st.info(f"📂 File diproses: **{fmt_int_id(a.get('file_count', 0))}**")
            st.success(f"✅ Baris valid: **{fmt_int_id(a.get('valid_rows', 0))}**")
            st.warning(f"⚠️ Diabaikan (luar wilayah): **{fmt_int_id(a.get('luar_wilayah', 0))}**")
            st.warning(f"⚠️ Error parsing harga: **{fmt_int_id(a.get('error_harga', 0))}**")
            st.caption(f"API calls: {fmt_int_id(a.get('api_calls', 0))}")

# ======================================================================================
# PAGE: TOKOPEDIA
# ======================================================================================
elif menu == "🟢 Tokopedia":
    section_header("Tokopedia Marketplace", "Workflow Tokopedia dengan UI enterprise.", "MARKETPLACE")
    banner("Dashboard UMKM — Tokopedia", "Ekstraksi data UMKM dari Tokopedia (Bangka Belitung)")

    with st.container(border=True):
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV Tokopedia", type=["csv"], accept_multiple_files=True, key="file_tkp")
            run = st.button("🚀 Proses Data Tokopedia", type="primary", use_container_width=True)
        with col2:
            st.subheader("🧾 Catatan")
            st.info("• Sistem akan menebak kolom bila struktur CSV berbeda.\n• Data difilter otomatis hanya Babel.")
            st.caption("Jika format CSV berubah, pastikan minimal ada link & nama produk terbaca.")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Tokopedia terlebih dahulu.")
        else:
            with st.status("Memproses data Tokopedia…", expanded=True) as status:
                try:
                    total_semua_baris = 0
                    for f in files:
                        df_temp = pd.read_csv(f, dtype=str, on_bad_lines="skip")
                        total_semua_baris += len(df_temp)
                        f.seek(0)

                    hasil = []
                    total_baris = 0
                    err_h = 0
                    luar_wilayah = 0
                    progress = st.progress(0)
                    info = st.empty()
                    baris_diproses = 0

                    for file in files:
                        df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                        total_baris += len(df_raw)

                        if "Link" in df_raw.columns and "Nama Produk" in df_raw.columns:
                            col_links = ["Link"]
                            col_namas = ["Nama Produk"]
                            col_hargas = ["Harga"]
                            col_lokasis = ["Wilayah"]
                            col_tokos = ["Nama Toko"]
                        else:
                            col_links = [c for c in df_raw.columns if "Ui5" in c]
                            col_namas = [c for c in df_raw.columns if "+tnoqZhn" in c]
                            col_hargas = [c for c in df_raw.columns if "urMOIDHH" in c]
                            col_lokasis = [c for c in df_raw.columns if "gxi+fs" in c]
                            col_tokos = [c for c in df_raw.columns if "si3CN" in c]

                        max_items = max(len(col_links), len(col_namas), len(col_hargas), len(col_lokasis), len(col_tokos))
                        if max_items == 0:
                            max_items = 1

                        for i in range(len(df_raw)):
                            for j in range(max_items):
                                try:
                                    link = str(df_raw.iloc[i][col_links[j]]) if j < len(col_links) else "nan"
                                    nama = str(df_raw.iloc[i][col_namas[j]]) if j < len(col_namas) else "nan"
                                    harga_str = str(df_raw.iloc[i][col_hargas[j]]) if j < len(col_hargas) else "0"
                                    lokasi = safe_title(str(df_raw.iloc[i][col_lokasis[j]])) if j < len(col_lokasis) else "-"
                                    toko = str(df_raw.iloc[i][col_tokos[j]]) if j < len(col_tokos) else "Toko CSV"

                                    if link == "nan" or nama == "nan":
                                        continue
                                    if not is_in_babel(lokasi):
                                        luar_wilayah += 1
                                        continue

                                    try:
                                        harga_bersih = harga_str.replace(".", "").replace(",", "")
                                        angka_list = re.findall(r"\d+", harga_bersih)
                                        val_h = int(angka_list[0]) if angka_list else 0
                                        if val_h > 1_000_000_000:
                                            val_h = 0
                                    except Exception:
                                        val_h = 0
                                        err_h += 1

                                    if val_h > 0:
                                        tipe_usaha = deteksi_tipe_usaha(toko)
                                        hasil.append({
                                            "Nama Toko": toko,
                                            "Nama Produk": nama,
                                            "Harga": val_h,
                                            "Wilayah": lokasi,
                                            "Tipe Usaha": tipe_usaha,
                                            "Link": link
                                        })

                                except Exception:
                                    continue

                            baris_diproses += 1
                            if baris_diproses % 25 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses / max(total_semua_baris, 1), 1.0)
                                progress.progress(pct)
                                info.markdown(
                                    f"**⏳ Progress:** {fmt_int_id(baris_diproses)} / {fmt_int_id(total_semua_baris)} "
                                    f"({int(pct*100)}%)"
                                )

                    progress.empty()
                    info.empty()

                    df_final = pd.DataFrame(hasil).drop_duplicates()
                    st.session_state.data_tokped = df_final
                    st.session_state.audit_tokped = {
                        "file_count": len(files),
                        "total_rows": total_baris,
                        "valid_rows": len(df_final),
                        "luar_wilayah": luar_wilayah,
                        "error_harga": err_h,
                    }

                    status.update(label="✅ Selesai memproses Tokopedia", state="complete", expanded=False)
                    st.toast(f"Tokopedia: {fmt_int_id(len(df_final))} baris siap dianalisis", icon="✅")

                except Exception as e:
                    status.update(label="❌ Gagal memproses Tokopedia", state="error", expanded=True)
                    st.error(f"Error Sistem Tokopedia: {e}")

    df_tkp = st.session_state.data_tokped
    if df_tkp is not None and not df_tkp.empty:
        with st.container(border=True):
            st.subheader("🔎 Filter Pintar")
            c1, c2, c3 = st.columns([1.2, 1.2, 1.6], gap="medium")
            with c1:
                f_wil = st.multiselect(
                    "📍 Wilayah",
                    options=sorted(df_tkp["Wilayah"].unique()),
                    default=sorted(df_tkp["Wilayah"].unique()),
                    key="f_wil_tkp",
                )
            with c2:
                f_tipe = st.multiselect(
                    "🏢 Tipe Usaha",
                    options=sorted(df_tkp["Tipe Usaha"].unique()),
                    default=sorted(df_tkp["Tipe Usaha"].unique()),
                    key="f_tipe_tkp",
                )
            with c3:
                q = st.text_input("🔎 Cari", value="", key="q_tkp")

            max_h = int(df_tkp["Harga"].max()) if df_tkp["Harga"].max() > 0 else 1_000_000
            f_hrg = st.slider("💰 Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_tkp")

        df_f = df_tkp[
            df_tkp["Wilayah"].isin(f_wil)
            & df_tkp["Tipe Usaha"].isin(f_tipe)
            & (df_tkp["Harga"] >= f_hrg[0])
            & (df_tkp["Harga"] <= f_hrg[1])
        ].copy()

        if q.strip():
            qq = q.strip().lower()
            df_f = df_f[
                df_f["Nama Toko"].astype(str).str.lower().str.contains(qq, na=False)
                | df_f["Nama Produk"].astype(str).str.lower().str.contains(qq, na=False)
            ]

        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🗄️ Database", "📑 Audit"])

        with tab1:
            m1, m2, m3 = st.columns(3)
            m1.metric("📌 Total Ditampilkan", fmt_int_id(len(df_f)))
            m2.metric("🏠 Murni Online", fmt_int_id((df_f["Tipe Usaha"] == "Murni Online (Rumahan)").sum()))
            m3.metric("🗺️ Jumlah Wilayah", fmt_int_id(df_f["Wilayah"].nunique()))

            if (not st.session_state.get("fast_mode")) and (not df_f.empty):
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", hole=0.44, title="Komposisi Model Bisnis UMKM (Tokopedia)")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)

                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah")
                    fig = px.bar(grp, x="Wilayah", y="Jumlah", title="Total Usaha per Wilayah (Tokopedia)", color="Wilayah")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(
                lambda x: f"Rp {int(x):,}".replace(",", ".") if str(x).isdigit() else f"Rp {x}"
            )
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=420)

            excel_bytes = df_to_excel_bytes({"Data Tokopedia": df_f})
            st.download_button(
                "⬇️ Unduh Excel — Tokopedia",
                data=excel_bytes,
                file_name=f"UMKM_Tokopedia_{datetime.date.today()}.xlsx",
                use_container_width=True,
                type="primary",
            )

        with tab3:
            a = st.session_state.audit_tokped or {}
            st.info(f"📂 File diproses: **{fmt_int_id(a.get('file_count', 0))}**")
            st.success(f"✅ Baris valid: **{fmt_int_id(a.get('valid_rows', 0))}**")
            st.warning(f"⚠️ Diabaikan (luar wilayah): **{fmt_int_id(a.get('luar_wilayah', 0))}**")
            st.warning(f"⚠️ Error parsing harga: **{fmt_int_id(a.get('error_harga', 0))}**")

# ======================================================================================
# PAGE: GOOGLE MAPS
# ======================================================================================
elif menu == "📍 Google Maps":
    section_header("Google Maps", "Visualisasi & pembersihan data lokasi UMKM.", "LOCATION")
    banner("Dashboard UMKM — Google Maps", "Upload CSV hasil ekstensi → auto-clean → peta interaktif + export Excel/CSV")

    with st.container(border=True):
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV Google Maps", type=["csv"], accept_multiple_files=True, key="file_maps")
            do_clean = st.toggle("✨ Auto-clean (disarankan)", value=True, key="clean_maps")
            run = st.button("🚀 Proses Data Google Maps", type="primary", use_container_width=True)
        with col2:
            st.subheader("🧾 Format Kolom")
            st.code("foto_url, nama_usaha, alamat,\nno_telepon, latitude, longitude, link", language="text")
            st.caption("Kalau beda nama kolom, sistem tetap coba map otomatis.")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Google Maps terlebih dahulu.")
        else:
            with st.status("Memproses data Google Maps…", expanded=True) as status:
                try:
                    df_raw, total_rows = read_csv_files(files)

                    if do_clean:
                        df_clean, audit = clean_maps_dataframe(df_raw)
                    else:
                        df_clean = df_raw.copy()
                        audit = {"rows_in": len(df_raw), "rows_out": len(df_clean), "dedup_removed": 0, "invalid_coord": 0, "invalid_link": 0, "empty_name": 0, "missing_cols": []}

                    st.session_state.data_maps = df_clean
                    st.session_state.audit_maps = {
                        "file_count": len(files),
                        "rows_in": audit.get("rows_in", 0),
                        "rows_out": audit.get("rows_out", 0),
                        "dedup_removed": audit.get("dedup_removed", 0),
                        "invalid_coord": audit.get("invalid_coord", 0),
                        "invalid_link": audit.get("invalid_link", 0),
                        "empty_name": audit.get("empty_name", 0),
                        "missing_cols": audit.get("missing_cols", []),
                    }

                    status.update(label="✅ Selesai memproses Google Maps", state="complete", expanded=False)
                    st.toast(f"Google Maps: {fmt_int_id(len(df_clean))} baris siap dianalisis", icon="✅")

                except Exception as e:
                    status.update(label="❌ Gagal memproses Google Maps", state="error", expanded=True)
                    st.error(f"Error Sistem Google Maps: {e}")

    df_maps = st.session_state.data_maps
    if df_maps is not None and not df_maps.empty:
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🧹 Data Bersih", "📑 Audit"])

        with tab1:
            # Handle both cleaned schema and raw schema safely
            lat_col = "Latitude" if "Latitude" in df_maps.columns else ("latitude" if "latitude" in df_maps.columns else None)
            lon_col = "Longitude" if "Longitude" in df_maps.columns else ("longitude" if "longitude" in df_maps.columns else None)
            link_col = "Link" if "Link" in df_maps.columns else ("link" if "link" in df_maps.columns else None)
            tel_col = "No Telepon" if "No Telepon" in df_maps.columns else ("no_telepon" if "no_telepon" in df_maps.columns else None)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📌 Total Data", fmt_int_id(len(df_maps)))
            m2.metric("📍 Koordinat Valid", fmt_int_id(df_maps[lat_col].notna().sum() if lat_col else 0))
            m3.metric("🔗 Link Valid", fmt_int_id((df_maps[link_col].astype(str).str.len() > 0).sum() if link_col else 0))
            m4.metric("☎️ No Telp Valid", fmt_int_id((df_maps[tel_col].astype(str).str.len() > 0).sum() if tel_col else 0))

            if not st.session_state.get("fast_mode"):
                # Only render map if cleaned schema exists
                if "Latitude" in df_maps.columns and "Longitude" in df_maps.columns:
                    render_real_map_folium(df_maps, height=560)
                else:
                    st.info("Map membutuhkan schema kolom bersih: Latitude & Longitude. Aktifkan Auto-clean.")

        with tab2:
            st.dataframe(df_maps, use_container_width=True, hide_index=True, height=440)

            excel_bytes = df_to_excel_bytes({"Data Google Maps": df_maps})
            st.download_button(
                "⬇️ Unduh Excel — Google Maps",
                data=excel_bytes,
                file_name=f"UMKM_GoogleMaps_{datetime.date.today()}.xlsx",
                use_container_width=True,
                type="primary",
            )

            csv_bytes = df_maps.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Unduh CSV — Google Maps",
                data=csv_bytes,
                file_name=f"UMKM_GoogleMaps_{datetime.date.today()}.csv",
                use_container_width=True,
            )

        with tab3:
            a = st.session_state.audit_maps or {}
            st.info(f"📂 File diproses: **{fmt_int_id(a.get('file_count', 0))}**")
            st.success(f"📥 Baris masuk: **{fmt_int_id(a.get('rows_in', 0))}**")
            st.success(f"✅ Baris keluar: **{fmt_int_id(a.get('rows_out', 0))}**")
            st.warning(f"🧽 Duplikat dihapus: **{fmt_int_id(a.get('dedup_removed', 0))}**")
            st.warning(f"📍 Koordinat invalid: **{fmt_int_id(a.get('invalid_coord', 0))}**")
            st.warning(f"🔗 Link invalid: **{fmt_int_id(a.get('invalid_link', 0))}**")
            st.warning(f"🏷️ Nama usaha kosong: **{fmt_int_id(a.get('empty_name', 0))}**")
            if a.get("missing_cols"):
                st.warning(f"Kolom tidak ditemukan (diisi kosong): {', '.join(a['missing_cols'])}")

# ======================================================================================
# PAGE: EXPORT GABUNGAN
# ======================================================================================
elif menu == "📊 Export Gabungan":
    section_header("Export Gabungan", "Satukan data lintas platform lalu unduh dalam format rapi.", "EXPORT")
    banner("Export Master Data Gabungan", "Konsolidasi (Shopee, Tokopedia, Google Maps) → 1 Excel, sheet terpisah")

    df_shp_ready = st.session_state.data_shopee is not None and not st.session_state.data_shopee.empty
    df_tkp_ready = st.session_state.data_tokped is not None and not st.session_state.data_tokped.empty
    df_maps_ready = st.session_state.data_maps is not None and not st.session_state.data_maps.empty

    if not (df_shp_ready or df_tkp_ready or df_maps_ready):
        st.warning("⚠️ Belum ada data. Silakan proses dulu di menu Shopee/Tokopedia/Google Maps.")
    else:
        with st.container(border=True):
            st.subheader("✅ Data Siap Dikonsolidasi")
            c1, c2, c3 = st.columns(3)
            c1.metric("📦 Shopee", fmt_int_id(len(st.session_state.data_shopee)) if df_shp_ready else 0)
            c2.metric("📦 Tokopedia", fmt_int_id(len(st.session_state.data_tokped)) if df_tkp_ready else 0)
            c3.metric("📦 Google Maps", fmt_int_id(len(st.session_state.data_maps)) if df_maps_ready else 0)
            st.caption("Output: 1 file Excel berisi sheet terpisah per sumber + autofilter + header rapi.")

        sheets = {}
        if df_shp_ready:
            sheets["Data Shopee"] = st.session_state.data_shopee
        if df_tkp_ready:
            sheets["Data Tokopedia"] = st.session_state.data_tokped
        if df_maps_ready:
            sheets["Data Google Maps"] = st.session_state.data_maps

        excel_bytes = df_to_excel_bytes(sheets)

        with st.container(border=True):
            st.subheader("⬇️ Unduh File Master")
            _, col_btn, _ = st.columns([1, 2, 1])
            with col_btn:
                st.download_button(
                    label="⬇️ UNDUH EXCEL MASTER",
                    data=excel_bytes,
                    file_name=f"Master_UMKM_BPS_{datetime.date.today()}.xlsx",
                    use_container_width=True,
                    type="primary",
                )

# ======================================================================================
# FOOTER
# ======================================================================================
st.markdown(
    """
<div style='
  margin-top: 32px;
  padding: 16px 0;
  border-top: 1px solid rgba(245,95,0,0.12);
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(74,40,0,0.55);
  font-size: 0.84rem;
  font-family: "DM Sans", sans-serif;
'>
  <span style="font-size:1.1rem">🏛️</span>
  <span>Built with Streamlit &nbsp;•&nbsp; Badan Pusat Statistik UMKM Toolkit &nbsp;•&nbsp; Bangka Belitung</span>
</div>
""",
    unsafe_allow_html=True,
)
