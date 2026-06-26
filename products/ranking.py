"""
Three-tier relevance ranking engine.

Tier 1: category matches query              → score 0.70–1.00
Tier 2: tags contain query (category miss)  → score 0.40–0.69
Tier 3: name or description contains query  → score 0.10–0.39
"""

def _normalize(text: str) -> str:
    return text.lower().strip()

def score_product(product, query: str) -> tuple[float, str]:
    """Return (relevance_score, rank_reason) for a product given a query."""
    q = _normalize(query)
    category = _normalize(product.category)
    tags = [_normalize(t) for t in product.tags.split(',') if t.strip()]
    name = _normalize(product.product_name)
    description = _normalize(product.product_description)

    # ── Tier 1: category match ────────────────────────────────────────────────
    if q in category or category in q:
        # sub-sort: more matching tags → higher score
        matching_tags = sum(1 for t in tags if q in t or t in q)
        score = 0.70 + min(matching_tags * 0.06, 0.30)
        return round(score, 4), "Category match"

    # ── Tier 2: tag match ─────────────────────────────────────────────────────
    exact_tag_match = q in tags
    partial_tag_match = any(q in t or t in q for t in tags)

    if exact_tag_match:
        return 0.65, f"Tag match ({q})"
    if partial_tag_match:
        matched = [t for t in tags if q in t or t in q]
        return 0.50, f"Tag match ({matched[0]})"

    # ── Tier 3: name / description match ─────────────────────────────────────
    if q in name:
        return 0.35, "Name match"
    if q in description:
        return 0.20, "Description match"

    return 0.0, "No match"


def rank_products(queryset, query: str):
    """
    Return a list of (product, score, reason) tuples sorted by score desc.
    Products with score 0 are excluded.
    """
    results = []
    for product in queryset:
        score, reason = score_product(product, query)
        if score > 0:
            results.append((product, score, reason))

    results.sort(key=lambda x: x[1], reverse=True)
    return results
