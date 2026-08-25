import base64
import io
import mysql.connector
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Import ReportLab untuk Export PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ==============================================================================
# 1. KONFIGURASI HALAMAN & DATABASE MYSQL
# ==============================================================================
st.set_page_config(
    page_title="Sistem Pengolahan Nilai Siswa",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Sesuaikan jika MySQL Anda menggunakan password
    "database": "db_nilai_siswa",
    "port": 3306,
}


@st.cache_resource
def get_db_connection():
  return mysql.connector.connect(**DB_CONFIG)


def execute_query(query, params=None):
  conn = mysql.connector.connect(**DB_CONFIG)
  cursor = conn.cursor(dictionary=True)
  cursor.execute(query, params or ())
  result = cursor.fetchall()
  conn.close()
  return result


def execute_commit(query, params=None):
  conn = mysql.connector.connect(**DB_CONFIG)
  cursor = conn.cursor()
  cursor.execute(query, params or ())
  conn.commit()
  conn.close()


# ==============================================================================
# 2. LOAD DATA DARI MYSQL & FUNGSI GENERATE PDF
# ==============================================================================
@st.cache_data(ttl=300)
def load_full_data():
  query = """
        SELECT 
            s.nis,
            s.nisn,
            s.nama_siswa,
            s.jenis_kelamin,
            s.ttl,
            k.nama_kelas,
            mp.nama_mapel,
            n.semester,
            n.nilai
        FROM nilai n
        JOIN siswa s ON n.nis = s.nis
        LEFT JOIN kelas k ON s.id_kelas = k.id_kelas
        JOIN mata_pelajaran mp ON n.id_mapel = mp.id_mapel
    """
  data = execute_query(query)
  df = pd.DataFrame(data)

  if not df.empty:
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")

  return df


