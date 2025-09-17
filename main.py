import pandas as pd
import numpy as np

# -----------------------------
# Model metadata
# -----------------------------
n_models = 10
model_names = [f"MPD_{i:02d}" for i in range(1, n_models+1)]
model_types = ["binary","binary","continuous","continuous","binary","continuous","binary","continuous","binary","continuous"]
volumes = [1500000, 1200000, 2000000, 1800000, 1000000, 2200000, 1300000, 2500000, 1100000, 2000000]
risco_qual = ["Médio","Alto","Médio","Baixo","Alto","Médio","Baixo","Médio","Alto","Médio"]
risco_quant = ["Médio","Alto","Médio","Baixo","Médio","Médio","Baixo","Alto","Alto","Médio"]
risco_geral = ["Médio","Alto","Médio","Baixo","Alto","Médio","Baixo","Alto","Alto","Médio"]

df_models = pd.DataFrame({
    "id": range(1, n_models+1),
    "name": model_names,
    "description": ["Modelo de PD IFRS9"]*n_models,
    "type": model_types,
    "vol_carteira": volumes,
    "risco_qualitativo": risco_qual,
    "risco_quantitativo": risco_quant,
    "risco_geral": risco_geral
})

df_models.to_csv("models.csv", index=False)
print("models.csv criado com sucesso!")

# -----------------------------
# Simulação de métricas mensais
# -----------------------------
months = pd.date_range("2025-01-01", periods=6, freq="MS")
metrics_perf = ["Accuracy","ROC-AUC","KS","RMSE","R2"]
metrics_stab = ["PSI"]

rows = []

for _, model in df_models.iterrows():
    model_id = model.id
    vol_carteira = model.vol_carteira
    
    for month in months:
        # Performance
        for metric in metrics_perf:
            if metric in ["Accuracy","ROC-AUC","R2"]:
                value = np.round(np.random.uniform(0.7, 0.95), 2)
            else:
                value = np.round(np.random.uniform(0.2, 0.4), 2)
            rows.append([model_id, metric, value, "performance", month])
        
        # Stability
        for metric in metrics_stab:
            value = np.round(np.random.uniform(0.05, 0.15),2)
            rows.append([model_id, metric, value, "stability", month])
        
        # Default metrics
        vol = np.random.randint(int(0.03*vol_carteira), int(0.05*vol_carteira))
        taxa_real = np.round(np.random.binomial(1,0.02,vol).mean(),4)
        taxa_est = np.round(np.random.uniform(0.01,0.05,vol).mean(),4)
        rows.append([model_id,"taxa_default_realizada",taxa_real,"default",month])
        rows.append([model_id,"taxa_default_estimada",taxa_est,"default",month])
        rows.append([model_id,"vol_contratos",vol,"default",month])

        # Risco agregado
        risk_score = taxa_est
        if risk_score < 0.02:
            risk_level = "low"
        elif risk_score < 0.04:
            risk_level = "medium"
        else:
            risk_level = "high"
        rows.append([model_id,"risk_score",np.round(risk_score,4),"risk",month])
        rows.append([model_id,"risk_level",risk_level,"risk",month])

# Criar DataFrame de métricas
df_metrics = pd.DataFrame(rows, columns=["model_id","metric_name","metric_value","metric_type","date"])
df_metrics.to_csv("models_metrics.csv", index=False)
print("models_metrics.csv criado com sucesso!")


metrics_desc = [
    # Performance
    ["ROC-AUC", "Área sob a curva ROC", 0.75, 0.70, "performance", "higher_better"],
    ["KS", "Kolmogorov-Smirnov", 0.25, 0.20, "performance", "higher_better"],
    ["Accuracy", "Acurácia do modelo", 0.80, 0.75, "performance", "higher_better"],
    ["RMSE", "Erro quadrático médio", 0.35, 0.40, "performance", "lower_better"],
    ["R2", "Coeficiente de determinação", 0.60, 0.50, "performance", "higher_better"],

    # Estabilidade
    ["PSI", "Population Stability Index", 0.10, 0.25, "stability", "lower_better"],

    # Default / IFRS9
    ["taxa_default_realizada", "Taxa de default realizada no mês", None, None, "default", "neutral"],
    ["taxa_default_estimada", "Taxa de default estimada pelo modelo", None, None, "default", "neutral"],
    ["vol_contratos", "Volume de contratos analisados no mês", 1000, 5000, "default", "neutral"],

    # Risco
    ["risk_score", "Score de risco médio do modelo", 0.02, 0.05, "risk", "lower_better"],
    ["risk_level", "Nível de risco categórico do modelo (low, medium, high)", None, None, "risk", "neutral"]
]

df_desc = pd.DataFrame(metrics_desc, columns=["metric_name","description","attention","alert","type","direction"])
df_desc.to_csv("metricas_descricao.csv", index=False)
print("metricas_descricao.csv criado com sucesso!")