import streamlit as st
import ezdxf
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import math

st.set_page_config(page_title="STC Construction", page_icon="🏗️", layout="wide")

st.title("🏗️ STC Construction - Material Calculator Pro")
st.markdown("**STC Construction, Bhokar | Estimate Cement, Sand, Aggregate, Steel & Cost**")
st.divider()

# Sidebar
st.sidebar.header("Project Details")
client_name = st.sidebar.text_input("Client Name", "Tejaswini Client")
site = st.sidebar.text_input("Site Location", "Bhokar")
work_type = st.sidebar.selectbox("Work Type", ["Slab / Roof", "Column", "Beam", "Foundation Footing", "Full Building"])

st.sidebar.divider()
st.sidebar.header("Material Rates (Rs)")
cement_rate = st.sidebar.number_input("Cement Rate / bag (50kg)", value=400)
sand_rate = st.sidebar.number_input("Sand Rate / brass", value=4500)
aggregate_rate = st.sidebar.number_input("Aggregate Rate / brass", value=5500)
steel_rate = st.sidebar.number_input("Steel Rate / kg", value=65)

# Main inputs
col1, col2 = st.columns(2)

with col1:
    st.subheader("📐 Dimensions (in Feet)")
    length = st.number_input("Length (ft)", value=20.0)
    width = st.number_input("Width (ft)", value=15.0)
    thickness = st.number_input("Thickness / Height (ft)", value=0.5, help="For slab 0.4-0.6 ft, for column/beam height")
    
    st.subheader("Concrete Grade")
    grade = st.selectbox("Grade", ["M15 (1:2:4)", "M20 (1:1.5:3)", "M25 (1:1:2)"])
    
    if grade == "M15 (1:2:4)":
        cement_ratio, sand_ratio, agg_ratio = 1, 2, 4
    elif grade == "M20 (1:1.5:3)":
        cement_ratio, sand_ratio, agg_ratio = 1, 1.5, 3
    else:
        cement_ratio, sand_ratio, agg_ratio = 1, 1, 2

with col2:
    st.subheader("🔩 Steel Details")
    steel_percent = st.number_input("Steel % (for RCC, 80-120 kg/cum)", value=80)
    wastage = st.number_input("Wastage %", value=5)

# Calculations
volume_cft = length * width * thickness
volume_cum = volume_cft * 0.0283168  # cft to cum

# Dry volume 1.54x
dry_volume = volume_cum * 1.54
total_ratio = cement_ratio + sand_ratio + agg_ratio

cement_cum = dry_volume * (cement_ratio / total_ratio)
sand_cum = dry_volume * (sand_ratio / total_ratio)
agg_cum = dry_volume * (agg_ratio / total_ratio)

# Cement bags: 1 cum = 28.8 bags (1440kg/cum, 50kg/bag)
cement_bags = cement_cum * 28.8
cement_bags_with_wastage = cement_bags * (1 + wastage/100)

sand_cft = sand_cum * 35.3147
sand_brass = sand_cft / 100

agg_cft = agg_cum * 35.3147
agg_brass = agg_cft / 100

steel_kg = volume_cum * steel_percent
steel_kg_with_wastage = steel_kg * (1 + wastage/100)

# Cost
cement_cost = cement_bags_with_wastage * cement_rate
sand_cost = sand_brass * sand_rate
agg_cost = agg_brass * aggregate_rate
steel_cost = steel_kg_with_wastage * steel_rate
total_cost = cement_cost + sand_cost + agg_cost + steel_cost

st.divider()
st.subheader("📊 Result - Material Estimate")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Volume", f"{volume_cft:.2f} CFT", f"{volume_cum:.3f} CUM")
m2.metric("Cement Bags", f"{cement_bags_with_wastage:.1f} Bags", f"{cement_bags:.1f} without waste")
m3.metric("Sand", f"{sand_brass:.2f} Brass", f"{sand_cft:.0f} CFT")
m4.metric("Aggregate", f"{agg_brass:.2f} Brass", f"{agg_cft:.0f} CFT")

