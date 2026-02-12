import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import matplotlib.patches as patches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ishikawa Analytics Pro 4.0", page_icon="📊", layout="wide")

# --- BARRA LATERAL (CONTROL TOTAL DE COLORES) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Claro.svg/1280px-Claro.svg.png", width=150)
    st.markdown("### 🎨 PERSONALIZACIÓN DE ESTILO")
    bg_style = st.selectbox("Estilo de Fondo", ["Cyber Dark", "Deep Ocean", "Soft Gray", "Claro Red"])
    tema_lineas = st.color_picker("Color de Espinas/Flechas", "#EF3829")
    color_clasif = st.color_picker("Color de Clasificaciones", "#FFFFFF")
    color_causas = st.color_picker("Color de Causas/Texto", "#00D4FF")
    
    st.markdown("---")
    metodo = st.radio("Método de Entrada", ["Manual", "Subir Excel"])
    problema_input = st.text_area("Problema Principal", "CASOS PROACTIVOS (60)")

# --- CSS DINÁMICO ---
bg_presets = {
    "Cyber Dark": "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
    "Deep Ocean": "linear-gradient(135deg, #000428, #004e92)",
    "Soft Gray": "#f0f2f6",
    "Claro Red": "linear-gradient(135deg, #4d0000, #EF3829)"
}
text_base = "white" if bg_style != "Soft Gray" else "#262730"

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_presets[bg_style]}; color: {text_base}; }}
    .titulo-epico {{ font-family: 'Arial Black', sans-serif; color: {text_base}; font-size: 3rem; text-align: center; margin-bottom: 0px; }}
    .autor {{ text-align: right; font-size: 1.1rem; color: #EF3829; font-weight: bold; margin-top: -10px; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="titulo-epico">ISHIKAWA ANALYTICS 4.0</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="autor">Creado por Ing. Dariel A. Peña</p>', unsafe_allow_html=True)

# --- MOTOR GRÁFICO DE OTRO NIVEL ---
def draw_master_ishikawa(data_dict, title, c_lineas, c_text_causas, c_text_clasif, bg_type):
    # Cálculo dinámico de dimensiones basado en la densidad de datos
    num_cats = len(data_dict)
    fig_height = 10 + (num_cats * 1.2)
    fig, ax = plt.subplots(figsize=(18, fig_height), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(-1, 15)
    ax.set_ylim(-8, 8)
    ax.axis('off')

    # 1. Espina Dorsal (Línea Maestra)
    ax.plot([0, 13], [0, 0], color=c_lineas, lw=4, zorder=1)

    # 2. CABEZA (Cuadrado Redondeado con Auto-ajuste de texto)
    box_head = patches.FancyBboxPatch((12.5, -1.5), 2.5, 3, boxstyle="round,pad=0.2", 
                                      ec=c_lineas, fc="#d3d3d3", lw=2, zorder=3)
    ax.add_patch(box_head)
    
    # Ajustar tamaño de fuente según longitud del título
    f_size_head = 12 if len(title) < 15 else 9 if len(title) < 30 else 7
    ax.text(13.75, 0, title, fontsize=f_size_head, fontweight='black', color='black', 
            ha='center', va='center', wrap=True, linespacing=1.2)

    # 3. Dibujo de Espinas (Nacen desde la cabeza hacia atrás)
    categorias = list(data_dict.keys())
    for i, cat in enumerate(categorias):
        is_top = i % 2 == 0 # Alternar arriba y abajo
        # X se calcula de derecha a izquierda (desde la cabeza)
        x_base = 11.5 - (int(i/2) * 3.5)
        
        y_fin = 6 if is_top else -6
        x_fin = x_base - 2.5 # Inclinación \ para arriba, / para abajo
        
        # Línea de Clasificación Principal
        ax.plot([x_base, x_fin], [0, y_fin], color=c_lineas, lw=3, alpha=0.9)
        
        # Etiqueta de Clasificación
        ax.text(x_fin, y_fin + (0.5 if is_top else -0.8), cat, 
                fontsize=12, fontweight='bold', color=c_text_clasif, ha='center',
                bbox=dict(facecolor=c_lineas, edgecolor='white', boxstyle='round,pad=0.4'))

        # 4. Niveles: Categoría -> Causa -> Sub-causa
        causas_dict = {k: v for k, v in data_dict[cat].items() if k != '_pct'}
        for j, (cat_secundaria, causas_list) in enumerate(causas_dict.items()):
            # Posicionamiento en la espina principal
            r = (j + 1) / (len(causas_dict) + 1)
            cx, cy = x_base + (x_fin - x_base) * r, 0 + (y_fin - 0) * r
            
            # Línea de Categoría Secundaria (horizontal)
            len_h = 1.5
            ax.plot([cx, cx - len_h], [cy, cy], color=c_lineas, lw=1.5, alpha=0.7)
            ax.text(cx - (len_h + 0.1), cy, cat_secundaria, fontsize=9, color=c_text_causas, 
                    ha='right', va='center', fontweight='bold')
            
            # Dibujar Causas y Sub-causas conectadas
            for k, (causa_txt, subs) in enumerate(causas_list.items()):
                y_off = (k + 1) * 0.4 * (1 if is_top else -1)
                # Punto de conexión en la línea horizontal
                px, py = cx - 0.7, cy
                
                # Línea de Causa (diagonal pequeña)
                ax.plot([px, px - 0.5], [py, py - (0.3 if is_top else -0.3)], color=c_lineas, lw=0.8)
                ax.text(px - 0.6, py - (0.3 if is_top else -0.3), causa_txt, 
                        fontsize=8, color=c_text_causas, ha='right')
                
                # Sub-causas (texto simple debajo)
                for m, sub in enumerate(subs):
                    ax.text(px - 0.8, py - (0.3 if is_top else -0.3) - ((m+1)*0.25 if is_top else -(m+1)*0.25),
                            f"↳ {sub}", fontsize=7, color='#00d4ff', style='italic', alpha=0.8)
    return fig

# --- LÓGICA DE DATOS SEGMENTADA ---
data_final = {}

if metodo == "Manual":
    if 'm_cats' not in st.session_state: st.session_state.m_cats = 2
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Clasificación"): st.session_state.m_cats += 1
    with col2:
        if st.button("➖ Clasificación") and st.session_state.m_cats > 1: st.session_state.m_cats -= 1

    for i in range(st.session_state.m_cats):
        with st.expander(f"📦 CLASIFICACIÓN #{i+1}", expanded=True):
            n_cat = st.text_input("Nombre (ej. Mano de obra)", f"Clasificación {i+1}", key=f"nc_{i}")
            
            # Categorías Secundarias (ej. Accionar Técnico)
            k_sec = f"n_sec_{i}"
            if k_sec not in st.session_state: st.session_state[k_sec] = 1
            
            dict_secundario = {}
            for j in range(st.session_state[k_sec]):
                st.markdown(f"---")
                c_sec = st.text_input(f"Categoría Secundaria {j+1}", f"Cat {j+1}", key=f"sec_{i}_{j}")
                c_causa = st.text_input(f"Causa para {c_sec}", "Causa X", key=f"cau_{i}_{j}")
                c_subs = st.text_input(f"Sub-causas (separadas por coma)", "", key=f"sub_{i}_{j}")
                
                if c_sec:
                    dict_secundario[c_sec] = {c_causa: [s.strip() for s in c_subs.split(",") if s.strip()]}
            
            if st.button(f"➕ Añadir Categoría a {n_cat}", key=f"bsec_{i}"):
                st.session_state[k_sec] += 1
                st.rerun()
            data_final[n_cat] = dict_secundario

else:
    file = st.file_uploader("Sube Excel", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        # El Excel debe tener: CLASIFICACION, CATEGORIA, CAUSA, SUB_CAUSA
        for cl in df['CLASIFICACION'].unique():
            df_cl = df[df['CLASIFICACION'] == cl]
            dict_cl = {}
            for cat_s in df_cl['CATEGORIA'].unique():
                df_cat = df_cl[df_cl['CATEGORIA'] == cat_s]
                dict_cau = {}
                for cau in df_cat['CAUSA'].unique():
                    dict_cau[cau] = df_cat[df_cat['CAUSA'] == cau]['SUB_CAUSA'].dropna().tolist()
                dict_cl[cat_s] = dict_cau
            data_final[cl] = dict_cl

# --- RENDERIZADO FINAL ---
if data_final:
    st.markdown(f"### 📈 Visualización Avanzada: {problema_input}")
    fig_master = draw_master_ishikawa(data_final, problema_input, tema_lineas, color_causas, color_clasif, bg_style)
    st.pyplot(fig_master, transparent=True)
    
    # Descargas
    b_png = BytesIO()
    fig_master.savefig(b_png, format="png", dpi=300, transparent=True)
    st.download_button("📥 DESCARGAR PNG", b_png.getvalue(), "ishikawa_pro.png", "image/png")
    
    b_svg = BytesIO()
    fig_master.savefig(b_svg, format="svg", transparent=True)
    st.download_button("✏️ DESCARGAR SVG (EDITABLE)", b_svg.getvalue(), "ishikawa_edit.svg", "image/svg+xml")
