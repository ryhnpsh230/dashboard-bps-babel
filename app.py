import streamlit as st
import pandas as pd
import re
import io
import requests
import datetime
import os
import time
from urllib.parse import urlparse

def section_header(title: str, subtitle: str = "", badge: str = "MODULE"):
    """Premium section header (international look)."""
    st.markdown(
        f"""
<div class="bps-section">
  <div class="left">
    <div class="bps-badge">{badge}</div>
    <h2 class="bps-h">{title}</h2>
    {f'<p class="bps-sub">{subtitle}</p>' if subtitle else ''}
    <div class="bps-divider"></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def goto_menu(label: str):
    """Jump navigation safely (cannot mutate widget state after creation)."""
    st.session_state["nav_target"] = label
    st.session_state["show_sidebar"] = True
    st.rerun()


import plotly.express as px

import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium


# ======================================================================================
# CONFIG
# ======================================================================================
APP_TITLE = "Dashboard UMKM BPS"
APP_ICON = "🏛️"

BPS_OREN_UTAMA = "#FF6F00"
BPS_AMBER = "#FFC107"
BPS_DARK = "#0b0b0c"
BPS_PAPER = "rgba(0,0,0,0)"

BPS_PALETTE = ["#FF6F00", "#FFA000", "#FFB300", "#FFC107", "#263238", "#37474F", "#455A64"]

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

px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = BPS_PALETTE


# ======================================================================================
# THEME / CSS (Orange-heavy modern glass)
# ======================================================================================
# ======================================================================================
# THEME / CSS (Original + Polished Add-ons)
# ======================================================================================
CSS_THEME = r"""@import url("https://fonts.googleapis.com/css2?family=Manrope:wght@600;700;800&display=swap");
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap");



/* -------------------- Global background: PREMIUM SUNSET MODE -------------------- */
[data-testid="stAppViewContainer"] {
    background:
      radial-gradient(1600px 900px at 5% 15%, rgba(255,120,0,.55) 0%, rgba(255,120,0,.28) 35%, rgba(255,120,0,0) 70%),
      radial-gradient(1400px 900px at 95% 10%, rgba(255,170,0,.35) 0%, rgba(255,170,0,.18) 40%, rgba(255,170,0,0) 75%),
      radial-gradient(1200px 800px at 50% 100%, rgba(255,200,120,.18) 0%, rgba(255,200,120,0) 70%),
      linear-gradient(155deg, #1b0f08 0%, #2a1306 22%, #140c08 55%, #07090d 100%) !important;
    background-attachment: fixed !important;
}

[data-testid="stAppViewContainer"] {
    background:
      radial-gradient(1200px 720px at 12% 12%, rgba(255,111,0,.38) 0%, rgba(255,111,0,0) 60%),
      radial-gradient(900px 650px at 88% 16%, rgba(255,193,7,.28) 0%, rgba(255,193,7,0) 58%),
      radial-gradient(1000px 600px at 60% 95%, rgba(255,111,0,.16) 0%, rgba(255,111,0,0) 60%),
      linear-gradient(135deg, #070708 0%, #0c0c10 55%, #060607 100%) !important;
    background-attachment: fixed !important;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0) !important;
}

/* Top glow bar */
.block-container {
    padding-top: 1.1rem;
    padding-bottom: 2.1rem;
}
.block-container::before {
    content: "";
    display: block;
    height: 6px;
    width: 100%;
    border-radius: 999px;
    margin-bottom: 14px;
    background: linear-gradient(90deg,
        rgba(255,111,0,0) 0%,
        rgba(255,111,0,.95) 28%,
        rgba(255,193,7,.95) 56%,
        rgba(255,111,0,.95) 80%,
        rgba(255,111,0,0) 100%);
    box-shadow: 0 8px 36px rgba(255,111,0,.25);
}

/* -------------------- Sidebar: oren lebih dominan -------------------- */
[data-testid="stSidebar"] {
    background:
      radial-gradient(600px 420px at 20% 10%, rgba(255,111,0,.32) 0%, rgba(255,111,0,0) 62%),
      linear-gradient(180deg, rgba(14,14,16,.98) 0%, rgba(10,10,12,.98) 55%, rgba(8,8,9,.99) 100%) !important;
    border-right: 1px solid rgba(255,111,0,.45);
    box-shadow: 10px 0 40px rgba(0,0,0,.45);
}
[data-testid="stSidebar"] * {
    color: #f3f3f3 !important;
}

/* -------------------- Cards (containers) -------------------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,111,0,0.34) !important;
    border-radius: 18px;
    padding: 18px 18px;
    box-shadow:
      0 14px 38px rgba(0,0,0,.33),
      0 0 0 1px rgba(255,111,0,.07) inset;
    backdrop-filter: blur(12px);
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(255,193,7,.48) !important;
    box-shadow:
      0 18px 46px rgba(0,0,0,.36),
      0 0 0 1px rgba(255,193,7,.10) inset,
      0 22px 70px rgba(255,111,0,.10);
}

/* -------------------- Banner -------------------- */
.bps-banner {
    border-radius: 20px;
    padding: 24px 28px;
    margin: 2px 0 18px 0;
    background:
      radial-gradient(900px 360px at 15% 0%, rgba(255,111,0,.40) 0%, rgba(255,111,0,0) 62%),
      radial-gradient(900px 380px at 85% 10%, rgba(255,193,7,.26) 0%, rgba(255,193,7,0) 62%),
      linear-gradient(135deg, rgba(255,111,0,.30) 0%, rgba(255,193,7,.10) 40%, rgba(255,255,255,.04) 100%);
    border: 1px solid rgba(255,111,0,.34);
    box-shadow: 0 18px 55px rgba(0,0,0,.34);
    backdrop-filter: blur(14px);
}
.bps-kicker {
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 800;
    font-size: .78rem;
    color: rgba(255,193,7,.98);
    margin-bottom: 8px;
}
.bps-title {
    font-size: 2.10rem;
    font-weight: 950;
    margin: 0 0 8px 0;
    color: #ffffff;
}
.bps-subtitle {
    margin: 0;
    color: rgba(240,240,240,.90);
    font-size: 1.03rem;
}

/* -------------------- Metrics -------------------- */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,111,0,0.30);
    border-left: 7px solid __BPS_OREN__;
    border-radius: 16px;
    padding: 14px 16px;
    box-shadow:
      0 12px 34px rgba(0,0,0,.26),
      0 0 0 1px rgba(255,111,0,.06) inset;
    backdrop-filter: blur(12px);
    transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    border-color: rgba(255,193,7,.58);
    box-shadow:
      0 18px 46px rgba(0,0,0,.30),
      0 0 0 1px rgba(255,193,7,.10) inset,
      0 30px 90px rgba(255,111,0,.12);
}
div[data-testid="metric-container"] label {
    color: rgba(240,240,240,.86) !important;
    font-weight: 800;
    letter-spacing: .2px;
}

/* -------------------- Tabs -------------------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,111,0,.30);
    padding: 10px;
    border-radius: 16px;
    backdrop-filter: blur(12px);
}
.stTabs [data-baseweb="tab"] {
    height: 46px;
    border-radius: 14px;
    padding: 0 16px;
    background: rgba(255,255,255,0.03);
    color: rgba(245,245,245,.86);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(255,111,0,.95) 0%, rgba(255,193,7,.95) 100%) !important;
    color: #111 !important;
    font-weight: 950;
    box-shadow: 0 16px 44px rgba(255,111,0,.32);
}

/* -------------------- Buttons -------------------- */
div[data-testid="stDownloadButton"] button,
.stButton > button {
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    background: linear-gradient(135deg, rgba(255,111,0,.92) 0%, rgba(255,193,7,.88) 100%) !important;
    color: #111 !important;
    font-weight: 950 !important;
    height: 48px !important;
    box-shadow: 0 16px 44px rgba(255,111,0,.52);
    transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
}
div[data-testid="stDownloadButton"] button:hover,
.stButton > button:hover {
    transform: translateY(-1px);
    filter: brightness(1.04);
    box-shadow: 0 22px 60px rgba(255,111,0,.28);
}
button[kind="secondary"] {
    background: rgba(255,255,255,.08) !important;
    border: 1px solid rgba(255,111,0,.52) !important;
    color: #f2f2f2 !important;
}

/* -------------------- Dataframe -------------------- */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(255,111,0,.32);
}


/* ============================================================================
   Sidebar — international nav styling (keeps your original theme)
   ========================================================================== */
[data-testid="stSidebar"] .block-container{
  padding-top: 1.15rem !important;
}
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h1{
  letter-spacing: -0.02em;
}

/* Radio group -> pill nav */
[data-testid="stSidebar"] [role="radiogroup"]{
  gap: 10px;
}
[data-testid="stSidebar"] [role="radiogroup"] > label{
  width: 100%;
  padding: 10px 12px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,.10);
  background: rgba(255,255,255,.045);
  transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease, background .14s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:hover{
  transform: translateY(-1px);
  border-color: rgba(255,255,255,.18);
  background: rgba(255,255,255,.06);
  box-shadow: 0 14px 40px rgba(0,0,0,.28);
}
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked){
  background: linear-gradient(135deg, rgba(255,111,0,.92) 0%, rgba(255,193,7,.86) 100%);
  border-color: rgba(255,193,7,.32);
  box-shadow: 0 18px 56px rgba(255,111,0,.32);
}
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) p{
  color: #101113 !important;
  font-weight: 950 !important;
}
[data-testid="stSidebar"] [role="radiogroup"] p{
  margin: 0 !important;
  font-weight: 800;
  letter-spacing: .2px;
}

/* Make the radio dot subtle */
[data-testid="stSidebar"] [role="radiogroup"] input{
  accent-color: rgba(16,17,19,.0);
}
[data-testid="stSidebar"] [role="radiogroup"] svg{
  filter: drop-shadow(0 6px 14px rgba(0,0,0,.28));
}

/* Sidebar separators */
[data-testid="stSidebar"] hr{
  border-color: rgba(255,255,255,.10) !important;
}


/* -------------------- Typography -------------------- */
h1, h2, h3, h4, h5{
  font-family: "Manrope", "Inter", system-ui, sans-serif !important;
  letter-spacing: -0.025em;
}
h1{ font-weight: 900 !important; }
h2{ font-weight: 850 !important; }
p, li, label, .stMarkdown{
  color: var(--text) !important;
  line-height: 1.6;
}


/* -------------------- Buttons (premium) -------------------- */
.stButton > button, div[data-testid="stDownloadButton"] button{
  border-radius: 16px !important;
  height: 52px !important;
  font-weight: 900 !important;
  letter-spacing: .2px;
  background: linear-gradient(135deg, rgba(255,111,0,.98) 0%, rgba(255,179,0,.92) 55%, rgba(255,213,79,.88) 100%) !important;
  color: #111114 !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  box-shadow: 0 20px 70px rgba(255,111,0,0.26), 0 10px 26px rgba(0,0,0,0.35) !important;
  transition: transform .14s ease, box-shadow .14s ease, filter .14s ease;
}
.stButton > button:hover, div[data-testid="stDownloadButton"] button:hover{
  transform: translateY(-2px);
  filter: brightness(1.03);
  box-shadow: 0 26px 92px rgba(255,111,0,0.34), 0 14px 36px rgba(0,0,0,0.38) !important;
}
.stButton > button:active{
  transform: translateY(0px) scale(.99);
}
button[kind="secondary"]{
  background: rgba(255,255,255,0.08) !important;
  color: rgba(255,255,255,0.92) !important;
  border: 1px solid rgba(255,255,255,0.16) !important;
  box-shadow: 0 12px 32px rgba(0,0,0,0.34) !important;
}
button:focus-visible{
  outline: none !important;
  box-shadow: 0 0 0 4px rgba(255,111,0,0.26), 0 26px 92px rgba(255,111,0,0.22) !important;
}


