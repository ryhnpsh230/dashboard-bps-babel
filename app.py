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
# MASTER CSS — Ultra Premium Redesign
# ======================================================================================
MASTER_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,300;1,400&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;0,9..144,700;0,9..144,900;1,9..144,400&display=swap');

/* ============================================================
   DESIGN TOKENS
   ============================================================ */
:root {
  /* Core palette */
  --fire:        #F55F00;
  --fire-light:  #FF7A1F;
  --fire-pale:   #FF9A4D;
  --amber:       #FFB347;
  --amber-light: #FFD08A;
  --cream:       #FFF8F2;
  --parchment:   #FFF2E6;
  --paper:       #FFFFFF;

  /* Ink scale */
  --ink-900: #1C0800;
  --ink-700: #3D1A00;
  --ink-500: #7A3C14;
  --ink-300: #B37048;
  --ink-100: #E8C4A8;

  /* Semantic */
  --success:  #22C55E;
  --warning:  #F59E0B;
  --error:    #EF4444;
  --info:     #3B82F6;

  /* Surfaces */
  --surface-0: #FFFFFF;
  --surface-1: rgba(255,248,242,0.92);
  --surface-2: rgba(255,242,230,0.70);
  --glass:     rgba(255,255,255,0.75);
  --glass-border: rgba(245,95,0,0.14);

  /* Shadows */
  --shadow-xs: 0 1px 3px rgba(245,95,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-sm: 0 4px 16px rgba(245,95,0,0.08), 0 1px 4px rgba(0,0,0,0.05);
  --shadow-md: 0 8px 32px rgba(245,95,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
  --shadow-lg: 0 20px 60px rgba(245,95,0,0.16), 0 4px 16px rgba(0,0,0,0.08);
  --shadow-xl: 0 32px 100px rgba(245,95,0,0.22), 0 8px 24px rgba(0,0,0,0.10);
  --shadow-fire: 0 8px 32px rgba(245,95,0,0.42), 0 2px 8px rgba(245,95,0,0.24);

  /* Radius */
  --r-xs:  6px;
  --r-sm:  10px;
  --r-md:  16px;
  --r-lg:  22px;
  --r-xl:  32px;
  --r-2xl: 44px;
  --r-full: 9999px;

  /* Transitions */
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out:    cubic-bezier(0, 0, 0.2, 1);
  --dur-fast:    150ms;
  --dur-base:    250ms;
  --dur-slow:    400ms;
}

/* ============================================================
   RESET & BASE
   ============================================================ */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  background:
    radial-gradient(ellipse 120% 80% at -10% -5%,  rgba(245,95,0,0.07) 0%, transparent 55%),
    radial-gradient(ellipse 80%  60% at 110% 0%,   rgba(255,163,71,0.06) 0%, transparent 50%),
    radial-gradient(ellipse 60%  50% at 50% 115%,  rgba(245,95,0,0.04) 0%, transparent 60%),
    linear-gradient(160deg, #FFFFFF 0%, #FFF8F2 40%, #FFF4EA 70%, #FFF0E0 100%) !important;
  background-attachment: fixed !important;
  color: var(--ink-900) !important;
}

[data-testid="stHeader"] { background: transparent !important; }
section.main, .main, .block-container { background: transparent !important; }

.block-container {
  max-width: 1240px;
  padding-top: 0.5rem !important;
  padding-bottom: 4rem !important;
}

/* Noise texture overlay */
.block-container::after {
  content: "";
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.025'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
  opacity: 0.4;
}

/* ============================================================
   TYPOGRAPHY
   ============================================================ */
h1, h2, h3, h4, h5 {
  font-family: 'Fraunces', serif !important;
  letter-spacing: -0.03em;
  color: var(--ink-900) !important;
}
h1 { font-weight: 900 !important; font-size: clamp(1.8rem, 4vw, 2.6rem) !important; }
h2 { font-weight: 700 !important; font-size: clamp(1.3rem, 2.5vw, 1.75rem) !important; }
h3 { font-weight: 600 !important; }

p, li, span, label { color: var(--ink-700) !important; }
.caption, small { color: var(--ink-300) !important; }

/* ============================================================
   SCROLLBAR
   ============================================================ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, var(--fire), var(--amber));
  border-radius: var(--r-full);
}

/* ============================================================
   TOP ACCENT LINE
   ============================================================ */
.block-container::before {
  content: "";
  display: block;
  height: 2px;
  width: 100%;
  margin-bottom: 20px;
  border-radius: var(--r-full);
  background: linear-gradient(90deg,
    transparent 0%,
    var(--fire) 15%,
    var(--fire-light) 35%,
    var(--amber) 50%,
    var(--fire-light) 65%,
    var(--fire) 85%,
    transparent 100%
  );
  opacity: 0.45;
  animation: shimmerBar 3s ease-in-out infinite;
}

@keyframes shimmerBar {
  0%, 100% { opacity: 0.35; }
  50% { opacity: 0.65; }
}

/* ============================================================
   CARDS / CONTAINERS
   ============================================================ */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--glass) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--r-xl) !important;
  box-shadow: var(--shadow-sm) !important;
  backdrop-filter: blur(20px) saturate(1.4) !important;
  -webkit-backdrop-filter: blur(20px) saturate(1.4) !important;
  transition: all var(--dur-base) var(--ease-smooth) !important;
  padding: 22px 26px !important;
  position: relative !important;
  overflow: hidden !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(245,95,0,0.3), transparent);
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: rgba(245,95,0,0.26) !important;
  box-shadow: var(--shadow-md) !important;
  transform: translateY(-2px) !important;
}

