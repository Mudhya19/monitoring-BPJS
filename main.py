import streamlit as st
import pandas as pd
import pygwalker as pyg
import streamlit.components.v1 as components
from pygwalker.api.streamlit import StreamlitRenderer

# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="Data Analisis BPJS Antrol",
    layout="wide"
)

# Nama file CSV
csv_file = './data/juli 2024.csv'

# Fungsi untuk memuat CSV
@st.cache_data
def load_data():
    # Membaca file CSV menggunakan pandas
    data = pd.read_csv(csv_file)
    
    # Pastikan kolom tanggal berbentuk datetime
    data['tanggal_periksa'] = pd.to_datetime(data['tanggal_periksa'], errors='coerce')
    return data

# Fungsi untuk mendapatkan renderer pygwalker (menggunakan caching untuk efisiensi)
@st.cache_resource
def get_pyg_renderer(df: pd.DataFrame) -> "StreamlitRenderer":
    # Jika ingin menyimpan konfigurasi chart, set `spec_io_mode="rw"`
    return StreamlitRenderer(df, spec="./gw_config.json", spec_io_mode="rw")

# Aplikasi Streamlit
st.title('Data Analisis BPJS Antrol')

st.write('Aplikasi ini menampilkan data secara real-time dari file CSV yang terus diperbarui.')

# Memuat data
data = load_data()

# Menampilkan widget untuk memilih rentang tanggal
st.write('Filter Data Berdasarkan Tanggal Periksa:')
start_date = st.date_input('Tanggal Mulai', value=pd.to_datetime(data['tanggal_periksa'].min()).date())
end_date = st.date_input('Tanggal Selesai', value=pd.to_datetime(data['tanggal_periksa'].max()).date())

# Pastikan tanggal mulai tidak melebihi tanggal selesai
if start_date > end_date:
    st.error('Tanggal mulai tidak boleh melebihi tanggal selesai.')

# Tombol untuk refresh data
if st.button('Refresh Data'):
    # Filter data berdasarkan tanggal yang dipilih
    mask = (data['tanggal_periksa'] >= pd.to_datetime(start_date)) & (data['tanggal_periksa'] <= pd.to_datetime(end_date))
    filtered_data = data.loc[mask]

    st.write('Menampilkan data terbaru berdasarkan filter tanggal:')
    with st.container():
        st.write(filtered_data)

    # Menggunakan container untuk memuat Pygwalker dengan renderer
    st.write('Analisis dan Visualisasi dengan Pygwalker:')
    
    # Membuat renderer pygwalker
    renderer = get_pyg_renderer(filtered_data)

    # Render Pygwalker explorer secara responsif
    renderer.render_explore()

# Pesan instruksi tambahan
st.write('Klik "Refresh Data" untuk memperbarui data secara real-time.')