import pandas as pd
import numpy as np
from typing import Dict, Any, List

def calculate_data_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes a comprehensive and transparent Data Quality & Integrity audit.
    """
    if df.empty:
        return {
            "overall_score": 0,
            "total_rows": 0,
            "total_columns": 0,
            "completeness_pct": 0.0,
            "validity_pct": 0.0,
            "uniqueness_pct": 0.0,
            "consistency_pct": 0.0,
            "diagnostics": []
        }

    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols

    # 1. Missing Values (Completeness)
    missing_counts = df.isnull().sum()
    total_missing_cells = int(missing_counts.sum())
    missing_pct = (total_missing_cells / total_cells * 100) if total_cells > 0 else 0.0
    completeness_score = max(0, 100 - (missing_pct * 2))

    # 2. Duplicate Rows (Uniqueness)
    exact_duplicates = int(df.duplicated().sum())
    dup_pct = (exact_duplicates / total_rows * 100) if total_rows > 0 else 0.0
    uniqueness_score = max(0, 100 - (dup_pct * 5))

    # 3. Invalid / Negative Revenue (Validity)
    negative_revenue = int((df["revenue"] <= 0).sum())
    null_dates = int(df["date"].isnull().sum())
    invalid_records = negative_revenue + null_dates
    invalid_pct = (invalid_records / total_rows * 100) if total_rows > 0 else 0.0
    validity_score = max(0, 100 - (invalid_pct * 10))

    # 4. Outlier Analysis (Statistical Consistency)
    mean_rev = df["revenue"].mean()
    std_rev = df["revenue"].std() if total_rows > 1 else 1.0
    outlier_count = int(((df["revenue"] - mean_rev).abs() > 3 * std_rev).sum())
    outlier_pct = (outlier_count / total_rows * 100) if total_rows > 0 else 0.0
    consistency_score = max(0, 100 - (outlier_pct * 3))

    # 5. Data Freshness / Span
    min_date = str(df["date"].min().strftime("%Y-%m-%d")) if not df["date"].isnull().all() else "N/A"
    max_date = str(df["date"].max().strftime("%Y-%m-%d")) if not df["date"].isnull().all() else "N/A"
    date_span_days = int((df["date"].max() - df["date"].min()).days) if not df["date"].isnull().all() else 0

    # Overall Quality Score
    overall_score = round(
        (completeness_score * 0.35) +
        (validity_score * 0.30) +
        (uniqueness_score * 0.20) +
        (consistency_score * 0.15)
    )

    column_stats = []
    for col in df.columns:
        col_missing = int(df[col].isnull().sum())
        col_missing_pct = (col_missing / total_rows * 100) if total_rows > 0 else 0.0
        unique_vals = int(df[col].nunique())
        dtype_str = str(df[col].dtype)

        column_stats.append({
            "column": col,
            "type": dtype_str,
            "missing": col_missing,
            "missing_pct": col_missing_pct,
            "unique_values": unique_vals,
            "status": "🟢 Good" if col_missing_pct < 1.0 else ("🟡 Moderate" if col_missing_pct < 5.0 else "🔴 High Missing")
        })

    diagnostics = [
        {
            "dimension": "Completeness",
            "score": round(completeness_score),
            "status": "🟢 Passed" if completeness_score >= 90 else "🟡 Warning",
            "metric": f"{total_missing_cells:,} missing cells ({missing_pct:.2f}%)",
            "detail": "Evaluates the proportion of non-null attributes across all columns."
        },
        {
            "dimension": "Validity & Bounds",
            "score": round(validity_score),
            "status": "🟢 Passed" if validity_score >= 95 else "🔴 Error",
            "metric": f"{negative_revenue} invalid price records (≤ ₹0)",
            "detail": "Checks whether monetary fields have positive valid numeric values."
        },
        {
            "dimension": "Uniqueness",
            "score": round(uniqueness_score),
            "status": "🟢 Passed" if uniqueness_score >= 95 else "🟡 Duplicates",
            "metric": f"{exact_duplicates:,} duplicate rows ({dup_pct:.2f}%)",
            "detail": "Identifies exact duplicate row records in the active dataset."
        },
        {
            "dimension": "Statistical Consistency",
            "score": round(consistency_score),
            "status": "🟢 Passed" if consistency_score >= 90 else "🟡 Review",
            "metric": f"{outlier_count:,} statistical outliers (|Z| > 3.0)",
            "detail": "Scans for extreme transactions that deviate substantially from average order size."
        }
    ]

    return {
        "overall_score": overall_score,
        "total_rows": total_rows,
        "total_columns": total_cols,
        "total_missing_cells": total_missing_cells,
        "missing_pct": missing_pct,
        "exact_duplicates": exact_duplicates,
        "negative_revenue": negative_revenue,
        "outlier_count": outlier_count,
        "min_date": min_date,
        "max_date": max_date,
        "date_span_days": date_span_days,
        "diagnostics": diagnostics,
        "column_stats": column_stats
    }
