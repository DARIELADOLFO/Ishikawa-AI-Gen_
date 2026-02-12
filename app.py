import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generar_ishikawa(excel_path, problema, output="ishikawa.png"):
    df = pd.read_excel(excel_path)

    categorias = df["Categoria"].unique()
    total_categorias = len(categorias)

    # Configuración de figura grande y profesional
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.set_xlim(0, 20)
    ax.set_ylim(-10, 10)
    ax.axis("off")

    # Línea principal (espina)
    ax.plot([1, 18], [0, 0], linewidth=3)

    # Cabeza del pez
    ax.text(
        19, 0, problema,
        fontsize=18,
        va='center',
        ha='center',
        bbox=dict(boxstyle="round,pad=0.8", ec="black", fc="#f0f0f0")
    )

    # Espaciado horizontal dinámico
    posiciones_x = np.linspace(3, 16, total_categorias)

    for i, categoria in enumerate(categorias):
        causas = df[df["Categoria"] == categoria]["Causa"].tolist()

        x = posiciones_x[i]

        # Alternar arriba y abajo
        if i % 2 == 0:
            y = 6
            direccion = 1
        else:
            y = -6
            direccion = -1

        # Línea diagonal principal
        ax.plot([x, x - 1.5], [0, y], linewidth=2)

        # Texto categoría
        ax.text(
            x - 1.5, y + direccion * 1,
            categoria.upper(),
            fontsize=14,
            fontweight="bold",
            ha='center'
        )

        # Subcausas con separación real
        separacion = 1.5
        total_causas = len(causas)

        for j, causa in enumerate(causas):
            offset = (j - total_causas/2) * separacion

            ax.plot(
                [x - 1.5, x - 3],
                [y + offset, y + offset + direccion * 0.5],
                linewidth=1
            )

            ax.text(
                x - 3.2,
                y + offset + direccion * 0.5,
                causa,
                fontsize=11,
                ha='right'
            )

    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Diagrama generado: {output}")


# -------------------------------
# USO
# -------------------------------
generar_ishikawa(
    excel_path="datos_ishikawa.xlsx",
    problema="AVERÍAS RED CORE"
)
