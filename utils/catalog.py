from __future__ import annotations

import pandas as pd


PRODUCT_CATALOG = {
    "Fruta": [
        "Aguacate", "Banano", "Mango", "Melon", "Papaya", "Pina", "Naranja", "Limon", "Mandarina",
        "Guayaba", "Maracuya", "Mora", "Fresa", "Uva", "Manzana", "Pera", "Durazno", "Ciruela",
        "Sandia", "Pitahaya", "Granadilla", "Lulo", "Tomate de arbol", "Arandano", "Coco", "Guanabana",
        "Zapote", "Tamarindo", "Kiwi", "Cereza", "Frambuesa", "Curuba", "Feijoa", "Nispero",
    ],
    "Hortaliza": [
        "Tomate", "Cebolla", "Cilantro", "Lechuga", "Zanahoria", "Aji topito", "Aji dulce", "Pimenton",
        "Pepino", "Habichuela", "Brocoli", "Coliflor", "Repollo", "Espinaca", "Acelga", "Apio",
        "Berenjena", "Calabacin", "Remolacha", "Rabano", "Papa", "Yuca", "Name", "Ahuyama",
        "Arveja", "Maiz tierno", "Ajo", "Puerro", "Cebollin", "Rucula", "Batata", "Oregano fresco",
    ],
    "Planta medicinal": [
        "Sabila (Aloe vera)", "Manzanilla", "Menta", "Toronjil (Melisa)", "Calendula", "Eucalipto",
        "Romero", "Hierbabuena", "Limoncillo", "Valeriana", "Albahaca", "Oregano", "Tomillo", "Ruda",
        "Jengibre", "Curcuma", "Diente de leon", "Ortiga", "Salvia", "Anis", "Lavanda", "Cedron",
        "Boldo", "Sauco", "Achiote", "Aloe", "Malva", "Verbena", "Poleo", "Mejorana",
    ],
}


