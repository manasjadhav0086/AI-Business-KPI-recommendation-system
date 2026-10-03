import re
from typing import Union, Optional

CURRENCY_MAP = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "AED": "د.إ",
    "₹": "₹",
    "$": "$",
    "€": "€",
    "£": "£",
    "د.إ": "د.إ"
}

def format_business_number(
    value: Union[int, float, None],
    metric_type: str = "number",
    currency_symbol: str = "₹",
    numbering_mode: str = "Indian",
    decimals: int = 2
) -> str:
    """
    Enterprise universal number & currency formatter.
    Supports Indian (Lakh/Crore) and International (K/M/B) notation.
    Respects metric types (currency, count, percentage, ratio, number).
    """
    if value is None or (isinstance(value, float) and (value != value)):  # NaN check
        return "N/A"

    try:
        val = float(value)
    except (ValueError, TypeError):
        return str(value)

    if metric_type == "percentage":
        return f"{val:+.{decimals}f}%" if abs(val) < 1000 else f"{val:+.1f}%"

    if metric_type == "ratio":
        return f"{val:.{decimals}f}x"

    symbol = CURRENCY_MAP.get(currency_symbol.strip(), currency_symbol.strip()) if currency_symbol else ""
    prefix = symbol if (metric_type == "currency" and symbol) else ""
    sign = "-" if val < 0 else ""
    abs_val = abs(val)

    # Values under 1,000 are not abbreviated
    if abs_val < 1000:
        if abs_val == int(abs_val):
            formatted = f"{int(abs_val):,}"
        else:
            formatted = f"{abs_val:.{decimals}f}".rstrip("0").rstrip(".")
        return f"{sign}{prefix}{formatted}"

    # Indian Numbering System: K -> Lakh -> Crore
    if str(numbering_mode).lower().startswith("ind"):
        if abs_val < 100_000:  # 1K to 99.9K
            k_val = abs_val / 1000.0
            formatted = f"{k_val:.{decimals}f}".rstrip("0").rstrip(".") + "K"
        elif abs_val < 10_000_000:  # 1 Lakh to 99.9 Lakh
            lakh_val = abs_val / 100_000.0
            formatted = f"{lakh_val:.{decimals}f}".rstrip("0").rstrip(".") + " Lakh"
        elif abs_val < 1_000_000_000:  # 1 Crore to 99.9 Crore
            cr_val = abs_val / 10_000_000.0
            formatted = f"{cr_val:.{decimals}f}".rstrip("0").rstrip(".") + " Cr"
        else:  # >= 100 Crore / 1 Billion
            b_val = abs_val / 1_000_000_000.0
            formatted = f"{b_val:.{decimals}f}".rstrip("0").rstrip(".") + "B"
        return f"{sign}{prefix}{formatted}"

    # International Numbering System: K -> M -> B -> T
    else:
        if abs_val < 1_000_000:
            k_val = abs_val / 1000.0
            formatted = f"{k_val:.{decimals}f}".rstrip("0").rstrip(".") + "K"
        elif abs_val < 1_000_000_000:
            m_val = abs_val / 1_000_000.0
            formatted = f"{m_val:.{decimals}f}".rstrip("0").rstrip(".") + "M"
        else:
            b_val = abs_val / 1_000_000_000.0
            formatted = f"{b_val:.{decimals}f}".rstrip("0").rstrip(".") + "B"
        return f"{sign}{prefix}{formatted}"

def clean_ai_text(text: str) -> str:
    """
    Sanitizes AI text output to prevent raw markdown symbol dumps (###, **, *, etc.).
    """
    if not text or not isinstance(text, str):
        return ""

    # Remove markdown header syntax at line starts
    cleaned = re.sub(r'^[#]+\s*', '', text, flags=re.MULTILINE)
    # Convert bold markdown **word** into clean string or preserve readable text
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
    cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
    # Convert bullet points * or • to clean hyphen bullets
    cleaned = re.sub(r'^[•*]\s*', '- ', cleaned, flags=re.MULTILINE)
    # Remove excessive blank lines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()
