
import streamlit as st
import geopandas as gpd
import plotly.express as px
import pandas as pd
import numpy as np
from shapely.geometry import Point
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import from_origin
from io import BytesIO
from fpdf import FPDF
from tempfile import NamedTemporaryFile
import base64

path = r"C:\Users\wijda\Downloads\Dashboard_Streamlit\pages\Wiju.geoparquet"
# Charger le GeoParquet
gdf = gpd.read_parquet(path)

# Title for the Streamlit app

st.title("Cartographie du jour J")
# Sidebar for selecting the day
selected_day = st.selectbox('Select Day', ['Jour0', 'Jour1', 'Jour2','Jour3','Jour4','Jour5','Jour6'])

# Get the properties columns for the selected day
properties_for_day = [col for col in gdf.columns if col.startswith(selected_day)]

# Choose the property using a selectbox
selected_property = st.selectbox(f'Select Property for {selected_day}', properties_for_day)

# Create a proportional symbols map for the selected property and day
fig = px.scatter_mapbox(gdf, 
                        lat=gdf.geometry.y, 
                        lon=gdf.geometry.x, 
                        size=selected_property,
                        mapbox_style="carto-positron",
                        title=f'Proportional Symbols Map for {selected_property} on {selected_day}',
                        )

# Display the map in the Streamlit app
st.plotly_chart(fig)

# Sidebar with the slider for day selection
selected_day0 = st.slider('Select Day', min_value=-5, max_value=0, value=0)



def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'


    # Export the page to PDF
export_as_pdf = st.button("Export Report")

if export_as_pdf:
    pdf = FPDF()

    pdf.add_page()

    # Save Plotly figure as a PNG image
    with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        fig.write_image(tmpfile.name)

        # Embed the PNG image in the PDF
        pdf.image(tmpfile.name, 10, 10, 200, 100)

    # Provide a download link for the generated PDF
    html_link = create_download_link(pdf.output(dest="S").encode("latin-1"), "testfile")
    st.markdown(html_link, unsafe_allow_html=True)