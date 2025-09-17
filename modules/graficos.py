import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


def plot_metric_interactive(df, metric, thresholds=None, direction="neutral"):
    """
    df: DataFrame com colunas ['date', 'metric_value']
    metric: nome da métrica
    thresholds: dict com 'attention' e 'alert' (valores numéricos)
    direction: "higher_better", "lower_better", "neutral"
    """
    import plotly.express as px
    
    df = df.copy()
    df["metric_value"] = pd.to_numeric(df["metric_value"], errors="coerce")

    # --- Definir cor dos pontos de acordo com direção e thresholds ---
    colors = []
    for val in df["metric_value"]:
        if direction == "neutral" or thresholds is None:
            colors.append("blue")
        elif direction == "higher_better":
            if thresholds.get("alert") is not None and val < thresholds["alert"]:
                colors.append("red")
            elif thresholds.get("attention") is not None and val < thresholds["attention"]:
                colors.append("orange")
            else:
                colors.append("blue")
        elif direction == "lower_better":
            if thresholds.get("alert") is not None and val > thresholds["alert"]:
                colors.append("red")
            elif thresholds.get("attention") is not None and val > thresholds["attention"]:
                colors.append("orange")
            else:
                colors.append("blue")
        else:
            colors.append("blue")

    # --- Linha principal com cores dos pontos ---
    fig = px.line(
        df,
        x="date",
        y="metric_value",
        markers=True,
        labels={"metric_value": metric, "date": "Data"}
    )
    fig.update_traces(marker=dict(color=colors, size=10))

    # --- Adicionar thresholds ---
    if thresholds:
        if thresholds.get("attention") is not None:
            fig.add_hline(
                y=thresholds["attention"], line_dash="dash", line_color="orange",
                annotation_text=f"Atenção ({thresholds['attention']})", annotation_position="top left"
            )
        if thresholds.get("alert") is not None:
            fig.add_hline(
                y=thresholds["alert"], line_dash="dash", line_color="red",
                annotation_text=f"Alerta ({thresholds['alert']})", annotation_position="top left"
            )

    # --- Legenda de cores “fantasma” ---
    fig.add_scatter(x=[None], y=[None], mode="markers",
                    marker=dict(color="blue", size=10), name="Bom")
    fig.add_scatter(x=[None], y=[None], mode="markers",
                    marker=dict(color="orange", size=10), name="Atenção")
    fig.add_scatter(x=[None], y=[None], mode="markers",
                    marker=dict(color="red", size=10), name="Alerta")

    # --- Layout final ---
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title=metric,
        legend_title="Legenda",
        template="plotly_white",
        hovermode="x unified"
    )

    return fig


def plot_metric(df, metric, thresholds=None):
    fig, ax = plt.subplots(figsize=(12, 5))

    # --- Plot da métrica ---
    ax.plot(
        df["date"], 
        df["metric_value"], 
        marker="o", 
        color="#1f77b4", 
        linewidth=2, 
        markersize=6,
        label=metric
    )

    # --- Adicionar thresholds ---
    if thresholds:
        if "attention" in thresholds:
            ax.axhline(y=thresholds["attention"], color="orange", linestyle="--", linewidth=2, label="Atenção")
        if "alert" in thresholds:
            ax.axhline(y=thresholds["alert"], color="red", linestyle="--", linewidth=2, label="Alerta")

    # --- Ajustes de estética ---
    ax.set_xlabel("Data", fontsize=12)
    ax.set_ylabel(metric, fontsize=12)

    # Grid pontilhado leve
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)

    # Remover bordas desnecessárias
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#AAAAAA')

    # Pontos destacados acima do threshold (opcional)
    if thresholds:
        alert_value = thresholds.get("alert", None)
        if alert_value:
            exceed = df[df["metric_value"] > alert_value]
            ax.scatter(exceed["date"], exceed["metric_value"], color="red", s=50, zorder=5)

        attention_value = thresholds.get("attention", None)
        if attention_value:
            exceed = df[(df["metric_value"] > attention_value) & (df["metric_value"] <= alert_value)]
            ax.scatter(exceed["date"], exceed["metric_value"], color="orange", s=50, zorder=5)

    # Ajuste do eixo x
    plt.xticks(rotation=45, ha="right", fontsize=10)

    # Legenda fora do gráfico
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), title="Legenda",
            title_fontsize=11, fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    return fig