def generate_pdf_transkrip(info_siswa, df_siswa):
  """Fungsi pembentuk dokumen PDF Transkrip Nilai Format SMKN 26 Jakarta"""
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      buffer,
      pagesize=portrait(A4),
      rightMargin=0.8 * cm,
      leftMargin=0.8 * cm,
      topMargin=0.8 * cm,
      bottomMargin=0.8 * cm,
  )

  elements = []
  styles = getSampleStyleSheet()

  style_center_bold = ParagraphStyle(
      "CenterBold",
      parent=styles["Normal"],
      fontName="Helvetica-Bold",
      fontSize=9,
      leading=11,
      alignment=1,
  )
  style_header_title = ParagraphStyle(
      "HeaderTitle",
      parent=styles["Normal"],
      fontName="Helvetica-Bold",
      fontSize=11,
      leading=13,
      alignment=1,
  )
  style_cell = ParagraphStyle(
      "CellText",
      parent=styles["Normal"],
      fontName="Helvetica",
      fontSize=7,
      leading=8.5,
  )
  style_cell_center = ParagraphStyle(
      "CellCenter",
      parent=styles["Normal"],
      fontName="Helvetica",
      fontSize=7,
      leading=8.5,
      alignment=1,
  )

  zero_padding_style = TableStyle([
      ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
      ("LEFTPADDING", (0, 0), (-1, -1), 0),
      ("RIGHTPADDING", (0, 0), (-1, -1), 0),
      ("TOPPADDING", (0, 0), (-1, -1), 1),
      ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
  ])

  kop_text = Paragraph(
      "<b>PEMERINTAH PROVINSI DAERAH KHUSUS IBUKOTA JAKARTA</b><br/>"
      "<b>DINAS PENDIDIKAN</b><br/>"
      "<font size=10><b>SEKOLAH MENENGAH KEJURUAN NEGERI 26 JAKARTA</b></font><br/>"
      "<font size=6.5>Jalan Balai Pustaka Baru I Rawamangun Jakarta Timur<br/>"
      "E-mail: smkn26jkt@gmail.com | Website: www.smkn26jakarta.sch.id</font>",
      style_center_bold,
  )

  kop_table = Table(
      [[Paragraph("", style_cell), kop_text, Paragraph("", style_cell)]],
      colWidths=[1.5 * cm, 16.4 * cm, 1.5 * cm],
  )
  kop_table.setStyle(zero_padding_style)
  elements.append(kop_table)
  elements.append(
      HRFlowable(
          width="100%",
          thickness=1.2,
          color=colors.black,
          spaceBefore=2,
          spaceAfter=4,
      )
  )

  elements.append(Paragraph("<u>TRANSKRIP NILAI</u>", style_header_title))
  elements.append(Spacer(1, 4))

  data_left = [
      [
          Paragraph("Nama Siswa", style_cell),
          Paragraph(":", style_cell),
          Paragraph(f"<b>{info_siswa.get('nama_siswa', '-')}</b>", style_cell),
      ],
      [
          Paragraph("NIS / NISN", style_cell),
          Paragraph(":", style_cell),
          Paragraph(
              f"{info_siswa.get('nis', '-')} / {info_siswa.get('nisn', '-')}",
              style_cell,
          ),
      ],
      [
          Paragraph("Tempat, Tgl Lahir", style_cell),
          Paragraph(":", style_cell),
          Paragraph(str(info_siswa.get("ttl", "-")), style_cell),
      ],
      [
          Paragraph("Jenis Kelamin", style_cell),
          Paragraph(":", style_cell),
          Paragraph(str(info_siswa.get("jenis_kelamin", "-")), style_cell),
      ],
  ]

  data_right = [
      [
          Paragraph("Bidang Keahlian", style_cell),
          Paragraph(":", style_cell),
          Paragraph("Teknologi dan Rekayasa", style_cell),
      ],
      [
          Paragraph("Program Keahlian", style_cell),
          Paragraph(":", style_cell),
          Paragraph("Teknik Konstruksi dan Properti", style_cell),
      ],
      [
          Paragraph("Kompetensi Keahlian", style_cell),
          Paragraph(":", style_cell),
          Paragraph("Konstruksi Gedung, Sanitasi dan Perawatan", style_cell),
      ],
  ]

  tbl_l = Table(
      data_left, colWidths=[2.3 * cm, 0.3 * cm, 5.6 * cm], rowHeights=11
  )
  tbl_l.setStyle(zero_padding_style)

  tbl_r = Table(
      data_right, colWidths=[2.8 * cm, 0.3 * cm, 5.6 * cm], rowHeights=11
  )
  tbl_r.setStyle(zero_padding_style)

  photo_box = Paragraph(
      "<font size=6><b>PAS FOTO<br/>3 x 4</b></font>", style_center_bold
  )

  info_table = Table(
      [[tbl_l, tbl_r, photo_box]], colWidths=[8.2 * cm, 8.7 * cm, 2.5 * cm]
  )
  info_table.setStyle(zero_padding_style)
  elements.append(info_table)
  elements.append(Spacer(1, 6))

  table_data = [[
      Paragraph("<b>No</b>", style_cell_center),
      Paragraph("<b>Mata Pelajaran</b>", style_cell_center),
      Paragraph("<b>NILAI RAPOR SEMESTER</b>", style_cell_center),
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      Paragraph("<b>Ujian Sekolah</b>", style_cell_center),
  ]]

  table_data.append([
      "",
      "",
      Paragraph("<b>1</b>", style_cell_center),
      Paragraph("<b>2</b>", style_cell_center),
      Paragraph("<b>3</b>", style_cell_center),
      Paragraph("<b>4</b>", style_cell_center),
      Paragraph("<b>5</b>", style_cell_center),
      Paragraph("<b>6</b>", style_cell_center),
      Paragraph("<b>7</b>", style_cell_center),
      Paragraph("<b>8</b>", style_cell_center),
      "",
  ])

  pivot_df = pd.pivot_table(
      df_siswa,
      values="nilai",
      index="nama_mapel",
      columns="semester",
      aggfunc="first",
  )

  mapel_list = sorted(df_siswa["nama_mapel"].unique().tolist())
  for idx, mp in enumerate(mapel_list, 1):
    row = [Paragraph(str(idx), style_cell_center), Paragraph(mp, style_cell)]
    for sem in range(1, 9):
      val = ""
      if sem in pivot_df.columns and mp in pivot_df.index:
        v = pivot_df.loc[mp, sem]
        if pd.notna(v):
          val = str(int(np.ceil(v)))
      row.append(Paragraph(val, style_cell_center))

    us_val = ""
    if 8 in pivot_df.columns and mp in pivot_df.index:
      v = pivot_df.loc[mp, 8]
      if pd.notna(v):
        us_val = str(int(np.ceil(v)))
    row.append(Paragraph(us_val, style_cell_center))

    table_data.append(row)

  col_w = [0.6 * cm, 7.8 * cm] + [1.1 * cm] * 8 + [1.6 * cm]
  t_nilai = Table(table_data, colWidths=col_w)
  t_style = [
      ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
      ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
      ("SPAN", (0, 0), (0, 1)),
      ("SPAN", (1, 0), (1, 1)),
      ("SPAN", (2, 0), (9, 0)),
      ("SPAN", (10, 0), (10, 1)),
      ("BACKGROUND", (0, 0), (-1, 1), colors.HexColor("#F0F0F0")),
      ("LEFTPADDING", (0, 0), (-1, -1), 2),
      ("RIGHTPADDING", (0, 0), (-1, -1), 2),
  ]
  t_nilai.setStyle(TableStyle(t_style))
  elements.append(t_nilai)

  doc.build(elements)
  buffer.seek(0)
  return buffer


