import io
import os
import re
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

# Standard Recognized Field Synonyms
COLUMN_PATTERNS = {
    "date": [
        r"^(order|trx|trans|sales|invoice|created|purchase|booking)?[\s_]*(date|timestamp|time|datetime|day)$",
        r"^(date|timestamp)$"
    ],
    "revenue": [
        r"^(total|net|gross|item|sales)?[\s_]*(revenue|sales|amount|price|turnover|gmv|val|value)$",
        r"^(revenue|sales|amount|price)$"
    ],
    "profit": [
        r"^(net|gross|operating)?[\s_]*(profit|margin|earnings|income)[\s_]*(amount)?$",
        r"^(profit|margin)$"
    ],
    "quantity": [
        r"^(order|item|unit|sales)?[\s_]*(quantity|qty|units|volume|count)$",
        r"^(qty|quantity|units)$"
    ],
    "product": [
        r"^(product|item|sku|article|good)?[\s_]*(name|id|title|description|code)?$",
        r"^(product|item|sku)$"
    ],
    "category": [
        r"^(product|item)?[\s_]*(category|segment|dept|department|group|class|family)$",
        r"^(category|segment|department)$"
    ],
    "region": [
        r"^(customer|delivery|billing|shipping|store)?[\s_]*(region|state|area|zone|territory|location|city|country|province)$",
        r"^(region|state|area|zone|location)$"
    ],
    "customer": [
        r"^(customer|client|buyer|account|user)?[\s_]*(name|id|code|email|key)$",
        r"^(customer|client|buyer)$"
    ]
}

IGNORED_SHEET_NAMES = [
    "dashboard", "summary", "instructions", "instruction", "readme",
    "read me", "cover", "notes", "metadata", "config", "settings"
]

CURRENCY_DETECTION_PATTERNS = {
    "₹": [r"₹", r"\brs\.?\b", r"\binr\b", r"rupee"],
    "$": [r"\$", r"\busd\b", r"dollar"],
    "€": [r"€", r"\beur\b", r"euro"],
    "£": [r"£", r"\bgbp\b", r"pound"],
    "د.إ": [r"aed", r"dirham"]
}

def inspect_excel_workbook(file_bytes: bytes, filename: str) -> List[str]:
    """
    Returns the list of sheets available in an Excel workbook.
    """
    if filename.lower().endswith(".csv"):
        return ["CSV Data"]

    try:
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        return excel_file.sheet_names
    except Exception:
        return ["Sheet1"]

def detect_best_data_sheet(sheet_names: List[str]) -> str:
    """
    Automatically identifies the most probable data worksheet.
    """
    if len(sheet_names) == 1:
        return sheet_names[0]

    for name in sheet_names:
        clean_name = name.lower().strip()
        if clean_name not in IGNORED_SHEET_NAMES and not any(ign in clean_name for ign in IGNORED_SHEET_NAMES):
            return name

    return sheet_names[0]

def clean_numeric_string(val: Any) -> Optional[float]:
    """
    Cleans messy currency strings, commas, spaces, percentages, and Indian lakh notations.
    """
    if val is None or pd.isna(val):
        return None

    if isinstance(val, (int, float)):
        return float(val)

    str_val = str(val).strip()
    if not str_val:
        return None

    # Remove currency symbols, commas, spaces, and percentage signs
    cleaned = re.sub(r'[₹$€£\s,]', '', str_val, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b(rs|inr|usd|eur|gbp|aed|rupees?|dollars?)\b\.?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[%]', '', cleaned)

    # Check for negative in parentheses e.g. (1000) -> -1000
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = "-" + cleaned[1:-1]

    try:
        return float(cleaned)
    except ValueError:
        return None

def detect_currency_symbol(df_raw: pd.DataFrame) -> str:
    """
    Scans column headers and sample cell values to detect active currency.
    Defaults to INR (₹) if ambiguous.
    """
    combined_sample = " ".join(df_raw.columns.astype(str).tolist())
    
    # Sample first 20 rows of text
    sample_values = df_raw.head(20).astype(str).values.flatten()
    combined_sample += " " + " ".join(sample_values)

    for symbol, patterns in CURRENCY_DETECTION_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, combined_sample, re.IGNORECASE):
                return symbol

    return "₹"

def auto_detect_columns(columns: List[str]) -> Dict[str, Optional[str]]:
    """
    Matches raw column headers against standard business dimensions using regex.
    """
    detected_mapping: Dict[str, Optional[str]] = {
        "date": None,
        "revenue": None,
        "profit": None,
        "quantity": None,
        "product": None,
        "category": None,
        "region": None,
        "customer": None
    }

    used_cols = set()

    for std_field, patterns in COLUMN_PATTERNS.items():
        for col in columns:
            if col in used_cols:
                continue
            col_clean = col.lower().strip()
            for pat in patterns:
                if re.search(pat, col_clean):
                    detected_mapping[std_field] = col
                    used_cols.add(col)
                    break
            if detected_mapping[std_field]:
                break

    return detected_mapping

