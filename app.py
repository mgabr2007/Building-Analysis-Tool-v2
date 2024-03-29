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
import matplotlib.pyplot as plt
from collections import defaultdict
import tempfile
import os
import plotly.express as px  # For interactive plots
from fpdf import FPDF
from io import BytesIO
import base64

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

# Unified visualization function for both bar and pie charts using Plotly
def visualize_component_count(component_count, chart_type='bar'):
    labels, values = zip(*sorted(component_count.items(), key=lambda item: item[1], reverse=True)) if component_count else ((), ())
    if chart_type == 'bar':
        fig = px.bar(x=labels, y=values)
    elif chart_type == 'pie':
        fig = px.pie(values=values, names=labels)
    fig.update_layout(transition_duration=500)
    return fig

def detailed_analysis(ifc_file, product_type, sort_by=None):
    product_count = defaultdict(int)
    try:
        for product in ifc_file.by_type(product_type):
            product_name = product.Name if product.Name else "Unnamed"
            type_name = product_name.split(':')[0] if product_name else "Unnamed"
            product_count[type_name] += 1
    except Exception as e:
        st.error(f"Error during detailed analysis: {e}")
        return

    labels, values = zip(*product_count.items()) if product_count else ((), ())
    if values:
        fig = px.pie(values=values, names=labels, title=f"Distribution of {product_type} Products by Type")
        st.plotly_chart(fig)

        if sort_by:
            df = pd.DataFrame({'Type': labels, 'Count': values}).sort_values(by=sort_by, ascending=False)
            st.table(df)
    else:
        st.write(f"No products found for {product_type}.")
# Initialize session state for storing the user's analysis choice
if 'analysis_choice' not in st.session_state:
    st.session_state.analysis_choice = 'Welcome'

def set_analysis_choice(choice):
    st.session_state.analysis_choice = choice
    
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
                fig = visualize_component_count(component_count, chart_type)
                st.plotly_chart(fig)

                with st.expander("Show Detailed Component Analysis"):
                    product_types = sorted({entity.is_a() for entity in ifc_file.by_type('IfcProduct')})
                    selected_product_type = st.selectbox("Select a product type for detailed analysis", product_types, key="product_type")
                    sort_by = st.radio("Sort by", ["Type", "Count"], key="sort")
                    detailed_analysis(ifc_file, selected_product_type, sort_by)
            finally:
                os.remove(tmp_file_path)

def excel_file_analysis():
    uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'], key="excel")
    if uploaded_file is not None:
        df = read_excel(uploaded_file)
        if not df.empty:
            selected_columns = st.multiselect("Select columns to display", df.columns.tolist(), default=df.columns.tolist(), key="columns")
            if selected_columns:
                st.dataframe(df[selected_columns])
                if st.button("Visualize Data", key="visualize"):
                    visualize_data(df, selected_columns)
                if st.button("Generate Insights", key="insights"):
                    generate_insights(df[selected_columns])

def visualize_data(df, columns):
    for column in columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            fig = px.histogram(df, x=column)
            st.plotly_chart(fig)
        else:
            fig = px.bar(df, x=column, title=f"Bar chart of {column}")
            st.plotly_chart(fig)

def generate_insights(df):
    if not df.empty:
        st.write("Descriptive Statistics:", df.describe())
        # Placeholder for more sophisticated analysis or predictive modeling
# Function to convert Plotly figures into images and then into PDF
def convert_plotly_fig_to_pdf(fig, filename="visualization.pdf"):
    # Save the Plotly figure to an image
    fig_path = "temp_figure.png"
    fig.write_image(fig_path)
    # Create a PDF using FPDF and add the image
    pdf = FPDF()
    pdf.add_page()
    pdf.image(fig_path, 10, 8, 190)  # Adjust as needed
    # Save PDF to a bytes buffer
    pdf_output = BytesIO()
    pdf.output(pdf_output, 'F')
    pdf_output.seek(0)
    os.remove(fig_path)  # Clean up the image file
    # Convert the bytes buffer to a Base64 encoded string and create a download link
    b64 = base64.b64encode(pdf_output.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download PDF</a>'
    return href

# Visualization function adjusted to save figures
def visualize_component_count(component_count, chart_type='bar'):
    labels, values = zip(*sorted(component_count.items(), key=lambda item: item[1], reverse=True)) if component_count else ((), ())
    if chart_type == 'bar':
        fig = px.bar(x=labels, y=values)
    elif chart_type == 'pie':
        fig = px.pie(values=values, names=labels)
    fig.update_layout(transition_duration=500)
    # Return the figure for further processing (e.g., saving as PDF)
    return fig

# Adjusted analysis functions to include PDF export feature...
# Ensure these functions call visualize_component_count and then use the returned figure for PDF conversion

def welcome_page():
    st.title("IFC and Excel File Analysis Tool")
    st.write("""

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

""")

def main():
    st.sidebar.title("Navigation")
    if st.sidebar.button("Home"):
        set_analysis_choice("Welcome")
    if st.sidebar.button("Analyze IFC File"):
        set_analysis_choice("IFC File Analysis")
    if st.sidebar.button("Analyze Excel File"):
        set_analysis_choice("Excel File Analysis")

    if st.session_state.analysis_choice == 'Welcome':
        welcome_page()
    elif st.session_state.analysis_choice == "IFC File Analysis":
        ifc_file_analysis()
    elif st.session_state.analysis_choice == "Excel File Analysis":
        excel_file_analysis()

if __name__ == "__main__":
    main()

# Add copyright notice and license information to the sidebar
st.sidebar.markdown("""
----------------
#### Copyright Notice
Copyright (C) [2024] [Mostafa Gabr]. All rights reserved.

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).
""")
