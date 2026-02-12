import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import matplotlib.patches as patches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ishikawa Analytics Pro 4.0", page_icon="📊", layout="wide")

# --- BARRA LATERAL (CONTROL TOTAL) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Claro.svg/1280px-Claro.svg.png", width=150)
    st.markdown("### 🎨 PERSONALIZACIÓN")
    bg_style = st.selectbox("Estilo de Fondo", ["Cyber Dark", "Deep Ocean", "Soft Gray", "Claro Red"])
    tema_lineas = st.color_picker("Color de Espinas", "#EF3829")
    color_clasif = st.color_picker("Color de Clasificaciones", "#FFFFFF")
    color_causas = st.color_picker("Color de Causas", "#FFFFFF")
    color_subs = st.color_picker("Color de Sub-Causas", "#00D4FF")
    
    st.markdown("---")
    metodo = st.radio("Método de Entrada", ["Manual", "Subir Excel"])
    problema_input = st.text_area("Problema Principal", "CASOS PROACTIVOS (60)")

# --- ESTILOS CSS ---
bg_presets = {
    "Cyber Dark": "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
    "Deep Ocean": "linear-gradient(135deg, #000428, #004e92)",
    "Soft Gray": "#f0f2f6",
    "Claro Red": "linear-gradient(135deg, #4d0000, #EF3829)"
}
text_base = "white" if bg_style != "Soft Gray" else "#262730"

st.markdown(f"<style>.stApp {{ background: {bg_presets[bg_style]}; color: {text_base}; }} .titulo-epico {{ font-family: 'Arial Black', sans-serif; text-align: center; color: {text_base}; }} .autor {{ text-align: right; color: #EF3829; font-weight: bold; }}</style>", unsafe_allow_html=True)

st.markdown('<h1 class="titulo-epico">ISHIKAWA ANALYTICS 4.0</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="autor">Creado por Ing. Dariel A. Peña</p>', unsafe_allow_html=True)

