import streamlit as st
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Industrial Sheet Metal AI Bot")
st.title("🤖 Industrial Sheet Metal Engineering Bot")

# -------------------------
# ADVANCED MATERIAL DATABASE
# -------------------------
material_db = {
    "crca": {"shear": 300, "density": 7850, "aliases": ["en10130", "dc01"]},
    "s235jr": {"shear": 310, "density": 7850, "aliases": ["en10025"]},
    "ss304": {"shear": 520, "density": 8000, "aliases": ["en10088", "aisi304"]},
    "aluminium 5052": {"shear": 210, "density": 2700, "aliases": ["en aw-5052"]},
    "copper": {"shear": 250, "density": 8960, "aliases": ["cw004a"]}
}

# -------------------------
# SESSION MEMORY
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.context = {}

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about tonnage, allowances, EN material, scrap %...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})
    text = user_input.lower()
    ctx = st.session_state.context

    # -------------------------
    # MATERIAL DETECTION (WITH EN SUPPORT)
    # -------------------------
    for mat, data in material_db.items():
        if mat in text or any(alias in text for alias in data["aliases"]):
            ctx["material"] = mat
            ctx["shear"] = data["shear"]
            ctx["density"] = data["density"]

    # -------------------------
    # NUMBER EXTRACTION
    # -------------------------
    numbers = re.findall(r"\d+\.?\d*", text)
    numbers = list(map(float, numbers))

    # Auto assign thickness, length, width if 3 numbers found
    if len(numbers) >= 3:
        ctx["thickness"] = numbers[0]
        ctx["length"] = numbers[1]
        ctx["width"] = numbers[2]

    # Scrap %
    if "%" in text:
        ctx["scrap_percent"] = numbers[-1]

    # Allowance override detection
    if "carriage" in text:
        ctx["carriage_allowance"] = numbers[-1]

    if "stripping" in text:
        ctx["stripping_allowance"] = numbers[-1]

    # -------------------------
    # VALIDATION
    # -------------------------
    required = ["material", "thickness", "length", "width"]
    missing = [r for r in required if r not in ctx]

    if missing:
        response = f"I still need: {', '.join(missing)}"
    else:
        thickness = ctx["thickness"]
        length = ctx["length"]
        width = ctx["width"]
        shear = ctx["shear"]
        density = ctx["density"]

        # Default allowance logic
        carriage_allowance = ctx.get("carriage_allowance", round(thickness * 1.5, 2))
        stripping_allowance = ctx.get("stripping_allowance", round(thickness * 1.2, 2))

        strip_width = width + (2 * carriage_allowance)
        pitch = length + stripping_allowance

        # Tonnage
        perimeter = ((2 * length) + (2 * width)) * 0.7
        cutting_force = perimeter * thickness * shear
        fos = cutting_force * 0.5
        stripping_force = cutting_force * 0.4
        tonnage = (cutting_force + fos + stripping_force) / (1000 * 9.81)

        # Weight
        strip_area = strip_width * pitch
        part_area = length * width

        volume_strip = (strip_area * thickness) / 1e9
        volume_part = (part_area * thickness) / 1e9

        deployed_weight = volume_strip * density
        part_weight = volume_part * density

        scrap_weight = deployed_weight - part_weight

        # Scrap %
        scrap_percent = ctx.get("scrap_percent", (scrap_weight / deployed_weight) * 100)

        response = f"""
### 📊 Engineering Output

Material: {ctx['material'].upper()}  
Shear Strength: {shear} MPa  

Thickness: {thickness} mm  

Carriage Allowance: {carriage_allowance} mm  
Stripping Allowance: {stripping_allowance} mm  

Required Tonnage: {tonnage:.2f} Tons  

Deployed Weight: {deployed_weight:.4f} kg  
Part Weight: {part_weight:.4f} kg  

Scrap Weight: {scrap_weight:.4f} kg  
Scrap Percentage: {scrap_percent:.2f} %
"""

        # -------------------------
        # STRIP IMAGE
        # -------------------------
        fig, ax = plt.subplots()
        ax.add_patch(plt.Rectangle((0, 0), pitch, strip_width, fill=False))
        ax.add_patch(plt.Rectangle(
            (stripping_allowance/2, carriage_allowance),
            length,
            width,
            fill=False
        ))
        ax.set_title("Strip Layout")
        st.pyplot(fig)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()