def process_uploaded_business_data(
    file_bytes: bytes,
    filename: str,
    selected_sheet: str = None,
    custom_mapping: Dict[str, Optional[str]] = None
) -> Dict[str, Any]:
    """
    Comprehensive ingestion, cleaning, schema normalization, and validation engine.
    """
    try:
        if filename.lower().endswith(".csv"):
            df_raw = pd.read_csv(io.BytesIO(file_bytes))
        else:
            sheet_to_read = selected_sheet or 0
            df_raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_to_read)

        if df_raw.empty:
            return {"success": False, "error": "Uploaded worksheet contains no records."}

        # Drop completely empty rows and columns
        df_raw = df_raw.dropna(how="all").dropna(axis=1, how="all")
        raw_cols = df_raw.columns.astype(str).tolist()

        # Currency Detection
        detected_currency = detect_currency_symbol(df_raw)

        # Column Mapping Detection
        mapping = auto_detect_columns(raw_cols)
        if custom_mapping:
            for k, v in custom_mapping.items():
                if v:
                    mapping[k] = v

        # Build Standardized Data Model
        standard_df = pd.DataFrame(index=df_raw.index)

        # 1. Revenue
        rev_col = mapping.get("revenue")
        if rev_col and rev_col in df_raw.columns:
            standard_df["revenue"] = df_raw[rev_col].apply(clean_numeric_string)
        else:
            # Fallback: search for first valid float column
            numeric_cols = df_raw.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                standard_df["revenue"] = df_raw[numeric_cols[0]].apply(clean_numeric_string)
                mapping["revenue"] = numeric_cols[0]
            else:
                return {
                    "success": False,
                    "error": "No numeric revenue or sales metric column could be detected in this file.",
                    "raw_columns": raw_cols,
                    "detected_mapping": mapping
                }

        standard_df["revenue"] = standard_df["revenue"].fillna(0.0)

        # 2. Date
        date_col = mapping.get("date")
        if date_col and date_col in df_raw.columns:
            standard_df["date"] = pd.to_datetime(df_raw[date_col], errors="coerce")
            # Drop invalid dates if any
            standard_df = standard_df.dropna(subset=["date"])
        else:
            # Synthetic sequential date baseline if date is absent
            standard_df["date"] = pd.date_range(end=pd.Timestamp.today(), periods=len(standard_df), freq="D")

        standard_df["date_only"] = standard_df["date"].dt.normalize()
        standard_df["month"] = standard_df["date"].dt.to_period("M").astype(str)
        standard_df["year"] = standard_df["date"].dt.year
        standard_df["quarter"] = standard_df["date"].dt.to_period("Q").astype(str)
        standard_df["day_name"] = standard_df["date"].dt.day_name()

        # 3. Product / Category
        prod_col = mapping.get("product") or mapping.get("category")
        if prod_col and prod_col in df_raw.columns:
            standard_df["product"] = df_raw[prod_col].fillna("General Item").astype(str).str.strip()
        else:
            standard_df["product"] = "All Products"

        # 4. Region
        reg_col = mapping.get("region")
        if reg_col and reg_col in df_raw.columns:
            standard_df["region"] = df_raw[reg_col].fillna("General Region").astype(str).str.strip().str.upper()
        else:
            standard_df["region"] = "Overall Market"

        # 5. Profit (Optional)
        prof_col = mapping.get("profit")
        if prof_col and prof_col in df_raw.columns:
            standard_df["profit"] = df_raw[prof_col].apply(clean_numeric_string).fillna(0.0)
            has_profit = True
        else:
            has_profit = False

        # 6. Quantity (Optional)
        qty_col = mapping.get("quantity")
        if qty_col and qty_col in df_raw.columns:
            standard_df["quantity"] = df_raw[qty_col].apply(clean_numeric_string).fillna(1.0)
            has_quantity = True
        else:
            standard_df["quantity"] = 1.0
            has_quantity = False

        # Sort chronologically
        standard_df = standard_df.sort_values("date").reset_index(drop=True)

        # Data Quality Statistics
        total_rows = len(standard_df)
        total_cols = len(raw_cols)
        duplicates = int(df_raw.duplicated().sum())
        missing_cells = int(df_raw.isnull().sum().sum())
        missing_pct = (missing_cells / (total_rows * total_cols) * 100) if (total_rows * total_cols) > 0 else 0.0
        
        quality_score = max(50, round(100 - (missing_pct * 2) - (duplicates / total_rows * 100 if total_rows > 0 else 0)))

        return {
            "success": True,
            "df": standard_df,
            "filename": filename,
            "currency_symbol": detected_currency,
            "raw_columns": raw_cols,
            "mapping": mapping,
            "has_profit": has_profit,
            "has_quantity": has_quantity,
            "quality_summary": {
                "total_rows": total_rows,
                "total_columns": total_cols,
                "date_range": f"{standard_df['date'].min().strftime('%b %Y')} - {standard_df['date'].max().strftime('%b %Y')}",
                "missing_pct": missing_pct,
                "duplicates": duplicates,
                "quality_score": quality_score
            }
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to parse file: {str(e)}"}

# Convenience aliases and direct dataframe helpers
def detect_column_mapping(columns: List[str]) -> Dict[str, Optional[str]]:
    return auto_detect_columns(columns)

def detect_currency_from_df(df_raw: pd.DataFrame) -> str:
    sym = detect_currency_symbol(df_raw)
    for code, s in [("INR", "₹"), ("USD", "$"), ("EUR", "€"), ("GBP", "£"), ("AED", "د.إ")]:
        if s == sym:
            return code
    return "INR"

def clean_numeric_series(series: pd.Series) -> pd.Series:
    return series.apply(clean_numeric_string)

def calculate_data_quality_score(df: pd.DataFrame) -> Dict[str, Any]:
    total_rows = len(df)
    total_cols = len(df.columns)
    duplicates = int(df.duplicated().sum())
    missing_cells = int(df.isnull().sum().sum())
    missing_pct = (missing_cells / (total_rows * total_cols) * 100) if (total_rows * total_cols) > 0 else 0.0
    quality_score = max(50, round(100 - (missing_pct * 2) - (duplicates / total_rows * 100 if total_rows > 0 else 0)))
    
    date_range_str = "N/A"
    if "date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["date"]) and not df["date"].empty:
        date_range_str = f"{df['date'].min().strftime('%b %Y')} - {df['date'].max().strftime('%b %Y')}"

    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "duplicates": duplicates,
        "missing_pct": missing_pct,
        "score": quality_score,
        "quality_score": quality_score,
        "date_range": date_range_str
    }

