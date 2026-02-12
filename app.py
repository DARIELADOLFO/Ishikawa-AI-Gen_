import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Ishikawa AI Gen - Vision Metrics",
    page_icon="📊",
    layout="wide"
)

# --- DISEÑO UX/UI EVOLUCIONADO (CSS ANIMADO) ---
st.markdown("""
    <style>
    /* Fondo Animado de Partículas */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #0f0c29 100%);
        background-attachment: fixed;
    }
    
    /* Animación de fondo sutil */
    @keyframes move {
        from { background-position: 0 0; }
        to { background-position: 100% 100%; }
    }

    /* Efecto Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(15px);
        border-right: 2px solid #EF3829;
    }

    /* Títulos Impactantes */
    .titulo-epico {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(90deg, #EF3829, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        letter-spacing: -1px;
    }
    
    .autor {
        text-align: right;
        font-size: 1rem;
        color: #ffffff;
        opacity: 0.8;
        margin-top: -15px;
        font-weight: 300;
    }

    /* Estilo de Inputs */
    .stTextInput > div > div > input, .stTextArea > div > textarea {
        background-color: rgba(255,255,255,0.05) !important;
        color: white !important;
        border: 1px solid #EF3829 !important;
    }

    /* Botón Pro */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #EF3829 0%, #7d1109 100%);
        color: white;
        border: none;
        padding: 12px;
        border-radius: 5px;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Logo_Claro.svg/1200px-Logo_Claro.svg.png", width=130)

with col_tit:
    st.markdown('<h1 class="titulo-epico">ISHIKAWA ANALYTICS 4.0</h1>', unsafe_allow_html=True)
    st.markdown('<p class="autor">Powered by Vision Metrics | Creado por <b>Dariel A. Peña</b></p>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- MOTOR DE DIBUJO ---
def draw_ishikawa(data_dict, title, color_theme):
    fig, ax = plt.subplots(figsize=(16, 10), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(0, 13)
    ax.set_ylim(-6, 6)
    ax.axis('off')

    # Espina dorsal
    ax.annotate('', xy=(11.5, 0), xytext=(0.5, 0),
                arrowprops=dict(arrowstyle='->', lw=6, color=color_theme, mutation_scale=20))

    # CABEZA DEL PESCADO (TRIÁNGULO ESTILO IMAGEN)
    triangle_pts = np.array([[11.5, 2], [11.5, -2], [13, 0]])
    polygon = plt.Polygon(triangle_pts, closed=True, facecolor='#d3d3d3', edgecolor=color_theme, lw=2)
    ax.add_patch(polygon)
    
    # Texto dentro de la cabeza
    ax.text(12, 0, title, fontsize=11, fontweight='black', color='black',
            ha='center', va='center', wrap=True)

    categorias = list(data_dict.keys())
    x_positions = [2, 5.5, 9] 

    for i, cat in enumerate(categorias):
        is_top = i < 3
        idx = i if is_top else i - 3
        if idx >= len(x_positions): break
        
        x_i = x_positions[idx]
        x_f = x_i + 1.5
        y_f = 4.5 if is_top else -4.5
        
        # Clasificación
        ax.plot([x_i, x_f], [0, y_f], color='white', lw=3, alpha=0.9)
        
        # Etiqueta de Clasificación con %
        pct = data_dict[cat].get('_pct', 0)
        label_cat = f"{cat} | {pct:.1f}%"
        ax.text(x_f, y_f + (0.5 if is_top else -0.8), label_cat, 
                fontsize=11, fontweight='bold', color='white', ha='center',
                bbox=dict(facecolor=color_theme, edgecolor='white', boxstyle='square,pad=0.5'))

        # Causas
        causas = [k for k in data_dict[cat].keys() if k != '_pct']
        for j, causa in enumerate(causas):
            r = (j + 1) / (len(causas) + 1)
            cx, cy = x_i + (x_f - x_i) * r, y_f * r
            
            ax.plot([cx, cx - 1.2], [cy, cy], color='white', lw=1.5, alpha=0.6)
            ax.text(cx - 1.3, cy, causa, fontsize=9, color='white', ha='right', va='center')
            
            # Sub-causas
            subcausas = data_dict[cat][causa]
            for k, sub in enumerate(subcausas):
                offset = (k + 1) * 0.35
                ax.text(cx - 0.6, cy - offset if is_top else cy + offset, 
                        f"→ {sub}", fontsize=8, ha='left', color='#00d4ff', alpha=0.9)

    return fig

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### 🛠️ PANEL DE CONFIGURACIÓN")
    tema_color = st.color_picker("Color de Identidad", "#EF3829")
    metodo = st.radio("Método de Datos", ["Manual", "Subir Excel"])
    problema_input = st.text_area("Problema (Cabeza)", "TOP 20 CLIENTE REPETIDO")

data_final = {}

# --- LÓGICA MANUAL (FORMULARIO) ---
if metodo == "Manual":
    st.sidebar.markdown("---")
    num_cats = st.sidebar.slider("¿Cuántas Clasificaciones?", 1, 6, 3)
    
    manual_data = []
    for i in range(num_cats):
        with st.expander(f"Clasificación {i+1}"):
            c1 = st.text_input(f"Nombre de Clasificación {i+1}", f"CATEGORÍA {i+1}")
            c2 = st.text_area(f"Causas y Sub-causas para {c1} (Formato: Causa:Subcausa1,Subcausa2)", "Falla:Hardware,Soft")
            manual_data.append({"cat": c1, "raw": c2})

    if st.button("GENERAR DESDE MANUAL"):
        total_items = len(manual_data)
        for item in manual_data:
            cat_name = item['cat']
            data_final[cat_name] = {'_pct': 100 / total_items}
            lines = item['raw'].split('\n')
            for line in lines:
                if ":" in line:
                    causa, subs = line.split(":")
                    data_final[cat_name][causa] = subs.split(",")
                else:
                    data_final[cat_name][line] = []

# --- LÓGICA EXCEL ---
else:
    file = st.file_uploader("Sube el reporte (.xlsx)", type=["xlsx"])
    if file:
        df = pd.read_excel(file, sheet_name=0)
        total = len(df)
        for cat in df['CLASIFICACION'].unique():
            df_cat = df[df['CLASIFICACION'] == cat]
            data_final[cat] = {'_pct': (len(df_cat)/total)*100}
            for causa in df_cat['Causa'].unique():
                data_final[cat][causa] = df_cat[df_cat['Causa'] == causa]['Sub-Causa'].dropna().tolist()

# --- RENDERIZADO ---
if data_final:
    st.markdown(f"### 📈 Visualización Proactiva: {problema_input}")
    fig = draw_ishikawa(data_final, problema_input, tema_color)
    st.pyplot(fig, transparent=True)
    
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, transparent=True)
    st.download_button("🚀 DESCARGAR ANÁLISIS 4.0", buf.getvalue(), "ishikawa_vision_metrics.png", "image/png")
else:
    st.info("👋 Bienvenida/o. Selecciona un método en el panel izquierdo para comenzar el análisis.")
