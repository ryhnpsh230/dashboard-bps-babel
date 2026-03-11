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
APP_TITLE  = "ALPING UMKM BPS"
APP_ICON   = "🏛️"

BPS_OREN_UTAMA = "#C94400"
BPS_AMBER      = "#E89A1A"
BPS_DARK       = "#140400"
BPS_PAPER      = "rgba(0,0,0,0)"
BPS_PALETTE    = ["#C94400","#E06020","#E89A1A","#F2C050","#962E00","#501800","#E05020"]

BABEL_KEYS = [
    "pangkal","bangka","belitung","sungailiat","mentok","muntok",
    "koba","toboali","manggar","tanjung pandan","tanjungpandan"
]

PLACEHOLDER  = "Pemilik tidak mencantumkan"
PHONE_EMPTY  = "Pemilik belum meletakkan nomor"

# ======================================================================================
# PAGE SETUP
# ======================================================================================
st.set_page_config(
    page_title=APP_TITLE, page_icon=APP_ICON,
    layout="wide", initial_sidebar_state="expanded",
)

px.defaults.template                = "plotly_white"
px.defaults.color_discrete_sequence = BPS_PALETTE

# ======================================================================================
# MASTER CSS — Fluid Editorial v5 (Warm • Organic • Professional)
# ======================================================================================
MASTER_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ═══════════════════════════════════════════════════════
   DESIGN TOKENS
   ═══════════════════════════════════════════════════════ */
:root {
  /* Core palette — deep terracotta + warm sand */
  --fire:        #C94400;
  --fire-mid:    #DE5A1C;
  --fire-lite:   #EF7A3C;
  --fire-glow:   rgba(201, 68, 0, 0.18);
  --gold:        #D08A00;
  --gold-lite:   #F0B030;
  --sand:        #F5E6D3;
  --sand-deep:   #EDD4B8;

  /* Ink scale */
  --ink-0:   #FFFFFF;
  --ink-50:  #FBF7F4;
  --ink-100: #F2EAE0;
  --ink-200: #E0CCBA;
  --ink-300: #C4A07E;
  --ink-400: #A07040;
  --ink-600: #6B3A1A;
  --ink-800: #3A1A08;
  --ink-900: #1C0800;

  /* Surfaces */
  --surf-card:  rgba(255, 252, 248, 0.82);
  --surf-hover: rgba(255, 248, 240, 0.96);
  --glass:      rgba(255, 255, 255, 0.60);
  --glass-edge: rgba(201, 68, 0, 0.10);
  --glass-edge-hover: rgba(201, 68, 0, 0.22);

  /* Shadows — organic, soft */
  --shadow-xs: 0 1px 4px rgba(60,20,0,0.06);
  --shadow-sm: 0 3px 12px rgba(60,20,0,0.08), 0 1px 3px rgba(60,20,0,0.05);
  --shadow-md: 0 8px 28px rgba(60,20,0,0.10), 0 2px 8px rgba(60,20,0,0.06);
  --shadow-lg: 0 18px 52px rgba(60,20,0,0.13), 0 4px 16px rgba(60,20,0,0.07);
  --shadow-xl: 0 32px 80px rgba(60,20,0,0.16), 0 8px 24px rgba(60,20,0,0.09);
  --glow-fire: 0 0 0 1px rgba(201,68,0,0.14), 0 6px 28px rgba(201,68,0,0.32);

  /* Radii — fluid, organic feel */
  --r-xs:  6px;
  --r-sm:  12px;
  --r-md:  18px;
  --r-lg:  24px;
  --r-xl:  32px;
  --r-2xl: 48px;
  --r-pill: 9999px;

  /* Spacing rhythm */
  --sp-1:  4px;
  --sp-2:  8px;
  --sp-3:  12px;
  --sp-4:  16px;
  --sp-5:  20px;
  --sp-6:  24px;
  --sp-8:  32px;
  --sp-10: 40px;
  --sp-12: 48px;

  /* Type */
  --font-display: 'Playfair Display', Georgia, serif;
  --font-body:    'Plus Jakarta Sans', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', 'Courier New', monospace;

  /* Motion */
  --ease-spring:  cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-out:     cubic-bezier(0.0, 0.0, 0.2, 1);
  --ease-smooth:  cubic-bezier(0.4, 0, 0.2, 1);
  --dur-fast:     160ms;
  --dur-base:     260ms;
  --dur-slow:     440ms;
}

/* ═══════════════════════════════════════════════════════
   GLOBAL
   ═══════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  font-family: var(--font-body);
  background:
    radial-gradient(ellipse 140% 80% at -5% -5%,   rgba(201,68,0,0.07)  0%, transparent 52%),
    radial-gradient(ellipse 100% 70% at 108%  0%,   rgba(212,136,10,0.06) 0%, transparent 48%),
    radial-gradient(ellipse  70% 50% at  25% 105%,  rgba(201,68,0,0.04)  0%, transparent 55%),
    radial-gradient(ellipse  50% 40% at  88%  95%,  rgba(212,136,10,0.04) 0%, transparent 50%),
    linear-gradient(160deg,
      #FFFFFF  0%,
      #FFFDF9 22%,
      #FFF9F2 48%,
      #FFF4E8 74%,
      #FFEEDD 100%
    ) !important;
  background-attachment: fixed !important;
  color: var(--ink-800) !important;
}

[data-testid="stHeader"] { background: transparent !important; }
section.main, .main, .block-container { background: transparent !important; }
.block-container {
  max-width: 1340px;
  padding-top: 0 !important;
  padding-bottom: 5rem !important;
}

/* Noise grain — very subtle */
body::after {
  content: "";
  position: fixed; inset: 0; pointer-events: none; z-index: 9998;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.80' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.022'/%3E%3C/svg%3E");
  opacity: 0.5;
}

/* ═══════════════════════════════════════════════════════
   CUSTOM SCROLLBAR
   ═══════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--fire-mid), var(--gold));
  border-radius: var(--r-pill);
}

/* ═══════════════════════════════════════════════════════
   TYPOGRAPHY
   ═══════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5 {
  font-family: var(--font-display) !important;
  color: var(--ink-900) !important;
  font-weight: 500 !important;
  letter-spacing: -0.02em;
  line-height: 1.2;
}
h1 { font-size: clamp(2rem, 4vw, 3.2rem) !important; }
h2 { font-size: clamp(1.4rem, 2.5vw, 2rem) !important; }
h3 { font-size: clamp(1.1rem, 1.8vw, 1.4rem) !important; }
p, li, span, label { color: var(--ink-600) !important; }
code {
  font-family: var(--font-mono) !important;
  font-size: 0.80em;
  padding: 2px 6px;
  background: rgba(201,68,0,0.07);
  border-radius: var(--r-xs);
  color: var(--fire) !important;
}

/* ═══════════════════════════════════════════════════════
   GLASS CARD BASE
   ═══════════════════════════════════════════════════════ */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--surf-card) !important;
  border: 1px solid var(--glass-edge) !important;
  border-radius: var(--r-xl) !important;
  box-shadow: var(--shadow-md) !important;
  backdrop-filter: blur(24px) saturate(1.5) !important;
  -webkit-backdrop-filter: blur(24px) saturate(1.5) !important;
  transition:
    transform var(--dur-base) var(--ease-spring),
    box-shadow var(--dur-base) var(--ease-smooth),
    border-color var(--dur-fast) !important;
  padding: 26px 30px !important;
  position: relative !important;
  overflow: hidden !important;
}

/* Organic blob accent — top left */
div[data-testid="stVerticalBlockBorderWrapper"]::before {
  content: "";
  position: absolute; top: -30px; left: -30px;
  width: 120px; height: 120px; border-radius: 50%;
  background: radial-gradient(circle, rgba(201,68,0,0.06) 0%, transparent 70%);
  pointer-events: none;
}

div[data-testid="stVerticalBlockBorderWrapper"]::after {
  content: "";
  position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent 10%, rgba(255,255,255,0.5) 50%, transparent 90%);
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: var(--glass-edge-hover) !important;
  box-shadow: var(--shadow-lg) !important;
  transform: translateY(-2px) !important;
}

/* ═══════════════════════════════════════════════════════
   TOPBAR
   ═══════════════════════════════════════════════════════ */
.topbar {
  position: relative; overflow: hidden;
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 12px 20px;
  margin: 10px 0 22px;
  background: rgba(255,255,255,0.75);
  border: 1px solid rgba(201,68,0,0.10);
  border-radius: var(--r-xl);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(32px) saturate(1.8);
}

/* Flowing gradient stripe */
.topbar::before {
  content: "";
  position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg,
    transparent 0%,
    var(--fire) 15%,
    var(--fire-mid) 35%,
    var(--gold) 50%,
    var(--fire-mid) 65%,
    var(--fire) 85%,
    transparent 100%
  );
  opacity: 0.45;
}

.top-left   { display: flex; align-items: center; gap: 12px; }
.top-right  { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

.top-logo {
  width: 42px; height: 42px;
  border-radius: var(--r-md);
  background: linear-gradient(135deg, var(--fire) 0%, var(--fire-mid) 55%, var(--gold) 100%);
  box-shadow: var(--glow-fire);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; flex-shrink: 0;
  transition: transform var(--dur-fast) var(--ease-spring);
  position: relative; overflow: hidden;
}
.top-logo:hover { transform: scale(1.08) rotate(-4deg); }
.top-logo::after {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 50%;
  background: linear-gradient(180deg, rgba(255,255,255,0.22), transparent);
  border-radius: inherit;
}

.top-wordmark { display: flex; flex-direction: column; gap: 1px; }
.top-title {
  font-family: var(--font-display) !important;
  font-weight: 600; font-size: 1.05rem;
  color: var(--ink-900) !important;
  letter-spacing: -0.02em; line-height: 1.2;
}
.top-sub {
  font-size: 0.68rem; font-weight: 500;
  color: var(--ink-300) !important;
  letter-spacing: 0.01em;
}

.top-divider {
  width: 1px; height: 24px;
  background: linear-gradient(180deg, transparent, rgba(201,68,0,0.15), transparent);
}

.top-page {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.76rem; font-weight: 600;
  color: var(--ink-400) !important;
  background: rgba(201,68,0,0.055);
  border: 1px solid rgba(201,68,0,0.10);
  border-radius: var(--r-pill);
  padding: 5px 14px;
  font-family: var(--font-body);
}

.top-tag {
  font-size: 0.64rem; font-weight: 700;
  color: var(--ink-300) !important;
  background: rgba(255,255,255,0.65);
  border: 1px solid rgba(201,68,0,0.09);
  border-radius: var(--r-pill);
  padding: 4px 11px;
  font-family: var(--font-mono);
  letter-spacing: 0.04em;
}

/* ═══════════════════════════════════════════════════════
   SECTION HEADER
   ═══════════════════════════════════════════════════════ */
.bps-section { margin: 0 0 26px 0; }

.sec-eyebrow {
  display: inline-flex; align-items: center; gap: 8px; margin-bottom: 10px;
}
.sec-pill {
  font-family: var(--font-body);
  font-size: 0.60rem; font-weight: 700;
  letter-spacing: 0.20em; text-transform: uppercase;
  color: var(--fire);
  background: rgba(201,68,0,0.07);
  border: 1px solid rgba(201,68,0,0.18);
  border-radius: var(--r-pill);
  padding: 3px 11px;
}
.sec-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--fire);
  animation: dotPulse 2.8s ease-in-out infinite;
  box-shadow: 0 0 0 0 rgba(201,68,0,0);
}
@keyframes dotPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(201,68,0,0.3); }
  50%       { box-shadow: 0 0 0 6px rgba(201,68,0,0); }
}

.sec-title {
  font-family: var(--font-display) !important;
  font-size: clamp(1.9rem, 3.5vw, 2.6rem) !important;
  font-weight: 600 !important;
  line-height: 1.1 !important;
  letter-spacing: -0.03em !important;
  margin: 0 !important;
  background: linear-gradient(135deg, var(--ink-900) 0%, var(--ink-600) 50%, var(--fire) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.sec-sub {
  color: var(--ink-300) !important;
  font-size: 0.92rem; font-weight: 400;
  margin: 6px 0 0 !important; line-height: 1.65;
}
.sec-rule {
  margin-top: 14px; height: 1px;
  background: linear-gradient(90deg, var(--fire) 0%, var(--gold-lite) 30%, rgba(201,68,0,0.08) 68%, transparent 100%);
  border-radius: var(--r-pill);
}

/* ═══════════════════════════════════════════════════════
   HERO BANNER — Full-bleed organic
   ═══════════════════════════════════════════════════════ */
.bps-hero {
  position: relative; overflow: hidden;
  border-radius: var(--r-xl);
  padding: 48px 52px;
  margin-bottom: 26px;
  background:
    radial-gradient(ellipse 60% 100% at 95% 50%, rgba(212,136,10,0.35) 0%, transparent 60%),
    radial-gradient(ellipse 80% 80% at -10% 120%, rgba(180,40,0,0.40) 0%, transparent 55%),
    linear-gradient(148deg, #C94400 0%, #D86020 28%, #E07830 52%, #CC7000 76%, #B85800 100%);
  box-shadow: var(--shadow-xl);
  isolation: isolate;
}

/* Organic blob overlays */
.bps-hero::before {
  content: "";
  position: absolute; top: -80px; right: -100px;
  width: 500px; height: 500px;
  border-radius: 40% 60% 55% 45% / 45% 50% 50% 55%;
  background: rgba(255,255,255,0.06);
  pointer-events: none;
  animation: blobFloat 10s ease-in-out infinite;
}
.bps-hero::after {
  content: "";
  position: absolute; bottom: -60px; left: -40px;
  width: 280px; height: 280px;
  border-radius: 55% 45% 40% 60% / 50% 60% 40% 50%;
  background: rgba(255,255,255,0.04);
  pointer-events: none;
  animation: blobFloat 14s ease-in-out infinite reverse;
}
@keyframes blobFloat {
  0%, 100% { transform: translate(0,0) rotate(0deg); }
  33%       { transform: translate(12px,-8px) rotate(3deg); }
  66%       { transform: translate(-6px,10px) rotate(-2deg); }
}

/* Mesh dots */
.hero-mesh {
  position: absolute; inset: 0; pointer-events: none; z-index: 0;
  background-image: radial-gradient(rgba(255,255,255,0.10) 1px, transparent 1px);
  background-size: 28px 28px;
  mask-image: radial-gradient(ellipse 90% 90% at 50% 50%, black 0%, transparent 100%);
}

.bps-hero-badge {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: var(--font-body);
  font-size: 0.60rem; font-weight: 700;
  letter-spacing: 0.20em; text-transform: uppercase;
  color: rgba(255,255,255,0.85);
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.22);
  border-radius: var(--r-pill);
  padding: 5px 16px;
  margin-bottom: 20px;
  position: relative; z-index: 1;
  backdrop-filter: blur(8px);
}
.bps-hero-badge::before {
  content: ""; width: 5px; height: 5px; border-radius: 50%;
  background: rgba(255,255,255,0.85);
  box-shadow: 0 0 6px rgba(255,255,255,0.5);
  animation: blinkDot 2.2s ease-in-out infinite;
}
@keyframes blinkDot { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }

.bps-hero h1 {
  font-family: var(--font-display) !important;
  font-size: clamp(1.9rem, 3.8vw, 2.8rem) !important;
  font-weight: 600 !important;
  color: #fff !important;
  margin: 0 0 14px !important;
  position: relative; z-index: 1;
  line-height: 1.15 !important;
  letter-spacing: -0.03em !important;
}
.bps-hero p {
  color: rgba(255,255,255,0.80) !important;
  font-size: 1rem; line-height: 1.75;
  margin: 0; position: relative; z-index: 1;
  max-width: 580px;
}

.hero-chips {
  display: flex; gap: 9px; flex-wrap: wrap;
  margin-top: 24px; position: relative; z-index: 1;
}
.hero-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 16px; border-radius: var(--r-pill);
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.22);
  color: #fff !important; font-weight: 600; font-size: 0.82rem;
  backdrop-filter: blur(10px);
  transition: all var(--dur-base) var(--ease-spring);
  cursor: default;
}
.hero-chip:hover {
  background: rgba(255,255,255,0.24);
  transform: translateY(-2px) scale(1.04);
  box-shadow: 0 8px 20px rgba(0,0,0,0.13);
}

