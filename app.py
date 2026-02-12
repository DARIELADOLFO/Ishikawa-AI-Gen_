import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ishikawa Analytics Pro Final", page_icon="📊", layout="wide")

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

st.markdown('<h1 class="titulo">ISHIKAWA ANALYTICS FINAL</h1>', unsafe_allow_html=True)

# --- MOTOR GRÁFICO (JERARQUÍA VISUAL CORREGIDA) ---
def draw_ishikawa_hierarchical(data, title, col_line, col_txt_cls, col_txt_cau, col_txt_sub):
    
    # Calcular altura necesaria
    max_items = 0
    for cat in data.values():
        for subcat in cat.values():
            count = len(subcat) + sum(len(subs) for subs in subcat.values())
            if count > max_items: max_items = count
            
    fig_height = max(14, 8 + (max_items * 0.7)) 
    fig, ax = plt.subplots(figsize=(26, fig_height), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(-2, 24)
    ax.set_ylim(-fig_height/2, fig_height/2)
    ax.axis('off')

    # 1. ESPINA DORSAL (Backbone)
    ax.plot([0, 20], [0, 0], color=col_line, lw=6, zorder=1)

    # 2. CABEZA
    head = patches.FancyBboxPatch((20, -2.5), 3.5, 5, boxstyle="round,pad=0.2", 
                                  ec=col_line, fc="#d3d3d3", lw=3, zorder=3)
    ax.add_patch(head)
    ax.text(21.75, 0, title, ha='center', va='center', fontsize=12, fontweight='bold', color='black', wrap=True)

    # 3. DIBUJAR CLASIFICACIONES (Diagonales grandes)
    cats = list(data.keys())
    for i, cat_name in enumerate(cats):
        is_top = i % 2 == 0
        direction = 1 if is_top else -1
        
        x_root = 19 - (i // 2) * 6.5  # Espaciado horizontal
        x_tip = x_root - 4.5
        y_root = 0
        y_tip = 9 * direction
        
        # Línea Diagonal de Clasificación
        ax.plot([x_root, x_tip], [y_root, y_tip], color=col_line, lw=4, alpha=0.9)
        
        # Etiqueta Clasificación
        ax.text(x_tip, y_tip + (0.6 * direction), cat_name, ha='center', va='center', 
                fontsize=14, fontweight='bold', color=col_txt_cls,
                bbox=dict(facecolor=col_line, edgecolor='white', boxstyle='round,pad=0.5'))

        # 4. CATEGORÍAS (Líneas Horizontales saliendo de la diagonal)
        subcats = data[cat_name]
        num_sub = len(subcats)
        
        for j, (subcat_name, causas_dict) in enumerate(subcats.items()):
            ratio = (j + 1) / (num_sub + 1)
            cx = x_root + (x_tip - x_root) * ratio
            cy = y_root + (y_tip - y_root) * ratio
            
            # Línea Horizontal de Categoría
            len_h = 4.0
            ax.plot([cx, cx - len_h], [cy, cy], color=col_line, lw=2.5) # Más gruesa para notar jerarquía
            ax.text(cx - len_h - 0.2, cy, subcat_name, ha='right', va='center', 
                    fontsize=12, fontweight='bold', color=col_txt_cau)
            
            # 5. CAUSAS (Saliendo de la línea Horizontal de Categoría)
            # Usamos el cursor vertical para que no choquen
            vertical_cursor = 0.8 * direction 
            
            for causa_txt, subs_list in causas_dict.items():
                
                # Coordenadas de la CAUSA
                # La Causa debe conectarse visualmente a la línea de categoría (cy)
                
                # Punto donde va el texto de la causa
                px_text = cx - 1.5
                py_text = cy + vertical_cursor
                
                # Punto de conexión en la línea horizontal de la categoría
                # Hacemos que la línea salga inclinada desde la horizontal hacia el texto
                px_connect = cx - 0.5 
                
                # DIBUJAR CONECTOR: De la línea horizontal -> Al texto de la Causa
                ax.plot([px_connect, px_text + 0.1], [cy, py_text], color=col_line, lw=1.0)
                
                # Texto de la Causa
                ax.text(px_text, py_text, causa_txt, ha='right', va='center', 
                        fontsize=10, color=col_txt_cau, fontweight='bold')
                
                # Mover cursor para las subcausas
                vertical_cursor += (0.6 * direction)
                
                # 6. SUB-CAUSAS (Debajo de la causa)
                for sub in subs_list:
                    sy = cy + vertical_cursor
                    
                    # Conector sutil para subcausa (opcional, o solo identación)
                    # ax.plot([px_text, px_text + 0.2], [py_text, sy], color=col_line, lw=0.5, alpha=0.5)
                    
                    ax.text(px_text + 0.5, sy, f"↳ {sub}", ha='left', va='center', 
                            fontsize=9, color=col_txt_sub, style='italic')
                    
                    vertical_cursor += (0.45 * direction)
                
                # Espacio extra entre bloques de causas
                vertical_cursor += (0.4 * direction)

    return fig

# --- LECTURA DE DATOS ---
data_final = {}
file = st.file_uploader("Sube Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    if df.shape[1] >= 4:
        df.columns = ["CLS", "CAT", "CAU", "SUB"]
        # Agrupación estricta
        for cls, g1 in df.groupby("CLS"):
            data_final[cls] = {}
            for cat, g2 in g1.groupby("CAT"):
                data_final[cls][cat] = {}
                for cau, g3 in g2.groupby("CAU"):
                    subs = [str(x).strip() for x in g3["SUB"].dropna() if str(x).strip() != '']
                    data_final[cls][cat][cau] = subs

# --- RENDER ---
if data_final:
    fig = draw_ishikawa_hierarchical(data_final, problema_input, tema_lineas, color_clasif, color_causas, color_subs)
    st.pyplot(fig, transparent=True)
    
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, transparent=True)
    st.download_button("📥 Descargar PNG", buf.getvalue(), "ishikawa.png", "image/png")
    
    buf_svg = BytesIO()
    fig.savefig(buf_svg, format="svg", transparent=True)
    st.download_button("📥 Descargar SVG", buf_svg.getvalue(), "ishikawa.svg", "image/svg+xml")
    
