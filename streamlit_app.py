import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from fpdf import FPDF
import os
import math

# ========== Fungsi-fungsi ========== #

def calculate_age(birth_date):
    today = datetime.today()
    age_days = (today - birth_date).days
    age_years = age_days // 365
    age_months = age_days // 30
    return age_years, age_months, age_days

def calculate_z_score(x, l, m, s):
    if l == 0:
        return np.log(x / m) / s
    else:
        return ((x / m) ** l - 1) / (l * s)

@st.cache_data
def load_growth_reference(file_path):
    return pd.read_csv(file_path)

def get_lms_values(df, month):
    if month not in df['Month'].values:
        nearest = df.iloc[(df['Month'] - month).abs().argsort()[:1]]
        row = nearest.iloc[0]
    else:
        row = df[df['Month'] == month].iloc[0]
    return row['L'], row['M'], row['S']

def interpret_z_score(z, tipe):
    if tipe == 'HFA':
        if z < -3:
            return 'Stunting Berat'
        elif z < -2:
            return 'Stunting'
        else:
            return 'Normal'
    elif tipe == 'WFA':
        if z < -3:
            return 'Berat Badan Sangat Kurang'
        elif z < -2:
            return 'Berat Badan Kurang'
        elif z > 2:
            return 'Risiko Obesitas'
        elif z > 1:
            return 'Risiko Berat Lebih'
        else:
            return 'Normal'

def load_avatar(gender, status):
    status_key = status.lower().replace(" ", "_")
    path = f"avatars/{gender.lower()}_{status_key}.png"
    if os.path.exists(path):
        return path
    return None

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Hasil Deteksi Status Gizi Anak", ln=True, align='C')
    pdf.ln(10)
    for k, v in data.items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    path = "hasil_deteksi.pdf"
    pdf.output(path)
    return path

# ========== Load Data WHO ========== #
hfa_boys = load_growth_reference('data/hfa_boys.csv')
hfa_girls = load_growth_reference('data/hfa_girls.csv')
wfa_boys = load_growth_reference('data/wfa_boys.csv')
wfa_girls = load_growth_reference('data/wfa_girls.csv')

# ========== UI Streamlit ========== #
st.set_page_config(page_title="Deteksi Stunting Anak SD", layout="centered")
st.title("📊 Deteksi Stunting Anak SD di Desa")
st.markdown("Aplikasi ini membantu mendeteksi status gizi anak berdasarkan standar WHO.")

with st.form("form_anak"):
    nama = st.text_input("Nama Anak")
    kelas = st.selectbox("Kelas", ["1", "2", "3", "4", "5", "6"])
    gender = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    tgl_lahir = st.date_input("Tanggal Lahir")
    berat = st.number_input("Berat Badan (kg)", min_value=5.0, max_value=60.0, step=0.1)
    tinggi = st.number_input("Tinggi Badan (cm)", min_value=80.0, max_value=180.0, step=0.1)
    submit = st.form_submit_button("Deteksi Sekarang")

if submit:
    age_y, age_m, age_d = calculate_age(tgl_lahir)
    st.success(f"Usia anak: {age_y} tahun {age_m%12} bulan ({age_d} hari)")

    df_hfa = hfa_boys if gender == "Laki-laki" else hfa_girls
    df_wfa = wfa_boys if gender == "Laki-laki" else wfa_girls

    l_hfa, m_hfa, s_hfa = get_lms_values(df_hfa, age_m)
    l_wfa, m_wfa, s_wfa = get_lms_values(df_wfa, age_m)

    z_hfa = calculate_z_score(tinggi, l_hfa, m_hfa, s_hfa)
    z_wfa = calculate_z_score(berat, l_wfa, m_wfa, s_wfa)

    status_hfa = interpret_z_score(z_hfa, 'HFA')
    status_wfa = interpret_z_score(z_wfa, 'WFA')

    st.subheader("📋 Hasil Deteksi")
    st.markdown(f"- **Status Tinggi Badan (HFA)**: `{status_hfa}` (Z={z_hfa:.2f})")
    st.markdown(f"- **Status Berat Badan (WFA)**: `{status_wfa}` (Z={z_wfa:.2f})")

    avatar_path = load_avatar(gender, status_hfa)
    if avatar_path:
        st.image(avatar_path, width=150)

    st.info("Tips & Saran: Perbanyak konsumsi protein, istirahat cukup, dan aktif bermain di luar rumah.")

    result_data = {
        "Nama": nama,
        "Kelas": kelas,
        "Jenis Kelamin": gender,
        "Usia (bulan)": age_m,
        "Tinggi": tinggi,
        "Berat": berat,
        "Status HFA": status_hfa,
        "Status WFA": status_wfa
    }

    if st.button("📄 Unduh Hasil PDF"):
        pdf_file = generate_pdf(result_data)
        with open(pdf_file, "rb") as f:
            st.download_button("Download PDF", f, file_name="hasil_deteksi.pdf")

# ========== (Optional) Tambah Visualisasi dan Tabel jika ada data anak-anak lain ==========
