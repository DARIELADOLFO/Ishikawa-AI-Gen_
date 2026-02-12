import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import matplotlib.patches as patches

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Ishikawa Analytics Pro 6.0",
                   page_icon="📊",
                   layout="wide")

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:

    bg_style = st.selectbox("Estilo",
                            ["Cyber Dark", "Deep Ocean", "Soft Gray"])

    color_lineas = st.color_picker("Color Espinas", "#00D4FF")
    color_clasif = st.color_picker("Color Clasificaciones", "#FFFFFF")
    color_causas = st.color_picker("Color Causas", "#FFFFFF")
    color_subs = st.color_picker("Color Sub-Causas", "#00FFAA")

    problema_input = st.text_area("Problema Principal",
                                  "AVERÍAS RED CORE")

# -------------------------------------------------
# BACKGROUND
# -------------------------------------------------
bg_presets = {
    "Cyber Dark": "linear-gradient(135deg, #141E30, #243B55)",
    "Deep Ocean": "linear-gradient(135deg, #000428, #004e92)",
    "Soft Gray": "#f2f2f2"
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

st.title("ISHIKAWA ANALYTICS PRO")

# -------------------------------------------------
# MOTOR GRÁFICO NUEVO (LAYOUT CORREGIDO)
# -------------------------------------------------
def draw_master_ishikawa(data_dict,
                         title,
                         c_lineas,
                         c_text_clasif,
                         c_text_causas,
                         c_subs):

    total_cats = len(data_dict)
    fig_width = 24
    fig_height = 12

    fig, ax = plt.subplots(figsize=(fig_width, fig_height),
                           facecolor='none')

    ax.axis('off')

    # Ajuste de escala más cerrado (más zoom)
    ax.set_xlim(-2, 22)
    ax.set_ylim(-9, 9)

    # -------------------------------------------------
    # CABEZA
    # -------------------------------------------------
    head_x = 18
    head_width = 3.5

    head = patches.FancyBboxPatch(
        (head_x, -2.5),
        head_width,
        5,
        boxstyle="round,pad=0.5,rounding_size=0.8",
        ec=c_lineas,
        fc="#e6e6e6",
        lw=3
    )
    ax.add_patch(head)

    ax.text(head_x + head_width / 2,
            0,
            title,
            ha='center',
            va='center',
            fontsize=13,
            fontweight='bold',
            color='black')

    # -------------------------------------------------
    # ESPINA DORSAL
    # -------------------------------------------------
    spine_start = -1
    spine_end = head_x

    ax.plot([spine_start, spine_end],
            [0, 0],
            color=c_lineas,
            lw=4)

    # -------------------------------------------------
    # CLASIFICACIONES DESDE CABEZA HACIA COLA
    # -------------------------------------------------
    categorias = list(data_dict.keys())

    if total_cats == 0:
        return fig

    spacing = (spine_end - spine_start) / (total_cats + 1)

    for i, cat in enumerate(categorias):

        # 🔥 primera clasificación nace cerca de la cabeza
        x_base = spine_end - (i + 1) * spacing
        y_base = 0

        is_top = i % 2 == 0
        y_tip = 7 if is_top else -7
        x_tip = x_base - 2.8

        # Línea principal
        ax.plot([x_base, x_tip],
                [y_base, y_tip],
                color=c_lineas,
                lw=3)

        # Caja clasificación
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

        # -------------------------------------------------
        # CATEGORÍAS SECUNDARIAS
        # -------------------------------------------------
        categorias_sec = data_dict[cat]
        total_sec = len(categorias_sec)

        for j, (sec, causas_dict) in enumerate(categorias_sec.items()):

            ratio = (j + 1) / (total_sec + 1)

            cx = x_base + (x_tip - x_base) * ratio
            cy = y_base + (y_tip - y_base) * ratio

            sec_len = 2.3

            ax.plot([cx, cx - sec_len],
                    [cy, cy],
                    color=c_lineas,
                    lw=1.6)

            ax.text(cx - sec_len - 0.2,
                    cy,
                    sec,
                    ha='right',
                    va='center',
                    fontsize=9,
                    fontweight='bold',
                    color=c_text_causas)

            # -------------------------------------------------
            # CAUSAS DISTRIBUCIÓN DINÁMICA
            # -------------------------------------------------
            causas_items = list(causas_dict.items())
            total_causas = len(causas_items)

            if total_causas == 0:
                continue

            spacing_y = 0.85 if total_causas < 12 else 0.6
            block_height = total_causas * spacing_y
            start_offset = -block_height / 2

            for k, (causa_txt, sub_list) in enumerate(causas_items):

                y_offset = start_offset + k * spacing_y
                if not is_top:
                    y_offset *= -1

                px = cx - sec_len - 1.1
                py = cy + y_offset

                ax.annotate('',
                            xy=(cx - 0.2, cy),
                            xytext=(px, py),
                            arrowprops=dict(arrowstyle='->',
                                            color=c_lineas,
                                            lw=0.9))

                ax.text(px - 0.1,
                        py,
                        causa_txt,
                        ha='right',
                        va='center',
                        fontsize=8,
                        color=c_text_causas)

                for m, sub in enumerate(sub_list):

                    sub_y = py - (m + 1) * 0.35 if is_top else py + (m + 1) * 0.35

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
# LECTURA Y AGRUPACIÓN
# -------------------------------------------------
data_final = {}

file = st.file_uploader(
    "Sube Excel con columnas: CLASIFICACION, CATEGORIA, CAUSA, SUB_CAUSA",
    type=["xlsx"]
)

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

    fig = draw_master_ishikawa(
        data_final,
        problema_input,
        color_lineas,
        color_clasif,
        color_causas,
        color_subs
    )

    st.pyplot(fig, transparent=True)

    # PNG
    buf_png = BytesIO()
    fig.savefig(buf_png, format="png", dpi=400, transparent=True)
    st.download_button("📥 Descargar PNG",
                       buf_png.getvalue(),
                       "ishikawa.png",
                       "image/png")

    # SVG
    buf_svg = BytesIO()
    fig.savefig(buf_svg, format="svg", transparent=True)
    st.download_button("📥 Descargar SVG Editable",
                       buf_svg.getvalue(),
                       "ishikawa.svg",
                       "image/svg+xml")
