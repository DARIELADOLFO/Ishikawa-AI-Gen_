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

# --- MOTOR GRÁFICO OPTIMIZADO (ESTILO PROFESIONAL) ---
def draw_master_ishikawa(data_dict, title, c_lineas, c_text_causas, c_text_clasif, c_subs):
    num_cats = len(data_dict)
    
    # Cálculo dinámico de altura
    max_items = max([sum([len(causas_dict) for causas_dict in cat_data.values()]) for cat_data in data_dict.values()] or [1])
    fig_height = max(14, 12 + (max_items * 0.3))
    
    fig, ax = plt.subplots(figsize=(22, fig_height), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(-1, 18)
    ax.set_ylim(-12, 12)
    ax.axis('off')

    # 1. ESPINA DORSAL - Línea principal
    spine_start_x = 0
    spine_end_x = 13.5
    ax.plot([spine_start_x, spine_end_x], [0, 0], color=c_lineas, lw=5, zorder=1, solid_capstyle='butt')

    # 2. CABEZA (Flecha/Box) - Estilo profesional
    box_width = 3.8
    box_height = 4.0
    head_x = spine_end_x
    
    # Crear polígono de flecha como en la imagen
    arrow_points = np.array([
        [head_x, box_height/2],
        [head_x + box_width - 1, box_height/2],
        [head_x + box_width, 0],
        [head_x + box_width - 1, -box_height/2],
        [head_x, -box_height/2],
        [head_x, box_height/2]
    ])
    
    arrow_head = patches.Polygon(arrow_points, closed=True, 
                                  ec=c_lineas, fc='#888888', 
                                  lw=2.5, zorder=3)
    ax.add_patch(arrow_head)
    
    ax.text(head_x + box_width/2, 0, title, 
            fontsize=11, fontweight='black', color='white', 
            ha='center', va='center', wrap=True, zorder=4)

    categorias = list(data_dict.keys())
    
    # DISTRIBUCIÓN DE CATEGORÍAS: De la cabeza hacia la cola
    for i, cat in enumerate(categorias):
        is_top = i % 2 == 0
        
        # Las categorías se distribuyen de derecha (cabeza) a izquierda (cola)
        # Primera categoría cerca de la cabeza, última cerca de la cola
        spacing = spine_end_x / (num_cats // 2 + 1)
        
        if i < 2:  # Primeras dos categorías (arriba y abajo) cerca de la cabeza
            x_base = spine_end_x - spacing
        else:
            x_base = spine_end_x - ((i // 2 + 1) * spacing)
        
        # Coordenadas de la espina principal de clasificación
        spine_length = 5.5
        angle = 50  # Ángulo de inclinación en grados
        
        if is_top:
            x_fin = x_base - spine_length * np.cos(np.radians(angle))
            y_fin = spine_length * np.sin(np.radians(angle))
        else:
            x_fin = x_base - spine_length * np.cos(np.radians(angle))
            y_fin = -spine_length * np.sin(np.radians(angle))
        
        # ESPINA PRINCIPAL DE CLASIFICACIÓN
        ax.plot([x_base, x_fin], [0, y_fin], color=c_lineas, lw=3.5, alpha=0.95, zorder=2)
        
        # Etiqueta de Clasificación (en recuadro de color)
        label_offset = 0.8 if is_top else -0.8
        
        # Crear recuadro de color para la clasificación
        bbox_clasif = dict(
            facecolor=c_lineas if i % 4 < 2 else '#6B4C9A',  # Alternar colores
            edgecolor='white', 
            boxstyle='round,pad=0.6', 
            alpha=0.9,
            linewidth=2
        )
        
        ax.text(x_fin, y_fin + label_offset, cat, 
                fontsize=11, fontweight='bold', color=c_text_clasif, 
                ha='center', va='center',
                bbox=bbox_clasif,
                zorder=5)

        # 3. PROCESAMIENTO DE CATEGORÍAS SECUNDARIAS
        cat_secundarias = data_dict[cat]
        num_secundarias = len(cat_secundarias)
        
        for j, (nombre_sec, causas_dict) in enumerate(cat_secundarias.items()):
            # Distribución uniforme a lo largo de la espina
            ratio = (j + 1) / (num_secundarias + 1)
            cx = x_base + (x_fin - x_base) * ratio
            cy = 0 + (y_fin - 0) * ratio
            
            # LÍNEA DE CATEGORÍA SECUNDARIA (perpendicular a la espina)
            sec_length = 3.5
            
            # Calcular perpendicular a la espina principal
            if is_top:
                sec_end_x = cx - sec_length * np.cos(np.radians(angle - 90))
                sec_end_y = cy - sec_length * np.sin(np.radians(angle - 90))
            else:
                sec_end_x = cx - sec_length * np.cos(np.radians(angle + 90))
                sec_end_y = cy + sec_length * np.sin(np.radians(angle + 90))
            
            ax.plot([cx, sec_end_x], [cy, sec_end_y], 
                   color=c_lineas, lw=2.2, alpha=0.85, zorder=2)
            
            # Etiqueta de Categoría Secundaria
            label_shift = 0.3 if is_top else -0.3
            ax.text(sec_end_x, sec_end_y + label_shift, nombre_sec, 
                   fontsize=10, color=c_text_causas, 
                   ha='center', va='center', fontweight='bold',
                   bbox=dict(facecolor='black', alpha=0.4, 
                            boxstyle='round,pad=0.35', edgecolor=c_lineas),
                   zorder=4)
            
            # 4. DISTRIBUCIÓN DE CAUSAS (UNIFORME Y ORGANIZADA)
            causas_items = list(causas_dict.items())
            num_causas = len(causas_items)
            
            # Espaciado vertical para causas
            causa_spacing = 0.6
            start_y = sec_end_y - ((num_causas - 1) * causa_spacing / 2)
            
            for k, (causa_txt, sub_list) in enumerate(causas_items):
                causa_y = start_y + (k * causa_spacing)
                causa_x = sec_end_x - 1.5
                
                # FLECHA HACIA LA CAUSA
                ax.annotate('', 
                           xy=(sec_end_x, sec_end_y), 
                           xytext=(causa_x, causa_y),
                           arrowprops=dict(arrowstyle='->', 
                                         color=c_lineas, 
                                         lw=1, 
                                         alpha=0.7),
                           zorder=3)
                
                # Texto de Causa
                ax.text(causa_x - 0.1, causa_y, causa_txt, 
                       fontsize=8.5, color=c_text_causas, 
                       ha='right', va='center',
                       bbox=dict(facecolor='black', alpha=0.25, 
                                boxstyle='round,pad=0.25'),
                       zorder=4)
                
                # 5. SUB-CAUSAS (en línea debajo de cada causa)
                for m, sub in enumerate(sub_list):
                    sub_y = causa_y - ((m + 1) * 0.3)
                    sub_x = causa_x - 0.5
                    
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
                            
                        subcausas = df_cat[df_cat['Causa'] == causa]['SubCausa'].dropna().tolist()
                        dict_causas[str(causa)] = [str(sc) for sc in subcausas]
                    
                    if dict_causas:
                        dict_categorias[str(categoria)] = dict_causas
                
                if dict_categorias:
                    data_final[str(clasificacion)] = dict_categorias
            
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
