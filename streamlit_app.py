# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
import io
import os
from who import who2007  # pip install who-standards

# Helper functions
def calculate_age(birthdate):
    today = datetime.today()
    delta = relativedelta(today, birthdate)
    return delta.years, delta.months, delta.days, (today - birthdate).days / 30

def get_z_score_hfa(age_months, gender, height):
    result = who2007.hfa(age_in_months=age_months, sex='M' if gender == 'Laki-laki' else 'F', height=height)
    return result.zscore

def get_z_score_wfa(age_months, gender, weight):
    result = who2007.wfa(age_in_months=age_months, sex='M' if gender == 'Laki-laki' else 'F', weight=weight)
    return result.zscore

def interpret_status(hfa_z, wfa_z):
    if hfa_z is None or wfa_z is None:
        return "Data Tidak Lengkap", "gray"
    if hfa_z < -2:
        return "🚨 Tanda Stunting", "red"
    elif -2 <= hfa_z < -1:
        return "⚠️ Butuh Perhatian", "orange"
    elif wfa_z > 2:
        return "📈 Risiko Overweight", "purple"
    else:
        return "🌿 Sehat & Tumbuh Baik", "green"

def avatar_by_status(status, gender):
    if "Stunting" in status:
        return f"avatars/{'boy' if gender == 'Laki-laki' else 'girl'}_stunting.png"
    elif "Perhatian" in status:
        return f"avatars/{'boy' if gender == 'Laki-laki' else 'girl'}_warning.png"
    elif "Overweight" in status:
        return f"avatars/{'boy' if gender == 'Laki-laki' else 'girl'}_overweight.png"
    else:
        return f"avatars/{'boy' if gender == 'Laki-laki' else 'girl'}_healthy.png"

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Hasil Deteksi Stunting Anak", ln=1, align="C")
    pdf.ln(5)
    for key, val in data.items():
        pdf.cell(200, 10, txt=f"{key}: {val}", ln=1)
    buffer = io.BytesIO()
    pdf.output(buffer)
    b64 = base64.b64encode(buffer.getvalue()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="hasil_stunting.pdf">📄 Download PDF</a>'
    return href

# Streamlit UI
st.set_page_config(page_title="Deteksi Stunting Anak SD", layout="wide")
st.title("🧒 Deteksi Stunting Anak SD - Desa KKN")
st.markdown("Alat bantu deteksi awal dan edukasi status pertumbuhan anak SD.")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Nama Anak")
        gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        dob = st.date_input("Tanggal Lahir")
        kelas = st.selectbox("Kelas", ["1", "2", "3", "4", "5", "6"])
    with col2:
        height = st.number_input("Tinggi Badan (cm)", min_value=50.0, max_value=200.0)
        weight = st.number_input("Berat Badan (kg)", min_value=10.0, max_value=100.0)

    submitted = st.form_submit_button("🩺 Deteksi Sekarang")

if submitted:
    years, months, days, total_months = calculate_age(dob)
    age_str = f"{years} tahun, {months} bulan, {days} hari"
    hfa_z = get_z_score_hfa(int(total_months), gender, height)
    wfa_z = get_z_score_wfa(int(total_months), gender, weight)
    status, color = interpret_status(hfa_z, wfa_z)
    avatar = avatar_by_status(status, gender)

    col1, col2 = st.columns([1,2])
    with col1:
        st.image(avatar, width=150)
        st.markdown(f"**Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
        st.markdown(f"**Umur:** {age_str}")
        st.markdown(f"**Kelas:** {kelas}")
    with col2:
        st.markdown("### Saran dan Tips")
        if "Stunting" in status:
            st.warning("Segera konsultasi ke puskesmas dan perbaiki pola makan bergizi seimbang.")
        elif "Perhatian" in status:
            st.info("Pantau pertumbuhan, lebihkan asupan protein dan sayuran.")
        elif "Overweight" in status:
            st.info("Kurangi makanan ultra-proses dan minuman manis.")
        else:
            st.success("Pertahankan pola makan sehat dan aktivitas fisik.")

    # Simpan data
    if "results" not in st.session_state:
        st.session_state.results = []
    st.session_state.results.append({
        "Nama": name,
        "Jenis Kelamin": gender,
        "Kelas": kelas,
        "Umur": age_str,
        "Tinggi": height,
        "Berat": weight,
        "Status": status
    })

    # Download PDF
    st.markdown(generate_pdf({
        "Nama": name,
        "Jenis Kelamin": gender,
        "Umur": age_str,
        "Tinggi": f"{height} cm",
        "Berat": f"{weight} kg",
        "Status": status,
        "Saran": "Lihat hasil & konsultasikan jika perlu."
    }), unsafe_allow_html=True)

# Tampilkan hasil semua
if "results" in st.session_state:
    df = pd.DataFrame(st.session_state.results)
    st.markdown("---")
    st.header("📋 Rekap Deteksi Anak")
    st.dataframe(df)

    st.subheader("📈 Visualisasi per Kelas")
    kelas_group = df.groupby(["Kelas", "Status"]).size().unstack().fillna(0)
    kelas_group.plot(kind='bar', stacked=True, colormap='Pastel1')
    st.pyplot(plt.gcf())
