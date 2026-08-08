"""Loads the product catalog and FAQ document from the baked-in data files.

Data is generated once at build time (see _generate_data.py at the repo root) and
committed as data/ecommerce_products.csv + data/faq.json, rather than regenerated
on every Space cold start -- faster startup, and identical data across restarts.
"""

import json
import pandas as pd
import streamlit as st


@st.cache_resource
def load_products(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


@st.cache_resource
def load_faq(json_path: str) -> list:
    with open(json_path, "r") as f:
        return json.load(f)
