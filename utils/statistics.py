from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats


CONTROL_CONSTANTS = {
    2: {"A2": 1.880, "D3": 0.000, "D4": 3.267, "A3": 2.659, "B3": 0.000, "B4": 3.267},
    3: {"A2": 1.023, "D3": 0.000, "D4": 2.574, "A3": 1.954, "B3": 0.000, "B4": 2.568},
    4: {"A2": 0.729, "D3": 0.000, "D4": 2.282, "A3": 1.628, "B3": 0.000, "B4": 2.266},
    5: {"A2": 0.577, "D3": 0.000, "D4": 2.114, "A3": 1.427, "B3": 0.000, "B4": 2.089},
    6: {"A2": 0.483, "D3": 0.000, "D4": 2.004, "A3": 1.287, "B3": 0.030, "B4": 1.970},
    7: {"A2": 0.419, "D3": 0.076, "D4": 1.924, "A3": 1.182, "B3": 0.118, "B4": 1.882},
    8: {"A2": 0.373, "D3": 0.136, "D4": 1.864, "A3": 1.099, "B3": 0.185, "B4": 1.815},
    9: {"A2": 0.337, "D3": 0.184, "D4": 1.816, "A3": 1.032, "B3": 0.239, "B4": 1.761},
    10: {"A2": 0.308, "D3": 0.223, "D4": 1.777, "A3": 0.975, "B3": 0.284, "B4": 1.716},
}


