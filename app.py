import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import matplotlib.patches as patches

# -------------------------------------------------
# CONFIGURACIÓN GENERAL
# -------------------------------------------------
st.set_page_config(page_title="Ishikawa Analytics Pro 5.0", page_icon="📊", layout="wide")

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown("## 🎨 Personalización")

    bg_style = st.selectbox(
        "Estilo de Fondo",
        ["Cyber Dark", "Deep Ocean", "Soft Gray"]
    )

    color_lineas = st.color_picker("Color Espinas", "#00D4FF")
    color_clasif = st.color_picker("Color Clasificaciones", "#FFFFFF")
    color_causas = st.color_picker("Color Causas", "#FFFFFF")
    color_subs = st.color_picker("Color Sub-Causas", "#00FFAA")

    st.markdown("---")

    metodo = st.radio("Método de Entrada", ["Subir Excel"])
    problema_input = st.text_area("Problema Principal", "AVERÍAS RED CORE")

# -------------------------------------------------
# ESTILOS
# -------------------------------------------------
bg_presets = {
    "Cyber Dark": "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
    "Deep Ocean": "linear-gradient(135deg, #000428, #004e92)",
    "Soft Gray": "#f0f2f6"
}

text_color = "white" if bg_style != "Soft Gray" else "black"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {bg_presets[bg_style]};
        color: {text_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("# ISHIKAWA ANALYTICS PRO")

# -------------------------------------------------
# FUNCIÓN PRINCIPAL (MOTOR GRÁFICO PROFESIONAL)
# -------------------------------------------------
def draw_master_ishikawa(data_dict, title,
                         c_lineas,
                         c_text_clasif,
                         c_text_causas,
                         c_subs):

    fig, ax = plt.subplots(figsize=(22, 12), facecolor='none')
    ax.set_xlim(-2, 20)
    ax.set_ylim(-10, 10)
    ax.axis('off')

    # ===============================
    # ESPINA DORSAL
    # ===============================
    spine_start = 0
    spine_end = 15
    ax.plot([spine_start, spine_end], [0, 0],
            color=c_lineas, lw=4)

    # ===============================
    # CABEZA
    # ===============================
    head_width = 3.5
    head = patches.FancyBboxPatch(
        (spine_end, -2),
        head_width,
        4,
        boxstyle="round,pad=0.4,rounding_size=0.5",
        ec=c_lineas,
        fc="#e6e6e6",
        lw=2.5
    )
    ax.add_patch(head)

    ax.text(spine_end + head_width / 2, 0,
            title,
            ha='center',
            va='center',
            fontsize=12,
            fontweight='bold',
            color='black',
            wrap=True)

    categorias = list(data_dict.keys())
    total_cats = len(categorias)

    if total_cats == 0:
        return fig

    cat_spacing = (spine_end - 2) / total_cats

    # ===============================
    # DIBUJO DE CATEGORÍAS PRINCIPALES
    # ===============================
    for i, cat in enumerate(categorias):

        is_top = i % 2 == 0

        x_base = spine_end - (i + 1) * cat_spacing
        y_base = 0

        y_tip = 7 if is_top else -7
        x_tip = x_base - 2.5

        ax.plot([x_base, x_tip],
                [y_base, y_tip],
                color=c_lineas,
                lw=3)

        ax.text(x_tip,
                y_tip + (0.7 if is_top else -0.7),
                cat,
                ha='center',
                va='center',
                fontsize=12,
                fontweight='bold',
                color=c_text_clasif,
                bbox=dict(facecolor=c_lineas,
                          boxstyle="round,pad=0.4"))

        categorias_sec = data_dict[cat]
        total_sec = len(categorias_sec)

        if total_sec == 0:
            continue

        # ===============================
        # CATEGORÍAS SECUNDARIAS
        # ===============================
        for j, (sec, causas_dict) in enumerate(categorias_sec.items()):

            ratio = (j + 1) / (total_sec + 1)

            cx = x_base + (x_tip - x_base) * ratio
            cy = y_base + (y_tip - y_base) * ratio

            sec_length = 2.2

            ax.plot([cx, cx - sec_length],
                    [cy, cy],
                    color=c_lineas,
                    lw=1.5)

            ax.text(cx - sec_length - 0.2,
                    cy,
                    sec,
                    ha='right',
                    va='center',
                    fontsize=9,
                    fontweight='bold',
                    color=c_text_causas)

            causas_items = list(causas_dict.items())
            total_causas = len(causas_items)

            if total_causas == 0:
                continue

            # ===============================
            # BLOQUE VERTICAL DINÁMICO
            # ===============================
            spacing = 0.9 if total_causas <= 12 else 0.6
            block_height = total_causas * spacing
            start_offset = -block_height / 2

            for k, (causa_txt, sub_list) in enumerate(causas_items):

                y_offset = start_offset + k * spacing
                if not is_top:
                    y_offset *= -1

                px = cx - sec_length - 1.0
                py = cy + y_offset

                ax.annotate('',
                            xy=(cx - 0.2, cy),
                            xytext=(px, py),
                            arrowprops=dict(arrowstyle='->',
                                            color=c_lineas,
                                            lw=0.8))

                ax.text(px - 0.1,
                        py,
                        causa_txt,
                        ha='right',
                        va='center',
                        fontsize=8,
                        color=c_text_causas)

                # SUB-CAUSAS
                for m, sub in enumerate(sub_list):
                    sub_spacing = 0.35
                    sub_y = py - (m + 1) * sub_spacing if is_top else py + (m + 1) * sub_spacing

                    ax.text(px - 0.3,
                            sub_y,
                            f"↳ {sub}",
                            ha='right',
                            va='center',
                            fontsize=7,
                            color=c_subs,
                            style='italic')

    return fig


# -------------------------------------------------
# LECTURA Y AGRUPACIÓN JERÁRQUICA
# -------------------------------------------------
data_final = {}

if metodo == "Subir Excel":

    file = st.file_uploader("Sube Excel con columnas: CLASIFICACION, CATEGORIA, CAUSA, SUB_CAUSA",
                            type=["xlsx"])

    if file:
        df = pd.read_excel(file)

        df.columns = ["CLASIFICACION", "CATEGORIA", "CAUSA", "SUB_CAUSA"]

        for clasificacion, df_cl in df.groupby("CLASIFICACION"):

            dict_cat = {}

            for categoria, df_cat in df_cl.groupby("CATEGORIA"):

                dict_causa = {}

                for causa, df_cau in df_cat.groupby("CAUSA"):
                    subs = df_cau["SUB_CAUSA"].dropna().tolist()
                    dict_causa[causa] = subs

                dict_cat[categoria] = dict_causa

            data_final[clasificacion] = dict_cat


# -------------------------------------------------
# RENDER
# -------------------------------------------------
if data_final:

    fig_master = draw_master_ishikawa(
        data_final,
        problema_input,
        color_lineas,
        color_clasif,
        color_causas,
        color_subs
    )

    st.pyplot(fig_master, transparent=True)

    # PNG
    buf_png = BytesIO()
    fig_master.savefig(buf_png, format="png", dpi=400, transparent=True)
    st.download_button("📥 Descargar PNG",
                       buf_png.getvalue(),
                       "ishikawa.png",
                       "image/png")

    # SVG
    buf_svg = BytesIO()
    fig_master.savefig(buf_svg, format="svg", transparent=True)
    st.download_button("📥 Descargar SVG Editable",
                       buf_svg.getvalue(),
                       "ishikawa.svg",
                       "image/svg+xml")
