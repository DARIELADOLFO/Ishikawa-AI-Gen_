import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Ishikawa AI Gen - CENTRO PROACTIVO - REDUCCION DE AVERIAS",
    page_icon="📊",
    layout="wide"
)

# --- DISEÑO UX/UI ÉPICO (CSS) ---
st.markdown("""
    <style>
    /* Fondo y Estética General */
    .main {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }
    .stApp {
        background-color: transparent;
    }
    
    /* Efecto Glassmorphism en Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Títulos Impactantes */
    .titulo-epico {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(90deg, #ff0000, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .autor {
        text-align: right;
        font-size: 0.9rem;
        color: rgba(255,255,255,0.6);
        font-style: italic;
        margin-top: -10px;
    }

    /* Botones Estilo Cyberpunk */
    div.stButton > button {
        background: linear-gradient(45deg, #ff0000 0%, #a30000 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 10px;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.3);
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(255, 0, 0, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA (LOGO Y TÍTULO) ---
col_logo, col_tit = st.columns([1, 4])

with col_logo:
    # Logo de Claro Dominicana (URL de imagen sin fondo)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Logo_Claro.svg/1200px-Logo_Claro.svg.png", width=120)

with col_tit:
    st.markdown('<h1 class="titulo-epico">ISHIKAWA ANALYTICS 4.0</h1>', unsafe_allow_html=True)
    st.markdown('<p class="autor">Powered by Vision Metrics | Creado por <b>Dariel A. Peña</b></p>', unsafe_allow_html=True)

st.markdown("---")

# --- LÓGICA DE DIBUJO ---
def draw_ishikawa(data_dict, title, color_theme):
    fig, ax = plt.subplots(figsize=(16, 9), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(0, 12)
    ax.set_ylim(-6, 6)
    ax.axis('off')

    # Espina dorsal estilo neón
    ax.annotate('', xy=(10.5, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', lw=5, color=color_theme))

    # Cabeza (Problema)
    ax.text(10.7, 0, title, fontsize=14, fontweight='bold', color='white',
            bbox=dict(facecolor=color_theme, edgecolor='white', boxstyle='round,pad=1', lw=2),
            ha='left', va='center')

    categorias = list(data_dict.keys())
    x_positions = [1.5, 4.5, 7.5] 

    for i, cat in enumerate(categorias):
        is_top = i < 3
        idx = i if is_top else i - 3
        if idx >= len(x_positions): break
        
        x_i = x_positions[idx]
        x_f = x_i + 1.8
        y_f = 4.2 if is_top else -4.2
        
        # Clasificación
        ax.plot([x_i, x_f], [0, y_f], color='white', lw=3, alpha=0.8)
        
        label_cat = f"{cat}\n({data_dict[cat]['_pct']:.1f}%)"
        ax.text(x_f, y_f + (0.5 if is_top else -0.8), label_cat, 
                fontsize=11, fontweight='bold', color='white', ha='center',
                bbox=dict(facecolor='#1a1a1a', edgecolor=color_theme, boxstyle='round,pad=0.5'))

        # Causas
        causas = [k for k in data_dict[cat].keys() if k != '_pct']
        for j, causa in enumerate(causas):
            r = (j + 1) / (len(causas) + 1)
            cx, cy = x_i + (x_f - x_i) * r, y_f * r
            
            ax.plot([cx, cx - 1], [cy, cy], color=color_theme, lw=2)
            ax.text(cx - 1.1, cy, causa, fontsize=10, color='white', ha='right', va='center', fontweight='semibold')
            
            # Sub-causas
            subcausas = data_dict[cat][causa]
            for k, sub in enumerate(subcausas):
                offset = (k + 1) * 0.3
                ax.text(cx - 0.5, cy - offset if is_top else cy + offset, 
                        f"● {sub}", fontsize=9, ha='left', color='#00d4ff', style='italic')

    return fig

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### ⚙️ PANEL DE CONTROL")
    tema_color = st.color_picker("Color de Identidad", "#EF3829") # Rojo Claro
    problema = st.text_input("Causa Raíz (Cabeza)", "TOP 20 CLIENTES REPETIDOS")
    st.markdown("---")
    metodo = st.selectbox("Método de Datos", ["Subir Excel", "Entrada Manual"])

# --- PROCESAMIENTO ---
data_final = {}
if metodo == "Subir Excel":
    file = st.file_uploader("Sube el reporte de averías (.xlsx)", type=["xlsx"])
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
    st.markdown(f"### 🔍 Análisis Generado para: {problema}")
    fig = draw_ishikawa(data_final, problema, tema_color)
    st.pyplot(fig, transparent=True)
    
    # Descarga
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, transparent=True)
    st.download_button("🚀 EXPORTAR ANÁLISIS EN ALTA RESOLUCIÓN", buf.getvalue(), "ishikawa_vision_metrics.png", "image/png")
else:
    st.info("💡 Esperando datos... Sube un Excel con las columnas: CLASIFICACION, Causa, Sub-Causa")