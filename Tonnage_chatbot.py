import streamlit as st
import math
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="AI Sheet Metal Costing Bot")

# -----------------------------
# SESSION STATE FOR CHAT MODE
# -----------------------------

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

st.title("🤖 AI Sheet Metal Costing Assistant")

# -----------------------------
# CHATBOT START
# -----------------------------

if not st.session_state.chat_started:
    st.write("Hello  👋")
    st.write("I will help you calculate tonnage, deployed weight & scrap%")
    if st.button("Start Calculation"):
        st.session_state.chat_started = True

# -----------------------------
# MAIN FORM AFTER CHAT START
# -----------------------------

if st.session_state.chat_started:

    st.header("📋 Enter Part Details")

    # -----------------------------
    # MATERIAL DATABASE
    # -----------------------------

    material_db = {
        "CR Steel": {"density": 7850, "shear": 250},
        "Stainless Steel 304": {"density": 8000, "shear": 300},
        "Stainless Steel 430": {"density": 7700, "shear": 275},
        "Aluminium 5052": {"density": 2700, "shear": 110},
        "Copper": {"density": 8960, "shear": 210},
        "Brass": {"density": 8500, "shear": 200}
    }

    length = st.number_input("Part Length (mm)", min_value=0.0)
    width = st.number_input("Part Width (mm)", min_value=0.0)
    thickness = st.number_input("Thickness (mm)", min_value=0.0)

    material = st.selectbox("Select Material", list(material_db.keys()))

    auto_fill = st.checkbox("Auto select Shear Strength & Density", value=True)

    if auto_fill:
        shear_strength = material_db[material]["shear"]
        density = material_db[material]["density"]
        st.write(f"Shear Strength: {shear_strength} N/mm²")
        st.write(f"Density: {density} kg/m³")
    else:
        shear_strength = st.number_input("Shear Strength (N/mm²)", min_value=0.0)
        density = st.number_input("Material Density (kg/m³)", min_value=0.0)

    # Net weight in grams
    part_net_weight_grams = st.number_input("Part Net Weight (grams)", min_value=0.0)

    # -----------------------------
    # CALCULATE
    # -----------------------------

    if st.button("Calculate Results"):

        # Convert grams to kg
        part_net_weight = part_net_weight_grams / 1000

        # ---- TONNAGE ----
        perimeter = ((2 * length) + (2 * width)) * 0.7
        cutting_force = perimeter * thickness * shear_strength
        factor_of_safety = cutting_force * 0.5
        stripping_force = cutting_force * 0.4
        total_force = cutting_force + factor_of_safety + stripping_force
        tonnage = total_force / (1000 * 9.81)

        # ---- STRIP LAYOUT ----
        carriage_allowance = 5
        stripping_allowance = 3

        # Width includes BOTH allowances
        strip_width = width + ((2 *carriage_allowance)+(2*stripping_allowance ))

        # Pitch = 2 × thickness (as requested)
        pitch = 2 * thickness

        # Deployed dimensions include allowances
        deployed_width = strip_width
        deployed_length = pitch + length

        # ---- DEPLOYED WEIGHT ----
        strip_area = deployed_width * deployed_length
        volume_mm3 = strip_area * thickness
        volume_m3 = volume_mm3 / 1e9
        deployed_weight = volume_m3 * density

        scrap_weight = max(deployed_weight - part_net_weight, 0)
        scrap_percent = (scrap_weight / deployed_weight * 100) if deployed_weight > 0 else 0

        # -----------------------------
        # DISPLAY RESULTS
        # -----------------------------

        st.subheader("🔹 Results Summary")
        st.write(f"Required Tonnage: **{tonnage:.2f} Tons**")
        st.write(f"Deployed Weight per Stroke: **{deployed_weight:.4f} kg**")
        st.write(f"Scrap Percentage: **{scrap_percent:.2f} %**")

        # -----------------------------
        # STRIP LAYOUT VISUAL
        # -----------------------------

        fig, ax = plt.subplots()

        # Outer strip
        ax.add_patch(
            plt.Rectangle((0, 0), deployed_width, deployed_length,
                          fill=False, linewidth=2)
        )

        # Carriage zones (Left & Right)
        ax.add_patch(
            plt.Rectangle((0, 0), carriage_allowance, deployed_length,
                          color="green", alpha=0.3)
        )
        ax.add_patch(
            plt.Rectangle((deployed_width - carriage_allowance, 0),
                          carriage_allowance, deployed_length,
                          color="green", alpha=0.3)
        )

        # Stripping zones (Top & Bottom)
        ax.add_patch(
            plt.Rectangle((0, 0), deployed_width, stripping_allowance,
                          color="blue", alpha=0.2)
        )
        ax.add_patch(
            plt.Rectangle((0, deployed_length - stripping_allowance),
                          deployed_width, stripping_allowance,
                          color="blue", alpha=0.2)
        )

        # Part in center
        ax.add_patch(
            plt.Rectangle(
                (carriage_allowance, stripping_allowance),
                width,
                pitch,
                fill=False,
                linewidth=2
            )
        )

        ax.set_aspect('equal')
        ax.set_title("Strip Layout Representation")
        ax.invert_yaxis()
        st.pyplot(fig)

        # -----------------------------
        # EXPORT TO EXCEL
        # -----------------------------

        result_data = {
            "Material": [material],
            "Length (mm)": [length],
            "Width (mm)": [width],
            "Thickness (mm)": [thickness],
            "Tonnage (Tons)": [tonnage],
            "Deployed Weight (kg)": [deployed_weight],
            "Net Weight (kg)": [part_net_weight],
            "Scrap %": [scrap_percent]
        }

        df = pd.DataFrame(result_data)

        st.download_button(
            label="📥 Export Results to Excel",
            data=df.to_csv(index=False),
            file_name="sheet_metal_results.csv",
            mime="text/csv"
        )