/* -------------------- Chips / Pills -------------------- */
.bps-chip{
  display:inline-flex; align-items:center; gap:8px;
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.06);
  box-shadow: 0 14px 40px rgba(0,0,0,0.28);
  font-weight: 800;
}
.bps-chip:hover{
  border-color: rgba(255,179,0,0.38);
  box-shadow: 0 22px 64px rgba(255,111,0,0.18);
  transform: translateY(-1px);
}


/* -------------------- Sidebar nav (stronger active) -------------------- */
[data-testid="stSidebar"]{
  background:
    radial-gradient(680px 420px at 22% 8%, rgba(255,111,0,.26) 0%, rgba(255,111,0,0) 62%),
    radial-gradient(640px 420px at 78% 22%, rgba(255,179,0,.16) 0%, rgba(255,179,0,0) 60%),
    linear-gradient(180deg, rgba(13,15,20,.98) 0%, rgba(9,10,14,.99) 100%) !important;
  border-right: 1px solid rgba(255,255,255,0.10);
  box-shadow: 18px 0 60px rgba(0,0,0,.46);
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label{
  border-radius: 16px !important;
  padding: 10px 12px !important;
  margin: 8px 0 !important;
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover{
  border-color: rgba(255,179,0,0.30) !important;
  box-shadow: 0 18px 54px rgba(255,111,0,0.16);
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked){
  background: linear-gradient(135deg, rgba(255,111,0,.86) 0%, rgba(255,179,0,.76) 60%, rgba(255,213,79,.70) 100%) !important;
  border-color: rgba(255,255,255,0.16) !important;
  box-shadow: 0 22px 74px rgba(255,111,0,0.26);
}


/* ==================== Premium Motion & Smoothing ==================== */
*{ -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
@media (prefers-reduced-motion: no-preference){
  .stButton > button, [data-testid="stSidebar"] .stRadio label, .stTabs [data-baseweb="tab"]{
    transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease, background .16s ease, filter .16s ease;
  }
}

/* ==================== Sidebar (less rigid, more premium) ==================== */
[data-testid="stSidebar"]{
  border-right: 1px solid rgba(255,255,255,0.10);
}
[data-testid="stSidebar"] > div:first-child{
  padding-top: 18px;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"]{
  gap: 10px;
}

/* Make sidebar nav look like premium capsules */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label{
  background: linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.03)) !important;
  border-radius: 18px !important;
  padding: 12px 14px !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked){
  background: linear-gradient(135deg, rgba(255,111,0,.92) 0%, rgba(255,179,0,.82) 55%, rgba(255,213,79,.74) 100%) !important;
  transform: translateY(-1px);
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover{
  transform: translateY(-1px);
  filter: brightness(1.03);
}

/* "Back to Dashboard" button in sidebar */
[data-testid="stSidebar"] .stButton > button{
  height: 46px !important;
  border-radius: 16px !important;
}
[data-testid="stSidebar"] button[kind="secondary"]{
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.05)) !important;
  border: 1px solid rgba(255,179,0,0.22) !important;
  box-shadow: 0 14px 40px rgba(0,0,0,0.34) !important;
}
[data-testid="stSidebar"] button[kind="secondary"]:hover{
  border-color: rgba(255,179,0,0.34) !important;
  box-shadow: 0 22px 70px rgba(255,111,0,0.18), 0 16px 44px rgba(0,0,0,0.38) !important;
}

/* ==================== Buttons (reduce 'slab' feel) ==================== */
.stButton > button{
  border-radius: 18px !important;
}
.stButton > button:active{ transform: translateY(0px) scale(.995); }

/* Download buttons: less 'blocky' */
div[data-testid="stDownloadButton"] button{
  height: 50px !important;
  border-radius: 18px !important;
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04)) !important;
  color: rgba(255,255,255,0.92) !important;
  border: 1px solid rgba(255,179,0,0.28) !important;
  box-shadow: 0 16px 44px rgba(0,0,0,0.34) !important;
}
div[data-testid="stDownloadButton"] button:hover{
  border-color: rgba(255,179,0,0.40) !important;
  box-shadow: 0 26px 86px rgba(255,111,0,0.20), 0 18px 52px rgba(0,0,0,0.38) !important;
}

/* ==================== Tabs (more premium) ==================== */
.stTabs [data-baseweb="tab-list"]{
  background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.03));
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 10px;
}
.stTabs [data-baseweb="tab"]{
  border-radius: 16px;
  background: rgba(255,255,255,0.03);
}
.stTabs [aria-selected="true"]{
  background: linear-gradient(135deg, rgba(255,111,0,.95) 0%, rgba(255,179,0,.85) 55%, rgba(255,213,79,.78) 100%) !important;
  box-shadow: 0 18px 60px rgba(255,111,0,0.22) !important;
}

/* ==================== DataFrame polish ==================== */
[data-testid="stDataFrame"]{
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 18px 60px rgba(0,0,0,0.34);
}

/* Strong top orange accent line */
.block-container::before{
  height:6px;
  background: linear-gradient(90deg,
    rgba(255,140,0,0) 0%,
    rgba(255,111,0,.95) 30%,
    rgba(255,179,0,1) 55%,
    rgba(255,140,0,.95) 75%,
    rgba(255,140,0,0) 100%);
  box-shadow: 0 18px 70px rgba(255,111,0,.55);
}