m5, m6, m7, m8 = st.columns(4)
m5.metric("Steel", f"{steel_kg_with_wastage:.1f} Kg")
m6.metric("Cement Cost", f"Rs {cement_cost:,.0f}")
m7.metric("Total Material Cost", f"Rs {total_cost:,.0f}")
m8.metric("Cost per Sqft", f"Rs {total_cost/(length*width):,.0f}" if length*width>0 else "0")

# Chart
st.divider()
c1, c2 = st.columns(2)
with c1:
    st.subheader("Cost Distribution")
    fig, ax = plt.subplots()
    labels = ['Cement', 'Sand', 'Aggregate', 'Steel']
    values = [cement_cost, sand_cost, agg_cost, steel_cost]
    ax.pie(values, labels=labels, autopct='%1.1f%%')
    st.pyplot(fig)

with c2:
    st.subheader("Detailed Report")
    st.write(f"**Client:** {client_name}")
    st.write(f"**Site:** {site}")
    st.write(f"**Work:** {work_type} - {length} x {width} x {thickness} ft")
    st.write(f"**Grade:** {grade} = {cement_ratio}:{sand_ratio}:{agg_ratio}")
    st.write(f"**Volume:** {volume_cum:.3f} CUM")
    st.write(f"**Cement:** {cement_bags_with_wastage:.2f} Bags")
    st.write(f"**Sand:** {sand_brass:.3f} Brass ({sand_cft:.1f} CFT)")
    st.write(f"**Aggregate:** {agg_brass:.3f} Brass ({agg_cft:.1f} CFT)")
    st.write(f"**Steel:** {steel_kg_with_wastage:.2f} Kg")

# PDF Generation
st.divider()
st.subheader("📄 Download Reports")

def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "STC Construction - Material Estimate", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.cell(0, 8, f"Client: {client_name} | Site: {site} | Date: STC", ln=True)
    pdf.cell(0, 8, f"Work: {work_type} | Size: {length} x {width} x {thickness} ft", ln=True)
    pdf.cell(0, 8, f"Grade: {grade} | Total Volume: {volume_cum:.3f} CUM ({volume_cft:.2f} CFT)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Material Required (with wastage):", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Cement: {cement_bags_with_wastage:.2f} Bags (50kg) - Cost Rs {cement_cost:,.0f}", ln=True)
    pdf.cell(0, 8, f"Sand: {sand_brass:.2f} Brass ({sand_cft:.1f} CFT) - Cost Rs {sand_cost:,.0f}", ln=True)
    pdf.cell(0, 8, f"Aggregate: {agg_brass:.2f} Brass ({agg_cft:.1f} CFT) - Cost Rs {agg_cost:,.0f}", ln=True)
    pdf.cell(0, 8, f"Steel: {steel_kg_with_wastage:.2f} Kg - Cost Rs {steel_cost:,.0f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Total Estimated Cost: Rs {total_cost:,.0f}", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, "Note: This is estimate. Actual may vary 5-10% as per site conditions.", ln=True)
    return pdf.output(dest='S').encode('latin-1')

pdf_bytes = create_pdf()
st.download_button("📥 Download PDF Report", data=pdf_bytes, file_name=f"STC_Estimate_{client_name}.pdf", mime="application/pdf")

# DXF Generation
def create_dxf():
    doc = ezdxf.new()
    msp = doc.modelspace()
    # Draw rectangle for plan
    # Convert ft to drawing units (1 ft = 12 inches for dxf)
    l = length * 12
    w = width * 12
    msp.add_lwpolyline([(0,0), (l,0), (l,w), (0,w), (0,0)], close=True)
    msp.add_text(f"{length} ft", dxfattribs={"height": 4}).set_pos((l/2, -5))
    msp.add_text(f"{width} ft", dxfattribs={"height": 4}).set_pos((-15, w/2))
    msp.add_text(f"{client_name} - {site}", dxfattribs={"height": 6}).set_pos((0, w+10))
    buf = io.StringIO()
    doc.write(buf)
    return buf.getvalue().encode()

dxf_data = create_dxf()
st.download_button("📐 Download DXF Drawing (AutoCAD)", data=dxf_data, file_name=f"STC_Drawing_{client_name}.dxf", mime="application/dxf")

st.success("✅ App Ready! Now upload this file to GitHub to make online link.")
