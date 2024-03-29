"""
IFC and Excel File Analysis Tool

This Streamlit application provides an interactive interface for analyzing
IFC (Industry Foundation Classes) files and Excel spreadsheets. It allows
users to visualize component counts in IFC files and perform data analysis
and visualization on Excel files.

License:
This project is licensed under the GNU General Public License v3.0.
For more details, see the LICENSE file in the root directory of this source tree
or visit https://www.gnu.org/licenses/gpl-3.0.en.html.

Copyright:
Copyright (C) [2024] [Mostafa Gabr].
All rights reserved.

"""
import streamlit as st
import pandas as pd
import numpy as np
import ifcopenshell
from collections import defaultdict
import tempfile
import os
from plotly.io import to_image
from fpdf import FPDF
from PIL import Image
import io

# Function to count building components in an IFC file
def count_building_components(ifc_file):
    component_count = defaultdict(int)
    try:
        for ifc_entity in ifc_file.by_type('IfcProduct'):
            component_count[ifc_entity.is_a()] += 1
    except Exception as e:
        st.error(f"Error processing IFC file: {e}")
    return component_count

# Function to read Excel file with caching and error handling
@st.cache(hash_funcs={tempfile.NamedTemporaryFile: lambda _: None}, allow_output_mutation=True)
def read_excel(file):
    try:
        return pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        st.error(f"Failed to read Excel file: {e}")
        return pd.DataFrame()

# Function to convert Plotly figures to PDF
def fig_to_pdf(fig, filename='visualization.pdf'):
    img_bytes = to_image(fig, format='png')
    img = Image.open(io.BytesIO(img_bytes))
    pdf = FPDF(unit="pt", format=[img.width, img.height])
    pdf.add_page()
    pdf.image(img, 0, 0)
    pdf.output(filename)

    return filename

# Visualization function for both bar and pie charts using Plotly
def visualize_component_count(component_count, chart_type='bar'):
    import plotly.express as px
    labels, values = zip(*sorted(component_count.items(), key=lambda item: item[1], reverse=True)) if component_count else ((), ())
    if chart_type == 'bar':
        fig = px.bar(x=labels, y=values)
    elif chart_type == 'pie':
        fig = px.pie(values=values, names=labels)
    st.plotly_chart(fig, use_container_width=True)

    # Export to PDF button
    if st.button('Export to PDF'):
        pdf_path = fig_to_pdf(fig)
        with open(pdf_path, "rb") as pdf_file:
            PDFbyte = pdf_file.read()
        
        st.download_button(label="Download PDF",
                           data=PDFbyte,
                           file_name="visualization.pdf",
                           mime="application/octet-stream")

# Analysis functions...
def ifc_file_analysis():
    uploaded_file = st.file_uploader("Choose an IFC file", type=['ifc'], key="ifc")
    if uploaded_file is not None:
        with st.spinner('Processing IFC file...'):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ifc') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                ifc_file = ifcopenshell.open(tmp_file_path)
                component_count = count_building_components(ifc_file)
                chart_type = st.radio("Chart Type", ['bar', 'pie'], key="chart")
                visualize_component_count(component_count, chart_type)
            finally:
                os.remove(tmp_file_path)

# Main function...
def main():
    st.title("IFC and Excel File Analysis Tool")
    app_mode = st.sidebar.selectbox("Choose the type of analysis", ["Welcome", "IFC File Analysis", "Excel File Analysis"])

    if app_mode == "Welcome":
        st.write("Select an analysis type from the sidebar to get started.")
    elif app_mode == "IFC File Analysis":
        ifc_file_analysis()
    elif app_mode == "Excel File Analysis":
        # Placeholder for Excel analysis functionality
        st.write("Excel file analysis functionality will be here.")

if __name__ == "__main__":
    main()

