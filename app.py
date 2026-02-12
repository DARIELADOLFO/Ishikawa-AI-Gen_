import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import matplotlib.patches as patches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ishikawa Analytics Pro 6.0", page_icon="📊", layout="wide")

# --- BARRA LATERAL (CONTROL TOTAL) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Claro.svg/1280px-Claro.svg.png", width=150)
    st.markdown("### 🎨 ESTILO Y COLORES")
    bg_style = st.selectbox("Estilo de Fondo", ["Cyber Dark", "Deep Ocean", "Claro Red", "Soft Gray"])
    tema_lineas = st.color_picker("Color de Espinas", "#EF3829")
    color_clasif = st.color_picker("Color Clasificaciones", "#FFFFFF")
    color_causas = st.color_picker("Color Causas", "#FFFFFF")
    color_subs = st.color_picker("Color Sub-Causas", "#00D4FF")
    
    st.markdown("---")
    problema_input = st.text_area("Problema Principal (Cabeza)", "CASOS PROACTIVOS (60)")

# --- DISEÑO UX/UI (MODO VISTOSO) ---
bg_presets = {
    "Cyber Dark": "radial-gradient(circle, #1a1a2e 0%, #0f0c29 100%)",
    "Deep Ocean": "linear-gradient(135deg, #000428, #004e92)",
    "Claro Red": "linear-gradient(135deg, #4d0000, #EF3829)",
    "Soft Gray": "#f0f2f6"
}
text_base = "white" if bg_style != "Soft Gray" else "#262730"

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_presets[bg_style]}; color: {text_base}; }}
    .titulo-epico {{ font-family: 'Arial Black', sans-serif; text-align: center; font-size: 3.5rem; letter-spacing: -2px; margin-bottom: 0px; }}
    .autor {{ text-align: right; font-size: 1.1rem; color: #EF3829; font-weight: bold; margin-top: -10px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="titulo-epico">ISHIKAWA ANALYTICS 6.0</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="autor">Creado por Ing. Dariel A. Peña</p>', unsafe_allow_html=True)

# --- MOTOR GRÁFICO (DISTRIBUCIÓN INTELIGENTE) ---
def draw_master_ishikawa(data_dict, title, c_lineas, c_text_causas, c_text_clasif, c_subs):
    num_cats = len(data_dict)
    # Altura dinámica para evitar que choque
    fig_height = max(10, 8 + (num_cats * 1.5))
    fig, ax = plt.subplots(figsize=(20, fig_height), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(-1, 16)
    ax.set_ylim(-9, 9)
    ax.axis('off')

    # 1. Espina Dorsal (Anclaje Perfecto)
    ax.plot([0, 12.5], [0, 0], color=c_lineas, lw=5, zorder=1, alpha=0.8)

    # 2. Cabeza Cuadrada Redondeada (Estilo Vistoso)
    box_head = patches.FancyBboxPatch((12.5, -2.2), 3.2, 4.4, boxstyle="round,pad=0.2,rounding_size=0.5", 
                                      ec=c_lineas, fc="#d3d3d3", lw=3, zorder=3)
    ax.add_patch(box_head)
    
    # Auto-ajuste de fuente para el título
    f_size_head = 12 if len(title) < 15 else 9 if len(title) < 25 else 7
    ax.text(14.1, 0, title, fontsize=f_size_head, fontweight='black', color='black', ha='center', va='center', wrap=True)

    # 3. Dibujo de Espinas Orgánicas (Desde cabeza hacia atrás)
    categorias = list(data_dict.keys())
    for i, cat in enumerate(categorias):
        is_top = i % 2 == 0
        x_base = 11.5 - (int(i/2) * 4.2)
        y_fin, x_fin = (7.0 if is_top else -7.0), (x_base - 3.5)
        
        # Espina principal
        ax.plot([x_base, x_fin], [0, y_fin], color=c_lineas, lw=4, alpha=0.9)
        ax.text(x_fin, y_fin + (0.7 if is_top else -1.0), cat, fontsize=13, fontweight='bold', color=c_text_clasif, ha='center',
                bbox=dict(facecolor=c_lineas, edgecolor='white', boxstyle='round,pad=0.5', alpha=0.9))

        # 4. Jerarquía Dinámica con ZigZag
        cats_sec = data_dict[cat]
        for j, (nombre_sec, causas_dict) in enumerate(cats_sec.items()):
            r = (j + 1) / (len(cats_sec) + 1)
            cx, cy = x_base + (x_fin - x_base) * r, 0 + (y_fin - 0) * r
            
            # Alternar lado para evitar superposición (ZigZag)
            side = 1 if j % 2 == 0 else -1
            len_h = 2.2
            
            # Línea de Categoría secundaria
            ax.plot([cx, cx - (len_h * side)], [cy, cy], color=c_lineas, lw=2, alpha=0.7)
            ax.text(cx - ((len_h + 0.2) * side), cy, nombre_sec, fontsize=10, color=c_text_causas, 
                    ha='right' if side == 1 else 'left', va='center', fontweight='black')
            
            # 5. Causas y Sub-causas con distribución vertical
            items_causas = list(causas_dict.items())
            for k, (cau_txt, subs) in enumerate(items_causas):
                # Punto de anclaje
                v_gap = 0.5 * (1 if is_top else -1)
                px, py = cx - (1.1 * side), cy - (k * v_gap)
                
                # Línea de conexión a causa
                ax.plot([cx - (0.3 * side), px], [cy, py], color=c_lineas, lw=0.8, alpha=0.5)
                ax.text(px - (0.2 * side), py, cau_txt, fontsize=9, color=c_text_causas, 
                        ha='right' if side == 1 else 'left', fontweight='semibold')
                
                # Sub-causas (Color independiente)
                for m, sub in enumerate(subs):
                    m_off = (m + 1) * 0.3 * (1 if is_top else -1)
                    ax.text(px - (0.4 * side), py - m_off, f"↳ {sub}", fontsize=8, color=c_subs, 
                            style='italic', alpha=1.0, ha='right' if side == 1 else 'left')
    return fig

# --- LÓGICA DE DATOS (FLEXIBLE E INTELIGENTE) ---
data_final = {}

file = st.file_uploader("📂 Sube tu Excel (Clasificación, Categoría, Causa, Sub-Causa)", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    # Limpieza automática de columnas por posición (inmune a nombres mal escritos)
    if len(df.columns) >= 4:
        df.columns = ["CLASIF", "CAT", "CAU", "SUB"]
        for cl, df_cl in df.groupby("CLASIF"):
            dict_cl = {}
            for cat_s, df_cat in df_cl.groupby("CAT"):
                dict_cau = {}
                for cau, df_cau in df_cat.groupby("CAU"):
                    dict_cau[cau] = df_cau["SUB"].dropna().tolist()
                dict_cl[cat_s] = dict_cau
            data_final[cl] = dict_cl
    else:
        st.error("⚠️ El Excel necesita al menos 4 columnas.")

# --- RENDERIZADO ---
if data_final:
    st.markdown("### 🔍 Análisis de Causa Raíz Visual")
    fig_master = draw_master_ishikawa(data_final, problema_input, tema_lineas, color_causas, color_clasif, color_subs)
    st.pyplot(fig_master, transparent=True)
    
    # Botones de Descarga
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        buf_png = BytesIO()
        fig_master.savefig(buf_png, format="png", dpi=350, transparent=True)
        st.download_button("📥 DESCARGAR PNG (ALTA RES)", buf_png.getvalue(), "ishikawa_pro.png", "image/png")
    with col_d2:
        buf_svg = BytesIO()
        fig_master.savefig(buf_svg, format="svg", transparent=True)
        st.download_button("✏️ DESCARGAR SVG (POWERPOINT)", buf_svg.getvalue(), "ishikawa_editable.svg", "image/svg+xml")
else:
    st.info("💡 Sube un archivo Excel para generar automáticamente tu análisis de espina de pescado.")
