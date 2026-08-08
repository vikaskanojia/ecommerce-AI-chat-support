"""The three tools the agent can call. Built as a factory function so they can
close over the specific DataFrame/index instances loaded for this Space session,
rather than relying on module-level globals.
"""

from typing import Optional
from langchain_core.tools import tool


def _format_product_row(products_df, product_id: int) -> str:
    row = products_df.loc[products_df["product_id"] == product_id].iloc[0]
    return (
        f"[{row.product_id}] {row.product_name} - ${row.price_usd:.2f}, "
        f"{row.rating} stars ({row.num_reviews} reviews), {row.color}, "
        f"stock: {row.stock_quantity}. {row.description}"
    )


def build_tools(products_df, product_vector_store, faq_vector_store, faq_docs, top_k_products: int, top_k_faq: int):
    """Returns the list of tools, bound to this session's data and indexes."""

    @tool
    def semantic_product_search(description: str) -> str:
        """Find products that semantically match a fuzzy, descriptive query -- use this
        for vague requests like 'something for a coffee lover' or 'a gift for a hiker'.
        Args:
            description: what the shopper is looking for, in plain language
        """
        hits = product_vector_store.similarity_search(description, k=top_k_products)
        if not hits:
            return "No matching products found."
        return "\n".join(_format_product_row(products_df, h.metadata["product_id"]) for h in hits)

    @tool
    def filter_products_by_criteria(
        category: Optional[str] = "",
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        in_stock_only: Optional[bool] = False,
    ) -> str:
        """Filter the product catalog by exact structured criteria: category, max price,
        min rating, or stock availability. Leave a field empty/None to not filter on it.
        Args:
            category: exact category name, e.g. 'Electronics' (optional)
            max_price: maximum price in USD (optional)
            min_rating: minimum star rating, 0-5 (optional)
            in_stock_only: if true, only return products with stock_quantity > 0
        """
        result = products_df.copy()
        if category:
            result = result[result["category"].str.lower() == category.lower()]
        if max_price is not None:
            result = result[result["price_usd"] <= max_price]
        if min_rating is not None:
            result = result[result["rating"] >= min_rating]
        if in_stock_only:
            result = result[result["stock_quantity"] > 0]
        result = result.sort_values("rating", ascending=False).head(8)
        if result.empty:
            return "No products match those criteria."
        return "\n".join(_format_product_row(products_df, pid) for pid in result["product_id"])

    @tool
    def search_faq(question: str) -> str:
        """Search store policy FAQs -- shipping, returns, refunds, payments, account,
        warranty, discounts, and similar store-policy questions. Not for product
        recommendations.
        Args:
            question: the shopper's policy question, in plain language
        """
        hits = faq_vector_store.similarity_search(question, k=top_k_faq)
        if not hits:
            return "No matching FAQ entry found."
        results = []
        for h in hits:
            entry = next(f for f in faq_docs if f["id"] == h.metadata["faq_id"])
            results.append(f"Q: {entry['question']}\nA: {entry['answer']}")
        return "\n\n".join(results)

    return [semantic_product_search, filter_products_by_criteria, search_faq]
