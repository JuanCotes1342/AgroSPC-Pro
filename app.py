from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from charts.plots import control_chart, histogram_capability, normality_figure, pareto_chart
from charts.ishikawa_svg import ishikawa_html, ishikawa_svg
from components.ui import apply_theme, hero, kpi_card, page_header, status_box
from database.db import dataframe_from_json, dataframe_to_json, delete_analysis, init_db, list_analyses, load_analysis, save_temp_analysis
from reports.exporters import csv_bytes, excel_bytes, pdf_report
from utils.ai_client import deepseek_available, gemini_available, generate_text
from utils.assistant import ai_assistant_summary, capability_text
from utils.catalog import (
    NORMATIVES,
    all_products,
    attributes_dataframe,
    catalog_dataframe,
    recommend_chart,
    product_description,
    attributes_for_product,
    product_type_for,
    unit_for_variable,
    suggest_for_product,
    variables_dataframe,
)
from utils.i18n import t
from utils.sample_data import attribute_example, pareto_example, variable_example
from utils.statistics import (
    attribute_chart,
    capability,
    descriptive_stats,
    flatten_numeric,
    normality_tests,
    pareto_table,
    western_electric,
    xbar_r,
    xbar_s,
)


def init_state() -> None:
    st.session_state.setdefault("lang", "es")
    st.session_state.setdefault("page", "home")
    st.session_state.setdefault("ui_theme", "Light")
    st.session_state.setdefault("auto_rerun", False)
    st.session_state.setdefault("gemini_api_key", "")
    st.session_state.setdefault("session_code", "demo-agrospc")
    st.session_state.setdefault("show_spec_limits", True)
    st.session_state.setdefault("variable_df", variable_example(30, 15))
    st.session_state.setdefault("attribute_df", attribute_example(25))
    st.session_state.setdefault("pareto_df", pareto_example())
    st.session_state.setdefault("ishikawa_effect", "Golpes y Magulladuras")
    st.session_state.setdefault("ishikawa_causes", {
        "Mano de Obra": ["Falta de capacitacion", "Fatiga del personal", "Manipulacion incorrecta"],
        "Metodos": ["Procedimientos desactualizados", "Inspeccion inadecuada", "Almacenamiento incorrecto"],
        "Maquinaria": ["Calibracion incorrecta", "Mantenimiento preventivo", "Velocidad excesiva"],
        "Materiales": ["Calidad de materia prima", "Embalaje defectuoso", "Variedad sensible"],
        "Medio Ambiente": ["Temperatura alta", "Humedad elevada", "Contaminacion cruzada"],
        "Medicion": ["Instrumento sin calibrar", "Muestreo insuficiente", "Registro incompleto"],
    })
    st.session_state.setdefault("metadata", {
        "Producto": "Arandano fresco",
        "Tipo": "Fruta",
        "Variable": "Grados Brix",
        "Unidad": "°Brix",
        "Analista": "Calidad",
        "Lote": "L-001",
        "LIE": 11.5,
        "LSE": 13.5,
        "Fecha": str(date.today()),
        "Hora": datetime.now().strftime("%H:%M"),
        "Observaciones": "Datos demostrativos editables.",
    })
    go_to = st.query_params.get("go")
    valid_pages = {"home", "data_entry", "variables", "attributes", "capability", "pareto", "normality", "catalog", "reports", "export", "settings"}
    if go_to in valid_pages:
        st.session_state.page = go_to
        st.query_params.clear()


def sidebar() -> str:
    lang = st.session_state.lang
    logo_path = Path(__file__).resolve().parent / "logo imagen.png"
    brand_cols = st.sidebar.columns([0.24, 0.76], vertical_alignment="center")
    if logo_path.exists():
        brand_cols[0].image(str(logo_path), use_container_width=True)
    else:
        brand_cols[0].markdown("<div class='brand-logo'>🌿</div>", unsafe_allow_html=True)
    brand_cols[1].markdown("<div class='brand-name'>AgroSPC Pro</div>", unsafe_allow_html=True)

    def nav_button(label: str, page_key: str) -> None:
        active = st.session_state.page == page_key
        if st.sidebar.button(label, key=f"nav_{page_key}", type="primary" if active else "secondary"):
            st.session_state.page = page_key
            st.rerun()

    st.sidebar.markdown(f"<div class='side-section'>{'Espacio de trabajo' if lang == 'es' else 'Workspace'}</div>", unsafe_allow_html=True)
    nav_button("🏠  Inicio", "home")
    nav_button(f"📝  {t('data_entry', lang)}", "data_entry")
    nav_button(f"📈  {t('variables', lang)}", "variables")
    nav_button(f"✅  {t('attributes', lang)}", "attributes")
    nav_button(f"🎯  {t('capability', lang)}", "capability")
    nav_button(f"📊  {t('pareto', lang)}", "pareto")
    nav_button(f"🔎  {t('normality', lang)}", "normality")
    nav_button(f"🌿  {t('catalog', lang)}", "catalog")

    st.sidebar.markdown(f"<div class='side-section'>{'Salidas' if lang == 'es' else 'Outputs'}</div>", unsafe_allow_html=True)
    nav_button(f"📄  {t('reports', lang)}", "reports")
    nav_button(f"⬇️  {t('export', lang)}", "export")
    nav_button(f"⚙️  {t('settings', lang)}", "settings")

    st.sidebar.markdown(
        f"<div class='side-card'>{'Asistente IA basado en reglas SPC, normalidad y capacidad.' if lang == 'es' else 'AI assistant based on SPC, normality and capability rules.'}</div>",
        unsafe_allow_html=True,
    )
    return st.session_state.page


