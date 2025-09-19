import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


# ----------------------------------
# 1. Gráfico de taxas de default
# ----------------------------------
def plot_pd_error(df_pivot, yaxis_title, yaxis_range, ticksuffix="", height=350):
    """
    Gráfico de linha para erro de PD.
    df_pivot: DataFrame com colunas ['date', 'erro_pd']
    """
    fig = px.line(
        df_pivot,
        x="date",
        y="erro_pd",
        markers=True,
        labels={"date": "Data", "erro_pd": yaxis_title}
    )
    
    # Linha zero
    fig.add_hline(y=0, line_dash="dash", line_color="gray",
                annotation_text="Erro zero", annotation_position="bottom left")
    
    # Linha de erro
    fig.update_traces(line=dict(color="blue"), marker=dict(size=8), name="Erro")
    
    # Layout compacto
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title=yaxis_title,
        template="plotly_white",
        hovermode="x unified",
        height=height,
        margin=dict(l=40, r=20, t=20, b=40)  # margens reduzidas
    )
    
    fig.update_yaxes(range=yaxis_range, ticksuffix=ticksuffix)
    
    return fig
# ----------------------------------
# 2. Gráfico de erro PD
# ----------------------------------
def plot_default_rates(df_pivot, height=350):
    """
    Gráfico de linha para taxas de default.
    df_pivot: DataFrame pivotado com colunas ['date', 'taxa_default_realizada', 'taxa_default_estimada']
    """
    fig = px.line(
        df_pivot,
        x="date",
        y=["taxa_default_realizada", "taxa_default_estimada"],
        markers=True,
        labels={"date": "Data", "value": "Taxa de Default (%)", "variable": "Métrica"}
    )
    
    # Cores e estilos das linhas
    fig.update_traces(selector=dict(name="taxa_default_realizada"),
                    line=dict(color="gray"), name="Realizada (%)")
    fig.update_traces(selector=dict(name="taxa_default_estimada"),
                    line=dict(color="blue", dash="dot"), name="Estimada (%)")
    
    # Layout compacto
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Taxa de Default (%)",
        template="plotly_white",
        hovermode="x unified",
        height=height,
        margin=dict(l=40, r=20, t=20, b=40)  # margens reduzidas
    )
    
    fig.update_yaxes(ticksuffix="%")
    
    return fig

# ----------------------------------
# 3. Gráfico interativo genérico
# ----------------------------------
def plot_metric_interactive(
    df,
    metric,
    thresholds=None,
    direction="neutral",
    default_color="blue",
    marker_size=10,
    line_color="blue",
    height=350
):
    """
    df: DataFrame com colunas ['date', 'metric_value']
    metric: nome da métrica
    thresholds: dict com 'attention' e 'alert' (valores numéricos)
    direction: "higher_better", "lower_better", "neutral"
    """
    df = df.copy()
    df["metric_value"] = pd.to_numeric(df["metric_value"], errors="coerce")

    # --- Definir cor dos pontos ---
    colors = []
    for val in df["metric_value"]:
        if direction == "neutral" or thresholds is None:
            colors.append(default_color)
        elif direction == "higher_better":
            if thresholds.get("alert") is not None and val < thresholds["alert"]:
                colors.append("red")
            elif thresholds.get("attention") is not None and val < thresholds["attention"]:
                colors.append("orange")
            else:
                colors.append(default_color)
        elif direction == "lower_better":
            if thresholds.get("alert") is not None and val > thresholds["alert"]:
                colors.append("red")
            elif thresholds.get("attention") is not None and val > thresholds["attention"]:
                colors.append("orange")
            else:
                colors.append(default_color)
        else:
            colors.append(default_color)

    # --- Linha principal ---
    fig = px.line(
        df,
        x="date",
        y="metric_value",
        markers=True,
        labels={"metric_value": metric, "date": "Data"}
    )
    fig.update_traces(marker=dict(color=colors, size=marker_size), line=dict(color=line_color))

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
                    marker=dict(color=default_color, size=10), name="Bom")
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
        hovermode="x unified",
        height=height
    )

    return fig


# ----------------------------------
# 4. Gráfico estático (matplotlib)
# ----------------------------------
def plot_metric(
    df,
    metric,
    thresholds=None,
    figsize=(12, 5),
    line_color="#1f77b4",
    line_width=2,
    marker_size=6,
    grid=True,
    highlight_thresholds=True
):
    fig, ax = plt.subplots(figsize=figsize)

    # --- Plot da métrica ---
    ax.plot(
        df["date"],
        df["metric_value"],
        marker="o",
        color=line_color,
        linewidth=line_width,
        markersize=marker_size,
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

    if grid:
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        ax.xaxis.grid(True, linestyle='--', alpha=0.7)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#AAAAAA')

    # --- Destacar pontos acima dos thresholds ---
    if highlight_thresholds and thresholds:
        alert_value = thresholds.get("alert", None)
        if alert_value:
            exceed = df[df["metric_value"] > alert_value]
            ax.scatter(exceed["date"], exceed["metric_value"], color="red", s=50, zorder=5)

        attention_value = thresholds.get("attention", None)
        if attention_value:
            exceed = df[
                (df["metric_value"] > attention_value) &
                (alert_value is None or df["metric_value"] <= alert_value)
            ]
            ax.scatter(exceed["date"], exceed["metric_value"], color="orange", s=50, zorder=5)

    # --- Ajuste do eixo x ---
    plt.xticks(rotation=45, ha="right", fontsize=10)

    # --- Legenda fora do gráfico ---
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(
        by_label.values(), by_label.keys(),
        title="Legenda",
        title_fontsize=11, fontsize=10,
        bbox_to_anchor=(1.05, 1), loc='upper left'
    )

    plt.tight_layout()
    return fig


import plotly.express as px

def plot_n_contratos(df_contratos, date_column, count_column, height=400):
    """
    Plota o número de contratos por data.

    Parâmetros:
    -----------
    df_contratos : DataFrame
        DataFrame contendo as colunas de data e contagem.
    date_column : str
        Nome da coluna com as datas.
    count_column : str
        Nome da coluna com os valores de contagem.
    height : int
        Altura do gráfico.
    """
    fig = px.bar(
        df_contratos,
        x=date_column,
        y=count_column,
        labels={date_column: "Data", count_column: "Nº Contratos"},
        text=count_column
    )
    fig.update_traces(marker_color="lightgray", texttemplate="%{text}", textposition="outside")
    fig.update_layout(
        title=f"Número de Contratos por Mês",
        template="plotly_white",
        height=height,
        xaxis_title="Data",
        yaxis_title="Nº Contratos",
        hovermode="x unified"
    )
    return fig
