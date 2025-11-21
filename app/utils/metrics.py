# app/utils/metrics.py

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def compute_key_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute simple key metrics over all numeric columns in the DataFrame.
    Returns a flat dict suitable for feeding into the LLM.
    """
    out: Dict[str, Any] = {}

    if df.empty:
        return out

    num = df.select_dtypes(include=["number"])
    if num.empty:
        return out

    for col in num.columns:
        series = num[col].dropna()
        if series.empty:
            continue

        out[f"{col}_mean"] = float(series.mean())
        out[f"{col}_sum"] = float(series.sum())
        out[f"{col}_min"] = float(series.min())
        out[f"{col}_max"] = float(series.max())
        out[f"{col}_std"] = float(series.std(ddof=0))

    out["row_count"] = int(len(df))
    out["column_count"] = int(len(df.columns))

    return out


def detect_trends(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Detect simple up/down/stable trends for numeric columns
    based on the first and last value. Assumes row order ~ time order.
    """
    trends: List[Dict[str, Any]] = []

    if df.empty:
        return trends

    num = df.select_dtypes(include=["number"])
    if num.empty:
        return trends

    for col in num.columns:
        series = num[col].dropna()
        if len(series) < 2:
            continue

        first = series.iloc[0]
        last = series.iloc[-1]

        if first == 0:
            change_pct = np.inf if last != 0 else 0.0
        else:
            change_pct = (last - first) / abs(first) * 100.0

        if change_pct > 5:
            direction = "up"
        elif change_pct < -5:
            direction = "down"
        else:
            direction = "stable"

        trends.append(
            {
                "metric": col,
                "direction": direction,
                "change_pct": float(change_pct),
                "description": f"{col} changed by {change_pct:.1f}% from first to last row.",
            }
        )

    return trends


def compute_correlations(df: pd.DataFrame, threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Compute pairwise Pearson correlations between numeric columns,
    and return only strong relationships (|corr| >= threshold).
    """
    corrs: List[Dict[str, Any]] = []

    if df.empty:
        return corrs

    num = df.select_dtypes(include=["number"])
    if num.shape[1] < 2:
        return corrs

    corr_matrix = num.corr()

    cols = corr_matrix.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            a = cols[i]
            b = cols[j]
            coef = corr_matrix.loc[a, b]
            if pd.isna(coef):
                continue
            if abs(coef) >= threshold:
                corrs.append(
                    {
                        "a": a,
                        "b": b,
                        "coefficient": float(coef),
                    }
                )

    return corrs