# Load data utama
try:
  df_raw = load_full_data()
except Exception as e:
  st.error(
      f"❌ Gagal terhubung ke database MySQL. Pastikan XAMPP (Apache & MySQL)"
      f" aktif! Error: {e}"
  )
  st.stop()


# ==============================================================================
# 3. SISTEM AUTENTIKASI / LAMAN LOGIN
# ==============================================================================
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.user_role = None  # 'admin' atau 'siswa'
  st.session_state.user_nis = None
  st.session_state.user_nama = None

if not st.session_state.logged_in:
  st.markdown(
      "<h2 style='text-align: center;'>🎓 Portal Nilai SMKN 26 Jakarta</h2>",
      unsafe_allow_html=True,
  )

  col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
  with col_l2:
    with st.form("form_login"):
      st.subheader("🔑 Silakan Login")
      username_input = st.text_input(
          "Username / NIS:", placeholder="Masukkan NIS Anda"
      ).strip()
      password_input = st.text_input(
          "Password:", type="password", placeholder="Masukkan Password"
      ).strip()
      submit_login = st.form_submit_button("Masuk ke Sistem", use_container_width=True)

      if submit_login:
        # 1. Cek Admin / Guru
        if username_input == "admin" and password_input == "admin123":
          st.session_state.logged_in = True
          st.session_state.user_role = "admin"
          st.session_state.user_nama = "Administrator"
          st.success("Berhasil login sebagai Administrator!")
          st.rerun()

        # 2. Cek Siswa (Username = NIS & Password = 'siswa_smkn26jkt')
        elif password_input == "siswa_smkn26jkt":
          cek_siswa = df_raw[df_raw["nis"] == username_input]
          if not cek_siswa.empty:
            st.session_state.logged_in = True
            st.session_state.user_role = "siswa"
            st.session_state.user_nis = username_input
            st.session_state.user_nama = cek_siswa["nama_siswa"].values[0]
            st.success(
                f"Selamat datang, {st.session_state.user_nama}!"
            )
            st.rerun()
          else:
            st.error("❌ NIS tidak terdaftar dalam database!")
        else:
          st.error("❌ Username/NIS atau Password salah!")

    st.caption(
        "💡 **Petunjuk Akses Siswa:** Use Username = **NIS Anda** & Password ="
        " `siswa_smkn26jkt`"
    )
  st.stop()


# ==============================================================================
# 4. SIDEBAR NAVIGASI BERDASARKAN ROLE
# ==============================================================================
st.sidebar.markdown(
    f"👤 **Login sebagai:** {st.session_state.user_nama} "
    f"({'Siswa' if st.session_state.user_role == 'siswa' else 'Admin/Guru'})"
)

if st.sidebar.button("🚪 Logout", use_container_width=True):
  st.session_state.logged_in = False
  st.session_state.user_role = None
  st.session_state.user_nis = None
  st.session_state.user_nama = None
  st.rerun()

st.sidebar.markdown("---")

# Batasi menu navigasi untuk siswa
if st.session_state.user_role == "siswa":
  menu = st.sidebar.radio("📌 Navigasi:", ["📜 Transkrip / Rapor Saya"])
