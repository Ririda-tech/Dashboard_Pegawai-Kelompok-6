import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Data Cleaning Pegawai Kampus XYZ", page_icon="🧹", layout="wide")
st.title("🧹 Data Cleaning - Data Pegawai Kampus XYZ")
st.markdown("""
### 📥 Belum punya dataset?

Silakan download data mentah terlebih dahulu menggunakan tombol berikut:
""")
with open("Data Pegawai Kampus XYZ.csv", "rb") as file:
    st.download_button(
        label="📥 Download Data Mentah",
        data=file,
        file_name="Data Pegawai Kampus XYZ.csv",
        mime="text/csv"
    )
st.caption("UAS Visualisasi Data | Kelompok 6 | Visualisasi dashboard ")
st.sidebar.header("Upload Data")
uploaded = st.sidebar.file_uploader("Upload file CSV", type=["csv"])
if uploaded is None:
    st.info("Upload file data_pegawai.csv di sidebar kiri untuk memulai.")
    st.stop()
df_raw = pd.read_csv(uploaded)
df = df_raw.copy()
for col in ['tgl_lahir', 'tgl_jabatan_akademik']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
if 'tahun_sertifikasi' in df.columns:
    df['tahun_sertifikasi'] = pd.to_numeric(df['tahun_sertifikasi'], errors='coerce').astype('Int64')
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.strip()
before = len(df)
df = df.drop_duplicates()
dedup = before - len(df)
if 'tgl_lahir' in df.columns:
    df['usia'] = (pd.Timestamp.today() - df['tgl_lahir']).dt.days // 365
st.subheader("Profil Dataset")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Record", f"{len(df):,}")
c2.metric("Jumlah Kolom", len(df.columns))
c3.metric("Duplikat Dihapus", dedup)
c4.metric("Kolom Ada Missing", int((df.isnull().sum() > 0).sum()))
st.dataframe(df.head(5), use_container_width=True)
st.divider()
st.subheader("1. Missing Value Analysis")
mv = df.isnull().sum()
mv_pct = (mv / len(df) * 100).round(2)
mv_df = pd.DataFrame({'Jumlah Missing': mv, 'Persentase (%)': mv_pct})
mv_df = mv_df[mv_df['Jumlah Missing'] > 0].sort_values('Jumlah Missing', ascending=False)
col_a, col_b = st.columns([1, 2])
with col_a:
    st.dataframe(mv_df, use_container_width=True)
with col_b:
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(mv_df.index, mv_df['Jumlah Missing'], color='tomato', edgecolor='black')
    ax.set_title('Jumlah Missing Value per Kolom', fontweight='bold')
    ax.set_xlabel('Kolom')
    ax.set_ylabel('Jumlah')
    for i, v in enumerate(mv_df['Jumlah Missing']):
        ax.text(i, v + 1, str(v), ha='center', fontsize=9, fontweight='bold')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
st.divider()
st.subheader("2. Duplicate Analysis")
if dedup == 0:
    st.success(f"Tidak ada duplikat. Total data: {len(df):,} baris")
else:
    st.warning(f"Ditemukan {dedup} baris duplikat dan telah dihapus. Sisa data: {len(df):,} baris")
st.divider()
st.subheader("3. Data Type Validation")
st.markdown("""
| Kolom | Tipe Setelah Konversi | Status |
|---|---|---|
| tgl_lahir | datetime | OK |
| tgl_jabatan_akademik | datetime | OK |
| tahun_sertifikasi | integer | OK |
| Semua kolom string | string trimmed | OK |
""")
st.dataframe(
    pd.DataFrame({'Kolom': df.columns, 'Tipe Data': df.dtypes.astype(str).values}),
    use_container_width=True
)
st.divider()

