"""Builds the two FAISS indexes (products, FAQ) used by the retrieval tools.

Both share one embedding model instance. Indexing happens once per Space
lifetime via st.cache_resource -- not on every user message. Streamlit's cache
hasher natively supports DataFrames and lists of dicts as cache-key inputs, so
no manual conversion to a hashable type is needed here.
"""

import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


@st.cache_resource
def build_embeddings(model_name: str):
    return HuggingFaceEmbeddings(model_name=model_name)


@st.cache_resource
def build_product_index(_embeddings, products_df):
    docs = [
        Document(
            page_content=f"{row.product_name} | {row.category} | {row.brand} | {row.description}",
            metadata={"product_id": row.product_id},
        )
        for row in products_df.itertuples()
    ]
    return FAISS.from_documents(docs, _embeddings)


@st.cache_resource
def build_faq_index(_embeddings, faq_records: list):
    docs = [
        Document(page_content=f"{f['question']} {f['answer']}", metadata={"faq_id": f["id"]})
        for f in faq_records
    ]
    return FAISS.from_documents(docs, _embeddings)
