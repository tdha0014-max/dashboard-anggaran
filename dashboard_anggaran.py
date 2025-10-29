import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import mysql.connector
from mysql.connector import Error

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Anggaran 2025",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS untuk Dark Mode
def apply_theme(dark_mode):
    if dark_mode:
        st.markdown("""
        <style>
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            .css-1d391kg {
                background-color: #262730;
            }
        </style>
        """, unsafe_allow_html=True)


# Sidebar untuk koneksi database dan pengaturan
with st.sidebar:
    st.header("⚙️ Pengaturan")

    # Dark Mode Toggle
    dark_mode = st.toggle("🌙 Dark Mode", value=False)
    apply_theme(dark_mode)

    st.markdown("---")
    st.subheader("🔌 Koneksi Database MySQL")

    use_db = st.checkbox("Gunakan Database MySQL", value=False)

    if use_db:
        db_host = st.text_input("Host", value="localhost")
        db_port = st.number_input("Port", value=3306, min_value=1, max_value=65535)
        db_user = st.text_input("Username", value="root")
        db_password = st.text_input("Password", type="password")
        db_name = st.text_input("Database Name", value="anggaran_db")

        if st.button("🔗 Test Koneksi"):
            try:
                connection = mysql.connector.connect(
                    host=db_host,
                    port=db_port,
                    user=db_user,
                    password=db_password,
                    database=db_name
                )
                if connection.is_connected():
                    st.success("✅ Koneksi berhasil!")
                    connection.close()
            except Error as e:
                st.error(f"❌ Koneksi gagal: {e}")

    st.markdown("---")
    st.info("💡 **Tip**: Aktifkan koneksi database untuk data real-time!")