def numeric_matrix(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    if "Subgrupo" in clean.columns:
        clean = clean.drop(columns=["Subgrupo"])
    return clean.apply(pd.to_numeric, errors="coerce").dropna(how="all")


def flatten_numeric(df: pd.DataFrame) -> pd.Series:
    values = numeric_matrix(df).to_numpy().ravel()
    values = values[~np.isnan(values)]
    return pd.Series(values, name="Valor")


def descriptive_stats(values: pd.Series) -> dict:
    values = pd.to_numeric(values, errors="coerce").dropna()
    mode = values.mode()
    return {
        "count": int(values.count()),
        "mean": float(values.mean()) if len(values) else np.nan,
        "median": float(values.median()) if len(values) else np.nan,
        "mode": float(mode.iloc[0]) if not mode.empty else np.nan,
        "variance": float(values.var(ddof=1)) if len(values) > 1 else np.nan,
        "std": float(values.std(ddof=1)) if len(values) > 1 else np.nan,
        "range": float(values.max() - values.min()) if len(values) else np.nan,
        "cv": float(values.std(ddof=1) / values.mean() * 100) if len(values) > 1 and values.mean() else np.nan,
        "min": float(values.min()) if len(values) else np.nan,
        "max": float(values.max()) if len(values) else np.nan,
    }


def xbar_r(df: pd.DataFrame, manual_limits: dict | None = None) -> pd.DataFrame:
    mat = numeric_matrix(df)
    n = int(mat.shape[1])
    means = mat.mean(axis=1)
    ranges = mat.max(axis=1) - mat.min(axis=1)
    xbarbar = means.mean()
    rbar = ranges.mean()
    c = CONTROL_CONSTANTS.get(n)
    if c:
        ucl_x, lcl_x = xbarbar + c["A2"] * rbar, xbarbar - c["A2"] * rbar
        ucl_r, lcl_r = c["D4"] * rbar, c["D3"] * rbar
    else:
        sigma = mat.stack().std(ddof=1) / math.sqrt(max(n, 1))
        ucl_x, lcl_x = xbarbar + 3 * sigma, xbarbar - 3 * sigma
        ucl_r, lcl_r = rbar + 3 * ranges.std(ddof=1), max(0, rbar - 3 * ranges.std(ddof=1))
    limits = {"ucl_x": ucl_x, "cl_x": xbarbar, "lcl_x": lcl_x, "ucl_r": ucl_r, "cl_r": rbar, "lcl_r": lcl_r}
    if manual_limits:
        limits.update({k: v for k, v in manual_limits.items() if v is not None})
    out = pd.DataFrame({"Subgrupo": range(1, len(means) + 1), "Xbar": means, "R": ranges})
    for k, v in limits.items():
        out[k] = v
    out["Fuera_Xbar"] = (out["Xbar"] > out["ucl_x"]) | (out["Xbar"] < out["lcl_x"])
    out["Fuera_R"] = (out["R"] > out["ucl_r"]) | (out["R"] < out["lcl_r"])
    return out


def xbar_s(df: pd.DataFrame, manual_limits: dict | None = None) -> pd.DataFrame:
    mat = numeric_matrix(df)
    n = int(mat.shape[1])
    means = mat.mean(axis=1)
    stds = mat.std(axis=1, ddof=1)
    xbarbar = means.mean()
    sbar = stds.mean()
    c = CONTROL_CONSTANTS.get(n)
    if c:
        ucl_x, lcl_x = xbarbar + c["A3"] * sbar, xbarbar - c["A3"] * sbar
        ucl_s, lcl_s = c["B4"] * sbar, c["B3"] * sbar
    else:
        sigma = mat.stack().std(ddof=1) / math.sqrt(max(n, 1))
        ucl_x, lcl_x = xbarbar + 3 * sigma, xbarbar - 3 * sigma
        ucl_s, lcl_s = sbar + 3 * stds.std(ddof=1), max(0, sbar - 3 * stds.std(ddof=1))
    limits = {"ucl_x": ucl_x, "cl_x": xbarbar, "lcl_x": lcl_x, "ucl_s": ucl_s, "cl_s": sbar, "lcl_s": lcl_s}
    if manual_limits:
        limits.update({k: v for k, v in manual_limits.items() if v is not None})
    out = pd.DataFrame({"Subgrupo": range(1, len(means) + 1), "Xbar": means, "S": stds})
    for k, v in limits.items():
        out[k] = v
    out["Fuera_Xbar"] = (out["Xbar"] > out["ucl_x"]) | (out["Xbar"] < out["lcl_x"])
    out["Fuera_S"] = (out["S"] > out["ucl_s"]) | (out["S"] < out["lcl_s"])
    return out


def attribute_chart(df: pd.DataFrame, chart: str, manual_limits: dict | None = None) -> pd.DataFrame:
    data = df.copy()
    for col in ["Inspeccionados", "Defectuosos", "Defectos"]:
        if col in data:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    n = data.get("Inspeccionados", pd.Series([1] * len(data), index=data.index)).replace(0, np.nan)
    if chart == "p":
        # p chart: fraction defective, variable limits when subgroup sizes vary.
        pbar = data["Defectuosos"].sum() / n.sum()
        center = data["Defectuosos"] / n
        cl = pbar
        sigma = np.sqrt(pbar * (1 - pbar) / n)
        metric = "p"
    elif chart == "np":
        # np chart: number of defectives, with constant subgroup size.
        pbar = data["Defectuosos"].sum() / n.sum()
        n_const = float(n.dropna().iloc[0])
        center = data["Defectuosos"]
        cl = n_const * pbar
        sigma = np.sqrt(n_const * pbar * (1 - pbar))
        metric = "np"
    elif chart == "c":
        # c chart: number of defects per constant inspection unit.
        cbar = data["Defectos"].mean()
        center = data["Defectos"]
        cl = cbar
        sigma = np.sqrt(cbar)
        metric = "c"
    else:
        # u chart: defects per unit, variable limits when inspection sizes vary.
        ubar = data["Defectos"].sum() / n.sum()
        center = data["Defectos"] / n
        cl = ubar
        sigma = np.sqrt(ubar / n)
        metric = "u"
    if isinstance(sigma, pd.Series):
        ucl = cl + 3 * sigma
        lcl = (cl - 3 * sigma).clip(lower=0) if isinstance(cl, pd.Series) else pd.Series(cl - 3 * sigma, index=data.index).clip(lower=0)
    else:
        ucl = cl + 3 * sigma
        lcl = max(0, cl - 3 * sigma)
    out = pd.DataFrame({"Subgrupo": data.get("Subgrupo", range(1, len(data) + 1)), metric: center, "CL": cl, "UCL": ucl, "LCL": lcl})
    if manual_limits:
        for key, val in manual_limits.items():
            if val is not None and key.upper() in ["UCL", "CL", "LCL"]:
                out[key.upper()] = val
    out["Fuera"] = (out[metric] > out["UCL"]) | (out[metric] < out["LCL"])
    return out


def western_electric(values: pd.Series, cl: float, ucl: float, lcl: float) -> list[str]:
    values = pd.to_numeric(values, errors="coerce").dropna().reset_index(drop=True)
    alerts: list[str] = []
    sigma = (ucl - cl) / 3 if ucl != cl else np.nan
    if not np.isfinite(sigma) or sigma <= 0:
        return ["Los limites no permiten estimar sigma; revise limites manuales."]
    outside = values[(values > ucl) | (values < lcl)].index + 1
    if len(outside):
        alerts.append(f"Puntos fuera de limites 3 sigma: {outside.tolist()}.")
    for i in range(len(values) - 2):
        window = values.iloc[i:i + 3]
        if (window > cl + 2 * sigma).sum() >= 2 or (window < cl - 2 * sigma).sum() >= 2:
            alerts.append(f"Regla 2 de 3 mas alla de 2 sigma cerca de subgrupo {i + 1}.")
    for i in range(len(values) - 4):
        window = values.iloc[i:i + 5]
        if (window > cl + sigma).sum() >= 4 or (window < cl - sigma).sum() >= 4:
            alerts.append(f"Regla 4 de 5 mas alla de 1 sigma cerca de subgrupo {i + 1}.")
    for i in range(len(values) - 7):
        window = values.iloc[i:i + 8]
        if (window > cl).all() or (window < cl).all():
            alerts.append(f"Corrida de 8 puntos del mismo lado desde subgrupo {i + 1}.")
    for i in range(len(values) - 5):
        diffs = np.diff(values.iloc[i:i + 6])
        if (diffs > 0).all() or (diffs < 0).all():
            alerts.append(f"Tendencia de 6 puntos desde subgrupo {i + 1}.")
    return alerts or ["No se detectan patrones Western Electric clasicos."]


def normality_tests(values: pd.Series) -> dict:
    values = pd.to_numeric(values, errors="coerce").dropna()
    out = {}
    if len(values) < 3:
        return {"error": "Se requieren al menos 3 datos."}
    sample = values.sample(5000, random_state=1) if len(values) > 5000 else values
    shapiro = stats.shapiro(sample)
    out["Shapiro-Wilk"] = {"statistic": float(shapiro.statistic), "pvalue": float(shapiro.pvalue)}
    standardized = (values - values.mean()) / values.std(ddof=1) if values.std(ddof=1) else values * 0
    ks = stats.kstest(standardized, "norm")
    out["Kolmogorov-Smirnov"] = {"statistic": float(ks.statistic), "pvalue": float(ks.pvalue)}
    ad = stats.anderson(values, dist="norm")
    out["Anderson-Darling"] = {"statistic": float(ad.statistic), "critical_5": float(ad.critical_values[2]), "normal_5pct": bool(ad.statistic < ad.critical_values[2])}
    return out


def capability(values: pd.Series, lsl: float | None, usl: float | None) -> dict:
    values = pd.to_numeric(values, errors="coerce").dropna()
    mean = values.mean()
    sigma = values.std(ddof=1)
    if not sigma or not np.isfinite(sigma):
        return {"error": "Variabilidad insuficiente para calcular capacidad."}
    cp = (usl - lsl) / (6 * sigma) if lsl is not None and usl is not None else np.nan
    cpu = (usl - mean) / (3 * sigma) if usl is not None else np.nan
    cpl = (mean - lsl) / (3 * sigma) if lsl is not None else np.nan
    cpk = np.nanmin([cpu, cpl]) if not (np.isnan(cpu) and np.isnan(cpl)) else np.nan
    pp = cp
    ppk = cpk
    return {"Cp": float(cp) if np.isfinite(cp) else np.nan, "Cpk": float(cpk) if np.isfinite(cpk) else np.nan, "Pp": float(pp) if np.isfinite(pp) else np.nan, "Ppk": float(ppk) if np.isfinite(ppk) else np.nan, "mean": float(mean), "sigma": float(sigma)}


def pareto_table(df: pd.DataFrame, category: str, frequency: str) -> pd.DataFrame:
    out = df[[category, frequency]].copy()
    out[frequency] = pd.to_numeric(out[frequency], errors="coerce").fillna(0)
    out = out.groupby(category, as_index=False)[frequency].sum().sort_values(frequency, ascending=False)
    total = out[frequency].sum()
    out["Porcentaje"] = out[frequency] / total * 100 if total else 0
    out["Acumulado"] = out["Porcentaje"].cumsum()
    return out
