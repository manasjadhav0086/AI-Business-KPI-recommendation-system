def generate_insight(change, region, product):

    if change < 0:
        trend = "declined"
    else:
        trend = "increased"

    insight = f"""
Revenue {trend} by {abs(change)}%.

The primary driver of this change appears to be weaker performance
in the {product} category, particularly in the {region} region.

This suggests reduced demand in that category or regional
sales challenges that should be investigated further.
"""

    return insight.strip()