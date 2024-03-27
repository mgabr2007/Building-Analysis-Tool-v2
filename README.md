IFC and Excel File Analysis Tool V 2
This Streamlit application provides an interactive interface for analyzing IFC (Industry Foundation Classes) files and Excel spreadsheets. It allows users to visualize component counts in IFC files and perform data analysis and visualization on Excel files.

Features
IFC File Analysis: Upload IFC files to count and visualize different building components.
Excel File Analysis: Upload Excel files to display data, visualize selected columns, and generate basic statistical insights.
Installation
Before running the application, ensure you have Python installed on your system. This application requires Python 3.6 or later.

Clone the Repository (if applicable) or download the application code to your local machine.

Create a Virtual Environment (recommended):

python -m venv venv
Activate the virtual environment:

On Windows:
venv\Scripts\activate
On macOS/Linux:
source venv/bin/activate
Install Dependencies:

Install the required Python packages using the following command:

pip install streamlit pandas numpy matplotlib ifcopenshell
Usage
Navigate to the directory containing the application code in your terminal or command prompt.

Run the application using Streamlit:

streamlit run app.py
The command will start the Streamlit server and open the application in your default web browser. If the application does not automatically open, you can manually navigate to the URL provided by Streamlit in the terminal output (typically http://localhost:8501).

Use the sidebar to select the type of analysis (IFC File Analysis or Excel File Analysis) and follow the on-screen instructions to upload files and visualize data.

Customization
IFC Analysis: Extend the count_building_components and detailed_analysis functions to include more detailed analysis of IFC files based on specific project requirements.
Excel Analysis: Modify the visualize_data and generate_insights functions to include more advanced data visualization and insights generation techniques.
Contributing
Contributions to improve the application are welcome. Please follow the standard fork-branch-PR workflow.

Fork the repository.
Create a new branch for your feature or fix.
Commit your changes.
Push the branch to your fork.
Submit a pull request.
License
This project is licensed under the GNU General Public License (GPL). For more details, see the LICENSE file included with the project or visit the GNU General Public License GPL webpage.
