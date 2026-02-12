import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import matplotlib.patches as patches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ishikawa Analytics Pro 4.0", page_icon="📊", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Claro.svg/1280px-Claro.svg.png", width=150)
    st.markdown("### 🎨 PERSONALIZACIÓN")
    bg_style = st.selectbox("Estilo de Fondo", ["Cyber Dark", "Deep Ocean", "Soft Gray", "Claro Red"])
    tema_lineas = st.color_picker("Color de Espinas", "#EF3829")
    color_clasif = st.color_picker("Color de Clasificaciones", "#FFFFFF")
    color_causas = st.color_picker("Color de Texto (Causas)", "#00D4FF")
    
    st.markdown("---")
    metodo = st.radio("Método de Entrada", ["Manual", "Subir Excel"])
    problema_input = st.text_area("Problema Principal", "CASOS PROACTIVOS (60)")

bg_presets = {
    "Cyber Dark": "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
    "Deep Ocean": "linear-gradient(135deg, #000428, #004e92)",
    "Soft Gray": "#f0f2f6",
    "Claro Red": "linear-gradient(135deg, #4d0000, #EF3829)"
}
text_base = "white" if bg_style != "Soft Gray" else "#262730"

st.markdown(f"<style>.stApp {{ background: {bg_presets[bg_style]}; color: {text_base}; }} .titulo-epico {{ font-family: 'Arial Black', sans-serif; color: {text_base}; font-size: 3rem; text-align: center; }} .autor {{ text-align: right; font-size: 1.1rem; color: #EF3829; font-weight: bold; }}</style>", unsafe_allow_html=True)

st.markdown('<h1 class="titulo-epico">ISHIKAWA ANALYTICS 4.0</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="autor">Creado por Ing. Dariel A. Peña</p>', unsafe_allow_html=True)

