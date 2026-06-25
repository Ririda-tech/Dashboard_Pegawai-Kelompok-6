import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import warnings, os
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
COLORS = ['#2e6db4','#e07b39','#27ae60','#8e44ad','#c0392b','#16a085','#f39c12','#2980b9']
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if uploaded is None:
    st.title("📊Dashboard Analitik Pegawai Kampus XYZ")
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
t1, t2, t3, t4, t5, t6, t7 = st.tabs([
    "📋 Executive Summary",
    "📊 Perbandingan",
    "📈 Time Series",
    "📉 Distribusi",
    "🔗 Relationship",
    "🗺️ Geospasial",
    "🤖 AI Insight"
])
with t1:
    st.header("📋 Executive Summary")

    total = len(df_f)
    aktif = len(df_f[df_f['stat_aktif'] == 'Aktif']) if 'stat_aktif' in df_f.columns else 0
    sertif = int(df_f['sertifikasi'].notna().sum()) if 'sertifikasi' in df_f.columns else 0
    pct = sertif / total * 100 if total > 0 else 0
    prof = len(df_f[df_f['jabatan_akademik'] == 'Profesor']) if 'jabatan_akademik' in df_f.columns else 0
    belum_sertif = total - sertif
    au = df_f['usia'].mean() if 'usia' in df_f.columns else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👥 Total Pegawai", f"{total:,}")
    c2.metric("✅ Dosen Aktif", f"{aktif:,}", f"{aktif/total*100:.1f}%")
    c3.metric("🎖️ Tersertifikasi", f"{sertif:,}", f"{pct:.1f}%")
    c4.metric("🏅 Profesor", f"{prof}")
    c5.metric("📅 Rata-rata Usia", f"{au:.0f} th")

    st.divider()

    ca, cb = st.columns(2)
    with ca:
        st.subheader("Status Aktif")
        sc = df_f['stat_aktif'].value_counts().reset_index()
        sc.columns = ['Status', 'Jumlah']
        fig_pie = px.pie(sc, values='Jumlah', names='Status',
                         color_discrete_sequence=COLORS,
                         hole=0.35, title='Komposisi Status Aktif')
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

    with cb:
        st.subheader("Ikatan Kerja")
        kc = df_f['ikatan_kerja'].value_counts().reset_index()
        kc.columns = ['Ikatan Kerja', 'Jumlah']
        fig_bar = px.bar(kc, x='Jumlah', y='Ikatan Kerja',
                         orientation='h', text='Jumlah',
                         color='Ikatan Kerja',
                         color_discrete_sequence=COLORS,
                         title='Komposisi Ikatan Kerja')
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.subheader("📝 Ringkasan Insight")
    tf = df_f['fakultas'].value_counts().idxmax() if 'fakultas' in df_f.columns and len(df_f) > 0 else '-'
    tn = df_f['fakultas'].value_counts().max() if 'fakultas' in df_f.columns and len(df_f) > 0 else 0

    st.markdown(f'<div class="ibox"><b>Insight 1 — Komposisi SDM:</b> Total <b>{total:,} pegawai</b>, dosen aktif <b>{aktif:,} ({aktif/total*100:.1f}%)</b>.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ibox"><b>Insight 2 — Dominasi Fakultas:</b> Fakultas terbesar adalah <b>{tf}</b> dengan <b>{tn} pegawai</b>.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ibox"><b>Insight 3 — Gap Sertifikasi:</b> <b>{belum_sertif} dosen ({100-pct:.1f}%)</b> belum tersertifikasi — potensi masalah akreditasi.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ibox"><b>Insight 4 — Profil Usia:</b> Rata-rata usia pegawai <b>{au:.1f} tahun</b>. Perlu perencanaan regenerasi SDM.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ibox"><b>Insight 5 — Jenjang Jabatan:</b> Jumlah Profesor hanya <b>{prof} orang</b> dari total {total} — akselerasi jabatan sangat diperlukan.</div>', unsafe_allow_html=True)