/* ═══════════════════════════════════════════════════════
   BANNER (secondary)
   ═══════════════════════════════════════════════════════ */
.bps-banner {
  position: relative; overflow: hidden;
  border-radius: var(--r-xl);
  padding: 24px 30px;
  margin: 0 0 20px;
  background:
    radial-gradient(ellipse 50% 80% at 96% 50%, rgba(201,68,0,0.06) 0%, transparent 60%),
    rgba(255,255,255,0.80);
  border: 1px solid rgba(201,68,0,0.10);
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(24px);
}
.bps-banner::before {
  content: "";
  position: absolute; left: 0; top: 18px; bottom: 18px;
  width: 3px; border-radius: 0 var(--r-xs) var(--r-xs) 0;
  background: linear-gradient(180deg, var(--fire), var(--gold));
}
.bps-kicker {
  font-family: var(--font-body);
  font-size: 0.62rem; font-weight: 700;
  letter-spacing: 0.20em; text-transform: uppercase;
  color: var(--fire);
  margin-bottom: 8px; position: relative; z-index: 1;
  display: flex; align-items: center; gap: 9px;
}
.bps-kicker::before {
  content: "";
  width: 24px; height: 2px;
  background: linear-gradient(90deg, var(--fire), var(--gold));
  border-radius: var(--r-pill);
}
.bps-title {
  font-family: var(--font-display) !important;
  font-size: 1.75rem !important; font-weight: 600;
  margin: 0 0 7px; color: var(--ink-900);
  letter-spacing: -0.025em; position: relative; z-index: 1;
}
.bps-subtitle {
  color: var(--ink-400) !important;
  font-size: 0.92rem; line-height: 1.65;
  margin: 0; position: relative; z-index: 1;
}

/* ═══════════════════════════════════════════════════════
   METRICS
   ═══════════════════════════════════════════════════════ */
div[data-testid="metric-container"] {
  background: rgba(255,255,255,0.72) !important;
  border: 1px solid rgba(201,68,0,0.09) !important;
  border-radius: var(--r-lg) !important;
  padding: 20px 22px !important;
  box-shadow: var(--shadow-sm) !important;
  backdrop-filter: blur(20px) !important;
  transition:
    transform var(--dur-base) var(--ease-spring),
    box-shadow var(--dur-base) var(--ease-smooth),
    border-color var(--dur-fast) !important;
  position: relative !important;
  overflow: hidden !important;
}

div[data-testid="metric-container"]::before {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--fire), var(--gold-lite), var(--fire-lite));
  border-radius: var(--r-pill) var(--r-pill) 0 0;
}

div[data-testid="metric-container"]::after {
  content: "";
  position: absolute; top: -30px; right: -24px;
  width: 80px; height: 80px; border-radius: 50%;
  background: radial-gradient(circle, rgba(201,68,0,0.06), transparent 70%);
}

div[data-testid="metric-container"]:hover {
  transform: translateY(-3px) !important;
  box-shadow: var(--shadow-md) !important;
  border-color: rgba(201,68,0,0.18) !important;
}

div[data-testid="metric-container"] label {
  font-family: var(--font-body) !important;
  color: var(--ink-300) !important;
  font-weight: 600 !important;
  font-size: 0.70rem !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: var(--font-display) !important;
  font-weight: 600 !important;
  color: var(--ink-900) !important;
  font-size: 2.1rem !important;
  line-height: 1.1 !important;
  letter-spacing: -0.03em !important;
}

/* ═══════════════════════════════════════════════════════
   TABS
   ═══════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  gap: 2px;
  background: rgba(255,248,240,0.85);
  border: 1px solid rgba(201,68,0,0.10);
  border-radius: var(--r-lg);
  padding: 5px;
  backdrop-filter: blur(14px);
}

.stTabs [data-baseweb="tab"] {
  height: 38px; padding: 0 20px;
  border-radius: var(--r-md);
  background: transparent;
  color: var(--ink-400) !important;
  font-family: var(--font-body);
  font-weight: 600; font-size: 0.82rem;
  transition: all var(--dur-base) var(--ease-smooth);
  letter-spacing: 0.01em;
}
.stTabs [data-baseweb="tab"]:hover {
  background: rgba(201,68,0,0.06);
  color: var(--fire) !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--fire) 0%, var(--fire-mid) 55%, var(--gold) 100%) !important;
  color: #fff !important; font-weight: 700 !important;
  box-shadow: 0 4px 16px rgba(201,68,0,0.36), 0 1px 3px rgba(201,68,0,0.20) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ═══════════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════════ */
.stButton > button,
div[data-testid="stDownloadButton"] button {
  font-family: var(--font-body) !important;
  font-weight: 700 !important; font-size: 0.86rem !important;
  border-radius: var(--r-md) !important;
  height: 46px !important; letter-spacing: 0.01em !important;
  transition: all var(--dur-base) var(--ease-spring) !important;
  position: relative !important; overflow: hidden !important;
}

.stButton > button[kind="primary"],
div[data-testid="stDownloadButton"] button {
  background: linear-gradient(138deg, var(--fire) 0%, var(--fire-mid) 50%, var(--gold) 100%) !important;
  color: #fff !important; border: none !important;
  box-shadow: 0 5px 22px rgba(201,68,0,0.36), 0 2px 6px rgba(201,68,0,0.18),
    inset 0 1px 0 rgba(255,255,255,0.16) !important;
}
.stButton > button[kind="primary"]::before,
div[data-testid="stDownloadButton"] button::before {
  content: "";
  position: absolute; top: 0; left: -100%; width: 55%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent);
  transform: skewX(-20deg);
  transition: left 0.55s ease;
}
.stButton > button[kind="primary"]:hover::before,
div[data-testid="stDownloadButton"] button:hover::before { left: 150%; }
.stButton > button[kind="primary"]:hover,
div[data-testid="stDownloadButton"] button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 12px 36px rgba(201,68,0,0.42), 0 3px 12px rgba(201,68,0,0.24),
    inset 0 1px 0 rgba(255,255,255,0.16) !important;
}

.stButton > button[kind="secondary"] {
  background: rgba(255,255,255,0.70) !important;
  color: var(--fire) !important;
  border: 1.5px solid rgba(201,68,0,0.20) !important;
  box-shadow: var(--shadow-xs) !important;
  backdrop-filter: blur(10px) !important;
}
.stButton > button[kind="secondary"]:hover {
  background: rgba(201,68,0,0.055) !important;
  border-color: var(--fire) !important;
  transform: translateY(-2px) !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ═══════════════════════════════════════════════════════
   INPUTS & SELECTS
   ═══════════════════════════════════════════════════════ */
div[data-baseweb="input"] {
  background: rgba(255,255,255,0.78) !important;
  border-radius: var(--r-md) !important;
  border: 1.5px solid rgba(201,68,0,0.12) !important;
  backdrop-filter: blur(10px) !important;
  transition: all var(--dur-fast) var(--ease-smooth) !important;
}
div[data-baseweb="input"]:focus-within {
  border-color: var(--fire) !important;
  box-shadow: 0 0 0 3px rgba(201,68,0,0.10), var(--shadow-xs) !important;
  background: rgba(255,255,255,0.95) !important;
}
div[data-baseweb="select"] > div {
  background: rgba(255,255,255,0.78) !important;
  border: 1.5px solid rgba(201,68,0,0.12) !important;
  border-radius: var(--r-md) !important;
  backdrop-filter: blur(10px) !important;
}
div[data-baseweb="select"]:focus-within > div {
  border-color: var(--fire) !important;
  box-shadow: 0 0 0 3px rgba(201,68,0,0.10) !important;
}
input, textarea {
  color: var(--ink-800) !important;
  font-family: var(--font-body) !important;
}

/* ═══════════════════════════════════════════════════════
   SLIDER
   ═══════════════════════════════════════════════════════ */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
  background: linear-gradient(135deg, var(--fire), var(--gold)) !important;
  box-shadow: var(--glow-fire) !important;
  border: 2.5px solid rgba(255,255,255,0.85) !important;
}

/* ═══════════════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════════════ */
[data-testid="stProgress"] > div > div > div {
  background: linear-gradient(90deg, var(--fire), var(--gold-lite), var(--fire-lite)) !important;
  border-radius: var(--r-pill) !important;
}

/* ═══════════════════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background:
    radial-gradient(ellipse 600px 500px at 0% -5%,  rgba(201,68,0,0.07) 0%, transparent 50%),
    radial-gradient(ellipse 400px 350px at 100% 105%, rgba(212,136,10,0.05) 0%, transparent 50%),
    linear-gradient(170deg,
      #FFFFFF   0%,
      #FFFAF4  35%,
      #FFF5EC  68%,
      #FFEFE3 100%
    ) !important;
  border-right: 1px solid rgba(201,68,0,0.08) !important;
  box-shadow: 4px 0 40px rgba(60,20,0,0.05) !important;
}
[data-testid="stSidebar"] * { color: var(--ink-800) !important; }
[data-testid="stSidebar"] .stMarkdown p {
  color: var(--ink-300) !important; font-size: 0.80rem !important; line-height: 1.6;
}
[data-testid="stSidebar"] hr {
  border: none !important;
  border-top: 1px solid rgba(201,68,0,0.07) !important;
  margin: 4px 0 !important;
}

/* Sidebar brand */
.sb-brand {
  display: flex; align-items: center; gap: 12px;
  padding: 2px 0 18px;
  position: relative;
}
.sb-brand::after {
  content: "";
  position: absolute; bottom: 0; left: -4px; right: -4px; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(201,68,0,0.14), transparent);
}
.sb-logo {
  width: 48px; height: 48px;
  border-radius: var(--r-md);
  background: linear-gradient(138deg, var(--fire) 0%, var(--fire-mid) 50%, var(--gold) 100%);
  box-shadow: var(--glow-fire);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.45rem; flex-shrink: 0;
  transition: transform var(--dur-fast) var(--ease-spring);
  position: relative; overflow: hidden;
}
.sb-logo:hover { transform: scale(1.06) rotate(-4deg); }
.sb-logo::after {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 50%;
  background: linear-gradient(180deg, rgba(255,255,255,0.22), transparent);
  border-radius: inherit;
}
.sb-name {
  font-family: var(--font-display) !important;
  font-size: 1.02rem; font-weight: 600;
  color: var(--ink-900) !important; letter-spacing: -0.02em; line-height: 1.2;
}
.sb-sub {
  font-size: 0.62rem; font-weight: 700; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--ink-300) !important; margin-top: 2px;
}

/* Nav label */
.sb-nav-label {
  font-family: var(--font-mono);
  font-size: 0.58rem; font-weight: 700;
  letter-spacing: 0.20em; text-transform: uppercase;
  color: rgba(201,68,0,0.40) !important;
  padding: 10px 2px 5px;
}

/* Radio nav */
[data-testid="stSidebar"] div[role="radiogroup"] {
  gap: 4px !important; display: flex !important; flex-direction: column !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label {
  border-radius: var(--r-md) !important;
  border: 1px solid rgba(201,68,0,0.07) !important;
  background: rgba(255,255,255,0.72) !important;
  padding: 12px 15px !important;
  cursor: pointer !important;
  transition: all var(--dur-base) var(--ease-spring) !important;
  box-shadow: var(--shadow-xs) !important;
  overflow: hidden !important;
  position: relative !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label::before {
  content: "";
  position: absolute; left: 0; top: 7px; bottom: 7px;
  width: 3px; border-radius: 0 var(--r-xs) var(--r-xs) 0;
  background: linear-gradient(180deg, var(--fire), var(--gold));
  opacity: 0;
  transition: opacity var(--dur-fast);
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
  border-color: rgba(201,68,0,0.16) !important;
  background: rgba(255,255,255,0.94) !important;
  box-shadow: var(--shadow-sm) !important;
  transform: translateX(4px) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover::before { opacity: 1; }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
  background: linear-gradient(138deg, var(--fire) 0%, var(--fire-mid) 50%, var(--gold) 100%) !important;
  border-color: transparent !important;
  box-shadow: 0 5px 22px rgba(201,68,0,0.36), 0 2px 6px rgba(201,68,0,0.18) !important;
  transform: translateX(4px) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span {
  color: #fff !important; font-weight: 700 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked)::before { display: none; }
[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] { display: none !important; }

/* Sidebar CTA */
[data-testid="stSidebar"] .stButton > button {
  border-radius: var(--r-md) !important;
  background: rgba(201,68,0,0.055) !important;
  border: 1.5px solid rgba(201,68,0,0.14) !important;
  color: var(--fire) !important;
  font-weight: 700 !important; font-size: 0.81rem !important;
  height: 42px !important; box-shadow: none !important;
  transition: all var(--dur-base) var(--ease-smooth) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(201,68,0,0.10) !important;
  border-color: var(--fire) !important;
  box-shadow: 0 3px 14px rgba(201,68,0,0.15) !important;
  transform: none !important;
}

/* Sidebar stat grid */
.sb-stat-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 7px; margin: 4px 0;
}
.sb-stat {
  border-radius: var(--r-md); padding: 13px;
  background: rgba(255,255,255,0.75);
  border: 1px solid rgba(201,68,0,0.07);
  box-shadow: var(--shadow-xs);
  transition: all var(--dur-base) var(--ease-smooth);
  position: relative; overflow: hidden;
}
.sb-stat::before {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--fire), var(--gold));
  opacity: 0; transition: opacity var(--dur-fast);
}
.sb-stat:hover { border-color: rgba(201,68,0,0.14); box-shadow: var(--shadow-sm); transform: translateY(-1px); }
.sb-stat:hover::before { opacity: 0.7; }
.sb-stat-val {
  font-family: var(--font-display);
  font-size: 1.25rem; font-weight: 600;
  color: var(--fire) !important; line-height: 1.1;
}
.sb-stat-lbl {
  font-size: 0.62rem; font-weight: 700;
  color: var(--ink-300) !important; margin-top: 2px;
  letter-spacing: 0.04em; text-transform: uppercase;
}

/* Sidebar footer */
.sb-footer {
  margin-top: 10px;
  border-radius: var(--r-lg); overflow: hidden;
  border: 1px solid rgba(201,68,0,0.09);
}
.sb-footer-top {
  padding: 13px 15px 11px;
  background: linear-gradient(135deg, rgba(201,68,0,0.06), rgba(212,136,10,0.04));
  display: flex; align-items: center; gap: 10px;
}
.sb-footer-icon {
  width: 32px; height: 32px; border-radius: var(--r-sm);
  background: linear-gradient(135deg, var(--fire), var(--gold));
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(201,68,0,0.26);
}
.sb-footer-name {
  font-family: var(--font-display) !important;
  font-size: 0.86rem; font-weight: 600; color: var(--ink-900) !important; line-height: 1.2;
}
.sb-footer-ver {
  font-family: var(--font-mono) !important;
  font-size: 0.60rem; color: var(--ink-300) !important; margin-top: 1px;
}
.sb-footer-bottom {
  padding: 7px 15px;
  background: rgba(201,68,0,0.03);
  border-top: 1px solid rgba(201,68,0,0.06);
  font-size: 0.62rem; font-weight: 700;
  color: var(--ink-200) !important;
  text-align: center; letter-spacing: 0.07em; text-transform: uppercase;
  font-family: var(--font-mono);
}
.sb-divider { display:flex;align-items:center;gap:8px;margin:12px 0 6px; }
.sb-divider-line { flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(201,68,0,0.13),transparent); }