CONTINUOUS_VARIABLES = [
    {"Variable": "Altura de la planta", "Unidad": "cm", "Categoria": "Morfologica", "Descripcion": "Indica crecimiento y desarrollo", "Herramienta": "Xbar-R / Xbar-S"},
    {"Variable": "Peso fresco", "Unidad": "g", "Categoria": "Productiva", "Descripcion": "Determina rendimiento de cosecha", "Herramienta": "Xbar-R / Capacidad"},
    {"Variable": "Peso seco", "Unidad": "g", "Categoria": "Productiva", "Descripcion": "Evalua materia util tras secado", "Herramienta": "Xbar-R / Capacidad"},
    {"Variable": "Longitud de hojas", "Unidad": "cm", "Categoria": "Morfologica", "Descripcion": "Relacionada con calidad vegetal", "Herramienta": "Xbar-R"},
    {"Variable": "Ancho de hojas", "Unidad": "cm", "Categoria": "Morfologica", "Descripcion": "Caracteriza uniformidad vegetal", "Herramienta": "Xbar-R"},
    {"Variable": "Diametro", "Unidad": "cm", "Categoria": "Morfologica", "Descripcion": "Calibre comercial del producto", "Herramienta": "Xbar-R / Capacidad"},
    {"Variable": "Diametro del tallo", "Unidad": "mm", "Categoria": "Morfologica", "Descripcion": "Vigor y desarrollo de planta", "Herramienta": "Xbar-R"},
    {"Variable": "Numero de hojas, flores o frutos", "Unidad": "conteo", "Categoria": "Productiva", "Descripcion": "Indicador de productividad", "Herramienta": "c / u"},
    {"Variable": "Area foliar", "Unidad": "cm2", "Categoria": "Morfologica", "Descripcion": "Relacionada con fotosintesis", "Herramienta": "Xbar-S"},
    {"Variable": "Contenido de humedad", "Unidad": "%", "Categoria": "Fisiologica", "Descripcion": "Controla estabilidad y vida util", "Herramienta": "Xbar-R / Capacidad"},
    {"Variable": "Contenido de aceites esenciales", "Unidad": "%", "Categoria": "Fitoquimica", "Descripcion": "Indicador de potencia en plantas medicinales", "Herramienta": "Xbar-R / Capacidad"},
    {"Variable": "pH", "Unidad": "pH", "Categoria": "Fisicoquimica", "Descripcion": "Acidez o alcalinidad del producto", "Herramienta": "Xbar-R / Normalidad"},
    {"Variable": "Grados Brix", "Unidad": "Bx", "Categoria": "Fisicoquimica", "Descripcion": "Contenido de solidos solubles", "Herramienta": "Xbar-R / Capacidad"},
    {"Variable": "Firmeza", "Unidad": "N", "Categoria": "Fisica", "Descripcion": "Textura y madurez", "Herramienta": "Xbar-R / Capacidad"},
    {"Variable": "Temperatura de secado", "Unidad": "C", "Categoria": "Ambiental", "Descripcion": "Condicion critica del proceso", "Herramienta": "Xbar-R"},
    {"Variable": "Tiempo de secado", "Unidad": "h", "Categoria": "Proceso", "Descripcion": "Tiempo de exposicion o tratamiento", "Herramienta": "Xbar-R"},
    {"Variable": "Contenido de cenizas", "Unidad": "%", "Categoria": "Fitoquimica", "Descripcion": "Materia mineral total", "Herramienta": "Xbar-S / Capacidad"},
    {"Variable": "Actividad de agua", "Unidad": "aw", "Categoria": "Fisicoquimica", "Descripcion": "Riesgo microbiologico y estabilidad", "Herramienta": "Xbar-R / Capacidad"},
    {"Variable": "Principios activos", "Unidad": "mg/g", "Categoria": "Fitoquimica", "Descripcion": "Concentracion funcional del extracto", "Herramienta": "Xbar-S / Capacidad"},
    {"Variable": "Rendimiento del extracto", "Unidad": "%", "Categoria": "Productiva", "Descripcion": "Eficiencia de extraccion", "Herramienta": "Xbar-R / Capacidad"},
    {"Variable": "Humedad relativa", "Unidad": "%", "Categoria": "Ambiental", "Descripcion": "Condicion de almacenamiento o proceso", "Herramienta": "Xbar-R"},
    {"Variable": "Precipitacion", "Unidad": "mm", "Categoria": "Ambiental", "Descripcion": "Condicion agroclimatica", "Herramienta": "Xbar-S"},
]


