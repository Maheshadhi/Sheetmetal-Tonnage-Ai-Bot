import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import tempfile
from stl import mesh
import numpy as np

st.set_page_config(page_title="AI Sheet Metal Costing Assistant", layout="wide")

st.title("🤖 AI Sheet Metal Costing Assistant")

st.header("Enter Part Details")

# -----------------------------
# STL FILE INPUT
# -----------------------------

st.subheader("Upload 3D Model (STL)")

stl_file = st.file_uploader(
    "Upload STL File",
    type=["stl"]
)

manual_override = st.checkbox("Manual Enter Dimensions")

auto_length = None
auto_width = None
auto_thickness = None
auto_volume = None

if stl_file and not manual_override:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(stl_file.getbuffer())
        temp_path = tmp.name

    # Load STL
    your_mesh = mesh.Mesh.from_file(temp_path)

    # Get all vertices
    points = your_mesh.vectors.reshape(-1, 3)

    # Bounding box
    min_vals = np.min(points, axis=0)
    max_vals = np.max(points, axis=0)

    auto_length = max_vals[0] - min_vals[0]
    auto_width = max_vals[1] - min_vals[1]
    auto_thickness = max_vals[2] - min_vals[2]

    # Volume (in mm³)
    auto_volume = your_mesh.get_mass_properties()[0]

    st.success("STL Model Loaded Successfully")

    st.write(f"Detected Length : {auto_length:.2f} mm")
    st.write(f"Detected Width : {auto_width:.2f} mm")
    st.write(f"Detected Thickness : {auto_thickness:.2f} mm")

# -----------------------------
# INPUT SECTION
# -----------------------------

col1, col2, col3 = st.columns(3)

with col1:
    length = st.number_input(
        "Part Length (mm)",
        min_value=0.0,
        value=float(auto_length) if auto_length else 50.0
    )

with col2:
    width = st.number_input(
        "Part Width (mm)",
        min_value=0.0,
        value=float(auto_width) if auto_width else 30.0
    )

with col3:
    thickness = st.number_input(
        "Thickness (mm)",
        min_value=0.0,
        value=float(auto_thickness) if auto_thickness else 2.0
    )

material = st.selectbox(
    "Material",
    ["CR Steel", "SS304", "SS430", "Aluminium", "Copper"]
)

density_db = {
    "CR Steel":7850,
    "SS304":8000,
    "SS430":7700,
    "Aluminium":2700,
    "Copper":8960
}

shear_db = {
    "CR Steel":250,
    "SS304":300,
    "SS430":275,
    "Aluminium":110,
    "Copper":210
}

density = density_db[material]
shear_strength = shear_db[material]

# -----------------------------
# NET WEIGHT
# -----------------------------

net_weight_grams = st.number_input(
    "Part Net Weight (grams)",
    min_value=0.0,
    value=50.0
)

if auto_volume and not manual_override:

    volume_m3 = auto_volume / 1e9
    auto_weight = volume_m3 * density
    auto_weight_grams = auto_weight * 1000

    st.info(f"Estimated Net Weight from 3D Model : {auto_weight_grams:.2f} grams")

net_weight = net_weight_grams / 1000

# -----------------------------
# IMAGE UPLOAD
# -----------------------------

uploaded_image = st.file_uploader(
    "Upload Unfolded Part Image",
    type=["png","jpg","jpeg"]
)

if uploaded_image:
    st.image(uploaded_image,width=250)

# -----------------------------
# CALCULATION
# -----------------------------

