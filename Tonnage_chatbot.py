import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import tempfile
from stl import mesh
import numpy as np
from io import BytesIO
from fpdf import FPDF
import re
import os

st.set_page_config(
    page_title="SmartCost AI | Bosch",
    page_icon="⚙️",
    layout="wide"
)

# ─────────────────────────────────────────────
# CREDENTIALS
# ─────────────────────────────────────────────
VALID_USERS = {
    "Admin": "SmartCost AI@ Bosch"
}

# ─────────────────────────────────────────────
# GLOBAL CSS (Login + App)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #0f1117; color: #e0e0e0; }

    /* ── Login Page ── */
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    .login-card {
        background: linear-gradient(145deg, #13172a, #1a1f35);
        border: 1px solid #2a3050;
        border-radius: 24px;
        padding: 50px 48px 40px 48px;
        width: 100%;
        max-width: 460px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.6),
                    0 0 0 1px rgba(59,130,246,0.08),
                    inset 0 1px 0 rgba(255,255,255,0.05);
        position: relative;
        overflow: hidden;
    }
    .login-card::before {
        content: '';
        position: absolute;
        top: -60px; left: -60px;
        width: 200px; height: 200px;
        background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .login-card::after {
        content: '';
        position: absolute;
        bottom: -40px; right: -40px;
        width: 160px; height: 160px;
        background: radial-gradient(circle, rgba(167,139,250,0.12) 0%, transparent 70%);
        border-radius: 50%;
    }
    .bosch-bar {
        width: 100%;
        height: 5px;
        background: linear-gradient(90deg, #ea0016, #c8000e, #ea0016);
        border-radius: 3px;
        margin-bottom: 32px;
    }
    .login-logo-area {
        text-align: center;
        margin-bottom: 28px;
    }
    .login-brand {
        font-size: 28px;
        font-weight: 900;
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        line-height: 1.2;
        margin-bottom: 6px;
    }
    .login-tagline {
        font-size: 13px;
        color: #6b7280;
        font-style: italic;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    .login-subtitle {
        font-size: 13px;
        color: #4b5563;
        text-align: center;
        margin-bottom: 28px;
        letter-spacing: 0.3px;
    }
    .login-divider {
        border: none;
        border-top: 1px solid #1e2540;
        margin: 20px 0;
    }
    .login-footer {
        text-align: center;
        margin-top: 28px;
        font-size: 11px;
        color: #374151;
        letter-spacing: 0.3px;
    }
    .bosch-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(234,0,22,0.1);
        border: 1px solid rgba(234,0,22,0.25);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 11px;
        color: #f87171;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .security-note {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(59,130,246,0.06);
        border: 1px solid rgba(59,130,246,0.12);
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 16px;
        font-size: 11px;
        color: #6b7280;
    }
    .error-box {
        background: rgba(239,68,68,0.1);
        border: 1px solid rgba(239,68,68,0.3);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 12px 0;
        color: #fca5a5;
        font-size: 13px;
        text-align: center;
        font-weight: 500;
    }
    .success-box {
        background: rgba(34,197,94,0.1);
        border: 1px solid rgba(34,197,94,0.3);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 12px 0;
        color: #86efac;
        font-size: 13px;
        text-align: center;
        font-weight: 500;
    }

    /* ── Input overrides for login ── */
    .stTextInput > div > div > input {
        background: #0f1525 !important;
        border: 1.5px solid #1e2a45 !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
        transition: border-color 0.2s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    }
    .stTextInput > label {
        color: #8b9cbf !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }

    /* ── Login Button ── */
    .login-btn > button {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 30px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 20px rgba(59,130,246,0.4) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin-top: 8px !important;
    }
    .login-btn > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(59,130,246,0.55) !important;
    }

    /* ── Logout Button ── */
    .logout-btn > button {
        background: linear-gradient(135deg, #7f1d1d, #ef4444) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 6px 16px !important;
        box-shadow: 0 2px 10px rgba(239,68,68,0.3) !important;
    }

    /* ── App CSS (same as original) ── */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2130, #252840);
        border: 1px solid #3a3f5c;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] label {
        color: #8b9cbf !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }
    div[data-testid="metric-container"] div[data-testid="metric-value"] {
        color: #60a5fa !important;
        font-size: 20px !important;
        font-weight: 700 !important;
    }
    .section-header {
        background: linear-gradient(90deg, #1e3a5f, #1e2130);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 12px 20px;
        margin: 20px 0 15px 0;
        font-size: 18px;
        font-weight: 700;
        color: #93c5fd;
        letter-spacing: 0.5px;
    }
    .info-card {
        background: linear-gradient(135deg, #1a2744, #1e2130);
        border: 1px solid #2d4a7a;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 10px 0;
        color: #cbd5e1;
        font-size: 14px;
        line-height: 1.6;
    }
    .result-highlight {
        background: linear-gradient(135deg, #1a3a2a, #1e2130);
        border: 1px solid #22c55e;
        border-radius: 12px;
        padding: 20px 25px;
        margin: 15px 0;
        text-align: center;
        font-size: 22px;
        font-weight: 800;
        color: #4ade80;
        box-shadow: 0 0 20px rgba(34,197,94,0.2);
    }
    .chat-user {
        background: linear-gradient(135deg, #1d4ed8, #2563eb);
        border-radius: 16px 16px 4px 16px;
        padding: 12px 18px;
        margin: 8px 0;
        color: white;
        max-width: 75%;
        margin-left: auto;
        font-size: 14px;
        box-shadow: 0 2px 10px rgba(37,99,235,0.3);
    }
    .chat-bot {
        background: linear-gradient(135deg, #1e2130, #252840);
        border: 1px solid #3a3f5c;
        border-radius: 16px 16px 16px 4px;
        padding: 12px 18px;
        margin: 8px 0;
        color: #cbd5e1;
        max-width: 80%;
        font-size: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    .badge {
        display: inline-block;
        background: #1e3a5f;
        border: 1px solid #3b82f6;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 12px;
        color: #93c5fd;
        margin: 4px 2px;
    }
    .recalc-highlight {
        background: linear-gradient(135deg, #1a3a2a, #1e2130);
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 15px 20px;
        margin: 10px 0;
        color: #4ade80;
        font-size: 14px;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #1e2130;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] { color: #8b9cbf; border-radius: 8px; }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
        color: white !important;
    }
    .custom-divider { border: none; border-top: 1px solid #2d3748; margin: 25px 0; }
    .stSelectbox label, .stNumberInput label, .stCheckbox label {
        color: #8b9cbf !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(59,130,246,0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59,130,246,0.6);
    }
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, #13172a, #1a1f35);
        border-bottom: 1px solid #1e2540;
        border-radius: 0 0 12px 12px;
        padding: 10px 24px;
        margin-bottom: 10px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.3);
    }
    .top-bar-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .top-bar-brand {
        font-size: 18px;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .top-bar-user {
        font-size: 12px;
        color: #6b7280;
        background: rgba(59,130,246,0.08);
        border: 1px solid rgba(59,130,246,0.15);
        border-radius: 20px;
        padding: 4px 12px;
    }
    .bosch-dot {
        width: 10px; height: 10px;
        background: #ea0016;
        border-radius: 50%;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""
if "login_error" not in st.session_state:
    st.session_state["login_error"] = ""
if "login_attempts" not in st.session_state:
    st.session_state["login_attempts"] = 0


# ─────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────
def show_login_page():
    # Centre the card with columns
    _, mid, _ = st.columns([1, 1.6, 1])

    with mid:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # ── Bosch badge
        st.markdown("""
        <div style="text-align:center; margin-bottom:6px;">
            <span class="bosch-badge">
                ● &nbsp; BOSCH INTERNAL TOOL
            </span>
        </div>
        """, unsafe_allow_html=True)

        # ── Brand block
        st.markdown("""
        <div style="text-align:center; margin-bottom:30px;">
            <div class="login-brand">⚙️ SmartCost AI</div>
            <div class="login-tagline">"Design Smart. Cost Instantly."</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Bosch red bar
        st.markdown('<div class="bosch-bar"></div>', unsafe_allow_html=True)

        # ── Subtitle
        st.markdown("""
        <div class="login-subtitle">
            Sheet Metal Costing Intelligence Platform<br>
            <span style="color:#374151; font-size:11px;">
                Authorised Personnel Only
            </span>
        </div>
        """, unsafe_allow_html=True)

        # ── Error / success messages
        if st.session_state["login_error"]:
            st.markdown(
                f'<div class="error-box">⚠️ &nbsp;'
                f'{st.session_state["login_error"]}</div>',
                unsafe_allow_html=True)

        # ── Login form
        with st.form("login_form", clear_on_submit=False):
            st.markdown(
                '<p style="color:#8b9cbf; font-size:11px; '
                'font-weight:600; letter-spacing:0.8px; '
                'margin-bottom:4px;">USER ID</p>',
                unsafe_allow_html=True)
            username = st.text_input(
                "User ID",
                placeholder="Enter your User ID",
                label_visibility="collapsed")

            st.markdown(
                '<p style="color:#8b9cbf; font-size:11px; '
                'font-weight:600; letter-spacing:0.8px; '
                'margin: 14px 0 4px 0;">PASSWORD</p>',
                unsafe_allow_html=True)
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                label_visibility="collapsed")

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown('<div class="login-btn">', unsafe_allow_html=True)
            login_submit = st.form_submit_button(
                "🔐  Sign In to SmartCost AI",
                use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Handle submit
        if login_submit:
            if not username.strip():
                st.session_state["login_error"] = (
                    "User ID cannot be empty.")
                st.rerun()
            elif not password:
                st.session_state["login_error"] = (
                    "Password cannot be empty.")
                st.rerun()
            elif (username in VALID_USERS
                  and VALID_USERS[username] == password):
                st.session_state["authenticated"] = True
                st.session_state["current_user"]  = username
                st.session_state["login_error"]   = ""
                st.session_state["login_attempts"] = 0
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                attempts = st.session_state["login_attempts"]
                if attempts >= 3:
                    st.session_state["login_error"] = (
                        f"Access Denied. {attempts} failed attempt(s). "
                        "Please contact your administrator.")
                else:
                    st.session_state["login_error"] = (
                        f"Invalid User ID or Password. "
                        f"Attempt {attempts} of 3.")
                st.rerun()

        # ── Security note
        st.markdown("""
        <div class="security-note">
            🔒 &nbsp;
            This system is protected. Unauthorised access is prohibited.
            All login attempts are monitored.
        </div>
        """, unsafe_allow_html=True)

        # ── Footer
        st.markdown("""
        <div class="login-footer">
            <div style="margin-bottom:6px;">
                <span style="color:#ea0016; font-weight:700;">BOSCH</span>
                &nbsp;|&nbsp; SmartCost AI v1.0
                &nbsp;|&nbsp; Sheet Metal Division
            </div>
            <div>© 2024 Robert Bosch GmbH. All rights reserved.</div>
            <div style="margin-top:6px; font-size:10px; color:#1f2937;">
                For access issues contact: smartcost-support@bosch.com
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TOP BAR (shown when logged in)
# ─────────────────────────────────────────────
def show_top_bar():
    col_brand, col_right = st.columns([6, 1])
    with col_brand:
        st.markdown(f"""
        <div class="top-bar">
            <div class="top-bar-left">
                <span style="font-size:20px;">⚙️</span>
                <span class="top-bar-brand">SmartCost AI</span>
                <span style="color:#374151; font-size:11px;">|</span>
                <span style="color:#6b7280; font-size:12px;">
                    Sheet Metal Costing Platform
                </span>
                <span class="bosch-dot"></span>
                <span style="color:#f87171; font-size:11px; font-weight:600;">
                    BOSCH
                </span>
            </div>
            <div>
                <span class="top-bar-user">
                    👤 &nbsp;{st.session_state['current_user']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("⏻  Logout", key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CLEAN TEXT FOR PDF
# ─────────────────────────────────────────────
def clean(text):
    replacements = {
        "\u2014": "-", "\u2013": "-", "\u20ac": "EUR", "\u00b5": "u",
        "\u00b2": "2", "\u00b3": "3", "\u2192": "->", "\u2190": "<-",
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2022": "*", "\u00d7": "x", "\u00f7": "/", "\u00b0": " deg",
        "\u03bc": "u", "\u2264": "<=", "\u2265": ">=", "\u00e9": "e",
        "\u00e8": "e", "\u00ea": "e", "\u00e0": "a", "\u00e2": "a",
        "\u00fc": "u", "\u00f6": "o", "\u00e4": "a", "\u00df": "ss",
    }
    for char, replacement in replacements.items():
        text = str(text).replace(char, replacement)
    return text.encode("ascii", errors="ignore").decode("ascii")


# ─────────────────────────────────────────────
# CORE CALCULATION FUNCTION
# ─────────────────────────────────────────────
def run_calculation(params):
    p = params
    density_db = {
        "CR Steel": 7850, "SS304": 8000, "SS430": 7700,
        "Aluminium": 2700, "Copper": 8960
    }
    shear_db = {
        "CR Steel": 250, "SS304": 300, "SS430": 275,
        "Aluminium": 110, "Copper": 210
    }
    coating_density_db = {
        "Zinc": 7140, "Nickel": 8900, "Tin": 7310,
        "Silver": 10490, "Gold": 19300
    }
    coating_rate_db = {
        "Zinc": 3, "Nickel": 12, "Tin": 25,
        "Silver": 800, "Gold": 60000
    }
    material_rate_db = {
        "CR Steel": 0.9, "SS304": 2.5, "SS430": 1.8,
        "Aluminium": 3.0, "Copper": 11.2
    }

    density        = density_db[p["material"]]
    shear_strength = shear_db[p["material"]]

    perimeter       = ((2 * p["length"]) + (2 * p["width"])) * 0.7
    cutting_force   = perimeter * p["thickness"] * shear_strength
    fos             = cutting_force * 0.5
    stripping_force = cutting_force * 0.4
    total_force     = cutting_force + fos + stripping_force
    tonnage         = total_force / (1000 * 9.81)

    carriage_allowance  = 5
    stripping_allowance = 3
    pitch               = 2 * p["thickness"]
    strip_width         = p["width"] + (2 * carriage_allowance) + (2 * stripping_allowance)
    strip_length        = (2 * p["length"]) + pitch
    deployed_length     = p["length"] + pitch
    strip_area          = strip_width * deployed_length
    volume_mm3          = strip_area * p["thickness"]
    volume_m3           = volume_mm3 / 1e9
    deployed_weight     = volume_m3 * density
    net_weight          = p["net_weight"]
    scrap_weight        = deployed_weight - net_weight
    scrap_percent       = (scrap_weight / deployed_weight) * 100 if deployed_weight > 0 else 0
    part_area           = p["length"] * p["width"]
    strip_area_layout   = strip_length * strip_width
    utilization         = (2 * part_area / strip_area_layout) * 100
    surface_area_used   = p["surface_area"]

    def calc_coating(coat_type, microns, surface_mm2):
        if coat_type == "None" or surface_mm2 is None or microns == 0:
            return 0.0, 0.0
        t_m      = microns * 1e-6
        area_m2  = surface_mm2 / 1e6
        vol      = area_m2 * t_m
        c_weight = vol * coating_density_db[coat_type]
        c_cost   = c_weight * coating_rate_db[coat_type]
        return c_weight, c_cost

    base_w,  base_cost       = calc_coating(p["base_coating_type"],  p["base_coating_micron"],  surface_area_used)
    final_w, final_cost_coat = calc_coating(p["final_coating_type"], p["final_coating_micron"], surface_area_used)
    total_coating_cost       = base_cost + final_cost_coat

    material_rate       = p.get("material_rate_override", material_rate_db[p["material"]])
    material_cost       = deployed_weight * material_rate
    moh                 = material_cost * 0.05
    interest            = material_cost * (0.12 / 365) * 15
    total_material_cost = material_cost + moh + interest + total_coating_cost

    stamping_mhr    = p.get("stamping_mhr", 18)
    stamping_speed  = p.get("stamping_speed", 100)
    stamping_labour = p.get("stamping_labour_pct", 25) / 100
    stamping_rmoh   = p.get("stamping_rmoh_pct", 7) / 100
    stamping_base   = (60 / stamping_speed) / 3600 * stamping_mhr
    setup           = (2 * stamping_mhr) / 100_000
    tool            = 0.003
    stamping        = stamping_base + setup + tool
    stamping_total  = stamping + stamping * stamping_labour + stamping * stamping_rmoh

    coating_mhr        = p.get("coating_mhr", 130)
    coating_speed      = p.get("coating_speed", 1600)
    coating_labour     = p.get("coating_labour_pct", 100) / 100
    coating_rmoh       = p.get("coating_rmoh_pct", 10) / 100
    coating_proc       = (60 / coating_speed) / 3600 * coating_mhr
    coating_proc_total = coating_proc + coating_proc * coating_labour + coating_proc * coating_rmoh

    insp_mhr         = p.get("insp_mhr", 0.5)
    insp_labour      = p.get("insp_labour_pct", 100) / 100
    insp_rmoh        = p.get("insp_rmoh_pct", 8) / 100
    insp             = (120 / 180_000) / 3600 * insp_mhr
    inspection_total = insp + insp * insp_labour + insp * insp_rmoh

    manufacturing_cost = stamping_total + coating_proc_total + inspection_total

    sga_pct             = p.get("sga_pct", 10) / 100
    profit_pct          = p.get("profit_pct", 5) / 100
    subtotal            = total_material_cost + manufacturing_cost
    sga                 = subtotal * sga_pct
    profit_amt          = subtotal * profit_pct
    final_cost_per_part = subtotal + sga + profit_amt
    annual_total        = final_cost_per_part * p["annual_volume"]

    return {
        "tonnage":             tonnage,
        "deployed_weight_g":   deployed_weight * 1000,
        "net_weight_g":        net_weight * 1000,
        "scrap_percent":       scrap_percent,
        "utilization":         utilization,
        "material":            p["material"],
        "material_rate":       material_rate,
        "material_cost":       material_cost,
        "moh":                 moh,
        "interest":            interest,
        "base_coat":           p["base_coating_type"],
        "base_coat_micron":    p["base_coating_micron"],
        "base_coat_cost":      base_cost,
        "final_coat":          p["final_coating_type"],
        "final_coat_micron":   p["final_coating_micron"],
        "final_coat_cost":     final_cost_coat,
        "total_coating_cost":  total_coating_cost,
        "stamping_cost":       stamping_total,
        "coating_proc_cost":   coating_proc_total,
        "inspection_cost":     inspection_total,
        "manufacturing_cost":  manufacturing_cost,
        "subtotal":            subtotal,
        "sga":                 sga,
        "profit":              profit_amt,
        "final_cost_per_part": final_cost_per_part,
        "annual_volume":       p["annual_volume"],
        "lots_per_year":       p["lots_per_year"],
        "lot_size":            p["lot_size"],
        "annual_total":        annual_total,
        "region":              p["region"],
        "length":              p["length"],
        "width":               p["width"],
        "thickness":           p["thickness"],
        "pitch":               pitch,
        "strip_width":         strip_width,
        "strip_length":        strip_length,
        "surface_area_mm2":    surface_area_used,
        "stl_loaded":          p.get("stl_loaded", False),
        "carriage_allowance":  carriage_allowance,
        "stripping_allowance": stripping_allowance,
        "stamping_mhr":        stamping_mhr,
        "coating_mhr":         coating_mhr,
        "insp_mhr":            insp_mhr,
        "stamping_labour_pct": p.get("stamping_labour_pct", 25),
        "coating_labour_pct":  p.get("coating_labour_pct", 100),
        "insp_labour_pct":     p.get("insp_labour_pct", 100),
        "sga_pct":             p.get("sga_pct", 10),
        "profit_pct":          p.get("profit_pct", 5),
    }


# ─────────────────────────────────────────────
# PDF CLASS
# ─────────────────────────────────────────────
class CostingPDF(FPDF):
    def header(self):
        self.set_fill_color(29, 78, 216)
        self.rect(0, 0, 210, 22, "F")
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(255, 255, 255)
        self.set_y(6)
        self.cell(0, 10, "AI Sheet Metal Costing Report", align="C")
        self.set_text_color(0, 0, 0)
        self.ln(18)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10,
                  clean(f"Page {self.page_no()} - SmartCost AI | Bosch"),
                  align="C")

    def section_title(self, txt):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(219, 234, 254)
        self.set_text_color(29, 78, 216)
        self.cell(0, 8, clean(txt), ln=True, fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def two_col_table(self, rows):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(29, 78, 216)
        self.set_text_color(255, 255, 255)
        self.cell(95, 7, "Parameter", border=1, fill=True)
        self.cell(90, 7, "Value",     border=1, fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        for i, (lbl, val) in enumerate(rows):
            if i % 2 == 0:
                self.set_fill_color(240, 244, 255)
            else:
                self.set_fill_color(255, 255, 255)
            self.set_font("Helvetica", "", 9)
            self.cell(95, 6, clean(str(lbl)), border=1, fill=True)
            self.set_font("Helvetica", "B", 9)
            self.cell(90, 6, clean(str(val)), border=1, fill=True, ln=True)
        self.ln(3)


# ─────────────────────────────────────────────
# GENERATE PDF
# ─────────────────────────────────────────────
def generate_pdf_report(r):
    pdf = CostingPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5,
             clean("Generated by SmartCost AI | Bosch Sheet Metal Division"),
             align="C", ln=True)
    pdf.ln(3)

    pdf.section_title("  Part and Commercial Details")
    pdf.two_col_table([
        ("Region",          r["region"]),
        ("Material",        r["material"]),
        ("Part Length",     f"{r['length']:.2f} mm"),
        ("Part Width",      f"{r['width']:.2f} mm"),
        ("Thickness",       f"{r['thickness']:.2f} mm"),
        ("Annual Volume",   f"{int(r['annual_volume']):,} pcs"),
        ("Lots per Year",   f"{int(r['lots_per_year'])}"),
        ("Lot Size",        f"{int(r['lot_size']):,} pcs/lot"),
        ("Surface Area",    f"{r['surface_area_mm2']:.2f} mm2"),
        ("STL Model Used",  "Yes" if r["stl_loaded"] else "No"),
    ])

    pdf.section_title("  Press and Strip Results")
    pdf.two_col_table([
        ("Press Tonnage",        f"{r['tonnage']:.2f} T"),
        ("Deployed Weight",      f"{r['deployed_weight_g']:.2f} g"),
        ("Net Part Weight",      f"{r['net_weight_g']:.2f} g"),
        ("Scrap Percentage",     f"{r['scrap_percent']:.2f} %"),
        ("Material Utilization", f"{r['utilization']:.2f} %"),
        ("Pitch",                f"{r['pitch']:.2f} mm"),
        ("Strip Width",          f"{r['strip_width']:.2f} mm"),
        ("Strip Length",         f"{r['strip_length']:.2f} mm"),
    ])

    pdf.section_title("  Material Cost")
    pdf.two_col_table([
        ("Material Rate",        f"{r['material_rate']:.2f} EUR/kg"),
        ("Material Cost",        f"{r['material_cost']:.4f} EUR"),
        ("MOH 5%",               f"{r['moh']:.4f} EUR"),
        ("Inventory Interest",   f"{r['interest']:.4f} EUR"),
        ("Base Coating Type",    str(r["base_coat"])),
        ("Base Coat Thickness",  f"{r['base_coat_micron']:.1f} microns"),
        ("Base Coat Cost",       f"{r['base_coat_cost']:.5f} EUR"),
        ("Final Coating Type",   str(r["final_coat"])),
        ("Final Coat Thickness", f"{r['final_coat_micron']:.1f} microns"),
        ("Final Coat Cost",      f"{r['final_coat_cost']:.5f} EUR"),
        ("Total Coating Cost",   f"{r['total_coating_cost']:.5f} EUR"),
    ])

    pdf.section_title("  Manufacturing Cost")
    pdf.two_col_table([
        ("Stamping",             f"{r['stamping_cost']:.6f} EUR"),
        ("Coating Process",      f"{r['coating_proc_cost']:.6f} EUR"),
        ("Inspection / Packing", f"{r['inspection_cost']:.6f} EUR"),
        ("Total Mfg Cost",       f"{r['manufacturing_cost']:.6f} EUR"),
    ])

    pdf.section_title("  Machine and Rate Parameters")
    pdf.two_col_table([
        ("Stamping MHR",        f"{r['stamping_mhr']} EUR/hr"),
        ("Stamping Labour %",   f"{r['stamping_labour_pct']}%"),
        ("Coating MHR",         f"{r['coating_mhr']} EUR/hr"),
        ("Coating Labour %",    f"{r['coating_labour_pct']}%"),
        ("Inspection MHR",      f"{r['insp_mhr']} EUR/hr"),
        ("Inspection Labour %", f"{r['insp_labour_pct']}%"),
        ("SGA %",               f"{r['sga_pct']}%"),
        ("Profit %",            f"{r['profit_pct']}%"),
    ])

    pdf.section_title("  Final Costing Summary")
    pdf.two_col_table([
        ("Subtotal",     f"{r['subtotal']:.4f} EUR"),
        ("SGA Amount",   f"{r['sga']:.4f} EUR"),
        ("Profit Amount",f"{r['profit']:.4f} EUR"),
        ("Cost per Part",f"{r['final_cost_per_part']:.4f} EUR"),
        ("Annual Total", f"{r['annual_total']:,.2f} EUR"),
    ])

    # Strip chart
    try:
        lx = r["length"]; wx = r["width"]
        px = r["pitch"];  sw = r["strip_width"]; sl = r["strip_length"]
        ca = r["carriage_allowance"]; sa = r["stripping_allowance"]
        py_val = ca + sa

        fig, ax = plt.subplots(figsize=(10, 4), dpi=100, facecolor="white")
        ax.set_facecolor("white")
        ax.add_patch(plt.Rectangle((0, 0), sl, sw, fill=False,
                                   linewidth=2, edgecolor="#1d4ed8"))
        ax.add_patch(plt.Rectangle((0, 0), sl, ca,
                                   color="#f59e0b", alpha=0.6, label="Carriage"))
        ax.add_patch(plt.Rectangle((0, sw - ca), sl, ca,
                                   color="#f59e0b", alpha=0.6))
        ax.add_patch(plt.Rectangle((0, ca), sl, sa,
                                   color="#9ca3af", alpha=0.6, label="Stripping"))
        ax.add_patch(plt.Rectangle((0, sw - ca - sa), sl, sa,
                                   color="#9ca3af", alpha=0.6))
        ax.add_patch(plt.Rectangle((0, py_val), lx, wx,
                                   fill=True, facecolor="#dbeafe",
                                   edgecolor="#1d4ed8", linewidth=2, label="Part"))
        ax.add_patch(plt.Rectangle((lx + px, py_val), lx, wx,
                                   fill=True, facecolor="#dbeafe",
                                   edgecolor="#1d4ed8", linewidth=2))
        arr = dict(arrowstyle="<->", color="#374151", lw=1.5)
        txk = dict(color="#111827", fontsize=9, ha="center", fontweight="bold")
        ax.annotate("", xy=(0, py_val - 4),
                    xytext=(lx, py_val - 4), arrowprops=arr)
        ax.text(lx / 2, py_val - 8, f"Length = {lx} mm", **txk)
        ax.annotate("", xy=(lx, py_val - 13),
                    xytext=(lx + px, py_val - 13), arrowprops=arr)
        ax.text(lx + px / 2, py_val - 17, f"Pitch = {px} mm", **txk)
        ax.annotate("", xy=(sl + 3, 0),
                    xytext=(sl + 3, sw), arrowprops=arr)
        ax.text(sl + 6, sw / 2, f"Strip W\n{sw}mm",
                color="#111827", fontsize=8,
                ha="left", va="center", fontweight="bold")
        ax.annotate("", xy=(0, sw + 4),
                    xytext=(sl, sw + 4), arrowprops=arr)
        ax.text(sl / 2, sw + 8, f"Strip Length = {sl} mm", **txk)
        ax.legend(loc="upper right", fontsize=8)
        ax.set_xlim(-5, sl + 30)
        ax.set_ylim(-25, sw + 15)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title("Strip Layout Diagram",
                     fontsize=12, fontweight="bold", color="#1d4ed8")

        with tempfile.NamedTemporaryFile(
                delete=False, suffix=".png") as tmp_img:
            tmp_img_path = tmp_img.name
            fig.savefig(tmp_img_path, dpi=100,
                        bbox_inches="tight", facecolor="white")
            plt.close(fig)

        pdf.add_page()
        pdf.section_title("  Strip Layout Diagram")
        pdf.ln(3)
        img_w = 170
        img_x = (210 - img_w) / 2
        pdf.image(tmp_img_path, x=img_x, y=None, w=img_w)
        try:
            os.remove(tmp_img_path)
        except Exception:
            pass
    except Exception as chart_err:
        pdf.add_page()
        pdf.section_title("  Strip Layout")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, clean(f"Chart error: {chart_err}"), ln=True)

    return bytes(pdf.output())


# ─────────────────────────────────────────────
# GENERATE EXCEL
# ─────────────────────────────────────────────
def generate_excel_report(r):
    buffer = BytesIO()
    sections = {
        "Part and Commercial": [
            ("Region",             r["region"]),
            ("Material",           r["material"]),
            ("Part Length (mm)",   r["length"]),
            ("Part Width (mm)",    r["width"]),
            ("Thickness (mm)",     r["thickness"]),
            ("Annual Volume",      int(r["annual_volume"])),
            ("Lots per Year",      int(r["lots_per_year"])),
            ("Lot Size",           int(r["lot_size"])),
            ("Surface Area mm2",   r["surface_area_mm2"]),
            ("STL Loaded",         "Yes" if r["stl_loaded"] else "No"),
        ],
        "Press and Strip": [
            ("Tonnage (T)",        r["tonnage"]),
            ("Deployed Weight (g)",r["deployed_weight_g"]),
            ("Net Weight (g)",     r["net_weight_g"]),
            ("Scrap %",            r["scrap_percent"]),
            ("Utilization %",      r["utilization"]),
            ("Pitch (mm)",         r["pitch"]),
            ("Strip Width (mm)",   r["strip_width"]),
            ("Strip Length (mm)",  r["strip_length"]),
        ],
        "Material Cost": [
            ("Material Rate EUR/kg", r["material_rate"]),
            ("Material Cost EUR",    r["material_cost"]),
            ("MOH 5% EUR",           r["moh"]),
            ("Inv. Interest EUR",    r["interest"]),
            ("Base Coat",            r["base_coat"]),
            ("Base Coat Cost EUR",   r["base_coat_cost"]),
            ("Final Coat",           r["final_coat"]),
            ("Final Coat Cost EUR",  r["final_coat_cost"]),
            ("Total Coating EUR",    r["total_coating_cost"]),
        ],
        "Manufacturing": [
            ("Stamping EUR",         r["stamping_cost"]),
            ("Stamping MHR",         r["stamping_mhr"]),
            ("Stamping Labour %",    r["stamping_labour_pct"]),
            ("Coating Process EUR",  r["coating_proc_cost"]),
            ("Coating MHR",          r["coating_mhr"]),
            ("Coating Labour %",     r["coating_labour_pct"]),
            ("Inspection EUR",       r["inspection_cost"]),
            ("Inspection MHR",       r["insp_mhr"]),
            ("Inspection Labour %",  r["insp_labour_pct"]),
            ("Total Mfg EUR",        r["manufacturing_cost"]),
        ],
        "Final Cost": [
            ("Subtotal EUR",         r["subtotal"]),
            ("SGA % Used",           r["sga_pct"]),
            ("SGA EUR",              r["sga"]),
            ("Profit % Used",        r["profit_pct"]),
            ("Profit EUR",           r["profit"]),
            ("Cost per Part EUR",    r["final_cost_per_part"]),
            ("Annual Total EUR",     r["annual_total"]),
        ],
    }

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        wb = writer.book
        hdr_fmt = wb.add_format({
            "bold": True, "bg_color": "#1d4ed8",
            "font_color": "#ffffff", "border": 1, "font_size": 11})
        lbl_fmt = wb.add_format({
            "bold": True, "bg_color": "#dbeafe",
            "border": 1, "font_size": 10})
        val_fmt = wb.add_format({"border": 1, "font_size": 10})
        num_fmt = wb.add_format({
            "border": 1, "font_size": 10, "num_format": "0.000000"})
        title_fmt = wb.add_format({
            "bold": True, "font_size": 16, "font_color": "#1d4ed8"})
        sub_fmt = wb.add_format({
            "italic": True, "font_size": 10, "font_color": "#6b7280"})

        ws = wb.add_worksheet("Full Report")
        ws.set_column("A:A", 32)
        ws.set_column("B:B", 24)
        ws.write("A1", "SmartCost AI | Sheet Metal Costing Report", title_fmt)
        ws.write("A2", "Bosch Sheet Metal Division", sub_fmt)
        row = 3
        for section_name, rows in sections.items():
            ws.merge_range(row, 0, row, 1, f"  {section_name}", hdr_fmt)
            row += 1
            for lbl, val in rows:
                ws.write(row, 0, lbl, lbl_fmt)
                if isinstance(val, (int, float)):
                    ws.write(row, 1, val, num_fmt)
                else:
                    ws.write(row, 1, val, val_fmt)
                row += 1
            row += 1

        for section_name, rows in sections.items():
            ws2 = wb.add_worksheet(section_name[:31])
            ws2.set_column("A:A", 32)
            ws2.set_column("B:B", 24)
            ws2.merge_range(0, 0, 0, 1, section_name, hdr_fmt)
            for i, (lbl, val) in enumerate(rows, start=1):
                ws2.write(i, 0, lbl, lbl_fmt)
                if isinstance(val, (int, float)):
                    ws2.write(i, 1, val, num_fmt)
                else:
                    ws2.write(i, 1, val, val_fmt)

    buffer.seek(0)
    return buffer


# ─────────────────────────────────────────────
# GENERATE CSV
# ─────────────────────────────────────────────
def generate_csv_report(r):
    rows = [
        ("Material",             r["material"]),
        ("Region",               r["region"]),
        ("Length (mm)",          r["length"]),
        ("Width (mm)",           r["width"]),
        ("Thickness (mm)",       r["thickness"]),
        ("Annual Volume",        int(r["annual_volume"])),
        ("Lots/Year",            int(r["lots_per_year"])),
        ("Lot Size",             int(r["lot_size"])),
        ("Surface Area mm2",     r["surface_area_mm2"]),
        ("Tonnage (T)",          r["tonnage"]),
        ("Deployed Weight (g)",  r["deployed_weight_g"]),
        ("Net Weight (g)",       r["net_weight_g"]),
        ("Scrap %",              r["scrap_percent"]),
        ("Utilization %",        r["utilization"]),
        ("Material Rate EUR/kg", r["material_rate"]),
        ("Material Cost EUR",    r["material_cost"]),
        ("MOH EUR",              r["moh"]),
        ("Interest EUR",         r["interest"]),
        ("Base Coat",            r["base_coat"]),
        ("Base Coat Cost EUR",   r["base_coat_cost"]),
        ("Final Coat",           r["final_coat"]),
        ("Final Coat Cost EUR",  r["final_coat_cost"]),
        ("Total Coating EUR",    r["total_coating_cost"]),
        ("Stamping EUR",         r["stamping_cost"]),
        ("Stamping MHR",         r["stamping_mhr"]),
        ("Stamping Labour %",    r["stamping_labour_pct"]),
        ("Coating Process EUR",  r["coating_proc_cost"]),
        ("Coating MHR",         r["coating_mhr"]),
        ("Coating Labour %",     r["coating_labour_pct"]),
        ("Inspection EUR",       r["inspection_cost"]),
        ("Inspection MHR",       r["insp_mhr"]),
        ("Inspection Labour %",  r["insp_labour_pct"]),
        ("Manufacturing EUR",    r["manufacturing_cost"]),
        ("SGA %",                r["sga_pct"]),
        ("SGA EUR",              r["sga"]),
        ("Profit %",             r["profit_pct"]),
        ("Profit EUR",           r["profit"]),
        ("Cost per Part EUR",    r["final_cost_per_part"]),
        ("Annual Total EUR",     r["annual_total"]),
    ]
    df = pd.DataFrame(rows, columns=["Parameter", "Value"])
    return df.to_csv(index=False).encode("utf-8")


# ─────────────────────────────────────────────
# CHATBOT ANSWER ENGINE
# ─────────────────────────────────────────────
def answer_query(q: str, r: dict, params: dict):
    q_lower    = q.lower().strip()
    new_params = None
    reply      = ""

    def extract_number(text):
        nums = re.findall(r"[-+]?\d*\.?\d+", text)
        return float(nums[0]) if nums else None

    def is_set_command(text):
        return any(k in text for k in
                   ["set", "change", "update", "modify",
                    "to", "make it", "use"])

    if any(k in q_lower for k in ["material rate", "raw material",
                                   "material cost per kg", "material price",
                                   "eur/kg", "cost per kg"]):
        val = extract_number(q)
        if val and is_set_command(q_lower):
            new_params = dict(params)
            new_params["material_rate_override"] = val
            reply = (f"Material rate updated to {val} EUR/kg\n\n"
                     f"Previous: {r['material_rate']:.2f} EUR/kg"
                     f" -> New: {val} EUR/kg\nRecalculating...")
        else:
            reply = (f"Current Material Rate: {r['material_rate']:.2f} EUR/kg\n\n"
                     f"To change: say 'Set material rate to 3.5'")

    elif any(k in q_lower for k in ["stamping mhr", "stamping machine hour",
                                     "stamping rate", "press mhr",
                                     "press machine rate"]):
        val = extract_number(q)
        if val and is_set_command(q_lower):
            new_params = dict(params)
            new_params["stamping_mhr"] = val
            reply = (f"Stamping MHR updated to {val} EUR/hr\n\n"
                     f"Previous: {r['stamping_mhr']} EUR/hr"
                     f" -> New: {val} EUR/hr\nRecalculating...")
        else:
            reply = (f"Current Stamping MHR: {r['stamping_mhr']} EUR/hr\n\n"
                     f"To change: say 'Set stamping MHR to 25'")

    elif any(k in q_lower for k in ["coating mhr", "coating machine",
                                     "plating mhr", "coating rate",
                                     "plating rate"]):
        val = extract_number(q)
        if val and is_set_command(q_lower):
            new_params = dict(params)
            new_params["coating_mhr"] = val
            reply = (f"Coating MHR updated to {val} EUR/hr\n\n"
                     f"Previous: {r['coating_mhr']} EUR/hr"
                     f" -> New: {val} EUR/hr\nRecalculating...")
        else:
            reply = (f"Current Coating MHR: {r['coating_mhr']} EUR/hr\n\n"
                     f"To change: say 'Set coating MHR to 150'")

    elif any(k in q_lower for k in ["inspection mhr", "inspection rate",
                                     "insp mhr", "packing mhr",
                                     "inspection machine"]):
        val = extract_number(q)
        if val and is_set_command(q_lower):
            new_params = dict(params)
            new_params["insp_mhr"] = val
            reply = (f"Inspection MHR updated to {val} EUR/hr\n\n"
                     f"Previous: {r['insp_mhr']} EUR/hr"
                     f" -> New: {val} EUR/hr\nRecalculating...")
        else:
            reply = (f"Current Inspection MHR: {r['insp_mhr']} EUR/hr\n\n"
                     f"To change: say 'Set inspection MHR to 1.5'")

    elif any(k in q_lower for k in ["stamping labour", "stamping labor",
                                     "press labour", "press labor"]):
        val = extract_number(q)
        if val and is_set_command(q_lower):
            new_params = dict(params)
            new_params["stamping_labour_pct"] = val
            reply = (f"Stamping Labour updated to {val}%\n\n"
                     f"Previous: {r['stamping_labour_pct']}%"
                     f" -> New: {val}%\nRecalculating...")
        else:
            reply = (f"Current Stamping Labour: {r['stamping_labour_pct']}%\n\n"
                     f"To change: say 'Set stamping labour to 30'")

    elif any(k in q_lower for k in ["coating labour", "coating labor",
                                     "plating labour", "plating labor"]):
        val = extract_number(q)
        if val and is_set_command(q_lower):
            new_params = dict(params)
            new_params["coating_labour_pct"] = val
            reply = (f"Coating Labour updated to {val}%\n\n"
                     f"Previous: {r['coating_labour_pct']}%"
                     f" -> New: {val}%\nRecalculating...")
        else:
            reply = (f"Current Coating Labour: {r['coating_labour_pct']}%\n\n"
                     f"To change: say 'Set coating labour to 80'")

    elif any(k in q_lower for k in ["inspection labour", "inspection labor",
                                     "insp labour", "insp labor"]):
        val = extract_number(q)
        if val and is_set_command(q_lower):
            new_params = dict(params)
            new_params["insp_labour_pct"] = val
            reply = (f"Inspection Labour updated to {val}%\n\n"
                     f"Previous: {r['insp_labour_pct']}%"
                     f" -> New: {val}%\nRecalculating...")
        else:
            reply = (f"Current Inspection Labour: {r['insp_labour_pct']}%\n\n"
                     f"To change: say 'Set inspection labour to 80'")

    elif any(k in q_lower for k in ["sga", "sg&a", "selling",
                                     "general admin", "overhead"]):
        val = extract_number(q)
        if val and is_set_command(q_lower):
            new_params = dict(params)
            new_params["sga_pct"] = val
            reply = (f"SGA updated to {val}%\n\n"
                     f"Previous: {r['sga_pct']}%"
                     f" -> New: {val}%\nRecalculating...")
        else:
            reply = (f"Current SGA: {r['sga_pct']}% -> {r['sga']:.4f} EUR\n\n"
                     f"To change: say 'Set SGA to 12'")

    elif any(k in q_lower for k in ["profit", "margin"]):
        val = extract_number(q)
        if val and is_set_command(q_lower):
            new_params = dict(params)
            new_params["profit_pct"] = val
            reply = (f"Profit % updated to {val}%\n\n"
                     f"Previous: {r['profit_pct']}%"
                     f" -> New: {val}%\nRecalculating...")
        else:
            reply = (f"Current Profit: {r['profit_pct']}%"
                     f" -> {r['profit']:.4f} EUR\n\n"
                     f"To change: say 'Set profit to 8'")

    elif any(k in q_lower for k in ["tonnage", "ton",
                                     "press force", "force"]):
        reply = (f"Press Tonnage: {r['tonnage']:.2f} T\n\n"
                 f"- Perimeter x Thickness x Shear Strength -> Cutting Force\n"
                 f"- FOS = 50% | Stripping = 40% of Cutting Force\n"
                 f"- Total Force / (1000 x 9.81)")

    elif any(k in q_lower for k in ["material cost", "raw material cost"]):
        reply = (f"Material Cost: {r['material_cost']:.4f} EUR\n\n"
                 f"- {r['material']} @ {r['material_rate']:.2f} EUR/kg\n"
                 f"- Deployed Weight: {r['deployed_weight_g']:.2f} g\n"
                 f"- MOH: {r['moh']:.4f} EUR | Interest: {r['interest']:.4f} EUR\n\n"
                 f"To change rate: say 'Set material rate to 3.5'")

    elif any(k in q_lower for k in ["coat", "plating", "zinc",
                                     "nickel", "tin", "silver", "gold"]):
        if r["base_coat"] == "None" and r["final_coat"] == "None":
            reply = "No coating selected in this calculation."
        else:
            msg = "Coating Details:\n\n"
            if r["base_coat"] != "None":
                msg += (f"- Base: {r['base_coat']}"
                        f" @ {r['base_coat_micron']} microns"
                        f" -> {r['base_coat_cost']:.5f} EUR\n")
            if r["final_coat"] != "None":
                msg += (f"- Final: {r['final_coat']}"
                        f" @ {r['final_coat_micron']} microns"
                        f" -> {r['final_coat_cost']:.5f} EUR\n")
            msg += f"- Total: {r['total_coating_cost']:.5f} EUR"
            reply = msg

    elif any(k in q_lower for k in ["scrap", "waste", "utilization"]):
        reply = (f"Scrap and Utilization:\n\n"
                 f"- Deployed: {r['deployed_weight_g']:.2f} g"
                 f" | Net: {r['net_weight_g']:.2f} g\n"
                 f"- Scrap: {r['deployed_weight_g']-r['net_weight_g']:.2f} g"
                 f" | Scrap %: {r['scrap_percent']:.2f}%\n"
                 f"- Material Utilization: {r['utilization']:.2f}%")

    elif any(k in q_lower for k in ["strip", "layout", "pitch"]):
        reply = (f"Strip Layout:\n\n"
                 f"- Part: {r['length']} x {r['width']} mm"
                 f" | Thickness: {r['thickness']} mm\n"
                 f"- Pitch: {r['pitch']:.2f} mm\n"
                 f"- Strip Width: {r['strip_width']:.2f} mm\n"
                 f"- Strip Length: {r['strip_length']:.2f} mm")

    elif any(k in q_lower for k in ["manufactur", "stamp cost",
                                     "process cost", "machine cost"]):
        reply = (f"Manufacturing Cost: {r['manufacturing_cost']:.6f} EUR\n\n"
                 f"- Stamping: {r['stamping_cost']:.6f} EUR\n"
                 f"- Coating Process: {r['coating_proc_cost']:.6f} EUR\n"
                 f"- Inspection: {r['inspection_cost']:.6f} EUR\n\n"
                 f"To modify: say 'Set stamping MHR to 25'")

    elif any(k in q_lower for k in ["final", "total cost", "price",
                                     "per part", "unit cost",
                                     "cost per part"]):
        reply = (f"Cost per Part: {r['final_cost_per_part']:.4f} EUR\n\n"
                 f"- Subtotal: {r['subtotal']:.4f} EUR\n"
                 f"- SGA ({r['sga_pct']}%): {r['sga']:.4f} EUR\n"
                 f"- Profit ({r['profit_pct']}%): {r['profit']:.4f} EUR\n\n"
                 f"To modify: say 'Set SGA to 12' or 'Set profit to 8'")

    elif any(k in q_lower for k in ["annual", "yearly", "volume", "lot"]):
        reply = (f"Annual Summary:\n\n"
                 f"- {int(r['annual_volume']):,} pcs"
                 f" | {int(r['lots_per_year'])} lots"
                 f" | {int(r['lot_size']):,} pcs/lot\n"
                 f"- Cost/Part: {r['final_cost_per_part']:.4f} EUR\n"
                 f"- Annual Total: {r['annual_total']:,.2f} EUR")

    elif any(k in q_lower for k in ["weight", "mass", "gram"]):
        reply = (f"Weight Details:\n\n"
                 f"- Net Part Weight: {r['net_weight_g']:.2f} g\n"
                 f"- Deployed Weight: {r['deployed_weight_g']:.2f} g\n"
                 f"- Source: "
                 f"{'Auto from STL' if r['stl_loaded'] else 'Manual Entry'}")

    elif any(k in q_lower for k in ["surface", "area", "mm2"]):
        reply = (f"Surface Area: {r['surface_area_mm2']:.2f} mm2\n\n"
                 f"- Source: "
                 f"{'Computed from STL mesh' if r['stl_loaded'] else '2x(LxW + WxT + LxT)'}")

    elif any(k in q_lower for k in ["what can", "modify", "recalculate",
                                     "adjust", "parameters"]):
        reply = ("Parameters You Can Modify via Chat:\n\n"
                 "- Material Rate  -> 'Set material rate to 3.5'\n"
                 "- Stamping MHR   -> 'Set stamping MHR to 25'\n"
                 "- Coating MHR    -> 'Set coating MHR to 150'\n"
                 "- Inspection MHR -> 'Set inspection MHR to 1.5'\n"
                 "- Stamping Labour -> 'Set stamping labour to 30'\n"
                 "- Coating Labour  -> 'Set coating labour to 80'\n"
                 "- Insp. Labour    -> 'Set inspection labour to 50'\n"
                 "- SGA %           -> 'Set SGA to 12'\n"
                 "- Profit %        -> 'Set profit to 8'")

    elif any(k in q_lower for k in ["hello", "hi", "hey", "help"]):
        reply = ("Hello! I am your SmartCost AI Costing Assistant.\n\n"
                 "Ask about: Tonnage | Material | Coating | Scrap\n"
                 "Strip Layout | Manufacturing | Final Cost | Annual\n\n"
                 "Or modify parameters:\n"
                 "- 'Set stamping MHR to 25'\n"
                 "- 'Set material rate to 3.5'\n"
                 "- 'Set SGA to 12'\n"
                 "- 'Set profit to 8'")

    else:
        reply = ("I could not match that query.\n\n"
                 "Try: tonnage | material cost | coating | scrap\n"
                 "strip | manufacturing | final cost | annual\n\n"
                 "Say 'what can you change' to see modifiable parameters.")

    return reply, new_params


# ─────────────────────────────────────────────
# DISPLAY RESULTS
# ─────────────────────────────────────────────
def display_results(r):
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header">📊 Press & Strip Results</div>',
        unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tonnage",          f"{r['tonnage']:.2f} T")
    c2.metric("Deployed Weight",  f"{r['deployed_weight_g']:.2f} g")
    c3.metric("Scrap %",          f"{r['scrap_percent']:.2f} %")
    c4.metric("Utilization",      f"{r['utilization']:.2f} %")

    st.markdown(
        '<div class="section-header">💰 Material Cost</div>',
        unsafe_allow_html=True)
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Rate",            f"{r['material_rate']:.2f} EUR/kg")
    mc2.metric("Material Cost",   f"{r['material_cost']:.4f} EUR")
    mc3.metric("MOH (5%)",        f"{r['moh']:.4f} EUR")
    mc4.metric("Inv. Interest",   f"{r['interest']:.4f} EUR")

    st.markdown(
        '<div class="section-header">⚗️ Coating Cost</div>',
        unsafe_allow_html=True)
    if r["base_coat"] != "None" or r["final_coat"] != "None":
        cc1, cc2, cc3 = st.columns(3)
        if r["base_coat"] != "None":
            cc1.metric(f"Base ({r['base_coat']})",
                       f"{r['base_coat_cost']:.5f} EUR")
        if r["final_coat"] != "None":
            cc2.metric(f"Final ({r['final_coat']})",
                       f"{r['final_coat_cost']:.5f} EUR")
        cc3.metric("Total Coating",
                   f"{r['total_coating_cost']:.5f} EUR")
        src = "Auto from STL" if r["stl_loaded"] else "Manual"
        st.markdown(f"""
        <div class="info-card">
            Surface Area: <b>{r['surface_area_mm2']:.2f} mm2</b>
            <span class="badge">{src}</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="info-card">No coating selected.</div>',
            unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header">🏭 Manufacturing Cost</div>',
        unsafe_allow_html=True)
    mf1, mf2, mf3, mf4 = st.columns(4)
    mf1.metric("Stamping",        f"{r['stamping_cost']:.6f} EUR")
    mf2.metric("Coating Process", f"{r['coating_proc_cost']:.6f} EUR")
    mf3.metric("Inspection",      f"{r['inspection_cost']:.6f} EUR")
    mf4.metric("Total Mfg",       f"{r['manufacturing_cost']:.6f} EUR")
    st.markdown(f"""
    <div class="info-card">
        <b>Stamping</b> — MHR: {r['stamping_mhr']} EUR/hr |
        Labour: {r['stamping_labour_pct']}%<br>
        <b>Coating</b> — MHR: {r['coating_mhr']} EUR/hr |
        Labour: {r['coating_labour_pct']}%<br>
        <b>Inspection</b> — MHR: {r['insp_mhr']} EUR/hr |
        Labour: {r['insp_labour_pct']}%
    </div>""", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header">✅ Final Costing</div>',
        unsafe_allow_html=True)
    fc1, fc2, fc3, fc4 = st.columns(4)
    fc1.metric("Subtotal",              f"{r['subtotal']:.4f} EUR")
    fc2.metric(f"SGA ({r['sga_pct']}%)", f"{r['sga']:.4f} EUR")
    fc3.metric(f"Profit ({r['profit_pct']}%)", f"{r['profit']:.4f} EUR")
    fc4.metric("Cost / Part",           f"{r['final_cost_per_part']:.4f} EUR")
    st.markdown(f"""
    <div class="result-highlight">
        Cost per Part: {r['final_cost_per_part']:.4f} EUR
        &nbsp;&nbsp;|&nbsp;&nbsp;
        Annual ({int(r['annual_volume']):,} pcs):
        {r['annual_total']:,.2f} EUR
    </div>""", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header">📦 Volume Summary</div>',
        unsafe_allow_html=True)
    vs1, vs2, vs3 = st.columns(3)
    vs1.metric("Annual Volume", f"{int(r['annual_volume']):,} pcs")
    vs2.metric("Lots / Year",   f"{int(r['lots_per_year'])}")
    vs3.metric("Lot Size",      f"{int(r['lot_size']):,} pcs/lot")

    # Pie Chart
    st.markdown(
        '<div class="section-header">📊 Cost Breakdown Chart</div>',
        unsafe_allow_html=True)
    labels = ["Material", "MOH", "Inv.Interest", "Base Coat",
              "Final Coat", "Stamping", "Coat Process",
              "Inspection", "SGA", "Profit"]
    values = [r['material_cost'], r['moh'], r['interest'],
              r['base_coat_cost'], r['final_coat_cost'],
              r['stamping_cost'], r['coating_proc_cost'],
              r['inspection_cost'], r['sga'], r['profit']]
    filtered = [(l, v) for l, v in zip(labels, values) if v > 0]
    if filtered:
        lf, vf = zip(*filtered)
        clrs = ["#3b82f6", "#6366f1", "#8b5cf6", "#06b6d4", "#0ea5e9",
                "#10b981", "#22c55e", "#f59e0b", "#ef4444",
                "#f97316"][:len(lf)]
        fig2, ax2 = plt.subplots(figsize=(7, 7), facecolor="#0f1117")
        ax2.set_facecolor("#0f1117")
        wedges, _, autotexts = ax2.pie(
            vf, labels=None, autopct="%1.1f%%", startangle=140,
            colors=clrs,
            wedgeprops=dict(linewidth=1.5, edgecolor="#0f1117"),
            pctdistance=0.82)
        for at in autotexts:
            at.set_color("white")
            at.set_fontsize(10)
            at.set_fontweight("bold")
        ax2.legend(wedges, lf,
                   loc="lower center", bbox_to_anchor=(0.5, -0.12),
                   ncol=3, frameon=False, labelcolor="white", fontsize=10)
        ax2.set_title("Cost Breakdown per Part",
                      color="white", fontsize=14,
                      fontweight="bold", pad=20)
        st.pyplot(fig2)

    # Strip Layout
    st.markdown(
        '<div class="section-header">📐 Strip Layout</div>',
        unsafe_allow_html=True)
    lx = r["length"]; wx = r["width"]
    px = r["pitch"];  sw = r["strip_width"]; sl = r["strip_length"]
    ca = r["carriage_allowance"]; sa = r["stripping_allowance"]
    py_v = ca + sa

    fig, ax = plt.subplots(figsize=(10, 4), dpi=110, facecolor="#0f1117")
    ax.set_facecolor("#0f1117")
    ax.add_patch(plt.Rectangle((0, 0), sl, sw,
                               fill=False, linewidth=2, edgecolor="#3b82f6"))
    ax.add_patch(plt.Rectangle((0, 0), sl, ca, color="#f59e0b", alpha=0.5))
    ax.add_patch(plt.Rectangle((0, sw - ca), sl, ca, color="#f59e0b", alpha=0.5))
    ax.add_patch(plt.Rectangle((0, ca), sl, sa, color="#6b7280", alpha=0.5))
    ax.add_patch(plt.Rectangle((0, sw - ca - sa), sl, sa, color="#6b7280", alpha=0.5))
    ax.add_patch(plt.Rectangle((0, py_v), lx, wx,
                               fill=True, facecolor="#1e3a5f",
                               edgecolor="#60a5fa", linewidth=2))
    ax.add_patch(plt.Rectangle((lx + px, py_v), lx, wx,
                               fill=True, facecolor="#1e3a5f",
                               edgecolor="#60a5fa", linewidth=2))

    arr = dict(arrowstyle="<->", color="#94a3b8", lw=1.5)
    txk = dict(color="#e2e8f0", fontsize=9, ha="center", fontweight="bold")
    ax.annotate("", xy=(0, py_v - 4),
                xytext=(lx, py_v - 4), arrowprops=arr)
    ax.text(lx / 2, py_v - 8, f"Length = {lx} mm", **txk)
    ax.annotate("", xy=(lx, py_v - 13),
                xytext=(lx + px, py_v - 13), arrowprops=arr)
    ax.text(lx + px / 2, py_v - 17, f"Pitch = {px} mm", **txk)
    ax.annotate("", xy=(sl + 3, 0),
                xytext=(sl + 3, sw), arrowprops=arr)
    ax.text(sl + 6, sw / 2, f"Strip W\n{sw}mm",
            color="#e2e8f0", fontsize=8,
            ha="left", va="center", fontweight="bold")
    ax.annotate("", xy=(0, sw + 4),
                xytext=(sl, sw + 4), arrowprops=arr)
    ax.text(sl / 2, sw + 8, f"Strip Length = {sl} mm", **txk)
    ax.legend(handles=[
        mpatches.Patch(color="#f59e0b", alpha=0.7, label="Carriage"),
        mpatches.Patch(color="#6b7280", alpha=0.7, label="Stripping"),
        mpatches.Patch(facecolor="#1e3a5f", edgecolor="#60a5fa", label="Part"),
    ], loc="upper right", frameon=False, labelcolor="white", fontsize=9)
    ax.set_xlim(-5, sl + 20)
    ax.set_ylim(-25, sw + 15)
    ax.set_aspect("equal")
    ax.axis("off")
    st.pyplot(fig)

    # Downloads
    st.markdown(
        '<div class="section-header">📥 Download Report</div>',
        unsafe_allow_html=True)
    dl1, dl2, dl3 = st.columns(3)
    with dl1:
        try:
            pdf_bytes = generate_pdf_report(r)
            st.download_button(
                label="📄 Download PDF",
                data=pdf_bytes,
                file_name="smartcost_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key=f"pdf_dl_{id(r)}")
        except Exception as e:
            st.error(f"PDF error: {e}")
    with dl2:
        try:
            excel_buf = generate_excel_report(r)
            st.download_button(
                label="📊 Download Excel",
                data=excel_buf,
                file_name="smartcost_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument"
                     ".spreadsheetml.sheet",
                use_container_width=True,
                key=f"xlsx_dl_{id(r)}")
        except Exception as e:
            st.error(f"Excel error: {e}")
    with dl3:
        csv_bytes = generate_csv_report(r)
        st.download_button(
            label="📋 Download CSV",
            data=csv_bytes,
            file_name="smartcost_report.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"csv_dl_{id(r)}")


# ─────────────────────────────────────────────
# MAIN APP (shown after login)
# ─────────────────────────────────────────────
def show_main_app():
    show_top_bar()

    # App title
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 16px 0;'>
        <h1 style='font-size:34px; font-weight:900;
                   background: linear-gradient(90deg, #60a5fa, #a78bfa, #34d399);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   margin-bottom: 6px;'>
            AI Sheet Metal Costing Assistant
        </h1>
        <p style='color:#6b7280; font-size:14px; letter-spacing:1px;'>
            "Design Smart. Cost Instantly."
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📘 Terminal Pin Log", "🧮 Sheet Metal Costing"])

    with tab1:
        st.markdown(
            '<div class="section-header">📘 Terminal Pin Log</div>',
            unsafe_allow_html=True)
        st.info("Terminal pin records will appear here.")

    with tab2:
        # STL Upload
        st.markdown(
            '<div class="section-header">📁 3D Model Upload</div>',
            unsafe_allow_html=True)
        col_up1, col_up2 = st.columns([2, 1])
        with col_up1:
            stl_file = st.file_uploader("Upload STL File", type=["stl"])
        with col_up2:
            st.markdown("<br>", unsafe_allow_html=True)
            manual_override = st.checkbox("Manual Enter Dimensions")

        auto_length = auto_width = auto_thickness = None
        auto_volume = auto_surface_area = None
        stl_loaded  = False

        if stl_file and not manual_override:
            with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".stl") as tmp:
                tmp.write(stl_file.getbuffer())
                temp_path = tmp.name
            your_mesh = mesh.Mesh.from_file(temp_path)
            points    = your_mesh.vectors.reshape(-1, 3)
            min_vals  = np.min(points, axis=0)
            max_vals  = np.max(points, axis=0)
            auto_length    = max_vals[0] - min_vals[0]
            auto_width     = max_vals[1] - min_vals[1]
            auto_thickness = max_vals[2] - min_vals[2]
            auto_volume    = your_mesh.get_mass_properties()[0]
            area = 0
            for tri in your_mesh.vectors:
                a = tri[1] - tri[0]
                b = tri[2] - tri[0]
                area += np.linalg.norm(np.cross(a, b)) / 2
            auto_surface_area = area
            stl_loaded = True
            st.markdown(f"""
            <div class="info-card">
                STL Loaded Successfully<br>
                Length: {auto_length:.2f} mm |
                Width: {auto_width:.2f} mm |
                Thickness: {auto_thickness:.2f} mm |
                Surface Area: {auto_surface_area:.2f} mm2
            </div>""", unsafe_allow_html=True)

        # Commercial
        st.markdown(
            '<div class="section-header">🌍 Commercial & Volume Details</div>',
            unsafe_allow_html=True)
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            region = st.selectbox("Customer Region", [
                "Europe", "North America", "South America",
                "Asia Pacific", "Middle East & Africa", "India"])
        with col_r2:
            annual_volume = st.number_input(
                "Annual Volume (pcs/year)",
                min_value=1000, max_value=100_000_000,
                value=500_000, step=1000)
        with col_r3:
            lots_per_year = st.number_input(
                "Lots per Year",
                min_value=1, max_value=365, value=12, step=1)
        lot_size = int(annual_volume / lots_per_year)
        st.markdown(f"""
        <div class="info-card">
            Region: <b>{region}</b> |
            Annual: <b>{int(annual_volume):,} pcs</b> |
            Lots: <b>{int(lots_per_year)}</b> |
            Lot Size: <b>{lot_size:,} pcs/lot</b>
        </div>""", unsafe_allow_html=True)

        # Dimensions
        st.markdown(
            '<div class="section-header">📐 Part Dimensions & Material</div>',
            unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            length = st.number_input(
                "Part Length (mm)", min_value=0.0,
                value=float(auto_length) if auto_length else 50.0)
        with col2:
            width = st.number_input(
                "Part Width (mm)", min_value=0.0,
                value=float(auto_width) if auto_width else 30.0)
        with col3:
            thickness = st.number_input(
                "Thickness (mm)", min_value=0.0,
                value=float(auto_thickness) if auto_thickness else 2.0)

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            material = st.selectbox(
                "Material",
                ["CR Steel", "SS304", "SS430", "Aluminium", "Copper"])
        with col_m2:
            uploaded_image = st.file_uploader(
                "Upload Unfolded Part Image",
                type=["png", "jpg", "jpeg"])
            if uploaded_image:
                st.image(uploaded_image, width=200)

        density_db = {
            "CR Steel": 7850, "SS304": 8000, "SS430": 7700,
            "Aluminium": 2700, "Copper": 8960}
        density = density_db[material]

        # Net Weight
        if manual_override or not stl_loaded:
            st.markdown(
                '<div class="section-header">⚖️ Part Weight</div>',
                unsafe_allow_html=True)
            net_weight_grams = st.number_input(
                "Part Net Weight (grams)", min_value=0.0, value=50.0)
            net_weight = net_weight_grams / 1000
        else:
            volume_m3_auto = auto_volume / 1e9
            net_weight     = volume_m3_auto * density
            st.markdown(f"""
            <div class="info-card">
                Net Weight from STL: <b>{net_weight*1000:.2f} grams</b>
                <span class="badge">Auto from STL</span>
            </div>""", unsafe_allow_html=True)

        # Coating
        st.markdown(
            '<div class="section-header">⚗️ Coating Details</div>',
            unsafe_allow_html=True)
        if stl_loaded and not manual_override:
            surface_area_for_coating = auto_surface_area
            st.markdown(f"""
            <div class="info-card">
                Surface Area: <b>{auto_surface_area:.2f} mm2</b>
                <span class="badge">Auto from STL</span>
            </div>""", unsafe_allow_html=True)
        else:
            surface_area_for_coating = 2 * (
                length * width + width * thickness + length * thickness)
            st.markdown(f"""
            <div class="info-card">
                Surface Area (manual): <b>{surface_area_for_coating:.2f} mm2</b>
                <span class="badge">Calculated</span>
            </div>""", unsafe_allow_html=True)

        coat_c1, coat_c2 = st.columns(2)
        with coat_c1:
            st.markdown("**Base Coating**")
            base_coating_type = st.selectbox(
                "Base Coating Type",
                ["None", "Zinc", "Nickel", "Tin", "Silver", "Gold"],
                key="base_coat")
            base_coating_micron = st.number_input(
                "Base Coating Thickness (microns)",
                min_value=0.0, value=5.0, key="base_micron")
        with coat_c2:
            st.markdown("**Final / Top Coating**")
            final_coating_type = st.selectbox(
                "Final Coating Type",
                ["None", "Zinc", "Nickel", "Tin", "Silver", "Gold"],
                key="final_coat")
            final_coating_micron = st.number_input(
                "Final Coating Thickness (microns)",
                min_value=0.0, value=3.0, key="final_micron")

        # Calculate
        st.markdown("<br>", unsafe_allow_html=True)
        calc_btn = st.button("Calculate Results")

        if calc_btn:
            params = {
                "length":               length,
                "width":                width,
                "thickness":            thickness,
                "material":             material,
                "net_weight":           net_weight,
                "surface_area":         surface_area_for_coating,
                "base_coating_type":    base_coating_type,
                "base_coating_micron":  base_coating_micron,
                "final_coating_type":   final_coating_type,
                "final_coating_micron": final_coating_micron,
                "region":               region,
                "annual_volume":        annual_volume,
                "lots_per_year":        lots_per_year,
                "lot_size":             lot_size,
                "stl_loaded":           stl_loaded,
                "stamping_mhr":         18,
                "stamping_speed":       100,
                "stamping_labour_pct":  25,
                "stamping_rmoh_pct":    7,
                "coating_mhr":          130,
                "coating_speed":        1600,
                "coating_labour_pct":   100,
                "coating_rmoh_pct":     10,
                "insp_mhr":             0.5,
                "insp_labour_pct":      100,
                "insp_rmoh_pct":        8,
                "sga_pct":              10,
                "profit_pct":           5,
            }
            results = run_calculation(params)
            st.session_state["calc_results"] = results
            st.session_state["calc_params"]  = params
            st.session_state["chat_history"] = []

        if "calc_results" in st.session_state:
            display_results(st.session_state["calc_results"])

        # Chatbot
        if "calc_results" in st.session_state:
            st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
            st.markdown(
                '<div class="section-header">🤖 SmartCost AI Chatbot</div>',
                unsafe_allow_html=True)
            st.markdown("""
            <div class="info-card">
                Ask questions or modify parameters to recalculate instantly!<br>
                <span class="badge">Tonnage</span>
                <span class="badge">Material Cost</span>
                <span class="badge">Coating</span>
                <span class="badge">Scrap %</span>
                <span class="badge">Final Price</span>
                <span class="badge">Set MHR</span>
                <span class="badge">Set Labour %</span>
                <span class="badge">Set Material Rate</span>
                <span class="badge">Set SGA / Profit</span>
            </div>""", unsafe_allow_html=True)

            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = []

            for entry in st.session_state["chat_history"]:
                st.markdown(
                    f'<div class="chat-user">You: {entry["user"]}</div>',
                    unsafe_allow_html=True)
                if entry.get("recalculated"):
                    st.markdown(
                        f'<div class="recalc-highlight">'
                        f'Bot (Recalculated): {entry["bot"]}</div>',
                        unsafe_allow_html=True)
                    if "new_results" in entry:
                        nr = entry["new_results"]
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Cost/Part",
                                  f"{nr['final_cost_per_part']:.4f} EUR")
                        m2.metric("Annual Total",
                                  f"{nr['annual_total']:,.0f} EUR")
                        m3.metric("Mfg Cost",
                                  f"{nr['manufacturing_cost']:.6f} EUR")
                        m4.metric("Material Cost",
                                  f"{nr['material_cost']:.4f} EUR")
                else:
                    st.markdown(
                        f'<div class="chat-bot">Bot: {entry["bot"]}</div>',
                        unsafe_allow_html=True)

            with st.form(key="chat_form", clear_on_submit=True):
                ci, cb = st.columns([5, 1])
                with ci:
                    user_input = st.text_input(
                        "Ask or modify...",
                        placeholder=(
                            "e.g. 'Set stamping MHR to 25'"
                            " or 'What is final cost?'"),
                        label_visibility="collapsed")
                with cb:
                    send = st.form_submit_button("Send")

            if send and user_input.strip():
                r = st.session_state["calc_results"]
                p = st.session_state["calc_params"]
                bot_reply, new_params = answer_query(
                    user_input.strip(), r, p)

                entry = {
                    "user":         user_input.strip(),
                    "bot":          bot_reply,
                    "recalculated": False
                }

                if new_params is not None:
                    new_results = run_calculation(new_params)
                    st.session_state["calc_results"] = new_results
                    st.session_state["calc_params"]  = new_params
                    bot_reply += (
                        f"\n\nDone! New Cost/Part: "
                        f"{new_results['final_cost_per_part']:.4f} EUR"
                        f" (was {r['final_cost_per_part']:.4f} EUR) | "
                        f"Annual: {new_results['annual_total']:,.2f} EUR"
                        f" (was {r['annual_total']:,.2f} EUR)"
                    )
                    entry["bot"]          = bot_reply
                    entry["recalculated"] = True
                    entry["new_results"]  = new_results

                st.session_state["chat_history"].append(entry)
                st.rerun()

            if st.session_state.get("chat_history"):
                if st.button("Clear Chat"):
                    st.session_state["chat_history"] = []
                    st.rerun()


# ─────────────────────────────────────────────
# ROUTER  ← entry point
# ─────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    show_login_page()
else:
    show_main_app()