with t2:
    st.header("📊 Visualisasi Perbandingan")

    ca, cb = st.columns(2)
    with ca:
        st.subheader("Jumlah Pegawai per Fakultas")
        fd = df_f['fakultas'].value_counts().reset_index()
        fd.columns = ['Fakultas', 'Jumlah']
        fig = px.bar(fd, x='Jumlah', y='Fakultas', orientation='h',
                     text='Jumlah', color='Jumlah',
                     color_continuous_scale='Blues',
                     title='Pegawai per Fakultas')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with cb:
        st.subheader("Jabatan per Rumpun Ilmu")
        if 'rumpun_ilmu' in df_f.columns and 'jabatan_akademik' in df_f.columns:
            pv = df_f.dropna(subset=['rumpun_ilmu', 'jabatan_akademik'])
            pv = pv.groupby(['rumpun_ilmu', 'jabatan_akademik']).size().reset_index(name='Jumlah')
            # Shorten rumpun_ilmu labels
            pv['rumpun_ilmu'] = pv['rumpun_ilmu'].str.replace('RUMPUN ILMU ', '', regex=False)
            fig2 = px.bar(pv, x='rumpun_ilmu', y='Jumlah',
                          color='jabatan_akademik', barmode='stack',
                          color_discrete_sequence=COLORS,
                          title='Jabatan per Rumpun Ilmu',
                          labels={'rumpun_ilmu': 'Rumpun Ilmu', 'jabatan_akademik': 'Jabatan'})
            fig2.update_layout(height=400, xaxis_tickangle=-20, legend_title='Jabatan')
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Perbandingan Gender per Fakultas")
    if 'jk' in df_f.columns:
        gp = df_f.groupby(['fakultas', 'jk']).size().reset_index(name='Jumlah')
        gp['jk'] = gp['jk'].map({'L': 'Laki-laki', 'P': 'Perempuan'})
        fig3 = px.bar(gp, x='fakultas', y='Jumlah', color='jk',
                      barmode='group',
                      color_discrete_map={'Laki-laki': '#2e6db4', 'Perempuan': '#e07b39'},
                      title='Perbandingan Gender per Fakultas',
                      labels={'fakultas': 'Fakultas', 'jk': 'Jenis Kelamin'})
        fig3.update_layout(height=380, xaxis_tickangle=-20)
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Distribusi Tingkat Pendidikan")
    if 'pendidikan' in df_f.columns:
        pd2 = df_f['pendidikan'].value_counts().reset_index()
        pd2.columns = ['Pendidikan', 'Jumlah']
        fig4 = px.bar(pd2, x='Pendidikan', y='Jumlah', text='Jumlah',
                      color='Pendidikan',
                      color_discrete_sequence=COLORS,
                      title='Distribusi Tingkat Pendidikan')
        fig4.update_traces(textposition='outside')
        fig4.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

