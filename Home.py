import streamlit as st

st.set_page_config(
    page_title="Dashboard Pegawai Kampus XYZ",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Pegawai Kampus XYZ")

st.subheader("UAS Visualisasi Data")

st.info("""
Kelompok 6

Anggota Kelompok:
1. Zetta Yemimma Arini Uktolseja 2410501076
2. Riri RIda Lestari 2410501084
3. Hana Khaila 2410501093
""")

st.markdown("""
## Petunjuk Penggunaan Aplikasi

Aplikasi ini terdiri dari dua tahap utama:

### 🧹 Tahap 1 : Data Cleaning

1. Pilih menu **Data Cleaning** pada sidebar kiri.
2. Upload file data pegawai mentah (raw data).
3. Sistem akan melakukan proses pembersihan data.
4. Periksa hasil cleaning yang ditampilkan.
5. Klik tombol **Download Data Cleaning**.
6. Simpan file hasil cleaning ke perangkat Anda.

---

### 📊 Tahap 2 : Dashboard Pegawai

1. Pilih menu **Dashboard Pegawai** pada sidebar kiri.
2. Upload file hasil cleaning yang telah diunduh dari tahap sebelumnya.
3. Sistem akan menampilkan:
   - Ringkasan data pegawai
   - Statistik pegawai
   - Grafik dan visualisasi data
   - Insight hasil analisis

---

## Alur Penggunaan

Raw Data Pegawai
            
        ⬇
            
Data Cleaning
            
        ⬇
            
Download Hasil Cleaning
            
        ⬇
            
Dashboard Pegawai
            
        ⬇
            
Visualisasi dan Analisis Data

---

### ⚠️ Catatan

- Gunakan file data mentah hanya pada menu Data Cleaning.
- Gunakan file hasil cleaning pada menu Dashboard Pegawai.
- Pastikan file hasil cleaning tidak diubah sebelum diunggah ke dashboard.
""")

st.success("Silakan pilih menu Data Cleaning pada sidebar untuk memulai.")