/* ═══════════════════════════════════════════════════════
   MODULE CARDS
   ═══════════════════════════════════════════════════════ */
.module-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(230px,1fr));
  gap: 16px; margin: 20px 0;
}
.module-card {
  border-radius: var(--r-xl);
  padding: 24px 22px 20px;
  background: rgba(255,255,255,0.70);
  border: 1px solid rgba(201,68,0,0.09);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(22px);
  transition: all var(--dur-base) var(--ease-spring);
  cursor: pointer; position: relative; overflow: hidden;
}
.module-card::before {
  content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.module-card.shopee::before  { background: linear-gradient(90deg, #C94400, #E87828); }
.module-card.tokped::before  { background: linear-gradient(90deg, #00874A, #00C46A); }
.module-card.maps::before    { background: linear-gradient(90deg, #1A73E8, #34A853); }
.module-card.export::before  { background: linear-gradient(90deg, #7C3AED, #A78BFA); }

/* Organic corner blob */
.module-card::after {
  content: "";
  position: absolute; bottom: -35px; right: -35px;
  width: 110px; height: 110px;
  border-radius: 50% 40% 60% 45%;
  opacity: 0; transition: opacity var(--dur-slow);
}
.module-card.shopee::after  { background: radial-gradient(circle, rgba(201,68,0,0.08), transparent 65%); }
.module-card.tokped::after  { background: radial-gradient(circle, rgba(0,135,74,0.07), transparent 65%); }
.module-card.maps::after    { background: radial-gradient(circle, rgba(26,115,232,0.07), transparent 65%); }
.module-card.export::after  { background: radial-gradient(circle, rgba(124,58,237,0.07), transparent 65%); }

.module-card:hover {
  box-shadow: var(--shadow-lg) !important;
  transform: translateY(-5px) !important;
  border-color: rgba(201,68,0,0.18) !important;
  background: rgba(255,255,255,0.88) !important;
}
.module-card:hover::after { opacity: 1; }
.module-icon-wrap {
  width: 50px; height: 50px; border-radius: var(--r-md);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem; margin-bottom: 14px;
  background: rgba(255,255,255,0.68);
  border: 1px solid rgba(201,68,0,0.08);
  box-shadow: var(--shadow-xs);
  transition: transform var(--dur-base) var(--ease-spring);
}
.module-card:hover .module-icon-wrap { transform: scale(1.10) rotate(-5deg); }
.module-card-title {
  font-family: var(--font-display);
  font-size: 1.10rem; font-weight: 600;
  color: var(--ink-900); margin-bottom: 6px; letter-spacing: -0.01em;
}
.module-card-desc {
  font-size: 0.76rem; color: var(--ink-300); line-height: 1.65;
}
.module-card-badge {
  margin-top: 14px;
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 12px; border-radius: var(--r-pill);
  font-size: 0.70rem; font-weight: 700;
}
.module-card-badge.ready {
  background: rgba(22,163,74,0.09);
  border: 1px solid rgba(22,163,74,0.20);
  color: #15803D;
}
.module-card-badge.empty {
  background: rgba(201,68,0,0.065);
  border: 1px solid rgba(201,68,0,0.14);
  color: var(--fire);
}

/* ═══════════════════════════════════════════════════════
   WORKFLOW STEPS
   ═══════════════════════════════════════════════════════ */
.workflow-row {
  display: flex; align-items: center; gap: 7px; flex-wrap: wrap; margin: 16px 0;
}
.workflow-step {
  display: flex; align-items: center; gap: 10px;
  padding: 13px 18px; border-radius: var(--r-lg);
  background: rgba(255,255,255,0.68);
  border: 1px solid rgba(201,68,0,0.07);
  box-shadow: var(--shadow-xs);
  flex: 1; min-width: 140px;
  transition: all var(--dur-base) var(--ease-spring);
}
.workflow-step:hover { box-shadow: var(--shadow-sm); transform: translateY(-2px); border-color: rgba(201,68,0,0.16); }
.workflow-num {
  width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(138deg, var(--fire), var(--gold));
  color: #fff; font-size: 0.75rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(201,68,0,0.30);
  font-family: var(--font-mono);
}
.workflow-text { font-size: 0.80rem; font-weight: 700; color: var(--ink-800); }
.workflow-sub  { font-size: 0.68rem; color: var(--ink-300); margin-top: 1px; }
.workflow-arrow { color: var(--ink-200); font-size: 1.2rem; flex-shrink: 0; }

/* ═══════════════════════════════════════════════════════
   UPLOAD INFO CARD
   ═══════════════════════════════════════════════════════ */
.upload-info-card {
  border-radius: var(--r-lg); padding: 18px 20px; margin-bottom: 14px;
  background: linear-gradient(145deg, rgba(201,68,0,0.05), rgba(212,136,10,0.035));
  border: 1px solid rgba(201,68,0,0.10);
}
.upload-info-title {
  font-family: var(--font-display);
  font-size: 0.98rem; font-weight: 600;
  color: var(--ink-900); margin-bottom: 11px;
  display: flex; align-items: center; gap: 7px;
}
.upload-spec-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.upload-spec {
  display: flex; align-items: flex-start; gap: 7px;
  font-size: 0.77rem; color: var(--ink-400); line-height: 1.5;
}
.upload-spec-dot {
  width: 4px; height: 4px; border-radius: 50%; background: var(--fire);
  margin-top: 6px; flex-shrink: 0;
  box-shadow: 0 0 0 3px rgba(201,68,0,0.12);
}
.upload-timestamp {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 12px; border-radius: var(--r-pill);
  background: rgba(22,163,74,0.07);
  border: 1px solid rgba(22,163,74,0.18);
  font-size: 0.70rem; font-weight: 700; color: #15803D;
  margin-top: 9px;
}

/* ═══════════════════════════════════════════════════════
   PREMIUM DATA TABLE
   ═══════════════════════════════════════════════════════ */
.bps-table-wrap {
  width: 100%; overflow-x: auto;
  border-radius: var(--r-lg);
  border: 1px solid rgba(201,68,0,0.09);
  box-shadow: var(--shadow-sm);
  background: rgba(255,255,255,0.84);
  backdrop-filter: blur(18px);
  margin-bottom: 14px;
}
.bps-table {
  width: 100%; border-collapse: collapse;
  font-family: var(--font-body); font-size: 0.82rem;
}
.bps-table thead tr {
  background: linear-gradient(138deg, var(--fire) 0%, var(--fire-mid) 50%, var(--gold) 100%);
}
.bps-table thead th {
  padding: 13px 15px; text-align: left;
  font-weight: 700; font-size: 0.66rem;
  letter-spacing: 0.09em; text-transform: uppercase;
  color: rgba(255,255,255,0.93) !important; white-space: nowrap;
}
.bps-table thead th:first-child { border-radius: var(--r-md) 0 0 0; padding-left: 18px; }
.bps-table thead th:last-child  { border-radius: 0 var(--r-md) 0 0; }
.bps-table tbody tr {
  border-bottom: 1px solid rgba(201,68,0,0.048);
  transition: background var(--dur-fast);
}
.bps-table tbody tr:last-child { border-bottom: none; }
.bps-table tbody tr:hover { background: rgba(201,68,0,0.032) !important; }
.bps-table tbody tr:nth-child(even) { background: rgba(255,248,238,0.50); }
.bps-table tbody td { padding: 10px 15px; color: var(--ink-600) !important; vertical-align: middle; }
.bps-table tbody td:first-child { padding-left: 18px; }
.bps-table .td-toko { font-weight: 700; color: var(--ink-800) !important; }
.bps-table .td-harga {
  font-family: var(--font-display);
  font-size: 0.94rem; font-weight: 600; color: var(--fire) !important; white-space: nowrap;
}
.bps-table .td-link a {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 10px; border-radius: var(--r-pill);
  font-size: 0.70rem; font-weight: 700;
  background: rgba(201,68,0,0.06);
  border: 1px solid rgba(201,68,0,0.15);
  color: var(--fire) !important; text-decoration: none; white-space: nowrap;
  transition: all var(--dur-fast);
}
.bps-table .td-link a:hover { background: var(--fire); color: #fff !important; }

.tipe-badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 9px; border-radius: var(--r-pill);
  font-size: 0.68rem; font-weight: 700; white-space: nowrap;
}
.tipe-online { background: rgba(22,163,74,0.09);  border: 1px solid rgba(22,163,74,0.20);  color: #15803D !important; }
.tipe-fisik  { background: rgba(37,99,235,0.09);   border: 1px solid rgba(37,99,235,0.20);   color: #1D4ED8 !important; }
.tipe-other  { background: rgba(201,68,0,0.07);    border: 1px solid rgba(201,68,0,0.16);    color: var(--fire) !important; }

.td-num { color: var(--ink-200) !important; font-size: 0.66rem; font-weight: 700; text-align: right; padding-right: 7px !important; width: 34px; font-family: var(--font-mono); }
.td-truncate { max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.db-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px; flex-wrap: wrap; gap: 8px;
}
.db-title {
  font-family: var(--font-display);
  font-size: 1.05rem; font-weight: 600; color: var(--ink-900);
  display: flex; align-items: center; gap: 7px;
}
.db-count {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 13px; border-radius: var(--r-pill);
  background: rgba(201,68,0,0.065);
  border: 1px solid rgba(201,68,0,0.14);
  font-size: 0.72rem; font-weight: 700; color: var(--fire);
  font-family: var(--font-mono);
}

/* ═══════════════════════════════════════════════════════
   AUDIT CARDS
   ═══════════════════════════════════════════════════════ */
.audit-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(195px,1fr));
  gap: 12px; margin: 5px 0;
}
.audit-card {
  border-radius: var(--r-lg); padding: 18px;
  display: flex; align-items: flex-start; gap: 12px;
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(201,68,0,0.08);
  box-shadow: var(--shadow-xs);
  backdrop-filter: blur(18px);
  transition: all var(--dur-base) var(--ease-spring);
  position: relative; overflow: hidden;
}
.audit-card::before {
  content: ""; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, rgba(201,68,0,0.15), transparent);
  opacity: 0; transition: opacity var(--dur-fast);
}
.audit-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); border-color: rgba(201,68,0,0.16); }
.audit-card:hover::before { opacity: 1; }
.audit-icon {
  width: 40px; height: 40px; border-radius: var(--r-md);
  display: flex; align-items: center; justify-content: center; font-size: 1.15rem; flex-shrink: 0;
  position: relative; overflow: hidden;
}
.audit-icon::after { content:"";position:absolute;top:0;left:0;right:0;height:50%;background:linear-gradient(180deg,rgba(255,255,255,0.22),transparent);border-radius:inherit; }
.audit-icon.blue   { background: linear-gradient(135deg,#3B82F6,#60A5FA); }
.audit-icon.green  { background: linear-gradient(135deg,#22C55E,#4ADE80); }
.audit-icon.orange { background: linear-gradient(135deg,var(--fire),var(--fire-lite)); }
.audit-icon.red    { background: linear-gradient(135deg,#EF4444,#F87171); }
.audit-icon.amber  { background: linear-gradient(135deg,var(--gold),var(--gold-lite)); }
.audit-icon.purple { background: linear-gradient(135deg,#8B5CF6,#A78BFA); }
.audit-val {
  font-family: var(--font-display);
  font-size: 1.65rem; font-weight: 600; line-height: 1.0; color: var(--ink-900);
}
.audit-lbl { font-size: 0.70rem; font-weight: 600; color: var(--ink-300); margin-top: 3px; line-height: 1.4; }

/* Quality bar */
.quality-bar-wrap { margin: 18px 0 5px; }
.quality-header {
  display: flex; justify-content: space-between;
  font-size: 0.77rem; font-weight: 700; color: var(--ink-400); margin-bottom: 8px;
}
.quality-pct { color: var(--fire) !important; font-weight: 700; }
.quality-track {
  height: 9px; border-radius: var(--r-pill);
  background: rgba(201,68,0,0.08); overflow: hidden;
}
.quality-fill {
  height: 100%; border-radius: var(--r-pill);
  background: linear-gradient(90deg, #22C55E, #86EFAC);
  transition: width 1.1s var(--ease-out);
}
.quality-fill.mid { background: linear-gradient(90deg, #F59E0B, #FCD34D); }
.quality-fill.low { background: linear-gradient(90deg, #EF4444, #FCA5A5); }

/* ═══════════════════════════════════════════════════════
   EXPORT PAGE
   ═══════════════════════════════════════════════════════ */
.export-hero {
  border-radius: var(--r-xl); padding: 32px 38px; margin-bottom: 22px;
  background: linear-gradient(145deg, rgba(124,58,237,0.08), rgba(201,68,0,0.06), rgba(212,136,10,0.05));
  border: 1px solid rgba(124,58,237,0.12);
  box-shadow: var(--shadow-md);
  display: flex; align-items: center; gap: 28px;
  position: relative; overflow: hidden;
}
.export-hero::before {
  content: "";
  position: absolute; top: -50px; right: -50px;
  width: 220px; height: 220px;
  border-radius: 50% 40% 60% 45%;
  background: radial-gradient(circle, rgba(124,58,237,0.07), transparent 65%);
}
.export-hero-icon { font-size: 3.4rem; flex-shrink: 0; filter: drop-shadow(0 8px 16px rgba(124,58,237,0.24)); }
.export-hero-title { font-family: var(--font-display); font-size: 1.55rem; font-weight: 600; color: var(--ink-900); margin-bottom: 6px; letter-spacing: -0.02em; }
.export-hero-sub { font-size: 0.88rem; color: var(--ink-400); line-height: 1.7; }
.export-src-card {
  border-radius: var(--r-lg); padding: 16px 20px; margin-bottom: 9px;
  background: rgba(255,255,255,0.75);
  border: 1px solid rgba(201,68,0,0.08);
  box-shadow: var(--shadow-xs);
  display: flex; align-items: center; justify-content: space-between;
  transition: all var(--dur-base) var(--ease-smooth);
}
.export-src-card:hover { box-shadow: var(--shadow-sm); transform: translateY(-1px); }
.export-src-card.ready { border-left: 3px solid #22C55E !important; }
.export-src-card.empty { border-left: 3px solid rgba(201,68,0,0.25) !important; opacity: 0.70; }
.export-src-left { display: flex; align-items: center; gap: 12px; }
.export-src-icon { font-size: 1.75rem; }
.export-src-name { font-family: var(--font-display); font-size: 0.98rem; font-weight: 600; color: var(--ink-900); }
.export-src-meta { font-size: 0.74rem; color: var(--ink-300); margin-top: 2px; }
.export-src-badge { padding: 3px 12px; border-radius: var(--r-pill); font-size: 0.70rem; font-weight: 700; }
.export-src-badge.ready { background: rgba(22,163,74,0.09); border: 1px solid rgba(22,163,74,0.20); color: #15803D; }
.export-src-badge.empty { background: rgba(201,68,0,0.065); border: 1px solid rgba(201,68,0,0.14); color: var(--ink-300); }

/* ═══════════════════════════════════════════════════════
   ALERTS & TOASTS
   ═══════════════════════════════════════════════════════ */
div[data-testid="stAlert"] {
  border-radius: var(--r-lg) !important;
  border-left-width: 3px !important;
  backdrop-filter: blur(12px) !important;
  box-shadow: var(--shadow-xs) !important;
}
[data-testid="stToast"] {
  border-radius: var(--r-lg) !important;
  border-left: 3px solid var(--fire) !important;
  backdrop-filter: blur(24px) saturate(1.5) !important;
  box-shadow: var(--shadow-md) !important;
}

/* ═══════════════════════════════════════════════════════
   EXPANDERS
   ═══════════════════════════════════════════════════════ */
details {
  background: rgba(255,255,255,0.70);
  border: 1px solid rgba(201,68,0,0.09);
  border-radius: var(--r-md);
  padding: 2px 13px;
  backdrop-filter: blur(12px);
  transition: box-shadow var(--dur-base);
}
details[open] { box-shadow: var(--shadow-sm); }
details summary {
  font-family: var(--font-body);
  font-weight: 700; color: var(--ink-900); cursor: pointer;
}

/* ═══════════════════════════════════════════════════════
   LINKS
   ═══════════════════════════════════════════════════════ */
a { color: var(--fire) !important; text-decoration: none; transition: color var(--dur-fast); }
a:hover { color: var(--fire-mid) !important; }

/* ═══════════════════════════════════════════════════════
   FOOTER
   ═══════════════════════════════════════════════════════ */
.bps-footer {
  margin-top: 48px; padding: 18px 0;
  border-top: 1px solid rgba(201,68,0,0.07);
  display: flex; align-items: center; gap: 12px;
  color: rgba(92,32,0,0.32) !important;
  font-size: 0.76rem; font-family: var(--font-mono);
  letter-spacing: 0.02em;
}
.footer-dot { width: 3px; height: 3px; border-radius: 50%; background: rgba(201,68,0,0.22); flex-shrink: 0; }

/* ═══════════════════════════════════════════════════════
   DATAFRAME
   ═══════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
  border-radius: var(--r-lg) !important;
  overflow: hidden !important;
  border: 1px solid rgba(201,68,0,0.09) !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ═══════════════════════════════════════════════════════
   EMPTY STATE
   ═══════════════════════════════════════════════════════ */
.empty-state {
  padding: 44px 28px; text-align: center;
  border-radius: var(--r-xl);
  background: rgba(255,255,255,0.65);
  border: 1px dashed rgba(201,68,0,0.18);
  backdrop-filter: blur(18px);
}
.empty-icon { font-size: 2.8rem; margin-bottom: 12px; opacity: 0.65; }
.empty-title { font-family: var(--font-display); font-size: 1.25rem; font-weight: 600; color: var(--ink-900); margin-bottom: 7px; }
.empty-sub { font-size: 0.84rem; color: var(--ink-300); line-height: 1.65; }

/* Status badges */
.status-ok  { display:inline-flex;align-items:center;gap:4px;padding:2px 10px;border-radius:var(--r-pill);background:rgba(22,163,74,.08);border:1px solid rgba(22,163,74,.18);font-size:.68rem;font-weight:700;color:#15803D; }
.status-warn{ display:inline-flex;align-items:center;gap:4px;padding:2px 10px;border-radius:var(--r-pill);background:rgba(201,68,0,.07);border:1px solid rgba(201,68,0,.16);font-size:.68rem;font-weight:700;color:var(--fire); }

/* Filter head */
.filter-head { font-family:var(--font-display);font-size:1.02rem;font-weight:600;color:var(--ink-900);margin-bottom:13px;display:flex;align-items:center;gap:7px; }

/* Tip grid */
.tip-grid { display:flex;gap:16px;flex-wrap:wrap; }
.tip-col { flex:1;min-width:200px; }
.tip-head { font-weight:700;color:var(--ink-900);margin-bottom:6px;font-size:0.85rem;display:flex;align-items:center;gap:5px; }
.tip-body { font-size:0.76rem;color:var(--ink-300);line-height:1.75; }
.tip-body b { color:var(--ink-600) !important; }

/* ═══════════════════════════════════════════════════════
   SPLASH SCREEN
   (defined inline in Python function)
   ═══════════════════════════════════════════════════════ */
"""

st.markdown(f"<style>{MASTER_CSS}</style>", unsafe_allow_html=True)

# ======================================================================================
# UI HELPERS
# ======================================================================================
def section_header(title: str, subtitle: str = "", badge: str = "MODULE"):
    sub_html = f'<p class="sec-sub">{subtitle}</p>' if subtitle else ''
    st.markdown(f"""
<div class="bps-section">
  <div class="sec-eyebrow">
    <span class="sec-pill">{badge}</span>
    <div class="sec-dot"></div>
  </div>
  <h2 class="sec-title">{title}</h2>
  {sub_html}
  <div class="sec-rule"></div>
</div>""", unsafe_allow_html=True)

def banner(title: str, subtitle: str):
    st.markdown(f"""
<div class="bps-banner">
  <div class="bps-kicker">Badan Pusat Statistik</div>
  <div class="bps-title">{title}</div>
  <p class="bps-subtitle">{subtitle}</p>
</div>""", unsafe_allow_html=True)

def topbar(current_page: str, show_sidebar: bool):
    sidebar_label = "SIDEBAR ON" if show_sidebar else "SIDEBAR OFF"
    st.markdown(f"""
<div class="topbar">
  <div class="top-left">
    <div class="top-logo">🏛️</div>
    <div class="top-divider"></div>
    <div class="top-wordmark">
      <div class="top-title">{APP_TITLE}</div>
      <div class="top-sub">BPS Bangka Belitung · Toolkit Analisis UMKM</div>
    </div>
  </div>
  <div class="top-right">
    <div class="top-page">📍 {current_page}</div>
    <div class="top-tag">{sidebar_label}</div>
  </div>
</div>""", unsafe_allow_html=True)

def goto_menu(label: str):
    st.session_state["nav_target"] = label
    st.session_state["show_sidebar"] = True
    st.rerun()

def hide_sidebar_css():
    st.markdown("<style>[data-testid='stSidebar']{display:none !important;} section.main{margin-left:0 !important;}</style>", unsafe_allow_html=True)

# ======================================================================================
# PREMIUM TABLE RENDERER
# ======================================================================================
def render_premium_table(df: pd.DataFrame, max_rows: int = 200, source: str = ""):
    df_show = df.head(max_rows).copy()
    cols    = list(df_show.columns)
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
        v  = str(val) if not pd.isna(val) else "-"
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
            return f'<td style="color:var(--ink-200);font-size:.72rem;font-family:var(--font-mono)">{v}</td>'
        else:
            trunc = v[:40] + ("…" if len(v) > 40 else "")
            return f'<td class="td-truncate" title="{v}">{trunc}</td>'

    rows_html = ""
    for i, (_, row) in enumerate(df_show.iterrows()):
        cells      = "".join(_cell(c, row[c]) for c in cols)
        rows_html += f"<tr><td class='td-num'>{i+1:03d}</td>{cells}</tr>"

    total = len(df); shown = len(df_show)
    note  = f" <span style='color:var(--ink-200);font-size:.71rem'>(menampilkan {shown:,} dari {total:,})</span>" if total > max_rows else ""
    html  = f"""
<div class="db-header">
  <span class="db-title">📋 Data {source}{note}</span>
  <span class="db-count">{total:,} rows</span>
</div>
<div class="bps-table-wrap" style="max-height:490px;overflow-y:auto;">
<table class="bps-table">
  <thead><tr><th>#</th>{th_html}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>
</div>"""
    st.markdown(html, unsafe_allow_html=True)

# ======================================================================================
# AUDIT RENDERER
# ======================================================================================
def render_audit_cards(audit: dict, source: str = ""):
    fc    = audit.get("file_count", 0)
    tot   = audit.get("total_rows", audit.get("rows_in", 0))
    val   = audit.get("valid_rows", audit.get("rows_out", 0))
    luar  = audit.get("luar_wilayah", 0)
    err   = audit.get("error_harga", 0)
    api   = audit.get("api_calls", None)
    dedup = audit.get("dedup_removed", 0)
    inv_c = audit.get("invalid_coord", 0)
    inv_l = audit.get("invalid_link", 0)
    empty = audit.get("empty_name", 0)
    miss  = audit.get("missing_cols", [])

    quality_pct = round(val / tot * 100, 1) if tot > 0 else 0
    q_class     = "low" if quality_pct < 50 else ("mid" if quality_pct < 80 else "")

    st.markdown(f"""
<div class="quality-bar-wrap">
  <div class="quality-header">
    <span>📊 Kualitas Data — {source}</span>
    <span class="quality-pct">{quality_pct}% valid</span>
  </div>
  <div class="quality-track">
    <div class="quality-fill {q_class}" style="width:{quality_pct}%"></div>
  </div>
</div>""", unsafe_allow_html=True)

    cards = [
        ("blue",   "📂", str(fc),                        "File Diproses"),
        ("orange", "📥", f"{tot:,}".replace(",","."),    "Total Baris Masuk"),
        ("green",  "✅", f"{val:,}".replace(",","."),    "Baris Valid (Babel)"),
    ]
    if luar:  cards.append(("amber",  "🗺️",  f"{luar:,}".replace(",","."), "Luar Wilayah"))
    if err:   cards.append(("red",    "⚠️",  f"{err:,}".replace(",","."),  "Error Harga"))
    if api is not None: cards.append(("purple","🔌", f"{api:,}".replace(",","."), "API Calls"))
    if dedup: cards.append(("amber",  "🧽",  f"{dedup:,}".replace(",","."), "Duplikat Dihapus"))
    if inv_c: cards.append(("red",    "📍",  f"{inv_c:,}".replace(",","."), "Koordinat Invalid"))
    if inv_l: cards.append(("amber",  "🔗",  f"{inv_l:,}".replace(",","."), "Link Invalid"))
    if empty: cards.append(("red",    "🏷️",  f"{empty:,}".replace(",","."), "Nama Kosong"))

    cards_html = "".join(f"""<div class="audit-card">
  <div class="audit-icon {color}">{icon}</div>
  <div><div class="audit-val">{vs}</div><div class="audit-lbl">{lbl}</div></div>
</div>""" for color, icon, vs, lbl in cards)

    st.markdown(f'<div class="audit-grid">{cards_html}</div>', unsafe_allow_html=True)
    if miss:
        st.markdown(f"""<div style="margin-top:12px;padding:12px 16px;border-radius:var(--r-md);background:rgba(245,158,11,.07);border:1px solid rgba(245,158,11,.20);">
  <span style="font-size:.78rem;font-weight:700;color:#B45309;">⚠️ Kolom tidak ditemukan: <code>{", ".join(miss)}</code></span></div>""", unsafe_allow_html=True)

# ======================================================================================
# SPLASH SCREEN
# ======================================================================================
def splash_screen():
    logo_html = ""
    if os.path.exists("logo.png"):
        import base64
        with open("logo.png","rb") as _f:
            _b64 = base64.b64encode(_f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{_b64}" style="width:56px;height:56px;object-fit:contain;filter:brightness(0) invert(1);position:relative;z-index:1;" alt="Logo BPS">'
    else:
        logo_html = '<span style="font-size:2.4rem;position:relative;z-index:1;line-height:1;">🏛️</span>'

    st.markdown(f"""
<style>
  [data-testid="stSidebar"],[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],footer{{display:none !important}}
  html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"],.main,section.main,.block-container{{
    background:#FDF8F3 !important;padding:0 !important;margin:0 !important;overflow:hidden !important;
  }}
  .block-container::before,.block-container::after{{display:none !important}}

  #sp{{
    position:fixed;inset:0;z-index:999999;
    display:flex;align-items:center;justify-content:center;
    background:
      radial-gradient(ellipse 80% 70% at 15% 15%, rgba(201,68,0,0.10) 0%, transparent 55%),
      radial-gradient(ellipse 60% 50% at 88% 85%, rgba(212,136,10,0.08) 0%, transparent 50%),
      linear-gradient(155deg, #FFFFFF 0%, #FFFCF8 35%, #FFF7EE 65%, #FFF2E4 100%);
    font-family:'Plus Jakarta Sans','Segoe UI',system-ui,sans-serif;
  }}

  /* animated background blobs */
  #sp::before{{
    content:"";position:absolute;
    width:min(360px,38vw);height:min(360px,38vw);
    top:8%;right:8%;
    border-radius:40% 60% 55% 45% / 48% 52% 48% 52%;
    border:1px solid rgba(201,68,0,0.07);
    animation:splashBlob1 9s ease-in-out infinite;
    pointer-events:none;
  }}
  #sp::after{{
    content:"";position:absolute;
    width:min(200px,22vw);height:min(200px,22vw);
    bottom:10%;left:7%;
    border-radius:55% 45% 42% 58% / 50% 58% 42% 50%;
    border:1px solid rgba(212,136,10,0.06);
    animation:splashBlob1 13s ease-in-out infinite reverse;
    pointer-events:none;
  }}
  @keyframes splashBlob1{{
    0%,100%{{transform:rotate(0deg) scale(1)}}
    33%{{transform:rotate(4deg) scale(1.04)}}
    66%{{transform:rotate(-3deg) scale(0.97)}}
  }}

  .sp-card{{
    position:relative;z-index:1;
    width:min(480px,91vw);
    padding:48px 44px 42px;
    background:rgba(255,255,255,0.84);
    border:1px solid rgba(201,68,0,0.11);
    border-radius:36px;
    box-shadow:0 36px 90px rgba(60,20,0,0.12),0 8px 24px rgba(60,20,0,0.07),inset 0 1px 0 rgba(255,255,255,0.94);
    backdrop-filter:blur(28px) saturate(1.4);
    text-align:center;
    animation:spIn .7s cubic-bezier(0.34,1.56,0.64,1) both;
    overflow:hidden;
  }}

  /* flowing bottom stripe */
  .sp-card::after{{
    content:"";position:absolute;bottom:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,transparent 5%,#C94400 25%,#D08A00 55%,#C94400 80%,transparent 95%);
    opacity:0.45;
  }}

  @keyframes spIn{{
    from{{opacity:0;transform:translateY(32px) scale(0.92)}}
    to{{opacity:1;transform:translateY(0) scale(1)}}
  }}

  .sp-logo{{
    width:92px;height:92px;border-radius:24px;
    background:linear-gradient(138deg,#C94400 0%,#D86020 40%,#D08A00 80%,#C07000 100%);
    box-shadow:0 16px 48px rgba(201,68,0,0.38),0 4px 14px rgba(201,68,0,0.20),inset 0 1px 0 rgba(255,255,255,0.20);
    display:flex;align-items:center;justify-content:center;
    margin:0 auto 24px;
    position:relative;overflow:hidden;
    animation:spLogoIn .6s .12s cubic-bezier(0.34,1.56,0.64,1) both;
  }}
  .sp-logo::before{{
    content:"";position:absolute;top:0;left:0;right:0;height:50%;
    background:linear-gradient(180deg,rgba(255,255,255,0.22),transparent);
    border-radius:inherit;
  }}
  @keyframes spLogoIn{{from{{opacity:0;transform:scale(0.6) rotate(-12deg)}}to{{opacity:1;transform:scale(1) rotate(0)}}}}

  .sp-eyebrow{{font-size:.60rem;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:rgba(201,68,0,0.60);margin-bottom:10px;animation:spFUp .5s .25s ease both;}}
  .sp-title{{font-family:'Playfair Display',Georgia,serif;font-size:clamp(1.55rem,4.2vw,2.0rem);font-weight:600;color:#1C0800;letter-spacing:-.03em;line-height:1.15;margin:0 0 10px;animation:spFUp .5s .30s ease both;}}
  .sp-subtitle{{font-size:.85rem;color:rgba(92,32,0,0.52);line-height:1.65;margin:0 0 26px;animation:spFUp .5s .35s ease both;}}

  .sp-pills{{display:flex;flex-wrap:wrap;justify-content:center;gap:7px;margin-bottom:26px;animation:spFUp .5s .38s ease both;}}
  .sp-pill{{padding:5px 13px;border-radius:9999px;font-size:.72rem;font-weight:600;color:#C94400;background:rgba(201,68,0,0.07);border:1px solid rgba(201,68,0,0.16);}}

  .sp-progress-wrap{{animation:spFUp .5s .42s ease both;}}
  .sp-ph{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px;}}
  .sp-status{{font-size:.74rem;font-weight:500;color:rgba(92,32,0,0.48);}}
  .sp-pct{{font-size:.78rem;font-weight:700;color:#C94400;font-variant-numeric:tabular-nums;font-family:'JetBrains Mono',monospace;}}
  .sp-track{{width:100%;height:6px;border-radius:9999px;background:rgba(201,68,0,0.09);overflow:hidden;}}
  .sp-fill{{height:100%;border-radius:9999px;background:linear-gradient(90deg,#C94400,#D86020,#D08A00);background-size:200% 100%;width:0%;transition:width .16s ease;animation:spShimmer 2s linear infinite;}}
  @keyframes spShimmer{{0%{{background-position:0% 50%}}100%{{background-position:200% 50%}}}}

  .sp-dots{{display:flex;gap:5px;justify-content:center;margin-top:13px;}}
  .sp-dot{{width:6px;height:6px;border-radius:50%;background:rgba(201,68,0,0.20);animation:spDotB 1.4s ease-in-out infinite;}}
  .sp-dot:nth-child(2){{animation-delay:.20s}}
  .sp-dot:nth-child(3){{animation-delay:.40s}}
  @keyframes spDotB{{0%,80%,100%{{transform:scale(.72);opacity:.22}}42%{{transform:scale(1.22);opacity:1;background:#C94400}}}}

  @keyframes spFUp{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:translateY(0)}}}}
</style>

<div id="sp">
  <div class="sp-card">
    <div class="sp-logo">{logo_html}</div>
    <div class="sp-eyebrow">BPS Bangka Belitung · UMKM Intelligence Platform</div>
    <div class="sp-title">ALPING UMKM BPS</div>
    <div class="sp-subtitle">Memuat modul analisis marketplace, visualisasi peta lokasi usaha, dan sistem ekspor data terstruktur…</div>
    <div class="sp-pills">
      <span class="sp-pill">📊 Analisis Data</span>
      <span class="sp-pill">🗺️ Peta Interaktif</span>
      <span class="sp-pill">⬇️ Ekspor Excel</span>
      <span class="sp-pill">🔎 Filter Pintar</span>
    </div>
    <div class="sp-progress-wrap">
      <div class="sp-ph">
        <span class="sp-status" id="sp-lbl">Menginisialisasi…</span>
        <span class="sp-pct" id="sp-pct">0%</span>
      </div>
      <div class="sp-track"><div class="sp-fill" id="sp-fill"></div></div>
      <div class="sp-dots"><div class="sp-dot"></div><div class="sp-dot"></div><div class="sp-dot"></div></div>
    </div>
  </div>
</div>

<script>
(function(){{
  var steps=[
    [0,25,"Menginisialisasi komponen sistem…"],
    [25,52,"Memuat modul Shopee & Tokopedia…"],
    [52,78,"Menyiapkan engine visualisasi peta…"],
    [78,100,"Finalisasi & optimasi tampilan…"]
  ];
  var fill=document.getElementById('sp-fill'),
      lbl=document.getElementById('sp-lbl'),
      pct=document.getElementById('sp-pct');
  var si=0,cur=0;
  function tick(){{
    if(si>=steps.length)return;
    var s=steps[si];lbl.textContent=s[2];
    cur+=1;if(cur>s[1]){{si++;if(si>=steps.length)return;}}
    var v=Math.min(cur,100);
    fill.style.width=v+'%';pct.textContent=v+'%';
    setTimeout(tick,26);
  }}
  tick();
}})();
</script>""", unsafe_allow_html=True)

    for _ in range(4):
        time.sleep(0.52)
    st.session_state["__splash_done__"] = True
    st.rerun()

# ======================================================================================
# SESSION STATE
# ======================================================================================
def ensure_state():
    defaults = {
        "data_shopee": None,  "audit_shopee": {},
        "data_tokped": None,  "audit_tokped": {},
        "data_maps":   None,  "audit_maps":   {},
        "upload_time_shopee": None,
        "upload_time_tokped": None,
        "upload_time_maps":   None,
        "show_sidebar": False,
        "menu_nav":    "🏠 Dashboard",
        "nav_target":  None,
        "__boot__":    False,
        "__splash_done__": False,
        "show_tips":   True,
        "fast_mode":   False,
        "dark_mode":   False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ensure_state()

# ======================================================================================
# DATA HELPERS
# ======================================================================================
def fmt_int_id(n) -> str:
    try:    return f"{int(n):,}".replace(",",".")
    except: return "0"

def safe_title(x: str) -> str:
    if x is None: return ""
    s = str(x).strip()
    return s[:1].upper() + s[1:] if s else s

def _to_str(x):
    if pd.isna(x): return ""
    return str(x)

def clean_placeholder_to_empty(x) -> str:
    s = _to_str(x).strip()
    if not s: return ""
    if s.lower() == PLACEHOLDER.lower(): return ""
    if s.lower() in ["nan","none","null"]: return ""
    return re.sub(r"\s+", " ", s).strip()

def normalize_phone_id(x) -> str:
    s = clean_placeholder_to_empty(x)
    if not s: return ""
    s = s.replace(PHONE_EMPTY, "").strip()
    if not s: return ""
    s2 = re.sub(r"[^\d+]", "", s)
    if s2.startswith("08"):  s2 = "+62" + s2[1:]
    if re.fullmatch(r"62\d{7,15}", s2): s2 = "+" + s2
    if s2.startswith("+") and re.fullmatch(r"\+\d{8,16}", s2): return s2
    digits = re.sub(r"\D", "", s2)
    if digits.startswith("0") and len(digits) >= 9:  return "+62" + digits[1:]
    if digits.startswith("62") and len(digits) >= 9: return "+" + digits
    return s2

def normalize_url(x) -> str:
    s = clean_placeholder_to_empty(x)
    if not s: return ""
    s = s.strip()
    if s.startswith(("http://","https://")): return s
    if s.startswith("www."):  return "https://" + s
    if s.startswith("wa.me/"): return "https://" + s
    if s.startswith("instagram.com/"): return "https://" + s
    if s.startswith("@") and len(s) > 1: return "https://instagram.com/" + s[1:]
    return ""

def to_float_safe(x):
    s = clean_placeholder_to_empty(x)
    if not s: return None
    s = s.replace(",",".")
    try:    return float(s)
    except: return None

def is_in_babel(wilayah: str) -> bool:
    s = (wilayah or "").lower()
    return any(k in s for k in BABEL_KEYS)

def deteksi_tipe_usaha(nama_toko):
    if pd.isna(nama_toko) or nama_toko in ["Tidak Dilacak","Toko CSV","Anonim",""]:
        return "Tidak Terdeteksi (Butuh Nama Toko)"
    if str(nama_toko) == "FB Seller": return "Perorangan"
    nama_lower = str(nama_toko).lower()
    keyword_fisik = ["toko","warung","grosir","mart","apotek","cv.","pt.","official","agen","distributor","kios","kedai","supermarket","minimarket","cabang","jaya","abadi","makmur","motor","mobil","bengkel","snack","store","jajanan"]
    for kata in keyword_fisik:
        if kata in nama_lower: return "Ada Toko Fisik"
    return "Murni Online (Rumahan)"

def clean_maps_dataframe(df_raw):
    audit    = {"rows_in":0,"rows_out":0,"missing_cols":[],"dedup_removed":0,"invalid_coord":0,"invalid_link":0,"empty_name":0}
    out_cols = ["Foto URL","Nama Usaha","Alamat","No Telepon","Latitude","Longitude","Link"]
    if df_raw is None or df_raw.empty:
        return pd.DataFrame(columns=out_cols), audit
    audit["rows_in"] = len(df_raw)
    colmap_candidates = {
        "foto_url":   ["foto_url","foto","photo","gambar","image"],
        "nama_usaha": ["nama_usaha","nama usaha","nama","name"],
        "alamat":     ["alamat","address"],
        "no_telepon": ["no_telepon","telepon","phone","no telp","nomor"],
        "latitude":   ["latitude","lat"],
        "longitude":  ["longitude","lng","lon","long"],
        "link":       ["link","website","url","wa","ig"],
    }
    cols_lower = {c.lower(): c for c in df_raw.columns}
    found = {}
    for k, cands in colmap_candidates.items():
        real = None
        for cc in cands:
            if cc.lower() in cols_lower:
                real = cols_lower[cc.lower()]
                break
        if real is None: audit["missing_cols"].append(k)
        found[k] = real
    df = pd.DataFrame()
    for k, real in found.items():
        df[k] = "" if real is None else df_raw[real].astype(str)
    df["foto_url"]   = df["foto_url"].apply(clean_placeholder_to_empty)
    df["nama_usaha"] = df["nama_usaha"].apply(clean_placeholder_to_empty)
    df["alamat"]     = df["alamat"].apply(clean_placeholder_to_empty)
    df["no_telepon"] = df["no_telepon"].apply(normalize_phone_id)
    df["link"]       = df["link"].apply(normalize_url)
    df["latitude_f"]  = df["latitude"].apply(to_float_safe)
    df["longitude_f"] = df["longitude"].apply(to_float_safe)
    invalid_coord       = df["latitude_f"].isna() | df["longitude_f"].isna()
    audit["invalid_coord"] = int(invalid_coord.sum())
    df["latitude"]  = df["latitude_f"]
    df["longitude"] = df["longitude_f"]
    df.drop(columns=["latitude_f","longitude_f"], inplace=True)
    audit["invalid_link"] = int((df["link"] == "").sum())
    audit["empty_name"]   = int((df["nama_usaha"] == "").sum())
    def _key(r):
        name = (r["nama_usaha"] or "").lower()
        addr = (r["alamat"] or "").lower()
        lat  = "" if pd.isna(r["latitude"]) else f"{r['latitude']:.6f}"
        lng  = "" if pd.isna(r["longitude"]) else f"{r['longitude']:.6f}"
        return f"{name}__{addr}__{lat}__{lng}"
    before   = len(df)
    df["_k"] = df.apply(_key, axis=1)
    df       = df[df["_k"].str.strip() != "__"]
    df       = df.drop_duplicates(subset=["_k"], keep="first").drop(columns=["_k"])
    after    = len(df)
    audit["dedup_removed"] = int(before - after)
    df_out = pd.DataFrame({
        "Foto URL":    df["foto_url"].fillna(""),
        "Nama Usaha":  df["nama_usaha"].fillna(""),
        "Alamat":      df["alamat"].fillna(""),
        "No Telepon":  df["no_telepon"].fillna(""),
        "Latitude":    df["latitude"],
        "Longitude":   df["longitude"],
        "Link":        df["link"].fillna(""),
    })
    audit["rows_out"] = len(df_out)
    return df_out, audit

def df_to_excel_bytes(sheets: dict) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        wb          = writer.book
        header_fmt  = wb.add_format({"bold":True,"bg_color":BPS_OREN_UTAMA,"font_color":"white"})
        currency_fmt = wb.add_format({"num_format":"#,##0"})
        float_fmt   = wb.add_format({"num_format":"0.000000"})
        for sheet_name, df in sheets.items():
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            ws = writer.sheets[sheet_name]
            for col_num, value in enumerate(df.columns.values):
                ws.write(0, col_num, value, header_fmt)
            if len(df) > 0:
                ws.autofilter(0, 0, len(df), len(df.columns)-1)
            for i, col in enumerate(df.columns):
                sample  = df[col].astype(str).head(200).values
                max_len = max([len(str(col))] + [len(x) for x in sample]) if len(sample) else len(str(col))
                ws.set_column(i, i, min(max(12, max_len+2), 60))
            for i, col in enumerate(df.columns):
                if col.lower() == "harga":    ws.set_column(i, i, 18, currency_fmt)
                if col.lower() in ["latitude","longitude"]: ws.set_column(i, i, 14, float_fmt)
    return buf.getvalue()

def read_csv_files(files):
    dfs = []
    for f in files:
        df = pd.read_csv(f, dtype=str, on_bad_lines="skip")
        dfs.append(df)
    if not dfs: return pd.DataFrame(), 0
    combined = pd.concat(dfs, ignore_index=True)
    return combined, len(combined)

# ======================================================================================
# MAP RENDER
# ======================================================================================
def render_real_map_folium(df_maps, height: int = 560):
    df_plot = df_maps.dropna(subset=["Latitude","Longitude"]).copy()
    df_plot = df_plot[(df_plot["Latitude"].between(-90,90)) & (df_plot["Longitude"].between(-180,180))].copy()
    if df_plot.empty:
        st.info("Tidak ada koordinat valid untuk ditampilkan.")
        return
    tile_choice = st.selectbox("🗺️ Provider Peta", ["CartoDB Positron","CartoDB DarkMatter","OpenStreetMap"], index=0, key="maps_tile_provider")
    tiles_map   = {"OpenStreetMap":"OpenStreetMap","CartoDB Positron":"CartoDB positron","CartoDB DarkMatter":"CartoDB dark_matter"}
    center_lat  = float(df_plot["Latitude"].mean())
    center_lon  = float(df_plot["Longitude"].mean())
    try:
        m       = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles=tiles_map.get(tile_choice,"CartoDB positron"), control_scale=True)
        cluster = MarkerCluster(name="UMKM").add_to(m)
        def safe_html(s): return "" if s is None else str(s).replace("<","&lt;").replace(">","&gt;")
        for _, r in df_plot.iterrows():
            nama   = safe_html(r.get("Nama Usaha",""))
            alamat = safe_html(r.get("Alamat",""))
            telp   = safe_html(r.get("No Telepon",""))
            link   = safe_html(r.get("Link",""))
            link_html = f'<a href="{link}" target="_blank" style="color:#C94400;font-weight:700;">Buka Link →</a>' if link else "-"
            popup = f"""<div style="width:265px;font-family:'Plus Jakarta Sans',sans-serif;">
              <div style="font-weight:700;font-size:13px;color:#1C0800;margin-bottom:5px;">{nama}</div>
              <div style="font-size:11px;color:#6B3A1A;">{alamat}</div>
              <hr style="border:none;border-top:1px solid rgba(201,68,0,.12);margin:7px 0;">
              <div style="font-size:11px;color:#3A1A08;">☎️ {telp if telp else "-"}</div>
              <div style="font-size:11px;margin-top:3px;">{link_html}</div>
            </div>"""
            folium.CircleMarker(
                location=[float(r["Latitude"]), float(r["Longitude"])],
                radius=7, weight=2,
                color="#C94400", fill=True,
                fill_color="#E07030", fill_opacity=.88,
                popup=folium.Popup(popup, max_width=310),
            ).add_to(cluster)
        folium.LayerControl(collapsed=True).add_to(m)
        st_folium(m, width=None, height=height)
        st.caption("Jika peta tidak tampil, coba ganti Provider Peta.")
        return
    except Exception:
        st.warning("Provider tile tidak tersedia. Menampilkan peta fallback.")
        fig = px.scatter_geo(df_plot, lat="Latitude", lon="Longitude", hover_name="Nama Usaha", hover_data={"Alamat":True,"No Telepon":True,"Link":True}, projection="mercator", height=height)
        fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor=BPS_PAPER)
        st.plotly_chart(fig, use_container_width=True)

# ======================================================================================
# RESET HANDLER
# ======================================================================================
_qp         = st.query_params.to_dict()
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
        for _k in ["data_shopee","data_tokped","data_maps","audit_shopee","audit_tokped","audit_maps","upload_time_shopee","upload_time_tokped","upload_time_maps"]:
            st.session_state[_k] = None if ("data" in _k or "time" in _k) else {}
        st.toast("Semua data dihapus")
    st.query_params.clear()
    st.rerun()

# ======================================================================================
# NAVIGATION BOOT
# ======================================================================================
if not st.session_state["__boot__"]:
    st.session_state["__boot__"]     = True
    st.session_state["show_sidebar"] = False
    st.session_state["menu_nav"]     = "🏠 Dashboard"
    st.session_state["nav_target"]   = None

if st.session_state.get("nav_target"):
    st.session_state["menu_nav"]   = st.session_state["nav_target"]
    st.session_state["nav_target"] = None

if st.session_state.get("menu_nav") == "🏠 Dashboard":
    st.session_state["show_sidebar"] = False

if st.session_state.get("show_sidebar") and st.session_state.get("menu_nav") == "🏠 Dashboard":
    st.session_state["menu_nav"] = "🟠 Shopee"

# ======================================================================================
# SIDEBAR
# ======================================================================================
menu = "🏠 Dashboard"
if st.session_state["show_sidebar"]:
    with st.sidebar:
        st.markdown("""
<div class="sb-brand">
  <div class="sb-logo">🏛️</div>
  <div>
    <div class="sb-name">ALPING UMKM</div>
    <div class="sb-sub">BPS Bangka Belitung</div>
  </div>
</div>""", unsafe_allow_html=True)

        if st.button("⬅️ Kembali ke Dashboard", key="btn_home", use_container_width=True, type="secondary"):
            st.session_state["show_sidebar"] = False
            st.session_state["menu_nav"]     = "🏠 Dashboard"
            st.rerun()

        st.divider()
        st.markdown('<div class="sb-nav-label">📂 Modul Data</div>', unsafe_allow_html=True)

        NAV_OPTIONS = ["🟠 Shopee","🟢 Tokopedia","📍 Google Maps","📊 Export Gabungan"]
        cur_idx = NAV_OPTIONS.index(st.session_state["menu_nav"]) if st.session_state["menu_nav"] in NAV_OPTIONS else 0
        menu = st.radio("", NAV_OPTIONS, index=cur_idx, key="menu_nav", label_visibility="collapsed")

        st.divider()

        _shp_n = 0 if st.session_state.data_shopee is None else len(st.session_state.data_shopee)
        _tkp_n = 0 if st.session_state.data_tokped is None else len(st.session_state.data_tokped)
        _mp_n  = 0 if st.session_state.data_maps   is None else len(st.session_state.data_maps)
        _total = _shp_n + _tkp_n + _mp_n

        def _fmt(n): return f"{int(n):,}".replace(",",".") if n else "—"

        st.markdown('<div class="sb-nav-label">📊 Ringkasan Data</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div class="sb-stat-grid">
  <div class="sb-stat"><div class="sb-stat-val">{_fmt(_shp_n)}</div><div class="sb-stat-lbl">🟠 Shopee</div></div>
  <div class="sb-stat"><div class="sb-stat-val">{_fmt(_tkp_n)}</div><div class="sb-stat-lbl">🟢 Tokopedia</div></div>
  <div class="sb-stat"><div class="sb-stat-val">{_fmt(_mp_n)}</div><div class="sb-stat-lbl">📍 Maps</div></div>
  <div class="sb-stat"><div class="sb-stat-val">{_fmt(_total)}</div><div class="sb-stat-lbl">📦 Total</div></div>
</div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="sb-divider"><div class="sb-divider-line"></div><div class="sb-nav-label" style="margin:0;padding:0;white-space:nowrap;">PENGATURAN</div><div class="sb-divider-line"></div></div>', unsafe_allow_html=True)
        with st.expander("Opsi Tampilan & Performa", expanded=False):
            st.checkbox("Tampilkan tips cepat", value=st.session_state.get("show_tips", True), key="show_tips")
            st.checkbox("Mode cepat (kurangi chart)", value=st.session_state.get("fast_mode", False), key="fast_mode")

        st.markdown(
            '<div class="sb-footer">'
            '<div class="sb-footer-top">'
            '<div class="sb-footer-icon">🏛️</div>'
            '<div>'
            '<div class="sb-footer-name">BPS Bangka Belitung</div>'
            '<div class="sb-footer-ver">ALPING UMKM v5.0</div>'
            '</div>'
            '</div>'
            '<div class="sb-footer-bottom">'
            + _fmt(_total) + ' data dimuat &nbsp;·&nbsp; Data Statistik Berkualitas'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
else:
    hide_sidebar_css()

# ======================================================================================
# TOPBAR
# ======================================================================================
current_page_label = "Dashboard" if menu == "🏠 Dashboard" else menu.replace("🟠 ","").replace("🟢 ","").replace("📍 ","").replace("📊 ","")
topbar(current_page_label, st.session_state.get("show_sidebar", False))

# ======================================================================================
# PAGE: DASHBOARD
# ======================================================================================
if menu == "🏠 Dashboard":
    st.session_state["show_sidebar"] = False
    hide_sidebar_css()

    section_header("Dashboard Utama", "Ringkasan status data & akses cepat ke modul UMKM.", "DASHBOARD")

    df_shp  = st.session_state.data_shopee
    df_tkp  = st.session_state.data_tokped
    df_maps = st.session_state.data_maps
    shp_n   = 0 if df_shp  is None else len(df_shp)
    tkp_n   = 0 if df_tkp  is None else len(df_tkp)
    mp_n    = 0 if df_maps is None else len(df_maps)
    total_all = shp_n + tkp_n + mp_n

    # Hero
    st.markdown(f"""
<div class="bps-hero">
  <div class="hero-mesh"></div>
  <div class="bps-hero-badge">UMKM · BPS BABEL · v5.0</div>
  <h1>Kontrol Pusat Analisis UMKM</h1>
  <p>Upload data marketplace atau Google Maps, analisis dengan filter pintar, visualisasikan di peta interaktif, lalu ekspor ke Excel — semua dalam satu platform.</p>
  <div class="hero-chips">
    <span class="hero-chip">🟠 Shopee</span>
    <span class="hero-chip">🟢 Tokopedia</span>
    <span class="hero-chip">📍 Google Maps</span>
    <span class="hero-chip">📊 Export Master</span>
    <span class="hero-chip" style="font-family:'JetBrains Mono',monospace;font-size:0.78rem;">📦 {fmt_int_id(total_all)} data</span>
  </div>
</div>""", unsafe_allow_html=True)

    # KPI
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    k1.metric("📦 Total Data",  fmt_int_id(total_all), delta="All sources"  if total_all > 0 else None)
    k2.metric("🟠 Shopee",      fmt_int_id(shp_n),     delta="Loaded ✓"    if shp_n > 0     else "Belum upload")
    k3.metric("🟢 Tokopedia",   fmt_int_id(tkp_n),     delta="Loaded ✓"    if tkp_n > 0     else "Belum upload")
    k4.metric("📍 Google Maps", fmt_int_id(mp_n),      delta="Loaded ✓"    if mp_n  > 0     else "Belum upload")

    # Workflow
    st.markdown("""
<div style="margin:6px 0 4px 0;">
  <div style="font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:500;color:#3A1A08;margin-bottom:11px;">🗺️ Alur Kerja yang Disarankan</div>
  <div class="workflow-row">
    <div class="workflow-step"><div class="workflow-num">1</div><div><div class="workflow-text">Upload CSV</div><div class="workflow-sub">Shopee, Tokopedia, atau Maps</div></div></div>
    <div class="workflow-arrow">→</div>
    <div class="workflow-step"><div class="workflow-num">2</div><div><div class="workflow-text">Filter & Cari</div><div class="workflow-sub">Wilayah, tipe, harga</div></div></div>
    <div class="workflow-arrow">→</div>
    <div class="workflow-step"><div class="workflow-num">3</div><div><div class="workflow-text">Analisis</div><div class="workflow-sub">Dashboard Eksekutif</div></div></div>
    <div class="workflow-arrow">→</div>
    <div class="workflow-step"><div class="workflow-num">4</div><div><div class="workflow-text">Export</div><div class="workflow-sub">Excel / CSV master</div></div></div>
  </div>
</div>""", unsafe_allow_html=True)

    # Module cards
    def _mod_count(n, ts_key):
        ts  = st.session_state.get(ts_key)
        ts_str = f" · {ts}" if ts else ""
        if n > 0: return f'<span class="module-card-badge ready">✅ {fmt_int_id(n)} data{ts_str}</span>'
        return '<span class="module-card-badge empty">⏳ Belum diupload</span>'

    st.markdown(f"""
<div class="module-grid">
  <div class="module-card shopee">
    <div class="module-icon-wrap">🟠</div>
    <div class="module-card-title">Shopee</div>
    <div class="module-card-desc">Ekstrak produk UMKM Bangka Belitung dari Shopee Marketplace dengan deteksi nama toko via API.</div>
    {_mod_count(shp_n,"upload_time_shopee")}
  </div>
  <div class="module-card tokped">
    <div class="module-icon-wrap">🟢</div>
    <div class="module-card-title">Tokopedia</div>
    <div class="module-card-desc">Proses data produk Tokopedia dengan auto-deteksi kolom dan filter wilayah otomatis.</div>
    {_mod_count(tkp_n,"upload_time_tokped")}
  </div>
  <div class="module-card maps">
    <div class="module-icon-wrap">📍</div>
    <div class="module-card-title">Google Maps</div>
    <div class="module-card-desc">Visualisasi lokasi UMKM di peta interaktif dengan auto-clean koordinat & kontak.</div>
    {_mod_count(mp_n,"upload_time_maps")}
  </div>
  <div class="module-card export">
    <div class="module-icon-wrap">📊</div>
    <div class="module-card-title">Export Gabungan</div>
    <div class="module-card-desc">Konsolidasi semua sumber data ke 1 file Excel premium dengan autofilter & format rapi.</div>
    <span class="module-card-badge {"ready" if total_all > 0 else "empty"}">{"✅ Siap diexport" if total_all > 0 else "⏳ Perlu data dulu"}</span>
  </div>
</div>""", unsafe_allow_html=True)

    ca, cb = st.columns([1,1], gap="medium")
    with ca:
        if st.button("🚀 Mulai Upload Data Shopee", use_container_width=True, type="primary"):
            goto_menu("🟠 Shopee")
    with cb:
        if st.button("📊 Lihat Export Gabungan", use_container_width=True, type="secondary"):
            goto_menu("📊 Export Gabungan")

    if st.session_state.get("show_tips", True):
        with st.container(border=True):
            st.markdown("""
<div style="display:flex;gap:15px;flex-wrap:wrap;">
  <div style="flex:1;min-width:210px;">
    <div style="font-weight:700;color:#3A1A08;margin-bottom:5px;font-size:.84rem;">💡 Tips Performa</div>
    <div style="font-size:.76rem;color:#A07040;line-height:1.75;">• Aktifkan <b>Mode Cepat</b> di Settings untuk file besar<br>• Naikkan <b>jeda request</b> API Shopee kalau kena rate limit<br>• Upload beberapa CSV sekaligus untuk batch processing</div>
  </div>
  <div style="flex:1;min-width:210px;">
    <div style="font-weight:700;color:#3A1A08;margin-bottom:5px;font-size:.84rem;">✅ Kualitas Data</div>
    <div style="font-size:.76rem;color:#A07040;line-height:1.75;">• Pastikan kolom <b>wilayah/lokasi</b> terisi benar<br>• Google Maps butuh <b>lat/lon valid</b> untuk tampil di peta<br>• Link & telepon kosong dibersihkan otomatis</div>
  </div>
  <div style="flex:1;min-width:210px;">
    <div style="font-weight:700;color:#3A1A08;margin-bottom:5px;font-size:.84rem;">📊 Analisis Terbaik</div>
    <div style="font-size:.76rem;color:#A07040;line-height:1.75;">• Cek tab <b>Audit</b> setelah upload untuk validasi data<br>• Gunakan <b>Top 10 Toko</b> di Executive Dashboard<br>• Export Gabungan untuk laporan lintas platform</div>
  </div>
</div>""", unsafe_allow_html=True)

# ======================================================================================
# PAGE: SHOPEE
# ======================================================================================
elif menu == "🟠 Shopee":
    section_header("Shopee Marketplace", "Analisis & ekstraksi data UMKM Shopee.", "MARKETPLACE")
    banner("ALPING UMKM — Shopee", "Ekstraksi data UMKM dari Shopee Marketplace (Bangka Belitung)")

    with st.container(border=True):
        left, right = st.columns([1.25, 0.95], gap="large")
        with left:
            st.subheader("📥 Input Data")
            files    = st.file_uploader("Unggah CSV Shopee", type=["csv"], accept_multiple_files=True, key="file_shp")
            mode_api = st.toggle("🔎 Deteksi Nama Toko via API Shopee", value=True, key="api_shp")
            colA, colB, colC = st.columns(3)
            with colA: api_timeout  = st.number_input("Timeout API (detik)", min_value=1, max_value=10, value=2, step=1)
            with colB: api_sleep    = st.number_input("Jeda per request (s)", min_value=0.0, max_value=2.0, value=0.0, step=0.1)
            with colC: max_api_calls = st.number_input("Maks panggilan API", min_value=0, max_value=50000, value=8000, step=500)
            if st.session_state.get("show_tips", True):
                st.caption("Tips: kalau scraping terdeteksi robot, naikkan jeda request.")
            run = st.button("🚀 Proses Data Shopee", type="primary", use_container_width=True)
        with right:
            ts_shp = st.session_state.get("upload_time_shopee")
            if ts_shp: st.markdown(f'<div class="upload-timestamp">✅ Upload terakhir: {ts_shp}</div>', unsafe_allow_html=True)
            st.markdown("""
<div class="upload-info-card">
  <div class="upload-info-title">🧾 Ketentuan Data</div>
  <div class="upload-spec-row">
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Filter otomatis ke <b>Bangka Belitung</b></div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Harga dibersihkan ke integer</div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Tipe usaha via heuristik nama toko</div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Duplikat diabaikan otomatis</div></div>
  </div>
</div>""", unsafe_allow_html=True)
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
                        total_semua_baris += len(df_temp); f.seek(0)

                    hasil = []; total_baris = 0; err_h = 0; luar_wilayah = 0
                    progress = st.progress(0); info = st.empty()
                    baris_diproses = 0; api_calls = 0

                    for file in files:
                        df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                        total_baris += len(df_raw)

                        if "Link" in df_raw.columns and "Nama Produk" in df_raw.columns:
                            col_link=df_raw.columns[df_raw.columns.tolist().index("Link")]
                            col_nama="Nama Produk"; col_harga="Harga"; col_wilayah="Wilayah"
                        else:
                            col_link    = next((c for c in df_raw.columns if "href"    in c.lower()), df_raw.columns[0])
                            col_nama    = next((c for c in df_raw.columns if "whitespace-normal" in c.lower()), df_raw.columns[min(3,len(df_raw.columns)-1)])
                            col_harga   = next((c for c in df_raw.columns if "font-medium" in c.lower()), df_raw.columns[min(4,len(df_raw.columns)-1)])
                            idx_wilayah = 7 if len(df_raw.columns) > 7 else len(df_raw.columns)-1
                            col_wilayah = next((c for c in df_raw.columns if "ml-[3px]" in c.lower()), df_raw.columns[idx_wilayah])

                        for i in range(len(df_raw)):
                            row         = df_raw.iloc[i]
                            link        = str(row.get(col_link, ""))
                            nama_produk = str(row.get(col_nama, ""))
                            harga_str   = str(row.get(col_harga, ""))
                            lokasi      = safe_title(str(row.get(col_wilayah, "")))

                            if not is_in_babel(lokasi): luar_wilayah += 1; baris_diproses += 1; continue

                            try:
                                harga_bersih = harga_str.replace(".","").replace(",","")
                                angka_list   = re.findall(r"\d+", harga_bersih)
                                val_h        = int(angka_list[0]) if angka_list else 0
                                if val_h > 1_000_000_000: val_h = 0
                            except Exception:
                                val_h = 0; err_h += 1

                            toko = "Tidak Dilacak"
                            if mode_api and api_calls < int(max_api_calls):
                                match = re.search(r"i\.(\d+)\.", link)
                                if match:
                                    try:
                                        api_calls += 1
                                        res = requests.get(f"https://shopee.co.id/api/v4/shop/get_shop_base?shopid={match.group(1)}", headers={"User-Agent":"Mozilla/5.0"}, timeout=float(api_timeout))
                                        if res.status_code == 200: toko = res.json().get("data",{}).get("name","Anonim")
                                    except Exception: pass
                                    if api_sleep and api_sleep > 0: time.sleep(float(api_sleep))

                            tipe_usaha = deteksi_tipe_usaha(toko)
                            hasil.append({"Nama Toko":toko,"Nama Produk":nama_produk,"Harga":val_h,"Wilayah":lokasi,"Tipe Usaha":tipe_usaha,"Link":link})
                            baris_diproses += 1
                            if baris_diproses % 25 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses/max(total_semua_baris,1),1.0)
                                progress.progress(pct)
                                info.markdown(f"**⏳ Progress:** {fmt_int_id(baris_diproses)} / {fmt_int_id(total_semua_baris)} ({int(pct*100)}%) · API calls: {fmt_int_id(api_calls)}")

                    progress.empty(); info.empty()
                    df = pd.DataFrame(hasil)
                    st.session_state.data_shopee  = df
                    st.session_state.audit_shopee = {"file_count":len(files),"total_rows":total_baris,"valid_rows":len(df),"luar_wilayah":luar_wilayah,"error_harga":err_h,"api_calls":api_calls}
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
            c1, c2, c3, c4 = st.columns([1.2,1.2,1.6,1.2], gap="medium")
            with c1: f_wil  = st.multiselect("📍 Wilayah",    options=sorted(df_shp["Wilayah"].unique()),    default=sorted(df_shp["Wilayah"].unique()),    key="f_wil_shp")
            with c2: f_tipe = st.multiselect("🏢 Tipe Usaha", options=sorted(df_shp["Tipe Usaha"].unique()), default=sorted(df_shp["Tipe Usaha"].unique()), key="f_tipe_shp")
            with c3: q      = st.text_input("🔎 Cari (nama toko / produk)", value="", key="q_shp")
            with c4:
                max_h  = int(df_shp["Harga"].max()) if df_shp["Harga"].max() > 0 else 1_000_000
                f_hrg  = st.slider("💰 Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_shp")

        df_f = df_shp[df_shp["Wilayah"].isin(f_wil) & df_shp["Tipe Usaha"].isin(f_tipe) & (df_shp["Harga"] >= f_hrg[0]) & (df_shp["Harga"] <= f_hrg[1])].copy()
        if q.strip():
            qq   = q.strip().lower()
            df_f = df_f[df_f["Nama Toko"].astype(str).str.lower().str.contains(qq, na=False) | df_f["Nama Produk"].astype(str).str.lower().str.contains(qq, na=False)]

        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard","🗄️ Database","📑 Audit"])
        with tab1:
            n_total  = len(df_f); n_online = (df_f["Tipe Usaha"] == "Murni Online (Rumahan)").sum()
            n_fisik  = (df_f["Tipe Usaha"] == "Ada Toko Fisik").sum(); n_wil = df_f["Wilayah"].nunique()
            avg_harga = int(df_f["Harga"][df_f["Harga"] > 0].mean()) if (df_f["Harga"] > 0).any() else 0
            n_toko   = df_f["Nama Toko"].nunique()
            m1,m2,m3,m4,m5,m6 = st.columns(6)
            m1.metric("📌 Total Produk",   fmt_int_id(n_total))
            m2.metric("🏠 Murni Online",   fmt_int_id(n_online))
            m3.metric("🏬 Ada Toko Fisik", fmt_int_id(n_fisik))
            m4.metric("🗺️ Wilayah",        fmt_int_id(n_wil))
            m5.metric("🏪 Toko Unik",      fmt_int_id(n_toko))
            m6.metric("💰 Rata-rata Harga","Rp " + fmt_int_id(avg_harga))

            if not st.session_state.get("fast_mode") and not df_f.empty:
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", hole=.50, title="Komposisi Model Bisnis", color_discrete_sequence=BPS_PALETTE)
                    fig.update_traces(textposition="outside", textinfo="percent+label", pull=[.04]*len(df_f["Tipe Usaha"].unique()))
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(family="Plus Jakarta Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah").sort_values("Jumlah", ascending=True)
                    fig = px.bar(grp, y="Wilayah", x="Jumlah", orientation="h", title="Produk per Wilayah", color="Jumlah", color_continuous_scale=["#F8C060","#C94400"])
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, font=dict(family="Plus Jakarta Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)
                g3, g4 = st.columns(2, gap="large")
                with g3:
                    df_hrg = df_f[df_f["Harga"] > 0]
                    if not df_hrg.empty:
                        fig = px.histogram(df_hrg, x="Harga", nbins=30, title="Distribusi Harga Produk", color_discrete_sequence=["#C94400"])
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Plus Jakarta Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                        fig.update_xaxes(tickprefix="Rp ")
                        st.plotly_chart(fig, use_container_width=True)
                with g4:
                    top_toko = df_f[df_f["Nama Toko"].notna() & ~df_f["Nama Toko"].isin(["Tidak Dilacak","Anonim",""])]["Nama Toko"].value_counts().head(10).reset_index()
                    top_toko.columns = ["Toko","Produk"]
                    if not top_toko.empty:
                        fig = px.bar(top_toko.sort_values("Produk"), y="Toko", x="Produk", orientation="h", title="Top 10 Toko Paling Aktif", color="Produk", color_continuous_scale=["#F8C060","#C94400"])
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, font=dict(family="Plus Jakarta Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                        st.plotly_chart(fig, use_container_width=True)
        with tab2:
            render_premium_table(df_f, max_rows=300, source="Shopee")
            st.download_button("⬇️ Unduh Excel — Shopee", data=df_to_excel_bytes({"Data Shopee":df_f}), file_name=f"UMKM_Shopee_{datetime.date.today()}.xlsx", use_container_width=True, type="primary")
        with tab3:
            render_audit_cards(st.session_state.audit_shopee or {}, source="Shopee")

# ======================================================================================
# PAGE: TOKOPEDIA
# ======================================================================================
elif menu == "🟢 Tokopedia":
    section_header("Tokopedia Marketplace", "Workflow Tokopedia dengan UI enterprise.", "MARKETPLACE")
    banner("ALPING UMKM — Tokopedia", "Ekstraksi data UMKM dari Tokopedia (Bangka Belitung)")

    with st.container(border=True):
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV Tokopedia", type=["csv"], accept_multiple_files=True, key="file_tkp")
            run   = st.button("🚀 Proses Data Tokopedia", type="primary", use_container_width=True)
        with col2:
            ts_tkp = st.session_state.get("upload_time_tokped")
            if ts_tkp: st.markdown(f'<div class="upload-timestamp">✅ Upload terakhir: {ts_tkp}</div>', unsafe_allow_html=True)
            st.markdown("""
<div class="upload-info-card">
  <div class="upload-info-title">🧾 Ketentuan Data</div>
  <div class="upload-spec-row">
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Auto-deteksi nama kolom CSV</div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Filter otomatis ke <b>Babel</b></div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Multi-produk per baris didukung</div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div>Duplikat dihapus otomatis</div></div>
  </div>
</div>""", unsafe_allow_html=True)
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
                        total_semua_baris += len(df_temp); f.seek(0)

                    hasil = []; total_baris = 0; err_h = 0; luar_wilayah = 0
                    progress = st.progress(0); info = st.empty(); baris_diproses = 0

                    for file in files:
                        df_raw = pd.read_csv(file, dtype=str, on_bad_lines="skip")
                        total_baris += len(df_raw)

                        if "Link" in df_raw.columns and "Nama Produk" in df_raw.columns:
                            col_links=["Link"]; col_namas=["Nama Produk"]; col_hargas=["Harga"]; col_lokasis=["Wilayah"]; col_tokos=["Nama Toko"]
                        else:
                            col_links  = [c for c in df_raw.columns if "Ui5"     in c]
                            col_namas  = [c for c in df_raw.columns if "+tnoqZhn" in c]
                            col_hargas = [c for c in df_raw.columns if "urMOIDHH" in c]
                            col_lokasis= [c for c in df_raw.columns if "gxi+fs"  in c]
                            col_tokos  = [c for c in df_raw.columns if "si3CN"   in c]

                        max_items = max(len(col_links),len(col_namas),len(col_hargas),len(col_lokasis),len(col_tokos)) or 1

                        for i in range(len(df_raw)):
                            for j in range(max_items):
                                try:
                                    link      = str(df_raw.iloc[i][col_links[j]])  if j < len(col_links)  else "nan"
                                    nama      = str(df_raw.iloc[i][col_namas[j]])  if j < len(col_namas)  else "nan"
                                    harga_str = str(df_raw.iloc[i][col_hargas[j]]) if j < len(col_hargas) else "0"
                                    lokasi    = safe_title(str(df_raw.iloc[i][col_lokasis[j]])) if j < len(col_lokasis) else "-"
                                    toko      = str(df_raw.iloc[i][col_tokos[j]])  if j < len(col_tokos)  else "Toko CSV"
                                    if link == "nan" or nama == "nan": continue
                                    if not is_in_babel(lokasi): luar_wilayah += 1; continue
                                    try:
                                        harga_bersih = harga_str.replace(".","").replace(",","")
                                        angka_list   = re.findall(r"\d+", harga_bersih)
                                        val_h        = int(angka_list[0]) if angka_list else 0
                                        if val_h > 1_000_000_000: val_h = 0
                                    except Exception:
                                        val_h = 0; err_h += 1
                                    if val_h > 0:
                                        hasil.append({"Nama Toko":toko,"Nama Produk":nama,"Harga":val_h,"Wilayah":lokasi,"Tipe Usaha":deteksi_tipe_usaha(toko),"Link":link})
                                except Exception: continue
                            baris_diproses += 1
                            if baris_diproses % 25 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses/max(total_semua_baris,1),1.0)
                                progress.progress(pct)
                                info.markdown(f"**⏳ Progress:** {fmt_int_id(baris_diproses)} / {fmt_int_id(total_semua_baris)} ({int(pct*100)}%)")

                    progress.empty(); info.empty()
                    df_final = pd.DataFrame(hasil).drop_duplicates()
                    st.session_state.data_tokped  = df_final
                    st.session_state.audit_tokped = {"file_count":len(files),"total_rows":total_baris,"valid_rows":len(df_final),"luar_wilayah":luar_wilayah,"error_harga":err_h}
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
            c1, c2, c3 = st.columns([1.2,1.2,1.6], gap="medium")
            with c1: f_wil  = st.multiselect("📍 Wilayah",    options=sorted(df_tkp["Wilayah"].unique()),    default=sorted(df_tkp["Wilayah"].unique()),    key="f_wil_tkp")
            with c2: f_tipe = st.multiselect("🏢 Tipe Usaha", options=sorted(df_tkp["Tipe Usaha"].unique()), default=sorted(df_tkp["Tipe Usaha"].unique()), key="f_tipe_tkp")
            with c3: q      = st.text_input("🔎 Cari", value="", key="q_tkp")
            max_h = int(df_tkp["Harga"].max()) if df_tkp["Harga"].max() > 0 else 1_000_000
            f_hrg = st.slider("💰 Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_tkp")

        df_f = df_tkp[df_tkp["Wilayah"].isin(f_wil) & df_tkp["Tipe Usaha"].isin(f_tipe) & (df_tkp["Harga"] >= f_hrg[0]) & (df_tkp["Harga"] <= f_hrg[1])].copy()
        if q.strip():
            qq   = q.strip().lower()
            df_f = df_f[df_f["Nama Toko"].astype(str).str.lower().str.contains(qq, na=False) | df_f["Nama Produk"].astype(str).str.lower().str.contains(qq, na=False)]

        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard","🗄️ Database","📑 Audit"])
        with tab1:
            n_total  = len(df_f); n_online = (df_f["Tipe Usaha"] == "Murni Online (Rumahan)").sum()
            n_fisik  = (df_f["Tipe Usaha"] == "Ada Toko Fisik").sum(); n_wil = df_f["Wilayah"].nunique()
            avg_harga = int(df_f["Harga"][df_f["Harga"] > 0].mean()) if (df_f["Harga"] > 0).any() else 0
            n_toko   = df_f["Nama Toko"].nunique()
            m1,m2,m3,m4,m5,m6 = st.columns(6)
            m1.metric("📌 Total Produk",   fmt_int_id(n_total))
            m2.metric("🏠 Murni Online",   fmt_int_id(n_online))
            m3.metric("🏬 Ada Toko Fisik", fmt_int_id(n_fisik))
            m4.metric("🗺️ Wilayah",        fmt_int_id(n_wil))
            m5.metric("🏪 Toko Unik",      fmt_int_id(n_toko))
            m6.metric("💰 Rata-rata Harga","Rp " + fmt_int_id(avg_harga))
            if not st.session_state.get("fast_mode") and not df_f.empty:
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", hole=.50, title="Komposisi Model Bisnis", color_discrete_sequence=BPS_PALETTE)
                    fig.update_traces(textposition="outside", textinfo="percent+label", pull=[.04]*len(df_f["Tipe Usaha"].unique()))
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(family="Plus Jakarta Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah").sort_values("Jumlah", ascending=True)
                    fig = px.bar(grp, y="Wilayah", x="Jumlah", orientation="h", title="Produk per Wilayah", color="Jumlah", color_continuous_scale=["#F8C060","#C94400"])
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, font=dict(family="Plus Jakarta Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)
                g3, g4 = st.columns(2, gap="large")
                with g3:
                    df_hrg = df_f[df_f["Harga"] > 0]
                    if not df_hrg.empty:
                        fig = px.histogram(df_hrg, x="Harga", nbins=30, title="Distribusi Harga Produk", color_discrete_sequence=["#C94400"])
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Plus Jakarta Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                        fig.update_xaxes(tickprefix="Rp ")
                        st.plotly_chart(fig, use_container_width=True)
                with g4:
                    top_toko = df_f[df_f["Nama Toko"].notna() & ~df_f["Nama Toko"].isin(["Tidak Dilacak","Anonim",""])]["Nama Toko"].value_counts().head(10).reset_index()
                    top_toko.columns = ["Toko","Produk"]
                    if not top_toko.empty:
                        fig = px.bar(top_toko.sort_values("Produk"), y="Toko", x="Produk", orientation="h", title="Top 10 Toko Paling Aktif", color="Produk", color_continuous_scale=["#F8C060","#C94400"])
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, font=dict(family="Plus Jakarta Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                        st.plotly_chart(fig, use_container_width=True)
        with tab2:
            render_premium_table(df_f, max_rows=300, source="Tokopedia")
            st.download_button("⬇️ Unduh Excel — Tokopedia", data=df_to_excel_bytes({"Data Tokopedia":df_f}), file_name=f"UMKM_Tokopedia_{datetime.date.today()}.xlsx", use_container_width=True, type="primary")
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
            files    = st.file_uploader("Unggah CSV Google Maps", type=["csv"], accept_multiple_files=True, key="file_maps")
            do_clean = st.toggle("✨ Auto-clean (disarankan)", value=True, key="clean_maps")
            run      = st.button("🚀 Proses Data Google Maps", type="primary", use_container_width=True)
        with col2:
            ts_maps = st.session_state.get("upload_time_maps")
            if ts_maps: st.markdown(f'<div class="upload-timestamp">✅ Upload terakhir: {ts_maps}</div>', unsafe_allow_html=True)
            st.markdown("""
<div class="upload-info-card">
  <div class="upload-info-title">🧾 Format Kolom</div>
  <div class="upload-spec-row">
    <div class="upload-spec"><div class="upload-spec-dot"></div><div><code>foto_url</code> — URL foto</div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div><code>nama_usaha</code> — Nama toko</div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div><code>latitude / longitude</code></div></div>
    <div class="upload-spec"><div class="upload-spec-dot"></div><div><code>no_telepon / link</code></div></div>
  </div>
</div>""", unsafe_allow_html=True)
            st.caption("Nama kolom berbeda? Sistem tetap coba mapping otomatis.")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Google Maps terlebih dahulu.")
        else:
            with st.status("Memproses data Google Maps…", expanded=True) as status:
                try:
                    df_raw, _ = read_csv_files(files)
                    if do_clean:
                        df_clean, audit = clean_maps_dataframe(df_raw)
                    else:
                        df_clean = df_raw.copy()
                        audit    = {"rows_in":len(df_raw),"rows_out":len(df_clean),"dedup_removed":0,"invalid_coord":0,"invalid_link":0,"empty_name":0,"missing_cols":[]}
                    st.session_state.data_maps  = df_clean
                    st.session_state.audit_maps = {"file_count":len(files),"rows_in":audit.get("rows_in",0),"rows_out":audit.get("rows_out",0),"dedup_removed":audit.get("dedup_removed",0),"invalid_coord":audit.get("invalid_coord",0),"invalid_link":audit.get("invalid_link",0),"empty_name":audit.get("empty_name",0),"missing_cols":audit.get("missing_cols",[])}
                    st.session_state["upload_time_maps"] = datetime.datetime.now().strftime("%d/%m %H:%M")
                    status.update(label="✅ Selesai memproses Google Maps", state="complete", expanded=False)
                    st.toast(f"Google Maps: {fmt_int_id(len(df_clean))} baris siap dianalisis", icon="✅")
                except Exception as e:
                    status.update(label="❌ Gagal memproses Google Maps", state="error", expanded=True)
                    st.error(f"Error Sistem Google Maps: {e}")

    df_maps = st.session_state.data_maps
    if df_maps is not None and not df_maps.empty:
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard","🧹 Data Bersih","📑 Audit"])
        with tab1:
            lat_col  = "Latitude"   if "Latitude"   in df_maps.columns else ("latitude"   if "latitude"   in df_maps.columns else None)
            link_col = "Link"       if "Link"        in df_maps.columns else ("link"       if "link"       in df_maps.columns else None)
            tel_col  = "No Telepon" if "No Telepon"  in df_maps.columns else ("no_telepon" if "no_telepon" in df_maps.columns else None)
            nama_col = "Nama Usaha" if "Nama Usaha"  in df_maps.columns else ("nama_usaha" if "nama_usaha" in df_maps.columns else None)
            n_total  = len(df_maps)
            n_coord  = int(df_maps[lat_col].notna().sum()) if lat_col else 0
            n_link   = int((df_maps[link_col].astype(str).str.len() > 4).sum()) if link_col else 0
            n_telp   = int((df_maps[tel_col].astype(str).str.startswith("+")).sum()) if tel_col else 0
            n_nama   = int((df_maps[nama_col].astype(str).str.len() > 1).sum()) if nama_col else 0
            m1,m2,m3,m4,m5 = st.columns(5)
            m1.metric("📌 Total Lokasi",    fmt_int_id(n_total))
            m2.metric("📍 Koordinat Valid", fmt_int_id(n_coord))
            m3.metric("🏷️ Ada Nama Usaha",  fmt_int_id(n_nama))
            m4.metric("🔗 Link Valid",       fmt_int_id(n_link))
            m5.metric("☎️ No Telp Valid",    fmt_int_id(n_telp))
            if not st.session_state.get("fast_mode"):
                if "Latitude" in df_maps.columns and "Longitude" in df_maps.columns:
                    render_real_map_folium(df_maps, height=560)
                else:
                    st.info("Map membutuhkan schema kolom bersih: Latitude & Longitude. Aktifkan Auto-clean.")
        with tab2:
            render_premium_table(df_maps, max_rows=300, source="Google Maps")
            c1, c2 = st.columns(2, gap="medium")
            with c1: st.download_button("⬇️ Unduh Excel — Google Maps", data=df_to_excel_bytes({"Data Google Maps":df_maps}), file_name=f"UMKM_GoogleMaps_{datetime.date.today()}.xlsx", use_container_width=True, type="primary")
            with c2: st.download_button("⬇️ Unduh CSV — Google Maps",   data=df_maps.to_csv(index=False).encode("utf-8"),     file_name=f"UMKM_GoogleMaps_{datetime.date.today()}.csv",  use_container_width=True)
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

    st.markdown(f"""
<div class="export-hero">
  <div class="export-hero-icon">📦</div>
  <div>
    <div class="export-hero-title">Master Data UMKM Bangka Belitung</div>
    <div class="export-hero-sub">
      Gabungkan data dari Shopee, Tokopedia, dan Google Maps menjadi 1 file Excel terstruktur
      dengan sheet terpisah, autofilter, header berwarna, dan format kolom otomatis.<br>
      <b style="color:var(--fire)">{fmt_int_id(total_e)} total baris</b> siap diexport dari <b>{sum([df_shp_ready,df_tkp_ready,df_maps_ready])}</b> sumber data.
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    if not (df_shp_ready or df_tkp_ready or df_maps_ready):
        st.markdown("""
<div class="empty-state">
  <div class="empty-icon">📭</div>
  <div class="empty-title">Belum Ada Data</div>
  <div class="empty-sub">Proses dulu data di modul Shopee, Tokopedia, atau Google Maps.<br>Setelah itu kembali ke halaman ini untuk export.</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("#### 📋 Status Sumber Data")
        def _export_src(icon, name, n, ts_key, ready):
            ts       = st.session_state.get(ts_key, "")
            ts_str   = f"· Diupload {ts}" if ts else ""
            badge_cls = "ready" if ready else "empty"
            badge_txt = f"✅ {fmt_int_id(n)} baris" if ready else "⏳ Belum ada data"
            card_cls  = "ready" if ready else "empty"
            return f"""<div class="export-src-card {card_cls}" style="margin-bottom:9px;">
  <div class="export-src-left">
    <div class="export-src-icon">{icon}</div>
    <div><div class="export-src-name">{name}</div><div class="export-src-meta">{ts_str if ready else "Belum diproses"}</div></div>
  </div>
  <span class="export-src-badge {badge_cls}">{badge_txt}</span>
</div>"""
        st.markdown(
            _export_src("🟠","Shopee",      shp_n_e, "upload_time_shopee", df_shp_ready)  +
            _export_src("🟢","Tokopedia",   tkp_n_e, "upload_time_tokped", df_tkp_ready)  +
            _export_src("📍","Google Maps", maps_n_e,"upload_time_maps",   df_maps_ready),
            unsafe_allow_html=True)

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
<div style="display:flex;flex-direction:column;gap:8px;">
  <div style="display:flex;gap:8px;align-items:center;">
    <span style="font-size:1.05rem">📄</span>
    <div><div style="font-weight:700;font-size:.84rem;color:var(--ink-800);">Format: Excel (.xlsx)</div>
    <div style="font-size:.74rem;color:var(--ink-300);">{sum([df_shp_ready,df_tkp_ready,df_maps_ready])} sheet · Autofilter · Header oranye · Format kolom otomatis</div></div>
  </div>
  <div style="display:flex;gap:8px;align-items:center;">
    <span style="font-size:1.05rem">📦</span>
    <div><div style="font-weight:700;font-size:.84rem;color:var(--ink-800);">{fmt_int_id(total_e)} total baris data</div>
    <div style="font-size:.74rem;color:var(--ink-300);">File: Master_UMKM_BPS_{datetime.date.today()}.xlsx</div></div>
  </div>
</div>""", unsafe_allow_html=True)
            with col_btn:
                st.download_button(label="⬇️ Unduh Excel Master", data=excel_bytes, file_name=f"Master_UMKM_BPS_{datetime.date.today()}.xlsx", use_container_width=True, type="primary")

# ======================================================================================
# FOOTER
# ======================================================================================
st.markdown("""
<div class="bps-footer">
  <span style="font-size:1.05rem">🏛️</span>
  <span>Built with Streamlit</span>
  <span class="footer-dot"></span>
  <span>Badan Pusat Statistik · UMKM Toolkit</span>
  <span class="footer-dot"></span>
  <span>Bangka Belitung · v5.0</span>
</div>""", unsafe_allow_html=True)
