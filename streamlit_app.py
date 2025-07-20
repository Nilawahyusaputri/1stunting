# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fpdf import FPDF
import math
import os

st.set_page_config(page_title="Deteksi Stunting Anak SD", layout="wide")
st.title("📏 Deteksi Stunting untuk Anak SD di Desa")
st.markdown("""
Aplikasi ini membantu mendeteksi status gizi berdasarkan tinggi dan berat badan anak usia SD berdasarkan standar WHO.
""")

# --- Fungsi bantu WHO ---
def calculate_z_score(x, l, m, s):
    if l == 0:
        return np.log(x / m) / s
    else:
        return ((x / m) ** l - 1) / (l * s)

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

# --- Load data LMS WHO ---
hfa_boys = load_growth_reference("data/hfa_boys.csv")
hfa_girls = load_growth_reference("data/hfa_girls.csv")
wfa_boys = load_growth_reference("data/wfa_boys.csv")
wfa_girls = load_growth_reference("data/wfa_girls.csv")

# --- Form Input Data ---
st.subheader("🧒 Input Data Anak")
with st.form("form_anak"):
    nama = st.text_input("Nama Anak")
    kelas = st.selectbox("Kelas", ["1", "2", "3", "4", "5", "6"])
    gender = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    tgl_lahir = st.date_input("Tanggal Lahir")
    berat = st.number_input("Berat Badan (kg)", 10.0, 60.0, step=0.1)
    tinggi = st.number_input("Tinggi Badan (cm)", 80.0, 180.0, step=0.1)
    submit = st.form_submit_button("🔍 Deteksi")

if submit:
    today = datetime.today().date()
    age = relativedelta(today, tgl_lahir)
    age_months = age.years * 12 + age.months
    age_str = f"{age.years} tahun, {age.months} bulan, {age.days} hari"

    if gender == "Laki-laki":
        hfa_df = hfa_boys
        wfa_df = wfa_boys
    else:
        hfa_df = hfa_girls
        wfa_df = wfa_girls

    # Z-Score
    l_hfa, m_hfa, s_hfa = get_lms_values(hfa_df, age_months)
    l_wfa, m_wfa, s_wfa = get_lms_values(wfa_df, age_months)

    z_hfa = calculate_z_score(tinggi, l_hfa, m_hfa, s_hfa)
    z_wfa = calculate_z_score(berat, l_wfa, m_wfa, s_wfa)

    status_hfa = interpret_z_score(z_hfa, 'HFA')
    status_wfa = interpret_z_score(z_wfa, 'WFA')

    # --- Output Visual ---
    st.success(f"**{nama}** ({gender}), usia: {age_str}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Status Tinggi Badan (HFA)", status_hfa, f"Z = {z_hfa:.2f}")
    with col2:
        st.metric("Status Berat Badan (WFA)", status_wfa, f"Z = {z_wfa:.2f}")

    # --- Avatar ---
    avatar_path = f"avatars/{'boy' if gender == 'Laki-laki' else 'girl'}_{'stunting' if 'Stunting' in status_hfa else 'healthy'}.png"
    if os.path.exists(avatar_path):
        st.image(avatar_path, width=180)

    # --- Saran ---
    st.info("**Saran dan Tips:**")
    if "Stunting" in status_hfa:
        st.write("💡 Perbanyak konsumsi protein hewani seperti telur, ikan, daging, susu.")
    elif "Normal" in status_hfa and "Normal" in status_wfa:
        st.write("✅ Anak tumbuh dengan baik! Tetap jaga pola makan dan aktivitas.")
    elif "Risiko" in status_wfa:
        st.write("⚠️ Kurangi makanan manis/tinggi kalori, perbanyak sayur & buah.")
    else:
        st.write("📌 Perlu pemantauan rutin dan asupan gizi seimbang.")

    # --- Simpan Hasil ---
    if 'hasil' not in st.session_state:
        st.session_state.hasil = []

    st.session_state.hasil.append({
        "Nama": nama,
        "Kelas": kelas,
        "Usia": age_str,
        "Gender": gender,
        "Berat": berat,
        "Tinggi": tinggi,
        "HFA_Z": round(z_hfa,2),
        "WFA_Z": round(z_wfa,2),
        "Status HFA": status_hfa,
        "Status WFA": status_wfa
    })

# --- Tampilkan Rekap ---
if 'hasil' in st.session_state and len(st.session_state.hasil) > 0:
    st.subheader("📊 Rekap Data Anak")
    df_hasil = pd.DataFrame(st.session_state.hasil)
    st.dataframe(df_hasil, use_container_width=True)

    # Visual
    st.subheader("📈 Visualisasi Status HFA")
    fig, ax = plt.subplots(figsize=(6,4))
    pd.DataFrame(df_hasil.groupby(["Kelas", "Status HFA"]).size().unstack(fill_value=0)).plot(kind='bar', stacked=True, ax=ax)
    st.pyplot(fig)

    # Export PDF
    def export_pdf(df):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Laporan Deteksi Stunting", ln=True, align="C")

        for idx, row in df.iterrows():
            pdf.ln()
            pdf.multi_cell(0, 10, f"Nama: {row['Nama']}\nUsia: {row['Usia']}\nBerat: {row['Berat']} kg, Tinggi: {row['Tinggi']} cm\nStatus HFA: {row['Status HFA']}, WFA: {row['Status WFA']}")

        pdf_path = "hasil_deteksi.pdf"
        pdf.output(pdf_path)
        return pdf_path

    if st.button("⬇️ Download Hasil PDF"):
        pdf_file = export_pdf(df_hasil)
        with open(pdf_file, "rb") as f:
            st.download_button("📄 Unduh PDF", data=f, file_name="hasil_stunting.pdf")
