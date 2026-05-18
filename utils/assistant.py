from __future__ import annotations

import math


def capability_text(metrics: dict, lang: str = "es") -> str:
    cpk = metrics.get("Cpk")
    if cpk is None or not isinstance(cpk, (int, float)) or math.isnan(cpk):
        return "No hay especificaciones suficientes para evaluar capacidad." if lang == "es" else "There are not enough specifications to assess capability."
    if cpk >= 1.33:
        return "Proceso capaz para operacion rutinaria; mantener monitoreo." if lang == "es" else "Capable process for routine operation; keep monitoring."
    if cpk >= 1.0:
        return "Capacidad marginal; conviene reducir variabilidad o recentrar." if lang == "es" else "Marginal capability; reduce variation or recenter the process."
    return "Proceso no capaz; revisar causa raiz, especificaciones o metodo de medicion." if lang == "es" else "Not capable; review root causes, specifications, or measurement method."


def ai_assistant_summary(stats: dict, control_alerts: list[str], capability_metrics: dict | None, normality: dict | None, lang: str = "es") -> list[str]:
    notes: list[str] = []
    if stats.get("count", 0) < 25:
        notes.append("La muestra es valida para explorar, pero para decisiones robustas conviene aumentar subgrupos." if lang == "es" else "The sample is useful for exploration, but more subgroups improve robust decisions.")
    if stats.get("cv") and stats["cv"] > 10:
        notes.append("El coeficiente de variacion es alto; investigue mezcla de lotes, calibracion o condiciones de proceso." if lang == "es" else "Coefficient of variation is high; check lot mixing, calibration, or process conditions.")
    if control_alerts:
        severe = [a for a in control_alerts if "fuera" in a.lower() or "outside" in a.lower()]
        notes.append(("Se detectan senales SPC que requieren contencion y analisis de causa raiz." if severe else "Hay patrones no aleatorios; vigile tendencia y estabilidad.") if lang == "es" else ("SPC signals require containment and root-cause analysis." if severe else "Non-random patterns detected; monitor trend and stability."))
    if capability_metrics:
        notes.append(capability_text(capability_metrics, lang))
    if normality and "Shapiro-Wilk" in normality:
        pvalue = normality["Shapiro-Wilk"].get("pvalue", 1)
        notes.append(("Normalidad aceptable por Shapiro-Wilk (p >= 0.05)." if pvalue >= 0.05 else "Los datos no parecen normales; interprete capacidad con cautela o transforme datos.") if lang == "es" else ("Normality is acceptable by Shapiro-Wilk (p >= 0.05)." if pvalue >= 0.05 else "Data does not look normal; interpret capability carefully or transform data."))
    return notes or (["No se observan riesgos estadisticos relevantes con los datos actuales."] if lang == "es" else ["No relevant statistical risks are observed with current data."])