st.subheader("4️⃣ Outlier Detection")
if 'usia' in df.columns:
    outlier_count = len(df[(df['usia'] < 18) | (df['usia'] > 80)])
    st.write(f"Usia tidak wajar (< 18 atau > 80 tahun): **{outlier_count} data**")

    uv = df[(df['usia'] >= 18) & (df['usia'] <= 80)]['usia'].dropna()

    col_c, col_d = st.columns(2)
    with col_c:
        fig_hist = px.histogram(
            uv, nbins=20,
            title='Histogram Distribusi Usia',
            labels={'value': 'Usia (tahun)', 'count': 'Jumlah'},
            color_discrete_sequence=['#2e6db4']
        )
        fig_hist.add_vline(x=uv.mean(), line_dash='dash', line_color='red',
                           annotation_text=f'Rata-rata: {uv.mean():.1f} th', annotation_position='top right')
        fig_hist.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_d:
        fig_box = px.box(
            df[(df['usia'] >= 18) & (df['usia'] <= 80)],
            y='usia',
            title='Box Plot Distribusi Usia',
            labels={'usia': 'Usia (tahun)'},
            color_discrete_sequence=['#2e6db4']
        )
        fig_box.update_layout(height=350)
        st.plotly_chart(fig_box, use_container_width=True)

    st.dataframe(uv.describe().rename('Statistik Usia').to_frame().T, use_container_width=True)

st.divider()

# ── 5. Data Consistency Check ─────────────────────────────────────────────────
st.subheader("5️⃣ Data Consistency Check")

ok_count = 0
warn_count = 0

if 'sertifikasi' in df.columns and 'tahun_sertifikasi' in df.columns:
    ink1 = df[
        (df['sertifikasi'].notna() & df['tahun_sertifikasi'].isna()) |
        (df['sertifikasi'].isna() & df['tahun_sertifikasi'].notna())
    ]
    if len(ink1) == 0:
        st.success("✅ Kolom `sertifikasi` & `tahun_sertifikasi` konsisten.")
        ok_count += 1
    else:
        st.warning(f"⚠️ {len(ink1)} data inkonsisten antara `sertifikasi` dan `tahun_sertifikasi`.")
        st.dataframe(ink1[['id_pegawai', 'sertifikasi', 'tahun_sertifikasi']].head(10))
        warn_count += 1

if 'jabatan_akademik' in df.columns and 'tgl_jabatan_akademik' in df.columns:
    ink2 = df[
        (df['jabatan_akademik'].notna() & df['tgl_jabatan_akademik'].isna()) |
        (df['jabatan_akademik'].isna() & df['tgl_jabatan_akademik'].notna())
    ]
    if len(ink2) == 0:
        st.success("✅ Kolom `jabatan_akademik` & `tgl_jabatan_akademik` konsisten.")
        ok_count += 1
    else:
        st.warning(f"⚠️ {len(ink2)} data inkonsisten antara `jabatan_akademik` dan tanggalnya.")
        st.dataframe(ink2[['id_pegawai', 'jabatan_akademik', 'tgl_jabatan_akademik']].head(10))
        warn_count += 1

st.markdown("**Nilai unik per kolom kategorikal:**")
cat_cols = ['jk', 'stat_aktif', 'stat_pegawai', 'ikatan_kerja', 'pendidikan',
            'jabatan_akademik', 'sertifikasi', 'jenj_prodi', 'rumpun_ilmu', 'fakultas']
rows = []
for col in cat_cols:
    if col in df.columns:
        uniq = sorted(df[col].dropna().unique().tolist())
        rows.append({'Kolom': col, 'Jumlah Unique': len(uniq), 'Nilai': ', '.join(str(u) for u in uniq)})
st.dataframe(pd.DataFrame(rows), use_container_width=True)

st.divider()

# ── Download ──────────────────────────────────────────────────────────────────
st.subheader("⬇️ Download Hasil Cleaning")
csv_out = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download data_pegawai_clean.csv",
    data=csv_out,
    file_name='data_pegawai_clean.csv',
    mime='text/csv',
    use_container_width=True
)
st.info("Gunakan file ini untuk diunggah ke halaman **Dashboard Pegawai**.")
