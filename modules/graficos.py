import matplotlib.pyplot as plt
import plotly.express as px

def plot_metric_interactive(df, metric, thresholds=None):
    """
    df: DataFrame com colunas ['date', 'metric_value']
    metric: nome da métrica
    thresholds: dict com 'attention' e 'alert'
    """
    fig = px.line(
        df,
        x="date",
        y="metric_value",
        markers=True,
        labels={"metric_value": metric, "date": "Data"}
    )

    # Adicionar thresholds
    if thresholds:
        if "attention" in thresholds:
            fig.add_hline(y=thresholds["attention"], line_dash="dash", line_color="orange", 
                        annotation_text="Atenção", annotation_position="top left")
        if "alert" in thresholds:
            fig.add_hline(y=thresholds["alert"], line_dash="dash", line_color="red", 
                        annotation_text="Alerta", annotation_position="top left")

    # Destaque dos pontos acima do threshold
    if thresholds:
        alert_value = thresholds.get("alert")
        attention_value = thresholds.get("attention")
        
        if alert_value:
            exceed_alert = df[df["metric_value"] > alert_value]
            fig.add_scatter(x=exceed_alert["date"], y=exceed_alert["metric_value"],
                            mode="markers", marker=dict(color="red", size=10), name="Acima Alerta")
        
        if attention_value:
            exceed_attention = df[(df["metric_value"] > attention_value) & 
                                (df["metric_value"] <= alert_value)]
            fig.add_scatter(x=exceed_attention["date"], y=exceed_attention["metric_value"],
                            mode="markers", marker=dict(color="orange", size=10), name="Acima Atenção")

    fig.update_layout(
        xaxis_title="Data",
        yaxis_title=metric,
        legend_title="Legenda",
        template="plotly_white"
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