"""Loads config.yaml once and exposes it as a plain dict, cached by Streamlit."""

import os
import yaml
import streamlit as st

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")


@st.cache_resource
def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)
