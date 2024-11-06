import streamlit as st
import pandas as pd
import pygwalker as pyg
import streamlit.components.v1 as components
from pygwalker.api.streamlit import init_streamlit_comm
import MySQLdb
import os
from datetime import datetime, timedelta

# Set page config for wide layout
st.set_page_config(
    page_title="Data Analisis SIMRS",
    layout="wide"
)

# Establish communication between pygwalker and Streamlit
init_streamlit_comm()

# Function to format `jam_reg` to HH:MM:SS
def format_jam_reg(data):
    """Format `jam_reg` column in the DataFrame to HH:MM:SS if needed."""
    if 'jam_reg' in data.columns:
        def format_time(value):
            if isinstance(value, str):  # if it's a string, try to parse it
                try:
                    if len(value) <= 5:  # Assume HH:MM format
                        return datetime.strptime(value, '%H:%M').strftime('%H:%M:%S')
                    elif len(value) == 8:  # Assume already in HH:MM:SS format
                        return value
                except ValueError:
                    return value  # return as-is if formatting fails
            elif isinstance(value, timedelta):  # if it's a timedelta, format it directly
                total_seconds = int(value.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"
            return value  # return the value as-is if it doesn't match expected types
        
        data['jam_reg'] = data['jam_reg'].apply(format_time)
    return data

# Function to load data from database based on query
@st.cache_data(show_spinner=True)
def init_connection(start_date, end_date):
    try:
        connection = MySQLdb.connect(
            host=os.getenv("DB_HOST", "192.168.11.5"), 
            user=os.getenv("DB_USER", "rsds_db"),
            passwd=os.getenv("DB_PASS", "rsdsD4t4b4s3"),
            db=os.getenv("DB_NAME", "rsds_db"),
            port=int(os.getenv("DB_PORT", 3306))
        )

        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Query tetap sama
        query = f"""
            SELECT
            reg_periksa.no_rawat,
            mlite_antrian_referensi.tanggal_periksa,
            reg_periksa.jam_reg,
            poliklinik.nm_poli,
            dokter.nm_dokter,
            pasien.nm_pasien,
            pasien.no_rkm_medis,
            reg_periksa.status_lanjut,
            reg_periksa.status_bayar,
            reg_periksa.kd_dokter,
            mlite_antrian_referensi.nomor_kartu,
            mlite_antrian_referensi.nomor_referensi,
            mlite_antrian_referensi.kodebooking,
            mlite_antrian_referensi.jenis_kunjungan,
            mlite_antrian_referensi.status_kirim,
            mlite_antrian_referensi.keterangan 
            FROM
                reg_periksa
                INNER JOIN pasien ON reg_periksa.no_rkm_medis = pasien.no_rkm_medis
                INNER JOIN penjab ON reg_periksa.kd_pj = penjab.kd_pj
                INNER JOIN dokter ON reg_periksa.kd_dokter = dokter.kd_dokter
                INNER JOIN poliklinik ON reg_periksa.kd_poli = poliklinik.kd_poli
                INNER JOIN mlite_antrian_referensi ON reg_periksa.no_rkm_medis = mlite_antrian_referensi.no_rkm_medis 
            WHERE
                mlite_antrian_referensi.tanggal_periksa BETWEEN '{start_date}' 
                AND '{end_date}' AND poliklinik.nm_poli != 'INSTALASI GAWAT DARURAT'
            ORDER BY
                CONCAT( mlite_antrian_referensi.tanggal_periksa, ' ', reg_periksa.jam_reg);
        """

        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        connection.close()

        df = pd.DataFrame(data)
        return format_jam_reg(df)  # Apply time formatting

    except MySQLdb.Error as err:
        st.error(f"Database Error: {err}")
        return None

# Function to reset state
def reset_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Streamlit app
st.title('Data Analisis Pasien BPJS')

# Sidebar for date filtering
st.sidebar.title("Filter Tanggal")

# Initialize date filter
start_date = st.sidebar.date_input('Tanggal Mulai')
end_date = st.sidebar.date_input('Tanggal Selesai')

# Convert selected dates to SQL string format
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

# Button to refresh data
if st.sidebar.button('Refresh Data'):
    if start_date and end_date:
        filtered_data = init_connection(start_date_str, end_date_str)
        if filtered_data is not None and not filtered_data.empty:
            st.session_state['filtered_data'] = filtered_data
            st.sidebar.success('Data telah diperbarui.')
        else:
            st.error('Tidak ada data yang ditemukan atau gagal memuat data.')

# Button to display dashboard
if st.sidebar.button('View Dashboard'):
    if 'filtered_data' in st.session_state:
        filtered_data = st.session_state['filtered_data']
        
        # Display Pygwalker visualization only if data changes
        if 'pygwalker_html' not in st.session_state or st.session_state['filtered_data'] is not filtered_data:
            try:
                st.session_state['pygwalker_html'] = pyg.walk(filtered_data).to_html()
            except Exception as e:
                st.error(f"Error creating visualization with pygwalker: {e}")
                st.write("Preview of the data:")
                st.write(filtered_data.head())  # Show a preview if visualization fails
        
        st.sidebar.success('Analysis Report telah diperbarui.')

        # Embed stored HTML into Streamlit app
        if 'pygwalker_html' in st.session_state:
            components.html(st.session_state['pygwalker_html'], height=1000, scrolling=True)
    else:
        st.error("Tidak ada data yang difilter. Silakan klik 'Refresh Data' untuk memfilter data terlebih dahulu.")

# Button to reset data
if st.sidebar.button('Reset Data'):
    reset_state()

# Render filtered data if available
if 'filtered_data' in st.session_state:
    filtered_data = st.session_state['filtered_data']
    st.write('Menampilkan data terbaru berdasarkan filter tanggal:')
    st.write(filtered_data)

else:
    st.write("Silakan filter data dengan tekan tombol refresh data.")

# Additional instruction message
st.sidebar.write('Klik "Refresh Data" untuk memperbarui data berdasarkan filter yang dipilih.')