else:
  menu = st.sidebar.radio(
      "📌 Menu Navigasi:",
      [
          "🏠 Dashboard Utama",
          "📊 Rekap & Analisis Nilai",
          "📜 Transkrip / Rapor Siswa",
          "✏️ Input & Update Nilai",
      ],
  )


# ==============================================================================
# 5. FUNGSI RENDER DETAIL SISWA (TABEL & ALL GRAFIK)
# ==============================================================================
def render_detail_siswa(info, df_siswa):
  m1, m2, m3 = st.columns(3)
  m1.metric("Rata-Rata Akademik", f"{df_siswa['nilai'].mean():.2f}")
  m2.metric("Nilai Tertinggi", f"{df_siswa['nilai'].max():.2f}")
  m3.metric("Nilai Terendah", f"{df_siswa['nilai'].min():.2f}")

  col_t1, col_t2 = st.columns([3, 2])

  with col_t1:
    st.subheader("📋 Matriks Nilai Per Semester")
    siswa_pivot = pd.pivot_table(
        df_siswa,
        values="nilai",
        index="nama_mapel",
        columns="semester",
        aggfunc="first",
    ).fillna("-")

    for col in siswa_pivot.columns:
      siswa_pivot[col] = pd.to_numeric(siswa_pivot[col], errors="coerce")
    siswa_pivot = np.ceil(siswa_pivot)

    st.dataframe(
        siswa_pivot.style.format("{:.0f}", na_rep="-"),
        use_container_width=True,
    )

  with col_t2:
    st.subheader("🕸️ Analisis Radar Kompetensi")
    avg_per_mapel = (
        df_siswa.groupby("nama_mapel")["nilai"].mean().reset_index()
    )

    fig_radar = go.Figure(
        data=go.Scatterpolar(
            r=avg_per_mapel["nilai"],
            theta=avg_per_mapel["nama_mapel"],
            fill="toself",
            name=info["nama_siswa"],
        )
    )
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

  st.markdown("---")

  # --- GRAFIK 1: TREN RATA-RATA KESELURUHAN PER SEMESTER ---
  st.subheader("📈 Tren Rata-Rata Nilai Per Semester")
  sem_avg = df_siswa.groupby("semester")["nilai"].mean().round(2).reset_index()
  sem_avg.columns = ["Semester", "Rata-Rata Nilai"]
  sem_avg["Semester_Label"] = sem_avg["Semester"].apply(lambda x: f"SMT {x}")

  fig_avg = px.line(
      sem_avg,
      x="Semester_Label",
      y="Rata-Rata Nilai",
      text="Rata-Rata Nilai",
      markers=True,
  )
  fig_avg.update_traces(
      textposition="top center", line_color="#0066cc", line_width=3
  )
  st.plotly_chart(fig_avg, use_container_width=True)

  st.markdown("---")

  # --- GRAFIK 2: TREN PER MATA PELAJARAN (FITUR PREDIPILIH SPESIFIK) ---
  st.subheader("🎯 Tren Per Mata Pelajaran")
  available_mapel = sorted(df_siswa["nama_mapel"].unique().tolist())

  selected_mapel_trend = st.selectbox(
      "Pilih Mata Pelajaran:", options=available_mapel, key="select_mapel_trend"
  )

  df_mapel_trend = df_siswa[
      df_siswa["nama_mapel"] == selected_mapel_trend
  ].sort_values("semester")
  df_mapel_trend["Semester_Label"] = df_mapel_trend["semester"].apply(
      lambda x: f"SMT {x}"
  )
  df_mapel_trend["nilai_display"] = df_mapel_trend["nilai"].apply(
      lambda x: int(np.ceil(x)) if pd.notna(x) else np.nan
  )

  fig_mapel_trend = px.line(
      df_mapel_trend,
      x="Semester_Label",
      y="nilai_display",
      text="nilai_display",
      markers=True,
      labels={"Semester_Label": "Semester", "nilai_display": "Nilai"},
  )
  fig_mapel_trend.update_traces(
      textposition="top center", line_color="#28a745", line_width=3
  )
  fig_mapel_trend.update_layout(height=400)
  st.plotly_chart(fig_mapel_trend, use_container_width=True)


# ==============================================================================
# MODUL SISTEM BERDASARKAN HAK AKSES
# ==============================================================================