/* ============================================================
   TOPBAR
   ============================================================ */
.topbar {
  position: relative;
  border-radius: var(--r-xl);
  padding: 16px 22px;
  margin: 0 0 20px 0;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(20px) saturate(1.5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  overflow: hidden;
}

.topbar::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1.5px;
  background: linear-gradient(90deg, transparent 0%, var(--fire) 30%, var(--amber) 60%, transparent 100%);
  opacity: 0.6;
}

.top-left { display: flex; align-items: center; gap: 14px; }

.top-logo {
  width: 44px; height: 44px;
  border-radius: var(--r-md);
  background: linear-gradient(135deg, var(--fire) 0%, var(--fire-pale) 100%);
  box-shadow: var(--shadow-fire);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.35rem;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.top-logo::after {
  content: "";
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, transparent 60%);
  border-radius: inherit;
}

.top-title {
  font-family: 'Fraunces', serif !important;
  font-weight: 700;
  font-size: 1.05rem;
  letter-spacing: -0.02em;
  color: var(--ink-900);
  line-height: 1.2;
}

.top-sub {
  font-size: 0.78rem;
  color: var(--ink-300);
  margin-top: 2px;
  font-weight: 500;
}

.breadcrumb {
  font-size: 0.80rem;
  color: var(--ink-500);
  font-weight: 600;
}

.kbd {
  display: inline-flex; align-items: center;
  padding: 4px 10px;
  border-radius: var(--r-sm);
  border: 1px solid var(--glass-border);
  background: var(--surface-1);
  font-size: 0.74rem;
  color: var(--ink-500);
  font-weight: 700;
  letter-spacing: 0.03em;
}

/* ============================================================
   SECTION HEADER
   ============================================================ */
.bps-section { margin: 6px 0 22px 0; }

.sec-badge {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.20em;
  text-transform: uppercase;
  color: var(--fire);
  margin-bottom: 8px;
}

.sec-badge::before {
  content: "";
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--fire);
  box-shadow: 0 0 0 4px rgba(245,95,0,0.18);
  animation: pulseDot 2.2s ease-in-out infinite;
}

@keyframes pulseDot {
  0%, 100% { box-shadow: 0 0 0 4px rgba(245,95,0,0.18); }
  50% { box-shadow: 0 0 0 7px rgba(245,95,0,0.08); }
}

.sec-title {
  font-size: 2.0rem !important;
  font-weight: 900 !important;
  margin: 0 !important;
  background: linear-gradient(135deg, var(--ink-900) 0%, var(--ink-700) 60%, var(--fire) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sec-sub { color: var(--ink-300) !important; font-size: 0.95rem; margin: 4px 0 0 0 !important; }

.sec-rule {
  height: 2px; margin-top: 14px; width: 100%;
  background: linear-gradient(90deg, var(--fire) 0%, var(--amber) 40%, transparent 100%);
  border-radius: var(--r-full);
  opacity: 0.3;
}

/* ============================================================
   BANNER
   ============================================================ */
.bps-banner {
  position: relative; overflow: hidden;
  border-radius: var(--r-xl);
  padding: 24px 30px;
  margin: 0 0 20px 0;
  background: linear-gradient(135deg,
    rgba(255,255,255,0.95) 0%,
    rgba(255,248,242,0.95) 100%
  );
  border: 1px solid rgba(245,95,0,0.15);
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(20px);
}

.bps-banner::before {
  content: "";
  position: absolute; top: -80px; right: -100px;
  width: 380px; height: 380px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(245,95,0,0.10), transparent 70%);
  pointer-events: none;
}

.bps-banner::after {
  content: "";
  position: absolute; bottom: -40px; left: 40%;
  width: 220px; height: 220px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,179,71,0.08), transparent 70%);
  pointer-events: none;
}