def clean_and_standardize_dataframe(df_raw: pd.DataFrame, custom_mapping: Dict[str, Optional[str]] = None) -> Tuple[pd.DataFrame, Dict[str, Optional[str]]]:
    raw_cols = df_raw.columns.astype(str).tolist()
    mapping = auto_detect_columns(raw_cols)
    if custom_mapping:
        for k, v in custom_mapping.items():
            if v:
                mapping[k] = v

    standard_df = pd.DataFrame(index=df_raw.index)

    # Revenue
    rev_col = mapping.get("revenue")
    if rev_col and rev_col in df_raw.columns:
        standard_df["revenue"] = df_raw[rev_col].apply(clean_numeric_string)
    else:
        num_cols = df_raw.select_dtypes(include=[np.number]).columns
        if len(num_cols) > 0:
            standard_df["revenue"] = df_raw[num_cols[0]].apply(clean_numeric_string)
            mapping["revenue"] = num_cols[0]
        else:
            standard_df["revenue"] = 0.0

    standard_df["revenue"] = standard_df["revenue"].fillna(0.0)

    # Date
    date_col = mapping.get("date")
    if date_col and date_col in df_raw.columns:
        standard_df["date"] = pd.to_datetime(df_raw[date_col], errors="coerce")
        standard_df = standard_df.dropna(subset=["date"])
    else:
        standard_df["date"] = pd.date_range(end=pd.Timestamp.today(), periods=len(standard_df), freq="D")

    standard_df["date_only"] = standard_df["date"].dt.normalize()
    standard_df["month"] = standard_df["date"].dt.to_period("M").astype(str)
    standard_df["year"] = standard_df["date"].dt.year
    standard_df["quarter"] = standard_df["date"].dt.to_period("Q").astype(str)
    standard_df["day_name"] = standard_df["date"].dt.day_name()

    # Product
    prod_col = mapping.get("product") or mapping.get("category")
    if prod_col and prod_col in df_raw.columns:
        standard_df["product"] = df_raw[prod_col].fillna("General Item").astype(str).str.strip()
    else:
        standard_df["product"] = "All Products"

    # Region
    reg_col = mapping.get("region")
    if reg_col and reg_col in df_raw.columns:
        standard_df["region"] = df_raw[reg_col].fillna("General Region").astype(str).str.strip().str.upper()
    else:
        standard_df["region"] = "Overall Market"

    # Profit (optional)
    prof_col = mapping.get("profit")
    if prof_col and prof_col in df_raw.columns:
        standard_df["profit"] = df_raw[prof_col].apply(clean_numeric_string).fillna(0.0)

    # Quantity (optional)
    qty_col = mapping.get("quantity")
    if qty_col and qty_col in df_raw.columns:
        standard_df["quantity"] = df_raw[qty_col].apply(clean_numeric_string).fillna(1.0)
    else:
        standard_df["quantity"] = 1.0

    return standard_df.sort_values("date").reset_index(drop=True), mapping

