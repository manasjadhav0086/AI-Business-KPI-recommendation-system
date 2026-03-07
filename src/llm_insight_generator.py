def generate_insight(change, region, product):

    if change < 0:
        trend = "declined"
    else:
        trend = "increased"

    insight = f"""Revenue {trend} by {abs(change)}%.

The main contributing factor appears to be weaker
performance in the {product} category and lower
sales in the {region} region.

Further investigation into regional demand,
pricing, or product availability may be required.
"""

    return insight