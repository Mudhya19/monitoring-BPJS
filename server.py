import streamlit as st
import pandas as pd
import pygwalker as pyg
import streamlit.components.v1 as components
from pygwalker.api.streamlit import init_streamlit_comm
import mysql.connector
import MySQLdb
import os

# Set page config for wide layout
st.set_page_config(
    page_title="Data Analisis SIMRS",
    layout="wide"
)

# Establish communication between pygwalker and Streamlit
init_streamlit_comm()

# Fungsi untuk memuat CSV
# @st.cache_data
# def load_data(uploaded_file):
#     if uploaded_file is not None:
#         data = pd.read_csv(uploaded_file)
#         # Pastikan kolom tanggal berbentuk datetime
#         data['tanggal_periksa'] = pd.to_datetime(data['tanggal_periksa'], errors='coerce')
#         return data
#     return None


# with st.sidebar:
#     st.image("simrs.png")

# Fungsi untuk memuat data dari database berdasarkan query
@st.cache_data(show_spinner=True)
def init_connection(start_date, end_date):
    try:
        connection = MySQLdb.connect(
            host=os.getenv("DB_HOST", "192.168.11.30"),
            user=os.getenv("DB_USER", "rsds_db_20241012"),
            passwd=os.getenv("DB_PASS", "rsds_db_20241012"),
            db=os.getenv("DB_NAME", "rsds_db_20241012"),
            port=int(os.getenv("DB_PORT", 3306))
        )

        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Query tetap sama
        query = f"""
        SELECT pasien.no_peserta, pasien.no_rkm_medis, pasien.no_ktp, pasien.no_tlp, reg_periksa.no_reg, 
            reg_periksa.no_rawat, reg_periksa.tgl_registrasi, reg_periksa.kd_dokter, dokter.nm_dokter, 
            reg_periksa.kd_poli, poliklinik.nm_poli, reg_periksa.stts_daftar, reg_periksa.no_rkm_medis
        FROM reg_periksa 
        INNER JOIN pasien ON reg_periksa.no_rkm_medis = pasien.no_rkm_medis 
        INNER JOIN dokter ON reg_periksa.kd_dokter = dokter.kd_dokter 
        INNER JOIN poliklinik ON reg_periksa.kd_poli = poliklinik.kd_poli 
        WHERE reg_periksa.tgl_registrasi BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY CONCAT(reg_periksa.tgl_registrasi, ' ', reg_periksa.jam_reg);
        """

        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        connection.close()

        return pd.DataFrame(data)

    except MySQLdb.Error as err:
        st.error(f"Error: {err}")
        return None

# Fungsi untuk reset state
def reset_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Aplikasi Streamlit
st.title('Data Analisis Pasien BPJS')

# # Sidebar untuk file uploader dan tanggal
# st.sidebar.title("Unggah File ")
# uploaded_file = st.sidebar.file_uploader("", type=["csv"])

# # Memuat data dari file yang diunggah
# data = load_data(uploaded_file)

# Sidebar untuk filter tanggal
st.sidebar.title("Filter Tanggal")

# Inisialisasi filter tanggal
start_date = st.sidebar.date_input('Tanggal Mulai')
end_date = st.sidebar.date_input('Tanggal Selesai')

# Pastikan tanggal yang dipilih diubah menjadi string format SQL
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

# Tombol untuk refresh data
if st.sidebar.button('Refresh Data'):
    if start_date and end_date:
        # Filter berdasarkan tanggal
        filtered_data = init_connection(start_date_str, end_date_str)
        if filtered_data is not None:
            st.session_state['filtered_data'] = filtered_data
            st.sidebar.success('Data telah diperbarui.')
        else:
            st.error('Gagal memuat data.')

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

# Tombol untuk reset data
if st.sidebar.button('Reset Data'):
    reset_state()

# Render data yang telah difilter jika ada
if 'filtered_data' in st.session_state:
    filtered_data = st.session_state['filtered_data']
    st.write('Menampilkan data terbaru berdasarkan filter tanggal:')
    st.write(filtered_data)

else:
    st.write("Silakan filter data menggunakan sidebar.")

# Pesan instruksi tambahan
st.sidebar.write('Klik "Refresh Data" untuk memperbarui data berdasarkan filter yang dipilih.')
