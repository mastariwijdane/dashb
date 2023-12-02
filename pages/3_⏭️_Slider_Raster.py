

import streamlit as st
import geopandas as gpd
import plotly.express as px
import pandas as pd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt 
import folium

from streamlit_folium import folium_static as st_folium_static

# GeoParquet file path
path = r"C:\Users\Alaa\Desktop\StreamlitHajji\Wiju.geoparquet"

# Load your GeoDataFrame from GeoParquet
gdf = gpd.read_parquet(path)

# Title for the Streamlit app
st.title("Slider Raster")
# Sidebar for selecting the day with a slider
selected_day = st.sidebar.slider('Select Day', min_value=0, max_value=6, step=1)

# Get the properties columns for the selected day
properties_for_day = [col for col in gdf.columns if col.startswith(f'Jour{selected_day}')]

# Choose the property using a slider
selected_property_index = st.slider(f'Select Property for Day {selected_day}', min_value=0, max_value=len(properties_for_day)-1, step=1)
selected_property = properties_for_day[selected_property_index]

selected_day_column = f"{selected_property}"

if selected_day_column in gdf.columns:
    filtered_data = gdf[gdf[selected_day_column].notnull()]

    # CrÃ©er la carte raster avec Geopandas
    fig, ax = plt.subplots(figsize=(10, 8))
    filtered_data.plot(column=selected_day_column, cmap='viridis', legend=True, ax=ax)
    plt.axis('off')

else:
    st.warning(f"La colonne {selected_day_column} n'existe pas dans le GeoDataFrame.")
    # Clear the previous plot if it exists
    st.empty()

  
# Enregistrer la carte dans un fichier temporaire au format PNG
tmpfile = "temp_map.png"
plt.savefig(tmpfile, bbox_inches="tight", pad_inches=0.1, transparent=True)
plt.close()
# ...

# Charger la carte de base avec folium
m = folium.Map(location=[filtered_data.geometry.y.mean(), filtered_data.geometry.x.mean()], zoom_start=5)

# Ajouter la carte raster Ã  la carte de base avec GeoJson
folium.raster_layers.ImageOverlay(
    name="Raster Map",
    image=tmpfile,
    bounds=[[filtered_data.geometry.y.min(), filtered_data.geometry.x.min()],
            [filtered_data.geometry.y.max(), filtered_data.geometry.x.max()]],
    opacity=0.7,
).add_to(m)

# Afficher la carte de base dans Streamlit
st_folium_static(m)