.bps-kicker {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.70rem; font-weight: 800;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--fire);
  margin-bottom: 10px;
  position: relative; z-index: 1;
  display: flex; align-items: center; gap: 8px;
}

.bps-kicker::before {
  content: "";
  width: 24px; height: 2px;
  background: linear-gradient(90deg, var(--fire), var(--amber));
  border-radius: var(--r-full);
  display: inline-block;
}

.bps-title {
  font-family: 'Fraunces', serif !important;
  font-size: 1.75rem !important; font-weight: 900;
  margin: 0 0 8px 0;
  color: var(--ink-900);
  position: relative; z-index: 1;
  letter-spacing: -0.03em;
}

.bps-subtitle {
  color: var(--ink-500) !important;
  font-size: 0.96rem;
  margin: 0;
  position: relative; z-index: 1;
  font-weight: 400;
  line-height: 1.6;
}

/* ============================================================
   HERO
   ============================================================ */
.bps-hero {
  position: relative; overflow: hidden;
  border-radius: var(--r-xl);
  padding: 36px 40px;
  margin-bottom: 22px;
  background: linear-gradient(135deg,
    #F55F00 0%,
    #FF6B0A 25%,
    #FF8330 55%,
    #FFA050 80%,
    #FFB347 100%
  );
  box-shadow: var(--shadow-xl);
}

.bps-hero::before {
  content: "";
  position: absolute; top: -100px; right: -130px;
  width: 480px; height: 480px;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  pointer-events: none;
}

.bps-hero::after {
  content: "";
  position: absolute; bottom: -60px; left: -60px;
  width: 280px; height: 280px;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
  pointer-events: none;
}

/* Decorative geometric */
.bps-hero .geo-decor {
  position: absolute; top: 20px; right: 180px;
  width: 80px; height: 80px;
  border: 2px solid rgba(255,255,255,0.12);
  border-radius: 22px;
  transform: rotate(15deg);
  pointer-events: none;
}

.bps-hero h1 {
  font-size: clamp(1.7rem, 3.5vw, 2.4rem) !important;
  font-weight: 900 !important;
  color: #fff !important;
  margin: 0 0 12px 0 !important;
  position: relative; z-index: 1;
  line-height: 1.15 !important;
  letter-spacing: -0.035em !important;
}

.bps-hero p {
  color: rgba(255,255,255,0.84) !important;
  font-size: 1.02rem;
  line-height: 1.65;
  margin: 0;
  position: relative; z-index: 1;
  font-weight: 400;
}

.bps-badge {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.68rem; font-weight: 800;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: rgba(255,255,255,0.92);
  background: rgba(255,255,255,0.14);
  border: 1px solid rgba(255,255,255,0.24);
  border-radius: var(--r-full);
  padding: 6px 14px;
  margin-bottom: 18px;
  position: relative; z-index: 1;
  backdrop-filter: blur(8px);
}

.cta-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 22px; position: relative; z-index: 1; }

.bps-chip {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 9px 18px; border-radius: var(--r-full);
  background: rgba(255,255,255,0.16);
  border: 1px solid rgba(255,255,255,0.28);
  color: #fff !important;
  font-weight: 700; font-size: 0.86rem;
  backdrop-filter: blur(10px);
  transition: all var(--dur-base) var(--ease-spring);
  cursor: default;
}

.bps-chip:hover {
  background: rgba(255,255,255,0.26);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

/* ============================================================
   METRICS
   ============================================================ */
div[data-testid="metric-container"] {
  background: var(--glass) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--r-lg) !important;
  padding: 20px 22px !important;
  box-shadow: var(--shadow-sm) !important;
  backdrop-filter: blur(20px) !important;
  transition: all var(--dur-base) var(--ease-spring) !important;
  position: relative !important;
  overflow: hidden !important;
}

div[data-testid="metric-container"]::before {
  content: "";
  position: absolute; top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--fire), var(--amber));
  border-radius: var(--r-full);
  opacity: 0.7;
}

div[data-testid="metric-container"]::after {
  content: "";
  position: absolute; top: -30px; right: -20px;
  width: 90px; height: 90px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(245,95,0,0.07), transparent 70%);
}

div[data-testid="metric-container"]:hover {
  transform: translateY(-3px) !important;
  box-shadow: var(--shadow-md) !important;
  border-color: rgba(245,95,0,0.30) !important;
}

