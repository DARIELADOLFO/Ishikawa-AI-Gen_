import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ishikawa Analytics Pro 7.0", page_icon="📊", layout="wide")

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
    problema_input = st.text_area("Problema Principal", "CASOS PROACTIVOS (60)")

# --- ESTILOS ---
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
    .titulo {{ text-align: center; font-family: sans-serif; font-size: 3rem; font-weight: 800; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="titulo">ISHIKAWA ANALYTICS 7.0</h1>', unsafe_allow_html=True)

# --- MOTOR GRÁFICO (CURSOR ACUMULATIVO) ---
def draw_ishikawa_final(data, title, col_line, col_txt_cls, col_txt_cau, col_txt_sub):
    
    # Calcular altura necesaria basada en la cantidad máxima de ítems en una rama
    max_items = 0
    for cat in data.values():
        for subcat in cat.values():
            # Contamos causas + subcausas para saber la altura real
            count = len(subcat) + sum(len(subs) for subs in subcat.values())
            if count > max_items: max_items = count
            
    fig_height = max(12, 6 + (max_items * 0.6)) 
    fig, ax = plt.subplots(figsize=(24, fig_height), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(-2, 22)
    ax.set_ylim(-fig_height/2, fig_height/2)
    ax.axis('off')

    # 1. ESPINA DORSAL
    ax.plot([0, 18], [0, 0], color=col_line, lw=5, zorder=1)

    # 2. CABEZA
    head = patches.FancyBboxPatch((18, -2.5), 3.5, 5, boxstyle="round,pad=0.2", 
                                  ec=col_line, fc="#d3d3d3", lw=3, zorder=3)
    ax.add_patch(head)
    ax.text(19.75, 0, title, ha='center', va='center', fontsize=12, fontweight='bold', color='black', wrap=True)

    # 3. DIBUJAR CLASIFICACIONES
    cats = list(data.keys())
    for i, cat_name in enumerate(cats):
        is_top = i % 2 == 0
        direction = 1 if is_top else -1
        
        # Coordenadas base de la espina principal
        x_root = 17 - (i // 2) * 6
        x_tip = x_root - 4
        y_root = 0
        y_tip = 8 * direction
        
        # Línea de Clasificación
        ax.plot([x_root, x_tip], [y_root, y_tip], color=col_line, lw=4, alpha=0.8)
        
        # Etiqueta Clasificación
        ax.text(x_tip, y_tip + (0.5 * direction), cat_name, ha='center', va='center', 
                fontsize=14, fontweight='bold', color=col_txt_cls,
                bbox=dict(facecolor=col_line, edgecolor='white', boxstyle='round,pad=0.5'))

        # 4. CATEGORÍAS SECUNDARIAS (Ramificación)
        subcats = data[cat_name]
        num_sub = len(subcats)
        
        for j, (subcat_name, causas_dict) in enumerate(subcats.items()):
            # Posición a lo largo de la espina diagonal
            ratio = (j + 1) / (num_sub + 1)
            cx = x_root + (x_tip - x_root) * ratio
            cy = y_root + (y_tip - y_root) * ratio
            
            # Línea horizontal de Categoría Secundaria
            len_h = 3.5
            ax.plot([cx, cx - len_h], [cy, cy], color=col_line, lw=2)
            ax.text(cx - len_h - 0.2, cy, subcat_name, ha='right', va='center', 
                    fontsize=11, fontweight='bold', color=col_txt_cau)
            
            # --- LÓGICA DE NO-SUPERPOSICIÓN (CURSOR) ---
            # Este cursor lleva la cuenta de cuánto hemos bajado
            vertical_cursor = 0.6 * direction # Empezamos un poco separados de la línea
            
            for causa_txt, subs_list in causas_dict.items():
                # Coordenadas de la CAUSA
                px = cx - 1.5
                py = cy + vertical_cursor
                
                # Dibujar Causa
                ax.text(px, py, f"• {causa_txt}", ha='left', va='center', 
                        fontsize=9, color=col_txt_cau, fontweight='bold')
                
                # Mover cursor para las subcausas
                vertical_cursor += (0.5 * direction)
                
                # Dibujar Sub-causas
                for sub in subs_list:
                    sy = cy + vertical_cursor
                    ax.text(px + 0.5, sy, f"↳ {sub}", ha='left', va='center', 
                            fontsize=8, color=col_txt_sub, style='italic')
                    # Cada subcausa ocupa espacio, movemos el cursor
                    vertical_cursor += (0.4 * direction)
                
                # Espacio extra antes de la siguiente Causa para que no se peguen
                vertical_cursor += (0.3 * direction)

    return fig

# --- LECTURA DE DATOS (AGRUPACIÓN ROBUSTA) ---
data_final = {}
file = st.file_uploader("Sube Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    # Estandarizar nombres de columnas (toma las 4 primeras sin importar el nombre)
    if df.shape[1] >= 4:
        df.columns = ["CLS", "CAT", "CAU", "SUB"]
        
        # Agrupación Jerárquica REAL
        for cls, g1 in df.groupby("CLS"):
            data_final[cls] = {}
            for cat, g2 in g1.groupby("CAT"):
                data_final[cls][cat] = {}
                for cau, g3 in g2.groupby("CAU"):
                    # Lista de subcausas limpias
                    subs = [str(x).strip() for x in g3["SUB"].dropna() if str(x).strip() != '']
                    data_final[cls][cat][cau] = subs

# --- RENDER ---
if data_final:
    fig = draw_ishikawa_final(data_final, problema_input, tema_lineas, color_clasif, color_causas, color_subs)
    st.pyplot(fig, transparent=True)
    
    # Descargas
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, transparent=True)
    st.download_button("📥 Descargar PNG", buf.getvalue(), "ishikawa.png", "image/png")
    
    buf_svg = BytesIO()
    fig.savefig(buf_svg, format="svg", transparent=True)
    st.download_button("📥 Descargar SVG", buf_svg.getvalue(), "ishikawa.svg", "image/svg+xml")
