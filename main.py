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
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        # Pastikan kolom tanggal berbentuk datetime
        data['tanggal_periksa'] = pd.to_datetime(data['tanggal_periksa'], errors='coerce')
        return data
    return None


# with st.sidebar:
#     st.image("simrs.png")

# Fungsi untuk reset state
def reset_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Aplikasi Streamlit
st.title('Data Analisis Pasien BPJS')

# Sidebar untuk file uploader dan tanggal
st.sidebar.title("Unggah File ")
uploaded_file = st.sidebar.file_uploader("", type=["csv"])

# Memuat data dari file yang diunggah
data = load_data(uploaded_file)

if data is not None:
    # Inisialisasi session state untuk tanggal jika belum ada
    if 'start_date' not in st.session_state:
        st.session_state['start_date'] = pd.to_datetime(data['tanggal_periksa'].min()).date()
    if 'end_date' not in st.session_state:
        st.session_state['end_date'] = pd.to_datetime(data['tanggal_periksa'].max()).date()

    # Menampilkan widget untuk memilih rentang tanggal di sidebar
    st.sidebar.write('Data Berdasarkan Tanggal Periksa:')
    start_date = st.sidebar.date_input('Tanggal Mulai', value=st.session_state['start_date'])
    end_date = st.sidebar.date_input('Tanggal Selesai', value=st.session_state['end_date'])

    # Update session state untuk tanggal
    st.session_state['start_date'] = start_date
    st.session_state['end_date'] = end_date

    # Pastikan tanggal mulai tidak melebihi tanggal selesai
    if start_date > end_date:
        st.sidebar.error('Tanggal mulai tidak boleh melebihi tanggal selesai.')

    # Tombol untuk refresh data
    if st.sidebar.button('Refresh Data'):
        # Filter data berdasarkan tanggal yang dipilih
        mask = (data['tanggal_periksa'] >= pd.to_datetime(start_date)) & (data['tanggal_periksa'] <= pd.to_datetime(end_date))
        filtered_data = data.loc[mask]
        st.session_state['filtered_data'] = filtered_data
    
        # Menampilkan notifikasi setelah refresh data
        st.sidebar.success('Data telah diperbarui.')

     # Tombol untuk menampilkan dashboard
    if st.sidebar.button('View Dashboard'):
        # Pastikan filtered_data sudah tersedia sebelum mencoba memprosesnya
        if 'filtered_data' in st.session_state:
            filtered_data = st.session_state['filtered_data']
            
            # Visualisasi Pygwalker hanya jika ada perubahan data
            if 'pygwalker_html' not in st.session_state or st.session_state['filtered_data'] is not filtered_data:
                st.session_state['pygwalker_html'] = pyg.walk(filtered_data).to_html()
            
            st.sidebar.success('Analysis Report telah diperbarui.')

            # Embed the stored HTML into the Streamlit app
            components.html(st.session_state['pygwalker_html'], height=1000, scrolling=True)
        else:
            st.error("Tidak ada data yang difilter. Silakan klik 'Refresh Data' untuk memfilter data terlebih dahulu.")
    
    if st.sidebar.button('Reset Data'):
        reset_state()
        st.experimental_rerun()

    # Hanya render visualisasi jika ada data yang difilter
    if 'filtered_data' in st.session_state:
        filtered_data = st.session_state['filtered_data']
        st.write('Menampilkan data terbaru berdasarkan filter tanggal:')
        st.write(filtered_data)

    else:
        st.write("Silakan unggah file CSV untuk dianalisis.")

    # Pesan instruksi tambahan
    st.sidebar.write('Klik "Refresh Data" untuk memperbarui data berdasarkan tanggal yang dipilih.')
else:
    st.write("Silakan unggah file CSV untuk memulai analisis.")
