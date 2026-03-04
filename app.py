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
/* ============================================================
   DARK MODE
   ============================================================ */
body.dark-mode,
body.dark-mode [data-testid="stApp"],
body.dark-mode [data-testid="stAppViewContainer"] {
  background: linear-gradient(160deg, #180800 0%, #1F0E00 40%, #261200 70%, #1A0900 100%) !important;
}
body.dark-mode div[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(35,15,0,0.85) !important;
  border-color: rgba(245,95,0,0.20) !important;
}
body.dark-mode div[data-testid="metric-container"] {
  background: rgba(35,15,0,0.85) !important;
  border-color: rgba(245,95,0,0.20) !important;
}
body.dark-mode h1, body.dark-mode h2, body.dark-mode h3 { color: #FFF0E0 !important; }
body.dark-mode p, body.dark-mode span, body.dark-mode label { color: #D4A882 !important; }
body.dark-mode .topbar { background: rgba(30,12,0,0.90) !important; }
body.dark-mode [data-testid="stSidebar"] {
  background: linear-gradient(180deg,#1A0800 0%,#221000 60%,#1C0900 100%) !important;
}
body.dark-mode .bps-table tbody tr:nth-child(even) { background: rgba(40,18,0,0.50) !important; }
body.dark-mode .bps-table tbody td { color: #D4A882 !important; }
body.dark-mode .bps-table-wrap { background: rgba(28,12,0,0.90) !important; }
body.dark-mode .audit-card { background: rgba(35,15,0,0.85) !important; }
body.dark-mode .sb-stat { background: rgba(35,15,0,0.85) !important; }
body.dark-mode input, body.dark-mode textarea { background: #2A1000 !important; color: #FFD0A0 !important; }

/* dark toggle button */
.dark-toggle {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 7px 14px; border-radius: var(--r-full);
  border: 1.5px solid rgba(245,95,0,0.22);
  background: rgba(255,255,255,0.7);
  font-size: 0.80rem; font-weight: 800; cursor: pointer;
  color: var(--ink-700);
  transition: all 0.2s ease;
}
.dark-toggle:hover { background: rgba(245,95,0,0.08); border-color: var(--fire); }

/* ============================================================
   DASHBOARD — Module Cards
   ============================================================ */
.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.module-card {
  border-radius: var(--r-xl);
  padding: 24px 22px;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(20px);
  transition: all 0.25s var(--ease-spring);
  cursor: pointer;
  position: relative; overflow: hidden;
  text-decoration: none;
}

.module-card::before {
  content: "";
  position: absolute; top: 0; left: 0; right: 0;
  height: 3px;
  border-radius: var(--r-full) var(--r-full) 0 0;
}

.module-card.shopee::before  { background: linear-gradient(90deg,#F55F00,#FF8C00); }
.module-card.tokped::before  { background: linear-gradient(90deg,#00AA5B,#00D27A); }
.module-card.maps::before    { background: linear-gradient(90deg,#4285F4,#34A853); }
.module-card.export::before  { background: linear-gradient(90deg,#8B5CF6,#C4B5FD); }

.module-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
  border-color: rgba(245,95,0,0.28);
}

.module-card-icon {
  font-size: 2.2rem;
  margin-bottom: 14px;
  display: block;
  line-height: 1;
}

.module-card-title {
  font-family: 'Fraunces', serif;
  font-size: 1.15rem; font-weight: 700;
  color: var(--ink-900);
  margin-bottom: 6px;
}

.module-card-desc {
  font-size: 0.80rem;
  color: var(--ink-300);
  line-height: 1.5;
}

.module-card-count {
  margin-top: 14px;
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px; border-radius: var(--r-full);
  font-size: 0.74rem; font-weight: 800;
}

.module-card-count.ready {
  background: rgba(34,197,94,0.10);
  border: 1px solid rgba(34,197,94,0.22);
  color: #16A34A;
}

.module-card-count.empty {
  background: rgba(245,95,0,0.07);
  border: 1px solid rgba(245,95,0,0.15);
  color: var(--fire);
}

/* ============================================================
   WORKFLOW STEPS
   ============================================================ */
.workflow-row {
  display: flex; align-items: center; gap: 0;
  margin: 20px 0;
  flex-wrap: wrap; gap: 8px;
}

.workflow-step {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 18px; border-radius: var(--r-md);
  background: var(--glass);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-xs);
  backdrop-filter: blur(12px);
  flex: 1; min-width: 140px;
  transition: all 0.2s ease;
}

.workflow-step:hover { box-shadow: var(--shadow-sm); transform: translateY(-1px); }

.workflow-num {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, var(--fire), var(--amber));
  color: #fff; font-size: 0.78rem; font-weight: 900;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(245,95,0,0.30);
}

.workflow-text { font-size: 0.82rem; font-weight: 700; color: var(--ink-700); }
.workflow-sub  { font-size: 0.72rem; color: var(--ink-300); margin-top: 1px; }

.workflow-arrow {
  color: var(--ink-100); font-size: 1.2rem; font-weight: 300;
  flex-shrink: 0;
}

/* ============================================================
   UPLOAD ZONE (enhanced)
   ============================================================ */
.upload-info-card {
  border-radius: var(--r-lg);
  padding: 20px 22px;
  background: linear-gradient(135deg,
    rgba(245,95,0,0.06) 0%,
    rgba(255,179,71,0.04) 100%);
  border: 1px solid rgba(245,95,0,0.14);
  margin-bottom: 16px;
}

.upload-info-title {
  font-family: 'Fraunces', serif;
  font-size: 1.0rem; font-weight: 700;
  color: var(--ink-900); margin-bottom: 10px;
  display: flex; align-items: center; gap: 8px;
}

.upload-spec-row {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
}

.upload-spec {
  display: flex; align-items: flex-start; gap: 8px;
  font-size: 0.80rem; color: var(--ink-500);
  line-height: 1.45;
}

.upload-spec-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--fire); margin-top: 5px; flex-shrink: 0;
  box-shadow: 0 0 0 3px rgba(245,95,0,0.15);
}

/* Last upload timestamp */
.upload-timestamp {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 5px 12px; border-radius: var(--r-full);
  background: rgba(34,197,94,0.08);
  border: 1px solid rgba(34,197,94,0.20);
  font-size: 0.74rem; font-weight: 700;
  color: #16A34A;
  margin-top: 10px;
}

/* Reset button in sidebar */
.reset-btn-row { display: flex; gap: 8px; flex-direction: column; margin-top: 4px; }

/* ============================================================
   SIDEBAR RESET CARDS — Premium
   ============================================================ */
.sb-reset-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 6px 0 4px 0;
}

.sb-reset-card {
  border-radius: 14px;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  border: 1.5px solid rgba(245,95,0,0.12);
  background: rgba(255,255,255,0.80);
  box-shadow: 0 2px 8px rgba(245,95,0,0.05), 0 1px 3px rgba(0,0,0,0.04);
  transition: all 0.22s cubic-bezier(0.34,1.56,0.64,1);
  text-align: center;
  user-select: none;
}

.sb-reset-card:hover {
  border-color: rgba(245,95,0,0.32) !important;
  background: #fff !important;
  box-shadow: 0 6px 20px rgba(245,95,0,0.14), 0 2px 6px rgba(0,0,0,0.06) !important;
  transform: translateY(-2px);
}

.sb-reset-card:active { transform: scale(0.96) translateY(0); }

.sb-reset-card.danger {
  border-color: rgba(239,68,68,0.18) !important;
  background: rgba(255,248,248,0.85) !important;
}
.sb-reset-card.danger:hover {
  border-color: rgba(239,68,68,0.42) !important;
  background: rgba(255,240,240,0.95) !important;
  box-shadow: 0 6px 20px rgba(239,68,68,0.14) !important;
}

.sb-reset-icon {
  width: 36px; height: 36px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}
.sb-reset-icon.shopee  { background: linear-gradient(135deg,rgba(245,95,0,0.14),rgba(255,140,66,0.08)); }
.sb-reset-icon.tokped  { background: linear-gradient(135deg,rgba(0,170,91,0.12),rgba(0,210,122,0.07)); }
.sb-reset-icon.maps    { background: linear-gradient(135deg,rgba(66,133,244,0.12),rgba(52,168,83,0.08)); }
.sb-reset-icon.danger  { background: linear-gradient(135deg,rgba(239,68,68,0.14),rgba(252,165,165,0.08)); }

.sb-reset-label {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--ink-700);
  line-height: 1.3;
}
.sb-reset-label.danger-text { color: #DC2626 !important; }

.sb-reset-count {
  font-size: 0.64rem;
  font-weight: 700;
  color: var(--ink-300);
  line-height: 1;
}
.sb-reset-count.has-data {
  color: #16A34A;
  background: rgba(34,197,94,0.10);
  border: 1px solid rgba(34,197,94,0.20);
  border-radius: 999px;
  padding: 1px 7px;
}
.sb-reset-count.no-data {
  color: var(--ink-100);
}

/* Sidebar section divider */
.sb-section-divider {
  display: flex; align-items: center; gap: 8px;
  margin: 14px 0 10px 0;
}
.sb-section-divider-line {
  flex: 1; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(245,95,0,0.18), transparent);
}

/* Pengaturan checkboxes */
.sb-settings-row {
  display: flex; flex-direction: column; gap: 4px;
  padding: 4px 0;
}

/* Footer enhanced */
.sb-footer-v2 {
  margin-top: 12px;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(245,95,0,0.12);
}
.sb-footer-top {
  padding: 14px 16px 10px;
  background: linear-gradient(135deg, rgba(245,95,0,0.07), rgba(255,179,71,0.05));
  display: flex; align-items: center; gap: 10px;
}
.sb-footer-logo {
  width: 32px; height: 32px; border-radius: 9px;
  background: linear-gradient(135deg, var(--fire), var(--amber));
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(245,95,0,0.28);
}
.sb-footer-name {
  font-family: 'Fraunces', serif !important;
  font-size: 0.88rem; font-weight: 700;
  color: var(--ink-900) !important; line-height: 1.2;
}
.sb-footer-sub {
  font-size: 0.68rem; font-weight: 600;
  color: var(--ink-300) !important; margin-top: 1px;
}
.sb-footer-bottom {
  padding: 8px 16px;
  background: rgba(245,95,0,0.04);
  border-top: 1px solid rgba(245,95,0,0.08);
  font-size: 0.68rem; font-weight: 700;
  color: var(--ink-100) !important;
  text-align: center; letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* ============================================================
   FILTER BAR — Enhanced
   ============================================================ */
.filter-bar-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 14px;
}
.filter-bar-title {
  font-family: 'Fraunces', serif;
  font-size: 1.05rem; font-weight: 700; color: var(--ink-900);
  display: flex; align-items: center; gap: 8px;
}
.filter-active-badge {
  padding: 2px 10px; border-radius: var(--r-full);
  background: rgba(245,95,0,0.10); border: 1px solid rgba(245,95,0,0.22);
  font-size: 0.70rem; font-weight: 800; color: var(--fire);
}

/* ============================================================
   EXPORT PAGE — Premium
   ============================================================ */
.export-source-card {
  border-radius: var(--r-lg);
  padding: 20px 22px;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-xs);
  backdrop-filter: blur(16px);
  display: flex; align-items: center; justify-content: space-between;
  transition: all 0.2s ease;
}
.export-source-card:hover { box-shadow: var(--shadow-sm); transform: translateY(-1px); }
.export-source-card.ready { border-left: 4px solid #22C55E !important; }
.export-source-card.empty { border-left: 4px solid rgba(245,95,0,0.35) !important; opacity: 0.7; }

.export-source-left { display: flex; align-items: center; gap: 14px; }
.export-source-icon { font-size: 1.8rem; }
.export-source-name {
  font-family: 'Fraunces', serif;
  font-size: 1.0rem; font-weight: 700; color: var(--ink-900);
}
.export-source-meta { font-size: 0.78rem; color: var(--ink-300); margin-top: 2px; }
.export-source-badge {
  padding: 4px 12px; border-radius: var(--r-full);
  font-size: 0.74rem; font-weight: 800;
}
.export-source-badge.ready { background: rgba(34,197,94,0.10); border: 1px solid rgba(34,197,94,0.22); color: #16A34A; }
.export-source-badge.empty { background: rgba(245,95,0,0.07); border: 1px solid rgba(245,95,0,0.15); color: var(--ink-300); }

.export-hero {
  border-radius: var(--r-xl);
  padding: 32px 36px;
  margin-bottom: 20px;
  background: linear-gradient(135deg,
    rgba(139,92,246,0.10) 0%,
    rgba(245,95,0,0.08) 50%,
    rgba(255,179,71,0.06) 100%);
  border: 1px solid rgba(139,92,246,0.15);
  box-shadow: var(--shadow-sm);
  display: flex; align-items: center; gap: 28px;
}
.export-hero-icon {
  font-size: 3.5rem; flex-shrink: 0;
  filter: drop-shadow(0 8px 16px rgba(139,92,246,0.3));
}
.export-hero-title {
  font-family: 'Fraunces', serif;
  font-size: 1.55rem; font-weight: 900; color: var(--ink-900);
  margin-bottom: 6px; letter-spacing: -0.025em;
}
.export-hero-sub { font-size: 0.90rem; color: var(--ink-300); line-height: 1.6; }


/* ============================================================
   CUSTOM HTML TABLE
   ============================================================ */
.bps-table-wrap {
  width: 100%;
  overflow-x: auto;
  border-radius: var(--r-lg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-sm);
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(16px);
  margin-bottom: 16px;
}
.bps-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.84rem;
}
.bps-table thead tr {
  background: linear-gradient(135deg, #F55F00 0%, #FF8330 60%, #FFB347 100%);
}
.bps-table thead th {
  padding: 13px 16px;
  text-align: left;
  font-weight: 800;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #fff !important;
  white-space: nowrap;
}
.bps-table thead th:first-child { border-radius: var(--r-sm) 0 0 0; }
.bps-table thead th:last-child  { border-radius: 0 var(--r-sm) 0 0; }
.bps-table tbody tr {
  border-bottom: 1px solid rgba(245,95,0,0.06);
  transition: background 0.15s ease;
}
.bps-table tbody tr:last-child { border-bottom: none; }
.bps-table tbody tr:hover { background: rgba(245,95,0,0.04) !important; }
.bps-table tbody tr:nth-child(even) { background: rgba(255,248,242,0.60); }
.bps-table tbody td {
  padding: 11px 16px;
  color: var(--ink-700) !important;
  vertical-align: middle;
}
.bps-table .td-toko { font-weight: 700; color: var(--ink-900) !important; }
.bps-table .td-harga {
  font-family: 'Fraunces', serif;
  font-weight: 700; color: var(--fire) !important; white-space: nowrap;
}
.bps-table .td-link a {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 10px; border-radius: var(--r-full);
  font-size: 0.74rem; font-weight: 700;
  background: rgba(245,95,0,0.08); border: 1px solid rgba(245,95,0,0.18);
  color: var(--fire) !important; text-decoration: none; white-space: nowrap;
  transition: all 0.15s ease;
}
.bps-table .td-link a:hover { background: var(--fire); color: #fff !important; border-color: var(--fire); }
.tipe-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: var(--r-full);
  font-size: 0.72rem; font-weight: 800; white-space: nowrap;
}
.tipe-online { background: rgba(34,197,94,0.10); border: 1px solid rgba(34,197,94,0.22); color: #16A34A !important; }
.tipe-fisik  { background: rgba(59,130,246,0.10); border: 1px solid rgba(59,130,246,0.22); color: #2563EB !important; }
.tipe-other  { background: rgba(245,95,0,0.08);  border: 1px solid rgba(245,95,0,0.18);  color: var(--fire) !important; }
.td-num { color: var(--ink-100) !important; font-size: 0.72rem; font-weight: 700; text-align: right; padding-right: 8px !important; width: 36px; }
.td-truncate { max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ============================================================
   AUDIT CARDS
   ============================================================ */
.audit-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px; margin: 4px 0;
}
.audit-card {
  border-radius: var(--r-md); padding: 18px 20px;
  display: flex; align-items: flex-start; gap: 14px;
  background: var(--glass); border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-xs); backdrop-filter: blur(12px);
  transition: all 0.2s ease;
}
.audit-card:hover { box-shadow: var(--shadow-sm); transform: translateY(-2px); border-color: rgba(245,95,0,0.22); }
.audit-icon { width: 42px; height: 42px; border-radius: var(--r-sm); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; }
.audit-icon.blue   { background: rgba(59,130,246,0.12); }
.audit-icon.green  { background: rgba(34,197,94,0.12);  }
.audit-icon.orange { background: rgba(245,95,0,0.10);   }
.audit-icon.red    { background: rgba(239,68,68,0.10);  }
.audit-icon.amber  { background: rgba(245,158,11,0.10); }
.audit-icon.purple { background: rgba(139,92,246,0.10); }
.audit-val { font-family: 'Fraunces', serif; font-size: 1.65rem; font-weight: 900; line-height: 1.1; color: var(--ink-900); }
.audit-lbl { font-size: 0.74rem; font-weight: 700; color: var(--ink-300); margin-top: 2px; line-height: 1.4; }
.quality-bar-wrap { margin: 20px 0 4px 0; }
.quality-header { display: flex; justify-content: space-between; font-size: 0.80rem; font-weight: 700; color: var(--ink-500); margin-bottom: 8px; }
.quality-track { height: 10px; border-radius: var(--r-full); background: rgba(245,95,0,0.10); overflow: hidden; }
.quality-fill { height: 100%; border-radius: var(--r-full); background: linear-gradient(90deg, #22C55E, #86EFAC); transition: width 1s ease; }
.quality-fill.mid { background: linear-gradient(90deg, #F59E0B, #FCD34D); }
.quality-fill.low { background: linear-gradient(90deg, #EF4444, #FCA5A5); }

/* ============================================================
   DB TAB HEADER
   ============================================================ */
.db-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; flex-wrap: wrap; gap: 10px; }
.db-title { font-family: 'Fraunces', serif; font-size: 1.1rem; font-weight: 700; color: var(--ink-900); }
.db-count { display: inline-flex; align-items: center; gap: 6px; padding: 5px 14px; border-radius: var(--r-full); background: rgba(245,95,0,0.08); border: 1px solid rgba(245,95,0,0.18); font-size: 0.78rem; font-weight: 800; color: var(--fire); }
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
# PREMIUM TABLE RENDERER
# ======================================================================================
def render_premium_table(df: pd.DataFrame, max_rows: int = 200, source: str = ""):
    df_show = df.head(max_rows).copy()
    cols = list(df_show.columns)
    th_html = "".join(f"<th>{c}</th>" for c in cols)

    def _tipe_badge(val):
        v = str(val)
        if "Online" in v or "Rumahan" in v:
            return '<span class="tipe-badge tipe-online">🏠 Online</span>'
        elif "Fisik" in v:
            return '<span class="tipe-badge tipe-fisik">🏬 Toko Fisik</span>'
        else:
            return f'<span class="tipe-badge tipe-other">❓ {v[:18]}</span>'

    def _cell(col, val):
        v = str(val) if not pd.isna(val) else "-"
        cl = col.lower()
        if cl == "harga":
            try:
                num = int(float(str(val).replace("Rp","").replace(".","").replace(",","").strip()))
                return "<td class='td-harga'>Rp " + f"{num:,}".replace(",",".") + "</td>"
            except:
                return f"<td class='td-harga'>{v}</td>"
        elif cl == "tipe usaha":
            return f"<td>{_tipe_badge(v)}</td>"
        elif cl == "link":
            if v and v not in ["-","nan","None"] and v.startswith("http"):
                short = v.replace("https://","").replace("http://","")[:28] + "…"
                return f'<td class="td-link"><a href="{v}" target="_blank">🔗 {short}</a></td>'
            return "<td>—</td>"
        elif cl == "nama toko":
            return f"<td class='td-toko'>{v[:30]}</td>"
        elif cl == "nama produk":
            trunc = v[:55] + ("…" if len(v) > 55 else "")
            return f'<td class="td-truncate" title="{v}">{trunc}</td>'
        elif cl in ["latitude","longitude"]:
            return f'<td style="color:var(--ink-300);font-size:0.78rem;font-family:monospace">{v}</td>'
        else:
            trunc = v[:40] + ("…" if len(v) > 40 else "")
            return f'<td class="td-truncate" title="{v}">{trunc}</td>'

    rows_html = ""
    for i, (_, row) in enumerate(df_show.iterrows()):
        cells = "".join(_cell(c, row[c]) for c in cols)
        rows_html += f"<tr><td class='td-num'>{i+1}</td>{cells}</tr>"

    total = len(df)
    shown = len(df_show)
    note = f" <span style='color:var(--ink-300);font-size:0.78rem'>(menampilkan {shown:,} dari {total:,})</span>" if total > max_rows else ""
    html = f"""
<div class="db-header">
  <span class="db-title">📋 Data {source}{note}</span>
  <span class="db-count">🗂 {total:,} baris total</span>
</div>
<div class="bps-table-wrap" style="max-height:480px;overflow-y:auto;">
<table class="bps-table">
  <thead><tr><th>#</th>{th_html}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>
</div>"""
    st.markdown(html, unsafe_allow_html=True)

# ======================================================================================
# PREMIUM AUDIT RENDERER
# ======================================================================================
def render_audit_cards(audit: dict, source: str = ""):
    fc   = audit.get("file_count", 0)
    tot  = audit.get("total_rows", audit.get("rows_in", 0))
    val  = audit.get("valid_rows", audit.get("rows_out", 0))
    luar = audit.get("luar_wilayah", 0)
    err  = audit.get("error_harga", 0)
    api  = audit.get("api_calls", None)
    dedup = audit.get("dedup_removed", 0)
    inv_c = audit.get("invalid_coord", 0)
    inv_l = audit.get("invalid_link", 0)
    empty = audit.get("empty_name", 0)
    miss  = audit.get("missing_cols", [])

    quality_pct = round(val / tot * 100, 1) if tot > 0 else 0
    q_class = "low" if quality_pct < 50 else ("mid" if quality_pct < 80 else "")

    st.markdown(f"""
<div class="quality-bar-wrap">
  <div class="quality-header">
    <span>📊 Kualitas Data {source}</span>
    <span style="color:var(--fire);font-weight:900">{quality_pct}% valid</span>
  </div>
  <div class="quality-track">
    <div class="quality-fill {q_class}" style="width:{quality_pct}%"></div>
  </div>
</div>""", unsafe_allow_html=True)

    cards = [
        ("blue",   "📂", str(fc),   "File Diproses"),
        ("orange", "📥", f"{tot:,}".replace(",","."), "Total Baris Masuk"),
        ("green",  "✅", f"{val:,}".replace(",","."), "Baris Valid (Babel)"),
    ]
    if luar:   cards.append(("amber",  "🗺️", f"{luar:,}".replace(",","."), "Luar Wilayah Babel"))
    if err:    cards.append(("red",    "⚠️", f"{err:,}".replace(",","."),  "Error Parsing Harga"))
    if api is not None: cards.append(("purple","🔌", f"{api:,}".replace(",","."), "API Calls Shopee"))
    if dedup:  cards.append(("amber",  "🧽", f"{dedup:,}".replace(",","."), "Duplikat Dihapus"))
    if inv_c:  cards.append(("red",    "📍", f"{inv_c:,}".replace(",","."), "Koordinat Invalid"))
    if inv_l:  cards.append(("amber",  "🔗", f"{inv_l:,}".replace(",","."), "Link Kosong/Invalid"))
    if empty:  cards.append(("red",    "🏷️", f"{empty:,}".replace(",","."), "Nama Usaha Kosong"))

    cards_html = "".join(f"""<div class="audit-card">
  <div class="audit-icon {color}">{icon}</div>
  <div><div class="audit-val">{vs}</div><div class="audit-lbl">{lbl}</div></div>
</div>""" for color, icon, vs, lbl in cards)

    st.markdown(f'<div class="audit-grid">{cards_html}</div>', unsafe_allow_html=True)

    if miss:
        st.markdown(f"""<div style="margin-top:14px;padding:12px 16px;border-radius:var(--r-md);
  background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.20);">
  <span style="font-size:0.82rem;font-weight:700;color:#B45309;">
    ⚠️ Kolom tidak ditemukan: <code>{", ".join(miss)}</code>
  </span></div>""", unsafe_allow_html=True)

# ======================================================================================
# SESSION STATE
# ======================================================================================
def ensure_state():
    defaults = {
        "data_shopee": None, "audit_shopee": {},
        "data_tokped": None, "audit_tokped": {},
        "data_maps": None,   "audit_maps": {},
        "upload_time_shopee": None,
        "upload_time_tokped": None,
        "upload_time_maps":   None,
        "show_sidebar": False,
        "menu_nav": "🏠 Dashboard",
        "nav_target": None,
        "__boot__": False,
        "__splash_done__": False,
        "show_tips": True,
        "fast_mode": False,
        "dark_mode": False,
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
    # ── Encode logo.png → base64 so it works as inline <img> ──────────────────
    logo_html = ""
    if os.path.exists("logo.png"):
        import base64
        with open("logo.png", "rb") as _f:
            _b64 = base64.b64encode(_f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{_b64}" class="sp-logo-img" alt="Logo BPS">'
    else:
        logo_html = '<div class="sp-logo-emoji">🏛️</div>'

    # ── Step labels for JS progress animation ─────────────────────────────────
    steps_js = [
        (0,  28, "Menginisialisasi komponen sistem…"),
        (28, 56, "Memuat modul Shopee & Tokopedia…"),
        (56, 82, "Menyiapkan engine visualisasi peta…"),
        (82, 100,"Finalisasi &amp; optimasi tampilan…"),
    ]
    steps_json = str(steps_js).replace("'", '"')

    SPLASH_HTML = f"""
<style>
  /* ── Kill ALL streamlit chrome ───────────────────────────── */
  [data-testid="stSidebar"],
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  footer {{ display: none !important; }}

  html, body,
  [data-testid="stApp"],
  [data-testid="stAppViewContainer"],
  .main, section.main, .block-container {{
    background: #FFF4E8 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
  }}

  .block-container::before,
  .block-container::after {{ display: none !important; }}

  /* ── Fullscreen overlay ──────────────────────────────────── */
  #splash-overlay {{
    position: fixed;
    inset: 0;
    z-index: 999999;
    background: linear-gradient(160deg, #FFF8F2 0%, #FFF0E0 50%, #FFE8CC 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Plus Jakarta Sans', 'Segoe UI', system-ui, sans-serif;
  }}

  /* Soft blobs */
  #splash-overlay::before {{
    content: "";
    position: absolute;
    top: -10%; left: -10%;
    width: 55vw; height: 55vw;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(245,95,0,0.09) 0%, transparent 65%);
    pointer-events: none;
  }}
  #splash-overlay::after {{
    content: "";
    position: absolute;
    bottom: -10%; right: -8%;
    width: 45vw; height: 45vw;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,163,71,0.08) 0%, transparent 65%);
    pointer-events: none;
  }}

  /* ── Card ────────────────────────────────────────────────── */
  .sp-card {{
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    width: min(460px, 90vw);
    padding: 48px 40px 40px;
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(245,95,0,0.14);
    border-radius: 32px;
    box-shadow:
      0 32px 80px rgba(245,95,0,0.14),
      0 8px 24px rgba(0,0,0,0.06),
      inset 0 1px 0 rgba(255,255,255,0.9);
    backdrop-filter: blur(24px) saturate(1.4);
    animation: spCardIn 0.65s cubic-bezier(0.34,1.56,0.64,1) both;
  }}

  @keyframes spCardIn {{
    from {{ opacity:0; transform: translateY(32px) scale(0.94); }}
    to   {{ opacity:1; transform: translateY(0)    scale(1);    }}
  }}

  /* ── Logo ────────────────────────────────────────────────── */
  .sp-logo-wrap {{
    width: 110px; height: 110px;
    border-radius: 28px;
    background: linear-gradient(135deg, #F55F00 0%, #FF8330 60%, #FFB347 100%);
    box-shadow:
      0 16px 48px rgba(245,95,0,0.38),
      0 4px 12px rgba(245,95,0,0.20),
      inset 0 1px 0 rgba(255,255,255,0.22);
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    animation: spLogoIn 0.55s 0.15s cubic-bezier(0.34,1.56,0.64,1) both;
    flex-shrink: 0;
  }}

  .sp-logo-wrap::after {{
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.22) 0%, transparent 55%);
    border-radius: inherit;
    pointer-events: none;
  }}

  .sp-logo-img {{
    width: 70px; height: 70px;
    object-fit: contain;
    position: relative; z-index: 1;
    filter: brightness(0) invert(1);
  }}

  .sp-logo-emoji {{
    font-size: 2.8rem;
    position: relative; z-index: 1;
    line-height: 1;
  }}

  @keyframes spLogoIn {{
    from {{ opacity:0; transform: scale(0.7) rotate(-8deg); }}
    to   {{ opacity:1; transform: scale(1)   rotate(0deg);  }}
  }}

  /* ── Text ────────────────────────────────────────────────── */
  .sp-eyebrow {{
    font-size: 0.68rem; font-weight: 800;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: rgba(245,95,0,0.75);
    margin-bottom: 10px;
    animation: spFadeUp 0.5s 0.25s ease both;
  }}

  .sp-title {{
    font-family: 'Fraunces','Georgia',serif;
    font-size: clamp(1.55rem, 4vw, 1.9rem);
    font-weight: 900;
    color: #1C0800;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin: 0 0 8px 0;
    animation: spFadeUp 0.5s 0.30s ease both;
  }}

  .sp-sub {{
    font-size: 0.88rem;
    color: rgba(74,40,0,0.55);
    line-height: 1.6;
    margin: 0 0 28px 0;
    animation: spFadeUp 0.5s 0.35s ease both;
  }}

  @keyframes spFadeUp {{
    from {{ opacity:0; transform: translateY(14px); }}
    to   {{ opacity:1; transform: translateY(0);    }}
  }}

  /* ── Progress bar ────────────────────────────────────────── */
  .sp-progress-wrap {{
    width: 100%;
    animation: spFadeUp 0.5s 0.40s ease both;
  }}

  .sp-progress-header {{
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 8px;
  }}

  .sp-status-label {{
    font-size: 0.78rem; font-weight: 600;
    color: rgba(74,40,0,0.55);
  }}

  .sp-pct {{
    font-size: 0.78rem; font-weight: 800;
    color: #F55F00;
    font-variant-numeric: tabular-nums;
  }}

  .sp-track {{
    width: 100%; height: 7px;
    border-radius: 999px;
    background: rgba(245,95,0,0.12);
    overflow: hidden;
  }}

  .sp-fill {{
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #F55F00, #FF8330, #FFB347);
    background-size: 200% 100%;
    width: 0%;
    transition: width 0.18s ease;
    animation: shimmerFill 1.8s linear infinite;
  }}

  @keyframes shimmerFill {{
    0%   {{ background-position: 0%   50%; }}
    100% {{ background-position: 200% 50%; }}
  }}

  /* ── Feature pills ───────────────────────────────────────── */
  .sp-pills {{
    display: flex; flex-wrap: wrap; justify-content: center;
    gap: 8px; margin-bottom: 28px;
    animation: spFadeUp 0.5s 0.38s ease both;
  }}

  .sp-pill {{
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 0.76rem; font-weight: 700;
    color: #F55F00;
    background: rgba(245,95,0,0.08);
    border: 1px solid rgba(245,95,0,0.18);
  }}

  /* ── Dots ────────────────────────────────────────────────── */
  .sp-dots {{
    display: flex; gap: 5px; justify-content: center;
    margin-top: 14px;
  }}
  .sp-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: rgba(245,95,0,0.25);
    animation: dotBounce 1.4s ease-in-out infinite;
  }}
  .sp-dot:nth-child(2) {{ animation-delay: 0.20s; }}
  .sp-dot:nth-child(3) {{ animation-delay: 0.40s; }}
  @keyframes dotBounce {{
    0%,80%,100% {{ transform:scale(0.75); opacity:0.3; }}
    40%          {{ transform:scale(1.2);  opacity:1; background:#F55F00; }}
  }}
</style>

<div id="splash-overlay">
  <div class="sp-card">
    <div class="sp-logo-wrap">{logo_html}</div>
    <div class="sp-eyebrow">BPS Bangka Belitung · UMKM Toolkit</div>
    <div class="sp-title">Dashboard UMKM BPS</div>
    <div class="sp-sub">Memuat modul analisis marketplace, visualisasi lokasi, dan sistem ekspor data…</div>
    <div class="sp-pills">
      <span class="sp-pill">📊 Analisis Data</span>
      <span class="sp-pill">🗺️ Peta Interaktif</span>
      <span class="sp-pill">⬇️ Ekspor Excel</span>
      <span class="sp-pill">🔎 Filter Pintar</span>
    </div>
    <div class="sp-progress-wrap">
      <div class="sp-progress-header">
        <span class="sp-status-label" id="sp-label">Menginisialisasi…</span>
        <span class="sp-pct" id="sp-pct">0%</span>
      </div>
      <div class="sp-track"><div class="sp-fill" id="sp-fill"></div></div>
      <div class="sp-dots">
        <div class="sp-dot"></div>
        <div class="sp-dot"></div>
        <div class="sp-dot"></div>
      </div>
    </div>
  </div>
</div>

<script>
(function(){{
  var steps = {steps_json};
  var fill  = document.getElementById('sp-fill');
  var label = document.getElementById('sp-label');
  var pct   = document.getElementById('sp-pct');
  var si = 0, cur = 0;

  function tick() {{
    if (si >= steps.length) return;
    var s = steps[si];
    label.textContent = s[2];
    cur += 1;
    if (cur > s[1]) {{ si++; if(si>=steps.length) return; }}
    var v = Math.min(cur, 100);
    fill.style.width = v + '%';
    pct.textContent  = v + '%';
    setTimeout(tick, 28);
  }}
  tick();
}})();
</script>
"""

    st.markdown(SPLASH_HTML, unsafe_allow_html=True)

    # Python-side sleep to let the JS animation run + server do its work
    steps_py = [
        (0,  28, "Menginisialisasi komponen sistem…"),
        (28, 56, "Memuat modul Shopee & Tokopedia…"),
        (56, 82, "Menyiapkan engine visualisasi peta…"),
        (82, 100,"Finalisasi & optimasi tampilan…"),
    ]
    for _s, _e, _lbl in steps_py:
        span = _e - _s
        time.sleep(span * 0.018)   # ~0.5 s per phase → ~2 s total

    st.session_state["__splash_done__"] = True
    st.rerun()

if not st.session_state["__splash_done__"]:
    splash_screen()

# ======================================================================================
# RESET HANDLER (via query params from HTML card clicks)
# ======================================================================================
_qp = st.query_params.to_dict()
_rst_action = _qp.pop("rst", None)
if _rst_action:
    if _rst_action == "shp":
        st.session_state.data_shopee = None; st.session_state.audit_shopee = {}; st.session_state.upload_time_shopee = None
        st.toast("Data Shopee dihapus")
    elif _rst_action == "tkp":
        st.session_state.data_tokped = None; st.session_state.audit_tokped = {}; st.session_state.upload_time_tokped = None
        st.toast("Data Tokopedia dihapus")
    elif _rst_action == "maps":
        st.session_state.data_maps = None; st.session_state.audit_maps = {}; st.session_state.upload_time_maps = None
        st.toast("Data Maps dihapus")
    elif _rst_action == "all":
        for _k in ["data_shopee","data_tokped","data_maps","audit_shopee","audit_tokped","audit_maps",
                   "upload_time_shopee","upload_time_tokped","upload_time_maps"]:
            st.session_state[_k] = None if ("data" in _k or "time" in _k) else {}
        st.toast("Semua data dihapus")
    st.query_params.clear()
    st.rerun()

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

        # Reset cards using query param navigation
        _shp_n2 = 0 if st.session_state.data_shopee is None else len(st.session_state.data_shopee)
        _tkp_n2 = 0 if st.session_state.data_tokped is None else len(st.session_state.data_tokped)
        _mp_n2  = 0 if st.session_state.data_maps   is None else len(st.session_state.data_maps)
        _all_n2 = _shp_n2 + _tkp_n2 + _mp_n2

        def _rc(n, accent="245,95,0"):
            if n > 0:
                return (
                    '<div style="margin-top:5px;padding:2px 8px;border-radius:99px;font-size:0.62rem;'
                    'font-weight:800;background:rgba(34,197,94,0.11);border:1px solid rgba(34,197,94,0.24);'
                    'color:#15803D;display:inline-block;">✓ ' + fmt_int_id(n) + ' data</div>'
                )
            return (
                '<div style="margin-top:5px;padding:2px 8px;border-radius:99px;font-size:0.62rem;'
                'font-weight:700;color:rgba(74,40,0,0.28);display:inline-block;">Kosong</div>'
            )

        def _rst_card(href, icon_html, label, count_html,
                      bd_color, bg, icon_bg, hover_shadow,
                      label_color="#3D1A00", danger=False):
            return (
                '<a href="' + href + '" target="_self" style="text-decoration:none;display:block;">'
                '<div class="_rst_card" style="'
                'border-radius:14px;padding:14px 10px 12px;'
                'display:flex;flex-direction:column;align-items:center;gap:0;'
                'border:1.5px solid ' + bd_color + ';'
                'background:' + bg + ';'
                'box-shadow:0 2px 8px rgba(0,0,0,0.04);'
                'transition:all 0.18s ease;text-align:center;cursor:pointer;">'
                '<div style="width:40px;height:40px;border-radius:11px;'
                'background:' + icon_bg + ';'
                'display:flex;align-items:center;justify-content:center;font-size:1.15rem;'
                'box-shadow:0 2px 8px rgba(0,0,0,0.06);">' + icon_html + '</div>'
                '<div style="font-family:Plus Jakarta Sans,sans-serif;font-size:0.73rem;font-weight:800;'
                'color:' + label_color + ';margin-top:8px;line-height:1.2;">' + label + '</div>'
                + count_html +
                '</div></a>'
            )

        _cards = (
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:8px 0 4px;">'
            + _rst_card("?rst=shp",  "&#128992;", "Shopee",
                        _rc(_shp_n2),
                        "rgba(245,95,0,0.14)", "rgba(255,255,255,0.90)",
                        "linear-gradient(135deg,rgba(245,95,0,0.13),rgba(255,140,66,0.07))",
                        "rgba(245,95,0,0.18)")
            + _rst_card("?rst=tkp",  "&#129026;", "Tokopedia",
                        _rc(_tkp_n2),
                        "rgba(0,170,91,0.14)", "rgba(255,255,255,0.90)",
                        "linear-gradient(135deg,rgba(0,170,91,0.13),rgba(0,210,122,0.07))",
                        "rgba(0,170,91,0.18)")
            + _rst_card("?rst=maps", "&#128205;", "Google Maps",
                        _rc(_mp_n2),
                        "rgba(66,133,244,0.14)", "rgba(255,255,255,0.90)",
                        "linear-gradient(135deg,rgba(66,133,244,0.13),rgba(52,168,83,0.07))",
                        "rgba(66,133,244,0.18)")
            + _rst_card("?rst=all",  "&#128465;", "Reset Semua",
                        '<div style="margin-top:5px;padding:2px 8px;border-radius:99px;font-size:0.62rem;font-weight:700;color:rgba(220,38,38,0.55);display:inline-block;">Hapus semua</div>',
                        "rgba(239,68,68,0.16)", "rgba(255,248,248,0.92)",
                        "linear-gradient(135deg,rgba(239,68,68,0.14),rgba(252,165,165,0.08))",
                        "rgba(239,68,68,0.24)",
                        label_color="#DC2626", danger=True)
            + '</div>'
        )
        st.markdown(_cards, unsafe_allow_html=True)

        # Hover effect via injected style
        st.markdown(
            "<style>"
            "[data-testid=stSidebar] ._rst_card:hover{"
            "transform:translateY(-2px) !important;"
            "box-shadow:0 8px 24px rgba(0,0,0,0.10) !important;"
            "border-color:rgba(245,95,0,0.32) !important;}"
            "</style>",
            unsafe_allow_html=True
        )

        st.divider()

        st.markdown(
            '<div class="sb-section-divider">'
            '<div class="sb-section-divider-line"></div>'
            '<div class="sb-nav-label" style="margin:0;padding:0;white-space:nowrap;">PENGATURAN</div>'
            '<div class="sb-section-divider-line"></div>'
            '</div>',
            unsafe_allow_html=True
        )
        with st.expander("Opsi Tampilan & Performa", expanded=False):
            st.checkbox("Tampilkan tips cepat", value=st.session_state.get("show_tips", True), key="show_tips")
            st.checkbox("Mode cepat (kurangi chart)", value=st.session_state.get("fast_mode", False), key="fast_mode")
            st.checkbox("Dark Mode (eksperimental)", value=st.session_state.get("dark_mode", False), key="dark_mode")
            if st.session_state.get("dark_mode"):
                st.markdown('<script>document.body.classList.add("dark-mode")</script>', unsafe_allow_html=True)

        _total_sb = _shp_n2 + _tkp_n2 + _mp_n2
        st.markdown(
            '<div class="sb-footer-v2">'
            '<div class="sb-footer-top">'
            '<div class="sb-footer-logo">&#127963;</div>'
            '<div>'
            '<div class="sb-footer-name">BPS Bangka Belitung</div>'
            '<div class="sb-footer-sub">Dashboard UMKM v2.1</div>'
            '</div>'
            '</div>'
            '<div class="sb-footer-bottom">'
            + fmt_int_id(_total_sb) + ' data dimuat &nbsp;&middot;&nbsp; Data Statistik Berkualitas'
            '</div>'
            '</div>',
            unsafe_allow_html=True
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

    df_shp = st.session_state.data_shopee
    df_tkp = st.session_state.data_tokped
    df_maps = st.session_state.data_maps
    shp_n = 0 if df_shp is None else len(df_shp)
    tkp_n = 0 if df_tkp is None else len(df_tkp)
    mp_n  = 0 if df_maps is None else len(df_maps)
    total_all = shp_n + tkp_n + mp_n

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(
        f"""
<div class="bps-hero">
  <div class="geo-decor"></div>
  <div class="bps-badge">UMKM · BPS BABEL · v2.1</div>
  <h1>Kontrol Pusat Analisis UMKM</h1>
  <p>Upload data marketplace atau Google Maps, analisis dengan filter pintar, visualisasikan di peta interaktif, lalu ekspor ke Excel — semua dalam satu platform.</p>
  <div class="cta-row">
    <span class="bps-chip">🟠 Shopee</span>
    <span class="bps-chip">🟢 Tokopedia</span>
    <span class="bps-chip">📍 Google Maps</span>
    <span class="bps-chip">📊 Export Master</span>
    <span class="bps-chip" style="background:rgba(255,255,255,0.24)">📦 {fmt_int_id(total_all)} Data Loaded</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # ── KPI Row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    k1.metric("📦 Total Data",   fmt_int_id(total_all), delta="All sources" if total_all > 0 else None)
    k2.metric("🟠 Shopee",       fmt_int_id(shp_n),     delta="Loaded ✓" if shp_n > 0 else "Belum upload")
    k3.metric("🟢 Tokopedia",    fmt_int_id(tkp_n),     delta="Loaded ✓" if tkp_n > 0 else "Belum upload")
    k4.metric("📍 Google Maps",  fmt_int_id(mp_n),      delta="Loaded ✓" if mp_n > 0 else "Belum upload")

    # ── Workflow guide ────────────────────────────────────────────────────────
    st.markdown("""
<div style="margin: 6px 0 4px 0;">
  <div style="font-family:'Fraunces',serif; font-size:1.05rem; font-weight:700; color:var(--ink-900); margin-bottom:12px;">
    🗺️ Alur Kerja yang Disarankan
  </div>
  <div class="workflow-row">
    <div class="workflow-step">
      <div class="workflow-num">1</div>
      <div><div class="workflow-text">Upload CSV</div><div class="workflow-sub">Shopee, Tokopedia, atau Maps</div></div>
    </div>
    <div class="workflow-arrow">→</div>
    <div class="workflow-step">
      <div class="workflow-num">2</div>
      <div><div class="workflow-text">Filter & Cari</div><div class="workflow-sub">Wilayah, tipe, harga</div></div>
    </div>
    <div class="workflow-arrow">→</div>
    <div class="workflow-step">
      <div class="workflow-num">3</div>
      <div><div class="workflow-text">Analisis</div><div class="workflow-sub">Dashboard Eksekutif</div></div>
    </div>
    <div class="workflow-arrow">→</div>
    <div class="workflow-step">
      <div class="workflow-num">4</div>
      <div><div class="workflow-text">Export</div><div class="workflow-sub">Excel / CSV master</div></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Module Cards ──────────────────────────────────────────────────────────
    def _mod_count(n, ts_key):
        ts = st.session_state.get(ts_key)
        ts_str = f" · {ts}" if ts else ""
        if n > 0:
            return f'<span class="module-card-count ready">✅ {fmt_int_id(n)} data{ts_str}</span>'
        return '<span class="module-card-count empty">⏳ Belum diupload</span>'

    st.markdown(f"""
<div class="module-grid">
  <div class="module-card shopee">
    <span class="module-card-icon">🟠</span>
    <div class="module-card-title">Shopee</div>
    <div class="module-card-desc">Ekstrak produk UMKM Bangka Belitung dari Shopee dengan deteksi nama toko via API.</div>
    {_mod_count(shp_n, "upload_time_shopee")}
  </div>
  <div class="module-card tokped">
    <span class="module-card-icon">🟢</span>
    <div class="module-card-title">Tokopedia</div>
    <div class="module-card-desc">Proses data produk Tokopedia dengan auto-deteksi kolom dan filter wilayah otomatis.</div>
    {_mod_count(tkp_n, "upload_time_tokped")}
  </div>
  <div class="module-card maps">
    <span class="module-card-icon">📍</span>
    <div class="module-card-title">Google Maps</div>
    <div class="module-card-desc">Visualisasi lokasi UMKM di peta interaktif dengan auto-clean koordinat & kontak.</div>
    {_mod_count(mp_n, "upload_time_maps")}
  </div>
  <div class="module-card export">
    <span class="module-card-icon">📊</span>
    <div class="module-card-title">Export Gabungan</div>
    <div class="module-card-desc">Konsolidasi semua sumber data ke 1 file Excel premium dengan autofilter & format rapi.</div>
    <span class="module-card-count {"ready" if total_all > 0 else "empty"}">{"✅ Siap diexport" if total_all > 0 else "⏳ Perlu data dulu"}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── CTA + Tips ────────────────────────────────────────────────────────────
    ca, cb = st.columns([1, 1], gap="medium")
    with ca:
        if st.button("🚀 Mulai Upload Data Shopee", use_container_width=True, type="primary"):
            goto_menu("🟠 Shopee")
    with cb:
        if st.button("📊 Lihat Export Gabungan", use_container_width=True, type="secondary"):
            goto_menu("📊 Export Gabungan")

    if st.session_state.get("show_tips", True):
        with st.container(border=True):
            st.markdown("""
<div style="display:flex; gap:16px; flex-wrap:wrap;">
  <div style="flex:1; min-width:220px;">
    <div style="font-weight:800; color:var(--ink-900); margin-bottom:6px; font-size:0.88rem;">💡 Tips Performa</div>
    <div style="font-size:0.80rem; color:var(--ink-300); line-height:1.7;">
      • Aktifkan <b>Mode Cepat</b> di Settings untuk file besar<br>
      • Naikkan <b>jeda request</b> API Shopee kalau kena rate limit<br>
      • Upload beberapa CSV sekaligus untuk batch processing
    </div>
  </div>
  <div style="flex:1; min-width:220px;">
    <div style="font-weight:800; color:var(--ink-900); margin-bottom:6px; font-size:0.88rem;">✅ Kualitas Data</div>
    <div style="font-size:0.80rem; color:var(--ink-300); line-height:1.7;">
      • Pastikan kolom <b>wilayah/lokasi</b> terisi benar<br>
      • Google Maps butuh <b>lat/lon valid</b> untuk tampil di peta<br>
      • Link & telepon kosong dibersihkan otomatis
    </div>
  </div>
  <div style="flex:1; min-width:220px;">
    <div style="font-weight:800; color:var(--ink-900); margin-bottom:6px; font-size:0.88rem;">📊 Analisis Terbaik</div>
    <div style="font-size:0.80rem; color:var(--ink-300); line-height:1.7;">
      • Cek tab <b>Audit</b> setelah upload untuk validasi data<br>
      • Gunakan <b>Top 10 Toko</b> di Executive Dashboard<br>
      • Export Gabungan untuk laporan lintas platform
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

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
            ts_shp = st.session_state.get("upload_time_shopee")
            if ts_shp:
                st.markdown(f'''<div class="upload-timestamp">✅ Upload terakhir: {ts_shp}</div>''', unsafe_allow_html=True)
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown("""
<div class="upload-info-card">
  <div class="upload-info-title">🧾 Ketentuan Data</div>
  <div class="upload-spec-row">
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Filter otomatis ke <b>Bangka Belitung</b></div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Harga dibersihkan ke integer</div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Tipe usaha via heuristik nama toko</div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Duplikat diabaikan otomatis</div></div>
  </div>
</div>
""", unsafe_allow_html=True)
            st.caption("Jika API Shopee sering timeout, kecilkan max calls atau naikkan timeout.")

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

                    st.session_state["upload_time_shopee"] = datetime.datetime.now().strftime("%d/%m %H:%M")
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
            # ── KPI Row ───────────────────────────────────────────────────────
            n_total   = len(df_f)
            n_online  = (df_f["Tipe Usaha"] == "Murni Online (Rumahan)").sum()
            n_fisik   = (df_f["Tipe Usaha"] == "Ada Toko Fisik").sum()
            n_wil     = df_f["Wilayah"].nunique()
            avg_harga = int(df_f["Harga"][df_f["Harga"] > 0].mean()) if (df_f["Harga"] > 0).any() else 0
            n_toko    = df_f["Nama Toko"].nunique()

            m1, m2, m3, m4, m5, m6 = st.columns(6)
            m1.metric("📌 Total Produk",    fmt_int_id(n_total))
            m2.metric("🏠 Murni Online",    fmt_int_id(n_online))
            m3.metric("🏬 Ada Toko Fisik",  fmt_int_id(n_fisik))
            m4.metric("🗺️ Wilayah",         fmt_int_id(n_wil))
            m5.metric("🏪 Nama Toko Unik",  fmt_int_id(n_toko))
            m6.metric("💰 Rata-rata Harga",  "Rp " + fmt_int_id(avg_harga))

            if (not st.session_state.get("fast_mode")) and (not df_f.empty):
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", hole=0.50,
                                 title="Komposisi Model Bisnis UMKM",
                                 color_discrete_sequence=BPS_PALETTE)
                    fig.update_traces(textposition="outside", textinfo="percent+label",
                                      pull=[0.04]*len(df_f["Tipe Usaha"].unique()))
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER,
                                      showlegend=False, margin=dict(t=40,b=10,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah").sort_values("Jumlah", ascending=True)
                    fig = px.bar(grp, y="Wilayah", x="Jumlah", orientation="h",
                                 title="Produk per Wilayah",
                                 color="Jumlah", color_continuous_scale=["#FFD08A","#F55F00"])
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER,
                                      coloraxis_showscale=False, margin=dict(t=40,b=10,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)

                g3, g4 = st.columns(2, gap="large")
                with g3:
                    df_hrg = df_f[df_f["Harga"] > 0]
                    if not df_hrg.empty:
                        fig = px.histogram(df_hrg, x="Harga", nbins=30,
                                           title="Distribusi Harga Produk",
                                           color_discrete_sequence=["#F55F00"])
                        fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER,
                                          margin=dict(t=40,b=10,l=0,r=0))
                        fig.update_xaxes(tickprefix="Rp ")
                        st.plotly_chart(fig, use_container_width=True)
                with g4:
                    top_toko = df_f[df_f["Nama Toko"].notna() & ~df_f["Nama Toko"].isin(
                        ["Tidak Dilacak","Anonim",""])]["Nama Toko"].value_counts().head(10).reset_index()
                    top_toko.columns = ["Toko", "Produk"]
                    if not top_toko.empty:
                        fig = px.bar(top_toko.sort_values("Produk"), y="Toko", x="Produk",
                                     orientation="h", title="Top 10 Toko Paling Aktif",
                                     color="Produk", color_continuous_scale=["#FFD08A","#F55F00"])
                        fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER,
                                          coloraxis_showscale=False, margin=dict(t=40,b=10,l=0,r=0))
                        st.plotly_chart(fig, use_container_width=True)

        with tab2:
            render_premium_table(df_f, max_rows=300, source="Shopee")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            excel_bytes = df_to_excel_bytes({"Data Shopee": df_f})
            st.download_button(
                "⬇️ Unduh Excel — Shopee",
                data=excel_bytes,
                file_name=f"UMKM_Shopee_{datetime.date.today()}.xlsx",
                use_container_width=True,
                type="primary",
            )

        with tab3:
            render_audit_cards(st.session_state.audit_shopee or {}, source="Shopee")

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
            ts_tkp = st.session_state.get("upload_time_tokped")
            if ts_tkp:
                st.markdown(f'''<div class="upload-timestamp">✅ Upload terakhir: {ts_tkp}</div>''', unsafe_allow_html=True)
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown("""
<div class="upload-info-card">
  <div class="upload-info-title">🧾 Ketentuan Data</div>
  <div class="upload-spec-row">
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Auto-deteksi nama kolom CSV</div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Filter otomatis ke <b>Babel</b></div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Multi-produk per baris didukung</div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Duplikat dihapus otomatis</div></div>
  </div>
</div>
""", unsafe_allow_html=True)
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

                    st.session_state["upload_time_tokped"] = datetime.datetime.now().strftime("%d/%m %H:%M")
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
            n_total  = len(df_f)
            n_online = (df_f["Tipe Usaha"] == "Murni Online (Rumahan)").sum()
            n_fisik  = (df_f["Tipe Usaha"] == "Ada Toko Fisik").sum()
            n_wil    = df_f["Wilayah"].nunique()
            avg_harga = int(df_f["Harga"][df_f["Harga"] > 0].mean()) if (df_f["Harga"] > 0).any() else 0
            n_toko   = df_f["Nama Toko"].nunique()

            m1, m2, m3, m4, m5, m6 = st.columns(6)
            m1.metric("📌 Total Produk",    fmt_int_id(n_total))
            m2.metric("🏠 Murni Online",    fmt_int_id(n_online))
            m3.metric("🏬 Ada Toko Fisik",  fmt_int_id(n_fisik))
            m4.metric("🗺️ Wilayah",         fmt_int_id(n_wil))
            m5.metric("🏪 Nama Toko Unik",  fmt_int_id(n_toko))
            m6.metric("💰 Rata-rata Harga",  "Rp " + fmt_int_id(avg_harga))

            if (not st.session_state.get("fast_mode")) and (not df_f.empty):
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", hole=0.50,
                                 title="Komposisi Model Bisnis UMKM",
                                 color_discrete_sequence=BPS_PALETTE)
                    fig.update_traces(textposition="outside", textinfo="percent+label",
                                      pull=[0.04]*len(df_f["Tipe Usaha"].unique()))
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER,
                                      showlegend=False, margin=dict(t=40,b=10,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah").sort_values("Jumlah", ascending=True)
                    fig = px.bar(grp, y="Wilayah", x="Jumlah", orientation="h",
                                 title="Produk per Wilayah",
                                 color="Jumlah", color_continuous_scale=["#FFD08A","#F55F00"])
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER,
                                      coloraxis_showscale=False, margin=dict(t=40,b=10,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)

                g3, g4 = st.columns(2, gap="large")
                with g3:
                    df_hrg = df_f[df_f["Harga"] > 0]
                    if not df_hrg.empty:
                        fig = px.histogram(df_hrg, x="Harga", nbins=30,
                                           title="Distribusi Harga Produk",
                                           color_discrete_sequence=["#F55F00"])
                        fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER,
                                          margin=dict(t=40,b=10,l=0,r=0))
                        fig.update_xaxes(tickprefix="Rp ")
                        st.plotly_chart(fig, use_container_width=True)
                with g4:
                    top_toko = df_f[df_f["Nama Toko"].notna() & ~df_f["Nama Toko"].isin(
                        ["Tidak Dilacak","Anonim",""])]["Nama Toko"].value_counts().head(10).reset_index()
                    top_toko.columns = ["Toko", "Produk"]
                    if not top_toko.empty:
                        fig = px.bar(top_toko.sort_values("Produk"), y="Toko", x="Produk",
                                     orientation="h", title="Top 10 Toko Paling Aktif",
                                     color="Produk", color_continuous_scale=["#FFD08A","#F55F00"])
                        fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER,
                                          coloraxis_showscale=False, margin=dict(t=40,b=10,l=0,r=0))
                        st.plotly_chart(fig, use_container_width=True)

        with tab2:
            render_premium_table(df_f, max_rows=300, source="Tokopedia")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            excel_bytes = df_to_excel_bytes({"Data Tokopedia": df_f})
            st.download_button(
                "⬇️ Unduh Excel — Tokopedia",
                data=excel_bytes,
                file_name=f"UMKM_Tokopedia_{datetime.date.today()}.xlsx",
                use_container_width=True,
                type="primary",
            )

        with tab3:
            render_audit_cards(st.session_state.audit_tokped or {}, source="Tokopedia")

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
            ts_maps = st.session_state.get("upload_time_maps")
            if ts_maps:
                st.markdown(f'''<div class="upload-timestamp">✅ Upload terakhir: {ts_maps}</div>''', unsafe_allow_html=True)
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown("""
<div class="upload-info-card">
  <div class="upload-info-title">🧾 Format Kolom</div>
  <div class="upload-spec-row">
    <div class="upload-spec"><div class="upload-spec-dot"></div><div><code>foto_url</code> — URL foto</div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div><code>nama_usaha</code> — Nama toko</div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div><code>latitude / longitude</code></div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div><code>no_telepon / link</code></div></div>
  </div>
</div>
""", unsafe_allow_html=True)
            st.caption("Nama kolom berbeda? Sistem tetap coba mapping otomatis.")

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

                    st.session_state["upload_time_maps"] = datetime.datetime.now().strftime("%d/%m %H:%M")
                    status.update(label="✅ Selesai memproses Google Maps", state="complete", expanded=False)
                    st.toast(f"Google Maps: {fmt_int_id(len(df_clean))} baris siap dianalisis", icon="✅")

                except Exception as e:
                    status.update(label="❌ Gagal memproses Google Maps", state="error", expanded=True)
                    st.error(f"Error Sistem Google Maps: {e}")

    df_maps = st.session_state.data_maps
    if df_maps is not None and not df_maps.empty:
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🧹 Data Bersih", "📑 Audit"])

        with tab1:
            lat_col  = "Latitude"   if "Latitude"   in df_maps.columns else ("latitude"   if "latitude"   in df_maps.columns else None)
            link_col = "Link"       if "Link"        in df_maps.columns else ("link"        if "link"        in df_maps.columns else None)
            tel_col  = "No Telepon" if "No Telepon"  in df_maps.columns else ("no_telepon"  if "no_telepon"  in df_maps.columns else None)
            nama_col = "Nama Usaha" if "Nama Usaha"  in df_maps.columns else ("nama_usaha"  if "nama_usaha"  in df_maps.columns else None)

            n_total  = len(df_maps)
            n_coord  = int(df_maps[lat_col].notna().sum()) if lat_col else 0
            n_link   = int((df_maps[link_col].astype(str).str.len() > 4).sum()) if link_col else 0
            n_telp   = int((df_maps[tel_col].astype(str).str.startswith("+")).sum()) if tel_col else 0
            n_nama   = int((df_maps[nama_col].astype(str).str.len() > 1).sum()) if nama_col else 0

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("📌 Total Lokasi",     fmt_int_id(n_total))
            m2.metric("📍 Koordinat Valid",  fmt_int_id(n_coord))
            m3.metric("🏷️ Ada Nama Usaha",   fmt_int_id(n_nama))
            m4.metric("🔗 Link Valid",        fmt_int_id(n_link))
            m5.metric("☎️ No Telp Valid",     fmt_int_id(n_telp))

            if not st.session_state.get("fast_mode"):
                if "Latitude" in df_maps.columns and "Longitude" in df_maps.columns:
                    render_real_map_folium(df_maps, height=560)
                else:
                    st.info("Map membutuhkan schema kolom bersih: Latitude & Longitude. Aktifkan Auto-clean.")

        with tab2:
            render_premium_table(df_maps, max_rows=300, source="Google Maps")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2, gap="medium")
            with c1:
                excel_bytes = df_to_excel_bytes({"Data Google Maps": df_maps})
                st.download_button(
                    "⬇️ Unduh Excel — Google Maps",
                    data=excel_bytes,
                    file_name=f"UMKM_GoogleMaps_{datetime.date.today()}.xlsx",
                    use_container_width=True,
                    type="primary",
                )
            with c2:
                csv_bytes = df_maps.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Unduh CSV — Google Maps",
                    data=csv_bytes,
                    file_name=f"UMKM_GoogleMaps_{datetime.date.today()}.csv",
                    use_container_width=True,
                )

        with tab3:
            render_audit_cards(st.session_state.audit_maps or {}, source="Google Maps")

# ======================================================================================
# PAGE: EXPORT GABUNGAN
# ======================================================================================
elif menu == "📊 Export Gabungan":
    section_header("Export Gabungan", "Konsolidasi data lintas platform → 1 file Excel premium.", "EXPORT")

    df_shp_ready  = st.session_state.data_shopee is not None and not st.session_state.data_shopee.empty
    df_tkp_ready  = st.session_state.data_tokped is not None and not st.session_state.data_tokped.empty
    df_maps_ready = st.session_state.data_maps   is not None and not st.session_state.data_maps.empty

    shp_n_e  = len(st.session_state.data_shopee)  if df_shp_ready  else 0
    tkp_n_e  = len(st.session_state.data_tokped)  if df_tkp_ready  else 0
    maps_n_e = len(st.session_state.data_maps)    if df_maps_ready else 0
    total_e  = shp_n_e + tkp_n_e + maps_n_e

    # ── Export Hero ────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="export-hero">
  <div class="export-hero-icon">📦</div>
  <div>
    <div class="export-hero-title">Master Data UMKM Bangka Belitung</div>
    <div class="export-hero-sub">
      Gabungkan data dari Shopee, Tokopedia, dan Google Maps menjadi 1 file Excel terstruktur
      dengan sheet terpisah, autofilter, header berwarna, dan format kolom otomatis.
      <br><b style="color:var(--fire)">{fmt_int_id(total_e)} total baris</b> siap diexport dari <b>{sum([df_shp_ready, df_tkp_ready, df_maps_ready])}</b> sumber data.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    if not (df_shp_ready or df_tkp_ready or df_maps_ready):
        st.markdown("""
<div style="padding:32px; text-align:center; border-radius:var(--r-xl);
  background:var(--glass); border:1px dashed rgba(245,95,0,0.25);
  backdrop-filter:blur(12px);">
  <div style="font-size:2.5rem; margin-bottom:12px;">📭</div>
  <div style="font-family:'Fraunces',serif; font-size:1.2rem; font-weight:700; color:var(--ink-900); margin-bottom:8px;">
    Belum Ada Data
  </div>
  <div style="font-size:0.88rem; color:var(--ink-300);">
    Proses dulu data di modul Shopee, Tokopedia, atau Google Maps.<br>
    Setelah itu kembali ke halaman ini untuk export.
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        # ── Source cards ──────────────────────────────────────────────────────
        st.markdown("#### 📋 Status Sumber Data")

        def _export_src(icon, name, n, ts_key, ready):
            ts = st.session_state.get(ts_key, "")
            ts_str = f"· Diupload {ts}" if ts else ""
            badge_cls = "ready" if ready else "empty"
            badge_txt = f"✅ {fmt_int_id(n)} baris" if ready else "⏳ Belum ada data"
            card_cls  = "ready" if ready else "empty"
            return f"""<div class="export-source-card {card_cls}" style="margin-bottom:10px;">
  <div class="export-source-left">
    <div class="export-source-icon">{icon}</div>
    <div>
      <div class="export-source-name">{name}</div>
      <div class="export-source-meta">{ts_str if ready else "Belum diproses"}</div>
    </div>
  </div>
  <span class="export-source-badge {badge_cls}">{badge_txt}</span>
</div>"""

        st.markdown(
            _export_src("🟠", "Shopee",      shp_n_e,  "upload_time_shopee", df_shp_ready) +
            _export_src("🟢", "Tokopedia",   tkp_n_e,  "upload_time_tokped", df_tkp_ready) +
            _export_src("📍", "Google Maps", maps_n_e, "upload_time_maps",   df_maps_ready),
            unsafe_allow_html=True
        )

        sheets = {}
        if df_shp_ready:  sheets["Data Shopee"]      = st.session_state.data_shopee
        if df_tkp_ready:  sheets["Data Tokopedia"]   = st.session_state.data_tokped
        if df_maps_ready: sheets["Data Google Maps"] = st.session_state.data_maps

        excel_bytes = df_to_excel_bytes(sheets)

        st.markdown("#### ⬇️ Download")
        with st.container(border=True):
            col_info, col_btn = st.columns([1.8, 1.2], gap="large")
            with col_info:
                st.markdown(f"""
<div style="display:flex; flex-direction:column; gap:8px;">
  <div style="display:flex; gap:8px; align-items:center;">
    <span style="font-size:1.1rem">📄</span>
    <div>
      <div style="font-weight:800; font-size:0.88rem; color:var(--ink-900);">Format: Excel (.xlsx)</div>
      <div style="font-size:0.78rem; color:var(--ink-300);">
        {sum([df_shp_ready,df_tkp_ready,df_maps_ready])} sheet · Autofilter · Header oranye · Format kolom otomatis
      </div>
    </div>
  </div>
  <div style="display:flex; gap:8px; align-items:center;">
    <span style="font-size:1.1rem">📦</span>
    <div>
      <div style="font-weight:800; font-size:0.88rem; color:var(--ink-900);">{fmt_int_id(total_e)} total baris data</div>
      <div style="font-size:0.78rem; color:var(--ink-300);">
        File: Master_UMKM_BPS_{datetime.date.today()}.xlsx
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
            with col_btn:
                st.download_button(
                    label="⬇️ Unduh Excel Master",
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
