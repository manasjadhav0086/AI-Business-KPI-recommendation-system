def generate_recommendation(change, region, product):

    if change < 0:

        recommendation = f"""
Business Recommendation:

1. Investigate declining sales of {product} in the {region} region.
2. Consider running targeted marketing campaigns in this region.
3. Introduce limited-time discounts or promotional offers.
4. Review inventory availability and supply chain for this product.
5. Monitor customer feedback to identify demand issues.
"""

    else:

        recommendation = f"""
Business Recommendation:

1. Sales of {product} are improving in {region}.
2. Increase marketing investment in this region.
3. Expand product availability to capitalize on demand.
4. Introduce cross-selling opportunities with related products.
"""

    return recommendation.strip()