if st.button("Calculate Results"):

    perimeter = ((2*length)+(2*width))*0.7
    cutting_force = perimeter*thickness*shear_strength

    fos = cutting_force*0.5
    stripping_force = cutting_force*0.4

    total_force = cutting_force + fos + stripping_force

    tonnage = total_force/(1000*9.81)

    carriage_allowance = 5
    stripping_allowance = 3
    pitch = 2*thickness

    strip_width = width + (2*carriage_allowance) + (2*stripping_allowance)
    strip_length = (2*length) + pitch

    deployed_length = length + pitch

    strip_area = strip_width * deployed_length

    volume_mm3 = strip_area * thickness
    volume_m3 = volume_mm3 / 1e9

    deployed_weight = volume_m3 * density

    scrap_weight = deployed_weight - net_weight
    scrap_percent = (scrap_weight/deployed_weight)*100 if deployed_weight>0 else 0

    part_area = length * width
    strip_area_layout = strip_length * strip_width
    utilization = (2*part_area/strip_area_layout)*100

    # -----------------------------
    # RESULTS
    # -----------------------------

    st.subheader("Results")

    st.write(f"Tonnage Required : **{tonnage:.2f} Tons**")
    st.write(f"Deployed Weight : **{deployed_weight:.4f} kg**")
    st.write(f"Scrap % : **{scrap_percent:.2f} %**")
    st.write(f"Material Utilization : **{utilization:.2f} %**")

    # -----------------------------
    # STRIP LAYOUT
    # -----------------------------

    st.subheader("Strip Layout Representation")

    fig, ax = plt.subplots(figsize=(8,3), dpi=100)

    ax.add_patch(
        plt.Rectangle((0,0), strip_length, strip_width,
        fill=False, linewidth=2)
    )

    ax.add_patch(
        plt.Rectangle((0,0), strip_length, carriage_allowance,
        color="orange", alpha=0.4)
    )

    ax.add_patch(
        plt.Rectangle((0,carriage_allowance),
        strip_length, stripping_allowance,
        color="grey", alpha=0.4)
    )

    part_y = carriage_allowance + stripping_allowance

    ax.add_patch(
        plt.Rectangle((0,part_y), length, width,
        fill=False, linewidth=2)
    )

    ax.add_patch(
        plt.Rectangle((length+pitch,part_y),
        length, width,
        fill=False, linewidth=2)
    )

    ax.add_patch(
        plt.Rectangle((0,part_y+width),
        strip_length, stripping_allowance,
        color="grey", alpha=0.4)
    )

    ax.add_patch(
        plt.Rectangle((0,part_y+width+stripping_allowance),
        strip_length, carriage_allowance,
        color="orange", alpha=0.4)
    )

    ax.annotate("",
    xy=(0,part_y-3),
    xytext=(length,part_y-3),
    arrowprops=dict(arrowstyle="<->"))

    ax.text(length/2,part_y-6,f"Part Length = {length} mm",ha="center")

    ax.annotate("",
    xy=(length,part_y-10),
    xytext=(length+pitch,part_y-10),
    arrowprops=dict(arrowstyle="<->"))

    ax.text(length+pitch/2,part_y-13,f"Pitch = {pitch} mm",ha="center")

    ax.annotate("",
    xy=(strip_length+2,0),
    xytext=(strip_length+2,strip_width),
    arrowprops=dict(arrowstyle="<->"))

    ax.text(strip_length+3,strip_width/2,
    f"Strip Width\n{strip_width} mm",
    rotation=90)

    ax.annotate("",
    xy=(0,strip_width+3),
    xytext=(strip_length,strip_width+3),
    arrowprops=dict(arrowstyle="<->"))

    ax.text(strip_length/2,strip_width+6,
    f"Strip Length = {strip_length} mm",
    ha="center")

    ax.set_xlim(-5, strip_length+15)
    ax.set_ylim(-5, strip_width+15)

    ax.set_aspect('equal')
    ax.axis('off')

    st.pyplot(fig)

    plt.close(fig)

    # -----------------------------
    # EXPORT
    # -----------------------------

    results = pd.DataFrame({
        "Material":[material],
        "Length":[length],
        "Width":[width],
        "Thickness":[thickness],
        "Net Weight":[net_weight],
        "Tonnage":[tonnage],
        "Deployed Weight":[deployed_weight],
        "Scrap %":[scrap_percent],
        "Utilization %":[utilization]
    })

    st.download_button(
        "Download Results CSV",
        results.to_csv(index=False),
        file_name="sheet_metal_results.csv"
    )