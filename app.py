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
# MASTER CSS — Ultra-Luxury v4 (Maximalist Editorial Government)
# ======================================================================================
MASTER_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,600&family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ═══════════════════════════════════════════════════════════════════════════
   DESIGN SYSTEM TOKENS
   ═══════════════════════════════════════════════════════════════════════════ */
:root {
  /* Signature palette — deep burnt sienna + warm gold */
  --ember:       #C94400;
  --ember-mid:   #E05A1A;
  --ember-lite:  #F07A40;
  --gold:        #D4880A;
  --gold-lite:   #F0B030;
  --gold-pale:   #FCEABD;

  /* Ink scale */
  --ink-950: #110200;
  --ink-900: #1C0400;
  --ink-800: #2E0A00;
  --ink-600: #5A2000;
  --ink-400: #9A5028;
  --ink-200: #D4A080;
  --ink-100: #EDD0B8;
  --ink-050: #FAF0EA;

  /* Surfaces */
  --surf-0:  #FFFFFF;
  --surf-1:  rgba(255,252,248,0.96);
  --surf-2:  rgba(255,247,240,0.85);
  --glass:   rgba(255,255,255,0.68);
  --glass-b: rgba(201,68,0,0.12);
  --glass-b2:rgba(201,68,0,0.22);

  /* Elevation shadows */
  --e0: none;
  --e1: 0 1px 3px rgba(201,68,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --e2: 0 4px 16px rgba(201,68,0,0.09), 0 2px 6px rgba(0,0,0,0.05);
  --e3: 0 10px 36px rgba(201,68,0,0.13), 0 4px 12px rgba(0,0,0,0.07);
  --e4: 0 20px 64px rgba(201,68,0,0.18), 0 6px 20px rgba(0,0,0,0.09);
  --e5: 0 36px 100px rgba(201,68,0,0.24), 0 10px 32px rgba(0,0,0,0.11);
  --glow: 0 0 0 1px rgba(201,68,0,0.15), 0 8px 32px rgba(201,68,0,0.40), 0 2px 8px rgba(201,68,0,0.24);
  --glow-gold: 0 0 0 1px rgba(212,136,10,0.20), 0 8px 32px rgba(212,136,10,0.36);

  /* Radii */
  --r-xs:   4px;
  --r-sm:   8px;
  --r-md:  14px;
  --r-lg:  20px;
  --r-xl:  28px;
  --r-2xl: 40px;
  --r-pill: 9999px;

  /* Easing */
  --ease-back:   cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-out:    cubic-bezier(0.0, 0.0, 0.2, 1);
  --ease-inout:  cubic-bezier(0.4, 0, 0.2, 1);
  --dur-snap:    100ms;
  --dur-fast:    180ms;
  --dur-base:    280ms;
  --dur-slow:    500ms;
}

/* ═══════════════════════════════════════════════════════════════════════════
   GLOBAL RESET & BASE
   ═══════════════════════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  font-family: 'Outfit', system-ui, sans-serif;
  background:
    radial-gradient(ellipse 160% 100% at -15% -10%, rgba(201,68,0,0.10) 0%, transparent 50%),
    radial-gradient(ellipse 120% 80%  at 115%  -5%, rgba(212,136,10,0.08) 0%, transparent 48%),
    radial-gradient(ellipse  80% 60%  at  20% 110%, rgba(201,68,0,0.06) 0%, transparent 55%),
    radial-gradient(ellipse  60% 40%  at  90% 100%, rgba(212,136,10,0.05) 0%, transparent 50%),
    linear-gradient(158deg,
      #FFFFFF   0%,
      #FFFCF8   25%,
      #FFF8F0   55%,
      #FFF3E6   80%,
      #FFEDE0  100%
    ) !important;
  background-attachment: fixed !important;
  color: var(--ink-900) !important;
}

[data-testid="stHeader"] { background: transparent !important; }
section.main, .main, .block-container { background: transparent !important; }
.block-container {
  max-width: 1300px;
  padding-top: 0.2rem !important;
  padding-bottom: 6rem  !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   GRAIN TEXTURE OVERLAY
   ═══════════════════════════════════════════════════════════════════════════ */
body::after {
  content: "";
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cfilter id='grain'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23grain)' opacity='0.028'/%3E%3C/svg%3E");
  pointer-events: none; z-index: 9998; opacity: 0.6;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TOP ACCENT STRIPE
   ═══════════════════════════════════════════════════════════════════════════ */
.block-container::before {
  content: "";
  display: block; height: 3px; width: 100%;
  margin-bottom: 0px;
  background: linear-gradient(90deg,
    transparent 0%,
    var(--ember) 12%,
    var(--ember-mid) 30%,
    var(--gold) 50%,
    var(--ember-mid) 70%,
    var(--ember) 88%,
    transparent 100%
  );
  border-radius: var(--r-pill);
  opacity: 0.5;
  animation: accentPulse 4s ease-in-out infinite;
}
@keyframes accentPulse {
  0%, 100% { opacity: 0.38; transform: scaleX(0.97); }
  50%       { opacity: 0.65; transform: scaleX(1.00); }
}

/* ═══════════════════════════════════════════════════════════════════════════
   CUSTOM SCROLLBAR
   ═══════════════════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--ember), var(--gold));
  border-radius: var(--r-pill);
}

/* ═══════════════════════════════════════════════════════════════════════════
   TYPOGRAPHY
   ═══════════════════════════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5 {
  font-family: 'Cormorant Garamond', Georgia, serif !important;
  color: var(--ink-900) !important;
  font-weight: 600 !important;
  letter-spacing: -0.03em;
}
h1 { font-size: clamp(2rem, 4vw, 3rem) !important; }
h2 { font-size: clamp(1.5rem, 2.8vw, 2.1rem) !important; }
h3 { font-size: clamp(1.15rem, 2vw, 1.5rem) !important; }
p, li, span, label { color: var(--ink-600) !important; }
code { font-family: 'JetBrains Mono', monospace !important; font-size: 0.82em; }

/* ═══════════════════════════════════════════════════════════════════════════
   GEOMETRIC DECORATIVE PATTERNS (reusable via pseudo)
   ═══════════════════════════════════════════════════════════════════════════ */
.geo-ring {
  position: absolute; border-radius: 50%;
  border: 1px solid rgba(201,68,0,0.12);
  pointer-events: none;
}
.geo-square {
  position: absolute;
  border: 1px solid rgba(201,68,0,0.09);
  pointer-events: none;
  transform: rotate(45deg);
}

/* ═══════════════════════════════════════════════════════════════════════════
   GLASS CARD — BASE
   ═══════════════════════════════════════════════════════════════════════════ */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--glass) !important;
  border: 1px solid var(--glass-b) !important;
  border-radius: var(--r-xl) !important;
  box-shadow: var(--e2) !important;
  backdrop-filter: blur(28px) saturate(1.6) !important;
  -webkit-backdrop-filter: blur(28px) saturate(1.6) !important;
  transition:
    transform  var(--dur-base) var(--ease-back),
    box-shadow var(--dur-base) var(--ease-inout),
    border-color var(--dur-fast) var(--ease-inout) !important;
  padding: 24px 28px !important;
  position: relative !important;
  overflow: hidden !important;
}

/* Inner top shimmer line */
div[data-testid="stVerticalBlockBorderWrapper"]::before {
  content: "";
  position: absolute; top: 0; left: 10%; right: 10%; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(201,68,0,0.35), rgba(212,136,10,0.25), rgba(201,68,0,0.35), transparent);
  border-radius: var(--r-pill);
}

/* Inner bottom reflection */
div[data-testid="stVerticalBlockBorderWrapper"]::after {
  content: "";
  position: absolute; bottom: 0; left: 20%; right: 20%; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
  border-radius: var(--r-pill);
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: var(--glass-b2) !important;
  box-shadow: var(--e3) !important;
  transform: translateY(-3px) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TOPBAR
   ═══════════════════════════════════════════════════════════════════════════ */
.topbar {
  position: relative; overflow: hidden;
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  padding: 14px 24px;
  margin: 8px 0 20px 0;
  background: linear-gradient(135deg,
    rgba(255,255,255,0.88) 0%,
    rgba(255,252,248,0.85) 100%
  );
  border: 1px solid rgba(201,68,0,0.13);
  border-radius: var(--r-xl);
  box-shadow: var(--e2);
  backdrop-filter: blur(30px) saturate(1.8);
}

/* Diagonal accent stripe */
.topbar::before {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg,
    transparent 0%,
    var(--ember) 20%,
    var(--gold) 50%,
    var(--ember) 80%,
    transparent 100%
  );
  opacity: 0.6;
}

/* Corner gem */
.topbar::after {
  content: "";
  position: absolute; top: -40px; right: -40px;
  width: 120px; height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(201,68,0,0.07) 0%, transparent 70%);
  pointer-events: none;
}

.top-left   { display: flex; align-items: center; gap: 14px; }
.top-right  { display: flex; align-items: center; gap: 10px; }

