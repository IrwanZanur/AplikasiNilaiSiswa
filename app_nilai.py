import io
import math
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# ==========================================
# KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Aplikasi Mekanika Teknik Terpadu",
    page_icon="🏗️",
    layout="wide",
)

# ==========================================
# SIDEBAR: NAVIGASI MODUL APLIKASI
# ==========================================
st.sidebar.title("📌 Navigasi Modul")
pilihan_aplikasi = st.sidebar.radio(
    "Pilih Modul Pembelajaran:",
    ["📐 1. Analisis Resultan Gaya", "🏗️ 2. Hitung Reaksi Tumpuan Balok"],
)
st.sidebar.markdown("---")


# ==============================================================================
# MODUL 1: ANALISIS RESULTAN GAYA
# ==============================================================================
if pilihan_aplikasi == "📐 1. Analisis Resultan Gaya":
    st.title("📐 Kalkulator & Visualisator Resultan Gaya Interaktif")
    st.caption("🚀 **Created by : IrwanZanur@MekTek**")
    st.write(
        "Aplikasi untuk menghitung, memvisualisasikan, dan mengunduh laporan "
        "resultan gaya secara grafis maupun analitis."
    )

    # --- SIDEBAR METODE & INPUT ---
    st.sidebar.header("⚙️ Pengaturan Simulasi Gaya")

    metode = st.sidebar.radio(
        "Pilih Metode Visualisasi:",
        ["Jajaran Genjang Bertingkat", "Poligon Gaya (Tip-to-Tail)"],
    )

    skala = st.sidebar.number_input(
        "Skala Gaya (1 cm = ... kg)", min_value=1.0, value=100.0, step=10.0
    )

    default_data = [
        {"Gaya": "P1", "Beban (kg)": 500.0, "Sudut (°)": 90.0},
        {"Gaya": "P2", "Beban (kg)": 400.0, "Sudut (°)": 45.0},
        {"Gaya": "P3", "Beban (kg)": 450.0, "Sudut (°)": 0.0},
        {"Gaya": "P4", "Beban (kg)": 550.0, "Sudut (°)": -40.0},
        {"Gaya": "P5", "Beban (kg)": 350.0, "Sudut (°)": 205.0},
    ]

    st.sidebar.subheader("Tabel Input Gaya")
    df_input = st.sidebar.data_editor(
        pd.DataFrame(default_data), num_rows="dynamic", use_container_width=True
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("👨‍💻 **Created by : IrwanZanur@MekTek**")

    # --- PERHITUNGAN ANALITIS GAYA ---
    if not df_input.empty:
        df_calc = df_input.copy()
        df_calc["Panjang (cm)"] = df_calc["Beban (kg)"] / skala

        rad = np.radians(df_calc["Sudut (°)"])
        df_calc["Fx (kg)"] = df_calc["Beban (kg)"] * np.cos(rad)
        df_calc["Fy (kg)"] = df_calc["Beban (kg)"] * np.sin(rad)
        df_calc["Vx (cm)"] = df_calc["Panjang (cm)"] * np.cos(rad)
        df_calc["Vy (cm)"] = df_calc["Panjang (cm)"] * np.sin(rad)

        Rx_kg = df_calc["Fx (kg)"].sum()
        Ry_kg = df_calc["Fy (kg)"].sum()
        R_total_kg = np.sqrt(Rx_kg**2 + Ry_kg**2)
        R_total_cm = R_total_kg / skala
        Sudut_R_deg = np.degrees(np.arctan2(Ry_kg, Rx_kg))

        # Metrik Ringkasan
        col1, col2, col3 = st.columns(3)
        col1.metric("Resultan Gaya (R)", f"{R_total_kg:.2f} kg")
        col2.metric("Panjang Garis Resultan", f"{R_total_cm:.2f} cm")
        col3.metric("Arah / Sudut Resultan", f"{Sudut_R_deg:.2f}°")

        st.markdown("---")

        # Visualisasi Matplotlib Vektor
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_aspect("equal")

        ax.minorticks_on()
        ax.grid(
            True,
            which="major",
            color="#b0bec5",
            linestyle="-",
            linewidth=0.8,
            alpha=0.7,
        )
        ax.grid(
            True,
            which="minor",
            color="#e0e0e0",
            linestyle=":",
            linewidth=0.5,
            alpha=0.7,
        )

        ax.axhline(0, color="black", linewidth=1.2)
        ax.axvline(0, color="black", linewidth=1.2)

        ax.plot(
            0,
            0,
            marker="o",
            markersize=8,
            markerfacecolor="white",
            markeredgecolor="gray",
            markeredgewidth=2,
            zorder=5,
        )

        vx_list = df_calc["Vx (cm)"].values
        vy_list = df_calc["Vy (cm)"].values
        n_gaya = len(df_calc)

        resultant_colors = ["#1a76d2", "#e53935", "#4caf50", "#00bcd4", "#9c27b0"]
        all_x = [0.0]
        all_y = [0.0]

        if metode == "Jajaran Genjang Bertingkat" and n_gaya >= 2:
            for idx, row in df_calc.iterrows():
                vx, vy = row["Vx (cm)"], row["Vy (cm)"]
                all_x.append(vx)
                all_y.append(vy)
                ax.quiver(
                    0,
                    0,
                    vx,
                    vy,
                    angles="xy",
                    scale_units="xy",
                    scale=1,
                    color="#333333",
                    width=0.005,
                    zorder=4,
                )

                offset_x = 0.3 if vx >= 0 else -0.8
                offset_y = 0.3 if vy >= 0 else -0.5
                ax.text(
                    vx + offset_x,
                    vy + offset_y,
                    f"{row['Gaya']}= {row['Beban (kg)']:.0f} Kg",
                    fontsize=9,
                    fontweight="bold",
                    color="black",
                )

            r_x = vx_list[0] + vx_list[1]
            r_y = vy_list[0] + vy_list[1]
            all_x.append(r_x)
            all_y.append(r_y)

            ax.plot(
                [vx_list[0], r_x],
                [vy_list[0], r_y],
                linestyle="--",
                color="#555555",
                linewidth=1.2,
            )
            ax.plot(
                [vx_list[1], r_x],
                [vy_list[1], r_y],
                linestyle="--",
                color="#555555",
                linewidth=1.2,
            )

            c_r1 = resultant_colors[0]
            ax.quiver(
                0,
                0,
                r_x,
                r_y,
                angles="xy",
                scale_units="xy",
                scale=1,
                color=c_r1,
                width=0.006,
                label="R1",
                zorder=3,
            )
            ax.text(
                r_x * 0.85, r_y * 0.9, "R1", fontsize=10, fontweight="bold", color=c_r1
            )

            prev_rx, prev_ry = r_x, r_y

            for i in range(2, n_gaya):
                px, py = vx_list[i], vy_list[i]
                next_rx = prev_rx + px
                next_ry = prev_ry + py

                all_x.append(next_rx)
                all_y.append(next_ry)

                is_last = i == n_gaya - 1
                r_name = f"R{i}" if not is_last else "RAkhir"
                r_color = (
                    resultant_colors[(i - 1) % len(resultant_colors)]
                    if not is_last
                    else "#00acc1"
                )

                proj_color_1 = (
                    "#e53935" if i == 3 else ("#555555" if i == 2 else "#4caf50")
                )
                proj_color_2 = (
                    "#1a76d2" if i == 2 else ("#555555" if i == 3 else "#1a76d2")
                )

                ax.plot(
                    [prev_rx, next_rx],
                    [prev_ry, next_ry],
                    linestyle="--",
                    color=proj_color_1,
                    linewidth=1.3,
                )
                ax.plot(
                    [px, next_rx],
                    [py, next_ry],
                    linestyle="--",
                    color=proj_color_2,
                    linewidth=1.3,
                )

                if i == 2:
                    ax.plot(
                        px,
                        py,
                        marker="o",
                        markersize=6,
                        markerfacecolor="white",
                        markeredgecolor="gray",
                        markeredgewidth=1.5,
                    )

                ax.quiver(
                    0,
                    0,
                    next_rx,
                    next_ry,
                    angles="xy",
                    scale_units="xy",
                    scale=1,
                    color=r_color,
                    width=0.007 if not is_last else 0.008,
                    label=r_name,
                    zorder=4,
                )
                ax.text(
                    next_rx * 0.88,
                    next_ry * 0.95,
                    f"{r_name}",
                    fontsize=10,
                    fontweight="bold",
                    color=r_color,
                )

                prev_rx, prev_ry = next_rx, next_ry

        else:  # Poligon Gaya
            curr_x, curr_y = 0.0, 0.0
            colors = [
                "#1f77b4",
                "#ff7f0e",
                "#2ca02c",
                "#d62728",
                "#9467bd",
                "#8c564b",
            ]

            for idx, row in df_calc.iterrows():
                vx, vy = row["Vx (cm)"], row["Vy (cm)"]
                next_x = curr_x + vx
                next_y = curr_y + vy

                all_x.extend([curr_x, next_x])
                all_y.extend([curr_y, next_y])

                ax.quiver(
                    curr_x,
                    curr_y,
                    vx,
                    vy,
                    angles="xy",
                    scale_units="xy",
                    scale=1,
                    color=colors[idx % len(colors)],
                    width=0.006,
                    label=f"{row['Gaya']}",
                )
                ax.text(
                    (curr_x + next_x) / 2,
                    (curr_y + next_y) / 2,
                    f" {row['Gaya']}",
                    fontsize=10,
                    fontweight="bold",
                    color=colors[idx % len(colors)],
                )

                curr_x, curr_y = next_x, next_y

            end_x, end_y = curr_x, curr_y
            ax.quiver(
                0,
                0,
                end_x,
                end_y,
                angles="xy",
                scale_units="xy",
                scale=1,
                color="red",
                width=0.008,
                label="R Akhir",
            )

        ax.text(
            0.5,
            -0.12,
            f"Rakhir = {R_total_cm:.2f} cm x {skala:.0f} kg = {R_total_kg:.0f} kg",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="black", lw=1),
        )

        fig.text(
            0.99,
            0.01,
            "Created by : IrwanZanur@MekTek",
            fontsize=9,
            color="gray",
            ha="right",
            va="bottom",
            fontstyle="italic",
            fontweight="bold",
        )

        ax.set_xlabel("Sumbu X (cm)")
        ax.set_ylabel("Sumbu Y (cm)")
        ax.legend(loc="upper left")

        margin = 3.0
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(min(all_y) - margin, max(all_y) + margin)

        col_plot, col_export = st.columns([3, 1])

        with col_plot:
            st.pyplot(fig)

        with col_export:
            st.subheader("📥 Export Hasil")
            buf_png = io.BytesIO()
            fig.savefig(buf_png, format="png", bbox_inches="tight", dpi=300)
            st.download_button(
                "🖼️ Gambar PNG (HD)",
                data=buf_png.getvalue(),
                file_name="diagram_gaya.png",
                mime="image/png",
            )

            buf_pdf = io.BytesIO()
            fig.savefig(buf_pdf, format="pdf", bbox_inches="tight")
            st.download_button(
                "📄 Vektor PDF",
                data=buf_pdf.getvalue(),
                file_name="diagram_gaya.pdf",
                mime="application/pdf",
            )

            csv_data = (
                df_calc[
                    [
                        "Gaya",
                        "Beban (kg)",
                        "Panjang (cm)",
                        "Sudut (°)",
                        "Fx (kg)",
                        "Fy (kg)",
                    ]
                ]
                .to_csv(index=False)
                .encode("utf-8")
            )
            st.download_button(
                "📊 Tabel CSV",
                data=csv_data,
                file_name="analisis_gaya.csv",
                mime="text/csv",
            )

        with st.expander("📊 Lihat Detail Perhitungan Komponen Vektor"):
            st.dataframe(
                df_calc[
                    [
                        "Gaya",
                        "Beban (kg)",
                        "Panjang (cm)",
                        "Sudut (°)",
                        "Fx (kg)",
                        "Fy (kg)",
                    ]
                ],
                use_container_width=True,
            )

        # --- TAHAPAN MODUL PEMBELAJARAN DETAIL ---
        with st.expander(
            "📖 Panduan & Langkah Pengerjaan Belajar Mandiri (Step-by-Step)",
            expanded=True,
        ):
            st.subheader("1. Konversi Gaya ke Skala Panjang Gambar")
            st.write(f"Skala yang diterapkan: **1 cm = {skala:.0f} kg**")

            konversi_text = ""
            for idx, row in df_calc.iterrows():
                gaya_nama = row["Gaya"]
                beban_val = row["Beban (kg)"]
                panjang_val = row["Panjang (cm)"]
                sudut_val = row["Sudut (°)"]
                konversi_text += f"* **{gaya_nama}**: {beban_val:.0f} kg ÷ {skala:.0f} kg/cm = **{panjang_val:.2f} cm** (Sudut {sudut_val}°)\n"
            st.markdown(konversi_text)

            st.subheader("2. Analisis Komponen Gaya (Sumbu X dan Y)")
            st.write(
                "Uraikan setiap gaya ke dalam komponen horizontal ($F_x$) dan "
                "vertikal ($F_y$):"
            )
            st.latex(r"F_x = F \cdot \cos(\theta), \quad F_y = F \cdot \sin(\theta)")

            komponen_text = ""
            for idx, row in df_calc.iterrows():
                gaya_nama = row["Gaya"]
                beban_val = row["Beban (kg)"]
                sudut_val = row["Sudut (°)"]
                fx_val = row["Fx (kg)"]
                fy_val = row["Fy (kg)"]

                komponen_text += f"* **{gaya_nama}** ({beban_val:.0f} kg, {sudut_val}°):\n"
                komponen_text += f"  * $F_x = {beban_val:.0f} \\cdot \\cos({sudut_val}°) = \\mathbf{{{fx_val:.2f}\\text{{ kg}}}}$\n"
                komponen_text += f"  * $F_y = {beban_val:.0f} \\cdot \\sin({sudut_val}°) = \\mathbf{{{fy_val:.2f}\\text{{ kg}}}}$\n"
            st.markdown(komponen_text)

            st.write("**Total Akumulasi Komponen Gaya:**")
            st.markdown(f"* $\\sum F_x = \\mathbf{{{Rx_kg:.2f}\\text{{ kg}}}}$")
            st.markdown(f"* $\\sum F_y = \\mathbf{{{Ry_kg:.2f}\\text{{ kg}}}}$")

            st.subheader("3. Perhitungan Resultan Akhir (Analitis)")
            st.write("Hitung nilai resultan gaya ($R$) dan sudut arahnya ($\theta_R$):")
            st.latex(r"R = \sqrt{(\sum F_x)^2 + (\sum F_y)^2}")
            st.markdown(
                f"* $R = \\sqrt{{({Rx_kg:.2f})^2 + ({Ry_kg:.2f})^2}} = \\mathbf{{{R_total_kg:.2f}\\text{{ kg}}}}$"
            )
            st.markdown(
                f"* Panjang garis $R$ pada kertas = ${R_total_kg:.2f} \\text{{ kg}} \\div {skala:.0f} \\text{{ kg/cm}} = \\mathbf{{{R_total_cm:.2f}\\text{{ cm}}}}$"
            )

            st.latex(r"\theta_R = \arctan\left(\frac{\sum F_y}{\sum F_x}\right)")
            st.markdown(
                f"* Sudut Resultan $\\theta_R = \\mathbf{{{Sudut_R_deg:.2f}^\circ}}$"
            )

            st.subheader(f"4. Langkah Melukis Diagram Grafis ({metode})")
            if metode == "Jajaran Genjang Bertingkat":
                st.markdown("""
            1. **Tentukan Titik Tangkap**: Buat titik awal $(0,0)$ sebagai pusat seluruh gaya.
            2. **Gambarkan Vektor Asli**: Tarik garis gaya $P_1, P_2, \dots, P_n$ sesuai panjang (cm) dan sudutnya dari titik pusat $(0,0)$.
            3. **Langkah 1 (Jajaran Genjang Pertama)**:
               * Tarik garis proyeksi putus-putus sejajar $P_1$ dari ujung $P_2$.
               * Tarik garis proyeksi putus-putus sejajar $P_2$ dari ujung $P_1$.
               * Titik potong kedua garis proyeksi tersebut adalah ujung **$R_1$**. Tarik garis lurus dari $(0,0)$ ke titik potong tersebut.
            4. **Langkah Bertingkat ($R_2, R_3, \dots, R_{\text{akhir}}$)**:
               * Hubungkan $R_1$ dengan $P_3$ menggunakan garis proyeksi sejajar untuk membentuk **$R_2$**.
               * Lanjutkan proses bertingkat ini secara berurutan hingga gaya terakhir ($P_n$).
            5. **Resultan Akhir**: Garis dari $(0,0)$ menuju titik potong jajaran genjang terakhir adalah **$R_{\text{akhir}}$**.
            """)
            else:
                st.markdown("""
            1. **Tentukan Titik Awal**: Buat titik pusat $(0,0)$ sebagai titik mula menggambar.
            2. **Gambarkan Vektor Pertama ($P_1$)**: Tarik gaya $P_1$ dari titik $(0,0)$ sesuai sudut dan panjang skalanya.
            3. **Gambarkan Vektor Berurutan (Tip-to-Tail)**:
               * Dari **ujung/kepala** $P_1$, tarik garis gaya $P_2$ sesuai sudut dan panjangnya.
               * Dari **ujung/kepala** $P_2$, lanjutkan menarik gaya $P_3$, dan seterusnya hingga gaya terakhir ($P_n$).
            4. **Tarik Resultan Akhir ($R_{\text{akhir}}$)**: Hubungkan garis lurus dari titik awal $(0,0)$ langsung ke **ujung gaya terakhir ($P_n$)**. Garis ini merupakan resultan gaya akhir.
            """)


