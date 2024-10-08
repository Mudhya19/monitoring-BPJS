import streamlit as st
import pandas as pd
import pygwalker as pyg
import streamlit.components.v1 as components

# Nama file CSV
csv_file = './data/juli 2024.csv'

# Fungsi untuk memuat CSV
def load_data():
    # Membaca file CSV menggunakan pandas
    data = pd.read_csv(csv_file)
    return data

# Aplikasi Streamlit
st.title('Aplikasi Visualisasi Data Real-time dengan Streamlit dan Pygwalker')

st.write('Aplikasi ini menampilkan data secara real-time dari file CSV yang terus diperbarui.')

# Menampilkan data secara berkala
if st.button('Refresh Data'):
    data = load_data()
    st.write('Menampilkan data terbaru:')
    with st.container():
        st.write(data)

    # Menggunakan container untuk memuat Pygwalker
    with st.container():
        st.write('Analisis dan Visualisasi dengan Pygwalker:')
        
        # Menghasilkan visualisasi Pygwalker dalam bentuk HTML
        pyg_html = pyg.walk(data).to_html()
        
        # Menampilkan HTML visualisasi dengan Streamlit components
        components.html(pyg_html, height=600, width=900, scrolling=False)

st.write('Klik "Refresh Data" untuk memperbarui data secara real-time.')