with t3:
    st.header("📈 Visualisasi Time Series")

    ca, cb = st.columns(2)
    with ca:
        st.subheader("Tren Jabatan per Tahun + Prediksi")
        if 'tahun_jabatan' in df_f.columns and 'jabatan_akademik' in df_f.columns:
            ts = df_f.dropna(subset=['tahun_jabatan', 'jabatan_akademik'])
            ts = ts.groupby(['tahun_jabatan', 'jabatan_akademik']).size().reset_index(name='Jumlah')
            ts['tahun_jabatan'] = ts['tahun_jabatan'].astype(int)

            fig = px.line(ts, x='tahun_jabatan', y='Jumlah', color='jabatan_akademik',
                          markers=True,
                          color_discrete_sequence=COLORS,
                          title='Tren Jabatan Akademik per Tahun',
                          labels={'tahun_jabatan': 'Tahun', 'jabatan_akademik': 'Jabatan'})

            # Prediksi linear per jabatan
            for jab in ts['jabatan_akademik'].unique():
                sub = ts[ts['jabatan_akademik'] == jab].sort_values('tahun_jabatan')
                if len(sub) > 2:
                    x = sub['tahun_jabatan'].values
                    y = sub['Jumlah'].values
                    z = np.polyfit(x, y, 1)
                    xp = np.arange(int(x[-1]) + 1, int(x[-1]) + 4)
                    yp = np.poly1d(z)(xp)
                    fig.add_scatter(x=xp, y=yp, mode='lines',
                                    line=dict(dash='dot', width=1.5),
                                    name=f'{jab} (prediksi)',
                                    showlegend=False)

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Garis putus-putus = prediksi tren linear 3 tahun ke depan")

    with cb:
        st.subheader("Kumulatif Sertifikasi + Prediksi")
        if 'tahun_sertifikasi' in df_f.columns:
            sg = df_f.dropna(subset=['tahun_sertifikasi'])
            sg = sg.groupby('tahun_sertifikasi').size().reset_index(name='jml')
            sg = sg.sort_values('tahun_sertifikasi')
            sg['kum'] = sg['jml'].cumsum()

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=sg['tahun_sertifikasi'], y=sg['kum'],
                mode='lines+markers', name='Kumulatif Aktual',
                line=dict(color='#27ae60', width=2),
                fill='tozeroy', fillcolor='rgba(39,174,96,0.15)'
            ))

            # Prediksi
            if len(sg) > 2:
                x = sg['tahun_sertifikasi'].values
                y = sg['kum'].values
                z = np.polyfit(x, y, 1)
                xp = np.arange(int(x[-1]) + 1, int(x[-1]) + 6)
                yp = np.poly1d(z)(xp)
                fig2.add_trace(go.Scatter(
                    x=xp, y=yp, mode='lines+markers',
                    name='Prediksi', line=dict(color='#e07b39', dash='dash', width=2)
                ))

            fig2.update_layout(
                title='Kumulatif Sertifikasi + Prediksi 5 Tahun',
                xaxis_title='Tahun', yaxis_title='Jumlah Kumulatif',
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.caption("Garis oranye = prediksi tren ke depan")

    st.subheader("Area Chart — Perolehan Jabatan per Tahun")
    if 'tahun_jabatan' in df_f.columns:
        tg = df_f.dropna(subset=['tahun_jabatan'])
        tg = tg.groupby('tahun_jabatan').size().reset_index(name='Jumlah')
        tg = tg.sort_values('tahun_jabatan')
        fig3 = px.area(tg, x='tahun_jabatan', y='Jumlah',
                       color_discrete_sequence=['#2e6db4'],
                       title='Tren Perolehan Jabatan per Tahun',
                       labels={'tahun_jabatan': 'Tahun'})
        fig3.update_layout(height=300)
        st.plotly_chart(fig3, use_container_width=True)
with t4:
    st.header("📉 Visualisasi Distribusi")

    ca, cb = st.columns(2)
    with ca:
        st.subheader("Histogram Usia Pegawai")
        if 'usia' in df_f.columns:
            uv = df_f[(df_f['usia'] >= 20) & (df_f['usia'] <= 75)]['usia'].dropna()
            fig = px.histogram(
                uv, nbins=20,
                color_discrete_sequence=['#2e6db4'],
                title='Distribusi Usia Pegawai',
                labels={'value': 'Usia (tahun)', 'count': 'Jumlah'}
            )
            fig.add_vline(x=uv.mean(), line_dash='dash', line_color='red',
                          annotation_text=f'Mean: {uv.mean():.1f}', annotation_position='top right')
            fig.add_vline(x=uv.median(), line_dash='dot', line_color='green',
                          annotation_text=f'Median: {uv.median():.1f}', annotation_position='top left')
            fig.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with cb:
        st.subheader("Box Plot Usia per Fakultas")
        if 'usia' in df_f.columns and 'fakultas' in df_f.columns:
            bdf = df_f[(df_f['usia'] >= 20) & (df_f['usia'] <= 75)].dropna(subset=['usia', 'fakultas'])
            fig2 = px.box(bdf, x='usia', y='fakultas', color='fakultas',
                          color_discrete_sequence=COLORS,
                          title='Box Plot Usia per Fakultas',
                          labels={'usia': 'Usia (tahun)', 'fakultas': 'Fakultas'})
            fig2.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Distribusi Jabatan Akademik")
    if 'jabatan_akademik' in df_f.columns:
        order_jab = ['Asisten Ahli', 'Lektor', 'Lektor Kepala', 'Profesor']
        jd = df_f.dropna(subset=['jabatan_akademik'])
        jd = jd.groupby('jabatan_akademik').size().reset_index(name='Jumlah')
        jd['jabatan_akademik'] = pd.Categorical(jd['jabatan_akademik'],
                                                 categories=[x for x in order_jab if x in jd['jabatan_akademik'].values],
                                                 ordered=True)
        jd = jd.sort_values('jabatan_akademik')
        fig3 = px.bar(jd, x='jabatan_akademik', y='Jumlah',
                      text='Jumlah', color='jabatan_akademik',
                      color_discrete_sequence=COLORS,
                      title='Distribusi Jabatan Akademik (Jenjang Karir)',
                      labels={'jabatan_akademik': 'Jabatan'})
        fig3.update_traces(textposition='outside')
        fig3.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Distribusi Pangkat ASN")
    if 'pangkat' in df_f.columns:
        pk = df_f.dropna(subset=['pangkat'])['pangkat'].value_counts().reset_index()
        pk.columns = ['Pangkat', 'Jumlah']
        fig4 = px.bar(pk, x='Jumlah', y='Pangkat', orientation='h',
                      text='Jumlah', color='Jumlah',
                      color_continuous_scale='Blues',
                      title='Distribusi Pangkat / Golongan ASN')
        fig4.update_traces(textposition='outside')
        fig4.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

with t5:
    st.header("🔗 Visualisasi Relationship")

    st.subheader("Bubble Chart — Tahun Jabatan vs Tahun Sertifikasi")
    if 'tahun_jabatan' in df_f.columns and 'tahun_sertifikasi' in df_f.columns:
        sc = df_f.dropna(subset=['tahun_jabatan', 'tahun_sertifikasi', 'jabatan_akademik'])
        bb = sc.groupby(['tahun_jabatan', 'tahun_sertifikasi', 'jabatan_akademik']).size().reset_index(name='cnt')
        bb['tahun_jabatan'] = bb['tahun_jabatan'].astype(int)
        bb['tahun_sertifikasi'] = bb['tahun_sertifikasi'].astype(int)
        fig = px.scatter(bb, x='tahun_jabatan', y='tahun_sertifikasi',
                         size='cnt', color='jabatan_akademik',
                         color_discrete_sequence=COLORS,
                         hover_data=['cnt'],
                         title='Hubungan Tahun Jabatan & Tahun Sertifikasi',
                         labels={
                             'tahun_jabatan': 'Tahun Jabatan',
                             'tahun_sertifikasi': 'Tahun Sertifikasi',
                             'jabatan_akademik': 'Jabatan',
                             'cnt': 'Jumlah Dosen'
                         })
        fig.update_layout(height=480)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Ukuran bubble = jumlah dosen pada kombinasi tersebut. Hover untuk detail.")

    st.subheader("Scatter Plot — Usia vs Tahun Sertifikasi")
    if 'usia' in df_f.columns and 'tahun_sertifikasi' in df_f.columns:
        s2 = df_f.dropna(subset=['usia', 'tahun_sertifikasi', 'jabatan_akademik'])
        s2 = s2[(s2['usia'] >= 20) & (s2['usia'] <= 75)]
        fig2 = px.scatter(s2, x='usia', y='tahun_sertifikasi',
                          color='jabatan_akademik',
                          color_discrete_sequence=COLORS,
                          trendline='ols',
                          title='Hubungan Usia dan Tahun Sertifikasi',
                          labels={
                              'usia': 'Usia (tahun)',
                              'tahun_sertifikasi': 'Tahun Sertifikasi',
                              'jabatan_akademik': 'Jabatan'
                          },
                          hover_data=['fakultas'] if 'fakultas' in s2.columns else None)
        fig2.update_layout(height=450)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Garis trend = regresi linear OLS per jabatan.")

with t6:
    st.header("🗺️ Visualisasi Geospasial")
    st.info("Dataset tidak memiliki kolom koordinat langsung. Rumpun ilmu dipetakan ke wilayah domisili kampus dan klaster regional yang relevan.")

    # Mapping rumpun ilmu → koordinat kota/wilayah di Indonesia
    RUMPUN_GEO = {
        'RUMPUN ILMU ALAM':      {'lat': -7.2504, 'lon': 112.7688, 'kota': 'Surabaya, Jawa Timur'},
        'RUMPUN ILMU TERAPAN':   {'lat': -6.9175,  'lon': 107.6191, 'kota': 'Bandung, Jawa Barat'},
        'RUMPUN ILMU FORMAL':    {'lat': -6.2088,  'lon': 106.8456, 'kota': 'Jakarta, DKI Jakarta'},
        'RUMPUN ILMU HUMANIORA': {'lat': -7.0051,  'lon': 110.4381, 'kota': 'Semarang, Jawa Tengah'},
        'RUMPUN ILMU KEAGAMAAN': {'lat': -7.7956,  'lon': 110.3695, 'kota': 'Yogyakarta'},
        'RUMPUN ILMU SOSIAL':    {'lat': -6.1781,  'lon': 106.6298, 'kota': 'Tangerang, Banten'},
    }

    if 'rumpun_ilmu' in df_f.columns:
        dg = df_f.dropna(subset=['rumpun_ilmu']).copy()
        gc = dg.groupby('rumpun_ilmu').size().reset_index(name='Jumlah')

        # Tambah koordinat
        gc['lat'] = gc['rumpun_ilmu'].map(lambda r: RUMPUN_GEO.get(r, {}).get('lat', -6.2))
        gc['lon'] = gc['rumpun_ilmu'].map(lambda r: RUMPUN_GEO.get(r, {}).get('lon', 106.8))
        gc['kota'] = gc['rumpun_ilmu'].map(lambda r: RUMPUN_GEO.get(r, {}).get('kota', ''))
        gc['rumpun_label'] = gc['rumpun_ilmu'].str.replace('RUMPUN ILMU ', '', regex=False)

        ca, cb = st.columns([2, 1])
        with ca:
            st.subheader("🗺️ Peta Distribusi Rumpun Ilmu (Folium Interactive)")

            # Buat peta Folium
            m = folium.Map(location=[-2.5, 108.0], zoom_start=5,
                           tiles='CartoDB positron')

            # Skala lingkaran: radius proporsional ke jumlah
            max_jml = gc['Jumlah'].max()
            color_map = {
                'ALAM': '#2e6db4', 'TERAPAN': '#e07b39', 'FORMAL': '#27ae60',
                'HUMANIORA': '#8e44ad', 'KEAGAMAAN': '#c0392b', 'SOSIAL': '#16a085'
            }

            for _, row in gc.iterrows():
                label = row['rumpun_label']
                color = color_map.get(label, '#2e6db4')
                radius = max(15, int(row['Jumlah'] / max_jml * 60))

                popup_html = f"""
                <div style='font-family:Arial; min-width:160px'>
                    <b style='color:{color}'>Rumpun Ilmu {label}</b><br>
                    📍 {row['kota']}<br>
                    👥 <b>{row['Jumlah']} pegawai</b><br>
                    📊 {row['Jumlah']/len(df_f)*100:.1f}% dari total
                </div>
                """
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=radius,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.6,
                    popup=folium.Popup(popup_html, max_width=200),
                    tooltip=f"Rumpun {label}: {row['Jumlah']} pegawai"
                ).add_to(m)

                folium.Marker(
                    location=[row['lat'], row['lon']],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size:10px;font-weight:bold;color:{color};'
                             f'text-shadow:1px 1px 2px white;margin-top:-10px">{row["Jumlah"]}</div>',
                        icon_size=(40, 20),
                        icon_anchor=(20, 0)
                    )
                ).add_to(m)

            st_folium(m, use_container_width=True, height=400, returned_objects=[])

        with cb:
            st.subheader("📊 Tabel Distribusi")
            display_gc = gc[['rumpun_label', 'kota', 'Jumlah']].copy()
            display_gc.columns = ['Rumpun Ilmu', 'Kota Ref.', 'Jumlah']
            display_gc['%'] = (display_gc['Jumlah'] / display_gc['Jumlah'].sum() * 100).round(1)
            display_gc = display_gc.sort_values('Jumlah', ascending=False)
            st.dataframe(display_gc, use_container_width=True, hide_index=True)

            # Bar chart geospasial
            fig_geo = px.bar(
                display_gc, x='Jumlah', y='Rumpun Ilmu',
                orientation='h', text='Jumlah',
                color='Rumpun Ilmu',
                color_discrete_sequence=COLORS,
                title='Distribusi per Rumpun Ilmu'
            )
            fig_geo.update_traces(textposition='outside')
            fig_geo.update_layout(height=320, showlegend=False)
            st.plotly_chart(fig_geo, use_container_width=True)

        # Plotly peta Indonesia bubble chart
        st.subheader("📍 Bubble Map Interaktif (Plotly)")
        fig_map = px.scatter_geo(
            gc,
            lat='lat', lon='lon',
            size='Jumlah',
            color='rumpun_label',
            hover_name='rumpun_label',
            hover_data={'Jumlah': True, 'kota': True, 'lat': False, 'lon': False},
            color_discrete_sequence=COLORS,
            size_max=40,
            title='Peta Distribusi Rumpun Ilmu di Indonesia',
            labels={'rumpun_label': 'Rumpun Ilmu', 'kota': 'Kota Referensi'}
        )
        fig_map.update_geos(
            scope='asia',
            center=dict(lat=-2.5, lon=118),
            projection_scale=5,
            showland=True, landcolor='#f5f5f0',
            showocean=True, oceancolor='#d0e8f5',
            showcoastlines=True, coastlinecolor='#aaa',
            showcountries=True, countrycolor='#999'
        )
        fig_map.update_layout(height=420, legend_title='Rumpun Ilmu')
        st.plotly_chart(fig_map, use_container_width=True)

