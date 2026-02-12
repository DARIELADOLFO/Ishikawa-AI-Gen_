import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import matplotlib.patches as patches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ishikawa Analytics Pro 6.0", page_icon="📊", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Claro.svg/1280px-Claro.svg.png", width=150)
    st.markdown("### 🎨 PERSONALIZACIÓN")
    bg_style = st.selectbox("Estilo de Fondo", ["Cyber Dark", "Deep Ocean", "Soft Gray", "Claro Red"])
    tema_lineas = st.color_picker("Color de Espinas", "#EF3829")
    color_clasif = st.color_picker("Color Clasificaciones", "#FFFFFF")
    color_causas = st.color_picker("Color Causas", "#FFFFFF")
    color_subs = st.color_picker("Color Sub-Causas", "#00D4FF")
    
    st.markdown("---")
    problema_input = st.text_area("Problema Principal (Cabeza)", "CASOS PROACTIVOS (60)")

# --- ESTILOS CSS ---
bg_presets = {
    "Cyber Dark": "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
    "Deep Ocean": "linear-gradient(135deg, #000428, #004e92)",
    "Soft Gray": "#f0f2f6",
    "Claro Red": "linear-gradient(135deg, #4d0000, #EF3829)"
}
text_base = "white" if bg_style != "Soft Gray" else "#262730"

st.markdown(f"<style>.stApp {{ background: {bg_presets[bg_style]}; color: {text_base}; }} .titulo-epico {{ font-family: 'Arial Black', sans-serif; text-align: center; color: {text_base}; font-size: 3rem; }} .autor {{ text-align: right; color: #EF3829; font-weight: bold; }}</style>", unsafe_allow_html=True)

st.markdown('<h1 class="titulo-epico">ISHIKAWA ANALYTICS 6.0</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="autor">Creado por Ing. Dariel A. Peña</p>', unsafe_allow_html=True)

# --- MOTOR GRÁFICO (LÓGICA ANTI-SUPERPOSICIÓN) ---
def draw_master_ishikawa(data_dict, title, c_lineas, c_text_causas, c_text_clasif, c_subs):
    num_cats = len(data_dict)
    # Altura dinámica más agresiva para dar espacio
    fig_height = max(12, 10 + (num_cats * 2))
    fig, ax = plt.subplots(figsize=(20, fig_height), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(-2, 18) # Ampliamos X para que la cabeza no se salga
    ax.set_ylim(-10, 10)
    ax.axis('off')

    # 1. Espina Dorsal (Anclaje exacto)
    ax.plot([0, 12.5], [0, 0], color=c_lineas, lw=5, zorder=1)

    # 2. Cabeza (Cuadro redondeado centrado)
    box_head = patches.FancyBboxPatch((12.5, -2.5), 4.0, 5.0, boxstyle="round,pad=0.2,rounding_size=0.5", 
                                      ec=c_lineas, fc="#d3d3d3", lw=3, zorder=3)
    ax.add_patch(box_head)
    ax.text(14.5, 0, title, fontsize=11, fontweight='black', color='black', ha='center', va='center', wrap=True)

    categorias = list(data_dict.keys())
    for i, cat in enumerate(categorias):
        is_top = i % 2 == 0
        # Espaciado horizontal de las espinas principales
        x_base = 11.5 - (int(i/2) * 4.5)
        y_fin, x_fin = (7.5 if is_top else -7.5), (x_base - 3.5)
        
        # Espina Principal
        ax.plot([x_base, x_fin], [0, y_fin], color=c_lineas, lw=4, alpha=0.9)
        ax.text(x_fin, y_fin + (0.8 if is_top else -1.2), cat, fontsize=13, fontweight='bold', color=c_text_clasif, 
                ha='center', bbox=dict(facecolor=c_lineas, edgecolor='white', boxstyle='round,pad=0.5'))

        # 3. Categorías Secundarias (Agrupadas)
        cat_secundarias = data_dict[cat]
        for j, (nombre_sec, causas_dict) in enumerate(cat_secundarias.items()):
            # Distribuimos las categorías secundarias a lo largo de la espina diagonal
            r_sec = (j + 1) / (len(cat_secundarias) + 1)
            cx, cy = x_base + (x_fin - x_base) * r_sec, 0 + (y_fin - 0) * r_sec
            
            # Línea horizontal de categoría
            len_h = 2.5
            ax.plot([cx, cx - len_h], [cy, cy], color=c_lineas, lw=2, alpha=0.8)
            ax.text(cx - (len_h + 0.2), cy, nombre_sec, fontsize=10, color=c_text_causas, ha='right', va='center', fontweight='bold')
            
            # 4. DISTRIBUCIÓN DE CAUSAS (Evita superposición)
            causas_items = list(causas_dict.items())
            num_causas = len(causas_items)
            
            for k, (causa_txt, sub_list) in enumerate(causas_items):
                # Calculamos un desplazamiento vertical (offset) para cada causa dentro de la categoría
                # Esto las separa aunque la categoría sea la misma
                offset_v = (k - (num_causas - 1) / 2) * 0.9 * (1 if is_top else -1)
                
                # Punto de inicio en la línea horizontal
                px_start = cx - 1.2
                py_start = cy
                
                # Punto final del texto de la causa
                px_text = cx - 2.8
                py_text = cy + offset_v
                
                # Línea conector a la causa
                ax.plot([px_start, px_text], [py_start, py_text], color=c_lineas, lw=1, alpha=0.6, linestyle='--')
                ax.text(px_text - 0.1, py_text, causa_txt, fontsize=8, color=c_text_causas, ha='right', va='center')
                
                # 5. Sub-causas (Escalonadas debajo de su causa)
                for m, sub in enumerate(sub_list):
                    m_off = (m + 1) * 0.35 * (1 if is_top else -1)
                    ax.text(px_text - 0.4, py_text - m_off, f"↳ {sub}", fontsize=7, color=c_subs, style='italic', ha='right')

    return fig

# --- LÓGICA DE DATOS ---
data_final = {}
file = st.file_uploader("📂 Sube el Excel (Columnas: Clasificación, Categoría, Causa, Sub-Causa)", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    # Limpieza automática: tomamos las primeras 4 columnas sin importar el nombre exacto
    if len(df.columns) >= 4:
        # Agrupamos jerárquicamente: Clasif -> Cat -> Causa -> Subcausa
        for cl, df_cl in df.groupby(df.columns[0]):
            dict_cl = {}
            for cat_s, df_cat in df_cl.groupby(df.columns[1]):
                dict_cau = {}
                for cau, df_cau in df_cat.groupby(df.columns[2]):
                    dict_cau[cau] = df_cau.iloc[:, 3].dropna().tolist()
                dict_cl[cat_s] = dict_cau
            data_final[cl] = dict_cl

# --- RENDERIZADO ---
if data_final:
    fig_master = draw_master_ishikawa(data_final, problema_input, tema_lineas, color_causas, color_clasif, color_subs)
    st.pyplot(fig_master, transparent=True)
    
    buf = BytesIO(); fig_master.savefig(buf, format="png", dpi=350, transparent=True)
    st.download_button("📥 DESCARGAR PNG", buf.getvalue(), "ishikawa.png", "image/png")
    
    buf_svg = BytesIO(); fig_master.savefig(buf_svg, format="svg", transparent=True)
    st.download_button("✏️ DESCARGAR SVG EDITABLE", buf_svg.getvalue(), "ishikawa_edit.svg", "image/svg+xml")