.top-logo {
  width: 46px; height: 46px;
  border-radius: var(--r-md);
  background: linear-gradient(135deg, var(--ember) 0%, var(--ember-mid) 50%, var(--gold) 100%);
  box-shadow: var(--glow);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; flex-shrink: 0;
  position: relative; overflow: hidden;
  transition: transform var(--dur-fast) var(--ease-back);
}
.top-logo:hover { transform: scale(1.08) rotate(-3deg); }
.top-logo::after {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 55%;
  background: linear-gradient(180deg, rgba(255,255,255,0.25), transparent);
  border-radius: inherit;
}

.top-wordmark {
  display: flex; flex-direction: column; gap: 1px;
}
.top-title {
  font-family: 'Cormorant Garamond', serif !important;
  font-weight: 600; font-size: 1.1rem;
  color: var(--ink-900) !important;
  letter-spacing: -0.02em; line-height: 1.2;
}
.top-sub {
  font-size: 0.72rem; font-weight: 500;
  color: var(--ink-200) !important;
  letter-spacing: 0.02em;
}

.top-divider {
  width: 1px; height: 28px;
  background: linear-gradient(180deg, transparent, rgba(201,68,0,0.20), transparent);
}

.top-page {
  display: flex; align-items: center; gap: 7px;
  font-size: 0.80rem; font-weight: 600; color: var(--ink-400) !important;
  background: rgba(201,68,0,0.05);
  border: 1px solid rgba(201,68,0,0.12);
  border-radius: var(--r-pill);
  padding: 5px 14px;
}

.top-tag {
  display: flex; align-items: center; gap: 5px;
  font-size: 0.68rem; font-weight: 700;
  color: var(--ink-200) !important;
  background: rgba(255,255,255,0.7);
  border: 1px solid rgba(201,68,0,0.10);
  border-radius: var(--r-pill);
  padding: 4px 11px;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.05em;
}

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION HEADER
   ═══════════════════════════════════════════════════════════════════════════ */
.bps-section { margin: 2px 0 24px 0; }

.sec-eyebrow {
  display: inline-flex; align-items: center; gap: 10px;
  margin-bottom: 10px;
}
.sec-pill {
  font-family: 'Outfit', sans-serif;
  font-size: 0.62rem; font-weight: 700;
  letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--ember);
  background: rgba(201,68,0,0.08);
  border: 1px solid rgba(201,68,0,0.20);
  border-radius: var(--r-pill);
  padding: 3px 12px;
}
.sec-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--ember);
  box-shadow: 0 0 0 3px rgba(201,68,0,0.16), 0 0 0 6px rgba(201,68,0,0.06);
  animation: secDotPulse 2.6s ease-in-out infinite;
}
@keyframes secDotPulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(201,68,0,0.16), 0 0 0 6px rgba(201,68,0,0.06); }
  50%       { box-shadow: 0 0 0 5px rgba(201,68,0,0.10), 0 0 0 9px rgba(201,68,0,0.03); }
}

.sec-title {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 2.4rem !important; font-weight: 600 !important;
  line-height: 1.1 !important; letter-spacing: -0.04em !important;
  margin: 0 !important;
  background: linear-gradient(138deg,
    var(--ink-900) 0%,
    var(--ink-600) 45%,
    var(--ember)   100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sec-sub {
  color: var(--ink-200) !important;
  font-size: 0.94rem; font-weight: 400;
  margin: 6px 0 0 0 !important; line-height: 1.6;
}

.sec-rule {
  margin-top: 16px;
  height: 1px;
  background: linear-gradient(90deg,
    var(--ember) 0%, var(--gold) 30%, rgba(201,68,0,0.15) 70%, transparent 100%
  );
  border-radius: var(--r-pill);
}

/* ═══════════════════════════════════════════════════════════════════════════
   HERO BANNER (FULL BLEED)
   ═══════════════════════════════════════════════════════════════════════════ */
.bps-hero {
  position: relative; overflow: hidden;
  border-radius: var(--r-xl);
  padding: 44px 52px;
  margin-bottom: 24px;
  background: linear-gradient(138deg,
    #C94400  0%,
    #D85818 18%,
    #E07030 40%,
    #D48020 65%,
    #C87000 82%,
    #B86000 100%
  );
  box-shadow: var(--e5);
  isolation: isolate;
}

/* Layered geometric decorations */
.bps-hero::before {
  content: "";
  position: absolute; top: -140px; right: -160px;
  width: 620px; height: 620px; border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.10) 0%, transparent 65%);
  pointer-events: none;
}
.bps-hero::after {
  content: "";
  position: absolute; bottom: -100px; left: -80px;
  width: 380px; height: 380px; border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 65%);
  pointer-events: none;
}

/* Mesh grid overlay */
.hero-mesh {
  position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 0%, transparent 100%);
}

/* Decorative geo shapes */
.hero-geo1 {
  position: absolute; top: 28px; right: 200px;
  width: 90px; height: 90px;
  border: 2px solid rgba(255,255,255,0.12);
  border-radius: 24px;
  transform: rotate(16deg);
  pointer-events: none;
  animation: geoSpin 18s linear infinite;
}
.hero-geo2 {
  position: absolute; bottom: 36px; right: 90px;
  width: 54px; height: 54px; border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.14);
  pointer-events: none;
  animation: geoFloat 6s ease-in-out infinite;
}
.hero-geo3 {
  position: absolute; top: 50%; right: 130px;
  width: 30px; height: 30px;
  border: 1.5px solid rgba(255,255,255,0.10);
  transform: translateY(-50%) rotate(45deg);
  pointer-events: none;
}

@keyframes geoSpin  { to { transform: rotate(376deg); } }
@keyframes geoFloat { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }

.bps-hero-badge {
  display: inline-flex; align-items: center; gap: 9px;
  font-family: 'Outfit', sans-serif;
  font-size: 0.62rem; font-weight: 700;
  letter-spacing: 0.22em; text-transform: uppercase;
  color: rgba(255,255,255,0.88);
  background: rgba(255,255,255,0.13);
  border: 1px solid rgba(255,255,255,0.24);
  border-radius: var(--r-pill);
  padding: 5px 16px;
  margin-bottom: 22px;
  position: relative; z-index: 1;
  backdrop-filter: blur(10px);
}
.bps-hero-badge::before {
  content: ""; width: 6px; height: 6px; border-radius: 50%;
  background: rgba(255,255,255,0.9);
  box-shadow: 0 0 8px rgba(255,255,255,0.6);
  animation: badgeBlink 2s ease-in-out infinite;
}
@keyframes badgeBlink { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }

.bps-hero h1 {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: clamp(2rem, 4vw, 2.9rem) !important;
  font-weight: 600 !important;
  color: #fff !important;
  margin: 0 0 14px 0 !important;
  position: relative; z-index: 1;
  line-height: 1.12 !important;
  letter-spacing: -0.04em !important;
  text-shadow: 0 2px 20px rgba(0,0,0,0.15);
}

.bps-hero p {
  color: rgba(255,255,255,0.82) !important;
  font-size: 1.02rem; line-height: 1.72;
  margin: 0; position: relative; z-index: 1;
  max-width: 600px;
}

.hero-chips {
  display: flex; gap: 10px; flex-wrap: wrap;
  margin-top: 26px; position: relative; z-index: 1;
}

.hero-chip {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 8px 18px; border-radius: var(--r-pill);
  background: rgba(255,255,255,0.14);
  border: 1px solid rgba(255,255,255,0.24);
  color: #fff !important; font-weight: 600; font-size: 0.85rem;
  backdrop-filter: blur(12px);
  transition: all var(--dur-base) var(--ease-back);
  cursor: default;
}
.hero-chip:hover {
  background: rgba(255,255,255,0.26);
  transform: translateY(-3px) scale(1.03);
  box-shadow: 0 10px 24px rgba(0,0,0,0.15);
}

/* ═══════════════════════════════════════════════════════════════════════════
   BANNER (inline/secondary)
   ═══════════════════════════════════════════════════════════════════════════ */
.bps-banner {
  position: relative; overflow: hidden;
  border-radius: var(--r-xl);
  padding: 26px 32px;
  margin: 0 0 20px 0;
  background: linear-gradient(145deg,
    rgba(255,255,255,0.96) 0%,
    rgba(255,250,244,0.95) 100%
  );
  border: 1px solid rgba(201,68,0,0.12);
  box-shadow: var(--e3);
  backdrop-filter: blur(28px);
}

.bps-banner::before {
  content: "";
  position: absolute; top: -70px; right: -80px;
  width: 320px; height: 320px; border-radius: 50%;
  background: radial-gradient(circle, rgba(201,68,0,0.08), transparent 65%);
  pointer-events: none;
}

/* Left accent strip */
.bps-banner::after {
  content: "";
  position: absolute; left: 0; top: 16px; bottom: 16px;
  width: 3px; border-radius: var(--r-pill);
  background: linear-gradient(180deg, var(--ember), var(--gold));
}

