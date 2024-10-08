import streamlit as st
import pandas as pd
import pygwalker as pyg
import streamlit.components.v1 as components
from pygwalker.api.streamlit import StreamlitRenderer

# Mengatur halaman Streamlit
st.set_page_config(page_title="PyGWalker in Streamlit", layout="wide")
st.title("Aplikasi Visualisasi Data Real-time dengan Streamlit dan Pygwalker")

# Nama file CSV
csv_file = './data/juli 2024.csv'

# Fungsi untuk memuat CSV
@st.cache_resource
def load_data():
    # Membaca file CSV menggunakan pandas
    data = pd.read_csv(csv_file)
    return data

# Fungsi untuk mendapatkan renderer dari Pygwalker
@st.cache_resource
def get_pyg_renderer(df: pd.DataFrame) -> StreamlitRenderer:
    # Renderer ini dapat menggunakan konfigurasi JSON untuk kustomisasi Pygwalker
    return StreamlitRenderer(df, spec="./gw_config.json", spec_io_mode="rw")

# Tab untuk eksplorasi, data profiling, dan chart
tab1, tab2, tab3 = st.tabs(["Explorer", "Data Profiling", "Charts"])

# Menampilkan data dan Pygwalker dalam tab
with tab1:
    if st.button('Refresh Data'):
        data = load_data()
        
        # Menampilkan data terbaru
        with st.container():
            st.write("Menampilkan data terbaru:")
            st.write(data)
        
        # Menggunakan pygwalker untuk analisis dan visualisasi
        with st.container():
            st.write("Analisis dan Visualisasi dengan Pygwalker:")
            
            # Menghasilkan visualisasi Pygwalker dalam bentuk HTML
            pyg_html = pyg.walk(data).to_html()
            
            # Menampilkan HTML visualisasi dengan Streamlit components
            components.html(pyg_html, height=600, width=900, scrolling=False)
    
    # Renderer untuk interaktif explorer
    df = load_data()
    renderer = get_pyg_renderer(df)
    renderer.explorer()

with tab2:
    # Tab untuk profiling data
    st.write("Profiling Data:")
    renderer.explorer(default_tab="data")

with tab3:
    # Menampilkan beberapa visualisasi statis (chart 0 dan chart 1)
    st.subheader("Registered per Weekday")
    renderer.chart(0)
    
    st.subheader("Registered per Day")
    renderer.chart(1)

st.write('Klik "Refresh Data" untuk memperbarui data secara real-time.')