div[data-testid="metric-container"] label {
  color: var(--ink-300) !important;
  font-weight: 700 !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: 'Fraunces', serif !important;
  font-weight: 900 !important;
  color: var(--ink-900) !important;
  font-size: 2.0rem !important;
  line-height: 1.1 !important;
  letter-spacing: -0.03em !important;
}

/* ============================================================
   TABS
   ============================================================ */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  background: var(--surface-2);
  border: 1px solid var(--glass-border);
  border-radius: var(--r-lg);
  padding: 6px;
}

.stTabs [data-baseweb="tab"] {
  height: 40px;
  padding: 0 20px;
  border-radius: var(--r-md);
  background: transparent;
  color: var(--ink-500) !important;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 700;
  font-size: 0.86rem;
  transition: all var(--dur-base) var(--ease-smooth);
  letter-spacing: 0.01em;
}

.stTabs [data-baseweb="tab"]:hover {
  background: rgba(245,95,0,0.08);
  color: var(--fire) !important;
}

.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--fire) 0%, var(--fire-light) 100%) !important;
  color: #fff !important;
  font-weight: 800 !important;
  box-shadow: 0 4px 16px rgba(245,95,0,0.38) !important;
}

.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ============================================================
   BUTTONS
   ============================================================ */
.stButton > button,
div[data-testid="stDownloadButton"] button {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 800 !important;
  font-size: 0.88rem !important;
  border-radius: var(--r-md) !important;
  height: 46px !important;
  letter-spacing: 0.01em !important;
  transition: all var(--dur-base) var(--ease-spring) !important;
}

.stButton > button[kind="primary"],
div[data-testid="stDownloadButton"] button {
  background: linear-gradient(135deg, var(--fire) 0%, var(--fire-light) 100%) !important;
  color: #fff !important;
  border: none !important;
  box-shadow: 0 6px 24px rgba(245,95,0,0.36), 0 2px 6px rgba(245,95,0,0.18) !important;
  position: relative !important;
  overflow: hidden !important;
}

.stButton > button[kind="primary"]::before,
div[data-testid="stDownloadButton"] button::before {
  content: "";
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.18) 0%, transparent 60%);
  pointer-events: none;
}

.stButton > button[kind="primary"]:hover,
div[data-testid="stDownloadButton"] button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 12px 36px rgba(245,95,0,0.44), 0 4px 12px rgba(245,95,0,0.24) !important;
}

.stButton > button[kind="primary"]:active,
div[data-testid="stDownloadButton"] button:active {
  transform: translateY(0) !important;
}

.stButton > button[kind="secondary"] {
  background: var(--glass) !important;
  color: var(--fire) !important;
  border: 1.5px solid rgba(245,95,0,0.22) !important;
  box-shadow: var(--shadow-xs) !important;
  backdrop-filter: blur(10px) !important;
}