.bps-kicker {
  font-family: 'Outfit', sans-serif;
  font-size: 0.64rem; font-weight: 700;
  letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--ember);
  margin-bottom: 10px; position: relative; z-index: 1;
  display: flex; align-items: center; gap: 10px;
}
.bps-kicker::before {
  content: "";
  width: 28px; height: 2px;
  background: linear-gradient(90deg, var(--ember), var(--gold));
  border-radius: var(--r-pill); display: inline-block;
}

.bps-title {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 1.85rem !important; font-weight: 600;
  margin: 0 0 8px 0; color: var(--ink-900);
  letter-spacing: -0.03em; position: relative; z-index: 1;
}

.bps-subtitle {
  color: var(--ink-400) !important;
  font-size: 0.94rem; line-height: 1.68;
  margin: 0; position: relative; z-index: 1;
}

/* ═══════════════════════════════════════════════════════════════════════════
   METRICS
   ═══════════════════════════════════════════════════════════════════════════ */
div[data-testid="metric-container"] {
  background: var(--glass) !important;
  border: 1px solid var(--glass-b) !important;
  border-radius: var(--r-lg) !important;
  padding: 22px 24px !important;
  box-shadow: var(--e2) !important;
  backdrop-filter: blur(28px) !important;
  transition:
    transform var(--dur-base) var(--ease-back),
    box-shadow var(--dur-base) var(--ease-inout),
    border-color var(--dur-fast) !important;
  position: relative !important;
  overflow: hidden !important;
  isolation: isolate !important;
}

/* Gradient top bar */
div[data-testid="metric-container"]::before {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 2.5px;
  background: linear-gradient(90deg, var(--ember), var(--gold), var(--ember-lite));
  border-radius: var(--r-pill) var(--r-pill) 0 0;
}

/* Ambient orb */
div[data-testid="metric-container"]::after {
  content: "";
  position: absolute; top: -40px; right: -30px;
  width: 110px; height: 110px; border-radius: 50%;
  background: radial-gradient(circle, rgba(201,68,0,0.07) 0%, transparent 70%);
}

div[data-testid="metric-container"]:hover {
  transform: translateY(-4px) !important;
  box-shadow: var(--e3) !important;
  border-color: rgba(201,68,0,0.24) !important;
}

div[data-testid="metric-container"] label {
  font-family: 'Outfit', sans-serif !important;
  color: var(--ink-200) !important;
  font-weight: 600 !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: 'Cormorant Garamond', serif !important;
  font-weight: 600 !important;
  color: var(--ink-900) !important;
  font-size: 2.3rem !important;
  line-height: 1.05 !important;
  letter-spacing: -0.035em !important;
}

div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
  font-size: 0.75rem !important;
  font-weight: 600 !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TABS
   ═══════════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  gap: 3px;
  background: rgba(255,248,240,0.88);
  border: 1px solid rgba(201,68,0,0.12);
  border-radius: var(--r-lg);
  padding: 5px;
  backdrop-filter: blur(16px);
}

.stTabs [data-baseweb="tab"] {
  height: 40px; padding: 0 22px;
  border-radius: var(--r-md);
  background: transparent;
  color: var(--ink-400) !important;
  font-family: 'Outfit', sans-serif;
  font-weight: 600; font-size: 0.84rem;
  transition: all var(--dur-base) var(--ease-inout);
  letter-spacing: 0.01em;
}

.stTabs [data-baseweb="tab"]:hover {
  background: rgba(201,68,0,0.07);
  color: var(--ember) !important;
}

.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--ember) 0%, var(--ember-mid) 60%, var(--gold) 100%) !important;
  color: #fff !important; font-weight: 700 !important;
  box-shadow: 0 4px 18px rgba(201,68,0,0.42), 0 1px 4px rgba(201,68,0,0.24) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════════════════════════════ */
.stButton > button,
div[data-testid="stDownloadButton"] button {
  font-family: 'Outfit', sans-serif !important;
  font-weight: 700 !important; font-size: 0.88rem !important;
  border-radius: var(--r-md) !important;
  height: 48px !important; letter-spacing: 0.01em !important;
  transition: all var(--dur-base) var(--ease-back) !important;
  position: relative !important; overflow: hidden !important;
}

/* Primary CTA */
.stButton > button[kind="primary"],
div[data-testid="stDownloadButton"] button {
  background: linear-gradient(138deg, var(--ember) 0%, var(--ember-mid) 50%, var(--gold) 100%) !important;
  color: #fff !important; border: none !important;
  box-shadow:
    0 6px 26px rgba(201,68,0,0.40),
    0 2px 8px rgba(201,68,0,0.22),
    inset 0 1px 0 rgba(255,255,255,0.18) !important;
}

/* Shine sweep */
.stButton > button[kind="primary"]::before,
div[data-testid="stDownloadButton"] button::before {
  content: "";
  position: absolute; top: 0; left: -100%; width: 60%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.22), transparent);
  transform: skewX(-20deg);
  transition: left 0.6s ease;
}

.stButton > button[kind="primary"]:hover::before,
div[data-testid="stDownloadButton"] button:hover::before {
  left: 150%;
}

.stButton > button[kind="primary"]:hover,
div[data-testid="stDownloadButton"] button:hover {
  transform: translateY(-3px) !important;
  box-shadow:
    0 14px 40px rgba(201,68,0,0.48),
    0 4px 14px rgba(201,68,0,0.28),
    inset 0 1px 0 rgba(255,255,255,0.18) !important;
}

.stButton > button[kind="secondary"] {
  background: rgba(255,255,255,0.75) !important;
  color: var(--ember) !important;
  border: 1.5px solid rgba(201,68,0,0.22) !important;
  box-shadow: var(--e1) !important;
  backdrop-filter: blur(12px) !important;
}
.stButton > button[kind="secondary"]:hover {
  background: rgba(201,68,0,0.06) !important;
  border-color: var(--ember) !important;
  transform: translateY(-2px) !important;
  box-shadow: var(--e2) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   INPUTS & SELECTS
   ═══════════════════════════════════════════════════════════════════════════ */
div[data-baseweb="input"] {
  background: rgba(255,255,255,0.80) !important;
  border-radius: var(--r-md) !important;
  border: 1.5px solid rgba(201,68,0,0.14) !important;
  backdrop-filter: blur(12px) !important;
  transition: all var(--dur-fast) var(--ease-inout) !important;
}
div[data-baseweb="input"]:focus-within {
  border-color: var(--ember) !important;
  box-shadow: 0 0 0 3px rgba(201,68,0,0.12), var(--e1) !important;
  background: rgba(255,255,255,0.95) !important;
}

div[data-baseweb="select"] > div {
  background: rgba(255,255,255,0.80) !important;
  border: 1.5px solid rgba(201,68,0,0.14) !important;
  border-radius: var(--r-md) !important;
  backdrop-filter: blur(12px) !important;
}
div[data-baseweb="select"]:focus-within > div {
  border-color: var(--ember) !important;
  box-shadow: 0 0 0 3px rgba(201,68,0,0.12) !important;
}

input, textarea {
  color: var(--ink-900) !important;
  font-family: 'Outfit', sans-serif !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   SLIDER
   ═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
  background: linear-gradient(135deg, var(--ember), var(--gold)) !important;
  box-shadow: var(--glow) !important;
  border: 2px solid rgba(255,255,255,0.8) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stProgress"] > div > div > div {
  background: linear-gradient(90deg, var(--ember), var(--gold), var(--ember-lite)) !important;
  border-radius: var(--r-pill) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   SIDEBAR — LUXURY EDITION
   ═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background:
    radial-gradient(ellipse 700px 600px at 0% -10%,  rgba(201,68,0,0.09) 0%, transparent 55%),
    radial-gradient(ellipse 500px 400px at 100% 110%, rgba(212,136,10,0.07) 0%, transparent 50%),
    linear-gradient(175deg,
      #FFFFFF   0%,
      #FFFAF5  30%,
      #FFF5EE  65%,
      #FFF0E5 100%
    ) !important;
  border-right: 1px solid rgba(201,68,0,0.10) !important;
  box-shadow: 5px 0 50px rgba(201,68,0,0.07), 1px 0 8px rgba(0,0,0,0.03) !important;
}

[data-testid="stSidebar"] * { color: var(--ink-900) !important; }
[data-testid="stSidebar"] .stMarkdown p {
  color: var(--ink-200) !important; font-size: 0.82rem !important; line-height: 1.6;
}
[data-testid="stSidebar"] hr {
  border: none !important;
  border-top: 1px solid rgba(201,68,0,0.08) !important;
  margin: 6px 0 !important;
}

/* Sidebar brand */
.sb-brand {
  display: flex; align-items: center; gap: 14px;
  padding: 2px 0 20px 0;
  position: relative;
}
.sb-brand::after {
  content: "";
  position: absolute; bottom: 0; left: -4px; right: -4px; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(201,68,0,0.18), transparent);
}

