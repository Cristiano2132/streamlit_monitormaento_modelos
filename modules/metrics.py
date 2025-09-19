def prepare_default_rates(df):
    """Converte taxas para porcentagem"""
    df_pivot = df.pivot(index="date", columns="metric_name", values="metric_value").reset_index()
    for col in ["taxa_default_realizada", "taxa_default_estimada"]:
        df_pivot[col] = df_pivot[col].astype(float) * 100
    return df_pivot

def calculate_error(df, vol, error_view="Taxa (%)"):
    """Calcula erro de PD em % ou R$"""
    df_pivot = df.pivot(index="date", columns="metric_name", values="metric_value").reset_index()
    for col in ["taxa_default_realizada", "taxa_default_estimada"]:
        df_pivot[col] = df_pivot[col].astype(float)

    if error_view == "Taxa (%)":
        df_pivot["erro_pd"] = (df_pivot["taxa_default_estimada"] - df_pivot["taxa_default_realizada"]) * 100
        return df_pivot, "Erro de PD (%)", [-5, 5], "%"
    else:
        df_pivot["erro_pd"] = (df_pivot["taxa_default_estimada"] - df_pivot["taxa_default_realizada"]) * vol
        return df_pivot, "Erro de PD (R$)", None, ""