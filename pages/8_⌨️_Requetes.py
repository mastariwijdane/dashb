import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static as st_folium_static
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import plotly.express as px

# Load GeoParquet
path = r"C:\Users\Alaa\Desktop\StreamlitHajji\Wiju.geoparquet"
gdf = gpd.read_parquet(path)

# Title for the Streamlit app
st.title("Spatial Filtering and Proportional Symbols Map with Streamlit")

# Sidebar for selecting the task
selected_task = st.selectbox('Select Task', ['Part 1: Proportional Symbols Map', 'Part 2: Spatial Filtering'])

# Part 1: Proportional Symbols Map
if selected_task == 'Part 1: Proportional Symbols Map':
    st.sidebar.header('Proportional Symbols Map Settings')
    # Sidebar for selecting the day
    selected_day = st.sidebar.selectbox('Select Day', ['Jour0', 'Jour1', 'Jour2', 'Jour3', 'Jour4', 'Jour5', 'Jour6'])

# Get the properties columns for the selected day
    properties_for_day = [col for col in gdf.columns if col.startswith(selected_day)]

# Choose the property using a selectbox
    selected_property = st.selectbox(f'Select Property for {selected_day}', properties_for_day)

# Interval slider for setting the filter value range
    filter_value_range = st.sidebar.slider('Select Filter Value Range', min_value=gdf[selected_property].min(), max_value=gdf[selected_property].max(), value=(gdf[selected_property].min(), gdf[selected_property].max()), key="filter_value_range")

# Choose the filter operator
    filter_operator = st.sidebar.radio('Select Filter Operator', ['inside', 'outside'], key="filter_operator")

# Apply attribute filter
    if filter_operator == 'inside':
        filtered_data = gdf[(gdf[selected_property] >= filter_value_range[0]) & (gdf[selected_property] <= filter_value_range[1])]
    else:  # 'outside'
        filtered_data = gdf[(gdf[selected_property] < filter_value_range[0]) | (gdf[selected_property] > filter_value_range[1])]

# Create a proportional symbols map for the selected property and day
    fig = px.scatter_mapbox(filtered_data, 
                        lat=filtered_data.geometry.y, 
                        lon=filtered_data.geometry.x, 
                        size=selected_property,
                        mapbox_style="carto-positron",
                        title=f'Proportional Symbols Map for {selected_property} on {selected_day}',
                        )

# Display the map in the Streamlit app
    st.plotly_chart(fig)

# Create the raster map with GeoPandas
    fig, ax = plt.subplots(figsize=(20, 8))
    filtered_data.plot(column=selected_property, cmap='viridis', legend=True, ax=ax)
    plt.axis('off')

# Save the map to a temporary file in PNG format
    tmpfile = "temp_map.png"
    plt.savefig(tmpfile, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()

# Load the base map with folium
    m = folium.Map(location=[filtered_data.geometry.y.mean(), filtered_data.geometry.x.mean()], zoom_start=5)   


# Part 2: Spatial Filtering
elif selected_task == 'Part 2: Spatial Filtering':
    st.sidebar.header('Spatial Filtering')


# Sidebar for spatial filtering options
    spatial_filter_option = st.sidebar.radio('Select Spatial Filter Option', ['Point Buffer', 'Draw Polygon'], key="spatial_filter_option")

# Filter based on point buffer or drawn polygon
    if spatial_filter_option == 'Point Buffer':
    # Select a point to create a buffer
        selected_point = st.sidebar.selectbox('Select Point for Buffer', gdf.geometry, format_func=lambda x: f"({x.x}, {x.y})", key="selected_point")
    
    # Buffer size slider
        buffer_size = st.sidebar.slider('Select Buffer Size', min_value=0.001, max_value=30.0, value=0.01, step=0.001, key="buffer_size")

    # Create a buffer around the selected point
        buffer_geometry = selected_point.buffer(buffer_size)

    # Filter GeoDataFrame based on the buffer
        filtered_data = gdf[gdf.geometry.within(buffer_geometry)]

    elif spatial_filter_option == 'Draw Polygon':
    # Use Folium to draw a polygon on the map
        m = folium.Map(location=[gdf.geometry.y.mean(), gdf.geometry.x.mean()], zoom_start=5)
        drawn_polygon = st.sidebar.folium_static(m, width=800, height=600, key="drawn_polygon")

    # Convert the drawn polygon to a Shapely geometry
        if drawn_polygon:
            coords = drawn_polygon['geometry']['coordinates'][0]
            polygon_geometry = Polygon(coords)

        # Filter GeoDataFrame based on the drawn polygon
            filtered_data = gdf[gdf.geometry.within(polygon_geometry)]
        else:
            filtered_data = gdf  # Show all data if no polygon is drawn
    
    # Display the filtered GeoDataFrame
    st.write("Filtered GeoDataFrame:")
    st.write(filtered_data)

    # Create a proportional symbols map for the selected property and day
    fig = folium.Map(location=[filtered_data.geometry.y.mean(), filtered_data.geometry.x.mean()], zoom_start=5)

    # Display the filtered GeoDataFrame on the map
    for _, row in filtered_data.iterrows():
        folium.Marker([row.geometry.y, row.geometry.x]).add_to(fig)

    # Display the map in the Streamlit app
    st_folium_static(fig)