import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# --- Setup Direktori ---
if not os.path.exists("laporan_gizi"):
    os.makedirs("laporan_gizi")
if not os.path.exists("grafik"):
    os.makedirs("grafik")

# --- WHO Standar HAZ (Sederhana) ---
def calculate_haz(height, age, sex):
    median_height = {
        'L': [109.2, 114.6, 120.0, 125.1, 130.1, 134.9],
        'P': [108.4, 113.7, 119.0, 124.2, 129.2, 134.0]
    }
    sd_height = {
        'L': [4.6, 4.9, 5.2, 5.5, 5.8, 6.0],
        'P': [4.5, 4.8, 5.1, 5.4, 5.7, 6.0]
    }
    usia_index = int(age) - 5
    if usia_index < 0 or usia_index >= len(median_height[sex]):
        return None
    z = (height - median_height[sex][usia_index]) / sd_height[sex][usia_index]
    return round(z, 2)

def generate_tip(status):
    if status == "Stunting":
        return "Asupan gizi perlu ditingkatkan dan perlu pemantauan rutin."
    elif status == "Normal":
        return "Pertumbuhan baik! Terus jaga pola makan dan kebersihan."
    else:
        return "Perlu validasi ulang data."

def generate_pdf(name, age, gender, height, weight, haz, status):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Laporan Status Gizi - StunTrack SD", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Nama: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Usia: {age} tahun", ln=True)
    pdf.cell(200, 10, txt=f"Jenis Kelamin: {'Laki-laki' if gender == 'L' else 'Perempuan'}", ln=True)
    pdf.cell(200, 10, txt=f"Tinggi Badan: {height} cm", ln=True)
    pdf.cell(200, 10, txt=f"Berat Badan: {weight} kg", ln=True)
    pdf.cell(200, 10, txt=f"Z-score HAZ: {haz}", ln=True)
    pdf.cell(200, 10, txt=f"Status: {status}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt="Saran: " + generate_tip(status))

    filename = f"laporan_gizi/{name.replace(' ', '_')}_gizi.pdf"
    pdf.output(filename)
    return filename

# --- Streamlit UI ---
st.set_page_config(page_title="StunTrack SD", layout="centered")
st.title("📏 Deteksi Dini Stunting Anak SD")
st.markdown("_Pantau pertumbuhan anak-anak sekolah dasar dengan mudah_")

with st.form("input_form"):
    name = st.text_input("Nama Anak")
    age = st.slider("Usia (tahun)", 5, 10)
    gender = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    height = st.number_input("Tinggi Badan (cm)", min_value=50.0, max_value=180.0)
    weight = st.number_input("Berat Badan (kg)", min_value=10.0, max_value=80.0)
    kelas = st.selectbox("Kelas", ["1", "2", "3", "4", "5", "6"])
    submit = st.form_submit_button("🔍 Cek Status Gizi")

if submit:
    sex_code = 'L' if gender == "Laki-laki" else 'P'
    haz = calculate_haz(height, age, sex_code)
    if haz is None:
        st.warning("Usia tidak valid untuk kalkulasi WHO")
    else:
        status = "Stunting" if haz < -2 else "Normal"

        st.success(f"Status: **{status}** (Z-Score: {haz})")
        st.progress(min(max((haz + 3) / 6, 0.0), 1.0))
        st.caption(generate_tip(status))

        # Simpan ke CSV
        new_data = pd.DataFrame([[name, age, gender, kelas, height, weight, haz, status]],
                                columns=["Nama", "Usia", "Gender", "Kelas", "Tinggi", "Berat", "HAZ", "Status"])
        if not os.path.isfile("data_stunting.csv"):
            new_data.to_csv("data_stunting.csv", index=False)
        else:
            new_data.to_csv("data_stunting.csv", mode='a', header=False, index=False)

        # PDF
        pdf_path = generate_pdf(name, age, sex_code, height, weight, haz, status)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Unduh PDF Laporan", f, file_name=pdf_path.split("/")[-1])

# --- Sidebar Laporan ---
st.sidebar.title("📊 Laporan Kolektif")

if st.sidebar.button("Tampilkan Rekap Data"):
    if os.path.exists("data_stunting.csv"):
        df = pd.read_csv("data_stunting.csv")
        st.sidebar.success("Data ditemukan")
        st.dataframe(df)

        # Grafik stunting per kelas
        st.subheader("📈 Grafik Jumlah Stunting per Kelas")
        chart_data = df[df['Status'] == 'Stunting'].groupby('Kelas').size()
        fig, ax = plt.subplots()
        chart_data.plot(kind='bar', ax=ax, color='tomato')
        ax.set_ylabel("Jumlah Anak Stunting")
        ax.set_xlabel("Kelas")
        ax.set_title("Distribusi Anak Stunting")
        st.pyplot(fig)
    else:
        st.sidebar.warning("Belum ada data anak yang dimasukkan.")
