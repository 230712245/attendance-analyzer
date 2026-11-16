import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman Web
st.set_page_config(page_title="Attendance Analyzer", layout="wide")

st.title("🚨 Employee Attendance Analyzer")
st.write("Sistem Cerdas Pendeteksi Kejanggalan Jam Kehadiran Karyawan (Dynamic Shift Auto-Detect)")

@st.cache_data
def load_data():
    return pd.read_csv('Model_Result_Attendance_V2.csv')

df = load_data()

# --- FITUR TAMBAHAN 1: SIDEBAR FILTERING ---
st.sidebar.header("🔍 Filter Investigasi HR")

# Dropdown Filter Departemen
list_dept = ['Semua Departemen'] + list(df['Departemen'].dropna().unique())
selected_dept = st.sidebar.selectbox("Pilih Departemen", list_dept)

# Dropdown Filter Shift
list_shift = ['Semua Shift'] + list(df['Kategori_Shift'].dropna().unique())
selected_shift = st.sidebar.selectbox("Pilih Kategori Shift", list_shift)

# Terapkan Filter pada Data
df_filtered = df.copy()
if selected_dept != 'Semua Departemen':
    df_filtered = df_filtered[df_filtered['Departemen'] == selected_dept]
if selected_shift != 'Semua Shift':
    df_filtered = df_filtered[df_filtered['Kategori_Shift'] == selected_shift]

# --- 1. TAMPILKAN KPI ---
total_data = len(df_filtered)
total_anomali = len(df_filtered[df_filtered['Label_AI'] == 'Anomali'])
total_normal = total_data - total_anomali

col1, col2, col3 = st.columns(3)
col1.info(f"**Total Absensi Terfilter**\n\n### {total_data} Log")
col2.success(f"**Absensi Wajar (Normal)**\n\n### {total_normal} Log")
col3.error(f"**Kejanggalan (Anomali)**\n\n### {total_anomali} Log")

st.markdown("---")

# Layout 2 Kolom untuk Grafik
c1, c2 = st.columns(2)

with c1:
    # Grafik 1: Scatter Plot Sebaran Waktu
    st.subheader("📊 Sebaran Waktu Kehadiran")
    fig1 = px.scatter(df_filtered, x='Timestamp', y='Hour_Decimal', color='Label_AI', 
                     color_discrete_map={'Normal': '#28a745', 'Anomali': '#dc3545'},
                     labels={'Hour_Decimal': 'Jam (Desimal)', 'Timestamp': 'Tanggal'})
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    # --- FITUR TAMBAHAN 2: GRAFIK PENYUMBANG ANOMALI ---
    st.subheader("🏢 Departemen Terbanyak Anomali")
    df_anomali_only = df_filtered[df_filtered['Label_AI'] == 'Anomali']
    
    if not df_anomali_only.empty:
        dept_count = df_anomali_only['Departemen'].value_counts().reset_index()
        dept_count.columns = ['Departemen', 'Jumlah Anomali']
        fig2 = px.bar(dept_count, x='Jumlah Anomali', y='Departemen', orientation='h', 
                      color='Jumlah Anomali', color_continuous_scale='Reds')
        fig2.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.success("🎉 Tidak ada anomali pada filter ini.")

# --- FITUR TAMBAHAN 3: TABEL & TOMBOL DOWNLOAD ---
st.subheader("📋 Daftar Target Investigasi")
if not df_anomali_only.empty:
    st.table(df_anomali_only[['Timestamp', 'Employee_ID', 'Departemen', 'Kategori_Shift', 'Hour_Decimal']].sort_values(by='Hour_Decimal'))
    
    # Tombol Ekspor Data ke CSV
    csv = df_anomali_only.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data Anomali (CSV)",
        data=csv,
        file_name='Target_Investigasi_HR.csv',
        mime='text/csv',
    )
else:
    st.info("Tabel kosong karena tidak ada anomali yang ditemukan.")
