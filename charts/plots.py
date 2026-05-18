from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats


BLUE = "#1f77b4"
NAVY = "#0b2545"
RED = "#ef4444"
GREEN = "#10b981"
ORANGE = "#f59e0b"


def control_chart(df: pd.DataFrame, metric: str, cl: str, ucl: str, lcl: str, title: str, lsl: float | None = None, usl: float | None = None) -> go.Figure:
    colors = np.where((df[metric] > df[ucl]) | (df[metric] < df[lcl]), RED, BLUE)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Subgrupo"], y=df[metric], mode="lines+markers", marker=dict(color=colors, size=9), line=dict(color=BLUE), name=metric))
    fig.add_trace(go.Scatter(x=df["Subgrupo"], y=df[ucl], mode="lines", line=dict(color=RED, dash="dash"), name="UCL"))
    fig.add_trace(go.Scatter(x=df["Subgrupo"], y=df[cl], mode="lines", line=dict(color=NAVY), name="CL"))
    fig.add_trace(go.Scatter(x=df["Subgrupo"], y=df[lcl], mode="lines", line=dict(color=RED, dash="dash"), name="LCL"))
    for val, label in [(usl, "LSE"), (lsl, "LIE")]:
        if val is not None and np.isfinite(val):
            fig.add_trace(go.Scatter(
                x=df["Subgrupo"],
                y=[val] * len(df),
                mode="lines",
                line=dict(color=GREEN, dash="dot", width=2),
                name=label,
            ))
    fig.update_layout(title=title, template="plotly_white", height=410, hovermode="x unified", margin=dict(l=20, r=20, t=55, b=20))
    fig.update_xaxes(title="Subgrupo", rangeslider_visible=True)
    return fig


def histogram_capability(values: pd.Series, lsl: float | None = None, usl: float | None = None) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=values, nbinsx=24, marker_color=BLUE, opacity=.75, name="Datos"))
    for val, label, color in [(lsl, "LSL", RED), (usl, "USL", RED), (values.mean(), "Media", NAVY)]:
        if val is not None and np.isfinite(val):
            fig.add_vline(x=val, line_color=color, line_dash="dash", annotation_text=label)
    fig.update_layout(template="plotly_white", title="Distribucion y especificaciones", height=390, bargap=.05)
    return fig


def normality_figure(values: pd.Series) -> go.Figure:
    values = pd.to_numeric(values, errors="coerce").dropna()
    osm, osr = stats.probplot(values, dist="norm", fit=False)
    slope, intercept, *_ = stats.linregress(osm, osr)
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Histograma", "Q-Q Plot"))
    fig.add_trace(go.Histogram(x=values, marker_color=BLUE, nbinsx=24), row=1, col=1)
    fig.add_trace(go.Scatter(x=osm, y=osr, mode="markers", marker_color=BLUE, name="Datos"), row=1, col=2)
    fig.add_trace(go.Scatter(x=osm, y=slope * np.array(osm) + intercept, mode="lines", line=dict(color=RED), name="Normal"), row=1, col=2)
    fig.update_layout(template="plotly_white", height=420, showlegend=False, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def pareto_chart(df: pd.DataFrame, category: str, frequency: str) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=df[category], y=df[frequency], marker_color=BLUE, name="Frecuencia", secondary_y=False)
    fig.add_scatter(x=df[category], y=df["Acumulado"], mode="lines+markers", marker_color=ORANGE, name="Acumulado %", secondary_y=True)
    fig.add_hline(y=80, line_dash="dot", line_color=RED, secondary_y=True)
    fig.update_layout(template="plotly_white", title="Diagrama de Pareto", height=430, hovermode="x unified")
    fig.update_yaxes(title_text="Frecuencia", secondary_y=False)
    fig.update_yaxes(title_text="% acumulado", range=[0, 105], secondary_y=True)
    return fig


def ishikawa_chart(effect: str, causes: dict[str, list[str]]) -> go.Figure:
    def wrap_text(text: str, width: int = 18) -> str:
        words = str(text).split()
        lines: list[str] = []
        current: list[str] = []
        for word in words:
            if sum(len(w) for w in current) + len(current) + len(word) > width:
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines.append(" ".join(current))
        return "<br>".join(lines[:2])

    fig = go.Figure()
    spine_color = "#08264a"
    teal = "#00a88f"
    spine_y = 0.50
    spine_start = 0.12
    spine_end = 0.84

    # Main body: tail, spine and head.
    fig.add_shape(type="line", x0=spine_start, y0=spine_y, x1=spine_end, y1=spine_y, line=dict(color=spine_color, width=5))
    fig.add_shape(type="path", path="M 0.07 0.50 L 0.12 0.60 L 0.12 0.40 Z", fillcolor=spine_color, line=dict(color=spine_color))
    fig.add_shape(type="path", path="M 0.84 0.50 L 0.91 0.62 L 0.98 0.50 L 0.91 0.38 Z", fillcolor=spine_color, line=dict(color=spine_color))
    fig.add_annotation(x=0.91, y=0.50, text=f"<b>Problema</b><br>{wrap_text(effect, 16)}", showarrow=False, font=dict(color="white", size=12), align="center")

    layout = [
        ("Materiales", 0.28, 0.74, -1),
        ("Maquinaria", 0.48, 0.74, -1),
        ("Metodos", 0.68, 0.74, -1),
        ("Mano de Obra", 0.28, 0.26, 1),
        ("Medio Ambiente", 0.48, 0.26, 1),
        ("Medicion", 0.68, 0.26, 1),
    ]

    for cat, anchor_x, label_y, side in layout:
        label_x = anchor_x - 0.095
        fig.add_shape(type="line", x0=anchor_x, y0=spine_y, x1=label_x, y1=label_y, line=dict(color=teal, width=3.2))
        fig.add_annotation(x=label_x, y=label_y + (0.055 if side < 0 else -0.055), text=f"<b>{cat}</b>", showarrow=False, bgcolor=teal, font=dict(color="white", size=12), borderpad=7)

        cat_causes = causes.get(cat, [])[:4]
        if not cat_causes:
            cat_causes = ["Causa"]
        for j, cause in enumerate(cat_causes):
            # Ribs stay inside the canvas and point into the main branch.
            t = 0.30 + j * 0.15
            branch_x = anchor_x + (label_x - anchor_x) * t
            branch_y = spine_y + (label_y - spine_y) * t
            rib_start_x = max(0.08, branch_x - 0.13)
            rib_start_y = branch_y + (0.035 if side < 0 else -0.035)
            fig.add_shape(type="line", x0=rib_start_x, y0=rib_start_y, x1=branch_x, y1=branch_y, line=dict(color=teal, width=1.8))
            fig.add_annotation(
                x=(rib_start_x + branch_x) / 2,
                y=rib_start_y + (0.028 if side < 0 else -0.028),
                text=wrap_text(cause, 18),
                showarrow=False,
                align="center",
                font=dict(size=10.5, color="#172033"),
            )

    fig.update_layout(
        template="plotly_white",
        height=520,
        margin=dict(l=25, r=25, t=20, b=20),
        xaxis=dict(visible=False, range=[0, 1]),
        yaxis=dict(visible=False, range=[0, 1]),
        autosize=True,
    )
    return fig
