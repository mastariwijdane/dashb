import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
import rasterio
from rasterio.transform import from_origin
from rasterio.enums import Resampling
import numpy as np
from streamlit_folium import folium_static as st_folium_static
import matplotlib.pyplot as plt
import os
import time


st.title("Split Panel Raster Maps")

# GeTiff files path
path1 = r"C:\Users\Alaa\Desktop\StreamlitHajji\Att1-Day0-.tif"
path=r"C:\Users\Alaa\Desktop\StreamlitHajji\Raster_Interpolation\tif1.tif"
path2 = r"C:\Users\Alaa\Desktop\StreamlitHajji\2016-2017.tif"
path3 = r"C:\Users\Alaa\Desktop\StreamlitHajji\2022-2023.tif"
left_layer=path
right_layer=path1
# Load the GeoTIFFs into Leafmap
m = leafmap.Map()
m.split_map(left_layer, right_layer)

# Display the map in Streamlit
st_folium_static(m)