# ==============================================================================
# MODUL 2: HITUNG REAKSI TUMPUAN BALOK (DENGAN NFD, SFD, BMD)
# ==============================================================================
else:
    st.title("🏗️ Aplikasi Perhitungan & Visualisasi Reaksi Tumpuan Balok")
    st.caption("🚀 **Created by : IrwanZanur@MekTek**")
    st.markdown("---")

    # --- INPUT SIDEBAR ---
    st.sidebar.header("1. Parameter Tumpuan (m)")
    st.sidebar.caption("💡 Posisi $x$ diukur dari Ujung Kiri Batang ($x=0\text{ m}$)")
    x_A = st.sidebar.number_input("Posisi Tumpuan A (Sendi)", value=4.0, step=0.5)
    x_B = st.sidebar.number_input("Posisi Tumpuan B (Rol)", value=17.0, step=0.5)

    st.sidebar.header("2. Input Beban Merata (w)")
    num_udl = st.sidebar.number_input(
        "Jumlah Beban Merata", min_value=0, max_value=5, value=1, step=1
    )

    udl_inputs = []
    default_udls = [
        {"w": 1.0, "unit": "ton/m", "x_start": 0.0, "x_end": 9.0},
    ]

    for j in range(int(num_udl)):
        st.sidebar.subheader(f"Beban Merata w{j+1}")
        def_w = default_udls[j]["w"] if j < len(default_udls) else 1.0
        def_unit = default_udls[j]["unit"] if j < len(default_udls) else "ton/m"
        def_xs = default_udls[j]["x_start"] if j < len(default_udls) else 0.0
        def_xe = default_udls[j]["x_end"] if j < len(default_udls) else 5.0

        col_w1, col_w2 = st.sidebar.columns(2)
        with col_w1:
            w_val = st.number_input(
                f"Besar w{j+1}", value=def_w, min_value=0.0, key=f"rt_w_{j}"
            )
            x_w_start = st.number_input(
                f"x Awal (m)", value=def_xs, key=f"rt_xs_{j}"
            )
        with col_w2:
            unit_w = st.selectbox(
                f"Satuan w{j+1}",
                ["ton/m", "kg/m"],
                index=0 if def_unit == "ton/m" else 1,
                key=f"rt_unit_{j}",
            )
            x_w_end = st.number_input(
                f"x Akhir (m)", value=def_xe, key=f"rt_xe_{j}"
            )

        udl_inputs.append({
            "id": f"w{j+1}",
            "w_orig": w_val,
            "unit": unit_w,
            "x_start": x_w_start,
            "x_end": x_w_end,
        })

    st.sidebar.header("3. Input Beban Terpusat (P)")
    num_loads = st.sidebar.number_input(
        "Jumlah Beban Terpusat", min_value=0, max_value=5, value=1, step=1
    )

    default_loads = [
        {"P": 3.0, "x": 13.0, "angle": 90.0, "dir_x": "Kiri"},
    ]

    loads = []
    for i in range(int(num_loads)):
        st.sidebar.subheader(f"Beban Terpusat P{i+1}")
        def_p = default_loads[i]["P"] if i < len(default_loads) else 2.0
        def_x = default_loads[i]["x"] if i < len(default_loads) else 10.0
        def_angle = default_loads[i]["angle"] if i < len(default_loads) else 90.0
        def_dir = default_loads[i]["dir_x"] if i < len(default_loads) else "Kiri"

        col1, col2 = st.sidebar.columns(2)
        with col1:
            P_val = st.number_input(
                f"Besar P{i+1} (ton)", value=def_p, min_value=0.0, key=f"rt_p_{i}"
            )
            angle_val = st.number_input(
                f"Sudut P{i+1} (° dr horisontal)",
                value=def_angle,
                min_value=0.0,
                max_value=90.0,
                key=f"rt_angle_{i}",
            )
        with col2:
            x_val = st.number_input(
                f"Posisi x P{i+1} (m)", value=def_x, key=f"rt_x_{i}"
            )
            dir_x = st.selectbox(
                f"Arah Horisontal P{i+1}",
                ["Kiri", "Kanan"],
                index=0 if def_dir == "Kiri" else 1,
                key=f"rt_dir_{i}",
            )

        loads.append({
            "id": f"P{i+1}",
            "P": P_val,
            "x": x_val,
            "angle": angle_val,
            "dir_x": dir_x,
        })

    st.sidebar.markdown("---")
    st.sidebar.caption("👨‍💻 **Created by : IrwanZanur@MekTek**")

    # --- PERHITUNGAN REAKSI TUMPUAN BALOK ---
    udl_details = []
    sum_Py_udl = 0.0
    sum_MA_udl = 0.0
    sum_MB_udl = 0.0

    for u in udl_inputs:
        w_conv = u["w_orig"] / 1000.0 if u["unit"] == "kg/m" else u["w_orig"]
        if u["x_end"] > u["x_start"] and w_conv > 0:
            L_w = u["x_end"] - u["x_start"]
            Q_equiv = w_conv * L_w
            x_Q = u["x_start"] + (L_w / 2.0)

            dist_A = x_Q - x_A
            dist_B = x_B - x_Q

            sum_Py_udl += Q_equiv
            sum_MA_udl += Q_equiv * dist_A
            sum_MB_udl += Q_equiv * dist_B

            udl_details.append({
                "id": u["id"],
                "w_orig": u["w_orig"],
                "unit": u["unit"],
                "w_conv": w_conv,
                "x_start": u["x_start"],
                "x_end": u["x_end"],
                "L_w": L_w,
                "Q_equiv": Q_equiv,
                "x_Q": x_Q,
                "dist_A": dist_A,
                "dist_B": dist_B,
            })

    load_details = []
    sum_Px = 0.0
    sum_Py_loads = 0.0
    sum_MA_loads = 0.0
    sum_MB_loads = 0.0

    for ld in loads:
        rad = math.radians(ld["angle"])
        # Mengatasi Galat Komputasi Komponen Horizontal untuk Sudut 90 Derajat
        if abs(ld["angle"] - 90.0) < 1e-5:
            Px = 0.0
        else:
            Px = ld["P"] * math.cos(rad)
            
        Py = ld["P"] * math.sin(rad)

        sign_x = -1 if ld["dir_x"] == "Kiri" else 1
        sum_Px += sign_x * Px
        sum_Py_loads += Py

        dist_A = ld["x"] - x_A
        dist_B = x_B - ld["x"]

        sum_MA_loads += Py * dist_A
        sum_MB_loads += Py * dist_B

        load_details.append({
            "id": ld["id"],
            "P": ld["P"],
            "x": ld["x"],
            "angle": ld["angle"],
            "dir_x": ld["dir_x"],
            "Px": Px,
            "Py": Py,
            "sign_x": sign_x,
            "dist_A": dist_A,
            "dist_B": dist_B,
        })

    # Total Gaya & Momen
    sum_Py = sum_Py_udl + sum_Py_loads
    sum_MA = sum_MA_udl + sum_MA_loads
    sum_MB = sum_MB_udl + sum_MB_loads

    L_span = x_B - x_A
    R_AH = -sum_Px if abs(sum_Px) > 1e-5 else 0.0
    R_BV = sum_MA / L_span if L_span != 0 else 0.0
    R_AV = sum_MB / L_span if L_span != 0 else 0.0
    check_Fy = (R_AV + R_BV) - sum_Py

    # --- PERHITUNGAN DIAGRAM GAYA-GAYA DALAM (NFD, SFD, BMD) ---
    all_x_points = [0.0, x_A, x_B]
    all_x_points += [u["x_start"] for u in udl_details] + [
        u["x_end"] for u in udl_details
    ]
    all_x_points += [ld["x"] for ld in load_details]

    min_x = min(all_x_points)
    max_x = max(all_x_points)

    # Diskretisasi Rentang Batang
    num_pts = 1000
    x_vals = np.linspace(min_x, max_x, num_pts)
    N_vals = np.zeros_like(x_vals)
    V_vals = np.zeros_like(x_vals)
    M_vals = np.zeros_like(x_vals)

    for i, x_curr in enumerate(x_vals):
        n = 0.0
        v = 0.0
        m = 0.0

        # Kontribusi Tumpuan A
        if x_curr >= x_A:
            v += R_AV
            m += R_AV * (x_curr - x_A)
            if abs(R_AH) > 1e-5:
                n -= R_AH

        # Kontribusi Tumpuan B
        if x_curr >= x_B:
            v += R_BV
            m += R_BV * (x_curr - x_B)

        # Kontribusi Beban Merata (UDL)
        for u in udl_details:
            xs, xe, w = u["x_start"], u["x_end"], u["w_conv"]
            if x_curr > xs:
                overlap = min(x_curr, xe) - xs
                if overlap > 0:
                    w_force = w * overlap
                    w_center = xs + overlap / 2.0
                    v -= w_force
                    m -= w_force * (x_curr - w_center)

        # Kontribusi Beban Terpusat (P)
        for ld in load_details:
            px_pos = ld["x"]
            if x_curr >= px_pos:
                v -= ld["Py"]
                m -= ld["Py"] * (x_curr - px_pos)
                if abs(ld["Px"]) > 1e-5:
                    if ld["sign_x"] == -1:  # Kiri -> Tarik (+N)
                        n += ld["Px"]
                    elif ld["sign_x"] == 1:  # Kanan -> Tekan (-N)
                        n -= ld["Px"]

        N_vals[i] = n
        V_vals[i] = v
        M_vals[i] = m

    # --- VISUALISASI UTAMA & LAYOUT METRIK ---
    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        st.subheader("🖼️ Diagram Gelagar, Beban, dan Reaksi Tumpuan")

        fig, ax = plt.subplots(figsize=(10, 4.8))

        min_plot_x = min_x - 1.0
        max_plot_x = max_x + 1.0

        # Plot Batang Gelagar
        ax.plot([min_plot_x + 0.5, max_plot_x - 0.5], [0, 0], color="#2c3e50", linewidth=5, zorder=2)

        # Plot Tumpuan A (Sendi)
        tumpuan_A = patches.Polygon(
            [[x_A, 0], [x_A - 0.25, -0.4], [x_A + 0.25, -0.4]],
            closed=True,
            color="#7f8c8d",
            ec="black",
            zorder=3,
        )
        ax.add_patch(tumpuan_A)
        ax.text(x_A, -0.65, "A (Sendi)", fontsize=10, fontweight="bold", ha="center")

        # Plot Tumpuan B (Rol)
        tumpuan_B = patches.Polygon(
            [[x_B, 0], [x_B - 0.25, -0.3], [x_B + 0.25, -0.3]],
            closed=True,
            color="#7f8c8d",
            ec="black",
            zorder=3,
        )
        ax.add_patch(tumpuan_B)
        ax.add_patch(
            patches.Circle(
                (x_B - 0.12, -0.38), 0.08, color="#34495e", ec="black", zorder=3
            )
        )
        ax.add_patch(
            patches.Circle(
                (x_B + 0.12, -0.38), 0.08, color="#34495e", ec="black", zorder=3
            )
        )
        ax.text(x_B, -0.65, "B (Rol)", fontsize=10, fontweight="bold", ha="center")

        # Plot Beban Merata (UDL)
        udl_height = 0.55
        for u in udl_details:
            xs = u["x_start"]
            xe = u["x_end"]
            length_u = u["L_w"]

            rect = patches.Rectangle(
                (xs, 0),
                length_u,
                udl_height,
                linewidth=1,
                edgecolor="#e67e22",
                facecolor="#f39c12",
                alpha=0.25,
                zorder=3,
            )
            ax.add_patch(rect)

            num_arrows = max(3, int(length_u * 2.5))
            x_arrows = np.linspace(xs, xe, num_arrows)
            for xa in x_arrows:
                ax.annotate(
                    "",
                    xy=(xa, 0),
                    xytext=(xa, udl_height),
                    arrowprops=dict(
                        arrowstyle="->", color="#d35400", lw=1.2, mutation_scale=8
                    ),
                    zorder=4,
                )

            ax.text(
                u["x_Q"],
                udl_height + 0.15,
                f"{u['id']} = {u['w_orig']} {u['unit']}",
                color="#d35400",
                fontweight="bold",
                fontsize=9,
                ha="center",
            )

            ax.vlines(
                u["x_Q"],
                ymin=-0.2,
                ymax=udl_height,
                colors="#7f8c8d",
                linestyles="--",
                linewidth=1,
                zorder=1,
            )
            ax.text(
                u["x_Q"],
                udl_height + 0.5,
                f"Q_{u['id']} = {u['Q_equiv']:.2f} t",
                fontsize=8.5,
                color="#2c3e50",
                ha="center",
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", fc="#fef9e7", ec="#f39c12", lw=1),
            )

        # Plot Beban Terpusat (P)
        arrow_len = 1.2
        for ld in load_details:
            x_pos = ld["x"]
            P_val = ld["P"]
            ang = ld["angle"]

            if ang == 90:
                ax.annotate(
                    f"{ld['id']} = {P_val:.1f} t",
                    xy=(x_pos, 0),
                    xytext=(x_pos, arrow_len),
                    arrowprops=dict(
                        facecolor="#e74c3c",
                        edgecolor="#e74c3c",
                        shrink=0.05,
                        width=2.5,
                        headwidth=8,
                    ),
                    ha="center",
                    va="bottom",
                    color="#e74c3c",
                    fontweight="bold",
                    fontsize=10,
                )
            else:
                rad = math.radians(ang)
                dir_mult = 1 if ld["sign_x"] < 0 else -1
                dx = dir_mult * arrow_len * math.cos(rad)
                dy = arrow_len * math.sin(rad)
                ax.annotate(
                    f"{ld['id']} = {P_val:.1f} t\n({ang}°)",
                    xy=(x_pos, 0),
                    xytext=(x_pos + dx, dy),
                    arrowprops=dict(
                        facecolor="#e74c3c",
                        edgecolor="#e74c3c",
                        shrink=0.05,
                        width=2.5,
                        headwidth=8,
                    ),
                    ha="center",
                    va="bottom",
                    color="#e74c3c",
                    fontweight="bold",
                    fontsize=10,
                )

        # Plot Reaksi Vertikal
        ax.annotate(
            f"R_AV\n{R_AV:.3f} t",
            xy=(x_A, 0),
            xytext=(x_A, -1.8),
            arrowprops=dict(
                facecolor="#2980b9",
                edgecolor="#2980b9",
                shrink=0.05,
                width=2,
                headwidth=8,
            ),
            ha="center",
            va="top",
            color="#2980b9",
            fontweight="bold",
        )

        ax.annotate(
            f"R_BV\n{R_BV:.3f} t",
            xy=(x_B, 0),
            xytext=(x_B, -1.8),
            arrowprops=dict(
                facecolor="#2980b9",
                edgecolor="#2980b9",
                shrink=0.05,
                width=2,
                headwidth=8,
            ),
            ha="center",
            va="top",
            color="#2980b9",
            fontweight="bold",
        )

        # Plot Reaksi Horizontal R_AH
        if abs(R_AH) > 0.001:
            ah_dir = 1 if R_AH > 0 else -1
            y_rah = 0.45
            x_start = x_A
            x_end = x_A + 1.8 * ah_dir

            ax.annotate(
                "",
                xy=(x_end, y_rah),
                xytext=(x_start, y_rah),
                arrowprops=dict(
                    facecolor="#8e44ad",
                    edgecolor="#8e44ad",
                    width=3,
                    headwidth=9,
                    shrinkA=0,
                    shrinkB=0,
                ),
            )

            ax.text(
                x_A + 0.9 * ah_dir,
                y_rah + 0.15,
                f"R_AH = {abs(R_AH):.3f} t",
                color="#8e44ad",
                fontweight="bold",
                fontsize=10,
                ha="center",
                va="bottom",
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="#fef9e7",
                    edgecolor="#8e44ad",
                    lw=1.5,
                ),
            )

        ax.set_xlim(min_plot_x - 0.5, max_plot_x + 0.5)
        ax.set_ylim(-2.2, 2.2)
        ax.axis("off")
        st.pyplot(fig)

    with col_right:
        st.subheader("📊 Hasil Perhitungan Reaksi Tumpuan")
        st.metric(
            label="Reaksi Horizontal A (R_AH)",
            value=f"{R_AH:.3f} ton",
            delta="Ke Kanan" if R_AH >= 0 else "Ke Kiri",
        )

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric(
                label="Reaksi Vertikal A (R_AV)",
                value=f"{R_AV:.3f} ton",
                delta="Ke Atas" if R_AV >= 0 else "Ke Bawah",
            )
        with col_r2:
            st.metric(
                label="Reaksi Vertikal B (R_BV)",
                value=f"{R_BV:.3f} ton",
                delta="Ke Atas" if R_BV >= 0 else "Ke Bawah",
            )

        st.markdown("---")
        st.subheader("✅ Kontrol Keseimbangan (ΣFy = 0)")
        st.write(
            f"**Total Reaksi Vertikal ($R_{{AV}} + R_{{BV}}$)**: `{R_AV + R_BV:.3f} ton`"
        )
        st.write(f"**Total Beban Vertikal ($\sum F_{{y,beban}}$)**: `{sum_Py:.3f} ton`")

        if abs(check_Fy) < 0.001:
            st.success(
                "✨ **KONTROL OK!** Struktur berada dalam kondisi seimbang sempurna."
            )
        else:
            st.error(f"❌ **TIDAK SEIMBANG!** Selisih: {check_Fy:.4f}")

    # ==========================================
    # VISUALISASI DIAGRAM GAYA-GAYA DALAM (NFD, SFD, BMD)
    # ==========================================
    st.markdown("---")
    st.subheader("📈 Diagram Gaya-Gaya Dalam (Internal Force Diagrams)")

    fig_diag, (ax_nfd, ax_sfd, ax_bmd) = plt.subplots(3, 1, figsize=(11, 9), sharex=True)

    # 1. DIAGRAM GAYA NORMAL (NFD)
    ax_nfd.plot(x_vals, N_vals, color="#8e44ad", linewidth=2)
    ax_nfd.fill_between(
        x_vals, 0, N_vals, where=(N_vals >= 0), color="#8e44ad", alpha=0.25, label="Tarik (+)"
    )
    ax_nfd.fill_between(
        x_vals, 0, N_vals, where=(N_vals < 0), color="#c0392b", alpha=0.25, label="Tekan (-)"
    )
    ax_nfd.axhline(0, color="black", linewidth=1.2)
    ax_nfd.set_ylabel("N (ton)", fontweight="bold")
    ax_nfd.set_title("Diagram Gaya Normal (NFD) — [Tarik (+) Di Atas / Tekan (-) Di Bawah]", fontsize=11, fontweight="bold")
    ax_nfd.grid(True, linestyle=":", alpha=0.6)
    ax_nfd.legend(loc="upper right", fontsize=8)

    # Mengunci Batas Sumbu Y NFD Jika Tidak Ada Gaya Aksial Nyata (Mencegah Zoom Auto-Scale Mikro)
    if np.max(np.abs(N_vals)) < 1e-5:
        ax_nfd.set_ylim(-1.0, 1.0)

    # 2. DIAGRAM BIDANG LINTANG (SFD)
    ax_sfd.plot(x_vals, V_vals, color="#2980b9", linewidth=2)
    ax_sfd.fill_between(
        x_vals, 0, V_vals, where=(V_vals >= 0), color="#2980b9", alpha=0.3, label="Positif (+)"
    )
    ax_sfd.fill_between(
        x_vals, 0, V_vals, where=(V_vals < 0), color="#e74c3c", alpha=0.3, label="Negatif (-)"
    )
    ax_sfd.axhline(0, color="black", linewidth=1.2)
    ax_sfd.set_ylabel("D / V (ton)", fontweight="bold")
    ax_sfd.set_title("Diagram Bidang Lintang (SFD) — [Positif (+) Di Atas / Negatif (-) Di Bawah]", fontsize=11, fontweight="bold")
    ax_sfd.grid(True, linestyle=":", alpha=0.6)
    ax_sfd.legend(loc="upper right", fontsize=8)

    # 3. DIAGRAM BIDANG MOMEN (BMD)
    ax_bmd.plot(x_vals, M_vals, color="#e67e22", linewidth=2)
    ax_bmd.fill_between(
        x_vals, 0, M_vals, where=(M_vals >= 0), color="#27ae60", alpha=0.3, label="Positif (+)"
    )
    ax_bmd.fill_between(
        x_vals, 0, M_vals, where=(M_vals < 0), color="#e74c3c", alpha=0.3, label="Negatif (-)"
    )
    ax_bmd.axhline(0, color="black", linewidth=1.2)
    ax_bmd.invert_yaxis()  # M(+) Di Bawah
    ax_bmd.set_ylabel("M (ton.m)", fontweight="bold")
    ax_bmd.set_xlabel("Posisi x dari Ujung Kiri Batang (m)", fontweight="bold")
    ax_bmd.set_title("Diagram Bidang Momen (BMD) — [Positif (+) Di Bawah / Negatif (-) Di Atas]", fontsize=11, fontweight="bold")
    ax_bmd.grid(True, linestyle=":", alpha=0.6)
    ax_bmd.legend(loc="upper right", fontsize=8)

    # Menandai Posisi Tumpuan A dan B dengan Garis Vertikal Putus-Putus
    for ax_curr in [ax_nfd, ax_sfd, ax_bmd]:
        ax_curr.axvline(x_A, color="#7f8c8d", linestyle="--", linewidth=1, alpha=0.7)
        ax_curr.axvline(x_B, color="#7f8c8d", linestyle="--", linewidth=1, alpha=0.7)

    plt.tight_layout()
    st.pyplot(fig_diag)

    # Ringkasan Nilai Maksimum Gaya Dalam
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Gaya Normal Maks (N)", f"{np.max(np.abs(N_vals)):.3f} ton")
    col_m2.metric("Gaya Lintang Maks (D/V)", f"{np.max(np.abs(V_vals)):.3f} ton")
    col_m3.metric("Momen Maksimum (M)", f"{np.max(np.abs(M_vals)):.3f} ton.m")

    # --- DETAIL URAIAN PERHITUNGAN (EXPANDER) ---
    st.markdown("---")
    st.subheader("📝 Uraian Langkah Perhitungan Detail")

    with st.expander("Klik untuk melihat penjelasan rinci tiap langkah", expanded=True):
        if udl_details:
            st.markdown("### 1. Ekuivalensi Beban Merata ($w$) Menjadi Beban Terpusat ($Q$)")
            for u in udl_details:
                st.write(f"**Beban Merata {u['id']} ({u['w_orig']} {u['unit']}):**")
                st.latex(
                    f"Q_{{{u['id']}}} = w \\times L_w = {u['w_conv']:.3f} \\text{{ t/m}} \\times ({u['x_end']} - {u['x_start']}) \\text{{ m}} = \\mathbf{{{u['Q_equiv']:.3f} \\text{{ ton}}}}"
                )
                st.latex(
                    f"x_{{Q_{{{u['id']}}}}} = {u['x_start']} + \\frac{{{u['L_w']}}}{{2}} = \\mathbf{{{u['x_Q']:.2f} \\text{{ m}}}} \\quad (\\text{{dari ujung kiri}})"
                )
                st.write(
                    f"* Jarak ke Tumpuan A ($d_A$): ${u['x_Q']:.2f} - {x_A:.2f} = \\mathbf{{{u['dist_A']:.2f}\\text{{ m}}}}$"
                )
                st.write(
                    f"* Jarak ke Tumpuan B ($d_B$): ${x_B:.2f} - {u['x_Q']:.2f} = \\mathbf{{{u['dist_B']:.2f}\\text{{ m}}}}$"
                )

        st.markdown("### 2. Penguraian Komponen Beban Terpusat ($P$)")
        if load_details:
            for ld in load_details:
                p_id = ld["id"]
                p_val = ld["P"]
                p_ang = ld["angle"]
                p_px = ld["Px"]
                p_py = ld["Py"]
                p_dir = ld["dir_x"].lower()

                if p_ang != 90:
                    st.write(f"**Beban {p_id} ({p_val} ton, {p_ang}°):**")
                    st.latex(
                        f"{p_id}_x = {p_val} \\times \\cos({p_ang}^\\circ) = {p_px:.3f} \\text{{ ton}} \\quad (\\text{{Arah {p_dir}}})"
                    )
                    st.latex(
                        f"{p_id}_y = {p_val} \\times \\sin({p_ang}^\\circ) = {p_py:.3f} \\text{{ ton}} \\quad (\\text{{Arah bawah}})"
                    )
                else:
                    st.write(
                        f"**Beban {p_id} ({p_val} ton):** Tegak lurus, maka "
                        f"${p_id}_x = 0$ ton dan ${p_id}_y = {p_py:.3f}$ ton."
                    )
        else:
            st.write("Tidak ada beban terpusat yang diinputkan.")

        st.markdown("### 3. Reaksi Horizontal ($\sum F_x = 0$)")
        st.latex(r"\sum F_x = 0 \implies R_{AH} + \sum P_x = 0")
        st.latex(f"R_{{AH}} = \\mathbf{{{R_AH:.3f} \\text{{ ton}}}}")

        st.markdown("### 4. Reaksi Vertikal B ($\sum M_A = 0$)")
        st.latex(
            r"\sum M_A = 0 \implies (R_{BV} \times L_{AB}) - \sum(Q \times d_{QA}) - \sum(P_y \times d_{PA}) = 0"
        )

        m_terms_A = []
        for u in udl_details:
            m_terms_A.append(f"({u['Q_equiv']:.3f} \\times {u['dist_A']:.2f})")
        for ld in load_details:
            m_terms_A.append(f"({ld['Py']:.3f} \\times {ld['dist_A']:.2f})")

        m_str_A = " + ".join(m_terms_A) if m_terms_A else "0"
        st.latex(f"R_{{BV}} \\times {L_span:.2f} = {m_str_A}")
        st.latex(
            f"R_{{BV}} = \\frac{{{sum_MA:.3f}}}{{{L_span:.2f}}} = \\mathbf{{{R_BV:.3f} \\text{{ ton}}}}"
        )

        st.markdown("### 5. Reaksi Vertikal A ($\sum M_B = 0$)")
        st.latex(
            r"\sum M_B = 0 \implies (R_{AV} \times L_{AB}) - \sum(Q \times d_{QB}) - \sum(P_y \times d_{PB}) = 0"
        )

        m_terms_B = []
        for u in udl_details:
            m_terms_B.append(f"({u['Q_equiv']:.3f} \\times {u['dist_B']:.2f})")
        for ld in load_details:
            m_terms_B.append(f"({ld['Py']:.3f} \\times {ld['dist_B']:.2f})")

        m_str_B = " + ".join(m_terms_B) if m_terms_B else "0"
        st.latex(f"R_{{AV}} \\times {L_span:.2f} = {m_str_B}")
        st.latex(
            f"R_{{AV}} = \\frac{{{sum_MB:.3f}}}{{{L_span:.2f}}} = \\mathbf{{{R_AV:.3f} \\text{{ ton}}}}"
        )

        st.markdown("### 6. Aturan Tanda Penggambaran Diagram Gaya-Gaya Dalam")
        st.markdown("""
        * **Diagram Gaya Normal (NFD)**:
          * **Tarik (+)**: Digambar **DI ATAS** garis netral ($N > 0$).
          * **Tekan (-)**: Digambar **DI BAWAH** garis netral ($N < 0$).
        * **Diagram Bidang Lintang (SFD)**:
          * **Positif (+)**: Digambar **DI ATAS** garis netral ($V > 0$).
          * **Negatif (-)**: Digambar **DI BAWAH** garis netral ($V < 0$).
        * **Diagram Bidang Momen (BMD)**:
          * **Positif (+)**: Digambar **DI BAWAH** garis netral ($M > 0$) — *Melambangkan serat bawah balok mengalami tegangan tarik (sagging).*
          * **Negatif (-)**: Digambar **DI ATAS** garis netral ($M < 0$) — *Melambangkan serat atas balok mengalami tegangan tarik (hogging/overhang).*
        """)
