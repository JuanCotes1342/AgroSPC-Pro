import numpy as np
import pandas as pd


def variable_example(subgroups: int = 30, sample_size: int = 5) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    data = rng.normal(loc=12.4, scale=0.28, size=(subgroups, sample_size))
    if subgroups > 14:
        data[14, 2] = 13.55
    df = pd.DataFrame(data, columns=[f"M{i+1}" for i in range(sample_size)]).round(3)
    df.insert(0, "Subgrupo", range(1, subgroups + 1))
    return df


def attribute_example(rows: int = 30) -> pd.DataFrame:
    rng = np.random.default_rng(8)
    inspected = rng.integers(80, 130, size=rows)
    defects = rng.poisson(4, size=rows)
    defectives = np.minimum(rng.poisson(3, size=rows), inspected)
    df = pd.DataFrame({
        "Subgrupo": range(1, rows + 1),
        "Inspeccionados": inspected,
        "Defectuosos": defectives,
        "Defectos": defects,
    })
    return df


def pareto_example() -> pd.DataFrame:
    return pd.DataFrame({
        "Categoria": ["Golpes", "Hongos", "Color", "Tamano", "Plagas", "Madurez", "Otros"],
        "Frecuencia": [42, 31, 24, 16, 11, 9, 6],
    })
