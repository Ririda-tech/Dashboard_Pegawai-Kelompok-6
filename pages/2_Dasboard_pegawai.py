import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
st.set_page_config(page_title="Dashboard Pegawai Kampus XYZ", page_icon="🎓", layout="wide")
st.markdown("""
<style>
[data-testid="metric-container"]{background:linear-gradient(135deg,#1e3a5f,#2e6db4);border-radius:12px;padding:16px;}
[data-testid="metric-container"] label{color:#cce0ff !important;font-size:13px;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:white !important;font-size:2rem;}
.ibox{background:#f0f7ff;border-left:5px solid #2e6db4;padding:12px 16px;border-radius:6px;margin:8px 0;}
</style>
""", unsafe_allow_html=True)
C = ['#2e6db4','#e07b39','#27ae60','#8e44ad','#c0392b','#16a085','#f39c12','#2980b9']
st.sidebar.title("Dashboard Pegawai Kampus XYZ")
st.sidebar.markdown("**Kelompok 6 | D3 Sistem Informasi**")
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if uploaded is None:
    st.title("Dashboard Analitik Pegawai Kampus XYZ")
    st.info("Upload file data_pegawai_clean.csv di sidebar kiri untuk memulai.")
    st.stop()
df = pd.read_csv(uploaded)
for col in ['tgl_lahir','tgl_jabatan_akademik']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
if 'tahun_sertifikasi' in df.columns:
    df['tahun_sertifikasi'] = pd.to_numeric(
        df['tahun_sertifikasi'],
        errors='coerce'
    )

    tahun_sekarang = pd.Timestamp.today().year

    df.loc[
        (df['tahun_sertifikasi'] < 1990) |
        (df['tahun_sertifikasi'] > tahun_sekarang),
        'tahun_sertifikasi'
    ] = np.nan

for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.strip()

df = df.drop_duplicates()

if 'tgl_lahir' in df.columns:
    df['usia'] = (pd.Timestamp.today() - df['tgl_lahir']).dt.days // 365

if 'tgl_jabatan_akademik' in df.columns:
    df['tahun_jabatan'] = df['tgl_jabatan_akademik'].dt.year

    tahun_sekarang = pd.Timestamp.today().year

    df.loc[
        (df['tahun_jabatan'] < 1990) |
        (df['tahun_jabatan'] > tahun_sekarang),
        'tahun_jabatan'
    ] = np.nan

st.sidebar.markdown("### Filter Data")
f1 = ['Semua'] + sorted(df['fakultas'].dropna().unique().tolist())
s1 = st.sidebar.selectbox("Fakultas", f1)
f2 = ['Semua'] + sorted(df['stat_aktif'].dropna().unique().tolist())
s2 = st.sidebar.selectbox("Status Aktif", f2)
f3 = ['Semua'] + sorted(df['ikatan_kerja'].dropna().unique().tolist())
s3 = st.sidebar.selectbox("Ikatan Kerja", f3)
f4 = ['Semua'] + sorted(df['jenj_prodi'].dropna().unique().tolist())
s4 = st.sidebar.selectbox("Jenjang Prodi", f4)
df_f = df.copy()
if s1 != 'Semua':
    df_f = df_f[df_f['fakultas'] == s1]
if s2 != 'Semua':
    df_f = df_f[df_f['stat_aktif'] == s2]
if s3 != 'Semua':
    df_f = df_f[df_f['ikatan_kerja'] == s3]
if s4 != 'Semua':
    df_f = df_f[df_f['jenj_prodi'] == s4]
