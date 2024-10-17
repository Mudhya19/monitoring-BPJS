import streamlit as st
import pandas as pd
import pygwalker as pyg
import streamlit.components.v1 as components
from pygwalker.api.streamlit import init_streamlit_comm

# Set page config for wide layout
st.set_page_config(
    page_title="Data Analisis SIMRS",
    layout="wide"
)

# Establish communication between pygwalker and streamlit
init_streamlit_comm()

# Fungsi untuk memuat CSV
@st.cache_data
def load_data(uploaded_file):
    # Membaca file CSV menggunakan pandas jika file diunggah
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        # Pastikan kolom tanggal berbentuk datetime
        data['tanggal_periksa'] = pd.to_datetime(
            data['tanggal_periksa'], errors='coerce')
        return data
    return None

# Aplikasi Streamlit
st.title('Data Analisis BPJS Antrol')

# Menambahkan widget untuk mengunggah file CSV
uploaded_file = st.file_uploader("Unggah file CSV Anda", type=["csv"])

# Memuat data dari file yang diunggah
data = load_data(uploaded_file)

if data is not None:
    # Memulai sesi state jika belum ada
    if 'start_date' not in st.session_state:
        st.session_state['start_date'] = pd.to_datetime(
            data['tanggal_periksa'].min()).date()
    if 'end_date' not in st.session_state:
        st.session_state['end_date'] = pd.to_datetime(
            data['tanggal_periksa'].max()).date()

    # Menampilkan widget untuk memilih rentang tanggal
    st.write('Filter Data Berdasarkan Tanggal Periksa:')
    start_date = st.date_input('Tanggal Mulai', value=st.session_state['start_date'])
    end_date = st.date_input('Tanggal Selesai', value=st.session_state['end_date'])

    # Update session state untuk tanggal
    st.session_state['start_date'] = start_date
    st.session_state['end_date'] = end_date

    # Pastikan tanggal mulai tidak melebihi tanggal selesai
    if start_date > end_date:
        st.error('Tanggal mulai tidak boleh melebihi tanggal selesai.')

    # Tombol untuk refresh data
    if st.button('Refresh Data'):
        # Filter data berdasarkan tanggal yang dipilih
        mask = (data['tanggal_periksa'] >= pd.to_datetime(start_date)) & (data['tanggal_periksa'] <= pd.to_datetime(end_date))
        st.session_state['filtered_data'] = data.loc[mask]

        # Menampilkan notifikasi hanya setelah refresh data
        st.success('Data telah diperbarui.')

    # Menampilkan data terbaru berdasarkan filter tanggal
    if 'filtered_data' in st.session_state:
        filtered_data = st.session_state['filtered_data']
        st.write('Menampilkan data terbaru berdasarkan filter tanggal:')
        st.write(filtered_data)

        # Membuat kontainer kosong
        container = st.empty()

        with container:
            st.write('Analisis dan Visualisasi dengan Pygwalker:')
            # Generate the HTML using Pygwalker
            pyg_html = pyg.walk(filtered_data).to_html()

            # Embed the HTML into the Streamlit app
            components.html(pyg_html, height=1000, scrolling=True)
else:
    st.write("Silakan unggah file CSV untuk dianalisis.")

# Pesan instruksi tambahan
st.write('Klik "Refresh Data" untuk memperbarui data berdasarkan tanggal yang dipilih.')