def metadata_form() -> dict:
    lang = st.session_state.lang
    md = st.session_state.metadata.copy()
    with st.expander("Trazabilidad" if lang == "es" else "Traceability", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        custom_label = "Escribir otro" if lang == "es" else "Write another"
        product_options = all_products() + [custom_label]
        current_product = md.get("Producto", "")
        product_index = product_options.index(current_product) if current_product in product_options else len(product_options) - 1
        selected_product = c1.selectbox(t("product", lang), product_options, index=product_index)
        if selected_product == custom_label:
            md["Producto"] = c1.text_input("Producto personalizado" if lang == "es" else "Custom product", current_product if current_product not in product_options else "")
            detected_type = None
        else:
            md["Producto"] = selected_product
            detected_type = product_type_for(selected_product)
        type_options = ["Fruta", "Hortaliza", "Planta medicinal", "Otro"]
        if detected_type:
            md["Tipo"] = detected_type
            c2.text_input(t("product_type", lang), md["Tipo"], disabled=True)
        else:
            md["Tipo"] = c2.selectbox(t("product_type", lang), type_options, index=type_options.index(md.get("Tipo", "Otro")) if md.get("Tipo") in type_options else 3)
        suggestions = suggest_for_product(md["Producto"])
        custom_feature_label = "Escribir otra" if lang == "es" else "Write another"
        feature_options = suggestions + [custom_feature_label]
        selected_feature = c3.selectbox("Variable sugerida" if lang == "es" else "Suggested feature", feature_options)
        if selected_feature == custom_feature_label:
            md["Variable"] = c3.text_input(t("variable", lang), md.get("Variable", ""))
            suggested_unit = None
        else:
            md["Variable"] = selected_feature
            suggested_unit = unit_for_variable(selected_feature)
        if suggested_unit:
            md["Unidad"] = suggested_unit
            c4.text_input(t("unit", lang), md["Unidad"], disabled=True)
        else:
            md["Unidad"] = c4.text_input(t("unit", lang), md.get("Unidad", ""))
        c5, c6, c7, c8 = st.columns(4)
        md["Analista"] = c5.text_input(t("analyst", lang), md.get("Analista", ""))
        md["Lote"] = c6.text_input(t("lot", lang), md.get("Lote", ""))
        md["LIE"] = c7.number_input(t("lsl", lang), value=float(md.get("LIE", 0.0)), step=0.1)
        md["LSE"] = c8.number_input(t("usl", lang), value=float(md.get("LSE", 1.0)), step=0.1)
        md["Observaciones"] = st.text_area("Observaciones" if lang == "es" else "Notes", md.get("Observaciones", ""), height=80)
        st.info(("Recomendacion del asistente: " if lang == "es" else "Assistant recommendation: ") + recommend_chart(md.get("Variable", ""), md.get("Tipo", "")))
    st.session_state.metadata = md
    return md


def page_home() -> None:
    lang = st.session_state.lang
    if lang == "es":
        title = "Control Estadistico de Procesos<br>para la Agroindustria"
        subtitle = "AgroSPC Pro integra cartas de control, capacidad, normalidad, Pareto, Ishikawa e IA para monitorear calidad en frutas, hortalizas y plantas medicinales."
        benefits_title = "Beneficios Clave de AgroSPC Pro"
        cards = [
            ("📈", "Cartas SPC en tiempo real", "Visualiza estabilidad, senales fuera de control y limites de especificacion."),
            ("📄", "Reportes automaticos de calidad", "Genera informes, conclusiones, recomendaciones y soporte para sustentacion."),
            ("🎯", "Analisis y reduccion de defectos", "Integra Pareto e Ishikawa para encontrar causas raiz y priorizar acciones."),
        ]
        start_label = "Comenzar"
        learn_label = "Aprender mas"
    else:
        title = "Statistical Process Control<br>for the Agro-Industry"
        subtitle = "AgroSPC Pro integrates control charts, capability, normality, Pareto, Ishikawa and AI to monitor quality in fruits, vegetables and medicinal plants."
        benefits_title = "Key Benefits of AgroSPC Pro"
        cards = [
            ("📈", "Real-time SPC Charts", "Visualize stability, out-of-control signals and specification limits."),
            ("📄", "Automated Quality Reports", "Generate reports, conclusions, recommendations and presentation support."),
            ("🎯", "Defect Analysis & Reduction", "Use Pareto and Ishikawa to find root causes and prioritize actions."),
        ]
        start_label = "Get Started"
        learn_label = "Learn More"

    st.markdown(
        f"""
        <div class="home-shell">
            <div class="home-hero">
                <div>
                    <h1>{title}</h1>
                    <p>{subtitle}</p>
                    <div class="home-actions">
                        <a class="home-btn primary" href="?go=data_entry" target="_self">{start_label}</a>
                        <a class="home-btn" href="#learn-more">{learn_label}</a>
                    </div>
                </div>
            </div>
            <div class="benefits">
                <h2>{benefits_title}</h2>
                <div class="benefit-grid">
                    <div class="benefit-card"><div class="benefit-icon">{cards[0][0]}</div><b>{cards[0][1]}</b><p>{cards[0][2]}</p></div>
                    <div class="benefit-card"><div class="benefit-icon">{cards[1][0]}</div><b>{cards[1][1]}</b><p>{cards[1][2]}</p></div>
                    <div class="benefit-card"><div class="benefit-icon">{cards[2][0]}</div><b>{cards[2][1]}</b><p>{cards[2][2]}</p></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if lang == "es":
        st.markdown("""
        <div id="learn-more" class="learn-card">
          <h3>Control estadistico en agroindustria</h3>
          <p>El Control Estadistico de Procesos permite verificar si una operacion agricola o poscosecha se mantiene estable, si cumple especificaciones y si los defectos se concentran en pocas causas importantes.</p>
          <div class="learn-grid">
            <div class="learn-item"><b>Xbar-R / Xbar-S</b><p>Controlan variables continuas como peso, pH, Brix, humedad, firmeza o principios activos.</p></div>
            <div class="learn-item"><b>p / np</b><p>Analizan unidades defectuosas: frutos no conformes, plagas, lotes rechazados.</p></div>
            <div class="learn-item"><b>c / u</b><p>Analizan defectos: golpes, manchas, hongos, impurezas o danos mecanicos.</p></div>
            <div class="learn-item"><b>Pareto</b><p>Prioriza los defectos de mayor impacto para enfocar acciones de mejora.</p></div>
            <div class="learn-item"><b>Ishikawa 6M</b><p>Organiza causas raiz en Metodo, Mano de obra, Maquinaria, Materiales, Medio ambiente y Medicion.</p></div>
            <div class="learn-item"><b>Capacidad y normalidad</b><p>Evalua si el proceso cumple especificaciones y si los datos soportan interpretaciones estadisticas.</p></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div id="learn-more" class="learn-card">
          <h3>Statistical process control in agroindustry</h3>
          <p>Statistical Process Control helps verify whether agricultural or post-harvest operations remain stable, meet specifications and concentrate defects in a few major causes.</p>
          <div class="learn-grid">
            <div class="learn-item"><b>Xbar-R / Xbar-S</b><p>Monitor continuous variables such as weight, pH, Brix, moisture, firmness or active compounds.</p></div>
            <div class="learn-item"><b>p / np</b><p>Analyze defective units: nonconforming fruits, pests or rejected lots.</p></div>
            <div class="learn-item"><b>c / u</b><p>Analyze defects: bruises, stains, fungi, impurities or mechanical damage.</p></div>
            <div class="learn-item"><b>Pareto</b><p>Prioritizes the highest-impact defects to focus improvement actions.</p></div>
            <div class="learn-item"><b>Ishikawa 6M</b><p>Organizes root causes into Method, Manpower, Machine, Material, Environment and Measurement.</p></div>
            <div class="learn-item"><b>Capability and normality</b><p>Evaluates whether the process meets specifications and whether data supports statistical interpretation.</p></div>
          </div>
        </div>
        """, unsafe_allow_html=True)


def ensure_min_subgroups(df: pd.DataFrame, context: str) -> bool:
    if len(df) < 25:
        st.error(f"{context}: se requieren minimo 25 subgrupos para cumplir la rubrica. Actualmente hay {len(df)}.")
        st.info("Agrega filas en Registro de datos o usa Cargar ejemplo para completar al menos 25 subgrupos.")
        return False
    return True


@st.cache_data(show_spinner=False)
def cached_xbar_r(df: pd.DataFrame) -> pd.DataFrame:
    return xbar_r(df)


@st.cache_data(show_spinner=False)
def cached_xbar_s(df: pd.DataFrame) -> pd.DataFrame:
    return xbar_s(df)


@st.cache_data(show_spinner=False)
def cached_descriptive(values: tuple[float, ...]) -> dict:
    return descriptive_stats(pd.Series(values))


def values_cache_key(values: pd.Series) -> tuple[float, ...]:
    return tuple(pd.to_numeric(values, errors="coerce").dropna().round(8).tolist())


def spec_limits() -> tuple[float | None, float | None]:
    lsl = st.session_state.metadata.get("LIE")
    usl = st.session_state.metadata.get("LSE")
    try:
        lsl_f = float(lsl)
        usl_f = float(usl)
    except (TypeError, ValueError):
        return None, None
    if lsl_f == 0 and usl_f == 0:
        return None, None
    return lsl_f, usl_f


def spec_violations(values: pd.Series, lsl: float | None, usl: float | None) -> int:
    values = pd.to_numeric(values, errors="coerce").dropna()
    if lsl is None and usl is None:
        return 0
    mask = pd.Series(False, index=values.index)
    if lsl is not None:
        mask = mask | (values < lsl)
    if usl is not None:
        mask = mask | (values > usl)
    return int(mask.sum())


def specification_note(count: int, unit: str = "") -> str:
    if count <= 0:
        return "Sin puntos fuera de especificacion."
    suffix = f" {unit}" if unit else ""
    return f"{count} punto(s) fuera de LIE/LSE{suffix}. Esto indica incumplimiento de especificacion aunque el proceso pueda estar estadisticamente estable."


def variable_specification_note(subgroup_count: int, measurement_count: int, unit: str = "") -> str:
    if subgroup_count <= 0 and measurement_count <= 0:
        return "Sin puntos ni mediciones fuera de especificacion."
    suffix = f" {unit}" if unit else ""
    return f"{subgroup_count} media(s) de subgrupo y {measurement_count} medicion(es) individuales fuera de LIE/LSE{suffix}. Esto indica incumplimiento de especificacion aunque el proceso pueda estar estadisticamente estable."


def current_analysis_payload() -> dict:
    return {
        "metadata": st.session_state.metadata,
        "variable_df": dataframe_to_json(st.session_state.variable_df),
        "attribute_df": dataframe_to_json(st.session_state.attribute_df),
        "pareto_df": dataframe_to_json(st.session_state.pareto_df),
        "ishikawa_effect": st.session_state.ishikawa_effect,
        "ishikawa_causes": st.session_state.ishikawa_causes,
    }


def restore_analysis_payload(payload: dict) -> None:
    st.session_state.metadata = payload.get("metadata", st.session_state.metadata)
    st.session_state.variable_df = dataframe_from_json(payload.get("variable_df", "[]"))
    st.session_state.attribute_df = dataframe_from_json(payload.get("attribute_df", "[]"))
    st.session_state.pareto_df = dataframe_from_json(payload.get("pareto_df", "[]"))
    st.session_state.ishikawa_effect = payload.get("ishikawa_effect", st.session_state.ishikawa_effect)
    st.session_state.ishikawa_causes = payload.get("ishikawa_causes", st.session_state.ishikawa_causes)


def upload_dataframe(key: str) -> None:
    lang = st.session_state.lang
    uploaded = st.file_uploader("Importar Excel/CSV" if lang == "es" else "Import Excel/CSV", type=["xlsx", "csv"], key=f"upload_{key}")
    if uploaded:
        try:
            df = read_uploaded_table(uploaded, key)
            st.session_state[key] = df
            st.success("Archivo importado." if lang == "es" else "File imported.")
        except Exception as exc:
            st.error(f"Error: {exc}")


def has_valid_headers(df: pd.DataFrame) -> bool:
    cols = [str(col).strip() for col in df.columns]
    if any(col.startswith("Unnamed") for col in cols):
        return False
    numeric_like = 0
    for col in cols:
        try:
            float(col)
            numeric_like += 1
        except ValueError:
            pass
    return numeric_like < max(1, len(cols) // 2)


def default_columns(width: int, key: str) -> list[str]:
    if key == "attribute_df":
        base = ["Subgrupo", "Inspeccionados", "Defectuosos", "Defectos"]
        return base[:width] + [f"A{i}" for i in range(1, max(0, width - len(base)) + 1)]
    return ["Subgrupo"] + [f"M{i}" for i in range(1, width)]


def read_uploaded_table(uploaded, key: str) -> pd.DataFrame:
    uploaded.seek(0)
    raw = pd.read_csv(uploaded, header=None) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded, header=None)
    first_row = raw.iloc[0].astype(str).str.strip().tolist() if not raw.empty else []
    numeric_first_row = 0
    blank_first_row = 0
    for value in first_row:
        if value == "" or value.lower() == "nan":
            blank_first_row += 1
            continue
        try:
            float(value)
            numeric_first_row += 1
        except ValueError:
            pass
    has_header = bool(first_row) and numeric_first_row < max(1, (len(first_row) - blank_first_row) // 2)
    if has_header:
        df = raw.iloc[1:].reset_index(drop=True)
        df.columns = [str(col).strip() if str(col).strip() and str(col).lower() != "nan" else f"Col{i+1}" for i, col in enumerate(raw.iloc[0].tolist())]
    else:
        df = raw
        df.columns = default_columns(len(df.columns), key)
    if "Subgrupo" not in df.columns:
        df.insert(0, "Subgrupo", range(1, len(df) + 1))
    else:
        df["Subgrupo"] = pd.to_numeric(df["Subgrupo"], errors="coerce").fillna(pd.Series(range(1, len(df) + 1))).astype(int)
    return df


def quick_paste_panel(key: str) -> None:
    lang = st.session_state.lang
    with st.expander("Carga rapida / pegar desde Excel" if lang == "es" else "Quick load / paste from Excel"):
        st.caption("Pega un bloque copiado de Excel. Si no trae encabezados, se asignan automaticamente: Subgrupo, M1, M2..." if lang == "es" else "Paste a block copied from Excel. If it has no headers, default names are assigned automatically.")
        raw = st.text_area("Datos pegados" if lang == "es" else "Pasted data", height=140, key=f"paste_{key}")
        c1, c2, c3 = st.columns(3)
        has_header = c1.checkbox("Primera fila tiene titulos" if lang == "es" else "First row has headers", value=False, key=f"paste_header_{key}")
        rows = c2.number_input("Filas blanco" if lang == "es" else "Blank rows", 1, 1000, 30, key=f"blank_rows_{key}")
        cols = c3.number_input("Columnas blanco" if lang == "es" else "Blank columns", 2, 100, 16 if key == "variable_df" else 4, key=f"blank_cols_{key}")
        b1, b2 = st.columns(2)
        if b1.button("Aplicar datos pegados" if lang == "es" else "Apply pasted data", key=f"apply_paste_{key}") and raw.strip():
            lines = [line for line in raw.strip().splitlines() if line.strip()]
            parsed = [line.split("\t") if "\t" in line else line.split(",") for line in lines]
            if has_header:
                df = pd.DataFrame(parsed[1:], columns=[str(x).strip() for x in parsed[0]])
            else:
                df = pd.DataFrame(parsed)
                df.columns = default_columns(len(df.columns), key)
            if not has_header:
                df.columns = default_columns(len(df.columns), key)
            if "Subgrupo" not in df.columns:
                df.insert(0, "Subgrupo", range(1, len(df) + 1))
            st.session_state[key] = df.apply(pd.to_numeric, errors="ignore")
            st.success("Datos pegados cargados." if lang == "es" else "Pasted data loaded.")
            st.rerun()
        if b2.button("Crear hoja en blanco" if lang == "es" else "Create blank sheet", key=f"blank_{key}"):
            df = pd.DataFrame(columns=default_columns(int(cols), key), index=range(int(rows)))
            df["Subgrupo"] = range(1, int(rows) + 1)
            st.session_state[key] = df
            st.rerun()


def data_schema_help() -> None:
    with st.expander("Como deben estar estructurados los datos y que graficos se generan", expanded=True):
        tab1, tab2 = st.tabs(["Variables continuas", "Atributos"])
        with tab1:
            st.markdown("""
            Para cartas **Xbar-R** y **Xbar-S**, cada fila debe ser un subgrupo y cada columna una medicion del subgrupo.

            Si el archivo no trae titulos, la app asigna automaticamente: `Subgrupo`, `M1`, `M2`, `M3`...
            """)
            st.dataframe(pd.DataFrame({
                "Subgrupo": [1, 2, 3],
                "M1": [12.1, 12.4, 12.3],
                "M2": [12.2, 12.5, 12.1],
                "M3": [12.0, 12.6, 12.2],
            }), use_container_width=True, hide_index=True)
            st.info("Con este formato puedes generar: Xbar-R, Xbar-S, normalidad, capacidad Cp/Cpk/Pp/Ppk y dashboard.")
        with tab2:
            st.markdown("""
            Para atributos, la estructura depende del grafico:

            `p`: requiere `Inspeccionados` y `Defectuosos`.

            `np`: requiere `Inspeccionados` y `Defectuosos`; funciona mejor si el tamano inspeccionado es constante.

            `c`: requiere `Defectos`.

            `u`: requiere `Inspeccionados` y `Defectos`.
            """)
            st.dataframe(pd.DataFrame({
                "Subgrupo": [1, 2, 3],
                "Inspeccionados": [400, 400, 400],
                "Defectuosos": [12, 18, 9],
                "Defectos": [15, 22, 11],
            }), use_container_width=True, hide_index=True)
            st.warning("Si subiste columnas con otros nombres, ve a Control por atributos y usa el mapeador de columnas para indicar que significa cada columna.")


def spreadsheet(key: str, default_cols: int = 5) -> pd.DataFrame:
    lang = st.session_state.lang
    quick_paste_panel(key)
    df = st.session_state[key].copy()
    c1, c2, c3, c4, c5 = st.columns(5)
    add_rows = c1.number_input("Filas a agregar" if lang == "es" else "Rows to add", 1, 1000, 5, key=f"rows_{key}")
    if c1.button("Agregar filas" if lang == "es" else "Add rows", key=f"add_rows_{key}"):
        start = len(df) + 1
        extra = pd.DataFrame({col: [np.nan] * add_rows for col in df.columns})
        if "Subgrupo" in extra:
            extra["Subgrupo"] = range(start, start + add_rows)
        df = pd.concat([df, extra], ignore_index=True)
    remove_rows = c2.number_input("Filas a eliminar" if lang == "es" else "Rows to remove", 1, max(len(df), 1), 1, key=f"rem_{key}")
    if c2.button("Eliminar ultimas" if lang == "es" else "Remove last", key=f"remove_{key}"):
        df = df.iloc[:-remove_rows] if remove_rows < len(df) else df.iloc[:0]
    if c3.button("Agregar columna" if lang == "es" else "Add column", key=f"add_col_{key}"):
        base = "M" if key == "variable_df" else "Nueva"
        idx = sum(str(col).startswith(base) for col in df.columns) + 1
        df[f"{base}{idx}"] = np.nan
    if c4.button(t("load_example", lang), key=f"example_{key}"):
        df = variable_example(30, default_cols) if key == "variable_df" else attribute_example(30)
    if c5.button("Eliminar hoja actual" if lang == "es" else "Clear current sheet", key=f"clear_{key}"):
        df = pd.DataFrame(columns=df.columns)
    st.session_state[key] = df
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, height=430, key=f"editor_{key}")
    st.session_state[key] = edited
    return edited


def compute_variable(chart_type: str, manual: bool = False) -> pd.DataFrame:
    if not ensure_min_subgroups(st.session_state.variable_df, "Control por variables"):
        st.stop()
    manual_limits = None
    if manual:
        st.caption("Limites manuales opcionales para Xbar y dispersion." if st.session_state.lang == "es" else "Optional manual limits for Xbar and dispersion.")
        c1, c2, c3 = st.columns(3)
        manual_limits = {"ucl_x": c1.number_input("UCL Xbar", value=np.nan), "cl_x": c2.number_input("CL Xbar", value=np.nan), "lcl_x": c3.number_input("LCL Xbar", value=np.nan)}
        manual_limits = {k: (None if np.isnan(v) else v) for k, v in manual_limits.items()}
    if manual:
        return xbar_s(st.session_state.variable_df, manual_limits) if chart_type == "Xbar-S" else xbar_r(st.session_state.variable_df, manual_limits)
    return cached_xbar_s(st.session_state.variable_df) if chart_type == "Xbar-S" else cached_xbar_r(st.session_state.variable_df)


def show_assistant(stats_dict: dict, alerts: list[str], cap: dict | None = None, norm: dict | None = None) -> None:
    lang = st.session_state.lang
    with st.container(border=True):
        st.subheader(t("assistant", lang))
        for note in ai_assistant_summary(stats_dict, alerts, cap, norm, lang):
            st.write(f"• {note}")
        if st.button("Analisis avanzado con IA" if lang == "es" else "Advanced AI analysis", key=f"ai_{st.session_state.page}"):
            prompt = f"""
Actua como experto senior en control estadistico de procesos agroindustriales.
Idioma: {'espanol' if lang == 'es' else 'english'}.
Producto y trazabilidad: {st.session_state.metadata}.
Estadistica descriptiva: {stats_dict}.
Nota de conteo: en cartas de control, subgrupos/puntos del grafico son filas evaluadas; mediciones totales es el total de datos individuales usados para estadistica descriptiva. No confundas ambos conteos.
Alertas Western Electric: {alerts}.
Capacidad: {cap}.
Normalidad: {norm}.
Entrega: diagnostico, grafico recomendado, posibles causas, validacion de limites, acciones correctivas y recomendaciones ejecutivas.
"""
            fallback = "\n".join(ai_assistant_summary(stats_dict, alerts, cap, norm, lang))
            text, source = generate_text(prompt, fallback)
            st.caption(f"Fuente: {source}")
            st.markdown(text)


def page_catalog() -> None:
    lang = st.session_state.lang
    hero(t("catalog", lang), "Monitoreo y analisis de calidad por producto agroindustrial." if lang == "es" else "Quality monitoring and analysis by agroindustrial product.")

    products = {
        "Plantas Medicinales": [
            ("Sabila (Aloe vera)", "Aloe vera", "🌿"), ("Manzanilla", "Matricaria chamomilla", "🌼"),
            ("Menta", "Mentha piperita", "🍃"), ("Calendula", "Calendula officinalis", "🌻"),
            ("Toronjil (Melisa)", "Melissa officinalis", "🌱"), ("Valeriana", "Valeriana officinalis", "🌾"),
            ("Hierbabuena", "Mentha spicata", "☘️"), ("Limoncillo", "Cymbopogon citratus", "🌾"),
            ("Romero", "Rosmarinus officinalis", "🌲"), ("Eucalipto", "Eucalyptus globulus", "🌳"),
            ("Cilantro", "Coriandrum sativum", "🌿"), ("Aji topito", "Capsicum frutescens", "🌶️"),
        ],
        "Frutas y Hortalizas": [
            ("Mango", "Mangifera indica", "🥭"), ("Aguacate", "Persea americana", "🥑"),
            ("Banano", "Musa paradisiaca", "🍌"), ("Melon", "Cucumis melo", "🍈"),
            ("Papaya", "Carica papaya", "🍈"), ("Pina", "Ananas comosus", "🍍"),
            ("Naranja", "Citrus sinensis", "🍊"), ("Fresa", "Fragaria", "🍓"),
            ("Tomate", "Solanum lycopersicum", "🍅"), ("Zanahoria", "Daucus carota", "🥕"),
            ("Lechuga", "Lactuca sativa", "🥬"), ("Pepino", "Cucumis sativus", "🥒"),
        ],
    }

    st.markdown("<div class='catalog-shell'>", unsafe_allow_html=True)
    st.markdown("<div class='catalog-hint'>Seleccione un producto para ver sus variables y atributos de calidad especificos.</div>", unsafe_allow_html=True)
    selected_product = None
    selected_icon = None
    selected_scientific = None
    for section, items in products.items():
        st.markdown(f"<div class='catalog-title'>{section}</div>", unsafe_allow_html=True)
        cols = st.columns(4)
        for idx, (name, scientific, icon) in enumerate(items):
            with cols[idx % 4]:
                st.markdown(
                    f"""
                    <div class='product-card'>
                        <div class='product-icon'>{icon}</div>
                        <div class='product-name'>{name}</div>
                        <div class='product-scientific'>{scientific}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Ver detalle", key=f"catalog_{name}", use_container_width=True):
                    selected_product = name
                    st.session_state.catalog_icon = icon
                    st.session_state.catalog_scientific = scientific
    st.markdown("</div>", unsafe_allow_html=True)

    selected_product = selected_product or st.session_state.get("catalog_selected")
    if selected_product:
        st.session_state.catalog_selected = selected_product
        selected_icon = st.session_state.get("catalog_icon", "🌿")
        selected_scientific = st.session_state.get("catalog_scientific", "Producto agroindustrial")
        suggestions = suggest_for_product(selected_product)
        attrs = attributes_for_product(selected_product)
        chips = "".join([f"<span class='quality-chip'>{item}</span>" for item in suggestions])
        attr_cards = "".join([
            f"<div class='mini-card'><strong>{row['Atributo']}</strong><span>{row['Evaluacion']} · {row['Herramienta']}</span><span>{row['Descripcion']}</span></div>"
            for _, row in attrs.iterrows()
        ])
        st.markdown(
            f"""
            <div class='detail-panel'>
                <div class='detail-head'>
                    <div class='detail-icon'>{selected_icon}</div>
                    <div>
                        <div class='detail-title'>Detalle de calidad: {selected_product}</div>
                        <div class='detail-subtitle'>{selected_scientific}</div>
                    </div>
                </div>
                <div class='detail-desc'>{product_description(selected_product)}</div>
                <div class='context-label'>Variables sugeridas</div>
                <div class='chip-wrap'>{chips}</div>
                <div class='context-label'>Atributos frecuentes de control</div>
                <div class='mini-card-grid'>{attr_cards}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("Ver recomendacion tecnica de graficos"):
            st.dataframe(pd.DataFrame({"Variable": suggestions, "Grafico recomendado": [recommend_chart(v, "continua") for v in suggestions]}), use_container_width=True, hide_index=True)
        if st.button("Usar este producto en Registro de datos", type="primary"):
            st.session_state.metadata["Producto"] = selected_product
            st.session_state.metadata["Variable"] = suggestions[0] if suggestions else st.session_state.metadata.get("Variable", "")
            st.session_state.page = "data_entry"
            st.rerun()

    with st.expander("Ver catalogo tecnico completo"):
        tab1, tab2, tab3, tab4 = st.tabs(["Productos", "Variables continuas", "Atributos", "Normativas"])
        with tab1:
            st.dataframe(catalog_dataframe(), use_container_width=True, height=360)
        with tab2:
            st.dataframe(variables_dataframe(), use_container_width=True, height=360)
        with tab3:
            st.dataframe(attributes_dataframe(), use_container_width=True, height=360)
        with tab4:
            st.dataframe(pd.DataFrame({"Normativa": NORMATIVES}), use_container_width=True)


def page_dashboard() -> None:
    lang = st.session_state.lang
    hero(t("app_title", lang), "Dashboard ejecutivo para calidad, estabilidad y capacidad de procesos agroindustriales." if lang == "es" else "Executive dashboard for agroindustrial quality, stability and capability.")
    values = flatten_numeric(st.session_state.variable_df)
    stats_dict = descriptive_stats(values)
    if ensure_min_subgroups(st.session_state.variable_df, "Dashboard SPC"):
        control = xbar_r(st.session_state.variable_df)
    else:
        return
    alerts = western_electric(control["Xbar"], control["cl_x"].iloc[0], control["ucl_x"].iloc[0], control["lcl_x"].iloc[0])
    lsl_spec, usl_spec = spec_limits()
    cap = capability(values, lsl_spec, usl_spec)
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card(t("records", lang), str(stats_dict["count"]), "mediciones")
    with c2: kpi_card(t("mean", lang), f"{stats_dict['mean']:.3f}", st.session_state.metadata.get("Unidad", ""))
    with c3: kpi_card("Cpk", f"{cap.get('Cpk', np.nan):.2f}" if "error" not in cap else "N/A", capability_text(cap, lang))
    with c4: kpi_card(t("process_status", lang), t("out_control", lang) if control["Fuera_Xbar"].any() else t("in_control", lang), f"{int(control['Fuera_Xbar'].sum())} senales")

    md = st.session_state.metadata
    chart_note = "Carta Xbar-R: monitorea la media de cada subgrupo y detecta cambios en el centro del proceso."
    st.markdown(
        f"""
        <div class="context-grid">
            <div class="context-item"><div class="context-label">Caso</div><div class="context-value">{md.get('Producto', 'Sin producto')}</div></div>
            <div class="context-item"><div class="context-label">Variable</div><div class="context-value">{md.get('Variable', 'Sin variable')}</div></div>
            <div class="context-item"><div class="context-label">Lote / Analista</div><div class="context-value">{md.get('Lote', 'N/A')} / {md.get('Analista', 'N/A')}</div></div>
            <div class="context-item"><div class="context-label">Especificacion</div><div class="context-value">LIE {md.get('LIE', 'N/A')} - LSE {md.get('LSE', 'N/A')} {md.get('Unidad', '')}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(chart_note + f" Se estan evaluando {len(control)} subgrupos y {stats_dict['count']} mediciones totales.")
    st.plotly_chart(control_chart(control, "Xbar", "cl_x", "ucl_x", "lcl_x", "Carta Xbar", lsl_spec, usl_spec), use_container_width=True)
    show_assistant(stats_dict, alerts, cap, normality_tests(values))


def process_summary_panel(stats_dict: dict, status: str, signal_count: int, note: str, cap: dict | None = None, defect_count: int | None = None) -> None:
    lang = st.session_state.lang
    md = st.session_state.metadata
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card(t("records", lang), str(stats_dict.get("count", 0)), "mediciones" if lang == "es" else "measurements")
    with c2:
        kpi_card(t("mean", lang), f"{stats_dict.get('mean', np.nan):.3f}" if np.isfinite(stats_dict.get("mean", np.nan)) else "N/A", md.get("Unidad", ""))
    with c3:
        if defect_count is not None:
            kpi_card(t("defects", lang), str(defect_count), "conteo total" if lang == "es" else "total count")
        elif cap:
            kpi_card("Cpk", f"{cap.get('Cpk', np.nan):.2f}" if "error" not in cap else "N/A", capability_text(cap, lang))
        else:
            kpi_card("Cpk", "N/A", "sin especificaciones" if lang == "es" else "no specs")
    with c4:
        kpi_card(t("process_status", lang), status, f"{signal_count} senales" if lang == "es" else f"{signal_count} signals")

    st.markdown(
        f"""
        <div class="context-grid">
            <div class="context-item"><div class="context-label">Caso</div><div class="context-value">{md.get('Producto', 'Sin producto')}</div></div>
            <div class="context-item"><div class="context-label">Variable</div><div class="context-value">{md.get('Variable', 'Sin variable')}</div></div>
            <div class="context-item"><div class="context-label">Lote / Analista</div><div class="context-value">{md.get('Lote', 'N/A')} / {md.get('Analista', 'N/A')}</div></div>
            <div class="context-item"><div class="context-label">Especificacion</div><div class="context-value">LIE {md.get('LIE', 'N/A')} - LSE {md.get('LSE', 'N/A')} {md.get('Unidad', '')}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(note)


def page_data_entry() -> None:
    page_header("Registro de Datos", "Monitoreo y analisis de calidad en tiempo real")
    st.markdown("<div class='info-strip'>Complete todos los campos requeridos. Los datos se almacenan con trazabilidad completa.</div>", unsafe_allow_html=True)
    metadata_form()
    data_schema_help()
    tab1, tab2 = st.tabs(["Variables continuas", "Atributos"])
    with tab1:
        upload_dataframe("variable_df")
        spreadsheet("variable_df", 15)
    with tab2:
        upload_dataframe("attribute_df")
        spreadsheet("attribute_df", 3)
    st.divider()
    st.subheader("Guardar analisis temporal")
    st.caption("Usa un codigo de sesion para recuperar este analisis durante 7 dias en esta instalacion de Streamlit.")
    st.session_state.session_code = st.text_input("Codigo de sesion", value=st.session_state.session_code, key="entry_session_code").strip().lower()
    name = st.text_input("Nombre del analisis temporal", f"{st.session_state.metadata.get('Producto','Analisis')} - {datetime.now():%Y-%m-%d %H:%M}")
    if st.button(t("save_analysis", st.session_state.lang), type="primary"):
        if not st.session_state.session_code:
            st.error("Escribe un codigo de sesion para guardar y recuperar el analisis.")
        else:
            save_temp_analysis(st.session_state.session_code, name, current_analysis_payload())
            st.success("Analisis guardado temporalmente por 7 dias.")


def page_variables() -> None:
    lang = st.session_state.lang
    page_header("Control de Variables", "Cartas Xbar-R y Xbar-S para variables continuas")
    copt1, copt2, copt3 = st.columns([1, 1, 1])
    chart_type = copt1.radio(t("chart_type", lang), ["Xbar-R", "Xbar-S"], horizontal=True)
    manual = copt2.toggle("Usar limites manuales" if lang == "es" else "Use manual limits")
    st.session_state.show_spec_limits = copt3.toggle("Mostrar LIE/LSE" if lang == "es" else "Show LSL/USL", value=st.session_state.show_spec_limits)
    result = compute_variable(chart_type, manual)
    values = flatten_numeric(st.session_state.variable_df)
    stats_dict = descriptive_stats(values)
    lsl_spec, usl_spec = spec_limits()
    cap = capability(values, lsl_spec, usl_spec)
    signal_count = int(result["Fuera_Xbar"].sum())
    spec_count = spec_violations(result["Xbar"], lsl_spec, usl_spec)
    measurement_spec_count = spec_violations(values, lsl_spec, usl_spec)
    total_spec_count = spec_count + measurement_spec_count
    status = t("out_control", lang) if signal_count else ("Fuera de especificacion" if total_spec_count else t("in_control", lang))
    spec_note = variable_specification_note(spec_count, measurement_spec_count, st.session_state.metadata.get('Unidad', ''))
    note = f"Carta {chart_type}: monitorea la media de cada subgrupo y la variabilidad del proceso. Se estan evaluando {len(result)} subgrupos y {stats_dict['count']} mediciones totales. {spec_note}"
    process_summary_panel(stats_dict, status, signal_count + total_spec_count, note, cap=cap)
    lsl = lsl_spec if st.session_state.show_spec_limits else None
    usl = usl_spec if st.session_state.show_spec_limits else None
    if chart_type == "Xbar-R":
        st.markdown("<div class='chart-panel'>", unsafe_allow_html=True)
        st.plotly_chart(control_chart(result, "Xbar", "cl_x", "ucl_x", "lcl_x", "Grafico de Control - Media (X-Barra)", lsl, usl), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-panel'>", unsafe_allow_html=True)
        st.plotly_chart(control_chart(result, "R", "cl_r", "ucl_r", "lcl_r", "Grafico de Control - Rango (R)"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='chart-panel'>", unsafe_allow_html=True)
        st.plotly_chart(control_chart(result, "Xbar", "cl_x", "ucl_x", "lcl_x", "Grafico de Control - Media (X-Barra)", lsl, usl), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-panel'>", unsafe_allow_html=True)
        st.plotly_chart(control_chart(result, "S", "cl_s", "ucl_s", "lcl_s", "Grafico de Control - Desviacion (S)"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    alerts = western_electric(result["Xbar"], result["cl_x"].iloc[0], result["ucl_x"].iloc[0], result["lcl_x"].iloc[0])
    if total_spec_count:
        alerts.append(spec_note)
    status_box(not any("fuera" in a.lower() for a in alerts), "<br>".join(alerts))
    show_assistant(descriptive_stats(flatten_numeric(st.session_state.variable_df)), alerts)
    st.dataframe(result, use_container_width=True)


def page_attributes() -> None:
    lang = st.session_state.lang
    page_header("Control de Atributos", "Cartas p, np, c y u para defectos y no conformidades")
    if not ensure_min_subgroups(st.session_state.attribute_df, "Control por atributos"):
        return
    st.info("Columnas esperadas: Subgrupo, Inspeccionados, Defectuosos, Defectos." if lang == "es" else "Expected columns: Subgroup, Inspected, Defectives, Defects.")
    df = st.session_state.attribute_df.copy()
    required_by_chart = {
        "p": ["Inspeccionados", "Defectuosos"],
        "np": ["Inspeccionados", "Defectuosos"],
        "c": ["Defectos"],
        "u": ["Inspeccionados", "Defectos"],
    }
    copt1, copt2 = st.columns([2, 1])
    chart = copt1.radio(t("chart_type", lang), ["p", "np", "c", "u"], horizontal=True)
    show_attr_specs = copt2.toggle("Mostrar LIE/LSE" if lang == "es" else "Show LSL/USL", value=st.session_state.show_spec_limits, key="show_attr_spec_limits")
    chart_explain = {
        "p": "Carta p: grafica proporcion de unidades defectuosas = Defectuosos / Inspeccionados.",
        "np": "Carta np: grafica numero de unidades defectuosas. CL = n*pbar; UCL/LCL estan en unidades defectuosas, no en proporcion.",
        "c": "Carta c: grafica numero de defectos cuando el area o unidad inspeccionada es constante.",
        "u": "Carta u: grafica defectos por unidad = Defectos / Inspeccionados cuando el tamano inspeccionado varia.",
    }
    st.caption(chart_explain[chart])

    missing = [col for col in required_by_chart[chart] if col not in df.columns]
    if missing:
        st.error(f"Faltan columnas para la carta {chart}: {', '.join(missing)}")
        st.markdown("""
        Tus datos fueron cargados, pero la app no puede saber automaticamente que significa cada columna.
        Usa el mapeo de abajo para asignar las columnas correctas sin volver a cargar el archivo.
        """)
        available = ["No usar"] + list(df.columns)
        c1, c2, c3 = st.columns(3)
        inspected_col = c1.selectbox("Columna Inspeccionados", available, index=available.index("Inspeccionados") if "Inspeccionados" in available else 0)
        defectives_col = c2.selectbox("Columna Defectuosos", available, index=available.index("Defectuosos") if "Defectuosos" in available else 0)
        defects_col = c3.selectbox("Columna Defectos", available, index=available.index("Defectos") if "Defectos" in available else 0)
        if st.button("Aplicar mapeo de columnas", type="primary"):
            mapped = df.copy()
            rename_map = {}
            if inspected_col != "No usar":
                rename_map[inspected_col] = "Inspeccionados"
            if defectives_col != "No usar":
                rename_map[defectives_col] = "Defectuosos"
            if defects_col != "No usar":
                rename_map[defects_col] = "Defectos"
            mapped = mapped.rename(columns=rename_map)
            if "Subgrupo" not in mapped.columns:
                mapped.insert(0, "Subgrupo", range(1, len(mapped) + 1))
            st.session_state.attribute_df = mapped
            st.rerun()
        st.dataframe(df.head(15), use_container_width=True)
        st.stop()

    invalid = []
    for col in required_by_chart[chart]:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.isna().any():
            invalid.append(col)
        df[col] = converted
    if invalid:
        st.error(f"Estas columnas tienen valores no numericos o vacios: {', '.join(invalid)}")
        st.dataframe(df[required_by_chart[chart]].head(15), use_container_width=True)
        st.stop()

    if chart in ["p", "np"] and (df["Defectuosos"] > df["Inspeccionados"]).any():
        st.warning("Hay subgrupos donde `Defectuosos` es mayor que `Inspeccionados`. Revisa si cargaste porcentajes en vez de conteos. Para cartas p/np se esperan conteos de unidades defectuosas.")
    if chart == "np" and df["Inspeccionados"].nunique(dropna=True) > 1:
        st.error("La carta np clasica requiere tamano de muestra constante. Tus valores de `Inspeccionados` varian, por eso no se debe graficar np. Usa carta p para proporciones con tamanos de muestra variables.")
        st.stop()
    if chart == "c" and "Inspeccionados" in df.columns and df["Inspeccionados"].nunique(dropna=True) > 1:
        st.warning("La carta c asume una unidad/area de inspeccion constante. Si el tamano inspeccionado varia, usa carta u.")

    result = attribute_chart(df, chart)
    metric_values = pd.to_numeric(result[chart], errors="coerce").dropna()
    stats_dict = descriptive_stats(metric_values)
    defect_count = None
    if chart in ["p", "np"] and "Defectuosos" in df.columns:
        defect_count = int(pd.to_numeric(df["Defectuosos"], errors="coerce").fillna(0).sum())
    elif chart in ["c", "u"] and "Defectos" in df.columns:
        defect_count = int(pd.to_numeric(df["Defectos"], errors="coerce").fillna(0).sum())
    signal_count = int(result["Fuera"].sum())
    attr_lsl_base, attr_usl_base = spec_limits()
    spec_count = spec_violations(result[chart], attr_lsl_base, attr_usl_base)
    status = t("out_control", lang) if signal_count else ("Fuera de especificacion" if spec_count else t("in_control", lang))
    note = f"Carta {chart}: {chart_explain[chart]} Se estan evaluando {len(result)} subgrupos. {specification_note(spec_count)}"
    process_summary_panel(stats_dict, status, signal_count + spec_count, note, defect_count=defect_count)
    metric = chart
    attr_lsl = attr_lsl_base if show_attr_specs else None
    attr_usl = attr_usl_base if show_attr_specs else None
    st.markdown("<div class='chart-panel'>", unsafe_allow_html=True)
    st.plotly_chart(control_chart(result, metric, "CL", "UCL", "LCL", f"Grafico de Control de Atributos - Carta {chart}", attr_lsl, attr_usl), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    status_box(not result["Fuera"].any() and spec_count == 0, f"Puntos fuera de control: {int(result['Fuera'].sum())}<br>{specification_note(spec_count)}")
    st.dataframe(result, use_container_width=True)


def page_capability() -> None:
    if not ensure_min_subgroups(st.session_state.variable_df, "Capacidad de procesos"):
        return
    values = flatten_numeric(st.session_state.variable_df)
    md = metadata_form()
    lsl_spec, usl_spec = spec_limits()
    cap = capability(values, lsl_spec, usl_spec)
    st.plotly_chart(histogram_capability(values, lsl_spec, usl_spec), use_container_width=True)
    if "error" in cap:
        st.warning(cap["error"])
    else:
        cols = st.columns(4)
        for col, key in zip(cols, ["Cp", "Cpk", "Pp", "Ppk"]):
            col.metric(key, f"{cap[key]:.3f}")
        status_box(cap.get("Cpk", 0) >= 1.33, capability_text(cap, st.session_state.lang))
        show_assistant(descriptive_stats(values), [], cap)


def page_pareto() -> None:
    lang = st.session_state.lang
    page_header("Analisis de Defectos y Pareto", "Frecuencia acumulada, causas raiz e Ishikawa inteligente")

    ish_categories = ["Materiales", "Maquinaria", "Metodos", "Mano de Obra", "Medio Ambiente", "Medicion"]

    def sync_ishikawa_category(category: str) -> None:
        raw_text = st.session_state.get(f"ish_{category}", "")
        st.session_state.ishikawa_causes[category] = [line.strip() for line in raw_text.splitlines() if line.strip()]

    def sync_ishikawa_effect() -> None:
        st.session_state.ishikawa_effect = st.session_state.get("ish_effect_input", st.session_state.ishikawa_effect)

    st.session_state.setdefault("ish_effect_input", st.session_state.ishikawa_effect)
    for cat in ish_categories:
        st.session_state.setdefault(f"ish_{cat}", "\n".join(st.session_state.ishikawa_causes.get(cat, [])))

    if st.button(t("load_example", st.session_state.lang)):
        st.session_state.pareto_df = pareto_example()
    df = st.session_state.pareto_df.copy()
    if df.empty:
        df = pd.DataFrame({"Categoria": [], "Frecuencia": []})
    category = st.selectbox("Categoria", df.columns, index=0)
    frequency = st.selectbox("Frecuencia", df.columns, index=min(1, len(df.columns) - 1))
    table = pareto_table(df, category, frequency)

    st.markdown("<div class='chart-panel'>", unsafe_allow_html=True)
    st.plotly_chart(pareto_chart(table, category, frequency), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Editar datos del Pareto" if lang == "es" else "Edit Pareto data", expanded=False):
        c1, c2, c3 = st.columns([2, 1, 1])
        new_cat = c1.text_input("Categoria / defecto" if lang == "es" else "Category / defect", key="pareto_new_cat")
        new_freq = c2.number_input("Frecuencia" if lang == "es" else "Frequency", min_value=0.0, value=0.0, step=1.0, key="pareto_new_freq")
        if c3.button("Agregar" if lang == "es" else "Add", key="pareto_add_manual") and new_cat.strip():
            row = pd.DataFrame({"Categoria": [new_cat.strip()], "Frecuencia": [new_freq]})
            st.session_state.pareto_df = pd.concat([st.session_state.pareto_df, row], ignore_index=True)
            st.rerun()

        raw = st.text_area("Pegar desde Excel (Categoria y Frecuencia)" if lang == "es" else "Paste from Excel (Category and Frequency)", height=110, key="pareto_paste")
        b1, b2, b3 = st.columns(3)
        if b1.button("Aplicar pegado" if lang == "es" else "Apply paste", key="pareto_apply_paste") and raw.strip():
            lines = [line for line in raw.strip().splitlines() if line.strip()]
            parsed = [line.split("\t") if "\t" in line else line.split(",") for line in lines]
            rows = []
            for parts in parsed:
                if len(parts) >= 2:
                    try:
                        freq = float(str(parts[1]).replace(",", "."))
                    except ValueError:
                        continue
                    rows.append({"Categoria": str(parts[0]).strip(), "Frecuencia": freq})
            if rows:
                st.session_state.pareto_df = pd.DataFrame(rows)
                st.rerun()
        if b2.button("Crear tabla vacia" if lang == "es" else "Create blank table", key="pareto_blank"):
            st.session_state.pareto_df = pd.DataFrame({"Categoria": ["" for _ in range(10)], "Frecuencia": [0 for _ in range(10)]})
            st.rerun()
        if b3.button("Limpiar Pareto" if lang == "es" else "Clear Pareto", key="pareto_clear"):
            st.session_state.pareto_df = pd.DataFrame({"Categoria": [], "Frecuencia": []})
            st.rerun()
        edited = st.data_editor(st.session_state.pareto_df, num_rows="dynamic", use_container_width=True, height=300, key="pareto_editor")
        st.session_state.pareto_df = edited

    st.subheader("Diagrama de Causa-Efecto (Ishikawa)")
    st.markdown("<div class='chart-panel'>", unsafe_allow_html=True)
    svg_markup = ishikawa_svg(st.session_state.ishikawa_effect, st.session_state.ishikawa_causes)
    components.html(ishikawa_html(st.session_state.ishikawa_effect, st.session_state.ishikawa_causes), height=780, scrolling=False)
    st.markdown("</div>", unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    d1.download_button("Descargar SVG", svg_markup.encode("utf-8"), "ishikawa_agrospc.svg", "image/svg+xml", use_container_width=True)
    d2.download_button("Descargar HTML", ishikawa_html(st.session_state.ishikawa_effect, st.session_state.ishikawa_causes).encode("utf-8"), "ishikawa_agrospc.html", "text/html", use_container_width=True)
    d3.caption("SVG/HTML conservan maxima calidad y escalan sin perder resolucion.")

    with st.expander("Editar Ishikawa 6M", expanded=True):
        st.text_input("Efecto principal", key="ish_effect_input", on_change=sync_ishikawa_effect)
        cols = st.columns(2)
        for idx, cat in enumerate(ish_categories):
            with cols[idx % 2]:
                st.text_area(cat, height=120, key=f"ish_{cat}", on_change=sync_ishikawa_category, args=(cat,))
        if st.button("Analizar Ishikawa con IA"):
            prompt = f"Analiza este Ishikawa 6M para el efecto {st.session_state.ishikawa_effect}. Causas: {st.session_state.ishikawa_causes}. Detecta inconsistencias, causas duplicadas, causas mal clasificadas, faltantes y propone correcciones concretas."
            fallback = "Revise duplicados, clasifique causas por 6M, priorice causas medibles y relacione el efecto con el Pareto."
            text, source = generate_text(prompt, fallback, temperature=0.25)
            st.caption(f"Fuente: {source}")
            st.markdown(text)
    st.dataframe(table, use_container_width=True)


def page_normality() -> None:
    if not ensure_min_subgroups(st.session_state.variable_df, "Normalidad"):
        return
    page_header("Normalidad del Proceso", "Distribucion, Q-Q plot y pruebas de normalidad")
    values = flatten_numeric(st.session_state.variable_df)
    tests = normality_tests(values)
    if "error" in tests:
        st.warning(tests["error"])
    else:
        stats_dict = descriptive_stats(values)
        shapiro_p = tests["Shapiro-Wilk"]["pvalue"]
        ks_p = tests["Kolmogorov-Smirnov"]["pvalue"]
        ad_ok = tests["Anderson-Darling"]["normal_5pct"]
        normal_votes = int(shapiro_p >= 0.05) + int(ks_p >= 0.05) + int(ad_ok)
        status_class = "good" if normal_votes >= 2 else "bad"
        status_text = "Compatible" if normal_votes >= 2 else "Revisar"
        st.markdown(
            f"""
            <div class='health-grid'>
                <div class='health-card {status_class}'><div class='health-label'>Estado</div><div class='health-value'>{status_text}</div><div class='health-note'>{normal_votes}/3 pruebas compatibles</div></div>
                <div class='health-card {'good' if shapiro_p >= 0.05 else 'bad'}'><div class='health-label'>Shapiro-Wilk</div><div class='health-value'>{shapiro_p:.3f}</div><div class='health-note'>p-value</div></div>
                <div class='health-card {'good' if ks_p >= 0.05 else 'bad'}'><div class='health-label'>Kolmogorov-Smirnov</div><div class='health-value'>{ks_p:.3f}</div><div class='health-note'>p-value</div></div>
                <div class='health-card warn'><div class='health-label'>Muestra</div><div class='health-value'>{stats_dict['count']}</div><div class='health-note'>Media {stats_dict['mean']:.3f} · s {stats_dict['std']:.3f}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cfig1, cfig2 = st.columns([1.15, .85])
        with cfig1:
            st.markdown("<div class='chart-panel'>", unsafe_allow_html=True)
            st.plotly_chart(histogram_capability(values), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with cfig2:
            st.markdown("<div class='chart-panel'>", unsafe_allow_html=True)
            st.plotly_chart(normality_figure(values), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        rows = []
        for name, result in tests.items():
            if name == "Anderson-Darling":
                normal = result["normal_5pct"]
                rows.append({
                    "Prueba": name,
                    "Estadistico": round(result["statistic"], 4),
                    "p-value": "No aplica",
                    "Criterio": f"Critico 5% = {result['critical_5']:.4f}",
                    "Decision": "Compatible con normalidad" if normal else "Posible no normalidad",
                })
            else:
                pvalue = result["pvalue"]
                rows.append({
                    "Prueba": name,
                    "Estadistico": round(result["statistic"], 4),
                    "p-value": round(pvalue, 4),
                    "Criterio": "p >= 0.05" if pvalue >= 0.05 else "p < 0.05",
                    "Decision": "Compatible con normalidad" if pvalue >= 0.05 else "Posible no normalidad",
                })
        summary = pd.DataFrame(rows)
        ok_count = int((summary["Decision"] == "Compatible con normalidad").sum())
        c1, c2, c3 = st.columns(3)
        with c1: kpi_card("Pruebas compatibles", f"{ok_count}/3", "normalidad")
        with c2: kpi_card("Shapiro p-value", f"{tests['Shapiro-Wilk']['pvalue']:.4f}", "p >= 0.05 acepta")
        with c3: kpi_card("K-S p-value", f"{tests['Kolmogorov-Smirnov']['pvalue']:.4f}", "contraste con normal")
        st.dataframe(summary, use_container_width=True, hide_index=True)
        p = tests["Shapiro-Wilk"]["pvalue"]
        if p >= 0.05:
            message = "Conclusion: no hay evidencia suficiente para rechazar normalidad. Puedes interpretar capacidad y cartas con mayor confianza."
        else:
            message = "Conclusion: los datos muestran posible no normalidad. Revisa atipicos, mezcla de lotes o considera transformacion antes de capacidad."
        status_box(p >= 0.05, message)
        with st.expander("Ver detalle tecnico JSON"):
            st.json(tests)


def page_reports() -> None:
    if not ensure_min_subgroups(st.session_state.variable_df, "Reportes"):
        return
    values = flatten_numeric(st.session_state.variable_df)
    stats_dict = descriptive_stats(values)
    control = xbar_r(st.session_state.variable_df)
    alerts = western_electric(control["Xbar"], control["cl_x"].iloc[0], control["ucl_x"].iloc[0], control["lcl_x"].iloc[0])
    lsl_spec, usl_spec = spec_limits()
    cap = capability(values, lsl_spec, usl_spec)
    conclusions = ai_assistant_summary(stats_dict, alerts, cap, normality_tests(values), st.session_state.lang)
    st.subheader("Reporte automatico")
    if deepseek_available():
        st.caption("IA activa: DeepSeek")
    elif gemini_available():
        st.caption("IA activa: Gemini")
    else:
        st.caption("IA externa no configurada: modo local")
    for item in conclusions:
        st.write(f"• {item}")
    pdf = pdf_report("Reporte SPC Agroindustrial", st.session_state.metadata, conclusions, control)
    st.download_button("Descargar PDF", pdf, "reporte_spc.pdf", "application/pdf")


def page_export() -> None:
    if not ensure_min_subgroups(st.session_state.variable_df, "Exportacion"):
        return
    values = flatten_numeric(st.session_state.variable_df)
    stats_df = pd.DataFrame([descriptive_stats(values)])
    control = xbar_r(st.session_state.variable_df)
    sheets = {"Datos variables": st.session_state.variable_df, "Datos atributos": st.session_state.attribute_df, "Control": control, "Estadistica": stats_df}
    st.download_button("Descargar Excel", excel_bytes(sheets), "spc_agroindustrial.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Descargar CSV variables", csv_bytes(st.session_state.variable_df), "variables.csv", "text/csv")
    st.download_button("Descargar CSV atributos", csv_bytes(st.session_state.attribute_df), "atributos.csv", "text/csv")


def page_settings() -> None:
    lang = st.session_state.lang
    st.subheader("Configuracion" if lang == "es" else "Settings")
    st.caption("Apariencia" if lang == "es" else "Appearance")
    theme = st.radio(
        "Tema" if lang == "es" else "Theme",
        ["System", "Light", "Dark"],
        index=["System", "Light", "Dark"].index(st.session_state.ui_theme),
        horizontal=True,
        label_visibility="collapsed",
    )
    if theme != st.session_state.ui_theme:
        st.session_state.ui_theme = theme
        st.rerun()

    st.divider()
    lang_label = st.selectbox(
        t("language", lang),
        ["Español", "English"],
        index=0 if lang == "es" else 1,
    )
    new_lang = "en" if lang_label == "English" else "es"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    st.divider()
    st.subheader("Asistente IA" if lang == "es" else "AI Assistant")
    st.caption("La clave se guarda solo en la sesion actual; no se escribe en archivos del proyecto." if lang == "es" else "The key is stored only in the current session; it is not written to project files.")
    api_value = st.text_input("Gemini API Key", value=st.session_state.get("gemini_api_key", ""), type="password")
    if api_value != st.session_state.get("gemini_api_key", ""):
        st.session_state.gemini_api_key = api_value
    if deepseek_available():
        st.info("DeepSeek configurado como proveedor principal.")
    elif gemini_available():
        st.info("Gemini configurado como proveedor secundario.")
    else:
        st.info("IA externa no configurada. Se usara asistente local.")

    st.divider()
    st.subheader("Analisis temporales" if lang == "es" else "Temporary analyses")
    st.caption("SQLite guarda estos datos en `database/spc_quality.db`. En Streamlit Cloud funciona para demo, pero el disco puede reiniciarse." if lang == "es" else "SQLite stores this data in `database/spc_quality.db`. On Streamlit Cloud it works for demos, but storage may reset.")
    st.session_state.session_code = st.text_input("Codigo de sesion" if lang == "es" else "Session code", value=st.session_state.session_code, key="settings_session_code").strip().lower()
    csave1, csave2 = st.columns([2, 1])
    temp_name = csave1.text_input("Nombre para guardar" if lang == "es" else "Save name", f"{st.session_state.metadata.get('Producto','Analisis')} - {datetime.now():%Y-%m-%d %H:%M}")
    if csave2.button("Guardar estado actual" if lang == "es" else "Save current state", type="primary", use_container_width=True):
        if not st.session_state.session_code:
            st.error("Escribe un codigo de sesion." if lang == "es" else "Enter a session code.")
        else:
            save_temp_analysis(st.session_state.session_code, temp_name, current_analysis_payload())
            st.success("Analisis guardado por 7 dias." if lang == "es" else "Analysis saved for 7 days.")

    analyses = list_analyses(st.session_state.session_code) if st.session_state.session_code else pd.DataFrame()
    st.dataframe(analyses, use_container_width=True, hide_index=True)
    if not analyses.empty:
        selected = st.selectbox("Seleccionar ID", analyses["id"].tolist())
        c1, c2 = st.columns(2)
        if c1.button("Recuperar"):
            payload = load_analysis(int(selected), st.session_state.session_code)
            restore_analysis_payload(payload)
            st.success("Analisis recuperado.")
            st.rerun()
        if c2.button("Borrar"):
            delete_analysis(int(selected), st.session_state.session_code)
            st.success("Analisis borrado.")
            st.rerun()
    st.caption("No hay login ni roles: quien conozca el codigo de sesion puede recuperar esos analisis temporales." if lang == "es" else "No login or roles: anyone with the session code can recover those temporary analyses.")


def main() -> None:
    apply_theme()
    init_db()
    init_state()
    page = sidebar()
    if page == "home":
        page_home()
    elif page == "dashboard":
        st.session_state.page = "home"
        page_home()
    elif page == "data_entry":
        page_data_entry()
    elif page == "variables":
        page_variables()
    elif page == "attributes":
        page_attributes()
    elif page == "capability":
        page_capability()
    elif page == "pareto":
        page_pareto()
    elif page == "normality":
        page_normality()
    elif page == "catalog":
        page_catalog()
    elif page == "reports":
        page_reports()
    elif page == "export":
        page_export()
    elif page == "settings":
        page_settings()


if __name__ == "__main__":
    main()