st.sidebar.markdown(f"**Total data: {len(df_f):,}**")
t1,t2,t3,t4,t5,t6,t7 = st.tabs(["Executive Summary","Perbandingan","Time Series","Distribusi","Relationship","Geospasial","AI Insight"])
with t1:
    st.header("Executive Summary")
    total = len(df_f)
    aktif = len(df_f[df_f['stat_aktif']=='Aktif']) if 'stat_aktif' in df_f.columns else 0
    sertif = int(df_f['sertifikasi'].notna().sum()) if 'sertifikasi' in df_f.columns else 0
    pct = sertif/total*100 if total > 0 else 0
    prof = len(df_f[df_f['jabatan_akademik']=='Profesor']) if 'jabatan_akademik' in df_f.columns else 0
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Pegawai", f"{total:,}")
    c2.metric("Dosen Aktif", f"{aktif:,}")
    c3.metric("Tersertifikasi", f"{pct:.1f}%")
    c4.metric("Profesor", f"{prof}")
    st.divider()
    ca,cb = st.columns(2)
    with ca:
        st.subheader("Status Aktif")
        sc = df_f['stat_aktif'].value_counts()
        fig,ax = plt.subplots(figsize=(5,4))
        ax.pie(sc.values, labels=sc.index, autopct='%1.1f%%', colors=C[:len(sc)], startangle=90, wedgeprops={'edgecolor':'white','linewidth':2})
        ax.set_title('Komposisi Status Aktif', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    with cb:
        st.subheader("Ikatan Kerja")
        kc = df_f['ikatan_kerja'].value_counts()
        fig2,ax2 = plt.subplots(figsize=(5,4))
        bars = ax2.barh(kc.index, kc.values, color=C[:len(kc)], edgecolor='white')
        ax2.set_title('Komposisi Ikatan Kerja', fontweight='bold')
        ax2.set_xlabel('Jumlah')
        for b in bars:
            ax2.text(b.get_width()+0.3, b.get_y()+b.get_height()/2, str(int(b.get_width())), va='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()
    st.divider()
    st.subheader("Ringkasan Insight")
    tf = df_f['fakultas'].value_counts().idxmax() if 'fakultas' in df_f.columns else '-'
    tn = df_f['fakultas'].value_counts().max() if 'fakultas' in df_f.columns else 0
    au = int(df_f['usia'].mean()) if 'usia' in df_f.columns else 0
    bl = total - sertif
    st.markdown(f'<div class="ibox"><b>Insight 1:</b> Total pegawai <b>{total:,}</b>, dosen aktif <b>{aktif:,} ({aktif/total*100:.1f}%)</b>.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ibox"><b>Insight 2:</b> Fakultas terbesar: <b>{tf}</b> dengan <b>{tn} pegawai</b>.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ibox"><b>Insight 3:</b> <b>{bl} dosen ({100-pct:.1f}%)</b> belum tersertifikasi.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ibox"><b>Insight 4:</b> Rata-rata usia pegawai <b>{au} tahun</b>.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ibox"><b>Insight 5:</b> Jumlah Profesor hanya <b>{prof} orang</b>, akselerasi jabatan sangat diperlukan.</div>', unsafe_allow_html=True)
with t2:
    st.header("Visualisasi Perbandingan")
    ca,cb = st.columns(2)
    with ca:
        st.subheader("Jumlah Pegawai per Fakultas")
        fd = df_f['fakultas'].value_counts().sort_values()
        fig,ax = plt.subplots(figsize=(6,5))
        bars = ax.barh(fd.index, fd.values, color='#2e6db4', edgecolor='white')
        ax.set_xlabel('Jumlah Pegawai')
        ax.set_title('Pegawai per Fakultas', fontweight='bold')
        for b in bars:
            ax.text(b.get_width()+0.2, b.get_y()+b.get_height()/2, str(int(b.get_width())), va='center', fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    with cb:
        st.subheader("Jabatan per Rumpun Ilmu")
        if 'rumpun_ilmu' in df_f.columns and 'jabatan_akademik' in df_f.columns:
            pv = df_f.dropna(subset=['rumpun_ilmu','jabatan_akademik'])
            pv = pv.groupby(['rumpun_ilmu','jabatan_akademik']).size().unstack(fill_value=0)
            fig2,ax2 = plt.subplots(figsize=(6,5))
            pv.plot(kind='bar', stacked=True, ax=ax2, color=C[:len(pv.columns)], edgecolor='white')
            ax2.set_title('Jabatan per Rumpun Ilmu', fontweight='bold')
            ax2.set_xlabel('Rumpun Ilmu')
            ax2.set_ylabel('Jumlah')
            ax2.legend(fontsize=7)
            plt.xticks(rotation=25, ha='right', fontsize=8)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close()
    st.subheader("Gender per Fakultas")
    if 'jk' in df_f.columns:
        gp = df_f.groupby(['fakultas','jk']).size().unstack(fill_value=0)
        fig3,ax3 = plt.subplots(figsize=(12,4))
        gp.plot(kind='bar', ax=ax3, color=['#e07b39','#2e6db4'], edgecolor='white')
        ax3.set_title('Perbandingan Gender per Fakultas', fontweight='bold')
        ax3.set_xlabel('Fakultas')
        ax3.set_ylabel('Jumlah')
        ax3.legend(title='Jenis Kelamin', fontsize=9)
        plt.xticks(rotation=30, ha='right', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()
    st.subheader("Distribusi Pendidikan")
    if 'pendidikan' in df_f.columns:
        pd2 = df_f['pendidikan'].value_counts()
        fig4,ax4 = plt.subplots(figsize=(6,3.5))
        ax4.bar(pd2.index, pd2.values, color=C[:len(pd2)], edgecolor='white')
        ax4.set_title('Distribusi Tingkat Pendidikan', fontweight='bold')
        ax4.set_xlabel('Pendidikan')
        ax4.set_ylabel('Jumlah')
        for i,v in enumerate(pd2.values):
            ax4.text(i, v+0.3, str(v), ha='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close()
with t3:
    st.header("Visualisasi Time Series")
    ca,cb = st.columns(2)
    with ca:
        st.subheader("Tren Jabatan per Tahun")
        if 'tahun_jabatan' in df_f.columns and 'jabatan_akademik' in df_f.columns:
            ts = df_f.dropna(subset=['tahun_jabatan','jabatan_akademik'])
            ts = ts.groupby(['tahun_jabatan','jabatan_akademik']).size().unstack(fill_value=0)
            fig,ax = plt.subplots(figsize=(6,4))
            for i,cn in enumerate(ts.columns):
                ax.plot(ts.index, ts[cn], marker='o', label=cn, color=C[i%len(C)], linewidth=2)
                x = ts.index.values
                y = ts[cn].values
                if len(x) > 2:
                    z = np.polyfit(x, y, 1)
                    ax.plot(x, np.poly1d(z)(x), '--', color=C[i%len(C)], alpha=0.4, linewidth=1)
            ax.set_title('Tren Jabatan Akademik + Prediksi (--)', fontweight='bold')
            ax.set_xlabel('Tahun')
            ax.set_ylabel('Jumlah')
            ax.legend(fontsize=7)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            st.caption("Garis putus-putus = prediksi tren linear")
    with cb:
        st.subheader("Kumulatif Sertifikasi")
        if 'tahun_sertifikasi' in df_f.columns:
            sg = df_f.dropna(subset=['tahun_sertifikasi'])
            sg = sg.groupby('tahun_sertifikasi').size().reset_index(name='jml')
            sg = sg.sort_values('tahun_sertifikasi')
            sg['kum'] = sg['jml'].cumsum()
            fig2,ax2 = plt.subplots(figsize=(6,4))
            ax2.fill_between(sg['tahun_sertifikasi'], sg['kum'], alpha=0.3, color='#27ae60')
            ax2.plot(sg['tahun_sertifikasi'], sg['kum'], color='#27ae60', marker='o', linewidth=2)
            x = sg['tahun_sertifikasi'].values
            y = sg['kum'].values
            if len(x) > 2:
                z = np.polyfit(x, y, 1)
                xp = np.arange(int(x[-1])+1, int(x[-1])+6)
                ax2.plot(xp, np.poly1d(z)(xp), '--', color='#e07b39', linewidth=2, label='Prediksi')
                ax2.legend(fontsize=8)
            ax2.set_title('Kumulatif Sertifikasi + Prediksi', fontweight='bold')
            ax2.set_xlabel('Tahun')
            ax2.set_ylabel('Jumlah Kumulatif')
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close()
            st.caption("Garis oranye = prediksi tren ke depan")
    st.subheader("Area Chart Tren Jabatan")
    if 'tahun_jabatan' in df_f.columns:
        tg = df_f.dropna(subset=['tahun_jabatan'])
        tg = tg.groupby('tahun_jabatan').size().reset_index(name='jml')
        tg = tg.sort_values('tahun_jabatan')
        fig3,ax3 = plt.subplots(figsize=(11,3.5))
        ax3.fill_between(tg['tahun_jabatan'], tg['jml'], alpha=0.3, color='#2e6db4')
        ax3.plot(tg['tahun_jabatan'], tg['jml'], color='#2e6db4', linewidth=2)
        ax3.set_title('Tren Perolehan Jabatan per Tahun', fontweight='bold')
        ax3.set_xlabel('Tahun')
        ax3.set_ylabel('Jumlah')
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()
with t4:
    st.header("Visualisasi Distribusi")
    ca,cb = st.columns(2)
    with ca:
        st.subheader("Histogram Usia")
        if 'usia' in df_f.columns:
            uv = df_f[(df_f['usia']>=20)&(df_f['usia']<=75)]['usia'].dropna()
            fig,ax = plt.subplots(figsize=(6,4))
            ax.hist(uv, bins=20, color='#2e6db4', edgecolor='white', alpha=0.85)
            ax.axvline(uv.mean(), color='red', linestyle='--', linewidth=1.5, label=f'Rata-rata: {uv.mean():.1f} th')
            ax.set_title('Distribusi Usia Pegawai', fontweight='bold')
            ax.set_xlabel('Usia (tahun)')
            ax.set_ylabel('Jumlah')
            ax.legend(fontsize=9)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
    with cb:
        st.subheader("Box Plot Usia per Fakultas")
        if 'usia' in df_f.columns and 'fakultas' in df_f.columns:
            fl = sorted(df_f['fakultas'].dropna().unique())
            dbp = [df_f[(df_f['fakultas']==f)&(df_f['usia']>=20)&(df_f['usia']<=75)]['usia'].dropna().values for f in fl]
            fig2,ax2 = plt.subplots(figsize=(6,5))
            bp = ax2.boxplot(dbp, tick_labels=[f[:10] for f in fl], orientation='horizontal', patch_artist=True)
            for i,patch in enumerate(bp['boxes']):
                patch.set_facecolor(C[i%len(C)])
                patch.set_alpha(0.7)
            ax2.set_title('Box Plot Usia per Fakultas', fontweight='bold')
            ax2.set_xlabel('Usia (tahun)')
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close()
    st.subheader("Distribusi Jabatan Akademik")
    if 'jabatan_akademik' in df_f.columns:
        jd = df_f['jabatan_akademik'].value_counts()
        fig3,ax3 = plt.subplots(figsize=(8,3.5))
        bars = ax3.bar(jd.index, jd.values, color=C[:len(jd)], edgecolor='white')
        ax3.set_title('Distribusi Jabatan Akademik', fontweight='bold')
        ax3.set_ylabel('Jumlah')
        for b in bars:
            ax3.text(b.get_x()+b.get_width()/2, b.get_height()+0.3, str(int(b.get_height())), ha='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()
with t5:
    st.header("Visualisasi Relationship")
    st.subheader("Bubble Chart: Tahun Jabatan vs Tahun Sertifikasi")
    if 'tahun_jabatan' in df_f.columns and 'tahun_sertifikasi' in df_f.columns:
        sc = df_f.dropna(subset=['tahun_jabatan','tahun_sertifikasi','jabatan_akademik'])
        bb = sc.groupby(['tahun_jabatan','tahun_sertifikasi','jabatan_akademik']).size().reset_index(name='cnt')
        jt = bb['jabatan_akademik'].unique()
        fig,ax = plt.subplots(figsize=(10,5))
        for i,jb in enumerate(jt):
            sub = bb[bb['jabatan_akademik']==jb]
            ax.scatter(sub['tahun_jabatan'], sub['tahun_sertifikasi'], s=sub['cnt']*30, alpha=0.6, color=C[i%len(C)], label=jb, edgecolors='white')
        ax.set_title('Hubungan Tahun Jabatan & Tahun Sertifikasi', fontweight='bold')
        ax.set_xlabel('Tahun Jabatan')
        ax.set_ylabel('Tahun Sertifikasi')
        ax.legend(title='Jabatan', fontsize=9)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        st.caption("Ukuran bubble = jumlah dosen")
    st.subheader("Scatter: Usia vs Tahun Sertifikasi")
    if 'usia' in df_f.columns and 'tahun_sertifikasi' in df_f.columns:
        s2 = df_f.dropna(subset=['usia','tahun_sertifikasi'])
        s2 = s2[(s2['usia']>=20)&(s2['usia']<=75)]
        fig2,ax2 = plt.subplots(figsize=(8,4))
        sc2 = ax2.scatter(s2['usia'], s2['tahun_sertifikasi'], alpha=0.4, c=s2['tahun_sertifikasi'], cmap='viridis', s=20)
        plt.colorbar(sc2, ax=ax2, label='Tahun Sertifikasi')
        xv = s2['usia'].values
        yv = s2['tahun_sertifikasi'].values
        z = np.polyfit(xv, yv, 1)
        ax2.plot(sorted(xv), np.poly1d(z)(sorted(xv)), 'r--', linewidth=1.5, label='Trend')
        ax2.set_title('Hubungan Usia dan Tahun Sertifikasi', fontweight='bold')
        ax2.set_xlabel('Usia (tahun)')
        ax2.set_ylabel('Tahun Sertifikasi')
        ax2.legend()
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()
with t6:
    st.header("Visualisasi Geospasial")
    st.info("Dataset tidak memiliki kolom koordinat geografis. Visualisasi menggunakan pemetaan simbolik Rumpun Ilmu ke wilayah Indonesia.")
    rm = {'RUMPUN ILMU ALAM':'Jawa Timur','TERAPAN':'Jawa Barat','FORMAL':'DKI Jakarta','HUMANIORA':'Jawa Tengah','KEAGAMAAN':'DI Yogyakarta','SOSIAL':'Banten'}
    if 'rumpun_ilmu' in df_f.columns:
        dg = df_f.dropna(subset=['rumpun_ilmu']).copy()
        dg['wilayah'] = dg['rumpun_ilmu'].map(rm)
        gc = dg.groupby('wilayah').size().reset_index(name='jumlah')
        ca,cb = st.columns(2)
        with ca:
            st.markdown("**Pemetaan Rumpun Ilmu ke Wilayah**")
            st.dataframe(pd.DataFrame(list(rm.items()), columns=['Rumpun Ilmu','Wilayah']), use_container_width=True)
            st.dataframe(gc, use_container_width=True)
        with cb:
            fig,ax = plt.subplots(figsize=(6,5))
            bars = ax.barh(gc['wilayah'], gc['jumlah'], color=C[:len(gc)], edgecolor='white')
            ax.set_title('Distribusi per Wilayah (Simbolik)', fontweight='bold')
            ax.set_xlabel('Jumlah Pegawai')
            for b in bars:
                ax.text(b.get_width()+0.2, b.get_y()+b.get_height()/2, str(int(b.get_width())), va='center', fontsize=9)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
with t7:
    st.header("AI Insight & Narrative Visualisation")
    st.markdown("*Insight otomatis dihasilkan berdasarkan analisis statistik data*")
    st.divider()
    total = len(df_f)
    aktif = len(df_f[df_f['stat_aktif']=='Aktif']) if 'stat_aktif' in df_f.columns else 0
    sertif = int(df_f['sertifikasi'].notna().sum()) if 'sertifikasi' in df_f.columns else 0
    bl = total - sertif
    prof = len(df_f[df_f['jabatan_akademik']=='Profesor']) if 'jabatan_akademik' in df_f.columns else 0
    tf = df_f['fakultas'].value_counts().idxmax() if 'fakultas' in df_f.columns else '-'
    tn = df_f['fakultas'].value_counts().max() if 'fakultas' in df_f.columns else 0
    au = df_f['usia'].mean() if 'usia' in df_f.columns else 0
    pred = '-'
    if 'tahun_sertifikasi' in df_f.columns:
        sg = df_f.dropna(subset=['tahun_sertifikasi']).groupby('tahun_sertifikasi').size().reset_index(name='n')
        sg = sg.sort_values('tahun_sertifikasi')
        sg['kum'] = sg['n'].cumsum()
        if len(sg) > 2:
            z = np.polyfit(sg['tahun_sertifikasi'].values, sg['kum'].values, 1)
            p = np.poly1d(z)
            for yr in range(2025,2040):
                if p(yr) >= total*0.8:
                    pred = str(yr)
                    break
    gd = '-'
    gp = 0
    if 'jk' in df_f.columns:
        gc2 = df_f['jk'].value_counts()
        gd = gc2.idxmax()
        gp = gc2.max()/total*100
    tr = 'tidak dapat dianalisis'
    if 'tahun_jabatan' in df_f.columns:
        tr = 'meningkat' if df_f[df_f['tahun_jabatan']>=2015].shape[0] > df_f[df_f['tahun_jabatan']<2015].shape[0] else 'menurun'
    st.markdown(f'<div class="ibox"><b>Insight 1 - Komposisi:</b> Total <b>{total:,} pegawai</b>, aktif <b>{aktif:,} ({aktif/total*100:.1f}%)</b>. Terbesar: <b>{tf}</b> ({tn}).</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ibox"><b>Insight 2 - Sertifikasi:</b> Tersertifikasi <b>{sertif:,} ({sertif/total*100:.1f}%)</b>, belum <b>{bl:,}</b>. Target 80% diperkirakan tahun <b>{pred}</b>.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ibox"><b>Insight 3 - Jabatan:</b> Tren jabatan <b>{tr}</b>. Profesor hanya <b>{prof} orang</b>.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ibox"><b>Insight 4 - Usia:</b> Rata-rata usia <b>{au:.1f} tahun</b>. Perlu perencanaan regenerasi SDM.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ibox"><b>Insight 5 - Gender:</b> Dominan gender <b>{gd}</b> ({gp:.1f}%). Perlu kebijakan kesetaraan.</div>', unsafe_allow_html=True)
    st.divider()
    st.subheader("Rekomendasi Berbasis Data")
    st.markdown(f"1. **Percepatan Sertifikasi** - Prioritaskan {bl:,} dosen belum sertifikasi, terutama yang bergelar S3.")
    st.markdown("2. **Akselerasi Jabatan Akademik** - Program pendampingan untuk dosen tanpa jabatan fungsional.")
    st.markdown("3. **Optimalisasi Distribusi SDM** - Rekrutmen di prodi dengan jumlah dosen rendah.")
    st.markdown(f"4. **Perencanaan Regenerasi** - Rata-rata usia {au:.1f} tahun, rekrutmen dosen muda perlu dilakukan berkala.")
    st.markdown(f"5. **Kesetaraan Gender** - Rekrutmen afirmatif di fakultas dengan distribusi gender tidak proporsional.")