# --- MOTOR GRÁFICO ---
def draw_master_ishikawa(data_dict, title, c_lineas, c_text_causas, c_text_clasif, bg_type):
    num_cats = len(data_dict)
    # Altura dinámica basada en el volumen de datos para que no choque nada
    fig_height = 10 + (num_cats * 1.8)
    fig, ax = plt.subplots(figsize=(18, fig_height), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(-1, 15)
    ax.set_ylim(-8, 8)
    ax.axis('off')

    # 1. Espina Dorsal (Anclada perfectamente a la cabeza)
    ax.plot([0, 12.5], [0, 0], color=c_lineas, lw=4, zorder=1)

    # 2. Cabeza Cuadrada Redondeada (Posición corregida para que no "vuele")
    box_head = patches.FancyBboxPatch((12.5, -1.8), 2.5, 3.6, boxstyle="round,pad=0.2", ec=c_lineas, fc="#d3d3d3", lw=2, zorder=3)
    ax.add_patch(box_head)
    
    f_size_head = 11 if len(title) < 18 else 8
    ax.text(13.75, 0, title, fontsize=f_size_head, fontweight='black', color='black', ha='center', va='center', wrap=True)

    # 3. Espinas Orgánicas (Desde cabeza hacia atrás)
    categorias = list(data_dict.keys())
    for i, cat in enumerate(categorias):
        is_top = i % 2 == 0
        x_base = 11.5 - (int(i/2) * 4.0)
        y_fin, x_fin = (6.5 if is_top else -6.5), (x_base - 3.0)
        
        ax.plot([x_base, x_fin], [0, y_fin], color=c_lineas, lw=3, alpha=0.9)
        ax.text(x_fin, y_fin + (0.5 if is_top else -0.8), cat, fontsize=12, fontweight='bold', color=c_text_clasif, ha='center', bbox=dict(facecolor=c_lineas, edgecolor='white', boxstyle='round,pad=0.4'))

        # 4. Jerarquía: Categoría -> Causa -> Sub-causa (ZigZag Inteligente)
        cats_sec = {k: v for k, v in data_dict[cat].items() if k != '_pct'}
        for j, (c_sec, causas_list) in enumerate(cats_sec.items()):
            r = (j + 1) / (len(cats_sec) + 1)
            cx, cy = x_base + (x_fin - x_base) * r, 0 + (y_fin - 0) * r
            
            # Alternar lado de la línea (Espejo) para evitar sobreescritura
            side = 1 if j % 2 == 0 else -1
            len_h = 1.8
            
            ax.plot([cx, cx - (len_h * side)], [cy, cy], color=c_lineas, lw=1.5, alpha=0.7)
            ax.text(cx - ((len_h + 0.1) * side), cy, c_sec, fontsize=9, color=c_text_causas, ha='right' if side == 1 else 'left', va='center', fontweight='bold')
            
            # Procesar Causas (Diferenciar por índice para evitar colisiones de nombres iguales)
            items_causas = list(causas_list.items()) if isinstance(causas_list, dict) else [(c, []) for c in causas_list]
            
            for k, (cau_txt, subs) in enumerate(items_causas):
                # Punto de anclaje en la línea secundaria
                px, py = cx - (0.7 * side), cy
                ax.plot([px, px - (0.4 * side)], [py, py - (0.3 if is_top else -0.3)], color=c_lineas, lw=1)
                ax.text(px - (0.5 * side), py - (0.3 if is_top else -0.3), cau_txt, fontsize=8, color=c_text_causas, ha='right' if side == 1 else 'left')
                
                for m, sub in enumerate(subs):
                    ax.text(px - (0.7 * side), py - (0.3 if is_top else -0.3) - ((m+1)*0.28 if is_top else -(m+1)*0.28), f"↳ {sub}", fontsize=7, color='#00d4ff', style='italic', alpha=0.9, ha='right' if side == 1 else 'left')
    return fig

# --- LÓGICA DE DATOS ---
data_final = {}
if metodo == "Manual":
    if 'm_cats' not in st.session_state: st.session_state.m_cats = 2
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("➕ Clasificación"): st.session_state.m_cats += 1
    with c2: 
        if st.button("➖ Clasificación") and st.session_state.m_cats > 1: st.session_state.m_cats -= 1
    for i in range(st.session_state.m_cats):
        with st.expander(f"📦 CLASIFICACIÓN #{i+1}", expanded=True):
            n_cat = st.text_input("Nombre", f"Clasificación {i+1}", key=f"nc_{i}")
            k_sec = f"n_sec_{i}"
            if k_sec not in st.session_state: st.session_state[k_sec] = 1
            d_sec = {}
            for j in range(st.session_state[k_sec]):
                st.markdown("---")
                s_sec = st.text_input(f"Categoría Secundaria {j+1}", f"Cat {j+1}", key=f"sec_{i}_{j}")
                s_cau = st.text_input(f"Causa", "Causa X", key=f"cau_{i}_{j}")
                s_sub = st.text_input(f"Sub-causas (comas)", "", key=f"sub_{i}_{j}")
                if s_sec: d_sec[s_sec] = {s_cau: [s.strip() for s in s_sub.split(",") if s.strip()]}
            if st.button(f"➕ Categoría a {n_cat}", key=f"bsec_{i}"):
                st.session_state[k_sec] += 1
                st.rerun()
            data_final[n_cat] = d_sec
else:
    file = st.file_uploader("Sube Excel", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        if len(df.columns) >= 4:
            for cl in df.iloc[:, 0].unique():
                df_cl = df[df.iloc[:, 0] == cl]
                dict_cl = {}
                for cat_s in df_cl.iloc[:, 1].unique():
                    df_cat = df_cl[df_cl.iloc[:, 1] == cat_s]
                    dict_cau = {}
                    for cau in df_cat.iloc[:, 2].unique():
                        dict_cau[cau] = df_cat[df_cat.iloc[:, 2] == cau].iloc[:, 3].dropna().tolist()
                    dict_cl[cat_s] = dict_cau
                data_final[cl] = dict_cl

# --- RENDERIZADO ---
if data_final:
    fig_master = draw_master_ishikawa(data_final, problema_input, tema_lineas, color_causas, color_clasif, bg_style)
    st.pyplot(fig_master, transparent=True)
    buf = BytesIO(); fig_master.savefig(buf, format="png", dpi=300, transparent=True)
    st.download_button("📥 DESCARGAR PNG", buf.getvalue(), "ishikawa_pro.png", "image/png")