ATTRIBUTE_VARIABLES = [
    {"Atributo": "Presencia de manchas", "Evaluacion": "Conforme / No conforme", "Descripcion": "Defectos visibles de superficie", "Herramienta": "p / np"},
    {"Atributo": "Danos por plagas", "Evaluacion": "Conforme / No conforme", "Descripcion": "Afectacion por insectos o plagas", "Herramienta": "p / np"},
    {"Atributo": "Golpes o magulladuras", "Evaluacion": "Conforme / No conforme", "Descripcion": "Deterioro mecanico", "Herramienta": "p / np"},
    {"Atributo": "Frutos podridos", "Evaluacion": "Conteo / Proporcion", "Descripcion": "Deterioro sanitario", "Herramienta": "p / c"},
    {"Atributo": "Defectos de color", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Uniformidad o desviacion del color", "Herramienta": "p / np"},
    {"Atributo": "Presencia de plagas", "Evaluacion": "Si / No", "Descripcion": "Sanidad del cultivo", "Herramienta": "p"},
    {"Atributo": "Presencia de enfermedades", "Evaluacion": "Conforme / No conforme", "Descripcion": "Deteccion de infecciones", "Herramienta": "p"},
    {"Atributo": "Danos mecanicos", "Evaluacion": "Conforme / No conforme", "Descripcion": "Golpes o deterioros", "Herramienta": "p / np"},
    {"Atributo": "Contaminacion por hongos", "Evaluacion": "Conforme / No conforme", "Descripcion": "Presencia de moho", "Herramienta": "p / c"},
    {"Atributo": "Material extrano", "Evaluacion": "Si / No", "Descripcion": "Piedras, tierra o residuos", "Herramienta": "p / c"},
    {"Atributo": "Uniformidad del color", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Indicador sensorial de calidad", "Herramienta": "p"},
    {"Atributo": "Aroma caracteristico", "Evaluacion": "Conforme / No conforme", "Descripcion": "Identificacion sensorial", "Herramienta": "p"},
    {"Atributo": "Pureza del lote", "Evaluacion": "Conforme / No conforme", "Descripcion": "Ausencia de adulteraciones", "Herramienta": "p / np"},
    {"Atributo": "Presencia de malezas", "Evaluacion": "Si / No", "Descripcion": "Control agronomico", "Herramienta": "p"},
    {"Atributo": "Cumplimiento BPA", "Evaluacion": "Cumple / No cumple", "Descripcion": "Buenas Practicas Agricolas", "Herramienta": "p"},
    {"Atributo": "Cumplimiento BPM", "Evaluacion": "Cumple / No cumple", "Descripcion": "Buenas Practicas de Manufactura", "Herramienta": "p"},
    {"Atributo": "Etiquetado correcto", "Evaluacion": "Conforme / No conforme", "Descripcion": "Informacion del producto", "Herramienta": "p / np"},
    {"Atributo": "Presencia de insectos", "Evaluacion": "Si / No", "Descripcion": "Indicador de contaminacion", "Herramienta": "p / c"},
    {"Atributo": "Empaque adecuado", "Evaluacion": "Conforme / No conforme", "Descripcion": "Condicion de empaque", "Herramienta": "p"},
    {"Atributo": "Nivel de limpieza", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Condicion higienica", "Herramienta": "p / np"},
]


PRODUCT_SUGGESTIONS = {
    "Sabila (Aloe vera)": ["Peso del gel", "pH", "Contenido de aloina", "Humedad", "Pureza del lote"],
    "Manzanilla": ["Contenido de aceites esenciales", "Aroma caracteristico", "Humedad", "Material extrano"],
    "Hierbabuena": ["Rendimiento", "Concentracion de mentol", "Longitud de hojas", "Aroma caracteristico"],
    "Calendula": ["Numero de flores", "Contenido de flavonoides", "Color", "Pureza del lote"],
    "Limoncillo": ["Concentracion de citral", "Contenido de aceites esenciales", "Humedad", "Aroma caracteristico"],
    "Mango": ["Peso fresco", "Grados Brix", "Firmeza", "Diametro", "Defectos de color"],
    "Banano": ["Peso fresco", "Grados Brix", "Firmeza", "Color", "Golpes o magulladuras"],
    "Aguacate": ["Peso fresco", "Diametro", "Materia seca", "Firmeza", "Danos mecanicos"],
    "Melon": ["Peso fresco", "Grados Brix", "Diametro", "Firmeza", "Presencia de manchas"],
    "Cilantro": ["Peso fresco", "Longitud de hojas", "Humedad", "Aroma caracteristico", "Nivel de limpieza"],
    "Aji topito": ["Peso fresco", "Diametro", "Color", "Grados Brix", "Danos por plagas"],
    "Tomate": ["Diametro", "Firmeza", "Color", "Grados Brix", "Frutos con pudricion"],
    "Lechuga": ["Peso fresco", "Diametro", "Color", "Humedad", "Hojas amarillas"],
    "Pina": ["Peso fresco", "Grados Brix", "pH", "Firmeza", "Golpes o magulladuras"],
    "Papaya": ["Peso fresco", "Grados Brix", "Firmeza", "Color", "Madurez no uniforme"],
    "Romero": ["Contenido de aceites esenciales", "Humedad", "Principios activos", "Aroma caracteristico", "Material extrano"],
    "Menta": ["Concentracion de mentol", "Contenido de aceites esenciales", "Humedad", "Longitud de hojas", "Aroma caracteristico"],
}

PRODUCT_DESCRIPTIONS = {
    "Valeriana": "Planta medicinal usada principalmente por sus compuestos asociados a relajacion y bienestar. En control de calidad interesa vigilar humedad, principios activos, aroma, pureza del lote y ausencia de contaminacion, porque estos factores afectan estabilidad, seguridad y aceptacion del producto.",
    "Sabila (Aloe vera)": "Planta medicinal de alto valor por su gel, usado en industrias cosmetica, farmaceutica y alimentaria. Sus controles clave incluyen peso del gel, pH, humedad, pureza y compuestos activos como aloina.",
    "Manzanilla": "Planta medicinal empleada en infusiones y extractos. La calidad depende del contenido de aceites esenciales, aroma caracteristico, humedad, color y ausencia de material extrano.",
    "Mango": "Fruta tropical de alta importancia comercial. Su calidad se evalua con peso, grados Brix, firmeza, color, madurez y defectos fisicos, variables relacionadas con sabor, vida util y aceptacion del mercado.",
    "Aguacate": "Fruta de alto valor comercial donde la materia seca, firmeza, calibre, peso y ausencia de danos mecanicos son decisivos para cosecha, exportacion y maduracion controlada.",
    "Banano": "Fruta climatérica cuyo control se centra en peso, color, firmeza, grados Brix, madurez y golpes. Estos indicadores ayudan a gestionar cosecha, transporte y vida poscosecha.",
    "Cilantro": "Hortaliza aromatica sensible a humedad, limpieza y deterioro. Sus controles de calidad incluyen peso fresco, longitud de hojas, aroma, presencia de plagas y nivel de limpieza.",
    "Tomate": "Hortaliza/fruto de alta rotacion donde firmeza, calibre, color, solidos solubles y sanidad definen aceptacion comercial, vida util y desempeno en empaque.",
    "Lechuga": "Hortaliza de hoja muy sensible a deshidratacion, danos mecanicos y contaminacion. El SPC ayuda a controlar frescura, peso, color, limpieza y descarte por hojas deterioradas.",
    "Pina": "Fruta tropical procesada y fresca donde Brix, pH, firmeza, calibre y danos por manejo determinan dulzor, estabilidad y categoria comercial.",
    "Papaya": "Fruta climatérica sensible a madurez, firmeza y golpes. El control de calidad permite separar lotes por estado de consumo, exportacion o procesamiento.",
    "Romero": "Planta aromatica usada en extractos, aceites e infusiones. La calidad depende de humedad, aceite esencial, aroma, pureza y ausencia de material extrano.",
    "Menta": "Planta aromatica cuyo valor esta asociado a mentol, aroma, color y frescura. El control estadistico ayuda a estabilizar cosecha, secado y recepcion de materia prima.",
}
PRODUCT_ATTRIBUTES = {
    "Valeriana": [
        {"Atributo": "Aroma terroso caracteristico", "Evaluacion": "Conforme / No conforme", "Descripcion": "Ayuda a identificar autenticidad y estado del material", "Herramienta": "p"},
        {"Atributo": "Raices quebradas o pulverizadas", "Evaluacion": "Conteo", "Descripcion": "Indica deterioro por manipulacion o secado excesivo", "Herramienta": "c / u"},
        {"Atributo": "Material extrano", "Evaluacion": "Si / No", "Descripcion": "Tierra, tallos no deseados o impurezas", "Herramienta": "p / c"},
        {"Atributo": "Moho visible", "Evaluacion": "Conforme / No conforme", "Descripcion": "Riesgo por humedad o almacenamiento deficiente", "Herramienta": "p"},
    ],
    "Sabila (Aloe vera)": [
        {"Atributo": "Gel oxidado", "Evaluacion": "Conforme / No conforme", "Descripcion": "Cambio de color por exposicion o deterioro", "Herramienta": "p"},
        {"Atributo": "Presencia de latex amarillo", "Evaluacion": "Si / No", "Descripcion": "Puede indicar contaminacion con aloina no deseada", "Herramienta": "p"},
        {"Atributo": "Hojas con danos mecanicos", "Evaluacion": "Conteo", "Descripcion": "Golpes, cortes o deterioro por transporte", "Herramienta": "c / u"},
        {"Atributo": "Impurezas en gel", "Evaluacion": "Conteo", "Descripcion": "Restos de epidermis o material extrano", "Herramienta": "c"},
    ],
    "Manzanilla": [
        {"Atributo": "Capitulos florales oscuros", "Evaluacion": "Conteo", "Descripcion": "Senal de envejecimiento o secado inadecuado", "Herramienta": "c / u"},
        {"Atributo": "Aroma debil", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Indicador sensorial de perdida de aceites esenciales", "Herramienta": "p"},
        {"Atributo": "Exceso de tallos", "Evaluacion": "Conforme / No conforme", "Descripcion": "Afecta pureza y presentacion", "Herramienta": "p"},
        {"Atributo": "Material extrano", "Evaluacion": "Conteo", "Descripcion": "Impurezas del proceso de cosecha", "Herramienta": "c"},
    ],
    "Mango": [
        {"Atributo": "Manchas negras", "Evaluacion": "Conteo", "Descripcion": "Defectos de piel que reducen aceptacion comercial", "Herramienta": "c / u"},
        {"Atributo": "Golpes o magulladuras", "Evaluacion": "Conforme / No conforme", "Descripcion": "Danos por cosecha o transporte", "Herramienta": "p / np"},
        {"Atributo": "Madurez no uniforme", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Dificulta clasificacion y vida poscosecha", "Herramienta": "p"},
        {"Atributo": "Ataque de mosca de la fruta", "Evaluacion": "Si / No", "Descripcion": "Riesgo fitosanitario critico", "Herramienta": "p"},
    ],
    "Aguacate": [
        {"Atributo": "Piel con rozaduras", "Evaluacion": "Conteo", "Descripcion": "Defecto superficial de manipulacion", "Herramienta": "c / u"},
        {"Atributo": "Madurez heterogenea", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Afecta proceso de despacho y consumo", "Herramienta": "p"},
        {"Atributo": "Antracnosis visible", "Evaluacion": "Si / No", "Descripcion": "Defecto sanitario de alto impacto", "Herramienta": "p"},
        {"Atributo": "Frutos deformes", "Evaluacion": "Conteo", "Descripcion": "Reduce categoria comercial", "Herramienta": "c"},
    ],
    "Banano": [
        {"Atributo": "Dedos golpeados", "Evaluacion": "Conteo", "Descripcion": "Dano mecanico frecuente en manejo", "Herramienta": "c / u"},
        {"Atributo": "Manchas de maduracion", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Indicador de estado comercial", "Herramienta": "p"},
        {"Atributo": "Corona con hongos", "Evaluacion": "Si / No", "Descripcion": "Riesgo sanitario poscosecha", "Herramienta": "p"},
        {"Atributo": "Calibre fuera de especificacion", "Evaluacion": "Conforme / No conforme", "Descripcion": "No cumple categoria comercial", "Herramienta": "p / np"},
    ],
    "Cilantro": [
        {"Atributo": "Hojas amarillas", "Evaluacion": "Conteo", "Descripcion": "Perdida de frescura y calidad visual", "Herramienta": "c / u"},
        {"Atributo": "Presencia de tierra", "Evaluacion": "Si / No", "Descripcion": "Defecto de limpieza", "Herramienta": "p"},
        {"Atributo": "Tallos marchitos", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Indicador de deshidratacion", "Herramienta": "p"},
        {"Atributo": "Aroma no caracteristico", "Evaluacion": "Conforme / No conforme", "Descripcion": "Perdida sensorial o contaminacion", "Herramienta": "p"},
    ],
    "Tomate": [
        {"Atributo": "Frutos rajados", "Evaluacion": "Conteo", "Descripcion": "Dano fisico que acelera deterioro", "Herramienta": "c / u"},
        {"Atributo": "Color no uniforme", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Madurez heterogenea del lote", "Herramienta": "p"},
        {"Atributo": "Pudricion apical", "Evaluacion": "Si / No", "Descripcion": "Defecto fisiologico de alto rechazo", "Herramienta": "p"},
        {"Atributo": "Danos por plagas", "Evaluacion": "Conforme / No conforme", "Descripcion": "Afectacion visible por insectos", "Herramienta": "p / np"},
    ],
    "Lechuga": [
        {"Atributo": "Hojas quemadas", "Evaluacion": "Conteo", "Descripcion": "Deterioro de borde o deshidratacion", "Herramienta": "c / u"},
        {"Atributo": "Presencia de tierra", "Evaluacion": "Si / No", "Descripcion": "Defecto de lavado o cosecha", "Herramienta": "p"},
        {"Atributo": "Marchitez", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Perdida de frescura comercial", "Herramienta": "p"},
        {"Atributo": "Hojas con insectos", "Evaluacion": "Conteo", "Descripcion": "Riesgo sanitario y rechazo visual", "Herramienta": "c"},
    ],
    "Pina": [
        {"Atributo": "Corona deteriorada", "Evaluacion": "Conforme / No conforme", "Descripcion": "Afecta presentacion y vida util", "Herramienta": "p"},
        {"Atributo": "Golpes en cascara", "Evaluacion": "Conteo", "Descripcion": "Dano por transporte o apilamiento", "Herramienta": "c / u"},
        {"Atributo": "Fermentacion visible", "Evaluacion": "Si / No", "Descripcion": "Senal de sobremadurez o dano interno", "Herramienta": "p"},
        {"Atributo": "Calibre fuera de especificacion", "Evaluacion": "Conforme / No conforme", "Descripcion": "No cumple categoria comercial", "Herramienta": "p / np"},
    ],
}


NORMATIVES = ["OMS", "USP", "Farmacopea Europea", "ISO 9001", "ISO 22000", "BPA", "BPM", "INVIMA Colombia"]
INDUSTRIES = ["Farmaceutica", "Cosmetica", "Alimentaria", "Agroindustrial"]


def all_products() -> list[str]:
    products: list[str] = []
    for values in PRODUCT_CATALOG.values():
        products.extend(values)
    return sorted(set(products))


def product_type_for(product: str) -> str | None:
    for product_type, products in PRODUCT_CATALOG.items():
        if product in products:
            return product_type
    return None


def catalog_dataframe() -> pd.DataFrame:
    rows = []
    for product_type, products in PRODUCT_CATALOG.items():
        for product in products:
            rows.append({"Tipo": product_type, "Producto": product, "Variables sugeridas": ", ".join(suggest_for_product(product))})
    return pd.DataFrame(rows)


def variables_dataframe() -> pd.DataFrame:
    return pd.DataFrame(CONTINUOUS_VARIABLES)


def attributes_dataframe() -> pd.DataFrame:
    return pd.DataFrame(ATTRIBUTE_VARIABLES)


def suggest_for_product(product: str) -> list[str]:
    if product in PRODUCT_SUGGESTIONS:
        return PRODUCT_SUGGESTIONS[product]
    lower = product.lower()
    if any(word in lower for word in ["sabila", "manzanilla", "menta", "romero", "calendula", "eucalipto", "valeriana"]):
        return ["Contenido de aceites esenciales", "Humedad", "pH", "Principios activos", "Aroma caracteristico"]
    if any(word in lower for word in ["tomate", "lechuga", "cilantro", "zanahoria", "aji", "pepino"]):
        return ["Peso fresco", "Diametro", "Color", "Nivel de limpieza", "Presencia de plagas"]
    return ["Peso fresco", "Diametro", "Grados Brix", "Firmeza", "Defectos de color"]


def product_description(product: str) -> str:
    if product in PRODUCT_DESCRIPTIONS:
        return PRODUCT_DESCRIPTIONS[product]
    lower = product.lower()
    if any(word in lower for word in ["sabila", "manzanilla", "menta", "romero", "calendula", "eucalipto", "valeriana", "limoncillo"]):
        return "Producto medicinal o aromatico cuya calidad depende de la estabilidad fisicoquimica, contenido de compuestos activos, humedad, aroma, pureza del lote y ausencia de contaminantes. El control estadistico permite detectar variaciones antes de que afecten seguridad o eficacia."
    if any(word in lower for word in ["tomate", "lechuga", "cilantro", "zanahoria", "aji", "pepino"]):
        return "Hortaliza de interes agroindustrial donde la calidad se relaciona con frescura, limpieza, calibre, color, danos mecanicos y sanidad. El monitoreo SPC ayuda a mantener uniformidad y reducir no conformidades."
    return "Fruta de interes comercial donde la calidad se evalua por calibre, peso, madurez, firmeza, contenido de solidos solubles y defectos visibles. El control estadistico ayuda a estabilizar el proceso y mejorar aceptacion del mercado."


def attributes_for_product(product: str) -> pd.DataFrame:
    if product in PRODUCT_ATTRIBUTES:
        return pd.DataFrame(PRODUCT_ATTRIBUTES[product])
    lower = product.lower()
    if any(word in lower for word in ["sabila", "manzanilla", "menta", "romero", "calendula", "eucalipto", "valeriana", "limoncillo"]):
        rows = [
            {"Atributo": "Aroma no caracteristico", "Evaluacion": "Conforme / No conforme", "Descripcion": "Perdida de identidad sensorial", "Herramienta": "p"},
            {"Atributo": "Material extrano", "Evaluacion": "Conteo", "Descripcion": "Impurezas del lote", "Herramienta": "c / u"},
            {"Atributo": "Moho visible", "Evaluacion": "Si / No", "Descripcion": "Riesgo por humedad", "Herramienta": "p"},
            {"Atributo": "Color no uniforme", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Variacion por secado o mezcla", "Herramienta": "p"},
        ]
    elif any(word in lower for word in ["tomate", "lechuga", "cilantro", "zanahoria", "aji", "pepino"]):
        rows = [
            {"Atributo": "Hojas o superficie deteriorada", "Evaluacion": "Conteo", "Descripcion": "Deterioro visible", "Herramienta": "c / u"},
            {"Atributo": "Presencia de tierra", "Evaluacion": "Si / No", "Descripcion": "Defecto de limpieza", "Herramienta": "p"},
            {"Atributo": "Danos por plagas", "Evaluacion": "Conforme / No conforme", "Descripcion": "Defecto sanitario", "Herramienta": "p / np"},
            {"Atributo": "Marchitez", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Perdida de frescura", "Herramienta": "p"},
        ]
    else:
        rows = [
            {"Atributo": "Golpes o magulladuras", "Evaluacion": "Conteo", "Descripcion": "Danos de cosecha o transporte", "Herramienta": "c / u"},
            {"Atributo": "Madurez no uniforme", "Evaluacion": "Aceptable / No aceptable", "Descripcion": "Variacion comercial del lote", "Herramienta": "p"},
            {"Atributo": "Defectos de color", "Evaluacion": "Conforme / No conforme", "Descripcion": "Calidad visual", "Herramienta": "p / np"},
            {"Atributo": "Frutos con pudricion", "Evaluacion": "Conteo", "Descripcion": "Deterioro sanitario", "Herramienta": "c"},
        ]
    return pd.DataFrame(rows)


def unit_for_variable(variable: str) -> str | None:
    normalized = variable.strip().lower()
    aliases = {
        "peso del gel": "g",
        "contenido de aloina": "mg/g",
        "humedad": "%",
        "materia seca": "%",
        "rendimiento": "%",
        "concentracion de mentol": "mg/g",
        "contenido de flavonoides": "mg/g",
        "concentracion de citral": "%",
        "color": "escala",
        "madurez": "escala",
    }
    if normalized in aliases:
        return aliases[normalized]
    for item in CONTINUOUS_VARIABLES:
        if item["Variable"].strip().lower() == normalized:
            return item["Unidad"]
    return None


def recommend_chart(feature: str, data_kind: str) -> str:
    text = f"{feature} {data_kind}".lower()
    if any(word in text for word in ["si/no", "conforme", "defectuoso", "proporcion", "plagas", "manchas"]):
        return "p si el tamano de muestra varia; np si el tamano es constante."
    if any(word in text for word in ["defectos", "conteo", "hojas defectuosas", "insectos"]):
        return "c si el area/unidad de inspeccion es constante; u si varia."
    return "Xbar-R para subgrupos pequenos; Xbar-S para subgrupos mayores o variabilidad estable."
