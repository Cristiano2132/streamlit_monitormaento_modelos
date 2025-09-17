import pandas as pd
import plotly.graph_objects as go

def plot_risk_matrix(models_df):
    """
    Gera a matriz de risco com base nos riscos qualitativos e quantitativos dos modelos.
    Retorna um objeto Plotly Figure.
    """
    risk_levels = ["Muito Baixo", "Baixo", "Médio", "Alto"]

    # Garantir que as colunas sejam categóricas ordenadas
    for col in ["risco_qualitativo", "risco_quantitativo"]:
        models_df[col] = pd.Categorical(models_df[col], categories=risk_levels, ordered=True)

    # Map de risco combinado
    risk_map = {
        ("Muito Baixo", "Muito Baixo"): 1, ("Muito Baixo", "Baixo"): 1, ("Muito Baixo", "Médio"): 2, ("Muito Baixo", "Alto"): 3,
        ("Baixo", "Muito Baixo"): 1, ("Baixo", "Baixo"): 2, ("Baixo", "Médio"): 3, ("Baixo", "Alto"): 3,
        ("Médio", "Muito Baixo"): 2, ("Médio", "Baixo"): 3, ("Médio", "Médio"): 3, ("Médio", "Alto"): 4,
        ("Alto", "Muito Baixo"): 3, ("Alto", "Baixo"): 3, ("Alto", "Médio"): 4, ("Alto", "Alto"): 4,
    }

    # Todas as combinações possíveis
    all_combos = pd.DataFrame(
        [(q, qt) for q in risk_levels for qt in risk_levels],
        columns=["risco_qualitativo", "risco_quantitativo"]
    )

    # Contagem de modelos por combinação
    count_data = models_df.groupby(["risco_qualitativo", "risco_quantitativo"]).size().reset_index(name="count")
    heat_data = all_combos.merge(count_data, on=["risco_qualitativo", "risco_quantitativo"], how="left").fillna(0)

    # Risco combinado
    heat_data["risk_score"] = heat_data.apply(
        lambda row: risk_map[(row["risco_qualitativo"], row["risco_quantitativo"])], axis=1
    )

    # Pivot para matriz
    z_text = heat_data.pivot(index="risco_qualitativo", columns="risco_quantitativo", values="count").reindex(index=risk_levels, columns=risk_levels).astype(int)
    z_color = heat_data.pivot(index="risco_qualitativo", columns="risco_quantitativo", values="risk_score").reindex(index=risk_levels, columns=risk_levels)

    # Cores do heatmap
    colors = {1: "#2ecc71", 2: "#f1c40f", 3: "#e67e22", 4: "#e74c3c"}

    fig = go.Figure(data=go.Heatmap(
        z=z_color.values,
        x=risk_levels,
        y=risk_levels,
        text=z_text.values,
        texttemplate="%{text}",
        textfont={"size":18, "color":"black"},
        colorscale=[[0, colors[1]], [0.33, colors[2]], [0.66, colors[3]], [1, colors[4]]],
        showscale=False,
        hovertemplate="Risco Qualitativo: %{y}<br>Risco Quantitativo: %{x}<br>Risco Combinado: %{z}<extra></extra>"
    ))

    # Anotações com negrito se houver modelos
    for i, y in enumerate(risk_levels):
        for j, x in enumerate(risk_levels):
            val = z_text.loc[y, x]
            text = f"<b>{val}</b>" if val > 0 else " "
            fig.add_annotation(
                x=x,
                y=y,
                text=text,
                showarrow=False,
                font=dict(size=18, color="black"),
                align="center"
            )

    fig.update_layout(
        xaxis=dict(title="Risco Quantitativo", side="top", scaleanchor="y"),
        yaxis=dict(title="Risco Qualitativo"),
        height=600,
        width=600
    )
    
    return fig