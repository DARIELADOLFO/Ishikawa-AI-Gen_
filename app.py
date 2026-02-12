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

# --- CSS DINÁMICO SEGÚN FONDO ---
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
    .titulo-epico {{
        font-family: 'Arial Black', sans-serif;
        color: {text_color};
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0px;
    }}
    .autor {{ text-align: right; font-size: 1.1rem; color: {tema_color}; font-weight: bold; margin-top: -10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<h1 class="titulo-epico">ISHIKAWA ANALYTICS 4.0</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="autor">Creado por Ing. Dariel A. Peña</p>', unsafe_allow_html=True)

# --- MOTOR GRÁFICO INTELIGENTE ---
def draw_smart_ishikawa(data_dict, title, color_theme, bg_type):
    # Ajustar tamaño de figura según cantidad de datos
    num_cats = len(data_dict)
    fig_width = 14 + (num_cats * 0.5)
    fig, ax = plt.subplots(figsize=(fig_width, 10), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(0, 14)
    ax.set_ylim(-6, 6)
    ax.axis('off')

    line_color = "white" if bg_type != "Soft Gray" else "#333333"

    # 1. Espina Dorsal
    ax.annotate('', xy=(11.8, 0), xytext=(0.5, 0),
                arrowprops=dict(arrowstyle='->', lw=5, color=color_theme))

    # 2. Cabeza Adaptable (Triángulo)
    tri_pts = np.array([[11.8, 2], [11.8, -2], [13.5, 0]])
    ax.add_patch(plt.Polygon(tri_pts, closed=True, facecolor='#d3d3d3', edgecolor=color_theme, lw=2, zorder=3))
    
    # Texto en cabeza con ajuste de tamaño (font-scaling)
    fs = 11 if len(title) < 15 else 9 if len(title) < 25 else 7
    ax.text(12.4, 0, title, fontsize=fs, fontweight='black', color='black', ha='center', va='center', wrap=True)

    # 3. Distribución Inteligente de Clasificaciones
    categorias = [c for c in data_dict.keys() if c != '_total']
    num_c = len(categorias)
    
    # Decidir cuántas van arriba y cuántas abajo (dispersión equilibrada)
    up_count = int(np.ceil(num_c / 2))
    x_positions = np.linspace(1.5, 10, up_count)
    
    for i, cat in enumerate(categorias):
        is_top = i < up_count
        # Reiniciar x si pasamos a la parte de abajo
        curr_x = x_positions[i] if is_top else x_positions[i - up_count] + 1.2
        
        y_end = 4.5 if is_top else -4.5
        x_end = curr_x + 1.5
        
        # Espina de Clasificación
        ax.plot([curr_x, x_end], [0, y_end], color=line_color, lw=3, alpha=0.8)
        
        # Caja de Clasificación
        pct = data_dict[cat].get('_pct', 0)
        ax.text(x_end, y_end + (0.4 if is_top else -0.7), f"{cat}\n{pct:.1f}%", 
                fontsize=10, fontweight='bold', color='white', ha='center',
                bbox=dict(facecolor=color_theme, edgecolor='white', boxstyle='round,pad=0.5'))

        # 4. Distribución Alternada de Causas (Zig-Zag)
        causas = [k for k in data_dict[cat].keys() if k != '_pct']
        for j, causa in enumerate(causas):
            r = (j + 1) / (len(causas) + 1)
            cx, cy = curr_x + (x_end - curr_x) * r, 0 + (y_end - 0) * r
            
            # Alternar lado de la línea (Izquierda / Derecha)
            side = 1 if j % 2 == 0 else -1
            len_c = 1.0
            
            ax.plot([cx, cx - (len_c * side)], [cy, cy], color=line_color, lw=1.5, alpha=0.6)
            ax.text(cx - ((len_c + 0.1) * side), cy, causa, fontsize=9, 
                    color=line_color, ha='right' if side == 1 else 'left', va='center', fontweight='semibold')
            
            # Sub-causas con flecha apuntando a la causa
            subcausas = data_dict[cat][causa]
            for k, sub in enumerate(subcausas):
                y_off = (k + 1) * 0.35 * (1 if is_top else -1)
                ax.annotate(sub, xy=(cx - (0.5 * side), cy), 
                            xytext=(cx - (0.5 * side), cy - y_off),
                            fontsize=8, color='#00d4ff', style='italic',
                            arrowprops=dict(arrowstyle='->', color='#00d4ff', lw=0.5, alpha=0.7),
                            ha='center')

    return fig

# --- LÓGICA DE DATOS ---
data_final = {}
if metodo == "Manual":
    num_cats = st.sidebar.slider("Clasificaciones", 1, 8, 3)
    for i in range(num_cats):
        with st.expander(f"⚙️ Clasificación {i+1}"):
            c1 = st.text_input(f"Nombre", f"CATEGORÍA {i+1}", key=f"n{i}")
            c2 = st.text_area(f"Causas (Formato: Causa1:Sub1,Sub2 | Causa2:Sub3)", key=f"t{i}")
            if c1 and c2:
                data_final[c1] = {'_pct': 100/num_cats}
                for part in c2.split("|"):
                    if ":" in part:
                        causa, subs = part.split(":")
                        data_final[c1][causa.strip()] = [s.strip() for s in subs.split(",")]
                    else:
                        data_final[c1][part.strip()] = []
else:
    file = st.file_uploader("Sube Excel", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        total = len(df)
        for cat in df['CLASIFICACION'].unique():
            df_cat = df[df['CLASIFICACION'] == cat]
            data_final[cat] = {'_pct': (len(df_cat)/total)*100}
            for causa in df_cat['Causa'].unique():
                data_final[cat][causa] = df_cat[df_cat['Causa'] == causa]['Sub-Causa'].dropna().tolist()

# --- RENDER ---
if data_final:
    st.markdown(f"### 🔍 Análisis: {problema_input}")
    fig_ish = draw_smart_ishikawa(data_final, problema_input, tema_color, bg_style)
    st.pyplot(fig_ish, transparent=True)
    
    buf = BytesIO()
    fig_ish.savefig(buf, format="png", dpi=300, transparent=True)
    st.download_button("📥 DESCARGAR ISHIKAWA 4.0", buf.getvalue(), "ishikawa_claro_pro.png", "image/png")
else:
    st.info("💡 Ingresa datos manualmente o sube un Excel para comenzar.")