# ------------------------------------------------------------------------------
# HAK AKSES SISWA: HANYA MELIHAT NILAI MILIK SENDIRI
# ------------------------------------------------------------------------------
if st.session_state.user_role == "siswa":
  st.title("📜 Transkrip Nilai Siswa")

  df_siswa = df_raw[df_raw["nis"] == st.session_state.user_nis].copy()
  df_siswa["nilai"] = pd.to_numeric(df_siswa["nilai"], errors="coerce")

  if not df_siswa.empty:
    info = df_siswa.iloc[0]

    st.markdown("---")
    col_info, col_pdf = st.columns([3, 1])

    with col_info:
      c1, c2, c3 = st.columns(3)
      c1.markdown(f"**NIS / NISN:** {info['nis']} / {info['nisn']}")
      c2.markdown(f"**Nama Lengkap:** {info['nama_siswa']}")
      c3.markdown(f"**Kelas:** {info['nama_kelas']}")

    with col_pdf:
      pdf_bytes = generate_pdf_transkrip(info, df_siswa)
      st.download_button(
          label="🖨️ Cetak Transkrip PDF",
          data=pdf_bytes,
          file_name=f"Transkrip_{info['nis']}_{info['nama_siswa'].replace(' ', '_')}.pdf",
          mime="application/pdf",
          use_container_width=True,
      )

    st.markdown("---")
    render_detail_siswa(info, df_siswa)

  else:
    st.warning("⚠️ Data nilai untuk NIS ini belum tersedia di database.")