.sb-logo {
  width: 52px; height: 52px;
  border-radius: var(--r-md);
  background: linear-gradient(138deg, var(--ember) 0%, var(--ember-mid) 50%, var(--gold) 100%);
  box-shadow: var(--glow);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.55rem; flex-shrink: 0;
  position: relative; overflow: hidden;
  transition: transform var(--dur-fast) var(--ease-back);
}
.sb-logo:hover { transform: scale(1.06) rotate(-4deg); }
.sb-logo::after {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 50%;
  background: linear-gradient(180deg, rgba(255,255,255,0.25), transparent);
  border-radius: inherit;
}

.sb-name {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 1.08rem; font-weight: 600;
  color: var(--ink-900) !important; letter-spacing: -0.02em; line-height: 1.2;
}
.sb-sub {
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.64rem; font-weight: 700; letter-spacing: 0.10em;
  text-transform: uppercase; color: var(--ink-200) !important; margin-top: 2px;
}

/* Nav label */
.sb-nav-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.60rem; font-weight: 700;
  letter-spacing: 0.22em; text-transform: uppercase;
  color: rgba(201,68,0,0.45) !important;
  padding: 10px 2px 6px 2px;
}

/* Radio nav */
[data-testid="stSidebar"] div[role="radiogroup"] {
  gap: 5px !important; display: flex !important; flex-direction: column !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label {
  border-radius: var(--r-md) !important;
  border: 1px solid rgba(201,68,0,0.08) !important;
  background: rgba(255,255,255,0.78) !important;
  padding: 13px 16px !important;
  cursor: pointer !important;
  transition: all var(--dur-base) var(--ease-back) !important;
  box-shadow: var(--e1) !important;
  overflow: hidden !important;
  position: relative !important;
}

/* Left marker */
[data-testid="stSidebar"] div[role="radiogroup"] label::before {
  content: "";
  position: absolute; left: 0; top: 6px; bottom: 6px;
  width: 3px; border-radius: 0 var(--r-xs) var(--r-xs) 0;
  background: linear-gradient(180deg, var(--ember), var(--gold));
  opacity: 0;
  transition: opacity var(--dur-fast) var(--ease-inout);
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
  border-color: rgba(201,68,0,0.20) !important;
  background: rgba(255,255,255,0.96) !important;
  box-shadow: var(--e2) !important;
  transform: translateX(5px) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover::before { opacity: 1; }

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
  background: linear-gradient(138deg, var(--ember) 0%, var(--ember-mid) 55%, var(--gold) 100%) !important;
  border-color: transparent !important;
  box-shadow:
    0 6px 26px rgba(201,68,0,0.40),
    0 2px 8px rgba(201,68,0,0.22),
    inset 0 1px 0 rgba(255,255,255,0.18) !important;
  transform: translateX(5px) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span {
  color: #fff !important; font-weight: 700 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked)::before { display: none; }
[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] { display: none !important; }

/* Sidebar CTA button */
[data-testid="stSidebar"] .stButton > button {
  border-radius: var(--r-md) !important;
  background: rgba(201,68,0,0.06) !important;
  border: 1.5px solid rgba(201,68,0,0.16) !important;
  color: var(--ember) !important;
  font-weight: 700 !important; font-size: 0.83rem !important;
  height: 44px !important; box-shadow: none !important;
  transition: all var(--dur-base) var(--ease-inout) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(201,68,0,0.11) !important;
  border-color: var(--ember) !important;
  box-shadow: 0 4px 18px rgba(201,68,0,0.18) !important;
  transform: none !important;
}

/* Sidebar stat grid */
.sb-stat-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 4px 0;
}

.sb-stat {
  border-radius: var(--r-md); padding: 14px 14px;
  background: rgba(255,255,255,0.82);
  border: 1px solid rgba(201,68,0,0.08);
  box-shadow: var(--e1);
  transition: all var(--dur-base) var(--ease-inout);
  position: relative; overflow: hidden;
}
.sb-stat::before {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--ember), var(--gold));
  opacity: 0; transition: opacity var(--dur-fast);
}
.sb-stat:hover { border-color: rgba(201,68,0,0.18); box-shadow: var(--e2); transform: translateY(-2px); }
.sb-stat:hover::before { opacity: 0.7; }

.sb-stat-val {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.35rem; font-weight: 600;
  color: var(--ember) !important; line-height: 1.1;
}
.sb-stat-lbl {
  font-size: 0.65rem; font-weight: 700;
  color: var(--ink-200) !important; margin-top: 3px;
  letter-spacing: 0.04em; text-transform: uppercase;
}

/* Sidebar divider */
.sb-divider {
  display: flex; align-items: center; gap: 8px; margin: 14px 0 8px 0;
}
.sb-divider-line {
  flex: 1; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(201,68,0,0.16), transparent);
}

/* Sidebar footer */
.sb-footer {
  margin-top: 10px;
  border-radius: var(--r-lg); overflow: hidden;
  border: 1px solid rgba(201,68,0,0.11);
}
.sb-footer-top {
  padding: 14px 16px 12px;
  background: linear-gradient(135deg, rgba(201,68,0,0.07), rgba(212,136,10,0.04));
  display: flex; align-items: center; gap: 10px;
}
.sb-footer-icon {
  width: 34px; height: 34px; border-radius: var(--r-sm);
  background: linear-gradient(135deg, var(--ember), var(--gold));
  display: flex; align-items: center; justify-content: center;
  font-size: 1.05rem; flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(201,68,0,0.30);
}
.sb-footer-name {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 0.90rem; font-weight: 600; color: var(--ink-900) !important; line-height: 1.2;
}
.sb-footer-ver {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.62rem; color: var(--ink-200) !important; margin-top: 1px;
}
.sb-footer-bottom {
  padding: 7px 16px;
  background: rgba(201,68,0,0.04);
  border-top: 1px solid rgba(201,68,0,0.07);
  font-size: 0.64rem; font-weight: 700;
  color: var(--ink-100) !important;
  text-align: center; letter-spacing: 0.08em; text-transform: uppercase;
  font-family: 'JetBrains Mono', monospace;
}

/* ═══════════════════════════════════════════════════════════════════════════
   MODULE CARDS (Dashboard)
   ═══════════════════════════════════════════════════════════════════════════ */
.module-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(238px,1fr));
  gap: 18px; margin: 22px 0;
}

.module-card {
  border-radius: var(--r-xl);
  padding: 26px 24px 22px;
  background: var(--glass);
  border: 1px solid var(--glass-b);
  box-shadow: var(--e2);
  backdrop-filter: blur(28px);
  transition: all var(--dur-base) var(--ease-back);
  cursor: pointer; position: relative; overflow: hidden;
}