.stButton > button[kind="secondary"]:hover {
  background: rgba(245,95,0,0.06) !important;
  border-color: var(--fire) !important;
  transform: translateY(-1px) !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ============================================================
   INPUTS & SELECTS
   ============================================================ */
div[data-baseweb="input"] {
  background: var(--glass) !important;
  border-radius: var(--r-sm) !important;
  border: 1.5px solid var(--glass-border) !important;
  backdrop-filter: blur(10px) !important;
  transition: all var(--dur-fast) var(--ease-smooth) !important;
}

div[data-baseweb="input"]:focus-within {
  border-color: var(--fire) !important;
  box-shadow: 0 0 0 3px rgba(245,95,0,0.14) !important;
}

div[data-baseweb="select"] > div {
  background: var(--glass) !important;
  border: 1.5px solid var(--glass-border) !important;
  border-radius: var(--r-sm) !important;
  backdrop-filter: blur(10px) !important;
}

div[data-baseweb="select"]:focus-within > div {
  border-color: var(--fire) !important;
  box-shadow: 0 0 0 3px rgba(245,95,0,0.14) !important;
}

input, textarea {
  color: var(--ink-900) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ============================================================
   DATAFRAME
   ============================================================ */
[data-testid="stDataFrame"] {
  border-radius: var(--r-lg) !important;
  overflow: hidden !important;
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ============================================================
   EXPANDERS
   ============================================================ */
details {
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: var(--r-md);
  padding: 4px 14px;
  backdrop-filter: blur(10px);
}

details summary {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 800;
  color: var(--ink-900);
}

details[open] { box-shadow: var(--shadow-sm); }

/* ============================================================
   ALERTS
   ============================================================ */
div[data-testid="stAlert"] {
  border-radius: var(--r-md) !important;
  border-left-width: 3px !important;
  backdrop-filter: blur(10px) !important;
}

/* ============================================================
   PROGRESS BAR
   ============================================================ */
[data-testid="stProgress"] > div > div > div {
  background: linear-gradient(90deg, var(--fire), var(--amber)) !important;
  border-radius: var(--r-full) !important;
}

/* ============================================================
   SIDEBAR
   ============================================================ */
[data-testid="stSidebar"] {
  background:
    radial-gradient(ellipse 600px 500px at 5% -5%, rgba(245,95,0,0.09) 0%, transparent 60%),
    radial-gradient(ellipse 400px 300px at 95% 100%, rgba(255,179,71,0.07) 0%, transparent 55%),
    linear-gradient(180deg, #FFFFFF 0%, #FFF8F2 50%, #FFF4EA 100%) !important;
  border-right: 1px solid rgba(245,95,0,0.12) !important;
  box-shadow: 4px 0 40px rgba(245,95,0,0.08), 1px 0 6px rgba(0,0,0,0.03) !important;
}

[data-testid="stSidebar"] * { color: var(--ink-900) !important; }

[data-testid="stSidebar"] .stMarkdown p {
  color: var(--ink-300) !important;
  font-size: 0.85rem !important;
}

[data-testid="stSidebar"] hr {
  border: none !important;
  border-top: 1px solid rgba(245,95,0,0.10) !important;
  margin: 8px 0 !important;
}

/* Sidebar brand */
.sb-brand { display: flex; align-items: center; gap: 14px; padding: 4px 0 18px 0; }

.sb-brand-icon {
  width: 50px; height: 50px; border-radius: var(--r-md);
  background: linear-gradient(135deg, var(--fire) 0%, var(--fire-pale) 100%);
  font-size: 1.5rem; display: flex; align-items: center; justify-content: center;
  box-shadow: var(--shadow-fire);
  flex-shrink: 0;
  position: relative; overflow: hidden;
}

.sb-brand-icon::after {
  content: "";
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.22) 0%, transparent 60%);
  border-radius: inherit;
}

.sb-brand-name {
  font-family: 'Fraunces', serif !important;
  font-size: 1.05rem; font-weight: 700;
  color: var(--ink-900) !important;
  letter-spacing: -0.02em; line-height: 1.25;
}

.sb-brand-sub {
  font-size: 0.70rem; font-weight: 700;
  color: var(--ink-300) !important;
  margin-top: 2px;
  text-transform: uppercase; letter-spacing: 0.06em;
}

/* Sidebar nav label */
.sb-nav-label {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.65rem; font-weight: 900;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: rgba(245,95,0,0.55) !important;
  padding: 8px 2px 6px 2px;
}

/* Sidebar radio nav */
[data-testid="stSidebar"] div[role="radiogroup"] {
  gap: 5px !important; display: flex !important; flex-direction: column !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label {
  border-radius: var(--r-md) !important;
  border: 1.5px solid rgba(245,95,0,0.08) !important;
  background: rgba(255,255,255,0.80) !important;
  padding: 13px 16px !important;
  cursor: pointer !important;
  transition: all var(--dur-base) var(--ease-spring) !important;
  box-shadow: var(--shadow-xs) !important;
  overflow: hidden !important;
  position: relative !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label::before {
  content: "";
  position: absolute; left: 0; top: 0; bottom: 0;
  width: 3px;
  background: linear-gradient(to bottom, var(--fire), var(--amber));
  opacity: 0;
  transition: opacity var(--dur-fast) var(--ease-smooth);
  border-radius: 0 var(--r-xs) var(--r-xs) 0;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
  border-color: rgba(245,95,0,0.22) !important;
  background: rgba(255,255,255,0.96) !important;
  box-shadow: var(--shadow-sm) !important;
  transform: translateX(4px) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover::before { opacity: 1; }

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
  background: linear-gradient(135deg, var(--fire) 0%, var(--fire-light) 100%) !important;
  border-color: transparent !important;
  box-shadow: 0 6px 24px rgba(245,95,0,0.36), 0 2px 6px rgba(245,95,0,0.18) !important;
  transform: translateX(4px) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span {
  color: #fff !important;
  font-weight: 800 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked)::before { display: none; }

[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] { display: none !important; }

/* Sidebar action button */
[data-testid="stSidebar"] .stButton > button {
  border-radius: var(--r-md) !important;
  background: rgba(245,95,0,0.06) !important;
  border: 1.5px solid rgba(245,95,0,0.18) !important;
  color: var(--fire) !important;
  font-weight: 800 !important;
  font-size: 0.85rem !important;
  height: 42px !important;
  box-shadow: none !important;
  transition: all var(--dur-base) var(--ease-smooth) !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(245,95,0,0.11) !important;
  border-color: var(--fire) !important;
  box-shadow: 0 4px 16px rgba(245,95,0,0.18) !important;
  transform: none !important;
}

/* Sidebar stats */
.sb-stat-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
  margin: 2px 0 4px 0;
}

.sb-stat {
  border-radius: var(--r-md); padding: 12px 14px;
  background: rgba(255,255,255,0.82);
  border: 1px solid rgba(245,95,0,0.09);
  box-shadow: var(--shadow-xs);
  transition: all var(--dur-base) var(--ease-smooth);
}

.sb-stat:hover {
  border-color: rgba(245,95,0,0.20);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.sb-stat-val {
  font-family: 'Fraunces', serif;
  font-size: 1.25rem; font-weight: 900;
  color: var(--fire) !important; line-height: 1.1;
}

.sb-stat-lbl {
  font-size: 0.67rem; font-weight: 800;
  color: var(--ink-300) !important; margin-top: 3px;
  letter-spacing: 0.04em;
}

/* Sidebar footer */
.sb-footer {
  margin-top: 12px; padding: 14px 16px;
  border-radius: var(--r-md);
  background: linear-gradient(135deg, rgba(245,95,0,0.05), rgba(255,179,71,0.04));
  border: 1px solid rgba(245,95,0,0.09);
  font-size: 0.74rem; color: var(--ink-300) !important;
  line-height: 1.7; text-align: center;
}

.sb-footer strong { color: var(--fire) !important; font-weight: 900; }

/* ============================================================
   STATUS PILLS
   ============================================================ */
.dash-pill {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 18px; border-radius: var(--r-full);
  margin: 6px 8px 0 0;
  font-weight: 700; font-size: 0.86rem;
  border: 1.5px solid var(--glass-border);
  background: var(--glass);
  color: var(--ink-500);
  box-shadow: var(--shadow-xs);
  backdrop-filter: blur(8px);
  transition: all var(--dur-base) var(--ease-smooth);
}

.dash-pill.ok {
  border-color: rgba(245,95,0,0.25);
  background: linear-gradient(135deg, rgba(245,95,0,0.07), rgba(255,140,66,0.05));
  color: var(--fire);
}

.dash-pill:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* ============================================================
   LINKS
   ============================================================ */
a { color: var(--fire) !important; text-decoration: none; transition: color var(--dur-fast); }
a:hover { color: var(--fire-light) !important; }

/* ============================================================
   TOAST
   ============================================================ */
[data-testid="stToast"] {
  border-radius: var(--r-md) !important;
  border-left: 3px solid var(--fire) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: var(--shadow-md) !important;
}

/* ============================================================
   SPLASH SCREEN
   ============================================================ */
.splash-outer {
  position: relative;
  min-height: 92vh;
  display: flex; align-items: center; justify-content: center;
}

.splash-wrap {
  position: relative; overflow: hidden;
  border-radius: var(--r-2xl);
  padding: 52px 56px;
  max-width: 820px; width: 100%;
  background: linear-gradient(135deg, #F55F00 0%, #FF6B0A 20%, #FF8330 50%, #FFA050 75%, #FFB347 100%);
  box-shadow: var(--shadow-xl);
  animation: splashIn 0.6s var(--ease-spring) forwards;
}

@keyframes splashIn {
  from { opacity: 0; transform: translateY(30px) scale(0.96); }
  to   { opacity: 1; transform: translateY(0)  scale(1); }
}

/* Decorative rings */
.splash-ring-1 {
  position: absolute; top: -120px; right: -140px;
  width: 560px; height: 560px; border-radius: 50%;
  background: rgba(255,255,255,0.06);
  pointer-events: none;
}
.splash-ring-2 {
  position: absolute; bottom: -80px; left: -80px;
  width: 340px; height: 340px; border-radius: 50%;
  background: rgba(255,255,255,0.04);
  pointer-events: none;
}
.splash-ring-3 {
  position: absolute; top: 40%; right: 8%;
  width: 100px; height: 100px; border-radius: 28px;
  border: 2px solid rgba(255,255,255,0.10);
  transform: rotate(12deg);
  pointer-events: none;
}
.splash-ring-4 {
  position: absolute; top: 12%; right: 22%;
  width: 60px; height: 60px; border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.12);
  pointer-events: none;
}

.splash-inner { position: relative; z-index: 1; }

.splash-eyebrow {
  display: inline-flex; align-items: center; gap: 10px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.70rem; font-weight: 800;
  letter-spacing: 0.20em; text-transform: uppercase;
  color: rgba(255,255,255,0.80);
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.20);
  padding: 5px 14px; border-radius: var(--r-full);
  margin-bottom: 18px;
  animation: fadeUp 0.5s 0.2s var(--ease-out) both;
}

.splash-logo-box {
  width: 72px; height: 72px;
  border-radius: 22px;
  background: rgba(255,255,255,0.18);
  border: 1.5px solid rgba(255,255,255,0.30);
  display: flex; align-items: center; justify-content: center;
  font-size: 2.2rem;
  margin-bottom: 20px;
  box-shadow: 0 8px 28px rgba(0,0,0,0.12);
  animation: fadeUp 0.5s 0.15s var(--ease-out) both;
  backdrop-filter: blur(10px);
}

.splash-title {
  font-family: 'Fraunces', serif;
  font-size: clamp(2rem, 5vw, 2.8rem);
  font-weight: 900;
  color: #fff;
  margin: 0 0 14px 0;
  letter-spacing: -0.04em;
  line-height: 1.1;
  animation: fadeUp 0.5s 0.25s var(--ease-out) both;
}

.splash-sub {
  color: rgba(255,255,255,0.82);
  font-size: 1.05rem;
  line-height: 1.65;
  margin: 0 0 24px 0;
  font-weight: 400;
  animation: fadeUp 0.5s 0.30s var(--ease-out) both;
  max-width: 480px;
}

.splash-features {
  display: flex; gap: 10px; flex-wrap: wrap;
  margin-bottom: 28px;
  animation: fadeUp 0.5s 0.35s var(--ease-out) both;
}

.splash-feat {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 7px 16px; border-radius: var(--r-full);
  background: rgba(255,255,255,0.16);
  border: 1px solid rgba(255,255,255,0.26);
  color: #fff; font-weight: 700; font-size: 0.84rem;
  backdrop-filter: blur(8px);
}

.splash-progress-wrap {
  animation: fadeUp 0.5s 0.40s var(--ease-out) both;
}

.splash-progress-label {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.82rem; font-weight: 700;
  color: rgba(255,255,255,0.80);
}

.splash-progress-track {
  height: 5px; border-radius: var(--r-full);
  background: rgba(255,255,255,0.15);
  overflow: hidden;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Animated dots in splash */
.splash-dots {
  display: flex; gap: 6px; margin-top: 14px;
}
.splash-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: rgba(255,255,255,0.40);
  animation: dotPulse 1.4s ease-in-out infinite;
}
.splash-dot:nth-child(2) { animation-delay: 0.2s; }
.splash-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotPulse {
  0%, 80%, 100% { opacity: 0.30; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1.2); background: rgba(255,255,255,0.80); }
}

/* ============================================================
   FOOTER
   ============================================================ */
.bps-footer {
  margin-top: 40px;
  padding: 18px 0;
  border-top: 1px solid rgba(245,95,0,0.10);
  display: flex; align-items: center; gap: 14px;
  color: rgba(74,40,0,0.45);
  font-size: 0.80rem;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.footer-dot {
  width: 4px; height: 4px; border-radius: 50%;
  background: rgba(245,95,0,0.30);
  flex-shrink: 0;
}
"""

st.markdown(f"<style>{MASTER_CSS}</style>", unsafe_allow_html=True)

# ======================================================================================
# UI HELPERS
# ======================================================================================
def section_header(title: str, subtitle: str = "", badge: str = "MODULE"):
    st.markdown(
        f"""
<div class="bps-section">
  <div class="sec-badge">{badge}</div>
  <h2 class="sec-title">{title}</h2>
  {f'<p class="sec-sub">{subtitle}</p>' if subtitle else ''}
  <div class="sec-rule"></div>
</div>
""",
        unsafe_allow_html=True,
    )

def banner(title: str, subtitle: str):
    st.markdown(
        f"""
<div class="bps-banner">
  <div class="bps-kicker">Badan Pusat Statistik</div>
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
      <div class="top-sub">BPS Bangka Belitung · Toolkit Analisis UMKM</div>
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
            <div style="width:270px; font-family:'Plus Jakarta Sans',sans-serif;">
              <div style="font-weight:800; font-size:14px; color:#1C0800; margin-bottom:6px;">{nama}</div>
              <div style="font-size:12px; color:#7A3C14;">{alamat}</div>
              <hr style="border:none;border-top:1px solid rgba(245,95,0,0.15); margin:8px 0;">
              <div style="font-size:12px; color:#3D1A00;">☎️ {telp if telp else "-"}</div>
              <div style="font-size:12px; margin-top:4px;">{link_html}</div>
            </div>
            """
            folium.CircleMarker(
                location=[float(r["Latitude"]), float(r["Longitude"])],
                radius=7, weight=2,
                color="#F55F00", fill=True,
                fill_color="#FF8330", fill_opacity=0.88,
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
# SPLASH SCREEN — Premium Redesign
# ======================================================================================
def splash_screen():
    st.markdown(
        """<style>
          [data-testid="stSidebar"]{ display:none !important; }
          [data-testid="stHeader"]{ background: transparent !important; }
          .block-container{ padding-top: 0 !important; }
          .block-container::before { display: none !important; }
          .block-container::after  { display: none !important; }
        </style>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="splash-outer">', unsafe_allow_html=True)
    st.markdown(
        """
<div class="splash-wrap">
  <div class="splash-ring-1"></div>
  <div class="splash-ring-2"></div>
  <div class="splash-ring-3"></div>
  <div class="splash-ring-4"></div>
  <div class="splash-inner">
    <div class="splash-logo-box">🏛️</div>
    <div class="splash-eyebrow">
      <span style="width:5px;height:5px;border-radius:50%;background:rgba(255,255,255,0.70);display:inline-block;"></span>
      BPS Bangka Belitung · UMKM Toolkit
    </div>
    <div class="splash-title">Dashboard UMKM BPS</div>
    <div class="splash-sub">Memuat modul analisis marketplace, visualisasi lokasi, dan sistem ekspor data terintegrasi…</div>
    <div class="splash-features">
      <span class="splash-feat">📊 Analisis Data</span>
      <span class="splash-feat">🗺️ Peta Interaktif</span>
      <span class="splash-feat">⬇️ Ekspor Excel</span>
      <span class="splash-feat">🔎 Filter Pintar</span>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Streamlit-native progress below the card
    st.markdown("<div style='max-width:820px; margin: 18px auto 0 auto;'>", unsafe_allow_html=True)
    prog = st.progress(0)
    status_text = st.empty()

    steps = [
        (0,  25, "⚙️  Menginisialisasi komponen sistem…"),
        (25, 55, "📦  Memuat modul Shopee & Tokopedia…"),
        (55, 80, "🗺️  Menyiapkan engine visualisasi peta…"),
        (80, 100,"✨  Finalisasi & optimasi tampilan…"),
    ]

    for start, end, label in steps:
        for i in range(start, end + 1, 2):
            prog.progress(i)
            status_text.markdown(
                f"<div style='text-align:center; font-family:\"Plus Jakarta Sans\",sans-serif; font-size:0.82rem; color:rgba(74,40,0,0.55); margin-top:8px;'>{label}</div>",
                unsafe_allow_html=True,
            )
            time.sleep(0.016)

    st.markdown("</div>", unsafe_allow_html=True)

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

if st.session_state.get("nav_target"):
    st.session_state["menu_nav"] = st.session_state["nav_target"]
    st.session_state["nav_target"] = None

if st.session_state.get("menu_nav") == "🏠 Dashboard":
    st.session_state["show_sidebar"] = False

if st.session_state.get("show_sidebar") and st.session_state.get("menu_nav") == "🏠 Dashboard":
    st.session_state["menu_nav"] = "🟠 Shopee"

# ======================================================================================
# SIDEBAR (Premium Redesign)
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
# TOPBAR
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
  <div class="geo-decor"></div>
  <div class="bps-badge">UMKM · BPS BABEL</div>
  <h1>Kontrol Pusat Analisis UMKM</h1>
  <p>Upload data dari marketplace atau Google Maps, cek ringkasan otomatis, lalu lanjutkan analisis mendalam dengan filter pintar dan visualisasi interaktif.</p>
  <div class="cta-row">
    <span class="bps-chip">🟠 Shopee</span>
    <span class="bps-chip">🟢 Tokopedia</span>
    <span class="bps-chip">📍 Google Maps</span>
    <span class="bps-chip">📊 Export Master</span>
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
                                    f"({int(pct*100)}%) · API calls: {fmt_int_id(api_calls)}"
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
<div class="bps-footer">
  <span style="font-size:1.1rem">🏛️</span>
  <span>Built with Streamlit</span>
  <span class="footer-dot"></span>
  <span>Badan Pusat Statistik · UMKM Toolkit</span>
  <span class="footer-dot"></span>
  <span>Bangka Belitung</span>
</div>
""",
    unsafe_allow_html=True,
)