# ------------------------------------------------------------------------------
# HAK AKSES ADMIN / GURU (AKSES PENUH)
# ------------------------------------------------------------------------------
elif menu == "🏠 Dashboard Utama":
  st.title("🎓 Dashboard Pengolahan Nilai Siswa")

  col1, col2, col3, col4 = st.columns(4)
  total_siswa = df_raw["nis"].nunique()
  total_kelas = df_raw["nama_kelas"].nunique()
  avg_nilai = df_raw["nilai"].mean() if not df_raw.empty else 0.0
  max_nilai = df_raw["nilai"].max() if not df_raw.empty else 0.0

  col1.metric("Total Siswa", f"{total_siswa} Orang")
  col2.metric("Total Kelas", f"{total_kelas} Kelas")
  col3.metric("Rata-Rata Nilai", f"{avg_nilai:.2f}")
  col4.metric("Nilai Tertinggi", f"{max_nilai:.2f}")

  st.markdown("---")
  col_left, col_right = st.columns(2)

  with col_left:
    st.subheader("📈 Rata-Rata Nilai Per Mata Pelajaran")
    avg_mapel = (
        df_raw.groupby("nama_mapel")["nilai"]
        .mean()
        .reset_index()
        .sort_values(by="nilai", ascending=True)
    )

    fig_mapel = px.bar(
        avg_mapel,
        x="nilai",
        y="nama_mapel",
        orientation="h",
        text_auto=".2f",
        color="nilai",
        color_continuous_scale="Blues",
    )
    fig_mapel.update_layout(showlegend=False, height=500)
    st.plotly_chart(fig_mapel, use_container_width=True)

  with col_right:
    st.subheader("📊 Distribusi Rentang Nilai")
    bins = [0, 60, 75, 85, 100]
    labels = [
        "Kurang (<60)",
        "Cukup (60-74)",
        "Baik (75-85)",
        "Sangat Baik (86-100)",
    ]
    df_raw["kategori"] = pd.cut(df_raw["nilai"], bins=bins, labels=labels)
    kat_counts = df_raw["kategori"].value_counts().reset_index()
    kat_counts.columns = ["Kategori", "Jumlah"]

    fig_pie = px.pie(
        kat_counts,
        names="Kategori",
        values="Jumlah",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_pie.update_layout(height=500)
    st.plotly_chart(fig_pie, use_container_width=True)

elif menu == "📊 Rekap & Analisis Nilai":
  st.title("📊 Tabel Rekap & Analisis Nilai")

  list_kelas = sorted(df_raw["nama_kelas"].dropna().unique().tolist())
  selected_kelas = st.selectbox("Pilih Kelas:", options=list_kelas)

  df_filtered = df_raw[df_raw["nama_kelas"] == selected_kelas]

  pivot_df = pd.pivot_table(
      df_filtered,
      values="nilai",
      index=["nama_kelas", "nis", "nama_siswa"],
      columns="nama_mapel",
      aggfunc="mean",
  ).reset_index()

  non_numeric_cols = ["nama_kelas", "nis", "nama_siswa"]
  mapel_cols = [c for c in pivot_df.columns if c not in non_numeric_cols]
  pivot_df[mapel_cols] = np.ceil(pivot_df[mapel_cols])

  st.dataframe(
      pivot_df.style.highlight_max(axis=0, subset=mapel_cols, color="#d4edda")
      .highlight_min(axis=0, subset=mapel_cols, color="#f8d7da")
      .format("{:.0f}", subset=mapel_cols, na_rep="-"),
      use_container_width=True,
  )

elif menu == "📜 Transkrip / Rapor Siswa":
  st.title("📜 Transkrip & Lembar Rapor Siswa")

  siswa_options = (
      df_raw[["nis", "nama_siswa", "nama_kelas"]]
      .drop_duplicates()
      .sort_values(by="nama_siswa")
  )
  siswa_list = [
      f"{row['nis']} - {row['nama_siswa']} ({row['nama_kelas']})"
      for _, row in siswa_options.iterrows()
  ]

  selected_siswa_str = st.selectbox("Cari / Pilih Siswa:", options=siswa_list)

  if selected_siswa_str:
    nis_selected = selected_siswa_str.split(" - ")[0]
    df_siswa = df_raw[df_raw["nis"] == nis_selected].copy()
    df_siswa["nilai"] = pd.to_numeric(df_siswa["nilai"], errors="coerce")

    if not df_siswa.empty:
      info = df_siswa.iloc[0]

      st.markdown("---")
      col_info, col_pdf = st.columns([3, 1])

      with col_info:
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**NIS / NISN:** {info['nis']} / {info['nisn']}")
        c2.markdown(f"**Nama Lengkap:** {info['nama_siswa']}")
        c3.markdown(f"**Kelas:** {info['nama_kelas']}")

      with col_pdf:
        pdf_bytes = generate_pdf_transkrip(info, df_siswa)
        st.download_button(
            label="🖨️ Cetak Transkrip PDF",
            data=pdf_bytes,
            file_name=f"Transkrip_{info['nis']}_{info['nama_siswa'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

      st.markdown("---")
      render_detail_siswa(info, df_siswa)

elif menu == "✏️ Input & Update Nilai":
  st.title("✏️ Pengelolaan & Editor Nilai Siswa")

  list_siswa_edit = (
      df_raw[["nis", "nama_siswa"]].drop_duplicates().sort_values("nama_siswa")
  )
  siswa_dict = dict(
      zip(list_siswa_edit["nama_siswa"], list_siswa_edit["nis"])
  )

  selected_nama = st.selectbox(
      "Pilih Siswa yang Akan Diupdate:", options=list(siswa_dict.keys())
  )
  selected_nis = siswa_dict[selected_nama]

  col_m1, col_m2 = st.columns(2)
  with col_m1:
    mapel_list = sorted(df_raw["nama_mapel"].unique().tolist())
    mapel_edit = st.selectbox("Pilih Mata Pelajaran:", options=mapel_list)

  with col_m2:
    sem_list = sorted(df_raw["semester"].unique().tolist())
    sem_edit = st.selectbox("Pilih Semester:", options=sem_list)

  with st.form("form_update_nilai"):
    new_nilai = st.number_input(
        "Masukkan Nilai Baru (0-100):",
        min_value=0.0,
        max_value=100.0,
        value=80.0,
        step=0.5,
    )
    submitted = st.form_submit_button("💾 Simpan Perubahan ke MySQL")

    if submitted:
      res_mapel = execute_query(
          "SELECT id_mapel FROM mata_pelajaran WHERE nama_mapel = %s",
          (mapel_edit,),
      )
      if res_mapel:
        id_mapel = res_mapel[0]["id_mapel"]
        execute_commit(
            """
            INSERT INTO nilai (nis, id_mapel, semester, nilai)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nilai = VALUES(nilai)
            """,
            (selected_nis, id_mapel, sem_edit, new_nilai),
        )
        st.success("✅ Nilai berhasil diperbarui!")
        st.cache_data.clear()
        st.rerun()