/* Top color accent */
.module-card::before {
  content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.module-card.shopee::before  { background: linear-gradient(90deg, #C94400, #E86820); }
.module-card.tokped::before  { background: linear-gradient(90deg, #00874A, #00C46A); }
.module-card.maps::before    { background: linear-gradient(90deg, #1A73E8, #34A853); }
.module-card.export::before  { background: linear-gradient(90deg, #6D28D9, #A78BFA); }

/* Ambient corner blob */
.module-card::after {
  content: "";
  position: absolute; bottom: -40px; right: -40px;
  width: 130px; height: 130px; border-radius: 50%;
  opacity: 0; transition: opacity var(--dur-base);
}
.module-card.shopee::after  { background: radial-gradient(circle, rgba(201,68,0,0.10), transparent 65%); }
.module-card.tokped::after  { background: radial-gradient(circle, rgba(0,135,74,0.08), transparent 65%); }
.module-card.maps::after    { background: radial-gradient(circle, rgba(26,115,232,0.08), transparent 65%); }
.module-card.export::after  { background: radial-gradient(circle, rgba(109,40,217,0.08), transparent 65%); }

.module-card:hover {
  box-shadow: var(--e4) !important;
  transform: translateY(-6px) !important;
  border-color: rgba(201,68,0,0.24) !important;
}
.module-card:hover::after { opacity: 1; }

.module-icon-wrap {
  width: 54px; height: 54px; border-radius: var(--r-md);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.7rem; margin-bottom: 16px;
  background: rgba(255,255,255,0.70);
  border: 1px solid rgba(201,68,0,0.09);
  box-shadow: var(--e1);
  transition: transform var(--dur-base) var(--ease-back);
}
.module-card:hover .module-icon-wrap { transform: scale(1.12) rotate(-5deg); }

.module-card-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.15rem; font-weight: 600;
  color: var(--ink-900); margin-bottom: 7px; letter-spacing: -0.01em;
}
.module-card-desc {
  font-size: 0.78rem; color: var(--ink-200); line-height: 1.6;
}
.module-card-badge {
  margin-top: 16px;
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 13px; border-radius: var(--r-pill);
  font-size: 0.71rem; font-weight: 700;
}
.module-card-badge.ready {
  background: rgba(22,163,74,0.10);
  border: 1px solid rgba(22,163,74,0.22);
  color: #15803D;
}
.module-card-badge.empty {
  background: rgba(201,68,0,0.07);
  border: 1px solid rgba(201,68,0,0.16);
  color: var(--ember);
}

/* ═══════════════════════════════════════════════════════════════════════════
   WORKFLOW STEPS
   ═══════════════════════════════════════════════════════════════════════════ */
.workflow-row {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  margin: 18px 0;
}
.workflow-step {
  display: flex; align-items: center; gap: 11px;
  padding: 14px 20px; border-radius: var(--r-lg);
  background: var(--glass);
  border: 1px solid var(--glass-b);
  box-shadow: var(--e1); backdrop-filter: blur(16px);
  flex: 1; min-width: 148px;
  transition: all var(--dur-base) var(--ease-back);
}
.workflow-step:hover { box-shadow: var(--e2); transform: translateY(-2px); border-color: rgba(201,68,0,0.20); }

.workflow-num {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(138deg, var(--ember), var(--gold));
  color: #fff; font-size: 0.78rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 14px rgba(201,68,0,0.34);
  font-family: 'JetBrains Mono', monospace;
}
.workflow-text { font-size: 0.82rem; font-weight: 700; color: var(--ink-800); }
.workflow-sub  { font-size: 0.70rem; color: var(--ink-200); margin-top: 1px; }
.workflow-arrow { color: var(--ink-100); font-size: 1.3rem; flex-shrink: 0; font-weight: 300; }

/* ═══════════════════════════════════════════════════════════════════════════
   UPLOAD INFO CARD
   ═══════════════════════════════════════════════════════════════════════════ */
.upload-info-card {
  border-radius: var(--r-lg); padding: 20px 22px; margin-bottom: 16px;
  background: linear-gradient(145deg, rgba(201,68,0,0.06), rgba(212,136,10,0.04));
  border: 1px solid rgba(201,68,0,0.13);
}
.upload-info-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.02rem; font-weight: 600;
  color: var(--ink-900); margin-bottom: 12px;
  display: flex; align-items: center; gap: 8px;
}
.upload-spec-row { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; }
.upload-spec {
  display: flex; align-items: flex-start; gap: 8px;
  font-size: 0.79rem; color: var(--ink-400); line-height: 1.5;
}
.upload-spec-dot {
  width: 5px; height: 5px; border-radius: 50%; background: var(--ember);
  margin-top: 6px; flex-shrink: 0;
  box-shadow: 0 0 0 3px rgba(201,68,0,0.14);
}
.upload-timestamp {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 5px 13px; border-radius: var(--r-pill);
  background: rgba(22,163,74,0.08);
  border: 1px solid rgba(22,163,74,0.20);
  font-size: 0.72rem; font-weight: 700; color: #15803D;
  margin-top: 10px;
}

/* ═══════════════════════════════════════════════════════════════════════════
   PREMIUM DATA TABLE
   ═══════════════════════════════════════════════════════════════════════════ */
.bps-table-wrap {
  width: 100%; overflow-x: auto;
  border-radius: var(--r-lg);
  border: 1px solid var(--glass-b);
  box-shadow: var(--e2);
  background: rgba(255,255,255,0.88);
  backdrop-filter: blur(20px);
  margin-bottom: 16px;
}
.bps-table {
  width: 100%; border-collapse: collapse;
  font-family: 'Outfit', sans-serif; font-size: 0.83rem;
}

/* Thead gradient */
.bps-table thead tr {
  background: linear-gradient(138deg, var(--ember) 0%, var(--ember-mid) 50%, var(--gold) 100%);
}
.bps-table thead th {
  padding: 14px 16px; text-align: left;
  font-weight: 700; font-size: 0.68rem;
  letter-spacing: 0.10em; text-transform: uppercase;
  color: rgba(255,255,255,0.95) !important; white-space: nowrap;
}
.bps-table thead th:first-child { border-radius: var(--r-md) 0 0 0; padding-left: 20px; }
.bps-table thead th:last-child  { border-radius: 0 var(--r-md) 0 0; }

.bps-table tbody tr {
  border-bottom: 1px solid rgba(201,68,0,0.055);
  transition: background var(--dur-snap);
}
.bps-table tbody tr:last-child { border-bottom: none; }
.bps-table tbody tr:hover { background: rgba(201,68,0,0.038) !important; }
.bps-table tbody tr:nth-child(even) { background: rgba(255,248,240,0.55); }
.bps-table tbody td { padding: 11px 16px; color: var(--ink-600) !important; vertical-align: middle; }
.bps-table tbody td:first-child { padding-left: 20px; }
.bps-table .td-toko { font-weight: 700; color: var(--ink-900) !important; }
.bps-table .td-harga {
  font-family: 'Cormorant Garamond', serif;
  font-size: 0.98rem; font-weight: 600; color: var(--ember) !important; white-space: nowrap;
}
.bps-table .td-link a {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 11px; border-radius: var(--r-pill);
  font-size: 0.72rem; font-weight: 700;
  background: rgba(201,68,0,0.07);
  border: 1px solid rgba(201,68,0,0.18);
  color: var(--ember) !important; text-decoration: none; white-space: nowrap;
  transition: all var(--dur-fast);
}
.bps-table .td-link a:hover { background: var(--ember); color: #fff !important; border-color: var(--ember); }

.tipe-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: var(--r-pill);
  font-size: 0.70rem; font-weight: 700; white-space: nowrap;
}
.tipe-online { background: rgba(22,163,74,0.10);  border: 1px solid rgba(22,163,74,0.22);  color: #15803D !important; }
.tipe-fisik  { background: rgba(37,99,235,0.10);   border: 1px solid rgba(37,99,235,0.22);   color: #1D4ED8 !important; }
.tipe-other  { background: rgba(201,68,0,0.08);    border: 1px solid rgba(201,68,0,0.18);    color: var(--ember) !important; }

.td-num { color: var(--ink-100) !important; font-size: 0.68rem; font-weight: 700; text-align: right; padding-right: 8px !important; width: 36px; font-family: 'JetBrains Mono', monospace; }
.td-truncate { max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.db-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 14px; flex-wrap: wrap; gap: 10px;
}
.db-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.10rem; font-weight: 600; color: var(--ink-900);
  display: flex; align-items: center; gap: 8px;
}
.db-count {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 14px; border-radius: var(--r-pill);
  background: rgba(201,68,0,0.07);
  border: 1px solid rgba(201,68,0,0.16);
  font-size: 0.74rem; font-weight: 700; color: var(--ember);
  font-family: 'JetBrains Mono', monospace;
}

/* ═══════════════════════════════════════════════════════════════════════════
   AUDIT CARDS
   ═══════════════════════════════════════════════════════════════════════════ */
.audit-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(205px,1fr));
  gap: 14px; margin: 6px 0;
}

.audit-card {
  border-radius: var(--r-lg); padding: 20px 20px;
  display: flex; align-items: flex-start; gap: 14px;
  background: var(--glass);
  border: 1px solid var(--glass-b);
  box-shadow: var(--e1); backdrop-filter: blur(20px);
  transition: all var(--dur-base) var(--ease-back);
  position: relative; overflow: hidden;
}
.audit-card::before {
  content: ""; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, rgba(201,68,0,0.18), transparent);
  opacity: 0; transition: opacity var(--dur-fast);
}
.audit-card:hover { box-shadow: var(--e3); transform: translateY(-3px); border-color: rgba(201,68,0,0.22); }
.audit-card:hover::before { opacity: 1; }

.audit-icon {
  width: 44px; height: 44px; border-radius: var(--r-md);
  display: flex; align-items: center; justify-content: center; font-size: 1.25rem; flex-shrink: 0;
  position: relative; overflow: hidden;
}
.audit-icon::after { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 50%; background: linear-gradient(180deg,rgba(255,255,255,0.25),transparent); border-radius: inherit; }

.audit-icon.blue   { background: linear-gradient(135deg,#3B82F6,#60A5FA); }
.audit-icon.green  { background: linear-gradient(135deg,#22C55E,#4ADE80); }
.audit-icon.orange { background: linear-gradient(135deg,var(--ember),var(--ember-lite)); }
.audit-icon.red    { background: linear-gradient(135deg,#EF4444,#F87171); }
.audit-icon.amber  { background: linear-gradient(135deg,var(--gold),var(--gold-lite)); }
.audit-icon.purple { background: linear-gradient(135deg,#8B5CF6,#A78BFA); }

.audit-val {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.80rem; font-weight: 600; line-height: 1.0; color: var(--ink-900);
}
.audit-lbl { font-size: 0.72rem; font-weight: 600; color: var(--ink-200); margin-top: 3px; line-height: 1.4; }

/* Quality bar */
.quality-bar-wrap { margin: 20px 0 6px 0; }
.quality-header {
  display: flex; justify-content: space-between;
  font-size: 0.79rem; font-weight: 700; color: var(--ink-400); margin-bottom: 9px;
}
.quality-pct { color: var(--ember) !important; font-weight: 700; }
.quality-track {
  height: 10px; border-radius: var(--r-pill);
  background: rgba(201,68,0,0.09); overflow: hidden;
  position: relative;
}
.quality-track::after {
  content: "";
  position: absolute; inset: 0;
  background: repeating-linear-gradient(90deg, rgba(255,255,255,0.08) 0px, rgba(255,255,255,0.08) 1px, transparent 1px, transparent 24px);
}
.quality-fill {
  height: 100%; border-radius: var(--r-pill);
  background: linear-gradient(90deg, #22C55E, #86EFAC);
  transition: width 1.2s var(--ease-out);
  position: relative; z-index: 1;
}
.quality-fill.mid { background: linear-gradient(90deg, #F59E0B, #FCD34D); }
.quality-fill.low { background: linear-gradient(90deg, #EF4444, #FCA5A5); }

/* ═══════════════════════════════════════════════════════════════════════════
   EXPORT PAGE
   ═══════════════════════════════════════════════════════════════════════════ */
.export-hero {
  border-radius: var(--r-xl); padding: 36px 40px; margin-bottom: 24px;
  background: linear-gradient(145deg,
    rgba(109,40,217,0.09) 0%,
    rgba(201,68,0,0.07) 45%,
    rgba(212,136,10,0.06) 100%
  );
  border: 1px solid rgba(109,40,217,0.14);
  box-shadow: var(--e2);
  display: flex; align-items: center; gap: 30px;
  position: relative; overflow: hidden;
}
.export-hero::before {
  content: "";
  position: absolute; top: -60px; right: -60px;
  width: 260px; height: 260px; border-radius: 50%;
  background: radial-gradient(circle, rgba(109,40,217,0.08), transparent 65%);
  pointer-events: none;
}
.export-hero-icon { font-size: 3.8rem; flex-shrink: 0; filter: drop-shadow(0 10px 20px rgba(109,40,217,0.28)); }
.export-hero-title { font-family: 'Cormorant Garamond', serif; font-size: 1.65rem; font-weight: 600; color: var(--ink-900); margin-bottom: 7px; letter-spacing: -0.025em; }
.export-hero-sub { font-size: 0.90rem; color: var(--ink-200); line-height: 1.7; }

.export-src-card {
  border-radius: var(--r-lg); padding: 18px 22px; margin-bottom: 10px;
  background: var(--glass); border: 1px solid var(--glass-b);
  box-shadow: var(--e1); backdrop-filter: blur(20px);
  display: flex; align-items: center; justify-content: space-between;
  transition: all var(--dur-base) var(--ease-inout);
}
.export-src-card:hover { box-shadow: var(--e2); transform: translateY(-1px); }
.export-src-card.ready { border-left: 4px solid #22C55E !important; }
.export-src-card.empty { border-left: 4px solid rgba(201,68,0,0.30) !important; opacity: 0.72; }
.export-src-left { display: flex; align-items: center; gap: 14px; }
.export-src-icon { font-size: 1.9rem; }
.export-src-name { font-family: 'Cormorant Garamond', serif; font-size: 1.02rem; font-weight: 600; color: var(--ink-900); }
.export-src-meta { font-size: 0.76rem; color: var(--ink-200); margin-top: 2px; }
.export-src-badge { padding: 4px 13px; border-radius: var(--r-pill); font-size: 0.72rem; font-weight: 700; }
.export-src-badge.ready { background: rgba(22,163,74,0.10); border: 1px solid rgba(22,163,74,0.22); color: #15803D; }
.export-src-badge.empty { background: rgba(201,68,0,0.07); border: 1px solid rgba(201,68,0,0.15); color: var(--ink-200); }

/* ═══════════════════════════════════════════════════════════════════════════
   ALERTS & TOASTS
   ═══════════════════════════════════════════════════════════════════════════ */
div[data-testid="stAlert"] {
  border-radius: var(--r-lg) !important;
  border-left-width: 3px !important;
  backdrop-filter: blur(14px) !important;
  box-shadow: var(--e1) !important;
}
[data-testid="stToast"] {
  border-radius: var(--r-lg) !important;
  border-left: 3px solid var(--ember) !important;
  backdrop-filter: blur(28px) saturate(1.6) !important;
  box-shadow: var(--e3) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   EXPANDERS
   ═══════════════════════════════════════════════════════════════════════════ */
details {
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(201,68,0,0.11);
  border-radius: var(--r-md);
  padding: 3px 14px;
  backdrop-filter: blur(14px);
  transition: box-shadow var(--dur-base);
}
details[open] { box-shadow: var(--e2); }
details summary {
  font-family: 'Outfit', sans-serif;
  font-weight: 700; color: var(--ink-900); cursor: pointer;
}

/* ═══════════════════════════════════════════════════════════════════════════
   LINKS
   ═══════════════════════════════════════════════════════════════════════════ */
a { color: var(--ember) !important; text-decoration: none; transition: color var(--dur-snap); }
a:hover { color: var(--ember-mid) !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   FOOTER
   ═══════════════════════════════════════════════════════════════════════════ */
.bps-footer {
  margin-top: 52px; padding: 20px 0;
  border-top: 1px solid rgba(201,68,0,0.09);
  display: flex; align-items: center; gap: 14px;
  color: rgba(92,32,0,0.38) !important;
  font-size: 0.78rem; font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.02em;
}
.footer-dot { width: 3px; height: 3px; border-radius: 50%; background: rgba(201,68,0,0.26); flex-shrink: 0; }

/* ═══════════════════════════════════════════════════════════════════════════
   SPLASH SCREEN — v4 Premium
   ═══════════════════════════════════════════════════════════════════════════ */
/* (defined inline in Python function) */

/* ═══════════════════════════════════════════════════════════════════════════
   DATAFRAME
   ═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
  border-radius: var(--r-lg) !important;
  overflow: hidden !important;
  border: 1px solid var(--glass-b) !important;
  box-shadow: var(--e2) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TIPS CARD
   ═══════════════════════════════════════════════════════════════════════════ */
.tip-grid { display: flex; gap: 18px; flex-wrap: wrap; }
.tip-col { flex: 1; min-width: 210px; }
.tip-head { font-weight: 700; color: var(--ink-900); margin-bottom: 7px; font-size: 0.87rem; display: flex; align-items: center; gap: 6px; }
.tip-body { font-size: 0.78rem; color: var(--ink-200); line-height: 1.75; }
.tip-body b { color: var(--ink-600) !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   FILTER BAR
   ═══════════════════════════════════════════════════════════════════════════ */
.filter-head { font-family: 'Cormorant Garamond', serif; font-size: 1.05rem; font-weight: 600; color: var(--ink-900); margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }

/* ═══════════════════════════════════════════════════════════════════════════
   STATUS BADGE (inline)
   ═══════════════════════════════════════════════════════════════════════════ */
.status-ok  { display:inline-flex;align-items:center;gap:5px;padding:3px 11px;border-radius:var(--r-pill);background:rgba(22,163,74,.10);border:1px solid rgba(22,163,74,.22);font-size:.70rem;font-weight:700;color:#15803D; }
.status-warn{ display:inline-flex;align-items:center;gap:5px;padding:3px 11px;border-radius:var(--r-pill);background:rgba(201,68,0,.08);border:1px solid rgba(201,68,0,.18);font-size:.70rem;font-weight:700;color:var(--ember); }

/* ═══════════════════════════════════════════════════════════════════════════
   EMPTY STATE
   ═══════════════════════════════════════════════════════════════════════════ */
.empty-state {
  padding: 48px 32px; text-align: center;
  border-radius: var(--r-xl);
  background: var(--glass);
  border: 1px dashed rgba(201,68,0,0.22);
  backdrop-filter: blur(20px);
}
.empty-icon { font-size: 3rem; margin-bottom: 14px; opacity: 0.7; }
.empty-title { font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; font-weight: 600; color: var(--ink-900); margin-bottom: 8px; }
.empty-sub { font-size: 0.86rem; color: var(--ink-200); line-height: 1.65; }
"""

st.markdown(f"<style>{MASTER_CSS}</style>", unsafe_allow_html=True)

# ======================================================================================
# UI HELPERS — Ultra-Premium v4
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
            return f'<td style="color:var(--ink-100);font-size:.74rem;font-family:\'JetBrains Mono\',monospace">{v}</td>'
        else:
            trunc = v[:40] + ("…" if len(v) > 40 else "")
            return f'<td class="td-truncate" title="{v}">{trunc}</td>'

    rows_html = ""
    for i, (_, row) in enumerate(df_show.iterrows()):
        cells      = "".join(_cell(c, row[c]) for c in cols)
        rows_html += f"<tr><td class='td-num'>{i+1:03d}</td>{cells}</tr>"

    total = len(df); shown = len(df_show)
    note  = f" <span style='color:var(--ink-100);font-size:.73rem'>(menampilkan {shown:,} dari {total:,})</span>" if total > max_rows else ""
    html  = f"""
<div class="db-header">
  <span class="db-title">📋 Data {source}{note}</span>
  <span class="db-count">{total:,} rows</span>
</div>
<div class="bps-table-wrap" style="max-height:500px;overflow-y:auto;">
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
        ("blue",   "📂", str(fc),                         "File Diproses"),
        ("orange", "📥", f"{tot:,}".replace(",","."),     "Total Baris Masuk"),
        ("green",  "✅", f"{val:,}".replace(",","."),     "Baris Valid (Babel)"),
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
        st.markdown(f"""<div style="margin-top:14px;padding:13px 18px;border-radius:var(--r-md);background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.22);">
  <span style="font-size:.80rem;font-weight:700;color:#B45309;">⚠️ Kolom tidak ditemukan: <code>{", ".join(miss)}</code></span></div>""", unsafe_allow_html=True)

# ======================================================================================
# SPLASH SCREEN — v4
# ======================================================================================
def splash_screen():
    logo_html = ""
    if os.path.exists("logo.png"):
        import base64
        with open("logo.png","rb") as _f:
            _b64 = base64.b64encode(_f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{_b64}" style="width:60px;height:60px;object-fit:contain;filter:brightness(0) invert(1);position:relative;z-index:1;" alt="Logo BPS">'
    else:
        logo_html = '<span style="font-size:2.6rem;position:relative;z-index:1;line-height:1;">🏛️</span>'

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
      radial-gradient(ellipse 80% 70% at 15% 15%, rgba(201,68,0,0.12) 0%, transparent 55%),
      radial-gradient(ellipse 60% 50% at 85% 85%, rgba(212,136,10,0.09) 0%, transparent 50%),
      linear-gradient(155deg, #FFFFFF 0%, #FFFCF8 35%, #FFF7EE 65%, #FFF2E4 100%);
    font-family:'Outfit','Segoe UI',system-ui,sans-serif;
  }}

  /* ambient geometry */
  #sp::before{{
    content:"";position:absolute;top:8%;right:10%;
    width:min(380px,40vw);height:min(380px,40vw);
    border-radius:50%;
    border:1px solid rgba(201,68,0,0.08);
    pointer-events:none;
    animation:spRingPulse 5s ease-in-out infinite;
  }}
  #sp::after{{
    content:"";position:absolute;bottom:12%;left:8%;
    width:min(220px,24vw);height:min(220px,24vw);
    border-radius:50%;
    border:1px solid rgba(212,136,10,0.07);
    pointer-events:none;
    animation:spRingPulse 7s ease-in-out infinite reverse;
  }}
  @keyframes spRingPulse{{0%,100%{{transform:scale(1);opacity:0.6}}50%{{transform:scale(1.04);opacity:1}}}}

  .sp-card{{
    position:relative;z-index:1;
    width:min(500px,92vw);
    padding:52px 46px 44px;
    background:rgba(255,255,255,0.86);
    border:1px solid rgba(201,68,0,0.13);
    border-radius:36px;
    box-shadow:
      0 40px 100px rgba(201,68,0,0.16),
      0 10px 30px rgba(0,0,0,0.07),
      inset 0 1px 0 rgba(255,255,255,0.95);
    backdrop-filter:blur(32px) saturate(1.5);
    text-align:center;
    animation:spCardIn .75s cubic-bezier(0.34,1.56,0.64,1) both;
    overflow:hidden;
  }}

  /* top shimmer */
  .sp-card::before{{
    content:"";position:absolute;top:0;left:10%;right:10%;height:2px;
    background:linear-gradient(90deg,transparent,#C94400 30%,#D4880A 60%,transparent);
    border-radius:9999px;
  }}

  @keyframes spCardIn{{
    from{{opacity:0;transform:translateY(36px) scale(0.93)}}
    to{{opacity:1;transform:translateY(0) scale(1)}}
  }}

  .sp-logo{{
    width:100px;height:100px;border-radius:26px;
    background:linear-gradient(138deg,#C94400 0%,#D85818 40%,#D4880A 80%,#C87000 100%);
    box-shadow:0 18px 52px rgba(201,68,0,0.42),0 5px 16px rgba(201,68,0,0.24),inset 0 1px 0 rgba(255,255,255,0.22);
    display:flex;align-items:center;justify-content:center;
    margin:0 auto 26px auto;
    position:relative;overflow:hidden;
    animation:spLogoIn .6s .15s cubic-bezier(0.34,1.56,0.64,1) both;
  }}
  .sp-logo::after{{content:"";position:absolute;top:0;left:0;right:0;height:52%;background:linear-gradient(180deg,rgba(255,255,255,0.24),transparent);border-radius:inherit;}}
  @keyframes spLogoIn{{from{{opacity:0;transform:scale(0.65) rotate(-10deg)}}to{{opacity:1;transform:scale(1) rotate(0)}}}}

  .sp-eyebrow{{
    font-size:.62rem;font-weight:700;letter-spacing:.24em;text-transform:uppercase;
    color:rgba(201,68,0,0.65);margin-bottom:11px;
    animation:spFadeUp .5s .28s ease both;
  }}

  .sp-title{{
    font-family:'Georgia',serif;
    font-size:clamp(1.6rem,4.5vw,2.1rem);font-weight:400;
    color:#1C0400;letter-spacing:-.03em;line-height:1.15;
    margin:0 0 10px 0;
    animation:spFadeUp .5s .34s ease both;
  }}

  .sp-subtitle{{
    font-size:.87rem;color:rgba(92,32,0,0.55);
    line-height:1.65;margin:0 0 28px 0;
    animation:spFadeUp .5s .40s ease both;
  }}

  .sp-pills{{
    display:flex;flex-wrap:wrap;justify-content:center;gap:8px;
    margin-bottom:28px;animation:spFadeUp .5s .42s ease both;
  }}
  .sp-pill{{
    padding:5px 14px;border-radius:9999px;
    font-size:.74rem;font-weight:600;
    color:#C94400;background:rgba(201,68,0,0.08);border:1px solid rgba(201,68,0,0.18);
  }}

  .sp-progress-wrap{{animation:spFadeUp .5s .46s ease both;}}
  .sp-ph{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:9px;}}
  .sp-status{{font-size:.76rem;font-weight:500;color:rgba(92,32,0,0.50);}}
  .sp-pct{{font-size:.80rem;font-weight:700;color:#C94400;font-variant-numeric:tabular-nums;font-family:'JetBrains Mono',monospace;}}
  .sp-track{{
    width:100%;height:7px;border-radius:9999px;
    background:rgba(201,68,0,0.10);overflow:hidden;position:relative;
  }}
  .sp-track::after{{
    content:"";position:absolute;inset:0;
    background:repeating-linear-gradient(90deg,rgba(255,255,255,0.12) 0px,rgba(255,255,255,0.12) 1px,transparent 1px,transparent 20px);
  }}
  .sp-fill{{
    height:100%;border-radius:9999px;position:relative;z-index:1;
    background:linear-gradient(90deg,#C94400,#D85818,#D4880A,#E09030);
    background-size:200% 100%;width:0%;
    transition:width .18s ease;
    animation:spShimmer 2.2s linear infinite;
  }}
  @keyframes spShimmer{{0%{{background-position:0% 50%}}100%{{background-position:200% 50%}}}}

  .sp-dots{{display:flex;gap:6px;justify-content:center;margin-top:14px;}}
  .sp-dot{{width:7px;height:7px;border-radius:50%;background:rgba(201,68,0,0.22);animation:spDotB 1.5s ease-in-out infinite;}}
  .sp-dot:nth-child(2){{animation-delay:.22s}}
  .sp-dot:nth-child(3){{animation-delay:.44s}}
  @keyframes spDotB{{0%,80%,100%{{transform:scale(.75);opacity:.25}}42%{{transform:scale(1.25);opacity:1;background:#C94400}}}}

  @keyframes spFadeUp{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}
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
            link_html = f'<a href="{link}" target="_blank" style="color:#E8500A;font-weight:700;">Buka Link →</a>' if link else "-"
            popup = f"""<div style="width:270px;font-family:'DM Sans',sans-serif;">
              <div style="font-weight:700;font-size:14px;color:#17060A;margin-bottom:6px;">{nama}</div>
              <div style="font-size:12px;color:#7A3A18;">{alamat}</div>
              <hr style="border:none;border-top:1px solid rgba(232,80,10,.15);margin:8px 0;">
              <div style="font-size:12px;color:#3D1800;">☎️ {telp if telp else "-"}</div>
              <div style="font-size:12px;margin-top:4px;">{link_html}</div>
            </div>"""
            folium.CircleMarker(
                location=[float(r["Latitude"]), float(r["Longitude"])],
                radius=7, weight=2,
                color="#E8500A", fill=True,
                fill_color="#F07030", fill_opacity=.88,
                popup=folium.Popup(popup, max_width=320),
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
# SPLASH SCREEN
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
    <div class="sb-name">ALIPING UMKM</div>
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

        # ── sidebar stats — use _shp_n / _tkp_n / _mp_n (defined here, NOT _shp_n2 etc.)
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

        # ── FIXED: use _shp_n / _tkp_n / _mp_n (already defined above) — NOT undefined _shp_n2 etc.
        st.markdown(
            '<div class="sb-footer">'
            '<div class="sb-footer-top">'
            '<div class="sb-footer-icon">🏛️</div>'
            '<div>'
            '<div class="sb-footer-name">BPS Bangka Belitung</div>'
            '<div class="sb-footer-ver">ALPING UMKM v4.0</div>'
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
  <div class="hero-orb-1"></div>
  <div class="hero-orb-2"></div>
  <div class="hero-orb-3"></div>
  <div class="bps-hero-badge">UMKM · BPS BABEL · v4.0</div>
  <h1>Kontrol Pusat Analisis UMKM</h1>
  <p>Upload data marketplace atau Google Maps, analisis dengan filter pintar, visualisasikan di peta interaktif, lalu ekspor ke Excel — semua dalam satu platform.</p>
  <div class="hero-chips">
    <span class="hero-chip">🟠 Shopee</span>
    <span class="hero-chip">🟢 Tokopedia</span>
    <span class="hero-chip">📍 Google Maps</span>
    <span class="hero-chip">📊 Export Master</span>
    <span class="hero-chip" style="background:rgba(255,255,255,.22);font-family:'JetBrains Mono',monospace">📦 {fmt_int_id(total_all)} data</span>
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
  <div style="font-family:'DM Serif Display',serif;font-size:1.05rem;font-weight:400;color:var(--ink9);margin-bottom:12px;">🗺️ Alur Kerja yang Disarankan</div>
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
<div style="display:flex;gap:16px;flex-wrap:wrap;">
  <div style="flex:1;min-width:220px;">
    <div style="font-weight:700;color:var(--ink9);margin-bottom:6px;font-size:.86rem;">💡 Tips Performa</div>
    <div style="font-size:.78rem;color:var(--ink3);line-height:1.7;">• Aktifkan <b>Mode Cepat</b> di Settings untuk file besar<br>• Naikkan <b>jeda request</b> API Shopee kalau kena rate limit<br>• Upload beberapa CSV sekaligus untuk batch processing</div>
  </div>
  <div style="flex:1;min-width:220px;">
    <div style="font-weight:700;color:var(--ink9);margin-bottom:6px;font-size:.86rem;">✅ Kualitas Data</div>
    <div style="font-size:.78rem;color:var(--ink3);line-height:1.7;">• Pastikan kolom <b>wilayah/lokasi</b> terisi benar<br>• Google Maps butuh <b>lat/lon valid</b> untuk tampil di peta<br>• Link & telepon kosong dibersihkan otomatis</div>
  </div>
  <div style="flex:1;min-width:220px;">
    <div style="font-weight:700;color:var(--ink9);margin-bottom:6px;font-size:.86rem;">📊 Analisis Terbaik</div>
    <div style="font-size:.78rem;color:var(--ink3);line-height:1.7;">• Cek tab <b>Audit</b> setelah upload untuk validasi data<br>• Gunakan <b>Top 10 Toko</b> di Executive Dashboard<br>• Export Gabungan untuk laporan lintas platform</div>
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
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(family="Instrument Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah").sort_values("Jumlah", ascending=True)
                    fig = px.bar(grp, y="Wilayah", x="Jumlah", orientation="h", title="Produk per Wilayah", color="Jumlah", color_continuous_scale=["#F8C060","#E8500A"])
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, font=dict(family="Instrument Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)
                g3, g4 = st.columns(2, gap="large")
                with g3:
                    df_hrg = df_f[df_f["Harga"] > 0]
                    if not df_hrg.empty:
                        fig = px.histogram(df_hrg, x="Harga", nbins=30, title="Distribusi Harga Produk", color_discrete_sequence=["#E8500A"])
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Instrument Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                        fig.update_xaxes(tickprefix="Rp ")
                        st.plotly_chart(fig, use_container_width=True)
                with g4:
                    top_toko = df_f[df_f["Nama Toko"].notna() & ~df_f["Nama Toko"].isin(["Tidak Dilacak","Anonim",""])]["Nama Toko"].value_counts().head(10).reset_index()
                    top_toko.columns = ["Toko","Produk"]
                    if not top_toko.empty:
                        fig = px.bar(top_toko.sort_values("Produk"), y="Toko", x="Produk", orientation="h", title="Top 10 Toko Paling Aktif", color="Produk", color_continuous_scale=["#F8C060","#E8500A"])
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, font=dict(family="Instrument Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
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
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(family="Instrument Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah").sort_values("Jumlah", ascending=True)
                    fig = px.bar(grp, y="Wilayah", x="Jumlah", orientation="h", title="Produk per Wilayah", color="Jumlah", color_continuous_scale=["#F8C060","#E8500A"])
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, font=dict(family="Instrument Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)
                g3, g4 = st.columns(2, gap="large")
                with g3:
                    df_hrg = df_f[df_f["Harga"] > 0]
                    if not df_hrg.empty:
                        fig = px.histogram(df_hrg, x="Harga", nbins=30, title="Distribusi Harga Produk", color_discrete_sequence=["#E8500A"])
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Instrument Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
                        fig.update_xaxes(tickprefix="Rp ")
                        st.plotly_chart(fig, use_container_width=True)
                with g4:
                    top_toko = df_f[df_f["Nama Toko"].notna() & ~df_f["Nama Toko"].isin(["Tidak Dilacak","Anonim",""])]["Nama Toko"].value_counts().head(10).reset_index()
                    top_toko.columns = ["Toko","Produk"]
                    if not top_toko.empty:
                        fig = px.bar(top_toko.sort_values("Produk"), y="Toko", x="Produk", orientation="h", title="Top 10 Toko Paling Aktif", color="Produk", color_continuous_scale=["#F8C060","#E8500A"])
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, font=dict(family="Instrument Sans, sans-serif", color="#3A1A08"), margin=dict(t=44,b=12,l=0,r=0))
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
<div style="padding:32px;text-align:center;border-radius:var(--r4);background:var(--glass);border:1px dashed rgba(232,80,10,.25);backdrop-filter:blur(12px);">
  <div style="font-size:2.5rem;margin-bottom:12px;">📭</div>
  <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;font-weight:400;color:var(--ink9);margin-bottom:8px;">Belum Ada Data</div>
  <div style="font-size:.86rem;color:var(--ink3);">Proses dulu data di modul Shopee, Tokopedia, atau Google Maps.<br>Setelah itu kembali ke halaman ini untuk export.</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("#### 📋 Status Sumber Data")
        def _export_src(icon, name, n, ts_key, ready):
            ts       = st.session_state.get(ts_key, "")
            ts_str   = f"· Diupload {ts}" if ts else ""
            badge_cls = "ready" if ready else "empty"
            badge_txt = f"✅ {fmt_int_id(n)} baris" if ready else "⏳ Belum ada data"
            card_cls  = "ready" if ready else "empty"
            return f"""<div class="export-src-card {card_cls}" style="margin-bottom:10px;">
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
    <span style="font-size:1.1rem">📄</span>
    <div><div style="font-weight:700;font-size:.86rem;color:var(--ink9);">Format: Excel (.xlsx)</div>
    <div style="font-size:.76rem;color:var(--ink3);">{sum([df_shp_ready,df_tkp_ready,df_maps_ready])} sheet · Autofilter · Header oranye · Format kolom otomatis</div></div>
  </div>
  <div style="display:flex;gap:8px;align-items:center;">
    <span style="font-size:1.1rem">📦</span>
    <div><div style="font-weight:700;font-size:.86rem;color:var(--ink9);">{fmt_int_id(total_e)} total baris data</div>
    <div style="font-size:.76rem;color:var(--ink3);">File: Master_UMKM_BPS_{datetime.date.today()}.xlsx</div></div>
  </div>
</div>""", unsafe_allow_html=True)
            with col_btn:
                st.download_button(label="⬇️ Unduh Excel Master", data=excel_bytes, file_name=f"Master_UMKM_BPS_{datetime.date.today()}.xlsx", use_container_width=True, type="primary")

# ======================================================================================
# FOOTER
# ======================================================================================
st.markdown("""
<div class="bps-footer">
  <span style="font-size:1.1rem">🏛️</span>
  <span>Built with Streamlit</span>
  <span class="footer-dot"></span>
  <span>Badan Pusat Statistik · UMKM Toolkit</span>
  <span class="footer-dot"></span>
  <span>Bangka Belitung · v3.0</span>
</div>""", unsafe_allow_html=True)

