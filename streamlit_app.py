import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
from fpdf import FPDF

st.set_page_config(page_title="Deteksi Stunting Anak SD", layout="centered")

# ---------- FUNGSI UMUR ----------
def hitung_umur(tanggal_lahir):
    today = date.today()
    umur_hari = (today - tanggal_lahir).days
    tahun = umur_hari // 365
    bulan = (umur_hari % 365) // 30
    hari = (umur_hari % 365) % 30
    return f"{tahun} tahun {bulan} bulan {hari} hari", tahun, bulan

# ---------- FUNGSI STUNTING ----------
def cek_stunting(jk, umur_tahun, tinggi_cm):
    batas_stunting = 115 if umur_tahun >= 5 else 110
    return "Stunting" if tinggi_cm < batas_stunting else "Tidak Stunting"

# ---------- HEADER ----------
st.title("📊 Deteksi Stunting untuk Anak SD")
st.markdown("### 👶 Deteksi Dini Anak-Anak Desa")
st.markdown("*Isi form berikut untuk mengecek status stunting dan mendapatkan tips bergambar!*")

# ---------- INPUT ----------
nama = st.text_input("Nama Anak")
tanggal_lahir = st.date_input("Tanggal Lahir", min_value=date(2010,1,1), max_value=date.today())
jk = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"])
tinggi_cm = st.number_input("Tinggi Badan (cm)", 50, 200)

# ---------- OUTPUT ----------
if st.button("Cek Status"):
    umur_str, umur_th, umur_bln = hitung_umur(tanggal_lahir)
    status = cek_stunting(jk, umur_th, tinggi_cm)

    st.success(f"📌 Umur: {umur_str}")
    st.info(f"📈 Status Stunting: **{status}**")

    # ---------- TIPS ----------
    if status == "Stunting":
        st.markdown("### 🌟 Tips Khusus untuk Anak Stunting")
        st.markdown("""
        <div style="background-color:#ffdddd; padding:15px; border-radius:10px">
        ✅ Konsumsi makanan tinggi protein dan zat besi (ikan, telur, tempe, sayuran hijau).<br>
        ✅ Tidur cukup minimal 9 jam per malam.<br>
        ✅ Rutin olahraga ringan: jalan pagi, bermain aktif.<br>
        ✅ Pantau tinggi badan setiap 3 bulan.<br>
        ✅ Jangan lupa sarapan bergizi tiap pagi!
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("### 🌈 Tips Menjaga Pertumbuhan Anak Sehat")
        st.markdown("""
        <div style="background-color:#ddffdd; padding:15px; border-radius:10px">
        🥦 Makan 3x sehari dan 2x camilan sehat.<br>
        🚰 Minum cukup air putih.<br>
        🏃 Sering bermain dan bergerak.<br>
        😴 Tidur malam yang cukup dan berkualitas.<br>
        🧼 Cuci tangan sebelum makan!
        </div>
        """, unsafe_allow_html=True)

    # ---------- CHART ----------
    st.markdown("### 📊 Grafik Persebaran Stunting (Simulasi Desa)")
    data = {'Stunting': 30, 'Tidak Stunting': 70}
    fig, ax = plt.subplots(1,2, figsize=(10,4))

    # Bar Chart
    ax[0].bar(data.keys(), data.values(), color=['#ff6666','#66b3ff'])
    ax[0].set_title("Jumlah Anak Berdasarkan Status")
    ax[0].set_ylabel("Jumlah Anak")

    # Pie Chart
    ax[1].pie(data.values(), labels=data.keys(), autopct='%1.1f%%',
              colors=['#ff9999','#66b3ff'], explode=(0.1, 0), shadow=True, startangle=90)
    ax[1].axis('equal')
    ax[1].set_title("Persentase Status Stunting")

    st.pyplot(fig)

    # ---------- PDF ----------
    st.markdown("### 📄 Unduh Hasil & Tips PDF")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.set_fill_color(240, 240, 255)

    pdf.cell(200, 10, txt="Laporan Deteksi Stunting Anak SD", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Nama Anak: {nama}", ln=True)
    pdf.cell(200, 10, txt=f"Jenis Kelamin: {jk}", ln=True)
    pdf.cell(200, 10, txt=f"Tanggal Lahir: {tanggal_lahir.strftime('%d-%m-%Y')}", ln=True)
    pdf.cell(200, 10, txt=f"Umur: {umur_str}", ln=True)
    pdf.cell(200, 10, txt=f"Tinggi Badan: {tinggi_cm} cm", ln=True)
    pdf.cell(200, 10, txt=f"Status: {status}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="Tips untuk Anak:", ln=True)
    pdf.set_font("Arial", size=11)

    if status == "Stunting":
        tips = [
            "✅ Konsumsi makanan tinggi protein (ikan, tempe, telur).",
            "✅ Tidur cukup minimal 9 jam per malam.",
            "✅ Rutin olahraga ringan.",
            "✅ Pantau tinggi badan setiap 3 bulan.",
            "✅ Jangan lupa sarapan bergizi."
        ]
    else:
        tips = [
            "🧼 Cuci tangan sebelum makan.",
            "🥦 Makan 3x sehari dan 2x camilan sehat.",
            "🚰 Minum cukup air putih.",
            "🏃 Aktif bergerak dan bermain.",
            "😴 Tidur cukup dan berkualitas."
        ]
    
    for tip in tips:
        pdf.cell(200, 10, txt=tip, ln=True)

    pdf_output = f"/mnt/data/laporan_{nama.replace(' ', '_')}.pdf"
    pdf.output(pdf_output)

    with open(pdf_output, "rb") as f:
        st.download_button("📥 Unduh PDF Hasil Deteksi", data=f, file_name=f"{nama}_hasil_stunting.pdf")