with t7:
    st.header("🤖 AI Insight & Narrative Visualisation")
    st.markdown("*Insight otomatis dihasilkan berdasarkan analisis statistik data yang difilter.*")
    st.divider()

    # Hitung semua metrik
    total = len(df_f)
    aktif = len(df_f[df_f['stat_aktif'] == 'Aktif']) if 'stat_aktif' in df_f.columns else 0
    sertif = int(df_f['sertifikasi'].notna().sum()) if 'sertifikasi' in df_f.columns else 0
    bl = total - sertif
    prof = len(df_f[df_f['jabatan_akademik'] == 'Profesor']) if 'jabatan_akademik' in df_f.columns else 0
    tf = df_f['fakultas'].value_counts().idxmax() if 'fakultas' in df_f.columns else '-'
    tn = df_f['fakultas'].value_counts().max() if 'fakultas' in df_f.columns else 0
    au = df_f['usia'].mean() if 'usia' in df_f.columns else 0
    pct = sertif / total * 100 if total > 0 else 0

    # Prediksi target 80% sertifikasi
    pred = 'tidak dapat diestimasi'
    if 'tahun_sertifikasi' in df_f.columns:
        sg = df_f.dropna(subset=['tahun_sertifikasi']).groupby('tahun_sertifikasi').size().reset_index(name='n')
        sg = sg.sort_values('tahun_sertifikasi')
        sg['kum'] = sg['n'].cumsum()
        if len(sg) > 2:
            z = np.polyfit(sg['tahun_sertifikasi'].values, sg['kum'].values, 1)
            p = np.poly1d(z)
            for yr in range(2025, 2045):
                if p(yr) >= total * 0.8:
                    pred = str(yr)
                    break

    # Gender dominan
    gd = '-'
    gp_val = 0
    if 'jk' in df_f.columns:
        gc2 = df_f['jk'].value_counts()
        gd = 'Laki-laki' if gc2.idxmax() == 'L' else 'Perempuan'
        gp_val = gc2.max() / total * 100

    # Tren jabatan
    tr = 'tidak dapat dianalisis'
    if 'tahun_jabatan' in df_f.columns:
        mid = 2015
        tr = 'meningkat' if df_f[df_f['tahun_jabatan'] >= mid].shape[0] > df_f[df_f['tahun_jabatan'] < mid].shape[0] else 'menurun'

    # S3 belum sertif
    s3_belum = 0
    if 'pendidikan' in df_f.columns and 'sertifikasi' in df_f.columns:
        s3_belum = len(df_f[(df_f['pendidikan'] == 'S3') & (df_f['sertifikasi'].isna())])

    # Gauge chart sertifikasi
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        delta={'reference': 80, 'suffix': '%'},
        title={'text': "Tingkat Sertifikasi (%)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': '#27ae60' if pct >= 80 else '#e07b39'},
            'steps': [
                {'range': [0, 50], 'color': '#ffcccc'},
                {'range': [50, 80], 'color': '#ffe8cc'},
                {'range': [80, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 3},
                'thickness': 0.75,
                'value': 80
            }
        },
        number={'suffix': '%', 'font': {'size': 40}}
    ))
    fig_gauge.update_layout(height=280)

    col_g, col_ins = st.columns([1, 2])
    with col_g:
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption("Target sertifikasi: 80% (garis merah). Saat ini: {:.1f}%".format(pct))

    with col_ins:
        st.markdown("### 💡 5 Insight Utama")
        st.markdown(f'<div class="ibox"><b>Insight 1 — Komposisi SDM:</b> Total <b>{total:,} pegawai</b> aktif <b>{aktif:,} ({aktif/total*100:.1f}%)</b>. Fakultas terbesar <b>{tf}</b> ({tn} orang).</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ibox"><b>Insight 2 — Gap Sertifikasi:</b> Tersertifikasi <b>{sertif:,} ({pct:.1f}%)</b>, masih <b>{bl:,} belum</b>. Target 80% diperkirakan tercapai tahun <b>{pred}</b>. Ada <b>{s3_belum} dosen S3</b> yang belum sertifikasi — prioritas utama.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ibox"><b>Insight 3 — Tren Jabatan:</b> Tren perolehan jabatan akademik cenderung <b>{tr}</b> sejak 2015. Profesor hanya <b>{prof} orang</b> — perlu program akselerasi guru besar.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ibox"><b>Insight 4 — Profil Usia:</b> Rata-rata usia pegawai <b>{au:.1f} tahun</b>. Risiko aging workforce; diperlukan rekrutmen dosen muda secara berkelanjutan.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ibox"><b>Insight 5 — Kesetaraan Gender:</b> Dominan gender <b>{gd}</b> ({gp_val:.1f}%). Kebijakan rekrutmen afirmatif diperlukan untuk keseimbangan representasi.</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("📌 Rekomendasi Berbasis Data")
    rekom = [
    f"Percepatan Sertifikasi Dosen S3 — {s3_belum:,} dosen bergelar S3 belum tersertifikasi. Prioritaskan kelompok ini karena memenuhi syarat akademik dan dapat mempercepat pencapaian target 80% (estimasi: {pred}).",

    f"Akselerasi Jabatan Akademik ke Profesor — Hanya {prof} Profesor dari {total:,} pegawai ({prof/total*100:.1f}%). Buat program pendampingan penulisan karya ilmiah dan pengajuan jabatan fungsional.",

    f"Optimalisasi Distribusi SDM Antar Fakultas — Terdapat ketimpangan signifikan. FK memiliki {df_f[df_f['fakultas']=='FK'].shape[0]} dosen sementara FT hanya {df_f[df_f['fakultas']=='FT'].shape[0]}.",

    f"Perencanaan Regenerasi SDM — Rata-rata usia {au:.1f} tahun. Susun peta jalan rekrutmen dosen muda secara berkelanjutan.",

    f"Kebijakan Kesetaraan Gender — Gender {gd} mendominasi ({gp_val:.1f}%). Terapkan kebijakan untuk menjaga keseimbangan representasi."
]

for i, r in enumerate(rekom, 1):
    st.info(f"Rekomendasi {i}\n\n{r}")
