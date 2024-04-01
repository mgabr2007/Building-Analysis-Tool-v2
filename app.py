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
import plotly.graph_objects as go

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
def visualize_component_count(component_count, chart_type='Bar Chart'):
    labels, values = zip(*sorted(component_count.items(), key=lambda item: item[1], reverse=True)) if component_count else ((), ())
    if chart_type == 'Bar Chart':
        fig = px.bar(x=labels, y=values)
    elif chart_type == 'Pie Chart':
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
                chart_type = st.radio("Chart Type", options=['Bar Chart', 'Pie Chart'], key="chart")
                fig = visualize_component_count(component_count, chart_type)
                st.plotly_chart(fig)

                with st.expander("Show Detailed Component Analysis"):
                    product_types = sorted({entity.is_a() for entity in ifc_file.by_type('IfcProduct')})
                    selected_product_type = st.selectbox("Select a product type for detailed analysis", product_types, key="product_type")
                    sort_by = st.select_slider("Sort by", ["Type", "Count"], value='Count', key="sort")
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
# Comparison Analysis Functions
def compare_ifc_files(ifc_file1, ifc_file2):
    # Compare the building components of two IFC files
    components1 = count_building_components(ifc_file1)
    components2 = count_building_components(ifc_file2)

    # Initialize a dictionary to store comparison results
    comparison_result = defaultdict(dict)

    # Get all unique component types from both files
    all_component_types = set(components1.keys()) | set(components2.keys())

    # Loop through each component type and compare
    for component_type in all_component_types:
        count1 = components1.get(component_type, 0)
        count2 = components2.get(component_type, 0)
        
        # Store comparison data
        comparison_result[component_type]['File 1 Count'] = count1
        comparison_result[component_type]['File 2 Count'] = count2
        comparison_result[component_type]['Difference'] = count1 - count2

    return comparison_result

def compare_ifc_files_ui():
    st.title("Compare IFC Files")
    # Instructions for the user
    st.write("""
    ### Instructions for Comparing IFC Files:

    Please follow the steps below to compare the components of two IFC (Industry Foundation Classes) files:

    1. **Upload First IFC File:** Click on the "Choose File" button below labeled **"Choose the first IFC file"**. Navigate to the location of the first IFC file on your device and select it for upload.

    2. **Upload Second IFC File:** Similarly, use the second "Choose File" button labeled **"Choose the second IFC file"** to upload the second IFC file you wish to compare with the first one.

    After uploading both files, the application will automatically process and compare them, displaying the comparison results on this page. This comparison will help you understand the differences in building components, such as walls, doors, and windows, between the two IFC files.
    """)
    

    uploaded_file1 = st.file_uploader("Choose the first IFC file", type=['ifc'], key="ifc1")
    uploaded_file2 = st.file_uploader("Choose the second IFC file", type=['ifc'], key="ifc2")

    if uploaded_file1 and uploaded_file2:
        file_name1 = uploaded_file1.name
        file_name2 = uploaded_file2.name

        with tempfile.NamedTemporaryFile(delete=False, suffix='.ifc') as tmp_file1, \
             tempfile.NamedTemporaryFile(delete=False, suffix='.ifc') as tmp_file2:
            tmp_file1.write(uploaded_file1.getvalue())
            tmp_file2.write(uploaded_file2.getvalue())
            tmp_file1_path = tmp_file1.name
            tmp_file2_path = tmp_file2.name

        ifc_file1 = ifcopenshell.open(tmp_file1_path)
        ifc_file2 = ifcopenshell.open(tmp_file2_path)
        comparison_result = compare_ifc_files(ifc_file1, ifc_file2)

        # Let the user select which component types to compare
        all_component_types = list(comparison_result.keys())
        selected_components = st.multiselect('Select component types to compare:', all_component_types, default=all_component_types)

        # Filter the comparison_result based on the selected components
        filtered_comparison_result = {component: comparison_result[component] for component in selected_components}

        # Generate and display the bar chart for selected components
        component_types = list(filtered_comparison_result.keys())
        counts_file1 = [filtered_comparison_result[component]['File 1 Count'] for component in component_types]
        counts_file2 = [filtered_comparison_result[component]['File 2 Count'] for component in component_types]
        differences = [filtered_comparison_result[component]['Difference'] for component in component_types]

        fig = go.Figure(data=[
            go.Bar(name=file_name1, x=component_types, y=counts_file1),
            go.Bar(name=file_name2, x=component_types, y=counts_file2),
            go.Bar(name='Difference', x=component_types, y=differences)
        ])
        fig.update_layout(barmode='group', title_text='Selected IFC File Component Comparison', xaxis_title="Component Type", yaxis_title="Count")
        st.plotly_chart(fig)

        # Generate and display the pie chart for overall differences
        fig_pie = go.Figure(data=[go.Pie(labels=component_types, values=differences, title='Overall Differences in Selected Components')])
        st.plotly_chart(fig_pie)

        os.remove(tmp_file1_path)
        os.remove(tmp_file2_path)

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

# Main function updated for button-based navigation
def main():
    st.sidebar.title("Navigation")
    # Navigation buttons
    if st.sidebar.button("Home"):
        set_analysis_choice("Welcome")
    if st.sidebar.button("Analyze IFC File"):
        set_analysis_choice("Analyze IFC File")
    if st.sidebar.button("Analyze Excel File"):
        set_analysis_choice("Analyze Excel File")
    if st.sidebar.button("Compare IFC Files"):
        set_analysis_choice("Compare IFC Files")


    # Handling the display based on the user's choice
    if 'analysis_choice' not in st.session_state:
        st.session_state.analysis_choice = "Welcome"

    if st.session_state.analysis_choice == "Welcome":
        welcome_page()
    elif st.session_state.analysis_choice == "Analyze IFC File":
        ifc_file_analysis()
    elif st.session_state.analysis_choice == "Analyze Excel File":
        excel_file_analysis()
    elif st.session_state.analysis_choice == "Compare IFC Files":
        compare_ifc_files_ui()  # Ensure this function does not require arguments and is defined correctly


if __name__ == "__main__":
    main()
# Add copyright notice and license information to the sidebar
st.sidebar.markdown("""
----------------
#### Copyright Notice
Copyright (C) [2024] [Mostafa Gabr]. All rights reserved.

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).
""")
