import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
from folium.plugins import MarkerCluster  # Import MarkerCluster
import plotly.express as px
from streamlit.components.v1 import html
from fpdf import FPDF
from tempfile import NamedTemporaryFile
import base64

# Charger la GeoDataFrame depuis le fichier geoparquet
path = r"C:\Users\Alaa\Desktop\StreamlitHajji\Wiju.geoparquet"
gdf = gpd.read_parquet(path)

# Titre de la page
st.title("GeoAnalytic Dashboard")

# Fonction pour générer des dates séquentielles avec seulement le jour, le mois et l'année
def generate_dates(start_date, num_dates):
    # Convert the start_date string to a datetime object
    start_date = datetime.strptime(start_date, '%d-%m-%Y')
    
    return [(start_date - timedelta(days=i)).strftime('%d-%m-%Y') for i in range(num_dates)]

# Add a Selectbox to choose the date
start_date = '21-11-2023'  # Use a string for the starting date
num_dates = 7
dates = generate_dates(start_date, num_dates) 

date_rows_list = []
for date in dates:
    filtered_gdf = gdf[gdf['Date'] == date]
    rows_count = len(filtered_gdf)
    date_rows_list.append({'the date': date, 'nmbr_points': rows_count})

# Add a Selectbox to choose the date
selected_date_numpoint = st.selectbox("Select Date", date_rows_list)

# Retrieve the information for the selected date from the list
selected_date_str = selected_date_numpoint["the date"]
selected_date = datetime.strptime(selected_date_str, "%d-%m-%Y")
# Create a list of the selected date and the 6 previous dates
selected_dates = [selected_date - timedelta(days=i) for i in range(6, -1, -1)]

# Convert the datetime objects back to string format if needed
selected_dates_str = [date.strftime("%d-%m-%Y") for date in selected_dates]

# Filter the GeoDataFrame based on the selected date
filtered_gdf = gdf[gdf['Date'] == selected_date_str]

# Afficher la carte interactive avec Folium
m = folium.Map(location=[gdf.geometry.y.mean(), gdf.geometry.x.mean()], zoom_start=5)

# Add MarkerCluster to the map
marker_cluster = MarkerCluster(disable_clustering_at_zoom=8).add_to(m)  # Adjust the zoom level as needed

# Add markers to the MarkerCluster
for idx, row in filtered_gdf.iterrows():
    popup_content = f"<strong>Point ID:</strong> {idx}<br>" \
                    f"<strong>Nom:</strong> {row['Nom']}<br>" \
                    f"<strong>Densité_de_population(/m²):</strong> {row['Densité_de_population(/m²)']}<br>" \
                    f"<strong>Taux_Alphabétisme(%):</strong> {row['Taux_Alphabétisme(%)']}<br>"

    folium.Marker([row.geometry.y, row.geometry.x],
                  popup=popup_content).add_to(marker_cluster)

# Afficher la carte dans le Dashboard
folium_static(m)


# Gestion du clic sur la carte
selected_point = st.selectbox("Sélectionnez un point sur la carte", filtered_gdf.index)
selected_point_data = filtered_gdf.loc[selected_point]

# Créer des graphiques interactifs avec Plotly
fig = px.line(title="Données spatio-temporelles",
              labels={'value': 'Valeur', 'variable': 'Attribut'},
              width=800,
              height=500)


attribut1_columns = [f"Jour{j}-Pression(hPa)" for j in range(6, -1, -1)]
attribut1_values = [selected_point_data[col] for col in attribut1_columns]
fig.add_scatter(x=selected_dates_str, y=attribut1_values, mode='lines+markers', name='Pression(hPa)')

attribut2_columns = [f"Jour{k}-Vitesse_Vent(Km/h)" for k in range(6, -1, -1)]
attribut2_values = [selected_point_data[col] for col in attribut2_columns]
fig.add_scatter(x=selected_dates_str, y=attribut2_values, mode='lines+markers', name='Vitesse_Vent(Km/h)')

attribut3_columns = [f"Jour{n}-Température(en °C)" for n in range(6, -1, -1)]
attribut2_values = [selected_point_data[col] for col in attribut3_columns]
fig.add_scatter(x=selected_dates_str, y=attribut2_values, mode='lines+markers', name='Température(en °C)')

# Afficher le graphique interactif dans le Dashboard
st.plotly_chart(fig)

###### Download pdf
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