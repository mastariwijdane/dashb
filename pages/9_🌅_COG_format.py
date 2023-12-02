import streamlit as st
import rasterio
from rasterio.windows import Window
from PIL import Image
import numpy as np
import tempfile
import os
from rio_cogeo.cogeo import cog_translate


st.title("COG TIFF")

# Function to read a GeoTIFF image with multiple bands
def read_image(file_path, band_order):
    with rasterio.open(file_path) as dataset:
        # Read the image data for the specified bands
        bands_data = [dataset.read(band) for band in band_order]

        # Stack the bands to create a multi-band image
        stacked_data = np.stack(bands_data, axis=-1)

        # Normalize the data to 0-255 for display
        normalized_data = (stacked_data / stacked_data.max()) * 255

        # Convert to uint8 to work with PIL
        uint8_data = normalized_data.astype(np.uint8)

        return uint8_data

# Function to convert GeoTIFF to COG
def convert_to_cog(input_path, output_path):
    with rasterio.open(input_path) as src_ds:
        profile = src_ds.profile.copy()

        # Specify the destination (dst) parameters
        dst_kwargs = {
            "driver": "COG",
            "blockxsize": 256,
            "blockysize": 256,
            "tiled": True,
            "compress": "deflate",
        }

        profile.update(**dst_kwargs)

        with rasterio.open(output_path, 'w', **profile) as dst_ds:
            cog_translate(src_ds, dst_ds, dst_kwargs=dst_kwargs)

def main():
    st.title("GeoTIFF and COG Image Viewer")

    # File uploader for GeoTIFF
    tiff_file = st.file_uploader("Upload GeoTIFF File", type=["tif", "tiff"])

    # Input band order with example for GeoTIFF
    example_band_order = "4, 3, 2"  # Example: enter the band order as a comma-separated list
    band_order_str = st.text_input(f"Enter the band order for GeoTIFF (e.g., '4,3,2' for RGB Sentinel-2 image):", value=example_band_order)
    band_order = [int(band.strip()) for band in band_order_str.split(',') if band.strip()]

    if tiff_file and band_order:
        # Save the uploaded GeoTIFF file to a temporary location
        temp_tiff_path = os.path.join(tempfile.gettempdir(), "uploaded_tiff.tif")
        with open(temp_tiff_path, "wb") as temp_file:
            temp_file.write(tiff_file.read())

        # Display the GeoTIFF image using PIL
        image_data = read_image(temp_tiff_path, band_order)
        image = Image.fromarray(image_data)
        st.image(image, caption="GeoTIFF Image", use_column_width=True)

        # Clean up temporary files
        os.remove(temp_tiff_path)

    # File uploader for COG
    cog_file = st.file_uploader("Upload COG File", type=["tif", "tiff"])

    # Button to trigger COG conversion
    if st.button("Convert GeoTIFF to COG") and tiff_file:
        # Save the uploaded GeoTIFF file to a temporary location
        temp_tiff_path = os.path.join(tempfile.gettempdir(), "uploaded_tiff.tif")
        with open(temp_tiff_path, "wb") as temp_file:
            temp_file.write(tiff_file.read())

        # Convert GeoTIFF to COG
        output_cog_path = os.path.join(tempfile.gettempdir(), "output_cog.tif")
        convert_to_cog(temp_tiff_path, output_cog_path)

        # Display the COG image using PIL
        cog_image = Image.open(output_cog_path)
        st.image(cog_image, caption="Converted COG Image", use_column_width=True)

        # Provide download link for COG file
        st.markdown(f"**Download COG Image:** [Download Link]({output_cog_path})")

        # Clean up temporary files
        os.remove(temp_tiff_path)
        os.remove(output_cog_path)

if __name__ == "__main__":
    main()
