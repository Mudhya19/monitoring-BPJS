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
    page_title="Data Analisis BPJS",
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
            r.no_rawat,
            mr.tanggal_periksa,
            r.jam_reg,
            pl.nm_poli,
            d.nm_dokter,
            p.nm_pasien,
            p.no_rkm_medis,
            r.status_lanjut,
            # r.status_bayar,
            pj.png_jawab,
            # r.kd_dokter,
            mr.nomor_kartu,
            mr.nomor_referensi,
            mr.kodebooking,
            mr.jenis_kunjungan,
            mr.status_kirim,
            mr.keterangan
        FROM
            reg_periksa r
            INNER JOIN pasien p ON r.no_rkm_medis = p.no_rkm_medis
            INNER JOIN penjab pj ON r.kd_pj = pj.kd_pj
            INNER JOIN dokter d ON r.kd_dokter = d.kd_dokter
            INNER JOIN poliklinik pl ON r.kd_poli = pl.kd_poli
            INNER JOIN mlite_antrian_referensi mr ON r.no_rkm_medis = mr.no_rkm_medis
        WHERE
            mr.tanggal_periksa BETWEEN '{start_date}' AND '{end_date}'
            AND pl.nm_poli != 'INSTALASI GAWAT DARURAT'
            AND (mr.tanggal_periksa, r.jam_reg) IN (
                SELECT MIN(mr_inner.tanggal_periksa), MIN(r_inner.jam_reg)
                FROM reg_periksa r_inner
                INNER JOIN mlite_antrian_referensi mr_inner ON r_inner.no_rkm_medis = mr_inner.no_rkm_medis
                WHERE mr_inner.tanggal_periksa BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY r_inner.no_rkm_medis
            )
        GROUP BY
            r.no_rawat
        ORDER BY
            mr.tanggal_periksa, r.jam_reg;
        """

        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        connection.close()

        df = pd.DataFrame(data)
        return format_jam_reg(df.drop_duplicates())  # Apply time formatting

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