/* Cinematic glass depth */
div[data-testid="stVerticalBlockBorderWrapper"]{
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
  border: 1px solid rgba(255,170,0,0.18);
  backdrop-filter: blur(18px);
  box-shadow: 0 25px 90px rgba(255,120,0,0.18);
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover{
  box-shadow: 0 35px 120px rgba(255,120,0,0.28);
  border-color: rgba(255,200,120,0.28);
}

/* Softer premium buttons */
.stButton > button{
  background: linear-gradient(135deg, rgba(255,120,0,.95) 0%, rgba(255,170,0,.85) 60%, rgba(255,210,140,.75) 100%) !important;
  box-shadow: 0 24px 80px rgba(255,120,0,0.25), 0 12px 30px rgba(0,0,0,0.35) !important;
}
.stButton > button:hover{
  box-shadow: 0 34px 110px rgba(255,120,0,0.35), 0 18px 50px rgba(0,0,0,0.40) !important;
}

/* Elegant top accent */
.block-container::before{
  height:5px;
  background: linear-gradient(90deg,
    rgba(255,140,0,0) 0%,
    rgba(255,120,0,.85) 30%,
    rgba(255,200,120,.95) 55%,
    rgba(255,140,0,.85) 75%,
    rgba(255,140,0,0) 100%);
  box-shadow: 0 18px 60px rgba(255,120,0,.40);
}
"""

# Inject BPS accent tokens safely (no f-string CSS parsing issues)
CSS_THEME = (CSS_THEME
    .replace("__BPS_OREN__", BPS_OREN_UTAMA)
    .replace("__BPS_AMBER__", BPS_AMBER)
)

EXTRA_CSS = """
/* Dashboard quick-nav buttons */
.bps-hero + div .stButton > button{
  background: linear-gradient(135deg, rgba(255,111,0,.95) 0%, rgba(255,193,7,.88) 100%) !important;
}
.bps-hero + div button[kind="secondary"],
.bps-hero + div .stButton > button:disabled{
  background: rgba(255,255,255,.08) !important;
}
"""

st.markdown("<style>\n" + CSS_THEME + "\n" + EXTRA_CSS + "\n</style>", unsafe_allow_html=True)

# --- Force background override (Premium Sunset) ---
st.markdown(
    """
<style>
/* FINAL OVERRIDE — ensures background changes apply */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"]{
  background:
    radial-gradient(1600px 900px at 5% 15%, rgba(255,120,0,.55) 0%, rgba(255,120,0,.28) 35%, rgba(255,120,0,0) 70%),
    radial-gradient(1400px 900px at 95% 10%, rgba(255,170,0,.35) 0%, rgba(255,170,0,.18) 40%, rgba(255,170,0,0) 75%),
    radial-gradient(1200px 800px at 50% 100%, rgba(255,200,120,.18) 0%, rgba(255,200,120,0) 70%),
    linear-gradient(155deg, #1b0f08 0%, #2a1306 22%, #140c08 55%, #07090d 100%) !important;
  background-attachment: fixed !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# Hide sidebar entirely on Dashboard mode
if not st.session_state.get("show_sidebar", False):
    st.markdown(
        "<style>[data-testid='stSidebar']{display:none !important;} section.main{margin-left:0 !important;}</style>",
        unsafe_allow_html=True,
    )



# ======================================================================================
# UI ADD-ON (keep your original design, add premium components)
# ======================================================================================
st.markdown(
    """
<style>
/* =============================================================================
   Dashboard UMKM BPS — International UI v4 (ADD-ON POLISH)
   - DOES NOT remove your existing look; it enhances consistency, hierarchy, and
     interactive states.
   - Safe injection (no f-string), to prevent CSS being parsed as Python.
   ========================================================================== */

/* ---- Font ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ---- Tokens ---- */
:root{
  --bg0:#07080B;
  --bg1:#0B0D12;
  --card:rgba(255,255,255,.06);
  --card2:rgba(255,255,255,.085);
  --border:rgba(255,255,255,.10);
  --border2:rgba(255,255,255,.16);
  --text:rgba(255,255,255,.92);
  --muted:rgba(255,255,255,.68);

  /* Keep your BPS orange feel, but use it as accent (international style) */
  --accent: rgba(255,111,0,1);
  --accent2: rgba(255,193,7,1);

  --r-xl:22px;
  --r-lg:16px;
  --r-md:12px;

  --shadow-sm: 0 10px 26px rgba(0,0,0,.30);
  --shadow-md: 0 18px 64px rgba(0,0,0,.38);
  --shadow-glow: 0 26px 90px rgba(255,111,0,.26);
  --ring: 0 0 0 4px rgba(255,111,0,.24);
}

/* ---- Base ---- */
[data-testid="stAppViewContainer"]{
  font-family: "Inter", system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
  color: var(--text);
  background:
    radial-gradient(1100px 720px at 12% 12%, rgba(255,111,0,.22) 0%, rgba(255,111,0,0) 62%),
    radial-gradient(900px 640px at 88% 16%, rgba(255,193,7,.13) 0%, rgba(255,193,7,0) 58%),
    radial-gradient(920px 700px at 55% 105%, rgba(59,130,246,.12) 0%, rgba(59,130,246,0) 60%),
    linear-gradient(160deg, var(--bg0) 0%, var(--bg1) 62%, #05060A 100%) !important;
  background-attachment: fixed !important;
}
[data-testid="stHeader"]{ background: transparent !important; }
.block-container{ max-width: 1180px; padding-top: 1.15rem !important; padding-bottom: 2.2rem !important; }

/* Subtle top accent line */
.block-container::before{
  content:"";
  display:block;
  height:5px;
  width:100%;
  border-radius:999px;
  margin: 2px 0 16px 0;
  background: linear-gradient(90deg,
    rgba(255,111,0,0) 0%,
    rgba(255,111,0,.72) 26%,
    rgba(255,193,7,.72) 54%,
    rgba(255,111,0,.72) 82%,
    rgba(255,111,0,0) 100%);
  box-shadow: 0 12px 44px rgba(255,111,0,.26);
}

/* Typography hierarchy */
h1,h2,h3,h4{ letter-spacing:-0.02em; }
h1{ font-weight: 950 !important; }
h2,h3{ font-weight: 850 !important; }
p,li,label,.stMarkdown{ color: var(--text); }
small,.muted{ color: var(--muted); }

/* Scrollbar polish (desktop) */
::-webkit-scrollbar{ width: 10px; height: 10px; }
::-webkit-scrollbar-thumb{
  background: rgba(255,255,255,.12);
  border: 2px solid rgba(0,0,0,0);
  background-clip: padding-box;
  border-radius: 999px;
}
::-webkit-scrollbar-thumb:hover{ background: rgba(255,255,255,.18); background-clip: padding-box; }

/* ---- Cards / containers ---- */
div[data-testid="stVerticalBlockBorderWrapper"]{
  background: linear-gradient(180deg, rgba(255,255,255,0.075), rgba(255,255,255,0.045));
  border: 1px solid var(--border);
  border-radius: var(--r-xl);
  padding: 18px 18px;
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(14px);
  transition: transform .16s ease, box-shadow .18s ease, border-color .18s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover{
  border-color: rgba(255,255,255,0.17);
  box-shadow: var(--shadow-md), var(--shadow-glow);
  transform: translateY(-1px);
}

/* ---- Premium Section Header (helper HTML) ---- */
.bps-section{
  display:flex; align-items:flex-end; justify-content:space-between; gap:12px;
  margin: 4px 0 14px 0;
}
.bps-section .left{ display:flex; flex-direction:column; gap:6px; }
.bps-badge{
  display:inline-flex; align-items:center; gap:8px;
  font-size:.76rem; font-weight:900; letter-spacing:.14em;
  text-transform:uppercase;
  color: rgba(255,193,7,.92);
}
.bps-badge::before{
  content:"";
  width:10px; height:10px; border-radius:999px;
  background: linear-gradient(135deg, rgba(255,111,0,1), rgba(255,193,7,1));
  box-shadow: 0 10px 28px rgba(255,111,0,.22);
}
.bps-h{
  font-size: 1.55rem;
  font-weight: 950;
  margin: 0;
}
.bps-sub{
  margin: 0;
  color: var(--muted);
  line-height: 1.45;
}
.bps-divider{
  height:1px;
  margin-top: 12px;
  background: linear-gradient(90deg, rgba(255,111,0,0), rgba(255,111,0,.40), rgba(255,193,7,.34), rgba(255,111,0,0));
}

/* ---- Hero (your style, refined) ---- */
.bps-hero{
  display:flex; justify-content:space-between; gap:18px;
  padding: 22px 24px; border-radius: 22px;
  background:
    radial-gradient(900px 420px at 10% 0%, rgba(255,111,0,.22) 0%, rgba(255,111,0,0) 60%),
    radial-gradient(900px 420px at 92% 10%, rgba(255,193,7,.14) 0%, rgba(255,193,7,0) 62%),
    linear-gradient(135deg, rgba(255,255,255,.09) 0%, rgba(255,255,255,.05) 60%, rgba(255,255,255,.03) 100%);
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: 0 18px 60px rgba(0,0,0,.34);
  backdrop-filter: blur(16px);
}
.bps-hero h1{
  font-size: 2.05rem;
  font-weight: 980;
  margin: 0 0 8px 0;
  color: #fff;
}
.bps-hero p{ margin:0; color: var(--muted); font-size: 1.02rem; line-height:1.55; }
.bps-hero .cta-row{ display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; }
.bps-chip{
  display:inline-flex; align-items:center; gap:8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255,255,255,.06);
  border: 1px solid rgba(255,255,255,.10);
  color: rgba(255,255,255,.86);
  font-weight: 700;
  font-size: .88rem;
}

/* ---- Metrics ---- */
div[data-testid="metric-container"]{
  background: linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.045));
  border: 1px solid var(--border);
  border-left: 6px solid rgba(255,111,0,.95);
  border-radius: var(--r-lg);
  padding: 14px 16px;
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(14px);
  transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
}
div[data-testid="metric-container"]:hover{
  transform: translateY(-2px);
  border-color: rgba(255,255,255,0.18);
  box-shadow: var(--shadow-sm), var(--shadow-glow);
}
div[data-testid="metric-container"] label{
  color: var(--muted) !important;
  font-weight: 750;
  letter-spacing: .2px;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"]{ font-weight: 950; }

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"]{
  gap: 10px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  padding: 10px;
  border-radius: var(--r-lg);
  backdrop-filter: blur(14px);
}
.stTabs [data-baseweb="tab"]{
  height: 46px;
  border-radius: 14px;
  padding: 0 16px;
  background: rgba(255,255,255,0.03);
  color: rgba(255,255,255,.78);
}
.stTabs [aria-selected="true"]{
  background: linear-gradient(135deg, rgba(255,111,0,.92) 0%, rgba(255,193,7,.88) 100%) !important;
  color: #101113 !important;
  font-weight: 950;
  box-shadow: 0 18px 54px rgba(255,111,0,.26);
}

/* ---- Buttons ---- */
div[data-testid="stDownloadButton"] button,
.stButton > button{
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,.10) !important;
  background: linear-gradient(135deg, rgba(255,111,0,.92) 0%, rgba(255,193,7,.88) 100%) !important;
  color: #101113 !important;
  font-weight: 950 !important;
  height: 48px !important;
  box-shadow: 0 16px 44px rgba(255,111,0,.24);
  transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
}
div[data-testid="stDownloadButton"] button:hover,
.stButton > button:hover{
  transform: translateY(-1px);
  filter: brightness(1.04);
  box-shadow: 0 22px 64px rgba(255,111,0,.24);
}
button[kind="secondary"]{
  background: rgba(255,255,255,.08) !important;
  border: 1px solid rgba(255,255,255,.14) !important;
  color: rgba(255,255,255,.92) !important;
}

/* ---- Inputs ---- */
div[data-baseweb="input"] input,
div[data-baseweb="select"] > div{
  border-radius: 14px !important;
}
div[data-baseweb="input"]{
  background: rgba(255,255,255,.05) !important;
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,.10) !important;
}
div[data-baseweb="input"]:focus-within{
  box-shadow: var(--ring) !important;
  border-color: rgba(255,111,0,.35) !important;
}
div[data-baseweb="select"] > div{
  background: rgba(255,255,255,.05) !important;
  border: 1px solid rgba(255,255,255,.10) !important;
}
div[data-baseweb="select"]:focus-within > div{
  box-shadow: var(--ring) !important;
  border-color: rgba(255,111,0,.35) !important;
}

/* ---- Dataframe ---- */
[data-testid="stDataFrame"]{
  border-radius: var(--r-lg);
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: var(--shadow-sm);
}

/* ---- Expanders ---- */
details{
  background: rgba(255,255,255,.045);
  border: 1px solid rgba(255,255,255,.10);
  border-radius: var(--r-lg);
  padding: 6px 10px;
}
details[open]{ box-shadow: var(--shadow-sm); }

/* ---- Sidebar (major polish) ---- */
[data-testid="stSidebar"]{
  background:
    radial-gradient(600px 460px at 25% 10%, rgba(255,111,0,.16) 0%, rgba(255,111,0,0) 62%),
    linear-gradient(180deg, rgba(13,15,20,.98) 0%, rgba(9,10,14,.99) 100%) !important;
  border-right: 1px solid rgba(255,255,255,0.10);
  box-shadow: 14px 0 46px rgba(0,0,0,.44);
}
[data-testid="stSidebar"] *{ color: rgba(255,255,255,.92) !important; }
[data-testid="stSidebar"] .stMarkdown p{ color: rgba(255,255,255,.74) !important; }
[data-testid="stSidebar"] hr{ border-color: rgba(255,255,255,.10) !important; }

/* Radio menu -> pill navigation */
[data-testid="stSidebar"] div[role="radiogroup"]{
  gap: 10px;
}
[data-testid="stSidebar"] div[role="radiogroup"] label{
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,.10);
  background: rgba(255,255,255,.05);
  padding: 10px 12px;
  transition: transform .14s ease, border-color .14s ease, box-shadow .14s ease, background .14s ease;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover{
  transform: translateY(-1px);
  border-color: rgba(255,255,255,.18);
  background: rgba(255,255,255,.07);
  box-shadow: 0 16px 38px rgba(0,0,0,.26);
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){
  background: linear-gradient(135deg, rgba(255,111,0,.95) 0%, rgba(255,193,7,.88) 100%);
  border-color: rgba(255,255,255,.12);
  box-shadow: 0 18px 54px rgba(255,111,0,.24);
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p{
  color: #101113 !important;
  font-weight: 950 !important;
}

/* ---- Link ---- */
a{ color: rgba(255,193,7,.95) !important; }
a:hover{ color: rgba(255,193,7,1) !important; }

/* ---- Splash screen polish (keep) ---- */
.splash-wrap{
  border-radius: 26px;
  padding: 26px 28px;
  margin: 8px 0 10px 0;
  background:
    radial-gradient(900px 380px at 12% 0%, rgba(255,111,0,.24) 0%, rgba(255,111,0,0) 62%),
    radial-gradient(900px 380px at 88% 8%, rgba(255,193,7,.14) 0%, rgba(255,193,7,0) 62%),
    linear-gradient(135deg, rgba(255,255,255,.09) 0%, rgba(255,255,255,.05) 60%, rgba(255,255,255,.03) 100%);
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: 0 20px 70px rgba(0,0,0,.36);
  backdrop-filter: blur(16px);
}
.splash-kicker{
  display:inline-flex; align-items:center; gap:8px;
  font-weight: 900;
  font-size: .78rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(255,193,7,.92);
  margin-bottom: 10px;
}
.splash-title{
  font-size: 2.0rem;
  font-weight: 980;
  margin: 0 0 8px 0;
  color:#fff;
}
.splash-sub{
  margin: 0;
  color: rgba(255,255,255,.70);
  font-size: 1.02rem;
  line-height: 1.55;
}
.splash-row{ display:flex; gap:10px; flex-wrap:wrap; margin-top: 14px; }
.splash-pill{
  display:inline-flex; align-items:center; gap:8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255,255,255,.06);
  border: 1px solid rgba(255,255,255,.10);
  color: rgba(255,255,255,.86);
  font-weight: 750;
  font-size: .88rem;
}
</style>
""",
    unsafe_allow_html=True,
)
# ======================================================================================
# SESSION STATE
# ======================================================================================
def ensure_state():
    defaults = {
        "data_shopee": None, "audit_shopee": {},
        "data_tokped": None, "audit_tokped": {},
        "data_fb": None,     "audit_fb": {},
        "data_fb_forum": None, "audit_fb_forum": {},
        "data_maps": None,   "audit_maps": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ensure_state()


# ======================================================================================
# HELPERS (UI)
# ======================================================================================
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

def fmt_int_id(n: int) -> str:
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return "0"

def safe_title(x: str) -> str:
    if x is None:
        return ""
    s = str(x).strip()
    return s[:1].upper() + s[1:] if s else s


# ======================================================================================
# HELPERS (CLEANERS)
# ======================================================================================
def _to_str(x):
    if pd.isna(x):
        return ""
    return str(x)

def clean_placeholder_to_empty(x: str) -> str:
    s = _to_str(x).strip()
    if not s:
        return ""
    if s.lower() == PLACEHOLDER.lower():
        return ""
    if s.lower() in ["nan", "none", "null"]:
        return ""
    return re.sub(r"\s+", " ", s).strip()

def normalize_phone_id(x: str) -> str:
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

def normalize_url(x: str) -> str:
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

def to_float_safe(x: str):
    s = clean_placeholder_to_empty(x)
    if not s:
        return None
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


# ======================================================================================
# BUSINESS LOGIC
# ======================================================================================
def deteksi_tipe_usaha(nama_toko):
    if pd.isna(nama_toko) or nama_toko in ["Tidak Dilacak", "Toko CSV", "Anonim", ""]:
        return "Tidak Terdeteksi (Butuh Nama Toko)"

    if str(nama_toko) == "FB Seller":
        return "Perorangan (Facebook)"

    nama_lower = str(nama_toko).lower()
    keyword_fisik = [
        "toko", "warung", "grosir", "mart", "apotek", "cv.", "pt.", "official", "agen",
        "distributor", "kios", "kedai", "supermarket", "minimarket", "cabang", "jaya",
        "abadi", "makmur", "motor", "mobil", "bengkel", "snack", "store","jajanan"
    ]
    
    for kata in keyword_fisik:
        if kata in nama_lower:
            return "Ada Toko Fisik"
    return "Murni Online (Rumahan)"

def clean_maps_dataframe(df_raw: pd.DataFrame) -> (pd.DataFrame, dict):
    audit = {
        "rows_in": 0,
        "rows_out": 0,
        "missing_cols": [],
        "dedup_removed": 0,
        "invalid_coord": 0,
        "invalid_link": 0,
        "empty_name": 0,
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

def read_csv_smart(file_obj) -> pd.DataFrame:
    """
    Read CSV from Streamlit UploadedFile / file-like object with best-effort delimiter detection.
    Supports comma/semicolon/tab/pipe, and utf-8-sig (Excel-friendly).
    """
    # Read bytes (do not rely on current pointer)
    try:
        raw = file_obj.getvalue()
    except Exception:
        pos = None
        try:
            pos = file_obj.tell()
        except Exception:
            pos = None
        raw = file_obj.read()
        try:
            if pos is not None:
                file_obj.seek(pos)
        except Exception:
            pass

    if raw is None:
        return pd.DataFrame()

    # Try a small set of common delimiters and pick the one that yields the most columns.
    seps = [",", ";", "\t", "|"]
    best_df = None
    best_cols = -1

    for sep in seps:
        try:
            df = pd.read_csv(io.BytesIO(raw), sep=sep, dtype=str, on_bad_lines="skip",
                             encoding="utf-8-sig", engine="python")
            if df is not None and df.shape[1] > best_cols:
                best_df, best_cols = df, df.shape[1]
        except Exception:
            continue

    if best_df is not None and best_cols > 0:
        return best_df

    # Final fallback
    try:
        return pd.read_csv(io.BytesIO(raw), sep=None, dtype=str, on_bad_lines="skip",
                           encoding="utf-8-sig", engine="python")
    except Exception:
        return pd.DataFrame()


def read_csv_files(files) -> (pd.DataFrame, int):
    dfs = []
    total = 0
    for f in files:
        df = read_csv_smart(f)
        total += len(df)
        dfs.append(df)
    if not dfs:
        return pd.DataFrame(), 0
    return pd.concat(dfs, ignore_index=True), total


def _parse_price_int_any(x: str) -> int:
    s = clean_placeholder_to_empty(x)
    if not s:
        return 0
    digits = re.findall(r"\d+", s.replace(".", "").replace(",", ""))
    if not digits:
        return 0
    try:
        val = int(digits[0])
        return 0 if val > 1_000_000_000 else val
    except Exception:
        return 0


def _parse_coord_pair(x: str):
    s = clean_placeholder_to_empty(x)
    if not s or s == "-":
        return (None, None)
    s = s.replace(" ", "")
    m = re.search(r"(-?\d+(?:\.\d+)?)[,;](-?\d+(?:\.\d+)?)", s)
    if not m:
        return (None, None)
    try:
        lat = float(m.group(1))
        lon = float(m.group(2))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return (None, None)
        return (lat, lon)
    except Exception:
        return (None, None)


def _infer_wilayah_from_text(text: str) -> str:
    s = (text or "").lower()
    for k in BABEL_KEYS:
        if k in s:
            return safe_title(k.replace("tanjungpandan", "tanjung pandan"))
    return ""
def _pick_col(columns, candidates):
    colset = set(columns)
    for c in candidates:
        if c in colset:
            return c
    # case-insensitive fallback
    lower_map = {str(c).lower(): c for c in columns}
    for c in candidates:
        lc = str(c).lower()
        if lc in lower_map:
            return lower_map[lc]
    return None

def is_in_babel(wilayah: str) -> bool:
    s = (wilayah or "").lower()
    return any(k in s for k in BABEL_KEYS)


# ======================================================================================
# REAL MAP (FOLIUM) + FALLBACK SAFE (NO TILE)
# ======================================================================================
def render_real_map_folium(df_maps: pd.DataFrame, height: int = 560):
    """Real map (Leaflet/Folium). Jika tile diblok (403), user bisa ganti provider.
    Kalau tetap gagal, otomatis fallback ke peta aman (tanpa tile) via scatter_geo.
    """
    df_plot = df_maps.dropna(subset=["Latitude", "Longitude"]).copy()
    df_plot = df_plot[(df_plot["Latitude"].between(-90, 90)) & (df_plot["Longitude"].between(-180, 180))].copy()
    if df_plot.empty:
        st.info("Tidak ada koordinat valid untuk ditampilkan.")
        return

    tile_choice = st.selectbox(
        "🗺️ Provider Peta (kalau blank/403, ganti ini)",
        [
            "CartoDB DarkMatter (recommended)",
            "CartoDB Positron",
            "OpenStreetMap",
        ],
        index=0,
        key="maps_tile_provider",
    )

    tiles_map = {
        "OpenStreetMap": "OpenStreetMap",
        "CartoDB Positron": "CartoDB positron",
        "CartoDB DarkMatter (recommended)": "CartoDB dark_matter",
    }

    center_lat = float(df_plot["Latitude"].mean())
    center_lon = float(df_plot["Longitude"].mean())

    try:
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles=tiles_map.get(tile_choice, "CartoDB dark_matter"),
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

            link_html = f'<a href="{link}" target="_blank">Buka Link</a>' if link else "-"

            popup = f"""
            <div style="width:260px;">
              <div style="font-weight:800; font-size:14px; margin-bottom:6px;">{nama}</div>
              <div style="font-size:12px; opacity:.92;">{alamat}</div>
              <hr style="border:none;border-top:1px solid rgba(255,111,0,.25); margin:8px 0;">
              <div style="font-size:12px;">☎️ {telp if telp else "-"}</div>
              <div style="font-size:12px; margin-top:4px;">🔗 {link_html}</div>
            </div>
            """

            folium.CircleMarker(
                location=[float(r["Latitude"]), float(r["Longitude"])],
                radius=7,
                weight=2,
                color="#FF6F00",
                fill=True,
                fill_color="#FF6F00",
                fill_opacity=0.85,
                popup=folium.Popup(popup, max_width=340),
            ).add_to(cluster)

        folium.LayerControl(collapsed=True).add_to(m)

        st_folium(m, width=None, height=height)
        st.caption("Jika peta tidak tampil (tile diblok), coba ganti Provider Peta di atas.")
        return

    except Exception:
        st.warning("Provider tile diblok/403. Menampilkan peta aman (tanpa tile) sebagai fallback.")
        fig = px.scatter_geo(
            df_plot,
            lat="Latitude",
            lon="Longitude",
            hover_name="Nama Usaha",
            hover_data={"Alamat": True, "No Telepon": True, "Link": True, "Latitude": ":.6f", "Longitude": ":.6f"},
            projection="mercator",
            height=height,
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor=BPS_PAPER,
            plot_bgcolor=BPS_PAPER,
            font=dict(color="white"),
        )
        st.plotly_chart(fig, use_container_width=True)



# ======================================================================================
# SPLASH / LOADING SCREEN (first open per session)
# - Shows a brief progress bar before entering the dashboard
# ======================================================================================
def splash_screen():
    """Splash screen shown once per session."""
    # Temporarily hide the sidebar while loading
    st.markdown(
        """
        <style>
          [data-testid="stSidebar"]{ display:none !important; }
          [data-testid="stHeader"]{ background: transparent !important; }
          .block-container{ padding-top: 2.2rem !important; }
          .splash-wrap{
            border-radius: 28px;
            padding: 30px 32px;
            max-width: 860px;
            margin: 6vh auto 0 auto;
            background:
              radial-gradient(1200px 520px at 12% 0%, rgba(255,111,0,.26) 0%, rgba(255,111,0,0) 62%),
              radial-gradient(1000px 520px at 88% 12%, rgba(255,193,7,.12) 0%, rgba(255,193,7,0) 62%),
              linear-gradient(135deg, rgba(255,255,255,.10) 0%, rgba(255,255,255,.05) 60%, rgba(255,255,255,.03) 100%);
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 22px 70px rgba(0,0,0,.42);
            backdrop-filter: blur(16px);
          }
          .splash-kicker{
            display:inline-flex; align-items:center; gap:10px;
            font-weight: 900; font-size: .80rem; letter-spacing: .16em;
            text-transform: uppercase; color: rgba(255,193,7,.92);
            margin-bottom: 10px;
          }
          .splash-title{
            font-size: 2.2rem; font-weight: 950; margin: 0 0 10px 0; color: #fff;
            letter-spacing: -0.02em;
          }
          .splash-sub{
            margin: 0 0 18px 0; color: rgba(255,255,255,.70);
            font-size: 1.04rem; line-height: 1.55;
          }
          .splash-row{ display:flex; gap:14px; align-items:center; margin-top: 12px; }
          .splash-pill{
            padding: 10px 12px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,.10);
            background: rgba(255,255,255,.05);
            color: rgba(255,255,255,.86);
            font-weight: 700;
            font-size: .92rem;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Content
    st.markdown('<div class="splash-wrap">', unsafe_allow_html=True)

    # Header row with logo (if exists)
    cols = st.columns([0.55, 2.2])
    with cols[0]:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
    with cols[1]:
        st.markdown('<div class="splash-kicker">BPS BABEL • DASHBOARD UMKM</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="splash-title">{APP_TITLE}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="splash-sub">Menyiapkan tampilan, memuat modul, dan mengoptimalkan pengalaman penggunaan…</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="splash-row">', unsafe_allow_html=True)
    st.markdown('<div class="splash-pill">UI Modern</div>', unsafe_allow_html=True)
    st.markdown('<div class="splash-pill">Navigasi Cepat</div>', unsafe_allow_html=True)
    st.markdown('<div class="splash-pill">Akurat & Rapi</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    prog = st.progress(0)
    status = st.empty()

    # Fast, smooth progression (no heavy work; just UX)
    for i in range(0, 101, 4):
        prog.progress(i)
        if i < 30:
            status.caption("Menginisialisasi komponen…")
        elif i < 70:
            status.caption("Menyiapkan modul marketplace…")
        else:
            status.caption("Hampir selesai…")
        time.sleep(0.02)

    st.markdown("</div>", unsafe_allow_html=True)

    # Mark loaded and rerun to enter the main app
    st.session_state["__splash_done__"] = True
    st.rerun()


if "__splash_done__" not in st.session_state:
    st.session_state["__splash_done__"] = False

if not st.session_state["__splash_done__"]:
    splash_screen()


# ======================================================================================
# SIDEBAR (hidden on Dashboard)
# ======================================================================================
# --- Navigation state (safe) ---
if "__boot__" not in st.session_state:
    # always start clean: Dashboard without sidebar
    st.session_state["__boot__"] = True
    st.session_state["show_sidebar"] = False
    st.session_state["menu_nav"] = "🏠 Dashboard"
    st.session_state["nav_target"] = None

if "show_sidebar" not in st.session_state:
    st.session_state["show_sidebar"] = False  # start without sidebar on Dashboard
if "menu_nav" not in st.session_state:
    st.session_state["menu_nav"] = "🏠 Dashboard"

# Apply pending navigation target BEFORE widget creation
if st.session_state.get("nav_target"):
    st.session_state["menu_nav"] = st.session_state["nav_target"]
    st.session_state["nav_target"] = None

# If we're on Dashboard, force-hide sidebar (even if previous run left it on)
if st.session_state.get("menu_nav") == "🏠 Dashboard" and not st.session_state.get("nav_target"):
    st.session_state["show_sidebar"] = False

# Ensure widget value is valid when sidebar is shown
if st.session_state.get("show_sidebar") and st.session_state.get("menu_nav") == "🏠 Dashboard":
    st.session_state["menu_nav"] = "🟠 Shopee"



menu = "🏠 Dashboard"

if st.session_state["show_sidebar"]:
    with st.sidebar:
        st.markdown(f"### {APP_ICON} {APP_TITLE}")
        st.caption("Penyedia Data Statistik Berkualitas untuk Indonesia Maju")
        st.divider()

        # Premium "Back to Dashboard"
        if st.button("⬅️ Kembali ke Dashboard", key="btn_home", use_container_width=True, type="secondary"):
            st.session_state["show_sidebar"] = False
            st.session_state["menu_nav"] = "🏠 Dashboard"
            st.rerun()

        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)

        menu = st.radio(
            "🧭 Navigasi",
            ["🟠 Shopee", "🟢 Tokopedia", "🔵 Facebook", "🟣 FB Forum", "📍 Google Maps", "📊 Export Gabungan"],
            index=0,
            key="menu_nav",
        )

        st.divider()
        with st.expander("⚙️ Pengaturan Umum", expanded=False):
            st.checkbox("Tampilkan tips cepat", value=True, key="show_tips")
            st.checkbox("Mode cepat (kurangi rendering chart besar)", value=False, key="fast_mode")

# Hide sidebar visually when not used (Dashboard mode)
if not st.session_state.get("show_sidebar", False):
    st.markdown(
        "<style>[data-testid='stSidebar']{display:none !important;} section.main{margin-left:0 !important;}</style>",
        unsafe_allow_html=True,
    )

# ======================================================================================
# PAGE: DASHBOARD (Before entering UMKM modules)
# ======================================================================================
if menu == "🏠 Dashboard":
    # Always hide sidebar on Dashboard
    st.session_state["show_sidebar"] = False

    section_header("Dashboard Utama", "Ringkasan status data & akses cepat ke modul UMKM.", "DASHBOARD")
    banner("Dashboard Utama", "Mulai dari ringkasan cepat, lalu masuk ke modul UMKM yang kamu butuhkan.")

    # Hero / quick actions
    st.markdown(
        """
<div class="bps-hero">
  <div>
    <div class="bps-badge">UMKM • BPS BABEL</div>
    <h1>Kontrol Pusat Analisis UMKM</h1>
    <p>Upload data dari marketplace / maps, cek ringkasan, lalu lanjutkan analisis.</p>
    <div class="cta-row">
      <span class="bps-chip">🟠 Shopee</span>
      <span class="bps-chip">🟢 Tokopedia</span>
      <span class="bps-chip">🔵 Facebook</span>
      <span class="bps-chip">🟣 FB Forum</span>
      <span class="bps-chip">📍 Google Maps</span>
      <span class="bps-chip">📊 Export</span>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Data readiness
    df_shp = st.session_state.data_shopee
    df_tkp = st.session_state.data_tokped
    df_fb = st.session_state.data_fb
    df_fb_forum = st.session_state.data_fb_forum
    df_maps = st.session_state.data_maps

    shp_n = 0 if df_shp is None else len(df_shp)
    tkp_n = 0 if df_tkp is None else len(df_tkp)
    fb_n  = 0 if df_fb is None else len(df_fb)
    fbf_n = 0 if df_fb_forum is None else len(df_fb_forum)
    mp_n  = 0 if df_maps is None else len(df_maps)

    total_all = shp_n + tkp_n + fb_n + fbf_n + mp_n

    
    # Premium KPI cards (less "kaku" than st.metric)
    st.markdown(
        f"""
<style>
.kpi-grid{{
  display:grid;
  grid-template-columns: repeat(6, minmax(0,1fr));
  gap: 14px;
  margin-top: 6px;
}}
@media (max-width: 1200px){{
  .kpi-grid{{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
}}
.kpi-card{{
  border-radius: 18px;
  border: 1px solid rgba(255,200,120,0.18);
  background: linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.035));
  box-shadow: 0 18px 60px rgba(0,0,0,0.34);
  padding: 14px 14px;
  backdrop-filter: blur(16px);
  position: relative;
  overflow: hidden;
}}
.kpi-card::before{{
  content:"";
  position:absolute; inset:-2px;
  background: radial-gradient(700px 240px at 10% 10%, rgba(255,140,40,0.26), rgba(255,140,40,0));
  opacity:.9;
  pointer-events:none;
}}
.kpi-top{{
  display:flex; align-items:center; justify-content:space-between;
  position: relative;
}}
.kpi-label{{
  font-weight: 800;
  letter-spacing: .2px;
  color: rgba(255,255,255,0.78);
  font-size: .92rem;
}}
.kpi-ico{{
  width: 34px; height: 34px;
  border-radius: 12px;
  display:flex; align-items:center; justify-content:center;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
}}
.kpi-val{{
  position: relative;
  margin-top: 10px;
  font-size: 2.05rem;
  font-weight: 950;
  letter-spacing: -0.03em;
  color: rgba(255,255,255,0.96);
}}
.kpi-sub{{
  position: relative;
  margin-top: 2px;
  color: rgba(255,255,255,0.62);
  font-size: .86rem;
}}
.kpi-accent{{
  position:absolute; left:0; top:0; bottom:0;
  width: 6px;
  background: linear-gradient(180deg, rgba(255,120,0,0.95), rgba(255,210,140,0.65));
}}
</style>

<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-top">
      <div class="kpi-label">📦 Total Data</div>
      <div class="kpi-ico">⚡</div>
    </div>
    <div class="kpi-val">{fmt_int_id(total_all)}</div>
    <div class="kpi-sub">Akumulasi semua sumber</div>
  </div>

  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-top">
      <div class="kpi-label">🟠 Shopee</div>
      <div class="kpi-ico">🛒</div>
    </div>
    <div class="kpi-val">{fmt_int_id(shp_n)}</div>
    <div class="kpi-sub">Siap diproses</div>
  </div>

  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-top">
      <div class="kpi-label">🟢 Tokopedia</div>
      <div class="kpi-ico">🧾</div>
    </div>
    <div class="kpi-val">{fmt_int_id(tkp_n)}</div>
    <div class="kpi-sub">Siap diproses</div>
  </div>

  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-top">
      <div class="kpi-label">🔵 Facebook</div>
      <div class="kpi-ico">💬</div>
    </div>
    <div class="kpi-val">{fmt_int_id(fb_n)}</div>
    <div class="kpi-sub">Siap diproses</div>
  </div>


<div class="kpi-card">
  <div class="kpi-accent"></div>
  <div class="kpi-top">
    <div class="kpi-label">🟣 FB Forum</div>
    <div class="kpi-ico">🧵</div>
  </div>
  <div class="kpi-val">{fmt_int_id(fbf_n)}</div>
  <div class="kpi-sub">Siap diproses</div>
</div>
  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-top">
      <div class="kpi-label">📍 Google Maps</div>
      <div class="kpi-ico">🧭</div>
    </div>
    <div class="kpi-val">{fmt_int_id(mp_n)}</div>
    <div class="kpi-sub">Siap divisualisasi</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.subheader("🚦 Status Modul")
        s1, s2 = st.columns([1.1, 0.9], gap="large")

        def _pill(ok: bool, text: str):
            cls = "ok" if ok else "no"
            icon = "✅" if ok else "⏳"
            return f'<span class="dash-pill {cls}">{icon} {text}</span>'

        st.markdown(
            """
<style>
/* Dashboard pills */
.dash-pill{
  display:inline-flex; align-items:center; gap:8px;
  padding: 10px 12px;
  border-radius: 999px;
  margin: 6px 10px 0 0;
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.05);
  font-weight: 800;
}
.dash-pill.ok{
  border-color: rgba(255,193,7,.32);
  background: linear-gradient(135deg, rgba(255,111,0,.26), rgba(255,193,7,.10));
  box-shadow: 0 18px 50px rgba(255,111,0,.10);
}
.dash-pill.no{
  opacity: .82;
}
</style>
""",
            unsafe_allow_html=True,
        )

        with s1:
            st.markdown(
                _pill(shp_n > 0, "Shopee siap dianalisis") +
                _pill(tkp_n > 0, "Tokopedia siap dianalisis") +
                _pill(fb_n > 0, "Facebook siap dianalisis") +
                _pill(fbf_n > 0, "FB Forum siap dianalisis") +
                _pill(mp_n > 0, "Google Maps siap divisualisasi"),
                unsafe_allow_html=True,
            )
            st.caption("Tip: Mulai dari modul yang datanya sudah siap. Setelah itu gunakan Export Gabungan untuk konsolidasi.")
        with s2:
            st.subheader("🧭 Navigasi Cepat")

            st.markdown("Klik tombol di bawah untuk mulai mengelola data UMKM. Sidebar akan muncul otomatis.")
            if st.button("🚀 Ayo Upload Data", use_container_width=True):
                goto_menu("🟠 Shopee")



    # Recommendations / tips area
    with st.container(border=True):
        st.subheader("✨ Rekomendasi Cepat")
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
        left, right = st.columns([1.2, 1.0], gap="large")

        with left:
            st.subheader("📥 Input Data")
            files = st.file_uploader("Unggah CSV Shopee", type=["csv"], accept_multiple_files=True, key="file_shp")

            mode_api = st.toggle(
                "🔎 Deteksi Nama Toko via API Shopee",
                value=True,
                help="Jika ON: sistem akan mencoba mengambil nama toko dari API shopid di link produk.",
                key="api_shp",
            )

            colA, colB, colC = st.columns(3)
            with colA:
                api_timeout = st.number_input("Timeout API (detik)", min_value=1, max_value=10, value=2, step=1)
            with colB:
                api_sleep = st.number_input("Jeda per request (detik)", min_value=0.0, max_value=2.0, value=0.0, step=0.1)
            with colC:
                max_api_calls = st.number_input("Maks panggilan API", min_value=0, max_value=50000, value=8000, step=500)

            st.caption("Tips: kalau scraping kamu “terdeteksi robot”, coba naikkan jeda request.")
            run = st.button("🚀 Proses Data Shopee", type="primary", use_container_width=True)

        with right:
            st.subheader("🧾 Ringkasan & Aturan")
            st.info(
                "• Data otomatis difilter **Bangka Belitung**.\n"
                "• Harga dibersihkan jadi integer.\n"
                "• Tipe Usaha dihitung pakai heuristik (kata kunci nama toko)."
            )
            if st.session_state.get("show_tips"):
                st.success("Kalau CSV beda struktur, sistem akan coba tebak kolom link/nama/harga/wilayah.")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Shopee terlebih dahulu.")
        else:
            with st.status("Memproses data Shopee…", expanded=True) as status:
                try:
                    total_semua_baris = 0
                    for f in files:
                        df_temp = read_csv_smart(f)
                        total_semua_baris += len(df_temp)

                    hasil = []
                    total_baris = 0
                    err_h = 0
                    luar_wilayah = 0

                    progress = st.progress(0)
                    info = st.empty()
                    baris_diproses = 0

                    for file in files:
                        df_raw = read_csv_smart(file)
                        total_baris += len(df_raw)
                        if df_raw is None or df_raw.empty:
                            continue

                        # Support CSV dari server_marketplace.py (delimiter ;) dan variasi lainnya
                        col_toko = _pick_col(df_raw.columns, ["Nama_Penjual", "Nama Penjual", "Nama_Toko", "Nama Toko", "Penjual", "Seller"])
                        col_nama = _pick_col(df_raw.columns, ["Nama_Barang", "Nama Barang", "Nama Produk", "Produk", "Judul", "Title"])
                        col_harga = _pick_col(df_raw.columns, ["Harga", "Price"])
                        col_alamat = _pick_col(df_raw.columns, ["Alamat", "Wilayah", "Lokasi"])
                        col_nomor = _pick_col(df_raw.columns, ["Nomor_HP", "Nomor HP", "Nomor", "No HP", "No. HP", "Nomor WA", "WhatsApp"])
                        col_koor = _pick_col(df_raw.columns, ["Koordinat", "Coordinate"])
                        col_linkmap = _pick_col(df_raw.columns, ["Link_Map", "Link Map", "Link Maps"])
                        col_desc = _pick_col(df_raw.columns, ["Deskripsi", "Keterangan", "Description"])
                        col_link = _pick_col(df_raw.columns, ["URL", "Link", "Tautan"])
                        col_foto = _pick_col(df_raw.columns, ["Foto_Profil", "Foto Profil", "Foto", "foto", "Avatar"])

                        # Fallback lama (kalau struktur CSV tidak dikenal)
                        if not col_link and len(df_raw.columns) > 0:
                            col_link = df_raw.columns[-1]
                        if not col_harga and len(df_raw.columns) > 0:
                            col_harga = df_raw.columns[min(3, len(df_raw.columns) - 1)]
                        if not col_alamat and len(df_raw.columns) > 0:
                            col_alamat = df_raw.columns[min(2, len(df_raw.columns) - 1)]
                        if not col_nama and len(df_raw.columns) > 0:
                            col_nama = df_raw.columns[min(1, len(df_raw.columns) - 1)]
                        if not col_toko and len(df_raw.columns) > 0:
                            col_toko = df_raw.columns[0]

                        for i in range(len(df_raw)):
                            row = df_raw.iloc[i]

                            toko = clean_placeholder_to_empty(str(row.get(col_toko, ""))) or "FB Seller"
                            nama = clean_placeholder_to_empty(str(row.get(col_nama, "")))
                            harga_str = str(row.get(col_harga, "")) if col_harga else ""
                            alamat = clean_placeholder_to_empty(str(row.get(col_alamat, ""))) if col_alamat else ""
                            nomor = clean_placeholder_to_empty(str(row.get(col_nomor, ""))) if col_nomor else ""
                            deskripsi = clean_placeholder_to_empty(str(row.get(col_desc, ""))) if col_desc else ""
                            link = clean_placeholder_to_empty(str(row.get(col_link, ""))) if col_link else ""
                            foto = clean_placeholder_to_empty(str(row.get(col_foto, ""))) if col_foto else ""
                            koordinat = clean_placeholder_to_empty(str(row.get(col_koor, ""))) if col_koor else ""
                            link_map = clean_placeholder_to_empty(str(row.get(col_linkmap, ""))) if col_linkmap else ""

                            lat, lon = _parse_coord_pair(koordinat)
                            if (not link_map) and lat is not None and lon is not None:
                                link_map = f"https://www.google.com/maps?q={lat},{lon}"

                            wilayah_tag = _infer_wilayah_from_text(alamat) or safe_title(alamat)
                            # Validasi Bangka Belitung berdasarkan alamat/wilayah tag
                            if not is_in_babel(alamat) and not is_in_babel(wilayah_tag):
                                luar_wilayah += 1
                                baris_diproses += 1
                                continue

                            try:
                                val_h = _parse_price_int_any(harga_str)
                            except Exception:
                                val_h = 0
                                err_h += 1

                            if val_h > 0:
                                tipe_usaha = deteksi_tipe_usaha(toko)
                                hasil.append({
                                    "Nama Toko": toko,
                                    "Nama Produk": nama,
                                    "Harga": val_h,
                                    "Wilayah": wilayah_tag if wilayah_tag else "Bangka Belitung",
                                    "Alamat": alamat if alamat else wilayah_tag,
                                    "Nomor HP": nomor,
                                    "Latitude": lat,
                                    "Longitude": lon,
                                    "Koordinat": koordinat,
                                    "Link Maps": link_map,
                                    "Deskripsi": deskripsi,
                                    "Foto Profil": foto,
                                    "Tipe Usaha": tipe_usaha,
                                    "Link": link
                                })

                            baris_diproses += 1
                            if baris_diproses % 25 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses / max(total_semua_baris, 1), 1.0)
                                progress.progress(pct)
                                info.markdown(f"**⏳ Progress:** {fmt_int_id(baris_diproses)} / {fmt_int_id(total_semua_baris)} ({int(pct*100)}%)")

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
                f_wil = st.multiselect("📍 Wilayah", options=sorted(df_shp["Wilayah"].unique()),
                                       default=sorted(df_shp["Wilayah"].unique()), key="f_wil_shp")
            with c2:
                f_tipe = st.multiselect("🏢 Tipe Usaha", options=sorted(df_shp["Tipe Usaha"].unique()),
                                        default=sorted(df_shp["Tipe Usaha"].unique()), key="f_tipe_shp")
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

            if not st.session_state.get("fast_mode") and not df_f.empty:
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", hole=0.44,
                                 title="Komposisi Model Bisnis UMKM (Shopee)")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah")
                    fig = px.bar(grp, x="Wilayah", y="Jumlah",
                                 title="Total Usaha per Wilayah (Shopee)",
                                 color="Wilayah")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {int(x):,}".replace(",", ".") if str(x).isdigit() else f"Rp {x}")
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
    section_header("Tokopedia Marketplace", "Workflow Tokopedia dengan UI enterprise dan feedback yang jelas.", "MARKETPLACE")
    banner("Dashboard UMKM — Tokopedia", "Ekstraksi data UMKM dari Tokopedia (Bangka Belitung)")

    with st.container(border=True):
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV Tokopedia", type=["csv"], accept_multiple_files=True, key="file_tkp")
            run = st.button("🚀 Proses Data Tokopedia", type="primary", use_container_width=True)
        with col2:
            st.subheader("🧾 Catatan")
            st.info("• Sistem akan menebak kolom bila struktur CSV berbeda.\n• Data difilter otomatis hanya Babel.")

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
                                            "Nama Toko": toko, "Nama Produk": nama, "Harga": val_h,
                                            "Wilayah": lokasi, "Tipe Usaha": tipe_usaha, "Link": link
                                        })
                                except Exception:
                                    continue

                            baris_diproses += 1
                            if baris_diproses % 25 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses / max(total_semua_baris, 1), 1.0)
                                progress.progress(pct)
                                info.markdown(f"**⏳ Progress:** {fmt_int_id(baris_diproses)} / {fmt_int_id(total_semua_baris)} ({int(pct*100)}%)")

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
                f_wil = st.multiselect("📍 Wilayah", options=sorted(df_tkp["Wilayah"].unique()),
                                       default=sorted(df_tkp["Wilayah"].unique()), key="f_wil_tkp")
            with c2:
                f_tipe = st.multiselect("🏢 Tipe Usaha", options=sorted(df_tkp["Tipe Usaha"].unique()),
                                        default=sorted(df_tkp["Tipe Usaha"].unique()), key="f_tipe_tkp")
            with c3:
                q = st.text_input("🔎 Cari (nama toko / produk)", value="", key="q_tkp")

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

            if not st.session_state.get("fast_mode") and not df_f.empty:
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", hole=0.44,
                                 title="Komposisi Model Bisnis UMKM (Tokopedia)")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah")
                    fig = px.bar(grp, x="Wilayah", y="Jumlah",
                                 title="Total Usaha per Wilayah (Tokopedia)",
                                 color="Wilayah")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {int(x):,}".replace(",", ".") if str(x).isdigit() else f"Rp {x}")
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
# PAGE: FACEBOOK
# ======================================================================================
elif menu == "🔵 Facebook":
    section_header("Facebook Marketplace", "Scraping/olah data Facebook Marketplace dengan panel kontrol yang clean.", "MARKETPLACE")
    banner("Dashboard UMKM — Facebook Marketplace", "Ekstraksi data UMKM dari Facebook Marketplace (Bangka Belitung)")

    with st.container(border=True):
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV Facebook", type=["csv"], accept_multiple_files=True, key="file_fb")
            run = st.button("🚀 Proses Data Facebook", type="primary", use_container_width=True)
        with col2:
            st.subheader("🧾 Catatan")
            st.info("• Nama toko sering kosong → akan diisi default.\n• Tipe Usaha perorangan otomatis bila terdeteksi.")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Facebook terlebih dahulu.")
        else:
            with st.status("Memproses data Facebook…", expanded=True) as status:
                try:
                    total_semua_baris = 0
                    for f in files:
                        df_temp = read_csv_smart(f)
                        total_semua_baris += len(df_temp)

                    hasil = []
                    total_baris = 0
                    err_h = 0
                    luar_wilayah = 0

                    progress = st.progress(0)
                    info = st.empty()
                    baris_diproses = 0

                    for file in files:
                        df_raw = read_csv_smart(file)
                        total_baris += len(df_raw)
                        if df_raw is None or df_raw.empty:
                            continue

                        # Support CSV dari server_marketplace.py (delimiter ;) dan variasi lainnya
                        col_toko = _pick_col(df_raw.columns, ["Nama_Penjual", "Nama Penjual", "Nama_Toko", "Nama Toko", "Penjual", "Seller"])
                        col_nama = _pick_col(df_raw.columns, ["Nama_Barang", "Nama Barang", "Nama Produk", "Produk", "Judul", "Title"])
                        col_harga = _pick_col(df_raw.columns, ["Harga", "Price"])
                        col_alamat = _pick_col(df_raw.columns, ["Alamat", "Wilayah", "Lokasi"])
                        col_nomor = _pick_col(df_raw.columns, ["Nomor_HP", "Nomor HP", "Nomor", "No HP", "No. HP", "Nomor WA", "WhatsApp"])
                        col_koor = _pick_col(df_raw.columns, ["Koordinat", "Coordinate"])
                        col_linkmap = _pick_col(df_raw.columns, ["Link_Map", "Link Map", "Link Maps"])
                        col_desc = _pick_col(df_raw.columns, ["Deskripsi", "Keterangan", "Description"])
                        col_link = _pick_col(df_raw.columns, ["URL", "Link", "Tautan"])
                        col_foto = _pick_col(df_raw.columns, ["Foto_Profil", "Foto Profil", "Foto", "foto", "Avatar"])

                        # Fallback lama (kalau struktur CSV tidak dikenal)
                        if not col_link and len(df_raw.columns) > 0:
                            col_link = df_raw.columns[-1]
                        if not col_harga and len(df_raw.columns) > 0:
                            col_harga = df_raw.columns[min(3, len(df_raw.columns) - 1)]
                        if not col_alamat and len(df_raw.columns) > 0:
                            col_alamat = df_raw.columns[min(2, len(df_raw.columns) - 1)]
                        if not col_nama and len(df_raw.columns) > 0:
                            col_nama = df_raw.columns[min(1, len(df_raw.columns) - 1)]
                        if not col_toko and len(df_raw.columns) > 0:
                            col_toko = df_raw.columns[0]

                        for i in range(len(df_raw)):
                            row = df_raw.iloc[i]

                            toko = clean_placeholder_to_empty(str(row.get(col_toko, ""))) or "FB Seller"
                            nama = clean_placeholder_to_empty(str(row.get(col_nama, "")))
                            harga_str = str(row.get(col_harga, "")) if col_harga else ""
                            alamat = clean_placeholder_to_empty(str(row.get(col_alamat, ""))) if col_alamat else ""
                            nomor = clean_placeholder_to_empty(str(row.get(col_nomor, ""))) if col_nomor else ""
                            deskripsi = clean_placeholder_to_empty(str(row.get(col_desc, ""))) if col_desc else ""
                            link = clean_placeholder_to_empty(str(row.get(col_link, ""))) if col_link else ""
                            foto = clean_placeholder_to_empty(str(row.get(col_foto, ""))) if col_foto else ""
                            koordinat = clean_placeholder_to_empty(str(row.get(col_koor, ""))) if col_koor else ""
                            link_map = clean_placeholder_to_empty(str(row.get(col_linkmap, ""))) if col_linkmap else ""

                            lat, lon = _parse_coord_pair(koordinat)
                            if (not link_map) and lat is not None and lon is not None:
                                link_map = f"https://www.google.com/maps?q={lat},{lon}"

                            wilayah_tag = _infer_wilayah_from_text(alamat) or safe_title(alamat)
                            # Validasi Bangka Belitung berdasarkan alamat/wilayah tag
                            if not is_in_babel(alamat) and not is_in_babel(wilayah_tag):
                                luar_wilayah += 1
                                baris_diproses += 1
                                continue

                            try:
                                val_h = _parse_price_int_any(harga_str)
                            except Exception:
                                val_h = 0
                                err_h += 1

                            if val_h > 0:
                                tipe_usaha = deteksi_tipe_usaha(toko)
                                hasil.append({
                                    "Nama Toko": toko,
                                    "Nama Produk": nama,
                                    "Harga": val_h,
                                    "Wilayah": wilayah_tag if wilayah_tag else "Bangka Belitung",
                                    "Alamat": alamat if alamat else wilayah_tag,
                                    "Nomor HP": nomor,
                                    "Latitude": lat,
                                    "Longitude": lon,
                                    "Koordinat": koordinat,
                                    "Link Maps": link_map,
                                    "Deskripsi": deskripsi,
                                    "Foto Profil": foto,
                                    "Tipe Usaha": tipe_usaha,
                                    "Link": link
                                })

                            baris_diproses += 1
                            if baris_diproses % 25 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses / max(total_semua_baris, 1), 1.0)
                                progress.progress(pct)
                                info.markdown(f"**⏳ Progress:** {fmt_int_id(baris_diproses)} / {fmt_int_id(total_semua_baris)} ({int(pct*100)}%)")

                    progress.empty()
                    info.empty()

                    df_final = pd.DataFrame(hasil).drop_duplicates()
                    st.session_state.data_fb = df_final
                    st.session_state.audit_fb = {
                        "file_count": len(files),
                        "total_rows": total_baris,
                        "valid_rows": len(df_final),
                        "luar_wilayah": luar_wilayah,
                        "error_harga": err_h,
                    }

                    status.update(label="✅ Selesai memproses Facebook", state="complete", expanded=False)
                    st.toast(f"Facebook: {fmt_int_id(len(df_final))} baris siap dianalisis", icon="✅")

                except Exception as e:
                    status.update(label="❌ Gagal memproses Facebook", state="error", expanded=True)
                    st.error(f"Error Sistem FB: {e}")

    df_fb = st.session_state.data_fb
    if df_fb is not None and not df_fb.empty:
        with st.container(border=True):
            st.subheader("🔎 Filter Pintar")
            c1, c2, c3 = st.columns([1.2, 1.2, 1.6], gap="medium")
            with c1:
                f_wil = st.multiselect("📍 Wilayah", options=sorted(df_fb["Wilayah"].unique()),
                                       default=sorted(df_fb["Wilayah"].unique()), key="f_wil_fb")
            with c2:
                f_tipe = st.multiselect("🏢 Tipe Usaha", options=sorted(df_fb["Tipe Usaha"].unique()),
                                        default=sorted(df_fb["Tipe Usaha"].unique()), key="f_tipe_fb")
            with c3:
                q = st.text_input("🔎 Cari (nama toko / produk)", value="", key="q_fb")

            max_h = int(df_fb["Harga"].max()) if df_fb["Harga"].max() > 0 else 1_000_000
            f_hrg = st.slider("💰 Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_fb")

        df_f = df_fb[
            df_fb["Wilayah"].isin(f_wil)
            & df_fb["Tipe Usaha"].isin(f_tipe)
            & (df_fb["Harga"] >= f_hrg[0])
            & (df_fb["Harga"] <= f_hrg[1])
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
            m2.metric("👤 Perorangan", fmt_int_id((df_f["Tipe Usaha"] == "Perorangan (Facebook)").sum()))
            m3.metric("🗺️ Jumlah Wilayah", fmt_int_id(df_f["Wilayah"].nunique()))

            if not st.session_state.get("fast_mode") and not df_f.empty:
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    fig = px.pie(df_f, names="Tipe Usaha", hole=0.44,
                                 title="Komposisi Model Bisnis (Facebook)")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    grp = df_f.groupby("Wilayah").size().reset_index(name="Jumlah")
                    fig = px.bar(grp, x="Wilayah", y="Jumlah",
                                 title="Total Usaha per Wilayah (Facebook)",
                                 color="Wilayah")
                    fig.update_layout(paper_bgcolor=BPS_PAPER, plot_bgcolor=BPS_PAPER)
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            df_view = df_f.copy()
            df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {int(x):,}".replace(",", ".") if str(x).isdigit() else f"Rp {x}")
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=420)
            excel_bytes = df_to_excel_bytes({"Data Facebook": df_f})
            st.download_button(
                "⬇️ Unduh Excel — Facebook",
                data=excel_bytes,
                file_name=f"UMKM_Facebook_{datetime.date.today()}.xlsx",
                use_container_width=True,
                type="primary",
            )

        with tab3:
            a = st.session_state.audit_fb or {}
            st.info(f"📂 File diproses: **{fmt_int_id(a.get('file_count', 0))}**")
            st.success(f"✅ Baris valid: **{fmt_int_id(a.get('valid_rows', 0))}**")
            st.warning(f"⚠️ Diabaikan (luar wilayah): **{fmt_int_id(a.get('luar_wilayah', 0))}**")
            st.warning(f"⚠️ Error parsing harga: **{fmt_int_id(a.get('error_harga', 0))}**")


# ======================================================================================
# PAGE: GOOGLE MAPS
# ======================================================================================
elif menu == "🟣 FB Forum":
    section_header("Facebook Forum", "Scraping/olah data dari postingan forum/grup Facebook.", "FORUM")
    banner("Dashboard UMKM — Facebook Forum", "Ekstraksi data UMKM dari Forum/Grup Facebook (Bangka Belitung)")

    with st.container(border=True):
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV FB Forum", type=["csv"], accept_multiple_files=True, key="file_fb_forum")
            run = st.button("🚀 Proses Data FB Forum", type="primary", use_container_width=True)
        with col2:
            st.subheader("🧾 Catatan")
            st.info("• Struktur CSV bisa berbeda-beda (delimiter , / ;). Sistem akan auto-detect.\n• Data difilter hanya Bangka Belitung.")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV FB Forum terlebih dahulu.")
        else:
            with st.status("Memproses data FB Forum…", expanded=True) as status:
                try:
                    total_semua_baris = 0
                    for f in files:
                        total_semua_baris += len(read_csv_smart(f))

                    hasil = []
                    total_baris = 0
                    err_h = 0
                    luar_wilayah = 0

                    progress = st.progress(0)
                    info = st.empty()
                    baris_diproses = 0

                    for file in files:
                        df_raw = read_csv_smart(file)
                        total_baris += len(df_raw)
                        if df_raw is None or df_raw.empty:
                            continue

                        col_toko = _pick_col(df_raw.columns, ["Nama_Penjual", "Nama Penjual", "Nama", "Akun", "Penjual", "Seller"])
                        col_nama = _pick_col(df_raw.columns, ["Nama_Barang", "Nama Barang", "Nama Produk", "Produk", "Judul", "Title"])
                        col_harga = _pick_col(df_raw.columns, ["Harga", "Price"])
                        col_alamat = _pick_col(df_raw.columns, ["Alamat", "Wilayah", "Lokasi"])
                        col_nomor = _pick_col(df_raw.columns, ["Nomor_HP", "Nomor HP", "Nomor", "No HP", "No. HP", "Nomor WA", "WhatsApp"])
                        col_desc = _pick_col(df_raw.columns, ["Deskripsi", "Keterangan", "Description"])
                        col_link = _pick_col(df_raw.columns, ["URL", "Link", "Tautan"])
                        col_foto = _pick_col(df_raw.columns, ["Foto_Profil", "Foto Profil", "Foto", "foto", "Avatar"])

                        if not col_link and len(df_raw.columns) > 0:
                            col_link = df_raw.columns[-1]
                        if not col_harga and len(df_raw.columns) > 0:
                            col_harga = df_raw.columns[min(3, len(df_raw.columns) - 1)]
                        if not col_alamat and len(df_raw.columns) > 0:
                            col_alamat = df_raw.columns[min(2, len(df_raw.columns) - 1)]
                        if not col_nama and len(df_raw.columns) > 0:
                            col_nama = df_raw.columns[min(1, len(df_raw.columns) - 1)]
                        if not col_toko and len(df_raw.columns) > 0:
                            col_toko = df_raw.columns[0]

                        for i in range(len(df_raw)):
                            row = df_raw.iloc[i]

                            toko = clean_placeholder_to_empty(str(row.get(col_toko, ""))) or "FB Seller"
                            nama = clean_placeholder_to_empty(str(row.get(col_nama, "")))
                            harga_str = str(row.get(col_harga, "")) if col_harga else ""
                            alamat = clean_placeholder_to_empty(str(row.get(col_alamat, ""))) if col_alamat else ""
                            nomor = clean_placeholder_to_empty(str(row.get(col_nomor, ""))) if col_nomor else ""
                            deskripsi = clean_placeholder_to_empty(str(row.get(col_desc, ""))) if col_desc else ""
                            link = clean_placeholder_to_empty(str(row.get(col_link, ""))) if col_link else ""
                            foto = clean_placeholder_to_empty(str(row.get(col_foto, ""))) if col_foto else ""

                            wilayah_tag = _infer_wilayah_from_text(alamat) or safe_title(alamat)
                            if not is_in_babel(alamat) and not is_in_babel(wilayah_tag):
                                luar_wilayah += 1
                                baris_diproses += 1
                                continue

                            try:
                                val_h = _parse_price_int_any(harga_str)
                            except Exception:
                                val_h = 0
                                err_h += 1

                            if val_h > 0:
                                tipe_usaha = deteksi_tipe_usaha(toko)
                                hasil.append({
                                    "Nama Toko": toko,
                                    "Nama Produk": nama,
                                    "Harga": val_h,
                                    "Wilayah": wilayah_tag if wilayah_tag else "Bangka Belitung",
                                    "Alamat": alamat if alamat else wilayah_tag,
                                    "Nomor HP": nomor,
                                    "Deskripsi": deskripsi,
                                    "Foto Profil": foto,
                                    "Tipe Usaha": tipe_usaha,
                                    "Link": link
                                })

                            baris_diproses += 1
                            if baris_diproses % 25 == 0 or baris_diproses == total_semua_baris:
                                pct = min(baris_diproses / max(total_semua_baris, 1), 1.0)
                                progress.progress(pct)
                                info.markdown(f"**⏳ Progress:** {fmt_int_id(baris_diproses)} / {fmt_int_id(total_semua_baris)} ({int(pct*100)}%)")

                    progress.empty()
                    info.empty()

                    df_final = pd.DataFrame(hasil).drop_duplicates()
                    st.session_state.data_fb_forum = df_final
                    st.session_state.audit_fb_forum = {
                        "file_count": len(files),
                        "total_rows": total_baris,
                        "valid_rows": len(df_final),
                        "luar_wilayah": luar_wilayah,
                        "error_harga": err_h,
                    }

                    status.update(label="✅ Selesai memproses FB Forum", state="complete", expanded=False)
                    st.toast(f"FB Forum: {fmt_int_id(len(df_final))} baris siap dianalisis", icon="✅")

                except Exception as e:
                    status.update(label="❌ Gagal memproses FB Forum", state="error", expanded=True)
                    st.error(f"Error Sistem FB Forum: {e}")

    df_fb = st.session_state.data_fb_forum
    if df_fb is not None and not df_fb.empty:
        with st.container(border=True):
            st.subheader("🔎 Filter Pintar")
            c1, c2, c3 = st.columns([1.2, 1.2, 1.6], gap="medium")
            with c1:
                f_wil = st.multiselect("📍 Wilayah", options=sorted(df_fb["Wilayah"].unique()),
                                       default=sorted(df_fb["Wilayah"].unique()), key="f_wil_fb_forum")
            with c2:
                f_tipe = st.multiselect("🏢 Tipe Usaha", options=sorted(df_fb["Tipe Usaha"].unique()),
                                        default=sorted(df_fb["Tipe Usaha"].unique()), key="f_tipe_fb_forum")
            with c3:
                q = st.text_input("🔎 Cari (nama toko / produk)", value="", key="q_fb_forum")

            max_h = int(df_fb["Harga"].max()) if df_fb["Harga"].max() > 0 else 1_000_000
            f_hrg = st.slider("💰 Harga (Rp)", 0, max_h, (0, max_h), key="f_hrg_fb_forum")

        df_f = df_fb[
            df_fb["Wilayah"].isin(f_wil)
            & df_fb["Tipe Usaha"].isin(f_tipe)
            & (df_fb["Harga"] >= f_hrg[0])
            & (df_fb["Harga"] <= f_hrg[1])
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
            m2.metric("👤 Perorangan", fmt_int_id((df_f["Tipe Usaha"] == "Perorangan (Facebook)").sum()))
            m3.metric("🏪 Usaha", fmt_int_id((df_f["Tipe Usaha"] != "Perorangan (Facebook)").sum()))

            st.divider()
            colA, colB = st.columns([1.1, 0.9], gap="large")
            with colA:
                st.caption("Top 10 Wilayah")
                st.bar_chart(df_f["Wilayah"].value_counts().head(10))
            with colB:
                st.caption("Distribusi Harga (ringkas)")
                df_hist = df_f[df_f["Harga"] > 0].copy()
                if not df_hist.empty:
                    st.line_chart(df_hist["Harga"].sort_values().reset_index(drop=True).head(200))
                else:
                    st.info("Belum ada harga valid untuk visualisasi.")

        with tab2:
            st.dataframe(df_f, use_container_width=True, height=460)
            st.download_button("⬇️ Unduh CSV (FB Forum Filtered)", data=df_f.to_csv(index=False).encode("utf-8-sig"),
                               file_name="fb_forum_filtered.csv", mime="text/csv", use_container_width=True)

        with tab3:
            audit = st.session_state.audit_fb_forum or {}
            st.json(audit)

    else:
        st.info("📭 Belum ada data FB Forum. Unggah CSV lalu klik proses.")

elif menu == "📍 Google Maps":
    section_header("Google Maps", "Pencarian lokasi & visualisasi peta dengan tampilan modern.", "LOCATION")
    banner("Dashboard UMKM — Google Maps", "Upload CSV hasil ekstensi → auto-clean → REAL MAP (Folium) + export Excel/CSV")

    with st.container(border=True):
        col1, col2 = st.columns([1.15, 0.85], gap="large")
        with col1:
            files = st.file_uploader("Unggah CSV Google Maps", type=["csv"], accept_multiple_files=True, key="file_maps")
            do_clean = st.toggle("✨ Auto-clean (disarankan)", value=True, key="clean_maps")
            run = st.button("🚀 Proses Data Google Maps", type="primary", use_container_width=True)

        with col2:
            st.subheader("🧾 Format Kolom (disarankan)")
            st.code("foto_url, nama_usaha, alamat, no_telepon, latitude, longitude, link", language="text")
            st.caption("Kalau beda nama kolom, sistem tetap coba map otomatis (toleran).")

    if run:
        if not files:
            st.error("⚠️ Silakan unggah file CSV Google Maps terlebih dahulu.")
        else:
            with st.status("Memproses data Google Maps…", expanded=True) as status:
                try:
                    df_raw, total_rows = read_csv_files(files)
                    df_clean, audit = clean_maps_dataframe(df_raw)

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
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📌 Total Data", fmt_int_id(len(df_maps)))
            m2.metric("📍 Koordinat Valid", fmt_int_id(df_maps["Latitude"].notna().sum()))
            m3.metric("🔗 Link Valid", fmt_int_id((df_maps["Link"].astype(str).str.len() > 0).sum()))
            m4.metric("☎️ No Telp Valid", fmt_int_id((df_maps["No Telepon"].astype(str).str.len() > 0).sum()))

            if not st.session_state.get("fast_mode"):
                render_real_map_folium(df_maps, height=560)

        with tab2:
            st.dataframe(df_maps, use_container_width=True, hide_index=True, height=440)

            excel_bytes = df_to_excel_bytes({"Data Google Maps": df_maps})
            st.download_button(
                "⬇️ Unduh Excel — Google Maps (Bersih)",
                data=excel_bytes,
                file_name=f"UMKM_GoogleMaps_Bersih_{datetime.date.today()}.xlsx",
                use_container_width=True,
                type="primary",
            )

            csv_bytes = df_maps.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Unduh CSV — Google Maps (Bersih)",
                data=csv_bytes,
                file_name=f"UMKM_GoogleMaps_Bersih_{datetime.date.today()}.csv",
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
# PAGE: EXPORT MASTER
# ======================================================================================
elif menu == "📊 Export Gabungan":
    section_header("Export Gabungan", "Satukan data lintas platform lalu unduh dalam format rapi.", "EXPORT")
    banner("Export Master Data Gabungan", "Konsolidasi (Shopee, Tokopedia, Facebook Marketplace, FB Forum, Google Maps) → 1 Excel, sheet terpisah")

    df_shp_ready = st.session_state.data_shopee is not None and not st.session_state.data_shopee.empty
    df_tkp_ready = st.session_state.data_tokped is not None and not st.session_state.data_tokped.empty
    df_fb_ready = st.session_state.data_fb is not None and not st.session_state.data_fb.empty
    df_fbf_ready = st.session_state.data_fb_forum is not None and not st.session_state.data_fb_forum.empty
    df_maps_ready = st.session_state.data_maps is not None and not st.session_state.data_maps.empty

    if not (df_shp_ready or df_tkp_ready or df_fb_ready or df_fbf_ready or df_maps_ready):
        st.warning("⚠️ Belum ada data. Silakan proses dulu di menu Shopee/Tokopedia/Facebook/FB Forum/Google Maps.")
    else:
        with st.container(border=True):
            st.subheader("✅ Data Siap Dikonsolidasi")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("📦 Shopee", fmt_int_id(len(st.session_state.data_shopee)) if df_shp_ready else 0)
            c2.metric("📦 Tokopedia", fmt_int_id(len(st.session_state.data_tokped)) if df_tkp_ready else 0)
            c3.metric("📦 Facebook", fmt_int_id(len(st.session_state.data_fb)) if df_fb_ready else 0)
            c4.metric("📦 FB Forum", fmt_int_id(len(st.session_state.data_fb_forum)) if df_fbf_ready else 0)
            c5.metric("📦 Google Maps", fmt_int_id(len(st.session_state.data_maps)) if df_maps_ready else 0)
            st.caption("Output: 1 file Excel berisi sheet terpisah per sumber + autofilter + header rapi.")

        sheets = {}
        if df_shp_ready:
            sheets["Data Shopee"] = st.session_state.data_shopee
        if df_tkp_ready:
            sheets["Data Tokopedia"] = st.session_state.data_tokped
        if df_fb_ready:
            sheets["Data Facebook"] = st.session_state.data_fb
        if df_fbf_ready:
            sheets["Data FB Forum"] = st.session_state.data_fb_forum
        if df_maps_ready:
            sheets["Data Google Maps"] = st.session_state.data_maps

        excel_bytes = df_to_excel_bytes(sheets)

        with st.container(border=True):
            st.subheader("⬇️ Unduh File Master")
            _, col_btn, _ = st.columns([1, 2, 1])
            with col_btn:
                st.download_button(
                    label="⬇️ UNDUH EXCEL MASTER (4-IN-1)",
                    data=excel_bytes,
                    file_name=f"Master_UMKM_BPS_{datetime.date.today()}.xlsx",
                    use_container_width=True,
                    type="primary",
                )


# ======================================================================================
# FOOTER
# ======================================================================================
st.markdown(
    "<div style='margin-top:22px; opacity:.78; font-size:.86rem;'>"
    "Built with Streamlit • Badan Pusat Statistik UMKM Toolkit"
    "</div>",
    unsafe_allow_html=True,
)

# --- FINAL FINAL OVERRIDE (Premium Sunset v3: toned down + vignette) ---
st.markdown(
    """
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"]{
  background:
    radial-gradient(1700px 980px at 7% 12%, rgba(255,140,40,.36) 0%, rgba(255,140,40,.16) 38%, rgba(255,140,40,0) 72%),
    radial-gradient(1500px 980px at 92% 14%, rgba(255,200,90,.22) 0%, rgba(255,200,90,.10) 42%, rgba(255,200,90,0) 78%),
    radial-gradient(1400px 900px at 45% 105%, rgba(255,210,140,.10) 0%, rgba(255,210,140,0) 72%),
    radial-gradient(1200px 820px at 55% 55%, rgba(30,58,138,.10) 0%, rgba(30,58,138,0) 62%),
    linear-gradient(155deg, #1a0f0a 0%, #22110b 20%, #111018 55%, #070a10 100%) !important;
  background-attachment: fixed !important;
}

/* Cinematic vignette to prevent "too bright" look */
[data-testid="stAppViewContainer"]::before{
  content:"";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(1200px 700px at 50% 35%, rgba(0,0,0,0) 0%, rgba(0,0,0,0.28) 60%, rgba(0,0,0,0.52) 100%),
    linear-gradient(180deg, rgba(0,0,0,0.18) 0%, rgba(0,0,0,0.42) 100%);
  mix-blend-mode: multiply;
}

/* Slightly calm the top accent line */
.block-container::before{
  height:5px;
  background: linear-gradient(90deg,
    rgba(255,140,0,0) 0%,
    rgba(255,120,0,.72) 30%,
    rgba(255,200,120,.80) 55%,
    rgba(255,140,0,.72) 75%,
    rgba(255,140,0,0) 100%);
  box-shadow: 0 14px 44px rgba(255,120,0,.26);
}
</style>
""",
    unsafe_allow_html=True,
)


