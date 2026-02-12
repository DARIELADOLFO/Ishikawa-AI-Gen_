import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import matplotlib.patches as patches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ishikawa Analytics Pro", page_icon="📊", layout="wide")

# --- BARRA LATERAL (CONFIGURACIÓN) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Claro.svg/1280px-Claro.svg.png", width=150)
    st.markdown("### 🎨 PERSONALIZACIÓN")
    bg_style = st.selectbox("Estilo de Fondo", ["Cyber Dark", "Deep Ocean", "Soft Gray", "Claro Red"])
    tema_color = st.color_picker("Color de Líneas/Identidad", "#EF3829")
    metodo = st.radio("Método de Entrada", ["Manual", "Subir Excel"])
    problema_input = st.text_area("Problema Principal", "TOP 20 CLIENTE REPETIDO")

# --- CSS DINÁMICO ---
bg_presets = {
    "Cyber Dark": "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
    "Deep Ocean": "linear-gradient(135deg, #000428, #004e92)",
    "Soft Gray": "#f0f2f6",
    "Claro Red": "linear-gradient(135deg, #4d0000, #EF3829)"
}
text_color = "white" if bg_style != "Soft Gray" else "#262730"

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_presets[bg_style]}; color: {text_color}; }}
    .titulo-epico {{ font-family: 'Arial Black', sans-serif; color: {text_color}; font-size: 3rem; text-align: center; margin-bottom: 0px; }}
    .autor {{ text-align: right; font-size: 1.1rem; color: {tema_color}; font-weight: bold; margin-top: -10px; }}
    .stButton>button {{ width: 100%; border-radius: 20px; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="titulo-epico">ISHIKAWA ANALYTICS 4.0</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="autor">Creado por Ing. Dariel A. Peña</p>', unsafe_allow_html=True)

# --- MOTOR GRÁFICO ---
def draw_smart_ishikawa(data_dict, title, color_theme, bg_type):
    num_cats = len(data_dict)
    fig_width = 14 + (num_cats * 0.5)
    fig, ax = plt.subplots(figsize=(fig_width, 10), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(0, 14)
    ax.set_ylim(-6, 6)
    ax.axis('off')

    line_color = "white" if bg_type != "Soft Gray" else "#333333"

    # Espina Dorsal
    ax.annotate('', xy=(11.8, 0), xytext=(0.5, 0), arrowprops=dict(arrowstyle='->', lw=5, color=color_theme))

    # CABEZA (TRIÁNGULO CON TEXTO CENTRALIZADO)
    tri_pts = np.array([[11.8, 2.2], [11.8, -2.2], [13.8, 0]])
    ax.add_patch(plt.Polygon(tri_pts, closed=True, facecolor='#d3d3d3', edgecolor=color_theme, lw=2, zorder=3))
    
    # Auto-ajuste de fuente para el título
    max_chars = max([len(s) for s in title.split('\n')])
    if len(title) > 40 or max_chars > 15: font_size = 7
    elif len(title) > 20: font_size = 9
    else: font_size = 11

    ax.text(12.5, 0, title, fontsize=font_size, fontweight='black', color='black', 
            ha='center', va='center', wrap=True, linespacing=1.2)

    # Distribución de Clasificaciones
    categorias = [c for c in data_dict.keys()]
    num_c = len(categorias)
    up_count = int(np.ceil(num_c / 2))
    x_positions = np.linspace(1.5, 10, up_count)
    
    for i, cat in enumerate(categorias):
        is_top = i < up_count
        curr_x = x_positions[i] if is_top else x_positions[i - up_count] + 1.2
        y_end, x_end = (4.5 if is_top else -4.5), curr_x + 1.5
        
        ax.plot([curr_x, x_end], [0, y_end], color=line_color, lw=3, alpha=0.8)
        pct = data_dict[cat].get('_pct', 0)
        ax.text(x_end, y_end + (0.4 if is_top else -0.7), f"{cat}\n{pct:.1f}%", 
                fontsize=10, fontweight='bold', color='white', ha='center',
                bbox=dict(facecolor=color_theme, edgecolor='white', boxstyle='round,pad=0.5'))

        # Causas en Zig-Zag
        causas_dict = {k: v for k, v in data_dict[cat].items() if k != '_pct'}
        for j, (causa, subcausas) in enumerate(causas_dict.items()):
            r = (j + 1) / (len(causas_dict) + 1)
            cx, cy = curr_x + (x_end - curr_x) * r, 0 + (y_end - 0) * r
            side = 1 if j % 2 == 0 else -1
            
            ax.plot([cx, cx - (1.0 * side)], [cy, cy], color=line_color, lw=1.5, alpha=0.6)
            ax.text(cx - (1.1 * side), cy, causa, fontsize=9, color=line_color, 
                    ha='right' if side == 1 else 'left', va='center', fontweight='semibold')
            
            for k, sub in enumerate(subcausas):
                y_off = (k + 1) * 0.35 * (1 if is_top else -1)
                ax.annotate(sub, xy=(cx - (0.5 * side), cy), xytext=(cx - (0.5 * side), cy - y_off),
                            fontsize=8, color='#00d4ff', style='italic',
                            arrowprops=dict(arrowstyle='->', color='#00d4ff', lw=0.5, alpha=0.7), ha='center')
    return fig

# --- LÓGICA DE DATOS SEGMENTADA ---
data_final = {}

if metodo == "Manual":
    if 'num_categorias' not in st.session_state: st.session_state.num_categorias = 3
    
    col_add, col_rem = st.columns(2)
    with col_add:
        if st.button("➕ Añadir Clasificación"): st.session_state.num_categorias += 1
    with col_rem:
        if st.button("➖ Quitar Clasificación") and st.session_state.num_categorias > 1: st.session_state.num_categorias -= 1

    for i in range(st.session_state.num_categorias):
        with st.expander(f"📁 CLASIFICACIÓN #{i+1}", expanded=True):
            nombre_cat = st.text_input(f"Nombre de Clasificación", f"CATEGORÍA {i+1}", key=f"cat_{i}")
            
            # Gestión de causas por categoría
            key_causas = f"count_causas_{i}"
            if key_causas not in st.session_state: st.session_state[key_causas] = 1
            
            causas_temp = {}
            for j in range(st.session_state[key_causas]):
                c_col1, c_col2 = st.columns([1, 2])
                with c_col1:
                    nombre_causa = st.text_input(f"Causa {j+1}", f"Causa {j+1}", key=f"causa_{i}_{j}")
                with c_col2:
                    subs_raw = st.text_input(f"Sub-Causas (separar por coma)", "", key=f"subs_{i}_{j}")
                
                if nombre_causa:
                    causas_temp[nombre_causa] = [s.strip() for s in subs_raw.split(",") if s.strip()]
            
            if st.button(f"➕ Añadir Causa a {nombre_cat}", key=f"btn_causa_{i}"):
                st.session_state[key_causas] += 1
                st.rerun()
            
            data_final[nombre_cat] = {'_pct': 100/st.session_state.num_categorias, **causas_temp}

else:
    file = st.file_uploader("Sube Excel", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        for cat in df['CLASIFICACION'].unique():
            df_cat = df[df['CLASIFICACION'] == cat]
            data_final[cat] = {'_pct': (len(df_cat)/len(df))*100}
            for causa in df_cat['Causa'].unique():
                data_final[cat][causa] = df_cat[df_cat['Causa'] == causa]['Sub-Causa'].dropna().tolist()

# --- RENDER ---
if data_final:
    st.markdown(f"### 🔍 Vista Previa: {problema_input}")
    fig_ish = draw_smart_ishikawa(data_final, problema_input, tema_color, bg_style)
    st.pyplot(fig_ish, transparent=True)
    
    buf = BytesIO()
    fig_ish.savefig(buf, format="png", dpi=300, transparent=True)
    st.download_button("📥 DESCARGAR ISHIKAWA PRO", buf.getvalue(), "ishikawa_pro.png", "image/png")