# Fungsi koneksi ke MySQL
def get_mysql_connection(host, port, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None


# Load data dari MySQL atau fallback ke data statis
@st.cache_data(ttl=300)  # Cache 5 menit
def load_data_from_mysql(_connection):
    try:
        query = """
                SELECT kode_wilayah as kode, \
                       nama_skpd, \
                       anggaran
                FROM anggaran_2025
                WHERE nama_skpd IS NOT NULL \
                  AND nama_skpd != '' \
                """
        df = pd.read_sql(query, _connection)
        # Convert anggaran to numeric
        df['anggaran'] = pd.to_numeric(df['anggaran'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading data from MySQL: {e}")
        return None


# Load data statis (fallback)
@st.cache_data
def load_static_data():
    # Data kategori
    kategori_data = {
        'kode': [
            'UNSUR KEWILAYAHAN',
            'UNSUR PEMERINTAHAN UMUM',
            'UNSUR PENDUKUNG URUSAN PEMERINTAHAN',
            'UNSUR PENGAWASAN URUSAN PEMERINTAHAN',
            'UNSUR PENUNJANG URUSAN PEMERINTAHAN',
            'URUSAN PEMERINTAHAN PILIHAN',
            'URUSAN PEMERINTAHAN WAJIB YANG BERKAITAN DENGAN PELAYANAN DASAR',
            'URUSAN PEMERINTAHAN WAJIB YANG TIDAK BERKAITAN DENGAN PELAYANAN DASAR'
        ],
        'kategori': [
            'Unsur Kewilayahan',
            'Unsur Pemerintahan Umum',
            'Unsur Pendukung',
            'Unsur Pengawasan',
            'Unsur Penunjang',
            'Urusan Pilihan',
            'Urusan Wajib - Pelayanan Dasar',
            'Urusan Wajib - Non Pelayanan Dasar'
        ],
        'anggaran': [
            22863237930, 2278313362, 34471899685, 7735642420,
            168860731367, 35753724291, 518444580026, 45180777831
        ]
    }

    # Data SKPD dengan kategori
    skpd_data = {
        'kode': [
            '7.01.0.00.0.00.01.0000', '7.01.0.00.0.00.02.0000', '7.01.0.00.0.00.03.0000',
            '7.01.0.00.0.00.04.0000', '7.01.0.00.0.00.05.0000', '7.01.0.00.0.00.06.0000',
            '7.01.0.00.0.00.07.0000', '8.01.0.00.0.00.01.0000', '4.01.2.10.3.29.01.0000',
            '4.02.0.00.0.00.01.0000', '6.01.0.00.0.00.01.0000', '5.01.5.05.0.00.01.0000',
            '5.02.0.00.0.00.01.0000', '5.03.5.04.0.00.01.0000', '3.25.0.00.0.00.01.0000',
            '3.26.0.00.0.00.01.0000', '3.27.0.00.0.00.01.0000', '3.27.0.00.0.00.02.0000',
            '3.32.2.07.0.00.02.0000', '1.01.2.22.0.00.01.0000', '1.02.0.00.0.00.01.0000',
            '1.03.0.00.0.00.01.0000', '1.04.0.00.0.00.01.0000', '1.05.0.00.0.00.01.0000',
            '1.05.0.00.0.00.02.0000', '1.06.0.00.0.00.01.0000', '2.09.0.00.0.00.01.0000',
            '2.11.3.28.0.00.01.0000', '2.12.0.00.0.00.01.0000', '2.13.2.08.0.00.01.0000',
            '2.14.0.00.0.00.01.0000', '2.15.0.00.0.00.01.0000', '2.16.2.20.2.21.01.0000',
            '2.18.0.00.0.00.01.0000', '2.19.0.00.0.00.01.0000', '2.23.2.24.0.00.01.0000'
        ],
        'nama_skpd': [
            'Kecamatan Aesesa', 'Kecamatan Boawae', 'Kecamatan Mauponggo',
            'Kecamatan Nangaroro', 'Kecamatan Wolowae', 'Kecamatan Keo Tengah',
            'Kecamatan Aesesa Selatan', 'Badan Kesatuan Bangsa dan Politik',
            'Sekretariat Daerah', 'Sekretariat DPRD',
            'Inspektorat', 'Badan Perencanaan Pembangunan',
            'Badan Keuangan Daerah', 'Badan Kepegawaian',
            'Dinas Kelautan dan Perikanan', 'Dinas Pariwisata', 'Dinas Pertanian',
            'Dinas Peternakan', 'Dinas Transmigrasi',
            'Dinas Pendidikan dan Kebudayaan', 'Dinas Kesehatan',
            'Dinas Pekerjaan Umum', 'Dinas Perumahan Rakyat',
            'Satuan Polisi Pamong Praja', 'Badan Penanggulangan Bencana',
            'Dinas Sosial', 'Dinas Pangan', 'Dinas Lingkungan Hidup',
            'Dinas Kependudukan dan Pencatatan Sipil',
            'Dinas Pemberdayaan Masyarakat',
            'Dinas Pengendalian Penduduk dan KB', 'Dinas Perhubungan',
            'Dinas Komunikasi dan Informatika', 'Dinas Penanaman Modal',
            'Dinas Kepemudaan dan Olahraga', 'Dinas Perpustakaan'
        ],
        'kategori': [
            'Unsur Kewilayahan', 'Unsur Kewilayahan', 'Unsur Kewilayahan',
            'Unsur Kewilayahan', 'Unsur Kewilayahan', 'Unsur Kewilayahan',
            'Unsur Kewilayahan', 'Unsur Pemerintahan Umum', 'Unsur Pendukung',
            'Unsur Pendukung', 'Unsur Pengawasan', 'Unsur Penunjang',
            'Unsur Penunjang', 'Unsur Penunjang', 'Urusan Pilihan',
            'Urusan Pilihan', 'Urusan Pilihan', 'Urusan Pilihan',
            'Urusan Pilihan', 'Urusan Wajib - Pelayanan Dasar', 'Urusan Wajib - Pelayanan Dasar',
            'Urusan Wajib - Pelayanan Dasar', 'Urusan Wajib - Pelayanan Dasar',
            'Urusan Wajib - Pelayanan Dasar', 'Urusan Wajib - Pelayanan Dasar',
            'Urusan Wajib - Pelayanan Dasar', 'Urusan Wajib - Non Pelayanan Dasar',
            'Urusan Wajib - Non Pelayanan Dasar', 'Urusan Wajib - Non Pelayanan Dasar',
            'Urusan Wajib - Non Pelayanan Dasar', 'Urusan Wajib - Non Pelayanan Dasar',
            'Urusan Wajib - Non Pelayanan Dasar', 'Urusan Wajib - Non Pelayanan Dasar',
            'Urusan Wajib - Non Pelayanan Dasar', 'Urusan Wajib - Non Pelayanan Dasar',
            'Urusan Wajib - Non Pelayanan Dasar'
        ],
        'anggaran': [
            6223022625, 7646781503, 2530582520, 2508571150, 1193921348, 1458126928,
            1302231856, 2278313362, 16543274276, 17928625409, 7735642420, 4704900714,
            159364654742, 4328449467, 10918488956, 2792771772, 13357727381, 8264620432,
            186996200, 248036170749, 165156847795, 86179490390, 8419273044,
            5112252744, 2337363871, 3203181433, 2422550560, 3499115744,
            2769261244, 4060458306, 5544150797, 4015991096, 2473281891,
            3229338292, 2666001411, 3607193869
        ]
    }

    # Data trend multi-tahun (simulasi)
    trend_data = {
        'tahun': [2023, 2023, 2023, 2024, 2024, 2024, 2025, 2025, 2025],
        'kategori': ['Pendidikan', 'Kesehatan', 'Infrastruktur'] * 3,
        'anggaran': [
            220000000000, 150000000000, 80000000000,  # 2023
            235000000000, 160000000000, 85000000000,  # 2024
            248036170749, 165156847795, 86179490390  # 2025
        ]
    }

    df_kategori = pd.DataFrame(kategori_data)
    df_skpd = pd.DataFrame(skpd_data)
    df_trend = pd.DataFrame(trend_data)

    df_kategori['anggaran_miliar'] = df_kategori['anggaran'] / 1_000_000_000
    df_skpd['anggaran_miliar'] = df_skpd['anggaran'] / 1_000_000_000
    df_trend['anggaran_miliar'] = df_trend['anggaran'] / 1_000_000_000

    return df_kategori, df_skpd, df_trend


# Load data berdasarkan pilihan
if use_db and all([db_host, db_user, db_password, db_name]):
    connection = get_mysql_connection(db_host, db_port, db_user, db_password, db_name)
    if connection:
        df_skpd_raw = load_data_from_mysql(connection)
        connection.close()

        if df_skpd_raw is not None:
            df_skpd_raw['anggaran_miliar'] = df_skpd_raw['anggaran'] / 1_000_000_000
            # Tambahkan kategori berdasarkan kode
            df_skpd_raw['kategori'] = df_skpd_raw['kode'].apply(
                lambda x: 'Urusan Wajib - Pelayanan Dasar' if x.startswith('1.')
                else 'Urusan Pilihan' if x.startswith('3.')
                else 'Unsur Kewilayahan' if x.startswith('7.')
                else 'Lainnya'
            )
            df_kategori, df_skpd, df_trend = load_static_data()
            df_skpd = df_skpd_raw
            st.sidebar.success("✅ Data dimuat dari MySQL")
        else:
            df_kategori, df_skpd, df_trend = load_static_data()
            st.sidebar.warning("⚠️ Menggunakan data statis")
    else:
        df_kategori, df_skpd, df_trend = load_static_data()
        st.sidebar.warning("⚠️ Menggunakan data statis")
else:
    df_kategori, df_skpd, df_trend = load_static_data()

# Judul Dashboard
st.title("📊 Dashboard Anggaran Pemerintah Daerah 2025")
st.markdown("---")

# Search Box
st.subheader("🔍 Pencarian SKPD")
search_term = st.text_input("Cari nama SKPD...", placeholder="Ketik nama SKPD (contoh: Pendidikan)")

if search_term:
    df_skpd_filtered = df_skpd[df_skpd['nama_skpd'].str.contains(search_term, case=False, na=False)]
    st.info(f"Ditemukan {len(df_skpd_filtered)} SKPD yang cocok dengan '{search_term}'")
else:
    df_skpd_filtered = df_skpd

# Filter Kategori
st.subheader("🎯 Filter Berdasarkan Kategori")
col_f1, col_f2 = st.columns([2, 1])

with col_f1:
    selected_categories = st.multiselect(
        "Pilih Kategori:",
        options=df_skpd['kategori'].unique().tolist(),
        default=df_skpd['kategori'].unique().tolist()
    )

with col_f2:
    if st.button("🔄 Reset Filter"):
        st.rerun()

if selected_categories:
    df_skpd_filtered = df_skpd_filtered[df_skpd_filtered['kategori'].isin(selected_categories)]

st.markdown("---")

# Metrics Row
st.subheader("📈 Ringkasan Anggaran")
col1, col2, col3, col4 = st.columns(4)

total_anggaran = df_kategori['anggaran'].sum()
rata_rata = df_skpd_filtered['anggaran'].mean()
tertinggi = df_skpd_filtered['anggaran'].max()
jumlah_skpd = len(df_skpd_filtered)

with col1:
    st.metric("Total Anggaran", f"Rp {total_anggaran / 1_000_000_000_000:.2f} T")
with col2:
    st.metric("Rata-rata SKPD", f"Rp {rata_rata / 1_000_000_000:.2f} M")
with col3:
    st.metric("Anggaran Tertinggi", f"Rp {tertinggi / 1_000_000_000:.2f} M")
with col4:
    st.metric("Jumlah SKPD", f"{jumlah_skpd}")

st.markdown("---")

# Tab Navigation
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Perbandingan", "📉 Trend", "📋 Data Detail"])

with tab1:
    # Visualisasi 1 & 2
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Distribusi Anggaran per Kategori")
        fig_pie = px.pie(
            df_kategori,
            values='anggaran_miliar',
            names='kategori',
            title='Distribusi Anggaran (Miliar Rupiah)',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=True, height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("📊 Perbandingan Anggaran Kategori")
        fig_bar = px.bar(
            df_kategori.sort_values('anggaran_miliar', ascending=True),
            x='anggaran_miliar',
            y='kategori',
            orientation='h',
            title='Anggaran per Kategori (Miliar Rupiah)',
            labels={'anggaran_miliar': 'Anggaran (Miliar Rp)', 'kategori': 'Kategori'},
            color='anggaran_miliar',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Top 10 SKPD
    st.subheader("🏆 Top 10 SKPD dengan Anggaran Terbesar")
    top_skpd = df_skpd_filtered.nlargest(10, 'anggaran')

    fig_top = px.bar(
        top_skpd,
        x='anggaran_miliar',
        y='nama_skpd',
        orientation='h',
        title='Top 10 SKPD (Miliar Rupiah)',
        labels={'anggaran_miliar': 'Anggaran (Miliar Rp)', 'nama_skpd': 'Nama SKPD'},
        color='anggaran_miliar',
        color_continuous_scale='Viridis',
        text='anggaran_miliar'
    )
    fig_top.update_traces(texttemplate='Rp %{text:.1f}M', textposition='outside')
    fig_top.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_top, use_container_width=True)

with tab2:
    st.subheader("📈 Perbandingan Anggaran Antar SKPD")

    # Pilih SKPD untuk dibandingkan
    skpd_to_compare = st.multiselect(
        "Pilih SKPD untuk dibandingkan (max 10):",
        options=df_skpd_filtered['nama_skpd'].tolist(),
        default=df_skpd_filtered.nlargest(5, 'anggaran')['nama_skpd'].tolist(),
        max_selections=10
    )

    if skpd_to_compare:
        compare_df = df_skpd_filtered[df_skpd_filtered['nama_skpd'].isin(skpd_to_compare)]

        # Bar Chart Comparison
        fig_compare = px.bar(
            compare_df.sort_values('anggaran_miliar', ascending=False),
            x='nama_skpd',
            y='anggaran_miliar',
            title='Perbandingan Anggaran SKPD (Miliar Rupiah)',
            labels={'anggaran_miliar': 'Anggaran (Miliar Rp)', 'nama_skpd': 'SKPD'},
            color='anggaran_miliar',
            color_continuous_scale='Plasma',
            text='anggaran_miliar'
        )
        fig_compare.update_traces(texttemplate='Rp %{text:.1f}M', textposition='outside')
        fig_compare.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig_compare, use_container_width=True)

        # Radar Chart
        st.subheader("📊 Radar Chart Perbandingan")
        fig_radar = go.Figure()

        for skpd in skpd_to_compare[:5]:  # Limit to 5 for readability
            skpd_data = compare_df[compare_df['nama_skpd'] == skpd]
            fig_radar.add_trace(go.Scatterpolar(
                r=[skpd_data['anggaran_miliar'].values[0]],
                theta=[skpd],
                fill='toself',
                name=skpd
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=True,
            height=500
        )
        st.plotly_chart(fig_radar, use_container_width=True)

with tab3:
    st.subheader("📉 Trend Anggaran Multi-Tahun")

    # Line Chart Trend
    fig_trend = px.line(
        df_trend,
        x='tahun',
        y='anggaran_miliar',
        color='kategori',
        markers=True,
        title='Trend Anggaran 2023-2025 (Miliar Rupiah)',
        labels={'anggaran_miliar': 'Anggaran (Miliar Rp)', 'tahun': 'Tahun'}
    )
    fig_trend.update_layout(height=500)
    st.plotly_chart(fig_trend, use_container_width=True)

    # Area Chart
    st.subheader("📊 Area Chart Trend")
    fig_area = px.area(
        df_trend,
        x='tahun',
        y='anggaran_miliar',
        color='kategori',
        title='Komposisi Anggaran dari Tahun ke Tahun',
        labels={'anggaran_miliar': 'Anggaran (Miliar Rp)', 'tahun': 'Tahun'}
    )
    fig_area.update_layout(height=400)
    st.plotly_chart(fig_area, use_container_width=True)

with tab4:
    st.subheader("📋 Data Detail Anggaran SKPD")

    # Format tampilan tabel
    display_df = df_skpd_filtered[['kode', 'nama_skpd', 'kategori', 'anggaran_miliar']].copy()
    display_df['anggaran_miliar'] = display_df['anggaran_miliar'].apply(lambda x: f"Rp {x:.2f} M")
    display_df.columns = ['Kode', 'Nama SKPD', 'Kategori', 'Anggaran']
    display_df = display_df.sort_values('Kode')

    st.dataframe(display_df, use_container_width=True, height=400)

    # Export buttons
    st.subheader("📥 Export Data")
    col1, col2, col3 = st.columns(3)

    with col1:
        # CSV Export
        csv = df_skpd_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name='anggaran_2025.csv',
            mime='text/csv',
        )

    with col2:
        # Excel Export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_skpd_filtered.to_excel(writer, index=False, sheet_name='Anggaran SKPD')
            df_kategori.to_excel(writer, index=False, sheet_name='Kategori')
            df_trend.to_excel(writer, index=False, sheet_name='Trend')

        excel_data = output.getvalue()
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name='anggaran_2025.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    with col3:
        # JSON Export
        json_data = df_skpd_filtered.to_json(orient='records', indent=2)
        st.download_button(
            label="📋 Download JSON",
            data=json_data,
            file_name='anggaran_2025.json',
            mime='application/json',
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><b>Dashboard Anggaran Pemerintah Daerah 2025</b></p>
    <p style='font-size: 12px; color: gray;'>Data diperbarui: Oktober 2025 | Powered by Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)