# --- MOTOR GRÁFICO OPTIMIZADO ---
def draw_master_ishikawa(data_dict, title, c_lineas, c_text_causas, c_text_clasif, c_subs):
    num_cats = len(data_dict)
    # Cálculo dinámico de altura basado en contenido
    max_items = max([sum([len(causas_dict) for causas_dict in cat_data.values()]) for cat_data in data_dict.values()] or [1])
    fig_height = max(12, 10 + (max_items * 0.4))
    
    fig, ax = plt.subplots(figsize=(20, fig_height), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(-2, 17)
    ax.set_ylim(-10, 10)
    ax.axis('off')

    # 1. ESPINA DORSAL - Anclada exactamente al cuadro
    spine_start_x = 0
    spine_end_x = 12.5
    ax.plot([spine_start_x, spine_end_x], [0, 0], color=c_lineas, lw=4.5, zorder=1, solid_capstyle='butt')

    # 2. CABEZA (Box) - Perfectamente alineada
    box_width = 3.2
    box_height = 3.6
    box_head = patches.FancyBboxPatch(
        (spine_end_x, -box_height/2), 
        box_width, 
        box_height, 
        boxstyle="round,pad=0.2", 
        ec=c_lineas, 
        fc="#d3d3d3", 
        lw=2.5, 
        zorder=3
    )
    ax.add_patch(box_head)
    ax.text(spine_end_x + box_width/2, 0, title, 
            fontsize=10, fontweight='black', color='black', 
            ha='center', va='center', wrap=True, zorder=4)

    categorias = list(data_dict.keys())
    
    for i, cat in enumerate(categorias):
        is_top = i % 2 == 0
        
        # Distribución equitativa de clasificaciones a lo largo de la espina
        segment_width = spine_end_x / ((num_cats + 1) / 2)
        x_base = spine_end_x - ((i // 2 + 1) * segment_width)
        
        # Coordenadas de la espina principal de clasificación
        y_fin = 7.5 if is_top else -7.5
        x_fin = x_base - 3.5
        
        # ESPINA PRINCIPAL DE CLASIFICACIÓN
        ax.plot([x_base, x_fin], [0, y_fin], color=c_lineas, lw=3.2, alpha=0.95, zorder=2)
        
        # Etiqueta de Clasificación
        label_y = y_fin + (0.6 if is_top else -0.9)
        ax.text(x_fin, label_y, cat, 
                fontsize=12, fontweight='bold', color=c_text_clasif, 
                ha='center', va='center',
                bbox=dict(facecolor=c_lineas, edgecolor='white', 
                         boxstyle='round,pad=0.5', alpha=0.9),
                zorder=5)

        # 3. PROCESAMIENTO DE CATEGORÍAS SECUNDARIAS (AGRUPADAS)
        cat_secundarias = data_dict[cat]
        num_secundarias = len(cat_secundarias)
        
        for j, (nombre_sec, causas_dict) in enumerate(cat_secundarias.items()):
            # Distribución proporcional a lo largo de la espina de clasificación
            ratio = (j + 1) / (num_secundarias + 1)
            cx = x_base + (x_fin - x_base) * ratio
            cy = 0 + (y_fin - 0) * ratio
            
            # LÍNEA DE CATEGORÍA SECUNDARIA (horizontal)
            len_horizontal = 2.2
            sec_end_x = cx - len_horizontal if is_top else cx - len_horizontal
            
            ax.plot([cx, sec_end_x], [cy, cy], 
                   color=c_lineas, lw=2, alpha=0.85, zorder=2)
            
            # Etiqueta de Categoría Secundaria
            text_x = sec_end_x - 0.15
            ax.text(text_x, cy, nombre_sec, 
                   fontsize=9.5, color=c_text_causas, 
                   ha='right', va='center', fontweight='bold',
                   bbox=dict(facecolor='black', alpha=0.3, 
                            boxstyle='round,pad=0.3', edgecolor=c_lineas),
                   zorder=4)
            
            # 4. DISTRIBUCIÓN INTELIGENTE DE CAUSAS (ALGORITMO ANTI-SOLAPAMIENTO)
            causas_items = list(causas_dict.items())
            num_causas = len(causas_items)
            
            # Espaciado vertical adaptativo
            vertical_spacing = min(0.7, 5.0 / max(num_causas, 1))
            start_offset = -((num_causas - 1) * vertical_spacing) / 2
            
            for k, (causa_txt, sub_list) in enumerate(causas_items):
                # Offset vertical para distribuir las causas
                y_offset = start_offset + (k * vertical_spacing)
                
                # Alternancia en profundidad horizontal para mayor claridad
                x_depth = 1.2 + (0.2 if k % 2 == 0 else 0)
                
                causa_x = sec_end_x - x_depth
                causa_y = cy + y_offset
                
                # LÍNEA DE CAUSA (flecha pequeña)
                ax.annotate('', 
                           xy=(sec_end_x - 0.15, cy), 
                           xytext=(causa_x, causa_y),
                           arrowprops=dict(arrowstyle='->', 
                                         color=c_lineas, 
                                         lw=1.2, 
                                         alpha=0.8),
                           zorder=3)
                
                # Texto de Causa
                ax.text(causa_x - 0.12, causa_y, causa_txt, 
                       fontsize=8.5, color=c_text_causas, 
                       ha='right', va='center',
                       bbox=dict(facecolor='black', alpha=0.2, 
                                boxstyle='round,pad=0.25'),
                       zorder=4)
                
                # 5. SUB-CAUSAS (Distribución en cascada)
                num_subs = len(sub_list)
                sub_spacing = 0.35
                
                for m, sub in enumerate(sub_list):
                    sub_y_offset = (m + 1) * sub_spacing * (1 if is_top else -1)
                    sub_x = causa_x - 0.4
                    sub_y = causa_y + sub_y_offset
                    
                    ax.text(sub_x, sub_y, f"↳ {sub}", 
                           fontsize=7.5, color=c_subs, 
                           style='italic', alpha=0.95, 
                           ha='right', va='center',
                           zorder=4)

    return fig

# --- LÓGICA DE DATOS CON AGRUPACIÓN JERÁRQUICA ---
data_final = {}

if metodo == "Manual":
    if 'm_cats' not in st.session_state: 
        st.session_state.m_cats = 2
    
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("➕ Clasificación"): 
            st.session_state.m_cats += 1
    with c2: 
        if st.button("➖ Clasificación") and st.session_state.m_cats > 1: 
            st.session_state.m_cats -= 1
    
    for i in range(st.session_state.m_cats):
        with st.expander(f"📦 CLASIFICACIÓN #{i+1}", expanded=True):
            n_cat = st.text_input("Nombre", f"Clasificación {i+1}", key=f"nc_{i}")
            k_sec = f"n_sec_{i}"
            if k_sec not in st.session_state: 
                st.session_state[k_sec] = 1
            
            d_sec = {}
            for j in range(st.session_state[k_sec]):
                st.markdown("---")
                s_sec = st.text_input(f"Categoría Secundaria {j+1}", f"Cat {j+1}", key=f"sec_{i}_{j}")
                s_cau = st.text_input(f"Causa", "Causa X", key=f"cau_{i}_{j}")
                s_sub = st.text_input(f"Sub-causas (comas)", "", key=f"sub_{i}_{j}")
                
                if s_sec and s_cau:
                    # AGRUPACIÓN: Si la categoría ya existe, agregar a ella
                    if s_sec not in d_sec: 
                        d_sec[s_sec] = {}
                    d_sec[s_sec][s_cau] = [s.strip() for s in s_sub.split(",") if s.strip()]
            
            if st.button(f"➕ Categoría a {n_cat}", key=f"bsec_{i}"):
                st.session_state[k_sec] += 1
                st.rerun()
            
            if n_cat and d_sec:
                data_final[n_cat] = d_sec

else:  # Subir Excel
    file = st.file_uploader("Sube Excel (Columnas: Clasificación, Categoría, Causa, Sub-Causa)", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        
        # AGRUPACIÓN JERÁRQUICA OPTIMIZADA
        if len(df.columns) >= 4:
            df.columns = ['Clasificacion', 'Categoria', 'Causa', 'SubCausa']
            
            # Eliminar filas vacías
            df = df.dropna(subset=['Clasificacion', 'Categoria', 'Causa'])
            
            for clasificacion in df['Clasificacion'].unique():
                if pd.isna(clasificacion):
                    continue
                    
                df_clasif = df[df['Clasificacion'] == clasificacion]
                dict_categorias = {}
                
                for categoria in df_clasif['Categoria'].unique():
                    if pd.isna(categoria):
                        continue
                        
                    df_cat = df_clasif[df_clasif['Categoria'] == categoria]
                    dict_causas = {}
                    
                    for causa in df_cat['Causa'].unique():
                        if pd.isna(causa):
                            continue
                            
                        # AGRUPACIÓN DE SUB-CAUSAS
                        subcausas = df_cat[df_cat['Causa'] == causa]['SubCausa'].dropna().tolist()
                        dict_causas[str(causa)] = [str(sc) for sc in subcausas]
                    
                    if dict_causas:
                        dict_categorias[str(categoria)] = dict_causas
                
                if dict_categorias:
                    data_final[str(clasificacion)] = dict_categorias
            
            # Mostrar preview de datos procesados
            st.success(f"✅ Datos cargados: {len(data_final)} clasificaciones procesadas")
            with st.expander("🔍 Vista previa de estructura de datos"):
                for clasif, cats in data_final.items():
                    st.write(f"**{clasif}**: {len(cats)} categorías")

# --- RENDERIZADO Y DESCARGA ---
if data_final:
    fig_master = draw_master_ishikawa(
        data_final, 
        problema_input, 
        tema_lineas, 
        color_causas, 
        color_clasif, 
        color_subs
    )
    
    st.pyplot(fig_master, transparent=True)
    
    # Descarga PNG
    buf_png = BytesIO()
    fig_master.savefig(buf_png, format="png", dpi=300, transparent=True, bbox_inches='tight')
    st.download_button("📥 DESCARGAR PNG", buf_png.getvalue(), "ishikawa.png", "image/png")
    
    # Descarga SVG
    buf_svg = BytesIO()
    fig_master.savefig(buf_svg, format="svg", transparent=True, bbox_inches='tight')
    st.download_button("📥 DESCARGAR SVG (Editable)", buf_svg.getvalue(), "ishikawa.svg", "image/svg+xml")
    
else:
    st.info("👆 Configura los datos en la barra lateral para generar el diagrama")
