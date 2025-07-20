import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from io import BytesIO

st.set_page_config(page_title="Deteksi Stunting Anak SD", layout="centered")

# Fungsi hitung umur
def hitung_umur(tgl_lahir):
    today = date.today()
    umur = today - tgl_lahir
    tahun = umur.days // 365
    bulan = (umur.days % 365) // 30
    hari = (umur.days % 365) % 30
    return tahun, bulan, hari

# Fungsi deteksi stunting sederhana (versi lokal)
def deteksi_stunting(umur_tahun, tinggi):
    # Ambang batas WHO sangat kompleks, ini versi sederhana
    if umur_tahun <= 5:
        batas = 110
    elif umur_tahun <= 7:
        batas = 115
    elif umur_tahun <= 9:
        batas = 125
    else:
        batas = 130

    if tinggi < batas:
        return "Stunting", "Tinggi badan anak tergolong pendek untuk usianya."
    else:
        return "Normal", "Tinggi badan anak sesuai dengan usianya."

# Input
st.title("📏 Deteksi Dini Stunting untuk Anak Sekolah Dasar")
st.markdown("Masukkan data anak untuk mengetahui status pertumbuhan dan tips perbaikannya.")

nama = st.text_input("Nama Anak")
tgl_lahir = st.date_input("Tanggal Lahir", min_value=date(2010, 1, 1), max_value=date.today())
tinggi_badan = st.number_input("Tinggi Badan (cm)", min_value=50.0, max_value=200.0, step=0.1)

# Tombol Proses
if st.button("🔍 Periksa Status"):
    umur_tahun, umur_bulan, umur_hari = hitung_umur(tgl_lahir)
    status, keterangan = deteksi_stunting(umur_tahun, tinggi_badan)

    # Hasil
    st.subheader("📊 Hasil Pemeriksaan")
    st.write(f"**Nama:** {nama}")
    st.write(f"**Umur:** {umur_tahun} tahun, {umur_bulan} bulan, {umur_hari} hari")
    st.write(f"**Status Gizi:** {status}")
    st.info(keterangan)

    # Tips
    st.subheader("🍽️ Tips Khusus")
    if status == "Stunting":
        st.error("Anak tergolong stunting. Berikut beberapa saran:")
        st.markdown("""
        - Pastikan konsumsi makanan tinggi protein: telur, ikan, tempe.
        - Rutin ke posyandu dan periksa pertumbuhan.
        - Cukup tidur dan aktivitas fisik.
        """)
    else:
        st.success("Anak tergolong normal. Tetap jaga pertumbuhan dengan:")
        st.markdown("""
        - Makan makanan bergizi seimbang.
        - Minum air putih cukup.
        - Bermain aktif dan tidur cukup.
        """)

    # Simpan ke PDF
    st.subheader("📥 Unduh Hasil sebagai PDF")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "Laporan Status Pertumbuhan Anak")
    c.setFont("Helvetica", 12)
    c.drawString(50, 770, f"Nama Anak: {nama}")
    c.drawString(50, 750, f"Umur: {umur_tahun} tahun, {umur_bulan} bulan, {umur_hari} hari")
    c.drawString(50, 730, f"Tinggi Badan: {tinggi_badan} cm")
    c.drawString(50, 710, f"Status: {status}")
    c.drawString(50, 690, f"Keterangan: {keterangan}")

    if status == "Stunting":
        c.setFillColor(colors.red)
        c.drawString(50, 660, "Tips:")
        c.setFillColor(colors.black)
        c.drawString(60, 640, "- Perbanyak protein (ikan, telur, tempe).")
        c.drawString(60, 620, "- Rutin periksa ke posyandu.")
        c.drawString(60, 600, "- Tidur cukup, olahraga rutin.")
    else:
        c.setFillColor(colors.green)
        c.drawString(50, 660, "Tips:")
        c.setFillColor(colors.black)
        c.drawString(60, 640, "- Makanan bergizi seimbang.")
        c.drawString(60, 620, "- Minum air putih yang cukup.")
        c.drawString(60, 600, "- Jaga waktu tidur dan aktivitas.")

    c.save()
    st.download_button("📄 Unduh PDF", buffer.getvalue(), file_name="hasil_pemeriksaan.pdf")

# Contoh data populasi
data = {
    'Nama': ['Ani', 'Budi', 'Citra', 'Dodi', 'Eka'],
    'Status': ['Stunting', 'Normal', 'Normal', 'Stunting', 'Normal']
}
df = pd.DataFrame(data)

# Grafik
st.subheader("📈 Statistik Persebaran")

# Bar chart
status_counts = df['Status'].value_counts()
fig_bar, ax_bar = plt.subplots()
ax_bar.bar(status_counts.index, status_counts.values, color=['#ff9999', '#66b3ff'])
ax_bar.set_ylabel('Jumlah Anak')
ax_bar.set_title('Persebaran Status Gizi')
st.pyplot(fig_bar)

# Pie chart
fig_pie, ax_pie = plt.subplots()
ax_pie.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%',
           colors=['#ff9999', '#66b3ff'], explode=(0.1, 0), shadow=True, startangle=90)
ax_pie.axis('equal')
st.pyplot(fig_pie)

# Tabel
st.dataframe(df.style.highlight_max(axis=0))
